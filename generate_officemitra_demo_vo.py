"""
Narration for the OfficeMitra product demo (composition OfficeMitraDemo16x9).

    python generate_officemitra_demo_vo.py

Every claim matches the shipped product (github.com/jayamurli1954/SSDV:
README and docs/CLIENT_MANUAL.md) and the screenshots in public/officemitra/.
Writes public/audio/officemitra_demo/<scene>.mp3 and
src/officemitra/demo/demoTimings.json (seconds per scene, audio + pause).
"""

import asyncio
import json
import os
import subprocess

import edge_tts

VOICE = "en-IN-PrabhatNeural"  # Indian English, for CA and SME audiences
RATE = "+12%"
PAUSE = 0.6  # seconds of breathing room after each line

SCENES = [
    ("s01_hook", "Your books show a profit. Your bank balance tells a different story. "
                 "And by the time the monthly MIS is ready, it is often too late to act."),
    ("s02_intro", "Meet OfficeMitra, your AI CFO dashboard, from SanMitra Tech Solutions."),
    ("s03_connect", "Connect the books you already keep: Tally, Zoho Books, Busy, or a journal export from any ERP. "
                    "OfficeMitra only reads your data. It never changes a voucher, and it runs on your own computer."),
    ("s04_ceo", "The CEO pack shows how the business is really doing: sales growth, margins, cash position and "
                "working capital, with plain notes on what needs attention."),
    ("s05_cfo", "The CFO pack goes deeper, with debtor days, inventory, the GST position, and a thirty, sixty and "
                "ninety day cash forecast, built from your open receivables and payables."),
    ("s06_aging", "See exactly where your cash is stuck: how long customers have owed you, who owes the most, "
                  "and which suppliers you depend on."),
    ("s07_board", "For the board, OfficeMitra raises red flags automatically, such as debtor days above your policy "
                  "or a negative cash position, and exports a meeting-ready pack as PDF or Excel."),
    ("s08_why", "When a number moves, OfficeMitra explains why, straight from the posted books. "
                "And with a local AI model, you can ask questions about your books in plain English."),
    ("s09_firms", "For CA practices, every client's books sit on one screen, so you can see who needs attention first."),
    ("s10_close", "OfficeMitra, by SanMitra Tech Solutions. Clear numbers. Early warnings. Better decisions. "
                  "Visit sanmitratech dot in."),
]

AUDIO_DIR = os.path.join("public", "audio", "officemitra_demo")
TIMINGS = os.path.join("src", "officemitra", "demo", "demoTimings.json")


def duration(path):
    out = subprocess.run(f'npx remotion ffprobe -v error -show_entries format=duration -of csv=p=0 "{path}"',
                         shell=True, capture_output=True, text=True).stdout.strip().splitlines()
    return float(out[-1])


async def main():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(TIMINGS), exist_ok=True)
    timings = []
    for scene_id, text in SCENES:
        path = os.path.join(AUDIO_DIR, f"{scene_id}.mp3")
        await edge_tts.Communicate(text, VOICE, rate=RATE).save(path)
        secs = round(duration(path) + PAUSE, 2)
        timings.append({"id": scene_id, "audio": f"audio/officemitra_demo/{scene_id}.mp3", "seconds": secs, "text": text})
        print(f"{scene_id}: {secs:.2f}s")
    with open(TIMINGS, "w", encoding="utf-8") as f:
        json.dump(timings, f, indent=2)
    print(f"Total {sum(t['seconds'] for t in timings):.1f}s -> {TIMINGS}")


if __name__ == "__main__":
    asyncio.run(main())
