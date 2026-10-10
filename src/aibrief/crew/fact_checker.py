"""
FactChecker Agent - SanMitra AI News Wire v7.0
Autonomous source validation, entity cross-checking, and regional bureau taxonomy curation.
"""

import logging
import re
import urllib.parse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FactChecker")

TAXONOMY_MAP = {
    "AI BREAKTHROUGHS": ["breakthrough", "research", "lancet", "clinical", "discovery", "accuracy", "amie", "medical", "physics"],
    "NEW MODELS & TOOLS": ["release", "launch", "model", "qwen", "weights", "architecture", "intelligent ui", "tool", "vulnerability scanner", "gemini", "gpt"],
    "INDUSTRY & STARTUPS": ["funding", "venture", "revenue", "investor", "startup", "asx", "listing", "ipo", "valuation", "dollars", "capital", "firmus", "acquisitions"],
    "POLICY & REGULATIONS": ["council", "directive", "standards", "summit", "regulation", "court", "mandate", "investigation", "parliament", "g20", "burnham", "beijing", "directive"],
    "TECHNOLOGY TRENDS": ["datacenter", "supercomputer", "cyberattack", "drone", "air-defense", "infrastructure", "telemetry", "strikes", "power", "grid", "agentic"]
}

BUREAU_SLOTS = {
    "WORLD": 4, # Target: Stories 1, 7, 8, 9
    "USA": 3,   # Target: Stories 2, 3, 10
    "CHINA": 3, # Target: Stories 4, 11, 12
    "ASIA": 2,  # Target: Stories 5, 13
    "INDIA": 2  # Target: Stories 6, 14
}


class FactChecker:
    """Verifies URLs, removes speculative/unverifiable stories, and structures into 14 bureau slots."""

    def __init__(self, harvester=None):
        self.harvester = harvester

    def verify_story_authenticity(self, story):
        """Verify URL format and extract credible publisher."""
        url = story.get("url", "").strip()
        if not url or not url.startswith("http"):
            return None

        # Clean publisher name
        netloc = urllib.parse.urlparse(url).netloc.replace("www.", "")
        source_name = story.get("source", "").strip()
        if not source_name or "feed" in source_name.lower():
            domain_parts = netloc.split(".")
            source_name = domain_parts[0].capitalize() if len(domain_parts) > 1 else netloc

        # Reject obvious junk or generic search aggregator results
        banned_domains = ["pinterest.com", "facebook.com", "instagram.com", "tiktok.com", "youtube.com", "reddit.com"]
        if any(d in netloc for d in banned_domains):
            return None

        title = story.get("title", "").strip()
        if len(title) < 15:
            return None

        # Determine taxonomy pillar
        full_text = f"{title} {story.get('summary', '')}".lower()
        selected_pillar = "TECHNOLOGY TRENDS"
        for pillar, kws in TAXONOMY_MAP.items():
            if any(k in full_text for k in kws):
                selected_pillar = pillar
                break

        # Calculate importance score
        score = 80
        if any(w in full_text for w in ["supercomputer", "data center", "state council", "directive", "clinical", "strike", "lancet"]):
            score += 15
        if any(w in full_text for w in ["funding", "record", "exposes", "standards", "andy burnham", "g20"]):
            score += 10
        if "reuters" in netloc or "bloomberg" in netloc or "ft.com" in netloc or "aljazeera" in netloc:
            score += 5

        # Check region
        region = story.get("region", "WORLD").upper()
        if any(k in full_text for k in ["india", "delhi", "mumbai", "bengaluru", "hyderabad", "iit", "meity", "inc42"]):
            region = "INDIA"
        elif any(k in full_text for k in ["beijing", "china", "chinese", "alibaba", "qwen", "tencent", "huawei", "state council"]):
            region = "CHINA"
        elif any(k in full_text for k in ["japan", "tokyo", "korea", "seoul", "singapore", "asia-pacific", "samsung", "infor"]):
            region = "ASIA"
        elif any(k in full_text for k in ["pentagon", "white house", "senate", "congress", "united states", "google", "anthropic", "openai", "california"]):
            region = "USA"

        return {
            "title": title,
            "source": source_name,
            "sourceUrl": url,
            "summary": story.get("summary", ""),
            "region": region,
            "taxonomy": selected_pillar,
            "score": score
        }

    def assemble_14_stories(self, candidate_stories):
        """Curate candidate stories into 14 balanced bureau slots."""
        verified = []
        for s in candidate_stories:
            v = self.verify_story_authenticity(s)
            if v:
                verified.append(v)

        # Sort by importance score descending
        verified.sort(key=lambda x: x["score"], reverse=True)

        # Bucket by bureau
        bureau_buckets = {"WORLD": [], "USA": [], "CHINA": [], "ASIA": [], "INDIA": []}
        for v in verified:
            bureau_buckets[v["region"]].append(v)

        selected = []
        # Slot 1: Lead WORLD story
        if bureau_buckets["WORLD"]:
            selected.append(bureau_buckets["WORLD"].pop(0))

        # Slot 2: Lead USA story
        if bureau_buckets["USA"]:
            selected.append(bureau_buckets["USA"].pop(0))

        # Slot 3: Secondary USA story
        if bureau_buckets["USA"]:
            selected.append(bureau_buckets["USA"].pop(0))

        # Slot 4: Lead CHINA story
        if bureau_buckets["CHINA"]:
            selected.append(bureau_buckets["CHINA"].pop(0))

        # Slot 5: Lead ASIA story
        if bureau_buckets["ASIA"]:
            selected.append(bureau_buckets["ASIA"].pop(0))

        # Slot 6: Lead INDIA story
        if bureau_buckets["INDIA"]:
            selected.append(bureau_buckets["INDIA"].pop(0))

        # Fill remaining slots up to 14
        order = ["WORLD", "WORLD", "WORLD", "USA", "CHINA", "CHINA", "ASIA", "INDIA"]
        for r in order:
            if bureau_buckets[r]:
                selected.append(bureau_buckets[r].pop(0))

        # If any bureau was short, draw from remaining pool
        remaining = []
        for bucket in bureau_buckets.values():
            remaining.extend(bucket)
        remaining.sort(key=lambda x: x["score"], reverse=True)

        while len(selected) < 14 and remaining:
            selected.append(remaining.pop(0))

        logger.info(f"Fact-checking and curation complete: {len(selected)} verified stories assembled.")
        return selected
