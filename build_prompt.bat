@echo off
cd /d "%~dp0"
set PYTHONPATH=src
.\.venv\Scripts\python.exe -m sandbox_dating_sim.cli build-blueprint-prompt
echo.
pause
