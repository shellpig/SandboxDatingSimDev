# 沙盒戀愛模擬遊戲生成工具文件管線規格 (v1.1)

## 版本紀錄

| 版本 | 日期 | 內容 |
| :--- | :--- | :--- |
| v1.3 | 2026-05-01 | 明確規定 Setup Package 中沒有秘密時使用 `secrets: []`；`none = 沒有秘密` 只屬 UI 操作，不輸出給 AI 作為秘密語意。 |
| v1.2 | 2026-05-01 | 對齊 UIW Phase 1-G-3：Setup Package 語意型欄位改為保存 `id + label`，讓 AI 能讀取中文語意，系統仍使用英文 canonical ID。 |
| v1.1 | 2026-04-27 | 將 Setup Package 範例中的 `uiw_version` 統一為 `1.2`，對齊 UIW 初始設定 v1.2。 |
| v1.0 | 2026-04-27 | 初版，定義 Setup Package MD、Event Blueprint MD、Scene Draft MD 與分階段生成流程。 |

## 1. 文件目的

本文件定義遊戲生成工具在「使用者完成 User Input Wizard」之後，如何產出可供 AI 讀取、可供人類檢查、也可供工具解析的文件。

本管線的核心原則是：

- 內部資料以 JSON 或 YAML 保存。
- 對外交換與 AI 讀取使用 Markdown。
- Markdown 中主要內容應放在 YAML 區塊中，確保可解析。
- AI 先生成事件骨架，再逐步生成對話與演出內容。
- 事件骨架是劇情邏輯合約，後續生成不得擅自修改。

## 2. 文件類型總覽

本工具至少包含兩種核心文件：

1. Setup Package MD
2. Event Blueprint MD

後續可擴充：

- Scene Draft MD
- Final Script MD
- Validation Report MD
- Asset Request MD

## 3. Setup Package MD

Setup Package MD 是 User Input Wizard 完成後產出的設定資料文件。

它的用途：

- 讓使用者檢查遊戲初始設定。
- 作為 Mega-Prompt 的主要上下文。
- 作為 Event Blueprint 生成時的輸入。
- 作為 Map Manager、Route Validator、Linter 與資產管理器的共同資料來源。

### 3.1 格式原則

Setup Package MD 使用 Markdown 作為外殼，主要資料放在 YAML 區塊。

範例：

````md
# Setup Package: 夏日債務街

```yaml
setup_package_version: 1.0
uiw_version: 1.2
target_game_spec_version: 1.2

world:
  world_id: summer_city_2026
  title: 夏日債務街
  start_date: 2026-04-27
  end_date: 2026-05-26
  time_slots:
    - morning
    - afternoon
    - evening
  global_style:
    - id: urban_romance
      label: 都市戀愛
    - id: black_humor
      label: 黑色幽默

protagonist:
  protagonist_id: protagonist
  name: 佑介
  gender: male
  occupation:
    id: cafe_staff
    label: 咖啡廳店員
  personality:
    id: kind_but_tired
    label: 善良但疲憊
  secrets:
    - id: family_debt
      label: 背負家族債務
  initial_stats:
    INT: 5
    CHA: 6
    STR: 4
    MORAL: 5
    Cash: 3000
    Debt: 50000

characters:
  - character_id: sophie
    display_name: 蘇菲
    role: main_love_interest
    personality_tags:
      - id: guarded
        label: 戒心重
      - id: secretly_kind
        label: 其實很溫柔
    secrets:
      - id: family_scandal
        label: 家族醜聞
    initial_favor: 0
    allowed_emotions:
      - neutral
      - happy
      - embarrassed
      - love_struck
    allowed_costumes:
      - casual
      - school_uniform

locations: []
flags: []
status_flags: []
endings: []
asset_vocabularies: {}
alias_tables: {}
```
````

### 3.2 必要內容

Setup Package MD 必須包含：

- `setup_package_version`
- `uiw_version`
- `target_game_spec_version`
- `world`
- `protagonist`
- `locations`
- `characters`
- `flags`
- `status_flags`
- `endings`
- `asset_vocabularies`
- `alias_tables`

