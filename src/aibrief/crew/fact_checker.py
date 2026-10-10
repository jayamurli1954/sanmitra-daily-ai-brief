"""
FactChecker Agent - SanMitra AI News Wire
Decides which harvested stories may air, and on what evidence.

A story passes only if:
  * it comes from a recognised outlet (source_authority), not an unknown blog;
  * it is not an opinion piece and its headline is not a rumour;
  * it is not the same event as a stronger candidate or a story aired in the last 7 days;
  * its article text can be fetched, it was published in the broadcast window,
    and every figure and name in its headline appears in that article.

The narration summary is taken from the article body itself, so every claim in
the script is traceable to the page the story is attributed to.
"""

from datetime import datetime, timedelta
import logging
import re
import urllib.parse

from src.aibrief.source_authority import is_company_source, is_recognised_source, score_source

from .text_utils import contains_any, count_matches, extractive_summary, is_recent, same_event, ungrounded_claims

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FactChecker")

BANNED_DOMAINS = ["pinterest.com", "facebook.com", "instagram.com", "tiktok.com", "youtube.com", "reddit.com"]

# Anonymous sourcing ("sources say") is normal reporting and is allowed.
RUMOUR_MARKERS = [
    "rumour", "rumor", "rumoured", "rumored", "unconfirmed", "insiders say",
    "speculation", "could be", "might be",
]

FEATURE_MARKERS = ["here are", "here's", "how to", "cartoon", "podcast", "newsletter", "week in review", "quiz"]

OPINION_PATH_MARKERS = ("/opinion", "/commentisfree", "/comment/", "/editorial", "/op-ed", "/column", "/letters/")

REGION_KEYWORDS = {
    "INDIA": ["india", "indian", "delhi", "new delhi", "mumbai", "bengaluru", "bangalore", "hyderabad",
              "chennai", "meity", "indiaai"],
    "CHINA": ["china", "chinese", "beijing", "shanghai", "shenzhen", "alibaba", "tencent", "huawei",
              "baidu", "bytedance", "deepseek", "qwen", "state council"],
    "ASIA": ["japan", "japanese", "tokyo", "korea", "korean", "seoul", "singapore", "taiwan", "tsmc",
             "samsung", "sk hynix", "asia-pacific", "philippines", "indonesia", "vietnam", "malaysia",
             "australia", "australian", "asx"],
    "USA": ["pentagon", "white house", "senate", "congress", "washington", "california", "silicon valley",
            "u.s.", "united states", "american", "ftc", "fcc"],
}

TAXONOMY_MAP = {
    "AI BREAKTHROUGHS": ["breakthrough", "research", "lancet", "clinical", "discovery", "medical", "physics"],
    "NEW MODELS & TOOLS": ["release", "launch", "model", "weights", "open-source", "tool", "gemini", "gpt", "claude", "qwen"],
    "INDUSTRY & STARTUPS": ["funding", "venture", "revenue", "investor", "startup", "ipo", "valuation", "acquisition"],
    "POLICY & REGULATIONS": ["regulation", "regulator", "law", "court", "lawsuit", "mandate", "investigation", "parliament", "directive"],
    "TECHNOLOGY TRENDS": ["datacenter", "data center", "supercomputer", "cyberattack", "drone", "infrastructure", "power", "grid", "agentic"],
}

HIGH_IMPACT_TERMS = ["supercomputer", "data center", "state council", "directive", "clinical", "regulation",
                     "lawsuit", "investigation", "export controls", "ipo", "acquisition"]

BUREAU_ORDER = ["WORLD", "USA", "USA", "CHINA", "ASIA", "INDIA", "WORLD", "WORLD", "WORLD", "USA",
                "CHINA", "CHINA", "ASIA", "INDIA"]

MIN_ARTICLE_CHARS = 500
REPEAT_WINDOW_DAYS = 7


def resolve_region(title, default_region, summary=""):
    """Route by headline, whole words only. A passing mention in the body
    ("...with India to follow") does not move a story to another bureau.

    A regional feed's default (Inc42 -> INDIA) holds only when the blurb is
    about that region; a regional outlet rewriting a US story goes to WORLD."""
    hits = [region for region, kws in REGION_KEYWORDS.items() if contains_any(title, kws)]
    # "US" only as the capitalised abbreviation, never the pronoun "us".
    if "USA" not in hits and re.search(r"\bUS\b", title or ""):
        hits.append("USA")
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        # Several regions in one headline is an international story.
        return "WORLD"
    default = (default_region or "WORLD").upper()
    if default in ("INDIA", "CHINA", "ASIA") and not contains_any(summary, REGION_KEYWORDS[default]):
        return "WORLD"
    return default


def classify_taxonomy(text):
    best, best_hits = "TECHNOLOGY TRENDS", 0
    for pillar, kws in TAXONOMY_MAP.items():
        hits = count_matches(text, kws)
        if hits > best_hits:
            best, best_hits = pillar, hits
    return best


