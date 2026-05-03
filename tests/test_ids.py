from sandbox_dating_sim.core.ids import is_valid_id, normalize_id, _slugify_label, _make_unique_id

def test_valid_id():
    assert is_valid_id("sophie_route_started")

def test_invalid_id_starts_with_number():
    assert not is_valid_id("1sophie")

def test_invalid_id_contains_chinese():
    assert not is_valid_id("蘇菲")

def test_normalize_id():
    assert normalize_id("Summer City") == "summer_city"

def test_normalize_id_with_hyphens():
    assert normalize_id("cool-place-123") == "cool_place_123"

def test_normalize_id_rejects_chinese():
    import pytest
    with pytest.raises(ValueError, match="contains Chinese characters"):
        normalize_id("Summer夏日")

def test_slugify_label_chinese():
    assert _slugify_label("咖啡廳") == "ka_fei_ting"

def test_slugify_label_english():
    assert _slugify_label("Cafe Shop") == "cafe_shop"

def test_slugify_label_empty():
    assert _slugify_label("") == "unnamed"
    assert _slugify_label("   ") == "unnamed"

def test_slugify_label_truncation():
    # 超過 8 個 token 應截斷
    label = "一二三四五六七八九十"
    # pinyin tokens: yi_er_san_si_wu_liu_qi_ba_jiu_shi
    result = _slugify_label(label)
    assert result == "yi_er_san_si_wu_liu_qi_ba"
    assert len(result.split("_")) == 8

def test_slugify_label_punctuation():
    assert _slugify_label("商店、超市、藥局") == "shang_dian_chao_shi_yao_ju"
    assert _slugify_label("你好，世界！") == "ni_hao_shi_jie"

def test_make_unique_id_no_conflict():
    assert _make_unique_id("咖啡廳", "loc_", "unnamed", set()) == "loc_ka_fei_ting"

def test_make_unique_id_with_conflict():
    existing = {"loc_ka_fei_ting"}
    assert _make_unique_id("咖啡廳", "loc_", "unnamed", existing) == "loc_ka_fei_ting_2"

def test_make_unique_id_sequential():
    existing = {"loc_ka_fei_ting", "loc_ka_fei_ting_2"}
    assert _make_unique_id("咖啡廳", "loc_", "unnamed", existing) == "loc_ka_fei_ting_3"

def test_make_unique_id_skips_occupied():
    # 測試「順序遞增取最小未占用」
    existing = {"loc_ka_fei_ting", "loc_ka_fei_ting_3"}
    assert _make_unique_id("咖啡廳", "loc_", "unnamed", existing) == "loc_ka_fei_ting_2"

def test_1g7_signature_stability():
    """1-G-7: 確認 _generate_system_id 簽章未被修改（1-G-3 回歸）。"""
    import inspect
    from sandbox_dating_sim.ui.streamlit_uiw import _generate_system_id
    sig = inspect.signature(_generate_system_id)
    assert "label" in sig.parameters
    assert len(sig.parameters) == 1

def test_1g7_fallback_unnamed():
    """1-G-7: 測試空白來源時產生 <prefix>unnamed。"""
    assert _make_unique_id("", "flag_", "unnamed", set()) == "flag_unnamed"
    assert _make_unique_id("   ", "loc_", "unnamed", set()) == "loc_unnamed"

def test_1g7_cross_type_isolation():
    """1-G-7: 測試跨類 prefix 隔離。"""
    # 已有 loc_lin_xiao_yu，新增角色「林小雨」應產生 ch_lin_xiao_yu 而非 ch_lin_xiao_yu_2
    existing = {"loc_lin_xiao_yu"}
    assert _make_unique_id("林小雨", "ch_", "unnamed", existing) == "ch_lin_xiao_yu"

def test_1g7_npc_auto_id():
    """1-G-7: 測試 NPC 中文名稱自動產生 ID。"""
    assert _make_unique_id("蘇菲", "ch_", "unnamed", set()) == "ch_su_fei"
    assert _make_unique_id("林小雨", "ch_", "unnamed", set()) == "ch_lin_xiao_yu"

def test_1g7_ending_auto_id():
    """1-G-7: 測試結局標題自動產生 ID。"""
    assert _make_unique_id("完美的約會", "end_", "unnamed", set()) == "end_wan_mei_de_yue_hui"
