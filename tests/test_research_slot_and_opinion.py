import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.aibrief import breaking_wire
from src.aibrief.crew.editor_brief import merge_editor_brief, parse_stories
from src.aibrief.source_authority import is_opinion_url

FARAGE = "https://www.theguardian.com/commentisfree/2026/nov/06/nigel-farage-telegraph-story-newspaper-ai"


HEADLINES = [
    "Hospital chain Medora deploys triage assistant in emergency wards",
    "Railway operator Trenza tests track inspection drones",
    "Satellite startup Orbix raises funding for crop monitoring",
    "Brewery group Hopwell automates quality checks with cameras",
    "Orchestra in Vienna stages concert with robotic conductor",
    "Lighthouse keepers replaced by remote sensors along Norwegian coast",
    "Glacier researchers map ice loss with machine learning",
    "Volcano observatory issues faster eruption warnings using neural networks",
    "Monastery archive digitised by handwriting recognition project",
    "Vineyard owners in Bordeaux predict frost with weather models",
    "Harbour authority in Rotterdam schedules ships with optimisation tool",
    "Stadium security in Madrid adopts crowd counting system",
    "Library network in Toronto launches multilingual reading tutor",
    "Museum in Cairo restores papyrus images with generative tools",
    "Bakery franchise Crumbly forecasts bread demand to cut waste",
    "Cathedral restorers in Paris scan stonework for cracks",
    "Canyon park rangers track wildlife with acoustic monitors",
    "Aquarium in Osaka monitors fish health with underwater vision",
    "Greenhouse farmers in Kenya control irrigation with soil probes",
    "Ferry company in Istanbul predicts delays from traffic data",
]


def _story(n):
    return (f"### {HEADLINES[n]}\n"
            f"Source: Outlet {n}\nhttps://example{n}.com/news/{n}\n\n"
            f"Officials said the system went live this week after a pilot.\n")


PAPER = """### VFlash: Fast, Accurate Visual Planning via Flash Primitive Decoding
Desk: Research Watch
Source: arXiv Pre-print
https://arxiv.org/abs/2611.08449

The researchers take on a speed problem in the AI that guides robots.
"""


class ResearchSlotTest(unittest.TestCase):
    """6 Nov 2026: a re-run's prompt already held the paper, so an editor brief
    plus the collector's stories gave 9 news stories + the paper, not 10 + 1."""

    def test_paper_does_not_take_a_news_place(self):
        editor = "# USA\n\n" + "\n".join(_story(i) for i in range(1, 6))
        collector = "# WORLD\n\n" + PAPER + "\n" + "\n".join(_story(i) for i in range(11, 20))
        merged, report = merge_editor_brief(editor, collector, "2026-11-06", 10)
        stories = parse_stories(merged)
        news = [s for s in stories if "arxiv.org" not in " ".join(s["lines"])]
        self.assertEqual(len(news), 10)
        self.assertEqual(report["editor"] + report["added"], 10)
        self.assertEqual(sum("VFlash" in s["headline"] for s in stories), 1)
        self.assertIn("Desk: Research Watch", merged)

    def test_paper_is_kept_when_the_brief_is_short(self):
        editor = "# USA\n\n" + _story(1)
        merged, report = merge_editor_brief(editor, "# WORLD\n\n" + PAPER, "2026-11-06", 10)
        self.assertIn("VFlash", merged)
        self.assertEqual(report["added"], 0)


class OpinionPiecesTest(unittest.TestCase):
    def test_opinion_urls(self):
        self.assertTrue(is_opinion_url(FARAGE))
        self.assertTrue(is_opinion_url("https://www.example.com/opinion/2026/ai-column"))
        self.assertFalse(is_opinion_url("https://www.theguardian.com/technology/2026/nov/06/ai-agents-rules"))
        self.assertFalse(is_opinion_url(""))

    def test_breaking_wire_skips_comment_pieces(self):
        now = format_datetime(datetime.now(timezone.utc))
        body = ("The artificial intelligence company said the model is available today to hospitals across the "
                "country, after months of testing with doctors and regulators.")
        rss = f"""<rss><channel>
<item><title>Telegraph drops Nigel Farage, warns AI shake-up will hit journalism</title>
<link>{FARAGE}</link><pubDate>{now}</pubDate><description>{body}</description></item>
<item><title>OpenAI launches new AI model for hospitals across India</title>
<link>https://www.theguardian.com/technology/2026/nov/06/openai-hospitals</link><pubDate>{now}</pubDate>
<description>{body}</description></item>
</channel></rss>"""
        resp = mock.Mock(status_code=200, content=rss.encode(), headers={"Content-Type": "application/rss+xml"})
        day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        with mock.patch.object(breaking_wire.requests, "get", return_value=resp), \
                mock.patch.object(breaking_wire, "window_start", return_value=day_ago):
            items = breaking_wire.fetch_feed({"bureau": "WORLD", "source": "The Guardian", "url": "https://x"})
        links = [i["link"] for i in items]
        self.assertNotIn(FARAGE, links)
        self.assertIn("https://www.theguardian.com/technology/2026/nov/06/openai-hospitals", links)


if __name__ == "__main__":
    unittest.main()
