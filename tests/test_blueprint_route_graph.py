import pytest
from sandbox_dating_sim.schema.blueprint import EventBlueprint
from sandbox_dating_sim.walkthrough.route_graph import build_route_graph

def test_route_graph_edges():
    bp = EventBlueprint.model_validate({
        "blueprint_id": "bp1",
        "source_world_id": "w1",
        "source_setup_package": "sp.md",
        "initial_event_id": "ev1",
        "events": [
            {
                "event_id": "ev1",
                "title": "Start",
                "scene_summary": "sum",
                "location_id": "home",
                "time_slot": "morning",
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
                    },
                    {
                        "choice_id": "ch2",
                        "choice_label": "Direct Go",
                        "choice_intent": "Go",
                        "result": ["goto: ev2"]
                    }
                ]
            },
            {
                "event_id": "ev2",
                "title": "Very Long Event Title To See If It Will Break Something",
                "scene_summary": "sum",
                "location_id": "home",
                "time_slot": "afternoon",
                "priority": "normal",
                "repeat_policy": "once",
                "route_tags": [],
                "conditions": [],
                "event_purpose": "Next",
                "cast": [],
                "expected_assets": {"backgrounds": [], "bgms": [], "characters": []},
                "time_cost": 1,
                "choices": [
                    {
                        "choice_id": "ch1",
                        "choice_label": "A very very long choice label that should be truncated by the graph builder",
                        "choice_intent": "End",
                        "result": ["ending: end1"]
                    }
                ]
            }
        ],
        "new_flags_proposed": []
    })
    
    graph = build_route_graph(bp)
    
    # 1. generated
    assert "```mermaid" in graph
    assert "### Adjacency Summary" in graph
    
    # 2. goto event edge
    assert 'ev1 -- "Direct Go" --> ev2' in graph
    
    # 3. goto free_roam edge
    assert 'ev1 -- "Go" --> free_roam' in graph
    
    # 4. ending edge
    # The label should be truncated to 20 chars + ...
    label = "A very very long choice label that should be truncated by the graph builder"
    trunc = label[:20] + "..."
    assert f'ev2 -- "{trunc}" --> end1' in graph
    assert 'end1("end1")' in graph
    
    # 5. no free_roam outgoing
    assert "free_roam --" not in graph
    assert "free_roam -->" not in graph
    
    # 7. adjacency summary choice_id + label
    assert "[ch1] Go -> goto: free_roam" in graph
    assert "[ch2] Direct Go -> goto: ev2" in graph
    assert f"[ch1] {label} -> ending: end1" in graph
