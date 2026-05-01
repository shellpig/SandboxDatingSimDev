# Sandbox Dating Sim Dev: User Input Wizard (UIW) 初始設定規格 v1.2

## 版本紀錄

| 版本 | 日期 | 內容 |
| :--- | :--- | :--- |
| v1.2.6 | 2026-05-01 | 補充 Phase 1-G-3：語意型欄位改為保存 `id + label`；主角與 NPC 秘密改為最多 3 個複選；新增職業與秘密預設選項；改善中文自訂輸入與系統 ID 欄位。 |
| v1.2.5 | 2026-04-28 | 補充 Phase 1-G-2 使用者操作回饋：主角 ID 固定隱藏、性別/性取向/定位 UI 選項中文化、主角預設年齡 29、角色性格標籤預設選項，以及自訂 canonical ID 欄位英文輸入說明。 |
| v1.2.4 | 2026-04-28 | 補充 Phase 1-G-1 使用者操作回饋：UIW 分頁順序與中文/英文導覽顯示、每頁下一頁按鈕、已選風格中文顯示、主角職業/性格/秘密預設選項，以及初始債務等級模式。 |
| v1.2.3 | 2026-04-27 | 明確規定 `required_flags` / `forbidden_flags` 必須使用 `flag.<id> == <value>` 完整表達式；明確 `status_flags.effect` 為 list of dict 並只在資料層要求非空。 |
| v1.2.2 | 2026-04-27 | 補充 Phase 1-F UI 可先採用樸素表單與表格實作，完整地圖樹可留到 Dashboard 階段。 |
| v1.2.1 | 2026-04-27 | 將 Setup Package 輸出的 `uiw_version` 統一為 `1.2`，並更新文件管線引用至 v1.1。 |
| v1.2 | 2026-04-27 | 新增 UI 參考選項與點選帶入規則；補充風格關鍵字參考詞庫、地點模板、主地點/子地點建立流程與 UI 編排要求。 |
| v1.1 | 2026-04-27 | 將 Wizard 欄位映射為 canonical data；補強 Map Manager 欄位、structured schedule、Flag Registry、Status Flag Lifecycle、Schedule Conflict Resolution、Review & Export。 |

## 1. 文件目的

本文件定義 User Input Wizard 需要向使用者收集的初始設定，以及這些設定如何轉換為「沙盒戀愛模擬遊戲規格 v1.2」可使用的結構化資料。

User Input Wizard 不只是問卷介面。它的輸出應該是一組可供 Mega-Prompt、Map Manager、Linter、Route Validator、Auto Repair Layer 與資產管理器共同使用的 canonical data。

## 2. 設計原則

### 2.1 使用者介面顯示中文，系統資料使用英文 ID

Wizard 介面可顯示中文欄位、中文選項與中文說明，但輸出給 DSL、Markdown、素材檔名與驗證器時，必須使用穩定英文 ID。

範例：

```yaml
allowed_emotions:
  - id: neutral
    label: 平常
  - id: love_struck
    label: 暈了
```

在 Markdown DSL 中應寫：

```md
[Character: sophie, Costume: casual, Emotion: love_struck, Position: center]
```

不得寫：

```md
[Character: 蘇菲, Costume: 私服, Emotion: 暈了]
```

### 2.2 決定性優先

UIW 不應產生不可重現的隱藏隨機值。若使用隨機，必須使用 seed，並將 seed 與結果記錄在輸出資料中。

### 2.3 輸出資料必須可驗證

每個角色、地點、旗標、結局、素材標籤都應有唯一 ID。UIW 完成後，應先執行 UIW Linter，檢查是否有缺漏、重複或不合法 ID。

### 2.4 參考選項可點選帶入

Wizard 介面應在容易空泛或需要大量輸入的欄位旁提供參考選項。使用者可以手動輸入，也可以點選參考詞、模板或預設值快速帶入。

設計原則：

- 參考選項必須顯示中文 label。
- 寫入資料模型時必須使用英文 canonical ID。
- 點選參考選項後，使用者仍可修改。
- 參考選項不可限制使用者創作，只作為快速填入與格式引導。
- 若使用者輸入自訂值，系統應要求補上英文 ID 或自動檢查 ID 合法性。

範例：

```yaml
style_presets:
  - id: urban_romance
    label: 都市戀愛
  - id: black_humor
    label: 黑色幽默
```

---

## 第一階段：世界觀與曆法 (World Meta)

定義遊戲的時間跨度、社會背景與敘事風格。

### 1.1 遊戲識別碼

- UI Label: 遊戲識別碼
- Field: `world.world_id`
- Type: string
- Required: true
- 說明: 系統使用的英文唯一編號。
- 範例: `summer_city_2026`

命名規則：

- 小寫英文、數字、底線
- 不可使用空格
- 不可使用中文

### 1.2 遊戲標題

- UI Label: 遊戲標題
- Field: `world.title`
- Type: string
- Required: true
- 說明: 顯示於遊戲介面上的標題。

### 1.3 日期與天數

- UI Label: 開始日期
- Field: `world.start_date`
- Type: date
- Required: true
- Format: `YYYY-MM-DD`

- UI Label: 結束日期
- Field: `world.end_date`
- Type: date
- Required: true
- Format: `YYYY-MM-DD`

系統輸出：

```yaml
total_days: auto_calculated
calendar_rules:
  weekday_logic: enabled
  holiday_logic: optional
```

說明：

- 系統將由開始日期與結束日期自動計算 `total_days`。
- 若使用節日邏輯，節日必須可被明確列出，不應只由 AI 即興判定。

### 1.4 時間段

