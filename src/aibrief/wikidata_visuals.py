"""
Story-subject visuals from Wikidata and the subject's own website.

For a name taken from a headline ("Sarvam", "SpaceX", "Zhipu", "Ant Group") this
finds, in order of preference:
  1. the official logo on Wikimedia Commons (Wikidata P154),
  2. the entity's own photo (Wikidata P18): a company's headquarters, a named
     person's portrait, or a city when the city is the story's subject,
  3. the share image (og:image) of the official website (Wikidata P856),
  4. the website's app icon, or Google's 256 px favicon of the domain.

Logos and icons come back with LOGO_MARK appended to the URL; the downloader
renders them centred on a branded card instead of cropping them.
"""

import json
import re
import urllib.parse
from functools import lru_cache
from typing import List, Optional, Tuple

import requests

HEADERS = {"User-Agent": "SanMitraNewsBot/1.0 (https://sanmitra.ai; newsdesk@sanmitra.ai)"}
BROWSER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
LOGO_MARK = "#logo"
TIMEOUT = 12

HUMAN = "Q5"
# A city may be the subject ("San Francisco is enjoying an AI boom"); other places
# (mountains, rivers, stations) are scenery.
CITY_TYPES = {"Q515", "Q1549591", "Q1093829", "Q5119", "Q200250", "Q1637706", "Q174844", "Q22865"}
# Creative works and other things that share a company's name ("Sarvam" the film).
EXCLUDED_TYPES = {
    "Q11424", "Q24869", "Q229390", "Q202866", "Q482994", "Q134556", "Q7366", "Q105543609", "Q5398426",
    "Q7725634", "Q571", "Q47461344", "Q2001305", "Q1002697", "Q15416", "Q4167410", "Q13442814",
    "Q16521", "Q7432", "Q55488", "Q8502", "Q4022", "Q23397",
}


def _json(url: str) -> dict:
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def commons_file_url(filename: str, width: int = 1280) -> Optional[str]:
    """PNG/JPEG rendering of a Commons file (SVG logos come back as PNG)."""
    try:
        data = _json("https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo"
                     f"&iiprop=url&iiurlwidth={width}&titles=" + urllib.parse.quote("File:" + filename))
        for page in data.get("query", {}).get("pages", {}).values():
            info = (page.get("imageinfo") or [{}])[0]
            return info.get("thumburl") or info.get("url")
    except Exception:
        return None
    return None


def _claim(claims: dict, prop: str):
    for c in claims.get(prop, []):
        value = c.get("mainsnak", {}).get("datavalue", {}).get("value")
        if value:
            return value
    return None


def _instance_ids(claims: dict) -> List[str]:
    return [c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
            for c in claims.get("P31", [])]


@lru_cache(maxsize=256)
def find_entity(name: str) -> Optional[Tuple[str, str, dict]]:
    """(id, label, claims) of the Wikidata item whose label or alias is exactly
    `name` (case-insensitive), preferring items that have a logo, photo or website."""
    try:
        hits = _json("https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en"
                     "&type=item&limit=7&search=" + urllib.parse.quote(name)).get("search", [])
    except Exception:
        return None
    # Exact, case-sensitive: "Own" must not find the OWN network, "Ant" not the insect.
    exact = [h for h in hits if name in ((h.get("label") or ""), (h.get("match", {}).get("text") or ""))]
    if not exact:
        return None
    try:
        ents = _json("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=claims|labels"
                     "&languages=en&ids=" + "|".join(h["id"] for h in exact)).get("entities", {})
    except Exception:
        return None
    for h in exact:
        claims = ents.get(h["id"], {}).get("claims", {})
        types = set(_instance_ids(claims))
        if types & EXCLUDED_TYPES or "P225" in claims or "P171" in claims:  # creative works, taxa
            continue
        if any(p in claims for p in ("P154", "P18", "P856")):
            return h["id"], h.get("label") or name, claims
    return None


@lru_cache(maxsize=128)
def commons_logo_search(label: str) -> Optional[str]:
    """A Commons file named like "<label> logo" (e.g. "L&T Technology Services logo.png")
    for organisations whose Wikidata item has no logo. Every word of the label and
    the word "logo" must be in the file name."""
    words = re.findall(r"[a-z0-9]+", label.lower())
    if not words:
        return None
    try:
        hits = _json("https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search"
                     "&srnamespace=6&srlimit=8&srsearch=" + urllib.parse.quote(f"{label} logo")
                     ).get("query", {}).get("search", [])
    except Exception:
        return None
    for h in hits:
        title = h.get("title", "")[len("File:"):]
        stem, _, ext = title.rpartition(".")
        if ext.lower() not in ("png", "svg", "jpg", "jpeg", "webp"):
            continue
        name_words = set(re.findall(r"[a-z0-9]+", stem.lower()))
        if "logo" in name_words and all(w in name_words for w in words):
            return commons_file_url(title)
    return None


