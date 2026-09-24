"""
Configures Windows Task Scheduler to run SanMitra AI News Wire every day at 07:30 AM IST.
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

def setup_scheduler():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    batch_file = os.path.join(project_dir, "run_daily_730am.bat")

    if not os.path.exists(batch_file):
        print(f"[!] Batch file not found: {batch_file}")
        sys.exit(1)

    # Wrap target in quotes for schtasks
    target = f'"{batch_file}"'
    task_name = "SanMitra_Daily_AI_Brief"

    print("=" * 70)
    print("⏰ REGISTERING 07:30 AM DAILY WINDOWS TASK")
    print(f"📌 Task Name: {task_name}")
    print(f"🎯 Command:   {target}")
    print(f"⏰ Schedule:  Daily at 07:30 AM")
    print("=" * 70)

    cmd = f'schtasks /Create /F /SC DAILY /TN "{task_name}" /TR "\\"{batch_file}\\"" /ST 07:30'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if res.returncode == 0:
        print(f"\n[+] SUCCESS! Windows Task '{task_name}' registered successfully.")
        print(f"    Output: {res.stdout.strip()}")
    else:
        print(f"\n[!] Notice / Output: {res.stdout.strip()} {res.stderr.strip()}")
        # Also show PowerShell ScheduledTask alternative if needed
        ps_cmd = f'powershell -Command "$action = New-ScheduledTaskAction -Execute \'{batch_file}\'; $trigger = New-ScheduledTaskTrigger -Daily -At 7:30am; Register-ScheduledTask -TaskName \'{task_name}\' -Action $action -Trigger $trigger -Force"'
        ps_res = subprocess.run(ps_cmd, shell=True, capture_output=True, text=True)
        if ps_res.returncode == 0:
            print(f"[+] SUCCESS via PowerShell Register-ScheduledTask!")
        else:
            print(f"    PowerShell fallback output: {ps_res.stdout} {ps_res.stderr}")

if __name__ == "__main__":
    setup_scheduler()