預設時間段：

```yaml
time_slots:
  - morning
  - afternoon
  - evening
```

UI 顯示：

- 上午
- 下午
- 晚上

### 1.5 風格關鍵字

- UI Label: 風格關鍵字
- Field: `world.global_style`
- Type: semantic choice array (`id + label`)
- Required: at least 1
- Max: 5

範例：

```yaml
global_style:
  - id: black_humor
    label: 黑色幽默
  - id: class_anxiety
    label: 階級焦慮
  - id: urban_romance
    label: 都市戀愛
```

Phase 1-G-3 起，風格關鍵字必須同時保存英文 `id` 與中文 `label`。英文 `id` 供系統驗證與後續引用；中文 `label` 供使用者確認與 AI 生成劇情時理解語意。

#### 風格參考詞庫

UI 應在欄位旁提供可點選參考詞。點選後加入 `world.global_style`，使用者也可手動輸入自訂風格。

建議參考詞：

```yaml
style_presets:
  - id: urban_romance
    label: 都市戀愛
  - id: school_life
    label: 校園生活
  - id: coming_of_age
    label: 青春成長
  - id: comedy
    label: 喜劇
  - id: black_humor
    label: 黑色幽默
  - id: class_anxiety
    label: 階級焦慮
  - id: melancholy
    label: 淡淡憂鬱
  - id: mystery
    label: 懸疑
  - id: slice_of_life
    label: 日常系
  - id: social_satire
    label: 社會諷刺
  - id: bittersweet
    label: 苦甜戀愛
  - id: healing
    label: 治癒
```

UI 行為：

- 參考詞可用 chip / tag button 呈現。
- 使用者點選後加入已選清單。
- 已選詞可移除。
- 自訂輸入若為中文，系統應要求使用者補一個英文 ID，或在匯出前由使用者確認 canonical ID。

---

## 第二階段：主角設定 (Protagonist)

定義玩家的初始能力、社會階級、財務壓力與秘密。

### 2.1 主角 ID

- UI Label: 主角 ID
- Field: `protagonist.protagonist_id`
- Type: string
- Required: true
- Default: `protagonist`

命名規則同 `world_id`。

Phase 1-G-2 起，Interactive UIW 不顯示主角 ID 輸入欄位。主角 ID 在遊戲設計上固定為 `protagonist`，避免一般使用者誤改。

輸出資料仍必須包含：

```yaml
protagonist_id: protagonist
```

### 2.2 基本身分

- UI Label: 主角姓名
- Field: `protagonist.name`
- Type: string
- Required: true

- UI Label: 主角性別
- Field: `protagonist.gender`
- Type: enum
- Required: true

選項：

```yaml
- id: male
  label: 男性
- id: female
  label: 女性
- id: non_binary
  label: 非二元
```

- UI Label: 主角年齡
- Field: `protagonist.age`
- Type: integer
- Required: true
- UI Default: `29`

- UI Label: 主角職業
- Field: `protagonist.occupation`
- Type: semantic choice (`id + label`)
- Required: true

範例：

```yaml
occupation:
  id: cafe_staff
  label: 咖啡廳店員
```

### 2.3 初始數值

核心能力範圍為 1-10，普通人為 5。

```yaml
initial_stats:
  INT: 5
  CHA: 5
  STR: 5
  MORAL: 5
```

欄位說明：

- `INT`: 智力，影響推理、學習、談判、解謎類事件。
- `CHA`: 魅力，影響社交、說服、第一印象。
- `STR`: 勇氣，影響冒險、對抗、保護他人或承擔風險。
- `MORAL`: 道德，影響誠實、責任感、是否能走向特定結局。

### 2.4 財務與生存壓力

- UI Label: 初始現金
- Field: `protagonist.initial_stats.Cash`
- Type: integer
- Required: true
- Range: 0 - 100000

- UI Label: 是否有初始債務
- Field: `protagonist.has_debt`
- Type: boolean
- Required: true

Phase 1-G-1 起，Interactive UIW 的初始債務設定使用等級模式。使用者在 UI 中選擇債務等級，系統將等級映射為 canonical `protagonist.initial_stats.Debt` 數值。

#### 等級模式

```yaml
debt_mode: tier
debt_tier: high
Debt: auto_calculated_from_tier
```

等級建議：

- `none`: 無債務
- `low`: 低債務
- `medium`: 中債務
- `high`: 高債務
- `desperate`: 絕望級債務

說明：

- `debt_tier` 屬 UI 收集策略，不一定需要寫入 Setup Package canonical schema。
- Setup Package canonical data 只需保存已計算完成的 `Debt: int`。
- 若後續需要保存 UI 草稿狀態，應另建 UI draft model，不污染 Setup Package canonical schema。

### 2.5 性格與秘密

- UI Label: 性格描述
- Field: `protagonist.personality`
- Type: semantic choice (`id + label`)
- Required: true

- UI Label: 主角的秘密
- Field: `protagonist.secrets`
- Type: semantic choice array (`id + label`)
- Required: false
- Max: 3

範例：

```yaml
personality:
  id: kind_but_tired
  label: 善良但疲憊
secrets:
  - id: family_debt
    label: 背負家族債務
  - id: past_betrayal
    label: 曾背叛重要的人
```

用途：

- 影響 AI 生成對話語氣
- 生成內心獨白
- 建議初始 Flag
- 影響特定事件與結局條件

### 2.6 Phase 1-G-1 UI 操作回饋規格

Phase 1-G-1 是使用者實際操作 Interactive UIW 後的第一批操作體驗調整。此階段不改變 Setup Package canonical schema，優先改善 UI 導覽、顯示文字與預設選項。