使用者語意型欄位必須保存 `id + label`，例如 `world.global_style`、`protagonist.occupation`、`protagonist.personality`、`protagonist.secrets`、`characters[].personality_tags`、`characters[].secrets`。AI 讀取 Setup Package 時應使用中文 `label` 理解語意，工具與驗證器則使用英文 `id` 做穩定引用。

若 `protagonist.secrets` 或 `characters[].secrets` 為空，必須輸出為 `secrets: []`。這代表使用者沒有指定秘密；AI 不得把 `none` 視為一個秘密、伏筆或角色特質。UI 的 `none = 沒有秘密` 僅用來清空清單，不應出現在 Setup Package MD。

### 3.3 輸出與保存

工具內部應保存 JSON 或 YAML 作為 canonical data。

Markdown 版本用途為：

- 使用者檢查
- 版本管理
- AI prompt context
- 人類手動修訂

若 Markdown 與內部 JSON/YAML 不一致，內部 JSON/YAML 為優先真相來源；但工具應提供重新匯出 Markdown 的功能。

## 4. Event Blueprint MD

Event Blueprint MD 是 AI 根據 Setup Package MD 產出的事件骨架文件。

它只描述劇情邏輯，不負責完整對話。

### 4.1 Event Blueprint 的責任

Event Blueprint 必須定義：

- 事件 ID
- 事件標題
- 事件地點
- 事件時間段
- 事件優先權
- 路線標籤
- 觸發條件
- 事件目的
- 選項數量
- 選項意圖
- 選項結果
- Flag 變化
- 數值變化
- status flag 變化
- goto
- time cost

Event Blueprint 不應產出：

- 完整長篇對話
- 細緻旁白
- 最終選項文案
- 大量演出細節
- 未經宣告的素材需求

### 4.2 事件格式

範例：

````md
# Event Blueprint: Sophie Route Opening

```yaml
event_blueprint_version: 1.0
source_setup_package: summer_city_2026_setup.md
target_game_spec_version: 1.2

events:
  - event_id: sophie_park_001
    title: 公園偶遇
    location_id: central_park
    time_slot: afternoon
    priority: route
    route_tags:
      - character_route:sophie
      - ending_prerequisite
    conditions:
      - day >= 3
      - flag.is_met_sophie == true
    event_purpose: 蘇菲第一次主動透露家庭壓力，開啟她的個人路線。
    cast:
      - sophie
    expected_assets:
      background: central_park_day
      bgm: park_afternoon
      characters:
        - character_id: sophie
          costume: casual
          emotion: surprised
          position: center
    choices:
      - choice_id: listen_quietly
        choice_intent: 溫柔傾聽
        result:
          - character.sophie.favor += 5
          - flag.sophie_trust_started = true
          - goto: free_roam

      - choice_id: make_joke
        choice_intent: 用玩笑緩和氣氛
        result:
          - character.sophie.favor += 1
          - flag.sophie_teased_at_park = true
          - goto: free_roam
    time_cost: 1
```
````

### 4.3 Event Blueprint 是邏輯合約

Event Blueprint 通過驗證後，應視為後續生成的劇情邏輯合約。

後續 Scene Draft 生成不得擅自修改：

- `event_id`
- `location_id`
- `time_slot`
- `priority`
- `route_tags`
- `conditions`
- `choices[].choice_id`
- `choices[].result`
- `time_cost`
- `goto`
- Flag 變化
- 數值變化
- status flag 變化

若後續生成發現邏輯需要修改，必須回到 Event Blueprint 階段修改，並重新執行驗證。

## 5. Scene Draft MD

Scene Draft MD 是根據單一事件或一組事件生成的敘事內容。

它可以補充：

- 對話
- 旁白
- 選項顯示文字
- 表情演出
- BGM 與背景標籤
- 節奏與轉場

但它不得修改 Event Blueprint 的邏輯結果。

### 5.1 Scene Draft 生成限制

Scene Draft 生成時必須遵守：

