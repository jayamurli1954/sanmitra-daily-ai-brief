"""
Sunday weekly round-up: the week's biggest AI stories as Sunday's brief.

    python weekly_roundup.py --date 2026-10-18

Reads the episodes that aired Monday-Saturday before the given Sunday
(src/aibrief/data/aired/<date>.json, saved by run_autonomous_brief.py after each
upload), groups the same event across days, ranks the events, and writes
prompts/<sunday>.md in the usual brief format. The nightly crew then builds,
voices and renders it like any other day (the editor's own brief, if any, still
goes first).

Ranking, from what the pipeline actually knows about each story:
  - days it ran      (a story that kept developing is a big story)  x3
  - days it led      (the editor's or the collector's top pick)      x2
  - recency          (Saturday 1.0 ... Monday 0.5)
"""

import argparse
import glob
import json
import os
import re
from datetime import datetime, timedelta

from src.aibrief.crew.editor_brief import parse_stories
from src.aibrief.crew.fact_checker import MAX_EPISODE_STORIES
from src.aibrief.crew.text_utils import is_stock_market_story, same_event
from src.aibrief.generate_linkedin_article import clean_summary

AIRED_DIR = os.path.join("src", "aibrief", "data", "aired")
REGION_ORDER = ["WORLD", "USA", "CHINA", "ASIA", "INDIA"]


def week_dates(sunday: str) -> list:
    day = datetime.strptime(sunday, "%Y-%m-%d")
    return [(day - timedelta(days=n)).strftime("%Y-%m-%d") for n in range(6, 0, -1)]  # Mon..Sat


def _brief_bodies(date: str) -> dict:
    """headline -> (summary text, Source/Also/URL lines) from that day's brief."""
    path = os.path.join("prompts", f"{date}.md")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        stories = parse_stories(f.read())
    out = {}
    for s in stories:
        meta = [l for l in s["lines"][1:] if l.strip().lower().startswith(("source:", "also:", "http"))]
        body = " ".join(l.strip() for l in s["lines"][1:]
                        if l.strip() and not l.strip().lower().startswith(("source:", "also:", "http", "lead:")))
        out[s["headline"]] = (body, meta)
    return out


def load_week(sunday: str) -> list:
    """Every story that aired that week, with the date and whether it led."""
    rows = []
    for date in week_dates(sunday):
        path = os.path.join(AIRED_DIR, f"{date}.json")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            episode = json.load(f)
        bodies = _brief_bodies(date)
        for i, s in enumerate(episode.get("stories", [])):
            # The no-stock-market rule (2026-10-14) applies to stories that aired before it.
            if is_stock_market_story(s["headline"]):
                continue
            body, meta = bodies.get(s["headline"], ("", []))
            rows.append({
                "date": date,
                "led": i == 0,
                "pos": i,
                "headline": s["headline"],
                "region": (s.get("region") or "WORLD").upper(),
                "summary": body or clean_summary(s.get("script", "")),
                "meta": meta or [f"Source: {s.get('source', '')}", s.get("sourceUrl", "")],
            })
    return rows


def rank_events(rows: list, sunday: str) -> list:
    """Group the same event across days and rank the groups."""
    events = []
    for row in rows:
        for ev in events:
            if any(same_event(row["headline"], r["headline"]) for r in ev):
                ev.append(row)
                break
        else:
            events.append([row])

    dates = week_dates(sunday)

    def score(ev):
        days = {r["date"] for r in ev}
        latest = max(dates.index(d) for d in days)
        # Earlier in its episode means the editor/collector ranked it higher.
        return 3 * len(days) + 2 * sum(r["led"] for r in ev) + 0.1 * latest - 0.01 * min(r["pos"] for r in ev)

    ranked = sorted(events, key=score, reverse=True)
    # Each event is told through its latest development.
    return [max(ev, key=lambda r: r["date"]) | {"days": len({r["date"] for r in ev})} for ev in ranked]


# One-day stories per day, so the round-up covers the whole week rather than
# Saturday's episode; stories that ran on several days are not limited.
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
    # Thin week (few aired days): fill from the rest in rank order.
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
        f"The week's biggest AI stories, {first.strftime('%d %B')} to {(day - timedelta(days=1)).strftime('%d %B %Y')}, "
        "ranked by how many days they ran and whether they led. Each story is told through its latest development.",
    ]
    lead = top[0]["headline"] if top else None
    for region in REGION_ORDER + sorted({s["region"] for s in top} - set(REGION_ORDER)):
        group = [s for s in top if s["region"] == region]
        if not group:
            continue
        lines += ["", "---", "", f"# {region}"]
        for s in group:
            lines += ["", f"### {s['headline']}"]
            if s["headline"] == lead:
                lines.append("Lead: yes")
            lines += [m for m in s["meta"] if m] + ["", s["summary"]]
    return "\n".join(lines) + "\n"


def build_weekly_prompt(sunday: str, max_stories: int = MAX_EPISODE_STORIES) -> str:
    rows = load_week(sunday)
    if not rows:
        raise SystemExit(f"[X] No aired episodes found in {AIRED_DIR} for the week before {sunday}.")
    top = pick_across_week(rank_events(rows, sunday), max_stories)
    path = os.path.join("prompts", f"{sunday}.md")
    os.makedirs("prompts", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(render_weekly_prompt(top, sunday))
    print(f"[+] Weekly round-up: {len(rows)} aired stories over {len({r['date'] for r in rows})} days -> {path}")
    for i, s in enumerate(top, 1):
        print(f"    {i}. ({s['days']} day{'s' if s['days'] > 1 else ''}) {s['headline'][:80]}")
    return path


def is_weekly_brief(markdown: str) -> bool:
    return bool(re.search(r"(?im)^##\s*Weekly Round-up", markdown or ""))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write Sunday's weekly round-up brief")
    parser.add_argument("--date", required=True, help="The Sunday it airs (YYYY-MM-DD)")
    args = parser.parse_args()
    build_weekly_prompt(args.date)
