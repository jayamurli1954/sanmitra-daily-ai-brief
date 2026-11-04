import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.aibrief.crew import crew_orchestrator as orch
from src.aibrief.crew.editor_brief import parse_stories
from src.aibrief.crew.fact_checker import FactChecker
from src.aibrief.crew.news_harvester import NewsHarvester


def entry(title, upvotes, featured="2026-10-14T00:00:00.000Z", pid="2610.00001"):
    return {"publishedAt": "2026-09-30T00:00:00.000Z",
            "paper": {"id": pid, "title": title, "upvotes": upvotes, "submittedOnDailyAt": featured,
                      "summary": "A study of agents.", "publishedAt": "2026-09-30T00:00:00.000Z"}}


class FetchDailyPaperTest(unittest.TestCase):
    def fetch(self, entries):
        h = NewsHarvester(target_date="2026-10-14")
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


PAPER = {"title": "Urbex: Agentic Spatial Grounding", "source": "arXiv", "sourceUrl": "https://arxiv.org/abs/2610.1",
         "summary": "The researchers propose Urbex.", "region": "WORLD", "desk": "Research Watch"}


class AddDailyPaperTest(unittest.TestCase):
    def run_add(self, n_stories, header=""):
        prompt = os.path.join(tempfile.mkdtemp(), "p.md")
        md = header + block("Editor lead story", "https://a.com/0", lead=True)
        md += "".join(block(f"Editor story {i}", f"https://e.com/{i}") for i in range(n_stories - 1))
        open(prompt, "w", encoding="utf-8").write(md)
        fake_h = mock.MagicMock(); fake_h.filter_candidates.return_value = [PAPER]
        fake_fc = mock.MagicMock(); fake_fc.assemble_stories.return_value = [PAPER]
        with mock.patch.object(orch, "NewsHarvester", return_value=fake_h), \
             mock.patch.object(orch, "FactChecker", return_value=fake_fc), \
             mock.patch.object(orch, "StoryMemoryLedger"):
            orch._add_daily_paper(prompt, "2026-10-15", [])
        return parse_stories(open(prompt, encoding="utf-8").read())

    def test_rides_on_top_of_a_full_brief(self):
        stories = self.run_add(10)
        self.assertEqual(len(stories), 11)
        self.assertIn("Editor story 8", [s["headline"] for s in stories])
        paper = next(s for s in stories if s["headline"] == PAPER["title"])
        self.assertIn("Desk: Research Watch", paper["lines"])

    def test_not_added_to_the_sunday_round_up(self):
        stories = self.run_add(10, header="## Weekly Round-up — Sunday, 18 October 2026 (IST)\n\n")
        self.assertEqual(len(stories), 10)


NEWS_HEADS = ["Nvidia opens Bengaluru chip design centre", "Japan backs national AI safety rules",
              "Alibaba cuts Qwen cloud prices for developers", "Samsung ships HBM4 memory to Nvidia",
              "Reliance Jio launches Hindi voice assistant", "EU fines Meta over chatbot data transfers",
              "Anthropic signs Pentagon cyber defence contract", "Baidu robotaxis expand to Wuhan airport",
              "Singapore funds national language model lab", "Infosys trains staff on agentic coding tools",
              "UK regulator opens inquiry into deepfake apps"]


def news_block(i, head):
    region = ["WORLD", "USA", "CHINA", "ASIA", "INDIA"][i % 5]
    return (f"# {region}\n\n### {head}\n" + ("Lead: yes\n" if i == 0 else "")
            + f"Source: Reuters\nhttps://www.reuters.com/technology/story-{i}/\n\n"
            + f"Officials confirmed the development on Tuesday after weeks of talks. Story number {i} "
            + "continues with a second sentence about what happens next for the industry.\n\n")


