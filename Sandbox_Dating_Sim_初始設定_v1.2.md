# Sandbox Dating Sim Dev: User Input Wizard (UIW) 初始設定規格 v1.2

## 版本紀錄

| 版本 | 日期 | 內容 |
| :--- | :--- | :--- |
| v1.2.17 | 2026-05-03 | 補強 Phase 1-G-8 規格：挑邊「空 `targets` 由 schema `Field(min_length=1)` 拒絕」+「`model_validator(mode="before")` 在 schema 層 normalize 舊 `target`」；明列 fixture / 既有測試遷移工作；明列 1-G-5 / 1-G-6 同步更新；新增 UIW Linter issue types `unknown_status_target` / `empty_status_targets` / `unexpected_duration_value`；引用比對改用 word-boundary regex；`duration.type ∈ {until_event, until_cleared}` 時不顯示 value 並存 None；補純函式 helper、effect YAML corner cases、targets UI dedupe、widget key prefix 與 silent migration 鏈路。 |
| v1.2.16 | 2026-05-03 | 新增 Phase 1-G-8 規格：旗標 / 狀態頁改為清單 + inline expander 編輯；`StatusFlag.target` 升級為 `targets: list[str]`，UI 以主角 + 角色複選；持續類型改為中文(英文) 選項並加說明；`effect` 採 YAML text_area 保留 list[dict]；新增 flag/status 刪除引用防呆、keyed state 清理與相關驗收。 |
| v1.2.15 | 2026-05-03 | 補強 Phase 1-G-7 規格：全域 ID 集合補入固定 `protagonist`；明示「自動 ID 路徑因 prefix 隔離不會跨類衝突，跨類唯一只在進階手動 ID／模板套用／匯入既有資料時觸發」；模板衝突挑邊為「自動 suffix 避讓」；預覽 ID 時機定為「submit 後 caption」；suffix 連鎖規則為「順序遞增取最小未占用」。 |
| v1.2.14 | 2026-05-03 | 修正 Phase 1-G-7 規格：結局範例 ID 改為純拼音 `end_su_fei_hao_jie_ju`；旗標 ID 來源欄位改為 `description`；補 description slug 截斷、標點處理、`unnamed` fallback 與 `_make_unique_id` 包裝既有 `_generate_system_id` 的限制。 |
| v1.2.13 | 2026-05-03 | 新增 Phase 1-G-7 規格：地點 / NPC / 旗標 / 狀態 / 結局新增流程不再要求使用者輸入英文 ID，改由 UI 依中文名稱、標題、description 或 label 自動產生唯一 canonical ID；既有 ID rename / 引用搬移不納入本 phase。 |
| v1.2.12 | 2026-05-01 | 新增 Phase 1-G-6 規格：拆分旗標/狀態與結局為兩個分頁、結局頁 inline expander 編輯、priority 中文化 + 五級語意 caption、`target_character_id` 中文 selectbox、`required_flags` / `forbidden_flags` F-γ multiselect 快速加入、最小可用 Setup Package 匯出驗收；附帶修正 1-G-5 character_id 即時擋為跨類型唯一（UI 層含 `status_id`）。 |
| v1.2.11 | 2026-05-01 | 補強 Phase 1-G-5 Streamlit 實作限制：禁止 nested `st.expander`、所有編輯 widget 採 per-character keyed pattern、新增角色擋空/重複/非法 `character_id` 並禁止編輯期修改 `character_id`、刪除角色後清空相關 session state。 |
| v1.2.10 | 2026-05-01 | 補充 Phase 1-G-5 角色設定頁面 UX 完整化：角色清單顯示與刪除引用防呆、inline expander 編輯、行程清單與新增搬入編輯區、行程 enum 中文化、白名單顯示與進階設定收納；明確排除新增流程自動產生 ID（現排 1-G-7）與 schedule `specific_date` schema 升級（待後續 phase）。 |
| v1.2.9 | 2026-05-01 | 修正 Phase 1-G-4 地點模板規格：明確子地點 ID 由父地點 ID 與 suffix 組成、保留既有 standalone 模板，並區分同名便利商店模板顯示。 |
| v1.2.8 | 2026-05-01 | 補充 Phase 1-G-4 地點與地圖調整：地點頁順序提前、擴充模板、刪除引用防呆、中文化地點類型與可使用時段，並將 tags 定義為 AI 劇情參考用進階設定。 |
| v1.2.7 | 2026-05-01 | 補充 Phase 1-G-3 完成後規則：`none = 沒有秘密` 僅為 UI 清空操作，canonical data 以 `secrets: []` 表示沒有秘密；記錄 1-G-3 實作完成項目。 |
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
- `none = 沒有秘密` 是 UI 清空操作，點選後應清空秘密清單。
- Setup Package 中沒有秘密時必須保存為 `secrets: []`，不得保存 `{id: none, label: 沒有秘密}`。

AI 生成劇情時，`secrets: []` 表示使用者未指定秘密，不應自行把 `none` 解讀成角色秘密或伏筆。若後續事件需要「沒有秘密」作為條件，應使用獨立 flag，而不是在 `secrets` 中保存 `none`。

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
- `none` 不寫入 canonical data；UI 點選「沒有秘密」時應清空 secrets list。
- `characters[].personality_tags[].id` 不可重複。
- `world.global_style[].id` 不可重複。

#### Phase 1-G-3 完成紀錄

Phase 1-G-3 已完成下列項目：

- Setup Package schema 將語意型欄位升級為 `SemanticChoice` 或 `list[SemanticChoice]`。
- UIW 可用中文預設選項與中文自訂輸入建立語意型欄位，並產生合法 canonical ID。
- 主角與 NPC 秘密支援最多 3 個複選；「沒有秘密」清空秘密清單並輸出 `secrets: []`。
- 角色性格標籤與 NPC 秘密已移出 Streamlit form，避免 `st.button()` 與 `st.form()` 衝突。
- UIW Linter 已驗證語意型欄位 ID 格式、空 label、重複 ID、秘密上限與 `none` 衝突。
- exporter / parser roundtrip 保留中文 label。

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

Phase 1-G-4 起，地點頁應在角色頁之前完成，因為角色 schedule 會引用可進入地點。

模板規則：

