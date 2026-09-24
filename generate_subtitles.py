import json
import os
import re
import sys

def format_srt_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def split_into_phrases(text: str, max_words: int = 7) -> list:
    # Split text into sentences first
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    phrases = []
    
    for sent in sentences:
        words = sent.split()
        if not words:
            continue
        # Chunk sentence into groups of ~max_words
        for i in range(0, len(words), max_words):
            chunk = " ".join(words[i:i + max_words])
            if chunk:
                phrases.append(chunk)
    return phrases

def generate_subtitles(data_path="src/aibrief/data/active_episode.json", timings_path="src/aibrief/data/timings.json"):
    print("[*] Generating timed subtitles and SRT captions...")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    with open(timings_path, "r", encoding="utf-8") as f:
        timings = json.load(f)

    stories = data.get("stories", [])
    
    # Ordered scenes matching master broadcast sequence:
    # 1. intro
    # 2. stories[0..2]
    # 3. transition_safety (silent 2.0s)
    # 4. stories[3..4]
    # 5. transition_india (silent 2.0s)
    # 6. stories[5]
    # 7. recap
    # 8. market_snapshot
    # 9. outro
    scenes = []
    scenes.append(("intro", data.get("intro", {}).get("script", "")))

    # Block 1: Stories 1, 2, 3
    for s in stories[:3]:
        scenes.append((s.get("id"), s.get("script", "")))

    # Transition 1 (silent 2.0s)
    scenes.append(("transition_safety", ""))

    # Block 2: Stories 4, 5
    for s in stories[3:5]:
        scenes.append((s.get("id"), s.get("script", "")))

    # Transition 2 (silent 2.0s)
    scenes.append(("transition_india", ""))

    # Block 3: Story 6
    for s in stories[5:6]:
        scenes.append((s.get("id"), s.get("script", "")))

    # Recap
    recap = data.get("recap", {})
    recap_script = recap.get(
        "script",
        "To recap today's headlines: DeepSeek briefs the United Nations Security Council; OpenAI and Anthropic launch GPT-6 Sol, Luna, and Claude Opus 5.5; OpenEvidence expands clinical AI to one hundred nations; Tom Siegel champions youth safety standards; Alibaba reveals the Zhenwu V-900 chip; and Maharashtra formalizes public-sector AI governance."
    )
    scenes.append(("recap", recap_script))

    # Market Snapshot
    market = data.get("marketSnapshot", {})
    market_script = market.get(
        "script",
        "Turning to the SanMitra AI Market Snapshot: OpenAI and Anthropic intensify foundation model competition with lower-cost enterprise tiers. Google expands Gemini infrastructure, Meta refines agentic safety permissions, DeepSeek prepares for UN multilateral briefings, Alibaba scales sovereign Zhenwu silicon, and Microsoft deepens hyperscale datacenter investments."
    )
    scenes.append(("market_snapshot", market_script))

    # Outro
    scenes.append(("outro", data.get("outro", {}).get("script", "")))

    srt_entries = []
    remotion_captions = []
    
    current_time = 0.0
    caption_index = 1

    for scene_id, script in scenes:
        timing = timings.get(scene_id, {})
        audio_dur = timing.get("audioDurationSeconds", 0.0)
        scene_dur = timing.get("sceneDurationSeconds", 2.0)
        
        if not script or audio_dur == 0.0:
            current_time += scene_dur
            continue

        phrases = split_into_phrases(script, max_words=7)
        if not phrases:
            current_time += scene_dur
            continue

        # Distribute the audio duration proportionally across words
        total_words = sum(len(p.split()) for p in phrases)
        if total_words == 0:
            total_words = 1
        
        time_cursor = current_time
        for p in phrases:
            word_count = len(p.split())
            phrase_dur = (word_count / total_words) * audio_dur
            
            start_s = time_cursor
            end_s = min(time_cursor + phrase_dur, current_time + scene_dur)
            
            start_frame = int(round(start_s * 30))
            end_frame = int(round(end_s * 30))

            # SRT entry
            srt_start = format_srt_timestamp(start_s)
            srt_end = format_srt_timestamp(end_s)
            srt_entries.append(f"{caption_index}\n{srt_start} --> {srt_end}\n{p}\n")

            # Remotion JSON entry
            remotion_captions.append({
                "index": caption_index,
                "sceneId": scene_id,
                "startFrame": start_frame,
                "endFrame": end_frame,
                "startSeconds": round(start_s, 2),
                "endSeconds": round(end_s, 2),
                "text": p
            })

            caption_index += 1
            time_cursor += phrase_dur
        
        current_time += scene_dur

    # Write SRT file
    date_str = data.get("date", "latest")
    os.makedirs("out/aibrief", exist_ok=True)
    srt_file = f"out/aibrief/captions_{date_str}.srt"
    with open(srt_file, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))
    # Also copy as default captions.srt
    with open("out/aibrief/captions.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))
    print(f"[+] SRT subtitles generated: {srt_file} ({len(remotion_captions)} cues)")

    # Write Remotion JSON file
    remotion_captions_file = "src/aibrief/data/captions.json"
    with open(remotion_captions_file, "w", encoding="utf-8") as f:
        json.dump(remotion_captions, f, indent=2)
    print(f"[+] Remotion burn-in captions saved to: {remotion_captions_file}")

    return srt_file, remotion_captions_file

if __name__ == "__main__":
    generate_subtitles()
