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

from .text_utils import (IST, clean_feed_text, contains_any, is_election_story, is_personal_scandal_story, is_recent,
                         is_stock_market_story, parse_published, source_link_problem)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("NewsHarvester")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)


def third_person(text):
    """Papers say "We propose..."; read aloud, that sounds like the newsroom's work."""
    for pattern, repl in ((r"\bWe\b", "The researchers"), (r"\bwe\b", "the researchers"),
                          (r"\bOur\b", "Their"), (r"\bour\b", "their")):
        text = re.sub(pattern, repl, text)
    return text


_SECTION_HEADING = re.compile(r"^(?:\d+(?:\.\d+)*\.?\s+|Appendix\s)\S.{0,70}$")
_CONCLUSION_HEADING = re.compile(r"^\d+\.?\s+(?:Conclusions?|Discussion|Summary)\b", re.IGNORECASE)
_SPEAKABLE_JUNK = re.compile(r"\\|[{}_^]|\b(?:Fig|Figure|Table|Eq|Sec|Section|Appendix)\b\.?\s*\d|�|https?://")


def paper_sections(text):
    """Abstract, introduction and conclusion of a paper's full text, in that order,
    with formulas, citations and figure references taken out; the methods and
    results tables in between are not readable aloud."""
    lines = [l.strip() for l in text.splitlines()]
    wanted, keep = [], False
    for line in lines:
        if line.lower() in ("abstract", "abstract.") or re.match(r"^\d+\.?\s+Introduction\b", line, re.IGNORECASE) \
                or _CONCLUSION_HEADING.match(line):
            keep = True
            continue
        if _SECTION_HEADING.match(line) or line.lower().startswith(("references", "acknowledg")):
            keep = False
            continue
        if keep and len(line) > 60 and not line.startswith("|"):
            wanted.append(line)
    joined = " ".join(wanted)
    # Citations: "(Wan et al., 2025)", "(Black and others, 2024; Physical Intelligence, 2025)".
    joined = re.sub(r"\s*\([^()]{0,160}?,\s*(?:19|20)\d{2}[a-z]?\)", "", joined)
    joined = re.sub(r"\s*\[\d+(?:[,\u2013-]\s*\d+)*\]", "", joined)
    # A sentence with maths, a figure reference or a link in it is dropped whole.
    sentences = re.split(r"(?<=[.!?])\s+", joined)
    return third_person(" ".join(s for s in sentences if not _SPEAKABLE_JUNK.search(s)))

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



def is_ai_story(title, summary=""):
    return contains_any(f"{title} {summary}", AI_KEYWORDS)


def _entry_published(entry):
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        return datetime(*parsed[:6]).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    return entry.get("published", "") or entry.get("updated", "")


