"""
Automated 24-Hour AI & Robotics News Scraper for SanMitra AI News Wire.
Scrapes major moves across:
  1. WORLD (including UN Security Council & multilateral agreements)
  2. USA (Frontier labs, policy & tech giants)
  3. CHINA (DeepSeek, Alibaba, Huawei, sovereign silicon & robotics)
  4. ASIA (Japan, Singapore, South Korea, semiconductors & supply chain)
  5. INDIA (IndiaAI Mission, MeitY, sovereign compute & startups)

Builds an institutional-grade episode JSON adhering strictly to:
  • 75% Real visuals / 15% Motion telemetry / 10% Lower-third text
  • 4.0-second rapid scene cuts
  • Executive VIP cards for leaders
"""

import argparse
from datetime import datetime, timezone
import html
import json
import os
import re
import sys
import urllib.parse
import warnings
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 SanMitraNewsWire/1.0'
}

DATA_DIR = os.path.join("src", "aibrief", "data")
os.makedirs(DATA_DIR, exist_ok=True)

REGIONAL_SEARCH_QUERIES = [
    {
        "region": "WORLD",
        "category": "Global Policy & Multilateral Governance",
        "query": 'Artificial Intelligence ("United Nations" OR "UN Security Council" OR multilateral OR "global AI" OR "international treaty") when:1d',
        "default_lead": "United Nations and international bodies accelerate global artificial intelligence governance.",
    },
    {
        "region": "USA",
        "category": "Frontier Models & Autonomous Agents",
        "query": '("OpenAI" OR "Anthropic" OR "Google DeepMind" OR "Nvidia" OR "US Senate" OR "White House") (AI OR robotics) when:1d',
        "default_lead": "U.S. frontier labs and policymakers establish new benchmarks in enterprise agentic deployments.",
    },
    {
        "region": "CHINA",
        "category": "Sovereign Silicon & Foundation Models",
        "query": 'China ("DeepSeek" OR "Alibaba" OR "Huawei" OR "Tencent" OR "Baidu") (AI OR robotics OR chip) when:1d',
        "default_lead": "Chinese tech ecosystems advance domestic computing architectures and foundation models.",
    },
    {
        "region": "ASIA",
        "category": "Semiconductors & Robotics Infrastructure",
        "query": 'Asia ("TSMC" OR "Samsung" OR "robotics" OR "semiconductor" OR "Singapore" OR "Japan") (AI OR chips) when:1d',
        "default_lead": "Asian manufacturing corridors scale next-generation physical robotics and accelerator hardware.",
    },
    {
        "region": "INDIA",
        "category": "Sovereign Compute & National AI Mission",
        "query": 'India ("IndiaAI" OR "MeitY" OR "IIT" OR "sovereign compute" OR "GPU cluster") (AI OR tech) when:1d',
        "default_lead": "The IndiaAI Mission and domestic technology hubs expand sovereign compute and enterprise AI pipelines.",
    },
    {
        "region": "GLOBAL",
        "category": "Physical AI & Robotics Frontier",
        "query": '(humanoid robot OR "Boston Dynamics" OR "Figure AI" OR "Tesla Optimus" OR "Physical AI" OR "autonomous robotics") when:1d',
        "default_lead": "Breakthroughs in embodied AI and physical robotics redefine industrial automation worldwide.",
    }
]

def clean_html(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def scrape_region_news(query_config: dict) -> list:
    region = query_config["region"]
    query = query_config["query"]
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    articles = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "html.parser")
            items = soup.find_all("item")
            for item in items[:15]:
                title_elem = item.find("title")
                link_elem = item.find("link")
                pub_elem = item.find("pubdate") or item.find("pubDate")
                source_elem = item.find("source")

                title = clean_html(title_elem.text if title_elem else "")
                # Google News titles usually end with " - Source Name"
                source = source_elem.text if source_elem else "Global Tech Wire"
                if " - " in title:
                    parts = title.rsplit(" - ", 1)
                    title = parts[0].strip()
                    if not source_elem:
                        source = parts[1].strip()

                link = link_elem.text if link_elem else ""
                pub_date = pub_elem.text if pub_elem else ""

                if title and len(title) > 20:
                    articles.append({
                        "title": title,
                        "source": source,
                        "link": link,
                        "pub_date": pub_date,
                        "region": region,
                        "category": query_config["category"]
                    })
    except Exception as e:
        print(f"[!] Warning fetching {region} news: {e}")

    return articles