class FactChecker:
    """Screens, verifies and slots harvested stories into the 14 bureau slots."""

    def __init__(self, target_date=None, fetch_article=None, ledger=None):
        self.target_date = target_date or datetime.now().strftime("%Y-%m-%d")
        self.fetch_article = fetch_article
        self.ledger = ledger
        self.rejections = []

    def _reject(self, story, reason):
        self.rejections.append({"title": story.get("title", ""), "url": story.get("url", ""), "reason": reason})
        return None

    # -- Stage 1: screening (no network) -----------------------------------

    def screen(self, story):
        url = (story.get("url") or story.get("sourceUrl") or "").strip()
        title = (story.get("title") or "").strip()
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower().replace("www.", "")

        if parsed.scheme not in ("http", "https") or not netloc:
            return self._reject(story, "no article URL")
        if any(netloc == d or netloc.endswith("." + d) for d in BANNED_DOMAINS):
            return self._reject(story, f"social or video platform ({netloc})")
        if not is_recognised_source(url):
            return self._reject(story, f"unrecognised or low-tier outlet ({netloc})")
        if any(marker in parsed.path.lower() for marker in OPINION_PATH_MARKERS):
            return self._reject(story, "opinion or comment piece")
        if len(title) < 15:
            return self._reject(story, "headline too short")
        if contains_any(title, RUMOUR_MARKERS) or title.endswith("?"):
            return self._reject(story, "speculative or rumour headline")
        if contains_any(title, FEATURE_MARKERS):
            return self._reject(story, "feature, listicle or explainer rather than news")

        authority, _tier, outlet = score_source(url)
        text = f"{title} {story.get('summary', '')}"
        score = authority + (5 if contains_any(text, HIGH_IMPACT_TERMS) else 0)
        company = is_company_source(url)
        if company:
            score -= 5  # prefer independent reporting of the same news

        return {
            "title": title,
            "source": outlet,
            "sourceUrl": url,
            "sourceType": "company" if company else "reporting",
            "feedSummary": story.get("summary", ""),
            "region": resolve_region(title, story.get("region"), story.get("summary", "")),
            "taxonomy": classify_taxonomy(text),
            "score": score,
            "published": story.get("published", ""),
            "also": [],
        }

    # -- Stage 2: same-event merging and repeat check ------------------------

    def merge_same_events(self, screened):
        kept = []
        for story in sorted(screened, key=lambda s: s["score"], reverse=True):
            twin = next((k for k in kept if same_event(k["title"], story["title"])), None)
            if twin is None:
                kept.append(story)
                continue
            twin["also"].append({"source": story["source"], "url": story["sourceUrl"]})
            self._reject({"title": story["title"], "url": story["sourceUrl"]},
                         f"same event as '{twin['title'][:60]}' (kept as a second source)")
        return kept

    def recent_headlines(self):
        if not self.ledger:
            return []
        today = datetime.strptime(self.target_date, "%Y-%m-%d")
        cutoff = (today - timedelta(days=REPEAT_WINDOW_DAYS)).strftime("%Y-%m-%d")
        return [
            (s.get("headline", ""), s.get("first_covered", ""))
            for s in self.ledger.data.get("stories", [])
            # Today's own entries are excluded so a re-run does not reject itself.
            if cutoff <= s.get("first_covered", "") < self.target_date
        ]

    def is_repeat(self, title, recent):
        for headline, date in recent:
            if same_event(title, headline):
                return f"already covered on {date}: '{headline[:60]}'"
        return None

    # -- Stage 3: evidence --------------------------------------------------

    def verify_against_article(self, story):
        if self.fetch_article is None:
            return self._reject({"title": story["title"], "url": story["sourceUrl"]}, "no article fetcher configured")
        article = self.fetch_article(story["sourceUrl"]) or {}
        body = article.get("text", "") or ""
        if len(body) < MIN_ARTICLE_CHARS:
            return self._reject({"title": story["title"], "url": story["sourceUrl"]},
                                "article text could not be extracted, nothing to verify against")

        published = story["published"] or article.get("published", "")
        if not is_recent(published, self.target_date):
            return self._reject({"title": story["title"], "url": story["sourceUrl"]},
                                f"not published in the broadcast window (published: {published or 'unknown'})")

        missing = ungrounded_claims(story["title"], body)
        if missing:
            return self._reject({"title": story["title"], "url": story["sourceUrl"]},
                                f"headline claims not found in the article: {', '.join(missing[:5])}")

        summary = extractive_summary(body)
        if not summary:
            return self._reject({"title": story["title"], "url": story["sourceUrl"]}, "no usable sentences in the article")

        verified = dict(story)
        verified.update({"summary": summary, "published": published, "articleText": body})
        return verified

    # -- Assembly -----------------------------------------------------------

    def assemble_14_stories(self, candidate_stories, max_stories=14, max_fetches=40):
        screened = [s for s in (self.screen(c) for c in candidate_stories) if s]
        merged = self.merge_same_events(screened)

        recent = self.recent_headlines()
        fresh = []
        for story in merged:
            reason = self.is_repeat(story["title"], recent)
            if reason:
                self._reject({"title": story["title"], "url": story["sourceUrl"]}, reason)
            else:
                fresh.append(story)

        buckets = {r: [] for r in ("WORLD", "USA", "CHINA", "ASIA", "INDIA")}
        for story in fresh:
            buckets.setdefault(story["region"], []).append(story)

        selected, fetches = [], 0

        def take_from(region):
            nonlocal fetches
            while buckets.get(region) and fetches < max_fetches:
                fetches += 1
                verified = self.verify_against_article(buckets[region].pop(0))
                if verified:
                    return verified
            return None

        for region in BUREAU_ORDER:
            if len(selected) >= max_stories:
                break
            story = take_from(region)
            if story:
                selected.append(story)

        # Fill any short bureau from the strongest remaining candidates.
        leftovers = sorted((s for b in buckets.values() for s in b), key=lambda s: s["score"], reverse=True)
        for story in leftovers:
            if len(selected) >= max_stories or fetches >= max_fetches:
                break
            fetches += 1
            verified = self.verify_against_article(story)
            if verified:
                selected.append(verified)

        logger.info(
            f"Fact-check complete: {len(selected)} stories verified from {len(candidate_stories)} candidates "
            f"({len(self.rejections)} rejected, {fetches} articles fetched)."
        )
        for r in self.rejections:
            logger.info(f"  [REJECTED] {r['title'][:70]} -> {r['reason']}")
        return selected
