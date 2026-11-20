"""
URL Sanitizer and Shortener for SanMitra AI News Wire.

Cleans publisher and wire URLs to their shortest, canonical, tracking-free form
so they never wrap over 2-2.5 lines in YouTube descriptions, LinkedIn articles,
or terminal logs.
"""

import re
import urllib.parse
import urllib.request
from typing import Optional

# Query parameters that only track campaigns, sessions or referrals
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_id", "utm_reader", "ref", "ref_src", "ref_url", "cmpid", "source",
    "fbclid", "gclid", "dclid", "msclkid", "ncid", "ocid", "_hsenc", "_hsmi",
    "mc_cid", "mc_eid", "spjobid", "spmailingid", "spreportid", "feature",
    "feedtype", "feedname", "mbid", "igshid", "guccounter", "guce_referrer",
    "guce_referrer_cs", "si", "trk", "tracking_id"
}

# Known URL shortener hosts
KNOWN_SHORTENERS = {
    "tinyurl.com", "is.gd", "bit.ly", "t.co", "gu.com", "reut.rs", "buff.ly", "ow.ly"
}


def strip_tracking_params(url: str) -> str:
    """Removes tracking query parameters, hashes, and cleans URL structure."""
    if not url:
        return ""
    url = url.strip().rstrip(").,]>\"'")
    try:
        parsed = urllib.parse.urlsplit(url)
    except Exception:
        return url

    # Clean query parameters
    if parsed.query:
        query_dict = urllib.parse.parse_qs(parsed.query, keep_blank_values=False)
        cleaned_query = {
            k: v for k, v in query_dict.items()
            if k.lower() not in TRACKING_PARAMS and not k.lower().startswith("utm_")
        }
        new_query = urllib.parse.urlencode(cleaned_query, doseq=True)
    else:
        new_query = ""

    # Reconstruct without fragment (#...)
    cleaned = urllib.parse.urlunsplit((
        parsed.scheme or "https",
        parsed.netloc,
        parsed.path,
        new_query,
        ""  # drop fragment
    ))
    return cleaned


def canonicalize_publisher_url(url: str) -> str:
    """Reduces long publisher paths to their clean canonical permalinks."""
    if not url:
        return ""

    # Economic Times & Times of India article ID permalinks
    # e.g., https://economictimes.indiatimes.com/tech/.../articleshow/136010716.cms
    # -> https://economictimes.indiatimes.com/articleshow/136010716.cms
    et_match = re.search(
        r"https?://(economictimes|timesofindia)\.indiatimes\.com/.+?/articleshow/(\d+\.cms)",
        url,
        re.IGNORECASE
    )
    if et_match:
        host_sub = et_match.group(1).lower()
        art_id = et_match.group(2)
        return f"https://{host_sub}.indiatimes.com/articleshow/{art_id}"

    # arXiv papers: https://arxiv.org/abs/2611.26444
    arxiv_match = re.search(r"https?://arxiv\.org/(?:abs|pdf)/(\d+\.\d+)", url, re.IGNORECASE)
    if arxiv_match:
        return f"https://arxiv.org/abs/{arxiv_match.group(1)}"

    return url


def call_shortener_service(url: str, timeout_sec: float = 3.0) -> Optional[str]:
    """Attempts to shorten a long URL via public shortener APIs (tinyurl or is.gd)."""
    # Try is.gd first
    try:
        api = f"https://is.gd/create.php?format=simple&url={urllib.parse.quote(url)}"
        req = urllib.request.Request(api, headers={"User-Agent": "SanMitraURLCleaner/1.0"})
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            res = resp.read().decode("utf-8").strip()
            if res.startswith("https://is.gd/"):
                return res
    except Exception:
        pass

    # Try tinyurl second
    try:
        api = f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(url)}"
        req = urllib.request.Request(api, headers={"User-Agent": "SanMitraURLCleaner/1.0"})
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            res = resp.read().decode("utf-8").strip()
            if res.startswith("https://tinyurl.com/"):
                return res
    except Exception:
        pass

    return None


def clean_and_shorten_url(url: str, max_chars_before_shortening: int = 65, enable_service: bool = True) -> str:
    """Main entrypoint: strips tracking, applies canonical short permalinks, and shortens if still long."""
    if not url:
        return ""

    url = strip_tracking_params(url)
    url = canonicalize_publisher_url(url)

    # If it is already short or is a known shortener, return directly
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower()
    if host in KNOWN_SHORTENERS or any(host.endswith("." + s) for s in KNOWN_SHORTENERS):
        return url

    # If length exceeds threshold and service shortening is enabled, shorten it
    if enable_service and len(url) > max_chars_before_shortening:
        short = call_shortener_service(url)
        if short:
            return short

    return url


def is_shortener_host(host: str) -> bool:
    """Returns True if the hostname is a recognized shortener service."""
    host = (host or "").lower()
    return host in KNOWN_SHORTENERS or any(host.endswith("." + s) for s in KNOWN_SHORTENERS)
