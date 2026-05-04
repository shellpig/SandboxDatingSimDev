"""Phase 2-A Event Blueprint Schema 測試。

依測試指南 2-A 必測項目 #1-#11。
"""

import re
import pytest
import yaml
from pathlib import Path
from pydantic import ValidationError

from sandbox_dating_sim.schema.blueprint import (
    EventBlueprint,
    BlueprintEvent,
    BlueprintChoice,
    ExpectedAssets,
    ExpectedCharacterAsset,
    BlueprintPriority,
    RepeatPolicy,
)
from sandbox_dating_sim.schema.setup import FlagDef

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_yaml_block(md_text: str) -> str:
    """從 Markdown 中取出第一個 yaml / yml fenced code block。"""
    match = re.search(r"```(?:yaml|yml)\n(.*?)```", md_text, re.DOTALL)
    if not match:
        raise ValueError("找不到 YAML code block")
    return match.group(1)


def _load_blueprint_md(path: Path) -> EventBlueprint:
    text = path.read_text(encoding="utf-8")
    raw = _extract_yaml_block(text)
    data = yaml.safe_load(raw)
    return EventBlueprint(**data)


def _minimal_choice(**kw) -> dict:
    base = {
        "choice_id": "c1",
        "choice_label": "選項一",
        "choice_intent": "測試選項",
        "result": ["goto: free_roam"],
    }
    base.update(kw)
    return base


def _minimal_event(**kw) -> dict:
    base = {
        "event_id": "ev1",
        "title": "測試事件",
        "scene_summary": "場景摘要。",
        "location_id": "protagonist_home",
        "time_slot": "morning",
        "priority": "main",
        "repeat_policy": "once",
        "route_tags": [],
        "conditions": [],
        "event_purpose": "測試目的。",
        "cast": [],
        "expected_assets": {"background": None, "bgm": None, "characters": []},
        "choices": [_minimal_choice()],
        "time_cost": 1,
    }
    base.update(kw)
    return base


def _minimal_blueprint(**kw) -> dict:
    base = {
        "blueprint_id": "test_world_event_blueprint",
        "source_world_id": "test_world",
        "source_setup_package": "test_world_setup_package.md",
        "initial_event_id": "ev1",
        "events": [_minimal_event()],
        "new_flags_proposed": [],
    }
    base.update(kw)
    return base


# ---------------------------------------------------------------------------
# #1: minimal blueprint valid
# ---------------------------------------------------------------------------

def test_minimal_blueprint_valid_from_fixture():
    """#1: 載入最小合法 fixture，建成 EventBlueprint。"""
    bp = _load_blueprint_md(FIXTURES_DIR / "blueprint_minimal.md")
    assert isinstance(bp, EventBlueprint)
    assert bp.blueprint_id == "summer_city_2026_event_blueprint"
    assert bp.initial_event_id == "opening_morning"
    assert len(bp.events) == 1


def test_minimal_blueprint_valid_from_dict():
    """#1 (dict 版): 最小合法 dict 可建成 EventBlueprint。"""
    bp = EventBlueprint(**_minimal_blueprint())
    assert bp.source_world_id == "test_world"
    assert len(bp.events) == 1
    assert bp.events[0].time_cost == 1


# ---------------------------------------------------------------------------
# #2: top-level required fields
# ---------------------------------------------------------------------------

def test_missing_blueprint_id():
    """#2a: 缺 blueprint_id 應報 ValidationError。"""
    data = _minimal_blueprint()
    del data["blueprint_id"]
    with pytest.raises(ValidationError):
        EventBlueprint(**data)


def test_missing_source_world_id():
    """#2b: 缺 source_world_id 應報 ValidationError。"""
    data = _minimal_blueprint()
    del data["source_world_id"]
    with pytest.raises(ValidationError):
        EventBlueprint(**data)


def test_missing_initial_event_id():
    """#2c: 缺 initial_event_id 應報 ValidationError。"""
    data = _minimal_blueprint()
    del data["initial_event_id"]
    with pytest.raises(ValidationError):
        EventBlueprint(**data)


