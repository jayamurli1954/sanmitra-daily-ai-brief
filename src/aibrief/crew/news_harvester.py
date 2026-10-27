"""
NewsHarvester Agent - SanMitra AI News Wire
Gathers candidate stories from RSS feeds and search, keeps only AI stories
published in the window before the broadcast, and fetches the full article
text that the fact-checker verifies against.
"""

from datetime import datetime, timedelta
import json
import logging
import re
import urllib.parse
import urllib.request

from .text_utils import (IST, clean_feed_text, contains_any, is_election_story, is_paywalled_url, is_personal_scandal_story, is_recent,
                         is_stock_market_story, parse_published)

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
    {"outlet": "Defense News", "url": "https://www.defensenews.com/arc/outboundfeeds/rss/category/technology/?outputType=xml", "region": "WORLD"},
    {"outlet": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "region": "USA"},
    {"outlet": "VentureBeat", "url": "https://venturebeat.com/category/ai/feed/", "region": "USA"},
    {"outlet": "The Guardian", "url": "https://www.theguardian.com/technology/artificialintelligenceai/rss", "region": "WORLD"},
    {"outlet": "The Economic Times", "url": "https://economictimes.indiatimes.com/tech/artificial-intelligence/rssfeeds/81580397.cms", "region": "INDIA"},
    {"outlet": "Inc42", "url": "https://inc42.com/feed/", "region": "INDIA"},
    {"outlet": "The Times of India", "url": "https://timesofindia.indiatimes.com/rssfeeds/66949542.cms", "region": "INDIA"},
    {"outlet": "The Korea Times", "url": "https://www.koreatimes.co.kr/www/rss/tech.xml", "region": "ASIA"},
    {"outlet": "The Japan Times", "url": "https://www.japantimes.co.jp/feed/category/business/tech/", "region": "ASIA"},
    {"outlet": "Google", "url": "https://blog.google/technology/ai/rss/", "region": "USA"},
    {"outlet": "OpenAI", "url": "https://openai.com/news/rss.xml", "region": "USA"},
    # Added 2026-10-11 to reach 12-15 verified stories a day (live-tested).
    {"outlet": "CNBC", "url": "https://www.cnbc.com/id/19854910/device/rss/rss.html", "region": "USA"},
    {"outlet": "BBC", "url": "https://feeds.bbci.co.uk/news/technology/rss.xml", "region": "WORLD"},
    {"outlet": "NPR", "url": "https://feeds.npr.org/1019/rss.xml", "region": "USA"},
    {"outlet": "The Guardian", "url": "https://www.theguardian.com/uk/technology/rss", "region": "WORLD"},
    {"outlet": "Rest of World", "url": "https://restofworld.org/feed/latest", "region": "WORLD"},
    {"outlet": "The Register", "url": "https://www.theregister.com/software/ai_ml/headlines.atom", "region": "WORLD"},
    {"outlet": "Tech in Asia", "url": "https://www.techinasia.com/feed", "region": "ASIA"},
    # Added 2026-10-27: free China coverage in place of the South China Morning Post,
    # which asks viewers to subscribe (live-tested). Subscription sites are not used.
    {"outlet": "TechNode", "url": "https://technode.com/feed/", "region": "CHINA"},
    {"outlet": "Pandaily", "url": "https://pandaily.com/feed/", "region": "CHINA"},
    {"outlet": "The Economic Times", "url": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms", "region": "INDIA"},
    {"outlet": "Google DeepMind", "url": "https://deepmind.google/blog/rss.xml", "region": "USA"},
    {"outlet": "Nvidia", "url": "https://nvidianews.nvidia.com/releases.xml", "region": "USA"},
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
                    if title and link and not is_paywalled_url(link):
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
                            if is_paywalled_url(url):
                                continue
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
        # An arXiv abstract page starts with subject, submission date, title and
        # "View PDF" links; only the abstract itself is the story.
        if "arxiv.org/abs/" in url and "Abstract:" in text:
            text = text.split("Abstract:", 1)[1]
            text = re.split(r"\s(?:Comments:|Subjects:|Cite as:|Submission history|Additional Features"
                            r"|References & Citations|Bibliographic and Citation Tools)", text, maxsplit=1)[0]
            # Abstracts say "We propose..."; read aloud, that sounds like the newsroom's work.
            for pattern, repl in ((r"\bWe\b", "The researchers"), (r"\bwe\b", "the researchers"),
                                  (r"\bOur\b", "Their"), (r"\bour\b", "their")):
                text = re.sub(pattern, repl, text)
        return {"text": text.strip(), "published": published}

    def filter_candidates(self, raw_items):
        """URL/title dedup, AI relevance and recency. Undated search hits are kept for now."""
        seen_urls, seen_titles, kept = set(), set(), []
        rejected = {"duplicate": 0, "not_ai": 0, "stock_market": 0, "scandal": 0, "election": 0, "stale": 0}

        for item in raw_items:
            url = item.get("url", "").split("?")[0].rstrip("/")
            norm_title = " ".join(re.sub(r"[^a-z0-9\s]", "", item.get("title", "").lower()).split()[:8])
            if not url or not norm_title or url in seen_urls or norm_title in seen_titles:
                rejected["duplicate"] += 1
                continue
            # Daily Papers entries are AI research by definition; their titles often
            # don't say "AI" ("Multics: Generative Multi-Player World Model").
            if item.get("origin") != "papers" and not is_ai_story(item.get("title", ""), item.get("summary", "")):
                rejected["not_ai"] += 1
                continue
            if is_stock_market_story(item.get("title", "")):
                rejected["stock_market"] += 1
                continue
            if is_personal_scandal_story(item.get("title", "")):
                rejected["scandal"] += 1
                continue
            if is_election_story(item.get("title", ""), item.get("summary", "")):
                rejected["election"] += 1
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

    # Hugging Face Daily Papers: one research story a day at most, and only a
    # paper the research community upvoted strongly (editor's decision, 2026-10-14).
    DAILY_PAPERS_API = "https://huggingface.co/api/daily_papers"
    MIN_PAPER_UPVOTES = 30

    def _get_json(self, url):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def fetch_daily_paper(self):
        """The most upvoted paper on Hugging Face Daily Papers for the day the
        episode covers, as a candidate citing its arXiv page; [] if none
        reaches MIN_PAPER_UPVOTES."""
        covered = (datetime.strptime(self.target_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        try:
            entries = self._get_json(f"{self.DAILY_PAPERS_API}?date={covered}") or []
        except Exception as e:
            logger.debug(f"Daily Papers fetch failed: {e}")
            return []
        best = None
        for entry in entries:
            paper = entry.get("paper") or {}
            # Question titles ("Can Coding Agents Build...?") fail the fact-checker's
            # speculative-headline rule, so take the best paper that can run.
            if (paper.get("id") and paper.get("title") and "?" not in paper["title"]
                    and paper.get("upvotes", 0) >= self.MIN_PAPER_UPVOTES):
                if best is None or paper["upvotes"] > best["upvotes"]:
                    # submittedOnDailyAt is the day it was featured on Daily Papers;
                    # publishedAt is its arXiv date, often weeks earlier.
                    best = dict(paper, submitted=paper.get("submittedOnDailyAt") or entry.get("publishedAt", ""))
        if not best:
            logger.info(f"Daily Papers: no paper with {self.MIN_PAPER_UPVOTES}+ upvotes for {covered}.")
            return []
        logger.info(f"Daily Papers: {best['title'][:70]} ({best['upvotes']} upvotes)")
        return [{
            "title": clean_feed_text(best["title"]),
            "source": "arXiv",
            "url": f"https://arxiv.org/abs/{best['id']}",
            "summary": clean_feed_text(best.get("ai_summary") or best.get("summary") or "")[:600],
            "region": "WORLD",
            "published": best["submitted"],
            "origin": "papers",
        }]

    def harvest(self):
        return self.filter_candidates(self.fetch_feed_items() + self.search_recent_stories() + self.fetch_daily_paper())


if __name__ == "__main__":
    harvester = NewsHarvester()
    articles = harvester.harvest()
    print(f"Total articles harvested: {len(articles)}")
    for i, a in enumerate(articles[:10], 1):
        print(f"{i}. [{a['region']}] {a['title']} ({a['source']}, {a['published']})")