- 只能使用 Setup Package 中宣告的角色、地點、素材白名單。
- 只能使用 Event Blueprint 中既有的 `choice_id`。
- 可以美化選項文字，但不得改變 `choice_intent` 與 `result`。
- 不得新增未宣告 Flag。
- 不得新增未宣告 status flag。
- 不得修改 `time_cost`。
- 不得修改 `goto`。

## 6. 建議生成流程

完整流程：

```text
User Input Wizard
-> Setup Package MD
-> Event Blueprint Generation
-> Event Blueprint Validation
-> Scene Draft Generation
-> Scene Draft Validation
-> Final Script Assembly
```

### 6.1 Setup Package Generation

使用者完成 UIW 後，工具產出 Setup Package MD。

此階段需要執行：

- UIW Linter
- ID 檢查
- 語意型欄位 `id + label` 檢查
- schedule conflict 檢查
- status flag lifecycle 檢查
- asset vocabulary 檢查

### 6.2 Event Blueprint Generation

AI 讀取 Setup Package MD，產出 Event Blueprint MD。

此階段 AI 只負責設計事件網路與選項結果，不負責完整場景文本。

### 6.3 Event Blueprint Validation

工具對 Event Blueprint MD 執行：

- Parser
- Linter
- Map Manager free_roam 解析
- Route Validator
- Critical Path Mode
- Character Route Mode

只有通過驗證的 Event Blueprint 才能進入 Scene Draft 生成。

### 6.4 Scene Draft Generation

工具逐一事件或分批事件生成 Scene Draft。

建議以小批次生成：

- 單一事件
- 同一角色的一小段事件鏈
- 同一日期的事件
- 同一地點的事件

避免一次生成過多內容導致 AI 忽略邏輯合約。

### 6.5 Scene Draft Validation

Scene Draft 必須再次驗證：

- DSL 格式
- 素材白名單
- 選項 ID 是否一致
- 結果是否被修改
- goto 是否被修改
- time cost 是否被修改

## 7. AI Prompt 規則

### 7.1 生成 Event Blueprint 時

AI 必須遵守：

- 只使用 Setup Package 中宣告的角色與地點。
- 只使用 Setup Package 中宣告或允許新增的 Flag。
- 新 Flag 必須列入 `new_flags_proposed`，不得直接假裝已存在。
- status flag 必須存在於 registry，且具備 lifecycle。
- 每個事件必須有 `event_id`。
- 每個事件必須有 `conditions`。
- 每個事件必須有 `time_cost`。
- 每個選項必須有 `choice_id`、`choice_intent` 與 `result`。
- 若事件結束回到地圖，必須使用 `goto: free_roam`。

### 7.2 生成 Scene Draft 時

AI 必須遵守：

- 不得修改 Event Blueprint 的條件與結果。
- 不得新增或刪除選項。
- 不得修改選項 ID。
- 不得新增未宣告素材標籤。
- 對話與旁白必須服務於 `event_purpose`。
- 選項文字必須符合 `choice_intent`。

## 8. 驗證報告

每次生成後都應產出 Validation Report。

範例：

```yaml
validation_report:
  source_file: sophie_event_blueprint.md
  status: failed
  issues:
    - severity: error
      type: unknown_flag
      event_id: sophie_park_001
      message: flag.sophie_trust_started 未在 Flag Registry 宣告。
      suggested_action: 將此 flag 加入 proposed flags，或改用既有 flag。
```

## 9. 文件命名建議

Setup Package：

```text
<world_id>_setup_package.md
```

Event Blueprint：

```text
<world_id>_event_blueprint_v001.md
```

Scene Draft：

```text
<event_id>_scene_draft.md
```

Validation Report：

```text
<source_file_name>_validation_report.md
```

## 10. 核心結論

Setup Package MD 是設定資料包。

Event Blueprint MD 是劇情邏輯合約。

Scene Draft MD 是敘事表現稿。

工具應先驗證邏輯，再生成對話。這能最大限度降低 AI 一次生成完整劇本時造成的旗標錯亂、路線不可達、素材失控與劇情結果被偷改等問題。
