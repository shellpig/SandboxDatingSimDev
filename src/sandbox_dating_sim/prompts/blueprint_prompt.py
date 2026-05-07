"""Phase 2-B Blueprint Prompt Builder.

主要 API：
    build_event_blueprint_prompt(setup_package_markdown, scope, ...) -> str

產出章節化 Markdown prompt document，供使用者複製給外部 AI 生成 Event Blueprint。
"""

from typing import Literal

BlueprintPromptScope = Literal["minimal_complete", "ai_decides", "custom"]

# ── 固定 DSL 白名單說明 ───────────────────────────────────────────────────

_CONDITION_DSL = """\
支援的 Condition DSL（YAML list 代表 AND，不支援 OR/NOT/括號）：
```
day == N  |  day >= N  |  day <= N
date == YYYY-MM-DD  |  date >= YYYY-MM-DD  |  date <= YYYY-MM-DD
time_slot == <time_slot>
location.current == <location_id>
flag.<flag_id> == true  |  flag.<flag_id> == false
stat.INT >= N  |  stat.INT <= N  |  stat.INT == N
stat.CHA >= N  |  stat.CHA <= N  |  stat.CHA == N
stat.STR >= N  |  stat.STR <= N  |  stat.STR == N
stat.MORAL >= N  |  stat.MORAL <= N  |  stat.MORAL == N
stat.Cash >= N  |  stat.Cash <= N  |  stat.Cash == N
stat.Debt >= N  |  stat.Debt <= N  |  stat.Debt == N
character.<character_id>.favor >= N  |  ...favor <= N  |  ...favor == N
status.<target_id>.<status_id> == true  |  == false
```
❌ 禁止：AND / OR / NOT / 括號 / item.* / inventory.* / visited_event / random"""

_RESULT_DSL = """\
支援的 Result DSL（每個 choice result 是 str list）：
```
flag.<flag_id> = true  |  flag.<flag_id> = false
stat.INT += N  |  stat.INT -= N
stat.CHA += N  |  stat.CHA -= N
stat.STR += N  |  stat.STR -= N
stat.MORAL += N  |  stat.MORAL -= N
stat.Cash += N  |  stat.Cash -= N
stat.Debt += N  |  stat.Debt -= N
character.<character_id>.favor += N  |  ...favor -= N
status.<target_id>.<status_id> = true  |  = false
time_cost: N             # 覆蓋 event time_cost（可選，同一 choice 只能出現一次）
goto: <event_id>         # ┐ 流程出口恰好一個
goto: free_roam          # │
ending: <ending_id>      # ┘
```
❌ 禁止：item.* / inventory.*（劇情物品請用 boolean flag）
⚠️ 每個 choice result 必須恰好包含一個 goto 或 ending，不可同時出現。"""

_STATUS_RULES = """\
- Status 變更必須透過 event choice result 明確寫：
    status.<target>.<status_id> = true  或  = false
- 不可依賴 `clear_rule` 自動觸發；如需休息解除 status，請建立對應 event。
- StatusFlag.effect 在 Phase 2 不由 walkthrough 通用解讀。"""

_INITIAL_EVENT_RULES = """\
- initial event 必須位於 `protagonist_home`。
- initial event 的 `time_slot` 必須等於 world 的第一個 time_slot。
- initial event 的 conditions 可空，或只含 day / date / time / location checks。
- initial event 不可要求 flag / stat / favor / status 條件。
- initial event 不可要求 day > 1 或等價條件。"""

_ENDING_RULES = """\
- SetupPackage 中每個 ending_id 都必須至少被一個 `ending: <ending_id>` result 引用。
- 必須有至少一個帶 `fallback_ending` route_tag 的 event，且該 event 有 ending result。
- ending 只能由 event choice result 中的 `ending: <ending_id>` 顯式觸發，不可隱式達成。"""

_OUTPUT_FORMAT = """\
你的輸出必須是：
1. 一份 Markdown 文件（Event Blueprint MD）。
2. 文件中恰好包含 **一個** YAML fenced code block（以 ` ```yaml ` 開頭）。
3. 所有 canonical 資料只存在 YAML block 內；Markdown 外殼只供人類閱讀。
4. 不輸出完整對話文本，不輸出 Scene Draft，只輸出 Blueprint。
5. human-facing text（title / scene_summary / choice_label / choice_intent / event_purpose）使用繁體中文。
6. 所有 ID / DSL 使用英文 canonical ID。"""

