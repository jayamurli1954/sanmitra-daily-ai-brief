"""
Daily 7:30 AM Automated Production Runner for SanMitra AI News Wire.
Orchestrates:
  1. 24h Intelligence Scrape (World/UN, USA, China, Asia, India, Robotics)
  2. Institutional 4.0s Multi-Cut Television Assembly
  3. Edge TTS Voiceover & Subtitle Generation
  4. 1080p MP4 Video Rendering (Remotion Studio)
  5. Automated YouTube Upload (@SanMitraTechSolutions)
  6. Ready-to-Publish Facebook & LinkedIn Dispatches
"""

import argparse
from datetime import datetime
import os
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_command(cmd, desc):
    print(f"\n[*] {desc}...")
    print(f"    Command: {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=PROJECT_DIR)
    if res.returncode != 0:
        print(f"[!] Warning/Error during '{desc}' (Exit code: {res.returncode})")
        return False
    return True

def run_daily_pipeline(date_str=None, privacy="private"):
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    log_dir = os.path.join(PROJECT_DIR, "out", "aibrief")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"pipeline_run_{date_str}.log")

    print("=" * 75)
    print("🌅 SANMITRA AI NEWS WIRE — 07:30 AM AUTOMATED BROADCAST DESK")
    print(f"📅 Target Production Date: {date_str}")
    print(f"🔒 YouTube Privacy Mode:   {privacy.upper()}")
    print("=" * 75)

    # 1. Scrape 24h news across World, USA, China, Asia, India, Robotics
    scrape_success = run_command(
        f"python scrape_daily_ai_news.py --date {date_str}",
        f"Scraping previous 24h AI & Robotics moves across 5 regions for {date_str}"
    )

    # 2. Run master production (audio, subtitles, thumbnail ranker, 1080p MP4, LinkedIn cover/article, YouTube private upload)
    prod_cmd = f"python produce_from_prompt.py --privacy {privacy}"
    prod_success = run_command(prod_cmd, "Rendering 1080p MP4 Broadcast, LinkedIn Deliverables, and Uploading to YouTube")

    print("\n" + "=" * 75)
    if prod_success:
        print(f"🎉 BROADCAST PUBLISHED FOR {date_str}!")
        print(f"📺 Channel: https://www.youtube.com/@SanMitraTechSolutions")
        print(f"📱 Facebook share copy: out/aibrief/facebook_post.txt")
        print(f"💼 LinkedIn share copy: out/aibrief/linkedin_post.txt")
    else:
        print(f"[!] Pipeline finished with warnings. Check logs for details.")
    print("=" * 75)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily 7:30 AM AI News Wire Runner")
    parser.add_argument("--date", type=str, help="Specific episode date (YYYY-MM-DD, defaults to today)")
    parser.add_argument("--privacy", type=str, default="private", choices=["private", "unlisted", "public"], help="YouTube visibility")
    args = parser.parse_args()

    run_daily_pipeline(date_str=args.date, privacy=args.privacy)
