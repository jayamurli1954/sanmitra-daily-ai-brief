import json
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.aibrief import write_linkedin_article as w

EPISODE = {
    "date": "2026-11-01",
    "weekly": True,
    "stories": [
        {"region": "INDIA", "headline": "UP Cabinet approves robotics, AI park in Greater Noida", "source": "The Economic Times",
         "sourceUrl": "https://economictimes.example/up-park", "script": "Uttar Pradesh approved a park.", "whyThisMatters": "A park."},
        {"region": "WORLD", "headline": "WA seeks reimbursement from Deloitte", "source": "The Guardian",
         "sourceUrl": "https://www.theguardian.com/wa", "script": "WA paid Deloitte.", "whyThisMatters": "WA paid."},
        {"region": "USA", "headline": "Wabi valued at $1.25B", "source": "TechCrunch",
         "sourceUrl": "https://techcrunch.com/wabi", "script": "Wabi raised money.", "whyThisMatters": "Wabi raised."},
    ],
}

ANALYSIS = {
    "theme_headline": "AI's next phase: trust and infrastructure",
    "intro_paragraphs": ["AI is attracting investment.", "Here are the three developments that deserve attention."],
    "stories": [
        {"number": 1, "title": "Western Australia seeks reimbursement from Deloitte", "body_paragraphs": ["WA paid."],
         "why_it_matters": ["Quality assurance matters."]},
        {"number": 2, "title": "Wabi reaches a $1.25 billion valuation", "body_paragraphs": ["Wabi raised."],
         "why_it_matters": ["Agents build apps."]},
    ],
    "big_picture_intro": "Two trends stand out.",
    "big_picture_points": [{"heading": "Trust is non-negotiable", "paragraphs": ["The Deloitte case shows it."]}],
    "big_picture_closing": "",
    "takeaways": [{"label": "Accuracy before automation", "text": "Validate AI output."}],
    "closing_thought": ["The future of AI will be decided by who puts it to work responsibly."],
    "extra_hashtags": ["AIAgents", "#AI", "World Models"],
}


class FakeStream:
    def __init__(self, calls, stop="end_turn"):
        self.calls, self.stop = calls, stop

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return self

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get_final_message(self):
        return SimpleNamespace(stop_reason=self.stop, content=[
            SimpleNamespace(type="thinking"), SimpleNamespace(type="text", text=json.dumps(ANALYSIS))])


def fake_client(calls, stop="end_turn"):
    return SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(stream=FakeStream(calls, stop))))


class WriteArticleTest(unittest.TestCase):
    def write(self):
        calls = []
        with tempfile.TemporaryDirectory() as d:
            path = w.write_article(EPISODE, "https://youtu.be/5ZGF", d, fake_client(calls))
            with open(path, encoding="utf-8") as f:
                page = f.read()
            with open(os.path.join(d, "linkedin_article_2026-11-01.md"), encoding="utf-8") as f:
                md = f.read()
            self.assertTrue(os.path.exists(os.path.join(d, "linkedin_article.md")))
        return calls, page, md

    def test_weekly_header_in_the_editors_format(self):
        _, _, md = self.write()
        self.assertTrue(md.startswith("# 🌐 Weekly AI Round-up — Sunday, 1 November 2026 (IST)\n"))
        self.assertIn("Reporting period: Monday, 26 October – Saturday, 31 October 2026", md)
        self.assertIn("3 important AI stories | 3 news outlets | World • USA • India", md)
        self.assertIn("▶️ Watch this week's round-up: https://youtu.be/5ZGF", md)

    def test_daily_header(self):
        h = w.header(dict(EPISODE, date="2026-10-30", weekly=False), "https://youtu.be/x")
        self.assertEqual(h["title"], "🌐 Daily AI News Brief — Friday, 30 October 2026 (IST)")
        self.assertEqual(h["period"], ["Reporting window: Thursday, 29 October 2026", "Publication: Friday, 30 October 2026"])
        self.assertTrue(h["counts"].startswith("3 AI stories | 3 news outlets"))

    def test_stories_numbered_by_bureau_with_real_source_links(self):
        _, page, md = self.write()
        world, usa, india = md.index("## 🌍 WORLD"), md.index("## 🇺🇸 USA"), md.index("## 🇮🇳 INDIA")
        self.assertLess(world, usa)
        self.assertLess(usa, india)
        self.assertIn("### 1. Western Australia seeks reimbursement from Deloitte", md)
        self.assertIn("**Why it matters**\n\nQuality assurance matters.", md)
        self.assertIn("Source: [The Guardian — WA seeks reimbursement from Deloitte](https://www.theguardian.com/wa)", md)
        self.assertIn('<a href="https://www.theguardian.com/wa">The Guardian — WA seeks reimbursement from Deloitte</a>', page)

    def test_story_claude_left_out_falls_back_to_the_episode_text(self):
        _, _, md = self.write()
        self.assertIn("### 3. UP Cabinet approves robotics, AI park in Greater Noida\n\nA park.", md)

    def test_closing_sections_footer_and_hashtags(self):
        _, page, md = self.write()
        for heading in ("## THE BIG PICTURE", "## KEY TAKEAWAYS FOR BUSINESS LEADERS", "## CLOSING THOUGHT"):
            self.assertIn(heading, md)
        self.assertIn("* **Accuracy before automation:** Validate AI output.", md)
        self.assertIn("Follow me and tap the 🔔 bell on my profile", md)
        self.assertIn("#IndiaAI #AIAgents #WorldModels #SanMitraAINewsWire #OfficeMitraAIInsights", md)
        self.assertEqual(md.count("#AI "), 1)
        self.assertIn("Copy article", page)
        self.assertIn("individual article, not in a newsletter", page)

    def test_request_uses_structured_output_and_fallback(self):
        calls, _, _ = self.write()
        req = calls[0]
        self.assertEqual(req["model"], "claude-opus-5-5")
        self.assertEqual(req["output_config"]["format"]["type"], "json_schema")
        self.assertEqual(req["extra_body"], {"fallbacks": "default"})
        self.assertIn('<story number="1" region="World">', req["messages"][0]["content"])
        self.assertIn("weekly round-up", req["messages"][0]["content"])

    def test_refusal_or_cut_off_raises_so_the_template_stays(self):
        with tempfile.TemporaryDirectory() as d:
            for stop in ("refusal", "max_tokens"):
                with self.assertRaises(RuntimeError):
                    w.write_article(EPISODE, "https://youtu.be/x", d, fake_client([], stop))
            self.assertEqual(os.listdir(d), [])


if __name__ == "__main__":
    unittest.main()
