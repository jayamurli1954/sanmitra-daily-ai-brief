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

    for cluster in _STEMMED_CLUSTERS:
        if stems_a & cluster and stems_b & cluster:
            return True
    return len(shared - shared_subjects) >= 2


# ---------------------------------------------------------------------------
# Claim grounding
# ---------------------------------------------------------------------------

def _normalise_number(token):
    return token.replace(",", "").rstrip(".")


def extract_numbers(text):
    """Digit-bearing figures in text: 50, 1.5, 2026, 29,000 -> {'50', '1.5', '2026', '29000'}."""
    # A digit glued to letters before it is part of a name (a16z, H100), not a figure.
    return {_normalise_number(m) for m in re.findall(r"(?<![A-Za-z0-9.,])\d[\d,]*(?:\.\d+)?", text or "")}


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
    evidence_numbers = extract_numbers(evidence_text)
    missing = []
    for number in sorted(extract_numbers(claim_text)):
        if number not in evidence_numbers:
            missing.append(number)
    for name in sorted(_proper_noun_tokens(claim_text)):
        if not re.search(r"(?<![a-z0-9])" + re.escape(name.lower()) + r"(?![a-z0-9])", evidence_lower):
            missing.append(name)
    return missing
