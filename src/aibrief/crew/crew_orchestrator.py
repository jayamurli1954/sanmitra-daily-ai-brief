"""
Crew Orchestrator - SanMitra AI News Wire

Produces today's episode JSON from a prompt in the approved format:

  1. If prompts/<date>.md already exists (the 11 PM nightly collector or a human
     editor wrote it), that prompt is used as-is.
  2. Otherwise the crew harvests, fact-checks and writes prompts/<date>.md from
     the extracted article text.
  3. build_episode_from_prompt.py builds the episode from that prompt, so the
     source traceability gate always has a prompt to check against.

Every subprocess result is checked. The orchestrator never falls back to an
episode JSON that is already on disk, which could be yesterday's.
"""

from datetime import datetime
import json
import logging
import os
import subprocess
import sys

from src.aibrief.story_memory_ledger import StoryMemoryLedger

from .fact_checker import FactChecker
from .linkedin_publisher import LinkedInPublisher
from .news_harvester import NewsHarvester
from .prompt_writer import write_prompt
from .text_utils import IST

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CrewOrchestrator")

MIN_STORIES = 6
DATA_DIR = os.path.join("src", "aibrief", "data")


def _run(args, description):
    logger.info(f"{description}: {' '.join(args)}")
    return subprocess.run([sys.executable] + args).returncode == 0


def _build_episode(prompt_path, target_date):
    """Build the episode from the prompt and return it, or None if anything is off."""
    if not _run(["build_episode_from_prompt.py", prompt_path], "Building episode from prompt"):
        logger.error("Episode build failed.")
        return None
    episode_path = os.path.join(DATA_DIR, f"{target_date}.json")
    if not os.path.exists(episode_path):
        logger.error(f"Build finished but {episode_path} was not written; the prompt's date line may be wrong.")
        return None
    with open(episode_path, "r", encoding="utf-8") as f:
        episode = json.load(f)
    if episode.get("date") != target_date:
        logger.error(f"Built episode is dated {episode.get('date')}, expected {target_date}.")
        return None
    return episode


def _record_in_ledger(ledger, episode, target_date):
    """Record aired stories once per day, whichever path produced the prompt."""
    already = {s.get("headline") for s in ledger.data.get("stories", []) if s.get("first_covered") == target_date}
    for story in episode.get("stories", []):
        if story.get("headline") in already:
            continue
        ledger.record_story(
            headline=story["headline"],
            companies=[],
            topics=[],
            country=story.get("region", "WORLD"),
            source_urls=[story.get("sourceUrl")] if story.get("sourceUrl") else [],
            impact_score=int(story.get("importanceScore", 80)),
            current_date_str=target_date,
        )


def write_qa_summary(target_date, episode, prompt_origin, rejections, warnings):
    """A one-page summary for the human skim before the video is made public."""
    os.makedirs(os.path.join("out", "aibrief"), exist_ok=True)
    path = os.path.join("out", "aibrief", f"qa_summary_{target_date}.md")
    lines = [f"# QA summary — {target_date}", "", f"Prompt: {prompt_origin}", ""]
    lines.append(f"## Stories ({len(episode.get('stories', []))})")
    for i, s in enumerate(episode.get("stories", []), 1):
        label = "company announcement" if s.get("sourceType") == "company" else "reporting"
        lines.append(f"{i}. [{s.get('region')}] {s.get('headline')}")
        lines.append(f"   - {s.get('source')} ({label}): {s.get('sourceUrl')}")
    if warnings:
        lines += ["", "## Warnings"] + [f"- {w}" for w in warnings]
    if rejections:
        lines += ["", f"## Rejected by fact-check ({len(rejections)})"]
        lines += [f"- {r['title'][:90]} — {r['reason']}" for r in rejections]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    logger.info(f"QA summary written: {path}")
    return path


def run_autonomous_crew(target_date=None, force_visuals=False):
    """Returns the built episode dict, or None if no trustworthy episode could be made."""
    if not target_date:
        target_date = datetime.now(IST).strftime("%Y-%m-%d")

    logger.info("=" * 70)
    logger.info(f"AI NEWS WIRE CREW FOR: {target_date}")
    logger.info("=" * 70)

    ledger = StoryMemoryLedger()
    prompt_path = os.path.join("prompts", f"{target_date}.md")
    rejections, warnings = [], []

    if os.path.exists(prompt_path):
        prompt_origin = f"existing approved prompt {prompt_path}"
        logger.info(f"Using {prompt_origin}; the crew does not re-harvest.")
    else:
        prompt_origin = f"crew-drafted prompt {prompt_path}"
        harvester = NewsHarvester(target_date=target_date)
        candidates = harvester.harvest()

        fact_checker = FactChecker(target_date=target_date, fetch_article=harvester.fetch_article, ledger=ledger)
        verified = fact_checker.assemble_14_stories(candidates)
        rejections = fact_checker.rejections

        if len(verified) < MIN_STORIES:
            logger.error(f"Only {len(verified)} stories passed fact-checking (minimum {MIN_STORIES}). No episode today.")
            write_qa_summary(target_date, {"stories": []}, "none (too few verified stories)", rejections,
                             [f"Only {len(verified)} verified stories; episode not produced."])
            return None
        write_prompt(verified, target_date)

    episode = _build_episode(prompt_path, target_date)
    if not episode:
        return None

    # The downloader reads active_episode.json, so it runs after the first build;
    # the second build attaches the freshly downloaded stills to each story.
    downloader_args = ["download_daily_editorial_visuals.py", "--date", target_date]
    if force_visuals:
        downloader_args.append("--force")
    if not _run(downloader_args, "Downloading editorial visuals"):
        warnings.append("Editorial visual download failed; stories use fallback stills.")
    episode = _build_episode(prompt_path, target_date)
    if not episode:
        return None

    missing_cuts = sum(
        1 for s in episode.get("stories", []) for c in s.get("visualCuts", [])
        if f"/editorial/{target_date}/" not in c.get("image", "")
    )
    if missing_cuts:
        warnings.append(f"{missing_cuts} visual cuts use fallback library stills instead of today's downloads.")

    _record_in_ledger(ledger, episode, target_date)
    write_qa_summary(target_date, episode, prompt_origin, rejections, warnings)

    deliverables = LinkedInPublisher(episode).publish_deliverables()
    logger.info(f"LinkedIn post: {deliverables.get('article')} | cover: {deliverables.get('banner')}")
    return episode


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SanMitra Autonomous Crew Orchestrator")
    parser.add_argument("--date", type=str, help="Target broadcast date (YYYY-MM-DD)")
    parser.add_argument("--force-visuals", action="store_true", help="Force redownload of visual stills")
    args = parser.parse_args()
    sys.exit(0 if run_autonomous_crew(target_date=args.date, force_visuals=args.force_visuals) else 1)
