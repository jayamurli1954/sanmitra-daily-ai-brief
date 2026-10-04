"""
Breaking-wire intake for SanMitra AI News Wire.

Google News RSS only returns a headline. This module reads publisher feeds
that carry the article text, keeps developments from the last day, and
returns at most 12 breaks. Routine explainers, reviews, and headline-only
items are dropped. No story is invented when a bureau is quiet.
"""

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import html
import re
import warnings
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 SanMitraNewsWire/1.1"
    )
}

MAX_STORIES = 12
MIN_BODY_CHARS = 100
LOOKBACK_HOURS = 30
MAX_PAGE_FETCHES = 12
MAX_PER_ENTITY = 2

# Publisher feeds. Bureau is only the default; the headline can reassign it.
WIRE_FEEDS = [
    {"bureau": "USA", "source": "The Verge", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "ai_section": True},
    {"bureau": "USA", "source": "TechCrunch", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "ai_section": True},
    {"bureau": "USA", "source": "Ars Technica", "url": "https://arstechnica.com/ai/feed/", "ai_section": True},
    {"bureau": "USA", "source": "CNBC", "url": "https://www.cnbc.com/id/19854910/device/rss/rss.html"},
    {"bureau": "WORLD", "source": "BBC", "url": "https://feeds.bbci.co.uk/news/technology/rss.xml"},
    {"bureau": "WORLD", "source": "The Guardian", "url": "https://www.theguardian.com/technology/artificialintelligenceai/rss", "ai_section": True},
    {"bureau": "WORLD", "source": "United Nations", "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml"},
    {"bureau": "CHINA", "source": "Sixth Tone", "url": "https://www.sixthtone.com/rss"},
    {"bureau": "CHINA", "source": "Rest of World", "url": "https://restofworld.org/feed/"},
    {"bureau": "ASIA", "source": "Nikkei Asia", "url": "https://asia.nikkei.com/rss/feed/nar"},
    {"bureau": "ASIA", "source": "South China Morning Post", "url": "https://www.scmp.com/rss/318215/feed"},
    {"bureau": "INDIA", "source": "The Economic Times", "url": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms"},
    {"bureau": "INDIA", "source": "The Hindu", "url": "https://www.thehindu.com/sci-tech/technology/feeder/default.rss"},
    {"bureau": "INDIA", "source": "Mint", "url": "https://www.livemint.com/rss/technology"},
]

AI_PATTERN = re.compile(
    r"\b("
    r"artificial intelligence|generative ai|machine learning|large language|"
    r"openai|anthropic|deepseek|nvidia|chatbot|\bllm\b|\bgpu\b|semiconductor|"
    r"humanoid|frontier model|ai model|ai agent|ai safety|ai chip|"
    r"\bai\b"
    r")\b",
    re.I,
)

ROUTINE_PATTERN = re.compile(
    r"\b("
    r"how to|explainer|opinion|hands-on|what to know|buying guide|"
    r"newsletter|podcast|roundup|we tried|deal of the day|tips for|"
    r"beginner's guide|review:|product review"
    r")\b",
    re.I,
)

BREAKING_PATTERN = re.compile(
    r"\b("
    r"launch(?:es|ed)?|unveil(?:s|ed)?|ban(?:s|ned)?|acqui(?:re|res|sition)|"
    r"halt(?:s|ed)?|pause(?:s|d)?|sue[sd]?|lawsuit|file[sd]?|approv(?:e|es|ed)|"
    r"warn(?:s|ed|ing)?|scrap(?:s|ped)?|cancel(?:s|led)?|sign(?:s|ed)?|"
    r"ditch(?:es|ed)?|abandon(?:s|ed)?|rollout|orders?|"
    r"declar(?:e|es|ed)|breach|hack(?:ed|ing)?|ipo|merger|sanction(?:s|ed)?|"
    r"emergency|shutdown|recall|arrest(?:ed)?|probe|investigat(?:e|es|ion)|"
    r"exclusive|breaking|resign(?:s|ed)?|appoint(?:s|ed)?|"
    r"billion|treaty|executive order|block(?:s|ed)?|restrict(?:s|ed)?|"
    r"allow(?:s|ed)?|permit(?:s|ted)?|clear(?:s|ed)?|"
    r"plunge[sd]?|surge[sd]?|tumble[sd]?|slide[sd]?"
    r")\b",
    re.I,
)

PRODUCT_PATTERN = re.compile(
    r"\b(price, features|specs and|unboxing|smartphone|earbuds|smartwatch)\b|\barrives with\b",
    re.I,
)

LEAD_ENTITIES = (
    "openai", "nvidia", "anthropic", "google", "meta", "amd", "microsoft",
    "apple", "deepseek", "huawei", "samsung", "tsmc", "bytedance",
)

BUREAU_RULES = [
    ("INDIA", re.compile(r"\b(india|indian|delhi|bengaluru|bangalore|mumbai|meity|indiaai|sitharaman)\b", re.I)),
    ("CHINA", re.compile(r"\b(china|chinese|beijing|shanghai|huawei|deepseek|alibaba|bytedance|tencent|baidu)\b", re.I)),
    ("WORLD", re.compile(r"\b(united nations|un general assembly|security council|multilateral)\b", re.I)),
    ("ASIA", re.compile(r"\b(singapore|japan|japanese|korea|korean|taiwan|tsmc|samsung|indonesia|vietnam)\b", re.I)),
    ("USA", re.compile(r"\b(u\.s\.|united states|american|openai|anthropic|white house|congress|senate|silicon valley|trump|spacex|musk|nvidia|apple|google|meta|amazon|microsoft)\b", re.I)),
]


def _clean(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _parse_time(raw: str) -> Optional[datetime]:
    if not raw:
        return None
    raw = raw.strip()
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _sentences(text: str, limit: int = 4) -> List[str]:
    parts = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 40]
    return parts[:limit]


def _item_link(node) -> str:
    atom_links = node.find_all("link")
    for link in atom_links:
        href = link.get("href")
        rel = (link.get("rel") or ["alternate"])
        if isinstance(rel, str):
            rel = [rel]
        if href and "alternate" in rel:
            return href.strip()
    for link in atom_links:
        href = link.get("href")
        if href:
            return href.strip()
    link = node.find("link")
    if link and link.string and link.string.strip().startswith("http"):
        return link.string.strip()
    match = re.search(r"<link>(https?://[^<]+)</link>", str(node))
    if match:
        return match.group(1).strip()
    for child in node.children:
        if isinstance(child, str) and child.strip().startswith("http"):
            return child.strip().split()[0]
    loose = re.search(r"https?://[^\s<]+", str(node))
    if loose:
        return loose.group(0).rstrip(">")
    return ""


def _item_body(node) -> str:
    """Prefer a clean standfirst over a long HTML blob full of related links."""
    fields = [
        node.find("description"),
        node.find("summary"),
        node.find("encoded"),
        node.find("content"),
    ]
    cleaned = []
    for candidate in fields:
        if candidate is None:
            continue
        text = _clean(candidate.string or candidate.get_text() or "")
        if text and text not in cleaned:
            cleaned.append(text)
    standfirst = [text for text in cleaned if MIN_BODY_CHARS <= len(text) <= 1800]
    if standfirst:
        return max(standfirst, key=len)
    return max(cleaned, key=len) if cleaned else ""


def _lead_entity(headline: str) -> str:
    text = headline.lower()
    if "chatgpt" in text or "gpt-" in text:
        return "openai"
    for name in LEAD_ENTITIES:
        if name in text:
            return name
    return ""


_fetch_count = {"n": 0}


def _fetch_article_lead(url: str) -> str:
    if not url or "news.google.com" in url or _fetch_count["n"] >= MAX_PAGE_FETCHES:
        return ""
    _fetch_count["n"] += 1
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
    except Exception:
        return ""
    ctype = resp.headers.get("Content-Type", "")
    if resp.status_code != 200 or "html" not in ctype:
        return ""
    soup = BeautifulSoup(resp.content[:500_000], "html.parser")
    paragraphs = []
    for p in soup.select("article p"):
        text = _clean(p.get_text(" ", strip=True))
        if len(text) > 80:
            paragraphs.append(text)
        if len(paragraphs) >= 4:
            break
    if paragraphs:
        return " ".join(paragraphs)
    og = soup.find("meta", attrs={"property": "og:description"})
    if og and og.get("content"):
        return _clean(og["content"])
    return ""


def _assign_bureau(headline: str, body: str, default: str) -> str:
    """Headline country wins. A regional paper reprinting a US deal is not filed under that paper's country."""
    for bureau, pattern in BUREAU_RULES:
        if pattern.search(headline):
            return bureau
    lead = f"{headline} {body[:320]}"
    for bureau, pattern in BUREAU_RULES:
        if pattern.search(lead):
            return bureau
    if default:
        return default
    return "WORLD"


def _breaking_score(headline: str, body: str, age_hours: float) -> int:
    text = f"{headline} {body[:900]}"
    score = 25
    if BREAKING_PATTERN.search(headline):
        score += 30
    elif BREAKING_PATTERN.search(text):
        score += 18
    if re.search(r"\$?\d+(\.\d+)?\s*(billion|million|bn)", text, re.I):
        score += 12
    if age_hours <= 12:
        score += 18
    elif age_hours <= 24:
        score += 10
    if len(body) >= 500:
        score += 8
    if ROUTINE_PATTERN.search(headline):
        score -= 40
    return score


def _tokens(headline: str) -> set:
    stop = {
        "with", "from", "that", "this", "after", "over", "into", "about",
        "says", "said", "will", "have", "been", "their", "they", "what",
        "amid", "more", "than", "into", "your", "just", "news",
    }
    words = set(re.findall(r"[a-z0-9]{4,}", headline.lower()))
    return words - stop


def _same_story(a: set, b: set) -> bool:
    if not a or not b:
        return False
    overlap = a & b
    smaller = min(len(a), len(b))
    return len(overlap) >= 3 or (smaller and len(overlap) / smaller >= 0.55)


def fetch_feed(feed: Dict) -> List[Dict]:
    bureau = feed["bureau"]
    source = feed["source"]
    url = feed["url"]
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200 or not resp.content:
            print(f"    [!] {source} returned {resp.status_code}")
            return []
    except Exception as exc:
        print(f"    [!] {source} unreachable: {exc}")
        return []

    soup = BeautifulSoup(resp.content, "html.parser")
    nodes = soup.find_all("item") or soup.find_all("entry")
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=LOOKBACK_HOURS)

    for node in nodes[:20]:
        title_node = node.find("title")
        headline = _clean(title_node.get_text() if title_node else "")
        if " - " in headline:
            headline = headline.rsplit(" - ", 1)[0].strip()
        if len(headline) < 24:
            continue

        published = _parse_time(
            (node.find("pubdate") or node.find("published") or node.find("updated") or node.find("date") or {}).get_text()
            if (node.find("pubdate") or node.find("published") or node.find("updated") or node.find("date"))
            else ""
        )
        if published and published < cutoff:
            continue

        body = _item_body(node)
        link = _item_link(node)
        blob = f"{headline} {body}"
        if body and not AI_PATTERN.search(blob) and not BREAKING_PATTERN.search(headline):
            continue
        if PRODUCT_PATTERN.search(headline):
            continue
        if ROUTINE_PATTERN.search(headline) and not BREAKING_PATTERN.search(blob):
            continue
        if len(body) < len(headline) + 25 and not link:
            continue

        # A one-line dek is too short for a five-minute broadcast. Pull the article lead.
        if link and len(body.split()) < 80 and BREAKING_PATTERN.search(headline):
            fetched = _fetch_article_lead(link)
            if len(fetched) > len(body):
                body = fetched

        if len(body) < MIN_BODY_CHARS or len(body) < len(headline) + 25:
            continue
        lead = f"{headline} {body[:450]}"
        if not BREAKING_PATTERN.search(lead):
            continue
        if not AI_PATTERN.search(lead):
            continue
        summary = _broadcast_summary(body)
        shares_headline = len(_tokens(headline) & _tokens(summary))
        if _JUNK_SENTENCE.search(summary) and shares_headline < 2:
            continue

        age_hours = 20.0
        if published:
            age_hours = max(0.0, (now - published).total_seconds() / 3600.0)

        items.append({
            "headline": headline,
            "body": body,
            "link": link,
            "source": source,
            "published": published.isoformat() if published else "",
            "age_hours": round(age_hours, 1),
            "bureau": _assign_bureau(headline, body, bureau),
            "breaking_score": _breaking_score(headline, body, age_hours),
            "tokens": _tokens(headline),
        })
    return items


