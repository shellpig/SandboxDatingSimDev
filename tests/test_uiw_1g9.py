import pytest
from datetime import date
from unittest.mock import patch, MagicMock

import streamlit as st
if not hasattr(st, "session_state") or st.session_state is None:
    st.session_state = {}

from sandbox_dating_sim.schema.setup import ScheduleEntry, SetupPackage, World, Character, Protagonist, InitialStats, SemanticChoice
from sandbox_dating_sim.uiw.linter import UIWLinter
from sandbox_dating_sim.ui.streamlit_uiw import _collect_existing_ids, _tab_characters

def test_1g9_schema_specific_date():
    # 合法 cases
    s1 = ScheduleEntry(schedule_id="s1", day_type="specific_date", time_slot="morning", location_id="loc", specific_date=date(2026, 5, 1), schedule_order=10)
    assert s1.specific_date == date(2026, 5, 1)

    s2 = ScheduleEntry(schedule_id="s2", day_type="weekday", time_slot="morning", location_id="loc", specific_date=None, schedule_order=10)
    assert s2.specific_date is None

    s3 = ScheduleEntry(schedule_id="s3", day_type="weekday", time_slot="morning", location_id="loc", schedule_order=10)
    assert s3.specific_date is None

def test_1g9_linter_specific_date():
    linter = UIWLinter()
    pkg = SetupPackage(
        world=World(world_id="w1", title="w1", start_date=date(2026, 5, 1), end_date=date(2026, 5, 30), time_slots=["morning", "afternoon"]),
        protagonist=Protagonist(name="P", gender="male", age=18, occupation=SemanticChoice(id="stu", label="s"), initial_stats=InitialStats(INT=1, CHA=1, STR=1, MORAL=1, Cash=0), personality=SemanticChoice(id="p", label="p")),
        locations=[], characters=[
            Character(
                character_id="c1", display_name="C", gender="male", orientation=[], role="main", identity="", personality_tags=[], secrets=[], allowed_emotions=[], allowed_costumes=[], allowed_positions=[],
                schedule=[]
            )
        ]
    )

    def check_sch(sch):
        pkg.characters[0].schedule = [sch]
        return linter._check_schedules(pkg)

    # missing_specific_date
    sch = ScheduleEntry(schedule_id="s1", day_type="specific_date", time_slot="morning", location_id="loc", specific_date=None, schedule_order=1)
    issues = check_sch(sch)
    assert any(i.type == "missing_specific_date" for i in issues)

    # unexpected_specific_date
    sch = ScheduleEntry(schedule_id="s1", day_type="weekday", time_slot="morning", location_id="loc", specific_date=date(2026, 5, 5), schedule_order=1)
    issues = check_sch(sch)
    assert any(i.type == "unexpected_specific_date" for i in issues)

    # specific_date_out_of_range
    sch = ScheduleEntry(schedule_id="s1", day_type="specific_date", time_slot="morning", location_id="loc", specific_date=date(2026, 4, 30), schedule_order=1)
    issues = check_sch(sch)
    assert any(i.type == "specific_date_out_of_range" for i in issues)

    sch = ScheduleEntry(schedule_id="s1", day_type="specific_date", time_slot="morning", location_id="loc", specific_date=date(2026, 5, 31), schedule_order=1)
    issues = check_sch(sch)
    assert any(i.type == "specific_date_out_of_range" for i in issues)

    # specific_date boundaries
    sch = ScheduleEntry(schedule_id="s1", day_type="specific_date", time_slot="morning", location_id="loc", specific_date=date(2026, 5, 1), schedule_order=1)
    issues = check_sch(sch)
    assert not any(i.type == "specific_date_out_of_range" for i in issues)
    assert not any(i.type == "missing_specific_date" for i in issues)

    sch = ScheduleEntry(schedule_id="s1", day_type="specific_date", time_slot="morning", location_id="loc", specific_date=date(2026, 5, 30), schedule_order=1)
    issues = check_sch(sch)
    assert not any(i.type == "specific_date_out_of_range" for i in issues)

