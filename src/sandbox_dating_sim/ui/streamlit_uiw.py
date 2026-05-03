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
from sandbox_dating_sim.core.ids import _make_unique_id
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
from sandbox_dating_sim.uiw.helpers import (
    _has_flag_reference, _has_status_reference, _parse_effect_yaml, _status_targets_options
)


PAGE_LABELS = [
    "世界觀與曆法(World)",
    "主角設定(Protagonist)",
    "地點與地圖(Locations)",
    "角色設定(Characters)",
    "旗標與狀態(Flags & Status)",
    "結局(Endings)",
    "預覽與匯出(Review & Export)",
]

def _collect_existing_ids() -> set[str]:
    """收集全域已存在的系統 ID，用於跨類型唯一性檢查。"""
    s: set[str] = {"protagonist"} # 1-G-7: 全域 ID 集合補入固定 protagonist
    if st.session_state.get("world_id"):
        s.add(st.session_state["world_id"])
    s.update(c["character_id"] for c in st.session_state.get("characters", []) if c.get("character_id"))
    s.update(l["location_id"] for l in st.session_state.get("locations", []) if l.get("location_id"))
    s.update(f["flag_id"] for f in st.session_state.get("flags", []) if f.get("flag_id"))
    s.update(sf["status_id"] for sf in st.session_state.get("status_flags", []) if sf.get("status_id"))
    s.update(e["ending_id"] for e in st.session_state.get("endings", []) if e.get("ending_id"))
    return s

