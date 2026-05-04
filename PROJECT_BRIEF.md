# SandboxDatingSimDev 專案簡報

本文件供新 session 快速了解專案全貌，取代逐份閱讀全部規格文件。需要深入某區段時，按行號索引讀取對應文件。

最後更新：2026-05-04

---

## 專案概述

沙盒戀愛模擬器的開發工具鏈。Phase 1 產出 Setup Package（遊戲初始設定資料包），供 Phase 2 的 AI 事件生成使用。

## 技術棧

- Python 3.12+、套件管理 `uv`
- 資料模型 Pydantic、YAML 讀寫 PyYAML
- CLI Typer、UI Streamlit
- 測試 pytest、虛擬環境 `.venv\Scripts\python.exe`

## 目錄結構

```
src/sandbox_dating_sim/
├── core/          constants.py, exceptions.py, ids.py（ID 驗證、slugify、自動 ID）
├── schema/        setup.py（SetupPackage Pydantic models）, validation.py
├── uiw/           linter.py（UIW Linter）, defaults.py（UI 預設選項）, helpers.py（純函式）
├── pipeline/      setup_exporter.py, setup_parser.py, markdown.py
├── ui/            streamlit_uiw.py（Interactive UIW Prototype）
└── cli.py

tests/
├── fixtures/      setup_minimal.yaml, setup_legacy_status_target.yaml, ...
├── test_setup_schema.py, test_uiw_linter.py, test_setup_exporter.py
├── test_setup_parser.py, test_streamlit_uiw.py, test_cli.py
├── test_ids.py, test_uiw_defaults.py
├── test_uiw_1g7.py, test_uiw_1g8.py, test_uiw_1g9.py
```

## 核心設計原則

1. **Schema vs Linter 分工**：Schema（Pydantic）管資料形狀與型別；Linter 管語意、引用、跨欄位邏輯。測試也分層。
2. **ID 規則**：`^[a-z][a-z0-9_]*$`，UI 顯示中文但 canonical data 一律英文 ID。
3. **文件格式**：Markdown 外殼 + 單一 YAML code block。`model_dump(mode="json", exclude_none=True)`。
4. **1-G-7 自動 ID**：`_slugify_label`（中文轉拼音）→ `_make_unique_id`（prefix + suffix 避重），保留手動輸入。
5. **Phase 1 不呼叫外部 AI API**。

## Schema 主要模型（setup.py）

SetupPackage 包含：World、Protagonist、Location[]、Character[]（含 ScheduleEntry[]）、FlagDef[]、StatusFlag[]、Ending[]、asset_vocabularies、alias_tables、validation_report。

關鍵 Literal 型別：DayType、TimeSlot、SchedulePriority、FlagType、DurationType、ClearRule、Gender、Orientation、EventPriority。

## Phase 進度

| Phase | 狀態 | 概要 |
|:---|:---|:---|
| 0 | ✅ 完成 | 專案骨架、ID 工具 |
| 1-A | ✅ 完成 | Canonical Setup Schema |
| 1-B | ✅ 完成 | UIW Linter |
| 1-C | ✅ 完成 | Setup Package MD Exporter |
| 1-D | ✅ 完成 | Setup Package Parser + Roundtrip |
| 1-E | ✅ 完成 | CLI export-setup |
| 1-F | ✅ 完成 | Interactive UIW Prototype（Streamlit 表單填寫） |
| 1-G-1 | ✅ 完成 | 導覽順序、主角預設、債務等級 |
| 1-G-2 | ✅ 完成 | 主角 ID 隱藏、性別/性取向中文化 |
| 1-G-3 | ✅ 完成 | 語意型欄位 id+label、秘密複選 |
| 1-G-4 | ✅ 完成 | 地點模板擴充、刪除引用防呆 |
| 1-G-5 | ✅ 完成 | 角色清單、inline 編輯、行程管理 |
| 1-G-6 | ✅ 完成 | 結局頁 inline 編輯、F-γ multiselect |
| 1-G-7 | ✅ 完成 | 自動產生唯一 canonical ID |
| 1-G-8 | ✅ 大致完成 | 旗標/狀態頁 inline 編輯、targets 複選（UI 測試仍有缺口） |
| 1-G-9 | ✅ 完成 | ScheduleEntry `specific_date` + `schedule_id` 自動生成 |
| 2 | 未開始 | Event Blueprint MVP（schema, prompt builder, parser, linter） |
| 3 | 未開始 | Map Manager, Status Manager, Route Validator |
| 4-7 | 未開始 | Scene Draft, Dashboard, AI Provider, 資產管理 |

## 當前待辦

見 `已知問題.md`（~170 行，每次必讀）。

重點：
- 1-G-8 UI 行為測試覆蓋不足（已補強，待完整手動驗收）。
- 1-G-9 已完成並驗證通過（`tests/ -m "not integration"`：131 passed）。
- 下一主線：Phase 2 Event Blueprint MVP。

## 規格文件索引

### 開發設計方針.md（~3265 行）

