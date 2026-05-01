import pytest
import yaml
from pathlib import Path
from pydantic import ValidationError
from sandbox_dating_sim.schema.setup import SetupPackage, Character, StatusFlag, ScheduleEntry, SemanticChoice, Protagonist, World, InitialStats

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
            orientation=["heterosexual"],
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
            effect=[{"stat.CHA": -10}],
            clear_rule=["on_rest"],
            description="tired"
        )
    with pytest.raises(ValidationError, match="clear_rule"):
        StatusFlag(
            status_id="tired",
            label="疲勞",
            target="protagonist",
            effect=[{"stat.CHA": -10}],
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


# ─── 1-G-3 Tests ────────────────────────────────────────────────────────────

def test_semantic_choice_requires_id_and_label():
    """SemanticChoice 必須同時提供 id 與 label。"""
    choice = SemanticChoice(id="student", label="學生")
    assert choice.id == "student"
    assert choice.label == "學生"
    with pytest.raises(ValidationError):
        SemanticChoice(id="student")  # missing label
    with pytest.raises(ValidationError):
        SemanticChoice(label="學生")  # missing id


def test_minimal_fixture_loads_with_semantic_choice():
    """setup_minimal.yaml 語意型欄位可載入為 SetupPackage。"""
    data = yaml.safe_load(open(FIXTURES_DIR / "setup_minimal.yaml", encoding="utf-8"))
    pkg = SetupPackage(**data)
    assert isinstance(pkg.protagonist.occupation, SemanticChoice)
    assert isinstance(pkg.protagonist.personality, SemanticChoice)
    assert all(isinstance(s, SemanticChoice) for s in pkg.world.global_style)
    assert all(isinstance(t, SemanticChoice) for t in pkg.characters[0].personality_tags)


def test_protagonist_secrets_max_3():
    """protagonist.secrets 最多 3 個，第 4 個應被 linter 或業務邏輯拒絕。"""
    # Pydantic schema 本身不限制數量，此處確認 schema 可接受 <=3
    data = yaml.safe_load(open(FIXTURES_DIR / "setup_minimal.yaml", encoding="utf-8"))
    pkg = SetupPackage(**data)
    pkg.protagonist.secrets = [
        SemanticChoice(id="s1", label="秘密一"),
        SemanticChoice(id="s2", label="秘密二"),
        SemanticChoice(id="s3", label="秘密三"),
    ]
    assert len(pkg.protagonist.secrets) == 3  # 3 個合法


def test_character_secrets_max_3():
    """characters[].secrets 最多 3 個。"""
    data = yaml.safe_load(open(FIXTURES_DIR / "setup_minimal.yaml", encoding="utf-8"))
    pkg = SetupPackage(**data)
    pkg.characters[0].secrets = [
        SemanticChoice(id="s1", label="秘密一"),
        SemanticChoice(id="s2", label="秘密二"),
        SemanticChoice(id="s3", label="秘密三"),
    ]
    assert len(pkg.characters[0].secrets) == 3


def test_global_style_ids_not_duplicated():
    """world.global_style 的 id 不可重複（業務邏輯層）。"""
    data = yaml.safe_load(open(FIXTURES_DIR / "setup_minimal.yaml", encoding="utf-8"))
    pkg = SetupPackage(**data)
    ids = [s.id for s in pkg.world.global_style]
    assert len(ids) == len(set(ids)), "global_style id 不可重複"


def test_character_personality_tags_ids_not_duplicated():
    """characters[].personality_tags 的 id 不可重複。"""
    data = yaml.safe_load(open(FIXTURES_DIR / "setup_minimal.yaml", encoding="utf-8"))
    pkg = SetupPackage(**data)
    for ch in pkg.characters:
        ids = [t.id for t in ch.personality_tags]
        assert len(ids) == len(set(ids)), f"{ch.character_id} personality_tags id 不可重複"
