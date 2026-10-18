"""
Merge the editor's own brief into the day's prompt.

The editor saves stories gathered elsewhere (ChatGPT, Grok, own reading) to
prompts/editor/<date>.md in the usual prompt format:

    # WORLD
    ### Headline
    Source: Outlet
    https://link
    Also: Other outlet https://other-link

    Summary paragraph.

Editor stories come first, in the editor's order, up to MAX_EPISODE_STORIES (9).
A collector or crew story about the same event is dropped and its outlet is added
to the editor story as an "Also:" source, so the editor's wording wins. Remaining
stories fill any places left.
"""

import re
from datetime import datetime

from .text_utils import content_stems, is_election_story, same_event

REGION_ORDER = ["WORLD", "USA", "CHINA", "ASIA", "INDIA"]
_URL = re.compile(r"https?://\S+")


def parse_stories(markdown):
    """Story blocks with their region, headline, source links and original lines."""
    stories, region, current = [], "WORLD", None
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("### "):
            current = {"region": region, "headline": stripped[4:].strip(), "lines": [line]}
            stories.append(current)
        elif re.match(r"^# (?!#)", stripped):
            region = stripped[2:].strip().upper()
            current = None
        elif stripped.startswith("## ") or stripped == "---":
            current = None
        elif current is not None:
            current["lines"].append(line)
    for s in stories:
        while s["lines"] and not s["lines"][-1].strip():
            s["lines"].pop()
        s["urls"] = {u.rstrip(").,") for line in s["lines"] for u in _URL.findall(line)}
        source = next((l.split(":", 1)[1].strip() for l in s["lines"] if l.strip().lower().startswith("source:")), "")
        # The link may be on its own line or on the Source line itself
        # ("Source: Euronews https://..."), as editors often write it.
        inline = _URL.search(source)
        if inline:
            source = source[:inline.start()].strip(" —-")
        primary = next((l.strip() for l in s["lines"] if l.strip().startswith("http")), "")
        s["source"], s["primary_url"] = source, primary or (inline.group(0).rstrip(").,") if inline else "")
    return stories


# Two or more capitalised words in a row: "Kanishka Narayan", "Brad Smith", "Great Lakes Institute".
_NAME = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b")


def _summary(story):
    return " ".join(l.strip() for l in story["lines"][1:]
                    if l.strip() and not l.strip().lower().startswith(("source:", "also:", "http")))


def _names(story):
    return set(_NAME.findall(_summary(story)[:600]))


def _same_story(a, b):
    """Same event when links match, headlines match, or headlines overlap and the
    summaries name the same person or organisation. Outlets word headlines very
    differently ("Cyber-attack similar to OpenAI Medicare breach seems likely in UK"
    vs "AI minister warns 'likely' UK's cyber defences will be breached"), but both
    summaries name Kanishka Narayan."""
    if a["urls"] & b["urls"] or same_event(a["headline"], b["headline"]):
        return True
    shared_words = content_stems(a["headline"]) & content_stems(b["headline"])
    return len(shared_words) >= 2 and bool(_names(a) & _names(b))


def _duplicate_of(story, kept):
    return next((k for k in kept if _same_story(story, k)), None)


def _add_also(target, other):
    if not other["primary_url"] or other["primary_url"] in target["urls"]:
        return False
    # "Also:" lines sit right after the primary link, before the summary.
    insert_at = 1
    for i, line in enumerate(target["lines"]):
        if line.strip().startswith(("http", "Also:")):
            insert_at = i + 1
    target["lines"].insert(insert_at, f"Also: {other['source'] or 'Source'} {other['primary_url']}")
    target["urls"].add(other["primary_url"])
    return True


def render(stories, date_str, weekly=False):
    day = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %d %B %Y")
    out = [
        "# SanMitra AI News Wire",
        "",
        # Sunday's round-up keeps its header: the builder keys the weekly intro off it.
        f"## Weekly Round-up — {day} (IST)" if weekly else f"## Daily AI Brief — {day} (IST)",
        "",
        "Covering AI developments from the previous day. Consolidated from the editor's brief "
        "and the crew's verified harvest; duplicates removed. Only items with a named outlet are included.",
    ]
    regions = REGION_ORDER + sorted({s["region"] for s in stories} - set(REGION_ORDER))
    for region in regions:
        group = [s for s in stories if s["region"] == region]
        if not group:
            continue
        out += ["", "---", "", f"# {region}"]
        for s in group:
            out += [""] + s["lines"]
    return "\n".join(out) + "\n"


def merge_editor_brief(editor_md, other_md, date_str, max_stories):
    """Returns (merged markdown, report dict)."""
    # No election news, from the editor or the crew (YouTube blocks promotion of it).
    election = []

    def allowed(story):
        if is_election_story(story["headline"], _summary(story)):
            election.append(story["headline"])
            return False
        return True

    editor_stories = [s for s in parse_stories(editor_md) if allowed(s)]
    kept = editor_stories[:max_stories]
    editor_count = len(kept)
    merged_dupes = []
    # The editor's list is in priority order; anything past the cap waits for another day.
    dropped_for_space = [s["headline"] for s in editor_stories[max_stories:]]
    for story in parse_stories(other_md or ""):
        if not allowed(story):
            continue
        dup = _duplicate_of(story, kept)
        if dup is not None:
            if dup in kept[:editor_count]:
                _add_also(dup, story)
            merged_dupes.append((story["headline"], dup["headline"]))
        elif len(kept) < max_stories:
            kept.append(story)
        else:
            dropped_for_space.append(story["headline"])
    # The editor's first story is the day's lead; any other lead mark gives way.
    lead_re = re.compile(r"(?i)^\s*\*{0,2}Lead\*{0,2}\s*:")
    for s in kept:
        s["lines"] = [l for l in s["lines"] if not lead_re.match(l)]
    if editor_count:
        kept[0]["lines"].insert(1, "Lead: yes")
    report = {
        "editor": editor_count,
        "added": len(kept) - editor_count,
        "duplicates": merged_dupes,
        "dropped_for_space": dropped_for_space,
        "dropped_election": election,
        "total": len(kept),
    }
    weekly = "## Weekly Round-up" in (other_md or "")
    return render(kept, date_str, weekly=weekly), report
