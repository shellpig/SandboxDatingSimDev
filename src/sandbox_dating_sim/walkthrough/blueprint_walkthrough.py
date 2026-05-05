import re
from datetime import date, timedelta
from pydantic import BaseModel
from typing import Literal

from sandbox_dating_sim.schema.setup import SetupPackage, StatusFlag
from sandbox_dating_sim.schema.blueprint import EventBlueprint, BlueprintEvent, BlueprintChoice

class ActiveStatus(BaseModel):
    status_id: str
    target_id: str
    remaining_time_slots: int | None = None
    remaining_days: int | None = None
    source_event_id: str | None = None

class WalkthroughState(BaseModel):
    mode: Literal["free_roam", "in_event", "ending_reached", "dead_end", "blocked"]
    current_date: date
    current_time_slot: str
    current_location_id: str
    current_event_id: str | None = None
    flags: dict[str, bool] = {}
    stats: dict[str, int] = {}
    character_favor: dict[str, int] = {}
    active_statuses: dict[str, dict[str, ActiveStatus]] = {}  # target_id -> status_id -> ActiveStatus
    event_visit_log: dict[str, list[date]] = {}
    blocked_reason: str | None = None
    day_number: int = 1

class HistoryEntry(BaseModel):
    kind: Literal["event_choice", "rest", "wait", "ending"]
    date: date
    time_slot: str
    location_id: str | None = None
    event_id: str | None = None
    choice_id: str | None = None
    ending_id: str | None = None
    effective_time_cost: int | None = None

def create_initial_walkthrough_state(setup: SetupPackage, bp: EventBlueprint) -> WalkthroughState:
    flags = {}
    for flag in setup.flags:
        if flag.type == "boolean":
            flags[flag.flag_id] = True if flag.initial_value == "true" else False
    for nf in bp.new_flags_proposed:
        flags[nf.flag_id] = True if nf.initial_value == "true" else False

    stats = {}
    for st, val in setup.protagonist.initial_stats.model_dump().items():
        if val is not None:
            stats[st] = val

    favor = {}
    for ch in setup.characters:
        favor[ch.character_id] = ch.initial_favor

    return WalkthroughState(
        mode="free_roam",
        current_date=setup.world.start_date,
        day_number=1,
        current_time_slot=setup.world.time_slots[0],
        current_location_id="protagonist_home",
        flags=flags,
        stats=stats,
        character_favor=favor,
        active_statuses={},
        event_visit_log={}
    )

def _eval_op(op: str, left: int, right: int) -> bool:
    if op == "==": return left == right
    if op == ">=": return left >= right
    if op == "<=": return left <= right
    return False

def _check_condition(cond: str, state: WalkthroughState, setup: SetupPackage) -> bool:
    cond = cond.strip()
    
    m = re.match(r"^day (==|>=|<=) (\d+)$", cond)
    if m:
        return _eval_op(m.group(1), state.day_number, int(m.group(2)))
        
    m = re.match(r"^date (==|>=|<=) (\d{4}-\d{2}-\d{2})$", cond)
    if m:
        dt = date.fromisoformat(m.group(2))
        if m.group(1) == "==": return state.current_date == dt
        if m.group(1) == ">=": return state.current_date >= dt
        if m.group(1) == "<=": return state.current_date <= dt

    m = re.match(r"^time_slot == (morning|afternoon|evening)$", cond)
    if m:
        return state.current_time_slot == m.group(1)

    m = re.match(r"^location\.current == ([a-z][a-z0-9_]*)$", cond)
    if m:
        return state.current_location_id == m.group(1)

    m = re.match(r"^flag\.([a-z][a-z0-9_]*) == (true|false)$", cond)
    if m:
        fid = m.group(1)
        val = m.group(2) == "true"
        return state.flags.get(fid, False) == val

    m = re.match(r"^stat\.([A-Za-z]+) (==|>=|<=) (-?\d+)$", cond)
    if m:
        st = m.group(1)
        return _eval_op(m.group(2), state.stats.get(st, 0), int(m.group(3)))

    m = re.match(r"^character\.([a-z][a-z0-9_]*)\.favor (==|>=|<=) (-?\d+)$", cond)
    if m:
        cid = m.group(1)
        return _eval_op(m.group(2), state.character_favor.get(cid, 0), int(m.group(3)))

    m = re.match(r"^status\.([a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*) == (true|false)$", cond)
    if m:
        tid, sid = m.group(1), m.group(2)
        val = m.group(3) == "true"
        is_active = tid in state.active_statuses and sid in state.active_statuses[tid]
        return is_active == val

    return False

