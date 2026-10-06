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
import shutil
import glob

def cleanup_old_visual_assets(current_date_str: str, retention_days: int = 7):
    """
    Automatically deletes old visual assets to maintain a lean workspace and enforce anti-repetition:
    1. Removes daily editorial folders older than retention_days (default 7 days).
    2. Purges permanently banned legacy stock assets.
    3. Trims entries in visual_memory.json older than 14 days.
    """
    print(f"\n🧹 [Auto-Cleanup] Scanning for old visual assets (Retention: {retention_days} days)...")
    base_editorial = os.path.join("public", "aibrief", "assets", "editorial")

    try:
        current_dt = datetime.strptime(current_date_str, "%Y-%m-%d")
    except Exception:
        current_dt = datetime.now()

    # 1. Prune date folders older than retention_days
    deleted_folders = 0
    if os.path.exists(base_editorial):
        for entry in os.listdir(base_editorial):
            entry_path = os.path.join(base_editorial, entry)
            if os.path.isdir(entry_path):
                try:
                    folder_dt = datetime.strptime(entry, "%Y-%m-%d")
                    age_days = (current_dt - folder_dt).days
                    if age_days > retention_days:
                        shutil.rmtree(entry_path, ignore_errors=True)
                        deleted_folders += 1
                        print(f"    [-] Auto-deleted expired visual folder: {entry} ({age_days} days old)")
                except ValueError:
                    pass
    if deleted_folders == 0:
        print(f"    [+] No expired date folders found beyond {retention_days} days.")

    # 2. Purge permanently banned stock assets from all assets locations
    banned_files = [
        "gov_white_house.jpg", "gov_un_chamber.jpg", "un_declaration.png",
        "gov_india_delhi.jpg", "tech_neural_globe.jpg", "tech_data_telemetry.jpg",
        "tech_code_screen.jpg", "tech_server_hall.jpg", "tech_cyber_command.jpg"
    ]
    target_dirs = [
        base_editorial,
        os.path.join("public", "aibrief", "assets"),
        os.path.join("public", "aibrief", "backgrounds")
    ]
    purged_banned = 0
    for t_dir in target_dirs:
        if os.path.exists(t_dir):
            for b_name in banned_files:
                b_path = os.path.join(t_dir, b_name)
                if os.path.exists(b_path):
                    try:
                        os.remove(b_path)
                        purged_banned += 1
                        print(f"    [x] Permanently purged banned asset: {b_path}")
                    except Exception as e:
                        print(f"    [!] Error deleting {b_path}: {e}")

    # 3. Clean visual memory log entries older than 14 days
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                mem = json.load(f)
            history = mem.get("history", [])
            cutoff = (current_dt - timedelta(days=14)).strftime("%Y-%m-%d")
            fresh_hist = [h for h in history if h.get("date", "2000-01-01") >= cutoff]
            if len(fresh_hist) < len(history):
                mem["history"] = fresh_hist
                save_visual_memory(mem)
                print(f"    [+] Pruned {len(history) - len(fresh_hist)} visual memory entries older than 14 days.")
        except Exception:
            pass
    print("🧹 [Auto-Cleanup] Cleanup complete.\n")


def crop_and_grade(im: Image.Image) -> Image.Image:
    # 1. Fit to 1920x1080 (16:9)
    im = ImageOps.fit(im, (TARGET_WIDTH, TARGET_HEIGHT), method=Image.Resampling.LANCZOS)
    # 2. Subtle institutional broadcast grading: enhance contrast + slight saturation
    enhancer_contrast = ImageEnhance.Contrast(im)
    im = enhancer_contrast.enhance(1.08)
    enhancer_color = ImageEnhance.Color(im)
    im = enhancer_color.enhance(1.05)
    return im

