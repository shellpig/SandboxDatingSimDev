import pytest
import yaml
from unittest.mock import MagicMock
from sandbox_dating_sim.uiw.helpers import (
    _has_flag_reference,
    _has_status_reference,
    _parse_effect_yaml,
    _status_targets_options,
)
from sandbox_dating_sim.schema.setup import StatusFlag

def test_normalize_legacy_status():
    # Target to targets
    res = StatusFlag._normalize_legacy_target({"target": "protagonist", "status_id": "a", "label": "A", "effect": [], "duration": {"type": "days"}, "clear_rule": ["on_rest"], "description": ""})
    assert res.get("targets") == ["protagonist"]
    assert "target" not in res

    # Empty target
    res2 = StatusFlag._normalize_legacy_target({"target": "", "status_id": "a"})
    assert res2.get("targets") == []

    # Priority of targets over target
    res3 = StatusFlag._normalize_legacy_target({"targets": ["a"], "target": "b", "status_id": "a"})
    assert res3.get("targets") == ["a"]

def test_parse_effect_yaml():
    with pytest.raises(ValueError):
        _parse_effect_yaml("")

    with pytest.raises(ValueError):
        _parse_effect_yaml("foo: bar")

    with pytest.raises(ValueError):
        _parse_effect_yaml("- foo")

    with pytest.raises(ValueError):
        _parse_effect_yaml("- 123: x")

    valid_yaml = "- block_time_slot: evening\n- stat_multiplier:\n    stat: CHA\n    value: 0.8"
    parsed = _parse_effect_yaml(valid_yaml)
    assert len(parsed) == 2
    assert parsed[0] == {"block_time_slot": "evening"}
    assert parsed[1] == {"stat_multiplier": {"stat": "CHA", "value": 0.8}}

    # Check round-trip
    dumped = yaml.safe_dump(parsed)
    assert yaml.safe_load(dumped) == parsed

def test_parse_effect_yaml_rejects_non_string():
    """非字串輸入必須立刻 raise ValueError，避免 PyYAML Reader 把 MagicMock 等
    truthy 物件當 file-like 而陷入死迴圈（test_uiw_1g7 卡死的根因）。"""
    with pytest.raises(ValueError):
        _parse_effect_yaml(MagicMock())
    with pytest.raises(ValueError):
        _parse_effect_yaml(None)
    with pytest.raises(ValueError):
        _parse_effect_yaml(123)
    with pytest.raises(ValueError):
        _parse_effect_yaml([])
    with pytest.raises(ValueError):
        _parse_effect_yaml({"foo": "bar"})

def test_status_targets_options():
    res1 = _status_targets_options(characters=[{"character_id": "sophie", "display_name": "蘇菲"}], current_targets=[])
    assert res1[0] == ("主角(protagonist)", "protagonist")
    assert res1[1] == ("蘇菲(sophie)", "sophie")

    res2 = _status_targets_options(characters=[{"character_id": "protagonist", "display_name": "怪資料"}], current_targets=[])
    assert len(res2) == 1
    assert res2[0] == ("主角(protagonist)", "protagonist")

    res3 = _status_targets_options(characters=[], current_targets=["dangling_x"])
    assert res3[1] == ("dangling_x(角色已刪除)", "dangling_x")

def test_has_flag_reference():
    assert _has_flag_reference("not flag.over and flag.over_x", "over") is True
    assert _has_flag_reference("flag.over_x only", "over") is False

def test_has_status_reference():
    assert _has_status_reference("status.protagonist.overworked", "overworked") is True
    assert _has_status_reference("status.overworked == true", "overworked") is True
    assert _has_status_reference("status.overworked_x", "overworked") is False

