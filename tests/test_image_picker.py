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


def offline():
    """No network: Wikipedia, Wikidata and outlet lookups return nothing."""
    return mock.patch.multiple(r, search_wikipedia_image=mock.Mock(return_value=None),
                               _subject_visuals=mock.Mock(return_value=[]),
                               _outlet_visuals=mock.Mock(return_value=[]))


class SubjectNamesTest(unittest.TestCase):
    def names(self, headline):
        return [n for n, _ in r.subject_names(headline)]

    def test_title_case_headline_yields_the_company(self):
        self.assertIn("Sarvam", self.names("Sarvam Defends Hosting Chinese AI Models, Releases Upgraded 105B Model"))
        self.assertIn("L&T Technology Services", self.names("L&T Technology Services Launches AI Toolchain"))

    def test_question_words_and_regions_are_not_names(self):
        names = self.names("How Nvidia's turnaround in China is threatened")
        self.assertNotIn("How", names)
        self.assertNotIn("China", names)
        self.assertIn("Nvidia", names)


class WikidataFilterTest(unittest.TestCase):
    def visuals(self, claims, name="Thing", subject=False):
        from src.aibrief import wikidata_visuals as w
        with mock.patch.object(w, "find_entity", return_value=("Q1", name, claims)), \
             mock.patch.object(w, "commons_file_url", side_effect=lambda f, width=1280: "https://upload.wikimedia.org/x/" + f), \
             mock.patch.object(w, "commons_logo_search", return_value=None), \
             mock.patch.object(w, "website_visuals", return_value=[]):
            return w.entity_visuals(name, is_subject_place_ok=subject)

    @staticmethod
    def c(**props):
        return {p: [{"mainsnak": {"datavalue": {"value": v}}}] for p, v in props.items()}

    def test_company_logo_comes_first_on_a_card(self):
        out = self.visuals(self.c(P154="SpaceX logo.svg", P18="HQ.jpg", P856="https://spacex.com"), "SpaceX")
        self.assertTrue(out[0][0].endswith("#logo"))
        self.assertIn("OFFICIAL LOGO", out[0][1])

    def test_concepts_and_scenery_are_rejected(self):
        self.assertEqual(self.visuals(self.c(P18="BalanceOfPower.jpg"), "Balancing"), [])
        mountain = self.c(P18="Bolnatinden.jpg", P625={"latitude": 66})
        self.assertEqual(self.visuals(mountain, "Bolna", subject=True), [])

    def test_person_needs_a_full_name(self):
        human = self.c(P18="portrait.jpg", P31={"id": "Q5"})
        self.assertEqual(self.visuals(human, "Huang"), [])
        self.assertEqual(len(self.visuals(human, "Jensen Huang")), 1)


class ResolverTest(unittest.TestCase):
    def cuts(self, headline, body, idx=1):
        with offline():
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

    def test_person_needs_headline_or_two_mentions(self):
        badges = self.cuts("Meta launches a new coding assistant", "It is pitched as a rival to Sam Altman's OpenAI.")
        self.assertNotIn("SAM ALTMAN", badges)
        self.assertEqual(self.cuts("Sam Altman says GPT-6 ships next year", "No date was given.")[0], "SAM ALTMAN")

    def test_no_generic_or_mislabelled_stand_ins(self):
        # Common words and companies whose curated photo was someone else's building.
        stories = [
            ("DeepSeek releases a reasoning model", "The model is open-weight."),
            ("Startup tests delivery drone over Pune", "The drone carries robotics kits and a GPU."),
            ("Anthropic opens a Tokyo office", "Anthropic says the data center deal is separate."),
            ("Survey shows the surface of AI adoption", "Researchers used mathematics and biology data."),
        ]
        for i, (h, b) in enumerate(stories, 1):
            for badge in self.cuts(h, b, i):
                self.assertIn("AI INTELLIGENCE WIRE", badge, (h, badge))

    def test_candidates_end_with_both_approved_fallbacks(self):
        with offline():
            cands = r.resolve_hero_candidates(1, "Google ships Gemini update", "Google said so.", "USA")
        self.assertIn("GOOGLEPLEX", cands[0][1])
        self.assertEqual([u for u, _ in cands[-2:]], list(r.FALLBACK_IMAGES))

    def test_same_hero_not_used_twice_in_an_episode(self):
        used = set()
        with offline():
            first = r.resolve_cuts_for_story(1, "Google ships Gemini update", "", "USA", used)
            second = r.resolve_cuts_for_story(2, "Google expands AI search", "", "USA", used)
        self.assertIn("GOOGLEPLEX", first[0][1])
        self.assertTrue(r.is_fallback_image(second[0][0]))

    def test_regions_are_not_looked_up(self):
        with mock.patch.object(r, "search_wikipedia_image", return_value=("x.png", "MAP")) as wiki, \
             mock.patch.object(r, "_subject_visuals", return_value=[]), \
             mock.patch.object(r, "_outlet_visuals", return_value=[]):
            r.resolve_hero_candidates(1, "Asia-Pacific regulators weigh AI rules", "", "ASIA")
        self.assertEqual(wiki.call_count, 0)

    def test_wikipedia_maps_and_scenery_are_banned(self):
        for word in ("locator_map", "flag_of", "west_lake"):
            self.assertTrue(any(k in word for k in r.BANNED_WIKI_KEYWORDS), word)

    def test_whole_word_topic_matching(self):
        self.assertFalse(r._has_any("the bank will submit a diet plan", ["ban", "mit", "die"]))
        self.assertTrue(r._has_any("a ban on drones", ["ban"]))


if __name__ == "__main__":
    unittest.main()
