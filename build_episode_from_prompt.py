"""
Master Prompt-to-Episode Parser for SanMitra AI News Wire v6.0.
Strictly implements broadcast newsroom architecture:
1. Never reads Markdown headings (#, ##, ###).
2. Strips all markdown syntax (**, *, _, [url], etc.) from narration.
3. Never speaks "Story 1", "Story 2", "Item 1", or "Headline 1".
4. Never reads source URLs or raw "Source: Reuters" aloud.
5. Deduplicates similar stories appearing in multiple sections.
6. Converts article format into natural Bloomberg/Reuters broadcast television narration.
7. Employs natural anchor transitions ("In our lead story...", "Meanwhile in China...", "Turning to India...").
8. Each story keeps enough sentences to carry a broadcast of at least five minutes.
9. Avoids repeating on-screen headline verbatim in the narration.
"""

import argparse
from datetime import datetime
import json
import os
import re
import sys

from validate_episode_sources import is_proper_article_url

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def is_metadata_line(line: str) -> bool:
    """Source, Also, Desk, and bare URLs are records. They are not narration."""
    stripped = line.strip().lstrip("*").strip()
    if not stripped:
        return True
    lower = stripped.lower()
    if lower.startswith("http://") or lower.startswith("https://"):
        return True
    if re.match(r"(?i)^(source|also|desk)\s*:?\s+\S", stripped):
        # A leaked join looks like "Desk: ChatGPT and Grok The Prime Minister..."
        # That line still holds the story, so it is cleaned instead of dropped.
        if lower.startswith("desk:") and len(stripped.split()) > 8:
            return False
        return True
    return False


def strip_unspoken_metadata(text: str) -> str:
    """Remove Desk / Source labels from text that will be spoken."""
    if not text:
        return ""
    kept = []
    for line in re.split(r"\r?\n", text):
        stripped = line.strip()
        if not stripped or is_metadata_line(stripped):
            continue
        stripped = re.sub(
            r"(?i)^(?:\*\*)?Desk:\s*(?:ChatGPT and Grok|Scraper)\b\s*",
            "",
            stripped,
        )
        stripped = re.sub(r"(?i)^(?:\*\*)?(?:Source|Also)\s*:\s*", "", stripped)
        if stripped.strip():
            kept.append(stripped.strip())
    text = " ".join(kept)
    text = re.sub(r"(?i)\bDesk:\s*(?:ChatGPT and Grok|Scraper)\b", " ", text)
    return text


