@echo off
REM ==============================================================================
REM SanMitra AI News Wire - 11:00 PM IST Nightly Intelligence Collection
REM Gathers authentic 24h AI news, deduplicates, verifies visual memory, pushes to Git
REM ==============================================================================

cd /d "D:\MyProjects\Remotion Studio"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
if not exist "out\aibrief" mkdir "out\aibrief"
echo ============================================================================== >> out\aibrief\nightly_collector.log
echo [!] Starting 11:00 PM Nightly Intelligence Agent at %DATE% %TIME% >> out\aibrief\nightly_collector.log
python nightly_brief_collector.py >> out\aibrief\nightly_collector.log 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [+] 11:00 PM Nightly collection finished successfully. >> out\aibrief\nightly_collector.log
) else (
    echo [X] 11:00 PM Nightly collection encountered warnings/errors. >> out\aibrief\nightly_collector.log
)
