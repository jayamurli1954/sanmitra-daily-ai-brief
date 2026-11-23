"""
Dynamic Story-Aware Entity Visual Resolver for SanMitra AI News Wire.
Replaces generic/repeated stock imagery with authentic, contextual editorial visuals:
  - Resolves official entity photos (White House, Jay Clayton, Sam Altman, Justin Trudeau, Josephine Teo, Lisa Su, Cantwell, etc.)
  - Resolves corporate headquarters (OpenAI, Tencent Seafront Tower, Alibaba Cloud, AMD, Google DeepMind, Boston Dynamics, etc.)
  - Resolves institutions by their own buildings (New Jersey State House, IIT Madras, the Pentagon, etc.)
  - No topic words ("drone", "gpu", "data center") and no stand-in buildings: an entity with no
    verified photo of its own gets its Wikipedia lead image or an approved fallback (AGENTS.md section 2)
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

def to_wiki_thumb(url: Optional[str], width: int = 1280) -> str:
    """Converts a Wikimedia Commons or Wikipedia original file URL into a fast CDN thumbnail URL."""
    if not url:
        return ""
    clean_url = url.split("?")[0]
    for domain in ("/commons/", "/en/"):
        if f"upload.wikimedia.org/wikipedia{domain}" in clean_url and "/thumb/" not in clean_url:
            parts = clean_url.split(domain)
            filename = parts[1].split("/")[-1]
            ext = filename.split(".")[-1].lower()
            if ext == "svg":
                return f"{parts[0]}{domain}thumb/{parts[1]}/{width}px-{filename}.png"
            return f"{parts[0]}{domain}thumb/{parts[1]}/{width}px-{filename}"
        elif f"upload.wikimedia.org/wikipedia{domain}thumb/" in clean_url:
            if clean_url.lower().endswith(".svg"):
                return f"{clean_url}.png"
    return clean_url

# Curated high-res authentic editorial assets for common entities & topics
CURATED_ENTITY_MAP = {
    # Key political & tech leaders
    "jay clayton": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/7/70/Official_portrait_of_Jay_Clayton_%282026%29.jpg"), "JAY CLAYTON"),
    "sam altman": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg"), "SAM ALTMAN"),
    "josephine teo": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/3f/Josephine_Teo_at_AsiaTech_X_Artificial_Intelligence_%28ATxAI%29%2C_Capella_Singapore%2C_31_May_2024_-_cropped.jpg"), "JOSEPHINE TEO"),
    "jensen huang": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/c8/Jensen_Huang_Stanford_2026-04-30_010_%28cropped%29.jpg"), "JENSEN HUANG"),
    "sundar pichai": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/d/d6/Sundar_pichai.png"), "SUNDAR PICHAI"),
    "justin trudeau": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/b/b6/Justin_Trudeau_2023_%28cropped%29.jpg"), "JUSTIN TRUDEAU"),
    "mark carney": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/a/a2/Mark_Carney_2019.jpg"), "MARK CARNEY"),
    "nirmala sitharaman": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/38/Smt._Nirmala_Sitharaman_taking_charge_as_the_Union_Minister_for_Finance_%26_Corporate_Affairs%2C_in_New_Delhi_on_June_12%2C_2024_%28cropped%29.jpg"), "NIRMALA SITHARAMAN"),
    "lisa su": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/d/de/SXSW-2024-alih-OB7A0861-Lisa_Su_%28cropped_2%29.jpg"), "LISA SU"),
    "ashwini vaishnaw": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/35/Ashwini_Vaishnaw_cropped.jpg"), "ASHWINI VAISHNAW"),
    "vaishnaw": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/35/Ashwini_Vaishnaw_cropped.jpg"), "ASHWINI VAISHNAW"),
    "charlton": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/b/b6/Parliament_House_at_dusk%2C_Canberra_ACT.jpg"), "CANBERRA • ASSISTANT MINISTER ANDREW CHARLTON"),
    "stampe": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/7/7c/Christiansborg_Slot_Copenhagen_2014_01.jpg"), "COPENHAGEN • DANISH CULTURE MINISTRY"),
    "albanese": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/7/7b/Anthony_Albanese_portrait_%28re-crop%29.jpg"), "ANTHONY ALBANESE"),
    "anthony albanese": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/7/7b/Anthony_Albanese_portrait_%28re-crop%29.jpg"), "ANTHONY ALBANESE"),

    # Institutions & Government
    "white house": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/1d/White_House_north_and_south_sides.jpg"), "WASHINGTON D.C. • THE WHITE HOUSE BRIEFING"),
    "genesis mission": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/1d/White_House_north_and_south_sides.jpg"), "WASHINGTON D.C. • WHITE HOUSE GENESIS MISSION"),
    "capitol hill": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/9/9f/US_Capitol_east_side.JPG"), "CAPITOL HILL • FEDERAL REGULATORY COMMITTEE"),
    "us senate": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/9/9f/US_Capitol_east_side.JPG"), "WASHINGTON D.C. • US SENATE COMMERCE COMMITTEE"),
    "senate": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/9/9f/US_Capitol_east_side.JPG"), "WASHINGTON D.C. • US SENATE COMMERCE COMMITTEE"),
    "pentagon": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/2/2a/The_Pentagon%2C_Headquarters_of_the_US_Department_of_Defense_%28cropped2%29.jpg"), "ARLINGTON • THE PENTAGON HEADQUARTERS"),
    "canberra": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/b/b6/Parliament_House_at_dusk%2C_Canberra_ACT.jpg"), "CANBERRA • AUSTRALIAN PARLIAMENT HOUSE"),
    "copenhagen": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/7/7c/Christiansborg_Slot_Copenhagen_2014_01.jpg"), "COPENHAGEN • CHRISTIANSBORG PALACE"),
    "canada parliament": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/b/b5/Ottawa_-_ON_-_Stadtansicht.jpg"), "PARLIAMENT HILL • OTTAWA FEDERAL COMMERCE"),
    "parliament hill": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/b/b5/Ottawa_-_ON_-_Stadtansicht.jpg"), "PARLIAMENT HILL • CANADIAN POLICY DESK"),
    "new jersey": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/83/New_Jersey_State_House.jpg"), "TRENTON • NEW JERSEY STATE HOUSE"),
    "trenton": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/83/New_Jersey_State_House.jpg"), "TRENTON • NEW JERSEY GOVERNMENT COMPLEX"),
    "iit madras": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/c6/Facade_of_IIT_Madras_%28cropped%29.jpg"), "CHENNAI • IIT MADRAS RESEARCH CAMPUS"),
    "mas": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/8c/Monetary_Authority_of_Singapore_2.jpg"), "SINGAPORE • MONETARY AUTHORITY OF SINGAPORE"),
    "monetary authority of singapore": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/8c/Monetary_Authority_of_Singapore_2.jpg"), "SINGAPORE • MONETARY AUTHORITY OF SINGAPORE"),
    # Corporations & Laboratories
    "databricks": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/160_Spear_Street_from_across_Spear.jpg/1280px-160_Spear_Street_from_across_Spear.jpg"), "SAN FRANCISCO • DATABRICKS HEADQUARTERS"),
    "spotify": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/1024px-Spotify_logo_without_text.svg.png"), "SPOTIFY GLOBAL • ENTERPRISE STRATEGY"),
    "daniel ek": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Daniel_Ek_EC_2025_%28cropped%29.jpg/1280px-Daniel_Ek_EC_2025_%28cropped%29.jpg"), "DANIEL EK"),
    "oracle": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Oracle_Corporation_headquarters_in_Redwood_City.jpg/1280px-Oracle_Corporation_headquarters_in_Redwood_City.jpg"), "ORACLE CLOUD INFRASTRUCTURE • WORLD HEADQUARTERS"),
    "sec": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Securities_and_Exchange_Commission_headquarters.jpg/1280px-Securities_and_Exchange_Commission_headquarters.jpg"), "WASHINGTON DC • US SECURITIES & EXCHANGE COMMISSION"),
    "securities and exchange commission": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Securities_and_Exchange_Commission_headquarters.jpg/1280px-Securities_and_Exchange_Commission_headquarters.jpg"), "WASHINGTON DC • US SECURITIES & EXCHANGE COMMISSION"),
    "openai": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/a/a7/1515_Third_Street.jpg"), "MISSION BAY • OPENAI HEADQUARTERS"),
    "gpt-6": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/a/a7/1515_Third_Street.jpg"), "OPENAI • GPT-6 FRONTIER MODEL CANVAS"),
    "intelligent ui": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/a/a7/1515_Third_Street.jpg"), "CHATGPT • INTELLIGENT UI INTERACTION"),
    "google deepmind": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/4/4b/Platform_37_-_2026-04-25_2.jpg"), "KING'S CROSS • GOOGLE DEEPMIND CAMPUS"),
    "synthid": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/4/4b/Platform_37_-_2026-04-25_2.jpg"), "GOOGLE DEEPMIND • SYNTHID WATERMARK DETECTOR"),
    "google": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/32/Googleplex_HQ_%28cropped%29.jpg"), "MOUNTAIN VIEW • GOOGLEPLEX HEADQUARTERS"),
    "google cloud": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/32/Googleplex_HQ_%28cropped%29.jpg"), "GOOGLE CLOUD • ENTERPRISE AI CAMPUS"),
    "gemini agent": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/32/Googleplex_HQ_%28cropped%29.jpg"), "GOOGLE CLOUD • GEMINI AGENT WORKSPACE"),
    "tencent": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/cd/Tencent_Seafront_Tower_in_Dec2020.jpg"), "SHENZHEN • TENCENT SEAFRONT TOWERS"),
    "workbuddy": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/cd/Tencent_Seafront_Tower_in_Dec2020.jpg"), "SHENZHEN • TENCENT WORKBUDDY AI FILE OS"),
    "qantas": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/d/d1/Qantas_%28VH-ZNN%29_Boeing_787-9_Dreamliner_on_final_at_Melbourne_Airport_%281%29.jpg"), "SYDNEY • QANTAS FLEET OPERATIONS"),
    "hugging face": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/e/ea/Hugging_Face_logo.svg"), "OPEN SCIENCE • HUGGING FACE PLATFORM"),
    "red hat": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/d/d8/Red_Hat_logo.svg"), "RALEIGH • RED HAT ENTERPRISE SYSTEMS"),
    "openshift": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/d/d8/Red_Hat_logo.svg"), "HYBRID CLOUD • OPENSHIFT 5 RUNTIME"),
    "alibaba": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/39/Phase_4_of_Alibaba_Xixi_Park_20200913.jpg"), "HANGZHOU • ALIBABA CLOUD XIXI CAMPUS"),
    "amd": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/11/2485_Augustine_Drive_headquarters_in_Santa_Clara%2C_California.jpg"), "SANTA CLARA • AMD CORPORATE HEADQUARTERS"),
    "boston dynamics": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/9/9b/Atlas_during_testing.jpg"), "WALTHAM • BOSTON DYNAMICS ROBOTICS LAB"),
    "apple": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/5a/Aerial_view_of_Apple_Park_dllu.jpg"), "CUPERTINO • APPLE PARK"),
    "meta": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/7/7c/Meta_Platforms_Headquarters_Menlo_Park_California.jpg"), "MENLO PARK • META HEADQUARTERS"),
    "disney": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/32/Walt_Disney_Studios_Alameda_Entrance.jpg"), "BURBANK • WALT DISNEY STUDIOS"),
    "microsoft": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/6/64/Microsoft_Redmond_Campus_redevelopment_aerial_view%2C_Sept._2021.jpg"), "REDMOND • MICROSOFT REDMOND CAMPUS"),
    "samsung": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/e/e2/Samsung_headquarters.jpg"), "SUWON • SAMSUNG DIGITAL CITY HEADQUARTERS"),
    "samsung electronics": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/e/e2/Samsung_headquarters.jpg"), "SUWON • SAMSUNG ELECTRONICS HEADQUARTERS"),
    "yandex": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/a/ad/Yandex_main_office.jpg"), "MOSCOW • YANDEX CLOUD COMPUTING HEADQUARTERS"),
    "amie": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/32/Googleplex_HQ_%28cropped%29.jpg"), "GOOGLE HEALTH CLINICAL AI • AMIE EVALUATION"),
    # Direct military & aerospace defense systems
    "north korea missile": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/35/North_Korea%27s_ballistic_missile_-_North_Korea_Victory_Day-2013_01.jpg"), "PYONGYANG • STRATEGIC BALLISTIC MISSILE"),
    # Cybersecurity & Banking
    # Research & Universities
    "george washington university": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/7/71/George_Washington_University_School_of_Engineering_and_Applied_Science_%2855266857738%29.jpg"), "WASHINGTON D.C. • GWU SCIENCE & ENGINEERING"),
    "gwu": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/7/71/George_Washington_University_School_of_Engineering_and_Applied_Science_%2855266857738%29.jpg"), "WASHINGTON D.C. • GWU SCIENCE & ENGINEERING"),
    "mit": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/0/03/MIT_Building_10_and_the_Great_Dome%2C_Cambridge_MA.jpg"), "CAMBRIDGE • MIT COMPUTER SCIENCE & AI LAB"),
    "kaiming he": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/0/03/MIT_Building_10_and_the_Great_Dome%2C_Cambridge_MA.jpg"), "MIT CSAIL • VISTA VISUAL HARNESS BENCHMARK"),
    # Cities & Regions
    "nvidia": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/cc/Nvidia_HQ.jpg"), "SANTA CLARA • NVIDIA CORPORATE HEADQUARTERS"),
    "siemens": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/2/2c/Siemens_AG_-_Corporate_Headquarters%2C_Munich_02.jpg"), "MUNICH • SIEMENS GLOBAL HEADQUARTERS"),
    "citibank": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/39/388_Greenwich_Street_%2824252%29.jpg"), "NEW YORK • CITIGROUP GLOBAL HEADQUARTERS"),
    "citi": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/39/388_Greenwich_Street_%2824252%29.jpg"), "NEW YORK • CITIGROUP GLOBAL HEADQUARTERS"),
    "gift city": ("https://upload.wikimedia.org/wikipedia/commons/9/93/Gift_City.jpg", "GUJARAT • GIFT CITY INTERNATIONAL FINANCIAL TECH-CITY")
}

# Keys whose image is a person (or captioned with one). A person appears only when
# named in the headline or at least twice in the story (AGENTS.md section 2).
PERSON_KEYS = {
    "jay clayton", "sam altman", "josephine teo", "jensen huang", "sundar pichai", "justin trudeau",
    "mark carney", "nirmala sitharaman", "lisa su", "ashwini vaishnaw", "vaishnaw", "charlton",
    "stampe", "albanese", "anthony albanese", "daniel ek", "kaiming he",
}

# Domain-specific B-roll pools (100% authentic editorial visuals, NO server cables, NO plasma balls, NO toy drones)
# Stand-in stills for cuts the story itself cannot supply. Only generic,
# location-free images: a named place here (Canberra, Capitol Hill, Samsung HQ)
# ended up captioned as the setting of unrelated stories.
DOMAIN_POOLS = {
    "cyber": [
        (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/5a/NSOC-2012.jpg"), "SECURITY OPERATIONS • INCIDENT RESPONSE SOC"),
        ("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&q=85", "CYBER THREAT OPERATIONS • LIVE TELEMETRY"),
        ("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1920&q=85", "NETWORK SECURITY DESK • ACCESS LOG AUDIT"),
        ("https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1920&q=85", "INFORMATION SECURITY & DATA AUDITING")
    ],
    "defense": [
        (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/5a/NSOC-2012.jpg"), "TACTICAL OPERATIONS CENTER • INCIDENT DESK"),
        ("https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=1920&q=85", "DEFENSE RESEARCH LAB • AUTONOMOUS GUIDANCE"),
        (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/2/2f/U-s-service-members-stand-by-a-patriot-missile-battery-in-gaziantep-turkey.jpg"), "AIR DEFENSE • PATRIOT RADAR BATTERY"),
        ("https://images.unsplash.com/photo-1563770660941-20978e870e26?w=1920&q=85", "AEROSPACE TELEMETRY • RADAR MONITORING GRID")
    ],
    "policy": [
        ("https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=1920&q=85", "MULTILATERAL FORUM • REGULATORY HARMONIZATION"),
        ("https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1920&q=85", "STANDARDS AUDITING • COMPLIANCE FRAMEWORK"),
        ("https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1920&q=85", "REGULATORY OVERSIGHT • JUDICIAL INQUIRY"),
        ("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1920&q=85", "METROPOLITAN CIVIC CENTER • ETHICS DESK")
    ],
    "hardware": [
        (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/9/95/Aerial_photograph_of_Globalfoundries_Dresden.jpg"), "SEMICONDUCTOR FAB • ADVANCED FOUNDRY"),
        (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/57/Data_Center_of_CNPC.jpg"), "HYPERSCALE AI CLUSTER • SERVER INFRASTRUCTURE"),
        ("https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=85", "ADVANCED SILICON DIE • FABRICATION CLEANROOM"),
        ("https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1920&q=85", "HIGH-DENSITY GPU RACKS • THERMAL MANAGEMENT"),
        ("https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1920&q=85", "SUPERCOMPUTING BACKBONE • TENSOR CLUSTERS"),
        ("https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1920&q=85", "HARDWARE ACCELERATION • SYSTEM INTEGRATION"),
        ("https://images.unsplash.com/photo-1555680202-c86f0e12f086?w=1920&q=85", "SEMICONDUCTOR WAFER • ADVANCED PACKAGING")
    ],
    "research": [
        ("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&q=85", "AGENT HARNESS AUDIT • SCAFFOLD VERIFICATION"),
        ("https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=1920&q=85", "RESEARCH SCIENTISTS • ALGORITHMIC GOVERNANCE"),
        ("https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1920&q=85", "DEVELOPER PLATFORM • MULTI-AGENT WORKSPACE"),
        ("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1920&q=85", "DIGITAL TELEMETRY • SYSTEM EVALUATION"),
        ("https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=1920&q=85", "LABORATORY INSTRUMENTATION • MODEL EVALUATION"),
        ("https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=1920&q=85", "DEEP LEARNING PIPELINE • KERNEL TRACING")
    ],
    "energy": [
        (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/57/Data_Center_of_CNPC.jpg"), "HYPERSCALE FACILITY • CLOUD INFRASTRUCTURE"),
        ("https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1920&q=85", "REGIONAL POWER GRID • SUBSTATION TELEMETRY"),
        ("https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1920&q=85", "HIGH-VOLTAGE DATACENTER • MEGAWATT CLUSTER"),
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


BANNED_WIKI_KEYWORDS = [
    "polygon", "diagram", "election", "survey", "schema", "attack", "storming", "protest",
    "beer", "carlsberg", "tuborg", "alcohol", "oil_on_canvas",
    "sailing", "frigate", "hermione", "manga", "anime", "cartoon", "comic", "drawing",
    "temple", "mosque", "church", "sculpture", "statue", "monument",
    # Maps, flags and scenery are not story visuals (AGENTS.md section 1).
    "map", "flag", "locator", "orthographic", "coat_of_arms", "emblem", "seal_of",
    "lake", "river", "beach", "mountain", "landscape", "panorama", "satellite",
]


_CORP_SUFFIXES = {"inc", "corp", "corporation", "ltd", "limited", "group", "holdings", "company", "co",
                  "technologies", "platforms", "systems", "plc", "llc", "ag", "sa"}


def _title_matches(query: str, title: str) -> bool:
    """The page must be the thing searched for. Search results alone gave
    "WindBorne" -> "Aeolian processes", "Haven" -> "Jack Haven", "Mac" -> "Fleetwood Mac"."""
    def words(text):
        return [w for w in re.findall(r"[a-z0-9]+", text.lower().replace(".", ""))]
    q = words(query)
    t = [w for w in words(re.sub(r"\([^)]*\)", " ", title)) if w not in _CORP_SUFFIXES]
    if not q or not t:
        return False
    if t == q:
        return True
    # Acronyms: "IMF" -> "International Monetary Fund"
    if len(q) == 1 and query.isupper() and len(query) >= 2:
        initials = "".join(w[0] for w in t if w not in ("of", "and", "the", "for"))
        return initials == q[0]
    return False


def search_wikipedia_image(query: str) -> Optional[Tuple[str, str]]:
    """Fetches high-resolution lead image from Wikipedia for a named entity with strict negative filtering."""
    q_lower = query.lower().strip()
    # Query disambiguation
    if q_lower == "pentagon":
        query = "The Pentagon"
    elif q_lower in ("senate", "us senate"):
        query = "United States Senate"
    elif q_lower in ("harmattan", "irifi"):
        query = "Unmanned aerial vehicle"
    elif q_lower in ("lisa su", "su"):
        query = "Lisa Su"

    url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrlimit=4&prop=pageimages&piprop=original|thumbnail&pithumbsize=1920&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for pid, p in pages.items():
                title = p.get("title", query)
                src = p.get("original", {}).get("source") or p.get("thumbnail", {}).get("source")
                if not src:
                    continue
                src_lower = src.lower()
                title_lower = title.lower()

                # "Mia (given name)", "Character (arts)", "Study (room)": a page about
                # the word, not the subject. Company and product pages are fine.
                paren = re.search(r"\(([^)]*)\)", title_lower)
                if paren and paren.group(1) not in ("company", "software", "website", "app", "organization", "brand", "chatbot", "programming language"):
                    continue
                if title_lower.startswith("list of") or "disambiguation" in title_lower:
                    continue
                if not _title_matches(query, title):
                    continue

                # Exclude diagrams, election maps, polygons, beers, paintings, manga
                if any(k in src_lower or k in title_lower for k in BANNED_WIKI_KEYWORDS):
                    continue
                if src_lower.endswith(".gif"):
                    continue

                return to_wiki_thumb(src), title
    except Exception:
        pass
    return None


# Capitalised words that are not names: headline words in sentence or title case,
# roles, and demonyms. "Indian states" found the Indian Army, "Study" found
# "Study (room)", "Actress Mia Goth" should look up "Mia Goth".
_NOT_NAMES = {
    "a", "an", "the", "and", "or", "of", "for", "to", "in", "on", "at", "by", "with", "from", "as", "after",
    "over", "into", "than", "that", "this", "these", "its", "it", "is", "are", "be", "how", "why", "what",
    "who", "when", "new", "first", "more", "most", "ai", "says", "say", "said", "warns", "warn",
    "launches", "launch", "unveils", "unveil", "raises", "raise", "files", "wins", "win", "rush", "rushes",
    "details", "backs", "back", "finds", "find", "seeks", "plans", "calls", "urges", "slide", "slides",
    "move", "moves", "closer", "lead", "leads", "set", "sets", "gets", "may", "could", "will", "can",
    "study", "report", "reports", "actress", "actor", "investors", "investor", "chip", "chips", "stocks",
    "shares", "startup", "start-up", "startups", "firm", "company", "boss", "ceo", "ceos", "minister",
    "president", "chief", "government", "state", "states", "city", "police", "court", "team", "models",
    "model", "agents", "agent", "autonomous", "combat", "jets", "drone", "drones", "language", "personal",
    "smart", "home", "devices", "funding", "fund", "deal", "data", "tech", "technology", "global",
    "national", "daily", "brief", "news", "special", "monday", "tuesday", "wednesday", "thursday", "friday",
    "saturday", "sunday", "breaking", "exclusive", "update", "analysis",
}
_DEMONYM = re.compile(r"(?:ian|ese|ish|ean|ani)$")
_SUFFIXED = re.compile(r"-(?:backed|based|led|funded|owned|founded|built|made|style|like)$", re.IGNORECASE)
_WORD = re.compile(r"[A-Za-z0-9][\w.&'’-]*")


def headline_entities(headline: str) -> List[str]:
    """Names in a headline, in headline order (the subject usually comes first):
    runs of capitalised words that are not common words, demonyms or "X-backed"
    style modifiers ("Sequoia-backed" names the investor, not the subject).
    A possessive ends a name: "Anthropic's Claude" is Anthropic, then Claude."""
    clauses = re.split(r"[:;—–,\.\?!\"]\s*", headline or "")
    runs = []
    for clause in clauses:
        current = []
        for raw in _WORD.findall(clause):
            possessive = bool(re.search(r"(?:'s|’s)$", raw))
            word = re.sub(r"(?:'s|’s)$", "", raw).strip(".,:;'’")
            lower = word.lower()
            proper = (
                word[:1].isupper()
                and lower not in _NOT_NAMES
                and not _SUFFIXED.search(word)
                and not (word.isalpha() and word[1:].islower() and _DEMONYM.search(lower))
            )
            if proper:
                current.append(word)
                if possessive:
                    runs.append(" ".join(current))
                    current = []
            elif current:
                runs.append(" ".join(current))
                current = []
        if current:
            runs.append(" ".join(current))

    seen, names = set(), []
    for name in runs:
        if len(name) >= 3 and name.lower() not in seen:
            seen.add(name.lower())
            names.append(name)
    return names


def _mentions(key: str, text: str) -> int:
    return len(re.findall(r"\b" + re.escape(key) + r"\b", text, re.IGNORECASE))


def _has_any(text: str, words: List[str]) -> bool:
    return any(_mentions(w, text) for w in words)


FALLBACK_IMAGES = (
    "aibrief/assets/fallbacks/default_ai_brain_ai.jpg",
    "aibrief/assets/fallbacks/default_ai_network.jpg",
)

# Countries and regions: their Wikipedia lead image is a map or a flag (AGENTS.md
# bans arbitrary maps), e.g. "Asia-Pacific" -> Asia_and_the_Pacific.png.
_BROAD_PLACES = {
    "china", "asia", "india", "usa", "us", "u.s", "america", "united states", "uk", "britain", "europe",
    "eu", "european union", "world", "big", "global", "asia-pacific", "asia pacific", "apac",
    "southeast asia", "south asia", "east asia", "middle east", "africa", "latin america", "gulf",
    "japan", "korea", "south korea", "north korea", "taiwan", "singapore", "australia", "canada",
    "germany", "france", "russia", "ukraine", "israel", "uae", "saudi arabia", "brazil", "indonesia",
}


def is_fallback_image(url: str) -> bool:
    return any(url.endswith(f) for f in FALLBACK_IMAGES)


def _is_person_key(key: str) -> bool:
    return key in PERSON_KEYS


def resolve_hero_candidates(idx: int, headline: str, summary: str, region: str) -> List[Tuple[str, str]]:
    """Every acceptable (url, badge) hero for a story, best first, ending with the
    approved fallbacks. The downloader takes the first one not shown in the last
    14 days (AGENTS.md section 3), so a company that is in the news every day gets
    its headquarters once, then its Wikipedia lead image, then the fallback.

    Order:
      1. Curated entity named in the HEADLINE (the story's subject).
      2. Curated entity mentioned at least twice in the body. People need two
         mentions too: "a rival to Sam Altman's OpenAI" must not put Altman on screen.
      3. The Wikipedia lead image of each matched entity and of each name in the headline.
      4. The two approved fallbacks, the alternating one first.
    """
    hl_text = (headline or "").lower()
    body_text = (summary or "").replace(headline or "", " ", 1).lower()
    candidates: List[Tuple[str, str]] = []
    matched_names: List[str] = []

    for key, (img_url, badge) in CURATED_ENTITY_MAP.items():
        if _mentions(key, hl_text):
            candidates.append((img_url, badge))
            matched_names.append(key)
    for key, (img_url, badge) in CURATED_ENTITY_MAP.items():
        if key not in matched_names and _mentions(key, body_text) >= 2:
            candidates.append((img_url, badge))
            matched_names.append(key)

    lookups = [k for k in matched_names if not _is_person_key(k)] + headline_entities(headline or "")
    seen_lookups = set()
    for ent in lookups:
        low = ent.lower()
        if low in _BROAD_PLACES or low in seen_lookups:
            continue
        seen_lookups.add(low)
        wiki_res = search_wikipedia_image(ent)
        if wiki_res:
            src, title = wiki_res
            candidates.append((src, f"{title.upper()} • CONTEXTUAL REPORTING"))

    first, second = FALLBACK_IMAGES if idx % 2 == 1 else FALLBACK_IMAGES[::-1]
    fallback_badge = f"{region} • AI INTELLIGENCE WIRE"
    candidates += [(first, fallback_badge), (second, fallback_badge)]

    unique, seen_urls = [], set()
    for url, badge in candidates:
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append((url, badge))
    return unique


def resolve_cuts_for_story(
    idx: int,
    headline: str,
    summary: str,
    region: str,
    global_used_urls: Optional[set] = None
) -> List[Tuple[str, str]]:
    """EXACTLY 1 authoritative (url, badge) hero for the story: the first candidate
    from resolve_hero_candidates that this episode has not already used."""
    used = global_used_urls if global_used_urls is not None else set()
    candidates = resolve_hero_candidates(idx, headline, summary, region)
    for url, badge in candidates:
        if is_fallback_image(url) or url not in used:
            used.add(url)
            return [(url, badge)]
    return [candidates[-1]]


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
