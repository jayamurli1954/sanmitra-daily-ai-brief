"""
Production Pipeline from User-Supplied Prompt (Zero Scraping).
Executes end-to-end:
  1. (Optional) Ingest prompt markdown -> active_episode.json
  2. Edge TTS Christopher Voiceover synthesis
  3. SRT Subtitles & Remotion burn-in captions
  4. 1080p MP4 Remotion rendering
  5. Custom High-Contrast Thumbnail rendering
  6. Direct YouTube upload
  7. Google Drive backup
"""

import argparse
from datetime import datetime
import os
import shutil
import subprocess
import sys

def run_command(cmd, desc):
    print(f"\n[*] {desc}...")
    print(f"    Command: {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"[!] Warning/Error during '{desc}' (Exit code: {res.returncode})")
        return False
    return True

def produce_from_prompt(prompt_file=None, privacy="public", upload_youtube=True, render_video=True):
    print("=" * 75)
    print("🎬 SANMITRA AI NEWS WIRE — CLOUD PROMPT PRODUCTION ENGINE")
    print(f"🔒 YouTube Privacy: {privacy.upper()}")
    print("=" * 75)

    # 1. Parse prompt if given
    if prompt_file and os.path.exists(prompt_file):
        ok = run_command(f"python build_episode_from_prompt.py \"{prompt_file}\"", f"Parsing prompt from {prompt_file}")
        if not ok:
            print("[X] Failed to parse prompt. Aborting.")
            sys.exit(1)
    else:
        print("[*] Using existing active episode: src/aibrief/data/active_episode.json")

    active_file = os.path.join("src", "aibrief", "data", "active_episode.json")
    if not os.path.exists(active_file):
        print(f"[X] Active episode not found at {active_file}!")
        sys.exit(1)

    import json
    with open(active_file, "r", encoding="utf-8") as f:
        ep = json.load(f)
    date_str = ep.get("date", datetime.now().strftime("%Y-%m-%d"))

    # 2. Check and generate newsroom theme music if missing
    if not os.path.exists("public/audio/aibrief_theme.wav"):
        run_command("python generate_aibrief_music.py", "Generating newsroom background music bed")

    # 3. Generate voiceovers, timings, chapters, metadata
    ok_vo = run_command(f"python generate_aibrief_vo.py {active_file}", "Synthesizing voiceovers (en-US-ChristopherNeural)")
    if not ok_vo:
        print("[X] Voiceover synthesis failed!")
        sys.exit(1)

    # 4. Generate subtitles & burn-in captions
    run_command("python generate_subtitles.py", "Generating timed SRT and Remotion captions")

    # 5. Render Thumbnail Still
    os.makedirs("out/aibrief", exist_ok=True)
    thumb_path = f"out/aibrief/thumbnail_{date_str}.png"
    run_command(f"npx remotion still AIBriefThumbnailA {thumb_path}", "Rendering High-Contrast Breaking News Thumbnail")
    shutil.copyfile(thumb_path, "out/aibrief/thumbnail_A.png")

    # 6. Render Full 1080p Video
    video_out = f"out/aibrief/AI_Brief_{date_str}.mp4"
    if render_video:
        # Use concurrency suitable for GitHub Actions runners or local
        concurrency = 2 if os.environ.get("GITHUB_ACTIONS") else 6
        ok_render = run_command(
            f"npx remotion render AIBriefMaster16x9 {video_out} --concurrency {concurrency}",
            f"Rendering 1080p Master Video -> {video_out}"
        )
        if not ok_render:
            print("[X] Remotion render failed!")
            sys.exit(1)

    # 7. Upload to YouTube
    if upload_youtube and os.path.exists(video_out):
        ok_yt = run_command(
            f"python upload_to_youtube.py --date {date_str} --privacy {privacy} --video-file {video_out} --thumb-file {thumb_path}",
            f"Uploading 1080p Broadcast to YouTube ({privacy.upper()})"
        )

    # 8. Google Drive Backup
    folder_id = os.environ.get("GDRIVE_FOLDER_ID")
    if folder_id:
        run_command(f"python upload_to_gdrive.py --folder-id {folder_id}", "Backing up broadcast deliverables to Google Drive")

    print("\n" + "=" * 75)
    print("🚀 PRODUCTION FINISHED SUCCESSFULLY!")
    print(f"📅 Date:    {date_str}")
    print(f"🎬 Video:   {video_out}")
    print(f"🖼️  Thumb:   {thumb_path}")
    print("=" * 75)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Produce AI Brief directly from user prompt (zero scraping)")
    parser.add_argument("--prompt-file", help="Path to markdown prompt file")
    parser.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"], help="YouTube privacy")
    parser.add_argument("--no-render", action="store_true", help="Skip rendering")
    parser.add_argument("--no-upload", action="store_true", help="Skip YouTube upload")
    args = parser.parse_args()

    produce_from_prompt(
        prompt_file=args.prompt_file,
        privacy=args.privacy,
        upload_youtube=not args.no_upload,
        render_video=not args.no_render
    )