def _check_conditions(conds: list[str], state: WalkthroughState, setup: SetupPackage) -> bool:
    return all(_check_condition(c, state, setup) for c in conds)

def _advance_time(state: WalkthroughState, time_cost: int, setup: SetupPackage) -> None:
    world_ts = list(setup.world.time_slots)
    ts_idx = world_ts.index(state.current_time_slot)
    
    for _ in range(time_cost):
        # Time slot step
        ts_idx += 1
        
        # Advance status time_slots
        for tid, statuses in list(state.active_statuses.items()):
            for sid, status in list(statuses.items()):
                if status.remaining_time_slots is not None:
                    status.remaining_time_slots -= 1
                    if status.remaining_time_slots <= 0:
                        del statuses[sid]
            if not statuses:
                del state.active_statuses[tid]

        if ts_idx >= len(world_ts):
            ts_idx = 0
            state.current_date += timedelta(days=1)
            state.day_number += 1
            
            # Advance status days
            for tid, statuses in list(state.active_statuses.items()):
                for sid, status in list(statuses.items()):
                    if status.remaining_days is not None:
                        status.remaining_days -= 1
                        if status.remaining_days <= 0:
                            del statuses[sid]
                if not statuses:
                    del state.active_statuses[tid]

    state.current_time_slot = world_ts[ts_idx]

def _check_end_date(state: WalkthroughState, setup: SetupPackage) -> None:
    if setup.world.end_date and state.current_date > setup.world.end_date:
        if state.mode not in ("ending_reached", "dead_end"):
            state.mode = "dead_end"
            state.blocked_reason = "遊戲結束日已過，未達成任何結局。"

def enter_event(setup: SetupPackage, bp: EventBlueprint, state: WalkthroughState, event_id: str) -> None:
    ev = next((e for e in bp.events if e.event_id == event_id), None)
    if not ev:
        state.mode = "blocked"
        state.blocked_reason = f"找不到 event: {event_id}"
        return

    # Direct goto validation
    if ev.time_slot not in setup.world.time_slots:
        state.mode = "blocked"
        state.blocked_reason = f"Event time_slot invalid: {ev.time_slot}"
        return
        
    world_ts = list(setup.world.time_slots)
    
    if ev.time_slot != state.current_time_slot:
        state.mode = "blocked"
        state.blocked_reason = f"goto '{event_id}' time_slot mismatch. Expected {ev.time_slot}, got {state.current_time_slot}"
        return

    # Check location available
    if not is_location_available(setup, state, ev.location_id):
        state.mode = "blocked"
        state.blocked_reason = f"Location {ev.location_id} closed/locked for event {event_id}"
        return

    if not _check_conditions(ev.conditions, state, setup):
        state.mode = "blocked"
        state.blocked_reason = f"Conditions fail for event {event_id}"
        return

    # Repeat policy
    visits = state.event_visit_log.get(event_id, [])
    if ev.repeat_policy == "once" and visits:
        state.mode = "blocked"
        state.blocked_reason = f"Event {event_id} already visited (once)"
        return
    if ev.repeat_policy == "daily" and state.current_date in visits:
        state.mode = "blocked"
        state.blocked_reason = f"Event {event_id} already visited today (daily)"
        return

    state.mode = "in_event"
    state.current_event_id = event_id
    state.current_location_id = ev.location_id

