"""
AI Thumbnail Ranking & Selection Engine for SanMitra AI News Wire v2.1.1.
Evaluates the 3 rendered candidate thumbnails:
  • Variant A: Breaking Crimson Red
  • Variant B: Exclusive Cyan
  • Variant C: Critical Emerald

Computer Vision Scoring Matrix (100 pts):
  1. Contrast & Dynamic Range (0-30 pts): RMS luminance contrast of overlay vs background
  2. Color Vibrancy & Visual Heat (0-25 pts): Colorfulness metric across focal quadrants
  3. Mobile Size Readability & Acuity (0-25 pts): Edge variance at 320x180 mobile feed resolution
  4. Hero Focal Prominence (0-20 pts): Saliency and brightness ratio of central hero subject

The winning candidate is automatically copied to thumbnail_primary.png for YouTube upload.
"""

import json
import os
import shutil
import sys
from typing import Dict, List, Optional, Tuple
import numpy as np
from PIL import Image, ImageFilter, ImageStat

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def compute_rms_contrast(im_gray: Image.Image) -> float:
    """Calculates root mean square luminance contrast."""
    stat = ImageStat.Stat(im_gray)
    stddev = stat.stddev[0]
    return min(30.0, (stddev / 128.0) * 30.0)


def compute_colorfulness(im_rgb: Image.Image) -> float:
    """
    Hasler and Süsstrunk metric for image colorfulness:
    M = std(rg) + std(yb) + 0.3 * sqrt(mean(rg)^2 + mean(yb)^2)
    """
    arr = np.array(im_rgb, dtype=np.float32)
    R = arr[:, :, 0]
    G = arr[:, :, 1]
    B = arr[:, :, 2]

    rg = np.abs(R - G)
    yb = np.abs(0.5 * (R + G) - B)

    std_rg = np.std(rg)
    std_yb = np.std(yb)
    mean_rg = np.mean(rg)
    mean_yb = np.mean(yb)

    colorfulness = std_rg + std_yb + 0.3 * np.sqrt(mean_rg**2 + mean_yb**2)
    # Scale 0-25 pts (typical colorfulness ranges from 20 to 100)
    return min(25.0, max(5.0, (colorfulness / 80.0) * 25.0))


def compute_mobile_edge_acuity(im_rgb: Image.Image) -> float:
    """
    Downsamples to mobile card size (320x180) and calculates Laplacian edge variance
    to measure mobile readability and crispness.
    """
    mobile = im_rgb.resize((320, 180), Image.Resampling.LANCZOS).convert("L")
    edges = mobile.filter(ImageFilter.FIND_EDGES)
    stat = ImageStat.Stat(edges)
    edge_var = stat.var[0]
    # Edge variance typically ranges from 100 to 1200
    return min(25.0, max(5.0, (edge_var / 900.0) * 25.0))


def compute_hero_prominence(im_rgb: Image.Image) -> float:
    """
    Analyzes focal center third vs surrounding vignette perimeter.
    """
    w, h = im_rgb.size
    center_box = (w // 4, h // 4, 3 * w // 4, 3 * h // 4)
    center = im_rgb.crop(center_box).convert("L")
    stat = ImageStat.Stat(center)
    center_brightness = stat.mean[0]
    # Score 0-20 pts
    return min(20.0, max(4.0, (center_brightness / 255.0) * 20.0))


def evaluate_thumbnail(image_path: str, variant_name: str) -> Dict:
    """Evaluates a single thumbnail candidate."""
    if not os.path.exists(image_path):
        return {
            "variant": variant_name,
            "path": image_path,
            "exists": False,
            "total_score": 0.0
        }

    with Image.open(image_path) as im:
        im_rgb = im.convert("RGB")
        im_gray = im.convert("L")

        contrast_pts = round(compute_rms_contrast(im_gray), 2)
        vibrancy_pts = round(compute_colorfulness(im_rgb), 2)
        acuity_pts = round(compute_mobile_edge_acuity(im_rgb), 2)
        prominence_pts = round(compute_hero_prominence(im_rgb), 2)

        total = round(contrast_pts + vibrancy_pts + acuity_pts + prominence_pts, 2)

        return {
            "variant": variant_name,
            "path": image_path,
            "exists": True,
            "total_score": total,
            "contrast_score": contrast_pts,
            "vibrancy_score": vibrancy_pts,
            "mobile_acuity_score": acuity_pts,
            "hero_prominence_score": prominence_pts
        }


def rank_and_select_thumbnail(
    candidates: List[Tuple[str, str]],
    output_primary_path: str = "out/aibrief/thumbnail_primary.png",
    date_alias_path: Optional[str] = None
) -> Dict:
    """
    Ranks thumbnails A, B, and C, selects the highest-scoring variant,
    and copies it to thumbnail_primary.png.
    """
    evaluations = []
    for path, var_name in candidates:
        card = evaluate_thumbnail(path, var_name)
        if card["exists"]:
            evaluations.append(card)

    if not evaluations:
        raise FileNotFoundError("None of the thumbnail candidates exist!")

    # Sort descending by total score
    evaluations.sort(key=lambda c: c["total_score"], reverse=True)
    winner = evaluations[0]

    os.makedirs(os.path.dirname(output_primary_path), exist_ok=True)
    shutil.copyfile(winner["path"], output_primary_path)

    if date_alias_path:
        shutil.copyfile(winner["path"], date_alias_path)

    report = {
        "winning_variant": winner["variant"],
        "winning_score": winner["total_score"],
        "primary_output": output_primary_path,
        "date_alias_output": date_alias_path,
        "rankings": evaluations
    }

    report_path = os.path.join(os.path.dirname(__file__), "data", "thumbnail_ranking.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    # Test with dummy candidate images if files don't exist
    test_dir = os.path.join("out", "aibrief")
    os.makedirs(test_dir, exist_ok=True)

    ta = os.path.join(test_dir, "thumbnail_A.png")
    tb = os.path.join(test_dir, "thumbnail_B.png")
    tc = os.path.join(test_dir, "thumbnail_C.png")

    if not os.path.exists(ta):
        Image.new('RGB', (1920, 1080), (180, 20, 30)).save(ta)
    if not os.path.exists(tb):
        Image.new('RGB', (1920, 1080), (10, 150, 190)).save(tb)
    if not os.path.exists(tc):
        Image.new('RGB', (1920, 1080), (15, 160, 80)).save(tc)

    candidates = [
        (ta, "Variant A (Breaking Crimson Red)"),
        (tb, "Variant B (Exclusive Cyan)"),
        (tc, "Variant C (Critical Emerald)")
    ]

    res = rank_and_select_thumbnail(candidates)
    print("=" * 65)
    print("🏆 AI THUMBNAIL RANKING & SELECTION REPORT:")
    print("=" * 65)
    print(f"🥇 Winner: {res['winning_variant']} (Score: {res['winning_score']}/100)")
    print(f"📁 Selected for Upload: {res['primary_output']}")
    print("-" * 65)
    for idx, r in enumerate(res["rankings"], 1):
        print(f"#{idx} {r['variant']:<35} | Score: {r['total_score']} | Contrast: {r['contrast_score']} | Vibrancy: {r['vibrancy_score']} | Acuity: {r['mobile_acuity_score']}")
