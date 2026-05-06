from datetime import date
import pytest
from pathlib import Path

from sandbox_dating_sim.pipeline.setup_parser import SetupPackageParser
from sandbox_dating_sim.schema.blueprint import EventBlueprint
from sandbox_dating_sim.walkthrough.blueprint_walkthrough import (
    create_initial_walkthrough_state, enter_event, apply_choice, apply_action,
    list_available_events, WalkthroughState, HistoryEntry
)

@pytest.fixture
def dummy_setup():
    import yaml
    p = Path("tests/fixtures/setup_minimal.yaml")
    with open(p, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    from sandbox_dating_sim.schema.setup import SetupPackage
    return SetupPackage(**data)

@pytest.fixture
def dummy_blueprint(dummy_setup):
    world_id = dummy_setup.world.world_id
    # We create a valid blueprint based on setup_minimal
    return EventBlueprint.model_validate({
        "blueprint_id": f"{world_id}_event_blueprint",
        "source_world_id": world_id,
        "source_setup_package": f"{world_id}_setup_package.md",
        "initial_event_id": "ev_start",
        "events": [
            {
                "event_id": "ev_start",
                "title": "Start",
                "scene_summary": "sum",
                "location_id": "protagonist_home",
                "time_slot": dummy_setup.world.time_slots[0],
                "priority": "normal",
                "repeat_policy": "once",
                "route_tags": [],
                "conditions": [],
                "event_purpose": "Start",
                "cast": [],
                "expected_assets": {"backgrounds": [], "bgms": [], "characters": []},
                "time_cost": 1,
                "choices": [
                    {
                        "choice_id": "ch1",
                        "choice_label": "Go",
                        "choice_intent": "Go",
                        "result": ["goto: free_roam"]
                    }
                ]
            },
            {
                "event_id": "ev_end",
                "title": "End",
                "scene_summary": "sum",
                "location_id": "protagonist_home",
                "time_slot": dummy_setup.world.time_slots[0],
                "priority": "critical",
                "repeat_policy": "once",
                "route_tags": ["fallback_ending"],
                "conditions": [],
                "event_purpose": "End",
                "cast": [],
                "expected_assets": {"backgrounds": [], "bgms": [], "characters": []},
                "time_cost": 1,
                "choices": [
                    {
                        "choice_id": "ch1",
                        "choice_label": "End",
                        "choice_intent": "End",
                        "result": [f"ending: {dummy_setup.endings[0].ending_id}"]
                    }
                ]
            }
        ],
        "new_flags_proposed": []
    })

def test_walkthrough_engine(dummy_setup, dummy_blueprint):
    state = create_initial_walkthrough_state(dummy_setup, dummy_blueprint)
    assert state.mode == "free_roam"
    assert state.current_date == dummy_setup.world.start_date
    assert state.current_time_slot == dummy_setup.world.time_slots[0]
    assert state.current_location_id == "protagonist_home"

    enter_event(dummy_setup, dummy_blueprint, state, "ev_start")
    assert state.mode == "in_event"

    history = []
    apply_choice(dummy_setup, dummy_blueprint, state, "ev_start", "ch1", history)
    assert state.mode == "free_roam"
    assert state.current_time_slot != dummy_setup.world.time_slots[0] # advanced by 1

def test_checkpoint_and_graph(dummy_setup, dummy_blueprint):
    pass  # Moved to dedicated files

def test_engine_time_progression(dummy_setup, dummy_blueprint):
    # #4 time cost 2
    # #5 time cost full day
    # #6 insufficient time
    state = create_initial_walkthrough_state(dummy_setup, dummy_blueprint)
    
    # current time slot is morning (0)
    # let's change ev_start time_cost to 2
    dummy_blueprint.events[0].time_cost = 2
    enter_event(dummy_setup, dummy_blueprint, state, "ev_start")
    history = []
    apply_choice(dummy_setup, dummy_blueprint, state, "ev_start", "ch1", history)
    
    assert state.current_time_slot == "evening" # morning + 2 = evening
    assert state.current_date == dummy_setup.world.start_date
    
    # let's advance 1 more to test cross-day
    # evening + 1 = next day morning
    apply_action(dummy_setup, dummy_blueprint, state, "rest", history)
    
    from datetime import timedelta
    assert state.current_date == dummy_setup.world.start_date + timedelta(days=1)
    assert state.current_time_slot == "morning"
    
    # #6 insufficient time
    # ev_end time_cost is 1. If we are at evening, and cost is 2, it shouldn't show up.
    dummy_blueprint.events[1].time_cost = 2
    dummy_blueprint.events[1].time_slot = "evening"
    state.current_time_slot = "evening"
    avail = list_available_events(dummy_setup, dummy_blueprint, state)
    assert "protagonist_home" not in avail

def test_engine_choice_override_time(dummy_setup, dummy_blueprint):
    state = create_initial_walkthrough_state(dummy_setup, dummy_blueprint)
    dummy_blueprint.events[0].choices[0].result.append("time_cost: 3")
    history = []
    enter_event(dummy_setup, dummy_blueprint, state, "ev_start")
    apply_choice(dummy_setup, dummy_blueprint, state, "ev_start", "ch1", history)
    
    # morning + 3 = next day morning
    from datetime import timedelta
    assert state.current_date == dummy_setup.world.start_date + timedelta(days=1)
    assert state.current_time_slot == "morning"

def test_engine_state_deltas(dummy_setup, dummy_blueprint):
    state = create_initial_walkthrough_state(dummy_setup, dummy_blueprint)
    dummy_blueprint.events[0].choices[0].result.extend([
        "flag.some_flag = true",
        "stat.Cash -= 100",
        "character.sophie.favor += 5"
    ])
    history = []
    enter_event(dummy_setup, dummy_blueprint, state, "ev_start")
    apply_choice(dummy_setup, dummy_blueprint, state, "ev_start", "ch1", history)
    
    assert state.flags.get("some_flag") is True
    assert state.stats.get("Cash", 0) == 2900 # 3000 - 100
    assert state.character_favor.get("sophie", 0) == 5

def test_engine_status_duration(dummy_setup, dummy_blueprint):
    from sandbox_dating_sim.schema.setup import StatusFlag
    dummy_setup.status_flags.append(StatusFlag.model_validate({
        "status_id": "tired",
        "label": "Tired",
        "description": "desc",
        "targets": ["protagonist"],
        "duration": {"type": "time_slots", "value": 2},
        "effect": [],
        "clear_rule": ["manual_only"]
    }))
    dummy_setup.status_flags.append(StatusFlag.model_validate({
        "status_id": "sick",
        "label": "Sick",
        "description": "desc",
        "targets": ["protagonist"],
        "duration": {"type": "days", "value": 1},
        "effect": [],
        "clear_rule": ["manual_only"]
    }))
    
    state = create_initial_walkthrough_state(dummy_setup, dummy_blueprint)
    dummy_blueprint.events[0].choices[0].result.extend([
        "status.protagonist.tired = true",
        "status.protagonist.sick = true"
    ])
    history = []
    enter_event(dummy_setup, dummy_blueprint, state, "ev_start")
    apply_choice(dummy_setup, dummy_blueprint, state, "ev_start", "ch1", history)
    
    # After event, advanced 1 time slot. tired remaining = 1, sick remaining = 1
    assert "tired" in state.active_statuses["protagonist"]
    assert state.active_statuses["protagonist"]["tired"].remaining_time_slots == 1
    assert "sick" in state.active_statuses["protagonist"]
    
    # Advance another slot
    apply_action(dummy_setup, dummy_blueprint, state, "wait", history)
    # tired remaining = 0 -> removed!
    assert "tired" not in state.active_statuses["protagonist"]
    assert "sick" in state.active_statuses["protagonist"]
    
    # Advance to next day
    apply_action(dummy_setup, dummy_blueprint, state, "wait", history)
    assert "protagonist" not in state.active_statuses # sick removed and protagonist dict removed

def test_engine_location_conditions(dummy_setup, dummy_blueprint):
    dummy_setup.locations[1].is_visitable = True
    dummy_setup.locations[1].unlock_conditions = ["flag.unlocked == true", "stat.Cash >= 100"]
    dummy_setup.locations[1].closed_conditions = ["flag.banned == true"]
    
    state = create_initial_walkthrough_state(dummy_setup, dummy_blueprint)
    state.flags["unlocked"] = True
    state.flags["banned"] = False
    
    from sandbox_dating_sim.walkthrough.blueprint_walkthrough import is_location_available
    assert is_location_available(dummy_setup, state, dummy_setup.locations[1].location_id)
    
    state.flags["banned"] = True
    assert not is_location_available(dummy_setup, state, dummy_setup.locations[1].location_id)

def test_engine_repeat_policy(dummy_setup, dummy_blueprint):
    state = create_initial_walkthrough_state(dummy_setup, dummy_blueprint)
    
    # 1. repeat once
    dummy_blueprint.events[0].repeat_policy = "once"
    history = []
    enter_event(dummy_setup, dummy_blueprint, state, "ev_start")
    apply_choice(dummy_setup, dummy_blueprint, state, "ev_start", "ch1", history)
    
    # try to re-enter
    state.current_time_slot = "morning"
    enter_event(dummy_setup, dummy_blueprint, state, "ev_start")
    assert state.mode == "blocked"
    assert "visited (once)" in state.blocked_reason
    
    # 2. repeat daily
    state = create_initial_walkthrough_state(dummy_setup, dummy_blueprint)
    dummy_blueprint.events[0].repeat_policy = "daily"
    enter_event(dummy_setup, dummy_blueprint, state, "ev_start")
    apply_choice(dummy_setup, dummy_blueprint, state, "ev_start", "ch1", history)
    
    state.current_time_slot = "morning"
    enter_event(dummy_setup, dummy_blueprint, state, "ev_start")
    assert state.mode == "blocked"
    assert "visited today (daily)" in state.blocked_reason

def test_engine_critical_events(dummy_setup, dummy_blueprint):
    state = create_initial_walkthrough_state(dummy_setup, dummy_blueprint)
    
    dummy_blueprint.events.append(dummy_blueprint.events[0].model_copy(deep=True))
    dummy_blueprint.events[-1].event_id = "ev_crit"
    dummy_blueprint.events[-1].priority = "critical"
    
    avail = list_available_events(dummy_setup, dummy_blueprint, state)
    
    # ev_end is also critical, so there are 2 critical events
    assert len(avail["protagonist_home"]) == 2
    assert any(e["event"].event_id == "ev_crit" for e in avail["protagonist_home"])
    
    # multiple critical
    dummy_blueprint.events.append(dummy_blueprint.events[-1].model_copy(deep=True))
    dummy_blueprint.events[-1].event_id = "ev_crit2"
    
    avail = list_available_events(dummy_setup, dummy_blueprint, state)
    assert len(avail["protagonist_home"]) == 3

def test_engine_dead_end_and_blocked(dummy_setup, dummy_blueprint):
    state = create_initial_walkthrough_state(dummy_setup, dummy_blueprint)
    # Jump date past end_date
    from datetime import timedelta
    state.current_date = dummy_setup.world.end_date + timedelta(days=1)
    
    history = []
    apply_action(dummy_setup, dummy_blueprint, state, "wait", history)
    assert state.mode == "dead_end"
    
    # Check blocked
    state = create_initial_walkthrough_state(dummy_setup, dummy_blueprint)
    dummy_blueprint.events[1].conditions = ["flag.impossible == true"]
    enter_event(dummy_setup, dummy_blueprint, state, dummy_blueprint.events[1].event_id)
    assert state.mode == "blocked"
    
    # Blocked by free_roam having nothing
    state = create_initial_walkthrough_state(dummy_setup, dummy_blueprint)
    dummy_setup.locations.clear()
    dummy_blueprint.events.clear()
    history = []
    apply_action(dummy_setup, dummy_blueprint, state, "wait", history)
    assert state.mode == "blocked"

