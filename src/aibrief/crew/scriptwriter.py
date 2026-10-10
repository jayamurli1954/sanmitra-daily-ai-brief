"""
BroadcastScriptwriter Agent - SanMitra AI News Wire v7.0
Autonomous dual-anchor broadcast scriptwriting conforming strictly to CNBC/Bloomberg delivery standards.
"""

from datetime import datetime
import logging
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BroadcastScriptwriter")

REGIONAL_INTROS = {
    "WORLD": ["In our lead story today,", "In other global developments,", "In enterprise infrastructure,"],
    "USA": ["Turning to the United States,", "In concurrent industry updates,", "Expanding on domestic developments,"],
    "CHINA": ["Meanwhile in China,", "Expanding on regulatory scrutiny,", "In domestic computing architecture,"],
    "ASIA": ["In Asia,", "Across the Asia-Pacific region,"],
    "INDIA": ["Turning to India,", "Expanding on Indian digital public infrastructure,"]
}


class BroadcastScriptwriter:
    """Writes dual-anchor newsroom scripts with phonetic currency rules and natural transitions."""

    @staticmethod
    def format_spoken_currencies_and_figures(text):
        """Converts symbols and abbreviations into natural spoken English."""
        # Currency: $X.X billion -> X.X billion dollars
        text = re.sub(r'\$(\d+(?:\.\d+)?)\s*billion\b', r'\1 billion dollars', text, flags=re.IGNORECASE)
        text = re.sub(r'\$(\d+(?:\.\d+)?)\s*million\b', r'\1 million dollars', text, flags=re.IGNORECASE)
        text = re.sub(r'\$(\d+(?:\.\d+)?)\s*trillion\b', r'\1 trillion dollars', text, flags=re.IGNORECASE)
        text = re.sub(r'\$(\d+(?:,\d+)*(?:\.\d+)?)\b', r'\1 dollars', text)

        # Euro: €X -> X euros
        text = re.sub(r'€(\d+(?:\.\d+)?)\s*billion\b', r'\1 billion euros', text, flags=re.IGNORECASE)
        text = re.sub(r'€(\d+(?:\.\d+)?)\s*million\b', r'\1 million euros', text, flags=re.IGNORECASE)
        text = re.sub(r'€(\d+(?:,\d+)*(?:\.\d+)?)\b', r'\1 euros', text)

        # Pound: £X -> X pounds
        text = re.sub(r'£(\d+(?:\.\d+)?)\s*billion\b', r'\1 billion pounds', text, flags=re.IGNORECASE)
        text = re.sub(r'£(\d+(?:\.\d+)?)\s*million\b', r'\1 million pounds', text, flags=re.IGNORECASE)

        # Percentages: 90% -> ninety percent
        percent_words = {
            "90%": "ninety percent",
            "80%": "eighty percent",
            "50%": "fifty percent",
            "100%": "one hundred percent",
            "4%": "four percent",
            "3.6%": "three point six percent",
            "200%": "two hundred percent"
        }
        for p, w in percent_words.items():
            text = text.replace(p, w)
        text = re.sub(r'(\d+(?:\.\d+)?)%', r'\1 percent', text)

        # Clean markdown symbols
        text = text.replace("**", "").replace("*", "").replace("`", "").replace("#", "")
        # Remove raw URLs
        text = re.sub(r'https?://\S+', '', text)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def write_story_script(self, story, index, prev_region=None):
        """Draft authoritative script for an individual story with anchor rotation."""
        region = story.get("region", "WORLD").upper()
        title = story.get("title", "")
        summary = story.get("summary", "")
        source = story.get("source", "Verified Reports")

        # Pick smooth introductory transition
        intros = REGIONAL_INTROS.get(region, ["In recent reporting,"])
        if index == 1:
            intro = "In our lead story today,"
        elif region != prev_region:
            intro = intros[0]
        else:
            intro = intros[min(1, len(intros) - 1)]

        # Combine into authoritative broadcast copy
        raw_body = f"{intro} {summary if len(summary) > 60 else title}."
        spoken_script = self.format_spoken_currencies_and_figures(raw_body)

        # Ensure sentence structure is clean
        if not spoken_script.endswith("."):
            spoken_script += "."

        # Estimate duration based on ~2.5 words per second
        word_count = len(spoken_script.split())
        duration_sec = max(24, min(48, int(word_count / 2.4)))

        # Assign voice based on index: odd = Christopher, even = Aria
        voice = "en-US-ChristopherNeural" if index % 2 == 1 else "en-US-AriaNeural"

        # Slugify ID
        slug = re.sub(r'[^a-zA-Z0-9]+', '_', title.lower()).strip('_')[:30]
        story_id = f"s{index}_{slug}"

        return {
            "id": story_id,
            "region": region,
            "category": f"{region} Intelligence",
            "categoryTag": f"{region} • SPECIAL REPORT" if index <= 2 else f"{region} • INTELLIGENCE",
            "headline": title[:95],
            "subheadline": f"Source: {source}",
            "importanceScore": story.get("score", 85),
            "durationSeconds": duration_sec,
            "source": source,
            "sourceUrl": story.get("sourceUrl", ""),
            "researchDesk": "",
            "script": spoken_script,
            "voice": voice,
            "whyThisMatters": f"Critical development shaping {region} artificial intelligence policy and sovereign compute.",
            "keyPoints": [
                title[:80],
                f"Source: {source}"
            ]
        }

    def generate_episode_script(self, verified_stories, episode_date):
        """Produce full episode structure with intro, 14 stories, recap, and outro."""
        stories = []
        prev_reg = None
        for i, s in enumerate(verified_stories, 1):
            sc = self.write_story_script(s, i, prev_region=prev_reg)
            prev_reg = s.get("region")
            stories.append(sc)

        parsed_date = datetime.strptime(episode_date, "%Y-%m-%d")
        formatted_date = parsed_date.strftime("%d %B %Y").lstrip("0")

        episode_payload = {
            "date": episode_date,
            "formattedDate": formatted_date,
            "channelName": "SanMitra AI News Wire",
            "episodeTitle": f"SanMitra AI News Wire — {formatted_date}",
            "leadStory": stories[0]["headline"] if stories else "Global AI Intelligence Brief",
            "stories": stories
        }

        logger.info(f"Broadcast script drafting complete: {len(stories)} stories drafted.")
        return episode_payload