- 原本既有模板必須保留。
- 文件已有但實作尚未提供的模板應補齊。
- 每個 `sub_location` 與 `standalone` 模板必須提供合理 `available_time_slots`；所有模板必須提供 `tags`。
- `tags` 可為中文或英文描述，作為 AI 生成劇情時的地點氣氛、用途、社交屬性、危險程度、約會適合度等參考，不是 canonical ID。
- 套用模板時若即將建立的主地點、獨立地點或任一子地點 ID 已存在，應阻止套用並提示使用者，不自動建立重複地點。
- 子地點實際 `location_id` 必須由 `<parent_location_id>_<location_id_suffix>` 組成。例如商店街中的便利商店應產生 `shopping_street_convenience_store`，避免與獨立地點 `convenience_store` 衝突。
- 若子地點與獨立地點名稱相同，UI 顯示時應提供脈絡或副標，例如 `便利商店(商店街內)` 與 `便利商店(獨立)`。

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
      - 校園日常
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
      - 約會與偶遇
    suggested_sub_locations:
      - cafe
      - convenience_store_sub
      - arcade

  - template_id: station_area_container
    label: 車站周邊
    location_id_suggestion: station_area
    location_type: container
    is_visitable: false
    tags:
      - transit
      - public
      - 通勤
      - 偶遇
    suggested_sub_locations:
      - platform
      - station_square
      - underground_mall

  - template_id: amusement_park_container
    label: 遊樂園
    location_id_suggestion: amusement_park
    location_type: container
    is_visitable: false
    tags:
      - entertainment
      - date_spot
      - 熱鬧
    suggested_sub_locations:
      - ferris_wheel
      - roller_coaster
      - haunted_house
      - souvenir_shop

  - template_id: department_store_container
    label: 百貨公司
    location_id_suggestion: department_store
    location_type: container
    is_visitable: false
    tags:
      - commercial
      - date_spot
      - 室內
    suggested_sub_locations:
      - food_court
      - luxury_floor
      - sky_garden

  - template_id: seaside_container
    label: 海邊
    location_id_suggestion: seaside
    location_type: container
    is_visitable: false
    tags:
      - outdoor
      - romantic
      - 開放感
    suggested_sub_locations:
      - beach
      - beach_house
      - observation_deck

  - template_id: hot_spring_inn_container
    label: 溫泉旅館
    location_id_suggestion: hot_spring_inn
    location_type: container
    is_visitable: false
    tags:
      - travel
      - private
      - 放鬆
    suggested_sub_locations:
      - lobby
      - guest_room
      - open_air_bath
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

  - template_id: rooftop
    label: 屋頂
    location_id_suffix: rooftop
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - afternoon
      - evening
    tags:
      - outdoor
      - private

  - template_id: sports_ground
    label: 操場
    location_id_suffix: sports_ground
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
    tags:
      - outdoor
      - school

  - template_id: convenience_store_sub
    label: 便利商店
    location_id_suffix: convenience_store
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
      - evening
    tags:
      - commercial
      - casual

  - template_id: arcade
    label: 遊戲中心
    location_id_suffix: arcade
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - afternoon
      - evening
    tags:
      - entertainment
      - noisy

  - template_id: platform
    label: 月台
    location_id_suffix: platform
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
      - evening
    tags:
      - transit
      - 偶遇

  - template_id: station_square
    label: 站前廣場
    location_id_suffix: station_square
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
      - evening
    tags:
      - public
      - meeting_spot

  - template_id: underground_mall
    label: 地下街
    location_id_suffix: underground_mall
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
      - evening
    tags:
      - commercial
      - indoor

  - template_id: ferris_wheel
    label: 摩天輪
    location_id_suffix: ferris_wheel
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - afternoon
      - evening
    tags:
      - romantic
      - date_spot

  - template_id: roller_coaster
    label: 雲霄飛車
    location_id_suffix: roller_coaster
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - afternoon
      - evening
    tags:
      - thrill
      - entertainment

  - template_id: haunted_house
    label: 鬼屋
    location_id_suffix: haunted_house
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - afternoon
      - evening
    tags:
      - thrill
      - close_contact

  - template_id: souvenir_shop
    label: 紀念品店
    location_id_suffix: souvenir_shop
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - afternoon
      - evening
    tags:
      - shopping
      - gift

  - template_id: food_court
    label: 美食街
    location_id_suffix: food_court
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
      - evening
    tags:
      - food
      - casual

  - template_id: luxury_floor
    label: 精品樓層
    location_id_suffix: luxury_floor
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - afternoon
      - evening
    tags:
      - luxury
      - social_status

  - template_id: sky_garden
    label: 空中花園
    location_id_suffix: sky_garden
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - afternoon
      - evening
    tags:
      - romantic
      - quiet

  - template_id: beach
    label: 沙灘
    location_id_suffix: beach
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
      - evening
    tags:
      - outdoor
      - romantic

  - template_id: beach_house
    label: 海之家
    location_id_suffix: beach_house
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - afternoon
      - evening
    tags:
      - food
      - summer

  - template_id: observation_deck
    label: 觀景台
    location_id_suffix: observation_deck
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - afternoon
      - evening
    tags:
      - scenic
      - confession_spot

  - template_id: lobby
    label: 大廳
    location_id_suffix: lobby
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
      - evening
    tags:
      - public
      - travel

  - template_id: guest_room
    label: 客房
    location_id_suffix: guest_room
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - afternoon
      - evening
    tags:
      - private
      - intimate

  - template_id: open_air_bath
    label: 露天溫泉
    location_id_suffix: open_air_bath
    location_type: sub_location
    is_visitable: true
    available_time_slots:
      - evening
    tags:
      - relaxing
      - intimate
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
    label: 便利商店(獨立)
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

  - template_id: protagonist_company
    label: 主角公司
    location_id_suggestion: protagonist_company
    location_type: standalone
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
    tags:
      - workplace
      - 壓力
      - 同事互動

  - template_id: park
    label: 公園
    location_id_suggestion: park
    location_type: standalone
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
      - evening
    tags:
      - outdoor
      - peaceful
      - 散步

  - template_id: hospital
    label: 醫院
    location_id_suggestion: hospital
    location_type: standalone
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
      - evening
    tags:
      - serious
      - health
      - 壓力

  - template_id: night_market
    label: 夜市
    location_id_suggestion: night_market
    location_type: standalone
    is_visitable: true
    available_time_slots:
      - evening
    tags:
      - food
      - crowded
      - 熱鬧

  - template_id: gym
    label: 健身房
    location_id_suggestion: gym
    location_type: standalone
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
      - evening
    tags:
      - exercise
      - self_improvement

  - template_id: public_library
    label: 圖書館
    location_id_suggestion: public_library
    location_type: standalone
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
    tags:
      - quiet
      - study

  - template_id: police_station
    label: 警察局
    location_id_suggestion: police_station
    location_type: standalone
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
      - evening
    tags:
      - authority
      - tension

  - template_id: art_museum
    label: 美術館
    location_id_suggestion: art_museum
    location_type: standalone
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
    tags:
      - art
      - quiet
      - date_spot

  - template_id: riverside_walk
    label: 河岸步道
    location_id_suggestion: riverside_walk
    location_type: standalone
    is_visitable: true
    available_time_slots:
      - morning
      - afternoon
      - evening
    tags:
      - outdoor
      - romantic
      - 散步

  - template_id: bar
    label: 酒吧
    location_id_suggestion: bar
    location_type: standalone
    is_visitable: true
    available_time_slots:
      - evening
    tags:
      - nightlife
      - secret_talk
      - 曖昧
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
- Phase 1-G-4 起，地點清單每個項目後方應直接顯示刪除按鈕，不需展開 JSON 才能刪除。
- 刪除 container 時，若仍有子地點引用該 `location_id`，應阻止刪除並提示引用的子地點。
- 刪除任何地點時，若角色 schedule 引用該 `location_id`，應阻止刪除並提示引用來源。
- `location_type` 選項在 UI 中應顯示 `主地點/區域(container)`、`子地點(sub_location)`、`獨立地點(standalone)`，資料仍保存英文 ID。
- `available_time_slots` 選項在 UI 中應顯示 `早上(morning)`、`下午(afternoon)`、`晚上(evening)`，資料仍保存英文 ID。
- 「標籤」欄位應放在「進階設定」中，允許中文或英文描述，並說明其用途是提供 AI 劇情生成參考。

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
- `tags`: 地點標籤，用於生成與事件篩選。Phase 1-G-4 起，此欄位是 AI 劇情參考用進階設定，可輸入中文或英文描述，例如地點氣氛、用途、社交屬性、危險程度、約會適合度；不視為 canonical ID。
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