def clean_text_for_broadcast(text: str) -> str:
    """Removes markdown artifacts, symbols, and formatting."""
    if not text:
        return ""
    # Convert currency symbols for natural speech
    text = text.replace('₹', ' rupees ')
    text = text.replace('$', ' dollars ')
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove markdown links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove Story/Headline labels
    text = re.sub(r'(?i)\b(?:Story|Headline|Item)\s+\d+[:\-\s]*', '', text)
    # Remove Markdown headers (#, ##, ###)
    text = re.sub(r'#+\s*', '', text)
    # Remove bold/italics
    text = re.sub(r'[*_~`]{1,3}', '', text)
    # Remove bullets/symbols
    text = re.sub(r'[✓•👉📌🔹🌐🔴💬🔔💡—–]', ' ', text)
    # Clean whitespace
    text = re.sub(r'(?i)\bpasted text\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def deduplicate_stories(raw_stories: list) -> list:
    """Removes duplicate stories covering the same event across different regions."""
    unique_stories = []
    seen_signatures = []

    for story in raw_stories:
        head = story["headline"].lower()
        # Extract meaningful keywords (> 4 chars)
        words = set(re.findall(r'[a-z]{4,}', head))
        # Remove common filler words
        words = words - {"launch", "formal", "major", "after", "takes", "center", "stage", "expands", "unveils"}
        
        is_duplicate = False
        for seen in seen_signatures:
            # Overlap threshold
            intersection = words & seen
            # Two shared words is not enough. "Meta" and "Muse" appear in
            # separate stories (research papers, and a hardware kit).
            if len(intersection) >= 3 or (len(words) > 0 and len(intersection) / len(words) > 0.5):
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_stories.append(story)
            if words:
                seen_signatures.append(words)

    return unique_stories

def format_broadcast_narration(idx: int, region: str, headline: str, body: str, prev_region: str = None) -> str:
    """Converts a raw news story into a calm, professional Bloomberg/Reuters broadcast delivery."""
    # Clean body of source attributions and the research-desk label.
    # Desk is stored on the episode. It is never spoken.
    cleaned_body = strip_unspoken_metadata(body)
    cleaned_body = re.sub(r'(?i)\bSource:\s*[^\n]*', '', cleaned_body)
    cleaned_body = cleaned_body.replace("U.S.", "US")
    cleaned_body = re.sub(r'(?i)\bAlso:?[^\n\.\;]*', '', cleaned_body)
    cleaned_body = clean_text_for_broadcast(cleaned_body)
    clean_head = clean_text_for_broadcast(headline)

    # Split into clean sentences
    raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned_body) if len(s.strip()) > 15]

    # Deduplicate body if it begins by repeating the exact headline
    filtered_sentences = []
    for s in raw_sentences:
        head_words = set(re.findall(r'[a-z]{4,}', clean_head.lower()))
        s_words = set(re.findall(r'[a-z]{4,}', s.lower()))
        # If sentence is virtually identical to headline, skip or rephrase
        if len(head_words) > 3 and len(s.split()) <= len(clean_head.split()) + 3 and len(head_words & s_words) / len(head_words) > 0.75:
            continue
        filtered_sentences.append(s)

    kept = []
    for sentence in filtered_sentences:
        kept.append(sentence)
        if len(kept) >= 6 or len(" ".join(kept).split()) >= 110:
            break
    content = " ".join(kept) if kept else cleaned_body[:700]

    # Generate natural broadcast anchor transitions
    transition = ""
    if idx == 1:
        transition = "In our lead story today,"
    elif prev_region and region != prev_region:
        if region == "USA":
            transition = "Turning to the United States,"
        elif region == "CHINA":
            transition = "Meanwhile in China,"
        elif region == "ASIA":
            transition = "In Asia,"
        elif region == "INDIA":
            transition = "Turning to India,"
        else:
            transition = "In other global developments,"
    else:
        transitions_pool = [
            "In another major development,",
            "In concurrent industry updates,",
            "Expanding on regulatory scrutiny,",
            "In enterprise infrastructure,"
        ]
        transition = transitions_pool[(idx - 2) % len(transitions_pool)]

    # Combine transition and content
    narration = f"{transition} {content}"
    return clean_text_for_broadcast(narration)