def test_1g9_linter_schedule_ids_and_tie():
    linter = UIWLinter()
    pkg = SetupPackage(
        world=World(world_id="w1", title="w1", start_date=date(2026, 5, 1), end_date=date(2026, 5, 30), time_slots=["morning", "afternoon"]),
        protagonist=Protagonist(name="P", gender="male", age=18, occupation=SemanticChoice(id="stu", label="s"), initial_stats=InitialStats(INT=1, CHA=1, STR=1, MORAL=1, Cash=0), personality=SemanticChoice(id="p", label="p")),
        locations=[], characters=[
            Character(
                character_id="c1", display_name="C", gender="male", orientation=[], role="main", identity="", personality_tags=[], secrets=[], allowed_emotions=[], allowed_costumes=[], allowed_positions=[],
                schedule=[]
            )
        ]
    )

    # schedule_id invalid format
    pkg.characters[0].schedule = [ScheduleEntry(schedule_id="bad-id", day_type="weekday", time_slot="morning", location_id="loc", schedule_order=1)]
    issues = linter._check_ids(pkg)
    assert any(i.type == "invalid_id_format" and "schedule_id" in i.path for i in issues), f"Issues: {[i.model_dump() for i in issues]}"

    # schedule_id duplicate (with world_id)
    pkg.characters[0].schedule = [ScheduleEntry(schedule_id="w1", day_type="weekday", time_slot="morning", location_id="loc", schedule_order=1)]
    issues = linter._check_ids(pkg)
    assert any(i.type == "duplicate_id" and "schedule_id" in i.path for i in issues), f"Issues: {[i.model_dump() for i in issues]}"

    # schedule_id duplicate within schedules
    pkg.characters[0].schedule = [
        ScheduleEntry(schedule_id="s1", day_type="weekday", time_slot="morning", location_id="loc", schedule_order=1),
        ScheduleEntry(schedule_id="s1", day_type="weekend", time_slot="morning", location_id="loc", schedule_order=2)
    ]
    issues = linter._check_ids(pkg)
    assert any(i.type == "duplicate_id" and "schedule_id" in i.path for i in issues), f"Issues: {[i.model_dump() for i in issues]}"

    # tie different dates
    pkg.characters[0].schedule = [
        ScheduleEntry(schedule_id="s1", day_type="specific_date", specific_date=date(2026, 5, 1), time_slot="morning", location_id="loc", schedule_order=10),
        ScheduleEntry(schedule_id="s2", day_type="specific_date", specific_date=date(2026, 5, 2), time_slot="morning", location_id="loc", schedule_order=10)
    ]
    issues = linter._check_schedules(pkg)
    assert not any(i.type == "schedule_tie" for i in issues)

    # tie same dates
    pkg.characters[0].schedule = [
        ScheduleEntry(schedule_id="s1", day_type="specific_date", specific_date=date(2026, 5, 1), time_slot="morning", location_id="loc", schedule_order=10),
        ScheduleEntry(schedule_id="s2", day_type="specific_date", specific_date=date(2026, 5, 1), time_slot="morning", location_id="loc", schedule_order=10)
    ]
    issues = linter._check_schedules(pkg)
    assert any(i.type == "schedule_tie" for i in issues)


def test_1g9_collect_existing_ids():
    st.session_state.clear()
    st.session_state.update({
        "world_id": "w1",
        "characters": [
            {"character_id": "c1", "schedule": [{"schedule_id": "s1"}, {"schedule_id": "s2"}]}
        ],
        "locations": [{"location_id": "l1"}],
        "flags": [{"flag_id": "f1"}],
        "status_flags": [{"status_id": "sf1"}],
        "endings": [{"ending_id": "e1"}],
    })
    ids = _collect_existing_ids()
    assert "protagonist" in ids
    assert "w1" in ids
    assert "c1" in ids
    assert "s1" in ids
    assert "s2" in ids
    assert "l1" in ids
    assert "f1" in ids
    assert "sf1" in ids
    assert "e1" in ids

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g9_add_schedule_ui_stale_date_and_auto_id(mock_st):
    mock_st.session_state = {
        "start_date": date(2026, 4, 27),
        "end_date": date(2026, 5, 26),
        "world_id": "w1",
        "locations": [{"location_id": "l1", "name": "L1", "location_type": "standalone", "is_visitable": True}],
        "characters": [
            {
                "character_id": "c1", "display_name": "C1", "gender": "male", "role": "main", "identity": "", 
                "personality_tags": [], "secrets": [], "allowed_emotions": [], "allowed_costumes": [], "allowed_positions": [],
                "schedule": [
                    {"schedule_id": "sch_c1_weekday_morning", "day_type": "weekday", "time_slot": "morning", "location_id": "l1", "priority": "normal", "schedule_order": 10, "condition": []}
                ]
            }
        ]
    }
    
    mock_st.columns.side_effect = lambda x, **kwargs: [MagicMock() for _ in range(len(x))] if isinstance(x, list) else [MagicMock() for _ in range(x)]
    mock_st.checkbox.return_value = False
    
    mock_st.text_input.return_value = ""
    mock_st.number_input.return_value = 20
    
    def mock_selectbox(label, options, *args, **kwargs):
        if options:
            return options[0]
        return None
    mock_st.selectbox.side_effect = mock_selectbox
    
    mock_st.date_input.return_value = date(2026, 5, 10)
    
    # We submit the "新增行程" button
    def mock_button(label=None, *args, **kwargs):
        if kwargs.get("key") == "btn_add_sch_c1":
            return True
        return False
    mock_st.button.side_effect = mock_button

    _tab_characters()
    
    # Check if a schedule was added
    schedules = mock_st.session_state["characters"][0]["schedule"]
    assert len(schedules) == 2, f"Failed to add schedule. Errors: {mock_st.error.call_args_list}"
    
    new_sch = schedules[1]
    assert new_sch["schedule_id"] == "sch_c1_weekday_morning_2" # auto id suffix avoidance
    assert new_sch["day_type"] == "weekday"
    assert new_sch.get("specific_date") is None # stale date cleared or None
