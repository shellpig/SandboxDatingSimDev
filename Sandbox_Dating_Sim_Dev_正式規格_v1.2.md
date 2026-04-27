# 沙盒戀愛模擬遊戲生成工具開發規格書 (v1.2)

## 版本紀錄

| 版本 | 日期 | 內容 |
| :--- | :--- | :--- |
| v1.2.1 | 2026-04-27 | 更新內容生成文件管線引用至 `Sandbox_Dating_Sim_文件管線規格_v1.1.md`，以統一 `uiw_version: 1.2`。 |
| v1.2 | 2026-04-27 | 新增 Map Manager、Controlled Asset Vocabulary、Auto Repair Layer、Critical Path Mode 與內容生成文件管線。 |

## 1. 產品定位

本工具是一套「AI 輔助沙盒戀愛模擬遊戲開發管線」。核心目標不是讓 AI 即興生成不可控劇情，而是讓使用者先定義世界、角色、時間、旗標與規則，再由 AI 生成符合規格的 Markdown 劇本，最後由本地引擎解析、驗證、預覽、修正與管理素材。

本工具參考經典戀愛模擬遊戲的時間管理與角色行程設計，採用三段式時間軸：

- 上午
- 下午
- 晚上

遊戲推進以條件、數值與旗標驅動。AI 只負責生成候選內容；引擎負責保存真實狀態、驗證邏輯、執行結果與顯示除錯資訊。

## 2. 設計原則

### 2.1 引擎是唯一真相來源

AI 生成的內容不得直接視為可信邏輯。所有條件、旗標、數值變動、角色位置、事件觸發與結局判定，都必須由本地資料模型與驗證器檢查。

### 2.2 可讀、可改、可驗證

劇本格式以 Markdown 為基礎，但在 Markdown 中使用固定 DSL 標籤。劇本必須同時滿足：

- 人類可閱讀
- AI 可生成
- Parser 可解析
- Linter 可檢查
- Route Validator 可驗證
- Flowchart 可視覺化
- Auto Repair Layer 可提出修正

### 2.3 決定性優先

預設不使用 runtime 純隨機。若需要變化，使用以下方式之一：

- 固定排程
- 條件排程
- 權重生成
- Seeded random

同一組世界設定、角色設定、劇本與 seed，必須產生可重現的結果。

### 2.4 受控詞彙優先

角色表情、服裝、姿勢、BGM、背景與 CG 等素材標籤，預設必須從資料層已宣告的白名單中選擇。AI 不得自由創造素材標籤，除非該新增項目經過使用者批准並寫回資料層。

## 3. 系統架構

系統分為五層：

1. 資料層
2. 腳本層
3. 生成層
4. 自動修正層
5. 驗證與預覽層

### 3.1 資料層

資料層負責保存遊戲世界的結構化設定。

必要資料包含：

- World Meta
- Calendar
- Location
- Protagonist
- Character
- Schedule
- Stats
- Flags
- Assets
- Endings
- Map Rules
- Controlled Vocabularies

### 3.2 腳本層

腳本層使用 Markdown DSL 描述事件、條件、對話、選項、結果與時間消耗。

腳本必須可以被解析為事件圖。每個事件節點應具有穩定 ID，不應只依賴中文標題或自然語言描述。

### 3.3 生成層

生成層負責將使用者輸入的世界設定、角色設定、系統規則與受控詞彙封裝成 Mega-Prompt。

AI 的任務是：

- 生成符合 DSL 的事件
- 補完角色對話
- 產生選項與結果
- 建議事件鏈
- 生成素材需求描述

AI 不負責最終判定事件是否有效。

### 3.4 自動修正層

自動修正層位於生成層與驗證層之間。它接收 AI 生成的 Markdown，先執行輕量修正，再交給 Linter 與 Route Validator。

自動修正層不得擅自改變劇情含義。所有修正都必須產生可檢查的修正紀錄。

### 3.5 驗證與預覽層

驗證與預覽層負責解析 Markdown 劇本，建立事件圖，檢查所有可到達路線，並提供開發者預覽與除錯。

核心功能包含：

- Parser
- Linter
- Route Validator
- Map Manager
- Flowchart
- Debug Console
- Event Preview Player

## 4. User Input Wizard

User Input Wizard 用於收集生成遊戲所需的核心參數。

### 4.1 World Meta

欄位：

- `world_id`
- `title`
- `start_date`
- `total_days`
- `time_slots`
- `calendar_rules`
- `holidays`
- `global_style`

範例：

