"""Phase 2-C Blueprint Linter 測試（blueprint-only #1-#11 + full #1-#30）。"""

import pytest
import yaml
from pathlib import Path
from sandbox_dating_sim.schema.blueprint import EventBlueprint
from sandbox_dating_sim.schema.setup import SetupPackage
from sandbox_dating_sim.validation.blueprint_linter import BlueprintLinter

FIXTURES = Path(__file__).parent / "fixtures"
linter = BlueprintLinter()


def _load_bp(md_path: Path) -> EventBlueprint:
    import re
    text = md_path.read_text(encoding="utf-8")
    m = re.search(r"```(?:yaml|yml)\n(.*?)```", text, re.DOTALL)
    return EventBlueprint(**yaml.safe_load(m.group(1)))


def _load_setup() -> SetupPackage:
    with open(FIXTURES / "setup_minimal.yaml", encoding="utf-8") as f:
        return SetupPackage(**yaml.safe_load(f))


def _minimal_bp(**kw) -> EventBlueprint:
    base = {
        "blueprint_id": "test_world_event_blueprint",
        "source_world_id": "test_world",
        "source_setup_package": "test_world_setup_package.md",
        "initial_event_id": "ev1",
        "events": [{
            "event_id": "ev1", "title": "T", "scene_summary": "S.",
            "location_id": "protagonist_home", "time_slot": "morning",
            "priority": "main", "repeat_policy": "once",
            "route_tags": [], "conditions": [], "event_purpose": "P.",
            "cast": [], "expected_assets": {"background": None, "bgm": None, "characters": []},
            "choices": [{"choice_id": "c1", "choice_label": "L", "choice_intent": "I",
                         "result": ["goto: free_roam"]}],
            "time_cost": 1,
        }],
        "new_flags_proposed": [],
    }
    base.update(kw)
    return EventBlueprint(**base)


def _types(report) -> list[str]:
    return [i.type for i in report.issues]


# ── Blueprint-only #1-#11 ─────────────────────────────────────────────────

def test_bo1_duplicate_event_id():
    ev = {"event_id": "ev1", "title": "T", "scene_summary": "S.",
          "location_id": "protagonist_home", "time_slot": "morning",
          "priority": "main", "repeat_policy": "once", "route_tags": [],
          "conditions": [], "event_purpose": "P.", "cast": [],
          "expected_assets": {"background": None, "bgm": None, "characters": []},
          "choices": [{"choice_id": "c1", "choice_label": "L", "choice_intent": "I",
                       "result": ["goto: free_roam"]}], "time_cost": 1}
    bp = EventBlueprint(**{
        "blueprint_id": "w_event_blueprint", "source_world_id": "w",
        "source_setup_package": "w_setup_package.md", "initial_event_id": "ev1",
        "events": [dict(ev), dict(ev)], "new_flags_proposed": [],
    })
    report = linter.validate_blueprint_only(bp)
    assert "duplicate_event_id" in _types(report)


def test_bo2_invalid_event_id():
    bp = _minimal_bp()
    bp.events[0].event_id = "Bad ID"
    bp.initial_event_id = "Bad ID"
    report = linter.validate_blueprint_only(bp)
    assert "invalid_id_format" in _types(report)


def test_bo3_missing_initial_reference():
    bp = _minimal_bp()
    bp.initial_event_id = "nonexistent"
    report = linter.validate_blueprint_only(bp)
    assert "unknown_initial_event" in _types(report)


def test_bo4_duplicate_choice_id():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _minimal_bp()
    bp.events[0].choices = [
        BlueprintChoice(choice_id="c1", choice_label="A", choice_intent="I", result=["goto: free_roam"]),
        BlueprintChoice(choice_id="c1", choice_label="B", choice_intent="I", result=["goto: free_roam"]),
    ]
    report = linter.validate_blueprint_only(bp)
    assert "duplicate_choice_id" in _types(report)


def test_bo5_missing_terminal():
    bp = _load_bp(FIXTURES / "blueprint_invalid_missing_terminal.md")
    report = linter.validate_blueprint_only(bp)
    assert "missing_terminal" in _types(report)


def test_bo6_multiple_terminal():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _minimal_bp()
    bp.events[0].choices = [
        BlueprintChoice(choice_id="c1", choice_label="L", choice_intent="I",
                        result=["goto: free_roam", "ending: some_end"]),
    ]
    report = linter.validate_blueprint_only(bp)
    assert "multiple_terminal" in _types(report)


