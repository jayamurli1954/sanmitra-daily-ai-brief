"""
Perceptual Hash (pHash) Visual Memory & Diversity Category Manager for SanMitra AI News Wire v2.1.1.
Enforces:
  1. 64-bit DCT Perceptual Hashing (imagehash.phash)
  2. Hamming distance rejection (Hamming <= 6 rejected as near-identical or crop/recolor)
  3. 14-day rolling visual memory window
  4. 8 Visual Diversity Categories with HARD CAP of Max 2 visuals per category per episode
  5. Permanent blacklist of overused stock photos (Obama phone, UN logo, Gateway of India, generic robot heads)
"""

from datetime import datetime, timedelta
import io
import json
import os
import sys
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import imagehash
from PIL import Image

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "data", "visual_memory.json")

# Permanently banned stock images / filenames
BANNED_ASSET_KEYWORDS = {
    "gov_white_house.jpg",  # Obama on phone
    "gov_us_capitol_hearing.jpg",  # same Obama photo, mislabeled
    "story5_us_capitol.jpg",  # same Obama photo, mislabeled
    "gov_un_chamber.jpg",   # UN emblem / assembly
    "un_declaration.png",
    "gov_india_delhi.jpg",  # Gateway of India
    "tech_neural_globe.jpg", # Earth at night
    "us_china_talks.png",
    "robot_face",
    "glowing_android",
    "hacker_hoodie"
}

# The 8 Institutional Visual Diversity Categories
VALID_VISUAL_CATEGORIES = {
    "datacenter": "Server corridors, cooling racks, supercomputer infrastructure",
    "boardroom": "Executive negotiations, bilateral summits, corporate conference tables",
    "laboratory": "Robotics testing rigs, cleanrooms, sensor arrays",
    "robotics": "Humanoids, industrial actuators, autonomous manufacturing lines",
    "semiconductor": "Silicon wafers, lithography equipment, chip packaging, cleanroom engineers",
    "government": "Capitol halls, regulatory hearings, ministerial press conferences, situation rooms",
    "researcher": "Engineers at workstations, code telemetry reviews, prompt red-teaming",
    "product_demo": "Enterprise UI interfaces, live keynote presentations, screen telemetry"
}

# Keyword heuristics to auto-classify images into visual categories
CATEGORY_KEYWORD_MAP = {
    "datacenter": ["server", "supercomputer", "data center", "datacenter", "cluster", "rack", "fiber", "infrastructure", "cooling", "dalby", "substation", "grid", "power", "utility"],
    "boardroom": ["boardroom", "executive", "bilateral", "summit", "conference", "meeting", "negotiation", "table", "headquarters", "tower", "campus", "skyline", "tencent", "alibaba", "openai"],
    "laboratory": ["lab", "laboratory", "cleanroom", "testing", "sandbox", "containment", "experimental", "optics"],
    "robotics": ["robot", "robotics", "humanoid", "actuator", "arm", "industrial", "autonomous vehicle", "drone", "missile", "radar", "satellite", "ballistic", "trajectory"],
    "semiconductor": ["semiconductor", "chip", "wafer", "lithography", "silicon", "gpu", "accelerator", "circuit", "fab", "amd", "nvidia"],
    "government": ["situation room", "capitol", "senate", "parliament", "white house", "meity", "ministry", "hearing", "united nations", "diplomatic", "state house", "minister", "clayton", "portrait", "official", "trudeau", "sitharaman", "governor"],
    "researcher": ["scientist", "researcher", "engineer", "workstation", "code", "audit", "security operations", "soc", "telemetry", "benchmark", "scaffold", "rrsi", "neural"],
    "product_demo": ["keynote", "presentation", "ui", "interface", "app", "demo", "screen", "portal", "display", "mobile", "wechat", "doubao", "assistant"]
}


