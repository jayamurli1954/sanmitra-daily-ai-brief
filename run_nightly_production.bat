@echo off
REM ==============================================================================
REM SanMitra AI News Wire - 10:15 PM IST nightly production on this PC
REM Collects the day's AI news, builds tomorrow's episode (8-9 stories, topping up
REM fact-checked stories), renders it, and uploads it to YouTube as PRIVATE with
REM a scheduled publish at 06:30 IST. YouTube makes it public; the PC can be off.
REM ==============================================================================
cd /d "D:\MyProjects\Remotion Studio"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
if not exist "out\aibrief\logs" mkdir "out\aibrief\logs"

for /f %%i in ('powershell -NoProfile -Command "(Get-Date).AddDays(1).ToString('yyyy-MM-dd')"') do set EPISODE_DATE=%%i
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmm"') do set RUNSTAMP=%%i
set LOG=out\aibrief\logs\nightly_%RUNSTAMP%.log

echo ====================================================================== >> "%LOG%"
echo NIGHTLY PRODUCTION for %EPISODE_DATE% - started %DATE% %TIME% >> "%LOG%"
echo ====================================================================== >> "%LOG%"

REM 1. Collect the day's news into prompts\%EPISODE_DATE%.md. A short brief is
REM    not fatal here: step 2 tops it up from the fact-checked live harvest.
python nightly_brief_collector.py >> "%LOG%" 2>&1
echo Collector exit code %ERRORLEVEL% >> "%LOG%"

REM 2. Build, fact-check, voice, render and upload (private until 06:30 IST).
python run_autonomous_brief.py --date %EPISODE_DATE% --privacy private --publish-at-ist 06:30 >> "%LOG%" 2>&1
set RC=%ERRORLEVEL%

echo Finished at %TIME% with exit code %RC%. >> "%LOG%"
exit /b %RC%