from unittest.mock import patch
from sandbox_dating_sim.ui.streamlit_uiw import _tab_flags, _tab_characters

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_delete_character_blocked_by_status_targets(mock_st):
    """測試 1-G-5 角色刪除防呆對 status_flags[].targets 的引用阻擋回歸。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "characters": [{"character_id": "sophie", "display_name": "蘇菲", "gender": "female", "role": "main_love_interest"}],
        "status_flags": [{"status_id": "status_guo_lao", "targets": ["sophie", "protagonist"]}],
    })

    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "刪除"

    _tab_characters()

    # Should not delete
    assert len(mock_st.session_state["characters"]) == 1

    # Should show toast
    error_found = False
    for call in mock_st.toast.call_args_list:
        if "status_guo_lao" in str(call):
            error_found = True
    assert error_found

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_status_inline_duration_and_effect(mock_st):
    """測試 status inline 編輯期間，缺 permanent_reason 不可儲存。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "status_flags": [{
            "status_id": "status_test", "label": "test", "targets": ["protagonist"],
            "effect": [{"a": "b"}], "duration": {"type": "permanent", "value": None},
            "clear_rule": ["on_rest"], "description": ""
        }]
    })

    # Click save on the inline editor
    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "儲存修改"

    # Provide empty permanent_reason
    def mock_text_input(label, value="", **kwargs):
        if label == "永久原因 (必填)": return ""
        return mock_st.session_state.get(kwargs.get("key"), value)
    mock_st.text_input.side_effect = mock_text_input

    mock_st.selectbox.side_effect = lambda label, options, **kwargs: "permanent" if label == "持續類型" else options[0]

    _tab_flags()

    # Should have shown error
    error_found = False
    for call in mock_st.error.call_args_list:
        if "永久原因" in str(call):
            error_found = True
    assert error_found

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_flag_inline_edit_save_cancel_delete(mock_st):
    """測試 flag inline 編輯儲存 / 取消 / 刪除防呆。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state["flags"] = [
        {"flag_id": "flag_a", "type": "boolean", "initial_value": False, "description": "A"}
    ]

    # 測試儲存
    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "儲存修改"
    mock_st.text_input.side_effect = lambda label, value="", **kwargs: "B" if label == "說明" else mock_st.session_state.get(kwargs.get("key"), value)
    _tab_flags()
    assert mock_st.session_state["flags"][0]["description"] == "B"

    # 測試取消
    mock_st.session_state["flag_desc_flag_a"] = "C"
    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "取消"
    _tab_flags()
    assert "flag_desc_flag_a" not in mock_st.session_state # keyed state purged

    # 測試刪除成功與否
    mock_st.session_state["endings"] = [{"ending_id": "end_1", "required_flags": ["flag.flag_a == true"]}]
    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "刪除"
    _tab_flags()
    assert len(mock_st.session_state["flags"]) == 1 # blocked

    mock_st.session_state["endings"] = []
    _tab_flags()
    assert len(mock_st.session_state["flags"]) == 0 # deleted

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_add_flag_status_draft_retained_on_failure(mock_st):
    """測試新增 Flag / Status 表單驗證失敗後，draft key 仍保留。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()

    # Simulate a validation failure for Add Flag (e.g. invalid ID)
    mock_st.session_state["add_f_id"] = "INVALID_ID!!!"
    mock_st.session_state["add_f_desc"] = "My Draft Desc"

    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "新增 Flag"

    _tab_flags()

    assert len(mock_st.session_state["flags"]) == 0
    # Draft keys should NOT be deleted
    assert mock_st.session_state["add_f_desc"] == "My Draft Desc"

    # Fix the error and submit again
    mock_st.session_state["add_f_id"] = "valid_id"
    _tab_flags()

    assert len(mock_st.session_state["flags"]) == 1
    # Draft keys SHOULD be deleted after success
    assert "add_f_desc" not in mock_st.session_state

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_duplicate_widget_keys(mock_st):
    """測試多筆 flag/status 同時展開不產生 duplicate widget key。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state["flags"] = [
        {"flag_id": "flag_a", "type": "boolean", "initial_value": False, "description": ""},
        {"flag_id": "flag_b", "type": "boolean", "initial_value": False, "description": ""}
    ]
    mock_st.session_state["status_flags"] = [
        {"status_id": "status_a", "label": "A", "targets": ["protagonist"], "effect": [], "duration": {"type": "days", "value": 1}, "clear_rule": ["on_rest"], "description": ""},
        {"status_id": "status_b", "label": "B", "targets": ["protagonist"], "effect": [], "duration": {"type": "days", "value": 1}, "clear_rule": ["on_rest"], "description": ""}
    ]

    generated_keys = set()
    duplicate_found = []

    def key_tracker(func):
        def wrapper(*args, **kwargs):
            k = kwargs.get("key")
            if k:
                if k in generated_keys:
                    duplicate_found.append(k)
                generated_keys.add(k)
            return func(*args, **kwargs)
        return wrapper

    mock_st.text_input.side_effect = key_tracker(lambda *args, **kwargs: "")
    mock_st.selectbox.side_effect = key_tracker(lambda label, options, *args, **kwargs: options[0] if options else None)
    mock_st.multiselect.side_effect = key_tracker(lambda *args, **kwargs: kwargs.get("default", []))
    mock_st.number_input.side_effect = key_tracker(lambda *args, **kwargs: 1)
    mock_st.text_area.side_effect = key_tracker(lambda *args, **kwargs: "[]")
    mock_st.button.side_effect = key_tracker(lambda *args, **kwargs: False)

    _tab_flags()

    assert not duplicate_found, f"Found duplicate widget keys: {duplicate_found}"

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_status_duration_value_visibility(mock_st):
    """測試 duration.type 每個選項的 value 顯示與 canonical 寫入。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()

    mock_st.session_state["add_sf_dur_type"] = "until_event"
    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "新增 Status Flag"
    mock_st.multiselect.side_effect = lambda label, options, **kwargs: ["protagonist", "on_time_advance"]
    mock_st.selectbox.side_effect = lambda label, options, **kwargs: "until_event" if kwargs.get("key") == "add_sf_dur_type" else options[0]

    _tab_flags()

    print("ST ERRORS:", mock_st.error.call_args_list)
    assert len(mock_st.session_state["status_flags"]) == 1
    assert mock_st.session_state["status_flags"][0]["duration"]["value"] is None

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_add_status_permanent_requires_reason_and_preserves_draft(mock_st):
    """新增 permanent status 缺 permanent_reason 時不可儲存，且 draft 保留。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "add_sf_id": "",
        "add_sf_label": "過勞",
        "add_sf_effect": "- block_time_slot: evening",
        "add_sf_dur_type": "permanent",
        "add_sf_desc": "desc",
        "add_sf_perm_reason": "",
    })

    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "新增 Status Flag"
    mock_st.selectbox.side_effect = lambda label, options, **kwargs: "permanent" if kwargs.get("key") == "add_sf_dur_type" else options[0]
    mock_st.multiselect.side_effect = lambda label, options, **kwargs: ["protagonist"] if label == "作用對象" else ["manual_only"]

    _tab_flags()

    assert len(mock_st.session_state["status_flags"]) == 0
    assert mock_st.session_state["add_sf_label"] == "過勞"
    assert mock_st.session_state["add_sf_effect"] == "- block_time_slot: evening"
    assert any("永久狀態必須填寫永久原因" in str(call) for call in mock_st.error.call_args_list)

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_add_status_permanent_success_clears_draft_and_sets_none_value(mock_st):
    """新增 permanent status 成功時，duration.value 應為 None，並清除 draft keys。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "add_sf_id": "",
        "add_sf_label": "過勞",
        "add_sf_effect": "- block_time_slot: evening",
        "add_sf_dur_type": "permanent",
        "add_sf_desc": "desc",
        "add_sf_perm_reason": "長期狀態",
    })

    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "新增 Status Flag"
    mock_st.selectbox.side_effect = lambda label, options, **kwargs: "permanent" if kwargs.get("key") == "add_sf_dur_type" else options[0]
    mock_st.multiselect.side_effect = lambda label, options, **kwargs: ["protagonist"] if label == "作用對象" else ["manual_only"]

    _tab_flags()

    assert len(mock_st.session_state["status_flags"]) == 1
    added = mock_st.session_state["status_flags"][0]
    assert added["duration"]["type"] == "permanent"
    assert added["duration"]["value"] is None
    assert added["permanent_reason"] == "長期狀態"
    assert "add_sf_label" not in mock_st.session_state
    assert "add_sf_effect" not in mock_st.session_state
    assert "add_sf_perm_reason" not in mock_st.session_state

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_add_status_non_permanent_requires_clear_rule(mock_st):
    """新增非 permanent status 缺 clear_rule 時不可儲存，且 draft 保留。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "add_sf_id": "",
        "add_sf_label": "受傷",
        "add_sf_effect": "- stat_multiplier:\n    stat: STR\n    value: 0.8",
        "add_sf_dur_type": "days",
        "add_sf_dur_val": 2,
        "add_sf_desc": "desc",
    })

    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "新增 Status Flag"
    mock_st.selectbox.side_effect = lambda label, options, **kwargs: "days" if kwargs.get("key") == "add_sf_dur_type" else options[0]
    mock_st.multiselect.side_effect = lambda label, options, **kwargs: ["protagonist"] if label == "作用對象" else []

    _tab_flags()

    assert len(mock_st.session_state["status_flags"]) == 0
    assert mock_st.session_state["add_sf_label"] == "受傷"
    assert any("非永久狀態必須設定解除條件" in str(call) for call in mock_st.error.call_args_list)

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_status_inline_cancel_purges_keyed_state(mock_st):
    """status inline 編輯按取消後，該 status 的 keyed state 應清除。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "status_flags": [{
            "status_id": "status_a",
            "label": "A",
            "targets": ["protagonist"],
            "effect": [{"block_time_slot": "evening"}],
            "duration": {"type": "days", "value": 1},
            "clear_rule": ["on_rest"],
            "description": "",
        }],
        "status_label_status_a": "dirty",
        "status_desc_status_a": "dirty",
    })

    mock_st.button.side_effect = lambda label, *args, **kwargs: kwargs.get("key") == "status_cancel_status_a"
    _tab_flags()

    assert "status_label_status_a" not in mock_st.session_state
    assert "status_desc_status_a" not in mock_st.session_state

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_status_delete_blocked_by_reference(mock_st):
    """刪除 status 時若被 ending.required_stats 引用應阻擋。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "status_flags": [{
            "status_id": "status_a",
            "label": "A",
            "targets": ["protagonist"],
            "effect": [{"block_time_slot": "evening"}],
            "duration": {"type": "days", "value": 1},
            "clear_rule": ["on_rest"],
            "description": "",
        }],
        "endings": [{
            "ending_id": "end_1",
            "required_stats": ["status.protagonist.status_a == true"],
        }],
    })

    mock_st.button.side_effect = lambda label, *args, **kwargs: kwargs.get("key") == "status_del_status_a"
    _tab_flags()

    assert len(mock_st.session_state["status_flags"]) == 1
    assert any("end_1" in str(call) for call in mock_st.toast.call_args_list)

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_status_delete_success_purges_state(mock_st):
    """刪除 status 成功時應移除資料並清空 keyed session state。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "status_flags": [{
            "status_id": "status_a",
            "label": "A",
            "targets": ["protagonist"],
            "effect": [{"block_time_slot": "evening"}],
            "duration": {"type": "days", "value": 1},
            "clear_rule": ["on_rest"],
            "description": "",
        }],
        "status_label_status_a": "dirty",
    })

    mock_st.button.side_effect = lambda label, *args, **kwargs: kwargs.get("key") == "status_del_status_a"
    _tab_flags()

    assert len(mock_st.session_state["status_flags"]) == 0
    assert "status_label_status_a" not in mock_st.session_state

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_status_inline_save_success_updates_fields(mock_st):
    """status inline 儲存成功路徑：應寫回更新後欄位。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "characters": [{"character_id": "sophie", "display_name": "蘇菲"}],
        "status_flags": [{
            "status_id": "status_a",
            "label": "舊名稱",
            "targets": ["protagonist"],
            "effect": [{"block_time_slot": "evening"}],
            "duration": {"type": "days", "value": 1},
            "clear_rule": ["on_rest"],
            "description": "old",
            "permanent_reason": None,
        }],
    })

    mock_st.button.side_effect = lambda label, *args, **kwargs: kwargs.get("key") == "status_save_status_a"

    def _text_input(label, value="", **kwargs):
        if kwargs.get("key") == "status_label_status_a":
            return "新名稱"
        if kwargs.get("key") == "status_desc_status_a":
            return "new"
        return mock_st.session_state.get(kwargs.get("key"), value)

    def _selectbox(label, options, **kwargs):
        if kwargs.get("key") == "status_durtype_status_a":
            return "days"
        return options[0] if options else None

    def _multiselect(label, options, **kwargs):
        if kwargs.get("key") == "status_targets_status_a":
            return ["protagonist", "sophie"]
        if kwargs.get("key") == "status_clear_status_a":
            return ["on_day_end"]
        return kwargs.get("default", [])

    def _number_input(*args, **kwargs):
        if kwargs.get("key") == "status_durval_status_a":
            return 3
        return 1

    mock_st.text_input.side_effect = _text_input
    mock_st.selectbox.side_effect = _selectbox
    mock_st.multiselect.side_effect = _multiselect
    mock_st.number_input.side_effect = _number_input
    mock_st.text_area.side_effect = lambda label, value="", **kwargs: "- block_time_slot: afternoon"

    _tab_flags()

    saved = mock_st.session_state["status_flags"][0]
    assert saved["label"] == "新名稱"
    assert saved["description"] == "new"
    assert saved["targets"] == ["protagonist", "sophie"]
    assert saved["duration"] == {"type": "days", "value": 3}
    assert saved["clear_rule"] == ["on_day_end"]
    assert saved["effect"] == [{"block_time_slot": "afternoon"}]
    assert saved.get("permanent_reason") is None

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_status_inline_until_cleared_sets_duration_value_none(mock_st):
    """status inline 設為 until_cleared 時，duration.value 應寫回 None。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "status_flags": [{
            "status_id": "status_a",
            "label": "A",
            "targets": ["protagonist"],
            "effect": [{"block_time_slot": "evening"}],
            "duration": {"type": "days", "value": 2},
            "clear_rule": ["on_rest"],
            "description": "",
        }],
    })

    mock_st.button.side_effect = lambda label, *args, **kwargs: kwargs.get("key") == "status_save_status_a"
    mock_st.selectbox.side_effect = lambda label, options, **kwargs: "until_cleared" if kwargs.get("key") == "status_durtype_status_a" else (options[0] if options else None)
    mock_st.multiselect.side_effect = lambda label, options, **kwargs: ["protagonist"] if kwargs.get("key") == "status_targets_status_a" else ["on_rest"]
    mock_st.text_area.side_effect = lambda label, value="", **kwargs: "- block_time_slot: evening"

    _tab_flags()

    saved = mock_st.session_state["status_flags"][0]
    assert saved["duration"]["type"] == "until_cleared"
    assert saved["duration"]["value"] is None
