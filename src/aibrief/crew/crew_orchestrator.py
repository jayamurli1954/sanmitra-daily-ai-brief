"""
Crew Orchestrator - SanMitra AI News Wire

Produces today's episode JSON from a prompt in the approved format:

  1. If prompts/<date>.md already exists (the 11 PM nightly collector or a human
     editor wrote it), it is used. If it has fewer than 12 usable stories, the
     crew tops it up with verified stories about other events.
  2. Otherwise the crew harvests, fact-checks and writes prompts/<date>.md from
     the extracted article text.
  3. build_episode_from_prompt.py builds the episode from that prompt, so the
     source traceability gate always has a prompt to check against.

An episode has 8-9 stories of about 50-60 seconds (under 10 minutes); with fewer
than 8, no episode is made.
Every subprocess result is checked, and the orchestrator never falls back to an
episode JSON that is already on disk, which could be yesterday's.
"""

from datetime import datetime
import json
import logging
import os
import subprocess
import sys

from src.aibrief.story_memory_ledger import StoryMemoryLedger

from .fact_checker import MAX_EPISODE_STORIES, MIN_EPISODE_STORIES, FactChecker
from .linkedin_publisher import LinkedInPublisher
from .news_harvester import NewsHarvester
from .prompt_writer import append_stories, write_prompt
from .text_utils import IST

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CrewOrchestrator")

DATA_DIR = os.path.join("src", "aibrief", "data")
ACTIVE_EPISODE = os.path.join(DATA_DIR, "active_episode.json")


def _run(args, description):
    logger.info(f"{description}: {' '.join(args)}")
    return subprocess.run([sys.executable] + args).returncode == 0


def prompt_story_headlines(prompt_path):
    """Headlines the builder will actually keep from this prompt (sourced, de-duplicated)."""
    from build_episode_from_prompt import parse_markdown_prompt
    with open(prompt_path, "r", encoding="utf-8") as f:
        episode = parse_markdown_prompt(f.read())
    return [s["headline"] for s in episode.get("stories", [])]


def _build_episode(prompt_path, target_date):
    """Build the episode and return what was just written to active_episode.json.

    The video renders active_episode.json, so that file is the one checked; a
    date-named file left over from an earlier build proves nothing.
    """
    if os.path.exists(ACTIVE_EPISODE):
        os.remove(ACTIVE_EPISODE)
    if not _run(["build_episode_from_prompt.py", prompt_path], "Building episode from prompt"):
        logger.error("Episode build failed.")
        return None
    if not os.path.exists(ACTIVE_EPISODE):
        logger.error("Build finished but active_episode.json was not written.")
        return None
    with open(ACTIVE_EPISODE, "r", encoding="utf-8") as f:
        episode = json.load(f)
    if episode.get("date") != target_date:
        logger.error(f"Built episode is dated {episode.get('date')}, expected {target_date}; check the prompt's date line.")
        return None
    if len(episode.get("stories", [])) < MIN_EPISODE_STORIES:
        logger.error(f"Built episode has {len(episode.get('stories', []))} stories; at least {MIN_EPISODE_STORIES} are required.")
        return None
    return episode


def record_aired_stories(target_date, episode_path=ACTIVE_EPISODE):
    """Add the episode's stories to the 14-day ledger. Call only after a successful upload,
    so a failed run does not block its unaired stories for the next 7 days."""
    with open(episode_path, "r", encoding="utf-8") as f:
        episode = json.load(f)
    ledger = StoryMemoryLedger()
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


def _crew_verify(target_date, max_stories, exclude_titles=()):
    harvester = NewsHarvester(target_date=target_date)
    candidates = harvester.harvest()
    fact_checker = FactChecker(target_date=target_date, fetch_article=harvester.fetch_article,
                               ledger=StoryMemoryLedger())
    verified = fact_checker.assemble_stories(candidates, max_stories=max_stories, exclude_titles=exclude_titles)
    return verified, fact_checker.rejections


def _merge_editor_brief(editor_path, prompt_path, target_date, warnings):
    """Put the editor's own stories first; collector stories on the same event become "Also:" sources."""
    from .editor_brief import merge_editor_brief
    with open(editor_path, "r", encoding="utf-8") as f:
        editor_md = f.read()
    other_md = ""
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            other_md = f.read()
        # Keep the collector's version for reference; the merged brief replaces it.
        backup = os.path.join("out", "aibrief", "logs", f"prompt_{target_date}_before_editor_merge.md")
        os.makedirs(os.path.dirname(backup), exist_ok=True)
        with open(backup, "w", encoding="utf-8") as f:
            f.write(other_md)
    merged, report = merge_editor_brief(editor_md, other_md, target_date, MAX_EPISODE_STORIES)
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(merged)
    logger.info(f"Merged editor brief {editor_path}: {report['editor']} editor stories, "
                f"{report['added']} collector stories added, {len(report['duplicates'])} duplicates folded in, "
                f"{len(report['dropped_for_space'])} dropped for space; {report['total']} in total.")
    for dup, kept in report["duplicates"]:
        logger.info(f"  [DUPLICATE] {dup[:70]} -> same event as editor/kept story '{kept[:60]}'")
    warnings.append(f"Editor brief merged: {report['editor']} editor stories + {report['added']} others "
                    f"({len(report['duplicates'])} duplicates removed).")


