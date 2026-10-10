"""
NewsHarvester Agent - SanMitra AI News Wire
Gathers candidate stories from RSS feeds and search, keeps only AI stories
published in the window before the broadcast, and fetches the full article
text that the fact-checker verifies against.
"""

from datetime import datetime
import logging
import re
import urllib.parse
import urllib.request

from .text_utils import IST, clean_feed_text, contains_any, is_recent, parse_published

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("NewsHarvester")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

# "outlet" is the name viewers see on screen. It must be the publication,
# never the feed ("TechCrunch AI") or a bare domain.
FEEDS = [
    {"outlet": "Reuters", "url": "https://www.reutersagency.com/feed/?best-topics=tech&post_type=best", "region": "WORLD"},
    {"outlet": "TechCrunch", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "region": "USA"},
    {"outlet": "The Verge", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "region": "USA"},
    {"outlet": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "region": "WORLD"},
    {"outlet": "Defense News", "url": "https://www.defensenews.com/arc/outboundfeeds/rss/category/technology/?outputType=xml", "region": "WORLD"},
    {"outlet": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "region": "USA"},
    {"outlet": "VentureBeat", "url": "https://venturebeat.com/category/ai/feed/", "region": "USA"},
    {"outlet": "The Guardian", "url": "https://www.theguardian.com/technology/artificialintelligenceai/rss", "region": "WORLD"},
    {"outlet": "The Economic Times", "url": "https://economictimes.indiatimes.com/tech/artificial-intelligence/rssfeeds/81580397.cms", "region": "INDIA"},
    {"outlet": "Inc42", "url": "https://inc42.com/feed/", "region": "INDIA"},
    {"outlet": "The Times of India", "url": "https://timesofindia.indiatimes.com/rssfeeds/66949542.cms", "region": "INDIA"},
    {"outlet": "South China Morning Post", "url": "https://www.scmp.com/rss/318208/feed", "region": "CHINA"},
    {"outlet": "The Korea Times", "url": "https://www.koreatimes.co.kr/www/rss/tech.xml", "region": "ASIA"},
    {"outlet": "The Japan Times", "url": "https://www.japantimes.co.jp/feed/category/business/tech/", "region": "ASIA"},
    {"outlet": "Google", "url": "https://blog.google/technology/ai/rss/", "region": "USA"},
    {"outlet": "OpenAI", "url": "https://openai.com/news/rss.xml", "region": "USA"},
]

SEARCH_QUERIES = [
    ("WORLD", "artificial intelligence defense drone radar supercomputer news"),
    ("USA", "OpenAI Google Anthropic frontier model clinical healthcare news"),
    ("CHINA", "China State Council Beijing artificial intelligence microelectronics Qwen"),
    ("ASIA", "Japan South Korea automated AI cyberattack banking semiconductor"),
    ("INDIA", "India AI startups sovereign compute MeitY GPU venture capital"),
]

# Whole-word matches only (see text_utils.contains_any). Generic company names
# like "Google" or "Meta" are left out: they are not evidence of an AI story.
AI_KEYWORDS = [
    "ai", "a.i.", "artificial intelligence", "machine learning", "deep learning", "llm",
    "large language model", "generative", "chatbot", "chatgpt", "openai", "anthropic",
    "claude", "gemini", "deepmind", "deepseek", "qwen", "mistral", "llama", "copilot",
    "nvidia", "gpu", "semiconductor", "chipmaker", "neural network", "datacenter",
    "data center", "data centre", "supercomputer", "humanoid", "robotics", "hugging face",
]

MAX_AGE_HOURS = 36


def is_ai_story(title, summary=""):
    return contains_any(f"{title} {summary}", AI_KEYWORDS)


def _entry_published(entry):
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        return datetime(*parsed[:6]).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    return entry.get("published", "") or entry.get("updated", "")


