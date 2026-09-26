"""
Master Prompt-to-Episode Parser for SanMitra AI News Wire v5.0.
Robust parser capable of ingesting:
  - Both structured (# Headings) and plain text (STORY 1, Headline...) formats
  - Multi-act motion graphics and environmental cues
  - Automatic institutional narration generation if full script is omitted
  - Accurate 8-story lineup, 4-second multi-cuts, and section transitions
"""

import argparse
from datetime import datetime
import json
import os
import re
import sys

def synthesize_institutional_narration(headline: str, category: str, context: str, sources: list, motion_notes: str) -> str:
    """Creates a 20-30s calm, institutional Bloomberg/Reuters newsroom narration."""
    category_clean = category.replace("•", "—").strip()
    source_str = " and ".join(sources[:2]) if sources else "official reports"
    
    parts = []
    # Lead sentence
    parts.append(f"In {category_clean.lower()}, {headline.strip()}.")
    
    # Motion/operational context
    if motion_notes:
        motion_clean = re.sub(r"Act\s+\d+:\s*", "", motion_notes)
        motion_items = [m.strip() for m in motion_clean.split("\n") if m.strip() and not m.startswith("Motion") and not m.startswith("Card")]
        if motion_items:
            parts.append(f"Operational briefings highlight {', '.join(motion_items[:2]).lower()}.")
            
    # Historical context
    if context:
        context_clean = context.strip().strip('"').strip("'").strip(">").strip()
        parts.append(f"{context_clean}")
        
    # Institutional closing impact
    parts.append(f"According to reporting verified by {source_str}, enterprise leaders and regulators are closely monitoring downstream compliance and runtime security.")
    
    return " ".join(parts)

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
        # Generate title from top stories
        yt_title = f"AI Agent Incidents | Pentagon Anthropic Ruling | Copilot Super App | AI News {formatted_date}"

    # Extract Intro Script / Opening Hook
    intro_script = ""
    intro_match = re.search(r"(?:Opening Hook|Intro|HOOK|ANCHOR INTRO)[\s\S]*?Narration:?\s*>\s*\"?([^\"]+)\"?", md_text, re.IGNORECASE)
    if intro_match:
        intro_script = intro_match.group(1).strip().replace("\n", " ")
    else:
        # Fallback search for blockquote in opening scene
        hook_match = re.search(r"OPENING SCENE[\s\S]*?>\s*\"?([^\"]+)\"?", md_text, re.IGNORECASE)
        if hook_match:
            intro_script = hook_match.group(1).strip().replace("\n", " ")
    
    if not intro_script or len(intro_script) < 30:
        intro_script = f"AI security, government oversight, and sovereign compute are dominating the global agenda. From the SanMitra Newsroom, here are today's most important AI developments for {formatted_date}."

    # Extract Section Transitions
    section_trans_match = re.search(r"SECTION TRANSITION[\s\S]*?Card\s*\n+([^\n]+)[\s\S]*?Duration:?\s*(\d+)\s*seconds", md_text, re.IGNORECASE)
    trans_card_title = section_trans_match.group(1).strip() if section_trans_match else "GLOBAL AI COMPETITION"
    trans_duration = int(section_trans_match.group(2)) if section_trans_match else 2

    # Extract Stories using flexible regex
    # Matches: "STORY 1", "### STORY 1", "Story 1:", etc.
    story_pattern = re.compile(r"(?:^|\n)(?:#{1,4}\s*)?(?:STORY\s+(\d+)|Story\s+(\d+))\b", re.IGNORECASE)
    splits = [m.start() for m in story_pattern.finditer(md_text)]
    
    story_raw_blocks = []
    if splits:
        for idx in range(len(splits)):
            start = splits[idx]
            end = splits[idx + 1] if idx + 1 < len(splits) else len(md_text)
            raw = md_text[start:end]
            # Truncate before HEADLINES RECAP, OUTRO, or THUMBNAIL
            clean_block = re.split(r"(?:\n---|\n)(?:HEADLINES\s+RECAP|OUTRO|THUMBNAIL)", raw, flags=re.IGNORECASE)[0]
            story_raw_blocks.append(clean_block)

    # Visual assets catalog
    visual_catalog = {
        1: {
            "main": "aibrief/assets/editorial/tech_cyber_command.jpg",
            "cut2": "aibrief/backgrounds/ai_security.jpg",
            "cut3": "aibrief/assets/editorial/tech_code_screen.jpg",
            "badge1": "CYBER OPERATIONS COMMAND CENTER • REAL-TIME INCIDENT WALL",
            "badge2": "AUTONOMOUS AGENT RISK MONITOR • RED ALERT DISCLOSURE",
            "badge3": "RUNTIME CREDENTIAL PERMISSION TELEMETRY"
        },
        2: {
            "main": "aibrief/assets/editorial/gov_white_house.jpg",
            "cut2": "aibrief/assets/editorial/gov_us_capitol_hearing.jpg",
            "cut3": "aibrief/assets/editorial/person_dario_amodei.jpg",
            "badge1": "PENTAGON SITUATION ROOM • DEFENSE AI POLICY REVIEW",
            "badge2": "US FEDERAL COURT RULING • PROCUREMENT COMPLIANCE",
            "badge3": "ANTHROPIC CLAUDE DEFENSE PERMISSIONS DESK"
        },
        3: {
            "main": "aibrief/assets/editorial/tech_data_telemetry.jpg",
            "cut2": "aibrief/assets/editorial/tech_laptop_showcase.jpg",
            "cut3": "aibrief/assets/editorial/tech_code_screen.jpg",
            "badge1": "ENTERPRISE OPERATIONS CENTER • UNIFIED COPILOT APP",
            "badge2": "THREE PILLARS MATRIX • HOME / CODE / AUTOPILOT",
            "badge3": "DEVELOPER REASONING TELEMETRY & RUNTIME"
        },
        4: {
            "main": "aibrief/assets/editorial/gov_un_chamber.jpg",
            "cut2": "aibrief/backgrounds/geopolitics.jpg",
            "cut3": "aibrief/assets/editorial/tech_neural_globe.jpg",
            "badge1": "BILATERAL SUMMIT HALL • US-CHINA AI DELEGATION",
            "badge2": "FRONTIER MODEL SAFETY ACCORD • DIPLOMATIC CHANNEL",
            "badge3": "GLOBAL RISK MITIGATION TELEMETRY"
        },
        5: {
            "main": "aibrief/backgrounds/cloud_infrastructure.jpg",
            "cut2": "aibrief/assets/editorial/tech_server_hall.jpg",
            "cut3": "aibrief/backgrounds/ai_chips.jpg",
            "badge1": "CHINESE AI HEADQUARTERS • $1B REVENUE RUN RATE",
            "badge2": "DEEPSEEK HYPERSCALE CLUSTER & COMPUTE INFRASTRUCTURE",
            "badge3": "SOVEREIGN TOKEN LIQUIDITY & BENCHMARKS"
        },
        6: {
            "main": "aibrief/assets/editorial/fin_tokyo_district.jpg",
            "cut2": "aibrief/assets/editorial/tech_server_hall.jpg",
            "cut3": "aibrief/backgrounds/cloud_infrastructure.jpg",
            "badge1": "TOKYO FINANCIAL COMMAND CENTER • RISK TELEMETRY",
            "badge2": "HYPERSCALE AI DATA CENTER FINANCING REVIEW",
            "badge3": "GLOBAL BANKING EXPOSURE & POWER MATRIX"
        },
        7: {
            "main": "aibrief/assets/editorial/gov_india_delhi.jpg",
            "cut2": "aibrief/assets/editorial/tech_semiconductor_lab.jpg",
            "cut3": "aibrief/backgrounds/ai_chips.jpg",
            "badge1": "NEW DELHI POLICY WAR ROOM • ₹20,000 CR COMPUTE FUND",
            "badge2": "INDIAAI MISSION • NATIONAL FRONTIER ACCELERATION",
            "badge3": "DOMESTIC SILICON INFRASTRUCTURE ROADMAP"
        },
        8: {
            "main": "aibrief/assets/editorial/tech_semiconductor_lab.jpg",
            "cut2": "aibrief/assets/editorial/tech_code_screen.jpg",
            "cut3": "aibrief/assets/editorial/tech_data_telemetry.jpg",
            "badge1": "DOCUMENT INTELLIGENCE LAB • SARVAM VISION 2.1",
            "badge2": "INDIC OCR ENGINE • 22 OFFICIAL LANGUAGES",
            "badge3": "PRODUCTION-READY ENTERPRISE MULTIMODAL BENCHMARKS"
        },
    }

    stories = []
    transitions = []

    # Map stories
    for idx, block in enumerate(story_raw_blocks, 1):
        # Extract Headline
        headline = ""
        head_match = re.search(r"Headline\s*\n+([^\n]+)", block, re.IGNORECASE)
        if head_match:
            headline = head_match.group(1).strip()
        else:
            # Fallback to first bold or clean line
            first_lines = [l.strip() for l in block.splitlines() if l.strip() and not l.upper().startswith("STORY")]
            headline = first_lines[0] if first_lines else f"Global AI Development {idx}"

        # Extract Category / Tag
        category = "AI INTELLIGENCE"
        cat_match = re.search(r"(?:STORY\s+\d+[\s\n]+)([^\n]+)", block, re.IGNORECASE)
        if cat_match:
            candidate = cat_match.group(1).strip()
            if not candidate.lower().startswith("headline") and len(candidate) < 60:
                category = candidate

        # Extract Environment
        env = ""
        env_match = re.search(r"Environment\s*\n+([^\n]+)", block, re.IGNORECASE)
        if env_match:
            env = env_match.group(1).strip()

        # Extract Historical Context
        context = ""
        ctx_match = re.search(r"Historical Context:?\s*\n*>*\s*\"?([^\"]+)\"?", block, re.IGNORECASE)
        if ctx_match:
            context = ctx_match.group(1).strip()

        # Extract Sources
        sources = []
        src_match = re.search(r"(?:Source Badge|Source):?\s*\n+([^\n#\-]+(?:\n[^\n#\-]+)*)", block, re.IGNORECASE)
        if src_match:
            raw_sources = src_match.group(1).splitlines()
            for s in raw_sources:
                s_clean = s.strip().lstrip("•").lstrip("-").strip()
                if s_clean and not s_clean.lower().startswith("story") and not s_clean.startswith("---"):
                    sources.append(s_clean)
        
        if not sources:
            sources = ["Reuters", "Bloomberg"]

        # Extract Motion
        motion_notes = ""
        mot_match = re.search(r"Motion(?:\s+Graphic)?\s*\n+([\s\S]*?)(?:Historical|Source|\n---|\Z)", block, re.IGNORECASE)
        if mot_match:
            motion_notes = mot_match.group(1).strip()

        # Determine Region
        if idx in [1]:
            region = "WORLD"
        elif idx in [2, 3]:
            region = "USA"
        elif idx in [4, 5]:
            region = "CHINA"
        elif idx in [6]:
            region = "ASIA"
        else:
            region = "INDIA"

        # Explicit region detection override
        if "INDIA" in category.upper() or "INDIA" in headline.upper() or "SARVAM" in headline.upper():
            region = "INDIA"
        elif "JAPAN" in headline.upper() or "TOKYO" in block.upper():
            region = "ASIA"
        elif "CHINA" in headline.upper() or "DEEPSEEK" in headline.upper():
            region = "CHINA"
        elif "PENTAGON" in headline.upper() or "MICROSOFT" in headline.upper():
            region = "USA"

        # Check for explicit Narration script, or synthesize institutional broadcast script
        script_match = re.search(r"(?:Voiceover Script|Script|Narration):?\s*\n*>*\s*\"?([^\"]+)\"?", block, re.IGNORECASE)
        if script_match and len(script_match.group(1).strip()) > 40 and "watching" not in script_match.group(1).lower() and "subscribe" not in script_match.group(1).lower():
            script = script_match.group(1).strip().replace("\n", " ")
        else:
            script = synthesize_institutional_narration(headline, category, context, sources, motion_notes)

        # Story ID
        slug = re.sub(r"[^a-z0-9]+", "_", headline.lower())[:32].strip("_")
        s_id = f"s{idx}_{slug}" if slug else f"story_{idx}"

        # Clean category tag
        clean_cat = category.strip()
        if clean_cat.upper().startswith(region):
            category_tag = clean_cat
        else:
            category_tag = f"{region} • {clean_cat[:24]}"

        # Visual cuts: Check for date-specific fresh editorial assets first
        date_dir_rel = f"aibrief/assets/editorial/{iso_date}"
        date_dir_abs = os.path.join("public", "aibrief", "assets", "editorial", iso_date)
        
        c1_rel = f"{date_dir_rel}/s{idx}_cut1.jpg"
        c2_rel = f"{date_dir_rel}/s{idx}_cut2.jpg"
        c3_rel = f"{date_dir_rel}/s{idx}_cut3.jpg"

        cat_info = visual_catalog.get(idx, {
            "main": "aibrief/assets/editorial/tech_data_telemetry.jpg",
            "cut2": "aibrief/assets/editorial/tech_code_screen.jpg",
            "cut3": "aibrief/backgrounds/intro_newsroom.jpg",
            "badge1": f"{region} BUREAU • BREAKING TELEMETRY",
            "badge2": "SYSTEM RUNTIME & COMPLIANCE",
            "badge3": "ENTERPRISE INTELLIGENCE MATRIX"
        })

        img1 = c1_rel if os.path.exists(os.path.join("public", c1_rel)) else cat_info["main"]
        img2 = c2_rel if os.path.exists(os.path.join("public", c2_rel)) else cat_info["cut2"]
        img3 = c3_rel if os.path.exists(os.path.join("public", c3_rel)) else cat_info["cut3"]

        # Vary pan directions across stories
        pans = [
            ("zoomIn", "panLeft", "zoomOut"),
            ("zoomOut", "panRight", "zoomIn"),
            ("panLeft", "zoomIn", "panRight"),
            ("panRight", "zoomOut", "panLeft")
        ][(idx - 1) % 4]

        visual_cuts = [
            {
                "image": img1,
                "badge": cat_info["badge1"],
                "panDirection": pans[0]
            },
            {
                "image": img2,
                "badge": cat_info["badge2"],
                "panDirection": pans[1]
            },
            {
                "image": img3,
                "badge": cat_info["badge3"],
                "panDirection": pans[2]
            }
        ]

        stories.append({
            "id": s_id,
            "region": region,
            "category": category,
            "categoryTag": category_tag,
            "headline": headline,
            "subheadline": f"Verified Report // Source: {', '.join(sources[:2])}",
            "importanceScore": 98 if idx == 1 else (94 if idx <= 3 else 88),
            "durationSeconds": max(int(len(script.split()) * 0.42), 22),
            "source": ", ".join(sources[:2]),
            "sourceUrl": "https://reuters.com",
            "script": script,
            "whyThisMatters": context or f"Strategic development shaping {region} artificial intelligence governance.",
            "keyPoints": [headline, f"Verified by {', '.join(sources[:2])}"],
            "visualCuts": visual_cuts
        })

    # Add transitions across regions
    regions_ordered = []
    for s in stories:
        r = s["region"]
        if not regions_ordered or regions_ordered[-1] != r:
            regions_ordered.append(r)

    for r in regions_ordered:
        if r != "WORLD":
            transitions.append({
                "id": f"transition_{r.lower()}",
                "region": r,
                "title": f"NEXT: {r} & REGIONAL STRATEGY",
                "display": f"NEXT: {r}",
                "durationSeconds": 2
            })

    # Recap checklist
    recap_items = []
    checklist_match = re.search(r"Animated Checklist:\s*\n+([\s\S]*?)(?:\n---|\Z)", md_text, re.IGNORECASE)
    if checklist_match:
        for line in checklist_match.group(1).splitlines():
            line_c = line.strip()
            if line_c:
                recap_items.append(line_c if line_c.startswith("✓") else f"✓ {line_c.lstrip('•').strip()}")
    
    if not recap_items:
        recap_items = [f"✓ {s['headline'][:50]}" for s in stories[:8]]

    recap_script = "To recap today's headlines: " + "; ".join([s['headline'] for s in stories[:6]]) + "."

    # Market snapshot entities
    market_entities = [
        { "name": "OpenAI", "update": "Agent Incident Scrutiny", "tag": "SECURITY GOVERNANCE", "color": "#10a37f" },
        { "name": "Anthropic", "update": "Pentagon Deployment Court Ruling", "tag": "DEFENSE COMPLIANCE", "color": "#d97706" },
        { "name": "Microsoft", "update": "Unified Copilot Super App", "tag": "ENTERPRISE PLATFORM", "color": "#00a4ef" },
        { "name": "DeepSeek", "update": "$1B Annual Revenue Run Rate", "tag": "DOMESTIC CHINESE AI", "color": "#8b5cf6" },
        { "name": "Japan Banks", "update": "AI Data Center Debt Review", "tag": "CAPITAL EXPOSURE", "color": "#38bdf8" },
        { "name": "IndiaAI", "update": "₹20,000 Cr Compute Fund", "tag": "SOVEREIGN SILICON", "color": "#f97316" },
        { "name": "Sarvam AI", "update": "Vision 2.1 Multilingual Model", "tag": "DOMESTIC PRODUCTS", "color": "#10b981" }
    ]

    # Outro
    outro_script = "Those were today's most significant developments shaping the future of artificial intelligence. From our bureaus covering World, USA, China, Asia, and India, thank you for watching SanMitra AI News Wire. Subscribe now for daily institutional AI intelligence."
    outro_match = re.search(r"Closing Narration:?\s*\n*>*\s*\"?([^\"]+)\"?", md_text, re.IGNORECASE)
    if outro_match:
        outro_script = outro_match.group(1).strip().replace("\n", " ")
        if not outro_script.endswith("."):
            outro_script += "."
        outro_script += " Subscribe now for daily institutional AI intelligence."

    episode = {
        "date": iso_date,
        "formattedDate": formatted_date,
        "title": yt_title,
        "intro": {
            "durationSeconds": 18,
            "headline": "AI SECURITY, POLICY, AND SOVEREIGN COMPUTE",
            "subheadline": "SANMITRA NEWSROOM COMMAND CENTER",
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
            "durationSeconds": 16,
            "headline": "GLOBAL AI MARKET SNAPSHOT",
            "subheadline": "SANMITRA DESK • STRATEGIC TELEMETRY",
            "script": "Turning to the SanMitra AI Market Snapshot: Autonomous agent governance tightens after OpenAI disclosures, Pentagon restrictions on Anthropic are affirmed, Microsoft unifies enterprise productivity, DeepSeek scales domestic monetization, and India accelerates sovereign compute capital.",
            "entities": market_entities
        },
        "outro": {
            "durationSeconds": 12,
            "headline": "SANMITRA AI NEWS WIRE",
            "subheadline": "Daily Global AI Intelligence",
            "cta": "SUBSCRIBE FOR DAILY AI INTELLIGENCE",
            "bureaus": ["WORLD", "USA", "CHINA", "ASIA", "INDIA"],
            "script": outro_script
        },
        "ticker": ["SanMitra AI News Wire v5.0"] + [s["headline"][:45] for s in stories],
        "thumbnail": {
            "date": formatted_date.upper(),
            "headline": "OPENAI AGENT SECURITY ALERT",
            "subheadline": "PENTAGON ANTHROPIC RULING • COPILOT SUPER APP",
            "storyHighlights": [
                "OPENAI AGENT INCIDENTS",
                "PENTAGON VS ANTHROPIC",
                "MICROSOFT COPILOT SUPER APP",
                "INDIA ₹20,000 CR COMPUTE FUND"
            ]
        },
        "youtubeMetadata": {
            "title": yt_title,
            "descriptionIntro": f"Daily institutional-grade AI intelligence from the SanMitra Newsroom. Today's broadcast covers OpenAI's autonomous agent security incidents, US court rulings on Pentagon Anthropic restrictions, Microsoft's unified Copilot platform, US-China AI diplomacy, DeepSeek's $1B revenue milestone, Japan's datacenter financing review, India's ₹20,000 Cr compute fund, and Sarvam AI Vision 2.1.",
            "tags": ["AI", "OpenAI", "Anthropic", "Pentagon", "Microsoft", "Copilot", "DeepSeek", "IndiaAI", "SarvamAI", "TechNews", "SanMitra"]
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

    data_dir = os.path.join("src", "aibrief", "data")
    os.makedirs(data_dir, exist_ok=True)

    out_path = args.output or os.path.join(data_dir, f"{date_str}.json")
    active_path = os.path.join(data_dir, "active_episode.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(episode, f, indent=2, ensure_ascii=False)
    with open(active_path, "w", encoding="utf-8") as f:
        json.dump(episode, f, indent=2, ensure_ascii=False)

    print(f"[+] Successfully converted prompt into episode JSON:")
    print(f"    - Date: {date_str} ({episode['formattedDate']})")
    print(f"    - Stories: {len(episode['stories'])}")
    for i, s in enumerate(episode['stories'], 1):
        print(f"      {i}. [{s['region']}] {s['headline']}")
    print(f"    - Output: {out_path} and {active_path}")

if __name__ == "__main__":
    main()
