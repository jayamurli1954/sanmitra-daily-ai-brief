import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import weekly_finance_post as w


def story(head, script, source="Reuters"):
    return {"headline": head, "script": script, "source": source, "sourceUrl": "https://www.reuters.com/x"}


class WeeklyFinancePostTest(unittest.TestCase):
    """Monday 26 Oct 2026: the week is Mon 19 - Sun 25."""

    def setUp(self):
        self.cwd = os.getcwd()
        self.dir = tempfile.mkdtemp()
        os.chdir(self.dir)
        os.makedirs(w.AIRED_DIR)
        os.makedirs(w.OUT_DIR)
        days = {
            "2026-10-19": [story("CERT-In warns AI agents breached company systems",
                                 "AI agents reached business records and confidential data without authorisation."),
                           story("Hone raises 60 million dollars for finance agents", "Investors back AI agents for finance teams.")],
            "2026-10-21": [story("Tally adds AI to its accounting software", "Tally said businesses can now ask questions of their ledger."),
                           story("World Bank warns AI will cut entry-level jobs", "Entry-level hiring is slowing as AI spreads.")],
            "2026-10-22": [story("Nvidia ships a faster gaming chip", "Gamers get more frames per second."),
                           story("Senate committee weighs AI tax rules", "Senators discussed tax filing rules for AI.")],
        }
        for date, stories in days.items():
            with open(os.path.join(w.AIRED_DIR, f"{date}.json"), "w", encoding="utf-8") as f:
                json.dump({"date": date, "stories": stories}, f)
        with open(os.path.join(w.OUT_DIR, "linkedin_article_2026-10-21.md"), "w", encoding="utf-8") as f:
            f.write("▶️ Watch today's video brief: https://youtu.be/abcdefghijk\n")

    def tearDown(self):
        os.chdir(self.cwd)

    def test_only_on_mondays(self):
        self.assertIsNone(w.build("2026-10-25"))
        self.assertIsNotNone(w.build("2026-10-26"))

    def test_picks_finance_stories_with_matching_guidance(self):
        heads = {r["story"]["headline"]: r["theme"] for r in w.pick_stories("2026-10-26")}
        self.assertEqual(heads.get("CERT-In warns AI agents breached company systems"), "access")
        self.assertEqual(heads.get("Tally adds AI to its accounting software"), "software")
        self.assertEqual(heads.get("World Bank warns AI will cut entry-level jobs"), "jobs")
        self.assertNotIn("Nvidia ships a faster gaming chip", heads)          # not relevant
        self.assertNotIn("Hone raises 60 million dollars for finance agents", heads)  # funding news
        self.assertNotIn("Senate committee weighs AI tax rules", heads)       # US politics

    def test_post_has_links_and_fits_linkedin(self):
        text = open(w.build("2026-10-26"), encoding="utf-8").read()
        self.assertIn("AI for Accountants: the week of 19 to 25 October 2026", text)
        self.assertIn("👉 What it means for accountants:", text)
        self.assertIn("https://youtu.be/abcdefghijk", text)
        self.assertIn("9:30 AM IST", text)
        self.assertLessEqual(len(text), w.LINKEDIN_LIMIT)


if __name__ == "__main__":
    unittest.main()