def test_bo7_unknown_goto():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _minimal_bp()
    bp.events[0].choices = [
        BlueprintChoice(choice_id="c1", choice_label="L", choice_intent="I",
                        result=["goto: missing_event"]),
    ]
    report = linter.validate_blueprint_only(bp)
    assert "unknown_goto_target" in _types(report)


def test_bo8_invalid_dsl_in_result():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _minimal_bp()
    bp.events[0].choices = [
        BlueprintChoice(choice_id="c1", choice_label="L", choice_intent="I",
                        result=["不合法的自然語言", "goto: free_roam"]),
    ]
    report = linter.validate_blueprint_only(bp)
    assert "invalid_result_dsl" in _types(report)


def test_bo8_invalid_dsl_in_conditions():
    """#8: event.conditions 自然語言 → invalid_condition_dsl。"""
    bp = _minimal_bp()
    bp.events[0].conditions = ["this is natural language"]
    report = linter.validate_blueprint_only(bp)
    assert "invalid_condition_dsl" in _types(report)


def test_bo9_item_inventory_in_result():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _minimal_bp()
    bp.events[0].choices = [
        BlueprintChoice(choice_id="c1", choice_label="L", choice_intent="I",
                        result=["item.key = true", "goto: free_roam"]),
    ]
    report = linter.validate_blueprint_only(bp)
    assert "forbidden_item_syntax" in _types(report)


def test_bo9_item_inventory_in_conditions():
    """#9: event.conditions item.* → forbidden_item_syntax。"""
    bp = _minimal_bp()
    bp.events[0].conditions = ["item.key == true"]
    report = linter.validate_blueprint_only(bp)
    assert "forbidden_item_syntax" in _types(report)


def test_bo10_duplicate_time_cost():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _minimal_bp()
    bp.events[0].choices = [
        BlueprintChoice(choice_id="c1", choice_label="L", choice_intent="I",
                        result=["time_cost: 1", "time_cost: 2", "goto: free_roam"]),
    ]
    report = linter.validate_blueprint_only(bp)
    assert "duplicate_time_cost_override" in _types(report)


def test_bo11_empty_route_tag():
    bp = _minimal_bp()
    bp.events[0].route_tags = [""]
    report = linter.validate_blueprint_only(bp)
    assert "empty_route_tag" in _types(report)


# ── Full linter #1-#30 ────────────────────────────────────────────────────

def _full_setup() -> SetupPackage:
    return _load_setup()


def _full_bp() -> EventBlueprint:
    """合法的最小 full blueprint（對應 setup_minimal.yaml）。"""
    return EventBlueprint(**{
        "blueprint_id": "summer_city_2026_event_blueprint",
        "source_world_id": "summer_city_2026",
        "source_setup_package": "summer_city_2026_setup_package.md",
        "initial_event_id": "opening_morning",
        "events": [
            {
                "event_id": "opening_morning",
                "title": "開場", "scene_summary": "主角在家醒來。",
                "location_id": "protagonist_home", "time_slot": "morning",
                "priority": "main", "repeat_policy": "once",
                "route_tags": ["opening"], "conditions": [],
                "event_purpose": "開場。", "cast": [],
                "expected_assets": {"background": None, "bgm": None, "characters": []},
                "choices": [
                    {"choice_id": "go", "choice_label": "出門", "choice_intent": "外出",
                     "result": ["goto: fallback_ev"]},
                ],
                "time_cost": 1,
            },
            {
                "event_id": "fallback_ev",
                "title": "通用結局", "scene_summary": "故事結束。",
                "location_id": "protagonist_home", "time_slot": "afternoon",
                "priority": "normal", "repeat_policy": "once",
                "route_tags": ["fallback_ending"], "conditions": [],
                "event_purpose": "兜底結局。", "cast": [],
                "expected_assets": {"background": None, "bgm": None, "characters": []},
                "choices": [
                    {"choice_id": "end", "choice_label": "接受", "choice_intent": "接受結局",
                     "result": ["ending: sophie_good_ending"]},
                ],
                "time_cost": 1,
            },
        ],
        "new_flags_proposed": [],
    })


def test_full_valid_passes():
    """合法 blueprint + setup 應 passed。"""
    report = linter.validate(_full_setup(), _full_bp())
    errors = [i for i in report.issues if i.severity == "error"]
    assert not errors, [i.message for i in errors]


