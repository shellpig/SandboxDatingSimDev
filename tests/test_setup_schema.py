import pytest
import yaml
from pathlib import Path
from pydantic import ValidationError
from sandbox_dating_sim.schema.setup import SetupPackage, Character, StatusFlag, ScheduleEntry

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def load_yaml(filename: str) -> dict:
    with open(FIXTURES_DIR / filename, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def test_minimal_setup_package_loads():
    """fixture setup_minimal.yaml 可載入為 SetupPackage。"""
    data = load_yaml("setup_minimal.yaml")
    pkg = SetupPackage(**data)
    assert pkg.world.world_id == "summer_city_2026"
    assert pkg.protagonist.name == "佑介"
    assert pkg.uiw_version == "1.2"

def test_schema_rejects_missing_required_fields():
    """測試 setup_invalid_missing_required.yaml 應該被拒絕"""
    data = load_yaml("setup_invalid_missing_required.yaml")
    with pytest.raises(ValidationError):
        SetupPackage(**data)

def test_character_requires_character_id():
    """角色缺 character_id 時 Pydantic validation fail。"""
    with pytest.raises(ValidationError, match="character_id"):
        Character(
            display_name="蘇菲",
            gender="female",
            orientation=["male"],
            role="main_love_interest",
            identity="classmate",
            personality_tags=["shy"],
            allowed_emotions=[],
            allowed_costumes=[],
            allowed_positions=[]
        )

def test_status_flag_requires_duration_and_clear_rule():
    """status flag 缺 duration 或 clear_rule 時 validation fail。"""
    with pytest.raises(ValidationError, match="duration"):
        StatusFlag(
            status_id="tired",
            label="疲勞",
            target="protagonist",
            effect=["-10 CHA"],
            clear_rule=["sleep"],
            description="tired"
        )
    with pytest.raises(ValidationError, match="clear_rule"):
        StatusFlag(
            status_id="tired",
            label="疲勞",
            target="protagonist",
            effect=["-10 CHA"],
            duration={"type": "days", "value": 1},
            description="tired"
        )

def test_schedule_requires_schedule_order():
    """schedule 缺 schedule_order 時 validation fail。"""
    with pytest.raises(ValidationError, match="schedule_order"):
        ScheduleEntry(
            schedule_id="sch_001",
            day_type="weekday",
            time_slot="morning",
            location_id="school"
        )
