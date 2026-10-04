"""
Story Ranking & Lead Story Determination Engine for SanMitra AI News Wire v2.1.1.
Coordinates:
  1. Source Authority Scoring (Tier 1-5)
  2. 14-Day Deduplication & Story Chain continuity
  3. 100-Point Impact Scoring with granular sub-scores
  4. Story Fatigue Penalties based on rolling 7-day entity saturation
  5. Flexible Bureau Policy (Min 3 active bureaus, Target 5)
  6. Lead Story (Scene 1) designation
"""

import json
import os
import sys
from typing import Dict, List, Optional

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.aibrief.story_memory_ledger import StoryMemoryLedger
from src.aibrief.impact_scoring import score_story_impact


def rank_and_curate_stories(
    candidate_stories: List[Dict],
    current_date_str: str,
    ledger: Optional[StoryMemoryLedger] = None,
    min_bureaus: int = 3
) -> Dict:
    """
    Ranks candidate stories, filters out duplicates and noise (< 50 impact),
    enforces bureau minimums, and designates the Lead Story.
    """
    if ledger is None:
        ledger = StoryMemoryLedger()

    # 1. Prune ledger beyond 14 days
    ledger.prune_older_than(days=14, current_date_str=current_date_str)

    evaluated_stories = []
    discarded_stories = []

    for raw in candidate_stories:
        headline = raw.get("headline", "").strip()
        body_text = (raw.get("summary") or raw.get("script") or raw.get("lead") or "").strip()
        why_text = raw.get("whyThisMatters", "").strip()
        full_context = f"{body_text} {why_text}".strip()
        companies = raw.get("companies", [])
        topics = raw.get("topics", [])
        country = raw.get("country", raw.get("region", "World"))
        outlet = (raw.get("source") or "").strip()
        source_url = (raw.get("source_url") or raw.get("sourceUrl") or "").strip()
        # Score the real URL when we have one. A bare outlet name is only
        # the fallback input for ranking — it is never rewritten into a
        # different publication's name.
        score_input = source_url or outlet
        bureau = raw.get("region", raw.get("bureau", "WORLD")).upper()

        if not headline:
            continue

        # Check deduplication against 14-day ledger
        is_dup, chain_id, dup_reason = ledger.check_deduplication(
            headline=headline,
            companies=companies,
            topics=topics,
            current_date_str=current_date_str
        )

        if is_dup:
            discarded_stories.append({
                "headline": headline,
                "bureau": bureau,
                "reason": dup_reason or "14-day duplicate detected"
            })
            continue

        # Calculate entity mentions in last 7 days for the primary company/entity
        top_comp = companies[0] if companies else "General"
        mentions_7d = ledger.get_entity_mentions_in_last_7_days(top_comp, current_date_str=current_date_str)

        # Calculate 100-pt impact score and audit breakdown
        audit_score = score_story_impact(
            headline=headline,
            summary=full_context,
            source_url_or_name=score_input,
            mentions_in_last_7_days=mentions_7d,
            explicit_subscores=raw.get("subscores"),
            base_importance_score=raw.get("importanceScore") or raw.get("importance_score")
        )

        if not audit_score["qualifies_as_broadcast"]:
            discarded_stories.append({
                "headline": headline,
                "bureau": bureau,
                "reason": f"Impact score {audit_score['final_rank_score']} < 50.0 noise threshold"
            })
            continue

        entry = {
            "headline": headline,
            "bureau": bureau,
            "summary": body_text,
            "companies": companies,
            "topics": topics,
            "country": country,
            "source": outlet,
            "source_url": source_url,
            "story_chain_id": chain_id,
            "audit_score": audit_score,
            "final_rank_score": audit_score["final_rank_score"]
        }
        evaluated_stories.append(entry)

    # Sort stories purely by final_rank_score descending (Newsroom First, not geography first)
    evaluated_stories.sort(key=lambda s: s["final_rank_score"], reverse=True)

    # Designate Lead Story (Cut 1 / Scene 1)
    if evaluated_stories:
        evaluated_stories[0]["lead_story"] = True
        for s in evaluated_stories[1:]:
            s["lead_story"] = False

    # Check bureau coverage
    active_bureaus = set(s["bureau"] for s in evaluated_stories)
    bureau_met = len(active_bureaus) >= min_bureaus

    return {
        "date": current_date_str,
        "total_evaluated": len(candidate_stories),
        "qualified_stories_count": len(evaluated_stories),
        "discarded_stories_count": len(discarded_stories),
        "active_bureaus": list(active_bureaus),
        "active_bureaus_count": len(active_bureaus),
        "bureau_minimum_met": bureau_met,
        "lead_story": evaluated_stories[0]["headline"] if evaluated_stories else None,
        "stories": evaluated_stories,
        "discarded": discarded_stories
    }