def test_full1_world_mismatch():
    bp = _full_bp(); bp.source_world_id = "other_world"
    assert "world_id_mismatch" in _types(linter.validate(_full_setup(), bp))


def test_full2_blueprint_id_mismatch():
    bp = _full_bp(); bp.blueprint_id = "wrong_id"
    assert "blueprint_id_mismatch" in _types(linter.validate(_full_setup(), bp))


def test_full3_source_setup_mismatch():
    bp = _full_bp(); bp.source_setup_package = "wrong.md"
    assert "source_setup_mismatch" in _types(linter.validate(_full_setup(), bp))


def test_full4_missing_protagonist_home():
    setup = _full_setup()
    setup.locations = [l for l in setup.locations if l.location_id != "protagonist_home"]
    assert "missing_protagonist_home" in _types(linter.validate(setup, _full_bp()))


def test_full5_protagonist_home_time_slots_mismatch():
    setup = _full_setup()
    for loc in setup.locations:
        if loc.location_id == "protagonist_home":
            loc.available_time_slots = ["morning"]
    assert "invalid_protagonist_home_time_slots" in _types(linter.validate(setup, _full_bp()))


def test_full6_location_time_slot_outside_world():
    setup = _full_setup()
    for loc in setup.locations:
        if loc.location_id == "school_library":
            loc.available_time_slots = list(loc.available_time_slots) + ["midnight"]
    assert "invalid_location_time_slot" in _types(linter.validate(setup, _full_bp()))


def test_full7_initial_event_wrong_location():
    bp = _full_bp(); bp.events[0].location_id = "school_library"
    assert "initial_event_wrong_location" in _types(linter.validate(_full_setup(), bp))


def test_full8_initial_event_wrong_slot():
    bp = _full_bp(); bp.events[0].time_slot = "evening"
    assert "initial_event_wrong_slot" in _types(linter.validate(_full_setup(), bp))


def test_full9_initial_event_gated():
    bp = _full_bp(); bp.events[0].conditions = ["flag.some_flag == true"]
    assert "initial_event_gated" in _types(linter.validate(_full_setup(), bp))


def test_full10_unknown_location():
    bp = _load_bp(FIXTURES / "blueprint_invalid_unknown_location.md")
    setup = _full_setup()
    setup.world.world_id = "summer_city_2026"
    assert "unknown_location" in _types(linter.validate(setup, bp))


def test_full11_event_time_outside_world():
    bp = _full_bp(); bp.events[1].time_slot = "midnight"
    assert "event_time_outside_world" in _types(linter.validate(_full_setup(), bp))


def test_full12_insufficient_time():
    bp = _full_bp(); bp.events[0].time_cost = 99
    assert "insufficient_time" in _types(linter.validate(_full_setup(), bp))


def test_full13_direct_goto_time_mismatch():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _full_bp()
    # opening(morning, time_cost=1) → fallback_ev(afternoon=ok)
    # Make goto target slot not match
    bp.events[1].time_slot = "evening"  # should be afternoon
    types = _types(linter.validate(_full_setup(), bp))
    assert "goto_time_mismatch" in types


def test_full14_unknown_cast():
    bp = _full_bp(); bp.events[0].cast = ["nonexistent_char"]
    assert "unknown_cast_character" in _types(linter.validate(_full_setup(), bp))


def test_full15_asset_not_in_cast():
    from sandbox_dating_sim.schema.blueprint import ExpectedCharacterAsset
    bp = _full_bp()
    bp.events[0].expected_assets.characters = [
        ExpectedCharacterAsset(character_id="sophie", costume="school_uniform",
                               emotion="happy", position="center")
    ]
    # cast is empty, so sophie not in cast
    assert "asset_character_not_in_cast" in _types(linter.validate(_full_setup(), bp))


def test_full16_asset_whitelist_warning():
    from sandbox_dating_sim.schema.blueprint import ExpectedCharacterAsset
    bp = _full_bp()
    bp.events[0].cast = ["sophie"]
    bp.events[0].expected_assets.characters = [
        ExpectedCharacterAsset(character_id="sophie", costume="nonexistent_costume",
                               emotion="happy", position="center")
    ]
    types = _types(linter.validate(_full_setup(), bp))
    assert "asset_costume_not_whitelisted" in types


