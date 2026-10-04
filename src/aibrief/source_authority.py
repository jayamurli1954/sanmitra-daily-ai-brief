"""
Source Authority Scoring Engine for SanMitra AI News Wire.
Implements the v2.1.1 Tiered Authority Model (0-100 pts):
  • Tier 1 (96-100): Global Financial & Wire Services (Reuters, Bloomberg, FT, AP)
  • Tier 2 (88-95): Investigative Tech & Business (The Information, WSJ, MIT Tech Review, TechCrunch)
  • Tier 3 (80-85): Primary Corporate Press & Research (OpenAI, Anthropic, DeepMind, Nvidia, MeitY, arXiv)
  • Tier 4 (60-75): Regional Tech Portals (Economic Times, SCMP, VentureBeat)
  • Tier 5 (0-40):  Unverified blogs and social media (Trigger quality warnings)

FIX (vs. original): domain matching no longer uses a bare substring check
(`known_dom in domain`), which could match unrelated domains that merely
contain a known domain's characters as a substring (e.g. a domain like
"myft.company.com" or "xapnews.co" would previously false-match "ft.com" /
"apnews.com"). Matching is now restricted to an exact match or a proper
dot-boundary suffix match (the domain IS the known domain, or ENDS WITH
".{known domain}").
"""

from typing import Tuple
from urllib.parse import urlparse

# Direct domain to authority score mapping
DOMAIN_AUTHORITY_MAP = {
    # Tier 1: Global Wires & Premier Financial (96 - 100)
    "reuters.com": (100, 1, "Reuters"),
    "bloomberg.com": (98, 1, "Bloomberg"),
    "ft.com": (96, 1, "Financial Times"),
    "apnews.com": (96, 1, "Associated Press"),

    # Tier 2: Investigative Tech & Premium Business (88 - 95)
    "theinformation.com": (95, 2, "The Information"),
    "wsj.com": (95, 2, "Wall Street Journal"),
    "technologyreview.com": (92, 2, "MIT Technology Review"),
    "techcrunch.com": (90, 2, "TechCrunch"),
    "arstechnica.com": (88, 2, "Ars Technica"),
    "cnbc.com": (88, 2, "CNBC"),
    "theverge.com": (86, 2, "The Verge"),
    "wired.com": (86, 2, "Wired"),
    "forbes.com": (82, 2, "Forbes Tech"),

    # Tier 3: Primary Frontier Labs & Institutional Gazettes (80 - 85)
    "openai.com": (85, 3, "OpenAI Newsroom"),
    "anthropic.com": (85, 3, "Anthropic Research"),
    "deepmind.google": (85, 3, "Google DeepMind"),
    "blogs.microsoft.com": (84, 3, "Microsoft Blog"),
    "nvidianews.nvidia.com": (84, 3, "Nvidia Newsroom"),
    "meity.gov.in": (85, 3, "MeitY India"),
    "pib.gov.in": (85, 3, "Press Information Bureau India"),
    "whitehouse.gov": (85, 3, "The White House"),
    "un.org": (85, 3, "United Nations"),
    "arxiv.org": (80, 3, "arXiv Pre-print"),

    # Tier 4: Credible Regional Business & Tech (60 - 75)
    "economictimes.indiatimes.com": (75, 4, "The Economic Times"),
    "businesstoday.in": (72, 4, "Business Today India"),
    "scmp.com": (75, 4, "South China Morning Post"),
    "venturebeat.com": (72, 4, "VentureBeat"),
    "restofworld.org": (72, 4, "Rest of World"),
    "techinasia.com": (70, 4, "Tech in Asia"),
    "koreajoongangdaily.joins.com": (70, 4, "Korea JoongAng Daily"),
    "nikkei.com": (75, 4, "Nikkei Asia"),
    "straitstimes.com": (73, 4, "The Straits Times"),
    "japantimes.co.jp": (75, 4, "The Japan Times"),
    "chosun.com": (68, 4, "ChosunBiz"),
    "military.com": (70, 4, "Military.com"),

    # Tier 5: Low-Verification / Unverified (0 - 40)
    "medium.com": (40, 5, "Medium Blog"),
    "substack.com": (35, 5, "Substack"),
    "twitter.com": (20, 5, "Twitter/X"),
    "x.com": (20, 5, "X"),
}