```yaml
world_id: summer_debt_city
title: 夏日債務街
start_date: 2026-04-27
total_days: 30
time_slots:
  - morning
  - afternoon
  - evening
global_style:
  - black_humor
  - class_anxiety
  - urban_romance
```

### 4.2 Location

地點必須有穩定 ID。

欄位：

- `location_id`
- `name`
- `type`
- `base_cost`
- `available_time_slots`
- `tags`
- `unlock_conditions`
- `map_priority`

範例：

```yaml
location_id: central_park
name: 中央公園
type: public
base_cost: 0
available_time_slots:
  - morning
  - afternoon
  - evening
tags:
  - date_spot
  - outdoor
unlock_conditions:
  - day >= 1
map_priority: normal
```

### 4.3 Protagonist

欄位：

- `protagonist_id`
- `name`
- `gender`
- `age`
- `occupation`
- `initial_stats`
- `initial_flags`
- `personality`
- `secret`

核心數值：

- `INT`
- `CHA`
- `STR`
- `MORAL`
- `Cash`
- `Debt`

### 4.4 Character

角色分為可攻略角色與關鍵配角。

欄位：

- `character_id`
- `display_name`
- `gender`
- `orientation`
- `role`
- `personality_tags`
- `initial_favor`
- `secret_flags`
- `schedule`
- `asset_profile`
- `allowed_emotions`
- `allowed_costumes`
- `allowed_positions`

範例：

```yaml
character_id: sophie
display_name: 蘇菲
gender: female
orientation:
  - male
role: main_love_interest
personality_tags:
  - guarded
  - proud
  - secretly_kind
initial_favor: 0
secret_flags:
  - sophie_family_debt
allowed_emotions:
  - neutral
  - happy
  - surprised
  - angry
  - embarrassed
  - sad
allowed_costumes:
  - casual
  - school_uniform
  - work_uniform
allowed_positions:
  - left
  - center
  - right
```

## 5. Map Manager 與 Free Roam Resolution

Map Manager 是 v1.2 新增的核心系統，專門處理 `goto: free_roam` 後的地圖狀態、NPC 分佈與可觸發事件。

### 5.1 Free Roam 狀態

`free_roam` 不得只是抽象跳轉點。它必須解析為完整狀態。

```text
FreeRoamState =
  day
  time_slot
  current_location
  unlocked_locations
  npc_distribution
  available_events
  blocked_events
```

### 5.2 Map Manager 職責

Map Manager 必須負責：

- 根據日期與時間段列出可用地點
- 根據角色 schedule 計算 NPC 所在地
- 根據事件條件列出可觸發事件
- 處理角色行程與特殊事件覆蓋
- 標示有事件、有人但無事件、空地點
- 檢查地點是否被鎖定
- 檢查玩家是否因 status flag 無法移動

### 5.3 NPC 分佈規則

角色位置解析優先順序：

1. 強制劇情位置
2. 主線或角色路線事件要求的位置
3. 條件排程
4. 固定排程
5. Seeded fallback
6. 不在地圖上

範例：

```yaml
schedule:
  - time_slot: afternoon
    location_id: central_park
    condition:
      - day >= 3
      - flag.sophie_route_started == true
    priority: route

  - time_slot: afternoon
    location_id: library
    condition:
      - day >= 1
    priority: normal
```

### 5.4 可觸發事件解析

當玩家進入地點時，引擎應依序檢查：

1. 玩家是否可進入該地點
2. 該時間段是否可用
3. NPC 是否在場
4. 事件條件是否成立
5. 事件優先權
6. 是否已觸發過且不可重複

若多個事件同時可觸發，依以下順序排序：

1. `priority: critical`
2. `priority: main`
3. `priority: route`
4. `priority: normal`
5. `priority: ambient`

## 6. Markdown DSL v1.2

### 6.1 基本規則

- 所有事件必須有唯一 `event_id`。
- 所有角色、地點、旗標、素材都必須使用穩定 ID。
- 顯示文字可以是中文，但邏輯判斷必須使用 ID。
- 條件與結果不得只寫自然語言。
- 每個事件最多消耗一個或多個時間段，但必須明確標示。
- 事件可用 `route_tags` 標記驗證優先權。

### 6.2 事件格式

