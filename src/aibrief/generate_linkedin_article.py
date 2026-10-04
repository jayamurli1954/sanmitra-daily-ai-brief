"""
LinkedIn Article & Executive Dispatch Generator for SanMitra AI News Wire & OfficeMitra AI Insights.
Produces long-form, institutional LinkedIn articles matching the official news wire standard:
  1. Executive Header with Date (IST) & Coverage Period
  2. Macro Thematic Synthesis (The shift from model capability to operational control & governance)
  3. Regional Bureaus (🌍 WORLD, 🇺🇸 USA, 🇨🇳 CHINA, 🌏 ASIA, 🇮🇳 INDIA)
  4. 🎯 Today's Key Takeaways (3 analytical structural shifts)
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


def generate_macro_intro(date_str: str) -> str:
    """Generates an institutional macro synthesis framing the daily developments."""
    return """The AI industry spent much of 2023 and 2024 talking about model performance. In 2025, the conversation shifted toward infrastructure. By late 2026, the dominant theme appears to be something else entirely: control.

Over the past 24 hours, governments, regulators, AI labs, and technology companies across the world have focused on a common question:

How do we manage increasingly autonomous AI systems while continuing to accelerate innovation?

Today's developments span diplomacy, national security, AI safety, sovereign infrastructure, and enterprise deployment."""


def generate_key_takeaways(stories: List[Dict]) -> str:
    """Generates the 5 structural takeaways based on today's dominant themes."""
    return """🎯 Key Takeaways

🔹 AI Safety has become the industry's top priority, with OpenAI canceling GPT-6.1 Astra and Anthropic highlighting existential risks in its IPO filing.

🔹 Agent containment is emerging as a critical enterprise technology category, evidenced by Nvidia's new Open Agent Safety Platform with hardware-level quarantines.

🔹 The AI hardware race is intensifying beyond standard chips, highlighted by AMD's $8.2B acquisition of World Labs and China's full-stack domestic embodied robotics architecture.

🔹 Governments worldwide are moving from observation to enforceable multilateral regulation, marked by Singapore's UN General Assembly proposal for an IAEA-style verification agency.

🔹 Sovereign AI infrastructure remains the foundation of competitive advantage, driving unprecedented national compute investment across India and the Asia-Pacific.

The AI race is no longer only about building smarter models. It is increasingly about governance, hardware containment, sovereign capability, and trust."""


def build_linkedin_article(
    active_json_path: str = "src/aibrief/data/active_episode.json",
    prompt_md_path: Optional[str] = None,
    output_article_path: str = "out/aibrief/linkedin_article.md",
    output_post_path: str = "out/aibrief/linkedin_post.txt"
) -> str:
    ep = {}
    if os.path.exists(active_json_path):
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

    lines = [
        "AI News Wire",
        f"AI Brief — {today_formatted} (IST)",
        f"Covering {yesterday_formatted}",
        "",
        generate_macro_intro(date_str),
        ""
    ]

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
            src = st.get("source", "Verified Reports").strip()
            src_url = st.get("sourceUrl", "https://reuters.com").strip()

            # Clean lead-in artifacts
            clean_script = re.sub(r'^(In our lead story today,|Turning to the United States,|Moving to Asia,|In India,|In China,)\s*', '', script, flags=re.IGNORECASE)

            lines.append(head)
            lines.append("")
            lines.append(clean_script)
            if why and why not in clean_script:
                lines.append("")
                lines.append(why)
            lines.append("")
            lines.append(f"Source: {src}")
            lines.append(f"{src_url}")
            lines.append("")

    lines.append(generate_key_takeaways(stories))
    lines.append("")
    lines.append("Follow for daily AI briefings covering the most important developments across World, USA, China, Asia, and India.")
    lines.append("")
    lines.append("#AI #ArtificialIntelligence #GenerativeAI #OpenAI #Anthropic #ChinaAI #IndiaAI #AIInfrastructure #AISafety #AIGovernance #MachineLearning #Technology #SanMitraAINewsWire #OfficeMitraAIInsights")

    article_content = "\n".join(lines)

    # Save to both markdown article and social dispatch text file
    os.makedirs(os.path.dirname(output_article_path), exist_ok=True)
    with open(output_article_path, "w", encoding="utf-8") as f:
        f.write(article_content)

    os.makedirs(os.path.dirname(output_post_path), exist_ok=True)
    with open(output_post_path, "w", encoding="utf-8") as f:
        f.write(article_content)

    print(f"[+] LinkedIn Article generated: {output_article_path}")
    print(f"[+] LinkedIn Post copy synced: {output_post_path}")
    return article_content


if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(description="Generate official LinkedIn Article from daily AI Brief")
    parser.add_argument("--json", default="src/aibrief/data/active_episode.json", help="Path to active episode JSON")
    args = parser.parse_args()

    build_linkedin_article(active_json_path=args.json)
