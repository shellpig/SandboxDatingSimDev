import pytest
from datetime import date
from sandbox_dating_sim.walkthrough.blueprint_walkthrough import WalkthroughState, HistoryEntry
from sandbox_dating_sim.walkthrough.checkpoint import make_checkpoint, dump_checkpoint, load_checkpoint, Checkpoint

def test_checkpoint_save_and_load():
    state = WalkthroughState(
        mode="free_roam",
        current_date=date(2026, 5, 1),
        current_time_slot="morning",
        current_location_id="cafe",
        flags={"f1": True},
        stats={"INT": 10},
        character_favor={"npc1": 5},
        active_statuses={"protagonist": {"tired": {"status_id": "tired", "target_id": "protagonist"}}},
        event_visit_log={"ev1": [date(2026, 5, 1)]}
    )
    history = [
        HistoryEntry(kind="event_choice", date=date(2026, 5, 1), time_slot="morning", event_id="ev1", choice_id="ch1", effective_time_cost=1)
    ]
    
    cp = make_checkpoint(state, history, "world1", "bp1", "my save")
    assert cp.source_world_id == "world1"
    assert cp.label == "my save"
    
    yaml_str = dump_checkpoint(cp)
    
    cp2 = load_checkpoint(yaml_str)
    assert cp2.checkpoint_id == cp.checkpoint_id
    assert cp2.state.flags["f1"] is True
    assert cp2.state.character_favor["npc1"] == 5
    assert "tired" in cp2.state.active_statuses["protagonist"]
    assert cp2.history[0].kind == "event_choice"
    assert cp2.history[0].event_id == "ev1"
    
def test_checkpoint_optional_label():
    state = WalkthroughState(mode="ending_reached", current_date=date(2026, 5, 1), current_time_slot="morning", current_location_id="home")
    cp = make_checkpoint(state, [], "w1", "b1")
    assert cp.label is None
    yaml_str = dump_checkpoint(cp)
    assert "label:" not in yaml_str
    # If we exclude_none, it won't be there. That's fine, pydantic defaults it.
    
    cp2 = load_checkpoint(yaml_str)
    assert cp2.label is None
