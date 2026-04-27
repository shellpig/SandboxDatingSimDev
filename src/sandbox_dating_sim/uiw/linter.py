import re
from sandbox_dating_sim.schema.setup import SetupPackage
from sandbox_dating_sim.schema.validation import ValidationReport, Issue
from sandbox_dating_sim.core.ids import is_valid_id

class UIWLinter:
    """
    檢查 SetupPackage 是否符合 UIW v1.2 與遊戲規格 v1.2。
    """

    def validate(self, package: SetupPackage) -> ValidationReport:
        issues: list[Issue] = []
        issues.extend(self._check_world(package))
        issues.extend(self._check_ids(package))
        issues.extend(self._check_locations(package))
        issues.extend(self._check_characters(package))
        issues.extend(self._check_schedules(package))
        issues.extend(self._check_status_flags(package))
        issues.extend(self._check_endings(package))

        status = "failed" if any(i.severity == "error" for i in issues) else "passed"
        return ValidationReport(status=status, issues=issues)

    def _check_world(self, package: SetupPackage) -> list[Issue]:
        issues = []
        if package.world.end_date <= package.world.start_date:
            issues.append(Issue(
                severity="error",
                type="invalid_date_range",
                path="world.end_date",
                message="end_date 必須晚於 start_date。"
            ))
        return issues

    def _check_ids(self, package: SetupPackage) -> list[Issue]:
        issues = []
        all_ids = set()

        def _check(id_val: str, path: str, context: str):
            if not is_valid_id(id_val):
                issues.append(Issue(
                    severity="error",
                    type="invalid_id_format",
                    path=path,
                    message=f"{context} ID 格式不合法：{id_val}。"
                ))
            if id_val in all_ids:
                issues.append(Issue(
                    severity="error",
                    type="duplicate_id",
                    path=path,
                    message=f"{context} ID 重複：{id_val}。"
                ))
            else:
                all_ids.add(id_val)

        _check(package.world.world_id, "world.world_id", "World")
        for i, char in enumerate(package.characters):
            _check(char.character_id, f"characters[{i}].character_id", "Character")
        for i, loc in enumerate(package.locations):
            _check(loc.location_id, f"locations[{i}].location_id", "Location")
        for i, flag in enumerate(package.flags):
            _check(flag.flag_id, f"flags[{i}].flag_id", "Flag")
        for i, end in enumerate(package.endings):
            _check(end.ending_id, f"endings[{i}].ending_id", "Ending")
        
        return issues

    def _check_locations(self, package: SetupPackage) -> list[Issue]:
        issues = []
        loc_map = {loc.location_id: loc for loc in package.locations}

        for i, loc in enumerate(package.locations):
            if loc.location_type == "sub_location":
                if not loc.parent_location_id:
                    issues.append(Issue(
                        severity="error",
                        type="missing_parent_location",
                        path=f"locations[{i}].parent_location_id",
                        message=f"子地點 {loc.location_id} 必須隸屬於某個主地點 (parent_location_id)。"
                    ))
                elif loc.parent_location_id in loc_map:
                    if loc_map[loc.parent_location_id].location_type != "container":
                        issues.append(Issue(
                            severity="error",
                            type="invalid_parent_location",
                            path=f"locations[{i}].parent_location_id",
                            message=f"子地點 {loc.location_id} 參考的父地點 {loc.parent_location_id} 必須是 container。"
                        ))

            if loc.parent_location_id:
                if loc.parent_location_id not in loc_map:
                    issues.append(Issue(
                        severity="error",
                        type="unknown_parent_location",
                        path=f"locations[{i}].parent_location_id",
                        message=f"地點 {loc.location_id} 參考了不存在的父地點 {loc.parent_location_id}。"
                    ))

            if loc.is_visitable and not loc.available_time_slots:
                issues.append(Issue(
                    severity="error",
                    type="missing_time_slots",
                    path=f"locations[{i}].available_time_slots",
                    message=f"可進入地點 {loc.location_id} 至少需要一個 time_slot。"
                ))
            
            if loc.location_type == "container":
                sub_locations = [
                    sub for sub in package.locations 
                    if sub.parent_location_id == loc.location_id and sub.is_visitable
                ]
                if not sub_locations:
                    issues.append(Issue(
                        severity="error",
                        type="container_without_visitable_sub",
                        path=f"locations[{i}]",
                        message=f"主地點 {loc.location_id} 沒有任何可進入的子地點。"
                    ))

        return issues

    def _check_characters(self, package: SetupPackage) -> list[Issue]:
        issues = []
        for i, char in enumerate(package.characters):
            if not char.allowed_emotions:
                issues.append(Issue(
                    severity="warning",
                    type="empty_allowed_emotions",
                    path=f"characters[{i}].allowed_emotions",
                    message=f"角色 {char.character_id} 缺乏 allowed_emotions 設定。"
                ))
            if not char.allowed_costumes:
                issues.append(Issue(
                    severity="warning",
                    type="empty_allowed_costumes",
                    path=f"characters[{i}].allowed_costumes",
                    message=f"角色 {char.character_id} 缺乏 allowed_costumes 設定。"
                ))
            if not char.allowed_positions:
                issues.append(Issue(
                    severity="warning",
                    type="empty_allowed_positions",
                    path=f"characters[{i}].allowed_positions",
                    message=f"角色 {char.character_id} 缺乏 allowed_positions 設定。"
                ))
        return issues

    def _check_schedules(self, package: SetupPackage) -> list[Issue]:
        issues = []
        loc_ids = {loc.location_id for loc in package.locations}
        time_slots = set(package.world.time_slots)
        
        for i, char in enumerate(package.characters):
            schedule_map = {}
            for j, sch in enumerate(char.schedule):
                if sch.location_id not in loc_ids:
                    issues.append(Issue(
                        severity="error",
                        type="unknown_schedule_location",
                        path=f"characters[{i}].schedule[{j}].location_id",
                        message=f"行程引用了不存在的地點：{sch.location_id}。"
                    ))
                
                if sch.time_slot not in time_slots:
                    issues.append(Issue(
                        severity="error",
                        type="invalid_schedule_time_slot",
                        path=f"characters[{i}].schedule[{j}].time_slot",
                        message=f"行程引用了不合法或不存在的時間段：{sch.time_slot}。"
                    ))

                key = (sch.day_type, sch.time_slot, sch.priority)
                if key not in schedule_map:
                    schedule_map[key] = []
                schedule_map[key].append((j, sch))

            for key, group in schedule_map.items():
                if len(group) > 1:
                    orders = [sch.schedule_order for _, sch in group]
                    if len(set(orders)) < len(orders):
                        issues.append(Issue(
                            severity="error",
                            type="schedule_tie",
                            path=f"characters[{i}].schedule",
                            message=f"角色 {char.character_id} 在同一天、時間段與優先權中存在 schedule_order 相同的衝突行程。"
                        ))
        return issues

    def _check_status_flags(self, package: SetupPackage) -> list[Issue]:
        issues = []
        for i, status in enumerate(package.status_flags):
            if not status.effect:
                issues.append(Issue(
                    severity="error",
                    type="empty_effect",
                    path=f"status_flags[{i}].effect",
                    message=f"狀態旗標 {status.status_id} 的 effect 不可為空。"
                ))
            if not status.clear_rule:
                issues.append(Issue(
                    severity="error",
                    type="empty_clear_rule",
                    path=f"status_flags[{i}].clear_rule",
                    message=f"狀態旗標 {status.status_id} 的 clear_rule 不可為空。"
                ))
            if status.duration.type == "permanent" and not status.permanent_reason:
                issues.append(Issue(
                    severity="error",
                    type="missing_permanent_reason",
                    path=f"status_flags[{i}].permanent_reason",
                    message=f"狀態旗標 {status.status_id} 設為永久，但缺乏 permanent_reason。"
                ))
            if status.duration.type != "permanent" and "manual_only" in status.clear_rule and len(status.clear_rule) == 1:
                issues.append(Issue(
                    severity="warning",
                    type="hard_to_clear",
                    path=f"status_flags[{i}].clear_rule",
                    message=f"狀態旗標 {status.status_id} 並非永久，但解除條件只有 manual_only。"
                ))
        return issues

    def _check_endings(self, package: SetupPackage) -> list[Issue]:
        issues = []
        char_ids = {char.character_id for char in package.characters}
        char_ids.add("global")
        flag_ids = {flag.flag_id for flag in package.flags}

        for i, end in enumerate(package.endings):
            if end.target_character_id and end.target_character_id not in char_ids:
                issues.append(Issue(
                    severity="error",
                    type="unknown_target_character",
                    path=f"endings[{i}].target_character_id",
                    message=f"結局引用了不存在的對象角色：{end.target_character_id}。"
                ))
            
            def check_flags(flag_list, path_prefix):
                for j, req_flag in enumerate(flag_list):
                    match = re.match(r"^flag\.([a-zA-Z0-9_]+)\s*==", req_flag)
                    if match:
                        fid = match.group(1)
                        if fid not in flag_ids:
                            issues.append(Issue(
                                severity="error",
                                type="unknown_flag",
                                path=f"{path_prefix}[{j}]",
                                message=f"結局條件引用了未宣告的旗標：{fid}。"
                            ))
            
            check_flags(end.required_flags, f"endings[{i}].required_flags")
            check_flags(end.forbidden_flags, f"endings[{i}].forbidden_flags")
        return issues
