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

    # Segments list: (id, title, filename, text)
    segments = []
    
    # 1. Intro
    intro = data.get("intro", {})
    segments.append((
        "intro",
        "Intro: Today's Biggest AI Developments",
        "s0_intro.mp3",
        intro.get("script", "Today on SanMitra AI News Wire: DeepSeek heads to the United Nations Security Council, OpenAI and Anthropic launch major new models, Alibaba unveils a powerful new AI chip, and India expands AI governance in higher education. From the SanMitra Newsroom, here are today's biggest AI developments.")
    ))

    # 2. Stories
    for i, story in enumerate(stories, 1):
        s_id = story.get("id", f"story_{i}")
        headline = story.get("headline", "")
        script = story.get("script", "")
        segments.append((
            s_id,
            f"Story {i}: {headline}",
            f"s{i}_{s_id}.mp3",
            script
        ))

    # 3. Headlines Recap
    recap = data.get("recap", {})
    recap_script = recap.get(
        "script",
        "To recap today's headlines: DeepSeek briefs the United Nations Security Council; OpenAI and Anthropic launch GPT-6 Sol, Luna, and Claude Opus 5.5; OpenEvidence expands clinical AI to one hundred nations; Tom Siegel champions youth safety standards; Alibaba reveals the Zhenwu V-900 chip; and Maharashtra formalizes public-sector AI governance."
    )
    segments.append((
        "recap",
        "Headlines Recap: Today's Critical Developments",
        "s_recap.mp3",
        recap_script
    ))

    # 4. Market Snapshot
    market = data.get("marketSnapshot", {})
    market_script = market.get(
        "script",
        "Turning to the SanMitra AI Market Snapshot: OpenAI and Anthropic intensify foundation model competition with lower-cost enterprise tiers. Google expands Gemini infrastructure, Meta refines agentic safety permissions, DeepSeek prepares for UN multilateral briefings, Alibaba scales sovereign Zhenwu silicon, and Microsoft deepens hyperscale datacenter investments."
    )
    segments.append((
        "market_snapshot",
        "AI Market Snapshot: 7 Strategic Leaders",
        "s_market_snapshot.mp3",
        market_script
    ))

    # 5. Outro
    outro = data.get("outro", {})
    segments.append((
        "outro",
        "Outro: Subscribe & Daily Bureaus",
        "s_outro.mp3",
        outro.get("script", "Those were today's critical developments across global artificial intelligence. From our bureaus covering World, USA, China, Asia, and India, thank you for watching SanMitra AI News Wire. Subscribe now for daily institutional AI intelligence.")
    ))

    print(f"[*] Generating {len(segments)} voiceover audio clips with Microsoft Edge TTS '{VOICE}' (Rate: {RATE})...")
    timings = {}
    total_time = 0.0
    chapters = []

    for seg_id, title, filename, text in segments:
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

    # Insert Section transitions (2.0s = 60 frames each)
    timings["transition_safety"] = {
        "audioFile": "",
        "audioDurationSeconds": 0.0,
        "sceneDurationSeconds": 2.0,
        "durationInFrames": 60,
        "title": "Transition: NEXT: AI SAFETY & RESPONSIBLE USE"
    }
    total_time += 2.0

    timings["transition_india"] = {
        "audioFile": "",
        "audioDurationSeconds": 0.0,
        "sceneDurationSeconds": 2.0,
        "durationInFrames": 60,
        "title": "Transition: NEXT: INDIA"
    }
    total_time += 2.0

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
    
    li_lines.append("Watch today's full 16:9 data briefing on YouTube: https://www.youtube.com/@SanMitraTechSolutions")
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
    
    fb_lines.append("🔴 Watch the full institutional broadcast (1080p @ 30 FPS):")
    fb_lines.append("👉 https://www.youtube.com/@SanMitraTechSolutions")
    fb_lines.append("")
    fb_lines.append("🔔 Subscribe to SanMitra Tech Solutions for daily AI intelligence!")
    fb_lines.append("")
    fb_lines.append("#AI #ArtificialIntelligence #TechNews #OpenAI #Anthropic #Nvidia #Google #IndiaAI #SanMitra")

    with open("out/aibrief/facebook_post.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(fb_lines))
    print("[+] Facebook post saved to out/aibrief/facebook_post.txt")

    return timings, total_time

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "src/aibrief/data/active_episode.json"
    asyncio.run(generate_voiceover(path))