### 4.6 Phase 1-G-5 UI 操作回饋規格

Phase 1-G-5 是使用者實際操作 Interactive UIW 角色設定頁後的操作體驗調整。此階段不改變 Setup Package canonical schema，重點是補完角色頁的清單可掃讀性、既有角色 inline 編輯、行程管理與中文化，並與 1-G-1 / 1-G-2 / 1-G-4 已建立的 UX 慣例對齊。

#### 範圍

包含：

- 角色清單顯示與刪除引用防呆（A 群組）。
- 既有角色 inline expander 編輯（A4）。
- 行程清單顯示與刪除、行程新增搬入編輯區、行程 enum 中文化、行程地點選單中文化（C / D 群組）。
- 受控素材白名單顯示精簡與進階設定收納（C2 / E 群組）。

排除：

- **新增流程自動產生唯一 canonical ID（B 群組）**：地點、NPC 角色、旗標、狀態與結局目前仍要求使用者輸入英文 ID。Phase 1-G-7 將比照 1-G-3「中文 label → 工具產 canonical ID」原則，把這些新增流程改為自動產生唯一系統 ID。
- **`day_type = specific_date` schema 補日期欄位（D2）**：1-G-5 的處理方式為「在 UI 行程 `day_type` 選項中暫時不顯示 `specific_date`」；schema 升級獨立成後續 phase（待確認編號），追蹤於 `已知問題.md`。
- **既有行程 inline 編輯**：1-G-5 行程修改 = 刪除 + 重新新增。

#### 角色清單顯示

每個角色以 `st.expander` 呈現，expander label 顯示：

```text
{display_name} · {性別中文} · {定位中文}
```

- 性別中文沿用 1-G-2 `GENDER_OPTIONS` label。
- 定位中文沿用 1-G-2 `ROLE_OPTIONS` label。
- 不再於 expander label 顯示 `(character_id)`；系統 ID 於編輯 expander 內進階設定區以唯讀文字顯示。

每個角色右側有獨立刪除按鈕，不需展開 expander 即可刪除，版面對齊 1-G-4 地點頁 `st.columns([5, 1])` pattern。

#### 角色刪除引用防呆

刪除角色前必須掃描下列引用：

- `endings[].target_character_id` 命中該 `character_id` → 阻擋。
- `status_flags[].targets` 包含該 `character_id`（排除 `protagonist`、`global` 與空字串等特殊值）→ 阻擋。匯入舊格式 `status_flags[].target` 時，1-G-8 parser 相容層需先正規化為 `targets`。

阻擋時以 `st.toast(..., icon="🚨")` 顯示，避免打亂角色清單排版。範例：

```text
無法刪除：被結局 sophie_good_end 引用
無法刪除：被狀態旗標 sophie_route_lock 引用
無法刪除：被結局 sophie_good_end、狀態旗標 sophie_route_lock 引用
```

僅在沒有任何引用時才允許刪除。

#### 既有角色 inline 編輯

採 inline expander 編輯範式，每個角色 expander 展開後即為完整編輯表單：

```text
[基本資訊]
  顯示名稱 / 性別 / 性取向(多選) / 定位 / 身分描述 / 初始好感度

[性格與秘密]   (form 外, keyed temp state)
  性格標籤 (allow_multiple)
  角色秘密 (最多 3 個, separate_none)

[角色行程]
  既有行程清單（每筆右側可刪除）
  新增行程表單

[進階設定 (Advanced Settings)]
  💡 受控素材說明
  表情白名單 / 服裝白名單 / 位置白名單
  系統 ID（character_id，唯讀）

[儲存修改]   [取消]
```

性格標籤、角色秘密的暫存 state 採 keyed pattern：

```text
temp_ch_tags_<character_id>
temp_ch_secrets_<character_id>
```

行為：

- 第一次 open expander 時若 key 不存在，使用該角色當前 `personality_tags` / `secrets` 初始化。
- 編輯期間僅修改 keyed temp state，不立即寫回 canonical 資料。
- 「儲存修改」將 keyed temp state 與 form 內欄位合併寫回該角色。
- 「取消」清空 keyed temp state；下次開啟 expander 重新依當前值初始化。
- 多角色同時編輯時不互相污染。

新增角色仍維持頁面下方獨立「新增角色」表單，沿用 1-G-3 既有 `temp_ch_tags`、`temp_ch_secrets`（無後綴 key）。

`character_id` 於編輯 expander 內以唯讀文字顯示於進階設定區，1-G-5 不開放修改。

#### 行程清單顯示與刪除

每個角色 expander 內「角色行程」區塊列出該角色 `schedule`，每筆顯示：

```text
{day_type 中文} {time_slot 中文} @ {地點 name} [{priority 中文}] order={schedule_order}
```

範例：

```text
平日 早上 @ 蘇菲家 [一般] order=20
週末 下午 @ 中央公園 [路線] order=10
```

- 地點 name 由 `location_id` 反查 `st.session_state["locations"]` 對應 `name`。
- 若該 `location_id` 已被刪除，顯示原 ID 並加註「(地點已刪除)」。
- 每筆右側「刪除」按鈕，按下後從該角色 `schedule` 移除該筆。
- 1-G-5 不提供行程 inline 編輯；修改 = 刪除 + 重新新增。

