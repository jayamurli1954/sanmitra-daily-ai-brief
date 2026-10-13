@echo off
REM Retired on 2026-10-13. Production now runs once at night from
REM run_nightly_production.bat (task SanMitra_Nightly_Production, 10:15 PM),
REM which uploads a private video that YouTube publishes at 06:30 IST.
REM Running this task as well would rebuild the shared episode files while that
REM run is rendering, so it only records that it was skipped.
cd /d "D:\MyProjects\Remotion Studio"
if not exist "out\aibrief\logs" mkdir "out\aibrief\logs"
echo %DATE% %TIME% run_daily_730am.bat skipped: retired, see run_nightly_production.bat >> out\aibrief\logs\retired_tasks.log
exit /b 0
