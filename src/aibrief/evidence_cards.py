"""
Evidence cards: on-screen proof for what the anchor is saying, timed to the word.

For each story script this finds
  - a dateline (city named in the script, plus a date if one is given),
  - stat cards (amounts, counts, "N times" multipliers; two like amounts in one
    sentence become a comparison),
  - one "reported" card: the key attributed sentence, shown as a clipping with
    the claim highlighted. It is only shown in quotation marks when the script
    itself quotes someone,
  - name tags for people introduced with a title ("Nvidia chief executive Jensen Huang").

Nothing is invented: every card is built from the script text and the story's
own source. Cards are placed at the time the anchor words are spoken
(word_timestamps.json) and never overlap.
"""

import re

CARD_SECONDS = 5.5
NAME_SECONDS = 4.0
GAP_SECONDS = 0.8
FIRST_CARD_AT = 2.0
MAX_CARDS = 4
MAX_STATS = 2

MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december"]

# Datelines only for places we are sure are places.
CITIES = [
    "New York", "San Francisco", "Washington", "Silicon Valley", "Seattle", "Boston", "Austin",
    "Los Angeles", "Santa Clara", "Mountain View", "Palo Alto", "Menlo Park", "Redmond",
    "London", "Paris", "Berlin", "Brussels", "Geneva", "Zurich", "Amsterdam", "Stockholm",
    "Davos", "Dublin", "Madrid", "Rome", "Munich", "Toronto", "Montreal", "Vancouver",
    "Beijing", "Shanghai", "Shenzhen", "Hangzhou", "Hong Kong", "Taipei", "Tokyo", "Osaka",
    "Seoul", "Pyongyang", "Singapore", "Bangkok", "Jakarta", "Kuala Lumpur", "Manila", "Hanoi",
    "Dubai", "Abu Dhabi", "Riyadh", "Doha", "Tel Aviv", "Sydney", "Melbourne",
    "New Delhi", "Delhi", "Mumbai", "Bengaluru", "Bangalore", "Hyderabad", "Chennai", "Pune",
    "Kolkata", "Noida", "Gurugram", "Ahmedabad", "Sriharikota",
]

TITLES = [
    ("chief executive officer", "Chief executive"), ("chief executive", "Chief executive"),
    ("chief technology officer", "Chief technology officer"), ("ceo", "Chief executive"),
    ("co-founder", "Co-founder"), ("cofounder", "Co-founder"), ("founder", "Founder"),
    ("chief scientist", "Chief scientist"), ("chairman", "Chairman"), ("chairwoman", "Chairwoman"),
    ("chief economic adviser", "Chief Economic Adviser"), ("prime minister", "Prime Minister"),
    ("minister", "Minister"), ("president", "President"), ("senator", "US Senator"),
    ("representative", "US Representative"), ("secretary", "Secretary"),
    ("lead author", "Lead author"), ("researcher", "Researcher"), ("professor", "Professor"),
]

WORD_NUMBERS = {
    "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
    "forty": 40, "fifty": 50, "hundred": 100, "thousand": 1000,
}

SCALES = {"thousand": "K", "million": "MILLION", "billion": "BILLION", "trillion": "TRILLION",
          "crore": "CRORE", "lakh": "LAKH"}
CURRENCIES = {"dollar": "$", "dollars": "$", "rupee": "₹", "rupees": "₹", "yuan": "¥",
              "euro": "€", "euros": "€", "pound": "£", "pounds": "£"}

ATTRIBUTION = re.compile(
    r"\b(said|says|told|argued|warned|called for|urged|announced|reported|claims?|claimed|"
    r"cited|described|pointed to|published|released|issued)\b", re.I)
NOT_STATS_AFTER = re.compile(r"^(?:%s)\b" % "|".join(MONTHS), re.I)

# A transition line the anchor reads before the story proper.
TRANSITION_SENTENCE = re.compile(r"^(turning to|now to|over to|in|from|and in|meanwhile in)\b[^.]{0,40}\.$", re.I)


def sentences(script):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"“])", script or "") if s.strip()]


def norm_tokens(text):
    return [t for t in (re.sub(r"[^a-z0-9]", "", w.lower()) for w in (text or "").split()) if t]


