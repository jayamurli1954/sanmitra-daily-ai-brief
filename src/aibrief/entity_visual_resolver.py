"""
Dynamic Story-Aware Entity Visual Resolver for SanMitra AI News Wire.
Replaces generic/repeated stock imagery with authentic, contextual editorial visuals:
  - Resolves official entity photos (White House, Jay Clayton, Sam Altman, Justin Trudeau, Josephine Teo, etc.)
  - Resolves corporate headquarters (OpenAI, Tencent Seafront Tower, Alibaba Cloud, AMD, Google DeepMind, etc.)
  - Resolves geographical landmarks (Dalby Queensland, Singapore Skyline, New Jersey State House, IIT Madras, etc.)
  - Resolves domain-specific operational visuals (Ballistic missile launches, hyperscale datacenters, semiconductor cleanrooms)
  - Permanently bans unrelated stock assets (bounce-rate charts, student HTML code, coffee-shop laptops)
"""

import io
import json
import os
import re
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageEnhance, ImageOps

TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080

HEADERS = {
    "User-Agent": "SanMitraNewsBot/1.0 (https://sanmitra.ai; newsdesk@sanmitra.ai)"
}

def to_wiki_thumb(url: str, width: int = 1280) -> str:
    """Converts a Wikimedia Commons original file URL into a fast CDN thumbnail URL."""
    clean_url = url.split("?")[0]
    if "upload.wikimedia.org/wikipedia/commons/" in clean_url and "/thumb/" not in clean_url:
        parts = clean_url.split("/commons/")
        filename = parts[1].split("/")[-1]
        ext = filename.split(".")[-1].lower()
        if ext == "svg":
            return f"{parts[0]}/commons/thumb/{parts[1]}/{width}px-{filename}.png"
        return f"{parts[0]}/commons/thumb/{parts[1]}/{width}px-{filename}"
    elif "upload.wikimedia.org/wikipedia/commons/thumb/" in clean_url:
        if clean_url.lower().endswith(".svg"):
            return f"{clean_url}.png"
    return clean_url

