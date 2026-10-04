"""
14-Day Story Memory Ledger & Multi-Day Continuity Engine.
Maintains persistent newsroom memory in src/aibrief/data/story_memory_ledger.json:
  • 14-day rolling story ledger
  • Multi-day story chains (story_chain_id) for longitudinal coverage
  • Entity mention frequency tracking over a 7-day rolling window for Story Fatigue Penalty
  • Strict cross-bureau deduplication
"""

from datetime import datetime, timedelta
import json
import os
import re
from typing import Dict, List, Optional, Tuple

LEDGER_PATH = os.path.join(os.path.dirname(__file__), "data", "story_memory_ledger.json")


ACTION_CLUSTERS = [
    {"quit", "quits", "quitting", "resign", "resigns", "resigned", "resignation", "leaves", "leaving", "departs", "departed", "departure", "whistleblower"},
    {"pause", "pauses", "paused", "halt", "halts", "halted", "pull", "pulls", "pulled", "scrap", "scraps", "scrapped", "cancel", "cancels", "cancelled"},
    {"acquire", "acquires", "acquired", "acquisition", "buy", "buys", "bought", "purchase", "purchases", "takeover"},
    {"probe", "probes", "probed", "investigate", "investigates", "investigation", "inquiry", "scrutiny", "subpoena"},
    {"rename", "renames", "renamed", "renaming", "rebrand", "rebrands", "rebranded", "super intelligence", "superintelligence"}
]

KNOWN_ENTITIES = [
    "openai", "anthropic", "google", "deepmind", "nvidia", "amd", "spacex", "tesla",
    "microsoft", "amazon", "apple", "meta", "indiaai", "alibaba", "deepseek", "tencent", "meity"
]


