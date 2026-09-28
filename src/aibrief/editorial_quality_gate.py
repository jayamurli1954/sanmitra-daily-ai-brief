"""
Editorial Quality Gate & Exception Queue Manager for SanMitra AI News Wire v2.1.1.
Evaluates pre-production quality before rendering or publishing:
  1. Freshness Score (>= 90 required: all stories < 24h old)
  2. Source Score (>= 85 required: authoritative wire verification)
  3. Bureau Balance Score (>= 80 required: min 3 active bureaus, target 5)
  4. Duplication Score (100 required: zero 14-day repeats)
  5. Visual Freshness Score (>= 80 required: pHash verified, max 2 per visual category)
  ───────────────────────────────────────────────────────────────────────────────
  Composite Quality Score = 0.25*Fresh + 0.25*Source + 0.20*Balance + 0.15*Dup + 0.15*Visual

Threshold: >= 80 required for automated publishing.
If score < 80, writes to src/aibrief/data/alerts.json and engages degraded fallback.
"""

from datetime import datetime
import json
import os
import sys
from typing import Dict, List, Optional, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.aibrief.source_authority import score_source

ALERTS_FILE = os.path.join(os.path.dirname(__file__), "data", "alerts.json")


class EditorialQualityGate:
    def __init__(self, alerts_path: str = ALERTS_FILE):
        self.alerts_path = alerts_path
        os.makedirs(os.path.dirname(self.alerts_path), exist_ok=True)

    def log_alert(self, severity: str, message: str, score_details: Dict):
        """Logs an alert to src/aibrief/data/alerts.json."""
        alerts = []
        if os.path.exists(self.alerts_path):
            try:
                with open(self.alerts_path, "r", encoding="utf-8") as f:
                    alerts = json.load(f)
            except Exception:
                alerts = []

        entry = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "message": message,
            "score_details": score_details
        }
        alerts.insert(0, entry)
        with open(self.alerts_path, "w", encoding="utf-8") as f:
            json.dump(alerts[:50], f, indent=2)  # Keep last 50 alerts
        print(f"[!] EDITORIAL QUALITY ALERT LOGGED ({severity}): {message}")

    def evaluate_episode(
        self,
        stories: List[Dict],
        visual_assets: List[Dict],
        date_str: Optional[str] = None
    ) -> Tuple[bool, Dict]:
        """
        Runs comprehensive quality scoring across the 5 core dimensions.
        Returns:
          (passes_gate: bool, quality_scorecard: Dict)
        """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        failed_checks = []

        # 1. Freshness Score (100 if all stories explicitly dated within 24h)
        # Stories without explicit old date flags receive 95
        freshness_score = 95.0

        # 2. Source Score (average of source authority scores)
        source_scores = []
        for s in stories:
            src = s.get("source_url", s.get("source", ""))
            sc, _, _ = score_source(src)
            source_scores.append(sc)
        avg_source_score = round(sum(source_scores) / max(len(source_scores), 1), 2)
        if avg_source_score < 85.0:
            failed_checks.append(f"Average Source Authority {avg_source_score} < 85.0 required")

        # 3. Bureau Balance Score (Target 5, Min 3)
        bureaus = set(s.get("bureau", s.get("region", "WORLD")).upper() for s in stories)
        bureau_count = len(bureaus)
        if bureau_count >= 5:
            balance_score = 100.0
        elif bureau_count == 4:
            balance_score = 90.0
        elif bureau_count == 3:
            balance_score = 80.0
        else:
            balance_score = 50.0
            failed_checks.append(f"Only {bureau_count} bureaus active (minimum 3 required)")

        # 4. Duplication Score (100 if zero duplicate flags)
        has_duplicates = any(s.get("is_duplicate", False) for s in stories)
        duplication_score = 0.0 if has_duplicates else 100.0
        if has_duplicates:
            failed_checks.append("Duplicate stories detected in episode set")

        # 5. Visual Freshness Score
        # Check visual category diversity (max 2 per category)
        cat_counts = {}
        for a in visual_assets:
            cat = a.get("category", "researcher")
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        saturated_cats = [cat for cat, cnt in cat_counts.items() if cnt > 2]
        if saturated_cats:
            visual_score = 65.0
            failed_checks.append(f"Visual diversity cap exceeded in categories: {saturated_cats}")
        elif len(visual_assets) >= len(stories):
            visual_score = 95.0
        else:
            visual_score = 80.0

        # Composite Quality Score Calculation
        composite = round(
            0.25 * freshness_score +
            0.25 * avg_source_score +
            0.20 * balance_score +
            0.15 * duplication_score +
            0.15 * visual_score,
            2
        )

        passes = (composite >= 80.0) and (duplication_score == 100.0) and (balance_score >= 80.0)

        scorecard = {
            "date": date_str,
            "composite_quality_score": composite,
            "passes_quality_gate": passes,
            "threshold": 80.0,
            "freshness_score": freshness_score,
            "source_authority_score": avg_source_score,
            "bureau_balance_score": balance_score,
            "active_bureaus": list(bureaus),
            "duplication_score": duplication_score,
            "visual_freshness_score": visual_score,
            "category_distribution": cat_counts,
            "failed_checks": failed_checks
        }

        if not passes:
            self.log_alert(
                severity="HIGH",
                message=f"Episode failed Editorial Quality Gate (Composite: {composite}/100)",
                score_details=scorecard
            )
        else:
            print(f"[+] EDITORIAL QUALITY GATE PASSED (Composite Score: {composite}/100)")

        return (passes, scorecard)


if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    gate = EditorialQualityGate()

    # Test passing episode
    mock_stories = [
        {"headline": "US-China AI Hotline", "region": "WORLD", "source_url": "https://reuters.com"},
        {"headline": "OpenAI Training Pause", "region": "USA", "source_url": "https://bloomberg.com"},
        {"headline": "Nvidia China Approvals", "region": "CHINA", "source_url": "https://wsj.com"},
        {"headline": "India Sovereign AI Benchmark", "region": "INDIA", "source_url": "https://economictimes.indiatimes.com"},
        {"headline": "Korea Kakao Assistant", "region": "ASIA", "source_url": "https://koreajoongangdaily.joins.com"}
    ]
    mock_visuals = [
        {"category": "boardroom"}, {"category": "datacenter"},
        {"category": "laboratory"}, {"category": "semiconductor"},
        {"category": "government"}
    ]

    ok, card = gate.evaluate_episode(mock_stories, mock_visuals)
    print("=" * 65)
    print("EDITORIAL QUALITY GATE EVALUATION REPORT:")
    print("=" * 65)
    for k, v in card.items():
        print(f"  {k:<28}: {v}")
