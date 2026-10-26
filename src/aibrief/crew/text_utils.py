"""
Shared text helpers for the crew agents.

Every keyword test in the crew goes through contains_any(), which matches on
word boundaries. A bare `"ai" in text` matches "said", "again" and "paid", and
`"infor" in text` sends "information security" to the ASIA bureau.
"""

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import html
import re

IST = timezone(timedelta(hours=5, minutes=30))

_KEYWORD_CACHE = {}


def _keyword_pattern(keyword):
    pattern = _KEYWORD_CACHE.get(keyword)
    if pattern is None:
        # Allow an optional plural so "chip" matches "chips" but not "chipotle".
        pattern = re.compile(r"(?<![a-z0-9])" + re.escape(keyword.lower()) + r"(?:s|es)?(?![a-z0-9])")
        _KEYWORD_CACHE[keyword] = pattern
    return pattern


def contains_any(text, keywords):
    """True if any keyword appears in text as a whole word or phrase."""
    lowered = (text or "").lower()
    return any(_keyword_pattern(k).search(lowered) for k in keywords)


# The channel does not cover stock-market news (editor's decision, 2026-10-14):
# share-price moves, indices, trading. Startup funding rounds are not excluded.
STOCK_MARKET_TERMS = [
    "stock market", "stock markets", "stocks", "stock price", "share price", "share prices",
    "shares fell", "shares fall", "shares rose", "shares rise", "shares slide", "shares slid",
    "shares tumble", "shares tumbled", "shares jump", "shares jumped", "shares surge", "shares surged",
    "shares plunge", "shares plunged", "shares sink", "shares soar", "sell-off", "selloff",
    "wall street", "nasdaq", "dow jones", "s&p 500", "sensex", "nifty", "kospi", "nikkei",
    "hang seng", "ftse", "market cap", "market value", "stock exchange", "bear market", "bull market",
    # IPO filings and company financial results are out too (editor, 2026-10-21): not purely AI news.
    "ipo", "ipos", "initial public offering", "drhp", "draft red herring", "goes public", "go public",
    "going public", "public listing", "files to list",
    # "Anthropic officially files for its public debut" got through (editor, 2026-10-26).
    "public debut", "market debut", "trading debut", "listing debut", "public offering", "s-1",
    "quarterly results", "annual results",
    "q1 results", "q2 results", "q3 results", "q4 results", "q1 revenue", "q2 revenue", "q3 revenue",
    "q4 revenue", "quarterly revenue", "quarterly profit", "quarterly loss", "half-year revenue",
    "net profit", "net loss", "earnings",
    # Results wording without the word "results" (editor, 2026-10-22: "Meta beats expectations
    # but legal penalties hit profit amid AI race" got through).
    "profit", "profits", "operating loss", "net income", "beats expectations", "beat expectations",
    "misses expectations", "missed expectations", "tops expectations", "beats estimates", "beat estimates",
    "misses estimates", "missed estimates", "tops estimates", "topped estimates", "analyst estimates",
    "first-quarter", "second-quarter", "third-quarter", "fourth-quarter", "fiscal quarter",
    "quarterly sales", "revenue forecast", "profit warning",
]
# "Profit" inside these is about the kind of organisation, not its results.
NOT_RESULTS = re.compile(r"\b(?:non-?profits?|not-for-profit)\b")


def is_stock_market_story(title):
    """True when the headline is about share prices, markets or company results. Judged
    on the headline only: a passing mention in the body does not exclude a story."""
    return contains_any(NOT_RESULTS.sub(" ", (title or "").lower()), STOCK_MARKET_TERMS)


# No election news (editor's decision, 2026-10-18): YouTube disapproved two
# episodes for promotion because they mentioned the US election. Unlike the
# stock-market rule this is judged on the whole text, since a passing mention
# in the narration is enough to block promotion.
ELECTION_TERMS = [
    "election", "elections", "electoral", "re-election", "reelection", "pre-election", "post-election",
    "election commission", "electoral college", "ballot", "ballots", "ballot box", "voter", "voters",
    # Not plain "vote"/"voting": "a vote of confidence" and shareholder "voting rights" are not elections.
    "vote count", "vote counting", "votes cast", "postal vote", "popular vote", "voting machine",
    "voting machines", "voting booth", "voting day", "polling station", "polling booth", "exit poll", "exit polls",
    "opinion poll", "opinion polls", "campaign trail", "presidential race", "presidential campaign",
    "presidential candidate", "presidential debate", "running mate", "midterm", "midterms",
    "primaries", "caucus", "caucuses", "polling day", "election day", "political ad", "political ads",
    "political advertising", "campaign ad", "campaign ads", "lok sabha polls", "assembly polls",
    # US politicians count too (editor, 2026-10-18): YouTube treats videos featuring federal
    # officeholders as election content. Plain "lawmakers" is not a trigger (EU, India).
    "senator", "sen.", "congressman", "congresswoman", "congressmen", "congresswomen", "congress",
    "congressional", "senate", "house of representatives", "house speaker", "speaker of the house",
    "capitol hill", "white house", "president trump", "trump", "vance", "biden",
]