# Fallback name search if URL not available.
# NOTE: iteration order matters for substring matches below — keep longer,
# more specific names earlier so e.g. "ap news" doesn't swallow unrelated hits.
NAME_AUTHORITY_MAP = {
    "reuters": (100, 1),
    "bloomberg": (98, 1),
    "financial times": (96, 1),
    "associated press": (96, 1),
    "ap news": (96, 1),
    "the information": (95, 2),
    "wall street journal": (95, 2),
    "mit technology review": (92, 2),
    "techcrunch": (90, 2),
    "ars technica": (88, 2),
    "cnbc": (88, 2),
    "the verge": (86, 2),
    "wired": (86, 2),
    "openai": (85, 3),
    "anthropic": (85, 3),
    "google deepmind": (85, 3),
    "deepmind": (85, 3),
    "nvidia": (84, 3),
    "meity": (85, 3),
    "press information bureau": (85, 3),
    "the economic times": (75, 4),
    "economic times": (75, 4),
    "business today": (72, 4),
    "south china morning post": (75, 4),
    "scmp": (75, 4),
    "venturebeat": (72, 4),
    "nikkei": (75, 4),
    "the straits times": (73, 4),
    "straits times": (73, 4),
    "the japan times": (75, 4),
    "japan times": (75, 4),
    "chosunbiz": (68, 4),
    "military.com": (70, 4),
    "startupwire": (60, 4),
}


def _domain_matches(domain: str, known_domain: str) -> bool:
    """True only if domain IS known_domain, or ends with '.' + known_domain.
    Rejects false substring matches like 'xapnews.co' vs 'apnews.com'."""
    return domain == known_domain or domain.endswith("." + known_domain)


def score_source(url_or_name: str) -> Tuple[int, int, str]:
    """
    Evaluates source credibility and returns:
    (score: int, tier: int, identified_name: str)
    """
    if not url_or_name:
        return (50, 5, "Unknown Source")

    parsed = urlparse(url_or_name)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]

    if domain:
        # Exact match first
        if domain in DOMAIN_AUTHORITY_MAP:
            score, tier, name = DOMAIN_AUTHORITY_MAP[domain]
            return (score, tier, name)

        # Proper suffix match only (fixes the substring false-positive bug)
        for known_dom, (score, tier, name) in DOMAIN_AUTHORITY_MAP.items():
            if _domain_matches(domain, known_dom):
                return (score, tier, name)

    # Name-based lookup — longest known_name first so specific names win
    # over short substrings (e.g. "the economic times" before "economic times")
    clean_input = url_or_name.lower().strip()
    for known_name, (score, tier) in sorted(
        NAME_AUTHORITY_MAP.items(), key=lambda kv: -len(kv[0])
    ):
        if known_name in clean_input:
            return (score, tier, known_name.title())

    # Default unrecognized web source — surfaces the real domain/name instead
    # of silently inheriting an unrelated outlet's identity.
    return (65, 4, domain or url_or_name[:30])


def calculate_source_modifier(source_score: int) -> float:
    """
    Source Modifier = (source_score - 80) * 0.25
    """
    return round((source_score - 80) * 0.25, 2)


if __name__ == "__main__":
    test_sources = [
        "https://www.straitstimes.com/business/tencent-leases-chips-oracle",
        "https://www.businesstoday.in/technology/indiaai-mission-reset",
        "https://www.military.com/jet-powered-drones",
        "https://xapnews.co/not-really-ap",  # should NOT match Associated Press anymore
    ]
    print(f"{'Source Target':<55} | {'Score':<5} | {'Tier':<5} | Name")
    print("-" * 90)
    for src in test_sources:
        score, tier, name = score_source(src)
        print(f"{src[:55]:<55} | {score:<5} | {tier:<5} | {name}")
