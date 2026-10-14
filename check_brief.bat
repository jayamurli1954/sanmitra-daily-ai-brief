@echo off
REM Double-click to check tomorrow's editor brief (prompts\editor\<date>.md).
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
python check_editor_brief.py %1
echo.
pause