| 區段 | 行範圍 | 何時讀 |
|:---|:---|:---|
| 版本紀錄 | 3-44 | 查版本變更歷史 |
| 全域規範（技術棧、ID、Schema/Linter 分工） | 45-178 | 新 session 第一次實作前 |
| Phase 0 | 241-314 | 修改 core/ 時 |
| Phase 1-A Schema | 333-510 | 修改 schema/ 時 |
| Phase 1-B Linter | 512-594 | 修改 linter 時 |
| Phase 1-C Exporter | 595-686 | 修改 exporter 時 |
| Phase 1-D Parser | 687-728 | 修改 parser 時 |
| Phase 1-E CLI | 729-770 | 修改 CLI 時 |
| Phase 1-F UIW Prototype | 771-949 | 修改 streamlit_uiw.py 時 |
| 1-G-1 ~ 1-G-2 | 950-1309 | 查歷史決策 |
| 1-G-3 語意型欄位 | 1310-1441 | 修改 SemanticChoice 相關 |
| 1-G-4 地點模板 | 1442-1781 | 修改地點相關 |
| 1-G-5 角色/行程 UX | 1782-2188 | 修改角色/行程相關 |
| 1-G-6 結局頁 | 2189-2378 | 修改結局相關 |
| 1-G-7 自動 ID | 2379-2464 | 修改 ID 生成相關 |
| 1-G-8 旗標/狀態 | 2465-2789 | 修改 flag/status 相關 |
| **1-G-9 specific_date + schedule_id** | **2790-2930** | **修改 Character/Schedule 或回歸 1-G-9 時** |
| Phase 2 Event Blueprint | 2932-2936 | 進入 Phase 2 時 |
| Phase 3-7 | 3038-3198 | 遠期參考 |

### 測試指南.md（~1420 行）

| 區段 | 行範圍 | 何時讀 |
|:---|:---|:---|
| 環境準備 + 指令速查 | 30-89 | 首次跑測試 |
| 測試分層原則 | 90-154 | 寫新測試前 |
| Phase 0-1E 測試 | 155-496 | 修改對應模組時 |
| 1-F UIW 測試 | 497-600 | 修改 Streamlit UI 時 |
| 1-G-3 ~ 1-G-6 測試 | 601-991 | 修改對應功能時 |
| 1-G-7 自動 ID 測試 | 992-1092 | 修改 ID 生成時 |
| 1-G-8 旗標/狀態測試 | 1093-1239 | 修改 flag/status 時 |
| **1-G-9 測試** | **1240-1342** | **修改 Character/Schedule 或回歸 1-G-9 時** |
| Phase 1 全階段回歸 | 1345-1371 | Phase 完成後回歸 |

### Sandbox_Dating_Sim_Dev_正式規格_v1.2.md（~1020 行）

上游遊戲規格。定義系統架構、Markdown DSL、Conditions/Results 語法、Route Validator 模式、Asset 管理。通常不需整份閱讀，按需 grep 特定主題。

| 區段 | 行範圍 | 何時讀 |
|:---|:---|:---|
| 設計原則 | 24-57 | 查「為什麼這樣設計」 |
| 系統架構 | 57-126 | 理解整體 pipeline |
| UIW 欄位規格 | 126-310 | 確認欄位定義 |
| Map Manager / Free Roam | 310-388 | Phase 3 |
| Markdown DSL | 389-525 | Phase 2 事件格式 |
| Route Validator | 637-783 | Phase 3 |

### Sandbox_Dating_Sim_初始設定_v1.2.md（~2931 行）

UIW 的完整欄位定義、預設選項、地點模板、角色模組、旗標/狀態/結局。各 1-G-* phase 的 UI 規格細節在此。

| 區段 | 行範圍 | 何時讀 |
|:---|:---|:---|
| 世界觀 | 93-229 | 修改 World 相關 |
| 主角設定 | 230-620 | 修改 Protagonist 相關 |
| 地點與模板 | 763-1527 | 修改 Location 相關 |
| 角色模組（含 Schedule） | 1528-2080 | 修改 Character/Schedule 相關 |
| 旗標/狀態/結局 | 2081-2520 | 修改 Flag/Status/Ending 相關 |
| 1-G-7 自動 ID 規格 | 2521-2633 | 修改 ID 生成 |
| 1-G-8 旗標/狀態 UI 規格 | 2634-2820 | 修改 flag/status UI |
| 輸出規格 | 2821-2905 | 修改 exporter |

### Sandbox_Dating_Sim_文件管線規格_v1.1.md（~450 行）

定義三種文件格式（Setup Package MD、Event Blueprint MD、Scene Draft MD）的結構與生成流程。Phase 2 開始時讀。

## 測試速查

```powershell
# 全部單元測試
.\.venv\Scripts\python.exe -m pytest tests/ -v -m "not integration"

# 指定測試檔
.\.venv\Scripts\python.exe -m pytest tests/test_uiw_linter.py -v

# 啟動 UIW
.\.venv\Scripts\python.exe -m streamlit run src/sandbox_dating_sim/ui/streamlit_uiw.py
```

注意：Windows/OneDrive 路徑下 pytest 暫存目錄可能出現 PermissionError，視為環境問題，可提升權限重跑。
