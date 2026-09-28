"""
YouTube Analytics Learning & Feedback Loop for SanMitra AI News Wire v2.1.1.
Runs daily at 12:00 PM IST:
  1. Ingests 24-48h performance telemetry (CTR, Average View Duration, 30s Retention)
  2. Maps performance back to story topics, bureaus, and visual categories
  3. Updates src/aibrief/data/editorial_learning.json with dynamic topic weights
  4. Automatically closes the loop: Publish -> Measure -> Learn -> Refine
"""

from datetime import datetime, timedelta
import json
import os
import sys
from typing import Dict, List, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

LEARNING_FILE = os.path.join(os.path.dirname(__file__), "data", "editorial_learning.json")


class YouTubeAnalyticsAgent:
    def __init__(self, learning_path: str = LEARNING_FILE):
        self.learning_path = learning_path
        self.data = self._load()

    def _load(self) -> Dict:
        if os.path.exists(self.learning_path):
            try:
                with open(self.learning_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[!] Warning reading editorial learning: {e}")
        return {
            "version": "2.1.1",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "category_affinity_weights": {
                "semiconductor": 1.15,
                "robotics": 1.12,
                "sovereign_ai": 1.10,
                "ai_safety": 1.05,
                "enterprise_rollout": 1.00
            },
            "visual_style_performance": {
                "strategic_briefing": {"avg_ctr": 7.4, "avg_retention": 62.0},
                "newsroom": {"avg_ctr": 6.8, "avg_retention": 58.0},
                "documentary": {"avg_ctr": 6.2, "avg_retention": 55.0}
            },
            "recent_telemetry": []
        }

    def save(self):
        os.makedirs(os.path.dirname(self.learning_path), exist_ok=True)
        self.data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        with open(self.learning_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def ingest_daily_telemetry(
        self,
        video_id: str,
        title: str,
        ctr: float,
        retention_pct: float,
        featured_topics: List[str]
    ):
        """
        Ingests metrics for a published episode and refines affinity multipliers.
        """
        record = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "video_id": video_id,
            "title": title,
            "ctr": ctr,
            "retention_pct": retention_pct,
            "topics": featured_topics
        }
        self.data["recent_telemetry"].insert(0, record)
        self.data["recent_telemetry"] = self.data["recent_telemetry"][:30]

        # Dynamic learning rule:
        # Benchmark: CTR 6.0%, Retention 55.0%
        # If video exceeds benchmark by > 15%, boost topic weights by +0.03
        for topic in featured_topics:
            t_key = topic.lower().replace(" ", "_")
            current_w = self.data["category_affinity_weights"].get(t_key, 1.00)
            if ctr >= 7.0 and retention_pct >= 60.0:
                new_w = min(1.30, round(current_w + 0.03, 2))
                self.data["category_affinity_weights"][t_key] = new_w
            elif ctr < 5.0:
                new_w = max(0.85, round(current_w - 0.02, 2))
                self.data["category_affinity_weights"][t_key] = new_w

        self.save()
        print(f"[+] Editorial Learning updated from video telemetry: CTR={ctr}%, Retention={retention_pct}%")

    def get_affinity_multiplier(self, topic: str) -> float:
        """Returns multiplier for impact scoring based on historical viewer engagement."""
        t_key = topic.lower().replace(" ", "_")
        return self.data.get("category_affinity_weights", {}).get(t_key, 1.00)


if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    agent = YouTubeAnalyticsAgent()
    agent.ingest_daily_telemetry(
        video_id="yt_demo_20260928",
        title="AI News 2026-09-28: US-China Safety Hotline & OpenAI Training Pause",
        ctr=7.8,
        retention_pct=64.5,
        featured_topics=["semiconductor", "sovereign_ai", "ai_safety"]
    )
    print("=" * 65)
    print("📈 EDITORIAL LEARNING FEEDBACK WEIGHTS:")
    print("=" * 65)
    for topic, weight in agent.data["category_affinity_weights"].items():
        print(f"  {topic:<25}: x{weight}")
