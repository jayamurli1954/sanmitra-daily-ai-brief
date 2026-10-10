"""
NewsHarvester Agent - SanMitra AI News Wire v7.0
Autonomous multi-source intelligence gathering across 20+ authentic feeds & search APIs.
"""

from datetime import datetime, timedelta, timezone
import json
import logging
import os
import re
import urllib.parse
import urllib.request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("NewsHarvester")

FEEDS = [
    {"source": "Reuters Tech", "url": "https://www.reutersagency.com/feed/?best-topics=tech&post_type=best", "region": "WORLD"},
    {"source": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "region": "USA"},
    {"source": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "region": "USA"},
    {"source": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "region": "WORLD"},
    {"source": "Defense News", "url": "https://www.defensenews.com/arc/outboundfeeds/rss/category/technology/?outputType=xml", "region": "WORLD"},
    {"source": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "region": "USA"},
    {"source": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "region": "USA"},
    {"source": "The Guardian Tech", "url": "https://www.theguardian.com/technology/artificialintelligenceai/rss", "region": "WORLD"},
    {"source": "Economic Times AI", "url": "https://economictimes.indiatimes.com/tech/artificial-intelligence/rssfeeds/81580397.cms", "region": "INDIA"},
    {"source": "Inc42", "url": "https://inc42.com/feed/", "region": "INDIA"},
    {"source": "Times of India Tech", "url": "https://timesofindia.indiatimes.com/rssfeeds/66949542.cms", "region": "INDIA"},
    {"source": "South China Morning Post AI", "url": "https://www.scmp.com/rss/318208/feed", "region": "CHINA"},
    {"source": "Korea Times Tech", "url": "https://www.koreatimes.co.kr/www/rss/tech.xml", "region": "ASIA"},
    {"source": "Japan Times Tech", "url": "https://www.japantimes.co.jp/feed/category/business/tech/", "region": "ASIA"},
    {"source": "Google Blog", "url": "https://blog.google/technology/ai/rss/", "region": "USA"},
    {"source": "OpenAI Index", "url": "https://openai.com/news/rss.xml", "region": "USA"},
]

SEARCH_QUERIES = [
    ("WORLD", "artificial intelligence defense drone radar supercomputer news"),
    ("USA", "OpenAI Google Anthropic frontier model clinical healthcare news"),
    ("CHINA", "China State Council Beijing artificial intelligence microelectronics Qwen"),
    ("ASIA", "Japan South Korea automated AI cyberattack banking semiconductor"),
    ("INDIA", "India AI startups sovereign compute MeitY GPU venture capital"),
]


class NewsHarvester:
    """Harvests and extracts full-text articles for the last 24-48 hours."""

    def __init__(self, target_date=None):
        if target_date:
            self.target_date = target_date
        else:
            ist = timezone(timedelta(hours=5, minutes=30))
            self.target_date = datetime.now(ist).strftime("%Y-%m-%d")

    def fetch_feed_items(self):
        """Parse RSS/Atom feeds using feedparser or fallback urllib."""
        items = []
        try:
            import feedparser
            has_feedparser = True
        except ImportError:
            has_feedparser = False
            logger.warning("feedparser not installed; falling back to regex feed parser.")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }

        for feed_cfg in FEEDS:
            feed_url = feed_cfg["url"]
            source_name = feed_cfg["source"]
            default_region = feed_cfg["region"]

            try:
                if has_feedparser:
                    import feedparser
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:8]:
                        title = entry.get("title", "").strip()
                        link = entry.get("link", "").strip()
                        summary = entry.get("summary", "") or entry.get("description", "")
                        summary_clean = re.sub(r"<[^>]+>", " ", summary).strip()

                        if title and link:
                            items.append({
                                "title": title,
                                "source": source_name,
                                "url": link,
                                "summary": summary_clean[:400],
                                "region": default_region,
                                "published": entry.get("published", "")
                            })
                else:
                    req = urllib.request.Request(feed_url, headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        content = resp.read().decode("utf-8", errors="ignore")
                    titles = re.findall(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", content, re.IGNORECASE)
                    links = re.findall(r"<link>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</link>", content, re.IGNORECASE)
                    for t, l in zip(titles[1:9], links[1:9]):
                        items.append({
                            "title": t.strip(),
                            "source": source_name,
                            "url": l.strip(),
                            "summary": "",
                            "region": default_region,
                            "published": ""
                        })
            except Exception as e:
                logger.debug(f"Feed fetch failed for {source_name}: {e}")

        logger.info(f"Gathered {len(items)} feed items.")
        return items

    def search_recent_stories(self, queries=None):
        """Supplementary search for regional bureau coverage."""
        if queries is None:
            queries = SEARCH_QUERIES

        results = []
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                for region, q in queries:
                    try:
                        hits = list(ddgs.text(f"{q} {self.target_date}", max_results=4))
                        for h in hits:
                            results.append({
                                "title": h.get("title", "").strip(),
                                "source": urllib.parse.urlparse(h.get("href", "")).netloc.replace("www.", ""),
                                "url": h.get("href", ""),
                                "summary": h.get("body", ""),
                                "region": region,
                                "published": self.target_date
                            })
                    except Exception as e:
                        logger.debug(f"Search failed for '{q}': {e}")
        except Exception as e:
            logger.debug(f"duckduckgo_search unavailable: {e}")

        return results

    def extract_article_body(self, url):
        """Extract clean body text using trafilatura."""
        try:
            import trafilatura
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
                if text:
                    return text.strip()
        except Exception:
            pass

        # Lightweight fallback
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                html = r.read().decode("utf-8", errors="ignore")
            # Strip tags
            clean = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
            clean = re.sub(r"<[^>]+>", " ", clean)
            clean = re.sub(r"\s+", " ", clean).strip()
            return clean[:3000]
        except Exception:
            return ""

    def harvest(self):
        """Harvest, deduplicate, and enrich intelligence items."""
        feed_items = self.fetch_feed_items()
        search_items = self.search_recent_stories()
        all_raw = feed_items + search_items

        seen_urls = set()
        seen_titles = set()
        deduped = []

        for item in all_raw:
            url = item.get("url", "").split("?")[0].rstrip("/")
            title = re.sub(r"[^a-zA-Z0-9\s]", "", item.get("title", "").lower()).strip()
            norm_title = " ".join(title.split()[:8])

            if not url or url in seen_urls:
                continue
            if not norm_title or norm_title in seen_titles:
                continue

            # Must contain AI relevance
            full_context = f"{item['title']} {item['summary']}".lower()
            ai_keywords = ["ai", "artificial intelligence", "model", "chip", "semiconductor", "gpu", "neural",
                           "autonomous", "drone", "compute", "datacenter", "robot", "cyber", "openai", "deepseek",
                           "anthropic", "google", "meta", "nvidia", "yandex", "llm"]
            if not any(k in full_context for k in ai_keywords):
                continue

            seen_urls.add(url)
            seen_titles.add(norm_title)
            deduped.append(item)

        logger.info(f"Harvested {len(deduped)} relevant AI intelligence items.")
        return deduped


if __name__ == "__main__":
    harvester = NewsHarvester()
    articles = harvester.harvest()
    print(f"Total articles harvested: {len(articles)}")
    for i, a in enumerate(articles[:5], 1):
        print(f"{i}. [{a['region']}] {a['title']} ({a['source']})")
