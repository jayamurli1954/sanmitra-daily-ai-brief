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
    "justin trudeau": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/b/b6/Justin_Trudeau_2023_%28cropped%29.jpg"), "OFFICIAL ENGAGEMENT • CANADIAN FEDERAL DESK"),
    "mark carney": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/a/a2/Mark_Carney_2019.jpg"), "MACROECONOMIC AI SUMMIT • MARK CARNEY"),
    "nirmala sitharaman": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/38/Smt._Nirmala_Sitharaman_taking_charge_as_the_Union_Minister_for_Finance_%26_Corporate_Affairs%2C_in_New_Delhi_on_June_12%2C_2024_%28cropped%29.jpg"), "NEW DELHI • UNION FINANCE MINISTER SITHARAMAN"),
    "lisa su": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/d/de/SXSW-2024-alih-OB7A0861-Lisa_Su_%28cropped_2%29.jpg"), "AMD EXECUTIVE • DR. LISA SU"),
    "ashwini vaishnaw": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/35/Ashwini_Vaishnaw_cropped.jpg"), "NEW DELHI • UNION IT MINISTER ASHWINI VAISHNAW"),
    "vaishnaw": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/35/Ashwini_Vaishnaw_cropped.jpg"), "NEW DELHI • UNION IT MINISTER ASHWINI VAISHNAW"),
    "charlton": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/b/b6/Parliament_House_at_dusk%2C_Canberra_ACT.jpg"), "CANBERRA • ASSISTANT MINISTER ANDREW CHARLTON"),
    "stampe": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/7/7c/Christiansborg_Slot_Copenhagen_2014_01.jpg"), "COPENHAGEN • DANISH CULTURE MINISTRY"),

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
    "meity": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/cd/Bharat_Mandapam_Pragati_Maidan.jpg"), "NEW DELHI • INDIA SOVEREIGN AI INITIATIVE"),
    "indiaai": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/cd/Bharat_Mandapam_Pragati_Maidan.jpg"), "NEW DELHI • INDIAAI MISSION SAFETY FRAMEWORK"),
    "digilocker": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/cd/Bharat_Mandapam_Pragati_Maidan.jpg"), "DIGITAL INDIA • DIGILOCKER AGENT PLATFORM"),
    "corover": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/cd/Bharat_Mandapam_Pragati_Maidan.jpg"), "BENGALURU • UNIFIED GOVERNMENT AI ASSISTANT"),
    "mas": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/8c/Monetary_Authority_of_Singapore_2.jpg"), "SINGAPORE • MONETARY AUTHORITY OF SINGAPORE"),
    "monetary authority of singapore": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/8/8c/Monetary_Authority_of_Singapore_2.jpg"), "SINGAPORE • MONETARY AUTHORITY OF SINGAPORE"),
    "china sovereign": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/China_Senate_House.jpg/1280px-China_Senate_House.jpg"), "BEIJING • SOVEREIGN AI GOVERNANCE ARCHITECTURE"),
    "china reinforces": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/China_Senate_House.jpg/1280px-China_Senate_House.jpg"), "BEIJING • SOVEREIGN AI GOVERNANCE ARCHITECTURE"),
    "chinese open-weight": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Skyline_of_Beijing_CBD_with_B-5906_approaching_%2820211016171955%29_%281%29.jpg/1280px-Skyline_of_Beijing_CBD_with_B-5906_approaching_%2820211016171955%29_%281%29.jpg"), "BEIJING • OPEN-WEIGHT INFERENCE HUBS"),
    "open-weight": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Skyline_of_Beijing_CBD_with_B-5906_approaching_%2820211016171955%29_%281%29.jpg/1280px-Skyline_of_Beijing_CBD_with_B-5906_approaching_%2820211016171955%29_%281%29.jpg"), "BEIJING • OPEN-WEIGHT INFERENCE HUBS"),
    "deepseek": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/f/fd/Hangzhou_Skyline_against_the_West_Lake.png"), "HANGZHOU • HOME CITY OF DEEPSEEK"),

    # Corporations & Laboratories
    "openai": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/a/a7/1515_Third_Street.jpg"), "MISSION BAY • OPENAI HEADQUARTERS"),
    "gpt-6": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/a/a7/1515_Third_Street.jpg"), "OPENAI • GPT-6 FRONTIER MODEL CANVAS"),
    "intelligent ui": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/a/a7/1515_Third_Street.jpg"), "CHATGPT • INTELLIGENT UI INTERACTION"),
    "google deepmind": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/4/4b/Platform_37_-_2026-04-25_2.jpg"), "KING'S CROSS • GOOGLE DEEPMIND CAMPUS"),
    "synthid": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/4/4b/Platform_37_-_2026-04-25_2.jpg"), "GOOGLE DEEPMIND • SYNTHID WATERMARK DETECTOR"),
    "google": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/32/Googleplex_HQ_%28cropped%29.jpg"), "MOUNTAIN VIEW • GOOGLEPLEX HEADQUARTERS"),
    "google cloud": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/32/Googleplex_HQ_%28cropped%29.jpg"), "GOOGLE CLOUD • ENTERPRISE AI CAMPUS"),
    "gemini agent": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/32/Googleplex_HQ_%28cropped%29.jpg"), "GOOGLE CLOUD • GEMINI AGENT WORKSPACE"),
    "chrome": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/32/Googleplex_HQ_%28cropped%29.jpg"), "GOOGLE CHROME • GEMINI BROWSER AGENT"),
    "tencent": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/cd/Tencent_Seafront_Tower_in_Dec2020.jpg"), "SHENZHEN • TENCENT SEAFRONT TOWERS"),
    "workbuddy": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/cd/Tencent_Seafront_Tower_in_Dec2020.jpg"), "SHENZHEN • TENCENT WORKBUDDY AI FILE OS"),
    "manus": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/e/e2/Zhongguancun_from_Huangzhuang_North_Footbridge_%2820201214122926%29.jpg"), "BEIJING • MANUS AI AGENT LAB"),
    "butterfly effect": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/e/e2/Zhongguancun_from_Huangzhuang_North_Footbridge_%2820201214122926%29.jpg"), "BEIJING • BUTTERFLY EFFECT AGENT LAB"),
    "biren": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Skyline_of_Beijing_CBD_with_B-5906_approaching_%2820211016171955%29_%281%29.jpg/1280px-Skyline_of_Beijing_CBD_with_B-5906_approaching_%2820211016171955%29_%281%29.jpg"), "SHANGHAI • BIREN TECHNOLOGY CHIP PLACEMENT"),
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
    "apple": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/5a/Aerial_view_of_Apple_Park_dllu.jpg"), "CUPERTINO • APPLE PARK"),
    "meta": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/7/7c/Meta_Platforms_Headquarters_Menlo_Park_California.jpg"), "MENLO PARK • META HEADQUARTERS"),
    "disney": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/32/Walt_Disney_Studios_Alameda_Entrance.jpg"), "BURBANK • WALT DISNEY STUDIOS"),
    "microsoft": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/6/64/Microsoft_Redmond_Campus_redevelopment_aerial_view%2C_Sept._2021.jpg"), "REDMOND • MICROSOFT REDMOND CAMPUS"),
    "surface": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/6/64/Microsoft_Redmond_Campus_redevelopment_aerial_view%2C_Sept._2021.jpg"), "REDMOND • MICROSOFT SURFACE HARDWARE LAB"),
    "surface laptop": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/6/64/Microsoft_Redmond_Campus_redevelopment_aerial_view%2C_Sept._2021.jpg"), "REDMOND • MICROSOFT SURFACE HARDWARE LAB"),
    "samsung": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/e/e2/Samsung_headquarters.jpg"), "SUWON • SAMSUNG DIGITAL CITY HEADQUARTERS"),
    "samsung electronics": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/e/e2/Samsung_headquarters.jpg"), "SUWON • SAMSUNG ELECTRONICS HEADQUARTERS"),
    "vesta": ("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1920&q=85", "VENTURE FINANCE • AUTONOMOUS AGENT CAPITAL"),
    "catalyst": ("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1920&q=85", "VENTURE FINANCE • AUTONOMOUS AGENT CAPITAL"),
    "gpus": ("https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1920&q=85", "HIGH-DENSITY GPU CLUSTERS • ACCELERATED COMPUTE"),
    "gpu": ("https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1920&q=85", "HIGH-DENSITY GPU CLUSTERS • ACCELERATED COMPUTE"),
    "yandex": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/a/ad/Yandex_main_office.jpg"), "MOSCOW • YANDEX CLOUD COMPUTING HEADQUARTERS"),
    "amie": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/32/Googleplex_HQ_%28cropped%29.jpg"), "GOOGLE HEALTH CLINICAL AI • AMIE EVALUATION"),
    "tokyo": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/6/66/Tokyo_Skyline20210123.jpg"), "TOKYO • CITY SKYLINE"),
    "manchester": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/0/02/Beetham_Tower_from_below.jpg"), "MANCHESTER • G20 INNOVATION NATION SUMMIT"),
    "burnham": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/0/02/Beetham_Tower_from_below.jpg"), "MANCHESTER • G20 INNOVATION NATION SUMMIT"),
    "state council": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/China_Senate_House.jpg/1280px-China_Senate_House.jpg"), "BEIJING • STATE COUNCIL DIRECTIVES"),
    "firmus": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/57/Data_Center_of_CNPC.jpg"), "ASX • HYPERSCALE DATACENTER VALUATIONS"),

    # Direct military & aerospace defense systems
    "air defense": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/2/2f/U-s-service-members-stand-by-a-patriot-missile-battery-in-gaziantep-turkey.jpg"), "AIR DEFENSE • PATRIOT RADAR BATTERY"),
    "harmattan": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/12/MQ-9_Reaper_UAV_%28cropped%29.jpg"), "MARRAKECH • AUTONOMOUS DEEP-STRIKE DEFENSE"),
    "irifi": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/12/MQ-9_Reaper_UAV_%28cropped%29.jpg"), "MARRAKECH • IRIFI DEEP-STRIKE DRONE SYSTEM"),
    "drone": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/12/MQ-9_Reaper_UAV_%28cropped%29.jpg"), "TACTICAL AEROSPACE • AUTONOMOUS DRONE FLIGHT"),
    "drones": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/12/MQ-9_Reaper_UAV_%28cropped%29.jpg"), "TACTICAL AEROSPACE • AUTONOMOUS DRONE FLIGHT"),
    "north korea missile": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/35/North_Korea%27s_ballistic_missile_-_North_Korea_Victory_Day-2013_01.jpg"), "PYONGYANG • STRATEGIC BALLISTIC MISSILE"),
    "ballistic missile": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/3/35/North_Korea%27s_ballistic_missile_-_North_Korea_Victory_Day-2013_01.jpg"), "BALLISTIC TRAJECTORY • FLIGHT DYNAMICS"),

    # Cybersecurity & Banking
    "crowdstrike": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/5a/NSOC-2012.jpg"), "CYBER DEFENSE • CROWDSTRIKE THREAT INTEL"),
    "cyberattack": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/5a/NSOC-2012.jpg"), "SECURITY OPERATIONS • INCIDENT RESPONSE SOC"),
    "shinhan": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/4/45/Yeouido2025.jpg"), "SEOUL • YEOUIDO FINANCIAL DISTRICT"),
    "financial services commission": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/4/45/Yeouido2025.jpg"), "SEOUL • FINANCIAL SERVICES REGULATORY DESK"),

    # Research & Universities
    "george washington university": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/7/71/George_Washington_University_School_of_Engineering_and_Applied_Science_%2855266857738%29.jpg"), "WASHINGTON D.C. • GWU SCIENCE & ENGINEERING"),
    "gwu": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/7/71/George_Washington_University_School_of_Engineering_and_Applied_Science_%2855266857738%29.jpg"), "WASHINGTON D.C. • GWU SCIENCE & ENGINEERING"),
    "mit": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/0/03/MIT_Building_10_and_the_Great_Dome%2C_Cambridge_MA.jpg"), "CAMBRIDGE • MIT COMPUTER SCIENCE & AI LAB"),
    "kaiming he": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/0/03/MIT_Building_10_and_the_Great_Dome%2C_Cambridge_MA.jpg"), "MIT CSAIL • VISTA VISUAL HARNESS BENCHMARK"),
    "mathematics": ("https://images.unsplash.com/photo-1509228468518-180dd4864904?w=1920&q=85", "ADVANCED MATHEMATICS • FORMAL PROOF VERIFICATION"),
    "maths": ("https://images.unsplash.com/photo-1509228468518-180dd4864904?w=1920&q=85", "ADVANCED MATHEMATICS • FORMAL PROOF VERIFICATION"),
    "kakeya": ("https://images.unsplash.com/photo-1509228468518-180dd4864904?w=1920&q=85", "KAKEYA CONJECTURE • REASONING FRONTIER MODEL"),
    "riemann": ("https://images.unsplash.com/photo-1509228468518-180dd4864904?w=1920&q=85", "RIEMANN ZETA • MACHINE FORMALIZATION"),

    # Cities & Regions
    "casablanca": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/6/6c/Casa_finance_city_6_%28cropped%29.jpg"), "CASABLANCA • DEFENSE AEROSPACE COMPLEX"),
    "dalby": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/d/d3/Dalby_aerial.jpg"), "WESTERN DOWNS • DALBY RURAL REGION"),
    "queensland": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/d/d3/Dalby_aerial.jpg"), "QUEENSLAND • REGIONAL ENERGY & COMPUTE CORRIDOR"),
    "pyongyang": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/e/e7/The_Arch_of_Triumph_%2811360607534%29.jpg"), "PYONGYANG • STRATEGIC MILITARY COMMAND"),
    "bengaluru": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/c/cd/Bharat_Mandapam_Pragati_Maidan.jpg"), "BENGALURU • INDIA SOVEREIGN TECH CAPITAL"),
    "guwahati": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/11/Guwahati_citysky.jpg"), "GUWAHATI • NORTHEAST INDIA TECH PARK"),
    "new york city": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/1/10/Empire_State_Building_%28aerial_view%29.jpg"), "NEW YORK CITY • MUNICIPAL AI GOVERNANCE COUNCIL"),
    "nato": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/5a/NSOC-2012.jpg"), "BRUSSELS • NATO OPERATIONS CENTER"),
    "data center": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/57/Data_Center_of_CNPC.jpg"), "HYPERSCALE AI CLUSTER • FACILITY DEPLOYMENT"),
    "datacentre": (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/57/Data_Center_of_CNPC.jpg"), "HYPERSCALE AI CLUSTER • FACILITY DEPLOYMENT")
}