def _clip_words(text, n):
    words = text.split()
    out = " ".join(words[:n])
    return out.rstrip(",;:") + ("…" if len(words) > n else "")


# --------------------------------------------------------------------------- dateline

def find_dateline(script):
    city = None
    best = None
    for c in CITIES:
        m = re.search(r"\b(?:in|from|at)\s+(?:the\s+)?(?:[A-Z][\w&.-]*\s+){0,6}?" + re.escape(c) + r"\b", script)
        m = m or re.search(r"\bin\s+" + re.escape(c) + r"\b", script)
        if m and (best is None or m.start() < best):
            best, city = m.start(), c
    if not city:
        return None
    date = None
    d = re.search(r"\bon\s+(\d{1,2})\s+(%s)\b" % "|".join(MONTHS), script, re.I)
    if d:
        date = f"{int(d.group(1))} {d.group(2).upper()}"
    return {"type": "dateline", "place": city.upper(), "date": date}


# --------------------------------------------------------------------------- name tags

NAME = r"((?:[A-Z]\.\s)?[A-Z][a-z'’-]+(?:\s(?:[A-Z]\.\s?)?[A-Z][a-z'’-]+){1,2})"


def find_people(script):
    people = []
    seen = set()
    for key, label in TITLES:
        title = "(?i:" + re.escape(key) + ")"
        for m in re.finditer(r"(?:(\b[A-Z][\w&-]*(?:\s[A-Z][\w&-]*)?)(?:'s|’s)?\s)?\b" + title + r"\s" + NAME, script):
            org, name = m.group(1), m.group(2)
            name = re.sub(r"\s+(?:said|says|told|and|who)$", "", name)
            if name.split()[0] in ("The", "This", "That", "US", "AI"):
                continue
            last = name.split()[-1]
            if last in seen:
                continue
            if org and org.split()[0] in ("The", "A", "An", "Speaking", "In", "On", "At", "Its", "His", "Her", "Their"):
                org = None
            if org and org.lower() in (k for k, _ in TITLES):
                org = None  # "Prime Minister", "Chief Economic Adviser": part of the title
            role = label
            if org and label not in ("US Senator", "US Representative", "Prime Minister"):
                role = f"{label}, {org}"
            seen.add(last)
            people.append({"type": "name", "name": name.upper(), "role": role, "anchor": name, "pos": m.start(2)})
    people.sort(key=lambda p: p["pos"])
    return people


# --------------------------------------------------------------------------- stats

NUM = r"(\$\s?)?(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)"
STAT = re.compile(
    NUM + r"(\s?%|\s(?:percent|per cent))?(?:\s(thousand|million|billion|trillion|crore|lakh))?"
    r"(?:\s(dollars?|rupees?|yuan|euros?|pounds?))?", re.I)
TIMES = re.compile(r"\b(%s|\d+)(?:\s|-)?(?:times|fold)\b|\b(%s)fold\b" % (
    "|".join(WORD_NUMBERS), "|".join(WORD_NUMBERS)), re.I)


def _label_after(sentence, end):
    rest = sentence[end:].lstrip()
    rest = re.sub(r"^(?:dollars?|rupees?|yuan|euros?|pounds?)\b", "", rest, flags=re.I).lstrip()
    head = re.split(r"[,;:.()]|\s(?:and|but|while|which|plus|as)\s", rest)[0].strip()
    if len(head.split()) < 2 and rest.startswith(","):
        head = re.split(r"[;:.()]", rest[1:])[0].strip()
    return _clip_words(head, 7)


