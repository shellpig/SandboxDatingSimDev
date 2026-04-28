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
    PROTAGONIST_SECRET_PRESETS,
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
        PROTAGONIST_SECRET_PRESETS,
    ],
)
def test_protagonist_presets_have_usable_range_and_labels(presets):
    """1-G-1 主角預設選項每組應提供 6-12 個可點選項目。"""
    assert 6 <= len(presets) <= 12
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