# Curated high-res authentic editorial assets for common entities & topics
CURATED_ENTITY_MAP = {
    # Key political & tech leaders
    "jay clayton": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/7/70/Official_portrait_of_Jay_Clayton_%282026%29.jpg"), "OFFICIAL PORTRAIT • SIF CHAIR JAY CLAYTON"),
    "sam altman": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg"), "SAN FRANCISCO • SAM ALTMAN AI DOCTRINE"),
    "josephine teo": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/3f/Josephine_Teo_at_AsiaTech_X_Artificial_Intelligence_%28ATxAI%29%2C_Capella_Singapore%2C_31_May_2024_-_cropped.jpg"), "MINISTER JOSEPHINE TEO • AI SAFEGUARDS DESK"),
    "jensen huang": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/87/Jensen_Huang_at_Computex_2023.jpg"), "KEYNOTE STAGE • JENSEN HUANG NVIDIA"),
    "sundar pichai": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/d/d6/Sundar_pichai.png"), "EXECUTIVE BRIEFING • SUNDAR PICHAI ALPHABET"),
    "dario amodei": ("https://images.unsplash.com/photo-1544531586-fde5298cdd40?w=1920&q=85", "FRONTIER LABS DESK • DARIO AMODEI ANTHROPIC"),
    "justin trudeau": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/b/b6/Justin_Trudeau_2023_%28cropped%29.jpg"), "OFFICIAL ENGAGEMENT • CANADIAN FEDERAL DESK"),
    "mark carney": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/a/a2/Mark_Carney_2019.jpg"), "MACROECONOMIC AI SUMMIT • MARK CARNEY"),
    "nirmala sitharaman": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/38/Smt._Nirmala_Sitharaman_taking_charge_as_the_Union_Minister_for_Finance_%26_Corporate_Affairs%2C_in_New_Delhi_on_June_12%2C_2024_%28cropped%29.jpg"), "NEW DELHI • UNION FINANCE MINISTER SITHARAMAN"),

    # Institutions & Government
    "white house": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/1d/White_House_north_and_south_sides.jpg"), "WASHINGTON D.C. • THE WHITE HOUSE BRIEFING"),
    "capitol hill": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/4/4f/United_States_Capitol_west_front_edit2.jpg"), "CAPITOL HILL • FEDERAL REGULATORY COMMITTEE"),
    "canada parliament": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/b/b5/Ottawa_-_ON_-_Stadtansicht.jpg"), "PARLIAMENT HILL • OTTAWA FEDERAL COMMERCE"),
    "parliament hill": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/b/b5/Ottawa_-_ON_-_Stadtansicht.jpg"), "PARLIAMENT HILL • CANADIAN POLICY DESK"),
    "new jersey": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/83/New_Jersey_State_House.jpg"), "TRENTON • NEW JERSEY STATE HOUSE"),
    "trenton": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/83/New_Jersey_State_House.jpg"), "TRENTON • NEW JERSEY GOVERNMENT COMPLEX"),
    "iit madras": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/c6/Facade_of_IIT_Madras_%28cropped%29.jpg"), "CHENNAI • IIT MADRAS RESEARCH CAMPUS"),
    "meity": ("https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1920&q=85", "NEW DELHI • INDIA SOVEREIGN AI INITIATIVE"),
    "sovereign ai": ("https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1920&q=85", "NEW DELHI • INDIA SOVEREIGN AI INITIATIVE"),
    "indian industry": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/c6/Facade_of_IIT_Madras_%28cropped%29.jpg"), "CHENNAI • IIT MADRAS RESEARCH CAMPUS"),

    # Corporations & Headquarters
    "openai": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/a/a7/1515_Third_Street.jpg"), "MISSION BAY • OPENAI HEADQUARTERS"),
    "google deepmind": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/4/4b/Platform_37_-_2026-04-25_2.jpg"), "KING'S CROSS • GOOGLE DEEPMIND CAMPUS"),
    "google": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/32/Googleplex_HQ_%28cropped%29.jpg"), "MOUNTAIN VIEW • GOOGLEPLEX HEADQUARTERS"),
    "tencent": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/cd/Tencent_Seafront_Tower_in_Dec2020.jpg"), "SHENZHEN • TENCENT SEAFRONT TOWERS"),
    "alibaba": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/39/Phase_4_of_Alibaba_Xixi_Park_20200913.jpg"), "HANGZHOU • ALIBABA CLOUD XIXI CAMPUS"),
    "amd": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/11/2485_Augustine_Drive_headquarters_in_Santa_Clara%2C_California.jpg"), "SANTA CLARA • AMD CORPORATE HEADQUARTERS"),
    "spacex": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/83/SpaceX_Headquarters_Hawthorne_California.jpg"), "HAWTHORNE • SPACEX HEADQUARTERS & TELEMETRY"),

    # Cities & Regions
    "dalby": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/d/d3/Dalby_aerial.jpg"), "WESTERN DOWNS • DALBY RURAL REGION"),
    "queensland": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/d/d3/Dalby_aerial.jpg"), "QUEENSLAND • REGIONAL ENERGY & COMPUTE CORRIDOR"),
    "singapore": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/b/b6/Skyline_of_Singapore_Central_Business_District_20250903.jpg"), "SINGAPORE • CENTRAL BUSINESS DISTRICT SKYLINE"),
    "pyongyang": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/e/e7/The_Arch_of_Triumph_%2811360607534%29.jpg"), "PYONGYANG • STRATEGIC MILITARY COMMAND"),
    "bengaluru": ("https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1920&q=85", "BENGALURU • INDIA SOVEREIGN TECH CAPITAL"),
    "guwahati": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/11/Guwahati_citysky.jpg"), "GUWAHATI • NORTHEAST INDIA TECH PARK"),

    # Direct military / domain topics
    "north korea missile": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/35/North_Korea%27s_ballistic_missile_-_North_Korea_Victory_Day-2013_01.jpg"), "PYONGYANG • STRATEGIC BALLISTIC MISSILE"),
    "ballistic missile": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/35/North_Korea%27s_ballistic_missile_-_North_Korea_Victory_Day-2013_01.jpg"), "BALLISTIC TRAJECTORY • FLIGHT DYNAMICS"),
    "data center": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/57/Data_Center_of_CNPC.jpg"), "HYPERSCALE AI CLUSTER • FACILITY DEPLOYMENT"),
    "datacentre": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/57/Data_Center_of_CNPC.jpg"), "HYPERSCALE AI CLUSTER • FACILITY DEPLOYMENT"),

    # Story-specific 2026-10-06 entities
    "nato": ("https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1920&q=85", "BRUSSELS • NATO EASTERN FLANK DEFENSE DOCTRINE"),
    "eastern flank": ("https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1920&q=85", "EASTERN EUROPE • AUTONOMOUS SENSOR-TO-SHOOTER GRID"),
    "mit": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/0/03/MIT_Building_10_and_the_Great_Dome%2C_Cambridge_MA.jpg"), "CAMBRIDGE • MIT COMPUTER SCIENCE & AI LAB"),
    "kaiming he": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/0/03/MIT_Building_10_and_the_Great_Dome%2C_Cambridge_MA.jpg"), "MIT CSAIL • VISTA VISUAL HARNESS BENCHMARK"),
    "norway": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/c5/Stortinget_August_2019_01.jpg"), "OSLO • NORWEGIAN PARLIAMENT STORTINGET"),
    "new york city": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/10/Empire_State_Building_%28aerial_view%29.jpg"), "NEW YORK CITY • MUNICIPAL AI GOVERNANCE COUNCIL"),
    "new york": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/10/Empire_State_Building_%28aerial_view%29.jpg"), "NEW YORK CITY • CIVIC & MUNICIPAL REGULATION"),
    "south korea": ("https://images.unsplash.com/photo-1538485399081-7191377e8241?w=1920&q=85", "SEOUL • SOUTH KOREA SOVEREIGN FRONTIER AI"),
    "korea": ("https://images.unsplash.com/photo-1538485399081-7191377e8241?w=1920&q=85", "SEOUL • 10K GPU SOVEREIGN COMPUTE PROJECT"),
    "bank of japan": ("https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=1920&q=85", "TOKYO • BANK OF JAPAN MONETARY INTELLIGENCE"),
    "bigendian": ("https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=85", "BENGALURU • PROJECT VEERAI INDIGENOUS VISION CHIP"),
    "accenture": ("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1920&q=85", "MUMBAI • ENTERPRISE AI SYSTEMS INTEGRATION"),
    "am intelligence": ("https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1920&q=85", "HYPERSCALE COMPUTE • 20K NVIDIA GPU EXPANSION"),
    "aleph alpha": ("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&q=85", "HEIDELBERG • ALEPH ALPHA EUROPEAN SOVEREIGN AI")
}

