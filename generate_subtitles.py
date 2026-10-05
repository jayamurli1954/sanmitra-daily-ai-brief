"""
Automated Broadcast Subtitles & Word-Level Timestamp Engine.
Uses OpenAI's faster-whisper (CTranslate2) for millisecond-accurate word boundaries:
  - Generates timed SRT subtitles (out/aibrief/captions_YYYY-MM-DD.srt)
  - Generates phrased lower-third Remotion burn-in captions (src/aibrief/data/captions.json)
  - Generates word-level timestamps JSON for kinetic 'Hormozi-style' pop-ups (src/aibrief/data/word_timestamps.json)
"""

import json
import os
import re
import sys

# Cache model instance globally
_WHISPER_MODEL = None


def get_whisper_model():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        try:
            from faster_whisper import WhisperModel
            # 'tiny.en' or 'base.en' on CPU with int8 quantization is ultra-fast (<2 sec per clip)
            _WHISPER_MODEL = WhisperModel("base.en", device="cpu", compute_type="int8")
        except Exception as e:
            print(f"[!] Warning loading faster-whisper: {e}")
            _WHISPER_MODEL = False
    return _WHISPER_MODEL


def clean_subtitle_text(text: str) -> str:
    """Normalizes transcribed tokens for on-screen broadcast presentation."""
    if not text:
        return ""
    # 1. Normalize TTS spelled-out A.I. to AI: "A .I.", "A. I.", "A.I.", "A.I" -> "AI"
    text = re.sub(r'\bA\s*\.\s*I\.?\b', 'AI', text)
    # 2. Fix SanMitra proper noun spacing: "San Mitra" -> "SanMitra"
    text = re.sub(r'\bSan\s+Mitra\b', 'SanMitra', text, flags=re.IGNORECASE)
    # 3. Clean multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def format_srt_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def transcribe_audio_words(audio_file_path: str, offset_seconds: float = 0.0) -> list:
    """
    Transcribes an audio file and returns a list of words with absolute timeline timestamps.
    Returns: [{'word': str, 'start': float, 'end': float, 'startFrame': int, 'endFrame': int}, ...]
    """
    if not os.path.exists(audio_file_path):
        return []

    model = get_whisper_model()
    if not model:
        return []

    try:
        segments, _ = model.transcribe(
            audio_file_path,
            word_timestamps=True,
            language="en",
            initial_prompt="SanMitra AI News Wire, SanMitra, AI, LLM, OpenAI, Anthropic, DeepSeek, Google Cloud, Nvidia, AMD"
        )
        words_out = []
        for seg in segments:
            if not seg.words:
                continue
            for w in seg.words:
                w_text = clean_subtitle_text(w.word.strip())
                if not w_text:
                    continue
                start_abs = offset_seconds + w.start
                end_abs = offset_seconds + w.end
                words_out.append({
                    "word": w_text,
                    "start": round(start_abs, 3),
                    "end": round(end_abs, 3),
                    "startFrame": int(round(start_abs * 30)),
                    "endFrame": int(round(end_abs * 30))
                })
        return words_out
    except Exception as e:
        print(f"[!] Whisper transcription failed for {audio_file_path}: {e}")
        return []