_YAML_REQUIRED_FIELDS = """\
YAML block 必須包含以下頂層欄位：
```yaml
event_blueprint_version: "1.0"
blueprint_id: <world_id>_event_blueprint
source_world_id: <world_id>
source_setup_package: <world_id>_setup_package.md
target_game_spec_version: "1.2"
initial_event_id: <opening_event_id>
events:
  - event_id: ...
    title: ...           # 繁體中文
    scene_summary: ...   # 繁體中文，3-5 句場景描述
    location_id: ...
    time_slot: ...       # morning / afternoon / evening
    priority: ...        # critical / main / route / normal / ambient
    repeat_policy: ...   # once / daily
    route_tags: [...]
    conditions: [...]
    event_purpose: ...   # 繁體中文，設計意圖
    cast: [...]          # character_id list
    expected_assets:
      background: ...    # 背景圖 ID，不確定填 null
      bgm: ...           # BGM ID，不確定填 null
      characters:
        - character_id: ...
          costume: ...
          emotion: ...
          position: ...  # left / center / right
    choices:
      - choice_id: ...
        choice_label: ... # 繁體中文，玩家看到的短選項（< 20 字）
        choice_intent: ...# 繁體中文，設計意圖
        result:
          - "flag.xxx = true"    # 例
          - "goto: free_roam"    # 流程出口（必填且唯一）
    time_cost: 1               # 正整數
new_flags_proposed:
  - flag_id: ...
    type: boolean
    initial_value: false
    description: ...
```"""

_SILENT_CHECK = """\
輸出前，默默執行以下 self-check：
1. 每個 ending_id（來自 Setup Package）都被至少一個 `ending:` result 引用？
2. 有 `fallback_ending` route_tag 的 event 且包含 ending result？
3. initial event 位於 protagonist_home，time_slot 是第一個 world time slot？
4. 每個 choice result 恰好一個 goto 或 ending？
5. 沒有使用 item.* / inventory.*？
6. 所有新 flag 都在 new_flags_proposed 中（且 type: boolean）？
如任一項不符合，先修正再輸出。"""


# ── 主要 API ──────────────────────────────────────────────────────────────

def build_event_blueprint_prompt(
    setup_package_markdown: str,
    scope: BlueprintPromptScope = "minimal_complete",
    target_event_count: int | None = None,
    custom_scope: str | None = None,
) -> str:
    """
    產出章節化 Markdown prompt document，供使用者複製給外部 AI 生成 Event Blueprint。

    Args:
        setup_package_markdown: 完整的 Setup Package MD 文字內容。
        scope: 生成範圍。"minimal_complete" / "ai_decides" / "custom"。
        target_event_count: custom scope 下的目標事件數（可選）。
        custom_scope: custom scope 下的額外說明文字（可選）。

    Returns:
        Markdown prompt document 字串。
    """
    scope_section = _build_scope_section(scope, target_event_count, custom_scope)

    sections = [
        "# Event Blueprint Generation Instructions\n",
        "## 1. Your Task\n",
        _build_task_section(scope),
        "\n## 2. Output Format\n",
        _OUTPUT_FORMAT,
        "\n## 3. Required Top-Level YAML Fields\n",
        _YAML_REQUIRED_FIELDS,
        "\n## 4. Event Rules\n",
        _build_event_rules(),
        "\n## 5. Supported Condition DSL\n",
        _CONDITION_DSL,
        "\n## 6. Supported Result DSL\n",
        _RESULT_DSL,
        "\n## 7. Initial Event Rules\n",
        _INITIAL_EVENT_RULES,
        "\n## 8. Ending Rules\n",
        _ENDING_RULES,
        "\n## 9. Status Rules\n",
        _STATUS_RULES,
        "\n## 10. Scope\n",
        scope_section,
        "\n## 11. Setup Package\n",
        "以下是本次使用的 Setup Package 完整內容，請根據其中的世界觀、角色、地點、旗標、結局進行設計：\n\n",
        setup_package_markdown,
        "\n## 12. Silent Final Check\n",
        _SILENT_CHECK,
    ]
    return "\n".join(sections)


# ── 內部 helpers ──────────────────────────────────────────────────────────