def find_stats(script):
    out = []
    for sent in sentences(script):
        found = []
        for m in STAT.finditer(sent):
            dollar, num, pct, scale, cur = m.groups()
            before = sent[:m.start()].rstrip()
            after = sent[m.end():].lstrip()
            prev_word = before.split()[-1] if before.split() else ""
            if prev_word[:1].isupper() and prev_word.lower() not in ("about", "nearly", "over", "roughly") \
                    and not prev_word.endswith(","):
                continue  # model names and versions: "Flash 1017", "Zam 2.0"
            if re.match(r"^[-–]\w", sent[m.end():]) or NOT_STATS_AFTER.match(after):
                continue  # "five-year", dates
            value = float(num.replace(",", ""))
            if not (pct or scale or cur or dollar):
                if value < 100 or (1900 <= value <= 2100 and "." not in num):
                    continue
                if not re.match(r"^[a-z]", after):
                    continue
            symbol = "$" if dollar else CURRENCIES.get((cur or "").lower(), "")
            shown = f"{symbol}{num}"
            if pct:
                shown += "%"
            if scale:
                shown += " " + SCALES[scale.lower()]
            if re.search(r"\b(?:more than|over|at least|upwards of)$", before, re.I):
                shown += "+"
            label = _label_after(sent, m.end())
            found.append({"value": value, "shown": shown, "unit": (symbol, (scale or "").lower(), bool(pct)),
                          "label": label, "anchor": sent[m.start():m.end()].lstrip("$ ").strip(), "pos": m.start()})
        for m in TIMES.finditer(sent):
            word = (m.group(1) or m.group(2)).lower()
            n = WORD_NUMBERS.get(word) or (int(word) if word.isdigit() else None)
            if not n:
                continue
            found.append({"value": n, "shown": f"{n}×", "unit": ("×", "", False),
                          "label": _label_after(sent, m.end()), "anchor": m.group(0), "pos": m.start()})
        if not found:
            continue
        found.sort(key=lambda f: f["pos"])
        money = [f for f in found if f["unit"][0] or f["unit"][1]]
        if len(money) == 2 and money[0]["unit"][1:] == money[1]["unit"][1:] and money[0]["value"] != money[1]["value"]:
            a, b = money
            # "44 trillion dollars ... up from 30 trillion": the currency carries over.
            sym = a["unit"][0] or b["unit"][0]
            for x in (a, b):
                if sym and sym != "×" and not x["shown"].startswith(sym):
                    x["shown"] = sym + x["shown"]
            out.append({"type": "compare", "anchor": a["anchor"], "sentence": sent,
                        "items": [{"shown": a["shown"], "value": a["value"], "label": a["label"]},
                                  {"shown": b["shown"], "value": b["value"], "label": b["label"]}]})
            continue
        best = found[0]
        if best["label"]:
            out.append({"type": "stat", "anchor": best["anchor"], "shown": best["shown"], "label": best["label"],
                        "sentence": sent})
    return out[:MAX_STATS]


# --------------------------------------------------------------------------- reported / quote card

QUOTE = re.compile(r"[\"“]([^\"”]{12,220})[\"”]")


def _clip_sentence(sent, max_words):
    """Shorten a long sentence at its last comma that keeps it readable, not mid-phrase."""
    if len(sent.split()) <= max_words:
        return sent
    cut = None
    for m in re.finditer(r",", sent):
        if 14 <= len(sent[:m.start()].split()) <= max_words:
            cut = m.start()
    return (sent[:cut] if cut else " ".join(sent.split()[:max_words])).rstrip(",;: ") + "…"


def _short_highlight(claim, max_words=26):
    """Keep the highlight to one readable clause."""
    if len(claim.split()) <= max_words:
        return claim
    for m in re.finditer(r",", claim):
        if 6 <= len(claim[:m.start()].split()) <= max_words:
            return claim[:m.start()]
    return " ".join(claim.split()[:max_words])


def find_reported(script, source, people, skip=0):
    """The key attributed sentence (or a real quote) as a clipping card."""
    q = QUOTE.search(script or "")
    if q and len(q.group(1).split()) >= 4 and not skip:
        who = None
        before = script[:q.start()]
        for p in people:
            if p["anchor"] in before or p["anchor"].split()[-1] in before:
                who = p["anchor"]
        return {"type": "quote", "text": q.group(1).strip(), "speaker": who, "source": source,
                "anchor": " ".join(q.group(1).split()[:3])}
    pool = sentences(script)
    pool = pool[:4] if not skip else pool[skip:]
    for sent in pool:
        if TRANSITION_SENTENCE.match(sent):
            continue
        m = ATTRIBUTION.search(sent)
        if not m or len(sent.split()) < 8:
            continue
        claim = sent[m.end():].lstrip(" ,")
        # "told policymakers that ...", "said this week that ...": the claim starts after "that".
        lead = claim.split(" that ", 1)
        if len(lead) == 2 and len(lead[0].split()) <= 5:
            claim = lead[1]
        claim = re.sub(r"^(?:that|on|of)\s+", "", claim)
        claim = re.split(r"[,;](?=\s(?:and|but|with|while|which|plus)\b)", claim)[0].rstrip(".")
        text = _clip_sentence(sent, 44)
        visible = text.rstrip("…")
        if claim and claim not in visible:
            # The sentence was clipped: highlight the part of the claim still on the card.
            start = visible.find(claim[:30])
            claim = visible[start:] if start >= 0 else ""
        highlight = _short_highlight(claim.strip()) if claim and len(claim.split()) >= 3 else None
        return {"type": "reported", "text": text, "highlight": highlight, "source": source,
                "anchor": " ".join(sent.split()[:3])}
    return None


