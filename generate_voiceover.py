import asyncio
import edge_tts
import os

VOICE = "en-US-ChristopherNeural"

SEGMENTS = [
    ("vo_1.mp3", "You've been working for hours in pure focus... until an unexpected crash occurs."),
    ("vo_2.mp3", "Everything you just built vanishes into thin air. Unsaved progress lost forever."),
    ("vo_3.mp3", "Local storage shouldn't mean living on the edge of disaster."),
    ("vo_4.mp3", "Never hit save again. Introducing Instant Cloud Syncing for mobile and desktop."),
    ("vo_5.mp3", "Every keystroke and edit is mirrored silently to encrypted cloud storage in sub-milliseconds."),
    ("vo_6.mp3", "Seamlessly accessible across your phone, tablet, and laptop without missing a beat."),
    ("vo_7.mp3", "Your ideas deserve total security. Stop gambling with your critical data."),
    ("vo_8.mp3", "Download now and secure your data workflow with pure peace of mind."),
]

async def generate():
    os.makedirs("public/audio", exist_ok=True)
    for filename, text in SEGMENTS:
        output_path = os.path.join("public", "audio", filename)
        communicate = edge_tts.Communicate(text, VOICE, rate="+3%")
        await communicate.save(output_path)
        size = os.path.getsize(output_path)
        print(f"Generated {output_path} ({size} bytes)")

if __name__ == "__main__":
    asyncio.run(generate())
