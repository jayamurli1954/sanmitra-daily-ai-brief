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
from datetime import datetime, timedelta, timezone
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


def _story_attribution(story: dict) -> tuple:
    """Outlet name and article URL actually attached to this story.

    Banned fallback strings are treated as missing. The night job must not
    write 'Reuters / Bloomberg Wire' or reuters.com when the scraper did
    not record that outlet.
    """
    outlet = (story.get("source") or "").strip()
    url = (story.get("source_url") or story.get("sourceUrl") or "").strip()
    banned_names = {
        "reuters / bloomberg wire",
        "reuters, bloomberg",
        "reuters bloomberg",
        "verified reports",
        "global tech wire",
        "wire",
    }
    banned_urls = {"https://reuters.com", "https://sanmitra.ai", "http://reuters.com"}
    if outlet.lower() in banned_names:
        outlet = ""
    if url.rstrip("/").lower() in banned_urls:
        url = ""
    if not outlet and url:
        from src.aibrief.source_authority import score_source
        _score, _tier, identified = score_source(url)
        if identified and identified != "Unknown Source":
            outlet = identified
    return outlet, url


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
        # 11:00 PM IST prepares the next morning's broadcast. GitHub's clock is UTC,
        # so the date is decided in India time, not the machine clock.
        ist = timezone(timedelta(hours=5, minutes=30))
        now = datetime.now(ist)
        if now.hour >= 20:
            now = now + timedelta(days=1)
        target_date = now.strftime("%Y-%m-%d")

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

    # 5. Keep the human-approved markdown if it is already on disk.
    # The night scraper must not replace that file with a second, unlabeled
    # copy of the same news — that is how a Straits Times story became a
    # Financial Times citation with nothing left to check.
    prompts_dir = os.path.join(PROJECT_DIR, "prompts")
    os.makedirs(prompts_dir, exist_ok=True)
    prompt_file = os.path.join(prompts_dir, f"{target_date}.md")

    if os.path.exists(prompt_file):
        print(f"[*] Approved prompt already exists. Leaving it unchanged: {prompt_file}")
    else:
        dt_obj = datetime.strptime(target_date, "%Y-%m-%d")
        date_display = dt_obj.strftime("%A, %d %B %Y")

        lines = [
            "# SanMitra AI News Wire",
            "",
            f"## Daily AI Brief — {date_display} (IST)",
            "",
            "Covering AI developments from the previous day. Only items with a named outlet are included.",
            "",
            "---",
            ""
        ]

        bureau_map = {}
        for s in qualified_stories:
            b = s.get("bureau", "WORLD").upper()
            bureau_map.setdefault(b, []).append(s)

        bureau_icons = {
            "WORLD": "WORLD",
            "USA": "USA",
            "CHINA": "CHINA",
            "ASIA": "ASIA",
            "INDIA": "INDIA"
        }

        written = 0
        for b_code, s_list in bureau_map.items():
            titled = []
            for st in s_list:
                outlet, url = _story_attribution(st)
                if not outlet:
                    print(f"[!] Skipping unlabeled story (no outlet to cite): {st.get('headline', '')[:80]}")
                    continue
                titled.append((st, outlet, url))
            if not titled:
                continue
            lines.append(f"# {bureau_icons.get(b_code, b_code)}")
            lines.append("")
            for st, outlet, url in titled:
                lines.append(f"### {st['headline']}")
                lines.append(f"Source: {outlet}")
                if url:
                    lines.append(url)
                lines.append("")
                lines.append(st.get("summary") or "")
                lines.append("")
                written += 1
            lines.append("---")
            lines.append("")

        if written == 0:
            print("[X] No story had a real outlet name. Refusing to write a prompt.")
            return False

        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"[+] Formatted prompt generated with named sources: {prompt_file}")

        # Record accepted stories into the 14-day persistent memory ledger
        for st in qualified_stories:
            ledger.record_story(
                headline=st["headline"],
                companies=st.get("companies", []),
                topics=st.get("topics", []),
                country=st.get("country", st.get("bureau", "World")),
                source_urls=[st.get("source_url")] if st.get("source_url") else [],
                impact_score=int(st.get("final_rank_score", 80)),
                story_chain_id=st.get("story_chain_id"),
                current_date_str=target_date
            )
        ledger.save()
        print(f"[+] Recorded {len(qualified_stories)} stories into 14-day memory ledger.")

    built = run_command(
        f"python build_episode_from_prompt.py \"{prompt_file}\"",
        f"Building active episode JSON from {prompt_file}",
    )
    if not built:
        print("[X] Episode build failed. Stopping before commit, push, or upload.")
        return False

    traced = run_command(
        f"python validate_episode_sources.py --date {target_date}",
        "Source traceability gate",
    )
    if not traced:
        print("[X] Source traceability gate failed. Not committing, pushing, or rendering.")
        return False

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

    ok = run_nightly_collection(target_date=args.date, push_git=not args.no_git, sync_gdrive=not args.no_gdrive)
    sys.exit(0 if ok else 1)
