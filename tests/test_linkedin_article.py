import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.aibrief.generate_linkedin_article import build_linkedin_article, clean_summary

EPISODE = {
    "date": "2026-10-13",
    "stories": [
        {"region": "USA", "headline": "Intel, Broadcom CEOs warn capital crunch",
         "script": "In another major development, the CEOs of Intel and Broadcom warned about capital.",
         "whyThisMatters": "The CEOs of Intel and Broadcom warned about capital.",
         "source": "CNBC", "sourceUrl": "https://www.cnbc.com/x"},
        {"region": "INDIA", "headline": "How AI exposure varies across Indian states",
         "script": "Turning to India, Kerala leads.", "whyThisMatters": "",
         "source": "Mint", "sourceUrl": "https://www.livemint.com/y"},
    ],
}


class LinkedInArticleTest(unittest.TestCase):
    def build(self):
        with tempfile.TemporaryDirectory() as d:
            ep = os.path.join(d, "ep.json")
            with open(ep, "w", encoding="utf-8") as f:
                json.dump(EPISODE, f)
            text = build_linkedin_article(ep, output_article_path=os.path.join(d, "a.md"),
                                          output_post_path=os.path.join(d, "p.txt"))
            self.assertTrue(os.path.exists(os.path.join(d, "linkedin_article_2026-10-13.md")))
            return text

    def test_header_dates(self):
        text = self.build()
        self.assertIn("AI Brief — Tuesday, 13 October 2026 (IST)", text)
        self.assertIn("Covering Monday, 12 October 2026", text)

    def test_only_mentions_stories_in_the_brief(self):
        text = self.build()
        for invented in ("GPT-6.1", "World Labs", "Singapore", "Open Agent Safety Platform", "2023 and 2024"):
            self.assertNotIn(invented, text)
        self.assertIn("2 AI stories from 2 news outlets", text)
        self.assertIn("🔹 USA: Intel, Broadcom CEOs warn capital crunch.", text)

    def test_summary_not_repeated_and_lead_in_removed(self):
        text = self.build()
        self.assertEqual(text.count("warned about capital"), 1)
        self.assertNotIn("In another major development", text)
        self.assertIn("Kerala leads.", text)

    def test_clean_summary(self):
        self.assertEqual(clean_summary("Expanding on regulatory scrutiny, nuvacore is raising."), "Nuvacore is raising.")
        self.assertEqual(clean_summary("Also today. Nuvacore is raising."), "Nuvacore is raising.")
        self.assertEqual(clean_summary("In China. China Mobile tripled capacity."), "China Mobile tripled capacity.")


if __name__ == "__main__":
    unittest.main()
