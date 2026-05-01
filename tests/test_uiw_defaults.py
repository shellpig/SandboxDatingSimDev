import pytest
from sandbox_dating_sim.uiw.defaults import (
    STYLE_PRESETS,
    LOCATION_TEMPLATES,
    SUB_LOCATION_TEMPLATES,
    EMOTION_PRESETS,
    COSTUME_PRESETS,
    POSITION_PRESETS,
    PROTAGONIST_OCCUPATION_PRESETS,
    PROTAGONIST_PERSONALITY_PRESETS,
    SECRET_PRESETS,
    DEBT_TIER_PRESETS,
    GENDER_OPTIONS,
    ORIENTATION_OPTIONS,
    ROLE_OPTIONS,
    CHARACTER_PERSONALITY_TAG_PRESETS,
    PROTAGONIST_DEFAULT_AGE,
)
from sandbox_dating_sim.core.ids import is_valid_id


def test_style_presets_have_id_and_label():
    """每個 style preset 都有 id 與中文 label。"""
    for preset in STYLE_PRESETS:
        assert "id" in preset, f"preset 缺少 id: {preset}"
        assert "label" in preset, f"preset 缺少 label: {preset}"
        assert isinstance(preset["id"], str)
        assert isinstance(preset["label"], str)
        assert len(preset["label"]) > 0


def test_location_templates_have_required_fields():
    """每個 location template 都有 template_id、label、location_type。"""
    for tpl in LOCATION_TEMPLATES:
        assert "template_id" in tpl, f"template 缺少 template_id: {tpl}"
        assert "label" in tpl, f"template 缺少 label: {tpl}"
        assert "location_type" in tpl, f"template 缺少 location_type: {tpl}"


def test_container_templates_suggest_sub_locations():
    """container template 必須提供 suggested_sub_locations。"""
    containers = [t for t in LOCATION_TEMPLATES if t["location_type"] == "container"]
    assert len(containers) > 0, "應至少有一個 container template"
    for tpl in containers:
        assert "suggested_sub_locations" in tpl, f"container {tpl['template_id']} 缺少 suggested_sub_locations"
        assert len(tpl["suggested_sub_locations"]) > 0, f"container {tpl['template_id']} 的 suggested_sub_locations 為空"


def test_template_ids_are_unique():
    """template_id 不可重複。"""
    all_ids = [t["template_id"] for t in LOCATION_TEMPLATES]
    all_ids.extend(t["template_id"] for t in SUB_LOCATION_TEMPLATES)
    assert len(all_ids) == len(set(all_ids)), f"有重複的 template_id: {[x for x in all_ids if all_ids.count(x) > 1]}"


def test_template_ids_are_valid_canonical_ids():
    """template_id 與建議 location_id 必須符合 ID 規則。"""
    for tpl in LOCATION_TEMPLATES:
        assert is_valid_id(tpl["template_id"]), f"template_id 不合法: {tpl['template_id']}"
        if "location_id_suggestion" in tpl:
            assert is_valid_id(tpl["location_id_suggestion"]), f"location_id_suggestion 不合法: {tpl['location_id_suggestion']}"
    for tpl in SUB_LOCATION_TEMPLATES:
        assert is_valid_id(tpl["template_id"]), f"template_id 不合法: {tpl['template_id']}"
        if "location_id_suffix" in tpl:
            assert is_valid_id(tpl["location_id_suffix"]), f"location_id_suffix 不合法: {tpl['location_id_suffix']}"


def test_emotion_presets_have_id_and_label():
    """每個 emotion preset 都有 id 與中文 label。"""
    assert len(EMOTION_PRESETS) > 0
    for preset in EMOTION_PRESETS:
        assert "id" in preset and "label" in preset


def test_costume_presets_have_id_and_label():
    """每個 costume preset 都有 id 與中文 label。"""
    assert len(COSTUME_PRESETS) > 0
    for preset in COSTUME_PRESETS:
        assert "id" in preset and "label" in preset


def test_position_presets_have_id_and_label():
    """每個 position preset 都有 id 與中文 label。"""
    assert len(POSITION_PRESETS) > 0
    for preset in POSITION_PRESETS:
        assert "id" in preset and "label" in preset


@pytest.mark.parametrize(
    "presets",
    [
        PROTAGONIST_OCCUPATION_PRESETS,
        PROTAGONIST_PERSONALITY_PRESETS,
        SECRET_PRESETS,
    ],
)
def test_protagonist_presets_have_usable_range_and_labels(presets):
    """1-G-3 主角預設選項每組應提供 6-16 個可點選項目。"""
    assert 6 <= len(presets) <= 16
    ids = [preset["id"] for preset in presets]
    assert len(ids) == len(set(ids))
    for preset in presets:
        assert is_valid_id(preset["id"])
        assert isinstance(preset["label"], str)
        assert len(preset["label"]) > 0


def test_debt_tier_presets_have_ids_labels_and_debt_values():
    """債務等級模式必須能映射到 canonical Debt 數值。"""
    assert len(DEBT_TIER_PRESETS) >= 4
    tier_ids = [tier["id"] for tier in DEBT_TIER_PRESETS]
    assert "none" in tier_ids
    assert len(tier_ids) == len(set(tier_ids))
    for tier in DEBT_TIER_PRESETS:
        assert is_valid_id(tier["id"])
        assert isinstance(tier["label"], str)
        assert isinstance(tier["debt"], int)
        assert tier["debt"] >= 0


