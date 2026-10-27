"""
Narration and character dialogue for an OfficeMitra Finance Insights episode.

    python generate_finance_episode_vo.py ep001

Reads src/finance/<ep>/script.json (scenes of [speaker, text] lines), voices each
line with Edge TTS, and writes public/audio/finance/<ep>/<scene>_<n>.mp3 plus
src/finance/<ep>/timings.json: for each scene its lines (speaker, text, audio,
start offset, seconds) and the scene length, which the Remotion composition uses.
"""

import asyncio
import json
import os
import subprocess
import sys

import edge_tts

# Speaker -> (display name, voice, rate, pitch)
VOICES = {
    "N": ("", "en-IN-PrabhatNeural", "+8%", "+0Hz"),
    "L": ("Lata", "en-IN-NeerjaExpressiveNeural", "+4%", "+0Hz"),
    "V": ("Vikram", "hi-IN-MadhurNeural", "+12%", "+4Hz"),
    "M": ("Mr. Mehta", "hi-IN-MadhurNeural", "-6%", "-10Hz"),
    "K": ("Kapoor", "en-IN-PrabhatNeural", "-2%", "-14Hz"),
}
GAP = 0.35  # between lines within a scene
TAIL = 0.4  # after the last line of a scene


def duration(path):
    out = subprocess.run(f'npx remotion ffprobe -v error -show_entries format=duration -of csv=p=0 "{path}"',
                         shell=True, capture_output=True, text=True).stdout.strip().splitlines()
    return float(out[-1])


async def main(ep):
    with open(os.path.join("src", "finance", ep, "script.json"), encoding="utf-8") as f:
        script = json.load(f)
    audio_dir = os.path.join("public", "audio", "finance", ep)
    os.makedirs(audio_dir, exist_ok=True)
    scenes = []
    total = 0.0
    for scene in script["scenes"]:
        t = 0.0
        lines = []
        for n, (speaker, text) in enumerate(scene["lines"]):
            name, voice, rate, pitch = VOICES[speaker]
            path = os.path.join(audio_dir, f"{scene['id']}_{n}.mp3")
            await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(path)
            secs = round(duration(path), 2)
            lines.append({"speaker": speaker, "name": name, "text": text,
                          "audio": f"audio/finance/{ep}/{scene['id']}_{n}.mp3", "start": round(t, 2), "seconds": secs})
            t += secs + GAP
        seconds = round(t - GAP + TAIL, 2)
        scenes.append({"id": scene["id"], "seconds": seconds, "lines": lines})
        total += seconds
        print(f"{scene['id']}: {seconds:5.1f}s  " + " | ".join(l["speaker"] for l in lines), flush=True)
    with open(os.path.join("src", "finance", ep, "timings.json"), "w", encoding="utf-8") as f:
        json.dump({"episode": ep, "title": script["title"], "scenes": scenes}, f, indent=1, ensure_ascii=False)
    print(f"Total {total / 60:.1f} min")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "ep001"))
