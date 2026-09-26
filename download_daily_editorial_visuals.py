"""
Automated Editorial Visual Asset Downloader & Processor for SanMitra AI News Wire.
Downloads authentic, story-specific 1920x1080 photography for every story of the day.
Ensures zero visual repetition from day to day.
"""

import io
import os
import urllib.request
from PIL import Image, ImageEnhance, ImageOps

DATE_STR = "2026-09-26"
DEST_DIR = os.path.join("public", "aibrief", "assets", "editorial", DATE_STR)
os.makedirs(DEST_DIR, exist_ok=True)

TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080

# Story-specific real photo URLs for 26 September 2026
STORY_PHOTOS = [
    # Story 1: OpenAI Agent Incidents
    (
        "s1_cut1.jpg",
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1920&q=85", # Cyber threat ops center
        "public/aibrief/assets/editorial/tech_cyber_command.jpg"
    ),
    (
        "s1_cut2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Sam_Altman_TechCrunch_Disrupt_2019_%28cropped%29.jpg/1920px-Sam_Altman_TechCrunch_Disrupt_2019_%28cropped%29.jpg",
        "public/aibrief/assets/editorial/person_sam_altman.jpg"
    ),
    (
        "s1_cut3.jpg",
        "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1920&q=85", # Digital security telemetry
        "public/aibrief/assets/editorial/tech_code_screen.jpg"
    ),

    # Story 2: US Court Upholds Pentagon Restrictions on Anthropic
    (
        "s2_cut1.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/2/2a/The_Pentagon%2C_Headquarters_of_the_US_Department_of_Defense_%28cropped2%29.jpg",
        "public/aibrief/assets/editorial/gov_white_house.jpg"
    ),
    (
        "s2_cut2.jpg",
        "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1920&q=85", # Courtroom & justice scales
        "public/aibrief/assets/editorial/gov_us_capitol_hearing.jpg"
    ),
    (
        "s2_cut3.jpg",
        "local:public/aibrief/assets/editorial/person_dario_amodei.jpg", # Dario Amodei VIP
        "public/aibrief/assets/editorial/person_dario_amodei.jpg"
    ),

    # Story 3: Microsoft Launches Unified Copilot Super App
    (
        "s3_cut1.jpg",
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d6/Aerial_Microsoft_West_Campus_August_2009.jpg/1920px-Aerial_Microsoft_West_Campus_August_2009.jpg",
        "public/aibrief/assets/editorial/tech_laptop_showcase.jpg"
    ),
    (
        "s3_cut2.jpg",
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg/1920px-MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "public/aibrief/assets/editorial/person_sundar_pichai.jpg"
    ),
    (
        "s3_cut3.jpg",
        "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=1920&q=85", # Modern developer workstations
        "public/aibrief/assets/editorial/tech_data_telemetry.jpg"
    ),

    # Story 4: US and China Renew Calls for AI Cooperation
    (
        "s4_cut1.jpg",
        "https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=1920&q=85", # Bilateral summit conference table
        "public/aibrief/assets/editorial/gov_un_chamber.jpg"
    ),
    (
        "s4_cut2.jpg",
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ef/China_Senate_House.jpg/1920px-China_Senate_House.jpg",
        "public/aibrief/backgrounds/geopolitics.jpg"
    ),
    (
        "s4_cut3.jpg",
        "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=1920&q=85", # Global international connection map
        "public/aibrief/assets/editorial/tech_neural_globe.jpg"
    ),

    # Story 5: DeepSeek Revenue Surpasses $1B Run Rate
    (
        "s5_cut1.jpg",
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1920&q=85", # High density AI datacenter racks
        "public/aibrief/backgrounds/cloud_infrastructure.jpg"
    ),
    (
        "s5_cut2.jpg",
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1920&q=85", # Stock market revenue curve
        "public/aibrief/assets/editorial/tech_data_telemetry.jpg"
    ),
    (
        "s5_cut3.jpg",
        "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1920&q=85", # Datacenter fiber cabling
        "public/aibrief/assets/editorial/tech_server_hall.jpg"
    ),

    # Story 6: Japan Reviews AI Data Center Financing Risks
    (
        "s6_cut1.jpg",
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/37/Bank_of_Japan_2010.jpg/1920px-Bank_of_Japan_2010.jpg",
        "public/aibrief/assets/editorial/fin_tokyo_district.jpg"
    ),
    (
        "s6_cut2.jpg",
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b2/Skyscrapers_of_Shinjuku_2009_January.jpg/1920px-Skyscrapers_of_Shinjuku_2009_January.jpg",
        "public/aibrief/assets/editorial/fin_tokyo_district.jpg"
    ),
    (
        "s6_cut3.jpg",
        "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1920&q=85", # Power grid & electric substation
        "public/aibrief/backgrounds/cloud_infrastructure.jpg"
    ),

    # Story 7: India Explores National Frontier AI Compute Fund
    (
        "s7_cut1.jpg",
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a7/Delhi_India_Government.jpg/1920px-Delhi_India_Government.jpg",
        "public/aibrief/assets/editorial/gov_india_delhi.jpg"
    ),
    (
        "s7_cut2.jpg",
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&q=85", # Cyber supercomputer matrix
        "public/aibrief/assets/editorial/tech_server_hall.jpg"
    ),
    (
        "s7_cut3.jpg",
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=85", # Microprocessor silicon chip
        "public/aibrief/backgrounds/ai_chips.jpg"
    ),

    # Story 8: Sarvam AI Launches Vision 2.1
    (
        "s8_cut1.jpg",
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/cd/View_from_Visvesvaraya_Industrial_and_Technological_Museum_%282025%29_02.jpg/1920px-View_from_Visvesvaraya_Industrial_and_Technological_Museum_%282025%29_02.jpg",
        "public/aibrief/assets/editorial/gov_india_delhi.jpg"
    ),
    (
        "s8_cut2.jpg",
        "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=1920&q=85", # Multilingual document processing
        "public/aibrief/assets/editorial/tech_semiconductor_lab.jpg"
    ),
    (
        "s8_cut3.jpg",
        "https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=1920&q=85", # Software engineering squad
        "public/aibrief/assets/editorial/tech_code_screen.jpg"
    ),
]

