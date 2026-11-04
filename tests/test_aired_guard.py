import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.aibrief.crew import crew_orchestrator as orch

HEADS = ["Binance says fake job interviews used as part of crypto hack",
         "Brookfield plans AI data center at UK power station",
         "Apple restricts dating apps and AI companions to adults",
         "Moffett AI raises nearly RMB 1 billion in Series C+ funding"]


def brief(heads):
    md = "# SanMitra AI News Wire\n\n## Daily AI Brief — Wednesday, 04 November 2026 (IST)\n\n"
    for i, h in enumerate(heads):
        md += (f"# {['WORLD', 'USA', 'CHINA', 'INDIA'][i % 4]}\n\n### {h}\n" + ("Lead: yes\n" if i == 0 else "")
               + f"Source: Reuters\nhttps://www.reuters.com/technology/story-{i}/\n\n"
               + "Officials confirmed the development on Tuesday after weeks of talks with partners.\n\n")
    return md


class AiredGuardTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.dir)
        os.makedirs("prompts")
        self.aired_dir = os.path.join(self.dir, "aired")
        patcher = mock.patch.object(orch, "AIRED_DIR", self.aired_dir)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(os.chdir, self.cwd)

    def write_aired(self, heads):
        os.makedirs(self.aired_dir, exist_ok=True)
        with open(os.path.join(self.aired_dir, "2026-11-04.json"), "w", encoding="utf-8") as f:
            json.dump({"date": "2026-11-04", "stories": [{"headline": h} for h in heads]}, f)

    def test_brief_that_already_aired_is_set_aside(self):
        prompt = os.path.join("prompts", "2026-11-04.md")
        open(prompt, "w", encoding="utf-8").write(brief(HEADS))
        self.write_aired(HEADS)
        warnings = []
        moved = orch._set_aside_aired_prompt(prompt, "2026-11-04", orch.aired_headlines("2026-11-04"), warnings)
        self.assertTrue(moved)
        self.assertFalse(os.path.exists(prompt))
        self.assertIn("already aired", warnings[0])

    def test_fresh_brief_is_kept(self):
        prompt = os.path.join("prompts", "2026-11-04.md")
        open(prompt, "w", encoding="utf-8").write(brief(HEADS))
        self.write_aired(["Canva to cut more than 1,200 jobs in restructure"])
        self.assertFalse(orch._set_aside_aired_prompt(prompt, "2026-11-04", orch.aired_headlines("2026-11-04"), []))
        self.assertTrue(os.path.exists(prompt))

    def test_second_upload_keeps_the_first_ones_stories(self):
        self.write_aired(HEADS[:2])
        episode = os.path.join(self.dir, "active.json")
        json.dump({"date": "2026-11-04", "stories": [{"headline": HEADS[1]}, {"headline": HEADS[3]}]},
                  open(episode, "w", encoding="utf-8"))
        orch.save_aired_episode("2026-11-04", episode)
        self.assertEqual(sorted(orch.aired_headlines("2026-11-04")), sorted([HEADS[0], HEADS[1], HEADS[3]]))

    def test_crew_drafted_brief_gets_the_research_story(self):
        with mock.patch.object(orch, "_crew_verify", return_value=([{"title": h} for h in HEADS * 2], [])), \
             mock.patch.object(orch, "write_prompt"), \
             mock.patch.object(orch, "_add_daily_paper") as paper, \
             mock.patch.object(orch, "_add_research_of_the_week"), \
             mock.patch.object(orch, "rewrite_prompt_stories", return_value=[]), \
             mock.patch.object(orch, "_build_episode", return_value=None):
            orch.run_autonomous_crew("2026-11-04")
        paper.assert_called_once()


if __name__ == "__main__":
    unittest.main()
