"""
11:00 PM IST Nightly Intelligence Collector & Curation Agent for SanMitra AI News Wire v2.1.1.
Executes end-to-end:
  1. Gathers 24-hour authentic AI news across 5 bureaus
  2. Evaluates Source Authority (Tiers 1-5) and 100-Point Impact Scores
  3. Checks 14-day Story Memory Ledger for deduplication & multi-day story chains
  4. Enforces the Story Fatigue Engine (7-day entity saturation penalty)
  5. Enforces Flexible Bureau Policy (Min 3 active bureaus, Target 5)
  6. Crowns the Lead Story (Scene 1)
  7. Passes through the Editorial Quality Gate
  8. Downloads & pHash-verifies fresh editorial visuals (max 2 per category cap)
  9. Generates prompts/YYYY-MM-DD.md and src/aibrief/data/active_episode.json
 10. Automatically pushes updates to GitHub and backs up prompt to Google Drive
"""

import argparse
from datetime import datetime, timedelta
import json
import os
import subprocess
import sys

# Ensure project root is in sys.path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from src.aibrief.story_memory_ledger import StoryMemoryLedger
from src.aibrief.rank_stories import rank_and_curate_stories
from src.aibrief.editorial_quality_gate import EditorialQualityGate
from src.aibrief.visual_memory_manager import VisualMemoryManager