class BuilderResearchSlotTest(unittest.TestCase):
    def build(self, desk, body):
        from build_episode_from_prompt import parse_markdown_prompt
        md = "# SanMitra AI News Wire\n\n## Daily AI Brief — Thursday, 15 October 2026 (IST)\n\n"
        md += "".join(news_block(i, h) for i, h in enumerate(NEWS_HEADS))
        md += (f"# WORLD\n\n### Urbex: Agentic Spatial Grounding\nDesk: {desk}\nSource: arXiv\n"
               f"https://arxiv.org/abs/2610.00001\n\n{body}\n")
        return parse_markdown_prompt(md)["stories"]

    def test_ten_news_stories_then_the_research_story(self):
        stories = self.build("Research Watch", "The researchers built a system that locates objects in city scenes.")
        self.assertEqual(len(stories), 11)
        self.assertEqual(stories[-1]["headline"], "Urbex: Agentic Spatial Grounding")
        self.assertTrue(stories[-1]["script"].startswith("From the research desk."))
        self.assertEqual(stories[0]["headline"], NEWS_HEADS[0])

    def test_feature_runs_past_the_news_story_length(self):
        sentence = "The researchers describe how the system learns to ground language in street imagery step by step. "
        stories = self.build("Research of the Week", sentence * 16)
        script = stories[-1]["script"]
        self.assertTrue(script.startswith("And now, our research story of the week."))
        self.assertGreater(len(script.split()), 200)


class WeekPaperTest(unittest.TestCase):
    def test_most_upvoted_unaired_paper_of_the_week(self):
        h = NewsHarvester(target_date="2026-11-08")  # a Sunday
        by_date = {"2026-11-03": [entry("Aired Big Paper", 300, pid="2611.1")],
                   "2026-11-05": [entry("Fresh Paper", 200, pid="2611.2"), entry("Small", 10, pid="2611.3")]}
        text = "The researchers study how agents plan long tasks across many tools and settings. " * 30
        with mock.patch.object(h, "_get_json", side_effect=lambda url: by_date.get(url.split("date=")[1], [])), \
             mock.patch.object(h, "fetch_paper_text", return_value=text) as fetch:
            feature = h.fetch_week_paper(exclude_ids={"2611.1"})
        self.assertEqual(feature["title"], "Fresh Paper")
        self.assertEqual(feature["desk"], "Research of the Week")
        fetch.assert_called_with("2611.2")
        self.assertGreater(len(feature["summary"].split()), 250)


class PaperSectionsTest(unittest.TestCase):
    def test_keeps_abstract_intro_conclusion_without_maths_or_citations(self):
        from src.aibrief.crew.news_harvester import paper_sections
        full = "\n".join([
            "Wave Forcing", "Abstract",
            "We present a method that keeps long generated videos stable while they stream to viewers.",
            "1 Introduction",
            "Streaming video models drift over time (Wan et al., 2025), which hurts quality for long clips.",
            "Each chunk \\(i\\) undergoes \\(S\\) updates in this formulation, as shown in the overall design.",
            "2 Method",
            "This section has the detailed equations and ablations that are not read aloud on the broadcast.",
            "6 Conclusion",
            "Our approach doubles the frame rate while keeping appearance consistent across long videos.",
            "References",
            "Wan et al. 2025. A very long reference entry that should never be read out loud at all.",
        ])
        text = paper_sections(full)
        self.assertIn("The researchers present a method", text)
        self.assertIn("Their approach doubles the frame rate", text)
        self.assertNotIn("Wan et al", text)
        self.assertNotIn("ablations", text)
        self.assertNotIn("undergoes", text)  # had maths in it


class RewriterTargetTest(unittest.TestCase):
    def test_word_targets(self):
        from src.aibrief.crew.story_rewriter import _word_target
        self.assertEqual(_word_target(""), 140)
        self.assertEqual(_word_target("Research Watch"), 90)
        self.assertEqual(_word_target("Research of the Week"), 250)


class PaperTitleCheckTest(unittest.TestCase):
    def test_paper_title_need_not_appear_in_the_abstract(self):
        abstract = ("The researchers present a streaming video generator that renders frames as they are "
                    "requested. " * 8)
        checker = FactChecker(target_date="2026-10-14",
                              fetch_article=lambda url: {"text": abstract, "published": ""})
        story = {"title": "Wave Forcing: Towards Speed-of-Light Streaming Video Generation",
                 "sourceUrl": "https://arxiv.org/abs/2611.00859", "published": "2026-10-14T06:00:00+00:00"}
        self.assertIsNotNone(checker.verify_against_article(story), checker.rejections)


if __name__ == "__main__":
    unittest.main()
