"""
Automated Editorial Visual Asset Downloader & Processor for SanMitra AI News Wire v7.0.
Strictly complies with the Visual Freshness & Anti-Repetition Standard:
1. PERMANENTLY BANNED:
   - Obama on phone (gov_white_house.jpg)
   - UN logo / emblem (gov_un_chamber.jpg, un_declaration.png)
   - Gateway of India (gov_india_delhi.jpg)
   - Earth-at-night satellite image (tech_neural_globe.jpg)
   - Generic AI robot faces
   - Generic hacker in hoodie
2. STORY-BASED VISUALS:
   - Primary Visual (Representative direct story context)
   - Alternative Visual A (Infrastructure, hardware, or research angle)
   - Alternative Visual B (Human engineering, SOC operations, or data analytics)
3. 14-DAY VISUAL MEMORY SYSTEM:
   - Maintains rolling log in src/aibrief/data/visual_memory.json
   - Tracks image URLs, dates, and story contexts to guarantee >= 80% day-to-day freshness.
"""

import argparse
from datetime import datetime, timedelta
import io
import json
import os
import sys
import urllib.request
from PIL import Image, ImageEnhance, ImageOps

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080
MEMORY_FILE = os.path.join("src", "aibrief", "data", "visual_memory.json")

# Permanently banned asset paths / keywords
BANNED_ASSETS = {
    "gov_white_house.jpg", # Obama on phone
    "gov_us_capitol_hearing.jpg", # same Obama photo saved under another name
    "story5_us_capitol.jpg", # same Obama photo saved under another name
    "gov_un_chamber.jpg",  # UN emblem / assembly
    "gov_india_delhi.jpg", # Gateway of India
    "tech_neural_globe.jpg", # Earth at night
    "un_declaration.png",
    "us_china_talks.png"
}

