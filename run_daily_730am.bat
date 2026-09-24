@echo off
cd /d "D:\MyProjects\Remotion Studio"
echo ======================================================================
echo SANMITRA AI NEWS WIRE - 7:30 AM AUTOMATED PIPELINE
echo Date: %DATE% %TIME%
echo ======================================================================

python daily_brief_runner.py --privacy private >> out\aibrief\daily_scheduler.log 2>&1

echo Pipeline run finished at %TIME%.
