"""
Source Traceability Gate for SanMitra AI News Wire.

Run this AFTER build_episode_from_prompt.py and BEFORE render/upload.
It refuses to let an episode pass if any story's final "source" field
cannot be traced back to the approved prompts/YYYY-MM-DD.md that a human
signed off on — closing the gap where the rendered video can say
something the underlying research never said.

Usage:
    python validate_episode_sources.py --date 2026-10-03

Exit code 0  = every story's source is traceable; safe to proceed.
Exit code 1  = at least one story failed traceability; DO NOT render/upload.

Wire this into nightly_brief_collector.py / daily_brief_runner.py as a
hard gate: if this script exits non-zero, stop the pipeline there.
"""

import argparse
import json
import os
import re
import sys
from urllib.parse import urlparse

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Source strings that must NEVER appear in a published episode — these are
# known hardcoded fallbacks from the old pipeline, not real attributions.
BANNED_FALLBACK_SOURCES = {
    "reuters / bloomberg wire",
    "reuters, bloomberg",
    "reuters bloomberg",
    "verified reports",
    "global tech wire",
}

BANNED_FALLBACK_URLS = {
    "https://reuters.com",
    "https://sanmitra.ai",
}


def load_prompt_text(date_str: str) -> str:
    prompt_path = os.path.join(PROJECT_DIR, "prompts", f"{date_str}.md")
    if not os.path.exists(prompt_path):
        print(f"[FAIL] No approved prompt file found at {prompt_path}.")
        print("       An episode must never render from a prompt that was")
        print("       not committed — there would be nothing to check it against.")
        sys.exit(1)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def load_episode(date_str: str) -> dict:
    episode_path = os.path.join(
        PROJECT_DIR, "src", "aibrief", "data", f"{date_str}.json"
    )
    if not os.path.exists(episode_path):
        active_path = os.path.join(
            PROJECT_DIR, "src", "aibrief", "data", "active_episode.json"
        )
        if not os.path.exists(active_path):
            print(f"[FAIL] No episode JSON found for {date_str} and no active_episode.json.")
            sys.exit(1)
        episode_path = active_path
    with open(episode_path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def is_proper_article_url(url: str) -> bool:
    """A story may air only with a full article link, not a homepage or a cut-off slug."""
    if not url:
        return False
    cleaned = url.strip().rstrip(").,]>\"'")
    if cleaned.rstrip("/").lower() in BANNED_FALLBACK_URLS:
        return False
    parsed = urlparse(cleaned)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return False
    segments = [part for part in parsed.path.split("/") if part]
    if not segments:
        return False
    last = segments[-1]
    # ".../She" is a truncated slug, not an article.
    if len(last) < 8 and not any(ch.isdigit() for ch in last):
        return False
    return True


def source_appears_in_prompt(source_name: str, prompt_text: str) -> bool:
    """A story's attributed source must appear, case-insensitively, as a
    literal substring of the approved prompt markdown. This deliberately
    does NOT accept a fuzzy/semantic match — if the exact outlet name isn't
    in the signed-off research, it does not go on screen."""
    if not source_name:
        return False
    norm_prompt = normalize(prompt_text)
    # Split multi-source strings like "The Straits Times, Reuters"
    for piece in re.split(r",|/|&|\band\b", source_name):
        piece = normalize(piece)
        if piece and piece in norm_prompt:
            return True
    return False


# Claims that were painted on the cold open for every episode, with no
# connection to that day's approved brief. The intro must take its headline
# and outlet from the lead story instead.
BANNED_INTRO_CLAIMS = (
    "ars technica",
    "meta muse",
    "amazon blocked",
    "critical vulnerability exposed",
    "0-day",
)


def intro_scene_problems() -> list:
    """The opening card is the first claim a viewer sees. It cannot be a leftover literal."""
    scene_path = os.path.join(PROJECT_DIR, "src", "aibrief", "scenes", "IntroScene.tsx")
    problems = []
    if not os.path.exists(scene_path):
        return [f"Intro scene is missing: {scene_path}"]
    text = open(scene_path, "r", encoding="utf-8").read()
    lowered = text.lower()
    for phrase in BANNED_INTRO_CLAIMS:
        if phrase in lowered:
            problems.append(f"IntroScene.tsx still hardcodes '{phrase}'")
    if "leadHeadline" not in text or "leadSource" not in text:
        problems.append(
            "Intro cold open must render the lead story headline and source from the episode."
        )
    if re.search(r"SRC:\s*[A-Za-z]", text):
        problems.append("Intro source line must come from the lead story, not a typed outlet name.")
    return problems


def validate(date_str: str) -> bool:
    prompt_text = load_prompt_text(date_str)
    episode = load_episode(date_str)

    stories = episode.get("stories", [])
    if not stories:
        print("[FAIL] Episode has no stories to validate.")
        return False

    all_ok = True
    intro_problems = intro_scene_problems()
    if intro_problems:
        all_ok = False
        print("[FAIL] Cold open is not driven by today's lead story.")
        for problem in intro_problems:
            print(f"    - {problem}")
        print()

    print(f"Validating {len(stories)} stories for {date_str} against {date_str}.md\n")

    for idx, story in enumerate(stories, 1):
        headline = story.get("headline", "<no headline>")
        source = (story.get("source") or "").strip()
        source_url = (story.get("sourceUrl") or "").strip()

        problems = []

        if not source or normalize(source) in BANNED_FALLBACK_SOURCES:
            problems.append(f"source is missing or a banned generic fallback: '{source}'")

        if not is_proper_article_url(source_url):
            problems.append(
                f"sourceUrl is not a full article link: '{source_url}'. "
                "This story must not be in the video."
            )

        if not source_appears_in_prompt(source, prompt_text):
            problems.append(
                f"source '{source}' does not appear anywhere in prompts/{date_str}.md"
            )

        status = "OK" if not problems else "FAIL"
        marker = "OK" if status == "OK" else "FAIL"
        print(f"[{marker}] Story {idx}: {headline[:70]}")
        print(f"    source: {source!r}  sourceUrl: {source_url!r}")
        for p in problems:
            print(f"    - {p}")
        if problems:
            all_ok = False
        print()

    if all_ok:
        print("RESULT: All stories traceable to approved research. Safe to render/publish.")
    else:
        print("RESULT: One or more stories FAILED traceability.")
        print("        DO NOT render or upload this episode until fixed.")

    return all_ok


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate that every episode story's source traces to the approved prompt markdown."
    )
    parser.add_argument("--date", required=True, help="Episode date (YYYY-MM-DD)")
    args = parser.parse_args()

    ok = validate(args.date)
    sys.exit(0 if ok else 1)
