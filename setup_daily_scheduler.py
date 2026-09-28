"""
Configures Windows Task Scheduler for the SanMitra AI News Wire 24-Hour Autonomous Cycle:
  1. Task 1: 11:00 PM IST Nightly Intelligence Collection (run_nightly_1100pm.bat)
  2. Task 2: 07:30 AM IST Morning Broadcast Production & Private YouTube Upload (run_daily_730am.bat)
"""

import os
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def register_task(task_name: str, batch_file_name: str, scheduled_time: str):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    batch_file = os.path.join(project_dir, batch_file_name)

    if not os.path.exists(batch_file):
        print(f"[!] Batch file not found: {batch_file}")
        return False

    print("=" * 70)
    print(f"⏰ REGISTERING {scheduled_time} DAILY WINDOWS TASK: {task_name}")
    print(f"📌 Task Name: {task_name}")
    print(f"🎯 Target:    {batch_file}")
    print(f"⏰ Schedule:  Daily at {scheduled_time}")
    print("=" * 70)

    cmd = f'schtasks /Create /F /SC DAILY /TN "{task_name}" /TR "\\"{batch_file}\\"" /ST {scheduled_time}'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if res.returncode == 0:
        print(f"[+] SUCCESS! Task '{task_name}' registered successfully.\n")
        return True
    else:
        print(f"[!] Notice: {res.stdout.strip()} {res.stderr.strip()}")
        # PowerShell scheduled task fallback
        ps_cmd = f'powershell -Command "$action = New-ScheduledTaskAction -Execute \'{batch_file}\'; $trigger = New-ScheduledTaskTrigger -Daily -At {scheduled_time}; Register-ScheduledTask -TaskName \'{task_name}\' -Action $action -Trigger $trigger -Force"'
        ps_res = subprocess.run(ps_cmd, shell=True, capture_output=True, text=True)
        if ps_res.returncode == 0:
            print(f"[+] SUCCESS via PowerShell Register-ScheduledTask for {task_name}!\n")
            return True
        else:
            print(f"[!] Fallback failed: {ps_res.stderr.strip()}\n")
            return False

def setup_both_schedulers():
    print("🚀 CONFIGURING DUAL-CADENCE AUTONOMOUS BROADCAST DESK SCHEDULERS")
    # Task 1: 11:00 PM IST (23:00)
    register_task("SanMitra_Nightly_1100PM", "run_nightly_1100pm.bat", "23:00")
    # Task 2: 07:30 AM IST (07:30)
    register_task("SanMitra_Morning_0730AM", "run_daily_730am.bat", "07:30")

if __name__ == "__main__":
    setup_both_schedulers()
