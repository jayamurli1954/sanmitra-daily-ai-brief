"""
Dynamic Story-Aware Entity Visual Resolver for SanMitra AI News Wire.
Replaces generic/repeated stock imagery with authentic, contextual editorial visuals:
  - Resolves official entity photos (White House, Jay Clayton, Sam Altman, Justin Trudeau, Josephine Teo, Lisa Su, Cantwell, etc.)
  - Resolves corporate headquarters (OpenAI, Tencent Seafront Tower, Alibaba Cloud, AMD, Google DeepMind, Boston Dynamics, etc.)
  - Resolves geographical landmarks (Dalby Queensland, Singapore Skyline, New Jersey State House, IIT Madras, etc.)
  - Resolves domain-specific operational visuals (Ballistic missile launches, hyperscale datacenters, semiconductor cleanrooms)
  - Permanently bans unrelated stock assets (Obama photo, bounce-rate charts, student HTML code, coffee-shop laptops)
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
    """Converts a Wikimedia Commons original file URL into a fast CDN thumbnail URL."""
    if not url:
        return ""
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
    "maria cantwell": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/8f/Maria_Cantwell_%28cropped%29.jpg"), "SENATE COMMERCE CHAIR • MARIA CANTWELL"),
    "cantwell": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/8f/Maria_Cantwell_%28cropped%29.jpg"), "SENATE COMMERCE CHAIR • MARIA CANTWELL"),
    "lisa su": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/d/de/SXSW-2024-alih-OB7A0861-Lisa_Su_%28cropped_2%29.jpg"), "AMD EXECUTIVE • DR. LISA SU"),

    # Institutions & Government
    "white house": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/1d/White_House_north_and_south_sides.jpg"), "WASHINGTON D.C. • THE WHITE HOUSE BRIEFING"),
    "capitol hill": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/9/9f/US_Capitol_east_side.JPG"), "CAPITOL HILL • FEDERAL REGULATORY COMMITTEE"),
    "us senate": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/9/9f/US_Capitol_east_side.JPG"), "WASHINGTON D.C. • US SENATE COMMERCE COMMITTEE"),
    "senate": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/9/9f/US_Capitol_east_side.JPG"), "WASHINGTON D.C. • US SENATE COMMERCE COMMITTEE"),
    "pentagon": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/2/2a/The_Pentagon%2C_Headquarters_of_the_US_Department_of_Defense_%28cropped2%29.jpg"), "ARLINGTON • THE PENTAGON HEADQUARTERS"),
    "canada parliament": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/b/b5/Ottawa_-_ON_-_Stadtansicht.jpg"), "PARLIAMENT HILL • OTTAWA FEDERAL COMMERCE"),
    "parliament hill": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/b/b5/Ottawa_-_ON_-_Stadtansicht.jpg"), "PARLIAMENT HILL • CANADIAN POLICY DESK"),
    "new jersey": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/83/New_Jersey_State_House.jpg"), "TRENTON • NEW JERSEY STATE HOUSE"),
    "trenton": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/83/New_Jersey_State_House.jpg"), "TRENTON • NEW JERSEY GOVERNMENT COMPLEX"),
    "iit madras": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/c6/Facade_of_IIT_Madras_%28cropped%29.jpg"), "CHENNAI • IIT MADRAS RESEARCH CAMPUS"),
    "meity": ("https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1920&q=85", "NEW DELHI • INDIA SOVEREIGN AI INITIATIVE"),
    "indiaai": ("https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1920&q=85", "NEW DELHI • INDIAAI MISSION SAFETY FRAMEWORK"),
    "digilocker": ("https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1920&q=85", "DIGITAL INDIA • DIGILOCKER AGENT PLATFORM"),
    "corover": ("https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1920&q=85", "BENGALURU • UNIFIED GOVERNMENT AI ASSISTANT"),
    "mas": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/8c/Monetary_Authority_of_Singapore_2.jpg"), "SINGAPORE • MONETARY AUTHORITY OF SINGAPORE"),
    "monetary authority of singapore": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/8c/Monetary_Authority_of_Singapore_2.jpg"), "SINGAPORE • MONETARY AUTHORITY OF SINGAPORE"),
    "china sovereign": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/China_Senate_House.jpg/1280px-China_Senate_House.jpg"), "BEIJING • SOVEREIGN AI GOVERNANCE ARCHITECTURE"),
    "china reinforces": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/China_Senate_House.jpg/1280px-China_Senate_House.jpg"), "BEIJING • SOVEREIGN AI GOVERNANCE ARCHITECTURE"),
    "chinese open-weight": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Skyline_of_Beijing_CBD_with_B-5906_approaching_%2820211016171955%29_%281%29.jpg/1280px-Skyline_of_Beijing_CBD_with_B-5906_approaching_%2820211016171955%29_%281%29.jpg"), "BEIJING • OPEN-WEIGHT INFERENCE HUBS"),
    "open-weight": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Skyline_of_Beijing_CBD_with_B-5906_approaching_%2820211016171955%29_%281%29.jpg/1280px-Skyline_of_Beijing_CBD_with_B-5906_approaching_%2820211016171955%29_%281%29.jpg"), "BEIJING • OPEN-WEIGHT INFERENCE HUBS"),
    "deepseek": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Skyline_of_Beijing_CBD_with_B-5906_approaching_%2820211016171955%29_%281%29.jpg/1280px-Skyline_of_Beijing_CBD_with_B-5906_approaching_%2820211016171955%29_%281%29.jpg"), "BEIJING • DEEPSEEK FOUNDATION LABS"),
    "china": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/China_Senate_House.jpg/1280px-China_Senate_House.jpg"), "BEIJING • STATE AI GOVERNANCE DESK"),

    # Corporations & Laboratories
    "openai": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/a/a7/1515_Third_Street.jpg"), "MISSION BAY • OPENAI HEADQUARTERS"),
    "google deepmind": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/4/4b/Platform_37_-_2026-04-25_2.jpg"), "KING'S CROSS • GOOGLE DEEPMIND CAMPUS"),
    "synthid": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/4/4b/Platform_37_-_2026-04-25_2.jpg"), "GOOGLE DEEPMIND • SYNTHID WATERMARK DETECTOR"),
    "google": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/32/Googleplex_HQ_%28cropped%29.jpg"), "MOUNTAIN VIEW • GOOGLEPLEX HEADQUARTERS"),
    "chrome": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/32/Googleplex_HQ_%28cropped%29.jpg"), "GOOGLE CHROME • GEMINI BROWSER AGENT"),
    "tencent": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/cd/Tencent_Seafront_Tower_in_Dec2020.jpg"), "SHENZHEN • TENCENT SEAFRONT TOWERS"),
    "alibaba": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/39/Phase_4_of_Alibaba_Xixi_Park_20200913.jpg"), "HANGZHOU • ALIBABA CLOUD XIXI CAMPUS"),
    "amd": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/11/2485_Augustine_Drive_headquarters_in_Santa_Clara%2C_California.jpg"), "SANTA CLARA • AMD CORPORATE HEADQUARTERS"),
    "spacex": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/83/SpaceX_Headquarters_Hawthorne_California.jpg"), "HAWTHORNE • SPACEX HEADQUARTERS & TELEMETRY"),
    "boston dynamics": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/9/9b/Atlas_during_testing.jpg"), "WALTHAM • BOSTON DYNAMICS ROBOTICS LAB"),
    "atlas": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/9/9b/Atlas_during_testing.jpg"), "HUMANOID ROBOTICS • ELECTRIC ATLAS DEPLOYMENT"),
    "robotics": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/9/9b/Atlas_during_testing.jpg"), "EMBODIED AI • INDUSTRIAL ROBOTICS DEPLOYMENT"),
    "chan zuckerberg": ("https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=1920&q=85", "CHAN ZUCKERBERG BIOHUB • VIRTUAL BIOLOGY INITIATIVE"),
    "biohub": ("https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=1920&q=85", "CHAN ZUCKERBERG BIOHUB • VIRTUAL BIOLOGY LAB"),
    "biology": ("https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=1920&q=85", "CELLULAR DYNAMICS • PREDICTIVE BIOLOGY LAB"),
    "sierra": ("https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=1920&q=85", "ENTERPRISE PROTOCOL • PERSONAL AGENT PLATFORM"),
    "nous research": ("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&q=85", "OPEN RESEARCH LAB • NOUS HERMES FOUNDATION"),

    # Direct military & aerospace systems
    "harmattan": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/12/MQ-9_Reaper_UAV_%28cropped%29.jpg"), "MARRAKECH • AUTONOMOUS DEEP-STRIKE DEFENSE"),
    "irifi": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/12/MQ-9_Reaper_UAV_%28cropped%29.jpg"), "MARRAKECH • IRIFI DEEP-STRIKE DRONE SYSTEM"),
    "drone": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/12/MQ-9_Reaper_UAV_%28cropped%29.jpg"), "TACTICAL AEROSPACE • AUTONOMOUS DRONE FLIGHT"),
    "drones": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/12/MQ-9_Reaper_UAV_%28cropped%29.jpg"), "TACTICAL AEROSPACE • AUTONOMOUS DRONE FLIGHT"),
    "mq-20": ("https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=1920&q=85", "TACTICAL AUTONOMY • MQ-20 SWARM FLIGHT TEST"),
    "north korea missile": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/35/North_Korea%27s_ballistic_missile_-_North_Korea_Victory_Day-2013_01.jpg"), "PYONGYANG • STRATEGIC BALLISTIC MISSILE"),
    "ballistic missile": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/35/North_Korea%27s_ballistic_missile_-_North_Korea_Victory_Day-2013_01.jpg"), "BALLISTIC TRAJECTORY • FLIGHT DYNAMICS"),

    # Mathematics & AI formalization
    "mathematics": ("https://images.unsplash.com/photo-1509228468518-180dd4864904?w=1920&q=85", "ADVANCED MATHEMATICS • FORMAL PROOF VERIFICATION"),
    "maths": ("https://images.unsplash.com/photo-1509228468518-180dd4864904?w=1920&q=85", "ADVANCED MATHEMATICS • FORMAL PROOF VERIFICATION"),
    "kakeya": ("https://images.unsplash.com/photo-1509228468518-180dd4864904?w=1920&q=85", "KAKEYA CONJECTURE • REASONING FRONTIER MODEL"),
    "riemann": ("https://images.unsplash.com/photo-1509228468518-180dd4864904?w=1920&q=85", "RIEMANN ZETA • MACHINE FORMALIZATION"),

    # Cities & Regions
    "morocco": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/6/6c/Casa_finance_city_6_%28cropped%29.jpg"), "CASABLANCA • DEFENSE AEROSPACE COMPLEX"),
    "casablanca": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/6/6c/Casa_finance_city_6_%28cropped%29.jpg"), "CASABLANCA • DEFENSE AEROSPACE COMPLEX"),
    "dalby": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/d/d3/Dalby_aerial.jpg"), "WESTERN DOWNS • DALBY RURAL REGION"),
    "queensland": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/d/d3/Dalby_aerial.jpg"), "QUEENSLAND • REGIONAL ENERGY & COMPUTE CORRIDOR"),
    "singapore": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/b/b6/Skyline_of_Singapore_Central_Business_District_20250903.jpg"), "SINGAPORE • CENTRAL BUSINESS DISTRICT SKYLINE"),
    "pyongyang": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/e/e7/The_Arch_of_Triumph_%2811360607534%29.jpg"), "PYONGYANG • STRATEGIC MILITARY COMMAND"),
    "bengaluru": ("https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1920&q=85", "BENGALURU • INDIA SOVEREIGN TECH CAPITAL"),
    "guwahati": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/11/Guwahati_citysky.jpg"), "GUWAHATI • NORTHEAST INDIA TECH PARK"),
    "norway": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/c5/Stortinget_August_2019_01.jpg"), "OSLO • NORWEGIAN PARLIAMENT STORTINGET"),
    "new york city": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/10/Empire_State_Building_%28aerial_view%29.jpg"), "NEW YORK CITY • MUNICIPAL AI GOVERNANCE COUNCIL"),
    "south korea": ("https://images.unsplash.com/photo-1538485399081-7191377e8241?w=1920&q=85", "SEOUL • SOUTH KOREA SOVEREIGN FRONTIER AI"),
    "korea": ("https://images.unsplash.com/photo-1538485399081-7191377e8241?w=1920&q=85", "SEOUL • 10K GPU SOVEREIGN COMPUTE PROJECT"),

    # Direct institutional topics
    "nato": ("https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1920&q=85", "BRUSSELS • NATO EASTERN FLANK DEFENSE DOCTRINE"),
    "mit": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/0/03/MIT_Building_10_and_the_Great_Dome%2C_Cambridge_MA.jpg"), "CAMBRIDGE • MIT COMPUTER SCIENCE & AI LAB"),
    "kaiming he": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/0/03/MIT_Building_10_and_the_Great_Dome%2C_Cambridge_MA.jpg"), "MIT CSAIL • VISTA VISUAL HARNESS BENCHMARK"),
    "data center": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/57/Data_Center_of_CNPC.jpg"), "HYPERSCALE AI CLUSTER • FACILITY DEPLOYMENT"),
    "datacentre": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/57/Data_Center_of_CNPC.jpg"), "HYPERSCALE AI CLUSTER • FACILITY DEPLOYMENT")
}

# Domain-specific B-roll pools (High-grade authentic editorial TV shots, NEVER bounce rate charts, NEVER UN/Obama)
DOMAIN_POOLS = {
    "defense": [
        ("https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1920&q=85", "RADAR SURVEILLANCE • AIR-DEFENSE ENVELOPE"),
        ("https://images.unsplash.com/photo-1579829366248-204fe8413f31?w=1920&q=85", "TACTICAL TELEMETRY • AIR-DEFENSE OPERATIONS"),
        ("https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1920&q=85", "MILITARY OPERATIONS CENTER • INCIDENT DESK"),
        ("https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=1920&q=85", "SATELLITE GROUND STATION • SECURE TELEMETRY"),
        ("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&q=85", "CYBER DEFENSE OPERATIONS • LIVE INCIDENT FEED"),
        ("https://images.unsplash.com/photo-1563770660941-20978e870e26?w=1920&q=85", "AEROSPACE TELEMETRY • RADAR MONITORING GRID"),
        ("https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=1920&q=85", "DEFENSE RESEARCH LAB • AUTONOMOUS GUIDANCE"),
        ("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1920&q=85", "NETWORK SECURITY OPERATIONS • SENSOR AUDIT")
    ],
    "policy": [
        ("https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=1920&q=85", "MULTILATERAL FORUM • REGULATORY HARMONIZATION"),
        ("https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1920&q=85", "STANDARDS AUDITING • COMPLIANCE FRAMEWORK"),
        ("https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1920&q=85", "MINISTERIAL ENGAGEMENT • SOVEREIGN PACT"),
        ("https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1920&q=85", "REGULATORY OVERSIGHT • JUDICIAL INQUIRY"),
        ("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1920&q=85", "METROPOLITAN CIVIC CENTER • ETHICS DESK"),
        ("https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&q=85", "CORPORATE GOVERNANCE • STRATEGY BRIEFING"),
        ("https://images.unsplash.com/photo-1497215728101-856f4ea42174?w=1920&q=85", "EXECUTIVE AUDIT CHAMBER • COMPLIANCE REVIEW"),
        ("https://images.unsplash.com/photo-1577495508048-b635879837f1?w=1920&q=85", "GOVERNMENTAL ASSEMBLY • LEGISLATIVE DESK")
    ],
    "hardware": [
        ("https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=85", "ADVANCED SILICON DIE • FABRICATION CLEANROOM"),
        ("https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1920&q=85", "HIGH-DENSITY GPU RACKS • THERMAL MANAGEMENT"),
        ("https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1920&q=85", "SUPERCOMPUTING BACKBONE • TENSOR CLUSTERS"),
        ("https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1920&q=85", "HARDWARE ACCELERATION • SYSTEM INTEGRATION"),
        ("https://images.unsplash.com/photo-1555680202-c86f0e12f086?w=1920&q=85", "SEMICONDUCTOR WAFER • ADVANCED PACKAGING"),
        ("https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1920&q=85", "ROBOTICS HARDWARE • EMBODIED AUTOMATION BENCH"),
        ("https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=1920&q=85", "PROCESSOR ARCHITECTURE • DIE INSPECTION"),
        ("https://images.unsplash.com/photo-1563770660941-20978e870e26?w=1920&q=85", "EMBEDDED VISION CHIP • HARDWARE BENCH")
    ],
    "research": [
        ("https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=1920&q=85", "NEURAL BENCHMARKING • RECURSIVE EVALUATION HUD"),
        ("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&q=85", "AGENT HARNESS AUDIT • SCAFFOLD VERIFICATION"),
        ("https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=1920&q=85", "RESEARCH SCIENTISTS • ALGORITHMIC GOVERNANCE"),
        ("https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1920&q=85", "DEVELOPER PLATFORM • MULTI-AGENT WORKSPACE"),
        ("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1920&q=85", "DIGITAL TELEMETRY • SYSTEM EVALUATION"),
        ("https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=1920&q=85", "LABORATORY INSTRUMENTATION • MODEL EVALUATION"),
        ("https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=1920&q=85", "DEEP LEARNING PIPELINE • KERNEL TRACING"),
        ("https://images.unsplash.com/photo-1576086213369-97a306d36557?w=1920&q=85", "MULTIMODAL REASONING • SYNTHETIC BENCHMARK")
    ],
    "energy": [
        ("https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1920&q=85", "HYPERSCALE FACILITY • CLOUD INFRASTRUCTURE"),
        ("https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1920&q=85", "REGIONAL POWER GRID • SUBSTATION TELEMETRY"),
        ("https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1920&q=85", "HIGH-VOLTAGE DATACENTER • MEGAWATT CLUSTER"),
        ("https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=1920&q=85", "TERRAIN SURVEY • RURAL INFRASTRUCTURE"),
        ("https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=1920&q=85", "COMMUNICATIONS TOWER • BACKBONE LINK")
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
    "polygon", "diagram", "election", "map", "flag", "coat_of_arms", "emblem",
    "logo", "chart", "graph", "survey", "schema", "symbol", "attack", "storming", "protest"
]


def search_wikipedia_image(query: str) -> Optional[Tuple[str, str]]:
    """Fetches high-resolution lead image from Wikipedia for a named entity with strict negative filtering."""
    q_lower = query.lower().strip()
    # Query disambiguation
    if q_lower == "pentagon":
        query = "The Pentagon"
    elif q_lower == "senate":
        query = "United States Senate"
    elif q_lower in ("harmattan", "irifi"):
        query = "Unmanned aerial vehicle"
    elif q_lower in ("cantwell", "maria cantwell"):
        query = "Maria Cantwell"
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

                # Exclude diagrams, election maps, coats of arms, polygons
                if any(k in src_lower or k in title_lower for k in BANNED_WIKI_KEYWORDS):
                    continue
                if src_lower.endswith(".svg") or src_lower.endswith(".gif") or ".svg." in src_lower:
                    continue

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
    Guaranteed to return 3 distinct cuts with word-boundary matching and robust fallbacks.
    """
    hl_text = headline.lower()
    full_text = f"{headline} {summary}".lower()
    cuts = []

    # 1. Match curated entities appearing in the HEADLINE first (primary subject of the story)
    for key, (img_url, badge) in CURATED_ENTITY_MAP.items():
        if len(cuts) >= 2:
            break
        if re.search(r'\b' + re.escape(key) + r'\b', hl_text, re.IGNORECASE):
            if not any(c[0] == img_url for c in cuts):
                cuts.append((img_url, badge))

    # 2. If fewer than 2 cuts matched, check body/script text for secondary contextual entities
    if len(cuts) < 2:
        for key, (img_url, badge) in CURATED_ENTITY_MAP.items():
            if len(cuts) >= 2:
                break
            # Skip broad comparisons (e.g. comparing to OpenAI/Google) if headline was about something else
            if re.search(r'\b' + re.escape(key) + r'\b', full_text, re.IGNORECASE):
                if not any(c[0] == img_url for c in cuts):
                    cuts.append((img_url, badge))

    # 3. If no entity matched yet, try live Wikipedia image search for leading capitalized terms in headline
    if not cuts:
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', headline)
        for ent in entities:
            if ent.lower() in ("daily", "brief", "news", "special", "report", "wire", "monday", "tuesday", "technology", "development", "board", "world", "china", "asia", "india", "usa"):
                continue
            wiki_res = search_wikipedia_image(ent)
            if wiki_res:
                src, title = wiki_res
                badge = f"{title.upper()} • CONTEXTUAL REPORTING"
                if not any(c[0] == src for c in cuts):
                    cuts.append((src, badge))
                    break

    # 3. Determine domain for complementary operational B-roll
    text = full_text
    domain = "policy"
    if any(k in text for k in ["missile", "military", "weapon", "warhead", "pyongyang", "air-defense", "ballistic", "nato", "flank", "targeting", "drone", "cyber", "threat", "incursion", "avenger", "swarms", "kill-chain"]):
        domain = "defense"
    elif any(k in text for k in ["datacentre", "data center", "grid", "power", "energy", "substation", "hectare", "bedrock", "aws", "cloud", "hyperscale", "capacity"]):
        domain = "energy"
    elif any(k in text for k in ["chip", "semiconductor", "amd", "nvidia", "gpu", "hardware", "wafer", "silicon", "soc", "bigendian", "veerai", "die", "npu"]):
        domain = "hardware"
    elif any(k in text for k in ["research", "rrsi", "benchmark", "foundation model", "eval", "vista", "arc-agi", "mit", "agent", "deepseek", "moe", "weights", "mathematics", "maths", "kakeya", "riemann", "cellular", "biology"]):
        domain = "research"
    elif any(k in text for k in ["glasses", "wearable", "privacy", "ban", "kill switch", "whistleblower", "hearing", "council", "senate", "governance", "claim act", "liability", "mas"]):
        domain = "policy"

    pool = DOMAIN_POOLS.get(domain, DOMAIN_POOLS["policy"])

    # Pick from primary domain pool avoiding URLs already used across this story or episode
    for pool_url, pool_badge in pool:
        if len(cuts) >= 3:
            break
        if not any(c[0] == pool_url for c in cuts):
            if global_used_urls is not None and pool_url in global_used_urls:
                continue
            cuts.append((pool_url, pool_badge))
            if global_used_urls is not None:
                global_used_urls.add(pool_url)

    # Pad with complementary domain pools if still under 3
    if len(cuts) < 3:
        for backup_domain in ["hardware", "research", "defense", "energy", "policy"]:
            if backup_domain == domain:
                continue
            for pool_url, pool_badge in DOMAIN_POOLS[backup_domain]:
                if len(cuts) >= 3:
                    break
                if not any(c[0] == pool_url for c in cuts):
                    if global_used_urls is not None and pool_url in global_used_urls:
                        continue
                    cuts.append((pool_url, pool_badge))
                    if global_used_urls is not None:
                        global_used_urls.add(pool_url)

    # Fallback rotation if all pools are exhausted by a large episode (guarantee 3 unique cuts)
    fallback_index = 0
    while len(cuts) < 3:
        idx_pick = (idx + fallback_index) % len(pool)
        fallback_index += 1
        p_url, p_badge = pool[idx_pick]
        if not any(c[0] == p_url for c in cuts):
            cuts.append((p_url, f"{p_badge} • CUT {len(cuts)+1}"))
        else:
            # Pick from any available domain pool
            for b_dom in DOMAIN_POOLS:
                for b_url, b_b in DOMAIN_POOLS[b_dom]:
                    if not any(c[0] == b_url for c in cuts):
                        cuts.append((b_url, b_b))
                        break
                if len(cuts) >= 3:
                    break

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
