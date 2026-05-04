"""Phase 2-C Blueprint Linter."""

import re
from sandbox_dating_sim.schema.blueprint import EventBlueprint, BlueprintEvent
from sandbox_dating_sim.schema.setup import SetupPackage
from sandbox_dating_sim.schema.validation import ValidationReport, Issue
from sandbox_dating_sim.core.ids import is_valid_id

_VALID_STATS = {"INT", "CHA", "STR", "MORAL", "Cash", "Debt"}

# DSL pattern fragments
_COND_PATTERNS = [
    r"^day (==|>=|<=) \d+$",
    r"^date (==|>=|<=) \d{4}-\d{2}-\d{2}$",
    r"^time_slot == (morning|afternoon|evening)$",
    r"^location\.current == [a-z][a-z0-9_]*$",
    r"^flag\.[a-z][a-z0-9_]* == (true|false)$",
    r"^stat\.(INT|CHA|STR|MORAL|Cash|Debt) (==|>=|<=) -?\d+$",
    r"^character\.[a-z][a-z0-9_]*\.favor (==|>=|<=) -?\d+$",
    r"^status\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]* == (true|false)$",
]
_RESULT_PATTERNS = [
    r"^flag\.[a-z][a-z0-9_]* = (true|false)$",
    r"^stat\.(INT|CHA|STR|MORAL|Cash|Debt) [+\-]= -?\d+$",
    r"^character\.[a-z][a-z0-9_]*\.favor [+\-]= -?\d+$",
    r"^status\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]* = (true|false)$",
    r"^time_cost: \d+$",
    r"^goto: ([a-z][a-z0-9_]*|free_roam)$",
    r"^ending: [a-z][a-z0-9_]*$",
]

def _matches_any(s: str, patterns: list[str]) -> bool:
    return any(re.match(p, s.strip()) for p in patterns)

def _is_terminal(r: str) -> bool:
    r = r.strip()
    return r.startswith("goto:") or r.startswith("ending:")

def _is_item_syntax(s: str) -> bool:
    return bool(re.search(r"\b(item|inventory)\.", s))

def _get_goto_target(result_list: list[str]) -> str | None:
    for r in result_list:
        m = re.match(r"^goto: ([a-z][a-z0-9_]*|free_roam)$", r.strip())
        if m:
            return m.group(1)
    return None

def _get_ending_refs(result_list: list[str]) -> list[str]:
    endings = []
    for r in result_list:
        m = re.match(r"^ending: ([a-z][a-z0-9_]*)$", r.strip())
        if m:
            endings.append(m.group(1))
    return endings

def _extract_flag_refs(result_list: list[str]) -> list[str]:
    refs = []
    for r in result_list:
        m = re.match(r"^flag\.([a-z][a-z0-9_]*) = (true|false)$", r.strip())
        if m:
            refs.append(m.group(1))
    return refs

def _extract_cond_flag_refs(cond_list: list[str]) -> list[str]:
    refs = []
    for c in cond_list:
        m = re.match(r"^flag\.([a-z][a-z0-9_]*) == (true|false)$", c.strip())
        if m:
            refs.append(m.group(1))
    return refs

def _cond_has_gated(cond_list: list[str]) -> bool:
    """Check if conditions contain flag/stat/favor/status gates."""
    for c in cond_list:
        c = c.strip()
        if re.match(r"^flag\.", c) or re.match(r"^stat\.", c) or \
           re.match(r"^character\.", c) or re.match(r"^status\.", c):
            return True
    return False


