"""
Paywall Detector and Free Alternative Source Finder for SanMitra AI News Wire.

Enforces zero-subscription policy:
1. Detects paywalls and subscription gates (both domain-level and page content).
2. Searches for alternative free, reputable news outlets covering the exact same development.
3. If no free alternative is found, flags the story to be DROPPED.
"""

import html
import logging
import re
import urllib.parse
from typing import Optional, Dict
import requests
from bs4 import BeautifulSoup

from src.aibrief.crew.text_utils import same_event
from src.aibrief.source_authority import score_source, is_opinion_url
from src.aibrief.url_cleaner import clean_and_shorten_url, is_shortener_host

logger = logging.getLogger("PaywallDetector")

# Comprehensive set of domains with subscription paywalls, registration walls, or meter gates
PAYWALLED_DOMAINS = {
    "theverge.com", "thehindu.com", "thehindubusinessline.com", "scmp.com",
    "nikkei.com", "asia.nikkei.com", "livemint.com", "business-standard.com",
    "wired.com", "technologyreview.com", "bloomberg.com", "wsj.com", "ft.com",
    "theinformation.com", "nytimes.com", "washingtonpost.com", "economist.com",
    "theatlantic.com", "newyorker.com", "barrons.com", "businessinsider.com",
    "insider.com", "telegraph.co.uk", "straitstimes.com", "thetimes.co.uk",
    "thesundaytimes.co.uk", "fortune.com", "seekingalpha.com", "afr.com",
    "theaustralian.com.au", "smh.com.au", "theage.com.au", "theglobeandmail.com",
    "lemonde.fr", "lesechos.fr", "hbr.org", "newscientist.com", "techinasia.com",
    "inc42.com", "forbes.com", "law360.com", "semafor.com"
}

# Specific paths within otherwise free domains that require paid subscriptions
PAYWALLED_PATHS = {
    "economictimes.indiatimes.com": "/prime/",
}

# Phrases found inside article text indicating a paywall or subscriber gate
PAYWALL_CONTENT_MARKERS = [
    r"this article is for subscribers only",
    r"to continue reading, subscribe",
    r"subscribe to read the full (?:story|article)",
    r"exclusive to subscribers",
    r"join now to read",
    r"you have reached your limit of free articles",
    r"start your free trial to continue",
    r"already a subscriber\?\s*sign in",
    r"please subscribe to access",
    r"a paid subscription is required",
    r"subscriber-only",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 SanMitraNewsWire/1.0"
}


def _on_domain(host: str, domains: set) -> bool:
    host = (host or "").lower()
    return any(host == d or host.endswith("." + d) for d in domains)


def is_paywalled_url(url: str) -> bool:
    """Returns True if the URL points to a domain or section known to require subscriptions."""
    if not url:
        return False
    parsed = urllib.parse.urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    if _on_domain(host, PAYWALLED_DOMAINS):
        return True
    return any(_on_domain(host, [d]) and prefix in parsed.path for d, prefix in PAYWALLED_PATHS.items())


def has_paywall_markers(text: str) -> bool:
    """Checks whether the article HTML or body text contains subscriber paywall markers."""
    if not text:
        return False
    text_lower = text.lower()
    return any(re.search(marker, text_lower) for marker in PAYWALL_CONTENT_MARKERS)


def is_paywalled_story(url: str, body_text: str = "") -> bool:
    """Combines domain check and body marker check."""
    return is_paywalled_url(url) or has_paywall_markers(body_text)


def find_free_alternative(headline: str, original_url: str = "") -> Optional[Dict[str, str]]:
    """Searches news wires for a free alternative reporting on the exact same event.

    Returns dict with {"source": str, "url": str} if a free reputable source is found,
    or None if no alternative is available (mandating dropping the story).
    """
    if not headline:
        return None

    # Clean headline for search query: extract significant keywords
    clean_head = re.sub(r'[*_~`#"]+', '', headline)
    # Remove source prefixes/suffixes e.g. " - The Guardian", " | Letter"
    clean_head = re.sub(r'\s*[-|]\s*[A-Za-z0-9\s]+$', '', clean_head).strip()
    words = [w for w in clean_head.split() if len(w) > 3 and not re.match(r'^(about|after|their|these|those|which|where|could|would)$', w, re.I)]
    query = " ".join(words[:7])
    if not query:
        return None

    encoded_query = urllib.parse.quote(f'"{query}"' if len(words) <= 4 else query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    orig_parsed = urllib.parse.urlparse(original_url) if original_url else None
    orig_host = (orig_parsed.hostname or "").lower() if orig_parsed else ""

    try:
        resp = requests.get(rss_url, headers=HEADERS, timeout=6)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.content, "html.parser")
        items = soup.find_all("item")

        for item in items[:10]:
            title_elem = item.find("title")
            link_elem = item.find("link")
            source_elem = item.find("source")

            cand_title = html.unescape(title_elem.text if title_elem else "")
            cand_link = link_elem.text.strip() if link_elem else ""
            cand_source = source_elem.text.strip() if source_elem else ""

            if " - " in cand_title:
                parts = cand_title.rsplit(" - ", 1)
                cand_title = parts[0].strip()
                if not cand_source:
                    cand_source = parts[1].strip()

            # Skip if this is the exact same paywalled domain
            cand_parsed = urllib.parse.urlparse(cand_link)
            cand_host = (cand_parsed.hostname or "").lower()
            if orig_host and (cand_host == orig_host or cand_host.endswith("." + orig_host)):
                continue

            # Skip if candidate itself is a known paywalled site
            if is_paywalled_url(cand_link) or _on_domain(cand_host, PAYWALLED_DOMAINS):
                continue

            # Must be about the same event
            if not same_event(headline, cand_title):
                continue

            # Score candidate source
            score, tier, identified = score_source(cand_link)
            final_source = cand_source or identified

            cleaned_url = clean_and_shorten_url(cand_link)
            logger.info(f"[+] Found free alternative source for '{headline[:50]}...': {final_source} ({cleaned_url})")
            return {
                "source": final_source,
                "url": cleaned_url
            }

    except Exception as e:
        logger.warning(f"Error querying free alternative for '{headline[:40]}': {e}")

    return None