# Personal lawsuits, abuse allegations and celebrity gossip are not AI news, even when
# a famous AI name is involved (editor, 2026-10-22: "Judge dismisses Sam Altman's
# sister's sexual abuse lawsuit" was the collector's lead). Judged on the headline;
# a headline that is about AI itself (deepfakes, chatbots, AI models) is kept.
PERSONAL_SCANDAL_TERMS = [
    "sexual abuse", "sexual assault", "sexual harassment", "sexual misconduct", "abuse lawsuit",
    "abuse allegations", "rape", "molestation", "molested", "divorce", "custody battle",
    "affair", "his sister", "her sister", "sister's", "sister’s", "his brother", "her brother",
    "brother's", "brother’s",
    "his wife", "her husband", "family feud", "estranged", "scandal", "gossip", "celebrity",
    "actress", "actor", "bollywood", "hollywood star", "arrested", "murder", "domestic violence",
    "defamation suit", "paternity",
]
AI_SUBJECT_TERMS = [
    "deepfake", "deepfakes", "ai-generated", "ai generated", "chatbot", "chatbots", "ai model",
    "ai models", "ai tool", "ai tools", "ai agent", "ai agents", "generative ai", "algorithm",
    "ai image", "ai images", "ai video", "ai voice", "grok", "chatgpt", "gemini", "claude",
]


def is_personal_scandal_story(title):
    """True for personal lawsuits, abuse allegations and celebrity gossip whose
    headline is not about AI itself."""
    return contains_any(title, PERSONAL_SCANDAL_TERMS) and not contains_any(title, AI_SUBJECT_TERMS)


def is_election_story(title, body=""):
    """True when the headline or the text mentions elections, campaigns or US politicians."""
    return contains_any(f"{title or ''} {body or ''}", ELECTION_TERMS)


def count_matches(text, keywords):
    lowered = (text or "").lower()
    return sum(1 for k in keywords if _keyword_pattern(k).search(lowered))


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------

def parse_published(value):
    """Parse an RSS / ISO / page-metadata date into an aware UTC datetime, or None."""
    if not value:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        dt = None
        try:
            dt = parsedate_to_datetime(text)
        except (TypeError, ValueError, IndexError):
            dt = None
        if dt is None:
            try:
                dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def broadcast_reference_time(target_date):
    """06:00 IST on the broadcast date: the moment the episode goes out."""
    day = datetime.strptime(target_date, "%Y-%m-%d")
    return day.replace(hour=6, tzinfo=IST).astimezone(timezone.utc)


def is_recent(published, target_date, max_age_hours=36):
    """True if published falls in the window before the broadcast. Unknown dates fail."""
    dt = parse_published(published)
    if dt is None:
        return False
    ref = broadcast_reference_time(target_date)
    return ref - timedelta(hours=max_age_hours) <= dt <= ref + timedelta(hours=1)


# ---------------------------------------------------------------------------
# Feed and article text cleanup
# ---------------------------------------------------------------------------

_FEED_BOILERPLATE = [
    r"The post .{0,300}? appeared first on [^.]{1,80}\.?",
    r"\bContinue reading\b[^\n]*",
    r"\bRead (?:the )?(?:full|more)\b[^\n]*",
    r"\[(?:…|\.\.\.|&#8230;)\]",
    r"\(?Photo(?:graph)?: [^)]{1,120}\)?",
]

_BOILERPLATE_SENTENCE = re.compile(
    r"(subscribe|sign up|newsletter|cookie|all rights reserved|©|getty images|"
    r"click here|advertisement|follow us|reporting by|editing by|our standards)",
    re.IGNORECASE,
)