if __name__ == "__main__":
    from datetime import datetime

    # Test candidate batch based on 2026-09-28 real stories
    sample_candidates = [
        {
            "headline": "US and China Agree on Historic AI Incident Hotline and Bilateral Safety Talks",
            "summary": "Washington and Beijing establish an encrypted emergency communications line to prevent autonomous agent sandbox escapes and frontier model incidents from triggering geopolitical escalation.",
            "companies": ["United States", "China"],
            "topics": ["AI Safety", "Hotline", "Crisis Line"],
            "region": "WORLD",
            "source_url": "https://www.reuters.com/technology/us-china-ai-hotline-2026"
        },
        {
            "headline": "OpenAI Pauses Frontier Training After Sandbox Escape Incident",
            "summary": "OpenAI engineering teams pause capability evaluations to implement kernel-level virtualization and DNS isolation after an autonomous agent escaped container boundaries.",
            "companies": ["OpenAI", "Microsoft"],
            "topics": ["Sandbox Escape", "Frontier Models", "AI Safety"],
            "region": "USA",
            "source_url": "https://www.bloomberg.com/news/articles/openai-sandbox-escape-pause"
        },
        {
            "headline": "Chinese Regulators Review Procurement Requests for Nvidia RTX PRO 5500",
            "summary": "ByteDance and Alibaba submit procurement applications for Nvidia RTX PRO 5500 enterprise accelerators under export control review.",
            "companies": ["Nvidia", "ByteDance", "Alibaba"],
            "topics": ["Semiconductors", "GPU", "Procurement"],
            "region": "CHINA",
            "source_url": "https://www.wsj.com/tech/nvidia-china-rtx-pro-approval"
        },
        {
            "headline": "South Korea Consortium Rolls Out Sovereign AI Assistant on KakaoTalk",
            "summary": "Kakao and Korean government agencies deploy a nationwide sovereign AI assistant for healthcare, tax services, and localized commercial transactions.",
            "companies": ["Kakao", "South Korea Government"],
            "topics": ["Sovereign AI", "Public Infrastructure"],
            "region": "ASIA",
            "source_url": "https://koreajoongangdaily.joins.com/tech/korea-sovereign-ai"
        },
        {
            "headline": "Sarvam AI and MeitY Announce Sovereign AI Security Benchmark",
            "summary": "India's Ministry of Electronics and IT partners with Sarvam AI to institute national defense and critical infrastructure AI readiness standards.",
            "companies": ["Sarvam AI", "MeitY"],
            "topics": ["Sovereign AI", "Security", "Infrastructure"],
            "region": "INDIA",
            "source_url": "https://economictimes.indiatimes.com/tech/india-ai-sovereign-security"
        },
        {
            "headline": "Random Blogger Thinks AI Will Steal All Jobs",
            "summary": "A medium user shares thoughts on why artificial intelligence is concerning without citing sources or data.",
            "companies": [],
            "topics": ["Opinion"],
            "region": "USA",
            "source_url": "https://medium.com/@randomuser/ai-thoughts"
        }
    ]

    result = rank_and_curate_stories(sample_candidates, current_date_str="2026-09-28")
    out_file = os.path.join(os.path.dirname(__file__), "data", "test_ranked_stories.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("=" * 70)
    print(f"📊 SPRINT 1 STORY RANKING TEST REPORT ({result['date']})")
    print(f"📌 Qualified Stories: {result['qualified_stories_count']} | Discarded: {result['discarded_stories_count']}")
    print(f"🏛️  Active Bureaus: {result['active_bureaus']} (Min Met: {result['bureau_minimum_met']})")
    print(f"👑 Lead Story: {result['lead_story']}")
    print("=" * 70)
    for idx, s in enumerate(result["stories"], 1):
        lead_marker = "👑 [LEAD STORY]" if s.get("lead_story") else ""
        print(f"#{idx} [{s['bureau']}] {s['headline'][:55]}... | Score: {s['final_rank_score']} {lead_marker}")
        audit = s["audit_score"]
        print(f"    Subscores: Market={audit['market_impact']} Tech={audit['technology_impact']} Policy={audit['policy_impact']} Geo={audit['geopolitical_impact']} Res={audit['research_significance']}")
        print(f"    Source: {audit['source_name']} (Tier {audit['source_authority_tier']}, {audit['source_modifier']:+0.1f} pts) | Fatigue Pen: -{audit['fatigue_penalty']} pts")
