import asyncio
import json
import os
import sys
from pathlib import Path
from mutagen.mp3 import MP3
import edge_tts

VOICE = "en-US-ChristopherNeural"
RATE = "+1%"
VOLUME = "+25%"

def get_audio_duration(file_path: str) -> float:
    try:
        audio = MP3(file_path)
        return float(audio.info.length)
    except Exception as e:
        print(f"Warning measuring {file_path}: {e}")
        return 10.0

def format_timestamp(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

async def generate_voiceover(data_path: str = "src/aibrief/data/active_episode.json"):
    print(f"[*] Reading episode data from {data_path}...")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs("public/audio/aibrief", exist_ok=True)
    os.makedirs("out/aibrief", exist_ok=True)

    stories = data.get("stories", [])
    transitions = {t.get("region"): t for t in data.get("transitions", [])}

    # Build sequence of items
    sequence = []
    
    # 1. Intro
    intro = data.get("intro", {})
    sequence.append({
        "id": "intro",
        "title": "Intro: Today's Biggest AI Developments",
        "filename": "s0_intro.mp3",
        "text": intro.get("script", "Today on SanMitra AI News Wire: Here are today's biggest AI developments."),
        "is_transition": False
    })

    # 2. Stories with regional transitions
    for i, story in enumerate(stories, 1):
        s_id = story.get("id", f"story_{i}")
        headline = story.get("headline", "")
        script = story.get("script", "")
        region = story.get("region", "")

        # Check transition if region changed
        if i > 1 and region != stories[i - 2].get("region"):
            if region in transitions:
                trans = transitions[region]
                sequence.append({
                    "id": trans.get("id"),
                    "title": f"Transition: {trans.get('title', trans.get('display', region))}",
                    "filename": None,
                    "text": "",
                    "is_transition": True,
                    "duration_seconds": float(trans.get("durationSeconds", 2.0))
                })

        sequence.append({
            "id": s_id,
            "title": f"Story {i}: {headline}",
            "filename": f"s{i}_{s_id}.mp3",
            "text": script,
            "is_transition": False
        })

    # 3. Headlines Recap
    recap = data.get("recap", {})
    sequence.append({
        "id": "recap",
        "title": "Headlines Recap: Today's Critical Developments",
        "filename": "s_recap.mp3",
        "text": recap.get("script", ""),
        "is_transition": False
    })

    # 4. Market Snapshot
    market = data.get("marketSnapshot", {})
    sequence.append({
        "id": "market_snapshot",
        "title": "AI Market Snapshot",
        "filename": "s_market_snapshot.mp3",
        "text": market.get("script", ""),
        "is_transition": False
    })

    # 5. Outro
    outro = data.get("outro", {})
    sequence.append({
        "id": "outro",
        "title": "Outro: Subscribe & Daily Bureaus",
        "filename": "s_outro.mp3",
        "text": outro.get("script", ""),
        "is_transition": False
    })

    print(f"[*] Processing {len(sequence)} broadcast sequence elements...")
    timings = {}
    total_time = 0.0
    chapters = []

    for item in sequence:
        seg_id = item["id"]
        title = item["title"]

        if item["is_transition"]:
            scene_duration = item["duration_seconds"]
            frames = int(round(scene_duration * 30))
            timings[seg_id] = {
                "audioFile": "",
                "audioDurationSeconds": 0.0,
                "sceneDurationSeconds": round(scene_duration, 2),
                "durationInFrames": frames,
                "title": title
            }
            total_time += scene_duration
            print(f" -> Transition: {seg_id} -> {scene_duration:.2f}s ({frames} frames)")
            continue

        filename = item["filename"]
        text = item["text"]
        out_file = os.path.join("public", "audio", "aibrief", filename)

        # Add chapter timestamp
        timestamp_str = format_timestamp(total_time)
        chapters.append(f"{timestamp_str} {title}")

        print(f" -> Synthesizing: {filename}...")
        max_retries = 4
        for attempt in range(max_retries):
            try:
                communicate = edge_tts.Communicate(text, VOICE, rate=RATE, volume=VOLUME)
                await communicate.save(out_file)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"    [!] Retry {attempt + 1}/{max_retries} for {filename} after error: {e}")
                    await asyncio.sleep(2.0)
                else:
                    raise e

        raw_duration = get_audio_duration(out_file)
        # Add 1.2s broadcast breathing room
        scene_duration = max(raw_duration + 1.2, 4.0)
        frames = int(round(scene_duration * 30))

        timings[seg_id] = {
            "audioFile": f"audio/aibrief/{filename}",
            "audioDurationSeconds": round(raw_duration, 2),
            "sceneDurationSeconds": round(scene_duration, 2),
            "durationInFrames": frames,
            "title": title
        }

        total_time += scene_duration
        print(f"    [OK] {filename} duration: {raw_duration:.2f}s -> Scene: {scene_duration:.2f}s ({frames} frames)")

    # Ensure all configured transitions are present in timings
    for trans in data.get("transitions", []):
        t_id = trans.get("id")
        if t_id and t_id not in timings:
            t_dur = float(trans.get("durationSeconds", 2.0))
            timings[t_id] = {
                "audioFile": "",
                "audioDurationSeconds": 0.0,
                "sceneDurationSeconds": t_dur,
                "durationInFrames": int(round(t_dur * 30)),
                "title": f"Transition: {trans.get('title', t_id)}"
            }

    # Save timings to src/aibrief/data/timings.json
    with open("src/aibrief/data/timings.json", "w", encoding="utf-8") as f:
        json.dump(timings, f, indent=2)
    print(f"[+] Timings saved to src/aibrief/data/timings.json (Total video length: {format_timestamp(total_time)} / {int(total_time * 30)} frames)")

    # Generate YouTube metadata
    formatted_date = data.get("formattedDate", data.get("date", "Today"))
    yt_meta = data.get("youtubeMetadata", {})
    yt_title = yt_meta.get("title", f"SanMitra AI News Wire | {formatted_date}")
    
    desc_lines = [
        yt_meta.get("descriptionIntro", f"Daily institutional-grade AI intelligence from the SanMitra Newsroom."),
        "",
        "⏰ TIMESTAMPS / CHAPTERS:",
    ]
    for ch in chapters:
        desc_lines.append(ch)

    desc_lines.append("")
    desc_lines.append("📰 STORIES COVERED & OFFICIAL SOURCES:")
    for s in stories:
        desc_lines.append(f"• {s.get('headline', '')}")
        desc_lines.append(f"  Source ({s.get('source', '')}): {s.get('sourceUrl', '')}")
        if s.get("whyThisMatters"):
            desc_lines.append(f"  Impact: {s.get('whyThisMatters')}")
    
    desc_lines.append("")
    desc_lines.append("ABOUT SANMITRA AI NEWS WIRE:")
    desc_lines.append("SanMitra AI News Wire delivers institutional-grade global artificial intelligence intelligence covering multilateral policy, foundation models, semiconductor supply chains, and sovereign compute across World, USA, China, Asia, and India bureaus.")
    desc_lines.append("")
    
    tags = yt_meta.get("tags", ["AI", "Technology", "AIBrief", "DeepSeek", "OpenAI", "Anthropic", "Alibaba"])
    desc_lines.append(" ".join(f"#{t}" for t in tags))

    yt_content = f"TITLE:\n{yt_title}\n\nDESCRIPTION:\n" + "\n".join(desc_lines)
    with open("out/aibrief/youtube_metadata.txt", "w", encoding="utf-8") as f:
        f.write(yt_content)
    print("[+] YouTube metadata saved to out/aibrief/youtube_metadata.txt")

    # Generate LinkedIn Post
    li_lines = [
        f"SANMITRA AI NEWS WIRE — {formatted_date} 🌐",
        "",
        "Today's critical developments across frontier AI, global diplomacy, and sovereign silicon:",
        ""
    ]
    for s in stories:
        reg = s.get("region", "WORLD")
        head = s.get("headline", "")
        why = s.get("whyThisMatters", "")
        li_lines.append(f"🔹 [{reg}] {head}")
        if why:
            li_lines.append(f"💡 Why This Matters: {why}")
        li_lines.append(f"🔗 Source: {s.get('source', '')} - {s.get('sourceUrl', '')}")
        li_lines.append("")
    
    li_lines.append("💬 Discussion: Which AI policy or architecture shift will impact your organization most? Share your thoughts in today's YouTube comments.")
    li_lines.append("")
    li_lines.append("📺 Watch today's full 16:9 data briefing & subscribe:")
    li_lines.append("👉 https://www.youtube.com/@SanMitraTechSolutions?sub_confirmation=1")
    li_lines.append("")
    li_lines.append("#ArtificialIntelligence #DeepSeek #OpenAI #Anthropic #Alibaba #Semiconductors #Governance #SanMitra")
    
    with open("out/aibrief/linkedin_post.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(li_lines))
    print("[+] LinkedIn post saved to out/aibrief/linkedin_post.txt")

    # Generate Facebook Post
    fb_lines = [
        f"📢 SANMITRA AI NEWS WIRE | {formatted_date}",
        "Global Artificial Intelligence Intelligence Briefing 🌐",
        "",
        "Today's top institutional AI headlines:",
        ""
    ]
    for idx, s in enumerate(stories, 1):
        head = s.get("headline", "")
        why = s.get("whyThisMatters", "")
        fb_lines.append(f"📌 {idx}. {head}")
        if why:
            fb_lines.append(f"   👉 Impact: {why}")
        fb_lines.append("")
    
    fb_lines.append("💬 Join the conversation: Tell us your perspective on today's developments in the comments below!")
    fb_lines.append("")
    fb_lines.append("🔴 Watch the full institutional broadcast (1080p @ 30 FPS):")
    fb_lines.append("👉 https://www.youtube.com/@SanMitraTechSolutions?sub_confirmation=1")
    fb_lines.append("")
    fb_lines.append("🔔 Click above to watch and subscribe for daily AI wire briefings!")
    fb_lines.append("")
    fb_lines.append("#AI #ArtificialIntelligence #TechNews #OpenAI #Anthropic #Nvidia #Google #IndiaAI #SanMitra")

    with open("out/aibrief/facebook_post.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(fb_lines))
    print("[+] Facebook post saved to out/aibrief/facebook_post.txt")

    return timings, total_time

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "src/aibrief/data/active_episode.json"
    asyncio.run(generate_voiceover(path))
