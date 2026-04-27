# 沙盒戀愛模擬遊戲生成工具開發規格書 (v1.1)

## 1. 產品定位

本工具是一套「AI 輔助沙盒戀愛模擬遊戲開發管線」。核心目標不是讓 AI 即興生成不可控劇情，而是讓使用者先定義世界、角色、時間、旗標與規則，再由 AI 生成符合規格的 Markdown 劇本，最後由本地引擎解析、驗證、預覽與管理素材。

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
- Flowchart 可視覺化

### 2.3 決定性優先

預設不使用 runtime 純隨機。若需要變化，使用以下方式之一：

- 固定排程
- 條件排程
- 權重生成
- Seeded random

同一組世界設定、角色設定、劇本與 seed，必須產生可重現的結果。

## 3. 系統架構

系統分為四層：

1. 資料層
2. 腳本層
3. 生成層
4. 驗證與預覽層

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

### 3.2 腳本層

腳本層使用 Markdown DSL 描述事件、條件、對話、選項、結果與時間消耗。

腳本必須可以被解析為事件圖。每個事件節點應具有穩定 ID，不應只依賴中文標題或自然語言描述。

### 3.3 生成層

生成層負責將使用者輸入的世界設定、角色設定與系統規則封裝成 Mega-Prompt。

AI 的任務是：

- 生成符合 DSL 的事件
- 補完角色對話
- 產生選項與結果
- 建議事件鏈
- 生成素材需求描述

AI 不負責最終判定事件是否有效。

### 3.4 驗證與預覽層

驗證與預覽層負責解析 Markdown 劇本，建立事件圖，檢查所有可到達路線，並提供開發者預覽與除錯。

核心功能包含：

- Parser
- Linter
- Route Validator
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
```

## 5. Markdown DSL v1.1

### 5.1 基本規則

- 所有事件必須有唯一 `event_id`。
- 所有角色、地點、旗標、素材都必須使用穩定 ID。
- 顯示文字可以是中文，但邏輯判斷必須使用 ID。
- 條件與結果不得只寫自然語言。
- 每個事件最多消耗一個或多個時間段，但必須明確標示。

### 5.2 事件格式

```md
---
event_id: sophie_park_001
title: 公園裡的偶遇
location_id: central_park
time_slot: afternoon
priority: normal
---

## Conditions

- day >= 3
- flag.is_met_sophie == true
- stat.Cash >= 100
- character.sophie.favor >= 5

## Scene

[BGM: park_afternoon, Loop: true]
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

### 5.3 條件語法

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

### 5.4 結果語法

允許：

```md
- stat.Cash -= 100
- stat.Debt += 500
- character.sophie.favor += 5
- flag.sophie_route_started = true
- status.protagonist.overworked = true
- goto: sophie_route_002
```

### 5.5 資產標籤

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

## 6. Route Validator

Route Validator 是 v1.1 的核心新增功能。它負責在劇情生成後，快速驗證所有主要路線是否可執行，並指出問題點。

### 6.1 驗證目標

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

### 6.2 驗證方式

驗證器將劇本轉換為狀態圖。

狀態包含：

- day
- time_slot
- current_location
- protagonist_stats
- character_favor
- flags
- status_flags
- visited_events

每個選項會產生新的狀態分支。驗證器沿著分支展開，直到：

- 抵達結局
- 抵達自由行動狀態
- 當日時間耗盡
- 達到遊戲結束日期
- 命中最大探索深度
- 偵測到重複狀態

### 6.3 全路線驗證與限制

「全部路線跑過一次」在小型劇本中可以完全展開；在大型沙盒中可能出現組合爆炸。因此 v1.1 定義兩種模式：

#### Exhaustive Mode

完整展開所有可達分支。

適用於：

- 單日劇情
- 單角色路線
- 小型測試劇本
- MVP 驗證

#### Bounded Mode

在指定限制內探索所有重要路線。

限制參數：

- `max_depth`
- `max_states`
- `target_endings`
- `target_characters`
- `seed`
- `priority_events_only`

適用於：

- 30 天以上沙盒
- 多角色多路線劇本
- 大型測試

### 6.4 問題報告格式

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

### 6.5 開發者介面

Route Validator 應在 Dashboard 中提供：

- 一鍵驗證
- 指定角色路線驗證
- 指定結局驗證
- 指定日期範圍驗證
- 問題清單
- 點擊問題跳轉到劇本行數
- 顯示最短可達路徑
- 顯示阻斷條件
- 顯示建議修正方向

## 7. Flowchart

Flowchart 根據事件圖自動生成。

節點類型：

- Event
- Choice
- Result
- Free Roam
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

## 8. Linter

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

## 9. Mega-Prompt 生成規格

Mega-Prompt 必須包含：

- 世界設定
- 角色資料
- 地點資料
- 已存在事件摘要
- 已宣告 Flag
- 允許使用的 DSL
- 禁止事項
- 輸出格式
- 驗證提醒

AI 生成時必須遵守：

- 不得創造未宣告角色 ID
- 不得創造未宣告地點 ID
- 新 Flag 必須列入 `New Flags`
- 每個事件必須有唯一 `event_id`
- 每個選項必須有明確結果
- 每個事件必須有 `Time Cost`
- 事件不得只依靠自然語言條件

## 10. 資產管理

資產管理器從 Markdown DSL 中擷取素材需求。

### 10.1 圖像

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

### 10.2 音訊

來源標籤：

- `[BGM]`
- `[SFX]`

功能：

- 檢查音訊缺漏
- 設定 loop
- 設定淡入淡出
- 檢查同一場景音訊衝突

## 11. MVP 範圍

第一版可執行 MVP 建議只做以下閉環：

1. 建立世界、角色、地點資料
2. 生成或匯入 Markdown 事件
3. Parser 解析事件
4. Linter 檢查格式
5. Route Validator 跑單角色路線
6. Flowchart 顯示事件圖
7. Preview Player 播放單一事件

MVP 不必立即包含：

- 完整多語言
- 完整素材生成
- 商業打包
- 複雜動畫
- 完整 90 天大型劇本

## 12. 後續進階功能

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

## 13. v1.1 與 v1.0 的主要差異

- 明確定義「引擎是唯一真相來源」
- 將系統拆成資料層、腳本層、生成層、驗證與預覽層
- 將 Markdown 腳本升級為正式 DSL
- 新增穩定 ID 規範
- 新增 Route Validator
- 新增 Exhaustive Mode 與 Bounded Mode
- 補強 Linter、Flowchart 與素材管理規格
- 定義 MVP 開發範圍
