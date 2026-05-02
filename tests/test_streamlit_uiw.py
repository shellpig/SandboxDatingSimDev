import pytest
from unittest.mock import patch, MagicMock

# 需要先在全域環境匯入並初始化 session_state 避免被 streamlit 內部覆蓋
import streamlit as st
if not hasattr(st, "session_state") or st.session_state is None:
    st.session_state = {}

from sandbox_dating_sim.ui.streamlit_uiw import _purge_character_state, _tab_characters, _tab_flags

def test_purge_character_state():
    st.session_state.clear()
    st.session_state["keep_me"] = 1
    st.session_state["edit_name_alice"] = 2
    st.session_state["del_sch_alice_0"] = 3
    st.session_state["something_else_bob"] = 4

    _purge_character_state("alice")

    assert "keep_me" in st.session_state
    assert "something_else_bob" in st.session_state
    assert "edit_name_alice" not in st.session_state
    assert "del_sch_alice_0" not in st.session_state

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_tab_characters_keys_and_options(mock_st):
    mock_st.columns.side_effect = lambda x, **kwargs: [MagicMock() for _ in range(len(x))] if isinstance(x, list) else [MagicMock() for _ in range(x)]
    mock_st.text_input.return_value = ""
    mock_st.button.return_value = False
    mock_st.session_state = {
        "characters": [
            {"character_id": "alice", "display_name": "Alice", "gender": "female", "role": "main_love_interest", "personality_tags": [], "secrets": [], "schedule": []},
            {"character_id": "bob", "display_name": "Bob", "gender": "male", "role": "key_supporting_character", "personality_tags": [], "secrets": [], "schedule": []}
        ],
        "locations": [{"location_id": "home", "name": "Home", "location_type": "sub_location", "parent_location_id": "building", "is_visitable": True}]
    }

    _tab_characters()

    # 檢查 specific_date 不出現在新增行程 day_type UI 選項
    day_types_called = False
    for call in mock_st.selectbox.call_args_list:
        if call.kwargs.get("key", "").startswith("add_sch_day_"):
            options = call.args[1]
            assert "specific_date" not in options
            day_types_called = True
    assert day_types_called

    # 檢查角色刪除按鈕 key
    del_keys = [call.kwargs.get("key") for call in mock_st.button.call_args_list if call.args and call.args[0] == "刪除" and call.kwargs.get("key", "").startswith("del_ch_")]
    assert "del_ch_alice" in del_keys
    assert "del_ch_bob" in del_keys

    # 檢查不使用 nested st.expander 作為角色進階設定，應使用 checkbox
    checkbox_keys = [call.kwargs.get("key") for call in mock_st.checkbox.call_args_list]
    assert "show_adv_alice" in checkbox_keys
    assert "show_adv_bob" in checkbox_keys

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_add_character_validation(mock_st):
    mock_st.columns.side_effect = lambda x, **kwargs: [MagicMock() for _ in range(len(x))] if isinstance(x, list) else [MagicMock() for _ in range(x)]
    mock_st.button.return_value = False
    mock_st.session_state = {
        "characters": [{"character_id": "exist_id", "display_name": "Dummy", "gender": "male", "role": "main_love_interest", "personality_tags": [], "secrets": [], "schedule": []}],
        "locations": [{"location_id": "home", "name": "Home", "location_type": "sub_location", "parent_location_id": "building", "is_visitable": True}],
        "temp_ch_tags": [],
        "temp_ch_secrets": []
    }

    # 模擬按下新增按鈕
    mock_st.form_submit_button.return_value = True

    # 模擬輸入：空 ID
    def mock_text_input(label, *args, **kwargs):
        if label == "角色 ID (英文)":
            return ""
        return ""
    mock_st.text_input.side_effect = mock_text_input

    _tab_characters()
    mock_st.error.assert_any_call("角色 ID 不可為空")

    # 模擬輸入：重複 ID
    def mock_text_input_exist(label, *args, **kwargs):
        if label == "角色 ID (英文)":
            return "exist_id"
        return ""
    mock_st.text_input.side_effect = mock_text_input_exist

    _tab_characters()
    mock_st.error.assert_any_call("角色 ID 已存在 (與既有 ID 衝突)")

    # 模擬輸入：非法 ID
    def mock_text_input_invalid(label, *args, **kwargs):
        if label == "角色 ID (英文)":
            return "123_invalid!"
        return ""
    mock_st.text_input.side_effect = mock_text_input_invalid

    _tab_characters()
    mock_st.error.assert_any_call("角色 ID 格式錯誤 (須為小寫英文、數字、底線，且以英文字母開頭)")