#### 上方導覽順序

上方設定項目的順序必須為：

```text
World
-> Protagonist
-> Characters
-> Locations
-> Flags/Status/Endings
-> Review & Export
```

#### 上方導覽顯示文字

上方設定項目必須顯示為「中文名稱(英文名稱)」：

```text
世界觀與曆法(World)
主角設定(Protagonist)
角色設定(Characters)
地點與地圖(Locations)
旗標/狀態/結局(Flags/Status/Endings)
預覽與匯出(Review & Export)
```

#### 下一頁按鈕

每一個設定頁面的最下面都必須新增「下一頁」按鈕。點擊後，UI 應移動到下一個設定項目。

例外：

- `Review & Export` 是最後一頁，不需要「下一頁」按鈕。

#### 已選風格顯示

`世界觀與曆法` 頁面最下面的「已選風格：」後方，已選項目必須顯示中文 label。

資料保存仍使用英文 canonical ID。

範例：

```yaml
global_style:
  - urban_romance
  - black_humor
```

UI 顯示：

```text
已選風格：都市戀愛、黑色幽默
```

#### 主角欄位預設選項

`主角設定` 頁面的以下欄位必須提供 6-12 個可點選預設選項：

- 職業
- 性格描述
- 主角的秘密

預設選項必須顯示中文 label，寫入資料模型時使用英文 canonical ID 或使用者手動輸入的自訂值。

範例：

```yaml
occupation_presets:
  - id: student
    label: 學生
  - id: part_time_worker
    label: 打工族

personality_presets:
  - id: kind_but_tired
    label: 善良但疲憊

secret_presets:
  - id: family_debt
    label: 背負家族債務
```

#### 初始債務等級

Interactive UIW 不提供任意金額輸入作為主要流程，改提供債務等級選單。

建議映射：

```yaml
debt_tiers:
  - id: none
    label: 無債務
    Debt: 0
  - id: low
    label: 低債務
    Debt: 10000
  - id: medium
    label: 中債務
    Debt: 50000
  - id: high
    label: 高債務
    Debt: 120000
  - id: desperate
    label: 絕望級債務
    Debt: 300000
```

### 2.7 Phase 1-G-2 UI 操作回饋規格

Phase 1-G-2 是使用者實際操作 Interactive UIW 後的第二批操作體驗調整。此階段不改變 Setup Package canonical schema，優先簡化不必要欄位、降低英文 ID 暴露量，並補足自訂 ID 的輸入說明。

#### 主角 ID 固定隱藏

主角 ID 固定為 `protagonist`，Interactive UIW 不需要顯示主角 ID 輸入欄位。

規則：

- UI 不顯示 `protagonist.protagonist_id`。
- 系統建構 Setup Package 時自動填入 `protagonist`。
- 匯出的 Setup Package 仍保留 `protagonist_id: protagonist`。

#### 主角預設年齡

主角年齡的 UI 預設值改為 `29`。

使用者仍可手動調整年齡。

#### 選項中文化

主角或角色相關 enum 欄位在 UI 中顯示中文 label，不直接顯示英文 ID。

適用欄位：

- 主角性別 `protagonist.gender`
- 角色性別 `characters[].gender`
- 角色性取向 `characters[].orientation`
- 角色定位 `characters[].role`

資料保存仍使用英文 canonical ID。

範例：

```yaml
gender_options:
  - id: male
    label: 男性
  - id: female
    label: 女性
  - id: non_binary
    label: 非二元

orientation_options:
  - id: heterosexual
    label: 異性戀
  - id: homosexual
    label: 同性戀
  - id: bisexual
    label: 雙性戀
  - id: pansexual
    label: 全性戀

role_options:
  - id: main_love_interest
    label: 主要攻略對象
  - id: key_supporting_character
    label: 關鍵配角
```

#### 角色性格標籤預設選項

角色的 `personality_tags` 欄位必須提供可點選預設選項。

預設選項顯示中文 label。Phase 1-G-3 起，寫入資料模型時保存 `id + label`。

範例：

```yaml
character_personality_tag_presets:
  - id: guarded
    label: 戒心重
  - id: proud
    label: 自尊心強
  - id: secretly_kind
    label: 其實很溫柔
  - id: cheerful
    label: 開朗
  - id: cynical
    label: 犬儒
  - id: diligent
    label: 認真努力
```

使用者仍可新增自訂性格標籤。Phase 1-G-3 起，使用者輸入中文 label，由工具產生 canonical ID，最終保存 `id + label`。

#### 自訂 ID 輸入說明

凡是 UI 欄位名稱包含 `ID`，或輸入值會作為 canonical ID / tag 寫入 Setup Package 時，自訂輸入必須使用英文 canonical ID。

Phase 1-G-3 起，職業、主角性格、主角秘密、世界風格與角色性格標籤等語意型欄位，不應要求一般使用者直接輸入英文 ID。UI 應提供中文自訂輸入框，按下「選擇」後由工具產生系統 ID，並保留可進階手動修改的系統 ID 欄位。

規則：

- 小寫英文、數字、底線。
- 必須以英文字母開頭。
- 不可使用中文。
- 不可使用空格。

UI 必須在相關欄位旁顯示說明文字。

建議文案：

```text
請輸入英文 ID：小寫英文、數字、底線，且必須以英文字母開頭。
中文名稱或描述請填在顯示名稱、描述或秘密等文字欄位。
```

適用範例：

- 自訂職業 ID
- 自訂性格 ID
- 自訂性格標籤 ID
- 自訂風格 ID
- 自訂地點 ID
- 自訂角色 ID