```md
---
event_id: sophie_park_001
title: 公園裡的偶遇
location_id: central_park
time_slot: afternoon
priority: route
route_tags:
  - character_route:sophie
  - ending_prerequisite
---

## Conditions

- day >= 3
- flag.is_met_sophie == true
- stat.Cash >= 100
- character.sophie.favor >= 5

## Scene

[BGM: park_afternoon, Loop: true]
[Background: central_park_day]
[Character: sophie, Costume: casual, Emotion: surprised, Position: center]

> sophie: 你怎麼會在這裡？
> narrator: 她的語氣像是責備，但視線沒有移開。

## Choices

- choice_id: give_drink
  text: 買飲料給她
  type: empathetic
  power: 3
  result:
    - stat.Cash -= 100
    - character.sophie.favor += 5
    - flag.sophie_accepted_drink = true
    - goto: sophie_park_001_after_drink

- choice_id: tease_her
  text: 開玩笑說只是路過
  type: playful
  power: 2
  result:
    - character.sophie.favor += 1
    - flag.sophie_teased_at_park = true
    - goto: free_roam

## Time Cost

- 1
```

### 6.3 條件語法

允許：

```md
- day >= 3
- time_slot == afternoon
- flag.is_met_sophie == true
- stat.Cash >= 100
- character.sophie.favor >= 10
- location.current == central_park
```

不允許：

```md
- 如果蘇菲已經認識主角
- 好感度夠高時
- 錢差不多足夠
```

### 6.4 結果語法

允許：

```md
- stat.Cash -= 100
- stat.Debt += 500
- character.sophie.favor += 5
- flag.sophie_route_started = true
- status.protagonist.overworked = true
- goto: sophie_route_002
- goto: free_roam
```

### 6.5 資產標籤

角色資產：

```md
[Character: sophie, Costume: casual, Emotion: surprised, Position: center]
```

BGM：

```md
[BGM: park_afternoon, Loop: true]
```

背景：

```md
[Background: central_park_day]
```

CG：

```md
[CG: sophie_first_date]
```

資產檔名建議：

```text
character_sophie_casual_surprised.png
bg_central_park_day.png
bgm_park_afternoon.ogg
cg_sophie_first_date.png
```

## 7. Controlled Asset Vocabulary

Controlled Asset Vocabulary 用於避免 AI 任意創造素材標籤，導致素材清單無限膨脹。

### 7.1 角色素材白名單

每個角色必須定義：

- `allowed_emotions`
- `allowed_costumes`
- `allowed_positions`
- `allowed_poses`，可選

AI 只能使用白名單中的值。

### 7.2 全域素材白名單

全域素材可定義：

- `allowed_bgms`
- `allowed_sfx`
- `allowed_backgrounds`
- `allowed_cgs`

### 7.3 Alias Table

為了降低 AI 小錯誤造成的中斷，可設定同義詞表。

範例：

```yaml
emotion_aliases:
  臉紅: embarrassed
  害羞: embarrassed
  驚到: surprised
  生氣: angry
```

### 7.4 驗證規則

- 使用未宣告 emotion：error
- 使用可映射 alias：warning，並提供 deterministic repair
- 新增素材標籤：需要使用者批准
- 同一角色素材數超過上限：warning

## 8. Auto Repair Layer

Auto Repair Layer 負責修復 AI 生成內容中的小型結構錯誤，降低使用者手動修稿成本。

### 8.1 修正分級

#### Deterministic Repair

可自動套用的修正。

範例：

- 大小寫錯誤
- ID 近似拼字錯誤
- 角色顯示名轉換為 `character_id`
- emotion alias 轉換
- costume alias 轉換
- 缺少可推導的預設 `Time Cost`

#### LLM Assisted Repair

需要 LLM 局部重寫的修正。

範例：

- 條件語法不合法
- 選項缺少 result
- 事件沒有出口
- 新 Flag 未宣告
- 對話格式不一致

LLM Assisted Repair 必須只重寫最小必要片段，不得重寫整份劇本。

### 8.2 修正紀錄格式

所有修正都必須產生紀錄。

```yaml
repairs:
  - type: deterministic
    confidence: high
    event_id: sophie_park_001
    original: flag.met_already == true
    fixed: flag.is_met_sophie == true
    reason: nearest declared flag match

  - type: deterministic
    confidence: high
    event_id: sophie_park_001
    original: Emotion: 臉紅
    fixed: Emotion: embarrassed
    reason: emotion alias mapping
```

### 8.3 修正限制

Auto Repair Layer 不得：

- 自動新增關鍵劇情 Flag
- 自動改變角色好感度結果
- 自動刪除選項
- 自動改變結局條件
- 自動改變事件含義

低信心修正必須交由使用者確認。

## 9. Route Validator

Route Validator 負責在劇情生成後，快速驗證主要路線是否可執行，並指出問題點。

### 9.1 驗證目標

Route Validator 必須檢查：