# Domain-specific B-roll pools (High-grade authentic editorial TV shots, NEVER bounce rate charts)
DOMAIN_POOLS = {
    "defense": [
        ("https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1920&q=85", "RADAR SURVEILLANCE • AIR-DEFENSE ENVELOPE"),
        ("https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=85", "ORBITAL TELEMETRY • SATELLITE TRACKING GRID"),
        ("https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1920&q=85", "MILITARY OPERATIONS CENTER • INCIDENT DESK")
    ],
    "policy": [
        ("https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=1920&q=85", "MULTILATERAL FORUM • REGULATORY HARMONIZATION"),
        ("https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1920&q=85", "STANDARDS AUDITING • COMPLIANCE FRAMEWORK"),
        ("https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1920&q=85", "MINISTERIAL ENGAGEMENT • SOVEREIGN PACT"),
        ("https://images.unsplash.com/photo-1450133064473-71024230f91b?w=1920&q=85", "REGULATORY OVERSIGHT • JUDICIAL INQUIRY"),
        ("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1920&q=85", "METROPOLITAN CIVIC CENTER • ETHICS DESK")
    ],
    "hardware": [
        ("https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=85", "ADVANCED SILICON DIE • FABRICATION CLEANROOM"),
        ("https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1920&q=85", "HIGH-DENSITY GPU RACKS • THERMAL MANAGEMENT"),
        ("https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1920&q=85", "SUPERCOMPUTING BACKBONE • TENSOR CLUSTERS"),
        ("https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1920&q=85", "HARDWARE ACCELERATION • SYSTEM INTEGRATION")
    ],
    "research": [
        ("https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=1920&q=85", "NEURAL BENCHMARKING • RECURSIVE EVALUATION HUD"),
        ("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&q=85", "AGENT HARNESS AUDIT • SCAFFOLD VERIFICATION"),
        ("https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=1920&q=85", "RESEARCH SCIENTISTS • ALGORITHMIC GOVERNANCE"),
        ("https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1920&q=85", "DEVELOPER PLATFORM • MULTI-AGENT WORKSPACE"),
        ("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1920&q=85", "DIGITAL TELEMETRY • SYSTEM EVALUATION")
    ],
    "energy": [
        ("https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1920&q=85", "REGIONAL POWER GRID • SUBSTATION TELEMETRY"),
        ("https://images.unsplash.com/photo-1509391365360-2e959784a276?w=1920&q=85", "RENEWABLE UTILITY • HIGH-VOLTAGE TRANSMISSION"),
        ("https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=1920&q=85", "TERRAIN SURVEY • RURAL INFRASTRUCTURE")
    ]
}


