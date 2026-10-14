import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.aibrief.crew.fact_checker import MAX_EPISODE_STORIES, MIN_EPISODE_STORIES, STORY_MAX_WORDS
from src.aibrief.crew.news_harvester import NewsHarvester
from src.aibrief.crew.text_utils import is_stock_market_story


class StoryRulesTest(unittest.TestCase):
    def test_episode_size(self):
        self.assertEqual((MIN_EPISODE_STORIES, MAX_EPISODE_STORIES), (8, 9))
        self.assertLessEqual(STORY_MAX_WORDS * MAX_EPISODE_STORIES / 140, 10)  # ~140 words a minute

    def test_stock_market_headlines(self):
        for h in ["Chip stocks slide after Broadcom boss likens AI investing to casino",
                  "Nvidia's market value tops $5 trillion", "Samsung shares tumbled after CXMT claims progress",
                  "Sensex jumps as IT shares rally"]:
            self.assertTrue(is_stock_market_story(h), h)
        for h in ["Nuvacore raising funds at about a $2.5 billion valuation", "Microsoft unveils Maia 300 chip",
                  "Intel, Broadcom CEOs warn capital crunch could become AI's biggest bottleneck"]:
            self.assertFalse(is_stock_market_story(h), h)

    def test_harvest_drops_stock_market_stories(self):
        h = NewsHarvester(target_date="2026-10-14")
        items = [
            {"title": "Chip stocks slide as AI investing fears grow", "summary": "AI chip shares fell.",
             "url": "https://example.com/a", "published": "", "origin": "search"},
            {"title": "OpenAI launches new AI agent for developers", "summary": "The AI model writes code.",
             "url": "https://example.com/b", "published": "", "origin": "search"},
        ]
        kept = [i["title"] for i in h.filter_candidates(items)]
        self.assertNotIn("Chip stocks slide as AI investing fears grow", kept)


if __name__ == "__main__":
    unittest.main()
