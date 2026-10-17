"""
LinkedIn Article & Executive Dispatch Generator for SanMitra AI News Wire & OfficeMitra AI Insights.
Produces long-form, institutional LinkedIn articles matching the official news wire standard:
  1. Executive Header with Date (IST) & Coverage Period
  2. Opening paragraph naming the day's lead stories
  3. Regional Bureaus (🌍 WORLD, 🇺🇸 USA, 🇨🇳 CHINA, 🌏 ASIA, 🇮🇳 INDIA)
  4. 🎯 Today at a glance (each bureau's headlines)
Everything in the article comes from the episode's stories. The intro and
takeaways used to be fixed text naming events that were not in the brief.
  5. Closing CTA & Institutional Hashtags
"""

import argparse
from datetime import datetime, timedelta
import json
import os
import re
import sys
from typing import Dict, List, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# Lead-in phrases the scriptwriter adds for the spoken broadcast ("Turning to
# India, ..."). They read as filler in print and are often wrong out of context.
_LEAD_IN = re.compile(
    r"^(?:In our lead story today|In another major development|In concurrent industry updates|"
    r"Expanding on [^,]{1,40}|In enterprise infrastructure|Meanwhile(?: in [^,]{1,25})?|"
    r"Turning to [^,]{1,30}|Moving to [^,]{1,30}|In (?:Asia|India|China|Europe|the United States)),\s*"
    # Current builder: each transition is its own short sentence.
    r"|^(?:Our lead story today|Turning to the United States|Turning to India|In China|In Asia|"
    r"Around the world|Also today|In other news|Next|Elsewhere)\.\s+",
    re.IGNORECASE,
)


def clean_summary(text: str) -> str:
    text = _LEAD_IN.sub("", (text or "").strip())
    return text[:1].upper() + text[1:] if text else text


def generate_macro_intro(stories: List[Dict], weekly: bool = False) -> str:
    """Opening paragraph built only from the brief's stories, so it can never cite news that is not in the brief."""
    if not stories:
        return ""
    outlets = sorted({s.get("source", "").strip() for s in stories if s.get("source")})
    regions = [r for r in ["WORLD", "USA", "CHINA", "ASIA", "INDIA"]
               if any(s.get("region", "").upper() == r for s in stories)]
    leads = [s.get("headline", "").strip() for s in stories[:3] if s.get("headline")]
    what = "This week's round-up brings" if weekly else "Today's brief covers"
    intro = (f"{what} {len(stories)} AI stories from {len(outlets)} news outlets, "
             f"across {', '.join(r.title() if r != 'USA' else r for r in regions)}.")
    if leads:
        intro += (" Leading the week: " if weekly else " Leading the day: ") + "; ".join(leads) + "."
    return intro


def generate_key_takeaways(stories: List[Dict], weekly: bool = False) -> str:
    """One line per bureau listing its headlines. No claim appears here that is not a story in the brief."""
    lines = ["🎯 This week at a glance" if weekly else "🎯 Today at a glance", ""]
    for region in ["WORLD", "USA", "CHINA", "ASIA", "INDIA"]:
        heads = [s.get("headline", "").strip() for s in stories if s.get("region", "").upper() == region]
        if heads:
            label = region if region == "USA" else region.title()
            lines.append(f"🔹 {label}: " + "; ".join(heads) + ".")
            lines.append("")
    return "\n".join(lines).rstrip()


CHANNEL_URL = "https://www.youtube.com/@SanMitraTechSolutions"


