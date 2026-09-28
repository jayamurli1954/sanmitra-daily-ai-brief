@echo off
REM ==============================================================================
REM SanMitra AI News Wire - 11:00 PM IST Nightly Intelligence Collection
REM Gathers authentic 24h AI news, deduplicates, verifies visual memory, pushes to Git
REM ==============================================================================

cd /d "D:\MyProjects\Remotion Studio"
echo [!] Starting 11:00 PM Nightly Intelligence Agent...
python nightly_brief_collector.py
if %ERRORLEVEL% EQU 0 (
    echo [+] 11:00 PM Nightly collection finished successfully.
) else (
    echo [X] 11:00 PM Nightly collection encountered warnings/errors.
)
