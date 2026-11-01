@echo off
REM ==============================================================================
REM SanMitra AI News Wire - LinkedIn post of the day's brief
REM The nightly run queues the post (out\aibrief\linkedin_queue\). This posts it
REM once YouTube has made the video public; a queued post is posted only once,
REM so the task can repeat through the morning and catch a PC that was off.
REM
REM Register once (PowerShell, no admin needed):
REM   $a = New-ScheduledTaskAction -Execute "D:\MyProjects\Remotion Studio\run_linkedin_post.bat"
REM   $t = New-ScheduledTaskTrigger -Daily -At 09:35
REM   $t.Repetition = (New-ScheduledTaskTrigger -Once -At 09:35 -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Hours 12)).Repetition
REM   $s = New-ScheduledTaskSettingsSet -StartWhenAvailable
REM   Register-ScheduledTask -TaskName SanMitra_LinkedIn_Post -Action $a -Trigger $t -Settings $s
REM ==============================================================================
cd /d "D:\MyProjects\Remotion Studio"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
if not exist "out\aibrief\logs" mkdir "out\aibrief\logs"
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set TODAY=%%i
echo ---- %DATE% %TIME% >> "out\aibrief\logs\linkedin_%TODAY%.log"
python post_to_linkedin.py --due >> "out\aibrief\logs\linkedin_%TODAY%.log" 2>&1
exit /b %ERRORLEVEL%