#### 行程新增搬入編輯 expander

「新增行程」表單從頁面下方共用區搬入每個角色編輯 expander 內「角色行程」區塊下方。

- 不再透過 `selectbox` 選擇要綁定的角色，因為 expander 已限定該角色。
- 表單欄位：行程 ID / 日期類型 / 時間段 / 地點 / 優先權 / 排序值 / 條件。
- 顯示文字依下節中文化映射。
- 頁面下方既有共用「新增角色行程」表單於 1-G-5 移除。

#### 行程 enum 中文化映射

行程 UI 採「中文(英文)」混顯，canonical 仍英文 enum：

```text
day_type:
  weekday        -> 平日(weekday)
  weekend        -> 週末(weekend)
  holiday        -> 假日(holiday)
  any            -> 任意(any)
  specific_date  -> 1-G-5 暫不顯示於 UI 選項

time_slot:
  morning        -> 早上(morning)
  afternoon      -> 下午(afternoon)
  evening        -> 晚上(evening)

priority:
  critical       -> 必定(critical)
  route          -> 路線(route)
  normal         -> 一般(normal)
  ambient        -> 環境(ambient)
```

輸出資料維持原本英文 enum：

```yaml
schedule:
  - schedule_id: sophie_weekday_morning
    day_type: weekday
    time_slot: morning
    location_id: school_class_2a
    priority: normal
    schedule_order: 20
```

`time_slot` 中文化已在 1-G-4 地點頁建立；行程頁與地點頁必須使用相同映射，避免不一致。

#### 行程地點選單中文化

行程「地點」`selectbox` 顯示地點 `name`，底層 value 仍是 `location_id`：

- `selectbox` 使用 `format_func=lambda lid: location_name_map.get(lid, lid)`。
- 對齊 1-G-3 中文 label / 英文 canonical 原則。

#### 受控素材白名單顯示與進階設定收納

表情、服裝、位置白名單收進編輯 expander 內「進階設定 (Advanced Settings)」展開區。

- `multiselect` 顯示文字為純中文 label，移除目前 `"label (id)"` 的 `(id)` 後綴。
- 底層仍保存 `[{"id": ..., "label": ...}, ...]`，與 1-G-3 一致。
- 預設選擇邏輯：新增角色時可預填前 N 個常用 preset；既有角色編輯時依該角色當前值預填。

進階設定區頂部加入常駐說明：

```text
💡 受控素材清單：表情、服裝、位置白名單用於限制 AI 生成劇情時可用的角色素材，
避免 AI 任意創造。預設值可依角色定位調整。
```

#### Streamlit 實作限制

下列限制是 1-G-5 實作層必須遵守的硬性條件，避開 Streamlit 的 widget key 與 expander 限制，並保證 keyed session state 後綴穩定：

##### 禁止 nested `st.expander`

Streamlit 不允許 `st.expander` 內再放 `st.expander`，會 raise `StreamlitAPIException`。「進階設定 (Advanced Settings)」展開區改用 `st.checkbox("顯示進階設定", key=f"show_adv_{character_id}")` 或 `st.toggle(...)` 切換，`True` 時於 `st.container` 內顯示白名單區塊。切換 state 必須帶 per-character key。

##### 編輯 widget 全採 per-character keyed pattern

編輯 expander 內所有 widget 必須使用顯式 key，後綴為該角色 `character_id`：

```text
基本資訊：
  edit_display_name_<character_id>
  edit_gender_<character_id>
  edit_orientation_<character_id>
  edit_role_<character_id>
  edit_identity_<character_id>
  edit_initial_favor_<character_id>

進階設定（白名單）：
  show_adv_<character_id>
  edit_emotions_<character_id>
  edit_costumes_<character_id>
  edit_positions_<character_id>

行程新增表單：
  add_sch_id_<character_id>
  add_sch_day_<character_id>
  add_sch_slot_<character_id>
  add_sch_loc_<character_id>
  add_sch_prio_<character_id>
  add_sch_order_<character_id>
  add_sch_cond_<character_id>

性格 / 秘密 keyed temp state：
  temp_ch_tags_<character_id>
  temp_ch_secrets_<character_id>

按鈕：
  del_ch_<character_id>
  save_ch_<character_id>
  cancel_ch_<character_id>
  del_sch_<character_id>_<schedule_index>
```

頁面下方共用「新增角色」表單仍使用無後綴 key。

##### `character_id` 唯一性與生命週期

per-character keyed pattern 仰賴 `character_id` 在 expander 生命週期內唯一且不變。

新增角色時必須擋下：

- `character_id` 為空字串。
- `character_id` 與 `st.session_state["characters"]` 中既有 `character_id` 重複。
- `character_id` 不符 canonical ID 格式（小寫英數底線、不可中文、不可空格）。

失敗時顯示 `st.error(...)`，不寫入 `st.session_state["characters"]`。此即時擋與 UIW Linter 的 character_id 驗證重疊；UI 層只是把 fail-fast 提前。

編輯 expander 不開放修改 `character_id`：1-G-5 範圍內 `character_id` 一旦建立即不可變，UI 上以唯讀文字顯示於進階設定區。Phase 1-G-7 僅處理新增角色時自動產生 `character_id`；既有 NPC `character_id` 修改屬 ID rename / reference migration，不納入 1-G-7。

##### 刪除角色時清空相關 session state

刪除角色（通過 endings / status_flags 引用防呆檢查後）必須清掉該角色所有 keyed session state：

```python
def _purge_character_state(character_id: str) -> None:
    suffix = f"_{character_id}"
    schedule_prefix = f"del_sch_{character_id}_"
    keys_to_drop = [
        k for k in list(st.session_state.keys())
        if k.endswith(suffix) or k.startswith(schedule_prefix)
    ]
    for k in keys_to_drop:
        del st.session_state[k]
```

刪除流程：

1. 引用防呆檢查（endings / status_flags）。
2. 通過 → `st.session_state["characters"].pop(i)`。
3. `_purge_character_state(character_id)`。
4. `st.rerun()`。

防呆未通過 → 顯示 toast，不執行 2–4。

#### 不變項

- canonical schema 不動：`Character`、`ScheduleEntry`、`AssetOption`、`SemanticChoice` 維持現狀。
- exporter / parser 不需修改。
- UIW Linter 規則不需新增（A3 引用防呆是 UI 層即時阻擋，不是 export 時驗證；新增角色 character_id 即時擋是 UI 層 fail-fast，linter 仍保留 export 時驗證作為最終防線）。
- 1-G-3 `id + label`、1-G-4 地點頁排版、1-G-2 中文化選項全部保留。
- 主角頁、地點頁、旗標/結局頁不在此 phase 範圍。

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
    targets:
      - protagonist
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
- `targets`: 狀態可作用對象清單，例如 `protagonist` 或特定 `character_id`。1-G-8 起由單一 `target` 升級為複選清單；runtime 實際套用時仍可用 `status.<target_id>.<status_id>` 指定某一對象。
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

