import asyncio
import edge_tts
import os

# Confident, professional, authoritative tone suitable for CAs and CFOs
VOICE = "en-US-ChristopherNeural"

# Scene audio segments
SEGMENTS = [
    (
        "om_s01_problem.mp3",
        "Modern CA firms face an impossible challenge. More compliance. More documents. Strict statutory deadlines. Yet the same limited time.",
        "+3%"
    ),
    (
        "om_s02_chaos.mp3",
        "Client data arrives from everywhere. But meaningful insight remains buried inside unstructured documents.",
        "+3%"
    ),
    (
        "om_s03_intro.mp3",
        "Introducing OfficeMitra. The AI-powered operating system designed specifically for modern Chartered Accountants.",
        "+3%"
    ),
    (
        "om_s04_portal.mp3",
        "Collect documents seamlessly. Automatically classify, organize, and prepare data for processing without chasing clients.",
        "+4%"
    ),
    (
        "om_s05_extraction.mp3",
        "Built-in AI understands every document. Extracting critical tax and transactional data without manual data entry.",
        "+3%"
    ),
    (
        "om_s06_ssdv.mp3",
        "At the core lies SSDV. An intelligent accounting engine that transforms raw extractions into structured, immutable double-entry records.",
        "+3%"
    ),
    (
        "om_s06a_factory.mp3",
        "Every document becomes structured accounting intelligence automatically. Real double-entry books. Reconciled before review.",
        "+4%"
    ),
    (
        "om_s07_review.mp3",
        "Review faster with AI-assisted risk detection and automated GSTR-2B ITC reconciliation. Complete traceability from source document to working paper.",
        "+3%"
    ),
    (
        "om_s08_workingpapers.mp3",
        "Generate audit-ready working papers automatically—complete with unbroken audit trails and source document verification.",
        "+4%"
    ),
    (
        "om_s09_advisory.mp3",
        "Move beyond compliance. Transform accounting data into high-value CFO advisory, ninety-day cash forecasts, and investor-ready board packs.",
        "+3%"
    ),
    (
        "om_s10_commandcenter.mp3",
        "Manage hundreds of clients through a single intelligent operating system. From a compliance-driven practice to an intelligence-driven firm.",
        "+3%"
    ),
    (
        "om_s11_finale.mp3",
        "OfficeMitra plus SSDV. Built for Chartered Accountants. Powered by Accounting Intelligence.",
        "+2%"
    ),
]

async def generate():
    output_dir = os.path.join("public", "audio", "officemitra")
    os.makedirs(output_dir, exist_ok=True)
    for filename, text, rate in SEGMENTS:
        output_path = os.path.join(output_dir, filename)
        communicate = edge_tts.Communicate(text, VOICE, rate=rate)
        await communicate.save(output_path)
        print(f"Generated {output_path}")

if __name__ == "__main__":
    asyncio.run(generate())
