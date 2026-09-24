import argparse
import glob
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

def produce_weekly_roundup():
    parser = argparse.ArgumentParser(description="Weekly AI Brief Roundup Generator")
    parser.add_argument("--top", type=int, default=6, help="Number of top stories to include (default: 6)")
    parser.add_argument("--render-video", action="store_true", help="Render full MP4 video for the weekly roundup")
    args = parser.parse_args()

    archive_dir = os.path.join("src", "aibrief", "data", "archive")
    json_files = glob.glob(os.path.join(archive_dir, "*.json"))
    
    # If archive is small, also check current active episode
    active_path = os.path.join("src", "aibrief", "data", "active_episode.json")
    if active_path not in json_files and os.path.exists(active_path):
        json_files.append(active_path)

    if not json_files:
        print("[!] No archived episodes found in src/aibrief/data/archive/")
        sys.exit(1)

    print(f"[*] Scanning {len(json_files)} episode archive files for top stories...")
    all_stories = []
    seen_ids = set()

    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                stories = data.get("stories", [])
                for s in stories:
                    s_id = s.get("id")
                    if s_id and s_id not in seen_ids:
                        seen_ids.add(s_id)
                        all_stories.append(s)
        except Exception as e:
            print(f"Warning reading {jf}: {e}")

    # Rank all stories by importanceScore descending
    ranked_stories = sorted(all_stories, key=lambda s: s.get("importanceScore", 0), reverse=True)
    top_stories = ranked_stories[:args.top]

    week_date = datetime.now().strftime("%Y-W%W")
    formatted_date = f"Week {datetime.now().strftime('%W, %Y')}"

    weekly_data = {
        "date": f"weekly_{week_date}",
        "formattedDate": f"Weekly Roundup – {formatted_date}",
        "title": f"SanMitra AI News Wire | The Top AI Developments That Defined This Week",
        "intro": {
            "durationSeconds": 12,
            "headline": "WEEKLY AI ROUNDUP: TOP DEVELOPMENTS",
            "subheadline": "GLOBAL INTELLIGENCE RETROSPECTIVE",
            "script": "From the SanMitra Newsroom, here are the most critical artificial intelligence developments and strategic shifts that defined the global technology landscape this week."
        },
        "stories": top_stories,
        "outro": {
            "durationSeconds": 15,
            "headline": "SUBSCRIBE FOR WEEKLY & DAILY AI BRIEFS",
            "script": "Those were the top artificial intelligence stories of the week. Subscribe to SanMitra AI News Wire for daily morning intelligence and weekly institutional roundups.",
            "channels": ["World", "USA", "China", "Asia", "India"]
        },
        "thumbnail": {
            "brand": "SANMITRA AI",
            "date": "WEEKLY RECAP",
            "mainHeadline": top_stories[0].get("headline", "BIGGEST AI STORIES OF THE WEEK"),
            "secondaryHeadline": "WEEKLY TOP 6 STORIES",
            "subTag": "GLOBAL INTELLIGENCE",
            "badge": "WEEKLY ROUNDUP",
            "variants": {
                "A": {
                    "mainHeadline": top_stories[0].get("headline", "AI WEEK IN REVIEW"),
                    "badge": "WEEKLY ROUNDUP",
                    "secondaryHeadline": "TOP STORIES OF THE WEEK",
                    "subTag": "GLOBAL POLICY & HARDWARE"
                },
                "B": {
                    "mainHeadline": "WHAT HAPPENED IN AI THIS WEEK?",
                    "badge": "WEEKLY DEEP DIVE",
                    "secondaryHeadline": "6 CRITICAL STORIES",
                    "subTag": "EXECUTIVE RECAP"
                },
                "C": {
                    "mainHeadline": "THE AI RACE THIS WEEK",
                    "badge": "MARKET INTEL",
                    "secondaryHeadline": "WEEKLY EXECUTIVE BRIEF",
                    "subTag": "GLOBAL DEVELOPMENTS"
                }
            }
        },
        "ticker": [
            f"WEEKLY RECAP: Top {len(top_stories)} stories ranked by strategic global impact",
            "ARCHIVE INTELLIGENCE: Tracking sovereign AI, frontier safety, and hardware pipelines",
            "SUBSCRIBE: Daily morning briefs at 8 AM • Weekly comprehensive review every Sunday"
        ],
        "youtubeMetadata": {
            "title": f"AI Brief Weekly Roundup | Top AI News, Security & Policy Developments",
            "descriptionIntro": "This weekly executive roundup summarizes the most critical artificial intelligence stories from around the globe this week.",
            "tags": ["AI", "ArtificialIntelligence", "AINews", "TechRoundup", "WeeklyAI", "AIBrief"]
        }
    }

    out_json = os.path.join("src", "aibrief", "data", "weekly_roundup.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(weekly_data, f, indent=2)
    print(f"[+] Weekly roundup JSON generated: {out_json} ({len(top_stories)} top stories)")

    # Execute production pipeline for weekly roundup
    cmd = f"python produce_daily_ai_brief.py --date weekly_roundup"
    if args.render_video:
        cmd += " --render-video"
    
    print(f"[*] Running production pipeline on weekly roundup...")
    subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    produce_weekly_roundup()
