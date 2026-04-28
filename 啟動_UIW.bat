@echo off
chcp 65001 >nul
echo ==============================================
echo 正在啟動 Sandbox Dating Sim UIW (Streamlit)...
echo ==============================================
cd /d "%~dp0"
set "PYTHONPATH=%~dp0src;%PYTHONPATH%"
uv run streamlit run src/sandbox_dating_sim/ui/streamlit_uiw.py
pause