def _collapse_duplicates(items: List[Dict]) -> List[Dict]:
    kept: List[Dict] = []
    for item in sorted(items, key=lambda s: (s["breaking_score"], len(s["body"])), reverse=True):
        match = None
        for existing in kept:
            if _same_story(item["tokens"], existing["tokens"]):
                match = existing
                break
        if match is None:
            item["confirming_sources"] = [item["source"]]
            kept.append(item)
            continue
        if item["source"] not in match["confirming_sources"]:
            match["confirming_sources"].append(item["source"])
            match["breaking_score"] += 12
        if len(item["body"]) > len(match["body"]):
            match["body"] = item["body"]
            match["link"] = item["link"] or match["link"]
    return kept


def _within_entity_cap(story: Dict, chosen: List[Dict]) -> bool:
    entity = _lead_entity(story["headline"])
    if not entity:
        return True
    used = sum(1 for item in chosen if _lead_entity(item["headline"]) == entity)
    return used < MAX_PER_ENTITY


def _select(items: List[Dict], max_stories: int) -> List[Dict]:
    ranked = [s for s in items if s["breaking_score"] >= 45]
    ranked.sort(key=lambda s: s["breaking_score"], reverse=True)

    chosen: List[Dict] = []
    for bureau in ("WORLD", "USA", "CHINA", "ASIA", "INDIA"):
        for story in ranked:
            if story["bureau"] == bureau and story not in chosen and _within_entity_cap(story, chosen):
                chosen.append(story)
                break
    for story in ranked:
        if story in chosen:
            continue
        if len(chosen) >= max_stories:
            break
        if not _within_entity_cap(story, chosen):
            continue
        chosen.append(story)
    chosen = chosen[:max_stories]
    chosen.sort(key=lambda s: s["breaking_score"], reverse=True)
    return chosen