@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_add_status_time_slots_duration_value_written(mock_st):
    """新增 status：duration.type=time_slots 時，duration.value 應寫入數值。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "add_sf_id": "",
        "add_sf_label": "短暫疲勞",
        "add_sf_effect": "- block_time_slot: evening",
        "add_sf_dur_type": "time_slots",
        "add_sf_dur_val": 2,
        "add_sf_desc": "desc",
    })

    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "新增 Status Flag"
    mock_st.selectbox.side_effect = lambda label, options, **kwargs: "time_slots" if kwargs.get("key") == "add_sf_dur_type" else options[0]
    mock_st.multiselect.side_effect = lambda label, options, **kwargs: ["protagonist"] if label == "作用對象" else ["on_time_advance"]
    mock_st.number_input.side_effect = lambda *args, **kwargs: 2 if kwargs.get("key") == "add_sf_dur_val" else 1

    _tab_flags()

    assert len(mock_st.session_state["status_flags"]) == 1
    saved = mock_st.session_state["status_flags"][0]
    assert saved["duration"]["type"] == "time_slots"
    assert saved["duration"]["value"] == 2

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_add_status_days_duration_value_written(mock_st):
    """新增 status：duration.type=days 時，duration.value 應寫入數值。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "add_sf_id": "",
        "add_sf_label": "受傷",
        "add_sf_effect": "- stat_multiplier:\n    stat: STR\n    value: 0.8",
        "add_sf_dur_type": "days",
        "add_sf_dur_val": 4,
        "add_sf_desc": "desc",
    })

    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "新增 Status Flag"
    mock_st.selectbox.side_effect = lambda label, options, **kwargs: "days" if kwargs.get("key") == "add_sf_dur_type" else options[0]
    mock_st.multiselect.side_effect = lambda label, options, **kwargs: ["protagonist"] if label == "作用對象" else ["on_day_end"]
    mock_st.number_input.side_effect = lambda *args, **kwargs: 4 if kwargs.get("key") == "add_sf_dur_val" else 1

    _tab_flags()

    assert len(mock_st.session_state["status_flags"]) == 1
    saved = mock_st.session_state["status_flags"][0]
    assert saved["duration"]["type"] == "days"
    assert saved["duration"]["value"] == 4

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g8_add_status_until_cleared_duration_value_none(mock_st):
    """新增 status：duration.type=until_cleared 時，duration.value 應為 None。"""
    from tests.test_uiw_1g7 import apply_common_mocks, setup_basic_state
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "add_sf_id": "",
        "add_sf_label": "待解除狀態",
        "add_sf_effect": "- block_time_slot: evening",
        "add_sf_dur_type": "until_cleared",
        "add_sf_desc": "desc",
    })

    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "新增 Status Flag"
    mock_st.selectbox.side_effect = lambda label, options, **kwargs: "until_cleared" if kwargs.get("key") == "add_sf_dur_type" else options[0]
    mock_st.multiselect.side_effect = lambda label, options, **kwargs: ["protagonist"] if label == "作用對象" else ["on_rest"]

    _tab_flags()

    assert len(mock_st.session_state["status_flags"]) == 1
    saved = mock_st.session_state["status_flags"][0]
    assert saved["duration"]["type"] == "until_cleared"
    assert saved["duration"]["value"] is None