- 無法觸發的事件
- 沒有出口的事件
- 永遠無法達成的條件
- 條件互相矛盾的事件
- 未宣告的 Flag
- 未宣告的角色、地點、素材
- 數值變動導致的資源不足
- 時間消耗超過當日剩餘時間
- 路線無法抵達任何結局
- 結局條件永遠不會成立
- 角色行程與事件地點衝突
- 同一 ID 重複宣告
- `free_roam` 後無可用地點或無可觸發內容

### 9.2 驗證方式

驗證器將劇本轉換為狀態圖。

狀態包含：

- day
- time_slot
- current_location
- unlocked_locations
- npc_distribution
- available_events
- protagonist_stats
- character_favor
- flags
- status_flags
- visited_events

每個選項會產生新的狀態分支。驗證器沿著分支展開，直到：

- 抵達結局
- 抵達自由行動狀態並完成 Map Manager 解析
- 當日時間耗盡
- 達到遊戲結束日期
- 命中最大探索深度
- 偵測到重複狀態

### 9.3 驗證模式

#### Exhaustive Mode

完整展開所有可達分支。

適用於：

- 單日劇情
- 單角色路線
- 小型測試劇本
- MVP 驗證

#### Bounded Mode

在指定限制內探索重要路線。

限制參數：

- `max_depth`
- `max_states`
- `target_endings`
- `target_characters`
- `seed`
- `priority_events_only`

#### Critical Path Mode

優先驗證主線、角色路線與結局前置條件。

優先順序：

1. `route_tags` 包含 `critical`
2. `route_tags` 包含 `ending_prerequisite`
3. `route_tags` 包含 `main_route`
4. `route_tags` 包含 `character_route:<character_id>`
5. 最近修改的事件
6. 高影響 Flag 的事件
7. 一般事件

#### Character Route Mode

指定角色並驗證其主要路線是否能抵達任一有效結局。

參數：

- `character_id`
- `target_ending`
- `max_depth`
- `allow_side_events`

### 9.4 問題報告格式

驗證器輸出問題清單。

範例：

```yaml
issues:
  - severity: error
    type: unreachable_event
    event_id: sophie_date_003
    message: 此事件無法被任何路線觸發。
    reason:
      - requires flag.sophie_route_started == true
      - no previous event sets flag.sophie_route_started

  - severity: warning
    type: resource_block
    event_id: cafe_invitation_001
    message: 玩家在所有已探索路線中都無法累積足夠 Cash。
    required:
      stat.Cash: 500
    observed_max:
      stat.Cash: 300

  - severity: error
    type: unknown_asset
    event_id: sophie_park_001
    message: 找不到角色素材。
    asset_id: character_sophie_casual_surprised
```

### 9.5 開發者介面

Route Validator 應在 Dashboard 中提供：

- 一鍵驗證
- 指定角色路線驗證
- 指定結局驗證
- 指定日期範圍驗證
- Critical Path 驗證
- 問題清單
- 點擊問題跳轉到劇本行數
- 顯示最短可達路徑
- 顯示阻斷條件
- 顯示建議修正方向

## 10. Flowchart

Flowchart 根據事件圖自動生成。

節點類型：

- Event
- Choice
- Result
- Free Roam
- Location
- Ending
- Blocked

節點狀態：

- reachable
- unreachable
- warning
- error
- ending

Flowchart 必須能顯示：

- Flag 來源
- Flag 消耗
- 好感度變動
- 金錢變動
- 時間消耗
- 事件前置條件
- Free Roam 後的可用地點
- NPC 分佈

## 11. Linter

Linter 負責靜態檢查，不需要實際跑完整路線。

檢查項目：

- Markdown DSL 格式錯誤
- YAML front matter 錯誤
- 重複 `event_id`
- 未宣告 ID
- 未使用 Flag
- 設定後從未讀取的 Flag
- 缺少 `Time Cost`
- 缺少 `goto`
- 條件語法不合法
- 結果語法不合法
- 素材命名不合規
- 使用未宣告 emotion
- 使用未宣告 costume
- 使用未宣告 BGM
- `goto: free_roam` 但缺少 Map Manager 可解析狀態

## 12. Mega-Prompt 生成規格

Mega-Prompt 必須包含：

- 世界設定
- 角色資料
- 地點資料
- 角色行程資料
- 已存在事件摘要
- 已宣告 Flag
- 允許使用的 DSL
- 受控素材詞彙
- Alias Table
- 禁止事項
- 輸出格式
- 驗證提醒

AI 生成時必須遵守：

- 不得創造未宣告角色 ID
- 不得創造未宣告地點 ID
- 不得創造未宣告 emotion
- 不得創造未宣告 costume
- 不得創造未宣告 BGM
- 新 Flag 必須列入 `New Flags`
- 每個事件必須有唯一 `event_id`
- 每個選項必須有明確結果
- 每個事件必須有 `Time Cost`
- 事件不得只依靠自然語言條件