class NewsHarvester:
    """Harvests candidate AI stories from the window before the broadcast."""

    def __init__(self, target_date=None):
        self.target_date = target_date or datetime.now(IST).strftime("%Y-%m-%d")

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
                    if title and link and not source_link_problem(link):
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
                            if source_link_problem(url):
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
            text = third_person(text)
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
            if is_stock_market_story(item.get("title", ""), item.get("url", "")):
                rejected["stock_market"] += 1
                continue
            if is_personal_scandal_story(item.get("title", "")):
                rejected["scandal"] += 1
                continue
            if is_election_story(item.get("title", ""), item.get("summary", "")):
                rejected["election"] += 1
                continue
            published = item.get("published", "")
            if parse_published(published) is not None and not is_recent(published, self.target_date):
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

    def _papers_featured_on(self, date):
        """Papers on Daily Papers for one day that can run: MIN_PAPER_UPVOTES or more
        and no question title (those fail the fact-checker's speculative-headline rule)."""
        try:
            entries = self._get_json(f"{self.DAILY_PAPERS_API}?date={date}") or []
        except Exception as e:
            logger.debug(f"Daily Papers fetch failed for {date}: {e}")
            return []
        papers = []
        for entry in entries:
            paper = entry.get("paper") or {}
            if (paper.get("id") and paper.get("title") and "?" not in paper["title"]
                    and paper.get("upvotes", 0) >= self.MIN_PAPER_UPVOTES):
                # submittedOnDailyAt is the day it was featured on Daily Papers;
                # publishedAt is its arXiv date, often weeks earlier.
                papers.append(dict(paper, submitted=paper.get("submittedOnDailyAt") or entry.get("publishedAt", "")))
        return papers

    def fetch_daily_paper(self):
        """The most upvoted paper on Hugging Face Daily Papers for the day the
        episode covers, as a candidate citing its arXiv page; [] if none
        reaches MIN_PAPER_UPVOTES."""
        covered = self.target_date  # the evening episode covers its own day
        best = max(self._papers_featured_on(covered), key=lambda p: p["upvotes"], default=None)
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

    def fetch_week_paper(self, exclude_ids=()):
        """Sunday's Research of the Week: the most upvoted paper featured Monday-Saturday
        that is not in exclude_ids (already aired), else the most upvoted one, as a
        story whose text is drawn from its abstract, introduction and conclusion.
        None if no paper reached MIN_PAPER_UPVOTES or its text cannot be read."""
        from .fact_checker import FEATURE_DESK, FEATURE_MAX_SENTENCES
        from .text_utils import extractive_summary

        sunday = datetime.strptime(self.target_date, "%Y-%m-%d")
        week = [(sunday - timedelta(days=n)).strftime("%Y-%m-%d") for n in range(6, 0, -1)]
        papers = {p["id"]: p for date in week for p in self._papers_featured_on(date)}
        ranked = sorted(papers.values(), key=lambda p: p["upvotes"], reverse=True)
        ranked = [p for p in ranked if p["id"] not in exclude_ids] + [p for p in ranked if p["id"] in exclude_ids]
        for paper in ranked[:3]:
            text = self.fetch_paper_text(paper["id"])
            # About 360 words of the paper's own sentences; the rewriter tells it in ~280.
            summary = extractive_summary(text, max_sentences=FEATURE_MAX_SENTENCES + 6, max_words=360)
            if len(summary.split()) < 120:
                logger.info(f"Research of the Week: too little readable text in {paper['id']}, trying the next paper.")
                continue
            logger.info(f"Research of the Week: {paper['title'][:70]} ({paper['upvotes']} upvotes)")
            return {
                "title": clean_feed_text(paper["title"]),
                "source": "arXiv",
                "sourceUrl": f"https://arxiv.org/abs/{paper['id']}",
                "summary": summary,
                "region": "WORLD",
                "desk": FEATURE_DESK,
            }
        logger.info("Research of the Week: no paper this week.")
        return None

    def fetch_paper_text(self, arxiv_id):
        """The readable parts of a paper: its HTML full text on arXiv, or just the
        abstract when the paper has no HTML version."""
        try:
            import trafilatura
            req = urllib.request.Request(f"https://arxiv.org/html/{arxiv_id}", headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=20) as r:
                full = trafilatura.extract(r.read().decode("utf-8", errors="ignore")) or ""
            text = paper_sections(full)
            if len(text.split()) >= 150:
                return text
        except Exception as e:
            logger.debug(f"arXiv full text unavailable for {arxiv_id}: {e}")
        return self.fetch_article(f"https://arxiv.org/abs/{arxiv_id}").get("text", "")

    def harvest(self):
        # The day's paper is added on top of the news by the orchestrator, not in a news slot.
        return self.filter_candidates(self.fetch_feed_items() + self.search_recent_stories())


if __name__ == "__main__":
    harvester = NewsHarvester()
    articles = harvester.harvest()
    print(f"Total articles harvested: {len(articles)}")
    for i, a in enumerate(articles[:10], 1):
        print(f"{i}. [{a['region']}] {a['title']} ({a['source']}, {a['published']})")
