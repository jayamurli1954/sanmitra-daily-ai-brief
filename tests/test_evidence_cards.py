import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.aibrief.evidence_cards import (build_episode_cards, build_story_cards, find_dateline, find_people,
                                        find_reported, find_stats)

CLARK = ("Speaking on Saturday at the IMF and World Bank annual meetings in Bangkok, Anthropic co-founder "
         "Jack Clark told policymakers that AI capabilities are improving rapidly. He cited an internal "
         "Anthropic model in which US economic output could approach 44 trillion dollars by 2030 in an extreme "
         "scenario, up from just over 30 trillion today.")
HUANG = ("Turning to the United States. Nvidia chief executive Jensen Huang said this week that the United States "
         "absolutely must work with Chinese AI companies. The remarks followed Nvidia's announcement of a "
         "250 million dollar, five-year commitment to AI safety research in Britain.")


def words_for(script, gap=0.4):
    return [{"word": w, "start": 10 + i * gap, "end": 10 + i * gap + 0.3, "sceneId": "s1", "sceneStart": 9.8}
            for i, w in enumerate(script.split())]


class EvidenceCardsTest(unittest.TestCase):
    def test_dateline_only_for_known_places(self):
        self.assertEqual(find_dateline(CLARK)["place"], "BANGKOK")
        self.assertIsNone(find_dateline("The company said its new model is faster."))
        dl = find_dateline("Speaking in London on 16 October, the minister said so.")
        self.assertEqual((dl["place"], dl["date"]), ("LONDON", "16 OCTOBER"))

    def test_people_with_titles_and_orgs(self):
        self.assertEqual([(p["name"], p["role"]) for p in find_people(HUANG)],
                         [("JENSEN HUANG", "Chief executive, Nvidia")])
        self.assertEqual([(p["name"], p["role"]) for p in find_people(CLARK)],
                         [("JACK CLARK", "Co-founder, Anthropic")])
        people = find_people("Senator Bernie Sanders and Representative Greg Casar filed a bill.")
        self.assertEqual([p["role"] for p in people], ["US Senator", "US Representative"])

    def test_two_like_amounts_become_a_comparison(self):
        stats = find_stats(CLARK)
        self.assertEqual(stats[0]["type"], "compare")
        self.assertEqual([i["shown"] for i in stats[0]["items"]], ["$44 TRILLION", "$30 TRILLION+"])

    def test_stats_skip_dates_versions_and_hyphenated_words(self):
        self.assertEqual(find_stats("DeepSeek V4.1 Flash 1017 is live from 17 October with five-year plans."), [])
        stat = find_stats(HUANG)[0]
        self.assertEqual((stat["shown"], stat["label"]), ("$250 MILLION", "five-year commitment to AI safety research in…"))
        self.assertEqual(find_stats("It ran more than 180 trials over five years.")[0]["shown"], "180+")
        self.assertEqual(find_stats("It uses about seventeen times fewer gates.")[0]["shown"], "17×")

    def test_reported_card_highlights_the_claim_and_never_adds_quotes(self):
        rep = find_reported(HUANG, "CNBC", [])
        self.assertEqual(rep["type"], "reported")
        self.assertTrue(rep["highlight"].startswith("the United States absolutely must"))
        self.assertIn(rep["highlight"], rep["text"])
        quoted = find_reported('Clark called the figure "very outlandish but worth planning for" on stage.', "Reuters", [])
        self.assertEqual(quoted["type"], "quote")

    def test_cards_are_timed_to_the_words_and_do_not_overlap(self):
        cards = build_story_cards({"script": HUANG, "source": "CNBC"}, [
            dict(w, rel=round(w["start"] - 9.8, 3)) for w in words_for(HUANG)])
        big = [c for c in cards if c["type"] in ("reported", "stat", "compare", "quote")]
        self.assertTrue(big)
        for a, b in zip(big, big[1:]):
            self.assertGreaterEqual(b["start"], a["end"])
        stat = [c for c in cards if c["type"] == "stat"][0]
        idx = HUANG.split().index("250")
        self.assertAlmostEqual(stat["start"], 0.2 + idx * 0.4 - 0.2, places=1)

    def test_episode_uses_scene_start(self):
        ep = {"stories": [{"id": "s1", "script": HUANG, "source": "Yahoo Finance , Reuters"}]}
        cards = build_episode_cards(ep, words_for(HUANG))
        self.assertIn("s1", cards)
        self.assertTrue(all(c["start"] >= 0 for c in cards["s1"]))
        self.assertTrue(all(c.get("source", "CNBC") != "Yahoo Finance , Reuters" for c in cards["s1"]))


if __name__ == "__main__":
    unittest.main()