# Domain-specific B-roll pools (100% authentic editorial visuals, NO server cables, NO plasma balls, NO toy drones)
# Stand-in stills for cuts the story itself cannot supply. Only generic,
# location-free images: a named place here (Canberra, Capitol Hill, Samsung HQ)
# ended up captioned as the setting of unrelated stories.
DOMAIN_POOLS = {
    "defense": [
        (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/6/6f/FBX_T.jpg"), "RADAR SURVEILLANCE • PHASED ARRAY SYSTEM"),
        (to_wiki_thumb("https://upload.wikimedia.org/wikipedia/commons/5/5a/NSOC-2012.jpg"), "TACTICAL OPERATIONS CENTER • INCIDENT DESK"),
        ("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&q=85", "CYBER DEFENSE OPERATIONS • LIVE INCIDENT FEED"),
        ("https://images.unsplash.com/photo-1563770660941-20978e870e26?w=1920&q=85", "AEROSPACE TELEMETRY • RADAR MONITORING GRID"),
        ("https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=1920&q=85", "DEFENSE RESEARCH LAB • AUTONOMOUS GUIDANCE"),
        ("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1920&q=85", "NETWORK SECURITY OPERATIONS • SENSOR AUDIT")
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
    "polygon", "diagram", "election", "map", "flag", "coat_of_arms", "emblem",
    "logo", "chart", "graph", "survey", "schema", "symbol", "attack", "storming", "protest",
    "beer", "carlsberg", "tuborg", "alcohol", "painting", "portrait", "oil_on_canvas",
    "sailing", "frigate", "hermione", "manga", "anime", "cartoon", "comic", "drawing", "illustration",
    "temple", "mosque", "church", "sculpture", "statue", "monument"
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

                # Exclude diagrams, election maps, coats of arms, polygons, beers, paintings, manga
                if any(k in src_lower or k in title_lower for k in BANNED_WIKI_KEYWORDS):
                    continue
                if src_lower.endswith(".svg") or src_lower.endswith(".gif") or ".svg." in src_lower:
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
    runs, current = [], []
    for raw in _WORD.findall(headline or ""):
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


def resolve_cuts_for_story(
    idx: int,
    headline: str,
    summary: str,
    region: str,
    global_used_urls: Optional[set] = None
) -> List[Tuple[str, str]]:
    """
    Returns 3 distinct (url, badge) visual cuts tailored directly to the story's real content.
    Guaranteed to return 3 distinct cuts with word-boundary matching and robust domain isolation.
    """
    hl_text = headline.lower()
    full_text = f"{headline} {summary}".lower()
    body_text = (summary or "").replace(headline or "", " ", 1).lower()
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
            # A company named once in the body is usually a comparison ("matches OpenAI
            # and Anthropic"), not the subject; Meta's launch got OpenAI's headquarters.
            if _mentions(key, body_text) >= 2:
                if not any(c[0] == img_url for c in cuts):
                    cuts.append((img_url, badge))

    # 3. If no entity matched yet, try live Wikipedia image search for the headline's names
    if not cuts:
        for ent in headline_entities(headline):
            if ent.lower() in ("china", "asia", "india", "usa", "us", "uk", "europe", "world", "big"):
                continue
            wiki_res = search_wikipedia_image(ent)
            if wiki_res:
                src, title = wiki_res
                badge = f"{title.upper()} • CONTEXTUAL REPORTING"
                if not any(c[0] == src for c in cuts):
                    cuts.append((src, badge))
                    break

    # 4. Determine domain for complementary operational B-roll
    text = full_text
    domain = "policy"
    # Whole words only: substring tests matched "ban" in "bank", "mit" in "submit", "die" in "diet".
    if _has_any(text, ["missile", "missiles", "military", "weapon", "weapons", "warhead", "pyongyang", "air-defense", "ballistic", "nato", "targeting", "drone", "drones", "interceptor", "interceptors", "incursion", "swarms", "kill-chain"]):
        domain = "defense"
    elif _has_any(text, ["chip", "chips", "semiconductor", "semiconductors", "amd", "nvidia", "gpu", "gpus", "hardware", "wafer", "silicon", "soc", "npu", "cpu", "cpus", "processor", "accelerator"]):
        domain = "hardware"
    elif _has_any(text, ["datacentre", "data centre", "data center", "grid", "power", "energy", "substation", "hyperscale", "petaflops", "megawatt", "gigawatt"]):
        domain = "energy"
    elif _has_any(text, ["research", "researchers", "benchmark", "benchmarks", "foundation model", "study", "paper", "agent", "agents", "deepseek", "weights", "mathematics", "maths", "biology", "laboratory"]):
        domain = "research"
    elif _has_any(text, ["privacy", "ban", "whistleblower", "hearing", "council", "senate", "governance", "liability", "regulation", "regulator", "lawsuit", "bankruptcy", "court"]):
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

    # 5. Strict domain-isolated padding (NEVER cross defense with policy/banking!)
    SAFE_BACKUP_DOMAINS = {
        "policy": ["research", "hardware"],
        "defense": ["hardware", "research"],
        "hardware": ["research", "energy"],
        "research": ["hardware", "policy"],
        "energy": ["hardware", "policy"]
    }

    if len(cuts) < 3:
        for backup_domain in SAFE_BACKUP_DOMAINS.get(domain, ["research", "hardware"]):
            for pool_url, pool_badge in DOMAIN_POOLS.get(backup_domain, []):
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
            # Pick only from safe backup domain pools
            for b_dom in SAFE_BACKUP_DOMAINS.get(domain, ["research", "hardware"]):
                for b_url, b_b in DOMAIN_POOLS.get(b_dom, []):
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