純顯示或敘事文字欄位可使用中文，例如：

- 主角姓名
- 角色顯示名稱
- 地點名稱
- 身分描述
- 秘密描述
- 結局描述

### 2.8 Phase 1-G-3 UI 操作回饋規格

Phase 1-G-3 解決「使用者用中文理解、AI 需要中文語意、系統需要英文 ID」三者落差。此階段會變更 Setup Package canonical schema：語意型選項不再只保存英文 ID 字串，而是保存 `id + label`。

#### 語意型欄位

下列欄位必須改為 `id + label`：

```yaml
world.global_style:
  - id: urban_romance
    label: 都市戀愛

protagonist.occupation:
  id: cafe_staff
  label: 咖啡廳店員

protagonist.personality:
  id: kind_but_tired
  label: 善良但疲憊

protagonist.secrets:
  - id: family_debt
    label: 背負家族債務

characters[].personality_tags:
  - id: guarded
    label: 戒心重

characters[].secrets:
  - id: family_scandal
    label: 家族醜聞
```

純系統 ID 欄位維持英文 ID 字串，不改為 `id + label`，例如 `world_id`、`character_id`、`location_id`、`flag_id`、`status_id`、`ending_id`、`schedule_id`、`parent_location_id`、`target_character_id`。

#### UI 輸入模式

職業、主角性格、主角秘密、NPC 秘密、世界風格與角色性格標籤等語意型欄位，應採用一致 UI：

- 上方：預設中文選項按鈕，點選後直接帶入對應 `id + label`。
- 中間：自訂中文輸入框 +「選擇」按鈕。
- 下方：系統 ID 欄位，自動填入，可進階手動修改。
- 結果區：清楚顯示目前選擇，不再只用灰色 caption。

結果區範例：

```text
目前選擇：咖啡廳店員
系統 ID：cafe_staff
```

自訂中文輸入不稱為翻譯；工具行為定義為「依中文名稱產生穩定系統 ID」。不使用 AI 時，預設選項使用手寫 ID；自訂中文可先查內建對照表，找不到時使用 deterministic fallback，例如拼音 ID 或 hash ID。實作時需明確選定 fallback 策略並補測試。

#### 主角職業預設選項

保留 Phase 1-G-1 原本 8 個主角職業預設選項，並新增 8 個社會地位中到高的選項，總數為 16 個。

新增選項：

```yaml
- id: rich_heir
  label: 富二代
- id: startup_founder
  label: 新創公司老闆
- id: tech_worker
  label: 科技業
- id: finance_professional
  label: 金融業
- id: doctor
  label: 醫師
- id: lawyer
  label: 律師
- id: university_lecturer
  label: 大學講師
- id: graphic_designer
  label: 平面設計師
```

#### 主角與 NPC 秘密複選

`protagonist.secret` 改為 `protagonist.secrets`。
`characters[].secret` 改為 `characters[].secrets`。

規則：

- 每個主角或 NPC 最多選 3 個。
- 可選預設項目。
- 可新增自訂中文秘密。
- 每個秘密保存 `id + label`。
- UI 必須清楚顯示目前已選秘密。
- `none = 沒有秘密` 若被選取，不可與其他秘密並存。

新增 8 個秘密預設：

```yaml
- id: hidden_wealth
  label: 其實家境富裕
- id: criminal_record
  label: 曾有犯罪紀錄
- id: secret_childhood_friend
  label: 隱瞞童年舊識
- id: family_scandal
  label: 家族醜聞
- id: forbidden_relationship
  label: 曾有禁忌戀情
- id: fake_education
  label: 學歷造假
- id: underground_job
  label: 從事地下工作
- id: terminal_illness_in_family
  label: 家人身患重病
```

#### 驗證規則

UIW Linter 需新增或調整：

- 語意型欄位的 `id` 必須符合 canonical ID 規則。
- 語意型欄位的 `label` 不可為空。
- `protagonist.secrets` 最多 3 個。
- `characters[].secrets` 最多 3 個。
- `none` 不可和其他秘密同時存在。
- `characters[].personality_tags[].id` 不可重複。
- `world.global_style[].id` 不可重複。

---

## 第三階段：地點與地圖規則 (Location & Map)

建立具備層級關係的沙盒地圖，供 Map Manager 解析 free_roam 狀態。

### 3.1 地點類型

#### 主地點 / 區域 (Container)

不具備直接進入功能，僅作為容器。

範例：

- 學校
- 商店街
- 車站周邊

若主地點關閉，其下所有子地點皆不可進入。

#### 子地點 (Sub-location)

隸屬於主地點，玩家實際移動的目標。

範例：

- 2年A班
- 操場
- 圖書室

#### 獨立地點 (Standalone)

單一功能地點，無子地點。

範例：

- 主角家
- 電影院
- 便利商店

### 3.1.1 地點模板與參考選項

UI 應提供地點模板，讓使用者點選後自動帶入常用欄位。模板只負責建立草稿，使用者仍可修改名稱、ID、標籤、時間段與條件。

#### 主地點 / 區域模板

```yaml
container_templates:
  - template_id: school_container
    label: 學校
    location_id_suggestion: school
    location_type: container
    is_visitable: false
    tags:
      - school
      - public
    suggested_sub_locations:
      - classroom
      - library
      - rooftop
      - sports_ground

  - template_id: shopping_street_container
    label: 商店街
    location_id_suggestion: shopping_street
    location_type: container
    is_visitable: false
    tags:
      - commercial
      - public
    suggested_sub_locations:
      - cafe
      - convenience_store
      - arcade

  - template_id: station_area_container
    label: 車站周邊
    location_id_suggestion: station_area
    location_type: container
    is_visitable: false
    tags:
      - transit
      - public
    suggested_sub_locations:
      - station_square
      - ticket_gate
      - bus_stop
```

