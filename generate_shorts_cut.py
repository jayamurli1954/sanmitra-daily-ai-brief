#!/usr/bin/env python3
"""
SanMitra AI News Wire - YouTube Shorts 9:16 Auto-Cutter
Automatically crops 16:9 master broadcasts or individual stories into 9:16 vertical shorts,
respecting the YouTube mobile safe area (avoids UI dead-zones: header, like/share pill, description).
"""

import argparse
import json
import os
import subprocess
import sys


SAFE_AREA_TOP_MARGIN = 280     # Top 15% clear of header / sound info
SAFE_AREA_BOTTOM_MARGIN = 420  # Bottom 22% clear of description / like button
SAFE_AREA_SIDE_MARGIN = 60     # Side margins


def get_story_timing(episode_json_path: str, story_index: int):
    """Calculates start frame/second and duration for a given story from episode JSON."""
    if not os.path.exists(episode_json_path):
        raise FileNotFoundError(f"Episode JSON not found: {episode_json_path}")

    with open(episode_json_path, "r", encoding="utf-8") as f:
        ep = json.load(f)

    stories = ep.get("stories", [])
    if story_index < 1 or story_index > len(stories):
        raise ValueError(f"Invalid story index {story_index}. Episode has {len(stories)} stories.")

    # Story 1 starts after opening bumper / intro (approx 9 seconds = 270 frames)
    # Each segment has duration calculated from word count or durationSeconds
    # Let's read cumulative timing if present or compute from durationSeconds
    intro_sec = 9.5
    current_time = intro_sec

    for idx, s in enumerate(stories, 1):
        dur = s.get("durationSeconds", 30)
        if idx == story_index:
            return {
                "index": idx,
                "headline": s.get("headline", ""),
                "region": s.get("region", "WORLD"),
                "start_seconds": current_time,
                "duration_seconds": dur,
                "story_data": s
            }
        current_time += dur + 3.0  # +3s for chapter stinger transition

    return None


def generate_short(
    input_video: str,
    output_video: str,
    start_time: float = 0.0,
    duration: float = 58.0,
    add_safe_zone_guides: bool = False
):
    """
    Cuts and crops an input 16:9 MP4 into a 1080x1920 (9:16) vertical Short using FFmpeg.
    """
    if not os.path.exists(input_video):
        raise FileNotFoundError(f"Input video not found: {input_video}")

    os.makedirs(os.path.dirname(output_video) or ".", exist_ok=True)

    # 1. 9:16 Center-crop filter: take central 1080 horizontal pixels from 1920x1080
    # Center crop: crop=ih*9/16:ih:(iw-ow)/2:0,scale=1080:1920
    # In 1080p 16:9 (1920x1080): ih*9/16 = 607.5 px -> scaled to 1080x1920
    vf_filters = [
        "crop=ih*9/16:ih:(iw-ow)/2:0",
        "scale=1080:1920:flags=lanczos"
    ]

    if add_safe_zone_guides:
        # Draw translucent debug rectangles showing YouTube Shorts dead zones
        top_box = f"drawbox=y=0:h={SAFE_AREA_TOP_MARGIN}:color=red@0.25:t=fill"
        bot_box = f"drawbox=y=1920-{SAFE_AREA_BOTTOM_MARGIN}:h={SAFE_AREA_BOTTOM_MARGIN}:color=red@0.25:t=fill"
        vf_filters.extend([top_box, bot_box])

    filter_complex = ",".join(vf_filters)

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", f"{start_time:.2f}",
        "-t", f"{duration:.2f}",
        "-i", input_video,
        "-vf", filter_complex,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_video
    ]

    print(f"[*] Running FFmpeg 9:16 center-crop conversion...")
    print(f"    Start: {start_time:.2f}s | Duration: {duration:.2f}s | Safe Guides: {add_safe_zone_guides}")
    print(f"    Output: {output_video}")

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"[!] FFmpeg error: {result.stderr[-500:]}")
        raise RuntimeError("FFmpeg processing failed")

    print(f"[+] Successfully exported YouTube Short: {output_video}")


def main():
    parser = argparse.ArgumentParser(description="SanMitra AI News Wire YouTube Shorts Auto-Cutter")
    parser.add_argument("--input", default=None, help="Input master video path (16:9 MP4)")
    parser.add_argument("--output", default=None, help="Output short video path (9:16 MP4)")
    parser.add_argument("--date", default=None, help="Broadcast date (YYYY-MM-DD) to look up master video")
    parser.add_argument("--story", type=int, default=1, help="Story index to extract as a Short (1-based)")
    parser.add_argument("--start", type=float, default=None, help="Manual start time in seconds")
    parser.add_argument("--duration", type=float, default=None, help="Manual duration in seconds (max 60 for Shorts)")
    parser.add_argument("--guides", action="store_true", help="Burn visual dead-zone guidelines for testing")
    args = parser.parse_args()

    active_ep = os.path.join("src", "aibrief", "data", "active_episode.json")

    # Resolve input video
    input_file = args.input
    if not input_file:
        if args.date:
            candidate = os.path.join("out", "aibrief", f"AI_Brief_{args.date}.mp4")
            if os.path.exists(candidate):
                input_file = candidate
        if not input_file:
            import glob
            files = sorted(glob.glob("out/aibrief/AI_News_*.mp4"), reverse=True)
            if files:
                input_file = files[0]

    if not input_file or not os.path.exists(input_file):
        print(f"[!] No input video file found. Please provide --input <file.mp4>.")
        sys.exit(1)

    # Determine start and duration
    start = args.start
    duration = args.duration

    if start is None or duration is None:
        timing = get_story_timing(active_ep, args.story)
        if timing:
            if start is None:
                start = timing["start_seconds"]
            if duration is None:
                duration = min(timing["duration_seconds"], 58.0)
            print(f"[*] Auto-selected Story #{args.story} [{timing['region']}]: {timing['headline']}")
        else:
            start = start or 0.0
            duration = duration or 55.0

    output_file = args.output
    if not output_file:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join("out", "aibrief", f"{base_name}_Short_S{args.story}_9x16.mp4")

    generate_short(
        input_video=input_file,
        output_video=output_file,
        start_time=start,
        duration=duration,
        add_safe_zone_guides=args.guides
    )


if __name__ == "__main__":
    main()
