import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.aibrief import entity_visual_resolver as r

# Places and objects that were shown with stories that had nothing to do with them.
WRONG_SETTINGS = ("CANBERRA", "COPENHAGEN", "BHARAT MANDAPAM", "CAPITOL HILL", "GWU", "MIT CSAIL",
                  "PATRIOT", "CARRIER LAUNCH", "SEQUOIA", "(GIVEN NAME)", "(ARTS)", "INDIAN ARMY")


class HeadlineEntitiesTest(unittest.TestCase):
    def test_investor_modifier_is_not_the_subject(self):
        self.assertEqual(r.headline_entities("Sequoia-backed chip startup Nuvacore raising funds"), ["Nuvacore"])

    def test_full_names_and_no_demonyms_or_sentence_case_words(self):
        self.assertEqual(r.headline_entities("Actress Mia Goth says Instagram allowed an AI image"), ["Mia Goth", "Instagram"])
        self.assertEqual(r.headline_entities("How AI exposure varies across Indian states: Kerala leads"), ["Kerala"])
        self.assertEqual(r.headline_entities("Study finds language models are largely blind"), [])

    def test_possessive_ends_a_name_and_order_is_kept(self):
        self.assertEqual(r.headline_entities("Anthropic's Claude sent a fake tip to Philadelphia police"),
                         ["Anthropic", "Claude", "Philadelphia"])
        self.assertEqual(r.headline_entities("Apple Unveils New Smart Home Devices")[0], "Apple")


class TitleMatchTest(unittest.TestCase):
    def test_page_must_be_the_name(self):
        self.assertFalse(r._title_matches("WindBorne", "Aeolian processes"))
        self.assertFalse(r._title_matches("Haven", "Jack Haven"))
        self.assertTrue(r._title_matches("Broadcom", "Broadcom Inc."))
        self.assertTrue(r._title_matches("IMF", "International Monetary Fund"))


class ResolverTest(unittest.TestCase):
    def cuts(self, headline, body, idx=1):
        with mock.patch.object(r, "search_wikipedia_image", return_value=None):
            return [b for _, b in r.resolve_cuts_for_story(idx, headline, f"{headline} {body}", "WORLD", set())]

    def test_no_named_place_as_stand_in(self):
        stories = [
            ("Telangana minister launches Brilliance AI for schools", "The suite grades answer sheets."),
            ("Apple unveils new smart home devices", "The HomeView hub starts at 299 dollars."),
            ("World Bank jobs council urges support", "Delegates met in Bangkok."),
            ("David Pocock concerned about AI letter", "The committee wrote to the prime minister."),
        ]
        for i, (h, b) in enumerate(stories, 1):
            for badge in self.cuts(h, b, i):
                self.assertFalse(any(w in badge for w in WRONG_SETTINGS), (h, badge))

    def test_single_comparison_mention_is_not_the_subject(self):
        badges = self.cuts("Meta launches Muse Wonder models", "Meta says they match the latest OpenAI models.")
        self.assertIn("MENLO PARK • META HEADQUARTERS", badges)
        self.assertFalse(any("OPENAI" in b for b in badges))

    def test_whole_word_topic_matching(self):
        self.assertFalse(r._has_any("the bank will submit a diet plan", ["ban", "mit", "die"]))
        self.assertTrue(r._has_any("a ban on drones", ["ban"]))


if __name__ == "__main__":
    unittest.main()