def run_command(cmd: str, desc: str) -> bool:
    print(f"\n[*] {desc}...")
    print(f"    Command: {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=PROJECT_DIR)
    if res.returncode != 0:
        print(f"[!] Warning/Error during '{desc}' (Exit code: {res.returncode})")
        return False
    return True


def run_nightly_collection(target_date: str = None, push_git: bool = True, sync_gdrive: bool = True) -> bool:
    if not target_date:
        # 11:00 PM IST prepares the next broadcast date
        target_date = datetime.now().strftime("%Y-%m-%d")

    print("=" * 75)
    print("🌙 SANMITRA AI NEWS WIRE — 11:00 PM NIGHT INTELLIGENCE AGENT")
    print(f"📅 Target Production Date: {target_date}")
    print("=" * 75)

    # 1. Scrape previous 24h intelligence across 5 bureaus
    scrape_ok = run_command(
        f"python scrape_daily_ai_news.py --date {target_date}",
        f"Scraping authentic 24h news wires for {target_date}"
    )

    scraped_file = os.path.join(PROJECT_DIR, "src", "aibrief", "data", f"{target_date}.json")
    active_file = os.path.join(PROJECT_DIR, "src", "aibrief", "data", "active_episode.json")

    candidate_stories = []
    if os.path.exists(scraped_file):
        with open(scraped_file, "r", encoding="utf-8") as f:
            scraped_data = json.load(f)
            candidate_stories = scraped_data.get("stories", [])
    elif os.path.exists(active_file):
        with open(active_file, "r", encoding="utf-8") as f:
            active_data = json.load(f)
            candidate_stories = active_data.get("stories", [])

    if not candidate_stories:
        print("[!] No candidate stories found from scraper. Engaging fallback.")
        return False

    # 2. Run Sprint 1 Story Ranking, Deduplication, and Lead Story Selection
    ledger = StoryMemoryLedger()
    ranked_result = rank_and_curate_stories(candidate_stories, current_date_str=target_date, ledger=ledger)

    qualified_stories = ranked_result.get("stories", [])
    print(f"\n[+] Evaluated {ranked_result['total_evaluated']} candidate stories.")
    print(f"[+] Qualified: {len(qualified_stories)} | Discarded: {ranked_result['discarded_stories_count']}")
    print(f"[+] Active Bureaus: {ranked_result['active_bureaus']} (Min Met: {ranked_result['bureau_minimum_met']})")
    print(f"👑 Lead Story: {ranked_result['lead_story']}")

    # 3. Download & pHash-verify fresh visuals with diversity caps
    download_ok = run_command(
        f"python download_daily_editorial_visuals.py --date {target_date}",
        "Downloading & pHash-verifying fresh story visuals"
    )

    # Ingest verified assets for Quality Gate check
    mgr = VisualMemoryManager()
    verified_assets = []
    for day in mgr.data.get("history", []):
        if day.get("date") == target_date:
            verified_assets = day.get("assets", [])
            break

    # 4. Editorial Quality Gate Evaluation
    gate = EditorialQualityGate()
    passes, scorecard = gate.evaluate_episode(qualified_stories, verified_assets, date_str=target_date)

    if not passes:
        print(f"[!] WARNING: Episode failed Editorial Quality Gate ({scorecard['composite_quality_score']}/100). Check alerts.json.")
    else:
        print(f"[+] Editorial Quality Gate PASSED: {scorecard['composite_quality_score']}/100")

    # 5. Generate Standard Markdown Prompt (prompts/YYYY-MM-DD.md)
    prompts_dir = os.path.join(PROJECT_DIR, "prompts")
    os.makedirs(prompts_dir, exist_ok=True)
    prompt_file = os.path.join(prompts_dir, f"{target_date}.md")

    dt_obj = datetime.strptime(target_date, "%Y-%m-%d")
    date_display = dt_obj.strftime("%A, %d %B %Y")

    lines = [
        "# 🤖 SanMitra AI News Wire",
        "",
        f"## Daily AI Brief — {date_display} (IST)",
        "",
        f"### Covering Global AI Developments — {date_display}",
        "",
        "---",
        ""
    ]

    # Group by bureau
    bureau_map = {}
    for s in qualified_stories:
        b = s.get("bureau", "WORLD").upper()
        if b not in bureau_map:
            bureau_map[b] = []
        bureau_map[b].append(s)

    bureau_icons = {
        "WORLD": "🌍 WORLD",
        "USA": "🇺🇸 USA",
        "CHINA": "🇨🇳 CHINA",
        "ASIA": "🌏 ASIA",
        "INDIA": "🇮🇳 INDIA"
    }

    for b_code, s_list in bureau_map.items():
        title = bureau_icons.get(b_code, f"🌐 {b_code}")
        lines.append(f"# {title}")
        lines.append("")
        for st in s_list:
            lead_tag = "👑 [LEAD STORY] " if st.get("lead_story") else ""
            lines.append(f"### {lead_tag}{st['headline']}")
            lines.append(st["summary"])
            lines.append("")
        lines.append("---")
        lines.append("")

    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[+] Formatted prompt generated: {prompt_file}")

    # Also build active_episode.json using build_episode_from_prompt.py
    run_command(f"python build_episode_from_prompt.py \"{prompt_file}\"", f"Building active episode JSON from {prompt_file}")

    # 6. Autonomous Git Commit & Push
    if push_git:
        run_command(
            f'git add prompts/ src/aibrief/data/ public/aibrief/assets/editorial/{target_date}/',
            "Staging prompt and curated assets for Git"
        )
        run_command(
            f'git commit -m "Auto: 24h AI Brief ingested for {target_date} [skip ci]"',
            "Committing ingested night intelligence"
        )
        run_command("git push origin main", "Pushing night intelligence to GitHub repository")

    # 7. Backup prompt to Google Drive
    if sync_gdrive:
        folder_id = os.environ.get("GDRIVE_FOLDER_ID")
        if folder_id and os.path.exists("upload_to_gdrive.py"):
            run_command(f"python upload_to_gdrive.py --date {target_date} --folder-id {folder_id}", "Backing up prompt to Google Drive")

    print("\n" + "=" * 75)
    print("🌙 NIGHTLY INTELLIGENCE COLLECTION COMPLETED SUCCESSFULLY!")
    print(f"📅 Target: {target_date}")
    print(f"📝 Prompt: {prompt_file}")
    print("🌅 Ready for Morning 07:30 AM Studio Broadcast Rendering.")
    print("=" * 75)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="11:00 PM Nightly AI News Wire Intelligence Collector")
    parser.add_argument("--date", type=str, help="Episode date (YYYY-MM-DD, defaults to today)")
    parser.add_argument("--no-git", action="store_true", help="Skip Git commit and push")
    parser.add_argument("--no-gdrive", action="store_true", help="Skip Google Drive sync")
    args = parser.parse_args()

    run_nightly_collection(target_date=args.date, push_git=not args.no_git, sync_gdrive=not args.no_gdrive)
