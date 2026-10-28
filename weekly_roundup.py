"""
Sunday weekly round-up: the week's important AI stories that did NOT air.

    python weekly_roundup.py --date 2026-10-18

The daily episodes hold 8-9 stories, so every day good stories are left out for
length. Sunday picks the biggest of those, so nothing in the round-up repeats a
story viewers already heard that week.

Candidates, for each day Monday-Saturday before the Sunday:
  - the editor's brief           prompts/editor/<date>.md
  - the collector's harvest      out/aibrief/logs/prompt_<date>_before_editor_merge.md
  - the day's merged brief       prompts/<date>.md
Anything that aired in the seven days before the Sunday
(src/aibrief/data/aired/<date>.json) is dropped, as are stock-market and election stories
and stories without a proper article link.

The same event found on several days is told once, through its latest
development, and ranked by:
  - days it was in the news      x3  (a story that kept developing is a big story)
  - picked by the editor         x2
  - news value                   (impact_scoring: policy, market, research weight and source authority)
  - recency and position in that day's brief (earlier = ranked higher that day)

Writes prompts/<sunday>.md in the usual brief format. The nightly crew then
builds, voices and renders it like any other day (the editor's own Sunday
brief, if any, still goes first).
"""

import argparse
import json
import os
import re
from datetime import datetime, timedelta

from src.aibrief.crew.fact_checker import MAX_EPISODE_STORIES
from src.aibrief.crew.editor_brief import _same_story, _summary, parse_stories
from src.aibrief.crew.text_utils import is_election_story, is_personal_scandal_story, is_stock_market_story
from src.aibrief.impact_scoring import score_story_impact
from validate_episode_sources import is_proper_article_url

AIRED_DIR = os.path.join("src", "aibrief", "data", "aired")
EDITOR_DIR = os.path.join("prompts", "editor")
HARVEST_LOG = os.path.join("out", "aibrief", "logs", "prompt_{date}_before_editor_merge.md")
REGION_ORDER = ["WORLD", "USA", "CHINA", "ASIA", "INDIA"]


def week_dates(sunday: str) -> list:
    day = datetime.strptime(sunday, "%Y-%m-%d")
    return [(day - timedelta(days=n)).strftime("%Y-%m-%d") for n in range(6, 0, -1)]  # Mon..Sat


def _aired_dates(sunday: str) -> list:
    day = datetime.strptime(sunday, "%Y-%m-%d")
    return [(day - timedelta(days=n)).strftime("%Y-%m-%d") for n in range(7, 0, -1)]  # last Sun..Sat


def load_aired(sunday: str) -> list:
    """Stories that aired in the seven days before the Sunday, shaped like parsed brief stories."""
    aired = []
    for date in _aired_dates(sunday):
        path = os.path.join(AIRED_DIR, f"{date}.json")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            episode = json.load(f)
        for s in episode.get("stories", []):
            url = s.get("sourceUrl", "")
            aired.append({"headline": s.get("headline", ""), "lines": ["### " + s.get("headline", ""), s.get("script", "")],
                          "urls": {url} if url else set(), "date": date})
    return aired


def _candidate_files(date: str) -> list:
    return [
        (os.path.join(EDITOR_DIR, f"{date}.md"), True),
        (HARVEST_LOG.format(date=date), False),
        (os.path.join("prompts", f"{date}.md"), False),
    ]


def load_candidates(sunday: str) -> list:
    """Every story offered for Monday-Saturday, with its day, position and whether the editor chose it."""
    rows = []
    for date in week_dates(sunday):
        for path, editor in _candidate_files(date):
            if not os.path.exists(path):
                continue
            with open(path, "r", encoding="utf-8") as f:
                stories = parse_stories(f.read())
            for pos, s in enumerate(stories):
                if s["region"] not in REGION_ORDER:
                    s["region"] = "WORLD"
                rows.append(s | {"date": date, "pos": pos, "editor": editor})
    return rows


def unaired(candidates: list, aired: list) -> list:
    keep = []
    for s in candidates:
        if is_stock_market_story(s["headline"], s.get("primary_url", "")) or not is_proper_article_url(s.get("primary_url", "")):
            continue
        if is_election_story(s["headline"], _summary(s)) or is_personal_scandal_story(s["headline"]):
            continue
        if re.search(r"\s\|\s+[A-Z][a-z]+ [A-Z][a-z]+$", s["headline"]):
            continue  # an opinion column ("... | Richard Wilson"), not news
        if any(_same_story(s, a) for a in aired):
            continue
        keep.append(s)
    return keep