class NewsHarvester:
    """Harvests candidate AI stories from the window before the broadcast."""

    def __init__(self, target_date=None, max_age_hours=MAX_AGE_HOURS):
        self.target_date = target_date or datetime.now(IST).strftime("%Y-%m-%d")
        self.max_age_hours = max_age_hours

    def fetch_feed_items(self):
        """Parse RSS/Atom feeds using feedparser or a regex fallback."""
        items = []
        try:
            import feedparser
        except ImportError:
            feedparser = None
            logger.warning("feedparser not installed; falling back to regex feed parser.")

        for feed_cfg in FEEDS:
            try:
                if feedparser:
                    feed = feedparser.parse(feed_cfg["url"], agent=USER_AGENT)
                    entries = [
                        (e.get("title", ""), e.get("link", ""),
                         e.get("summary", "") or e.get("description", ""), _entry_published(e))
                        for e in feed.entries[:12]
                    ]
                else:
                    req = urllib.request.Request(feed_cfg["url"], headers={"User-Agent": USER_AGENT})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        content = resp.read().decode("utf-8", errors="ignore")
                    entries = []
                    for block in re.findall(r"<item>(.*?)</item>", content, re.DOTALL | re.IGNORECASE)[:12]:
                        def tag(name):
                            m = re.search(rf"<{name}>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{name}>", block, re.DOTALL | re.IGNORECASE)
                            return m.group(1).strip() if m else ""
                        entries.append((tag("title"), tag("link"), tag("description"), tag("pubDate")))

                for title, link, summary, published in entries:
                    title, link = clean_feed_text(title), link.strip()
                    if title and link:
                        items.append({
                            "title": title,
                            "source": feed_cfg["outlet"],
                            "url": link,
                            "summary": clean_feed_text(summary)[:600],
                            "region": feed_cfg["region"],
                            "published": published,
                            "origin": "feed",
                        })
            except Exception as e:
                logger.debug(f"Feed fetch failed for {feed_cfg['outlet']}: {e}")

        logger.info(f"Gathered {len(items)} feed items.")
        return items

    def search_recent_stories(self, queries=None):
        """Supplementary search for regional bureau coverage.

        Search results carry no reliable date, so "published" is left empty and
        filled from the article's own metadata in fetch_article().
        """
        results = []
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                for region, q in queries or SEARCH_QUERIES:
                    try:
                        for h in ddgs.news(q, max_results=5, timelimit="d"):
                            url = h.get("url") or h.get("href", "")
                            results.append({
                                "title": clean_feed_text(h.get("title", "")),
                                "source": h.get("source", "") or urllib.parse.urlparse(url).netloc.replace("www.", ""),
                                "url": url,
                                "summary": clean_feed_text(h.get("body", "")),
                                "region": region,
                                "published": h.get("date", ""),
                                "origin": "search",
                            })
                    except Exception as e:
                        logger.debug(f"Search failed for '{q}': {e}")
        except Exception as e:
            logger.debug(f"duckduckgo_search unavailable: {e}")
        return results

    def fetch_article(self, url):
        """Download an article and return {"text", "published"} from the page itself.

        Returns empty text when the article cannot be extracted. The fact-checker
        drops such stories: there is nothing to verify the script against.
        """
        try:
            import trafilatura
        except ImportError:
            logger.error("trafilatura is not installed; articles cannot be verified.")
            return {"text": "", "published": ""}

        html = None
        try:
            html = trafilatura.fetch_url(url)
        except Exception:
            html = None
        if not html:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=12) as r:
                    html = r.read().decode("utf-8", errors="ignore")
            except Exception as e:
                logger.debug(f"Article download failed for {url}: {e}")
                return {"text": "", "published": ""}

        text, published = "", ""
        try:
            text = trafilatura.extract(html, include_comments=False, include_tables=False) or ""
            meta = trafilatura.extract_metadata(html)
            if meta is not None and getattr(meta, "date", None):
                published = meta.date
        except Exception as e:
            logger.debug(f"Article extraction failed for {url}: {e}")
        return {"text": text.strip(), "published": published}

    def filter_candidates(self, raw_items):
        """URL/title dedup, AI relevance and recency. Undated search hits are kept for now."""
        seen_urls, seen_titles, kept = set(), set(), []
        rejected = {"duplicate": 0, "not_ai": 0, "stale": 0}

        for item in raw_items:
            url = item.get("url", "").split("?")[0].rstrip("/")
            norm_title = " ".join(re.sub(r"[^a-z0-9\s]", "", item.get("title", "").lower()).split()[:8])
            if not url or not norm_title or url in seen_urls or norm_title in seen_titles:
                rejected["duplicate"] += 1
                continue
            if not is_ai_story(item.get("title", ""), item.get("summary", "")):
                rejected["not_ai"] += 1
                continue
            published = item.get("published", "")
            if parse_published(published) is not None and not is_recent(published, self.target_date, self.max_age_hours):
                rejected["stale"] += 1
                continue
            if parse_published(published) is None and item.get("origin") == "feed":
                # A feed entry with no date cannot be shown to be from the last day.
                rejected["stale"] += 1
                continue

            seen_urls.add(url)
            seen_titles.add(norm_title)
            kept.append(item)

        logger.info(f"Harvest filter kept {len(kept)}; rejected {rejected}.")
        return kept

    def harvest(self):
        return self.filter_candidates(self.fetch_feed_items() + self.search_recent_stories())


if __name__ == "__main__":
    harvester = NewsHarvester()
    articles = harvester.harvest()
    print(f"Total articles harvested: {len(articles)}")
    for i, a in enumerate(articles[:10], 1):
        print(f"{i}. [{a['region']}] {a['title']} ({a['source']}, {a['published']})")