@pytest.mark.parametrize(
    "enum_options",
    [
        GENDER_OPTIONS,
        ORIENTATION_OPTIONS,
        ROLE_OPTIONS,
    ],
)
def test_enum_options_have_valid_ids_and_labels(enum_options):
    """1-G-2: 主角/角色 enum 選項都有 id 與 label，且 ID 符合 canonical ID 規則。"""
    assert len(enum_options) > 0
    ids = [opt["id"] for opt in enum_options]
    assert len(ids) == len(set(ids)), "enum 選項 ID 不可重複"
    for opt in enum_options:
        assert is_valid_id(opt["id"]), f"enum 選項 ID 不合法: {opt['id']}"
        assert isinstance(opt["label"], str)
        assert len(opt["label"]) > 0


def test_character_personality_tag_presets():
    """1-G-2: 角色性格標籤預設選項 ID 不重複，且符合 canonical ID 規則。"""
    assert len(CHARACTER_PERSONALITY_TAG_PRESETS) > 0
    ids = [tag["id"] for tag in CHARACTER_PERSONALITY_TAG_PRESETS]
    assert len(ids) == len(set(ids)), "性格標籤預設選項 ID 不可重複"
    for tag in CHARACTER_PERSONALITY_TAG_PRESETS:
        assert is_valid_id(tag["id"]), f"性格標籤 ID 不合法: {tag['id']}"
        assert isinstance(tag["label"], str)
        assert len(tag["label"]) > 0


def test_protagonist_default_age():
    """1-G-2: 主角預設年齡應驗證其值為 29。"""
    assert PROTAGONIST_DEFAULT_AGE == 29


# --- 1-G-4 Specific Tests ---

def test_1_g_4_required_templates_exist():
    """1-G-4: 必須包含指定新增與保留的模板。"""
    tpl_ids = [t["template_id"] for t in LOCATION_TEMPLATES]
    required = [
        "school_container", "shopping_street_container", "station_area_container",
        "home_standalone", "cinema_standalone", "convenience_store_standalone",
        "company_standalone", "park_standalone", "amusement_park_container",
        "department_store_container", "hospital_standalone", "seaside_container",
        "hot_spring_inn_container", "night_market_standalone", "gym_standalone",
        "public_library", "police_station_standalone", "art_museum_standalone",
        "riverside_walk_standalone", "bar_standalone"
    ]
    for req in required:
        assert req in tpl_ids, f"缺少要求的新增/保留模板: {req}"


def test_1_g_4_station_area_sub_locations():
    """1-G-4: 車站周邊必須產生月台/站前廣場/地下街。"""
    station = next((t for t in LOCATION_TEMPLATES if t["template_id"] == "station_area_container"), None)
    assert station is not None
    subs = station.get("suggested_sub_locations", [])
    assert "platform" in subs
    assert "station_square" in subs
    assert "underground_mall" in subs


def test_1_g_4_sub_location_uses_suffix():
    """1-G-4: 子地點模板必須定義 location_id_suffix，藉以在 UI 組成 <parent>_<suffix>。"""
    for sub in SUB_LOCATION_TEMPLATES:
        assert "location_id_suffix" in sub, f"子地點 {sub['template_id']} 缺少 location_id_suffix"
        assert "location_id_suggestion" not in sub, f"子地點 {sub['template_id']} 不應有獨立的 location_id_suggestion"


def test_1_g_4_time_slots_requirement():
    """1-G-4: standalone 與 sub_location 必須有 available_time_slots，container 則不強制。"""
    for tpl in LOCATION_TEMPLATES:
        if tpl["location_type"] == "standalone":
            assert "available_time_slots" in tpl, f"standalone 模板 {tpl['template_id']} 缺少 available_time_slots"
    for sub in SUB_LOCATION_TEMPLATES:
        assert "available_time_slots" in sub, f"sub_location 模板 {sub['template_id']} 缺少 available_time_slots"


def test_1_g_4_convenience_store_name_distinction():
    """1-G-4: 獨立便利商店與商店街便利商店，UI 顯示必須區分。"""
    standalone = next((t for t in LOCATION_TEMPLATES if t["template_id"] == "convenience_store_standalone"), None)
    assert standalone is not None
    assert standalone["label"] == "便利商店(獨立)"

    sub_loc = next((t for t in SUB_LOCATION_TEMPLATES if t["template_id"] == "convenience_store_sub"), None)
    assert sub_loc is not None
    assert sub_loc["label"] == "便利商店(商店街內)"


def test_1_g_4_page_labels_order():
    """1-G-4: 頁面順序必須為 World -> Protagonist -> Locations -> Characters -> Flags -> Review"""
    from sandbox_dating_sim.ui.streamlit_uiw import PAGE_LABELS
    expected = [
        "世界觀與曆法(World)",
        "主角設定(Protagonist)",
        "地點與地圖(Locations)",
        "角色設定(Characters)",
        "旗標/狀態/結局(Flags/Status/Endings)",
        "預覽與匯出(Review & Export)",
    ]
    assert PAGE_LABELS == expected
