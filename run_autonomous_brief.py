"""
Master Autonomous Production Pipeline - SanMitra AI News Wire v7.0
Executes the full end-to-end autonomous cycle with zero manual intervention:
  1. Multi-Agent News Gathering, Fact-Checking & Curation (Crew Architecture)
  2. Story-Specific Editorial Visual Sourcing (14-day anti-repetition memory)
  3. Dual-Anchor Edge TTS Voiceover Synthesis (-14 LUFS mastering)
  4. Timed SRT Subtitles & Remotion Burn-in Captions
  5. LinkedIn Executive Dispatch & 1080p Cover Banner Generation
  6. High-Contrast YouTube Thumbnails (A/B/C) with Algorithmic CTR Ranking
  7. Headless 1080p Remotion Video Rendering
  8. Automated YouTube Upload (Private by default) & Google Drive Backup
"""

import argparse
from datetime import datetime, timedelta, timezone
import json
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


def run_step(cmd, description):
    print(f"\n[*] {description}...")
    print(f"    Command: {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"[!] Warning/Error during '{description}' (Exit code: {res.returncode})")
        return False
    return True


def run_pipeline(date_str=None, privacy="private", upload_youtube=True, render_video=True, force_visuals=False):
    if not date_str:
        ist = timezone(timedelta(hours=5, minutes=30))
        date_str = datetime.now(ist).strftime("%Y-%m-%d")

    print("=" * 80)
    print("🎬 SANMITRA AI NEWS WIRE — FULLY AUTONOMOUS BROADCAST DESK")
    print(f"📅 Production Date: {date_str}")
    print(f"🔒 YouTube Privacy Mode: {privacy.upper()}")
    print("=" * 80)

    # 1. Multi-Agent Intelligence Gathering & Editorial Assembly
    from src.aibrief.crew import run_autonomous_crew
    ep = run_autonomous_crew(target_date=date_str, force_visuals=force_visuals)
    if not ep:
        print("[X] Agent crew failed to assemble episode. Aborting pipeline.")
        sys.exit(1)

    active_file = os.path.join("src", "aibrief", "data", "active_episode.json")

    # 2. Source Traceability Gate
    if os.path.exists("validate_episode_sources.py"):
        ok_trace = run_step(f"python validate_episode_sources.py --date {date_str}", "Source Traceability Gate")
        if not ok_trace:
            print("[X] Source traceability validation failed. Halting before voice and video rendering.")
            sys.exit(1)

    # 3. Audio Bed Verification
    if not os.path.exists("public/audio/aibrief_theme.wav"):
        run_step("python generate_aibrief_music.py", "Synthesizing Newsroom Theme Music Bed")

    # 4. Dual-Anchor Voiceover Synthesis (Christopher & Aria)
    ok_vo = run_step(f"python generate_aibrief_vo.py {active_file}", "Synthesizing Dual-Anchor Voiceover Audio")
    if not ok_vo:
        print("[X] Voiceover synthesis failed!")
        sys.exit(1)

    # 5. Timed SRT Subtitles & Remotion Captions
    run_step("python generate_subtitles.py", "Generating Timed Subtitles & Word Timestamps")

    # 6. Thumbnails Rendering & Algorithmic CTR Ranking
    os.makedirs(os.path.join("out", "aibrief"), exist_ok=True)
    thumb_path = f"out/aibrief/thumbnail_{date_str}.png"
    thumb_primary = "out/aibrief/thumbnail_primary.png"
    thumb_a = "out/aibrief/thumb_A.png"
    thumb_b = "out/aibrief/thumb_B.png"
    thumb_c = "out/aibrief/thumb_C.png"

    run_step(f"npx remotion still AIBriefThumbnailA {thumb_a}", "Rendering Thumbnail Variant A (Breaking Red)")
    run_step(f"npx remotion still AIBriefThumbnailB {thumb_b}", "Rendering Thumbnail Variant B (Exclusive Cyan)")
    run_step(f"npx remotion still AIBriefThumbnailC {thumb_c}", "Rendering Thumbnail Variant C (Critical Emerald)")

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
        print(f"[!] Thumbnail ranking notice: {e}. Fallback to Variant A.")
        if os.path.exists(thumb_a):
            shutil.copyfile(thumb_a, thumb_path)
            shutil.copyfile(thumb_a, thumb_primary)

    # 7. Render 1080p Master Video
    kw_slug = "Global_AI_Brief"
    try:
        stories = ep.get("stories", [])
        if stories:
            top_title = stories[0].get("headline", "")
            import re
            clean = re.sub(r'[^a-zA-Z0-9]+', '_', top_title).strip('_')[:40]
            if clean:
                kw_slug = clean
    except Exception:
        pass

    video_out = f"out/aibrief/AI_News_{date_str}_{kw_slug}.mp4"
    legacy_alias = f"out/aibrief/AI_Brief_{date_str}.mp4"

    if render_video:
        concurrency = 2
        gl_flag = "--gl angle" if sys.platform == "win32" else "--gl swangle"
        ok_render = run_step(
            f"npx remotion render AIBriefMaster16x9 {video_out} --concurrency {concurrency} --timeout 120000 {gl_flag}",
            f"Rendering 1080p Master Video -> {video_out}"
        )
        if not ok_render:
            print("[X] Remotion render failed!")
            sys.exit(1)
        shutil.copyfile(video_out, legacy_alias)

    # 8. Automated YouTube Upload
    if upload_youtube and os.path.exists(video_out):
        ok_yt = run_step(
            f"python upload_to_youtube.py {video_out} --privacy {privacy}",
            f"Uploading 1080p Broadcast to YouTube (Privacy: {privacy.upper()})"
        )
        if ok_yt:
            print("🎉 Video successfully uploaded to YouTube!")

    # 9. Google Drive Backup
    gdrive_folder = os.environ.get("GDRIVE_FOLDER_ID", "")
    if gdrive_folder and os.path.exists("upload_to_gdrive.py"):
        run_step(f"python upload_to_gdrive.py --folder-id {gdrive_folder}", "Syncing Deliverables to Google Drive")

    print("\n" + "=" * 80)
    print("🏆 FULL AUTONOMOUS BROADCAST DESK EXECUTION COMPLETE!")
    print(f"📺 Channel: https://www.youtube.com/@SanMitraTechSolutions")
    print(f"💼 LinkedIn Post: out/aibrief/linkedin_post.txt")
    print(f"🖼️ LinkedIn Banner: out/aibrief/linkedin_cover.png")
    print(f"🖼️ YouTube Thumbnail: {thumb_primary}")
    print(f"📹 1080p Broadcast: {video_out}")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SanMitra Autonomous Daily AI Brief Runner")
    parser.add_argument("--date", type=str, help="Target broadcast date (YYYY-MM-DD)")
    parser.add_argument("--privacy", type=str, default="private", choices=["private", "unlisted", "public"], help="YouTube visibility")
    parser.add_argument("--no-video", action="store_true", help="Skip video rendering")
    parser.add_argument("--no-upload", action="store_true", help="Skip YouTube upload")
    parser.add_argument("--force-visuals", action="store_true", help="Force redownload of editorial visual stills")
    args = parser.parse_args()

    run_pipeline(
        date_str=args.date,
        privacy=args.privacy,
        upload_youtube=not args.no_upload,
        render_video=not args.no_video,
        force_visuals=args.force_visuals
    )