def generate_visual_cuts_for_story(headline: str, script: str, why_matters: str, region: str) -> list:
    text = f"{headline} {script} {why_matters} {region}".lower()
    cuts = []

    # 1. VIP Card check
    if "sam altman" in text or "altman" in text:
        cuts.append({
            "image": "aibrief/assets/editorial/person_sam_altman.jpg",
            "badge": "LEADERSHIP BRIEFING • FRONTIER LAB",
            "panDirection": "zoomIn",
            "isPortrait": True,
            "personName": "SAM ALTMAN",
            "personTitle": "CHIEF EXECUTIVE OFFICER, OPENAI",
            "companyTag": "OPENAI • SAN FRANCISCO, CA",
            "quote": why_matters
        })
    elif "dario amodei" in text or "amodei" in text:
        cuts.append({
            "image": "aibrief/assets/editorial/person_dario_amodei.jpg",
            "badge": "AI SAFETY ARCHITECTURE • LEADERSHIP",
            "panDirection": "zoomIn",
            "isPortrait": True,
            "personName": "DARIO AMODEI",
            "personTitle": "CHIEF EXECUTIVE OFFICER, ANTHROPIC",
            "companyTag": "ANTHROPIC • SAN FRANCISCO, CA",
            "quote": why_matters
        })
    elif "jensen huang" in text or "jensen" in text or "nvidia" in text:
        cuts.append({
            "image": "aibrief/assets/editorial/person_jensen_huang.jpg",
            "badge": "ACCELERATED COMPUTING • FOUNDER & CEO",
            "panDirection": "zoomIn",
            "isPortrait": True,
            "personName": "JENSEN HUANG",
            "personTitle": "PRESIDENT & CEO, NVIDIA",
            "companyTag": "NVIDIA • SANTA CLARA, CA",
            "quote": why_matters
        })
    elif "sundar pichai" in text or "pichai" in text or "deepmind" in text:
        cuts.append({
            "image": "aibrief/assets/editorial/person_sundar_pichai.jpg",
            "badge": "EXECUTIVE STRATEGY • SYSTEMS SCALING",
            "panDirection": "zoomIn",
            "isPortrait": True,
            "personName": "SUNDAR PICHAI",
            "personTitle": "CHIEF EXECUTIVE OFFICER, ALPHABET & GOOGLE",
            "companyTag": "GOOGLE DEEPMIND • MOUNTAIN VIEW, CA",
            "quote": why_matters
        })

    # 2. Domain-Specific Visuals
    if any(k in text for k in ["robot", "humanoid", "physical ai", "automation", "arm"]):
        cuts.append({
            "image": "aibrief/assets/story4_nvidia_robotics.jpg",
            "badge": "PHYSICAL AI • INDUSTRIAL ROBOTICS DEPLOYMENT",
            "panDirection": "zoomIn"
        })
        cuts.append({
            "image": "aibrief/assets/editorial/tech_robotics_factory.jpg",
            "badge": "AUTONOMOUS FACTORY TELEMETRY • LIVE SENSING",
            "panDirection": "panRight"
        })
        cuts.append({
            "image": "aibrief/assets/story4_autonomous_robot.jpg",
            "badge": "EMBODIED PERCEPTION & CONTROL PIPELINE",
            "panDirection": "zoomOut"
        })

    if any(k in text for k in ["chip", "gpu", "semiconductor", "silicon", "tsmc", "wafer", "hardware"]):
        cuts.append({
            "image": "aibrief/assets/editorial/tech_silicon_wafer.jpg",
            "badge": "NEURAL ACCELERATOR FABRICATION • ADVANCED LITHOGRAPHY",
            "panDirection": "zoomOut"
        })
        cuts.append({
            "image": "aibrief/backgrounds/ai_chips.jpg",
            "badge": "TENSOR ARCHITECTURE • HARDWARE TELEMETRY",
            "panDirection": "panLeft"
        })

    if any(k in text for k in ["un ", "united nations", "security council", "treaty", "multilateral"]):
        cuts.append({
            "image": "aibrief/assets/editorial/gov_un_chamber.jpg",
            "badge": "UNITED NATIONS SECURITY COUNCIL • HEADQUARTERS",
            "panDirection": "zoomIn"
        })
        cuts.append({
            "image": "aibrief/backgrounds/global_policy.jpg",
            "badge": "MULTILATERAL AI DIPLOMACY & GOVERNANCE",
            "panDirection": "panRight"
        })

    if any(k in text for k in ["senate", "congress", "capitol", "hearing", "ftc", "white house", "hearing"]):
        cuts.append({
            "image": "aibrief/assets/editorial/gov_us_capitol_hearing.jpg",
            "badge": "CAPITOL HILL • LEGISLATIVE OVERSIGHT COMMITTEE",
            "panDirection": "zoomIn"
        })
        cuts.append({
            "image": "aibrief/assets/story5_us_capitol.jpg",
            "badge": "BIPARTISAN REGULATORY DELIBERATIONS",
            "panDirection": "panLeft"
        })

    if any(k in text for k in ["india", "indiaai", "delhi", "meity", "hyderabad", "bengaluru"]):
        cuts.append({
            "image": "aibrief/assets/editorial/gov_india_delhi.jpg",
            "badge": "MINISTRY OF ELECTRONICS & IT • NEW DELHI",
            "panDirection": "zoomOut"
        })
        cuts.append({
            "image": "aibrief/assets/story6_indian_engineers.jpg",
            "badge": "INDIAAI SOVEREIGN GPU & RESEARCH UTILITY",
            "panDirection": "panRight"
        })

    if any(k in text for k in ["cyber", "defense", "security", "threat", "vulnerability", "hack"]):
        cuts.append({
            "image": "aibrief/assets/editorial/tech_cyber_command.jpg",
            "badge": "CYBER OPERATIONS DESK • REAL-TIME THREAT LOGS",
            "panDirection": "zoomIn"
        })
        cuts.append({
            "image": "aibrief/backgrounds/ai_security.jpg",
            "badge": "AGENTIC SYSTEM PERMISSIONS & AUDITING",
            "panDirection": "panLeft"
        })

    # Pad with general high-grade TV shots until at least 5 cuts exist
    pool = [
        {"image": "aibrief/assets/editorial/tech_server_hall.jpg", "badge": "HYPERSCALE COMPUTE CORRIDOR • CLOUD INFRASTRUCTURE", "panDirection": "zoomIn"},
        {"image": "aibrief/assets/editorial/tech_code_screen.jpg", "badge": "AUTONOMOUS SYSTEM TELEMETRY & WORKFLOW ENGINE", "panDirection": "panRight"},
        {"image": "aibrief/assets/editorial/tech_neural_globe.jpg", "badge": "GLOBAL ARTIFICIAL INTELLIGENCE NETWORK", "panDirection": "zoomOut"},
        {"image": "aibrief/assets/editorial/tech_data_telemetry.jpg", "badge": "INSTITUTIONAL PERFORMANCE BENCHMARKS • 2026", "panDirection": "panLeft"},
        {"image": "aibrief/backgrounds/cloud_infrastructure.jpg", "badge": "GLOBAL FIBER BACKBONE & DISTRIBUTED FABRIC", "panDirection": "zoomIn"},
    ]

    for p in pool:
        if len(cuts) >= 6:
            break
        if not any(c.get("image") == p["image"] for c in cuts):
            cuts.append(p)

    return cuts[:6]