# ---------------------------------------------------------------------------
# #3: blueprint_id field accepted by schema
# ---------------------------------------------------------------------------

def test_blueprint_id_accepted():
    """#3: blueprint_id 任意合法字串 schema 均接受（full linter 再檢查命名規則）。"""
    bp = EventBlueprint(**_minimal_blueprint(blueprint_id="any_id"))
    assert bp.blueprint_id == "any_id"


# ---------------------------------------------------------------------------
# #4: choice_label required
# ---------------------------------------------------------------------------

def test_missing_choice_label():
    """#4: 缺 choice_label 應報 ValidationError。"""
    choice = _minimal_choice()
    del choice["choice_label"]
    event = _minimal_event(choices=[choice])
    data = _minimal_blueprint(events=[event])
    with pytest.raises(ValidationError):
        EventBlueprint(**data)


# ---------------------------------------------------------------------------
# #5: scene_summary required
# ---------------------------------------------------------------------------

def test_missing_scene_summary():
    """#5: 缺 scene_summary 應報 ValidationError。"""
    event = _minimal_event()
    del event["scene_summary"]
    data = _minimal_blueprint(events=[event])
    with pytest.raises(ValidationError):
        EventBlueprint(**data)


# ---------------------------------------------------------------------------
# #6: choices min / max
# ---------------------------------------------------------------------------

def test_choices_zero():
    """#6a: 0 個 choices 應報 ValidationError（min_length=1）。"""
    event = _minimal_event(choices=[])
    data = _minimal_blueprint(events=[event])
    with pytest.raises(ValidationError):
        EventBlueprint(**data)


def test_choices_five():
    """#6b: 5 個 choices 應報 ValidationError（max_length=4）。"""
    choices = [_minimal_choice(**{"choice_id": f"c{i}"}) for i in range(5)]
    event = _minimal_event(choices=choices)
    data = _minimal_blueprint(events=[event])
    with pytest.raises(ValidationError):
        EventBlueprint(**data)


def test_choices_four_ok():
    """#6c: 4 個 choices 合法。"""
    choices = [_minimal_choice(**{"choice_id": f"c{i}"}) for i in range(4)]
    event = _minimal_event(choices=choices)
    data = _minimal_blueprint(events=[event])
    bp = EventBlueprint(**data)
    assert len(bp.events[0].choices) == 4


# ---------------------------------------------------------------------------
# #7: priority literal
# ---------------------------------------------------------------------------

def test_invalid_priority():
    """#7: priority='important' 不在 Literal 中，應報 ValidationError。"""
    event = _minimal_event(priority="important")
    data = _minimal_blueprint(events=[event])
    with pytest.raises(ValidationError):
        EventBlueprint(**data)


def test_valid_priorities():
    """#7: 所有合法 priority 值均通過。"""
    for prio in ("critical", "main", "route", "normal", "ambient"):
        event = _minimal_event(priority=prio)
        data = _minimal_blueprint(events=[event])
        bp = EventBlueprint(**data)
        assert bp.events[0].priority == prio


# ---------------------------------------------------------------------------
# #8: repeat_policy literal
# ---------------------------------------------------------------------------

def test_invalid_repeat_policy():
    """#8: repeat_policy='always' 不在 Literal 中，應報 ValidationError。"""
    event = _minimal_event(repeat_policy="always")
    data = _minimal_blueprint(events=[event])
    with pytest.raises(ValidationError):
        EventBlueprint(**data)


def test_valid_repeat_policies():
    """#8: once / daily 均合法。"""
    for rp in ("once", "daily"):
        event = _minimal_event(repeat_policy=rp)
        data = _minimal_blueprint(events=[event])
        bp = EventBlueprint(**data)
        assert bp.events[0].repeat_policy == rp


# ---------------------------------------------------------------------------
# #9: expected_assets
# ---------------------------------------------------------------------------

def test_expected_assets_explicit_ok():
    """#9: expected_assets 顯式出現（含空內容）時 valid。"""
    event = _minimal_event(expected_assets={"background": None, "bgm": None, "characters": []})
    data = _minimal_blueprint(events=[event])
    bp = EventBlueprint(**data)
    ea = bp.events[0].expected_assets
    assert ea.background is None
    assert ea.characters == []