# ─── Endings Tests ──────────────────────────────────────────────────────────

from sandbox_dating_sim.ui.streamlit_uiw import _tab_endings

_BASE_FLAGS_SESSION = {
    "characters": [{"character_id": "alice", "display_name": "Alice", "gender": "female", "role": "main_love_interest", "personality_tags": [], "secrets": [], "schedule": []}],
    "locations": [],
    "flags": [],
    "status_flags": [],
    "endings": [],
    "world_id": "my_world",
}

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_tab_endings_delete_buttons(mock_st):
    """已有 ending 時，應為每個 ending render del_end_<ending_id> 刪除按鈕。"""
    mock_st.columns.side_effect = lambda x, **kwargs: [MagicMock() for _ in range(len(x))] if isinstance(x, list) else [MagicMock() for _ in range(x)]
    mock_st.button.return_value = False
    mock_st.text_input.return_value = ""
    mock_st.form_submit_button.return_value = False
    state = dict(_BASE_FLAGS_SESSION)
    state["endings"] = [
        {"ending_id": "end_good", "title": "好結局", "ending_type": "good", "target_character_id": None,
         "description": "", "required_flags": [], "required_stats": [], "forbidden_flags": [], "priority": "normal", "route_tags": []},
        {"ending_id": "end_bad", "title": "壞結局", "ending_type": "bad", "target_character_id": None,
         "description": "", "required_flags": [], "required_stats": [], "forbidden_flags": [], "priority": "normal", "route_tags": []},
    ]
    mock_st.session_state = state

    _tab_endings()

    del_keys = [
        call.kwargs.get("key")
        for call in mock_st.button.call_args_list
        if call.kwargs.get("key", "").startswith("del_end_")
    ]
    assert "del_end_end_good" in del_keys
    assert "del_end_end_bad" in del_keys


@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_add_ending_validation_empty_id(mock_st):
    """新增結局時 ending_id 為空應阻止寫入並顯示 error。"""
    mock_st.columns.side_effect = lambda x, **kwargs: [MagicMock() for _ in range(len(x))] if isinstance(x, list) else [MagicMock() for _ in range(x)]
    mock_st.button.return_value = False
    mock_st.text_input.return_value = ""
    mock_st.form_submit_button.return_value = True
    state = dict(_BASE_FLAGS_SESSION)
    state["endings"] = []
    mock_st.session_state = state

    _tab_endings()

    mock_st.error.assert_any_call("Ending ID 不可為空")
    assert state["endings"] == []