#### 子地點模板

```yaml
sub_location_templates:
  - template_id: classroom
    label: 教室
    location_id_suffix: classroom
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
    tags:
      - indoor
      - school

  - template_id: library
    label: 圖書室
    location_id_suffix: library
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
    tags:
      - indoor
      - study

  - template_id: cafe
    label: 咖啡廳
    location_id_suffix: cafe
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - afternoon
      - evening
    tags:
      - date_spot
      - commercial
```

#### 獨立地點模板

```yaml
standalone_templates:
  - template_id: protagonist_home
    label: 主角家
    location_id_suggestion: protagonist_home
    location_type: standalone
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
      - evening
    tags:
      - home
      - rest
    empty_behavior: allow_rest

  - template_id: cinema
    label: 電影院
    location_id_suggestion: cinema
    location_type: standalone
    is_visitable: true
    available_time_slots:
      - afternoon
      - evening
    tags:
      - date_spot
      - entertainment
    base_cost: 300

  - template_id: convenience_store
    label: 便利商店
    location_id_suggestion: convenience_store
    location_type: standalone
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
      - evening
    tags:
      - commercial
      - part_time_job
```

### 3.1.2 地點建立 UI 編排

地點頁面應清楚呈現主地點、子地點與獨立地點的差異。

建議 UI：

```text
左側：地圖樹
  - 學校
    - 2年A班
    - 圖書室
    - 操場
  - 主角家
  - 商店街
    - 咖啡廳
    - 便利商店

中間：模板與新增按鈕
  - 新增主地點
  - 新增子地點
  - 新增獨立地點
  - 套用地點模板

右側：目前選取地點的欄位編輯器
```

UI 行為：

- 點選「新增主地點」時，建立 `location_type: container` 且 `is_visitable: false`。
- 只要建立主地點，UI 必須提示使用者建立至少一個子地點。
- 若主地點沒有任何 `is_visitable: true` 的子地點，UIW Linter 必須報錯。
- 點選主地點後按「新增子地點」，`parent_location_id` 應自動帶入該主地點 ID。
- 子地點必須隸屬於某個主地點。
- 獨立地點不可有 `parent_location_id`。
- 玩家實際可移動目標只應是 `sub_location` 或 `standalone`。

Phase 1-F 的 Interactive UIW Prototype 可先採用樸素表單與表格實作，不必完成正式地圖樹。最小可行 UI 可以是：

```text
地點清單表格
+ 新增地點表單
+ parent_location_id 下拉選單
+ 套用地點模板按鈕
+ Validate 時檢查 container 是否有 sub_location
```

完整地圖樹、拖拉排序與視覺化編輯可留到 Dashboard 階段。

### 3.2 地點資料

每個地點都必須有唯一 `location_id`。

```yaml
locations:
  - location_id: school
    name: 學校
    location_type: container
    parent_location_id: null
    is_visitable: false
    base_cost: 0
    available_time_slots:
      - morning
      - afternoon
    tags:
      - school
      - public
    unlock_conditions:
      - day >= 1
    closed_conditions: []
    map_priority: high
    map_display_group: campus
    default_npc_capacity: 10
    empty_behavior: hidden

  - location_id: school_library
    name: 圖書室
    location_type: sub_location
    parent_location_id: school
    is_visitable: true
    base_cost: 0
    available_time_slots:
      - morning
      - afternoon
    tags:
      - indoor
      - study
    unlock_conditions:
      - day >= 1
    closed_conditions: []
    map_priority: normal
    map_display_group: campus
    default_npc_capacity: 4
    empty_behavior: show_ambient_text
    ambient_text: 圖書室裡很安靜，書頁翻動的聲音比腳步聲還清楚。
```

### 3.3 欄位說明

- `location_id`: 系統使用的英文唯一 ID。
- `name`: 使用者與玩家看到的中文名稱。
- `location_type`: `container`、`sub_location` 或 `standalone`。
- `parent_location_id`: 父地點 ID。子地點必填，其他類型可為 `null`。
- `is_visitable`: 玩家是否能直接進入。
- `base_cost`: 入場費或基本消費。
- `available_time_slots`: 可進入時間段。
- `tags`: 地點標籤，用於生成與事件篩選。
- `unlock_conditions`: 解鎖條件。
- `closed_conditions`: 關閉條件。
- `map_priority`: 地圖顯示與事件排序用優先權。
- `map_display_group`: 地圖 UI 分組。
- `default_npc_capacity`: 預設可容納 NPC 數量，用於 Map Manager 分配角色。
- `empty_behavior`: 無事件或無 NPC 時的呈現方式。
- `ambient_text`: 空地點文字，可選。

### 3.4 Empty Behavior

可用值：

```yaml
empty_behavior:
  - hidden
  - show_empty
  - show_ambient_text
  - allow_rest
  - allow_wait
```

說明：

- `hidden`: 沒有內容時不顯示在可選地點。
- `show_empty`: 顯示地點，但進入後提示目前沒有特別事件。
- `show_ambient_text`: 顯示地點並播放環境敘述。
- `allow_rest`: 可在此消耗時間恢復狀態。
- `allow_wait`: 可在此等待下一個時間段。

---

## 第四階段：角色完整模組 (Character Module)

將角色的社會身分、行為動態、路線定位與視覺標籤進行綁定。

### 4.1 角色 ID 與基本檔案

