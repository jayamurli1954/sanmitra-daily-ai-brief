"""
100-Point Impact Scoring & Story Fatigue Engine for SanMitra AI News Wire v2.1.1.
Calculates transparent, fully audited editorial scores:
  1. Market & Economic Impact (0-30 pts)
  2. Technology & Capability Leap (0-25 pts)
  3. Policy, Legal & National Security (0-20 pts)
  4. Geopolitical & Multilateral Impact (0-15 pts)
  5. Research & Academic Significance (0-10 pts)
  ─────────────────────────────────────────────
  Raw Impact Score = Sum of above (0-100 pts)

Adjusted with:
  • Source Authority Modifier: (source_score - 80) * 0.25
  • Story Fatigue Penalty: -0, -5, -10, or -15 pts based on 7-day entity saturation
"""

import os
import re
import sys
from typing import Dict, List, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.aibrief.source_authority import score_source, calculate_source_modifier

# Keyword-based heuristic indicators for automated impact scoring
MARKET_KEYWORDS = {
    "billion": 8, "trillion": 10, "valuation": 6, "funding": 6, "ipo": 7,
    "acquisition": 7, "capex": 6, "revenue": 5, "supply chain": 6, "stocks": 5,
    "chip procurement": 7, "enterprise rollout": 6, "commercial": 4, "market": 5,
    "tender": 7, "contract": 6, "commerce": 5, "procurement": 6, "enterprise": 5,
    "investment": 6, "consortium": 6, "rollout": 5, "infrastructure": 6, "services": 4
}

TECH_KEYWORDS = {
    "frontier model": 9, "gpt-5": 9, "gpt-6": 9, "reasoning": 7, "agent": 7,
    "sandbox escape": 10, "supercomputer": 8, "quantum": 7, "cluster": 6,
    "architecture": 5, "autonomous": 6, "breakthrough": 6, "hardware": 5,
    "semiconductor": 7, "gpu": 7, "training pause": 9, "training": 5,
    "accelerator": 6, "chip": 6, "chips": 6, "robot": 6, "robotics": 6,
    "ai assistant": 6, "compute": 6, "virtualization": 5, "sovereign ai": 7,
    "deploy": 6, "deployment": 6, "infrastructure": 6
}

POLICY_KEYWORDS = {
    "executive order": 8, "congress": 7, "senate": 7, "hearing": 7, "antitrust": 7,
    "investigation": 7, "sanctions": 8, "export control": 8, "export": 6, "parliament": 6,
    "court": 6, "lawsuit": 6, "ban": 7, "mandate": 6, "compliance": 5, "inquiry": 7,
    "talks": 6, "agreement": 7, "protocol": 6, "policy": 5, "regulat": 6,
    "minister": 6, "meity": 7, "white house": 7, "government": 6, "benchmark": 6
}

GEOPOLITICAL_KEYWORDS = {
    "us-china": 8, "bilateral": 7, "united nations": 7, "treaty": 7, "sovereign": 6,
    "national security": 7, "pentagon": 6, "defense": 6, "crisis line": 8,
    "hotline": 7, "cross-border": 5, "washington": 6, "beijing": 6, "global": 5,
    "diplomatic": 6, "multilateral": 7, "sovereign ai": 7, "sovereign compute": 7,
    "china": 6, "chinese": 6, "india": 6, "korea": 5, "asia": 5, "nationwide": 5
}

RESEARCH_KEYWORDS = {
    "safety audit": 5, "alignment": 4, "benchmark": 4, "arxiv": 4, "paper": 3,
    "evaluations": 4, "red-teaming": 4, "degradation": 4, "vulnerability": 4,
    "ai safety": 5, "incident": 4, "testify": 4, "containment": 5, "audit": 4,
    "readiness": 4, "standards": 4
}


def calculate_fatigue_penalty(mentions_in_last_7_days: int) -> int:
    """
    Prevents a handful of companies (OpenAI, Google, Nvidia) from dominating every episode.
      0 - 2 days:  0 pts
      3 - 4 days: -5 pts
      5 - 6 days: -10 pts
      7 days:     -15 pts
    """
    if mentions_in_last_7_days <= 2:
        return 0
    elif mentions_in_last_7_days <= 4:
        return 5
    elif mentions_in_last_7_days <= 6:
        return 10
    else:
        return 15


