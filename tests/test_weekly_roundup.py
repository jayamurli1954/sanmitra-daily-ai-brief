import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import weekly_roundup as w
from build_episode_from_prompt import parse_markdown_prompt

BODY = ("The company said the system is now in use across several states. Officials described the rollout "
        "as a first step and said more details would follow next month after a review of early results.")


def story(head, n):
    return {"headline": head, "region": "USA", "script": "Also today. " + BODY, "source": "Outlet",
            "sourceUrl": f"https://example.com/{abs(hash(head)) % 10**8}/{n}"}


class WeeklyRoundupTest(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.dir = tempfile.mkdtemp()
        os.chdir(self.dir)
        os.makedirs(w.AIRED_DIR)
        week = {  # Mon 12 .. Sat 17 Oct 2026, aired for Sunday 18
            "2026-10-12": ["Anthropic's Claude sent a fake murder tip to Philadelphia police",
                           "Kerala leads Indian states in AI-ready jobs", "Airbus flies Valkyrie combat drone"],
            "2026-10-13": ["Philadelphia police criticise Anthropic over fake murder tip delay",
                           "Meta launches Muse Wonder assistant models",
                           "Chip stocks slide after Broadcom boss likens AI investing to casino"],
            "2026-10-16": ["Microsoft unveils Maia accelerator", "DeepSeek backs robotics startup Winverse",
                           "SquadStack releases Arth speech model", "Telangana launches Brilliance classroom tool"],
            "2026-10-17": ["Nvidia ships Vera processors", "Alibaba details QwenGyre training system",
                           "ByteDance speeds up Doubao agent", "Tencent fast-tracks WorkBuddy agent"],
        }
        for date, heads in week.items():
            with open(os.path.join(w.AIRED_DIR, f"{date}.json"), "w", encoding="utf-8") as f:
                json.dump({"date": date, "stories": [story(h, i) for i, h in enumerate(heads)]}, f)

    def tearDown(self):
        os.chdir(self.cwd)

    def build(self):
        path = w.build_weekly_prompt("2026-10-18")
        return parse_markdown_prompt(open(path, encoding="utf-8").read())

    def test_week_is_monday_to_saturday(self):
        self.assertEqual(w.week_dates("2026-10-18"), ["2026-10-12", "2026-10-13", "2026-10-14",
                                                      "2026-10-15", "2026-10-16", "2026-10-17"])

    def test_story_that_ran_two_days_leads_with_its_latest_development(self):
        ep = self.build()
        self.assertTrue(ep["weekly"])
        self.assertEqual(ep["stories"][0]["headline"], "Philadelphia police criticise Anthropic over fake murder tip delay")
        self.assertTrue(ep["intro"]["script"].startswith("This week in AI: Philadelphia police criticise"))

    def test_spread_across_the_week_and_no_stock_market(self):
        heads = [s["headline"] for s in self.build()["stories"]]
        self.assertNotIn("Chip stocks slide after Broadcom boss likens AI investing to casino", heads)
        saturday = {"Nvidia ships Vera processors", "Alibaba details QwenGyre training system",
                    "ByteDance speeds up Doubao agent", "Tencent fast-tracks WorkBuddy agent"}
        self.assertLessEqual(len(saturday & set(heads[:6])), 2)
        self.assertIn("Kerala leads Indian states in AI-ready jobs", heads)
        self.assertEqual(len(heads), 9)


if __name__ == "__main__":
    unittest.main()