def download_daily_visuals(date_str: str, force: bool = False, retention_days: int = 7):
    print("=" * 75)
    print(f"🎬 DOWNLOADING FRESH STORY-BASED EDITORIAL VISUALS FOR {date_str} (Force: {force})")
    print("=" * 75)

    # 0. Automatically clean old visuals, banned assets, and expired memory
    cleanup_old_visual_assets(date_str, retention_days=retention_days)

    dest_dir = os.path.join("public", "aibrief", "assets", "editorial", date_str)
    os.makedirs(dest_dir, exist_ok=True)
    if not force and os.path.exists(os.path.join(dest_dir, "s1_cut1.jpg")) and os.path.exists(os.path.join(dest_dir, "s9_cut3.jpg")):
        print(f"[+] Editorial stills for {date_str} are already on disk. Leaving them in place.")
        return

    # If force, clear old/stale images in the target date folder before download
    if force and os.path.exists(dest_dir):
        for old_file in glob.glob(os.path.join(dest_dir, "*.*")):
            try:
                os.remove(old_file)
            except Exception:
                pass

    from src.aibrief.entity_visual_resolver import resolve_cuts_for_story, to_wiki_thumb, DOMAIN_POOLS

    # 1. Resolve authentic, story-specific visual cuts directly from active episode
    items = []
    active_path = os.path.join("src", "aibrief", "data", "active_episode.json")
    date_path = os.path.join("src", "aibrief", "data", f"{date_str}.json")
    chosen_file = active_path if os.path.exists(active_path) else (date_path if os.path.exists(date_path) else None)

    if chosen_file:
        try:
            with open(chosen_file, "r", encoding="utf-8") as f:
                ep_data = json.load(f)
            stories = ep_data.get("stories", [])
            print(f"[*] Resolving story-specific editorial visuals for {len(stories)} stories...")
            global_used = set()
            for idx, s in enumerate(stories, 1):
                cuts = resolve_cuts_for_story(
                    idx,
                    s.get("headline", ""),
                    s.get("summary", ""),
                    s.get("region", "WORLD"),
                    global_used_urls=global_used
                )
                for c_idx, (c_url, c_badge) in enumerate(cuts, 1):
                    items.append((f"s{idx}_cut{c_idx}.jpg", to_wiki_thumb(c_url), c_badge))
        except Exception as e:
            print(f"[!] Warning reading stories for dynamic visual resolution: {e}")

    if not items:
        raw_items = DAILY_VISUAL_MAP.get(date_str, DAILY_VISUAL_MAP["2026-09-28"])
        items = [(fn, to_wiki_thumb(u), b) for fn, u, b in raw_items]

    headers = {"User-Agent": "SanMitraNewsBot/1.0 (https://sanmitra.ai; newsdesk@sanmitra.ai)"}

    mgr = VisualMemoryManager()
    used_this_run = []
    category_counts = {}
    used_fallback_urls = set()

    import time
    for filename, url, badge in items:
        dest_file = os.path.join(dest_dir, filename)
        category = mgr.classify_visual_category(badge, url)
        print(f"[*] Processing visual: {filename} (Category: {category})...")

        time.sleep(0.3)  # Rate limit protection for Wikimedia/Unsplash
        success = False
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as r:
                data = r.read()
                im = Image.open(io.BytesIO(data)).convert("RGB")
                im = crop_and_grade(im)

                # Validate against 14-day pHash memory and diversity caps
                approved, cand_hash, rejection_reason = mgr.check_visual_candidate(
                    im, url, category, category_counts, current_date_str=date_str
                )

                if approved:
                    im.save(dest_file, quality=92)
                    category_counts[category] = category_counts.get(category, 0) + 1
                    print(f"    [+] APPROVED & SAVED (pHash: {cand_hash}, Category count: {category_counts[category]}/6): {dest_file}")
                    used_this_run.append({
                        "date": date_str,
                        "filename": filename,
                        "url": url,
                        "badge": badge,
                        "phash": cand_hash,
                        "category": category
                    })
                    success = True
                else:
                    print(f"    [!] REJECTED BY EDITORIAL VISUAL GATE: {rejection_reason}")
        except Exception as e:
            print(f"    [!] Error downloading from {url}: {e}")

        # If primary candidate failed or was rejected, apply guaranteed high-grade broadcast fallback
        if not success:
            print(f"    [*] Applying high-grade broadcast texture for {filename}...")
            lower_tag = f"{badge} {filename}".lower()
            if any(k in lower_tag for k in ["chip", "semiconductor", "wafer", "hardware", "soc", "bigendian", "veerai", "s10", "s13"]):
                pool_category = "hardware"
                local_fallback = "public/aibrief/assets/editorial/tech_silicon_wafer.jpg"
                fallback_badge = "ADVANCED SILICON DIE • FABRICATION CLEANROOM"
            elif any(k in lower_tag for k in ["defense", "missile", "radar", "military", "nato", "flank", "targeting", "drone", "cyber", "s1"]):
                pool_category = "defense"
                local_fallback = "public/aibrief/assets/story2_cyber_defense.jpg"
                fallback_badge = "DEFENSE OPERATIONS • LIVE TELEMETRY"
            elif any(k in lower_tag for k in ["datacenter", "datacentre", "cloud", "grid", "power", "bedrock", "s6"]):
                pool_category = "energy"
                local_fallback = "public/aibrief/assets/story6_datacenter_servers.jpg"
                fallback_badge = "HYPERSCALE COMPUTE • SERVER CLUSTER"
            elif any(k in lower_tag for k in ["research", "model", "bench", "eval", "vista", "mit", "s2", "s12"]):
                pool_category = "research"
                local_fallback = "public/aibrief/assets/editorial/tech_quantum_lab.jpg"
                fallback_badge = "FRONTIER AI RESEARCH • NEURAL HARNESS"
            else:
                pool_category = "policy"
                local_fallback = "public/aibrief/assets/editorial/gov_canberra_parliament.jpg"
                fallback_badge = "LEGISLATIVE OVERSIGHT • STATUTORY REVIEW"

            backup_pool = DOMAIN_POOLS.get(pool_category, DOMAIN_POOLS["policy"])
            for b_url, b_badge in backup_pool:
                if b_url in used_fallback_urls:
                    continue
                try:
                    time.sleep(0.2)
                    req = urllib.request.Request(b_url, headers=headers)
                    with urllib.request.urlopen(req, timeout=12) as r:
                        data = r.read()
                        im = Image.open(io.BytesIO(data)).convert("RGB")
                        im = crop_and_grade(im)
                        im.save(dest_file, quality=92)
                        b_hash = mgr.compute_phash(im)
                        used_fallback_urls.add(b_url)
                        print(f"    [+] Backup saved: {dest_file} ({b_badge})")
                        used_this_run.append({
                            "date": date_str,
                            "filename": filename,
                            "url": b_url,
                            "badge": b_badge,
                            "phash": b_hash,
                            "category": pool_category
                        })
                        success = True
                        break
                except Exception:
                    pass

            # Guaranteed local texture fallback so every single cut exists on disk
            if not success and os.path.exists(local_fallback):
                try:
                    shutil.copyfile(local_fallback, dest_file)
                    print(f"    [+] Local domain fallback applied: {dest_file} ({fallback_badge})")
                    used_this_run.append({
                        "date": date_str,
                        "filename": filename,
                        "url": local_fallback,
                        "badge": fallback_badge,
                        "phash": "local_fallback",
                        "category": pool_category
                    })
                    success = True
                except Exception as e:
                    print(f"    [!] Error copying local fallback: {e}")

    # Register in 14-day pHash visual memory
    if used_this_run:
        mgr.register_episode_visuals(date_str, used_this_run)
        print(f"\n[+] Visual memory updated with {len(used_this_run)} assets: {MEMORY_FILE}")
        print(f"[+] Category diversity distribution: {category_counts}")
        print(f"[+] All fresh visuals downloaded to: {dest_dir}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Broadcast date (YYYY-MM-DD)")
    parser.add_argument("--force", action="store_true", help="Force re-download of editorial stills even if present on disk")
    parser.add_argument("--retention-days", type=int, default=7, help="Number of past days of visual folders to retain (default: 7)")
    parser.add_argument("--cleanup-only", action="store_true", help="Only run cleanup of old and banned visuals without downloading")
    args = parser.parse_args()

    if args.cleanup_only:
        cleanup_old_visual_assets(args.date, retention_days=args.retention_days)
    else:
        download_daily_visuals(args.date, force=args.force, retention_days=args.retention_days)