def test_expected_assets_with_character():
    """#9: expected_assets 含角色素材時 valid。"""
    assets = {
        "background": "school_library_day",
        "bgm": "soft_piano",
        "characters": [
            {"character_id": "sophie", "costume": "school_uniform", "emotion": "happy", "position": "right"}
        ],
    }
    event = _minimal_event(expected_assets=assets)
    data = _minimal_blueprint(events=[event])
    bp = EventBlueprint(**data)
    assert bp.events[0].expected_assets.characters[0].character_id == "sophie"


# ---------------------------------------------------------------------------
# #10: time_cost positive
# ---------------------------------------------------------------------------

def test_time_cost_zero():
    """#10: time_cost=0 應報 ValidationError（Field(gt=0)）。"""
    event = _minimal_event(time_cost=0)
    data = _minimal_blueprint(events=[event])
    with pytest.raises(ValidationError):
        EventBlueprint(**data)


def test_time_cost_negative():
    """#10: time_cost 負數也應報 ValidationError。"""
    event = _minimal_event(time_cost=-1)
    data = _minimal_blueprint(events=[event])
    with pytest.raises(ValidationError):
        EventBlueprint(**data)


def test_time_cost_positive_ok():
    """#10: time_cost 正整數合法。"""
    event = _minimal_event(time_cost=2)
    data = _minimal_blueprint(events=[event])
    bp = EventBlueprint(**data)
    assert bp.events[0].time_cost == 2


# ---------------------------------------------------------------------------
# #11: new_flags_proposed — boolean FlagDef valid
# ---------------------------------------------------------------------------

def test_new_flags_proposed_boolean_valid():
    """#11: new_flags_proposed 含 boolean FlagDef 合法。"""
    flags = [
        {"flag_id": "test_flag", "type": "boolean", "initial_value": False, "description": "測試旗標。"}
    ]
    data = _minimal_blueprint(new_flags_proposed=flags)
    bp = EventBlueprint(**data)
    assert len(bp.new_flags_proposed) == 1
    assert bp.new_flags_proposed[0].type == "boolean"


def test_new_flags_proposed_empty_ok():
    """#11: new_flags_proposed 為空 list 合法。"""
    data = _minimal_blueprint(new_flags_proposed=[])
    bp = EventBlueprint(**data)
    assert bp.new_flags_proposed == []


# ---------------------------------------------------------------------------
# 版本欄位預設值
# ---------------------------------------------------------------------------

def test_default_version_fields():
    """event_blueprint_version / target_game_spec_version 預設值正確。"""
    bp = EventBlueprint(**_minimal_blueprint())
    assert bp.event_blueprint_version == "1.0"
    assert bp.target_game_spec_version == "1.2"


# ---------------------------------------------------------------------------
# result min_length
# ---------------------------------------------------------------------------

def test_choice_result_empty():
    """BlueprintChoice.result 空 list 應報 ValidationError（min_length=1）。"""
    choice = _minimal_choice(result=[])
    event = _minimal_event(choices=[choice])
    data = _minimal_blueprint(events=[event])
    with pytest.raises(ValidationError):
        EventBlueprint(**data)


# ---------------------------------------------------------------------------
# events min_length
# ---------------------------------------------------------------------------

def test_events_empty():
    """EventBlueprint.events 空 list 應報 ValidationError（min_length=1）。"""
    data = _minimal_blueprint(events=[])
    with pytest.raises(ValidationError):
        EventBlueprint(**data)


# ---------------------------------------------------------------------------
# invalid fixture 載入測試
# ---------------------------------------------------------------------------

def test_invalid_schema_fixture_raises():
    """blueprint_invalid_schema.md（缺 choice_label）應在 schema 驗證時失敗。"""
    text = (FIXTURES_DIR / "blueprint_invalid_schema.md").read_text(encoding="utf-8")
    raw = _extract_yaml_block(text)
    data = yaml.safe_load(raw)
    with pytest.raises((ValidationError, Exception)):
        EventBlueprint(**data)
