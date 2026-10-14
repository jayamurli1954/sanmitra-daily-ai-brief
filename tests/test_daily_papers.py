import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.aibrief.crew import crew_orchestrator as orch
from src.aibrief.crew.editor_brief import parse_stories
from src.aibrief.crew.news_harvester import NewsHarvester


def entry(title, upvotes, featured="2026-10-14T00:00:00.000Z", pid="2610.00001"):
    return {"publishedAt": "2026-09-30T00:00:00.000Z",
            "paper": {"id": pid, "title": title, "upvotes": upvotes, "submittedOnDailyAt": featured,
                      "summary": "A study of agents.", "publishedAt": "2026-09-30T00:00:00.000Z"}}


class FetchDailyPaperTest(unittest.TestCase):
    def fetch(self, entries):
        h = NewsHarvester(target_date="2026-10-15")
        with mock.patch.object(h, "_get_json", return_value=entries) as get:
            items = h.fetch_daily_paper()
        self.assertIn("date=2026-10-14", get.call_args[0][0])  # the day the episode covers
        return h, items

    def test_most_upvoted_non_question_paper(self):
        _, items = self.fetch([entry("Urbex: Agentic Spatial Grounding", 99, pid="2610.1"),
                               entry("Can Coding Agents Build Agents?", 205, pid="2610.2"),
                               entry("Small Paper", 12, pid="2610.3")])
        self.assertEqual([i["title"] for i in items], ["Urbex: Agentic Spatial Grounding"])
        self.assertEqual(items[0]["url"], "https://arxiv.org/abs/2610.1")
        self.assertTrue(items[0]["published"].startswith("2026-10-14"))  # featured date, not arXiv date

    def test_nothing_below_threshold(self):
        _, items = self.fetch([entry("Small Paper", 12)])
        self.assertEqual(items, [])

    def test_paper_titles_skip_the_ai_keyword_check(self):
        h, items = self.fetch([entry("Multics: Generative Multi-Player World Model", 40)])
        self.assertEqual(len(h.filter_candidates(items)), 1)


def block(head, url, lead=False, region="USA"):
    return f"# {region}\n\n### {head}\n" + ("Lead: yes\n" if lead else "") + f"Source: Outlet\n{url}\n\nBody text for {head}.\n"


class AddDailyPaperTest(unittest.TestCase):
    def run_add(self, n_collected, editor_heads=()):
        d = tempfile.mkdtemp()
        prompt, editor = os.path.join(d, "p.md"), os.path.join(d, "e.md")
        md = block("Editor lead story", "https://a.com/0", lead=True)
        md += "".join(block(h, f"https://e.com/{i}") for i, h in enumerate(editor_heads))
        md += "".join(block(f"Collected story {i}", f"https://c.com/{i}") for i in range(n_collected))
        open(prompt, "w", encoding="utf-8").write(md)
        open(editor, "w", encoding="utf-8").write(block("Editor lead story", "https://a.com/0")
                                                  + "".join(block(h, f"https://e.com/{i}") for i, h in enumerate(editor_heads)))
        paper = {"title": "Urbex: Agentic Spatial Grounding", "source": "arXiv", "sourceUrl": "https://arxiv.org/abs/2610.1",
                 "summary": "The researchers propose Urbex.", "region": "WORLD"}
        fake_h = mock.MagicMock(); fake_h.filter_candidates.return_value = [paper]
        fake_fc = mock.MagicMock(); fake_fc.assemble_stories.return_value = [paper]
        with mock.patch.object(orch, "NewsHarvester", return_value=fake_h), \
             mock.patch.object(orch, "FactChecker", return_value=fake_fc), \
             mock.patch.object(orch, "StoryMemoryLedger"):
            orch._add_daily_paper(prompt, "2026-10-15", editor, [])
        return [s["headline"] for s in parse_stories(open(prompt, encoding="utf-8").read())]

    def test_added_when_there_is_room(self):
        heads = self.run_add(3)
        self.assertIn("Urbex: Agentic Spatial Grounding", heads)
        self.assertEqual(len(heads), 5)

    def test_replaces_last_collected_story_when_full(self):
        heads = self.run_add(8)
        self.assertEqual(len(heads), 9)
        self.assertIn("Urbex: Agentic Spatial Grounding", heads)
        self.assertNotIn("Collected story 7", heads)
        self.assertIn("Editor lead story", heads)

    def test_never_replaces_editor_stories(self):
        heads = self.run_add(0, editor_heads=[f"Editor story {i}" for i in range(8)])
        self.assertNotIn("Urbex: Agentic Spatial Grounding", heads)
        self.assertEqual(len(heads), 9)


if __name__ == "__main__":
    unittest.main()
