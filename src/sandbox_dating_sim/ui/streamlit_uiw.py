"""Interactive User Input Wizard prototype (Streamlit)."""

import streamlit as st
import yaml
import re
import pypinyin
from datetime import date
from pathlib import Path

from sandbox_dating_sim.schema.setup import (
    SetupPackage, World, Protagonist, InitialStats, Location, SemanticChoice,
    Character, ScheduleEntry, AssetOption, FlagDef, StatusFlag,
    StatusDuration, Ending,
)
from sandbox_dating_sim.uiw.linter import UIWLinter
from sandbox_dating_sim.pipeline.setup_exporter import SetupPackageExporter
from sandbox_dating_sim.uiw.defaults import (
    STYLE_PRESETS, LOCATION_TEMPLATES, SUB_LOCATION_TEMPLATES,
    EMOTION_PRESETS, COSTUME_PRESETS, POSITION_PRESETS,
    PROTAGONIST_OCCUPATION_PRESETS, PROTAGONIST_PERSONALITY_PRESETS,
    SECRET_PRESETS, DEBT_TIER_PRESETS,
    GENDER_OPTIONS, ORIENTATION_OPTIONS, ROLE_OPTIONS,
    CHARACTER_PERSONALITY_TAG_PRESETS, PROTAGONIST_DEFAULT_AGE,
)


PAGE_LABELS = [
    "世界觀與曆法(World)",
    "主角設定(Protagonist)",
    "角色設定(Characters)",
    "地點與地圖(Locations)",
    "旗標/狀態/結局(Flags/Status/Endings)",
    "預覽與匯出(Review & Export)",
]