### 5.4 Phase 1-G-6 UI 操作回饋規格

Phase 1-G-6 是使用者實際操作 Interactive UIW 旗標/狀態/結局合併頁後的操作體驗調整。此階段不改變 Setup Package canonical schema，重點是拆分分頁、補完結局頁的 inline 編輯與中文化，並驗收「不設旗標 / 狀態時仍可匯出可用 Setup Package MD」這個目標。

#### 範圍

包含：

- 拆分原「旗標 / 狀態 / 結局」分頁為「旗標與狀態(Flags & Status)」與「結局(Endings)」兩個獨立分頁。
- 結局頁清單顯示與 inline expander 編輯。
- 結局 `priority` 中文化與五級語意 caption。
- `target_character_id` selectbox 中文顯示。
- `required_flags` / `forbidden_flags` F-γ multiselect 快速加入互動。
- 最小可用 Setup Package（flags=[] / status_flags=[]）匯出驗收。
- 附帶修正 1-G-5 character_id 即時擋為跨類型唯一。

排除：

- **新增流程自動產生唯一 canonical ID（B 群組）**：原排 1-G-6 的 B 群組擴大為 **1-G-7**，涵蓋地點、NPC 角色、旗標、狀態與結局新增流程。
- **旗標 / 狀態頁 inline 編輯**：1-G-6 內僅分頁搬移，inline 編輯與中文化排 **1-G-8**。
- **schedule `specific_date` schema 升級（D2）**：重排為 **1-G-9**。
- **`required_stats` 改 multiselect**：1-G-6 內維持 free-form，不動。

#### 分頁順序

`PAGE_LABELS` 更新為：

```python
PAGE_LABELS = [
    "世界觀與曆法(World)",
    "主角設定(Protagonist)",
    "地點與地圖(Locations)",
    "角色設定(Characters)",
    "旗標與狀態(Flags & Status)",
    "結局(Endings)",
    "預覽與匯出(Review & Export)",
]
```

`_tab_flags()` 拆成 `_tab_flags()` 與 `_tab_endings()`。旗標與狀態旗標保留在前者（1-G-6 內 UX 不動），結局搬到後者並進行 inline 編輯改造。

#### 結局清單顯示

每個結局以 `st.expander` 呈現：

```text
{title or ending_id} · {priority 中文} · {target 顯示}
```

- title 為空時 fallback 顯示 `ending_id`。
- priority 中文（精簡，不含括弧英文）：必定觸發 / 主線 / 路線 / 一般 / 背景。
- target 顯示：
  - `target_character_id is None` → `（無）`
  - `"global"` → `全局結局`
  - 命中既有角色 → 該角色 `display_name`（中文）
  - dangling reference（僅限歷史 / 外部匯入資料；正常 UI 刪除角色時會被 ending 引用防呆阻擋）→ 原 ID 並加註「(角色已刪除)」

每列右側直接顯示「刪除」按鈕，版面對齊 1-G-5 角色頁 / 1-G-4 地點頁 `st.columns([5, 1])` pattern。

#### 結局刪除

ending 沒被任何 setup package 欄位 reference，刪除不需引用防呆 toast：

1. `st.session_state["endings"].pop(i)`。
2. `_purge_ending_state(ending_id)`。
3. `st.rerun()`。

#### 既有結局 inline 編輯

採與 1-G-5 角色頁相同的 inline expander 編輯範式：

```text
[基本資訊]   (form 內)
  結局 ID (ending_id, 唯讀)
  結局標題 (title)
  結局類型 (ending_type)
  關聯角色 (target_character_id, 中文 selectbox)
  結局描述 (description)
  優先權 (priority, 中文化 selectbox + caption)
  路線標籤 (route_tags, free-form)

[條件]
  ── 必須條件 (required_flags) ──
  [form 外] multiselect: 從現有旗標快速選
  [form 外] [加入到必須條件] button → 展開 placeholder append 到下方
  [form 內] required_flags free-form text_area
            預填 keyed temp_req_flags_<ending_id>

  ── 禁止條件 (forbidden_flags) ──
  [form 外] multiselect + [加入到禁止條件] button
  [form 內] forbidden_flags free-form text_area
            預填 keyed temp_forb_flags_<ending_id>

  ── 必須數值 (required_stats) ──
  [form 內] required_stats free-form text_input
            (1-G-6 不動，保持 free-form)

[儲存修改]   [取消]
```

「加入到必須條件 / 加入到禁止條件」按鈕為 `st.button()`，必須位於 form 外，與 multiselect 同層；儲存 / 取消按鈕為 `st.form_submit_button()`，位於 form 內。

##### F-γ multiselect 互動規則

「加入」button 觸發後：

1. 讀取 multiselect 選中的 `flag_id` 清單。
2. 對每個 flag 產生 placeholder：
   - `boolean` flag → `flag.<id> == true` / `flag.<id> == false`
   - `integer` flag → `flag.<id> == <initial_value>`（不加引號）
   - `string` / `enum` flag → `flag.<id> == "<initial_value>"`（使用雙引號；值內若已有 `"` 或 `\`，需 escape）
3. append 到 `temp_req_flags_<ending_id>` / `temp_forb_flags_<ending_id>`，並更新 form 內 text_area 顯示。
4. 清空 multiselect 選擇。

multiselect 與 free-form text_area 為「單向 append」關係：取消勾選**不會**自動移除已加入的字串。修改條件值（true → false / 數值變動）必須直接編輯 text_area。

flags=[] 時 multiselect 空，下方 caption 顯示「尚未設定旗標。可在『旗標與狀態』分頁建立後再回此處快速加入」。此狀況下使用者仍可：

- 留 `required_flags` / `forbidden_flags` 為空 → 匯出 Setup Package（最小可用目標）。
- `required_stats` 仍可在下方 free-form text_input 輸入 `stat.*` 條件；`required_flags` / `forbidden_flags` 只放 `flag.*` 條件。

#### Priority 中文化映射

selectbox 採「中文(英文)」混顯：

```text
priority:
  critical -> 必定觸發(critical)
  main     -> 主線(main)
  route    -> 路線(route)
  normal   -> 一般(normal)
  ambient  -> 背景(ambient)
```

selectbox 下方常駐 caption（依正式規格 v1.2 §5 排序）：

```text
優先權由高到低：
  critical: 強制觸發，覆蓋其他所有結局
  main:     主線結局
  route:    角色路線結局
  normal:   一般結局
  ambient:  背景/支線結局，最低優先
