"""
PromptWriter - SanMitra AI News Wire
Writes the crew's verified stories as prompts/<date>.md in the same approved
format the nightly collector and human editors use (headline, Source:, URL,
Also:, body). build_episode_from_prompt.py turns it into the episode, and
validate_episode_sources.py checks the episode against it.
"""

from datetime import datetime
import logging
import os

logger = logging.getLogger("PromptWriter")

BUREAUS = ["WORLD", "USA", "CHINA", "ASIA", "INDIA"]


def render_prompt(stories, target_date):
    date_display = datetime.strptime(target_date, "%Y-%m-%d").strftime("%A, %d %B %Y")
    lines = [
        "# SanMitra AI News Wire",
        "",
        f"## Daily AI Brief — {date_display} (IST)",
        "",
        "Auto-drafted by the crew from extracted article text. Every headline figure and name "
        "was checked against the linked article. Only items with a named outlet are included.",
        "",
        "---",
        "",
    ]
    for bureau in BUREAUS:
        in_bureau = [s for s in stories if s.get("region") == bureau]
        if not in_bureau:
            continue
        lines += [f"# {bureau}", ""]
        for s in in_bureau:
            lines.append(f"### {s['title']}")
            lines.append(f"Source: {s['source']}")
            lines.append(s["sourceUrl"])
            for extra in s.get("also", [])[:2]:
                lines.append(f"Also: {extra['source']} {extra['url']}")
            lines += ["", s["summary"], ""]
        lines += ["---", ""]
    return "\n".join(lines)


def write_prompt(stories, target_date, prompts_dir="prompts"):
    """Write prompts/<date>.md. Never overwrites an existing (approved) prompt."""
    os.makedirs(prompts_dir, exist_ok=True)
    path = os.path.join(prompts_dir, f"{target_date}.md")
    if os.path.exists(path):
        logger.info(f"Prompt already exists, leaving it unchanged: {path}")
        return path
    with open(path, "w", encoding="utf-8") as f:
        f.write(render_prompt(stories, target_date))
    logger.info(f"Crew prompt written: {path} ({len(stories)} stories)")
    return path