def build_linkedin_article(
    active_json_path: str = "src/aibrief/data/active_episode.json",
    prompt_md_path: Optional[str] = None,
    output_article_path: str = "out/aibrief/linkedin_article.md",
    output_post_path: str = "out/aibrief/linkedin_post.txt",
    video_url: Optional[str] = None,
    episode: Optional[Dict] = None,
) -> str:
    """video_url (the day's YouTube episode) goes under the opening paragraph, where
    most readers still are; the channel subscribe line closes the article."""
    ep = episode or {}
    if not ep and os.path.exists(active_json_path):
        with open(active_json_path, "r", encoding="utf-8") as f:
            ep = json.load(f)

    date_str = ep.get("date", datetime.now().strftime("%Y-%m-%d"))
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    yesterday_dt = dt - timedelta(days=1)

    today_formatted = dt.strftime("%A, %d %B %Y")
    yesterday_formatted = yesterday_dt.strftime("%A, %d %B %Y")

    # Group stories by bureau
    stories = ep.get("stories", [])
    bureau_map = {
        "WORLD": [],
        "USA": [],
        "CHINA": [],
        "ASIA": [],
        "INDIA": []
    }

    # If prompt markdown exists, extract richer text if available
    for s in stories:
        reg = s.get("region", "WORLD").upper()
        if reg not in bureau_map:
            bureau_map[reg] = []
        bureau_map[reg].append(s)

    weekly = bool(ep.get("weekly"))
    lines = [
        "SanMitra AI News Wire",
        (f"Weekly AI Round-up — {today_formatted} (IST)" if weekly else f"AI Brief — {today_formatted} (IST)"),
        # The Sunday round-up is the week's stories that did not air in the daily episodes (weekly_roundup.py).
        (f"Important AI stories from {(dt - timedelta(days=6)).strftime('%d %B')} to {yesterday_dt.strftime('%d %B %Y')} "
         "that did not make the daily episodes" if weekly else f"Covering {yesterday_formatted}"),
        "",
        generate_macro_intro(stories, weekly),
        ""
    ]
    if video_url:
        lines += [f"▶️ Watch this week's round-up: {video_url}" if weekly else f"▶️ Watch today's video brief: {video_url}", ""]

    bureau_icons = {
        "WORLD": "🌍 WORLD",
        "USA": "🇺🇸 USA",
        "CHINA": "🇨🇳 CHINA",
        "ASIA": "🌏 ASIA",
        "INDIA": "🇮🇳 INDIA"
    }

    for b_key in ["WORLD", "USA", "CHINA", "ASIA", "INDIA"]:
        b_stories = bureau_map.get(b_key, [])
        if not b_stories:
            continue

        lines.append(bureau_icons.get(b_key, f"🌐 {b_key}"))
        lines.append("")

        for st in b_stories:
            head = st.get("headline", "").strip()
            script = st.get("script", "").strip()
            why = st.get("whyThisMatters", "").strip()
            src = st.get("source", "").strip()
            src_url = st.get("sourceUrl", "").strip()

            # The broadcast script is the fuller summary; whyThisMatters is usually
            # its first sentence, so printing both repeated the text.
            summary = clean_summary(script) or clean_summary(why)

            lines.append(head)
            lines.append(summary)
            if src:
                lines.append(f"Source: {src}")
            if src_url:
                lines.append(src_url)
            lines.append("")

    lines.append(generate_key_takeaways(stories, weekly))
    lines.append("")
    lines.append(f"🔔 Get the daily AI brief every morning at 6:30 AM IST. Subscribe on YouTube: {CHANNEL_URL}")
    lines.append("")
    lines.append("#AI #ArtificialIntelligence #AIGovernance #AISafety #AIInfrastructure #ChinaAI #IndiaAI #SanMitraAINewsWire #OfficeMitraAIInsights")

    article_content = "\n".join(lines)

    # Save to both markdown article and social dispatch text file
    os.makedirs(os.path.dirname(output_article_path), exist_ok=True)
    with open(output_article_path, "w", encoding="utf-8") as f:
        f.write(article_content)

    os.makedirs(os.path.dirname(output_post_path), exist_ok=True)
    with open(output_post_path, "w", encoding="utf-8") as f:
        f.write(article_content)

    # Dated copy: the undated files are overwritten by every run.
    dated_path = os.path.join(os.path.dirname(output_article_path), f"linkedin_article_{date_str}.md")
    with open(dated_path, "w", encoding="utf-8") as f:
        f.write(article_content)

    print(f"[+] LinkedIn Article generated: {output_article_path} (dated copy: {dated_path})")
    print(f"[+] LinkedIn Post copy synced: {output_post_path}")
    return article_content


if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(description="Generate official LinkedIn Article from daily AI Brief")
    parser.add_argument("--json", default="src/aibrief/data/active_episode.json", help="Path to active episode JSON")
    parser.add_argument("--video-url", help="The day's YouTube episode, linked under the opening paragraph")
    args = parser.parse_args()

    build_linkedin_article(active_json_path=args.json, video_url=args.video_url)