```

canonical 仍保存英文 enum：

```yaml
endings:
  - ending_id: sophie_good_end
    priority: route
```

#### `target_character_id` 中文 selectbox

```python
options = [None, "global"] + [ch["character_id"] for ch in st.session_state["characters"]]
# 若目前 ending.target_character_id 是 dangling reference，額外 append 該原 ID，
# 只為了讓歷史 / 外部匯入資料可顯示並保留；正常 UI 刪除角色時應被引用防呆阻擋。

format_func:
  None         -> 「（無 / 不指定）」
  "global"     -> 「全局結局 (global)」
  <character_id> -> 該角色 display_name（中文）
                   ※ dangling reference（歷史 / 外部匯入資料）時顯示原 ID 並加註「(角色已刪除)」
```

底層 value 仍存 `character_id` / `"global"` / `None`。

#### `ending_id` 唯一性與生命週期

新增結局時必須擋下：

- `ending_id` 為空字串。
- `ending_id` 與既有 **world_id / character_id / location_id / flag_id / status_id / ending_id** 任一重複（**跨類型唯一**；1-G-6 UI 即時擋納入 `status_id`，linter 的 `status_id` 補洞另排後續 phase）。
- `ending_id` 不符 canonical ID 格式（小寫英數底線）。

失敗時顯示 `st.error(...)`，不寫入 `st.session_state["endings"]`。

實作 helper：

```python
def _collect_existing_ids() -> set[str]:
    s: set[str] = set()
    world = st.session_state.get("world") or {}
    if world.get("world_id"):
        s.add(world["world_id"])
    s.update(c["character_id"] for c in st.session_state.get("characters", []) if c.get("character_id"))
    s.update(l["location_id"] for l in st.session_state.get("locations", []) if l.get("location_id"))
    s.update(f["flag_id"] for f in st.session_state.get("flags", []) if f.get("flag_id"))
    s.update(sf["status_id"] for sf in st.session_state.get("status_flags", []) if sf.get("status_id"))
    s.update(e["ending_id"] for e in st.session_state.get("endings", []) if e.get("ending_id"))
    return s
```

編輯 expander 內 `ending_id` 唯讀。

#### 附帶修正：1-G-5 character_id 即時擋擴為跨類型唯一

1-G-5 規格「新增角色 character_id 與既有 character_id 重複時擋下」**未涵蓋跨類型重複**（例 character_id `"sophie"` 與 location_id `"sophie"` 衝突）。雖然 UIW Linter export 時會擋為 `duplicate_id` error 作為最終防線，但 UI 層即時擋與 linter 行為不一致。

1-G-6 順帶修正：1-G-5 角色頁的「新增角色」流程改用 `_collect_existing_ids` helper，擋下 character_id 與**任何類型**既有 ID 重複，包含既有 `status_id`。其他 1-G-5 規格不變。

#### Streamlit 實作限制

對齊 1-G-5 已建立的 Streamlit pattern：

- **禁止 nested `st.expander`**：結局編輯 expander 內結構平鋪，無 nested expander。
- **per-ending keyed pattern**：所有編輯 widget 必須使用顯式 key，後綴為該結局 `ending_id`。
- **多結局並行編輯**：因 widget key 帶 `ending_id` 後綴，state 不互相污染。
- **刪除清空 state**：`_purge_ending_state(ending_id)` 清掉所有 `*_<ending_id>` keyed session state。

完整 keyed widget 清單：

```text
基本資訊：
  edit_title_<ending_id>
  edit_ending_type_<ending_id>
  edit_target_<ending_id>
  edit_description_<ending_id>
  edit_priority_<ending_id>
  edit_route_tags_<ending_id>

條件：
  ms_req_flags_<ending_id>
  add_req_flags_<ending_id>
  edit_req_flags_<ending_id>
  ms_forb_flags_<ending_id>
  add_forb_flags_<ending_id>
  edit_forb_flags_<ending_id>
  edit_req_stats_<ending_id>

按鈕：
  del_end_<ending_id>
  save_end_<ending_id>
  cancel_end_<ending_id>

Form-外暫存 state：
  temp_req_flags_<ending_id>
  temp_forb_flags_<ending_id>
```

#### 「儲存修改」與「取消」行為

對齊 1-G-5：

- 編輯期間僅修改 keyed temp state 與 form 內 widget value，不立即寫回 canonical。
- 「儲存修改」→ keyed temp state 與 form 內欄位合併寫回該 ending：
  - `required_flags` 從 form 內 free-form text_area 解析（逗號分隔字串 → list[str]）為最終結果。`temp_req_flags_<ending_id>` 僅用於 multiselect 「加入」期間的暫存，不直接覆寫 ending。
  - `forbidden_flags` 同理。
  - `required_stats` 從 form 內 free-form text_input 解析。
- 「取消」→ 清空 `temp_req_flags_<ending_id>` / `temp_forb_flags_<ending_id>`；下次開啟 expander 重新依當前 ending 值初始化。

#### 不變項

- canonical schema 完全不動：`Ending`、`FlagDef`、`StatusFlag`、`SetupPackage` 模型維持現狀。
- exporter / parser 不需修改。
- UIW Linter 規則不需新增（跨類型 ID 唯一檢查已存在於 `_check_ids`）。
- 1-G-3 / 1-G-4 / 1-G-5 既有行為全部保留。
- 主角頁、地點頁、角色頁、世界頁 1-G-6 不動。
- 旗標 / 狀態頁 1-G-6 內僅分頁搬移，UX 內容原樣。

#### 最小可用 Setup Package 驗收

定義「最小可用」Setup Package：

```text
最小可用條件：
  - World 必填欄位齊全
  - Protagonist 必填欄位齊全
  - locations 至少 1 筆（其中至少 1 筆 is_visitable=True）
  - characters 至少 1 筆
  - endings 至少 1 筆
  - flags = []
  - status_flags = []

預期結果：
  - UIW Linter 不報 error（warnings 可接受）
  - SetupPackageExporter.to_markdown() 成功產生 MD
  - MD 可被 parser 還原為 SetupPackage
  - 該 ending 的 required_flags / forbidden_flags / required_stats 全為空
