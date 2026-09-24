import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def run_command(cmd, desc):
    print(f"[*] {desc}...")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"[!] Error running: {cmd} (exit code: {result.returncode})")
        return False
    return True

def produce_daily_brief():
    today_str = datetime.now().strftime("%Y-%m-%d")
    parser = argparse.ArgumentParser(description="Daily AI Brief Master Production Pipeline")
    parser.add_argument("--date", type=str, default=today_str, help=f"Episode date (YYYY-MM-DD, default: {today_str})")
    parser.add_argument("--scrape-fresh", action="store_true", help="Force scraping fresh 24h AI news across World, USA, China, Asia, India")
    parser.add_argument("--render-video", action="store_true", help="Render full 1080p MP4 video")
    parser.add_argument("--sample-frames", action="store_true", help="Render sample frame snapshots for preview")
    parser.add_argument("--upload-youtube", action="store_true", help="Upload directly to YouTube upon rendering")
    parser.add_argument("--privacy", type=str, default="public", choices=["public", "unlisted", "private"], help="YouTube privacy status")
    args = parser.parse_args()

    date_str = args.date
    episode_file = os.path.join("src", "aibrief", "data", f"{date_str}.json")
    active_file = os.path.join("src", "aibrief", "data", "active_episode.json")
    archive_dir = os.path.join("src", "aibrief", "data", "archive")

    print("=" * 70)
    print(f"🎬 DAILY AI BRIEF AUTOMATED PRODUCTION PIPELINE")
    print(f"📅 Target Episode Date: {date_str} (Today: {today_str})")
    print("=" * 70)

    # 1. Scrape 24h AI & Robotics news if requested or if episode file missing
    if args.scrape_fresh or not os.path.exists(episode_file):
        print(f"[*] Ingesting previous 24h AI & Robotics news for {date_str} across World, USA, China, Asia, India...")
        run_command(f"python scrape_daily_ai_news.py --date {date_str}", f"Scraping 24h intelligence for {date_str}")
        if not os.path.exists(episode_file):
            print(f"[X] Fatal: Failed to generate episode for {date_str}!")
            sys.exit(1)
    
    if os.path.abspath(episode_file) != os.path.abspath(active_file):
        print(f"[*] Setting {episode_file} as active episode...")
        shutil.copyfile(episode_file, active_file)

    # Ensure archived
    os.makedirs(archive_dir, exist_ok=True)
    archive_dest = os.path.join(archive_dir, f"{date_str}.json")
    shutil.copyfile(active_file, archive_dest)
    print(f"[+] Archived episode to: {archive_dest}")

    os.makedirs("out/aibrief", exist_ok=True)
    os.makedirs("public/audio/aibrief", exist_ok=True)
    os.makedirs("public/aibrief/assets", exist_ok=True)

    # 2. Check and generate story visual assets if needed
    run_command("python generate_story_assets.py", "Verifying and generating story visual assets")

    # 3. Check and generate newsroom theme music if missing
    if not os.path.exists("public/audio/aibrief_theme.wav"):
        run_command("python generate_aibrief_music.py", "Generating newsroom background music bed")
    else:
        print("[+] Newsroom audio bed present: public/audio/aibrief_theme.wav")

    # 4. Generate voiceovers, timings, chapters, YouTube metadata, and LinkedIn post
    run_command(f"python generate_aibrief_vo.py {active_file}", "Generating male broadcast voiceovers & metadata")

    # 5. Generate SRT subtitles and Remotion burn-in captions
    run_command(f"python generate_subtitles.py", "Generating SRT subtitles & burn-in caption cues")

    # 6. Render High-Contrast Breaking News Thumbnail Variants (A, B, C)
    thumb_A = f"out/aibrief/thumbnail_A.png"
    thumb_B = f"out/aibrief/thumbnail_B.png"
    thumb_C = f"out/aibrief/thumbnail_C.png"
    thumb_default = f"out/aibrief/thumbnail_{date_str}.png"
    
    run_command(f"npx remotion still AIBriefThumbnailA {thumb_A}", f"Rendering Thumbnail Variant A (Technical)")
    run_command(f"npx remotion still AIBriefThumbnailB {thumb_B}", f"Rendering Thumbnail Variant B (Intrigue)")
    run_command(f"npx remotion still AIBriefThumbnailC {thumb_C}", f"Rendering Thumbnail Variant C (Impact)")
    shutil.copyfile(thumb_A, thumb_default)

    # 7. Render Sample Frames for Preview
    if args.sample_frames or not args.render_video:
        sample_frame = "out/aibrief/preview_sample_frame.png"
        run_command(f"npx remotion still AIBriefMaster16x9 {sample_frame} --frame=400", f"Rendering preview sample frame -> {sample_frame}")

    # 8. Render Full Video if requested
    video_out = f"out/aibrief/AI_Brief_{date_str}.mp4"
    if args.render_video or args.upload_youtube:
        print(f"[*] Commencing full MP4 broadcast rendering -> {video_out}...")
        run_command(f"npx remotion render AIBriefMaster16x9 {video_out}", "Rendering 1080p MP4 Video")

    # 9. Automated YouTube Upload
    if args.upload_youtube:
        print(f"[*] Commencing automated YouTube upload ({args.privacy.upper()})...")
        run_command(
            f"python upload_to_youtube.py --date {date_str} --privacy {args.privacy}",
            "Uploading Broadcast Video & Thumbnail to YouTube"
        )

    print("\n" + "=" * 70)
    print("✅ AI BRIEF PRODUCTION COMPLETED SUCCESSFULLY!")
    print(f"📸 YouTube Thumbnails: ")
    print(f"   • Variant A (Technical): {thumb_A}")
    print(f"   • Variant B (Intrigue):  {thumb_B}")
    print(f"   • Variant C (Impact):    {thumb_C}")
    print(f"💬 Subtitles (SRT):    out/aibrief/captions_{date_str}.srt")
    print(f"📝 YouTube Metadata:   out/aibrief/youtube_metadata.txt")
    print(f"💼 LinkedIn Post:      out/aibrief/linkedin_post.txt")
    print(f"🗄️  Archived To:        {archive_dest}")
    if args.render_video:
        print(f"🎥 Final 1080p Video:  {video_out}")
    else:
        print(f"🎥 Video Composition:  Ready in Remotion Studio ('npm run dev')")
        print(f"💡 To render full MP4: python produce_daily_ai_brief.py --date {date_str} --render-video")
    print("=" * 70)

if __name__ == "__main__":
    produce_daily_brief()
