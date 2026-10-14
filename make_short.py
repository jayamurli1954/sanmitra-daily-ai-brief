"""
Build a one-story vertical short (1080x1920) for Instagram Reels / YouTube Shorts.

    python make_short.py shorts/2026-10-14_claude_fake_tip.json

The spec file:
    {
      "date": "2026-10-14",
      "slug": "claude_fake_tip",
      "kicker": "BREAKING",
      "headline": "AI model sent a fake murder tip to police",
      "subhead": "One line under the headline.",
      "script": "What the anchor reads, ending with: Link in bio.",
      "voice": "aria",                      # or "christopher"
      "images": [{"src": "aibrief/assets/...jpg", "label": "PLACE • WHAT IT SHOWS"}],
      "source": "Sources: Outlet A, Outlet B",
      "storiesToday": 15
    }

Writes public/audio/aibrief/short_<date>_<slug>.mp3, src/aibrief/data/short_episode.json
and renders out/aibrief/short_<date>_<slug>.mp4 (composition AIBriefBreakingShort).
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime

import edge_tts
from mutagen.mp3 import MP3

from generate_aibrief_vo import CORRESPONDENT_VOICE, LEAD_VOICE, RATE, VOICE_VOLUME
from generate_subtitles import align_to_script, clean_subtitle_text, group_caption_words, transcribe_audio_words

FPS = 30
END_CARD_FRAMES = 75
# Vertical captions are about half the width of the episode's.
SHORT_CAPTION_CHARS = 26


def build(spec_path: str, render: bool = True) -> str:
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)
    date, slug = spec["date"], spec["slug"]
    voice = CORRESPONDENT_VOICE if spec.get("voice", "aria").lower() == "aria" else LEAD_VOICE

    audio_rel = f"audio/aibrief/short_{date}_{slug}.mp3"
    audio_path = os.path.join("public", audio_rel)
    asyncio.run(edge_tts.Communicate(spec["script"], voice, rate=RATE, volume=VOICE_VOLUME[voice]).save(audio_path))
    voice_frames = int(round(MP3(audio_path).info.length * FPS))

    words = align_to_script(transcribe_audio_words(audio_path, offset_seconds=0.0), spec["script"])
    cues = [
        {
            "text": clean_subtitle_text(" ".join(w["word"] for w in group)),
            "start": int(round(group[0]["start"] * FPS)),
            "end": int(round(group[-1]["end"] * FPS)),
        }
        for group in group_caption_words(words, max_chars=SHORT_CAPTION_CHARS, min_words=3)
    ]

    data = {
        "date": date,
        "dateLabel": datetime.strptime(date, "%Y-%m-%d").strftime("%d %B %Y").upper(),
        "kicker": spec.get("kicker", "BREAKING"),
        "headline": spec["headline"],
        "subhead": spec.get("subhead", ""),
        "source": spec["source"],
        "audioFile": audio_rel,
        "voiceFrames": voice_frames,
        "endCardFrames": END_CARD_FRAMES,
        "images": spec["images"],
        "cues": cues,
        "ctaTitle": "Full episode on YouTube",
        "ctaLine": "SanMitra AI News Wire",
        "ctaSub": f"{spec.get('storiesToday', 'All')} AI stories today • Link in bio",
    }
    with open(os.path.join("src", "aibrief", "data", "short_episode.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[+] Voice {voice_frames / FPS:.1f}s, {len(cues)} captions")

    out = os.path.join("out", "aibrief", f"short_{date}_{slug}.mp4")
    if render:
        npx = "npx.cmd" if sys.platform == "win32" else "npx"
        gl = "angle" if sys.platform == "win32" else "swangle"
        subprocess.run([npx, "remotion", "render", "AIBriefBreakingShort", out, "--codec=h264",
                        "--concurrency=2", f"--gl={gl}", "--log=error"], check=True)
        print(f"[+] Rendered {out}")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a one-story vertical short")
    parser.add_argument("spec", help="Path to the short's spec JSON")
    parser.add_argument("--no-render", action="store_true", help="Write voice and data only")
    args = parser.parse_args()
    build(args.spec, render=not args.no_render)
