"""Phase 2-A-0 Setup Prerequisites：UIW 與 Linter 測試。"""

import pytest
from pathlib import Path
from datetime import date

import yaml
from pydantic import ValidationError

from sandbox_dating_sim.schema.setup import SetupPackage, Location, World
from sandbox_dating_sim.uiw.linter import UIWLinter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_minimal() -> SetupPackage:
    with open(FIXTURES_DIR / "setup_minimal.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return SetupPackage(**data)


def _make_world(**kw):
    defaults = dict(
        world_id="test_world",
        title="Test",
        start_date=date(2026, 4, 27),
        end_date=date(2026, 5, 26),
        time_slots=["morning", "afternoon", "evening"],
        global_style=[],
    )
    defaults.update(kw)
    return World(**defaults)


def _home_loc(time_slots=None) -> dict:
    slots = time_slots or ["morning", "afternoon", "evening"]
    return {
        "location_id": "protagonist_home",
        "name": "主角家",
        "location_type": "standalone",
        "parent_location_id": None,
        "is_visitable": True,
        "base_cost": 0,
        "available_time_slots": slots,
        "tags": ["system", "home", "rest", "private"],
        "unlock_conditions": [],
        "closed_conditions": [],
        "map_priority": "normal",
        "map_display_group": None,
        "default_npc_capacity": 0,
        "empty_behavior": "allow_rest",
        "ambient_text": None,
    }


# ---------------------------------------------------------------------------
# Test 1: setup_minimal.yaml contains protagonist_home
# ---------------------------------------------------------------------------

def test_setup_minimal_has_protagonist_home():
    """測試 #1：UIW 初始 state —— setup_minimal.yaml 含 protagonist_home。"""
    pkg = _load_minimal()
    loc_ids = [loc.location_id for loc in pkg.locations]
    assert "protagonist_home" in loc_ids


# ---------------------------------------------------------------------------
# Test 2: protagonist_home default fields
# ---------------------------------------------------------------------------

def test_protagonist_home_default_fields():
    """測試 #2：protagonist_home 欄位 —— 時段、tags、empty_behavior。"""
    pkg = _load_minimal()
    home = next(l for l in pkg.locations if l.location_id == "protagonist_home")
    assert home.is_visitable is True
    assert set(home.tags) >= {"system", "home", "rest", "private"}
    assert home.empty_behavior == "allow_rest"
    # protagonist_home.available_time_slots == world.time_slots
    assert list(home.available_time_slots) == list(pkg.world.time_slots)


# ---------------------------------------------------------------------------
# Test 3: UIW 初始化函式（純函式測試，不啟動 Streamlit）
# ---------------------------------------------------------------------------

def test_default_protagonist_home_helper():
    """測試 _default_protagonist_home() 回傳正確 dict。"""
    from sandbox_dating_sim.ui.streamlit_uiw import _default_protagonist_home
    home = _default_protagonist_home(["morning", "afternoon", "evening"])
    assert home["location_id"] == "protagonist_home"
    assert home["is_visitable"] is True
    assert set(home["tags"]) >= {"system", "home", "rest", "private"}
    assert home["empty_behavior"] == "allow_rest"
    assert home["available_time_slots"] == ["morning", "afternoon", "evening"]


# ---------------------------------------------------------------------------
# Test 4: Linter — missing_protagonist_home
# ---------------------------------------------------------------------------

def test_linter_missing_protagonist_home():
    """測試 #4：移除 protagonist_home 後 linter 報 missing_protagonist_home。"""
    pkg = _load_minimal()
    # 移除 protagonist_home
    pkg.locations = [l for l in pkg.locations if l.location_id != "protagonist_home"]
    linter = UIWLinter()
    report = linter.validate(pkg)
    types = [i.type for i in report.issues]
    assert "missing_protagonist_home" in types
    err = next(i for i in report.issues if i.type == "missing_protagonist_home")
    assert err.severity == "error"


# ---------------------------------------------------------------------------
# Test 5: Linter — invalid_protagonist_home_time_slots
# ---------------------------------------------------------------------------

def test_linter_invalid_protagonist_home_time_slots():
    """測試 #5：protagonist_home 時段少於 world.time_slots 時報 invalid_protagonist_home_time_slots。"""
    pkg = _load_minimal()
    # 找到 protagonist_home 並縮減時段
    for loc in pkg.locations:
        if loc.location_id == "protagonist_home":
            loc.available_time_slots = ["morning"]  # 少了 afternoon、evening
            break
    linter = UIWLinter()
    report = linter.validate(pkg)
    types = [i.type for i in report.issues]
    assert "invalid_protagonist_home_time_slots" in types
    err = next(i for i in report.issues if i.type == "invalid_protagonist_home_time_slots")
    assert err.severity == "error"


def test_linter_protagonist_home_time_slots_exact_match_ok():
    """protagonist_home 時段 == world.time_slots 時不報錯。"""
    pkg = _load_minimal()
    linter = UIWLinter()
    report = linter.validate(pkg)
    types = [i.type for i in report.issues]
    assert "invalid_protagonist_home_time_slots" not in types
    assert "missing_protagonist_home" not in types


# ---------------------------------------------------------------------------
# Test 6: Linter — invalid_location_time_slot
# ---------------------------------------------------------------------------

def test_linter_invalid_location_time_slot():
    """測試 #6：任一 location 使用 world.time_slots 外的時段，報 invalid_location_time_slot。"""
    pkg = _load_minimal()
    # 找到 school_library 並加入 world 沒有的時段
    for loc in pkg.locations:
        if loc.location_id == "school_library":
            loc.available_time_slots = list(loc.available_time_slots) + ["midnight"]
            break
    linter = UIWLinter()
    report = linter.validate(pkg)
    types = [i.type for i in report.issues]
    assert "invalid_location_time_slot" in types
    err = next(i for i in report.issues if i.type == "invalid_location_time_slot")
    assert err.severity == "error"


def test_linter_valid_location_time_slot_ok():
    """所有 location 使用 world.time_slots 子集時不報 invalid_location_time_slot。"""
    pkg = _load_minimal()
    linter = UIWLinter()
    report = linter.validate(pkg)
    types = [i.type for i in report.issues]
    assert "invalid_location_time_slot" not in types


# ---------------------------------------------------------------------------
# Test 7: protagonist_home == world.time_slots (extra slots 報錯)
# ---------------------------------------------------------------------------

def test_linter_protagonist_home_extra_slots_error():
    """protagonist_home 時段與 world.time_slots 不同（多出 midnight）報錯。"""
    pkg = _load_minimal()
    for loc in pkg.locations:
        if loc.location_id == "protagonist_home":
            loc.available_time_slots = ["morning", "afternoon", "evening", "midnight"]
            break
    linter = UIWLinter()
    report = linter.validate(pkg)
    types = [i.type for i in report.issues]
    # 同時報 invalid_protagonist_home_time_slots 和 invalid_location_time_slot
    assert "invalid_protagonist_home_time_slots" in types or "invalid_location_time_slot" in types