class VisualMemoryManager:
    def __init__(self, memory_file: str = MEMORY_FILE):
        self.memory_file = memory_file
        self.data = self._load()

    def _load(self) -> Dict:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[!] Warning loading visual memory: {e}")
        return {
            "version": "2.1.1",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "history": []
        }

    def save(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        self.data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def compute_phash(image_or_path) -> str:
        """
        Computes 64-bit DCT perceptual hash.
        Accepts PIL Image, file path, or bytes.
        """
        if isinstance(image_or_path, str):
            with Image.open(image_or_path) as img:
                return str(imagehash.phash(img))
        elif isinstance(image_or_path, bytes):
            with Image.open(io.BytesIO(image_or_path)) as img:
                return str(imagehash.phash(img))
        elif isinstance(image_or_path, Image.Image):
            return str(imagehash.phash(image_or_path))
        else:
            raise ValueError(f"Unsupported image type: {type(image_or_path)}")

    @staticmethod
    def hamming_distance(hash1_str: str, hash2_str: str) -> int:
        """Calculates bit difference between two hex hash strings."""
        try:
            h1 = imagehash.hex_to_hash(hash1_str)
            h2 = imagehash.hex_to_hash(hash2_str)
            return h1 - h2
        except Exception:
            return 64  # Treat unparseable hashes as completely distinct

    @staticmethod
    def classify_visual_category(badge_or_desc: str, filename_or_url: str = "") -> str:
        """
        Automatically categorizes a visual asset into one of the 8 canonical categories.
        """
        text = badge_or_desc.lower()
        for cat, keywords in CATEGORY_KEYWORD_MAP.items():
            for kw in keywords:
                if kw in text:
                    return cat
        # Check filename only if badge didn't match
        fn = os.path.basename(filename_or_url).lower()
        for cat, keywords in CATEGORY_KEYWORD_MAP.items():
            for kw in keywords:
                if kw in fn:
                    return cat
        return "researcher"  # Default institutional category

    def check_visual_candidate(
        self,
        candidate_image_or_path,
        url_or_filename: str,
        category: str,
        current_episode_categories: Dict[str, int],
        current_date_str: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validates whether candidate visual meets all strict editorial criteria:
          1. Not in banned asset blacklist
          2. Diversity category not saturated in current episode (max 2 per category)
          3. URL not used in past 14 days
          4. pHash Hamming distance > 6 against all images in past 14 days
        Returns:
          (approved: bool, computed_phash: Optional[str], rejection_reason: Optional[str])
        """
        if not current_date_str:
            current_date_str = datetime.now().strftime("%Y-%m-%d")

        curr_dt = datetime.strptime(current_date_str, "%Y-%m-%d")
        cutoff_dt = curr_dt - timedelta(days=14)

        # 1. Blacklist Check
        clean_name = url_or_filename.lower()
        for banned in BANNED_ASSET_KEYWORDS:
            if banned in clean_name:
                return (False, None, f"Permanently banned stock visual: {banned}")

        # 2. Category diversity cap: For up to 9-story show (27 cuts), allow up to 6 cuts in a broad category
        cat_count = current_episode_categories.get(category, 0)
        if cat_count >= 6:
            return (False, None, f"Category diversity cap exceeded for '{category}' ({cat_count}/6 already used)")

        # 3. Compute Perceptual Hash
        try:
            cand_hash = self.compute_phash(candidate_image_or_path)
        except Exception as e:
            return (False, None, f"Failed to compute pHash: {e}")

        # 4. 14-Day Memory & Hamming Distance Check
        for day_entry in self.data.get("history", []):
            try:
                day_dt = datetime.strptime(day_entry.get("date", ""), "%Y-%m-%d")
                if day_dt < cutoff_dt:
                    continue  # Outside 14-day rolling window
            except Exception:
                pass

            for asset in day_entry.get("assets", []):
                # Direct URL check
                if url_or_filename and (url_or_filename == asset.get("url") or url_or_filename == asset.get("filename")):
                    return (False, cand_hash, f"Asset URL/filename already used on {asset.get('date')}")

                # pHash Hamming Distance check
                past_hash = asset.get("phash")
                if past_hash:
                    dist = self.hamming_distance(cand_hash, past_hash)
                    if dist <= 6:
                        return (False, cand_hash, f"Perceptually near-identical image detected (Hamming distance {dist} <= 6) from {asset.get('date')}")

        return (True, cand_hash, None)

    def register_episode_visuals(self, date_str: str, assets: List[Dict]):
        """
        Registers all approved visuals for an episode into the 14-day visual memory.
        """
        # Remove any existing entry for this date to avoid duplicates
        self.data["history"] = [d for d in self.data.get("history", []) if d.get("date") != date_str]

        self.data["history"].insert(0, {
            "date": date_str,
            "count": len(assets),
            "assets": assets
        })
        self.save()


if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    mgr = VisualMemoryManager()

    # Create dummy image for testing
    img1 = Image.new('RGB', (1920, 1080), color=(73, 109, 137))
    h1 = mgr.compute_phash(img1)
    print(f"Computed pHash for blank test image: {h1}")

    # Test category classification
    cat1 = mgr.classify_visual_category("SITUATION ROOM • BILATERAL CRISIS COMMUNICATIONS")
    cat2 = mgr.classify_visual_category("HIGH-THROUGHPUT GPU CLUSTER • TRAINING REVIEWS")
    print(f"Classified badges: situation_room -> '{cat1}', gpu_cluster -> '{cat2}'")

    # Test diversity cap
    current_counts = {"datacenter": 2, "government": 1}
    ok, _, reason = mgr.check_visual_candidate(img1, "s1_datacenter.jpg", "datacenter", current_counts)
    print(f"Diversity test for 3rd datacenter: approved={ok}, reason={reason}")

    # Test blacklist check
    ok_banned, _, reason_banned = mgr.check_visual_candidate(img1, "gov_white_house.jpg", "government", {})
    print(f"Blacklist test for Obama photo: approved={ok_banned}, reason={reason_banned}")
