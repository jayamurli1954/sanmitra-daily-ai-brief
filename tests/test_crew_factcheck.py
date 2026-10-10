"""
Offline tests for the crew's harvesting filters, fact-check and gate helpers.

Run from the project root:
    python -m unittest discover -s tests -v
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)
os.chdir(PROJECT_DIR)

from build_episode_from_prompt import parse_markdown_prompt
from src.aibrief.crew.fact_checker import FactChecker, resolve_region
from src.aibrief.crew.news_harvester import NewsHarvester, is_ai_story
from src.aibrief.crew.prompt_writer import render_prompt
from src.aibrief.crew.text_utils import (
    clean_feed_text, extractive_summary, is_recent, same_event, ungrounded_claims,
)
from validate_episode_sources import duplicate_events, source_appears_in_prompt, unsupported_figures

DATE = "2026-10-10"
FRESH = "2026-10-09T14:00:00+00:00"   # inside the window before 06:00 IST on DATE
STALE = "2026-10-05T14:00:00+00:00"

ARTICLE = (
    "OpenAI on Thursday released GPT-5.5, a model with a new reasoning mode for paid users. "
    "The company said the update cuts error rates by 40 percent on its internal benchmarks. "
    "OpenAI expects annual revenue of about $50 billion, according to people familiar with the plan. "
    "Subscribe to our newsletter for more. "
) + "Analysts said the release puts pressure on rivals including Google and Anthropic. " * 8


class FakeLedger:
    def __init__(self, stories):
        self.data = {"stories": stories}


def candidate(title, url, region="USA", summary="", published=FRESH, source="Feed"):
    return {"title": title, "url": url, "region": region, "summary": summary,
            "published": published, "source": source, "origin": "feed"}


class HarvestFilterTests(unittest.TestCase):
    def test_ai_keyword_needs_a_whole_word(self):
        self.assertFalse(is_ai_story("City council said parking rules will change again next month"))
        self.assertFalse(is_ai_story("Union paid staff after a long dispute"))
        self.assertTrue(is_ai_story("Bank rolls out AI-powered fraud checks"))
        self.assertTrue(is_ai_story("Nvidia ships new GPUs to Saudi buyers"))

    def test_recency_window(self):
        self.assertTrue(is_recent(FRESH, DATE))
        self.assertFalse(is_recent(STALE, DATE))
        self.assertFalse(is_recent("", DATE))
        self.assertTrue(is_recent("Fri, 09 Oct 2026 10:00:00 GMT", DATE))

    def test_filter_drops_stale_undated_and_non_ai(self):
        harvester = NewsHarvester(target_date=DATE)
        items = [
            candidate("OpenAI ships GPT-5.5 with new reasoning mode", "https://techcrunch.com/2026/10/09/openai-gpt"),
            candidate("Old Nvidia earnings story about GPUs", "https://techcrunch.com/2026/10/05/nvidia", published=STALE),
            candidate("Undated Anthropic story on Claude", "https://techcrunch.com/x/claude-story", published=""),
            candidate("City council said parking rules change again", "https://techcrunch.com/2026/10/09/parking"),
        ]
        kept = harvester.filter_candidates(items)
        self.assertEqual([k["title"] for k in kept], ["OpenAI ships GPT-5.5 with new reasoning mode"])


class TextCleanupTests(unittest.TestCase):
    def test_feed_boilerplate_and_double_full_stop_removed(self):
        raw = "OpenAI released an update for paid users.. The post OpenAI ships GPT update appeared first on TechCrunch."
        cleaned = clean_feed_text(raw)
        self.assertNotIn("appeared first", cleaned)
        self.assertNotIn("..", cleaned)

    def test_summary_comes_from_article_and_skips_boilerplate(self):
        summary = extractive_summary(ARTICLE)
        self.assertTrue(summary.startswith("OpenAI on Thursday released GPT-5.5"))
        self.assertNotIn("Subscribe", summary)


class RegionTests(unittest.TestCase):
    def test_substring_no_longer_routes_to_asia(self):
        self.assertEqual(resolve_region("Bank boosts information security spending", "WORLD"), "WORLD")

    def test_passing_mention_in_body_does_not_move_story(self):
        # Only the headline is used; the body mentioning India is irrelevant.
        self.assertEqual(resolve_region("OpenAI ships GPT update with new reasoning mode", "USA"), "USA")

    def test_regional_feed_default_needs_regional_blurb(self):
        us_story = "OpenAI and Anthropic are preparing for backlash after a possible AI incident."
        self.assertEqual(resolve_region("OpenAI, Anthropic Prepare For Backlash: Report", "INDIA", us_story), "WORLD")
        indian_story = "The Bengaluru startup raised funds to build GPU clouds for Indian enterprises."
        self.assertEqual(resolve_region("Startup raises funds for GPU cloud", "INDIA", indian_story), "INDIA")

    def test_headline_region(self):
        self.assertEqual(resolve_region("Alibaba unveils new Qwen model for enterprises", "WORLD"), "CHINA")
        self.assertEqual(resolve_region("US and China agree AI hotline", "WORLD"), "WORLD")


class SameEventTests(unittest.TestCase):
    def test_duplicates_from_the_2026_10_10_run(self):
        self.assertTrue(same_event(
            "Firmus pulls biggest ASX float since Telstra amid investor doubt about AI",
            "Nvidia-backed Aussie AI firm Firmus withdraws historic IPO, citing market conditions",
        ))
        self.assertTrue(same_event(
            "Anthropic bans users from 'needless abusive or cruel behavior' towards Claude",
            "Anthropic changes usage policy to ban model abuse and election interference",
        ))

    def test_different_events_are_kept(self):
        self.assertFalse(same_event("Google launches Gemini 3 for developers", "Meta launches Llama 5 for developers"))
        self.assertFalse(same_event("OpenAI ships GPT-5.5 with reasoning mode", "OpenAI sued by authors over training data"))
        # Seen in the live run: shared topic words alone are not the same event.
        self.assertFalse(same_event("Amazon drops data center NDAs, and AI agents want your credit card",
                                    "Amazon urges communities not to block data centers"))


class GroundingTests(unittest.TestCase):
    def test_numbers_must_be_in_article(self):
        self.assertEqual(ungrounded_claims("OpenAI targets $50 billion revenue", ARTICLE), [])
        self.assertIn("70", ungrounded_claims("OpenAI targets $70 billion revenue", ARTICLE))

    def test_entities_and_names_with_digits_are_not_figures(self):
        self.assertEqual(ungrounded_claims(clean_feed_text("&#8216;Pure insanity&#8217; at OpenAI"), ARTICLE), [])
        self.assertEqual(ungrounded_claims("a16z partner on the state of consumer AI", ARTICLE), [])

    def test_title_case_words_are_not_treated_as_names(self):
        self.assertEqual(ungrounded_claims("OpenAI Faces Pressure As Revenue Plan Shifts", ARTICLE), [])

    def test_names_must_be_in_article(self):
        self.assertIn("Microsoft", ungrounded_claims("OpenAI and Microsoft cut error rates", ARTICLE))


class FactCheckerTests(unittest.TestCase):
    def fetcher(self, articles):
        return lambda url: articles.get(url, {"text": "", "published": ""})

    def test_screening(self):
        fc = FactChecker(target_date=DATE)
        self.assertIsNone(fc.screen(candidate("RUMOUR: Nvidia secretly buying Anthropic, insiders say",
                                              "https://random-ai-blog.xyz/p/12345678")))
        self.assertIsNone(fc.screen(candidate("Nvidia is reportedly buying Anthropic, insiders say",
                                              "https://techcrunch.com/2026/10/09/nvidia-anthropic")))
        self.assertIsNone(fc.screen(candidate("AI and the climate crisis pose existential risks",
                                              "https://www.theguardian.com/commentisfree/2026/oct/09/ai-climate")))
        ok = fc.screen(candidate("OpenAI ships GPT-5.5 with new reasoning mode",
                                 "https://techcrunch.com/2026/10/09/openai-gpt", source="TechCrunch AI"))
        self.assertEqual(ok["source"], "TechCrunch")
        self.assertEqual(ok["sourceType"], "reporting")
        company = fc.screen(candidate("Introducing GPT-5.5 for ChatGPT users", "https://openai.com/index/gpt-5-5"))
        self.assertEqual(company["sourceType"], "company")

    def test_assembly_verifies_against_article(self):
        good_url = "https://techcrunch.com/2026/10/09/openai-gpt-5-5"
        twin_url = "https://www.theverge.com/2026/10/9/openai-gpt-5-5-release"
        bad_url = "https://arstechnica.com/ai/2026/10/openai-revenue-70"
        stale_url = "https://www.theguardian.com/technology/2026/oct/09/old-story"
        articles = {
            good_url: {"text": ARTICLE, "published": FRESH},
            twin_url: {"text": ARTICLE, "published": FRESH},
            bad_url: {"text": ARTICLE, "published": FRESH},
            stale_url: {"text": ARTICLE, "published": STALE},
        }
        candidates = [
            candidate("OpenAI releases GPT-5.5 with a new reasoning mode", good_url),
            candidate("OpenAI GPT-5.5 release adds reasoning mode for paid users", twin_url),
            candidate("OpenAI now expects $70 billion in revenue", bad_url),
            candidate("Google DeepMind opens a new London research lab", stale_url, published=""),
        ]
        fc = FactChecker(target_date=DATE, fetch_article=self.fetcher(articles))
        selected = fc.assemble_14_stories(candidates)

        self.assertEqual(len(selected), 1)
        story = selected[0]
        self.assertTrue(story["summary"].startswith("OpenAI on Thursday released GPT-5.5"))
        self.assertEqual(len(story["also"]), 1)  # the twin became a second source
        reasons = " | ".join(r["reason"] for r in fc.rejections)
        self.assertIn("same event", reasons)
        self.assertIn("70", reasons)
        self.assertIn("broadcast window", reasons)

    def test_story_aired_last_week_is_skipped_but_not_todays_rerun(self):
        ledger = FakeLedger([
            {"headline": "Firmus pulls biggest ASX float since Telstra", "first_covered": "2026-10-07"},
            {"headline": "OpenAI releases GPT-5.5 with a new reasoning mode", "first_covered": DATE},
        ])
        fc = FactChecker(target_date=DATE, ledger=ledger)
        recent = fc.recent_headlines()
        self.assertIsNotNone(fc.is_repeat("Firmus withdraws historic IPO", recent))
        self.assertIsNone(fc.is_repeat("OpenAI releases GPT-5.5 with a new reasoning mode", recent))


class PromptRoundTripTests(unittest.TestCase):
    def test_crew_prompt_builds_and_passes_source_checks(self):
        stories = [{
            "title": "OpenAI releases GPT-5.5 with a new reasoning mode",
            "source": "TechCrunch",
            "sourceUrl": "https://techcrunch.com/2026/10/09/openai-gpt-5-5",
            "region": "USA",
            "summary": extractive_summary(ARTICLE),
            "also": [{"source": "The Verge", "url": "https://www.theverge.com/2026/10/9/openai-gpt-5-5"}],
        }, {
            "title": "Disrupting covert influence operations that misuse ChatGPT",
            "source": "OpenAI",
            "sourceUrl": "https://openai.com/index/disrupting-influence-operations-2026",
            "region": "WORLD",
            "summary": "OpenAI said it removed account networks linked to 3 state influence campaigns this quarter.",
            "also": [],
        }]
        prompt = render_prompt(stories, DATE)
        episode = parse_markdown_prompt(prompt)

        self.assertEqual(episode["date"], DATE)
        by_url = {s["sourceUrl"]: s for s in episode["stories"]}
        self.assertEqual(by_url["https://techcrunch.com/2026/10/09/openai-gpt-5-5"]["sourceType"], "reporting")
        self.assertEqual(by_url["https://openai.com/index/disrupting-influence-operations-2026"]["sourceType"], "company")
        for s in episode["stories"]:
            self.assertTrue(source_appears_in_prompt(s["source"], prompt))
            self.assertEqual(unsupported_figures(s["script"], prompt), [])
            self.assertNotIn("sovereign compute", s["whyThisMatters"])


class GateHelperTests(unittest.TestCase):
    def test_unsupported_figures(self):
        self.assertEqual(unsupported_figures("Revenue of 50 billion dollars", "about $50 billion"), [])
        self.assertEqual(unsupported_figures("Revenue of 70 billion dollars", "about $50 billion"), ["70"])

    def test_duplicate_events(self):
        stories = [
            {"headline": "Firmus pulls biggest ASX float since Telstra"},
            {"headline": "Google launches Gemini 3 for developers"},
            {"headline": "Nvidia-backed Firmus withdraws historic IPO"},
        ]
        self.assertEqual(duplicate_events(stories), [(1, 3)])


if __name__ == "__main__":
    unittest.main()
