import asyncio
import edge_tts
import os

VOICE = "en-US-ChristopherNeural"

SEGMENTS = [
    ("legalmitra_s1.mp3", "Every missed deadline, misplaced brief, and wasted research hour costs your practice time and money.", "+4%"),
    ("legalmitra_s2.mp3", "Meet LegalMitra. Not another AI chatbot, but a professional intelligence workspace with instant BNS, BNSS, and BSA crosswalk.", "+5%"),
    ("legalmitra_s3.mp3", "Find relevant case law in minutes. Manage every matter in one place, and never miss a deadline—while your client data stays strictly private.", "+4%"),
    ("legalmitra_s4.mp3", "Research smarter. Manage better. Practice confidently. Visit legalmitra.sanmitratech.in and start free today.", "+4%"),
]

async def generate():
    os.makedirs("public/audio", exist_ok=True)
    for filename, text, rate in SEGMENTS:
        output_path = os.path.join("public", "audio", filename)
        communicate = edge_tts.Communicate(text, VOICE, rate=rate)
        await communicate.save(output_path)
        print(f"Generated {output_path}")

if __name__ == "__main__":
    asyncio.run(generate())