@lru_cache(maxsize=128)
def website_visuals(site: str) -> List[Tuple[str, str]]:
    """[(url, kind)] from an official homepage: its share image ('photo') and its
    largest raster icon ('logo'), then Google's 256 px favicon ('logo')."""
    out: List[Tuple[str, str]] = []
    try:
        r = requests.get(site, headers=BROWSER, timeout=TIMEOUT)
        page = r.text if r.ok else ""
        base = r.url if r.ok else site
    except Exception:
        page, base = "", site
    og = re.search(r'<meta[^>]+(?:property|name)=["\']og:image["\'][^>]*content=["\']([^"\']+)', page, re.I) \
        or re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name)=["\']og:image["\']', page, re.I)
    if og:
        out.append((urllib.parse.urljoin(base, og.group(1)), "photo"))
    icons = []
    for tag in re.findall(r"<link[^>]+>", page, re.I):
        if not re.search(r'rel=["\'][^"\']*(?:apple-touch-icon|icon)[^"\']*["\']', tag, re.I):
            continue
        href = re.search(r'href=["\']([^"\']+)', tag, re.I)
        if not href or href.group(1).lower().split("?")[0].endswith(".svg"):
            continue
        size = re.search(r'sizes=["\'](\d+)x', tag, re.I)
        score = int(size.group(1)) if size else (180 if "apple" in tag.lower() else 32)
        icons.append((score, urllib.parse.urljoin(base, href.group(1))))
    for score, url in sorted(icons, reverse=True):
        if score >= 120:
            out.append((url, "logo"))
            break
    domain = urllib.parse.urlparse(site).netloc
    if domain:
        out.append((f"https://www.google.com/s2/favicons?domain={domain}&sz=256", "logo"))
    return out


def entity_visuals(name: str, is_subject_place_ok: bool = False) -> List[Tuple[str, str]]:
    """[(url, badge)] for a named entity, best first. Places (items with a
    coordinate) only when `is_subject_place_ok`; their photos are scenery otherwise."""
    found = find_entity(name)
    if not found:
        return []
    _, label, claims = found
    is_human = HUMAN in _instance_ids(claims)
    is_place = "P625" in claims and not is_human
    is_city = bool(set(_instance_ids(claims)) & CITY_TYPES)
    # A city has a website and a seal too, but its photo is what tells the story.
    is_org = ("P154" in claims or "P856" in claims) and not is_city
    if is_place and not (is_city and is_subject_place_ok):
        return []
    if not (is_org or is_human or is_city):
        return []  # a concept's photo ("Balancing") is not a story visual
    if is_human and " " not in name.strip():
        return []  # "Huang" alone could be anyone: a person needs their full name
    title = label.upper()
    out: List[Tuple[str, str]] = []

    logo = _claim(claims, "P154")
    if logo and is_org:
        url = commons_file_url(logo)
        if url:
            out.append((url + LOGO_MARK, f"{title} • OFFICIAL LOGO"))
    elif is_org and not is_human:
        url = commons_logo_search(label)
        if url:
            out.append((url + LOGO_MARK, f"{title} • OFFICIAL LOGO"))
    photo = _claim(claims, "P18")
    if photo and (not is_place or is_subject_place_ok):
        url = commons_file_url(photo, 1920)
        if url:
            out.append((url, title))
    site = _claim(claims, "P856")
    if site and not is_human and not is_place:
        for url, kind in website_visuals(site):
            if kind == "logo":
                out.append((url + LOGO_MARK, f"{title} • OFFICIAL LOGO"))
            else:
                out.append((url, f"{title} • OFFICIAL IMAGE"))
    return out


def _domain(url: str) -> str:
    host = urllib.parse.urlparse(url or "").netloc.lower()
    return host[4:] if host.startswith("www.") else host


@lru_cache(maxsize=256)
def resolve_url(url: str) -> str:
    """Follow a short link (is.gd, tinyurl) to the article's real address."""
    if not url:
        return ""
    # Read the redirect headers only: the article's own site may be slow or refuse
    # robots, and only its address is needed.
    current = url
    for _ in range(4):
        try:
            r = requests.get(current, headers=BROWSER, timeout=TIMEOUT, allow_redirects=False, stream=True)
            r.close()
        except Exception:
            break
        location = r.headers.get("location")
        if r.status_code not in (301, 302, 303, 307, 308) or not location:
            break
        current = urllib.parse.urljoin(current, location)
    return current


def outlet_logo(name: str, story_url: str) -> Optional[Tuple[str, str]]:
    """(url, badge) for the logo of the outlet that published the story. Several
    outlets share a name ("The National" is a UAE paper, a Scottish paper and a
    band), so the Wikidata item counts only if its official website is the domain
    the story link actually points to."""
    domain = _domain(resolve_url(story_url))
    if not domain or not name:
        return None
    try:
        hits = _json("https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en"
                     "&type=item&limit=10&search=" + urllib.parse.quote(name)).get("search", [])
        ids = [h["id"] for h in hits if name.lower() in ((h.get("label") or "").lower(),
                                                       (h.get("match", {}).get("text") or "").lower())]
        if not ids:
            return None
        ents = _json("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=claims|labels"
                     "&languages=en&ids=" + "|".join(ids)).get("entities", {})
    except Exception:
        return None
    for eid in ids:
        ent = ents.get(eid, {})
        claims = ent.get("claims", {})
        sites = [c.get("mainsnak", {}).get("datavalue", {}).get("value") for c in claims.get("P856", [])]
        if not any(_domain(u) == domain or domain.endswith("." + _domain(u)) for u in sites if u):
            continue
        label = (ent.get("labels", {}).get("en", {}) or {}).get("value") or name
        logo = _claim(claims, "P154")
        url = commons_file_url(logo) if logo else commons_logo_search(label)
        if url:
            return url + LOGO_MARK, f"{label.upper()} • OFFICIAL LOGO"
    return None
