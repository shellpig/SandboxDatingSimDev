import pytest
import yaml
from pathlib import Path
from sandbox_dating_sim.schema.setup import SetupPackage
from sandbox_dating_sim.uiw.linter import UIWLinter

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def load_yaml(filename: str) -> SetupPackage:
    with open(FIXTURES_DIR / filename, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return SetupPackage(**data)

def test_linter_passes_minimal_fixture():
    """setup_minimal.yaml 應通過。"""
    pkg = load_yaml("setup_minimal.yaml")
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "passed"
    for issue in report.issues:
        assert issue.severity != "error"

def test_linter_rejects_no_characters_for_phase2_ready_export():
    """Phase 2-ready Setup Package 至少需要 1 個 character。"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.characters = []
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "missing_required_character" for i in report.issues)

def test_linter_rejects_no_endings_for_phase2_ready_export():
    """Phase 2-ready Setup Package 至少需要 2 個 endings。"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.endings = []
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "insufficient_endings" for i in report.issues)

def test_linter_rejects_single_ending_for_phase2_ready_export():
    """只有 1 個 ending 無法支援 fallback 與目標結局的最小分工。"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.endings = pkg.endings[:1]
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "insufficient_endings" for i in report.issues)

def test_linter_allows_empty_flags_and_status_flags():
    """flags/status_flags 可為空；Phase 2 可由 Blueprint 提出新 boolean flags。"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.flags = []
    pkg.status_flags = []
    for ending in pkg.endings:
        ending.required_flags = []
        ending.forbidden_flags = []
    linter = UIWLinter()
    report = linter.validate(pkg)
    errors = [i for i in report.issues if i.severity == "error"]
    assert not errors, [i.message for i in errors]

def test_linter_rejects_duplicate_character_id():
    """重複 character_id 應產生 error。"""
    pkg = load_yaml("setup_minimal.yaml")
    # Duplicate Sophie
    pkg.characters.append(pkg.characters[0].model_copy(deep=True))
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    errors = [i for i in report.issues if i.type == "duplicate_id"]
    assert len(errors) > 0

def test_linter_rejects_unknown_schedule_location():
    """schedule location_id 不存在應產生 error。"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.characters[0].schedule[0].location_id = "nowhere"
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "unknown_schedule_location" for i in report.issues)

def test_linter_rejects_container_without_sub_location():
    """container 沒有可進入 sub_location 應產生 error。"""
    pkg = load_yaml("setup_minimal.yaml")
    # Remove sub_location 'school_library'
    pkg.locations = [loc for loc in pkg.locations if loc.location_type != "sub_location"]
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "container_without_visitable_sub" for i in report.issues)

def test_linter_rejects_empty_clear_rule():
    """clear_rule 欄位存在但為空陣列時應產生 error。"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.status_flags[0].clear_rule = []
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "empty_clear_rule" for i in report.issues)

def test_linter_rejects_permanent_without_reason():
    """duration.type=permanent 但缺 permanent_reason 應產生 error。"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.status_flags[0].duration.type = "permanent"
    pkg.status_flags[0].permanent_reason = None
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "missing_permanent_reason" for i in report.issues)

def test_linter_detects_schedule_conflict():
    """同角色同時間段同 priority 且條件可能同時成立時應產生 issue。"""
    pkg = load_yaml("setup_minimal.yaml")
    char = pkg.characters[0]
    # Add identical schedule
    dup_sch = char.schedule[0].model_copy(deep=True)
    char.schedule.append(dup_sch)
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "schedule_tie" for i in report.issues)

def test_linter_rejects_sub_location_without_parent():
    """sub_location 必須有 parent_location_id，且其為 container。"""
    pkg = load_yaml("setup_minimal.yaml")
    # Change school_library to have no parent
    for loc in pkg.locations:
        if loc.location_type == "sub_location":
            loc.parent_location_id = None
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "missing_parent_location" for i in report.issues)

def test_linter_rejects_unknown_forbidden_flag():
    """forbidden_flags 未宣告 flag 應產生 error。"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.endings[0].forbidden_flags = ["flag.unknown_flag == true"]
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "unknown_flag" for i in report.issues)


# ─── 1-G-3 Tests ────────────────────────────────────────────────────────────

from sandbox_dating_sim.schema.setup import SemanticChoice