def crop_and_grade(im: Image.Image) -> Image.Image:
    im = ImageOps.fit(im, (TARGET_WIDTH, TARGET_HEIGHT), method=Image.Resampling.LANCZOS)
    enhancer_contrast = ImageEnhance.Contrast(im)
    im = enhancer_contrast.enhance(1.08)
    enhancer_color = ImageEnhance.Color(im)
    im = enhancer_color.enhance(1.05)
    return im


def search_wikipedia_image(query: str) -> Optional[Tuple[str, str]]:
    """Fetches high-resolution lead image from Wikipedia for a named entity."""
    url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrlimit=3&prop=pageimages&piprop=original|thumbnail&pithumbsize=1920&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for pid, p in pages.items():
                src = p.get("original", {}).get("source") or p.get("thumbnail", {}).get("source")
                if src and not src.lower().endswith(".svg") and not src.lower().endswith(".gif"):
                    title = p.get("title", query)
                    return to_wiki_thumb(src), title
    except Exception:
        pass
    return None


def resolve_cuts_for_story(
    idx: int,
    headline: str,
    summary: str,
    region: str,
    global_used_urls: Optional[set] = None
) -> List[Tuple[str, str]]:
    """
    Returns 3 distinct (url, badge) visual cuts tailored directly to the story's real content.
    """
    text = f"{headline} {summary}".lower()
    cuts = []

    # 1. Match curated entities first
    for key, (img_url, badge) in CURATED_ENTITY_MAP.items():
        if key in text and len(cuts) < 2:
            if not any(c[0] == img_url for c in cuts):
                cuts.append((img_url, badge))

    # 2. If no entity matched yet, try live Wikipedia image search for leading capitalized terms
    if not cuts:
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', headline)
        for ent in entities:
            if ent.lower() in ("daily", "brief", "news", "special", "report", "wire", "monday", "tuesday"):
                continue
            wiki_res = search_wikipedia_image(ent)
            if wiki_res:
                src, title = wiki_res
                badge = f"{title.upper()} • CONTEXTUAL REPORTING"
                cuts.append((src, badge))
                break

    # 3. Determine domain for complementary operational B-roll
    domain = "policy"
    if any(k in text for k in ["missile", "military", "weapon", "warhead", "pyongyang", "air-defense", "ballistic"]):
        domain = "defense"
    elif any(k in text for k in ["datacentre", "data center", "grid", "power", "energy", "substation", "hectare"]):
        domain = "energy"
    elif any(k in text for k in ["chip", "semiconductor", "amd", "nvidia", "gpu", "hardware", "wafer", "silicon"]):
        domain = "hardware"
    elif any(k in text for k in ["research", "rrsi", "benchmark", "foundation model", "eval"]):
        domain = "research"

    pool = DOMAIN_POOLS.get(domain, DOMAIN_POOLS["policy"])

    # Pick from domain pool avoiding URLs already used across this story or episode
    for pool_url, pool_badge in pool:
        if len(cuts) >= 3:
            break
        if not any(c[0] == pool_url for c in cuts):
            if global_used_urls is not None and pool_url in global_used_urls:
                continue
            cuts.append((pool_url, pool_badge))
            if global_used_urls is not None:
                global_used_urls.add(pool_url)

    # Pad with any domain pools if still under 3
    if len(cuts) < 3:
        for backup_domain in ["policy", "hardware", "research", "energy"]:
            for pool_url, pool_badge in DOMAIN_POOLS[backup_domain]:
                if len(cuts) >= 3:
                    break
                if not any(c[0] == pool_url for c in cuts):
                    if global_used_urls is not None and pool_url in global_used_urls:
                        continue
                    cuts.append((pool_url, pool_badge))
                    if global_used_urls is not None:
                        global_used_urls.add(pool_url)

    return cuts[:3]


def download_and_process_image(url: str, dest_path: str) -> bool:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
            im = Image.open(io.BytesIO(data)).convert("RGB")
            im = crop_and_grade(im)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            im.save(dest_path, quality=92)
            return True
    except Exception as e:
        print(f"  [!] Failed to download {url}: {e}")
        return False