def _purge_ending_state(ending_id: str) -> None:
    """清空指定結局的所有暫存 session state。"""
    # 支援 _<ending_id> 結尾，以及 _<ending_id>_v 帶版本號後綴的 key
    keys_to_drop = [k for k in list(st.session_state.keys()) if k.endswith(f"_{ending_id}") or f"_{ending_id}_v" in k or k == f"_ver_req_flags_{ending_id}" or k == f"_ver_forb_flags_{ending_id}"]
    for k in keys_to_drop:
        del st.session_state[k]


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

        loc_name_map = {loc["location_id"]: loc["name"] for loc in st.session_state["locations"]}
        printed_indices = set()
        display_order = []

        for i, loc in enumerate(st.session_state["locations"]):
            if i in printed_indices:
                continue
            if not loc.get("parent_location_id"):
                display_order.append((i, loc, False))
                printed_indices.add(i)
                for j, sub_loc in enumerate(st.session_state["locations"]):
                    if sub_loc.get("parent_location_id") == loc["location_id"] and j not in printed_indices:
                        display_order.append((j, sub_loc, True))
                        printed_indices.add(j)

        for i, loc in enumerate(st.session_state["locations"]):
            if i not in printed_indices:
                display_order.append((i, loc, bool(loc.get("parent_location_id"))))

        for i, loc, is_indented in display_order:
            parent_id = loc.get("parent_location_id")
            if parent_id:
                parent_name = loc_name_map.get(parent_id, parent_id)
                parent_str = f" (父: {parent_name})"
            else:
                parent_str = ""

            label = f"{loc['name']} [{loc['location_type']}]{parent_str}"

            c1, c2 = st.columns([5, 1], vertical_alignment="center")
            with c1:
                if is_indented:
                    col_space, col_exp = st.columns([1, 15])
                    with col_exp:
                        with st.expander(label):
                            st.json(loc)
                else:
                    with st.expander(label):
                        st.json(loc)
            with c2:
                if st.button("刪除", key=f"del_loc_{i}"):
                    loc_id = loc["location_id"]
                    has_subs = [l["location_id"] for l in st.session_state["locations"] if l.get("parent_location_id") == loc_id]
                    if has_subs:
                        st.toast(f"無法刪除：仍有子地點引用此地點 ({', '.join(has_subs)})", icon="🚨")
                    else:
                        ref_by = []
                        for ch in st.session_state["characters"]:
                            for sch in ch.get("schedule", []):
                                if sch["location_id"] == loc_id:
                                    ref_by.append(f"角色 {ch['character_id']} (行程 {sch['schedule_id']})")
                        if ref_by:
                            st.toast(f"無法刪除：被行程引用 ({', '.join(ref_by)})", icon="🚨")
                        else:
                            st.session_state["locations"].pop(i)
                            st.rerun()

    # --- 套用模板 ---
    st.subheader("套用地點模板")
    tpl_labels = [f"{t['label']} ({t['location_type']})" for t in LOCATION_TEMPLATES]
    tpl_idx = st.selectbox("選擇模板", range(len(LOCATION_TEMPLATES)), format_func=lambda i: tpl_labels[i])

    if st.button("套用模板"):
        tpl = LOCATION_TEMPLATES[tpl_idx]
        suggested_id = tpl.get("location_id_suggestion", tpl["template_id"])

        # 1-G-7: 使用 _make_unique_id 進行 suffix 避讓
        existing_ids = _collect_existing_ids()
        # 1-G-7 Fix: 模板主地點優先沿用建議 ID (suggested_id) 而非從中文 label 產生 pinyin
        # 我們將 suggested_id 傳入作為 fallback，並將 prefix 設為空
        # 注意：_make_unique_id 內部會先呼叫 _slugify_label(label)，這會產生中文拼音。
        # 為了優先使用 suggested_id，我們在此改採直接邏輯或調整 _make_unique_id 呼叫。
        # 根據 1-G-7 規格建議：模板應沿用建議 ID。
        base_id = suggested_id
        loc_id = base_id
        if loc_id in existing_ids:
            counter = 2
            while True:
                candidate = f"{loc_id}_{counter}"
                if candidate not in existing_ids:
                    loc_id = candidate
                    break
                counter += 1

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
                # 1-G-7 Fix: 子地點優先使用父 ID + location_id_suffix
                sub_base = f"{loc_id}_{sub_tpl['location_id_suffix']}"
                sub_loc_id = sub_base
                # 再次確保子地點 ID 唯一
                curr_ids = _collect_existing_ids()
                if sub_loc_id in curr_ids:
                    counter = 2
                    while True:
                        candidate = f"{sub_base}_{counter}"
                        if candidate not in curr_ids:
                            sub_loc_id = candidate
                            break
                        counter += 1

                sub_loc = {
                    "location_id": sub_loc_id,
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
    with st.form("add_location", clear_on_submit=False):
        loc_id_input = st.text_input("地點 ID (英文，留空則自動產生)", key="add_loc_id")
        loc_name = st.text_input("地點名稱", key="add_loc_name")
        loc_type_map = {"container": "主地點/區域(container)", "sub_location": "子地點(sub_location)", "standalone": "獨立地點(standalone)"}
        loc_type = st.selectbox("類型", list(loc_type_map.keys()), format_func=lambda x: loc_type_map[x], key="add_loc_type")

        # 尋找現有的 container 以供 sub_location 選擇為父地點
        containers = [l["location_id"] for l in st.session_state["locations"] if l["location_type"] == "container"]
        parent = st.selectbox("父地點", [None] + containers, key="add_loc_parent")

        # container 預設不可直接進入
        is_visit = st.checkbox("可進入", value=loc_type != "container", key="add_loc_visit")

        slot_map = {"morning": "早上(morning)", "afternoon": "下午(afternoon)", "evening": "晚上(evening)"}
        slots = st.multiselect("可用時間段", list(slot_map.keys()), default=["morning", "afternoon"], format_func=lambda x: slot_map[x], key="add_loc_slots")

        with st.expander("進階設定 (Advanced Settings)"):
            st.markdown("💡 **標籤用途**：可輸入中文或英文，會提供給 AI 生成劇情時參考，不是系統 ID。<br>範例：適合約會、容易偶遇、正式場合、私密、吵雜、危險、浪漫、工作壓力。", unsafe_allow_html=True)
            tags_str = st.text_input("標籤 (逗號分隔)", key="add_loc_tags")


        if st.form_submit_button("新增地點"):
            existing_ids = _collect_existing_ids()

            # 1-G-7: 自動產生 ID
            if not loc_id_input:
                final_loc_id = _make_unique_id(loc_name, "loc_", "unnamed", existing_ids)
            else:
                final_loc_id = loc_id_input

            valid = True
            if not final_loc_id:
                st.error("無法產生有效的地點 ID，請手動輸入")
                valid = False
            elif not re.match(r"^[a-z][a-z0-9_]*$", final_loc_id):
                st.error(f"地點 ID 格式錯誤: {final_loc_id} (須為小寫英文、數字、底線，且以英文字母開頭)")
                valid = False
            elif final_loc_id in existing_ids:
                st.error(f"地點 ID 已存在: {final_loc_id} (與既有 ID 衝突)")
                valid = False

            if valid:
                new_loc = {
                    "location_id": final_loc_id, "name": loc_name,
                    "location_type": loc_type,
                    # 只有子地點才保存父地點 ID
                    "parent_location_id": parent if loc_type == "sub_location" else None,
                    "is_visitable": is_visit if loc_type != "container" else False,
                    "base_cost": 0,
                    "available_time_slots": slots,
                    "tags": [t.strip() for t in tags_str.split(",") if t.strip()],
                    "empty_behavior": "show_empty",
                }
                st.session_state["locations"].append(new_loc)
                if not loc_id_input:
                    st.caption(f"已自動產生 ID: `{final_loc_id}`")

                for k in ["add_loc_id", "add_loc_name", "add_loc_type", "add_loc_parent", "add_loc_visit", "add_loc_slots", "add_loc_tags"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

    _next_page_button(PAGE_LABELS[2])


def _purge_character_state(character_id: str) -> None:
    suffix = f"_{character_id}"
    schedule_prefix = f"del_sch_{character_id}_"
    keys_to_drop = [
        k for k in list(st.session_state.keys())
        if k.endswith(suffix) or k.startswith(schedule_prefix)
    ]
    for k in keys_to_drop:
        del st.session_state[k]

def _tab_characters():
    """
    渲染「角色設定」分頁。
    包含角色的基本資訊、性格、白名單（表情、服裝、位置）設定，
    以及在角色下方建立其專屬行程 (Schedule) 的功能。
    """
    st.header("4. 角色設定")

    if st.session_state["characters"]:
        st.subheader("目前角色")
        for i, ch in enumerate(list(st.session_state["characters"])):
            c_id = ch["character_id"]

            gender_label = _preset_label(ch["gender"], GENDER_OPTIONS)
            role_label = _preset_label(ch["role"], ROLE_OPTIONS)

            c1, c2 = st.columns([5, 1], vertical_alignment="center")
            with c1:
                with st.expander(f"{ch['display_name']} · {gender_label} · {role_label}"):
                    # Initialize temp states for this character
                    tag_key = f"temp_ch_tags_{c_id}"
                    sec_key = f"temp_ch_secrets_{c_id}"
                    if tag_key not in st.session_state:
                        st.session_state[tag_key] = list(ch.get("personality_tags", []))
                    if sec_key not in st.session_state:
                        st.session_state[sec_key] = list(ch.get("secrets", []))

                    st.markdown("**[基本資訊]**")
                    with st.container():
                        e_name = st.text_input("顯示名稱", value=ch["display_name"], key=f"edit_display_name_{c_id}")

                        gender_ids = [g["id"] for g in GENDER_OPTIONS]
                        idx_g = gender_ids.index(ch["gender"]) if ch["gender"] in gender_ids else 0
                        e_gender = st.selectbox("性別", gender_ids, index=idx_g, format_func=lambda x: _preset_label(x, GENDER_OPTIONS), key=f"edit_gender_{c_id}")

                        orient_ids = [o["id"] for o in ORIENTATION_OPTIONS]
                        e_orient = st.multiselect("性取向", orient_ids, default=ch.get("orientation", ["heterosexual"]), format_func=lambda x: _preset_label(x, ORIENTATION_OPTIONS), key=f"edit_orientation_{c_id}")

                        role_ids = [r["id"] for r in ROLE_OPTIONS]
                        idx_r = role_ids.index(ch["role"]) if ch["role"] in role_ids else 0
                        e_role = st.selectbox("定位", role_ids, index=idx_r, format_func=lambda x: _preset_label(x, ROLE_OPTIONS), key=f"edit_role_{c_id}")

                        e_identity = st.text_input("身分描述", value=ch.get("identity", ""), key=f"edit_identity_{c_id}")
                        e_favor = st.number_input("初始好感度", value=ch.get("initial_favor", 0), key=f"edit_initial_favor_{c_id}")

                    st.markdown("**[性格與秘密]**")
                    _semantic_choice_input("性格標籤", tag_key, CHARACTER_PERSONALITY_TAG_PRESETS, allow_multiple=True)
                    _semantic_choice_input("角色秘密 (最多3個)", sec_key, SECRET_PRESETS, allow_multiple=True, max_items=3, separate_none=True)

                    st.markdown("**[角色行程]**")
                    day_type_map = {"weekday": "平日", "weekend": "週末", "holiday": "假日", "any": "任意"}
                    time_slot_map = {"morning": "早上", "afternoon": "下午", "evening": "晚上"}
                    prio_map = {"critical": "必定", "route": "路線", "normal": "一般", "ambient": "環境"}
                    loc_name_map = {loc["location_id"]: loc["name"] for loc in st.session_state["locations"]}

                    if ch.get("schedule"):
                        for s_idx, sch in enumerate(list(ch["schedule"])):
                            d_str = day_type_map.get(sch["day_type"], sch["day_type"])
                            t_str = time_slot_map.get(sch["time_slot"], sch["time_slot"])
                            p_str = prio_map.get(sch["priority"], sch["priority"])
                            l_id = sch["location_id"]
                            l_str = loc_name_map.get(l_id, f"{l_id} (地點已刪除)")

                            c_sch1, c_sch2 = st.columns([5, 1], vertical_alignment="center")
                            with c_sch1:
                                st.write(f"• {d_str} {t_str} @ {l_str} [{p_str}] order={sch['schedule_order']}")
                            with c_sch2:
                                if st.button("刪除", key=f"del_sch_{c_id}_{s_idx}"):
                                    ch["schedule"].pop(s_idx)
                                    st.rerun()
                    else:
                        st.write("尚無行程")

                    vis_locs = _visitable_location_ids()
                    if not vis_locs:
                        st.warning("尚無可進入地點，請先在地點頁建立。")
                    else:
                        with st.form(f"form_add_sch_{c_id}", clear_on_submit=True):
                            sch_id = st.text_input("行程 ID (英文)", key=f"add_sch_id_{c_id}")
                            day_types = ["weekday", "weekend", "holiday", "any"]
                            sch_day = st.selectbox("日期類型", day_types, format_func=lambda x: f"{day_type_map.get(x,x)}({x})", key=f"add_sch_day_{c_id}")
                            sch_slot = st.selectbox("時間段", ["morning", "afternoon", "evening"], format_func=lambda x: f"{time_slot_map.get(x,x)}({x})", key=f"add_sch_slot_{c_id}")
                            sch_loc = st.selectbox("地點", vis_locs, format_func=lambda x: loc_name_map.get(x, x), key=f"add_sch_loc_{c_id}")
                            sch_prio = st.selectbox("優先權", ["critical", "route", "normal", "ambient"], format_func=lambda x: f"{prio_map.get(x,x)}({x})", key=f"add_sch_prio_{c_id}")
                            sch_order = st.number_input("排序值 (越小越優先)", value=20, key=f"add_sch_order_{c_id}")
                            sch_cond = st.text_input("條件 (逗號分隔，可選)", key=f"add_sch_cond_{c_id}")

                            if st.form_submit_button("新增行程"):
                                entry = {
                                    "schedule_id": sch_id, "day_type": sch_day,
                                    "time_slot": sch_slot, "location_id": sch_loc,
                                    "priority": sch_prio, "schedule_order": int(sch_order),
                                    "condition": [c.strip() for c in sch_cond.split(",") if c.strip()],
                                }
                                ch["schedule"].append(entry)
                                st.rerun()

                    st.markdown("**[進階設定 (Advanced Settings)]**")
                    show_adv = st.checkbox("顯示進階設定", key=f"show_adv_{c_id}")

                    emo_labels = [e["label"] for e in EMOTION_PRESETS]
                    cos_labels = [c["label"] for c in COSTUME_PRESETS]
                    pos_labels = [p["label"] for p in POSITION_PRESETS]

                    cur_emo = [item["label"] for item in ch.get("allowed_emotions", []) if item["label"] in emo_labels]
                    cur_cos = [item["label"] for item in ch.get("allowed_costumes", []) if item["label"] in cos_labels]
                    cur_pos = [item["label"] for item in ch.get("allowed_positions", []) if item["label"] in pos_labels]

                    if show_adv:
                        st.info("💡 受控素材清單：表情、服裝、位置白名單用於限制 AI 生成劇情時可用的角色素材，避免 AI 任意創造。預設值可依角色定位調整。")
                        e_emo = st.multiselect("表情白名單", emo_labels, default=cur_emo, key=f"edit_emotions_{c_id}")
                        e_cos = st.multiselect("服裝白名單", cos_labels, default=cur_cos, key=f"edit_costumes_{c_id}")
                        e_pos = st.multiselect("位置白名單", pos_labels, default=cur_pos, key=f"edit_positions_{c_id}")
                        st.text(f"系統 ID (唯讀): {c_id}")
                    else:
                        e_emo = cur_emo
                        e_cos = cur_cos
                        e_pos = cur_pos

                    st.divider()
                    col_save, col_cancel, _ = st.columns([1, 1, 4])
                    with col_save:
                        if st.button("儲存修改", key=f"save_ch_{c_id}"):
                            ch["display_name"] = e_name
                            ch["gender"] = e_gender
                            ch["orientation"] = e_orient
                            ch["role"] = e_role
                            ch["identity"] = e_identity
                            ch["initial_favor"] = e_favor
                            ch["personality_tags"] = list(st.session_state[tag_key])
                            ch["secrets"] = list(st.session_state[sec_key])

                            def _resolve_presets(sel_labels, presets):
                                return [{"id": p["id"], "label": p["label"]} for p in presets if p["label"] in sel_labels]

                            ch["allowed_emotions"] = _resolve_presets(e_emo, EMOTION_PRESETS)
                            ch["allowed_costumes"] = _resolve_presets(e_cos, COSTUME_PRESETS)
                            ch["allowed_positions"] = _resolve_presets(e_pos, POSITION_PRESETS)

                            del st.session_state[tag_key]
                            del st.session_state[sec_key]
                            st.rerun()

                    with col_cancel:
                        if st.button("取消", key=f"cancel_ch_{c_id}"):
                            if tag_key in st.session_state: del st.session_state[tag_key]
                            if sec_key in st.session_state: del st.session_state[sec_key]
                            st.rerun()

            with c2:
                if st.button("刪除", key=f"del_ch_{c_id}"):
                    ref_msgs = []
                    for e in st.session_state.get("endings", []):
                        if e.get("target_character_id") == c_id:
                            ref_msgs.append(f"結局 {e['ending_id']}")
                    for sf in st.session_state.get("status_flags", []):
                        if c_id in sf.get("targets", []):
                            ref_msgs.append(f"狀態旗標 {sf['status_id']}")
                    if ref_msgs:
                        st.toast(f"無法刪除：被 {'、'.join(ref_msgs)} 引用", icon="🚨")
                    else:
                        st.session_state["characters"] = [c for c in st.session_state["characters"] if c["character_id"] != c_id]
                        _purge_character_state(c_id)
                        st.rerun()

    st.subheader("新增角色")

    if "temp_ch_tags" not in st.session_state:
        st.session_state["temp_ch_tags"] = []
    if "temp_ch_secrets" not in st.session_state:
        st.session_state["temp_ch_secrets"] = []
    _semantic_choice_input("性格標籤", "temp_ch_tags", CHARACTER_PERSONALITY_TAG_PRESETS, allow_multiple=True)
    _semantic_choice_input("角色秘密 (最多3個)", "temp_ch_secrets", SECRET_PRESETS, allow_multiple=True, max_items=3, separate_none=True)

    st.divider()
    with st.form("add_character", clear_on_submit=False):
        ch_id_input = st.text_input("角色 ID (英文，留空則自動產生)", key="add_ch_id")
        ch_name = st.text_input("顯示名稱", key="add_ch_name")

        gender_ids = [g["id"] for g in GENDER_OPTIONS]
        ch_gender = st.selectbox("性別", gender_ids, format_func=lambda x: _preset_label(x, GENDER_OPTIONS), key="add_ch_gender")

        orient_ids = [o["id"] for o in ORIENTATION_OPTIONS]
        ch_orient = st.multiselect("性取向", orient_ids, default=["heterosexual"], format_func=lambda x: _preset_label(x, ORIENTATION_OPTIONS), key="add_ch_orient")

        role_ids = [r["id"] for r in ROLE_OPTIONS]
        ch_role = st.selectbox("定位", role_ids, format_func=lambda x: _preset_label(x, ROLE_OPTIONS), key="add_ch_role")

        ch_identity = st.text_input("身分描述", key="add_ch_identity")
        ch_favor = st.number_input("初始好感度", value=0, key="add_ch_favor")

        emo_labels = [e["label"] for e in EMOTION_PRESETS]
        cos_labels = [c["label"] for c in COSTUME_PRESETS]
        pos_labels = [p["label"] for p in POSITION_PRESETS]

        st.markdown("**表情白名單**")
        sel_emo = st.multiselect("選擇表情", emo_labels, default=[e["label"] for e in EMOTION_PRESETS[:3]], key="add_ch_emo")
        st.markdown("**服裝白名單**")
        sel_cos = st.multiselect("選擇服裝", cos_labels, default=[c["label"] for c in COSTUME_PRESETS[:2]], key="add_ch_cos")
        st.markdown("**位置白名單**")
        sel_pos = st.multiselect("選擇位置", pos_labels, default=pos_labels, key="add_ch_pos")

        if st.form_submit_button("新增角色"):
            existing_ids = _collect_existing_ids()

            # 1-G-7: 自動產生 ID
            if not ch_id_input:
                final_ch_id = _make_unique_id(ch_name, "ch_", "unnamed", existing_ids)
            else:
                final_ch_id = ch_id_input

            valid = True
            if not final_ch_id:
                st.error("無法產生有效的角色 ID，請手動輸入")
                valid = False
            elif not re.match(r"^[a-z][a-z0-9_]*$", final_ch_id):
                st.error(f"角色 ID 格式錯誤: {final_ch_id} (須為小寫英文、數字、底線，且以英文字母開頭)")
                valid = False
            elif final_ch_id in existing_ids:
                st.error(f"角色 ID 已存在: {final_ch_id} (與既有 ID 衝突)")
                valid = False

            if valid:
                def _parse_presets_new(selected_labels, presets):
                    return [{"id": p["id"], "label": p["label"]} for p in presets if p["label"] in selected_labels]

                new_ch = {
                    "character_id": final_ch_id, "display_name": ch_name,
                    "gender": ch_gender, "orientation": ch_orient,
                    "role": ch_role, "identity": ch_identity,
                    "personality_tags": list(st.session_state["temp_ch_tags"]),
                    "secrets": list(st.session_state["temp_ch_secrets"]),
                    "initial_favor": ch_favor, "schedule": [],
                    "allowed_emotions": _parse_presets_new(sel_emo, EMOTION_PRESETS),
                    "allowed_costumes": _parse_presets_new(sel_cos, COSTUME_PRESETS),
                    "allowed_positions": _parse_presets_new(sel_pos, POSITION_PRESETS),
                }
                st.session_state["temp_ch_tags"] = []
                st.session_state["temp_ch_secrets"] = []
                st.session_state["characters"].append(new_ch)
                if not ch_id_input:
                    st.caption(f"已自動產生 ID: `{final_ch_id}`")

                for k in ["add_ch_id", "add_ch_name", "add_ch_gender", "add_ch_orient", "add_ch_role", "add_ch_identity", "add_ch_favor", "add_ch_emo", "add_ch_cos", "add_ch_pos"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

    _next_page_button(PAGE_LABELS[3])


def _purge_flag_state(flag_id: str) -> None:
    keys_to_drop = [k for k in list(st.session_state.keys()) if k.endswith(f"_{flag_id}")]
    for k in keys_to_drop:
        del st.session_state[k]

def _purge_status_state(status_id: str) -> None:
    keys_to_drop = [k for k in list(st.session_state.keys()) if k.endswith(f"_{status_id}")]
    for k in keys_to_drop:
        del st.session_state[k]

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
        for i, f in enumerate(list(st.session_state["flags"])):
            f_id = f["flag_id"]
            label = f"{f.get('description') or f_id} · {f['type']} · 初始值 {f['initial_value']}"
            c1, c2 = st.columns([5, 1], vertical_alignment="center")
            with c1:
                with st.expander(label):
                    st.markdown("**[基本資訊]**")
                    st.text(f"旗標 ID (唯讀): {f_id}")
                    e_type = st.selectbox("型別", ["boolean", "integer", "string", "enum"], index=["boolean", "integer", "string", "enum"].index(f["type"]), key=f"flag_type_{f_id}")

                    cur_val = f["initial_value"]
                    if e_type == "boolean":
                        cur_idx = 0 if cur_val is True else 1
                        e_val_bool = st.selectbox("初始值", ["true", "false"], index=cur_idx, key=f"flag_init_{f_id}")
                        e_val = (e_val_bool == "true")
                    elif e_type == "integer":
                        e_val = st.number_input("初始值", value=int(cur_val) if isinstance(cur_val, int) else 0, key=f"flag_init_{f_id}")
                    else:
                        e_val = st.text_input("初始值", value=str(cur_val), key=f"flag_init_{f_id}")

                    e_desc = st.text_input("說明", value=f["description"], key=f"flag_desc_{f_id}")

                    col_save, col_cancel, _ = st.columns([1, 1, 4])
                    with col_save:
                        if st.button("儲存修改", key=f"flag_save_{f_id}"):
                            f["type"] = e_type
                            f["initial_value"] = e_val
                            f["description"] = e_desc
                            st.rerun()
                    with col_cancel:
                        if st.button("取消", key=f"flag_cancel_{f_id}"):
                            _purge_flag_state(f_id)
                            st.rerun()
            with c2:
                if st.button("刪除", key=f"flag_del_{f_id}"):
                    ref_msgs = []
                    for e in st.session_state.get("endings", []):
                        if any(_has_flag_reference(cond, f_id) for cond in e.get("required_flags", [])):
                            ref_msgs.append(f"結局 {e['ending_id']} (required_flags)")
                        if any(_has_flag_reference(cond, f_id) for cond in e.get("forbidden_flags", [])):
                            ref_msgs.append(f"結局 {e['ending_id']} (forbidden_flags)")
                    for ch in st.session_state.get("characters", []):
                        for sch in ch.get("schedule", []):
                            if any(_has_flag_reference(cond, f_id) for cond in sch.get("condition", [])):
                                ref_msgs.append(f"角色 {ch['character_id']} 行程 {sch['schedule_id']}")
                    if ref_msgs:
                        st.toast(f"無法刪除：被 {'、'.join(ref_msgs)} 引用", icon="🚨")
                    else:
                        st.session_state["flags"].pop(i)
                        _purge_flag_state(f_id)
                        st.rerun()

    st.markdown("---")
    st.markdown("**[新增 Flag]**")
    f_id_input = st.text_input("Flag ID (英文，留空則依說明自動產生)", key="add_f_id")
    f_type = st.selectbox("型別", ["boolean", "integer", "string", "enum"], key="add_f_type")

    # Initialize add_f_val if not present
    if "add_f_val" not in st.session_state:
        st.session_state["add_f_val"] = "false"
    f_val = st.text_input("初始值", key="add_f_val")
    f_desc = st.text_input("說明", key="add_f_desc")

    if st.button("新增 Flag"):
        existing_ids = _collect_existing_ids()
        if not f_id_input:
            final_f_id = _make_unique_id(f_desc, "flag_", "unnamed", existing_ids)
        else:
            final_f_id = f_id_input

        valid = True
        if not final_f_id:
            st.error("無法產生有效的 Flag ID，請手動輸入")
            valid = False
        elif not re.match(r"^[a-z][a-z0-9_]*$", final_f_id):
            st.error(f"Flag ID 格式錯誤: {final_f_id}")
            valid = False
        elif final_f_id in existing_ids:
            st.error(f"Flag ID 已存在: {final_f_id}")
            valid = False

        if valid:
            val = f_val
            if f_type == "boolean":
                val = f_val.lower() == "true"
            elif f_type == "integer":
                try: val = int(f_val)
                except ValueError: val = 0

            st.session_state["flags"].append({
                "flag_id": final_f_id, "type": f_type,
                "initial_value": val, "description": f_desc,
            })
            for k in ["add_f_id", "add_f_type", "add_f_val", "add_f_desc"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    # --- Status Flags (狀態效果) ---
    st.subheader("狀態旗標 (Status Flags)")

    dur_type_map = {
        "time_slots": "時段數(time_slots)",
        "days": "天數(days)",
        "until_event": "直到事件(until_event)",
        "until_cleared": "直到解除(until_cleared)",
        "permanent": "永久(permanent)"
    }

    if st.session_state["status_flags"]:
        for i, sf in enumerate(list(st.session_state["status_flags"])):
            sf_id = sf["status_id"]

            tgt_display = []
            for t in sf.get("targets", []):
                if t == "protagonist": tgt_display.append("主角")
                else:
                    ch = next((c for c in st.session_state.get("characters", []) if c["character_id"] == t), None)
                    tgt_display.append(ch["display_name"] if ch else t)
            t_str = "、".join(tgt_display) if tgt_display else "(無)"

            d_str = dur_type_map.get(sf.get("duration", {}).get("type"), "unknown")
            c_str = "、".join(sf.get("clear_rule", [])) if sf.get("clear_rule") else "(無)"

            label = f"{sf.get('label') or sf_id} · {t_str} · {d_str} · {c_str}"

            c1, c2 = st.columns([5, 1], vertical_alignment="center")
            with c1:
                with st.expander(label):
                    st.markdown("**[基本資訊]**")
                    st.text(f"狀態 ID (唯讀): {sf_id}")
                    e_label = st.text_input("顯示名稱", value=sf.get("label", ""), key=f"status_label_{sf_id}")

                    tgt_options_full = _status_targets_options(st.session_state.get("characters", []), sf.get("targets", []))
                    tgt_options_ids = [t[1] for t in tgt_options_full]
                    def format_tgt(tid, opts=tgt_options_full):
                        return next((t[0] for t in opts if t[1] == tid), tid)

                    e_targets = st.multiselect("作用對象", tgt_options_ids, default=sf.get("targets", []), format_func=format_tgt, key=f"status_targets_{sf_id}")
                    e_desc = st.text_input("說明", value=sf.get("description", ""), key=f"status_desc_{sf_id}")

                    st.markdown("**[效果]**")
                    try:
                        effect_yaml_str = yaml.safe_dump(sf.get("effect", []), allow_unicode=True, sort_keys=False)
                    except Exception:
                        effect_yaml_str = "[]\n"
                    e_effect = st.text_area("effect YAML (list of dict)", value=effect_yaml_str, key=f"status_effect_{sf_id}")

                    st.markdown("**[生命週期]**")
                    e_dur_type = st.selectbox("持續類型", list(dur_type_map.keys()), index=list(dur_type_map.keys()).index(sf["duration"]["type"]), format_func=lambda x: dur_type_map[x], key=f"status_durtype_{sf_id}")
                    st.caption("時段數/天數: 經過指定數量後解除。直到事件/直到解除: 不需填寫數值。永久: 長期狀態，需填永久原因。")

                    if e_dur_type in ("time_slots", "days"):
                        e_dur_val = st.number_input("持續值", value=sf["duration"]["value"] if sf["duration"]["value"] is not None else 1, min_value=1, key=f"status_durval_{sf_id}")
                    else:
                        e_dur_val = None

                    clear_rule_opts = ["on_time_advance", "on_day_end", "on_rest", "on_item_used", "on_event_result", "on_location_visit", "manual_only"]
                    e_clear = st.multiselect("解除條件", clear_rule_opts, default=sf.get("clear_rule", []), key=f"status_clear_{sf_id}")

                    if e_dur_type == "permanent":
                        e_perm = st.text_input("永久原因 (必填)", value=sf.get("permanent_reason", ""), key=f"status_perm_{sf_id}")
                    else:
                        e_perm = ""

                    col_save, col_cancel, _ = st.columns([1, 1, 4])
                    with col_save:
                        if st.button("儲存修改", key=f"status_save_{sf_id}"):
                            valid = True
                            if not e_targets:
                                st.error("作用對象不可為空")
                                valid = False

                            parsed_effect = []
                            try:
                                parsed_effect = _parse_effect_yaml(e_effect)
                            except ValueError as ve:
                                st.error(str(ve))
                                valid = False
                            except Exception:
                                st.error("effect YAML 解析失敗")
                                valid = False

                            if e_dur_type != "permanent" and not e_clear:
                                st.error("非永久狀態必須設定解除條件")
                                valid = False
                            if e_dur_type == "permanent" and not e_perm:
                                st.error("永久狀態必須填寫永久原因")
                                valid = False
                            if e_dur_type != "permanent" and e_clear == ["manual_only"]:
                                st.warning("注意：解除條件只有 manual_only")

                            if valid:
                                sf["label"] = e_label
                                sf["targets"] = e_targets
                                sf["description"] = e_desc
                                sf["effect"] = parsed_effect
                                sf["duration"] = {"type": e_dur_type, "value": e_dur_val}
                                sf["clear_rule"] = e_clear
                                sf["permanent_reason"] = e_perm if e_dur_type == "permanent" else None
                                st.rerun()

                    with col_cancel:
                        if st.button("取消", key=f"status_cancel_{sf_id}"):
                            _purge_status_state(sf_id)
                            st.rerun()
            with c2:
                if st.button("刪除", key=f"status_del_{sf_id}"):
                    ref_msgs = []
                    for e in st.session_state.get("endings", []):
                        if any(_has_status_reference(cond, sf_id) for cond in e.get("required_stats", [])):
                            ref_msgs.append(f"結局 {e['ending_id']} (required_stats)")
                    for ch in st.session_state.get("characters", []):
                        for sch in ch.get("schedule", []):
                            if any(_has_status_reference(cond, sf_id) for cond in sch.get("condition", [])):
                                ref_msgs.append(f"角色 {ch['character_id']} 行程 {sch['schedule_id']}")
                    if ref_msgs:
                        st.toast(f"無法刪除：被 {'、'.join(ref_msgs)} 引用", icon="🚨")
                    else:
                        st.session_state["status_flags"].pop(i)
                        _purge_status_state(sf_id)
                        st.rerun()

    st.markdown("---")
    st.markdown("**[新增 Status Flag]**")
    sf_id_input = st.text_input("Status ID (英文，留空則依顯示名稱產生)", key="add_sf_id")
    sf_label = st.text_input("顯示名稱", key="add_sf_label")

    tgt_options_full = _status_targets_options(st.session_state.get("characters", []), [])
    tgt_options_ids = [t[1] for t in tgt_options_full]
    def format_tgt_add(tid):
        return next((t[0] for t in tgt_options_full if t[1] == tid), tid)

    if "add_sf_targets" not in st.session_state:
        st.session_state["add_sf_targets"] = ["protagonist"]
    sf_targets = st.multiselect("作用對象", tgt_options_ids, format_func=format_tgt_add, key="add_sf_targets")

    if "add_sf_effect" not in st.session_state:
        st.session_state["add_sf_effect"] = "- block_time_slot: evening"
    sf_effect = st.text_area("effect YAML (list of dict)", key="add_sf_effect")

    sf_dur_type = st.selectbox("持續類型", list(dur_type_map.keys()), format_func=lambda x: dur_type_map[x], key="add_sf_dur_type")
    st.caption("時段數/天數: 經過指定數量後解除。直到事件/直到解除: 不需填寫數值。永久: 長期狀態，需填永久原因。")

    if sf_dur_type in ("time_slots", "days"):
        if "add_sf_dur_val" not in st.session_state:
            st.session_state["add_sf_dur_val"] = 1
        sf_dur_val = st.number_input("持續值", min_value=1, key="add_sf_dur_val")
    else:
        sf_dur_val = None

    sf_clear = st.multiselect("解除條件", ["on_time_advance", "on_day_end", "on_rest", "on_item_used",
                                            "on_event_result", "on_location_visit", "manual_only"], key="add_sf_clear")
    sf_desc = st.text_input("說明", key="add_sf_desc")

    if sf_dur_type == "permanent":
        sf_perm_reason = st.text_input("永久原因（若 permanent）", key="add_sf_perm_reason")
    else:
        sf_perm_reason = ""

    if st.button("新增 Status Flag"):
        existing_ids = _collect_existing_ids()
        if not sf_id_input:
            final_sf_id = _make_unique_id(sf_label, "status_", "unnamed", existing_ids)
        else:
            final_sf_id = sf_id_input

        valid = True
        if not final_sf_id:
            st.error("無法產生有效的 Status ID，請手動輸入")
            valid = False
        elif not re.match(r"^[a-z][a-z0-9_]*$", final_sf_id):
            st.error(f"Status ID 格式錯誤: {final_sf_id}")
            valid = False
        elif final_sf_id in existing_ids:
            st.error(f"Status ID 已存在: {final_sf_id}")
            valid = False

        if not sf_targets:
            st.error("作用對象不可為空")
            valid = False

        parsed_effect = []
        try:
            parsed_effect = _parse_effect_yaml(sf_effect)
            if not isinstance(parsed_effect, list) or not parsed_effect:
                 # Let _parse_effect_yaml handle validation, but ensure it's not empty if we want to enforce it.
                 # The inline check does not strictly enforce non-empty if parsing succeeds as empty list, but the issue says "effect 必須 parse 成非空 list[dict]". Wait, let me check _parse_effect_yaml or just add a check here.
                 if not parsed_effect:
                     st.error("effect YAML 不可為空")
                     valid = False
        except ValueError as ve:
            st.error(str(ve))
            valid = False
        except Exception:
            st.error("effect YAML 解析失敗")
            valid = False

        if sf_dur_type != "permanent" and not sf_clear:
            st.error("非永久狀態必須設定解除條件")
            valid = False
        if sf_dur_type == "permanent" and not sf_perm_reason:
            st.error("永久狀態必須填寫永久原因")
            valid = False
        if sf_dur_type != "permanent" and sf_clear == ["manual_only"]:
            st.warning("注意：解除條件只有 manual_only")

        if valid:
            entry = {
                "status_id": final_sf_id, "label": sf_label, "targets": sf_targets,
                "effect": parsed_effect,
                "duration": {"type": sf_dur_type, "value": sf_dur_val},
                "clear_rule": sf_clear, "description": sf_desc,
            }
            if sf_dur_type == "permanent" and sf_perm_reason:
                entry["permanent_reason"] = sf_perm_reason
            st.session_state["status_flags"].append(entry)
            for k in ["add_sf_id", "add_sf_label", "add_sf_targets", "add_sf_effect", "add_sf_dur_type", "add_sf_dur_val", "add_sf_clear", "add_sf_desc", "add_sf_perm_reason"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    _next_page_button(PAGE_LABELS[4])


def _tab_endings():
    """
    渲染「結局」分頁。
    """
    st.header("6. 結局")

    priority_map = {
        "critical": "必定觸發(critical)",
        "main": "主線(main)",
        "route": "路線(route)",
        "normal": "一般(normal)",
        "ambient": "背景(ambient)"
    }
    priority_short_map = {
        "critical": "必定觸發",
        "main": "主線",
        "route": "路線",
        "normal": "一般",
        "ambient": "背景"
    }

    if st.session_state["endings"]:
        for e_idx, e in enumerate(list(st.session_state["endings"])):
            e_id = e["ending_id"]
            title_display = e.get("title") or e_id
            prio_display = priority_short_map.get(e.get("priority", "normal"), e.get("priority", "normal"))

            # Target character display
            target_id = e.get("target_character_id")
            if target_id is None:
                target_display = "（無）"
            elif target_id == "global":
                target_display = "全局結局"
            else:
                ch = next((c for c in st.session_state.get("characters", []) if c["character_id"] == target_id), None)
                if ch:
                    target_display = ch["display_name"]
                else:
                    target_display = f"{target_id} (角色已刪除)"

            label = f"{title_display} · {prio_display} · {target_display}"

            c_end1, c_end2 = st.columns([5, 1], vertical_alignment="center")
            with c_end1:
                with st.expander(label):
                    st.markdown("**[基本資訊]**")
                    with st.container():
                        st.text(f"結局 ID: {e_id}")

                        edit_title = st.text_input("結局標題", value=e.get("title", ""), key=f"edit_title_{e_id}")
                        edit_type = st.text_input("結局類型", value=e.get("ending_type", ""), key=f"edit_ending_type_{e_id}")

                        # Target selectbox
                        ch_options = [None, "global"] + [c["character_id"] for c in st.session_state.get("characters", [])]
                        if target_id not in ch_options:
                            ch_options.append(target_id)

                        def format_target(tid):
                            if tid is None: return "（無 / 不指定）"
                            if tid == "global": return "全局結局 (global)"
                            tc = next((c for c in st.session_state.get("characters", []) if c["character_id"] == tid), None)
                            if tc: return tc["display_name"]
                            return f"{tid} (角色已刪除)"

                        idx_t = ch_options.index(target_id) if target_id in ch_options else 0
                        edit_target = st.selectbox("關聯角色", ch_options, index=idx_t, format_func=format_target, key=f"edit_target_{e_id}")

                        edit_desc = st.text_input("結局描述", value=e.get("description", ""), key=f"edit_description_{e_id}")

                        prio_options = ["critical", "main", "route", "normal", "ambient"]
                        idx_p = prio_options.index(e.get("priority", "normal")) if e.get("priority", "normal") in prio_options else 3
                        edit_prio = st.selectbox("優先權", prio_options, index=idx_p, format_func=lambda x: priority_map.get(x, x), key=f"edit_priority_{e_id}")
                        st.caption("優先權由高到低：\ncritical: 強制觸發，覆蓋其他所有結局\nmain: 主線結局\nroute: 角色路線結局\nnormal: 一般結局\nambient: 背景/支線結局，最低優先")

                        edit_rtags = st.text_input("路線標籤 (逗號分隔)", value=",".join(e.get("route_tags", [])), key=f"edit_route_tags_{e_id}")

                    st.markdown("**[條件]**")

                    # required flags
                    st.markdown("── 必須條件 (required_flags) ──")
                    req_key = f"temp_req_flags_{e_id}"
                    if req_key not in st.session_state:
                        st.session_state[req_key] = list(e.get("required_flags", []))

                    flag_ids = [f["flag_id"] for f in st.session_state.get("flags", [])]

                    if not flag_ids:
                        st.multiselect("選擇旗標", [], key=f"ms_req_flags_{e_id}", disabled=True)
                        st.caption("尚未設定旗標。可在『旗標與狀態』分頁建立後再回此處快速加入")
                    else:
                        req_ver = st.session_state.get(f"_ver_req_flags_{e_id}", 0)
                        req_sel = st.multiselect("選擇旗標", flag_ids, key=f"ms_req_flags_{e_id}_v{req_ver}")
                        if st.button("加入到必須條件", key=f"add_req_flags_{e_id}"):
                            for fid in req_sel:
                                fdef = next((f for f in st.session_state["flags"] if f["flag_id"] == fid), None)
                                if fdef:
                                    if fdef["type"] == "boolean":
                                        expr = f"flag.{fid} == true"
                                    elif fdef["type"] == "integer":
                                        expr = f"flag.{fid} == {fdef['initial_value']}"
                                    else: # string, enum
                                        # handle escaping
                                        val = str(fdef['initial_value']).replace("\\", "\\\\").replace('"', '\\"')
                                        expr = f'flag.{fid} == "{val}"'
                                    if expr not in st.session_state[req_key]:
                                        st.session_state[req_key].append(expr)
                            # Increment version instead of clearing widget value
                            st.session_state[f"_ver_req_flags_{e_id}"] = req_ver + 1
                            st.rerun()

                    # forbidden flags
                    st.markdown("── 禁止條件 (forbidden_flags) ──")
                    forb_key = f"temp_forb_flags_{e_id}"
                    if forb_key not in st.session_state:
                        st.session_state[forb_key] = list(e.get("forbidden_flags", []))

                    if not flag_ids:
                        st.multiselect("選擇旗標", [], key=f"ms_forb_flags_{e_id}", disabled=True)
                        st.caption("尚未設定旗標。可在『旗標與狀態』分頁建立後再回此處快速加入")
                    else:
                        forb_ver = st.session_state.get(f"_ver_forb_flags_{e_id}", 0)
                        forb_sel = st.multiselect("選擇旗標", flag_ids, key=f"ms_forb_flags_{e_id}_v{forb_ver}")
                        if st.button("加入到禁止條件", key=f"add_forb_flags_{e_id}"):
                            for fid in forb_sel:
                                fdef = next((f for f in st.session_state["flags"] if f["flag_id"] == fid), None)
                                if fdef:
                                    if fdef["type"] == "boolean":
                                        expr = f"flag.{fid} == true"
                                    elif fdef["type"] == "integer":
                                        expr = f"flag.{fid} == {fdef['initial_value']}"
                                    else: # string, enum
                                        val = str(fdef['initial_value']).replace("\\", "\\\\").replace('"', '\\"')
                                        expr = f'flag.{fid} == "{val}"'
                                    if expr not in st.session_state[forb_key]:
                                        st.session_state[forb_key].append(expr)
                            st.session_state[f"_ver_forb_flags_{e_id}"] = forb_ver + 1
                            st.rerun()

                    with st.form(f"form_edit_cond_{e_id}"):
                        edit_req_flags = st.text_area("required_flags (逗號或換行分隔)", value=",\n".join(st.session_state[req_key]), key=f"edit_req_flags_{e_id}")
                        edit_forb_flags = st.text_area("forbidden_flags (逗號或換行分隔)", value=",\n".join(st.session_state[forb_key]), key=f"edit_forb_flags_{e_id}")

                        st.markdown("── 必須數值 (required_stats) ──")
                        edit_req_stats = st.text_input("required_stats (逗號分隔)", value=",".join(e.get("required_stats", [])), key=f"edit_req_stats_{e_id}")

                        st.divider()
                        col_save, col_cancel, _ = st.columns([1, 1, 4])
                        with col_save:
                            if st.form_submit_button("儲存修改"):
                                e["title"] = edit_title
                                e["ending_type"] = edit_type
                                e["target_character_id"] = edit_target if edit_target else None
                                e["description"] = edit_desc
                                e["priority"] = edit_prio
                                e["route_tags"] = [x.strip() for x in edit_rtags.split(",") if x.strip()]

                                # parsing text areas: split by newline and comma
                                req_list = []
                                for line in edit_req_flags.replace("\n", ",").split(","):
                                    if line.strip(): req_list.append(line.strip())
                                e["required_flags"] = req_list
                                st.session_state[req_key] = req_list

                                forb_list = []
                                for line in edit_forb_flags.replace("\n", ",").split(","):
                                    if line.strip(): forb_list.append(line.strip())
                                e["forbidden_flags"] = forb_list
                                st.session_state[forb_key] = forb_list

                                e["required_stats"] = [x.strip() for x in edit_req_stats.split(",") if x.strip()]

                                st.rerun()
                        with col_cancel:
                            if st.form_submit_button("取消"):
                                def _reset_ending_edit_state(eid: str):
                                    # 支援 _<eid> 結尾，以及 _<eid>_v 帶版本號後綴的 key
                                    keys_to_clear = [k for k in list(st.session_state.keys()) if ((k.endswith(f"_{eid}") or f"_{eid}_v" in k) and (k.startswith("edit_") or k.startswith("temp_") or k.startswith("ms_"))) or k == f"_ver_req_flags_{eid}" or k == f"_ver_forb_flags_{eid}"]
                                    for k in keys_to_clear:
                                        del st.session_state[k]

                                _reset_ending_edit_state(e_id)
                                st.rerun()

            with c_end2:
                if st.button("刪除", key=f"del_end_{e_id}"):
                    st.session_state["endings"].pop(e_idx)
                    _purge_ending_state(e_id)
                    st.rerun()

    st.subheader("新增結局")
    with st.form("add_ending", clear_on_submit=False):
        e_id_input = st.text_input("Ending ID (英文，留空則依標題自動產生)", key="add_end_id")
        e_title = st.text_input("結局標題", key="add_end_title")
        e_type = st.text_input("結局類型 (例: character_good)", key="add_end_type")

        ch_options = [None, "global"] + [c["character_id"] for c in st.session_state.get("characters", [])]
        def format_target(tid):
            if tid is None: return "（無 / 不指定）"
            if tid == "global": return "全局結局 (global)"
            tc = next((c for c in st.session_state.get("characters", []) if c["character_id"] == tid), None)
            if tc: return tc["display_name"]
            return f"{tid} (角色已刪除)"

        e_target = st.selectbox("關聯角色", ch_options, format_func=format_target, key="add_end_target")
        e_desc = st.text_input("結局描述", key="add_end_desc")
        e_req_flags = st.text_input("required_flags (逗號分隔)", key="add_end_req_f")
        e_req_stats = st.text_input("required_stats (逗號分隔)", key="add_end_req_s")
        e_forb_flags = st.text_input("forbidden_flags (逗號分隔)", key="add_end_forb_f")
        e_prio = st.selectbox("優先權", ["critical", "main", "route", "normal", "ambient"], index=3, format_func=lambda x: priority_map.get(x, x), key="add_end_prio")
        st.caption("優先權由高到低：\ncritical: 強制觸發，覆蓋其他所有結局\nmain: 主線結局\nroute: 角色路線結局\nnormal: 一般結局\nambient: 背景/支線結局，最低優先")
        e_rtags = st.text_input("route_tags (逗號分隔)", key="add_end_rtags")

        if st.form_submit_button("新增結局"):
            existing_ids = _collect_existing_ids()

            # 1-G-7: 自動產生 ID (依據標題)
            if not e_id_input:
                final_e_id = _make_unique_id(e_title, "end_", "unnamed", existing_ids)
            else:
                final_e_id = e_id_input

            # 即時驗證：Ending ID
            valid = True
            if not final_e_id:
                st.error("無法產生有效的 Ending ID，請手動輸入")
                valid = False
            elif not re.match(r"^[a-z][a-z0-9_]*$", final_e_id):
                st.error(f"Ending ID 格式錯誤: {final_e_id}")
                valid = False
            elif final_e_id in existing_ids:
                st.error(f"Ending ID 已存在: {final_e_id}")
                valid = False

            if valid:
                st.session_state["endings"].append({
                    "ending_id": final_e_id, "title": e_title, "ending_type": e_type,
                    "target_character_id": e_target if e_target else None,
                    "description": e_desc,
                    "required_flags": [x.strip() for x in e_req_flags.split(",") if x.strip()],
                    "required_stats": [x.strip() for x in e_req_stats.split(",") if x.strip()],
                    "forbidden_flags": [x.strip() for x in e_forb_flags.split(",") if x.strip()],
                    "priority": e_prio,
                    "route_tags": [x.strip() for x in e_rtags.split(",") if x.strip()],
                })
                if not e_id_input:
                    st.caption(f"已自動產生 ID: `{final_e_id}`")

                for k in ["add_end_id", "add_end_title", "add_end_type", "add_end_target", "add_end_desc", "add_end_req_f", "add_end_req_s", "add_end_forb_f", "add_end_prio", "add_end_rtags"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

    _next_page_button(PAGE_LABELS[5])


def _tab_review():
    """
    渲染「預覽與匯出」分頁。
    用以將前述表單收集到的 session_state 資料轉換為 SetupPackage，
    並呼叫 UIWLinter 執行業務邏輯檢查，最後預覽並輸出 Markdown 檔案。
    """
    st.header("7. 預覽與匯出")

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
    5. Flags & Status
    6. Endings
    7. Review & Export
    """
    st.set_page_config(page_title="Sandbox Dating Sim - UIW", layout="wide")

    # 注入 CSS 強制將所有 st.toast 彈出視窗移至畫面正中間
    st.markdown(
        """
        <style>
        div[data-testid="stToastContainer"] {
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            bottom: auto !important;
            right: auto !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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
        _tab_locations()
    elif selected_page == PAGE_LABELS[3]:
        _tab_characters()
    elif selected_page == PAGE_LABELS[4]:
        _tab_flags()
    elif selected_page == PAGE_LABELS[5]:
        _tab_endings()
    else:
        _tab_review()


if __name__ == "__main__":
    main()
()
()