def test_full17_non_boolean_flag():
    setup = _full_setup()
    from sandbox_dating_sim.schema.setup import FlagDef
    setup.flags.append(FlagDef(flag_id="int_flag", type="integer", initial_value=0, description="整數旗標"))
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _full_bp()
    bp.events[0].choices[0].result = ["flag.int_flag = true", "goto: fallback_ev"]
    types = _types(linter.validate(setup, bp))
    assert "non_boolean_flag" in types


def test_full18_unknown_flag():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _full_bp()
    bp.events[0].choices[0].result = ["flag.ghost_flag = true", "goto: fallback_ev"]
    assert "unknown_flag" in _types(linter.validate(_full_setup(), bp))


def test_full19_proposed_flag_not_boolean():
    from sandbox_dating_sim.schema.setup import FlagDef
    bp = _full_bp()
    bp.new_flags_proposed = [FlagDef(flag_id="bad_flag", type="integer", initial_value=0, description="x")]
    assert "proposed_flag_not_boolean" in _types(linter.validate(_full_setup(), bp))


def test_full20_unknown_stat():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _full_bp()
    bp.events[0].choices[0].result = ["stat.Luck += 1", "goto: fallback_ev"]
    assert "unknown_stat" in _types(linter.validate(_full_setup(), bp))


def test_full21_unknown_favor_character():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _full_bp()
    bp.events[0].choices[0].result = ["character.nobody.favor += 5", "goto: fallback_ev"]
    assert "unknown_favor_character" in _types(linter.validate(_full_setup(), bp))


def test_full22_unknown_status():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _full_bp()
    bp.events[0].choices[0].result = ["status.protagonist.ghost_status = true", "goto: fallback_ev"]
    assert "unknown_status" in _types(linter.validate(_full_setup(), bp))


def test_full23_invalid_status_target():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _full_bp()
    bp.events[0].choices[0].result = ["status.sophie.overworked = true", "goto: fallback_ev"]
    assert "invalid_status_target" in _types(linter.validate(_full_setup(), bp))


def test_full24_location_unlock_unknown_flag():
    """#24: location.unlock_conditions 引用未知 flag → error。"""
    setup = _full_setup()
    for loc in setup.locations:
        if loc.location_id == "school_library":
            loc.unlock_conditions = ["flag.ghost_flag == true"]
    assert "unknown_location_condition_reference" in _types(linter.validate(setup, _full_bp()))


def test_full24_location_closed_unknown_flag():
    """#24: location.closed_conditions 引用未知 flag → error。"""
    setup = _full_setup()
    for loc in setup.locations:
        if loc.location_id == "school_library":
            loc.closed_conditions = ["flag.phantom_flag == true"]
    assert "unknown_location_condition_reference" in _types(linter.validate(setup, _full_bp()))


def test_full24_known_flag_in_location_conditions_ok():
    """#24: location.unlock_conditions 引用已知 flag 就不報錯。"""
    setup = _full_setup()
    from sandbox_dating_sim.schema.setup import FlagDef
    setup.flags.append(FlagDef(flag_id="known_flag", type="boolean", initial_value=False, description="已知旗標"))
    for loc in setup.locations:
        if loc.location_id == "school_library":
            loc.unlock_conditions = ["flag.known_flag == true"]
    types = _types(linter.validate(setup, _full_bp()))
    assert "unknown_location_condition_reference" not in types


def test_full_condition_unknown_flag():
    """event.conditions 引用未知 flag → unknown_flag。"""
    bp = _full_bp()
    bp.events[1].conditions = ["flag.ghost_flag == true"]
    assert "unknown_flag" in _types(linter.validate(_full_setup(), bp))


def test_full_condition_unknown_stat():
    """event.conditions 引用不存在的 stat → unknown_stat。"""
    bp = _full_bp()
    bp.events[1].conditions = ["stat.Luck >= 5"]
    assert "unknown_stat" in _types(linter.validate(_full_setup(), bp))


def test_full_condition_unknown_favor_character():
    """event.conditions favor 引用不存在角色 → unknown_favor_character。"""
    bp = _full_bp()
    bp.events[1].conditions = ["character.nobody.favor >= 50"]
    assert "unknown_favor_character" in _types(linter.validate(_full_setup(), bp))


def test_full_condition_unknown_status():
    """event.conditions 引用不存在 status_id → unknown_status。"""
    bp = _full_bp()
    bp.events[1].conditions = ["status.protagonist.ghost_status == true"]
    assert "unknown_status" in _types(linter.validate(_full_setup(), bp))