- UI Label: 角色 ID
- Field: `characters[].character_id`
- Type: string
- Required: true
- 範例: `sophie`

命名規則：

- 小寫英文、數字、底線
- 不可使用空格
- 不可使用中文
- 每位角色不可重複

- UI Label: 顯示名稱
- Field: `characters[].display_name`
- Type: string
- Required: true
- 範例: `蘇菲`

- UI Label: 性別
- Field: `characters[].gender`
- Type: enum
- Required: true

選項：

```yaml
- id: male
  label: 男
- id: female
  label: 女
- id: non_binary
  label: 非二元
```

- UI Label: 性取向
- Field: `characters[].orientation`
- Type: enum array
- Required: true

選項：

```yaml
- id: heterosexual
  label: 異性戀
- id: homosexual
  label: 同性戀
- id: bisexual
  label: 雙性戀
- id: pansexual
  label: 全性戀
```

- UI Label: 定位
- Field: `characters[].role`
- Type: enum
- Required: true

選項：

```yaml
- id: main_love_interest
  label: 主要攻略對象
- id: key_supporting_character
  label: 關鍵配角
```

### 4.2 社會身分與敘事資訊

- UI Label: 身分
- Field: `characters[].identity`
- Type: string
- Required: true
- 範例: `主角的同班同學`

- UI Label: 性格標籤
- Field: `characters[].personality_tags`
- Type: semantic choice array (`id + label`)
- Required: true

Phase 1-G-2 起，Interactive UIW 應提供角色性格標籤預設選項。Phase 1-G-3 起，UI 顯示中文 label，寫入 `personality_tags` 時保存 `id + label`。

- UI Label: 秘密
- Field: `characters[].secrets`
- Type: semantic choice array (`id + label`)
- Required: false
- Max: 3

Phase 1-G-3 起，NPC / Character 秘密與主角秘密使用同一格式與限制：

```yaml
secrets:
  - id: family_scandal
    label: 家族醜聞
```

- UI Label: 初始好感度
- Field: `characters[].initial_favor`
- Type: integer
- Required: true
- Default: 0

### 4.3 角色生活動態 (Schedule)

角色行程必須輸出為可解析結構。UI 可以用中文表格呈現，但保存時應使用英文 ID。

範例：

```yaml
schedule:
  - schedule_id: sophie_weekday_morning
    day_type: weekday
    time_slot: morning
    location_id: school_class_2a
    condition:
      - day >= 1
    priority: normal
    schedule_order: 20

  - schedule_id: sophie_weekday_afternoon_library
    day_type: weekday
    time_slot: afternoon
    location_id: school_library
    condition:
      - flag.sophie_route_started == true
    priority: route
    schedule_order: 10

  - schedule_id: sophie_weekend_afternoon
    day_type: weekend
    time_slot: afternoon
    location_id: central_park
    condition:
      - day >= 1
    priority: normal
    schedule_order: 30
```

欄位說明：

- `schedule_id`: 行程唯一 ID。
- `day_type`: `weekday`、`weekend`、`holiday` 或 `specific_date`。
- `time_slot`: `morning`、`afternoon`、`evening`。
- `location_id`: 角色所在位置。
- `condition`: 行程生效條件。
- `priority`: `critical`、`route`、`normal`、`ambient`。
- `schedule_order`: 同優先權時的排序值。數字越小，越優先。

週末行程可以選擇「由 AI 根據身分與性格推導」，但推導後必須寫回固定 schedule，不可在 runtime 每次重新生成。

#### Schedule Conflict Resolution

若同一角色在同一天、同一時間段中，有多個行程條件同時成立，Map Manager 必須使用固定規則決定角色位置，不可交由 AI 即興判斷。

角色位置解析順序：

1. `priority` 較高者優先：`critical > route > normal > ambient`。
2. 條件更具體者優先。例如 `flag.sophie_route_started == true` 比 `day >= 1` 更具體。
3. 日期更具體者優先：`specific_date > holiday > weekend/weekday > any`。
4. 與主線、角色路線或結局前置相關者優先。
5. 若前一事件剛設定角色位置，且時間尚未推進，可保留最近劇情鎖定位置。
6. `schedule_order` 數字較小者優先。
7. 若仍完全相同，使用 `schedule_id` 字母排序作為 deterministic fallback。

AI 生成或推導 schedule 時，應避免產生「同角色、同時間段、同 priority、條件可能同時成立、且沒有 `schedule_order`」的行程。若不可避免，必須提供更具體的 condition 或明確的 `schedule_order`。

### 4.4 受控素材清單

受控素材清單用於避免 AI 任意創造角色表情與服裝。

UI 顯示中文；受控素材選項保存 `id + label`，事件與 DSL 引用時使用其中的英文 `id`。

#### 表情白名單

預設選項：

```yaml
allowed_emotions:
  - id: neutral
    label: 平常
  - id: happy
    label: 開心
  - id: surprised
    label: 驚訝
  - id: angry
    label: 憤怒
  - id: sad
    label: 悲傷
  - id: embarrassed
    label: 害羞
  - id: contempt
    label: 鄙視
  - id: love_struck
    label: 暈了
```

說明：

- `love_struck` 的中文顯示為「暈了」。
- 此處的「暈了」指「暈船、上頭、已經迷戀對方」的狀態，不是生理上的昏倒或暈眩。
- 若需要真正昏倒，應另外使用 `fainted` 或 status flag，不應混用。

#### 服裝白名單

預設選項：