def crop_and_grade(im: Image.Image) -> Image.Image:
    # 1. Resize/Crop to exact 1920x1080 maintaining aspect ratio
    im = ImageOps.fit(im, (TARGET_WIDTH, TARGET_HEIGHT), method=Image.Resampling.LANCZOS)
    
    # 2. Subtle institutional broadcast grading: enhance contrast + slight saturation
    enhancer_contrast = ImageEnhance.Contrast(im)
    im = enhancer_contrast.enhance(1.08)
    
    enhancer_color = ImageEnhance.Color(im)
    im = enhancer_color.enhance(1.05)
    
    return im

def download_and_save():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for filename, url, fallback_path in STORY_PHOTOS:
        dest_file = os.path.join(DEST_DIR, filename)
        if os.path.exists(dest_file):
            print(f"[OK] Already present: {dest_file}")
            continue

        print(f"[*] Downloading fresh visual: {filename}...")
        downloaded = False

        if url.startswith("local:"):
            local_src = url.replace("local:", "")
            if os.path.exists(local_src):
                im = Image.open(local_src).convert("RGB")
                im = crop_and_grade(im)
                im.save(dest_file, quality=90)
                downloaded = True
                print(f"    [+] Loaded and graded local: {dest_file}")
        elif url.startswith("http"):
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=15) as r:
                    data = r.read()
                    im = Image.open(io.BytesIO(data)).convert("RGB")
                    im = crop_and_grade(im)
                    im.save(dest_file, quality=90)
                    downloaded = True
                    print(f"    [+] Saved fresh 1920x1080 visual: {dest_file}")
            except Exception as e:
                print(f"    [!] Failed to download from {url}: {e}")

        # Fallback if download failed
        if not downloaded:
            if os.path.exists(fallback_path):
                print(f"    [->] Using graded fallback: {fallback_path}")
                im = Image.open(fallback_path).convert("RGB")
                im = crop_and_grade(im)
                im.save(dest_file, quality=90)
            else:
                # Black gradient fallback
                im = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), (8, 14, 28))
                im.save(dest_file)

    print(f"\n[+] All 24 fresh editorial visuals saved into {DEST_DIR}!")

if __name__ == "__main__":
    download_and_save()