@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_add_ending_validation_duplicate_id(mock_st):
    """新增結局時 ending_id 與角色 ID 重複應阻止寫入並顯示 error。"""
    mock_st.columns.side_effect = lambda x, **kwargs: [MagicMock() for _ in range(len(x))] if isinstance(x, list) else [MagicMock() for _ in range(x)]
    mock_st.button.return_value = False
    mock_st.form_submit_button.return_value = True

    def mock_text_input(label, *args, **kwargs):
        if label == "Ending ID":
            return "alice"  # 已被 character_id 使用
        return ""
    mock_st.text_input.side_effect = mock_text_input

    state = dict(_BASE_FLAGS_SESSION)
    state["endings"] = []
    mock_st.session_state = state

    _tab_endings()

    # 應顯示跨類型檢查 error
    error_calls = [str(call) for call in mock_st.error.call_args_list]
    assert any("Ending ID 已存在" in c for c in error_calls)
    assert state["endings"] == []

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_tab_endings_multiselect_versioning(mock_st):
    """1-G-6 已知問題1: F-γ multiselect 應使用 version 避免重複 key 錯誤。"""
    mock_st.columns.side_effect = lambda x, **kwargs: [MagicMock() for _ in range(len(x))] if isinstance(x, list) else [MagicMock() for _ in range(x)]
    mock_st.button.return_value = False
    mock_st.text_input.return_value = ""
    state = dict(_BASE_FLAGS_SESSION)
    state["flags"] = [{"flag_id": "flag1", "type": "boolean", "initial_value": False, "description": ""}]
    state["endings"] = [{"ending_id": "end1", "title": "End 1", "ending_type": "good", "target_character_id": None, "description": "", "required_flags": [], "required_stats": [], "forbidden_flags": [], "priority": "normal", "route_tags": []}]
    # 設定一個舊版號
    state["_ver_req_flags_end1"] = 1
    mock_st.session_state = state

    _tab_endings()

    # 檢查是否有建立帶版號的 widget key
    ms_calls = [call.kwargs.get("key") for call in mock_st.multiselect.call_args_list if "ms_req_flags_end1" in call.kwargs.get("key", "")]
    assert "ms_req_flags_end1_v1" in ms_calls


@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_tab_endings_cancel_resets_edit_state(mock_st):
    """1-G-6 已知問題2: 取消編輯應重置所有 edit_, temp_, ms_ 相關 state。"""
    mock_st.columns.side_effect = lambda x, **kwargs: [MagicMock() for _ in range(len(x))] if isinstance(x, list) else [MagicMock() for _ in range(x)]
    mock_st.button.return_value = False
    mock_st.text_input.return_value = ""

    # 模擬按下「取消」按鈕
    def mock_form_submit(label, *args, **kwargs):
        return label == "取消"
    mock_st.form_submit_button.side_effect = mock_form_submit

    state = dict(_BASE_FLAGS_SESSION)
    state["endings"] = [{"ending_id": "end1", "title": "End 1", "ending_type": "good", "target_character_id": None, "description": "", "required_flags": [], "required_stats": [], "forbidden_flags": [], "priority": "normal", "route_tags": []}]
    # 塞入預期會被清掉的草稿 state
    state["edit_title_end1"] = "Draft Title"
    state["temp_req_flags_end1"] = ["draft == true"]
    state["_ver_req_flags_end1"] = 2
    state["_ver_forb_flags_end1"] = 1
    state["ms_req_flags_end1_v0"] = ["flag1"]
    state["keep_me_end2"] = "should stay"
    mock_st.session_state = state

    _tab_endings()

    assert "edit_title_end1" not in state
    assert "temp_req_flags_end1" not in state
    assert "_ver_req_flags_end1" not in state
    assert "_ver_forb_flags_end1" not in state
    assert "ms_req_flags_end1_v0" not in state
    assert "keep_me_end2" in state


@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_tab_endings_priority_caption(mock_st):
    """1-G-6 已知問題3: priority 下方應有常駐的五級語意說明 caption。"""
    mock_st.columns.side_effect = lambda x, **kwargs: [MagicMock() for _ in range(len(x))] if isinstance(x, list) else [MagicMock() for _ in range(x)]
    mock_st.button.return_value = False
    mock_st.text_input.return_value = ""
    state = dict(_BASE_FLAGS_SESSION)
    state["endings"] = [{"ending_id": "end1", "title": "End 1", "ending_type": "good", "target_character_id": None, "description": "", "required_flags": [], "required_stats": [], "forbidden_flags": [], "priority": "normal", "route_tags": []}]
    mock_st.session_state = state

    _tab_endings()

    caption_calls = [str(call) for call in mock_st.caption.call_args_list]
    # 檢查是否有印出包含 "優先權由高到低" 的 caption
    assert any("優先權由高到低" in call for call in caption_calls)
