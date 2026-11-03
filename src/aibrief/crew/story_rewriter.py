"""
StoryRewriter - SanMitra AI News Wire

The collector and the fact-checker take each story's text from the outlet's own
article, and the anchors would otherwise read those sentences out word for word.
Before the episode is built, Claude rewrites every story body in prompts/<date>.md
in our own words: same facts, new sentences, the outlet credited once.

A rewrite that states a figure the original text does not is retried once, then
the original text is kept and the QA summary says so. Without ANTHROPIC_API_KEY,
or when the API fails, the prompt is left as it is.
"""

import json
import logging
import os
import re

from .text_utils import unsupported_quantities

logger = logging.getLogger("StoryRewriter")

MODEL = "claude-opus-5-5"
MAX_WORDS = 140  # fact_checker.STORY_MAX_WORDS: about 55 seconds read aloud
MARKER = "Story text rewritten by SanMitra in its own words."
_META = re.compile(r"^\s*\*{0,2}(?:Source|Also|Lead|Desk)\*{0,2}\s*:|^\s*https?://", re.IGNORECASE)

SYSTEM = """You rewrite news stories for a spoken daily AI news broadcast, the SanMitra AI News Wire. \
For each story you get the headline, the outlet and the outlet's text. Write the story fresh, \
in your own words, for a calm, authoritative broadcast anchor in the style of Reuters or Bloomberg.

Rules:
- Use only facts stated in the given text. Add no background, figures, dates, names or opinions it does not contain.
- Keep every name, number, amount and date exactly as stated.
- Write new sentences. Do not reuse the outlet's sentences or distinctive phrasing; apart from names, \
titles and a short quote, never repeat more than five words in a row from the text.
- Credit the outlet once, naturally ("according to Reuters", "the Guardian reports"). For a company's \
own announcement, say the company announced or said it.
- If the text quotes a person, you may keep one quote of under twelve words, with who said it.
- Write about as many words as the story's "words" value. A short text makes a short story: never pad \
it with commentary, context, significance or speculation.
- Plain spoken English. No markdown, bullet points, hashtags, URLs, region or section names, story \
numbers, or newspaper labels such as "Exclusive" or "can reveal".

Return every story id you were given, with its rewritten text."""

SCHEMA = {
    "type": "object",
    "properties": {
        "stories": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"id": {"type": "integer"}, "text": {"type": "string"}},
                "required": ["id", "text"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["stories"],
    "additionalProperties": False,
}


def story_bodies(lines):
    """[(headline, source, [line indexes of the body])] for each '### ' story, using the
    same block rules as editor_brief.parse_stories."""
    stories, current = [], None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("### "):
            current = {"headline": stripped[4:].strip(), "source": "", "body": []}
            stories.append(current)
        elif re.match(r"^# (?!#)", stripped) or stripped.startswith("## ") or stripped == "---":
            current = None
        elif current is not None and stripped:
            if stripped.lower().startswith("source:"):
                current["source"] = re.sub(r"https?://\S+", "", stripped.split(":", 1)[1]).strip(" —-")
            if not _META.match(stripped):
                current["body"].append(i)
    return [s for s in stories if s["body"]]


def _ask_claude(client, items):
    """{id: rewritten text} for the given [{id, headline, source, text}]."""
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        extra_body={"fallbacks": "default"},  # stories about hacking or weapons can trip a safety classifier
        system=SYSTEM,
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": json.dumps({"stories": items}, ensure_ascii=False)}],
    )
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"rewrite stopped early ({response.stop_reason})")
    text = next(b.text for b in response.content if b.type == "text")
    return {s["id"]: s["text"].strip() for s in json.loads(text)["stories"] if s["text"].strip()}


def _new_figures(rewritten, original):
    return unsupported_quantities(rewritten, original)


def rewrite_prompt_stories(prompt_path, client=None):
    """Rewrite each story body in the prompt in our own words. Returns QA warnings."""
    with open(prompt_path, "r", encoding="utf-8") as f:
        md = f.read()
    if MARKER in md:
        return []
    lines = md.splitlines()
    stories = story_bodies(lines)
    if not stories:
        return []

    if client is None:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return ["Story text was NOT rewritten (no ANTHROPIC_API_KEY): anchors read the outlets' own sentences."]
        import anthropic
        client = anthropic.Anthropic()

    originals = {i: " ".join(lines[n].strip() for n in s["body"]) for i, s in enumerate(stories)}
    items = [{"id": i, "headline": s["headline"], "source": s["source"], "text": originals[i],
              "words": min(MAX_WORDS, len(originals[i].split()))}
             for i, s in enumerate(stories)]
    try:
        rewritten = _ask_claude(client, items)
        retry = [it for it in items if it["id"] not in rewritten
                 or _new_figures(rewritten[it["id"]], originals[it["id"]])]
        if retry:
            rewritten.update(_ask_claude(client, retry))
    except Exception as e:
        logger.warning(f"Story rewrite failed: {e}")
        return [f"Story text was NOT rewritten ({e}): anchors read the outlets' own sentences."]

    warnings, replaced = [], {}
    for i, s in enumerate(stories):
        text = rewritten.get(i, "")
        extra = _new_figures(text, originals[i]) if text else ["no rewrite returned"]
        if extra:
            warnings.append(f"Kept the outlet's own text for '{s['headline']}': the rewrite "
                            f"did not match the original ({', '.join(map(str, extra))}).")
            continue
        replaced[s["body"][0]] = text
        for n in s["body"][1:]:
            replaced[n] = None

    out = [replaced.get(n, line) for n, line in enumerate(lines) if replaced.get(n, line) is not None]
    # The note sits above the first story, where the episode builder ignores it.
    first = next((n for n, line in enumerate(out) if line.strip() == "---" or line.startswith("# ")
                  and not line.startswith("# SanMitra")), 0)
    out[first:first] = [MARKER, ""]
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    logger.info(f"Rewrote {len(stories) - len(warnings)} of {len(stories)} stories in {prompt_path}")
    return warnings