# --------------------------------------------------------------------------- timing

def find_time(words, anchor):
    """Seconds into the scene at which the anchor phrase is spoken, or None."""
    target = norm_tokens(anchor)[:3]
    if not target:
        return None
    toks = [norm_tokens(w["word"]) for w in words]
    flat = [t[0] if t else "" for t in toks]
    for n in (len(target), 2, 1):
        tgt = target[:n]
        for i in range(len(flat) - n + 1):
            if flat[i:i + n] == tgt:
                return words[i]["rel"]
    return None


def _schedule(items, words, end_limit, seconds, first_at, limit, taken=()):
    """Place items at their spoken time, earliest first, without overlapping each other or `taken`."""
    timed = []
    for c in items:
        t = find_time(words, c["anchor"])
        if t is None:
            continue
        start = max(t - 0.2, first_at)
        end = min(start + seconds, end_limit)
        if end - start >= 2.5:
            timed.append((start, end, c))
    timed.sort(key=lambda x: x[0])
    chosen = []
    for start, end, c in timed:
        busy = list(taken) + chosen
        if len(busy) >= limit or any(start < b["end"] + GAP_SECONDS and end + GAP_SECONDS > b["start"] for b in busy):
            continue
        card = {k: v for k, v in c.items() if k not in ("anchor", "pos", "sentence")}
        card.update({"start": round(start, 2), "end": round(end, 2)})
        chosen.append(card)
    return chosen


def build_story_cards(story, scene_words, scene_seconds=None):
    """Two tracks: tags (dateline, then name tags) top left, and cards in the middle of the frame."""
    script = story.get("script", "")
    source = re.sub(r"\s+,\s+", " / ", story.get("source", ""))
    people = find_people(script)
    end_limit = (scene_seconds or (scene_words[-1]["rel"] + 1.0 if scene_words else 0)) - 0.5

    cards = []
    rep = find_reported(script, source, people)
    if rep:
        cards.append(rep)
    stats = find_stats(script)
    cards = _schedule(cards + stats, scene_words, end_limit, CARD_SECONDS, FIRST_CARD_AT, MAX_CARDS)
    if len(stats) < 2:
        # A thin story gets a second clipping from later in the script, in a free gap.
        later = find_reported(script, source, people, skip=3)
        if later and (not rep or later["text"] != rep["text"]):
            cards = sorted(cards + _schedule([later], scene_words, end_limit, CARD_SECONDS, FIRST_CARD_AT,
                                             MAX_CARDS, taken=cards), key=lambda c: c["start"])

    tags = []
    dl = find_dateline(script)
    tag_from = 0.4
    if dl and end_limit > 3:
        dl.update({"start": 0.4, "end": round(min(4.5, end_limit), 2)})
        tags.append(dl)
        tag_from = dl["end"] + GAP_SECONDS
    tags += _schedule(people, scene_words, end_limit, NAME_SECONDS, tag_from, 3)
    return tags + cards


def build_episode_cards(episode, word_timestamps, timings=None):
    """Return {story_id: [card, ...]} with times relative to the story scene."""
    by_scene = {}
    for w in word_timestamps:
        by_scene.setdefault(w.get("sceneId"), []).append(w)
    result = {}
    for story in episode.get("stories", []):
        sid = story.get("id")
        words = by_scene.get(sid, [])
        if words:
            base = words[0].get("sceneStart", words[0]["start"])
            for w in words:
                w["rel"] = round(w["start"] - base, 3)
        scene_seconds = (timings or {}).get(sid, {}).get("audioDurationSeconds")
        result[sid] = build_story_cards(story, words, scene_seconds)
    return result
