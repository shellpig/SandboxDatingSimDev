# Sandbox Dating Sim Dev

沙盒戀愛模擬遊戲生成工具。這是一個輔助 AI 生成高品質遊戲腳本的工具鏈，採用分階段生成策略：

1. **User Input Wizard (UIW)**: 讓使用者定義世界觀、角色、地點與初始數值，產出 `Setup Package MD`。
2. **Event Blueprint Generator**: 根據 Setup Package，AI 產出事件骨架 `Event Blueprint MD`（邏輯合約）。
3. **Scene Draft Generator**: 根據驗證通過的 Event Blueprint，AI 產出詳細的對話與演出。

此專案負責開發此工具鏈的核心資料模型、Linter、Parser 與 UIW。

## 開發環境設置

我們使用 `uv` 進行套件管理。

```powershell
# 安裝依賴
uv sync --extra dev

# 執行測試
uv run pytest tests/ -v -m "not integration"
```

## 核心架構

- `src/sandbox_dating_sim/core/`: 核心常數、例外處理、ID 驗證。
- `src/sandbox_dating_sim/schema/`: Pydantic 資料模型與 Validation Report 定義。
- `src/sandbox_dating_sim/uiw/`: UIW Linter 邏輯與預設選項。
- `src/sandbox_dating_sim/pipeline/`: Markdown Exporter 與 Parser。
- `src/sandbox_dating_sim/ui/`: Streamlit Interactive UIW。