def apply_choice(setup: SetupPackage, bp: EventBlueprint, state: WalkthroughState, event_id: str, choice_id: str, history: list[HistoryEntry]) -> None:
    ev = next((e for e in bp.events if e.event_id == event_id), None)
    if not ev:
        return
    ch = next((c for c in ev.choices if c.choice_id == choice_id), None)
    if not ch:
        return

    time_cost = ev.time_cost
    goto_target = None
    ending_id = None

    # Parse results
    for r in ch.result:
        r = r.strip()
        
        m = re.match(r"^flag\.([a-z][a-z0-9_]*) = (true|false)$", r)
        if m:
            state.flags[m.group(1)] = (m.group(2) == "true")
            continue

        m = re.match(r"^stat\.([A-Za-z]+) ([+\-])= (-?\d+)$", r)
        if m:
            st, op, val = m.group(1), m.group(2), int(m.group(3))
            state.stats[st] = state.stats.get(st, 0) + (val if op == "+" else -val)
            continue

        m = re.match(r"^character\.([a-z][a-z0-9_]*)\.favor ([+\-])= (-?\d+)$", r)
        if m:
            cid, op, val = m.group(1), m.group(2), int(m.group(3))
            state.character_favor[cid] = state.character_favor.get(cid, 0) + (val if op == "+" else -val)
            continue

        m = re.match(r"^status\.([a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*) = (true|false)$", r)
        if m:
            tid, sid, val = m.group(1), m.group(2), m.group(3) == "true"
            if val:
                # activate status
                sf = next((s for s in setup.status_flags if s.status_id == sid), None)
                if sf:
                    rt, rd = None, None
                    if sf.duration.type == "time_slots":
                        rt = sf.duration.value
                    elif sf.duration.type == "days":
                        rd = sf.duration.value
                    
                    if tid not in state.active_statuses:
                        state.active_statuses[tid] = {}
                    state.active_statuses[tid][sid] = ActiveStatus(
                        status_id=sid, target_id=tid, 
                        remaining_time_slots=rt, remaining_days=rd,
                        source_event_id=event_id
                    )
            else:
                # deactivate status
                if tid in state.active_statuses and sid in state.active_statuses[tid]:
                    del state.active_statuses[tid][sid]
                    if not state.active_statuses[tid]:
                        del state.active_statuses[tid]
            continue

        m = re.match(r"^time_cost: (\d+)$", r)
        if m:
            time_cost = int(m.group(1))
            continue

        m = re.match(r"^goto: ([a-z][a-z0-9_]*|free_roam)$", r)
        if m:
            goto_target = m.group(1)
            continue
            
        m = re.match(r"^ending: ([a-z][a-z0-9_]*)$", r)
        if m:
            ending_id = m.group(1)
            continue

    # Mark visit
    if event_id not in state.event_visit_log:
        state.event_visit_log[event_id] = []
    state.event_visit_log[event_id].append(state.current_date)

    if ending_id:
        history.append(HistoryEntry(
            kind="ending",
            date=state.current_date,
            time_slot=state.current_time_slot,
            ending_id=ending_id,
            effective_time_cost=time_cost
        ))
        _advance_time(state, time_cost, setup)
        state.mode = "ending_reached"
        state.current_event_id = None
        return

    history.append(HistoryEntry(
        kind="event_choice",
        date=state.current_date,
        time_slot=state.current_time_slot,
        location_id=state.current_location_id,
        event_id=event_id,
        choice_id=choice_id,
        effective_time_cost=time_cost
    ))

    _advance_time(state, time_cost, setup)
    _check_end_date(state, setup)
    if state.mode == "dead_end":
        return

    if goto_target == "free_roam":
        state.mode = "free_roam"
        state.current_event_id = None
        _check_free_roam_blocked(setup, bp, state)
    elif goto_target:
        enter_event(setup, bp, state, goto_target)

