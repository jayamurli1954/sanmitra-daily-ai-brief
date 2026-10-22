"""
Check the editor's brief before the night run picks it up.

    python check_editor_brief.py              # tomorrow's file (today's after midnight)
    python check_editor_brief.py 2026-10-15   # a specific air date

Reads prompts/editor/<date>.md the same way the night run does and reports
what will be used: how many stories, which one leads, and anything that would
be dropped (no link, unreadable layout, stock-market headline, over the cap).
Exit code 0 means OK.
"""

import os
import sys
from datetime import datetime, timedelta

from build_episode_from_prompt import clean_text_for_broadcast, parse_markdown_prompt
from src.aibrief.crew.editor_brief import merge_editor_brief, parse_stories
from src.aibrief.crew.fact_checker import MAX_EPISODE_STORIES, MIN_EPISODE_STORIES
from src.aibrief.crew.text_utils import is_election_story, is_personal_scandal_story, is_stock_market_story

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FORMAT_HELP = """Each story needs this layout (see prompts/editor/README.md):

    # WORLD

    ### Headline of the story
    Source: Outlet name https://link-to-the-article

    One or two paragraphs summarising the story.

Regions: # WORLD, # USA, # CHINA, # ASIA, # INDIA. Put the most important story first."""


def default_date() -> str:
    # In the evening the file is for tomorrow morning; after midnight, for today.
    now = datetime.now()
    return (now + timedelta(days=1) if now.hour >= 6 else now).strftime("%Y-%m-%d")


def check(date: str, editor_dir: str = os.path.join("prompts", "editor")) -> int:
    path = os.path.join(editor_dir, f"{date}.md")
    print(f"Checking {path} (for the {date} episode)\n")
    if not os.path.exists(path):
        print(f"[X] File not found. Save your brief as {path}")
        return 1
    with open(path, "r", encoding="utf-8") as f:
        md = f.read()

    stories = parse_stories(md)
    if not stories:
        print("[X] No stories found: the night run would ignore this file.\n")
        print(FORMAT_HELP)
        return 1

    problems = 0
    used = set()
    merged, report = merge_editor_brief(md, "", date, MAX_EPISODE_STORIES)
    episode_heads = {s["headline"] for s in parse_markdown_prompt(merged)["stories"]}

    for i, s in enumerate(stories, 1):
        body = " ".join(l.strip() for l in s["lines"][1:]
                        if l.strip() and not l.strip().lower().startswith(("source:", "also:", "http", "lead:")))
        words = len(body.split())
        notes = []
        if not s["source"]:
            notes.append("no 'Source:' line")
        if not s["primary_url"]:
            notes.append("no link: add the article URL on the Source line")
        if is_stock_market_story(s["headline"]):
            notes.append("stock-market headline: not covered")
        if is_personal_scandal_story(s["headline"]):
            notes.append("personal lawsuit / scandal / celebrity: not AI news")
        if is_election_story(s["headline"], body):
            notes.append("mentions elections or US politicians: not covered (YouTube blocks promotion)")
        if words < 60:
            notes.append(f"only {words} words (aim for 100-140 for ~50-60 seconds)")
        if i > MAX_EPISODE_STORIES:
            notes.append(f"over the {MAX_EPISODE_STORIES}-story limit: left out")
        # The builder rewrites headlines for speech ("$250 million" -> "250 million dollars").
        dropped = clean_text_for_broadcast(s["headline"]) not in episode_heads and i <= MAX_EPISODE_STORIES
        if dropped and not notes:
            notes.append("would be left out (duplicate of another story or no proper link)")
        status = "LEAD" if i == 1 else ("DROP" if dropped or i > MAX_EPISODE_STORIES else "ok")
        if status != "DROP":
            used.add(s["headline"])
        flag = "" if not notes else "  <-- " + "; ".join(notes)
        print(f"{i:2d}. [{status:4s}] {s['region']:6s} {s['headline'][:70]}  ({words} words){flag}")
        if dropped or not s["primary_url"]:
            problems += 1

    print()
    n = len(episode_heads)
    if n == 0:
        print("[X] None of these stories can be used.\n")
        print(FORMAT_HELP)
        return 1
    print(f"Lead story (opens the episode and becomes the Short): {stories[0]['headline']}")
    print(f"{n} of your stories will be used.", end=" ")
    if n < MIN_EPISODE_STORIES:
        print(f"The night run adds collected stories to reach {MIN_EPISODE_STORIES}-{MAX_EPISODE_STORIES}.")
    else:
        print("That fills the episode.")
    if problems:
        print(f"\n[!] {problems} story/stories need attention (see the arrows above).")
        return 1
    print("\nOK: ready for tonight's run.")
    return 0


if __name__ == "__main__":
    sys.exit(check(sys.argv[1] if len(sys.argv) > 1 else default_date()))