```

對應測試補在 `tests/test_exporter.py` 或 `tests/test_uiw_linter.py`，並提供手動驗收流程（見 `測試指南.md`）。

---

### 5.5 Phase 1-G-7 UI 操作回饋規格

Phase 1-G-7 是使用者確認 ID 輸入負擔後的操作體驗調整。除主角固定 `protagonist` 以外，地點、NPC 角色、旗標、狀態與結局的英文 ID 都是系統引用鍵，不應要求一般使用者手動輸入。UI 應依中文名稱、標題或 label 自動產生唯一 canonical ID。

#### 範圍

包含：

- 手動新增地點：`location_id`
- 新增 NPC 角色：`character_id`
- 新增旗標：`flag_id`
- 新增狀態旗標：`status_id`
- 新增結局：`ending_id`

排除：

- `world_id`：仍由 World 頁處理。
- `protagonist_id`：固定為 `protagonist`。
- 既有資料 ID rename 與引用搬移。
- schema / exporter / parser 資料契約修改。

#### UI 原則

新增表單以使用者可理解欄位為主，英文 ID 欄位不再是必填主欄位：

```text
地點：地點名稱
NPC：角色姓名 / 顯示名
旗標：用途描述
狀態：狀態名稱
結局：結局標題
```

UI 可在進階設定或 caption 顯示自動產生的系統 ID：

```text
系統 ID：ch_lin_xiao_yu
```

若提供手動調整 ID 的入口，必須放在進階設定中，並套用 canonical ID 格式檢查與全域唯一檢查。驗證失敗時不新增資料、不清空使用者已輸入內容。

#### ID 產生與唯一性

ID 產生規則：

1. 取中文名稱 / 標題 / label 作為來源；旗標因 canonical schema 沒有 `label` 欄位，使用 `description` 作為來源。
2. 中文轉拼音；英文轉小寫；空白與標點（包含中文標點如 `、`、`，`、`。`、`：`）轉 `_`。
3. 移除不符合 canonical ID 的字元。
4. 合併重複 `_`，去掉頭尾 `_`。
5. 將 slug 依 `_` 切成 token，最多保留前 8 個 token，避免 description 產生過長 ID；截斷後再次合併重複 `_` 並去掉頭尾 `_`。
6. 若結果空白，使用不含 prefix 的中性 fallback `unnamed`。
7. 加上類型 prefix。
8. 若與既有全域 ID 衝突，依序追加 `_2`、`_3`、`_4`，直到唯一；suffix 必須**順序遞增取最小未占用**（既有 `_2`、`_4` 時新增者為 `_3`）。

prefix 建議：

| 類型 | prefix | 範例 |
| :--- | :--- | :--- |
| 地點 | `loc_` | `loc_ka_fei_ting` |
| NPC 角色 | `ch_` | `ch_lin_xiao_yu` |
| 旗標 | `flag_` | `flag_shi_fou_shi_ye` |
| 狀態旗標 | `status_` | `status_guo_lao` |
| 結局 | `end_` | `end_su_fei_hao_jie_ju` |

產出 ID 必須符合：

```text
^[a-z][a-z0-9_]*$
```

唯一性檢查必須使用同一個全域 ID 集合：

```text
world.world_id
固定 protagonist_id（即字面 "protagonist"）
characters[].character_id
locations[].location_id
flags[].flag_id
status_flags[].status_id
endings[].ending_id
```

`protagonist` 為固定 ID 不在 `characters[]` 內，但仍須納入全域集合，以擋進階手動 ID 入口的衝突。目前 UI 層 `_collect_existing_ids` 已含 `status_id`，**尚未含 `protagonist`，1-G-7 須補**。

#### 跨類唯一性的觸發場景

自動 ID 路徑下，prefix 隔離使各類型永不可能跨類衝突。跨類衝突僅在以下情境發生：

1. **進階手動 ID 入口**：使用者繞過自動產生路徑自行輸入完整 ID。
2. **地點模板套用**：1-G-4 既有「沿用模板建議 ID」流程，若模板帶來的 ID 與其他類型既有 ID 撞。
3. **既有匯入 / 手寫 Setup Package**：外部資料的 ID 不一定遵循 prefix 慣例。

#### 模板套用衝突處理

地點模板套用時，模板建議 ID 必須經過 `_make_unique_id` 全域唯一性檢查。本期挑邊為「**自動 suffix 避讓**」（模板 ID `loc_home`、已存在則建立 `loc_home_2`），不採「阻止新增 + toast」，因為地點模板天生需要重複套用。

#### 預覽 ID 顯示時機

採「**submit 後在新增結果以 caption 顯示自動產生的系統 ID**」，不在 form 內 widget callback 即時預覽，以免 token 截斷與衝突 suffix 在使用者輸入過程中頻繁變動。自動 ID 預覽不允許做成 form 內必填或可編輯欄位。

#### 實作建議

實作時應新增 `_make_unique_id(label, prefix, fallback, existing_ids)` 這類包裝 helper，內部呼叫既有 `_generate_system_id(label)` 取得 base slug，再負責截斷、prefix 與唯一性 suffix。不得修改 `_generate_system_id` 的簽章與既有行為，因為 1-G-3 semantic choice 仍依賴它產生不帶類型 prefix 的系統 ID。

#### 不變項

- canonical data 仍保存英文 ID。
- UI 顯示中文名稱、標題與 label；底層引用仍使用英文 ID。
- 新增後，地點 parent、角色 schedule、結局 target、status targets 等引用欄位底層 value 不變。
- 不處理既有 ID rename，因此不需要搬移 reference 或 session state key。

---

### 5.6 Phase 1-G-8 旗標 / 狀態頁 inline 編輯規格

Phase 1-G-8 補完「旗標與狀態(Flags & Status)」分頁。此頁應比照地點、角色與結局頁，提供目前清單、每筆 inline expander 編輯、刪除防呆與成功 / 取消行為。此階段同時將 status 作用對象從單一欄位升級為可複選。

#### 範圍

包含：

- 旗標清單顯示、inline 編輯、刪除引用防呆。
- 狀態清單顯示、inline 編輯、刪除引用防呆。
- `flag_id` / `status_id` 唯讀，不做 rename。
- 狀態作用對象改為主角 + 角色複選。
- 狀態持續類型使用中文(英文) 選項，並顯示說明。
- `effect` 用 YAML 編輯，保留 list of dict 結構。
- **同步更新範圍**：
  - 1-G-5 角色刪除防呆對 `status_flags[].target` 的引用比對改用「`targets` 包含」並先經 normalize。
  - 1-G-6 結局頁與其他可能掃描 `target` 的位置同步改 `targets`。
  - `tests/fixtures/setup_minimal.yaml`、`tests/test_setup_schema.py`、`tests/test_uiw_linter.py` 內既有 `target=` 構造遷移為 `targets=[...]`。
  - 新增 `tests/fixtures/setup_legacy_status_target.yaml`（保留舊 `target:` 欄位）作為 parser 相容層測試 fixture。

排除：

- 不做完整 Status Manager runtime。
- 不解析 `effect` 內容的 domain 語意。
- 不掃描 Event Blueprint / Scene Draft 外部引用。
- 不把結局頁 `required_stats` 改成 status multiselect。
- 不處理 NPC `character_id == "protagonist"` 歷史衝突資料；UI 以 dedupe 規避，linter 修補留後續 phase。

#### `StatusFlag.targets`

1-G-8 起，Status Flag canonical data 使用：

```yaml
status_flags:
  - status_id: overworked
    label: 過勞
    targets:
      - protagonist
      - sophie
    effect:
      - block_time_slot: evening
    duration:
      type: time_slots
      value: 1
    clear_rule:
      - on_time_advance
      - on_rest
    description: 太累，晚上無法外出。
