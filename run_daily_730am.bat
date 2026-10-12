@echo off
cd /d "D:\MyProjects\Remotion Studio"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
if not exist "out\aibrief\logs" mkdir "out\aibrief\logs"

REM One log per day: a run that hangs and keeps its log open cannot stop the
REM next morning's run from starting (on 2026-10-12 a shared log did exactly that).
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmm"') do set RUNSTAMP=%%i
set LOG=out\aibrief\logs\daily_%RUNSTAMP%.log

echo ====================================================================== >> "%LOG%"
echo SANMITRA AI NEWS WIRE - 7:30 AM AUTOMATED PIPELINE >> "%LOG%"
echo Started: %DATE% %TIME% >> "%LOG%"
echo ====================================================================== >> "%LOG%"

python daily_brief_runner.py --privacy private >> "%LOG%" 2>&1
set RC=%ERRORLEVEL%

echo Pipeline finished at %TIME% with exit code %RC%. >> "%LOG%"
REM Pass the result to Task Scheduler so "Last Result" shows real failures.
exit /b %RC%