def test_full25_unknown_ending():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _full_bp()
    bp.events[1].choices[0].result = ["ending: nonexistent_ending"]
    assert "unknown_ending" in _types(linter.validate(_full_setup(), bp))


def test_full26_uncovered_ending():
    bp = _load_bp(FIXTURES / "blueprint_invalid_uncovered_ending.md")
    setup = _load_setup()
    types = _types(linter.validate(setup, bp))
    assert "uncovered_ending" in types


def test_full27_missing_fallback_ending():
    bp = _full_bp()
    for ev in bp.events:
        ev.route_tags = [t for t in ev.route_tags if t != "fallback_ending"]
    assert "missing_fallback_ending" in _types(linter.validate(_full_setup(), bp))


def test_full28_fallback_no_ending_result():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _full_bp()
    for ev in bp.events:
        if "fallback_ending" in ev.route_tags:
            ev.choices[0].result = ["goto: free_roam"]
    types = _types(linter.validate(_full_setup(), bp))
    assert "fallback_no_ending_result" in types


def test_full29_daily_high_impact_warning():
    from sandbox_dating_sim.schema.blueprint import BlueprintChoice
    bp = _full_bp()
    bp.events[0].repeat_policy = "daily"
    bp.events[0].choices[0].result = ["character.sophie.favor += 5", "goto: fallback_ev"]
    types = _types(linter.validate(_full_setup(), bp))
    assert "daily_high_impact" in types


def test_full30_multiple_critical_warning():
    import copy
    bp = _full_bp()
    base_ev = bp.events[0]
    for i in range(4):
        ev = copy.deepcopy(base_ev)
        ev.event_id = f"crit_ev_{i}"
        ev.priority = "critical"
        ev.choices[0].result = ["goto: free_roam"]
        bp.events.append(ev)
    bp.initial_event_id = "opening_morning"
    types = _types(linter.validate(_full_setup(), bp))
    assert "multiple_critical_events" in types


# ── CLI validate-blueprint 基本測試 ─────────────────────────────────────────

def _setup_cli_outputs(tmp_path):
    """Build outputs/<world_id>/setup_package + event_blueprints directories."""
    import re
    import yaml as _yaml
    from sandbox_dating_sim.pipeline.setup_exporter import SetupPackageExporter

    world_id = "summer_city_2026"
    outputs = tmp_path / "outputs"

    # write setup package
    setup_md_dir = outputs / world_id / "setup_package"
    setup_md_dir.mkdir(parents=True)
    with open(FIXTURES / "setup_minimal.yaml", encoding="utf-8") as f:
        from sandbox_dating_sim.schema.setup import SetupPackage
        pkg = SetupPackage(**_yaml.safe_load(f))
    exporter = SetupPackageExporter()
    setup_md_path = setup_md_dir / f"{world_id}_setup_package.md"
    setup_md_path.write_text(exporter.to_markdown(pkg), encoding="utf-8")

    # write blueprint
    from tests.test_blueprint_linter import _full_bp
    from sandbox_dating_sim.pipeline.blueprint_parser import BlueprintParser
    bp_dir = outputs / world_id / "event_blueprints"
    bp_dir.mkdir(parents=True)
    bp = _full_bp()
    bp_md = "# Blueprint\n\n```yaml\n" + _yaml.dump(bp.model_dump(mode="json"), allow_unicode=True) + "```\n"
    (bp_dir / f"{world_id}_event_blueprint.md").write_text(bp_md, encoding="utf-8")

    return outputs


def test_cli_validate_blueprint_passes(tmp_path):
    """CLI validate-blueprint 對合法 blueprint 应返回 exit code 0。"""
    from typer.testing import CliRunner
    from sandbox_dating_sim.cli import app

    outputs = _setup_cli_outputs(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["validate-blueprint", "--outputs-root", str(outputs)],
        input="1\n1\n",  # world=1, setup=1
    )
    assert result.exit_code == 0, result.output
    assert "passed" in result.output or "Blueprint-Only" in result.output


def test_cli_validate_blueprint_no_outputs(tmp_path):
    """outputs 目錄不存在時 CLI 報錯。"""
    from typer.testing import CliRunner
    from sandbox_dating_sim.cli import app

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["validate-blueprint", "--outputs-root", str(tmp_path / "nonexistent")],
        input="1\n",
    )
    assert result.exit_code == 1