def rank_events(rows: list, sunday: str) -> list:
    """Group the same event across days and files, and rank the groups."""
    events = []
    for row in rows:
        for ev in events:
            if any(_same_story(row, r) for r in ev):
                ev.append(row)
                break
        else:
            events.append([row])

    dates = week_dates(sunday)

    def score(ev):
        days = {r["date"] for r in ev}
        latest = max(dates.index(d) for d in days)
        # The pipeline's own news-value score (policy, market, research weight plus source authority), 0-100.
        impact = max(score_story_impact(r["headline"], _summary(r)[:800], r.get("primary_url", ""))["final_rank_score"]
                     for r in ev) / 25
        return (3 * len(days) + 2 * any(r["editor"] for r in ev) + impact
                + 0.1 * latest - 0.02 * min(r["pos"] for r in ev))

    ranked = sorted(events, key=score, reverse=True)
    # Each event is told through its latest development; on the same day the editor's version wins.
    return [max(ev, key=lambda r: (r["date"], r["editor"])) | {"days": len({r["date"] for r in ev})}
            for ev in ranked]


# One-day stories per day, so the round-up covers the whole week rather than
# Saturday's leftovers; stories in the news on several days are not limited.
ONE_DAY_STORIES_PER_DAY = 2


def pick_across_week(ranked: list, max_stories: int) -> list:
    picked, per_day = [], {}
    for s in ranked:
        if len(picked) >= max_stories:
            break
        if s["days"] == 1 and per_day.get(s["date"], 0) >= ONE_DAY_STORIES_PER_DAY:
            continue
        picked.append(s)
        per_day[s["date"]] = per_day.get(s["date"], 0) + 1
    # Thin week: fill from the rest in rank order.
    for s in ranked:
        if len(picked) >= max_stories:
            break
        if s not in picked:
            picked.append(s)
    return picked


def render_weekly_prompt(top: list, sunday: str) -> str:
    day = datetime.strptime(sunday, "%Y-%m-%d")
    first = datetime.strptime(week_dates(sunday)[0], "%Y-%m-%d")
    lines = [
        "# SanMitra AI News Wire",
        "",
        f"## Weekly Round-up — {day.strftime('%A, %d %B %Y')} (IST)",
        "",
        f"Important AI stories from {first.strftime('%d %B')} to {(day - timedelta(days=1)).strftime('%d %B %Y')} "
        "that did not fit in the daily episodes. Nothing here aired earlier in the week.",
    ]
    lead = top[0]["headline"] if top else None
    for region in REGION_ORDER:
        group = [s for s in top if s["region"] == region]
        if not group:
            continue
        lines += ["", "---", "", f"# {region}"]
        for s in group:
            body = [l for l in s["lines"][1:] if not l.strip().lower().startswith("lead:")]
            lines.append("")
            lines.append(s["lines"][0].rstrip())
            if s["headline"] == lead:
                lines.append("Lead: yes")
            lines += body
    return "\n".join(lines) + "\n"


def build_weekly_prompt(sunday: str, max_stories: int = MAX_EPISODE_STORIES):
    aired = load_aired(sunday)
    candidates = load_candidates(sunday)
    fresh = unaired(candidates, aired)
    if not fresh:
        print(f"[!] Weekly round-up: no unaired stories found for the week before {sunday}; "
              "the nightly run will build a normal brief.")
        return None
    top = pick_across_week(rank_events(fresh, sunday), max_stories)
    path = os.path.join("prompts", f"{sunday}.md")
    os.makedirs("prompts", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(render_weekly_prompt(top, sunday))
    print(f"[+] Weekly round-up: {len(candidates)} stories offered this week, {len(aired)} aired, "
          f"{len(fresh)} not aired -> {path}")
    for i, s in enumerate(top, 1):
        print(f"    {i}. ({s['date']}, {s['days']} day{'s' if s['days'] > 1 else ''}"
              f"{', editor' if s['editor'] else ''}) {s['headline'][:80]}")
    return path


def is_weekly_brief(markdown: str) -> bool:
    return bool(re.search(r"(?im)^##\s*Weekly Round-up", markdown or ""))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write Sunday's weekly round-up brief")
    parser.add_argument("--date", required=True, help="The Sunday it airs (YYYY-MM-DD)")
    args = parser.parse_args()
    build_weekly_prompt(args.date)
