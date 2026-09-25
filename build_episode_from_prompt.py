"""
Prompt-to-Episode Parser for SanMitra AI News Wire.
Parses master production prompt markdown into institutional broadcast JSON.
No web scraping required. Reads directly from user-supplied prompt text/file.
"""

import argparse
from datetime import datetime
import json
import os
import re
import sys

def parse_markdown_prompt(md_text: str) -> dict:
    lines = md_text.splitlines()

    # Detect date
    date_match = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(20\d\d)", md_text)
    if date_match:
        day, month_str, year = date_match.groups()
        try:
            dt = datetime.strptime(f"{day} {month_str} {year}", "%d %B %Y")
            formatted_date = dt.strftime("%d %B %Y")
            iso_date = dt.strftime("%Y-%m-%d")
        except Exception:
            formatted_date = f"{day} {month_str} {year}"
            iso_date = datetime.now().strftime("%Y-%m-%d")
    else:
        dt = datetime.now()
        formatted_date = dt.strftime("%d %B %Y")
        iso_date = dt.strftime("%Y-%m-%d")

    # YouTube Title
    title_match = re.search(r"YouTube\s+Title[:\s*]*`?([^`\n]+)`?", md_text, re.IGNORECASE)
    if title_match:
        yt_title = title_match.group(1).strip()
    else:
        yt_title = f"AI News Wire | Daily AI Brief {formatted_date}"

    # Extract Intro Script
    intro_script = ""
    intro_match = re.search(r"(?:Intro|HOOK|ANCHOR INTRO)[:\s*]+([^\n]+(?:\n[^\n#]+)*)", md_text, re.IGNORECASE)
    if intro_match:
        intro_candidate = intro_match.group(1).strip()
        intro_script = " ".join([l.strip() for l in intro_candidate.splitlines() if l.strip() and not l.startswith("#") and not l.startswith("-") and not l.startswith("*")])
    if not intro_script or len(intro_script) < 30:
        intro_script = f"Welcome to the SanMitra AI News Wire for {formatted_date}. Here are today's major artificial intelligence developments from around the world."

    # Extract Stories
    stories = []
    story_blocks = re.split(r"(?:^|\n)##?\s+(?:Story\s+\d+|STORY\s+\d+|Lead Story|LEAD STORY|\d+\.\s+)", md_text)
    
    if len(story_blocks) <= 1:
        # Fallback split on ### Story or bold Story
        story_blocks = re.split(r"(?:^|\n)###?\s+(?:Story\s+\d+|Segment\s+\d+)", md_text)

    # Visual assets catalog
    default_visuals = {
        "WORLD": "aibrief/assets/editorial/gov_canberra_parliament.jpg",
        "USA": "aibrief/assets/editorial/gov_white_house.jpg",
        "CHINA": "aibrief/assets/editorial/tech_laptop_showcase.jpg",
        "ASIA": "aibrief/assets/editorial/fin_tokyo_district.jpg",
        "INDIA": "aibrief/assets/editorial/tech_semiconductor_lab.jpg",
    }

    # Region ordering and transitions
    regions_seen = []
    transitions = []

    story_index = 1
    for block in story_blocks[1:]:
        block_clean = block.strip()
        if not block_clean:
            continue

        # Extract Region
        region = "WORLD"
        for r in ["WORLD", "USA", "CHINA", "ASIA", "INDIA", "GLOBAL"]:
            if re.search(rf"\b{r}\b", block_clean[:100], re.IGNORECASE):
                region = r
                break

        # Extract Headline
        headline = ""
        head_match = re.search(r"Headline[:\s*]+`?([^\n`]+)`?", block_clean, re.IGNORECASE)
        if head_match:
            headline = head_match.group(1).strip()
        else:
            first_line = block_clean.splitlines()[0].strip().lstrip("#").strip()
            headline = re.sub(r"^\d+[\.\)]\s*", "", first_line)

        # Extract Script
        script = ""
        script_match = re.search(r"(?:Voiceover Script|Script|Narration)[:\s*]+([^\n]+(?:\n[^\n#]+)*)", block_clean, re.IGNORECASE)
        if script_match:
            lines_s = [l.strip() for l in script_match.group(1).splitlines() if l.strip() and not l.startswith("#") and not l.startswith("Visual") and not l.startswith("VIP")]
            script = " ".join(lines_s)
        else:
            # Look for paragraph of text
            paras = [p.strip() for p in block_clean.split("\n\n") if len(p.strip()) > 50 and not p.strip().startswith("#")]
            if paras:
                script = paras[0]

        # Extract Source
        source = "Reuters / Bloomberg"
        source_match = re.search(r"Source[:\s*]+`?([^\n`]+)`?", block_clean, re.IGNORECASE)
        if source_match:
            source = source_match.group(1).strip()

        source_url = "https://reuters.com"
        url_match = re.search(r"(https?://[^\s\)]+)", block_clean)
        if url_match:
            source_url = url_match.group(1)

        # Extract Why This Matters / Context
        why_matters = ""
        why_match = re.search(r"(?:Why This Matters|Significance|Impact)[:\s*]+([^\n]+)", block_clean, re.IGNORECASE)
        if why_match:
            why_matters = why_match.group(1).strip()

        # Story ID
        slug = re.sub(r"[^a-z0-9]+", "_", headline.lower())[:35].strip("_")
        s_id = f"s{story_index}_{slug}" if slug else f"story_{story_index}"

        # Visual cuts
        visual_cuts = [
            {
                "image": default_visuals.get(region, "aibrief/backgrounds/intro_newsroom.jpg"),
                "badge": f"{region} BUREAU • BREAKING TELEMETRY",
                "panDirection": "zoomIn"
            },
            {
                "image": "aibrief/assets/editorial/tech_code_screen.jpg",
                "badge": "INFRASTRUCTURE TELEMETRY & RUNTIME",
                "panDirection": "zoomOut"
            },
            {
                "image": "aibrief/backgrounds/ai_chips.jpg",
                "badge": "GLOBAL SILICON & COMPUTE MATRIX",
                "panDirection": "panRight"
            }
        ]

        stories.append({
            "id": s_id,
            "region": region,
            "category": "Artificial Intelligence",
            "categoryTag": f"{region} • INTELLIGENCE",
            "headline": headline,
            "subheadline": f"Verified Report // Source: {source}",
            "importanceScore": 95 if story_index == 1 else 90,
            "durationSeconds": max(int(len(script.split()) * 0.4), 16),
            "source": source,
            "sourceUrl": source_url,
            "script": script,
            "whyThisMatters": why_matters,
            "keyPoints": [headline],
            "visualCuts": visual_cuts
        })

        if region not in regions_seen:
            regions_seen.append(region)
            if len(regions_seen) > 1 and region != "WORLD":
                transitions.append({
                    "id": f"transition_{region.lower()}",
                    "region": region,
                    "title": f"NEXT: {region} & STRATEGIC DEVELOPMENTS",
                    "display": f"NEXT: {region}",
                    "durationSeconds": 2
                })

        story_index += 1

    # Recap
    recap_items = [f"✓ {s['headline'][:60]}" for s in stories[:8]]
    recap_script = "To recap today's headlines: " + "; ".join([s['headline'] for s in stories[:6]]) + "."

    # Market Snapshot
    market_entities = []
    for s in stories[:6]:
        market_entities.append({
            "name": s["headline"].split()[0] if s["headline"] else "AI Global",
            "update": s["headline"][:32],
            "tag": s["region"],
            "color": "#38bdf8"
        })

    episode = {
        "date": iso_date,
        "formattedDate": formatted_date,
        "title": yt_title,
        "intro": {
            "durationSeconds": 18,
            "headline": "DAILY AI INTELLIGENCE BRIEFING",
            "subheadline": "SANMITRA COMMAND CENTER",
            "script": intro_script
        },
        "transitions": transitions,
        "stories": stories,
        "recap": {
            "durationSeconds": 12,
            "headline": "TODAY'S CRITICAL DEVELOPMENTS",
            "script": recap_script,
            "items": recap_items
        },
        "marketSnapshot": {
            "durationSeconds": 15,
            "headline": "GLOBAL AI MARKET SNAPSHOT",
            "subheadline": "SANMITRA DESK • STRATEGIC TELEMETRY",
            "script": "Turning to the SanMitra AI Market Snapshot across enterprise foundation models, sovereign silicon, and compute scaling.",
            "entities": market_entities
        },
        "outro": {
            "durationSeconds": 12,
            "headline": "SANMITRA AI NEWS WIRE",
            "subheadline": "Daily Global AI Intelligence",
            "cta": "Subscribe for daily AI intelligence updates.",
            "bureaus": ["WORLD", "USA", "CHINA", "ASIA", "INDIA"],
            "script": "Those were today's major AI developments from around the world. Subscribe to SanMitra AI News Wire for daily institutional AI coverage."
        },
        "ticker": ["SanMitra AI News Wire"] + [s["headline"][:45] for s in stories],
        "thumbnail": {
            "date": formatted_date.upper(),
            "headline": stories[0]["headline"].upper()[:30] if stories else "BREAKING AI NEWS",
            "subheadline": stories[1]["headline"].upper()[:35] if len(stories) > 1 else "GLOBAL INTELLIGENCE",
            "storyHighlights": [s["headline"][:35] for s in stories[:4]]
        },
        "youtubeMetadata": {
            "title": yt_title,
            "descriptionIntro": f"Daily institutional-grade AI intelligence from the SanMitra Newsroom covering {formatted_date}.",
            "tags": ["AI", "ArtificialIntelligence", "TechNews", "SanMitra", "MachineLearning"]
        }
    }

    return episode

def main():
    parser = argparse.ArgumentParser(description="Build episode from markdown prompt")
    parser.add_argument("prompt_file", help="Path to markdown prompt file")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    if not os.path.exists(args.prompt_file):
        print(f"[X] Prompt file not found: {args.prompt_file}")
        sys.exit(1)

    with open(args.prompt_file, "r", encoding="utf-8") as f:
        md_text = f.read()

    episode = parse_markdown_prompt(md_text)
    date_str = episode["date"]

    out_path = args.output or os.path.join("src", "aibrief", "data", f"{date_str}.json")
    active_path = os.path.join("src", "aibrief", "data", "active_episode.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(episode, f, indent=2, ensure_ascii=False)
    with open(active_path, "w", encoding="utf-8") as f:
        json.dump(episode, f, indent=2, ensure_ascii=False)

    print(f"[+] Successfully converted prompt into episode JSON:")
    print(f"    - Date: {date_str} ({episode['formattedDate']})")
    print(f"    - Stories: {len(episode['stories'])}")
    print(f"    - Output: {out_path} and {active_path}")

if __name__ == "__main__":
    main()