def _build_task_section(scope: BlueprintPromptScope) -> str:
    return (
        "你是一位沙盒戀愛模擬器的劇情設計師。\n"
        "你的任務是根據提供的 Setup Package，生成一份符合規格的 **Event Blueprint MD**。\n\n"
        "Event Blueprint 是遊戲劇情邏輯的骨架合約，定義所有可觸發事件、選擇、分支與結局。\n"
        "你**不需要**生成完整對話，**不需要**生成 Scene Draft。\n"
        "所有 canonical ID 使用英文，human-facing text 使用繁體中文。\n"
    )


def _build_event_rules() -> str:
    return """\
- 每個 event 必須有 1 到 4 個 choices。
- 每個 choice result 必須恰好含一個流程出口（`goto:` 或 `ending:`），不可同時出現兩者。
- `time_cost` 必須是正整數，且不超過 world time_slots 總數。
- `repeat_policy` 只允許 `once` 或 `daily`。
- `route_tags` 可自由命名（建議：main_route / character_route:<id> / ending_prerequisite / fallback_ending）。
- 空 route_tag 不允許。
- `cast` 列出此 event 出現的角色 character_id list。
- `expected_assets.characters` 只列出 cast 中的角色，costume / emotion / position 填預期值。
- 不可新增 canonical characters；`cast`、`expected_assets.characters`、`character.<id>.favor`、status target、ending target 只能引用 SetupPackage 已存在的 character_id。
- 可在 `scene_summary` 用純文字描寫背景 NPC / 路人 / 店員 / 同學，但這些背景 NPC 不可進入 cast / expected_assets / DSL / ending target。
- 新增的 boolean flag 必須列入 `new_flags_proposed`（只允許 type: boolean）。
- 不使用 item.* / inventory.*，劇情物品以 boolean flag 表示。"""


def _build_scope_section(
    scope: BlueprintPromptScope,
    target_event_count: int | None,
    custom_scope: str | None,
) -> str:
    if scope == "minimal_complete":
        return (
            "**scope: minimal_complete**\n\n"
            "請生成最小但完整的事件網。必須包含：\n"
            "- 一個 opening event（initial event，位於 protagonist_home）。\n"
            "- 各主要路線的關鍵事件（不需要 filler）。\n"
            "- 所有 SetupPackage endings 各至少一條觸發路徑。\n"
            "- 至少一個 fallback ending event（帶 `fallback_ending` route_tag）。\n"
            "生成事件數量以「能 cover all endings 的最小集合」為目標，避免冗餘事件。\n"
        )
    elif scope == "ai_decides":
        return (
            "**scope: ai_decides**\n\n"
            "你自行決定事件數量與結構，但必須：\n"
            "- 覆蓋 SetupPackage 中所有 endings（各至少一條觸發路徑）。\n"
            "- 有至少一個 fallback ending event（帶 `fallback_ending` route_tag）。\n"
            "- 不產生與主線無關的 filler 事件。\n"
            "設計原則：品質優先於數量，每個事件都要有明確的劇情目的。\n"
        )
    else:  # custom
        lines = ["**scope: custom**\n"]
        if target_event_count is not None:
            lines.append(f"目標事件數：**{target_event_count}** 個事件。\n")
        if custom_scope:
            lines.append(f"額外說明：\n{custom_scope}\n")
        lines.append(
            "無論如何，仍必須：\n"
            "- 覆蓋 SetupPackage 中所有 endings（各至少一條觸發路徑）。\n"
            "- 有至少一個 fallback ending event（帶 `fallback_ending` route_tag）。\n"
            "Phase 2 MVP 不支援 partial Blueprint；必須產出完整可驗證的 Blueprint。\n"
        )
        return "\n".join(lines)


# ── 輸出路徑工具 ──────────────────────────────────────────────────────────

def prompt_output_path(outputs_root, world_id: str):
    """回傳 prompt 的標準輸出路徑 Path 物件。"""
    from pathlib import Path
    root = Path(outputs_root)
    return root / world_id / "prompts" / f"{world_id}_event_blueprint_prompt.md"


def write_prompt_file(
    outputs_root,
    world_id: str,
    prompt_text: str,
) -> "Path":
    """
    寫出 prompt 到固定路徑。
    若目標檔案已存在則拋 FileExistsError（不覆寫）。
    """
    from pathlib import Path
    filepath = prompt_output_path(outputs_root, world_id)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    if filepath.exists():
        raise FileExistsError(
            f"Prompt 檔案已存在，拒絕覆寫：{filepath}\n"
            "請手動刪除或重新命名後再建立。"
        )
    filepath.write_text(prompt_text, encoding="utf-8")
    return filepath