```yaml
allowed_costumes:
  - id: school_uniform
    label: 校服
  - id: casual
    label: 私服
  - id: work_uniform
    label: 工作服
  - id: pajamas
    label: 睡衣
  - id: formal
    label: 正裝
  - id: swimsuit
    label: 泳裝
  - id: sportswear
    label: 體育服
  - id: maid_butler
    label: 女僕/執事
  - id: special_cosplay
    label: 特殊/Cosplay
```

#### 位置白名單

```yaml
allowed_positions:
  - id: left
    label: 左
  - id: center
    label: 中
  - id: right
    label: 右
```

### 4.5 Alias Table

Alias Table 用於 Auto Repair Layer 將中文或同義詞映射回 canonical ID。

範例：

```yaml
emotion_aliases:
  平常: neutral
  普通: neutral
  開心: happy
  高興: happy
  驚訝: surprised
  嚇到: surprised
  憤怒: angry
  生氣: angry
  悲傷: sad
  難過: sad
  害羞: embarrassed
  臉紅: embarrassed
  鄙視: contempt
  不屑: contempt
  暈了: love_struck
  暈船: love_struck
  上頭: love_struck
```

---

## 第五階段：旗標、系統狀態與結局 (Logic & Goals)

定義遊戲的初始旗標、狀態、運算邏輯與終極目標。

### 5.1 Flag Registry

所有初始旗標都必須宣告型別、初始值與用途。

範例：

```yaml
flags:
  - flag_id: is_unemployed
    type: boolean
    initial_value: true
    description: 主角目前沒有工作。

  - flag_id: sophie_route_started
    type: boolean
    initial_value: false
    description: 蘇菲路線是否已開始。
```

欄位說明：

- `flag_id`: 旗標唯一 ID。
- `type`: `boolean`、`integer`、`string`、`enum`。
- `initial_value`: 初始值。
- `description`: 給使用者與 AI 理解用途的中文說明。

### 5.2 Status Flags

Status Flags 用於描述會影響移動、時間或事件觸發的狀態。

範例：

```yaml
status_flags:
  - status_id: overworked
    label: 過勞
    target: protagonist
    effect:
      - block_time_slot: evening
    duration:
      type: time_slots
      value: 1
    clear_rule:
      - on_time_advance
      - on_rest
    description: 主角太累，晚上無法外出。
```

欄位說明：

- `status_id`: 狀態旗標的英文唯一 ID。
- `label`: 使用者介面顯示的中文名稱。
- `target`: 狀態作用對象，例如 `protagonist` 或特定 `character_id`。
- `effect`: 狀態造成的規則效果，例如鎖定時間段、禁止移動、限制地點、修改數值倍率。輸出為 list of dict，每筆使用單鍵格式（例如 `- block_time_slot: evening`）。Phase 3 Status Manager 才解析 dict 內容；資料層僅要求非空。
- `duration`: 狀態持續時間。
- `clear_rule`: 狀態解除條件。
- `description`: 給使用者與 AI 理解用途的中文說明。

#### Status Flag Lifecycle

所有 Status Flag 都必須定義解除機制。除非明確標記為永久狀態，否則不得產生沒有 `duration` 或 `clear_rule` 的狀態。

可用 `duration.type`：

```yaml
duration_types:
  - time_slots
  - days
  - until_event
  - until_cleared
  - permanent
```

可用 `clear_rule`：

```yaml
clear_rules:
  - on_time_advance
  - on_day_end
  - on_rest
  - on_item_used
  - on_event_result
  - on_location_visit
  - manual_only
```

說明：

- `on_time_advance`: 時間段推進後解除。
- `on_day_end`: 當日結束後解除。
- `on_rest`: 玩家執行休息行動後解除。
- `on_item_used`: 使用特定道具後解除。
- `on_event_result`: 由特定事件結果解除。
- `on_location_visit`: 前往特定地點後解除。
- `manual_only`: 只能由劇情或系統明確解除。

若狀態為永久狀態，必須明確寫出：

```yaml
duration:
  type: permanent
clear_rule:
  - manual_only
permanent_reason: 劇情上的長期身份變化，只有特定主線事件能解除。
```

AI 生成劇情時，若新增或套用 Status Flag，必須同時確認該狀態已存在於 Status Flag Registry，且具備 `effect`、`duration` 與 `clear_rule`。不得生成無解除條件的負面狀態。

### 5.3 結局設定 (Endings)

結局設定用於 Route Validator 與 Critical Path Mode 判定是否存在可達成路線。

範例：

```yaml
endings:
  - ending_id: sophie_good_ending
    title: 蘇菲 Good Ending
    ending_type: character_good
    target_character_id: sophie
    description: 主角與蘇菲互相理解，並一起面對債務與家庭問題。
    required_flags:
      - flag.sophie_route_completed == true
    required_stats:
      - character.sophie.favor >= 80
      - stat.Debt <= 0
    forbidden_flags:
      - flag.sophie_bad_breakup == true
    priority: critical
    route_tags:
      - character_route:sophie
      - critical
      - ending_prerequisite
```

#### 結局欄位中文說明

- `ending_id`: 結局的英文唯一 ID。系統、Validator 與 DSL 會使用它來判斷路線。
- `title`: 結局顯示名稱，玩家或開發者看到的文字。
- `ending_type`: 結局類型，例如角色好結局、角色壞結局、普通結局、債務結局、隱藏結局。
- `target_character_id`: 此結局主要關聯的角色。若是全局結局，可留空或使用 `global`。
- `description`: 結局內容摘要，給 AI 生成最後劇情時參考。
- `required_flags`: 必須成立的旗標條件。例如某角色路線已完成。每一條都必須使用 `flag.<flag_id> == <value>` 的完整表達式，不得只寫裸 `flag_id`。
- `required_stats`: 必須達成的數值條件。例如好感度、現金、債務、道德值。
- `forbidden_flags`: 若這些旗標成立，則此結局不可達成。例如已分手、角色死亡、重大背叛。表達式格式同 `required_flags`。
- `priority`: 驗證優先權。`critical` 代表 Route Validator 應優先測試。
- `route_tags`: 路線標籤，用於 Critical Path Mode、Flowchart 篩選與報告分類。