def clean_feed_text(text):
    """Strip HTML, feed boilerplate and doubled punctuation from a blurb or article."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text).replace(" ", " ")
    for pattern in _FEED_BOILERPLATE:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\.{2,}(?!\.)", ".", text)
    return text


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'“])", text or "")
    return [p.strip() for p in parts if p.strip()]


def extractive_summary(article_text, max_sentences=3, max_words=90):
    """The first substantive sentences of the article itself, not the feed blurb."""
    kept = []
    for sentence in split_sentences(clean_feed_text(article_text)):
        if len(sentence) < 40 or _BOILERPLATE_SENTENCE.search(sentence):
            continue
        if not sentence.endswith((".", "!", "?")):
            continue
        kept.append(sentence)
        if len(kept) >= max_sentences or len(" ".join(kept).split()) >= max_words:
            break
    return " ".join(kept)


# ---------------------------------------------------------------------------
# Same-event detection
# ---------------------------------------------------------------------------

_STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "after", "into", "over", "about",
    "its", "their", "has", "have", "will", "new", "says", "said", "amid", "as", "at", "by",
    "in", "of", "on", "to", "a", "an", "is", "are", "be", "was", "were", "it", "how", "why",
    "what", "ai", "artificial", "intelligence", "model", "models", "company", "firm", "tech",
    "technology", "report", "reports", "news", "update", "could", "may", "than", "more",
    # Topic words shared by unrelated stories ("data center", "AI agents").
    "data", "center", "centers", "centre", "centres", "agent", "agents", "startup", "startups",
    "user", "users", "chip", "chips",
}

# Different words reporters use for the same action.
ACTION_CLUSTERS = [
    {"pull", "withdraw", "scrap", "cancel", "halt", "shelve", "abandon", "postpone", "drop"},
    {"float", "ipo", "listing", "debut", "offering"},
    {"ban", "prohibit", "bar", "block", "restrict"},
    {"acquire", "acquisition", "buy", "purchase", "takeover", "merger"},
    {"probe", "investigate", "investigation", "inquiry", "scrutiny", "subpoena", "lawsuit", "sue"},
    {"resign", "quit", "depart", "exit", "fire", "dismiss", "oust", "sack"},
    {"raise", "funding", "round", "valuation", "invest", "investment"},
    {"launch", "release", "unveil", "debut", "introduce", "ship", "rollout"},
]


def _stem(word):
    for suffix in ("ations", "ation", "ings", "ing", "ives", "ive", "ied", "ies", "ed", "es", "s", "e"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


_STEMMED_CLUSTERS = [{_stem(w) for w in cluster} for cluster in ACTION_CLUSTERS]


def content_stems(text):
    words = re.findall(r"[a-z][a-z0-9'-]{1,}", (text or "").lower())
    return {_stem(w.strip("'-")) for w in words if w not in _STOPWORDS and len(w) > 2}


def named_entities(text):
    """Capitalised names (single or multi-word) that are not sentence-start filler."""
    found = set()
    for match in re.finditer(r"\b([A-Z][a-zA-Z0-9&.-]+(?:\s+[A-Z][a-zA-Z0-9&.-]+)*)", text or ""):
        name = match.group(1).strip(".")
        if name.lower() in _STOPWORDS or len(name) < 3:
            continue
        found.add(name.lower())
    return found


def _entity_words(text):
    words = set()
    for entity in named_entities(text):
        words.update(w for w in entity.split() if w not in _STOPWORDS and len(w) > 2)
    return words


def same_event(title_a, title_b):
    """True if two headlines describe the same news event.

    Two stories are the same event when they share a named subject AND either an
    action (pull/withdraw, ban/prohibit, ipo/float...) or two other content words.
    "Firmus pulls ASX float" and "Firmus withdraws historic IPO" share the subject
    and both the pull/withdraw and float/IPO actions.
    """
    stems_a, stems_b = content_stems(title_a), content_stems(title_b)
    if not stems_a or not stems_b:
        return False
    shared = stems_a & stems_b
    jaccard = len(shared) / len(stems_a | stems_b)
    if jaccard >= 0.5:
        return True

    action_stems = set().union(*_STEMMED_CLUSTERS)
    shared_subjects = (
        {_stem(w) for w in _entity_words(title_a)} & {_stem(w) for w in _entity_words(title_b)}
    ) - action_stems
    if not shared_subjects:
        return False

    # One shared action is not enough: "Google launches Gemini" and "Google
    # launches AI search" are different launches. It takes two shared actions
    # (pull + IPO), or an action plus another shared detail, or two details.
    shared_actions = sum(1 for cluster in _STEMMED_CLUSTERS if stems_a & cluster and stems_b & cluster)
    details = shared - shared_subjects - action_stems
    if shared_actions >= 2:
        return True
    if shared_actions == 1:
        return len(details) >= 1
    return len(details) >= 2


# ---------------------------------------------------------------------------
# Claim grounding
# ---------------------------------------------------------------------------

def _normalise_number(token):
    return token.replace(",", "").rstrip(".")


def extract_numbers(text):
    """Digit-bearing figures in text: 50, 1.5, 2026, 29,000 -> {'50', '1.5', '2026', '29000'}."""
    # A digit glued to letters before it is part of a name (a16z, H100), not a figure.
    return {_normalise_number(m) for m in re.findall(r"(?<![A-Za-z0-9.,])\d[\d,]*(?:\.\d+)?", text or "")}


_UNIT_WORDS = {
    "%": "percent", "percent": "percent", "per cent": "percent", "percentage": "percent",
    "thousand": "thousand", "k": "thousand",
    "million": "million", "mn": "million", "m": "million",
    "billion": "billion", "bn": "billion", "b": "billion",
    "trillion": "trillion", "tn": "trillion", "t": "trillion",
    "crore": "crore", "lakh": "lakh",
}

_QUANTITY = re.compile(
    r"(?<![A-Za-z0-9.,])(\d[\d,]*(?:\.\d+)?)"
    r"(?:\s*(%|per\s?cent|percent(?:age)?|thousand|million|billion|trillion|crore|lakh)(?![A-Za-z])"
    r"|(bn|mn|tn|[kmbt])(?![A-Za-z]))?",
    re.IGNORECASE,
)


def extract_quantities(text):
    """Figures with their magnitude: '$50 billion' and '$50bn' -> ('50', 'billion');
    '40%' and '40 percent' -> ('40', 'percent'); a bare 2026 -> ('2026', '')."""
    found = set()
    for match in _QUANTITY.finditer(text or ""):
        unit = (match.group(2) or match.group(3) or "").lower()
        unit = re.sub(r"\s+", " ", unit)
        found.add((_normalise_number(match.group(1)), _UNIT_WORDS.get(unit, unit)))
    return found


def unsupported_quantities(claim_text, evidence_text):
    """Figures in the claim the evidence does not state with the same magnitude.

    "$50 billion" is not supported by "$50 million". A bare figure in the claim
    only needs the same number somewhere in the evidence.
    """
    evidence = extract_quantities(evidence_text)
    evidence_numbers = {n for n, _u in evidence}
    missing = []
    for number, unit in sorted(extract_quantities(claim_text)):
        if unit:
            if (number, unit) not in evidence:
                missing.append(f"{number} {unit}")
        elif number not in evidence_numbers:
            missing.append(number)
    return missing


# Companies and labs are checked wherever they appear in a headline, including
# as its first word ("Microsoft cuts error rates..."), which the general name
# heuristic below has to skip.
KNOWN_COMPANIES = [
    "openai", "anthropic", "google", "alphabet", "deepmind", "microsoft", "meta", "amazon", "apple",
    "nvidia", "amd", "intel", "tsmc", "samsung", "sk hynix", "ibm", "oracle", "salesforce", "tesla",
    "spacex", "xai", "mistral", "cohere", "perplexity", "hugging face", "deepseek", "alibaba",
    "tencent", "baidu", "bytedance", "huawei", "infosys", "tcs", "wipro", "reliance", "softbank",
]


def _proper_noun_tokens(text):
    """Tokens that are names, not ordinary words.

    In a sentence-case line, any capitalised word that does not start a sentence.
    In a Title Case headline every word is capitalised, so only tokens that are
    unmistakably names count: acronyms and mixed case (ASX, OpenAI, GPT-5, xAI).
    """
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9&-]*", text or "")
    if not tokens:
        return set()
    capitalised = [t for t in tokens if t[0].isupper()]
    title_case = len(capitalised) / len(tokens) > 0.6
    names = set()
    for sentence in split_sentences(text) or [text]:
        words = re.findall(r"[A-Za-z][A-Za-z0-9&-]*", sentence)
        for position, word in enumerate(words):
            upper_count = sum(1 for ch in word if ch.isupper())
            mixed = upper_count >= 2 or (upper_count >= 1 and not word[0].isupper())
            if title_case:
                if mixed:
                    names.add(word)
            elif word[0].isupper() and (position > 0 or mixed):
                if word.lower() not in _STOPWORDS and len(word) > 2:
                    names.add(word)
    return names


def ungrounded_claims(claim_text, evidence_text):
    """Numbers and names in claim_text that never appear in evidence_text.

    The fact-check is deliberately literal: if a figure or a name is on screen or
    spoken, it has to be in the article the story is attributed to.
    """
    evidence_lower = (evidence_text or "").lower()
    missing = unsupported_quantities(claim_text, evidence_text)
    names = {n.lower() for n in _proper_noun_tokens(claim_text)}
    names.update(c for c in KNOWN_COMPANIES if contains_any(claim_text, [c]))
    for name in sorted(names):
        if not re.search(r"(?<![a-z0-9])" + re.escape(name) + r"(?![a-z0-9])", evidence_lower):
            missing.append(name)
    return missing
