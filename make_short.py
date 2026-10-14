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
        # Neutral wording: the same video goes to YouTube Shorts and Instagram.
        "ctaSub": f"All {spec.get('storiesToday', '')} of today's AI stories".replace("All  of", "All of"),
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


# ---------------------------------------------------------------------------
# Daily Short from the episode's lead story (called by run_autonomous_brief.py)
# ---------------------------------------------------------------------------

SHORT_MAX_WORDS = 110
SIGN_OFF = "Watch the full episode on SanMitra AI News Wire."


def _short_script(story_script: str) -> str:
    """The lead story's narration without the anchor's lead-in, cut at a sentence
    boundary near SHORT_MAX_WORDS, plus a sign-off that fits YouTube and Instagram."""
    import re
    from src.aibrief.generate_linkedin_article import clean_summary
    text = clean_summary(story_script)
    kept, words = [], 0
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        n = len(sentence.split())
        if kept and words + n > SHORT_MAX_WORDS:
            break
        kept.append(sentence)
        words += n
    return " ".join(kept).strip() + " " + SIGN_OFF


def spec_from_episode(episode: dict, date: str, slug: str = "lead") -> dict:
    lead = episode["stories"][0]
    why = (lead.get("whyThisMatters") or "").strip()
    subhead = why if 0 < len(why) <= 130 else ""
    return {
        "date": date,
        "slug": slug,
        "kicker": "BREAKING",
        "headline": lead["headline"],
        "subhead": subhead,
        "script": _short_script(lead.get("script", "")),
        "voice": "aria",
        "images": [{"src": c["image"], "label": c.get("badge", "")} for c in lead.get("visualCuts", [])[:3]],
        "source": f"Source: {lead.get('source', '')}",
        "storiesToday": len(episode.get("stories", [])),
    }


def write_platform_texts(spec: dict, main_video_url: str, out_dir: str = os.path.join("out", "aibrief")) -> tuple:
    """YouTube Shorts metadata (TITLE/DESCRIPTION file for upload_to_youtube.py)
    and an Instagram caption. Neither platform makes links in Shorts/Reels clickable:
    YouTube's "Related video" must be set by hand in Studio; Instagram uses the bio."""
    base = os.path.join(out_dir, f"short_{spec['date']}_{spec['slug']}")
    title = spec["headline"]
    if len(title) > 88:
        title = title[:88].rsplit(" ", 1)[0]
    summary = spec["script"].replace(SIGN_OFF, "").strip()
    yt = (
        f"TITLE:\n{title} #Shorts\n\nDESCRIPTION:\n{summary}\n\n"
        f"▶️ Full episode with all of today's AI stories: {main_video_url}\n\n"
        f"{spec['source']}\n\n#AI #AINews #ArtificialIntelligence #Shorts #SanMitraAINewsWire\n"
    )
    ig = (
        f"🚨 {spec['headline']}\n\n{summary}\n\n"
        f"▶️ Full episode with all of today's AI stories on YouTube: SanMitra AI News Wire. Link in bio.\n"
        f"{main_video_url}\n\n{spec['source']}\n\n"
        f"#AI #ArtificialIntelligence #AINews #TechNews #SanMitraAINewsWire\n"
    )
    with open(base + "_youtube_meta.txt", "w", encoding="utf-8") as f:
        f.write(yt)
    with open(base + "_instagram.txt", "w", encoding="utf-8") as f:
        f.write(ig)
    return base + "_youtube_meta.txt", base + "_instagram.txt"


def make_daily_short(date: str, main_video_id: str, privacy: str = "private", publish_at: str = None,
                     upload: bool = True) -> str:
    """Render the lead story as a Short and (optionally) upload it to YouTube."""
    with open(os.path.join("src", "aibrief", "data", "active_episode.json"), "r", encoding="utf-8") as f:
        episode = json.load(f)
    spec = spec_from_episode(episode, date)
    spec_path = os.path.join("shorts", f"{date}_{spec['slug']}.json")
    os.makedirs("shorts", exist_ok=True)
    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    video = build(spec_path, render=True)
    meta, ig = write_platform_texts(spec, f"https://youtu.be/{main_video_id}")
    print(f"[+] Short: {video}\n    YouTube text: {meta}\n    Instagram caption: {ig}")
    if upload:
        cmd = [sys.executable, "upload_to_youtube.py", "--date", date, "--privacy", privacy,
               "--video-file", video, "--meta-file", meta, "--thumb-file", "none", "--playlist", "shorts"]
        if publish_at:
            cmd += ["--publish-at", publish_at]
        subprocess.run(cmd, check=True)
    return video


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a one-story vertical short")
    parser.add_argument("spec", help="Path to the short's spec JSON")
    parser.add_argument("--no-render", action="store_true", help="Write voice and data only")
    args = parser.parse_args()
    build(args.spec, render=not args.no_render)