---

## 第六階段：設定摘要與輸出 (Review & Export)

UIW 完成後，必須顯示設定摘要，並輸出可被後續系統使用的資料包。此 Markdown 輸出稱為 Setup Package MD。

Setup Package MD 的完整格式與後續 Event Blueprint MD 流程，請參閱：

- `Sandbox_Dating_Sim_文件管線規格_v1.1.md`

### 6.1 設定摘要

摘要應包含：

- World YAML
- Protagonist YAML
- Location YAML
- Character YAML
- Schedule YAML
- Flag Registry
- Status Flags
- Ending YAML
- Asset Vocabulary
- Alias Table

### 6.2 UIW Linter

輸出前應執行 UIW Linter。

檢查項目：

- `world_id` 是否合法
- 日期是否有效
- `end_date` 是否晚於 `start_date`
- 角色 ID 是否重複
- 地點 ID 是否重複
- 子地點的 `parent_location_id` 是否存在
- 可進入地點是否至少有一個 time slot
- schedule 是否引用存在的地點
- schedule 是否引用合法 time slot
- schedule 是否提供 `schedule_order`
- 同角色、同 day_type、同 time_slot 的 schedule 是否存在無法解析的同優先權衝突
- 表情、服裝、位置是否有 canonical ID
- flag ID 是否重複
- status flag 是否定義 `effect`、`duration` 與 `clear_rule`
- 非永久 status flag 是否具備可達成的解除條件
- ending 是否引用存在的角色
- ending 條件是否引用已宣告 flag

### 6.3 Setup Package MD 輸出資料包

UIW 最終應輸出 Setup Package MD。Markdown 文件中主要資料應放在 YAML 區塊，工具內部則應保存 JSON 或 YAML 作為 canonical data。

Setup Package MD 的 YAML 區塊應包含：

```yaml
setup_package_version: 1.0
uiw_version: 1.2
target_game_spec_version: 1.2
world: {}
protagonist: {}
locations: []
characters: []
flags: []
status_flags: []
endings: []
asset_vocabularies: {}
alias_tables: {}
validation_report: {}
```

此資料包將作為 Mega-Prompt 生成層、Event Blueprint 生成、Map Manager、Route Validator 與資產管理器的共同輸入。

---

## 工具處理邏輯與驗證規則

1. 層級化權限檢查：若地點 A 是地點 B 的父地點，且 A 設定為關閉，則 B 自動不可進入。
2. 身分與位置合理化：當角色身分與行程位置不符時，AI 可在劇本中解釋原因，但該位置仍必須由 schedule 明確定義。
3. 受控詞彙過濾：所有劇本資產標籤若超出白名單，必須由 Auto Repair Layer 嘗試映射或交由使用者確認。
4. AI 推導內容必須寫回資料層：週末行程、建議 Flag、建議結局與素材標籤，不可只存在於 prompt 或臨時文本中。
5. 使用者介面可中文化；純系統引用欄位必須使用 canonical ID，語意型欄位必須保存 `id + label`。
6. Status Flag 必須具備生命週期：AI 不得生成沒有 `duration` 或 `clear_rule` 的負面狀態；引擎必須由 Status Manager 統一解除狀態。
7. Schedule 衝突必須 deterministic：同角色同時間段若多個行程同時成立，Map Manager 必須依 Schedule Conflict Resolution 固定排序，不可交由 AI 或 runtime 隨機判定。
8. UIW 應提供參考詞與模板：風格、地點、表情、服裝等常用欄位應提供可點選預設值；語意型選項需同時保存系統 ID 與中文 label。
9. 主地點必須具備子地點：若建立 `container`，至少要建立一個可進入的 `sub_location`，否則 Setup Package 不得通過驗證。

## v1.2 與 v1.1 的主要差異

- 新增版本紀錄。
- 新增「參考選項可點選帶入」原則。
- 新增風格關鍵字參考詞庫。
- 新增地點模板，包含主地點、子地點、獨立地點。
- 新增地點建立 UI 編排方向。
- 明確規定主地點必須至少有一個可進入子地點。
- 明確規定玩家可移動目標只應是子地點或獨立地點。

## v1.1 與 v1.0 的主要差異

- 統一 UI 顯示中文、系統輸出英文 ID 的原則。
- 將 Wizard 欄位改為可映射到資料模型的 canonical field。
- 移除不可重現的隱藏債務隨機值，改為 fixed、tier 或 seeded random。
- 補強 Map Manager 所需的 Location 欄位。
- 將 Schedule 改為可解析結構。
- 新增 `character_id`。
- 將表情、服裝與位置改為 ID + 中文 label。
- 明確定義「暈了」為 `love_struck`，代表暈船、上頭、迷戀，不代表昏倒。
- 補強 Ending 欄位，並加入中文說明。
- 新增 Flag Registry。
- 新增 Status Flag Lifecycle，要求狀態旗標必須有持續時間與解除條件。
- 新增 Schedule Conflict Resolution，定義同優先權行程的 deterministic tie-breaker。
- 新增 Review & Export 階段。
- 新增 UIW Linter 與輸出資料包格式。