def _init_state():
    """
    初始化 Streamlit session_state 中的預設資料結構。
    這些預設值作為表單的初始輸入，避免在渲染期間發生 KeyError。
    """
    defaults = {
        "world_id": "my_game", "title": "我的遊戲",
        "start_date": date(2026, 4, 27), "end_date": date(2026, 5, 26),
        "global_style": [],
        "protag_id": "protagonist", "protag_name": "主角",
        "protag_gender": "male", "protag_age": PROTAGONIST_DEFAULT_AGE,
        "protag_occupation": {"id": "student", "label": "學生"},
        "protag_personality": {"id": "kind_but_tired", "label": "善良但疲憊"},
        "protag_secrets": [],
        "debt_tier": "none",
        "active_page_label": PAGE_LABELS[0],
        "INT": 5, "CHA": 5, "STR": 5, "MORAL": 5, "Cash": 3000, "Debt": 0,
        "locations": [], "characters": [], "flags": [],
        "status_flags": [], "endings": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v



def _preset_label(value: str, presets: list[dict]) -> str:
    """將 canonical ID 轉回 UI 顯示用中文 label。"""
    for preset in presets:
        if preset["id"] == value:
            return preset["label"]
    return value


def _preset_button_grid(state_key: str, presets: list[dict], key_prefix: str, columns: int = 4) -> None:
    """用按鈕顯示一組預設選項，點選後寫入 session state。"""
    cols = st.columns(columns)
    for i, preset in enumerate(presets):
        with cols[i % columns]:
            if st.button(preset["label"], key=f"{key_prefix}_{preset['id']}"):
                st.session_state[state_key] = preset["id"]
                st.rerun()



def _generate_system_id(label: str) -> str:
    """從中文標籤產生合法的英文/拼音 ID（^[a-z][a-z0-9_]*$）"""
    if not label:
        return "custom_empty"
    if re.match(r"^[a-zA-Z0-9_ ]+$", label):
        candidate = re.sub(r"[^a-z0-9_]", "", label.strip().lower().replace(" ", "_"))
    else:
        pinyin_list = pypinyin.lazy_pinyin(label)
        pinyin_str = "_".join(pinyin_list)
        candidate = re.sub(r"[^a-z0-9_]", "", pinyin_str.lower())
    # 移除開頭的數字與底線，確保以字母開頭
    candidate = re.sub(r"^[0-9_]+", "", candidate)
    if not candidate:
        candidate = "custom_id"
    return candidate

def _semantic_choice_input(
    label: str,
    state_key: str,
    presets: list[dict],
    allow_multiple: bool = False,
    max_items: int | None = None,
    separate_none: bool = False,
) -> None:
    """語意型欄位通用輸入元件。
    separate_none=True：將 id=='none' 的選項獨立放在最下面一行，
    且點選時會同時清除其他已選項目的 edit_id session state。
    """
    st.subheader(label)

    # 分離 none 選項
    if separate_none:
        main_presets = [p for p in presets if p["id"] != "none"]
        none_presets  = [p for p in presets if p["id"] == "none"]
    else:
        main_presets = presets
        none_presets  = []

    # ── 主要預設按鈕（4欄） ──
    cols = st.columns(4)
    for i, preset in enumerate(main_presets):
        with cols[i % 4]:
            if st.button(preset["label"], key=f"btn_{state_key}_{preset['id']}"):
                new_item = {"id": preset["id"], "label": preset["label"]}
                if allow_multiple:
                    if new_item not in st.session_state[state_key]:
                        # 若目前選了 none，清掉再加入
                        st.session_state[state_key] = [
                            item for item in st.session_state[state_key] if item["id"] != "none"
                        ]
                        if max_items is None or len(st.session_state[state_key]) < max_items:
                            st.session_state[state_key].append(new_item)
                else:
                    st.session_state[state_key] = new_item
                    st.session_state[f"edit_id_{state_key}"] = new_item["id"]
                st.rerun()

    # ── 「沒有秘密」等 none 選項：獨立一行 ──
    for preset in none_presets:
        if st.button(f"⊘ {preset['label']}", key=f"btn_{state_key}_{preset['id']}", use_container_width=False):
            if allow_multiple:
                # 清空清單（不放入 none 項目）+ 遞增 reset_ver
                # → 下方顯示區不渲染任何 text_input
                # → 後續新增項目使用全新 widget key，值從 value= 取得而非舊 session state
                reset_key = f"_rst_{state_key}"
                st.session_state[reset_key] = st.session_state.get(reset_key, 0) + 1
                st.session_state[state_key] = []
            else:
                st.session_state[state_key] = {"id": preset["id"], "label": preset["label"]}
                st.session_state[f"edit_id_{state_key}"] = preset["id"]
            st.rerun()

    # ── 自訂輸入（半寬 + Y 軸對齊按鈕） ──
    col_in, col_btn, _ = st.columns([2, 1, 3], vertical_alignment="bottom")
    with col_in:
        custom_label = st.text_input(f"自訂{label}", key=f"custom_{state_key}")
    with col_btn:
        add_clicked = st.button("選擇", key=f"add_{state_key}")

    if add_clicked and custom_label:
        found_preset = next((p for p in presets if p["label"] == custom_label), None)
        sys_id = found_preset["id"] if found_preset else _generate_system_id(custom_label)
        new_item = {"id": sys_id, "label": custom_label}
        if allow_multiple:
            if new_item not in st.session_state[state_key]:
                st.session_state[state_key] = [
                    item for item in st.session_state[state_key] if item["id"] != "none"
                ]
                if max_items is None or len(st.session_state[state_key]) < max_items:
                    st.session_state[state_key].append(new_item)
        else:
            st.session_state[state_key] = new_item
            st.session_state[f"edit_id_{state_key}"] = new_item["id"]
        st.rerun()

    # ── 目前選擇顯示 ──
    st.write("目前選擇：")
    if allow_multiple:
        # reset_ver 改變時，text_input key 也改變，Streamlit 強制用 value= 重建 widget
        reset_ver = st.session_state.get(f"_rst_{state_key}", 0)
        for i, item in enumerate(list(st.session_state[state_key])):
            cc1, cc2, cc3 = st.columns([1, 4, 1], vertical_alignment="center")
            with cc1:
                st.write(f"**{item['label']}**")
            with cc2:
                item["id"] = st.text_input(
                    "系統 ID", value=item["id"],
                    key=f"edit_id_{state_key}_{i}_v{reset_ver}", label_visibility="collapsed"
                )
            with cc3:
                if st.button("✕", key=f"del_{state_key}_{i}_v{reset_ver}"):
                    st.session_state[state_key].pop(i)
                    st.rerun()
    else:
        current_item = st.session_state.get(state_key)
        if current_item and isinstance(current_item, dict):
            if f"edit_id_{state_key}" not in st.session_state:
                st.session_state[f"edit_id_{state_key}"] = current_item["id"]
            cc1, cc2 = st.columns([1, 4], vertical_alignment="center")
            with cc1:
                st.write(f"**{current_item['label']}**")
            with cc2:
                current_item["id"] = st.text_input(
                    "系統 ID", key=f"edit_id_{state_key}", label_visibility="collapsed"
                )


def _go_to_page(label: str) -> None:
    """切換目前設定頁。"""
    st.session_state["active_page_label"] = label


def _next_page_button(current_label: str) -> None:
    """在頁面底部顯示前往下一個設定項目的按鈕。"""
    current_index = PAGE_LABELS.index(current_label)
    if current_index < len(PAGE_LABELS) - 1:
        next_label = PAGE_LABELS[current_index + 1]
        st.divider()
        st.button("下一頁", on_click=_go_to_page, args=(next_label,), use_container_width=True)


def _build_package() -> SetupPackage:
    """
    從目前的 session_state 構建出完整的 SetupPackage Pydantic 模型。
    這會在每次點擊驗證、預覽或匯出時被呼叫，用以確保資料符合 Canonical Schema 契約。
    """
    s = st.session_state
    
    # 建立世界設定模型
    world = World(
        world_id=s["world_id"], title=s["title"],
        start_date=s["start_date"], end_date=s["end_date"],
        time_slots=["morning", "afternoon", "evening"],
        global_style=[SemanticChoice(**x) for x in s["global_style"]],
    )
    
    # 建立主角與初始數值模型
    protag = Protagonist(
        protagonist_id=s["protag_id"], name=s["protag_name"],
        gender=s["protag_gender"], age=s["protag_age"],
        occupation=SemanticChoice(**s["protag_occupation"]), personality=SemanticChoice(**s["protag_personality"]),
        secrets=[SemanticChoice(**x) for x in s.get("protag_secrets", [])],
        initial_stats=InitialStats(
            INT=s["INT"], CHA=s["CHA"], STR=s["STR"],
            MORAL=s["MORAL"], Cash=s["Cash"], Debt=s["Debt"],
        ),
    )
    
    # 組合並回傳完整的 SetupPackage
    return SetupPackage(
        world=world, protagonist=protag,
        locations=[Location(**loc) for loc in s["locations"]],
        characters=[Character(**ch) for ch in s["characters"]],
        flags=[FlagDef(**f) for f in s["flags"]],
        status_flags=[StatusFlag(**sf) for sf in s["status_flags"]],
        endings=[Ending(**e) for e in s["endings"]],
    )


def _visitable_location_ids() -> list[str]:
    """
    回傳目前所有設定為可進入（is_visitable=True）的地點 ID 列表。
    這用於在設定角色行程 (Schedule) 時過濾合法的地點選單。
    """
    return [
        loc["location_id"] for loc in st.session_state["locations"]
        if loc.get("is_visitable", False)
    ]


def _tab_world():
    """渲染「世界觀與曆法」設定分頁的 UI 元件。"""
    st.header("1. 世界觀與曆法")
    
    # 基本設定欄位
    st.session_state["world_id"] = st.text_input("遊戲識別碼", st.session_state["world_id"])
    st.session_state["title"] = st.text_input("遊戲標題", st.session_state["title"])
    st.session_state["start_date"] = st.date_input("開始日期", st.session_state["start_date"])
    st.session_state["end_date"] = st.date_input("結束日期", st.session_state["end_date"])

    _semantic_choice_input("風格關鍵字", "global_style", STYLE_PRESETS, allow_multiple=True)

    _next_page_button(PAGE_LABELS[0])


def _tab_protagonist():
    """渲染「主角設定」分頁的 UI 元件，包含基本身分與初始六維數值。"""
    st.header("2. 主角設定")
    
    # 收集主角基本資料 (主角 ID 依 1-G-2 需求不再顯示，固定為 protagonist)
    st.session_state["protag_name"] = st.text_input("主角姓名", st.session_state["protag_name"])
    
    gender_ids = [g["id"] for g in GENDER_OPTIONS]
    selected_gender = st.selectbox(
        "性別",
        gender_ids,
        index=gender_ids.index(st.session_state["protag_gender"]) if st.session_state["protag_gender"] in gender_ids else 0,
        format_func=lambda value: _preset_label(value, GENDER_OPTIONS)
    )
    st.session_state["protag_gender"] = selected_gender
    st.session_state["protag_age"] = st.number_input("年齡", 1, 100, st.session_state["protag_age"])
    _semantic_choice_input("職業", "protag_occupation", PROTAGONIST_OCCUPATION_PRESETS, allow_multiple=False)

    _semantic_choice_input("性格描述", "protag_personality", PROTAGONIST_PERSONALITY_PRESETS, allow_multiple=False)

    _semantic_choice_input("主角的秘密 (最多3個)", "protag_secrets", SECRET_PRESETS, allow_multiple=True, max_items=3, separate_none=True)

    st.subheader("初始數值")
    # 將數值輸入切分為三欄顯示
    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state["INT"] = st.slider("INT 智力", 1, 10, st.session_state["INT"])
        st.session_state["CHA"] = st.slider("CHA 魅力", 1, 10, st.session_state["CHA"])
    with c2:
        st.session_state["STR"] = st.slider("STR 勇氣", 1, 10, st.session_state["STR"])
        st.session_state["MORAL"] = st.slider("MORAL 道德", 1, 10, st.session_state["MORAL"])
    with c3:
        st.session_state["Cash"] = st.number_input("初始現金", 0, 100000, st.session_state["Cash"])
        debt_tier_ids = [tier["id"] for tier in DEBT_TIER_PRESETS]
        if st.session_state["debt_tier"] not in debt_tier_ids:
            st.session_state["debt_tier"] = "none"
        selected_debt_tier = st.selectbox(
            "初始債務等級",
            debt_tier_ids,
            index=debt_tier_ids.index(st.session_state["debt_tier"]),
            format_func=lambda value: _preset_label(value, DEBT_TIER_PRESETS),
        )
        st.session_state["debt_tier"] = selected_debt_tier
        selected_tier = next(tier for tier in DEBT_TIER_PRESETS if tier["id"] == selected_debt_tier)
        st.session_state["Debt"] = selected_tier["debt"]
        st.metric("初始債務", st.session_state["Debt"])

    _next_page_button(PAGE_LABELS[1])


def _tab_locations():
    """
    渲染「地點與地圖」分頁。
    允許使用者透過套用預設模板（如學校、商店街）來快速產生父子地點，
    或是透過表單手動新增 container、sub_location 或 standalone 地點。
    """
    st.header("3. 地點與地圖")

    # --- 地點清單 ---
    if st.session_state["locations"]:
        st.subheader("目前地點")
        for i, loc in enumerate(st.session_state["locations"]):
            parent = f" (父: {loc['parent_location_id']})" if loc.get("parent_location_id") else ""
            label = f"{loc['name']} [{loc['location_type']}]{parent}"
            with st.expander(label):
                st.json(loc)
                if st.button(f"刪除 {loc['location_id']}", key=f"del_loc_{i}"):
                    st.session_state["locations"].pop(i)
                    st.rerun()  # 重新執行以更新畫面

    # --- 套用模板 ---
    st.subheader("套用地點模板")
    tpl_labels = [f"{t['label']} ({t['location_type']})" for t in LOCATION_TEMPLATES]
    tpl_idx = st.selectbox("選擇模板", range(len(LOCATION_TEMPLATES)), format_func=lambda i: tpl_labels[i])
    
    if st.button("套用模板"):
        tpl = LOCATION_TEMPLATES[tpl_idx]
        loc_id = tpl.get("location_id_suggestion", tpl["template_id"])
        
        # 建立主要父地點（或獨立地點）
        new_loc = {
            "location_id": loc_id, "name": tpl["label"],
            "location_type": tpl["location_type"],
            "parent_location_id": None,
            "is_visitable": tpl.get("is_visitable", False),
            "base_cost": tpl.get("base_cost", 0),
            "available_time_slots": tpl.get("available_time_slots", ["morning", "afternoon"]),
            "tags": tpl.get("tags", []),
            "empty_behavior": tpl.get("empty_behavior", "show_empty"),
        }
        st.session_state["locations"].append(new_loc)
        
        # 根據模板中的建議，自動建立對應的子地點
        for sub_id in tpl.get("suggested_sub_locations", []):
            sub_tpl = next((s for s in SUB_LOCATION_TEMPLATES if s["template_id"] == sub_id), None)
            if sub_tpl:
                sub_loc = {
                    "location_id": f"{loc_id}_{sub_tpl['location_id_suffix']}",
                    "name": sub_tpl["label"],
                    "location_type": "sub_location",
                    "parent_location_id": loc_id,
                    "is_visitable": True,
                    "base_cost": 0,
                    "available_time_slots": sub_tpl.get("available_time_slots", ["morning", "afternoon"]),
                    "tags": sub_tpl.get("tags", []),
                    "empty_behavior": "show_empty",
                }
                st.session_state["locations"].append(sub_loc)
        st.rerun()

    # --- 手動新增 ---
    st.subheader("手動新增地點")
    with st.form("add_location", clear_on_submit=True):
        loc_id = st.text_input("地點 ID (英文)")
        loc_name = st.text_input("地點名稱")
        loc_type = st.selectbox("類型", ["container", "sub_location", "standalone"])
        
        # 尋找現有的 container 以供 sub_location 選擇為父地點
        containers = [l["location_id"] for l in st.session_state["locations"] if l["location_type"] == "container"]
        parent = st.selectbox("父地點", [None] + containers)
        
        # container 預設不可直接進入
        is_visit = st.checkbox("可進入", value=loc_type != "container")
        slots = st.multiselect("可用時間段", ["morning", "afternoon", "evening"], default=["morning", "afternoon"])
        tags = st.text_input("標籤 (逗號分隔)")
        
        if st.form_submit_button("新增地點"):
            new_loc = {
                "location_id": loc_id, "name": loc_name,
                "location_type": loc_type,
                # 只有子地點才保存父地點 ID
                "parent_location_id": parent if loc_type == "sub_location" else None,
                "is_visitable": is_visit if loc_type != "container" else False,
                "base_cost": 0,
                "available_time_slots": slots,
                "tags": [t.strip() for t in tags.split(",") if t.strip()],
                "empty_behavior": "show_empty",
            }
            st.session_state["locations"].append(new_loc)
            st.rerun()

    _next_page_button(PAGE_LABELS[3])


def _tab_characters():
    """
    渲染「角色設定」分頁。
    包含角色的基本資訊、性格、白名單（表情、服裝、位置）設定，
    以及在角色下方建立其專屬行程 (Schedule) 的功能。
    """
    st.header("4. 角色設定")

    if st.session_state["characters"]:
        st.subheader("目前角色")
        for i, ch in enumerate(st.session_state["characters"]):
            with st.expander(f"{ch['display_name']} ({ch['character_id']})"):
                st.json(ch)
                if st.button(f"刪除 {ch['character_id']}", key=f"del_ch_{i}"):
                    st.session_state["characters"].pop(i)
                    st.rerun()

    st.subheader("新增角色")

    # ── 語意型欄位必須在 form 外使用 st.button，故先在 form 前渲染 ──
    if "temp_ch_tags" not in st.session_state:
        st.session_state["temp_ch_tags"] = []
    if "temp_ch_secrets" not in st.session_state:
        st.session_state["temp_ch_secrets"] = []
    _semantic_choice_input("性格標籤", "temp_ch_tags", CHARACTER_PERSONALITY_TAG_PRESETS, allow_multiple=True)
    _semantic_choice_input("角色秘密 (最多3個)", "temp_ch_secrets", SECRET_PRESETS, allow_multiple=True, max_items=3, separate_none=True)

    st.divider()
    with st.form("add_character", clear_on_submit=True):
        ch_id = st.text_input("角色 ID (英文)")
        ch_name = st.text_input("顯示名稱")

        gender_ids = [g["id"] for g in GENDER_OPTIONS]
        ch_gender = st.selectbox("性別", gender_ids, format_func=lambda x: _preset_label(x, GENDER_OPTIONS))

        orient_ids = [o["id"] for o in ORIENTATION_OPTIONS]
        ch_orient = st.multiselect("性取向", orient_ids, default=["heterosexual"], format_func=lambda x: _preset_label(x, ORIENTATION_OPTIONS))

        role_ids = [r["id"] for r in ROLE_OPTIONS]
        ch_role = st.selectbox("定位", role_ids, format_func=lambda x: _preset_label(x, ROLE_OPTIONS))

        ch_identity = st.text_input("身分描述")
        ch_favor = st.number_input("初始好感度", value=0)

        # 白名單多選（st.multiselect 可在 form 內使用）
        st.markdown("**表情白名單**")
        sel_emo = st.multiselect("選擇表情", [f"{e['label']} ({e['id']})" for e in EMOTION_PRESETS],
                                  default=[f"{e['label']} ({e['id']})" for e in EMOTION_PRESETS[:3]])
        st.markdown("**服裝白名單**")
        sel_cos = st.multiselect("選擇服裝", [f"{c['label']} ({c['id']})" for c in COSTUME_PRESETS],
                                  default=[f"{c['label']} ({c['id']})" for c in COSTUME_PRESETS[:2]])
        st.markdown("**位置白名單**")
        sel_pos = st.multiselect("選擇位置", [f"{p['label']} ({p['id']})" for p in POSITION_PRESETS],
                                  default=[f"{p['label']} ({p['id']})" for p in POSITION_PRESETS])

        if st.form_submit_button("新增角色"):
            def _parse_presets(selected, presets):
                return [{"id": p["id"], "label": p["label"]} for p in presets
                        if f"{p['label']} ({p['id']})" in selected]

            new_ch = {
                "character_id": ch_id, "display_name": ch_name,
                "gender": ch_gender, "orientation": ch_orient,
                "role": ch_role, "identity": ch_identity,
                "personality_tags": list(st.session_state["temp_ch_tags"]),
                "secrets": list(st.session_state["temp_ch_secrets"]),
                "initial_favor": ch_favor, "schedule": [],
                "allowed_emotions": _parse_presets(sel_emo, EMOTION_PRESETS),
                "allowed_costumes": _parse_presets(sel_cos, COSTUME_PRESETS),
                "allowed_positions": _parse_presets(sel_pos, POSITION_PRESETS),
            }
            st.session_state["temp_ch_tags"] = []
            st.session_state["temp_ch_secrets"] = []
            st.session_state["characters"].append(new_ch)
            st.rerun()

    # --- Schedule 行程管理 ---
    # 在角色建立後，可透過此區塊將行程綁定給對應角色
    if st.session_state["characters"]:
        st.subheader("新增角色行程")
        vis_locs = _visitable_location_ids()
        if not vis_locs:
            st.warning("尚無可進入地點，請先在地點頁建立。")
        else:
            ch_names = [ch["character_id"] for ch in st.session_state["characters"]]
            with st.form("add_schedule", clear_on_submit=True):
                sch_char = st.selectbox("角色", ch_names)
                sch_id = st.text_input("行程 ID (英文)")
                sch_day = st.selectbox("日期類型", ["weekday", "weekend", "holiday", "specific_date", "any"])
                sch_slot = st.selectbox("時間段", ["morning", "afternoon", "evening"])
                sch_loc = st.selectbox("地點", vis_locs)
                sch_prio = st.selectbox("優先權", ["normal", "route", "critical", "ambient"])
                sch_order = st.number_input("排序值 (越小越優先)", value=20)
                sch_cond = st.text_input("條件 (逗號分隔，可選)")
                
                if st.form_submit_button("新增行程"):
                    entry = {
                        "schedule_id": sch_id, "day_type": sch_day,
                        "time_slot": sch_slot, "location_id": sch_loc,
                        "priority": sch_prio, "schedule_order": int(sch_order),
                        "condition": [c.strip() for c in sch_cond.split(",") if c.strip()],
                    }
                    # 找到指定的角色，將行程加入其 schedule 列表中
                    for ch in st.session_state["characters"]:
                        if ch["character_id"] == sch_char:
                            ch["schedule"].append(entry)
                    st.rerun()

    _next_page_button(PAGE_LABELS[2])


def _tab_flags():
    """
    渲染「旗標、狀態與結局」分頁。
    用以定義影響遊戲流程的全域變數 (Flags)、持續性增益與減益狀態 (Status Flags)，
    以及用來判定遊戲破關條件的各種結局 (Endings)。
    """
    st.header("5. 旗標、狀態與結局")

    # --- Flags (全域變數) ---
    st.subheader("旗標 (Flags)")
    if st.session_state["flags"]:
        for i, f in enumerate(st.session_state["flags"]):
            st.write(f"• {f['flag_id']} ({f['type']}) = {f['initial_value']} — {f['description']}")
            
    with st.form("add_flag", clear_on_submit=True):
        f_id = st.text_input("Flag ID")
        f_type = st.selectbox("型別", ["boolean", "integer", "string", "enum"])
        f_val = st.text_input("初始值", "false")
        f_desc = st.text_input("說明")
        if st.form_submit_button("新增 Flag"):
            # 依據選擇的型別強制轉型初始值
            val = f_val
            if f_type == "boolean":
                val = f_val.lower() == "true"
            elif f_type == "integer":
                val = int(f_val)
            st.session_state["flags"].append({
                "flag_id": f_id, "type": f_type,
                "initial_value": val, "description": f_desc,
            })
            st.rerun()

    # --- Status Flags (狀態效果) ---
    st.subheader("狀態旗標 (Status Flags)")
    if st.session_state["status_flags"]:
        for sf in st.session_state["status_flags"]:
            st.write(f"• {sf['status_id']} — {sf['description']}")
            
    with st.form("add_status_flag", clear_on_submit=True):
        sf_id = st.text_input("Status ID")
        sf_label = st.text_input("顯示名稱")
        sf_target = st.text_input("作用對象", "protagonist")
        sf_effect_key = st.text_input("效果 key (例: block_time_slot)")
        sf_effect_val = st.text_input("效果 value (例: evening)")
        sf_dur_type = st.selectbox("持續類型", ["time_slots", "days", "until_event", "until_cleared", "permanent"])
        sf_dur_val = st.number_input("持續值", value=1)
        # 解除條件必須多選，且若是 permanent 仍需要合理設定或保留為空 (依 schema 而定)
        sf_clear = st.multiselect("解除條件", ["on_time_advance", "on_day_end", "on_rest", "on_item_used",
                                                "on_event_result", "on_location_visit", "manual_only"])
        sf_desc = st.text_input("說明")
        sf_perm_reason = st.text_input("永久原因（若 permanent）", "")
        
        if st.form_submit_button("新增 Status Flag"):
            entry = {
                "status_id": sf_id, "label": sf_label, "target": sf_target,
                "effect": [{sf_effect_key: sf_effect_val}] if sf_effect_key else [],
                "duration": {"type": sf_dur_type, "value": sf_dur_val if sf_dur_type != "permanent" else None},
                "clear_rule": sf_clear, "description": sf_desc,
            }
            if sf_perm_reason:
                entry["permanent_reason"] = sf_perm_reason
            st.session_state["status_flags"].append(entry)
            st.rerun()

    # --- Endings (結局定義) ---
    st.subheader("結局 (Endings)")
    if st.session_state["endings"]:
        for e in st.session_state["endings"]:
            st.write(f"• {e['ending_id']} — {e['title']}")
            
    with st.form("add_ending", clear_on_submit=True):
        e_id = st.text_input("Ending ID")
        e_title = st.text_input("結局標題")
        e_type = st.text_input("結局類型 (例: character_good)")
        ch_ids = [ch["character_id"] for ch in st.session_state["characters"]]
        e_target = st.selectbox("關聯角色", [None, "global"] + ch_ids)
        e_desc = st.text_input("結局描述")
        e_req_flags = st.text_input("required_flags (逗號分隔)")
        e_req_stats = st.text_input("required_stats (逗號分隔)")
        e_forb_flags = st.text_input("forbidden_flags (逗號分隔)")
        e_prio = st.selectbox("優先權", ["normal", "critical", "main", "route", "ambient"])
        e_rtags = st.text_input("route_tags (逗號分隔)")
        
        if st.form_submit_button("新增結局"):
            st.session_state["endings"].append({
                "ending_id": e_id, "title": e_title, "ending_type": e_type,
                "target_character_id": e_target if e_target else None,
                "description": e_desc,
                "required_flags": [x.strip() for x in e_req_flags.split(",") if x.strip()],
                "required_stats": [x.strip() for x in e_req_stats.split(",") if x.strip()],
                "forbidden_flags": [x.strip() for x in e_forb_flags.split(",") if x.strip()],
                "priority": e_prio,
                "route_tags": [x.strip() for x in e_rtags.split(",") if x.strip()],
            })
            st.rerun()

    _next_page_button(PAGE_LABELS[4])


def _tab_review():
    """
    渲染「預覽與匯出」分頁。
    用以將前述表單收集到的 session_state 資料轉換為 SetupPackage，
    並呼叫 UIWLinter 執行業務邏輯檢查，最後預覽並輸出 Markdown 檔案。
    """
    st.header("6. 預覽與匯出")

    try:
        pkg = _build_package()
    except Exception as e:
        # 當 Pydantic 型別驗證不通過或必填欄位缺失時，捕捉並顯示異常
        st.error(f"資料建構失敗：{e}")
        return

    # --- Validate (業務邏輯與一致性驗證) ---
    if st.button("驗證"):
        linter = UIWLinter()
        report = linter.validate(pkg)
        if report.status == "passed":
            st.success("驗證通過 ✅")
        else:
            st.error(f"驗證未通過 ❌ — {len(report.issues)} 個問題")
        
        # 逐一顯示 issue，以 error 或 warning 的顏色提示
        for issue in report.issues:
            if issue.severity == "error":
                st.error(f"[{issue.type}] {issue.path}: {issue.message}")
            else:
                st.warning(f"[{issue.type}] {issue.path}: {issue.message}")

    # --- YAML Preview ---
    st.subheader("YAML 預覽")
    # 將 Pydantic 模型轉出，移除 None 以減少冗長顯示
    data = pkg.model_dump(mode="json", exclude_none=True)
    yaml_text = yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    st.code(yaml_text, language="yaml")

    # --- Export ---
    st.subheader("匯出 Setup Package MD")
    out_dir = st.text_input("輸出目錄", "examples")
    if st.button("匯出"):
        try:
            # 依據新需求，按下匯出時必須顯示驗證狀態
            linter = UIWLinter()
            report = linter.validate(pkg)
            
            if report.status == "failed":
                st.error("匯出失敗：資料驗證未通過 ❌")
                st.warning("請修正以下主要問題：")
                for issue in report.issues:
                    if issue.severity == "error":
                        st.error(f"[{issue.type}] {issue.path}: {issue.message}")
                    else:
                        st.warning(f"[{issue.type}] {issue.path}: {issue.message}")
            else:
                exporter = SetupPackageExporter(linter=linter)
                # 透過 Exporter 包裝為 Markdown 格式寫入磁碟
                filepath = exporter.write_file(pkg, Path(out_dir))
                st.success(f"匯出成功！驗證狀態：passed ✅")
                st.info(f"輸出檔案位置：{filepath.absolute()}")
        except Exception as e:
            st.error(f"發生未預期錯誤，匯出失敗：{e}")


def main() -> None:
    """
    Interactive User Input Wizard prototype.

    頁面流程：
    1. World Meta
    2. Protagonist
    3. Locations & Map
    4. Characters & Schedule
    5. Flags / Status / Endings
    6. Review & Export
    """
    st.set_page_config(page_title="Sandbox Dating Sim - UIW", layout="wide")
    st.title("Sandbox Dating Sim — User Input Wizard")
    _init_state()

    selected_page = st.radio(
        "設定頁面",
        PAGE_LABELS,
        key="active_page_label",
        horizontal=True,
        label_visibility="collapsed",
    )
    if selected_page == PAGE_LABELS[0]:
        _tab_world()
    elif selected_page == PAGE_LABELS[1]:
        _tab_protagonist()
    elif selected_page == PAGE_LABELS[2]:
        _tab_characters()
    elif selected_page == PAGE_LABELS[3]:
        _tab_locations()
    elif selected_page == PAGE_LABELS[4]:
        _tab_flags()
    else:
        _tab_review()


if __name__ == "__main__":
    main()
