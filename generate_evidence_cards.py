"""
Build the on-screen evidence cards (datelines, name tags, stat and "reported" cards)
for the active episode, timed to the narration.

Run after generate_subtitles.py, which writes the word timings this needs.
Writes src/aibrief/data/evidence_cards.json: {story_id: [card, ...]}.
"""

import json
import os
import sys

from src.aibrief.evidence_cards import build_episode_cards

DATA = os.path.join("src", "aibrief", "data")


def main(episode_path=os.path.join(DATA, "active_episode.json")):
    with open(episode_path, "r", encoding="utf-8") as f:
        episode = json.load(f)
    words_path = os.path.join(DATA, "word_timestamps.json")
    words = []
    if os.path.exists(words_path):
        with open(words_path, "r", encoding="utf-8") as f:
            words = json.load(f)
    timings = {}
    timings_path = os.path.join(DATA, "timings.json")
    if os.path.exists(timings_path):
        with open(timings_path, "r", encoding="utf-8") as f:
            timings = json.load(f)

    cards = build_episode_cards(episode, words, timings)
    with open(os.path.join(DATA, "evidence_cards.json"), "w", encoding="utf-8") as f:
        json.dump(cards, f, indent=2, ensure_ascii=False)

    total = sum(len(v) for v in cards.values())
    print(f"[+] Evidence cards: {total} across {len(cards)} stories")
    for sid, items in cards.items():
        print(f"    {sid[:40]:40} " + ", ".join(c["type"] for c in items))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