_JUNK_SENTENCE = re.compile(
    r"\b(sign up|newsletter|live updates|business live|latest updates|read more|subscribe|related stories)\b|"
    r"\b(i don't|i do not|do you still|neither should you|we must|fool me|by the day)\b",
    re.I,
)


def _broadcast_summary(body: str) -> str:
    sentences = []
    for sentence in _sentences(body, limit=8):
        if sentence.endswith("?"):
            continue
        if "|" in sentence or re.search(r"\b(getty images|photo caption|via reuters)\b", sentence, re.I):
            continue
        if _JUNK_SENTENCE.search(sentence):
            continue
        sentences.append(sentence)
        spoken = " ".join(sentences)
        # About six sentences, or ~110 words: long enough for a 5-minute show across a normal desk.
        if len(sentences) >= 6 or len(spoken.split()) >= 110:
            break
    if not sentences:
        clipped = body[:420].rsplit(" ", 1)[0].strip()
        return clipped
    return " ".join(sentences)


def collect_breaking_stories(max_stories: int = MAX_STORIES) -> List[Dict]:
    """
    Pull full-text breaks from publisher wires.
    Returns at most max_stories dicts with headline, summary, bureau, source, and score.
    """
    _fetch_count["n"] = 0
    print("=" * 70)
    print("SANMITRA BREAKING WIRE")
    print(f"Window: last {LOOKBACK_HOURS} hours | Cap: {max_stories} stories | Dek or article text required")
    print("=" * 70)

    pool: List[Dict] = []
    for feed in WIRE_FEEDS:
        print(f"[*] {feed['source']} ({feed['bureau']})")
        found = fetch_feed(feed)
        print(f"    -> {len(found)} full-text breaks")
        pool.extend(found)

    unique = _collapse_duplicates(pool)
    selected = _select(unique, max_stories)
    print(f"\n[+] Candidates with full text: {len(pool)} | After dedupe: {len(unique)} | On air: {len(selected)}")

    stories = []
    for story in selected:
        summary = _broadcast_summary(story["body"])
        stories.append({
            "headline": story["headline"],
            "summary": summary,
            "bureau": story["bureau"],
            "region": story["bureau"] if story["bureau"] != "GLOBAL" else "WORLD",
            "source": story["source"],
            "source_url": story["link"],
            "published_at": story["published"],
            "age_hours": story["age_hours"],
            "breaking_score": story["breaking_score"],
            "confirming_sources": story.get("confirming_sources", [story["source"]]),
        })
        print(
            f"    [{story['bureau']}] {story['breaking_score']:>3}  "
            f"{story['headline'][:88]}  ({story['source']}, {story['age_hours']}h)"
        )
    return stories