def score_story_impact(
    headline: str,
    summary: str,
    source_url_or_name: str,
    mentions_in_last_7_days: int = 0,
    explicit_subscores: Optional[Dict[str, int]] = None,
    base_importance_score: Optional[int] = None
) -> Dict:
    """
    Calculates detailed sub-scores and the final rank score.
    Returns an auditable score dictionary.
    """
    text = f"{headline} {summary}".lower()

    if explicit_subscores:
        m_pts = explicit_subscores.get("market_impact", 0)
        t_pts = explicit_subscores.get("technology_impact", 0)
        p_pts = explicit_subscores.get("policy_impact", 0)
        g_pts = explicit_subscores.get("geopolitical_impact", 0)
        r_pts = explicit_subscores.get("research_significance", 0)
    else:
        # Automated heuristic extraction
        m_pts = min(30, sum(weight for kw, weight in MARKET_KEYWORDS.items() if kw in text))
        t_pts = min(25, sum(weight for kw, weight in TECH_KEYWORDS.items() if kw in text))
        p_pts = min(20, sum(weight for kw, weight in POLICY_KEYWORDS.items() if kw in text))
        g_pts = min(15, sum(weight for kw, weight in GEOPOLITICAL_KEYWORDS.items() if kw in text))
        r_pts = min(10, sum(weight for kw, weight in RESEARCH_KEYWORDS.items() if kw in text))

        # Baseline floor for genuine news items
        if m_pts == 0 and ("investment" in text or "market" in text):
            m_pts = 10
        if t_pts == 0 and ("ai" in text or "model" in text or "safety" in text or "datacentre" in text or "datacenter" in text):
            t_pts = 10
        if p_pts == 0 and ("government" in text or "official" in text or "regulat" in text or "framework" in text or "pact" in text or "quit" in text):
            p_pts = 8

    # Dominant Category Scaling:
    # A story should not be penalized just because it is purely technological or purely financial.
    # If a story has an exceptional score in its primary domain, scale it appropriately.
    raw_sum = m_pts + t_pts + p_pts + g_pts + r_pts
    sorted_subscores = sorted([m_pts, t_pts, p_pts, g_pts, r_pts], reverse=True)
    top1 = sorted_subscores[0]
    top2 = sorted_subscores[1]

    # Combined impact captures both multi-dimensional and domain-dominant breakthroughs
    scaled_dominant = max(top1 * 2.6, (top1 + top2) * 1.5)
    raw_impact = min(100, int(round(max(raw_sum, scaled_dominant))))

    # Incorporate intake wire breaking importance if available
    if base_importance_score and base_importance_score > 0:
        raw_impact = min(100, max(raw_impact, int(base_importance_score)))

    # Source evaluation
    src_score, src_tier, src_name = score_source(source_url_or_name)
    src_mod = calculate_source_modifier(src_score)

    # Fatigue penalty
    fatigue_pen = calculate_fatigue_penalty(mentions_in_last_7_days)

    final_rank_score = round(max(0.0, raw_impact + src_mod - fatigue_pen), 2)

    return {
        "market_impact": m_pts,
        "technology_impact": t_pts,
        "policy_impact": p_pts,
        "geopolitical_impact": g_pts,
        "research_significance": r_pts,
        "raw_impact_score": raw_impact,
        "source_authority_score": src_score,
        "source_authority_tier": src_tier,
        "source_name": src_name,
        "source_modifier": src_mod,
        "entity_mentions_last_7_days": mentions_in_last_7_days,
        "fatigue_penalty": fatigue_pen,
        "final_rank_score": final_rank_score,
        "qualifies_as_broadcast": final_rank_score >= 50.0
    }


if __name__ == "__main__":
    test_story = {
        "headline": "US and China Agree on Historic AI Incident Hotline and Bilateral Safety Talks",
        "summary": "Washington and Beijing establish an encrypted emergency communications line to prevent autonomous agent sandbox escapes and frontier model incidents from triggering geopolitical escalation.",
        "source": "https://www.reuters.com/technology/us-china-ai-hotline-2026",
        "mentions": 1
    }

    result = score_story_impact(
        test_story["headline"],
        test_story["summary"],
        test_story["source"],
        mentions_in_last_7_days=test_story["mentions"]
    )
    print("=" * 65)
    print("AUDIT SCORECARD FOR TEST STORY:")
    print("=" * 65)
    for k, v in result.items():
        print(f"  {k:<30}: {v}")