```

規則：

- `targets` 必須是非空 list；schema 層以 `Field(min_length=1)` 直接拒絕空 list。
- 可選值為固定 `protagonist` 與 `characters[].character_id`。
- UI 顯示為「主角(protagonist)」與「角色顯示名(character_id)」；`_status_targets_options` 須 dedupe，避免 NPC `character_id == "protagonist"` 出現重複選項。
- 舊資料含 `target: protagonist` 時，由 `StatusFlag.model_validator(mode="before")` 在 schema 層 normalize 為 `targets: ["protagonist"]`（不在 parser 手動處理，避免相容邏輯散落）。exporter 一律輸出 `targets`。
- 若新格式與舊格式同時存在（同筆同時有 `targets` 與 `target`），新格式優先，`target` 直接捨棄。
- `targets` 表示此 status 可作用的對象清單，不代表 runtime 一定同時套用到所有對象。

挑邊摘要：

- **空 targets**：schema 層 `Field(min_length=1)` 拒絕（最後防線）；UI 層 submit 前先擋一次給友善訊息；UIW Linter 補一條 `empty_status_targets` 錯誤訊息以對齊使用者語境。
- **normalize 落點**：schema `model_validator(mode="before")`，所有進入點通吃。

#### 旗標 inline 編輯

清單顯示：

```text
{description or flag_id} · {type} · 初始值 {initial_value}
```

編輯欄位：

- `flag_id`：唯讀。
- `type`：`boolean` / `integer` / `string` / `enum`。
- `initial_value`：
  - `boolean` 用 `true` / `false` 選項。
  - `integer` 用數字輸入。
  - `string` 用文字輸入。
  - `enum` 本期仍用文字輸入，不新增 enum choices schema。
- `description`：文字輸入。

刪除前需檢查：

- `endings[].required_flags`
- `endings[].forbidden_flags`
- `characters[].schedule[].condition`

若命中 `flag.<flag_id>`，阻止刪除並列出引用位置。

#### 狀態 inline 編輯

清單顯示：

```text
{label or status_id} · {targets 顯示} · {duration.type 中文} · {clear_rule 摘要}
```

編輯欄位：

- `status_id`：唯讀。
- `label`：顯示名稱。
- `targets`：主角 + 角色複選，至少一個。
- `description`：說明。
- `effect`：YAML text_area，必須能 parse 成非空 `list[dict]`。
- `duration.type`：中文(英文) selectbox。
- `duration.value`：非永久狀態使用；永久狀態存 `None`。
- `clear_rule`：解除條件 multiselect。
- `permanent_reason`：`duration.type == permanent` 時必填。

`effect` 範例：

```yaml
- block_time_slot: evening
- stat_multiplier:
    stat: CHA
    value: 0.8
```

#### 持續類型 UI 說明

`duration.type` selectbox 顯示：

| canonical | UI 顯示 | 說明 |
| :--- | :--- | :--- |
| `time_slots` | 時段數(time_slots) | 經過指定數量的早上 / 下午 / 晚上後解除。 |
| `days` | 天數(days) | 經過指定天數後解除。 |
| `until_event` | 直到事件(until_event) | 直到特定劇情事件處理後解除；本期不解析事件 ID。 |
| `until_cleared` | 直到解除(until_cleared) | 持續到某個 clear_rule 被觸發。 |
| `permanent` | 永久(permanent) | 長期狀態；必須填永久原因。 |

UI 應在 selectbox 下方顯示目前選項的說明 caption，避免使用者只看到英文 enum。

#### `duration.value` 規則

| `duration.type` | UI 顯示 value 欄位 | canonical value |
| :--- | :--- | :--- |
| `time_slots` | 顯示 number_input，必填正整數 | `int >= 1` |
| `days` | 顯示 number_input，必填正整數 | `int >= 1` |
| `until_event` | 不顯示 | `None`（舊資料帶數字也 normalize 為 None） |
| `until_cleared` | 不顯示 | `None` |
| `permanent` | 不顯示 | `None`（並必填 `permanent_reason`） |

UIW Linter 對 `until_event` / `until_cleared` 但 value 非 None 報 `unexpected_duration_value` warning（不擋匯出，提醒使用者清整資料）。

#### 狀態刪除防呆

刪除 status 前需掃描：

- `endings[].required_stats`
- `characters[].schedule[].condition`
- 1-G-5 角色刪除路徑：比對 `status_flags[].targets` 是否包含該 `character_id`（normalize 後比對）。

引用比對採 **word-boundary regex**，不可使用 substring `in`：

- qualified：`\bstatus\.<target_id>\.<status_id>\b`
- bare：`\bstatus\.<status_id>\b`（須排除已被 qualified 命中的範圍）

flag 引用比對同樣採 `\bflag\.<flag_id>\b`，避免 `flag.over_x` 撞 `flag.over`。

若命中其中一種，阻止刪除並列引用位置。沒有引用才刪除，並清空該 `status_id` 對應的 keyed session state。

#### UIW Linter 新增 issue types

| issue type | severity | 描述 |
| :--- | :--- | :--- |
| `unknown_status_target` | error | `targets` 引用了非 `protagonist` 也非既有 NPC `character_id` 的對象。 |
| `empty_status_targets` | error | `targets` 為空（與 schema `Field(min_length=1)` 重複，提供使用者友善訊息與 path）。 |
| `unexpected_duration_value` | warning | `duration.type ∈ {until_event, until_cleared}` 但 `value` 非 None。 |

#### 儲存與取消

- 編輯期間不立即寫回 canonical。
- 「儲存修改」驗證成功才寫回。
- 「取消」清空該筆 keyed temp state，下一次開啟時重新從 canonical 初始化。
- 解析 YAML 或欄位驗證失敗時，不寫回、不清空使用者輸入。

#### 不變項

- 新增旗標 / 狀態仍沿用 1-G-7 自動 ID。
- `flag_id` / `status_id` 仍為英文 canonical ID。
- status runtime 套用語法仍可用 `status.<target_id>.<status_id>`。
- `status_id` 的格式與跨類型唯一檢查已在 1-G-7 收尾先行補入；1-G-8 只需納入回歸驗收。

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