def apply_action(setup: SetupPackage, bp: EventBlueprint, state: WalkthroughState, action: Literal["rest", "wait"], history: list[HistoryEntry]) -> None:
    history.append(HistoryEntry(
        kind=action,
        date=state.current_date,
        time_slot=state.current_time_slot,
        location_id=state.current_location_id,
        effective_time_cost=1
    ))
    _advance_time(state, 1, setup)
    _check_end_date(state, setup)
    if state.mode == "dead_end":
        return
    _check_free_roam_blocked(setup, bp, state)

def is_location_available(setup: SetupPackage, state: WalkthroughState, location_id: str) -> bool:
    loc = next((l for l in setup.locations if l.location_id == location_id), None)
    if not loc:
        return False
    if state.current_time_slot not in loc.available_time_slots:
        return False
    
    # unlock_conditions (AND)
    if loc.unlock_conditions:
        if not _check_conditions(loc.unlock_conditions, state, setup):
            return False
            
    # closed_conditions (OR)
    if loc.closed_conditions:
        if any(_check_condition(c, state, setup) for c in loc.closed_conditions):
            return False
            
    return True

def get_choice_effective_time_cost(ev: BlueprintEvent, ch: BlueprintChoice) -> int:
    for r in ch.result:
        m = re.match(r"^time_cost: (\d+)$", r.strip())
        if m:
            return int(m.group(1))
    return ev.time_cost

def list_available_events(setup: SetupPackage, bp: EventBlueprint, state: WalkthroughState) -> dict[str, list[dict]]:
    # Returns location_id -> [ {event: BlueprintEvent, choices: [BlueprintChoice, ...]} ]
    if state.mode != "free_roam":
        return {}

    candidates = []
    world_ts = list(setup.world.time_slots)
    ts_idx = world_ts.index(state.current_time_slot)
    remaining_slots = len(world_ts) - ts_idx

    for ev in bp.events:
        if ev.time_slot != state.current_time_slot:
            continue
        if not is_location_available(setup, state, ev.location_id):
            continue
        if not _check_conditions(ev.conditions, state, setup):
            continue
        
        visits = state.event_visit_log.get(ev.event_id, [])
        if ev.repeat_policy == "once" and visits:
            continue
        if ev.repeat_policy == "daily" and state.current_date in visits:
            continue
            
        if ev.time_cost > remaining_slots:
            continue
            
        available_choices = []
        for ch in ev.choices:
            if get_choice_effective_time_cost(ev, ch) <= remaining_slots:
                available_choices.append(ch)
                
        if not available_choices:
            continue
            
        candidates.append({"event": ev, "choices": available_choices})

    # Filter by priority (critical blocks others)
    critical_cands = [c for c in candidates if c["event"].priority == "critical"]
    if critical_cands:
        candidates = critical_cands
        
    res = {}
    for c in candidates:
        loc = c["event"].location_id
        if loc not in res:
            res[loc] = []
        res[loc].append(c)
        
    return res

def list_available_actions(setup: SetupPackage, state: WalkthroughState) -> dict[str, list[str]]:
    # location_id -> ["rest", "wait"]
    res = {}
    world_ts = list(setup.world.time_slots)
    if state.current_time_slot not in world_ts:
        return res
        
    for loc in setup.locations:
        if not is_location_available(setup, state, loc.location_id):
            continue
        actions = []
        if loc.empty_behavior == "allow_rest":
            actions.append("rest")
        elif loc.empty_behavior == "allow_wait":
            actions.append("wait")
            
        if actions:
            res[loc.location_id] = actions
    return res

def _check_free_roam_blocked(setup: SetupPackage, bp: EventBlueprint, state: WalkthroughState) -> None:
    events = list_available_events(setup, bp, state)
    actions = list_available_actions(setup, state)
    if not events and not actions:
        state.mode = "blocked"
        state.blocked_reason = "目前沒有可執行的事件或行動，劇情邏輯可能有缺口。"
