@echo off
REM ==============================================================================
REM SanMitra AI News Wire - 7:00 PM IST evening production on this PC
REM Collects the day's AI news, builds today's episode (8-10 stories, topping up
REM fact-checked stories), renders it, and uploads it to YouTube as PRIVATE with
REM a scheduled publish at 21:30 IST. YouTube makes it public; the PC can be off.
REM A late or catch-up run (the PC was asleep at 7 PM) cannot be ready by 9:30 PM:
REM   started 8 PM to 9:59 PM  -> still builds TODAY's episode, public at 23:59 IST
REM                               (or on upload, if the upload finishes after that)
REM   started 10 PM or later   -> builds tomorrow's episode, public at 09:30 IST
REM Only one production may run at a time: the runs share timings, audio and
REM metadata files, so a second run started alongside the first corrupts both.
REM ==============================================================================
cd /d "D:\MyProjects\Remotion Studio"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
if not exist "out\aibrief\logs" mkdir "out\aibrief\logs"

REM Refuse to start while another production is running (scheduled or started by hand).
powershell -NoProfile -Command "if (Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'run_autonomous_brief|nightly_brief_collector|weekly_roundup' }) { exit 1 } else { exit 0 }"
if errorlevel 1 (
    echo %DATE% %TIME% run_nightly_production.bat skipped: another production run is already active >> "out\aibrief\logs\skipped_runs.log"
    exit /b 0
)

for /f %%i in ('powershell -NoProfile -Command "if ((Get-Date).Hour -lt 22) { (Get-Date).ToString('yyyy-MM-dd') } else { (Get-Date).AddDays(1).ToString('yyyy-MM-dd') }"') do set EPISODE_DATE=%%i
for /f %%i in ('powershell -NoProfile -Command "$h = (Get-Date).Hour; if ($h -lt 20) { '21:30' } elseif ($h -lt 22) { '23:59' } else { '09:30' }"') do set PUBLISH_AT=%%i
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmm"') do set RUNSTAMP=%%i
set LOG=out\aibrief\logs\nightly_%RUNSTAMP%.log

echo ====================================================================== >> "%LOG%"
echo PRODUCTION for %EPISODE_DATE% at %PUBLISH_AT% IST - started %DATE% %TIME% >> "%LOG%"
echo ====================================================================== >> "%LOG%"

REM Sync with GitHub, then claim the episode. The cloud fallback
REM (.github\workflows\cloud_fallback.yml) wakes at about 7:45 PM IST and produces
REM the episode itself when nobody has claimed it, so the claim is what tells it
REM this PC is awake. A cloud claim means it is already producing: skip.
git pull --no-rebase --no-edit origin main >> "%LOG%" 2>&1
if errorlevel 1 (
    echo [!] git pull failed: commits from GitHub, including cloud fallback memory, are not merged. >> "%LOG%"
    git merge --abort >> "%LOG%" 2>&1
    git fetch origin main >> "%LOG%" 2>&1
)
git log origin/main -100 --format=%%s | findstr /C:"episode claim %EPISODE_DATE% by cloud" >nul
if errorlevel 1 goto cloudnotclaimed
REM The cloud claimed it. If it then failed it pushed a release: produce here after all.
git log origin/main -100 --format=%%s | findstr /C:"episode release %EPISODE_DATE% by cloud" >nul
if errorlevel 1 (
    echo [i] GitHub Actions (cloud autonomous) already claimed %EPISODE_DATE%: skipping local run. >> "%LOG%"
    exit /b 0
)
echo The cloud claimed %EPISODE_DATE% and then released/failed: producing locally. >> "%LOG%"
:cloudnotclaimed

REM If the episode has already been aired / recorded, skip local run entirely
if exist "src\aibrief\data\aired\%EPISODE_DATE%.json" (
    echo [i] Episode %EPISODE_DATE% has already aired / recorded in src\aibrief\data\aired: skipping local run. >> "%LOG%"
    exit /b 0
)

:claimcheckdone
git log origin/main -100 --format=%%s | findstr /C:"episode claim %EPISODE_DATE% by PC" >nul
if errorlevel 1 (
    git commit --allow-empty --only -m "Auto: episode claim %EPISODE_DATE% by PC [skip ci]" >> "%LOG%" 2>&1
    git push origin main >> "%LOG%" 2>&1
    if errorlevel 1 echo [!] Could not push the episode claim: the cloud fallback may also produce %EPISODE_DATE%. >> "%LOG%"
)

REM 0. An editor's brief saved as prompts\%EPISODE_DATE%.md instead of prompts\editor\
REM    would be overwritten by the collector: move it into prompts\editor\ first.
python adopt_editor_brief.py --date %EPISODE_DATE% >> "%LOG%" 2>&1

REM 1. Sunday's episode is the week's round-up of stories that did not air Monday to
REM    Saturday. Any other day: collect the day's news into prompts\%EPISODE_DATE%.md
REM    (a short brief is not fatal: step 2 tops it up from the live harvest).
for /f %%i in ('powershell -NoProfile -Command "([datetime]'%EPISODE_DATE%').DayOfWeek"') do set EPISODE_DAY=%%i
if /i "%EPISODE_DAY%"=="Sunday" goto weekly
python nightly_brief_collector.py --date %EPISODE_DATE% >> "%LOG%" 2>&1
echo Collector exit code %ERRORLEVEL% >> "%LOG%"
goto produce
:weekly
python weekly_roundup.py --date %EPISODE_DATE% >> "%LOG%" 2>&1
echo Weekly round-up exit code %ERRORLEVEL% >> "%LOG%"
REM No unaired stories this week: fall back to the day's news.
if not exist "prompts\%EPISODE_DATE%.md" python nightly_brief_collector.py --date %EPISODE_DATE% >> "%LOG%" 2>&1
:produce

REM 2. Build, fact-check, voice, render and upload (private until %PUBLISH_AT% IST).
python run_autonomous_brief.py --date %EPISODE_DATE% --privacy private --publish-at-ist %PUBLISH_AT% >> "%LOG%" 2>&1
set RC=%ERRORLEVEL%

REM 3. Monday's "AI for Accountants" LinkedIn post from the week's episodes
REM    (writes only when the episode date is a Monday; never fails the run).
python weekly_finance_post.py --date %EPISODE_DATE% >> "%LOG%" 2>&1

if %RC% equ 0 (
    git config user.name "SanMitra Intelligence Bot"
    git config user.email "bot@sanmitratech.com"
    git add prompts/ src/aibrief/data/aired/ src/aibrief/data/visual_memory.json src/aibrief/data/story_memory_ledger.json >> "%LOG%" 2>&1
    git commit -m "Auto: episode memory for %EPISODE_DATE% (PC run) [skip ci]" >> "%LOG%" 2>&1
    git push origin main >> "%LOG%" 2>&1
)

echo Finished at %TIME% with exit code %RC%. >> "%LOG%"
exit /b %RC%