# Curated Story-Specific Real Visuals for 2026-09-28
DAILY_VISUAL_MAP = {
    "2026-09-28": [
        # Story 1: US-China AI Safety Hotline (Diplomatic situation room, encrypted telemetry, global comms)
        ("s1_cut1.jpg", "https://images.unsplash.com/photo-1577495508048-b635879837f1?w=1920&q=85", "SITUATION ROOM • BILATERAL CRISIS COMMUNICATIONS"),
        ("s1_cut2.jpg", "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1920&q=85", "ENCRYPTED TELEMETRY • SUPERCOMPUTER BACKBONE"),
        ("s1_cut3.jpg", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=85", "GLOBAL FIBER NETWORK • DE-ESCALATION PROTOCOLS"),

        # Story 2: OpenAI Training Pause (Containment research lab, kernel-level code debug, GPU cluster)
        ("s2_cut1.jpg", "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=1920&q=85", "FRONTIER AI RESEARCH LAB • SANDBOX CONTAINMENT DESK"),
        ("s2_cut2.jpg", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&q=85", "DNS RESOLVER AUDIT • KERNEL-LEVEL VIRTUALIZATION LOCK"),
        ("s2_cut3.jpg", "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1920&q=85", "HIGH-THROUGHPUT GPU CLUSTER • TRAINING REVIEWS"),

        # Story 3: Growing AI Incident Investigations (SOC operations center, engineering team, analytics wall)
        ("s3_cut1.jpg", "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1920&q=85", "SECURITY OPERATIONS CENTER • THREAT INTELLIGENCE DESK"),
        ("s3_cut2.jpg", "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1920&q=85", "RESEARCH SCIENTISTS • MULTI-AGENT GUARDRAIL AUDITING"),
        ("s3_cut3.jpg", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1920&q=85", "INCIDENT TELEMETRY • SYSTEMATIC DRIFT MONITORING"),

        # Story 4: China - Nvidia RTX PRO 5500 Review (Semiconductor die inspection, tech campus, enterprise servers)
        ("s4_cut1.jpg", "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=85", "ENTERPRISE ACCELERATOR SILICON • TRADE COMPLIANCE AUDIT"),
        ("s4_cut2.jpg", "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1920&q=85", "BEIJING HIGH-TECH TECH PARK • PROCUREMENT DESK"),
        ("s4_cut3.jpg", "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1920&q=85", "LIQUID-COOLED COMPUTE HALL • ALIBABA & BYTEDANCE WORKLOADS"),

        # Story 5: South Korea - Kakao "Everyone's AI" (Seoul tech corridor, mobile UX, smart city services)
        ("s5_cut1.jpg", "https://images.unsplash.com/photo-1538485399081-7191377e8241?w=1920&q=85", "SEOUL TEHERAN VALLEY • SOVEREIGN PUBLIC AI INFRASTRUCTURE"),
        ("s5_cut2.jpg", "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=1920&q=85", "KAKAOTALK MOBILE ASSISTANT • CIVIC & HEALTHCARE SERVICES"),
        ("s5_cut3.jpg", "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1920&q=85", "SMART NATION DIGITAL FABRIC • MUNICIPAL TELEMETRY"),

        # Story 6: India - Sarvam AI Defense & Sovereign Security (Electronic City tech park, Indian tech team, cyber defense)
        ("s6_cut1.jpg", "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?w=1920&q=85", "BENGALURU ELECTRONIC CITY • DOMESTIC FOUNDATION MODELS"),
        ("s6_cut2.jpg", "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1920&q=85", "SARVAM AI ENGINEERING LAB • AIR-GAPPED BENCHMARKS"),
        ("s6_cut3.jpg", "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1920&q=85", "CRITICAL INFRASTRUCTURE DEFENSE • SOVEREIGN RUNTIME HUD")
    ],
    "2026-09-29": [
        # Story 1: AI Pioneers Warn of Intelligence Explosion; Anthropic IPO Existential Risk Warning
        ("s1_cut1.jpg", "https://images.unsplash.com/photo-1544531586-fde5298cdd40?w=1920&q=85", "EXECUTIVE SUMMIT • FRONTIER SAFETY ACCORD"),
        ("s1_cut2.jpg", "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1920&q=85", "CODE AUDIT • RECURSIVE R&D VERIFICATION"),
        ("s1_cut3.jpg", "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=1920&q=85", "SUPERCOMPUTER TELEMETRY • ACCELERATION AUDIT"),

        # Story 2: Nvidia Launches Open Agent Safety Platform; OpenAI Cancels GPT-6.1 Astra
        ("s2_cut1.jpg", "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1920&q=85", "VERA AI CPU ENCLAVE • CHIP INTEGRITY"),
        ("s2_cut2.jpg", "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=1920&q=85", "OPENSHELL RUNTIME • KERNEL ACCESS BOUNDARIES"),
        ("s2_cut3.jpg", "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=1920&q=85", "ENTERPRISE RACK DEPLOYMENT • SUB-MILLISECOND QUARANTINE"),

        # Story 3: AMD Acquires Fei-Fei Li's World Labs in $8.2B Physical-AI Megadeal
        ("s3_cut1.jpg", "https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=1920&q=85", "SPATIAL TESTING MATRIX • EXPERIMENTAL WORLD LAB"),
        ("s3_cut2.jpg", "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1920&q=85", "KEYNOTE DEMO INTERFACE • SPATIAL GENERATION HUD"),
        ("s3_cut3.jpg", "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1920&q=85", "PHYSICAL ROBOTICS CELL • HUMANOID KINEMATICS"),

        # Story 4: China - Full-Stack Domestic Embodied AI Robot; RTX PRO 5500 Review
        ("s4_cut1.jpg", "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=1920&q=85", "YICHANG ROBOT ACTUATOR ASSEMBLY • DOMESTIC ARCHITECTURE"),
        ("s4_cut2.jpg", "https://images.unsplash.com/photo-1517420704952-d9f39e95b43e?w=1920&q=85", "INTELLIGENT NERVOUS SYSTEM • WAFER AND DIE FABRIC"),
        ("s4_cut3.jpg", "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1920&q=85", "SCREEN PORTAL TELEMETRY • HIGH-THROUGHPUT COMPLIANCE"),

        # Story 5: Singapore - UN Framework Convention on AI Safeguards & IAEA-Style Agency
        ("s5_cut1.jpg", "https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=1920&q=85", "DIPLOMATIC MINISTERIAL ASSEMBLY • GLOBAL SAFEGUARDS"),
        ("s5_cut2.jpg", "https://images.unsplash.com/photo-1506351421178-63b52a2d2562?w=1920&q=85", "BILATERAL SUMMIT • SINGAPORE FRONTIER ACCORD"),
        ("s5_cut3.jpg", "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1920&q=85", "REGULATORY HEARING • STANDARDS VERIFICATION DESK"),

        # Story 6: India - FM Nirmala Sitharaman at IIT Madras Sangam 2026; Google ATLAS Study
        ("s6_cut1.jpg", "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=1920&q=85", "MINISTRY OF FINANCE DESK • SOVEREIGN COMPUTE ADDRESS"),
        ("s6_cut2.jpg", "https://images.unsplash.com/photo-1504384764586-bb4cdc1707b0?w=1920&q=85", "PATIENT CAPITAL INCUBATOR • DEEPTECH CLEANROOM"),
        ("s6_cut3.jpg", "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1920&q=85", "GOOGLE AI ATLAS METRICS • WORKSTATION MAPPING")
    ]
}

def load_visual_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"history": [], "banned": list(BANNED_ASSETS)}

def save_visual_memory(memory: dict):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

from src.aibrief.visual_memory_manager import VisualMemoryManager

def crop_and_grade(im: Image.Image) -> Image.Image:
    # 1. Fit to 1920x1080 (16:9)
    im = ImageOps.fit(im, (TARGET_WIDTH, TARGET_HEIGHT), method=Image.Resampling.LANCZOS)
    # 2. Subtle institutional broadcast grading: enhance contrast + slight saturation
    enhancer_contrast = ImageEnhance.Contrast(im)
    im = enhancer_contrast.enhance(1.08)
    enhancer_color = ImageEnhance.Color(im)
    im = enhancer_color.enhance(1.05)
    return im

def download_daily_visuals(date_str: str):
    print("=" * 75)
    print(f"🎬 DOWNLOADING FRESH STORY-BASED EDITORIAL VISUALS FOR {date_str}")
    print("=" * 75)

    dest_dir = os.path.join("public", "aibrief", "assets", "editorial", date_str)
    os.makedirs(dest_dir, exist_ok=True)
    if os.path.exists(os.path.join(dest_dir, "s1_cut1.jpg")) and os.path.exists(os.path.join(dest_dir, "s9_cut3.jpg")):
        print(f"[+] Editorial stills for {date_str} are already on disk. Leaving them in place.")
        return

    items = DAILY_VISUAL_MAP.get(date_str, DAILY_VISUAL_MAP["2026-09-28"])
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    mgr = VisualMemoryManager()
    used_this_run = []
    category_counts = {}

    for filename, url, badge in items:
        dest_file = os.path.join(dest_dir, filename)
        category = mgr.classify_visual_category(badge, url)
        print(f"[*] Processing visual: {filename} (Category: {category})...")

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as r:
                data = r.read()
                im = Image.open(io.BytesIO(data)).convert("RGB")
                im = crop_and_grade(im)

                # Validate against 14-day pHash memory and diversity caps
                approved, cand_hash, rejection_reason = mgr.check_visual_candidate(
                    im, url, category, category_counts, current_date_str=date_str
                )

                if not approved:
                    print(f"    [!] REJECTED BY EDITORIAL VISUAL GATE: {rejection_reason}")
                    continue

                im.save(dest_file, quality=92)
                category_counts[category] = category_counts.get(category, 0) + 1
                print(f"    [+] APPROVED & SAVED (pHash: {cand_hash}, Category count: {category_counts[category]}/2): {dest_file}")

                used_this_run.append({
                    "date": date_str,
                    "filename": filename,
                    "url": url,
                    "badge": badge,
                    "phash": cand_hash,
                    "category": category
                })
        except Exception as e:
            print(f"    [!] Error downloading from {url}: {e}")

    # Register in 14-day pHash visual memory
    if used_this_run:
        mgr.register_episode_visuals(date_str, used_this_run)
        print(f"\n[+] Visual memory updated with {len(used_this_run)} pHash-verified assets: {MEMORY_FILE}")
        print(f"[+] Category diversity distribution: {category_counts}")
        print(f"[+] All fresh visuals downloaded to: {dest_dir}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Broadcast date (YYYY-MM-DD)")
    args = parser.parse_args()
    download_daily_visuals(args.date)