class StoryMemoryLedger:
    def __init__(self, ledger_file: str = LEDGER_PATH):
        self.ledger_file = ledger_file
        self.data = self._load()

    def _load(self) -> Dict:
        if os.path.exists(self.ledger_file):
            try:
                with open(self.ledger_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[!] Warning loading story memory ledger: {e}")
        return {
            "version": "2.1.1",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "stories": [],
            "entity_index": {}  # entity -> list of "YYYY-MM-DD"
        }

    def save(self):
        os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)
        self.data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        with open(self.ledger_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def prune_older_than(self, days: int = 14, current_date_str: Optional[str] = None):
        """Removes stories older than 14 days to keep memory fresh and rolling."""
        if not current_date_str:
            current_date_str = datetime.now().strftime("%Y-%m-%d")
        curr_dt = datetime.strptime(current_date_str, "%Y-%m-%d")
        cutoff_dt = curr_dt - timedelta(days=days)

        active_stories = []
        for s in self.data.get("stories", []):
            try:
                s_dt = datetime.strptime(s.get("last_major_update", s.get("first_covered")), "%Y-%m-%d")
                if s_dt >= cutoff_dt:
                    active_stories.append(s)
            except Exception:
                active_stories.append(s)

        self.data["stories"] = active_stories
        self._rebuild_entity_index()

    def _rebuild_entity_index(self):
        """Rebuilds the index of entity -> covered dates from active stories."""
        entity_idx = {}
        for s in self.data.get("stories", []):
            date_covered = s.get("last_major_update", s.get("first_covered"))
            for comp in s.get("companies", []):
                norm_c = comp.strip().title()
                if norm_c not in entity_idx:
                    entity_idx[norm_c] = []
                if date_covered not in entity_idx[norm_c]:
                    entity_idx[norm_c].append(date_covered)
        self.data["entity_index"] = entity_idx

    def get_entity_mentions_in_last_7_days(self, entity: str, current_date_str: Optional[str] = None) -> int:
        """
        Calculates how many unique days in the past 7 days this entity was featured.
        Used to calculate the Story Fatigue Penalty.
        """
        if not current_date_str:
            current_date_str = datetime.now().strftime("%Y-%m-%d")
        curr_dt = datetime.strptime(current_date_str, "%Y-%m-%d")
        cutoff_dt = curr_dt - timedelta(days=7)

        norm_e = entity.strip().title()
        dates = self.data.get("entity_index", {}).get(norm_e, [])
        count = 0
        for d_str in dates:
            try:
                d_dt = datetime.strptime(d_str, "%Y-%m-%d")
                if cutoff_dt <= d_dt <= curr_dt:
                    count += 1
            except Exception:
                pass
        return count

    def check_deduplication(
        self,
        headline: str,
        companies: List[str],
        topics: List[str],
        current_date_str: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Checks whether this candidate story is a repeat or part of an existing story chain.
        Returns:
          (is_duplicate: bool, matched_chain_id: Optional[str], reason: Optional[str])
        """
        if not current_date_str:
            current_date_str = datetime.now().strftime("%Y-%m-%d")

        norm_head = set(re.findall(r'\b[a-zA-Z]{3,}\b', headline.lower()))
        norm_comps = set(c.lower().strip() for c in companies)
        # Auto-extract entities from headline if empty
        for ent in KNOWN_ENTITIES:
            if ent in headline.lower():
                norm_comps.add(ent)

        norm_topics = set(t.lower().strip() for t in topics)

        for s in self.data.get("stories", []):
            s_head = set(re.findall(r'\b[a-zA-Z]{3,}\b', s.get("headline", "").lower()))
            s_comps = set(c.lower().strip() for c in s.get("companies", []))
            for ent in KNOWN_ENTITIES:
                if ent in s.get("headline", "").lower():
                    s_comps.add(ent)

            # Common entity overlap
            shared_entities = norm_comps.intersection(s_comps)

            # Headline word intersection
            intersect = norm_head.intersection(s_head)
            # Remove filler words
            substantive_intersect = intersect - {"the", "and", "for", "with", "this", "that", "from", "after", "into", "over", "about", "company"}
            jaccard = len(intersect) / max(len(norm_head.union(s_head)), 1)

            # Case 1: Near-identical headline (>= 50% word overlap) -> REJECT as duplicate
            if jaccard >= 0.50:
                return (True, s.get("story_chain_id"), f"Headline near-identical to story from {s.get('first_covered')}")

            # Case 2: Same Entity + Action Cluster Match (e.g. OpenAI + Resignation/Quits)
            if shared_entities:
                for cluster in ACTION_CLUSTERS:
                    cand_in_cluster = bool(norm_head.intersection(cluster))
                    past_in_cluster = bool(s_head.intersection(cluster))
                    if cand_in_cluster and past_in_cluster:
                        return (True, s.get("story_chain_id"), f"Repeat story: {list(shared_entities)} action already covered on {s.get('first_covered')}")

            # Case 3: Same Entity + 2+ Substantive Shared Words within 14 days
            if shared_entities and len(substantive_intersect) >= 2:
                days_ago = (datetime.strptime(current_date_str, "%Y-%m-%d") -
                            datetime.strptime(s.get("last_major_update", s.get("first_covered")), "%Y-%m-%d")).days
                if days_ago <= 14:
                    return (True, s.get("story_chain_id"), f"Repeat story on {list(shared_entities)} ({list(substantive_intersect)}) already covered on {s.get('first_covered')}")

        return (False, None, None)

    def record_story(
        self,
        headline: str,
        companies: List[str],
        topics: List[str],
        country: str,
        source_urls: List[str],
        impact_score: int,
        story_chain_id: Optional[str] = None,
        update_phase: str = "initial_break",
        current_date_str: Optional[str] = None
    ) -> str:
        """
        Records a story into the persistent ledger and updates the entity index.
        """
        if not current_date_str:
            current_date_str = datetime.now().strftime("%Y-%m-%d")

        clean_slug = re.sub(r'[^a-zA-Z0-9]+', '_', headline.lower()).strip('_')[:35]
        story_id = f"story_{current_date_str.replace('-', '')}_{clean_slug}"

        if not story_chain_id:
            top_entity = (companies[0] if companies else "global").lower().replace(" ", "_")
            story_chain_id = f"chain_{top_entity}_{clean_slug[:20]}"

        entry = {
            "story_id": story_id,
            "story_chain_id": story_chain_id,
            "headline": headline,
            "companies": companies,
            "topics": topics,
            "country": country,
            "source_urls": source_urls,
            "first_covered": current_date_str,
            "last_major_update": current_date_str,
            "update_phase": update_phase,
            "impact_score": impact_score
        }

        self.data["stories"].append(entry)
        self._rebuild_entity_index()
        self.save()
        return story_id


if __name__ == "__main__":
    ledger = StoryMemoryLedger()
    ledger.prune_older_than(days=14, current_date_str="2026-09-28")

    # Test deduplication check
    is_dup, chain, reason = ledger.check_deduplication(
        headline="US and China Agree to Establish AI Crisis Communication Hotline",
        companies=["United States", "China"],
        topics=["AI Safety", "Hotline"],
        current_date_str="2026-09-28"
    )
    print(f"Deduplication test: duplicate={is_dup}, chain={chain}, reason={reason}")

    # Test entity mention count
    mentions = ledger.get_entity_mentions_in_last_7_days("OpenAI", current_date_str="2026-09-28")
    print(f"OpenAI mentions in last 7 days: {mentions}")