def test_linter_rejects_protagonist_secrets_over_3():
    """protagonist.secrets 超過 3 個時應產生 error。"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.protagonist.secrets = [
        SemanticChoice(id="s1", label="秘密一"),
        SemanticChoice(id="s2", label="秘密二"),
        SemanticChoice(id="s3", label="秘密三"),
        SemanticChoice(id="s4", label="秘密四"),
    ]
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "secrets_exceeds_max" for i in report.issues)


def test_linter_rejects_character_secrets_over_3():
    """characters[].secrets 超過 3 個時應產生 error。"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.characters[0].secrets = [
        SemanticChoice(id="s1", label="秘密一"),
        SemanticChoice(id="s2", label="秘密二"),
        SemanticChoice(id="s3", label="秘密三"),
        SemanticChoice(id="s4", label="秘密四"),
    ]
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "secrets_exceeds_max" for i in report.issues)


def test_linter_rejects_none_secret_with_others_protagonist():
    """protagonist.secrets 中 none 與其他秘密並存應產生 error。"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.protagonist.secrets = [
        SemanticChoice(id="none", label="沒有秘密"),
        SemanticChoice(id="family_debt", label="背負家族債務"),
    ]
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "none_secret_conflict" for i in report.issues)


def test_linter_rejects_none_secret_with_others_character():
    """characters[].secrets 中 none 與其他秘密並存應產生 error。"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.characters[0].secrets = [
        SemanticChoice(id="none", label="沒有秘密"),
        SemanticChoice(id="hidden_wealth", label="其實家境富裕"),
    ]
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "none_secret_conflict" for i in report.issues)


def test_linter_rejects_duplicate_global_style_id():
    """world.global_style 有重複 id 時應產生 error。"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.world.global_style.append(SemanticChoice(id="urban_romance", label="都市戀愛"))
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "duplicate_global_style_id" for i in report.issues)


def test_linter_rejects_duplicate_personality_tag_id():
    """characters[].personality_tags 有重複 id 時應產生 error。"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.characters[0].personality_tags.append(SemanticChoice(id="guarded", label="戒心重"))
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "duplicate_personality_tag_id" for i in report.issues)


def test_linter_rejects_duplicate_status_id():
    """status_id 與 character_id 衝突時應產生 error。"""
    from sandbox_dating_sim.schema.setup import StatusFlag, StatusDuration
    pkg = load_yaml("setup_minimal.yaml")
    # pkg_minimal 中的 character_id 是 "sophie"
    pkg.status_flags.append(StatusFlag(
        status_id="sophie",
        label="過勞",
        targets=["protagonist"],
        effect=[{"block_time_slot": "evening"}],
        duration=StatusDuration(type="days", value=1),
        clear_rule=["on_rest"],
        description="..."
    ))
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "duplicate_id" for i in report.issues)
    assert any("已被 characters[0].character_id 使用" in i.message for i in report.issues)


def test_linter_rejects_invalid_status_id_format():
    """status_id 格式不合法時應產生 error。"""
    from sandbox_dating_sim.schema.setup import StatusFlag, StatusDuration
    pkg = load_yaml("setup_minimal.yaml")
    pkg.status_flags.append(StatusFlag(
        status_id="Status-123",
        label="過勞",
        targets=["protagonist"],
        effect=[{"block_time_slot": "evening"}],
        duration=StatusDuration(type="days", value=1),
        clear_rule=["on_rest"],
        description="..."
    ))
    linter = UIWLinter()
    report = linter.validate(pkg)
    assert report.status == "failed"
    assert any(i.type == "invalid_id_format" for i in report.issues)

def test_linter_status_targets_1g8():
    from sandbox_dating_sim.schema.setup import StatusFlag, StatusDuration
    pkg = load_yaml("setup_minimal.yaml")

    # 測試 unknown_status_target
    pkg.status_flags.append(StatusFlag(
        status_id="unknown_target_test",
        label="測試",
        targets=["unknown_id"],
        effect=[{"block_time_slot": "evening"}],
        duration=StatusDuration(type="days", value=1),
        clear_rule=["on_rest"],
        description="..."
    ))

    # 測試 unexpected_duration_value
    pkg.status_flags.append(StatusFlag(
        status_id="unexpected_duration",
        label="測試",
        targets=["protagonist"],
        effect=[{"block_time_slot": "evening"}],
        duration=StatusDuration(type="until_event", value=3),
        clear_rule=["on_rest"],
        description="..."
    ))

    report = UIWLinter().validate(pkg)
    unknown = [i for i in report.issues if i.type == "unknown_status_target"]
    assert len(unknown) == 1
    assert "unknown_id" in unknown[0].message

    unexpected = [i for i in report.issues if i.type == "unexpected_duration_value"]
    assert len(unexpected) == 1
    assert unexpected[0].severity == "warning"
