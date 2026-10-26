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

    def test_ipo_and_company_results_headlines(self):
        for h in ["Anthropic's draft IPO filing shows $16.3B revenue and an $80.7B loss",
                  "Anthropic told investors Q3 revenue hit 16.8 billion dollars",
                  "Infosys quarterly results beat estimates on AI deals",
                  "Cerebras files DRHP-style papers to go public"]:
            self.assertTrue(is_stock_market_story(h), h)
        for h in ["DeepSeek nears a funding round of about 14 billion dollars",
                  "OpenAI will train government staff through iGOT Karmayogi",
                  "Hone raises 60 million dollars for AI agents"]:
            self.assertFalse(is_stock_market_story(h), h)

    def test_personal_scandal_headlines(self):
        from src.aibrief.crew.text_utils import is_personal_scandal_story
        for h in ["Judge dismisses Sam Altman’s sister’s sexual abuse lawsuit",
                  "Actress Mia Goth says it's 'incomprehensible' that Instagram allows this",
                  "Tech founder's divorce turns into a family feud"]:
            self.assertTrue(is_personal_scandal_story(h), h)
        for h in ["Grok generates deepfake sexual abuse images, regulators probe",
                  "Actor sues studio over AI voice clone of his performance",
                  "OpenAI sued by authors over training data",
                  "Anthropic’s Claude sent a fake murder tip to Philadelphia police"]:
            self.assertFalse(is_personal_scandal_story(h), h)

    def test_results_wording_without_the_word_results(self):
        for h in ["Meta beats expectations but legal penalties hit profit amid AI race",
                  "Samsung Electronics projects record $80 billion quarterly operating profit on HBM demand",
                  "Alphabet tops estimates as cloud AI demand grows",
                  "Microsoft third-quarter sales rise on Azure AI"]:
            self.assertTrue(is_stock_market_story(h), h)
        for h in ["Non-profit launches free AI tutor for rural schools",
                  "Nonprofit coalition publishes AI safety guidance",
                  "Nvidia will ship Rubin chips in the first quarter of 2027",
                  "AI model beats human experts at protein design"]:
            self.assertFalse(is_stock_market_story(h), h)

    def test_ipo_wording_without_the_word_ipo(self):
        for h in ["Anthropic officially files for its public debut",
                  "Cerebras makes its Nasdaq market debut",
                  "Startup confidentially submits S-1 ahead of listing",
                  "Chipmaker prices its public offering"]:
            self.assertTrue(is_stock_market_story(h), h)
        for h in ["Gemini 4 makes its debut in public preview",
                  "Meta debuts Muse Spark open weights",
                  "Moonshot launches Kimi K3.1 Pro"]:
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

    def test_election_stories(self):
        from src.aibrief.crew.text_utils import is_election_story
        for title, body in [
            ("AI deepfakes flood US election campaign", ""),
            ("Meta tightens rules on AI political ads", ""),
            ("Senate passes AI bill", "It came weeks before the midterms."),
            ("Georgia reviews whether AI can count ballots", ""),
            ("Election Commission of India issues AI guidelines", ""),
            ("Sanders renews push to pause advanced AI", "Senator Bernie Sanders argued for a ban."),
            ("Anthropic shops its AI safety bill to Congress", ""),
            ("White House issues AI order", ""),
        ]:
            self.assertTrue(is_election_story(title, body), title)
        for title, body in [
            ("Nvidia commits 250 million dollars to UK AI research", "The company devoted the funds to safety."),
            ("OpenAI pivoted its device plans", "It selected a new supplier."),
            ("India weighs disclosure rules for AI agents", "Officials are considering a consultation."),
            ("Nvidia commits UK compute", "The minister called it a vote of confidence in British research."),
            ("Anthropic proposes founder-control voting structure", "Shareholders keep voting rights."),
        ]:
            self.assertFalse(is_election_story(title, body), title)

    def test_editor_merge_drops_election_stories_and_fills_the_space(self):
        from src.aibrief.crew.editor_brief import merge_editor_brief
        body = ("The company said the system is now in use across several states. Officials described the "
                "rollout as a first step and said more details would follow next month.")
        editor = ("# USA\n\n### Candidates use AI chatbots on the campaign trail\nSource: AP\n"
                  "https://apnews.com/article/ai-campaign-123\n\n" + body + "\n\n"
                  "### Nvidia ships a new chip\nSource: Reuters\nhttps://www.reuters.com/tech/nvidia-chip-123/\n\n"
                  + body + "\n")
        other = ("# INDIA\n\n### Kerala leads AI-ready jobs\nSource: Mint\nhttps://www.livemint.com/ai/kerala-123\n\n"
                 + body + " Voters will decide next year.\n\n"
                 "### TCS opens an AI lab\nSource: Mint\nhttps://www.livemint.com/ai/tcs-123\n\n" + body + "\n")
        merged, report = merge_editor_brief(editor, other, "2026-10-19", 9)
        self.assertNotIn("campaign trail", merged)
        self.assertNotIn("Kerala leads", merged)
        self.assertIn("TCS opens an AI lab", merged)
        self.assertEqual(len(report["dropped_election"]), 2)


if __name__ == "__main__":
    unittest.main()