## 13. 資產管理

資產管理器從 Markdown DSL 中擷取素材需求。

### 13.1 圖像

來源標籤：

- `[Character]`
- `[Background]`
- `[CG]`

功能：

- 自動生成素材需求清單
- 檢查缺漏素材
- 智能重命名
- 角色 Y 軸對齊
- 表情與服裝差分管理
- 檢查素材詞彙是否超出白名單

### 13.2 音訊

來源標籤：

- `[BGM]`
- `[SFX]`

功能：

- 檢查音訊缺漏
- 設定 loop
- 設定淡入淡出
- 檢查同一場景音訊衝突
- 檢查音訊詞彙是否超出白名單

## 14. 內容生成文件管線

本工具採用分階段內容生成流程，不應要求 AI 一次產出完整劇本。

詳細格式與規則請參閱：

- `Sandbox_Dating_Sim_文件管線規格_v1.1.md`

### 14.1 核心文件

內容生成流程至少包含兩種核心文件：

- Setup Package MD
- Event Blueprint MD

Setup Package MD 由 User Input Wizard 產出。它使用 Markdown 作為人類可讀外殼，主要設定資料放在 YAML 區塊中。工具內部仍應以 JSON 或 YAML 保存 canonical data。

Event Blueprint MD 由 AI 根據 Setup Package MD 產出。它只描述事件骨架、觸發條件、選項數量、選項意圖、結果、Flag 變化、數值變化、`goto` 與 `time_cost`，不負責完整對話與細緻演出。

### 14.2 建議流程

```text
User Input Wizard
-> Setup Package MD
-> Event Blueprint Generation
-> Event Blueprint Validation
-> Scene Draft Generation
-> Scene Draft Validation
-> Final Script Assembly
```

### 14.3 邏輯合約原則

Event Blueprint 通過驗證後，視為劇情邏輯合約。

後續 Scene Draft 只能補充：

- 對話
- 旁白
- 選項顯示文字
- 表情演出
- BGM 與背景標籤
- 節奏與轉場

後續 Scene Draft 不得擅自修改：

- `conditions`
- `choices[].choice_id`
- `choices[].result`
- Flag 變化
- 數值變化
- status flag 變化
- `goto`
- `time_cost`

若需要修改上述邏輯，必須回到 Event Blueprint 階段調整並重新驗證。

## 15. MVP 範圍

第一版可執行 MVP 建議只做以下閉環：

1. 建立世界、角色、地點資料
2. 建立角色表情、服裝與位置白名單
3. 建立 Map Manager 的基本 free_roam 解析
4. User Input Wizard 產出 Setup Package MD
5. AI 生成 Event Blueprint MD
6. Auto Repair Layer 執行 deterministic repair
7. Parser 解析事件
8. Linter 檢查格式
9. Route Validator 跑單角色路線
10. Critical Path Mode 跑結局前置事件
11. Flowchart 顯示事件圖與 free_roam 地圖節點
12. Preview Player 播放單一事件

MVP 不必立即包含：

- 完整多語言
- 完整素材生成
- 商業打包
- 複雜動畫
- 完整 90 天大型劇本
- LLM Assisted Repair 全自動化

## 16. 後續進階功能

- 多語言翻譯，保留 DSL 不變
- 性別與稱謂動態替換
- AI 輔助修復不可達事件
- AI 生成角色行程建議
- 結局覆蓋率報告
- 劇情節奏分析
- 角色出場頻率分析
- 好感度曲線視覺化
- 分支複雜度警告
- Seeded playthrough 匯出
- LLM Assisted Repair 差異預覽
- Map heatmap
- 素材需求預算估算
- Scene Draft 分批生成
- Final Script Assembly

## 17. v1.2 與 v1.1 的主要差異

- 新增 Map Manager
- 正式定義 `free_roam` 解析流程
- 新增 Controlled Asset Vocabulary
- 角色設定中加入 `allowed_emotions`、`allowed_costumes`、`allowed_positions`
- 新增 Auto Repair Layer
- 將修正分為 deterministic repair 與 LLM assisted repair
- 新增 Critical Path Mode
- 新增 Character Route Mode
- Route Validator 加入 Map Manager 狀態
- Linter 加入素材白名單與 `free_roam` 檢查
- Mega-Prompt 必須注入受控素材詞彙
- 新增內容生成文件管線，並指向 `Sandbox_Dating_Sim_文件管線規格_v1.1.md`
- 正式納入 Setup Package MD 與 Event Blueprint MD