def _add_daily_paper(prompt_path, target_date, editor_path, warnings):
    """Give the day's most upvoted Hugging Face paper one slot in the brief.

    The crew's own harvest only runs when a brief is short, so on a full day the
    paper would never appear. It is added if there is room; otherwise it replaces
    the last story that is neither the lead nor one of the editor's."""
    from .editor_brief import parse_stories, render
    from .prompt_writer import render_story_sections

    with open(prompt_path, "r", encoding="utf-8") as f:
        md = f.read()
    if "arxiv.org/abs/" in md:
        return
    harvester = NewsHarvester(target_date=target_date)
    candidates = harvester.filter_candidates(harvester.fetch_daily_paper())
    if not candidates:
        return
    checker = FactChecker(target_date=target_date, fetch_article=harvester.fetch_article, ledger=StoryMemoryLedger())
    verified = checker.assemble_stories(candidates, max_stories=1)
    if not verified:
        logger.info(f"Daily paper not used: {checker.rejections}")
        return

    stories = parse_stories(md)
    paper = parse_stories("\n".join(render_story_sections(verified)))[0]
    editor_heads = set()
    if os.path.exists(editor_path):
        with open(editor_path, "r", encoding="utf-8") as f:
            editor_heads = {s["headline"] for s in parse_stories(f.read())}
    if len(stories) >= MAX_EPISODE_STORIES:
        replaceable = [i for i, s in enumerate(stories)
                       if s["headline"] not in editor_heads and not any(l.strip().lower() == "lead: yes" for l in s["lines"])]
        if not replaceable:
            logger.info("Daily paper not used: every story is the editor's or the lead.")
            return
        dropped = stories.pop(replaceable[-1])
        logger.info(f"Daily paper replaces: {dropped['headline'][:70]}")
    stories.append(paper)
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(render(stories, target_date))
    logger.info(f"Daily paper added: {paper['headline'][:70]}")
    warnings.append(f"Research story from Hugging Face Daily Papers: {paper['headline'][:70]}")


def run_autonomous_crew(target_date=None, force_visuals=False):
    """Returns the built episode dict, or None if no trustworthy 8+ story episode could be made."""
    if not target_date:
        target_date = datetime.now(IST).strftime("%Y-%m-%d")

    logger.info("=" * 70)
    logger.info(f"AI NEWS WIRE CREW FOR: {target_date}")
    logger.info("=" * 70)

    prompt_path = os.path.join("prompts", f"{target_date}.md")
    rejections, warnings = [], []

    def give_up(reason):
        logger.error(reason)
        write_qa_summary(target_date, {"stories": []}, "none", rejections, [reason])
        return None

    editor_path = os.path.join("prompts", "editor", f"{target_date}.md")
    if os.path.exists(editor_path):
        _merge_editor_brief(editor_path, prompt_path, target_date, warnings)

    if os.path.exists(prompt_path):
        try:
            _add_daily_paper(prompt_path, target_date, editor_path, warnings)
        except Exception as e:
            logger.warning(f"Daily paper skipped: {e}")

    if os.path.exists(prompt_path):
        existing = prompt_story_headlines(prompt_path)
        prompt_origin = f"existing prompt {prompt_path} ({len(existing)} usable stories)"
        if len(existing) < MIN_EPISODE_STORIES:
            logger.warning(f"{prompt_path} has only {len(existing)} usable stories; topping up from the crew.")
            extra, rejections = _crew_verify(target_date, MAX_EPISODE_STORIES - len(existing), exclude_titles=existing)
            if len(existing) + len(extra) < MIN_EPISODE_STORIES:
                return give_up(f"Only {len(existing) + len(extra)} stories available "
                               f"(prompt {len(existing)} + crew {len(extra)}); minimum is {MIN_EPISODE_STORIES}. No episode today.")
            append_stories(prompt_path, extra)
            prompt_origin += f", topped up with {len(extra)} crew-verified stories"
            warnings.append(f"The prompt had {len(existing)} stories; {len(extra)} were added by the crew.")
    else:
        verified, rejections = _crew_verify(target_date, MAX_EPISODE_STORIES)
        if len(verified) < MIN_EPISODE_STORIES:
            return give_up(f"Only {len(verified)} stories passed fact-checking (minimum {MIN_EPISODE_STORIES}). No episode today.")
        write_prompt(verified, target_date)
        prompt_origin = f"crew-drafted prompt {prompt_path}"

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
