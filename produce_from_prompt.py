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

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

def run_command(cmd, desc):
    print(f"\n[*] {desc}...")
    print(f"    Command: {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"[!] Warning/Error during '{desc}' (Exit code: {res.returncode})")
        return False
    return True

def produce_from_prompt(prompt_file=None, privacy="private", upload_youtube=True, render_video=True):
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

    # Ensure fresh story-specific editorial visuals are downloaded
    if os.path.exists("download_daily_editorial_visuals.py"):
        run_command(f"python download_daily_editorial_visuals.py --date {date_str}", "Ensuring fresh story-specific editorial visuals")

    # Hard gate: every on-screen source must appear in prompts/YYYY-MM-DD.md.
    # This runs after the prompt is parsed and before voiceover, render, or upload.
    traced = run_command(
        f"python validate_episode_sources.py --date {date_str}",
        "Source traceability gate",
    )
    if not traced:
        print("[X] Source traceability gate failed. Aborting before render and upload.")
        sys.exit(1)

    # 2. Check and generate newsroom theme music if missing
    if not os.path.exists("public/audio/aibrief_theme.wav"):
        run_command("python generate_aibrief_music.py", "Generating newsroom background music bed")

    # 3. Generate voiceovers, timings, chapters, metadata
    ok_vo = run_command(f"python generate_aibrief_vo.py {active_file}", "Synthesizing voiceovers (Christopher and Aria)")
    if not ok_vo:
        print("[X] Voiceover synthesis failed!")
        sys.exit(1)

    # 4. Generate subtitles & burn-in captions
    run_command("python generate_subtitles.py", "Generating timed SRT and Remotion captions")

    # 5. Render High-Contrast Thumbnails (Variants A, B, and C for A/B Testing)
    os.makedirs("out/aibrief", exist_ok=True)
    thumb_path = f"out/aibrief/thumbnail_{date_str}.png"
    thumb_primary = "out/aibrief/thumbnail_primary.png"
    thumb_a = "out/aibrief/thumbnail_A.png"
    thumb_b = "out/aibrief/thumbnail_B.png"
    thumb_c = "out/aibrief/thumbnail_C.png"

    run_command(f"npx remotion still AIBriefThumbnailA {thumb_a}", "Rendering Thumbnail Variant A (Breaking Red)")
    run_command(f"npx remotion still AIBriefThumbnailB {thumb_b}", "Rendering Thumbnail Variant B (Exclusive Cyan)")
    run_command(f"npx remotion still AIBriefThumbnailC {thumb_c}", "Rendering Thumbnail Variant C (Critical Emerald)")

    # AI Thumbnail Ranker: Algorithmic CTR selection
    try:
        from src.aibrief.thumbnail_ranker import rank_and_select_thumbnail
        candidates = [
            (thumb_a, "Variant A (Breaking Red)"),
            (thumb_b, "Variant B (Exclusive Cyan)"),
            (thumb_c, "Variant C (Critical Emerald)")
        ]
        rank_res = rank_and_select_thumbnail(candidates, output_primary_path=thumb_primary, date_alias_path=thumb_path)
        print(f"[+] AI Thumbnail Ranker Winner: {rank_res['winning_variant']} (Score: {rank_res['winning_score']}/100)")
    except Exception as e:
        print(f"[!] Warning ranking thumbnails: {e}. Fallback to Variant A.")
        shutil.copyfile(thumb_a, thumb_path)
        shutil.copyfile(thumb_a, thumb_primary)

    # 6. Render Full 1080p Video with Keyword-Rich Filename (YouTube SEO ingest optimization)
    import re
    kw_slug = "Global_AI_Brief"
    try:
        stories = ep.get("stories", [])
        if stories:
            top_title = stories[0].get("headline", "")
            clean = re.sub(r'[^a-zA-Z0-9]+', '_', top_title).strip('_')[:40]
            if clean:
                kw_slug = clean
    except Exception:
        pass

    video_out = f"out/aibrief/AI_News_{date_str}_{kw_slug}.mp4"
    legacy_alias = f"out/aibrief/AI_Brief_{date_str}.mp4"

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
        shutil.copyfile(video_out, legacy_alias)

    # 7. Upload to YouTube
    if upload_youtube and os.path.exists(video_out):
        ok_yt = run_command(
            f"python upload_to_youtube.py --date {date_str} --privacy {privacy} --video-file {video_out} --thumb-file {thumb_path}",
            f"Uploading 1080p Broadcast to YouTube ({privacy.upper()})"
        )

    # 8. Render LinkedIn Cover Banner & Generate LinkedIn Long-Form Article
    linkedin_cover = f"out/aibrief/linkedin_cover_{date_str}.png"
    run_command(f"npx remotion still AIBriefLinkedInCover {linkedin_cover}", "Rendering 16:9 LinkedIn Article Cover Banner")
    shutil.copyfile(linkedin_cover, "out/aibrief/linkedin_cover.png")

    run_command(f"python src/aibrief/generate_linkedin_article.py --json {active_file}", "Generating LinkedIn Long-Form Article & Executive Dispatch")

    # 9. Google Drive Backup
    folder_id = os.environ.get("GDRIVE_FOLDER_ID")
    f_arg = f"--folder-id {folder_id}" if folder_id else ""
    run_command(f"python upload_to_gdrive.py --date {date_str} {f_arg}", "Backing up broadcast & LinkedIn deliverables to Google Drive")

    print("\n" + "=" * 75)
    print("🚀 PRODUCTION FINISHED SUCCESSFULLY!")
    print(f"📅 Date:     {date_str}")
    print(f"🎬 Video:    {video_out}")
    print(f"🖼️  Thumb:    {thumb_path}")
    print(f"🎨 LI Cover: {linkedin_cover}")
    print(f"📝 LI Post:  out/aibrief/linkedin_article.md")
    print("=" * 75)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Produce AI Brief directly from user prompt (zero scraping)")
    parser.add_argument("--prompt-file", help="Path to markdown prompt file")
    parser.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"], help="YouTube privacy (default: private)")
    parser.add_argument("--no-render", action="store_true", help="Skip rendering")
    parser.add_argument("--no-upload", action="store_true", help="Skip YouTube upload")
    args = parser.parse_args()

    produce_from_prompt(
        prompt_file=args.prompt_file,
        privacy=args.privacy,
        upload_youtube=not args.no_upload,
        render_video=not args.no_render
    )
