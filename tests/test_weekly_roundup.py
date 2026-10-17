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


def slug(head):
    return "-".join(head.lower().replace("'", "").split())[:60]


def brief(heads, region="USA"):
    out = [f"# {region}"]
    for h in heads:
        out += ["", f"### {h}", "Source: Reuters", f"https://www.reuters.com/technology/{slug(h)}-2026-10-15/", "", BODY]
    return "\n".join(out) + "\n"


def aired_story(head):
    return {"headline": head, "region": "USA", "script": BODY, "source": "Reuters",
            "sourceUrl": f"https://www.reuters.com/technology/{slug(head)}-2026-10-15/"}


class WeeklyRoundupTest(unittest.TestCase):
    """Sunday 18 Oct 2026: the week is Mon 12 - Sat 17."""

    def setUp(self):
        self.cwd = os.getcwd()
        self.dir = tempfile.mkdtemp()
        os.chdir(self.dir)
        os.makedirs(w.AIRED_DIR)
        os.makedirs(w.EDITOR_DIR)
        os.makedirs(os.path.dirname(w.HARVEST_LOG))
        self.offered = {
            "2026-10-13": ["Meta launches Muse Wonder assistant models", "Kerala leads Indian states in AI-ready jobs",
                           "Airbus flies Valkyrie combat drone"],
            "2026-10-15": ["Microsoft unveils Maia accelerator", "ASML warns it cannot meet AI chip demand in 2027",
                           "Chip stocks slide after Broadcom boss likens AI investing to casino"],
            "2026-10-17": ["Nvidia ships Vera processors", "Yandex data centre shut by drone strike",
                           "ASML warns it cannot meet AI chip demand through 2028"],
        }
        aired = {"2026-10-13": ["Meta launches Muse Wonder assistant models"],
                 "2026-10-15": ["Microsoft unveils Maia accelerator"],
                 "2026-10-17": ["Nvidia ships Vera processors"]}
        for date, heads in self.offered.items():
            with open(w.HARVEST_LOG.format(date=date), "w", encoding="utf-8") as f:
                f.write(brief(heads))
        for date, heads in aired.items():
            with open(os.path.join(w.AIRED_DIR, f"{date}.json"), "w", encoding="utf-8") as f:
                json.dump({"date": date, "stories": [aired_story(h) for h in heads]}, f)
        with open(os.path.join(w.EDITOR_DIR, "2026-10-14.md"), "w", encoding="utf-8") as f:
            f.write(brief(["Editor's left-out pick on AI jobs in India"], "INDIA")
                    + "\n### Unlinked editor note\nSource: Somewhere\n\n" + BODY + "\n")

    def tearDown(self):
        os.chdir(self.cwd)

    def build(self):
        path = w.build_weekly_prompt("2026-10-18")
        return parse_markdown_prompt(open(path, encoding="utf-8").read())

    def test_week_is_monday_to_saturday(self):
        self.assertEqual(w.week_dates("2026-10-18"), ["2026-10-12", "2026-10-13", "2026-10-14",
                                                      "2026-10-15", "2026-10-16", "2026-10-17"])

    def test_nothing_that_aired_comes_back(self):
        ep = self.build()
        self.assertTrue(ep["weekly"])
        heads = [s["headline"] for s in ep["stories"]]
        for aired in ["Meta launches Muse Wonder assistant models", "Microsoft unveils Maia accelerator",
                      "Nvidia ships Vera processors"]:
            self.assertNotIn(aired, heads)
        self.assertIn("Yandex data centre shut by drone strike", heads)
        self.assertIn("Kerala leads Indian states in AI-ready jobs", heads)

    def test_no_stock_market_or_unlinked_stories(self):
        heads = [s["headline"] for s in self.build()["stories"]]
        self.assertNotIn("Chip stocks slide after Broadcom boss likens AI investing to casino", heads)
        self.assertNotIn("Unlinked editor note", heads)

    def test_story_in_the_news_two_days_leads_with_its_latest_development(self):
        heads = [s["headline"] for s in self.build()["stories"]]
        self.assertEqual(heads[0], "ASML warns it cannot meet AI chip demand through 2028")
        self.assertNotIn("ASML warns it cannot meet AI chip demand in 2027", heads)

    def test_editor_pick_ranks_above_one_day_harvest(self):
        heads = [s["headline"] for s in self.build()["stories"]]
        self.assertLess(heads.index("Editor's left-out pick on AI jobs in India"),
                        heads.index("Airbus flies Valkyrie combat drone"))

    def test_no_unaired_stories_writes_nothing(self):
        for date in self.offered:
            os.remove(w.HARVEST_LOG.format(date=date))
        os.remove(os.path.join(w.EDITOR_DIR, "2026-10-14.md"))
        self.assertIsNone(w.build_weekly_prompt("2026-10-18"))
        self.assertFalse(os.path.exists(os.path.join("prompts", "2026-10-18.md")))

    def test_sunday_editor_file_keeps_the_round_up(self):
        from src.aibrief.crew.editor_brief import merge_editor_brief
        weekly_md = open(w.build_weekly_prompt("2026-10-18"), encoding="utf-8").read()
        editor = ("# INDIA\n\n### Editor's pick of the week\nSource: Mint\nhttps://www.livemint.com/ai/pick-123\n\n"
                  + BODY + "\n")
        merged, _ = merge_editor_brief(editor, weekly_md, "2026-10-18", 9)
        ep = parse_markdown_prompt(merged)
        self.assertTrue(ep["weekly"])
        self.assertEqual(ep["stories"][0]["headline"], "Editor's pick of the week")


if __name__ == "__main__":
    unittest.main()
