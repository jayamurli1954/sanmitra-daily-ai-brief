"""
Crew Orchestrator - SanMitra AI News Wire v7.0
Executes autonomous multi-agent intelligence gathering, fact-checking, scriptwriting, and publishing.
"""

from datetime import datetime, timedelta, timezone
import json
import logging
import os
import sys

from .news_harvester import NewsHarvester
from .fact_checker import FactChecker
from .scriptwriter import BroadcastScriptwriter
from .visual_director import VisualDirector
from .linkedin_publisher import LinkedInPublisher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CrewOrchestrator")


def run_autonomous_crew(target_date=None, force_visuals=False):
    """Executes the full multi-agent cycle to generate active_episode.json and LinkedIn dispatches."""
    if not target_date:
        ist = timezone(timedelta(hours=5, minutes=30))
        target_date = datetime.now(ist).strftime("%Y-%m-%d")

    logger.info("=" * 70)
    logger.info(f"🚀 INITIATING AUTONOMOUS AI NEWS WIRE CREW FOR: {target_date}")
    logger.info("=" * 70)

    # 1. News Harvester Agent
    logger.info("[Agent 1: NewsHarvester] Gathering 24h intelligence across feeds & search...")
    harvester = NewsHarvester(target_date=target_date)
    raw_candidates = harvester.harvest()

    # 2. Fact Checker & Bureau Curator Agent
    logger.info("[Agent 2: FactChecker] Validating sources, numbers, and regional balance...")
    fact_checker = FactChecker()
    selected_stories = fact_checker.assemble_14_stories(raw_candidates)

    if not selected_stories or len(selected_stories) < 6:
        logger.warning("Low candidate count from live scraper; checking for approved prompts backup...")
        prompt_fallback = os.path.join("prompts", f"{target_date}.md")
        if os.path.exists(prompt_fallback):
            logger.info(f"Ingesting pre-approved prompt backup: {prompt_fallback}")
            import subprocess
            subprocess.run(f'python build_episode_from_prompt.py "{prompt_fallback}"', shell=True)
            active_path = os.path.join("src", "aibrief", "data", "active_episode.json")
            with open(active_path, "r", encoding="utf-8") as f:
                episode_payload = json.load(f)
        else:
            logger.error(f"Insufficient intelligence gathered and no fallback at {prompt_fallback}!")
            return None
    else:
        # 3. Broadcast Scriptwriter Agent
        logger.info("[Agent 3: BroadcastScriptwriter] Drafting dual-anchor scripts & phonetic currencies...")
        scriptwriter = BroadcastScriptwriter()
        episode_payload = scriptwriter.generate_episode_script(selected_stories, target_date)

        # 4. Visual Director Agent
        logger.info("[Agent 4: VisualDirector] Sourcing editorial stills with 14-day freshness...")
        visual_director = VisualDirector(target_date)
        episode_payload = visual_director.source_and_download_visuals(episode_payload, force=force_visuals)

        # Save to persistent storage
        date_out = os.path.join("src", "aibrief", "data", f"{target_date}.json")
        active_out = os.path.join("src", "aibrief", "data", "active_episode.json")

        with open(date_out, "w", encoding="utf-8") as f:
            json.dump(episode_payload, f, indent=2, ensure_ascii=False)
        with open(active_out, "w", encoding="utf-8") as f:
            json.dump(episode_payload, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved active episode to: {active_out} and {date_out}")

    # 5. LinkedIn Publisher Agent
    logger.info("[Agent 5: LinkedInPublisher] Generating executive LinkedIn article & cover banner...")
    publisher = LinkedInPublisher(episode_payload)
    deliverables = publisher.publish_deliverables()

    logger.info("=" * 70)
    logger.info("✅ AUTONOMOUS CREW INTELLIGENCE CYCLE COMPLETED SUCCESSFULLY")
    logger.info(f"   • Active Episode: src/aibrief/data/active_episode.json")
    logger.info(f"   • LinkedIn Post:  {deliverables.get('article')}")
    logger.info(f"   • LinkedIn Cover: {deliverables.get('banner')}")
    logger.info("=" * 70)

    return episode_payload


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SanMitra Autonomous Crew Orchestrator")
    parser.add_argument("--date", type=str, help="Target broadcast date (YYYY-MM-DD)")
    parser.add_argument("--force-visuals", action="store_true", help="Force redownload of visual stills")
    args = parser.parse_args()

    run_autonomous_crew(target_date=args.date, force_visuals=args.force_visuals)
