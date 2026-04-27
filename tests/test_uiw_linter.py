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