class BlueprintLinter:
    """Linter for EventBlueprint, with optional SetupPackage cross-checks."""

    def validate_blueprint_only(self, blueprint: EventBlueprint) -> ValidationReport:
        issues: list[Issue] = []
        issues.extend(self._check_bp_ids(blueprint))
        issues.extend(self._check_events_only(blueprint))
        status = "failed" if any(i.severity == "error" for i in issues) else "passed"
        return ValidationReport(status=status, issues=issues)

    def validate(self, setup_package: SetupPackage, blueprint: EventBlueprint) -> ValidationReport:
        issues: list[Issue] = []
        # blueprint-only first
        issues.extend(self._check_bp_ids(blueprint))
        issues.extend(self._check_events_only(blueprint))
        # cross-checks
        issues.extend(self._check_cross(setup_package, blueprint))
        status = "failed" if any(i.severity == "error" for i in issues) else "passed"
        return ValidationReport(status=status, issues=issues)

    # ── blueprint-only helpers ──

    def _check_bp_ids(self, bp: EventBlueprint) -> list[Issue]:
        issues = []
        for fld in ("blueprint_id", "source_world_id", "initial_event_id"):
            val = getattr(bp, fld)
            if not is_valid_id(val):
                issues.append(Issue(severity="error", type="invalid_id_format",
                    path=fld, message=f"{fld} 格式不合法：{val}。"))
        return issues

    def _check_events_only(self, bp: EventBlueprint) -> list[Issue]:
        issues = []
        event_ids: dict[str, int] = {}
        # 先蒐集所有 event_id（支援前向引用）
        event_id_set: set[str] = {ev.event_id for ev in bp.events}

        for i, ev in enumerate(bp.events):
            p = f"events[{i}]"
            if not is_valid_id(ev.event_id):
                issues.append(Issue(severity="error", type="invalid_id_format",
                    path=f"{p}.event_id", message=f"event_id 格式不合法：{ev.event_id}。"))
            if ev.event_id in event_ids:
                issues.append(Issue(severity="error", type="duplicate_event_id",
                    path=f"{p}.event_id",
                    message=f"event_id 重複：{ev.event_id}（已出現於 events[{event_ids[ev.event_id]}]）。"))
            else:
                event_ids[ev.event_id] = i

            for j, tag in enumerate(ev.route_tags):
                if not tag.strip():
                    issues.append(Issue(severity="error", type="empty_route_tag",
                        path=f"{p}.route_tags[{j}]", message="route_tag 不可為空字串。"))

            # event.conditions DSL 驗證（blueprint-only，不做 reference 驗證）
            for j, cond in enumerate(ev.conditions):
                if _is_item_syntax(cond):
                    issues.append(Issue(severity="error", type="forbidden_item_syntax",
                        path=f"{p}.conditions[{j}]",
                        message=f"禁止使用 item.* / inventory.*：{cond}。"))
                if not _matches_any(cond, _COND_PATTERNS):
                    issues.append(Issue(severity="error", type="invalid_condition_dsl",
                        path=f"{p}.conditions[{j}]",
                        message=f"condition 無法解析為合法 DSL：{cond}。"))

            choice_ids: set[str] = set()
            for j, ch in enumerate(ev.choices):
                cp = f"{p}.choices[{j}]"
                if not is_valid_id(ch.choice_id):
                    issues.append(Issue(severity="error", type="invalid_id_format",
                        path=f"{cp}.choice_id", message=f"choice_id 格式不合法：{ch.choice_id}。"))
                if ch.choice_id in choice_ids:
                    issues.append(Issue(severity="error", type="duplicate_choice_id",
                        path=f"{cp}.choice_id", message=f"同 event 中 choice_id 重複：{ch.choice_id}。"))
                else:
                    choice_ids.add(ch.choice_id)
                issues.extend(self._check_result_list(ch.result, cp, event_id_set))

        if bp.initial_event_id not in event_id_set:
            issues.append(Issue(severity="error", type="unknown_initial_event",
                path="initial_event_id",
                message=f"initial_event_id '{bp.initial_event_id}' 不存在於 events 中。"))
        return issues


    def _check_result_list(self, result: list[str], path: str, event_id_set: set[str]) -> list[Issue]:
        issues = []
        terminals = [r for r in result if _is_terminal(r)]
        gotos = [r for r in result if r.strip().startswith("goto:")]
        endings = [r for r in result if r.strip().startswith("ending:")]

        # item/inventory 禁止
        for r in result:
            if _is_item_syntax(r):
                issues.append(Issue(severity="error", type="forbidden_item_syntax",
                    path=path, message=f"禁止使用 item.* / inventory.*：{r}。"))

        # DSL 格式驗證
        for r in result:
            if not _matches_any(r, _RESULT_PATTERNS):
                issues.append(Issue(severity="error", type="invalid_result_dsl",
                    path=path, message=f"result 無法解析為合法 DSL：{r}。"))

        # exactly one terminal
        if len(terminals) == 0:
            issues.append(Issue(severity="error", type="missing_terminal",
                path=path, message="choice result 必須有恰好一個 goto 或 ending。"))
        elif len(terminals) > 1:
            issues.append(Issue(severity="error", type="multiple_terminal",
                path=path, message=f"choice result 同時有多個流程出口（{len(terminals)} 個）。"))

        # goto target 存在
        for r in gotos:
            m = re.match(r"^goto: ([a-z][a-z0-9_]*|free_roam)$", r.strip())
            if m:
                target = m.group(1)
                if target != "free_roam" and target not in event_id_set:
                    issues.append(Issue(severity="error", type="unknown_goto_target",
                        path=path, message=f"goto 目標事件不存在：{target}。"))

        # time_cost override 不重複
        tc_count = sum(1 for r in result if re.match(r"^time_cost: \d+$", r.strip()))
        if tc_count > 1:
            issues.append(Issue(severity="error", type="duplicate_time_cost_override",
                path=path, message="同一 choice 中 time_cost 覆蓋不可出現多次。"))

        return issues

    # ── cross-checks ──

    def _check_cross(self, setup: SetupPackage, bp: EventBlueprint) -> list[Issue]:
        issues = []
        world_id = setup.world.world_id

        # source_world_id match
        if bp.source_world_id != world_id:
            issues.append(Issue(severity="error", type="world_id_mismatch",
                path="source_world_id",
                message=f"source_world_id '{bp.source_world_id}' 不符合 setup.world.world_id '{world_id}'。"))

        # blueprint_id 格式
        if bp.blueprint_id != f"{world_id}_event_blueprint":
            issues.append(Issue(severity="error", type="blueprint_id_mismatch",
                path="blueprint_id",
                message=f"blueprint_id 必須為 '{world_id}_event_blueprint'，目前為 '{bp.blueprint_id}'。"))

        # source_setup_package 格式
        if bp.source_setup_package != f"{world_id}_setup_package.md":
            issues.append(Issue(severity="error", type="source_setup_mismatch",
                path="source_setup_package",
                message=f"source_setup_package 必須為 '{world_id}_setup_package.md'，目前為 '{bp.source_setup_package}'。"))

        loc_map = {l.location_id: l for l in setup.locations}
        char_map = {c.character_id: c for c in setup.characters}
        flag_ids = {f.flag_id: f for f in setup.flags}
        status_map = {s.status_id: s for s in setup.status_flags}
        ending_ids = {e.ending_id for e in setup.endings}
        world_ts = list(setup.world.time_slots)
        world_ts_set = set(world_ts)
        proposed_flag_ids = {f.flag_id for f in bp.new_flags_proposed}

        # protagonist_home
        if "protagonist_home" not in loc_map:
            issues.append(Issue(severity="error", type="missing_protagonist_home",
                path="locations", message="SetupPackage 缺少 protagonist_home。"))
        else:
            home = loc_map["protagonist_home"]
            if list(home.available_time_slots) != world_ts:
                issues.append(Issue(severity="error", type="invalid_protagonist_home_time_slots",
                    path="locations[protagonist_home].available_time_slots",
                    message=f"protagonist_home 時段必須等於 world.time_slots {world_ts}。"))

        # location time slot subset
        for loc in setup.locations:
            for slot in loc.available_time_slots:
                if slot not in world_ts_set:
                    issues.append(Issue(severity="error", type="invalid_location_time_slot",
                        path=f"locations[{loc.location_id}].available_time_slots",
                        message=f"地點 {loc.location_id} 使用了不在 world.time_slots 的時段：{slot}。"))
                    break

        # location unlock/closed_conditions — 驗證 flag reference（full #24）
        loc_cond_flag_ids = set(flag_ids.keys()) | {f.flag_id for f in bp.new_flags_proposed}
        for loc in setup.locations:
            for field, cond_list in (("unlock_conditions", loc.unlock_conditions),
                                     ("closed_conditions", loc.closed_conditions)):
                for k, cond in enumerate(cond_list):
                    m_flag = re.match(r"^flag\.([a-z][a-z0-9_]*) == (true|false)$", cond.strip())
                    if m_flag and m_flag.group(1) not in loc_cond_flag_ids:
                        issues.append(Issue(severity="error",
                            type="unknown_location_condition_reference",
                            path=f"locations[{loc.location_id}].{field}[{k}]",
                            message=f"地點 '{loc.location_id}' 的 {field} 引用了未知 flag：{m_flag.group(1)}。"))

        # new_flags_proposed: only boolean, no conflict
        all_flag_ids = set(flag_ids.keys())
        for j, nf in enumerate(bp.new_flags_proposed):
            if nf.type != "boolean":
                issues.append(Issue(severity="error", type="proposed_flag_not_boolean",
                    path=f"new_flags_proposed[{j}]",
                    message=f"new_flags_proposed[{j}] {nf.flag_id} 必須為 boolean，目前為 {nf.type}。"))
            if nf.flag_id in all_flag_ids:
                issues.append(Issue(severity="error", type="proposed_flag_id_conflict",
                    path=f"new_flags_proposed[{j}].flag_id",
                    message=f"new_flags_proposed flag_id '{nf.flag_id}' 與既有 flag 衝突。"))
        all_flag_ids |= proposed_flag_ids

        # per-event cross-checks
        all_ending_refs: set[str] = set()
        fallback_events: list[BlueprintEvent] = []
        event_id_set = {ev.event_id for ev in bp.events}

        for i, ev in enumerate(bp.events):
            p = f"events[{i}]({ev.event_id})"

            # location_id 存在
            if ev.location_id not in loc_map:
                issues.append(Issue(severity="error", type="unknown_location",
                    path=f"{p}.location_id",
                    message=f"event '{ev.event_id}' 的 location_id '{ev.location_id}' 不存在。"))

            # time_slot 在 world.time_slots
            if ev.time_slot not in world_ts_set:
                issues.append(Issue(severity="error", type="event_time_outside_world",
                    path=f"{p}.time_slot",
                    message=f"event '{ev.event_id}' 的 time_slot '{ev.time_slot}' 不在 world.time_slots。"))

            # cast 存在
            for cast_id in ev.cast:
                if cast_id not in char_map:
                    issues.append(Issue(severity="error", type="unknown_cast_character",
                        path=f"{p}.cast",
                        message=f"event '{ev.event_id}' cast 中角色 '{cast_id}' 不存在。"))

            # expected_assets.characters ⊆ cast
            cast_set = set(ev.cast)
            for j, ca in enumerate(ev.expected_assets.characters):
                if ca.character_id not in cast_set:
                    issues.append(Issue(severity="error", type="asset_character_not_in_cast",
                        path=f"{p}.expected_assets.characters[{j}]",
                        message=f"expected_assets 角色 '{ca.character_id}' 不在 cast 中。"))
                elif ca.character_id in char_map:
                    ch = char_map[ca.character_id]
                    emo_ids = {e.id for e in ch.allowed_emotions}
                    cos_ids = {c.id for c in ch.allowed_costumes}
                    pos_ids = {p2.id for p2 in ch.allowed_positions}
                    if emo_ids and ca.emotion not in emo_ids:
                        issues.append(Issue(severity="warning", type="asset_emotion_not_whitelisted",
                            path=f"{p}.expected_assets.characters[{j}].emotion",
                            message=f"角色 '{ca.character_id}' 的 emotion '{ca.emotion}' 不在白名單中。"))
                    if cos_ids and ca.costume not in cos_ids:
                        issues.append(Issue(severity="warning", type="asset_costume_not_whitelisted",
                            path=f"{p}.expected_assets.characters[{j}].costume",
                            message=f"角色 '{ca.character_id}' 的 costume '{ca.costume}' 不在白名單中。"))
                    if pos_ids and ca.position not in pos_ids:
                        issues.append(Issue(severity="warning", type="asset_position_not_whitelisted",
                            path=f"{p}.expected_assets.characters[{j}].position",
                            message=f"角色 '{ca.character_id}' 的 position '{ca.position}' 不在白名單中。"))

            # initial event rules
            if ev.event_id == bp.initial_event_id:
                if ev.location_id != "protagonist_home":
                    issues.append(Issue(severity="error", type="initial_event_wrong_location",
                        path=f"{p}.location_id",
                        message=f"initial event 必須位於 protagonist_home，目前為 '{ev.location_id}'。"))
                if world_ts and ev.time_slot != world_ts[0]:
                    issues.append(Issue(severity="error", type="initial_event_wrong_slot",
                        path=f"{p}.time_slot",
                        message=f"initial event 的 time_slot 必須為第一個 world time slot '{world_ts[0]}'，目前為 '{ev.time_slot}'。"))
                if _cond_has_gated(ev.conditions):
                    issues.append(Issue(severity="error", type="initial_event_gated",
                        path=f"{p}.conditions",
                        message="initial event 不可包含 flag/stat/favor/status 前置條件。"))

            # effective time_cost vs remaining slots
            ts_idx = world_ts.index(ev.time_slot) if ev.time_slot in world_ts else None
            if ts_idx is not None:
                remaining = len(world_ts) - ts_idx
                if ev.time_cost > remaining:
                    issues.append(Issue(severity="error", type="insufficient_time",
                        path=f"{p}.time_cost",
                        message=f"event '{ev.event_id}' time_cost={ev.time_cost} 超過當日 time_slot '{ev.time_slot}' 後剩餘的時段數 {remaining}。"))

            # event.conditions reference cross-checks
            ep = f"{p}.conditions"
            for cond in ev.conditions:
                m_flag = re.match(r"^flag\.([a-z][a-z0-9_]*) == (true|false)$", cond.strip())
                if m_flag:
                    fid = m_flag.group(1)
                    if fid not in all_flag_ids:
                        issues.append(Issue(severity="error", type="unknown_flag",
                            path=ep, message=f"condition 引用未知 flag：{fid}。"))
                    elif fid in flag_ids and flag_ids[fid].type != "boolean":
                        issues.append(Issue(severity="error", type="non_boolean_flag",
                            path=ep, message=f"condition 只能引用 boolean flag，'{fid}' 為 {flag_ids[fid].type}。"))
                m_stat = re.match(r"^stat\.([A-Za-z]+) (==|>=|<=) -?\d+$", cond.strip())
                if m_stat and m_stat.group(1) not in _VALID_STATS:
                    issues.append(Issue(severity="error", type="unknown_stat",
                        path=ep, message=f"condition 引用了不存在的 stat：{m_stat.group(1)}。"))
                m_fav = re.match(r"^character\.([a-z][a-z0-9_]*)\.favor (==|>=|<=) -?\d+$", cond.strip())
                if m_fav and m_fav.group(1) not in char_map:
                    issues.append(Issue(severity="error", type="unknown_favor_character",
                        path=ep, message=f"condition favor 引用了不存在的角色：{m_fav.group(1)}。"))
                m_sts = re.match(r"^status\.([a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*) == (true|false)$", cond.strip())
                if m_sts:
                    target_id, status_id = m_sts.group(1), m_sts.group(2)
                    if status_id not in status_map:
                        issues.append(Issue(severity="error", type="unknown_status",
                            path=ep, message=f"condition 引用了不存在的 status_id：{status_id}。"))
                    elif target_id not in {t for t in status_map[status_id].targets}:
                        issues.append(Issue(severity="error", type="invalid_status_target",
                            path=ep, message=f"status '{status_id}' 的 target '{target_id}' 不在 StatusFlag.targets 中。"))

            # per-choice cross-checks
            for j, ch in enumerate(ev.choices):
                cp = f"{p}.choices[{j}]"
                result = ch.result

                # result flag refs
                for flag_id in _extract_flag_refs(result):
                    if flag_id not in all_flag_ids:
                        issues.append(Issue(severity="error", type="unknown_flag",
                            path=cp, message=f"result 引用未知 flag：{flag_id}。"))
                    elif flag_id in flag_ids and flag_ids[flag_id].type != "boolean":
                        issues.append(Issue(severity="error", type="non_boolean_flag",
                            path=cp, message=f"Blueprint 只能引用 boolean flag，'{flag_id}' 為 {flag_ids[flag_id].type}。"))

                # stat references
                for r in result:
                    m = re.match(r"^stat\.([A-Za-z]+) [+\-]= -?\d+$", r.strip())
                    if m and m.group(1) not in _VALID_STATS:
                        issues.append(Issue(severity="error", type="unknown_stat",
                            path=cp, message=f"result 引用了不存在的 stat：{m.group(1)}。"))

                # favor references
                for r in result:
                    m = re.match(r"^character\.([a-z][a-z0-9_]*)\.favor [+\-]= -?\d+$", r.strip())
                    if m and m.group(1) not in char_map:
                        issues.append(Issue(severity="error", type="unknown_favor_character",
                            path=cp, message=f"result favor 引用了不存在的角色：{m.group(1)}。"))

                # status references
                for r in result:
                    m = re.match(r"^status\.([a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*) = (true|false)$", r.strip())
                    if m:
                        target_id, status_id = m.group(1), m.group(2)
                        if status_id not in status_map:
                            issues.append(Issue(severity="error", type="unknown_status",
                                path=cp, message=f"result 引用了不存在的 status_id：{status_id}。"))
                        elif target_id not in {t for t in status_map[status_id].targets}:
                            issues.append(Issue(severity="error", type="invalid_status_target",
                                path=cp, message=f"status '{status_id}' 的 target '{target_id}' 不在 StatusFlag.targets 中。"))

                # ending refs
                for eid in _get_ending_refs(result):
                    all_ending_refs.add(eid)
                    if eid not in ending_ids:
                        issues.append(Issue(severity="error", type="unknown_ending",
                            path=cp, message=f"result 引用了不存在的 ending_id：{eid}。"))

                # direct goto time progression
                goto_target = _get_goto_target(result)
                if goto_target and goto_target != "free_roam" and ts_idx is not None:
                    target_ev = next((e for e in bp.events if e.event_id == goto_target), None)
                    if target_ev and target_ev.time_slot in world_ts:
                        expected_idx = ts_idx + ev.time_cost
                        actual_idx = world_ts.index(target_ev.time_slot)
                        if expected_idx < len(world_ts) and actual_idx != expected_idx:
                            issues.append(Issue(severity="error", type="goto_time_mismatch",
                                path=cp,
                                message=(
                                    f"goto '{goto_target}' 的 time_slot '{target_ev.time_slot}' "
                                    f"與 source time_cost 後預期 time_slot '{world_ts[expected_idx]}' 不符。"
                                )))

                # choice-level time_cost override check
                tc_overrides = [r for r in result if re.match(r"^time_cost: (\d+)$", r.strip())]
                for r in tc_overrides:
                    m = re.match(r"^time_cost: (\d+)$", r.strip())
                    if m and ts_idx is not None:
                        tc = int(m.group(1))
                        remaining = len(world_ts) - ts_idx
                        if tc > remaining:
                            issues.append(Issue(severity="error", type="insufficient_time",
                                path=cp,
                                message=f"choice time_cost override={tc} 超過剩餘時段數 {remaining}。"))

            # fallback_ending tracking
            if "fallback_ending" in ev.route_tags:
                fallback_events.append(ev)

            # daily high-impact warning
            if ev.repeat_policy == "daily":
                has_impact = any(
                    re.match(r"^(character\.|stat\.)", r.strip())
                    for ch in ev.choices for r in ch.result
                ) or bool(ev.route_tags)
                if has_impact:
                    issues.append(Issue(severity="warning", type="daily_high_impact",
                        path=f"{p}.repeat_policy",
                        message=f"daily event '{ev.event_id}' 有 stat/favor/route_tag 影響，可能造成重複收益問題。"))

        # uncovered endings
        for eid in ending_ids:
            if eid not in all_ending_refs:
                issues.append(Issue(severity="error", type="uncovered_ending",
                    path="events",
                    message=f"SetupPackage ending '{eid}' 未被任何 event choice result 引用。"))

        # fallback ending event
        if not fallback_events:
            issues.append(Issue(severity="error", type="missing_fallback_ending",
                path="events",
                message="至少需要一個帶 'fallback_ending' route_tag 的 event。"))
        else:
            for fe in fallback_events:
                has_ending = any(
                    _get_ending_refs(ch.result)
                    for ch in fe.choices
                )
                if not has_ending:
                    issues.append(Issue(severity="error", type="fallback_no_ending_result",
                        path=f"events[{fe.event_id}]",
                        message=f"fallback_ending event '{fe.event_id}' 沒有任何 choice result 包含 ending。"))

        # multiple critical events warning
        critical_evs = [ev for ev in bp.events if ev.priority == "critical"]
        if len(critical_evs) > 3:
            issues.append(Issue(severity="warning", type="multiple_critical_events",
                path="events",
                message=f"存在 {len(critical_evs)} 個 critical priority 事件，可能同時可用造成衝突。"))

        return issues