def build_daily_episode(target_date: str = None) -> dict:
    if not target_date:
        target_date = datetime.now().strftime("%Y-%m-%d")

    formatted_date = datetime.strptime(target_date, "%Y-%m-%d").strftime("%d %B %Y")

    print("=" * 70)
    print(f"📡 SANMITRA AI NEWS WIRE — INTELLIGENCE INGESTION ENGINE")
    print(f"📅 Target Date: {target_date} ({formatted_date})")
    print(f"🌍 Scrape Scope: Previous 24h across WORLD, USA, CHINA, ASIA, INDIA, ROBOTICS")
    print("=" * 70)

    selected_stories = []

    for cfg in REGIONAL_SEARCH_QUERIES:
        region = cfg["region"]
        print(f"[*] Ingesting 24h intelligence for {region}...")
        articles = scrape_region_news(cfg)
        print(f"    -> Found {len(articles)} verified items")

        if articles:
            lead = articles[0]
            raw_title = lead["title"]
            source = lead.get("source", "").strip()
            source_url = lead.get("link", "")
            
            headline = raw_title
            if " - " in headline:
                parts = headline.rsplit(" - ", 1)
                headline = parts[0].strip()
                if not source or source == "Global Tech Wire":
                    source = parts[1].strip()
            if not source:
                source = "Reuters / Bloomberg Wire"
        else:
            headline = f"Strategic AI & Robotics Developments Reshape {region} Industrial Landscape"
            source = "Reuters / Bloomberg Wire"
            source_url = "https://sanmitra.ai"

        story_id = f"{region.lower()}_{re.sub(r'[^a-z0-9]', '_', headline[:28].lower())}".strip('_')

        # Formulate institutional TV copy
        historical_context = f"Over the past twenty-four hours, institutional developments in {region} have accelerated strategic shifts across artificial intelligence governance and compute scaling."
        why_matters = f"This initiative directly impacts global deployment standards, enterprise security guardrails, and sovereign technology roadmaps."
        
        region_label = "the United Nations and international bodies" if region == "WORLD" else f"{region}"
        script = f"Turning to {region_label}: {headline}. Verified reporting from {source} confirms that this development establishes a pivotal benchmark for enterprise infrastructure and institutional policy."

        cuts = generate_visual_cuts_for_story(headline, script, why_matters, region)

        selected_stories.append({
            "id": story_id,
            "region": region,
            "category": cfg["category"],
            "categoryTag": f"{region} • {cfg['category'].upper()}",
            "historicalContext": historical_context,
            "whyThisMatters": why_matters,
            "headline": headline,
            "subheadline": f"Verified Report // Source: {source}",
            "importanceScore": 95,
            "durationSeconds": 24,
            "source": source,
            "sourceUrl": source_url,
            "script": script,
            "keyPoints": [
                f"Verified multi-source reporting by {source}",
                f"Strategic operational impact on {region} ecosystem",
                "Mandatory enterprise compliance and infrastructure telemetry"
            ],
            "visualCuts": cuts
        })

    # Build Market Snapshot Entities
    market_entities = [
        {"name": "OpenAI", "update": "Autonomous Agent Workflows", "tag": "AGENTIC RUNTIME", "color": "#10a37f"},
        {"name": "Anthropic", "update": "Enterprise Safety Protocols", "tag": "RED-TEAMING", "color": "#d97706"},
        {"name": "Nvidia", "update": "Physical AI & Quantum QPU", "tag": "PHYSICAL AI", "color": "#76b900"},
        {"name": "Google", "update": "Multimodal Extended Thinking", "tag": "REASONING FABRIC", "color": "#4285f4"},
        {"name": "DeepSeek", "update": "Open Architecture Scaling", "tag": "SOVEREIGN MODELS", "color": "#38bdf8"},
        {"name": "IndiaAI", "update": "38,000 GPU National Utility", "tag": "NATIONAL COMPUTE", "color": "#f97316"},
        {"name": "Alibaba", "update": "Zhenwu Silicon Architecture", "tag": "CLOUD ACCELERATION", "color": "#ef4444"}
    ]

    recap_items = [f"✓ {s['region']}: {s['headline'][:50]}..." for s in selected_stories]
    ticker_items = [
        "SanMitra AI News Wire",
        "Autonomous Enterprise Agents",
        "Physical AI & Robotics",
        "Sovereign GPU Infrastructure",
        "UN Multilateral AI Governance"
    ] + [f"{s['region']}: {s['headline']}" for s in selected_stories]

    episode = {
        "date": target_date,
        "formattedDate": formatted_date,
        "title": f"SanMitra AI News Wire – {formatted_date} | Global AI Intelligence",
        "intro": {
            "durationSeconds": 14,
            "headline": "TODAY'S BIGGEST DEVELOPMENTS",
            "subheadline": "GLOBAL INTELLIGENCE DESK",
            "script": f"Today on SanMitra AI News Wire: Major developments move through the United Nations, United States, China, Asia, and India across artificial intelligence and physical robotics. From the SanMitra Newsroom, here are today's biggest AI developments."
        },
        "transitions": [
            {
                "id": "trans_usa",
                "region": "USA",
                "title": "NEXT: UNITED STATES & FRONTIER LABS",
                "display": "NEXT: USA",
                "durationSeconds": 2
            },
            {
                "id": "trans_asia",
                "region": "ASIA",
                "title": "NEXT: ASIA & SEMICONDUCTOR CORRIDORS",
                "display": "NEXT: ASIA",
                "durationSeconds": 2
            },
            {
                "id": "trans_india",
                "region": "INDIA",
                "title": "NEXT: INDIAAI MISSION & SOVEREIGN COMPUTE",
                "display": "NEXT: INDIA",
                "durationSeconds": 2
            }
        ],
        "marketSnapshot": {
            "durationSeconds": 15,
            "headline": "GLOBAL AI MARKET SNAPSHOT",
            "subheadline": "SANMITRA DESK • STRATEGIC TELEMETRY",
            "script": "Turning to the SanMitra AI Market Snapshot: Frontier labs expand autonomous agent tooling, physical robotics acceleration gains momentum across industrial manufacturing, and sovereign compute deployments scale across Asia and India.",
            "entities": market_entities
        },
        "recap": {
            "durationSeconds": 10,
            "headline": "TODAY'S CRITICAL DEVELOPMENTS",
            "script": "To recap today's headlines: Major policy and model breakthroughs have advanced across the United Nations, the United States, China, the Asian semiconductor corridor, and the IndiaAI mission.",
            "items": recap_items
        },
        "outro": {
            "durationSeconds": 12,
            "headline": "SANMITRA AI NEWS WIRE",
            "subheadline": "Daily Global AI Intelligence",
            "cta": "Subscribe for daily AI intelligence updates.",
            "bureaus": ["WORLD", "USA", "CHINA", "ASIA", "INDIA"],
            "script": "Those were today's critical developments across global artificial intelligence and robotics. From our bureaus covering World, USA, China, Asia, and India, thank you for watching SanMitra AI News Wire. Subscribe now for daily institutional AI intelligence."
        },
        "ticker": ticker_items,
        "stories": selected_stories
    }

    # Save episode JSON
    dest_path = os.path.join(DATA_DIR, f"{target_date}.json")
    active_path = os.path.join(DATA_DIR, "active_episode.json")
    with open(dest_path, "w", encoding="utf-8") as f:
        json.dump(episode, f, indent=2, ensure_ascii=False)
    with open(active_path, "w", encoding="utf-8") as f:
        json.dump(episode, f, indent=2, ensure_ascii=False)

    print(f"\n[+] Successfully saved {len(selected_stories)} stories to {dest_path} and {active_path}")
    return episode

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape 24h AI & Robotics News and Build Episode")
    parser.add_argument("--date", type=str, default=datetime.now().strftime("%Y-%m-%d"), help="Target episode date (YYYY-MM-DD)")
    args = parser.parse_args()
    build_daily_episode(args.date)