def extract_attribution(chunk: str) -> tuple:
    """Pull the outlet name and URL off a story block.

    Returns (source_names, source_url). Never invents an outlet or a link.
    A missing Source: line comes back as an empty list so the traceability
    gate can reject the episode instead of printing a fake citation.
    """
    srcs = []
    source_url = ""
    src_match = re.search(r"(?im)^\s*(?:Source|Also):\s*([^\n]+)", chunk)
    if not src_match:
        src_match = re.search(r"\b(?:Source|Also):\s*([^\n]+)", chunk, re.IGNORECASE)
    if src_match:
        raw_src = src_match.group(1)
        url_match = re.search(r"https?://\S+", raw_src)
        if url_match:
            source_url = url_match.group(0).rstrip(").,]>\"'")
        clean_src = re.sub(r"https?://\S+", "", raw_src)
        clean_src = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", clean_src)
        clean_src = re.sub(r"\[([^\]]+)\]", r"\1", clean_src)
        clean_src = clean_src.strip(" -–—*")
        if clean_src:
            srcs.append(clean_src)
    if not source_url:
        url_line = re.search(r"(?m)^\s*(https?://\S+)\s*$", chunk)
        if url_line:
            source_url = url_line.group(1).rstrip(").,]>\"'")
    desk = ""
    desk_match = re.search(r"(?im)^\s*(?:\*\*)?Desk:\s*(.+?)(?:\*\*)?\s*$", chunk)
    if desk_match:
        desk = desk_match.group(1).strip()
    return srcs, source_url, desk


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

    # Check for regional sections (# WORLD, # USA, # CHINA, # ASIA, # INDIA)
    regional_matches = list(re.finditer(
        r"(?:^|\n)#+\s*(?:[🌍🇺🇸🇨🇳🌏🇮🇳\s]*)(WORLD|USA|CHINA|ASIA|INDIA)\s*(?:\n|$)",
        md_text,
        flags=re.IGNORECASE,
    ))
    
    candidate_stories = []

    if regional_matches:
        for i, match in enumerate(regional_matches):
            reg = match.group(1).upper()
            start_pos = match.end()
            end_pos = regional_matches[i + 1].start() if i + 1 < len(regional_matches) else len(md_text)
            
            # Truncate before Master Prompt, Takeaways, Recap if this is the last regional section
            reg_text = md_text[start_pos:end_pos]
            reg_text = re.split(r"(?:\n#+\s*(?:MASTER\s+PROMPT|TODAY'S\s+KEY|HEADLINES|TAKEAWAYS))", reg_text, flags=re.IGNORECASE)[0]

            # Split stories within this regional block by ###
            story_chunks = re.split(r"(?:^|\n)###\s+", reg_text)
            for chunk in story_chunks:
                chunk = chunk.strip()
                if not chunk or len(chunk) < 20:
                    continue
                
                chunk_lines = chunk.splitlines()
                raw_head = chunk_lines[0].strip()
                head_clean = clean_text_for_broadcast(raw_head)
                
                srcs, source_url, research_desk = extract_attribution(chunk)
                if not srcs or not is_proper_article_url(source_url):
                    print(f"[SKIP] No proper source for {head_clean[:70]!r}. Left out of the video.")
                    continue

                body_lines = [l for l in chunk_lines[1:] if not is_metadata_line(l)]
                body_clean = strip_unspoken_metadata(" ".join(body_lines))

                if head_clean and body_clean:
                    candidate_stories.append({
                        "region": reg,
                        "headline": head_clean,
                        "body": body_clean,
                        "sources": srcs,
                        "source_url": source_url,
                        "research_desk": research_desk,
                    })

    # If no regional sections found, fall back to STORY \d+ blocks
    if not candidate_stories:
        story_pattern = re.compile(r"(?:^|\n)(?:#{1,4}\s*)?(?:STORY\s+(\d+)|Story\s+(\d+))\b", re.IGNORECASE)
        splits = [m.start() for m in story_pattern.finditer(md_text)]
        if splits:
            for idx in range(len(splits)):
                start = splits[idx]
                end = splits[idx + 1] if idx + 1 < len(splits) else len(md_text)
                raw = md_text[start:end]
                clean_block = re.split(r"(?:\n---|\n)(?:HEADLINES\s+RECAP|OUTRO|THUMBNAIL)", raw, flags=re.IGNORECASE)[0]
                
                first_lines = [
                    l.strip() for l in clean_block.splitlines()
                    if l.strip() and not l.upper().startswith("STORY") and not is_metadata_line(l)
                ]
                raw_head = first_lines[0] if first_lines else f"Global AI Development {idx + 1}"
                head_clean = clean_text_for_broadcast(raw_head)

                body_lines = first_lines[1:] if len(first_lines) > 1 else [head_clean]
                body_clean = strip_unspoken_metadata(" ".join(body_lines))
                srcs, source_url, research_desk = extract_attribution(clean_block)
                if not srcs or not is_proper_article_url(source_url):
                    print(f"[SKIP] No proper source for {head_clean[:70]!r}. Left out of the video.")
                    continue

                candidate_stories.append({
                    "region": "WORLD" if idx == 0 else ("USA" if idx in [1, 2] else ("CHINA" if idx == 3 else ("ASIA" if idx == 4 else "INDIA"))),
                    "headline": head_clean,
                    "body": body_clean,
                    "sources": srcs,
                    "source_url": source_url,
                    "research_desk": research_desk,
                })

    # Deduplicate stories
    unique_stories = deduplicate_stories(candidate_stories)

    # Balance selection across bureaus (WORLD, USA, CHINA, ASIA, INDIA)
    by_region = {}
    for s in unique_stories:
        by_region.setdefault(s["region"], []).append(s)
    
    selected_stories = []
    # 1. Lead story from WORLD
    if "WORLD" in by_region and by_region["WORLD"]:
        selected_stories.append(by_region["WORLD"].pop(0))
    # 2. USA Safety / Incident
    if "USA" in by_region and by_region["USA"]:
        selected_stories.append(by_region["USA"].pop(0))
    # 3. USA Regulation / Standards
    if "USA" in by_region and by_region["USA"]:
        selected_stories.append(by_region["USA"].pop(0))
    elif "WORLD" in by_region and by_region["WORLD"]:
        selected_stories.append(by_region["WORLD"].pop(0))
    # 4. CHINA Infrastructure / Compute
    if "CHINA" in by_region and by_region["CHINA"]:
        selected_stories.append(by_region["CHINA"].pop(0))
    # 5. ASIA Enterprise Adoption
    if "ASIA" in by_region and by_region["ASIA"]:
        selected_stories.append(by_region["ASIA"].pop(0))
    # 6. INDIA Sovereign Compute
    if "INDIA" in by_region and by_region["INDIA"]:
        selected_stories.append(by_region["INDIA"].pop(0))
    
    # Fill remaining slots from the brief. Keep every sourced story up to 18.
    for reg in ["WORLD", "USA", "CHINA", "ASIA", "INDIA"]:
        while len(selected_stories) < 18 and reg in by_region and by_region[reg]:
            selected_stories.append(by_region[reg].pop(0))

    # High-grade broadcast television fallback assets (Permanently bans bounce-rate charts and student code)
    clean_fallback_catalog = {
        1: {
            "main": "aibrief/backgrounds/geopolitics.jpg",
            "cut2": "aibrief/backgrounds/global_policy.jpg",
            "cut3": "aibrief/backgrounds/cloud_infrastructure.jpg",
            "badge1": "GLOBAL STRATEGIC BRIEFING • DEFENSE & POLICY",
            "badge2": "MULTILATERAL ACCORD • SOVEREIGN MONITORING",
            "badge3": "GLOBAL INFRASTRUCTURE • ORBITAL SATELLITE FABRIC"
        },
        2: {
            "main": "aibrief/assets/editorial/gov_us_capitol_hearing.jpg",
            "cut2": "aibrief/backgrounds/ai_security.jpg",
            "cut3": "aibrief/assets/editorial/tech_silicon_wafer.jpg",
            "badge1": "WASHINGTON D.C. • EXECUTIVE OVERSIGHT COUNCIL",
            "badge2": "CYBER OPERATIONS DESK • ACCESS MONITORING HUD",
            "badge3": "NEURAL ACCELERATOR SILICON • DIE INSPECTION"
        },
        3: {
            "main": "aibrief/assets/editorial/tech_silicon_wafer.jpg",
            "cut2": "aibrief/backgrounds/ai_standards.jpg",
            "cut3": "aibrief/backgrounds/cloud_infrastructure.jpg",
            "badge1": "ADVANCED SILICON DIE • FABRICATION CLEANROOM",
            "badge2": "STANDARDS VERIFICATION • RECURSIVE EVALUATION HUD",
            "badge3": "HYPERSCALE BACKBONE • COMPUTE SCALING"
        },
        4: {
            "main": "aibrief/backgrounds/ai_chips.jpg",
            "cut2": "aibrief/assets/editorial/tech_silicon_wafer.jpg",
            "cut3": "aibrief/backgrounds/cloud_infrastructure.jpg",
            "badge1": "TENSOR ARCHITECTURE • HARDWARE TELEMETRY",
            "badge2": "ACCELERATOR SILICON WAFER • COMPLIANCE AUDIT",
            "badge3": "COMMERCIAL RUN RATE • ENTERPRISE WORKLOADS"
        },
        5: {
            "main": "aibrief/assets/editorial/fin_tokyo_district.jpg",
            "cut2": "aibrief/backgrounds/global_policy.jpg",
            "cut3": "aibrief/backgrounds/cloud_infrastructure.jpg",
            "badge1": "REGIONAL DIGITAL FABRIC • SOVEREIGN TECH MAP",
            "badge2": "MINISTERIAL ENGAGEMENT • SOVEREIGN ACCORD",
            "badge3": "REGIONAL PRODUCTIVITY TELEMETRY • PUBLIC SERVICES"
        },
        6: {
            "main": "aibrief/assets/story6_indian_engineers.jpg",
            "cut2": "aibrief/assets/editorial/tech_silicon_wafer.jpg",
            "cut3": "aibrief/backgrounds/cloud_infrastructure.jpg",
            "badge1": "SOVEREIGN COMPUTE INFRASTRUCTURE • NATIONAL FABRIC",
            "badge2": "HIGH-DENSITY GPU CLUSTERS • DOMESTIC MODELS",
            "badge3": "DEFENSE READINESS & RUNTIME SECURITY HUD"
        }
    }

    # Load visual memory if present
    visual_mem_path = os.path.join("src", "aibrief", "data", "visual_memory.json")
    visual_memory_badges = {}
    if os.path.exists(visual_mem_path):
        try:
            with open(visual_mem_path, "r", encoding="utf-8") as vmf:
                vmd = json.load(vmf)
                for h in vmd.get("history", []):
                    if h.get("date") == iso_date:
                        for item in h.get("assets", []):
                            visual_memory_badges[item["filename"]] = item.get("badge")
        except Exception:
            pass

    stories = []
    transitions = []
    prev_reg = None

    for idx, s in enumerate(selected_stories, 1):
        reg = s["region"]
        head = s["headline"]
        body = s["body"]
        srcs = s["sources"]

        script = format_broadcast_narration(idx, reg, head, body, prev_reg)
        prev_reg = reg

        pans = [
            ("zoomIn", "panLeft", "zoomOut"),
            ("zoomOut", "panRight", "zoomIn"),
            ("panLeft", "zoomIn", "panRight"),
            ("panRight", "zoomOut", "panLeft")
        ][(idx - 1) % 4]

        # Check for fresh story-specific downloaded assets for this date
        date_editorial_dir = os.path.join("public", "aibrief", "assets", "editorial", iso_date)
        f_cut1 = os.path.join(date_editorial_dir, f"s{idx}_cut1.jpg")
        f_cut2 = os.path.join(date_editorial_dir, f"s{idx}_cut2.jpg")
        f_cut3 = os.path.join(date_editorial_dir, f"s{idx}_cut3.jpg")

        if os.path.exists(f_cut1) and os.path.exists(f_cut2) and os.path.exists(f_cut3):
            badge1 = visual_memory_badges.get(f"s{idx}_cut1.jpg", f"{reg} SPECIAL REPORT • CUT 1")
            badge2 = visual_memory_badges.get(f"s{idx}_cut2.jpg", f"{reg} INFRASTRUCTURE • CUT 2")
            badge3 = visual_memory_badges.get(f"s{idx}_cut3.jpg", f"{reg} DEPLOYMENT • CUT 3")
            visual_cuts = [
                {"image": f"aibrief/assets/editorial/{iso_date}/s{idx}_cut1.jpg", "badge": badge1, "panDirection": pans[0]},
                {"image": f"aibrief/assets/editorial/{iso_date}/s{idx}_cut2.jpg", "badge": badge2, "panDirection": pans[1]},
                {"image": f"aibrief/assets/editorial/{iso_date}/s{idx}_cut3.jpg", "badge": badge3, "panDirection": pans[2]}
            ]
        else:
            cat_info = clean_fallback_catalog.get(idx, clean_fallback_catalog[1])
            visual_cuts = [
                {"image": cat_info["main"], "badge": cat_info["badge1"], "panDirection": pans[0]},
                {"image": cat_info["cut2"], "badge": cat_info["badge2"], "panDirection": pans[1]},
                {"image": cat_info["cut3"], "badge": cat_info["badge3"], "panDirection": pans[2]}
            ]

        slug = re.sub(r"[^a-z0-9]+", "_", head.lower())[:32].strip("_")
        s_id = f"s{idx}_{slug}" if slug else f"story_{idx}"

        stories.append({
            "id": s_id,
            "region": reg,
            "category": f"{reg} Intelligence",
            "categoryTag": f"{reg} • SPECIAL REPORT",
            "headline": head,
            "subheadline": f"Source: {', '.join(srcs[:2])}",
            "importanceScore": 99 if idx == 1 else (95 if idx <= 3 else 90),
            "durationSeconds": max(int(len(script.split()) * 0.42), 24),
            "source": ", ".join(srcs[:2]),
            "sourceUrl": s.get("source_url") or "",
            "researchDesk": s.get("research_desk") or "",
            "script": script,
            "whyThisMatters": f"Critical development shaping {reg} artificial intelligence policy and sovereign compute.",
            "keyPoints": [head[:80], srcs[0] if srcs else ""],
            "visualCuts": visual_cuts
        })

    # Transitions across regions
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
    recap_items = [f"✓ {s['headline'][:48]}" for s in stories[:7]]
    recap_script = "To recap today's headlines: " + "; ".join([s['headline'] for s in stories[:6]]) + "."

    market_colors = ["#0ea5e9", "#ef4444", "#10b981", "#8b5cf6", "#38bdf8", "#f97316", "#10a37f"]
    market_entities = []
    for i, s in enumerate(stories[:6]):
        market_entities.append({
            "name": s["region"],
            "update": s["headline"][:72],
            "tag": "TODAY'S DESK",
            "color": market_colors[i % len(market_colors)],
        })

    # Intro script
    lead_head = stories[0]['headline'] if stories else "Frontier Artificial Intelligence"
    intro_script = (
        f"In a landmark development, {lead_head}. "
        f"From the SanMitra Newsroom, here is the Daily AI Brief for {formatted_date}."
    )

    # Outro script
    outro_script = (
        "Those were today's critical developments across global artificial intelligence. "
        "From our bureaus covering World, USA, China, Asia, and India, thank you for watching SanMitra AI News Wire. "
        "Subscribe now for daily institutional AI intelligence."
    )

    # Title & tags
    top_heads = " | ".join([s["headline"][:32] for s in stories[:3]])
    yt_title = f"{top_heads} | AI News {formatted_date}"

    episode = {
        "date": iso_date,
        "formattedDate": formatted_date,
        "title": yt_title,
        "intro": {
            "durationSeconds": 18,
            "headline": "GLOBAL AI INTELLIGENCE WIRE",
            "subheadline": "SANMITRA NEWSROOM COMMAND CENTER",
            "script": clean_text_for_broadcast(intro_script)
        },
        "transitions": transitions,
        "stories": stories,
        "recap": {
            "durationSeconds": 12,
            "headline": "TODAY'S CRITICAL DEVELOPMENTS",
            "script": clean_text_for_broadcast(recap_script),
            "items": recap_items
        },
        "marketSnapshot": {
            "durationSeconds": 16,
            "headline": "GLOBAL AI MARKET SNAPSHOT",
            "subheadline": "SANMITRA DESK • STRATEGIC TELEMETRY",
            "script": "On the desk today: " + ". ".join(s["headline"] for s in stories[:6]) + ".",
            "entities": market_entities
        },
        "outro": {
            "durationSeconds": 12,
            "headline": "SANMITRA AI NEWS WIRE",
            "subheadline": "Daily Global AI Intelligence",
            "cta": "SUBSCRIBE FOR DAILY AI INTELLIGENCE",
            "bureaus": ["WORLD", "USA", "CHINA", "ASIA", "INDIA"],
            "script": clean_text_for_broadcast(outro_script)
        },
        "ticker": ["SanMitra AI News Wire v6.0"] + [s["headline"][:45] for s in stories],
        "thumbnail": {
            "date": formatted_date.upper(),
            "headline": stories[0]["headline"].upper() if stories else "BIGGEST AI NEWS TODAY",
            "subheadline": "GLOBAL INTELLIGENCE BRIEFING",
            "storyHighlights": [s["headline"][:35].upper() for s in stories[:4]]
        },
        "youtubeMetadata": {
            "title": yt_title,
            "descriptionIntro": f"Daily institutional-grade AI intelligence from the SanMitra Newsroom covering {formatted_date}.",
            "tags": ["AI", "ArtificialIntelligence", "SuperIntelligence", "OpenAI", "DeepSeek", "TechNews", "SanMitra"]
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
    if not episode.get("stories"):
        print("[X] No story had a proper source. The video was not updated.")
        sys.exit(1)
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
        print(f"         Narration: {s['script'][:80]}...")
    print(f"    - Output: {out_path} and {active_path}")

if __name__ == "__main__":
    main()
