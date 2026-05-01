# Agent Instructions

## 新對話開場檢查

每次新對話開始時，先仔細閱讀根目錄最新文件與 GitHub / git commit 訊息，忽略 `舊文件/`。

回報時需告訴使用者：

- 目前進度
- 若有問題，列出問題與影響範圍

## 文件範圍規則

`舊文件/` 目錄中的文件屬於歷史版本，可以完全忽略。閱讀需求、確認規格或實作時，只以根目錄目前保留的最新文件為準。

## Project Skills

本專案使用 `C:\Users\User\OneDrive\桌面\AI_Work\Skills\` 內的本機 skills。

觸發規則：

- 使用者要求診斷 bug、分析錯誤、驗證、找 root cause 時：
  先讀 `C:\Users\User\OneDrive\桌面\AI_Work\Skills\engineering\diagnose\SKILL.md`
- 使用者需求不明、規格討論、要求規劃、要求先問問題時：
  先讀 `C:\Users\User\OneDrive\桌面\AI_Work\Skills\productivity\grill-me\SKILL.md`
- 一般狀態、無緊急或特殊狀況時：
  先讀 `C:\Users\User\OneDrive\桌面\AI_Work\Skills\productivity\caveman\SKILL.md`

只有在使用者明確要求修改、修復、實作、commit 時才能改檔；若只是驗證或診斷，只能回報。

## 驗證模式規則

當使用者要求「驗證」時，只能進行檢查、讀檔、執行測試、啟動本機服務與回報結果。

除非使用者明確要求「修」、「修改」、「commit」或「提交」，否則不得：

- 修改任何程式碼或文件
- 自行套 patch
- stage 檔案
- 建立 commit

若驗證中發現問題，只列出問題、影響範圍與建議修法，等待使用者下一步指示。

## 修改程式碼授權規則

除非使用者明確要求「修」、「修改」、「實作」、「處理某個 phase」、「commit」或「提交」，否則不得修改任何程式碼、文件或設定檔。

當使用者只是描述錯誤、貼截圖、詢問原因、要求解釋、要求列出問題、要求驗證，或詢問某功能怎麼使用時，只能分析與回報，不得自行套 patch。

## Python 執行環境規則

後續執行測試、匯入驗證、腳本執行時，預設固定使用專案虛擬環境：

- `.\.venv\Scripts\python.exe`

目標是讓 Agent 與使用者看到一致結果，避免誤用其他全域或內建 runtime Python。

### Pytest 暫存目錄權限注意

在此 Windows / OneDrive 專案路徑下，完整 pytest 回歸有時會在所有測試本體跑完後，於 session finish 清理 `.pytest_tmp*` / `--basetemp` 暫存目錄時出現 `PermissionError: [WinError 5] 存取被拒`。

若輸出顯示測試本體已跑完、失敗點只在 pytest 暫存目錄建立或清理，視為環境權限問題；不要反覆用一般權限重跑同一指令。應直接用同一專案虛擬環境與同一測試範圍，改以提升權限重跑一次確認正式結果，並在回報中說明一般權限卡在暫存目錄權限。

## 工具使用注意事項

若 `rg` 在此環境被拒絕執行，直接改用 PowerShell 原生命令列出檔案與搜尋內容；之後不需特別回報此環境限制，除非它影響任務結果。

讀取 `README.md` 時，改用明確 UTF-8 讀取，避免 PowerShell 預設編碼造成亂碼。

## 本機工具設定規則

`.claude/` 目錄屬於本機工具設定，不得納入 commit。

## Commit 與 Push 規則

當使用者明確要求 `commit + push` 時，視為前面已經完成必要驗證；不要再重跑測試，只需確認 git 狀態、提交並推送。

## 角色分工規則

當 AI 擔任實作者角色時，只能修改程式碼、測試與 fixture。
`已知問題.md`、`測試指南.md`、`開發設計方針.md` 等文件屬於驗證者職責，實作者不得自行修改。
若實作者發現文件需要更新，只能列出建議，等待使用者指示。

## 文件閱讀

- 舊文件/ 可完全忽略