def generate_subtitles(data_path="src/aibrief/data/active_episode.json", timings_path="src/aibrief/data/timings.json"):
    print("[*] Generating timed subtitles and word-level captions with faster-whisper...")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(timings_path, "r", encoding="utf-8") as f:
        timings = json.load(f)

    stories = data.get("stories", [])
    transitions = {t.get("region"): t for t in data.get("transitions", [])}

    # Ordered broadcast scenes
    scenes = [("intro", data.get("intro", {}).get("script", ""))]

    for i, s in enumerate(stories, 1):
        region = s.get("region", "")
        if i > 1 and region != stories[i - 2].get("region"):
            if region in transitions:
                trans = transitions[region]
                scenes.append((trans.get("id"), ""))
        scenes.append((s.get("id"), s.get("script", "")))

    scenes.append(("recap", data.get("recap", {}).get("script", "")))
    scenes.append(("market_snapshot", data.get("marketSnapshot", {}).get("script", "")))
    scenes.append(("outro", data.get("outro", {}).get("script", "")))

    srt_entries = []
    remotion_captions = []
    all_word_timestamps = []

    current_time = 0.0
    caption_index = 1

    for scene_id, script in scenes:
        timing = timings.get(scene_id, {})
        audio_dur = timing.get("audioDurationSeconds", 0.0)
        scene_dur = timing.get("sceneDurationSeconds", 2.0)
        audio_rel_path = timing.get("audioFile", "")
        audio_full_path = os.path.join("public", audio_rel_path) if audio_rel_path else ""

        if not script or audio_dur == 0.0:
            current_time += scene_dur
            continue

        # 1. Attempt word-level transcription via faster-whisper
        words = []
        if audio_full_path and os.path.exists(audio_full_path):
            words = transcribe_audio_words(audio_full_path, offset_seconds=current_time)

        # 2. If faster-whisper extracted words, build high-precision phrases
        if words:
            for w in words:
                w["sceneId"] = scene_id
                all_word_timestamps.append(w)

            # Chunk words into natural 5-7 word phrases for lower-third display
            phrase_size = 6
            for idx_w in range(0, len(words), phrase_size):
                chunk = words[idx_w:idx_w + phrase_size]
                p_text = clean_subtitle_text(" ".join(item["word"] for item in chunk))
                p_start = chunk[0]["start"]
                p_end = chunk[-1]["end"]

                srt_start = format_srt_timestamp(p_start)
                srt_end = format_srt_timestamp(p_end)
                srt_entries.append(f"{caption_index}\n{srt_start} --> {srt_end}\n{p_text}\n")

                remotion_captions.append({
                    "index": caption_index,
                    "sceneId": scene_id,
                    "startFrame": int(round(p_start * 30)),
                    "endFrame": int(round(p_end * 30)),
                    "startSeconds": p_start,
                    "endSeconds": p_end,
                    "text": p_text
                })
                caption_index += 1

        else:
            # Fallback to character-length estimation
            raw_sentences = re.split(r'(?<=[.!?])\s+', script.strip())
            phrases = []
            for sent in raw_sentences:
                swords = sent.split()
                for i in range(0, len(swords), 6):
                    c = clean_subtitle_text(" ".join(swords[i:i + 6]))
                    if c:
                        phrases.append(c)

            total_words = max(1, sum(len(p.split()) for p in phrases))
            time_cursor = current_time
            for p in phrases:
                w_count = len(p.split())
                p_dur = (w_count / total_words) * audio_dur
                start_s = time_cursor
                end_s = min(time_cursor + p_dur, current_time + scene_dur)

                srt_start = format_srt_timestamp(start_s)
                srt_end = format_srt_timestamp(end_s)
                srt_entries.append(f"{caption_index}\n{srt_start} --> {srt_end}\n{p}\n")

                remotion_captions.append({
                    "index": caption_index,
                    "sceneId": scene_id,
                    "startFrame": int(round(start_s * 30)),
                    "endFrame": int(round(end_s * 30)),
                    "startSeconds": round(start_s, 2),
                    "endSeconds": round(end_s, 2),
                    "text": p
                })
                caption_index += 1
                time_cursor += p_dur

        current_time += scene_dur

    # Write SRT file
    date_str = data.get("date", "latest")
    os.makedirs("out/aibrief", exist_ok=True)
    srt_file = f"out/aibrief/captions_{date_str}.srt"
    with open(srt_file, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))
    with open("out/aibrief/captions.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))
    print(f"[+] SRT subtitles generated: {srt_file} ({len(remotion_captions)} cues)")

    # Write Remotion JSON file
    remotion_captions_file = "src/aibrief/data/captions.json"
    with open(remotion_captions_file, "w", encoding="utf-8") as f:
        json.dump(remotion_captions, f, indent=2)
    print(f"[+] Remotion burn-in captions saved to: {remotion_captions_file}")

    # Write word-level timestamps JSON for kinetic pop-ups (Shorts / Reels)
    words_file = "src/aibrief/data/word_timestamps.json"
    with open(words_file, "w", encoding="utf-8") as f:
        json.dump(all_word_timestamps, f, indent=2)
    print(f"[+] Word-level kinetic timestamps saved: {words_file} ({len(all_word_timestamps)} words)")

    return srt_file, remotion_captions_file, words_file


if __name__ == "__main__":
    generate_subtitles()
