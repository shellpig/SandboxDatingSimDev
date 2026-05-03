import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
import re

# Initialize session_state before imports
if not hasattr(st, "session_state") or st.session_state is None:
    st.session_state = {}

from sandbox_dating_sim.ui.streamlit_uiw import _tab_locations, _tab_characters, _tab_flags, _tab_endings

def setup_basic_state():
    return {
        "locations": [],
        "characters": [],
        "flags": [],
        "status_flags": [],
        "endings": [],
        "world_id": "test_game",
    }

def apply_common_mocks(mock_st):
    mock_st.columns.side_effect = lambda x, **kwargs: [MagicMock() for _ in range(len(x))] if isinstance(x, list) else [MagicMock() for _ in range(x)]
    mock_st.button.return_value = False
    mock_st.text_input.side_effect = lambda label, value="", **kwargs: mock_st.session_state.get(kwargs.get("key"), value)
    # text_area 必須回傳 str（default value），否則 _tab_flags 會把 MagicMock 餵進 yaml.safe_load 造成 PyYAML Reader 死迴圈
    mock_st.text_area.side_effect = lambda label, value="", **kwargs: mock_st.session_state.get(kwargs.get("key"), value)
    mock_st.selectbox.side_effect = lambda label, options, **kwargs: options[0] if options else None
    mock_st.multiselect.side_effect = lambda label, options, **kwargs: kwargs.get("default", [])
    mock_st.form_submit_button.return_value = False
    mock_st.checkbox.return_value = True

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g7_auto_id_location(mock_st):
    """測試地點自動 ID 產生。"""
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "add_loc_name": "咖啡廳",
        "add_loc_id": "", 
        "add_loc_type": "standalone",
    })
    mock_st.form_submit_button.return_value = True

    _tab_locations()

    assert len(mock_st.session_state["locations"]) == 1
    assert mock_st.session_state["locations"][0]["location_id"] == "loc_ka_fei_ting"
    mock_st.caption.assert_any_call("已自動產生 ID: `loc_ka_fei_ting`")

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g7_suffix_avoidance_location(mock_st):
    """測試地點自動 ID 避讓 (Suffix Avoidance)。"""
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "locations": [{"location_id": "loc_ka_fei_ting", "name": "舊咖啡廳", "location_type": "standalone"}],
        "add_loc_name": "咖啡廳",
        "add_loc_id": "", 
        "add_loc_type": "standalone",
    })
    mock_st.form_submit_button.return_value = True

    _tab_locations()

    assert len(mock_st.session_state["locations"]) == 2
    assert mock_st.session_state["locations"][1]["location_id"] == "loc_ka_fei_ting_2"
    mock_st.caption.assert_any_call("已自動產生 ID: `loc_ka_fei_ting_2`")

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g7_auto_id_flag_from_desc(mock_st):
    """測試 Flag 從說明自動產生 ID。"""
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "add_f_id": "", 
    })
    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "新增 Flag"
    
    # 說明欄位在 Flag 表單沒有 key，我們透過 label 攔截
    def mock_text_input(label, value="", **kwargs):
        if label == "說明": return "完成蘇菲的約會"
        if label == "初始值": return "false"
        return mock_st.session_state.get(kwargs.get("key"), value)
    mock_st.text_input.side_effect = mock_text_input
    mock_st.selectbox.return_value = "boolean"

    _tab_flags()

    assert len(mock_st.session_state["flags"]) == 1
    assert mock_st.session_state["flags"][0]["flag_id"] == "flag_wan_cheng_su_fei_de_yue_hui"

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g7_protagonist_conflict_avoidance(mock_st):
    """測試 protagonist ID 被納入唯一性檢查，避免衝突。"""
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "add_loc_name": "主角", 
        "add_loc_id": "protagonist", 
    })
    mock_st.form_submit_button.return_value = True

    _tab_locations()

    # 檢查是否呼叫過 error。由於編碼問題，我們只檢查子字串或部分 match
    error_found = False
    for call in mock_st.error.call_args_list:
        if "protagonist" in str(call) and "衝突" in str(call):
            error_found = True
    assert error_found
    assert len(mock_st.session_state["locations"]) == 0

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g7_template_suffix_avoidance(mock_st):
    """測試套用模板時自動避讓。"""
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    # 學校模板建議 ID 為 school
    mock_st.session_state["locations"] = [{"location_id": "school", "name": "舊學校", "location_type": "container"}]
    mock_st.button.side_effect = lambda label, **kwargs: label == "套用模板"
    mock_st.selectbox.return_value = 0 # 學校模板

    _tab_locations()

    # 應產生 school_2 避讓
    assert mock_st.session_state["locations"][1]["location_id"] == "school_2"
    # 子地點也應隨之避讓 (school_2_classroom)
    sub_ids = [l["location_id"] for l in mock_st.session_state["locations"][2:]]
    assert "school_2_classroom" in sub_ids

@patch("sandbox_dating_sim.ui.streamlit_uiw.st")
def test_1g7_auto_id_status_flag(mock_st):
    """測試狀態旗標自動 ID 產生 (應帶 status_ prefix)。"""
    apply_common_mocks(mock_st)
    mock_st.session_state = setup_basic_state()
    mock_st.session_state.update({
        "add_sf_id": "",
    })
    mock_st.button.side_effect = lambda label, *args, **kwargs: label == "新增 Status Flag"
    mock_st.multiselect.side_effect = lambda label, options, **kwargs: ["protagonist", "on_time_advance"]
    
    def mock_text_input(label, value="", **kwargs):
        if label == "顯示名稱": return "過勞"
        return mock_st.session_state.get(kwargs.get("key"), value)
    mock_st.text_input.side_effect = mock_text_input

    _tab_flags()

    print("ST ERROR CALLS:", mock_st.error.call_args_list)
    assert len(mock_st.session_state["status_flags"]) == 1
    assert mock_st.session_state["status_flags"][0]["status_id"] == "status_guo_lao"
