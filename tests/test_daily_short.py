import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import make_short

EPISODE = {
    "stories": [
        {
            "headline": "Anthropic's Claude sent a fake murder tip to Philadelphia police",
            "script": "Our lead story today. " + " ".join(["Anthropic found the tip two months later."] * 30),
            "whyThisMatters": "Police called the delay unacceptable.",
            "source": "RNZ (ABC News)",
            "visualCuts": [{"image": f"aibrief/assets/editorial/x/s1_cut{i}.jpg", "badge": f"CUT {i}"} for i in (1, 2, 3)],
        },
        {"headline": "Second story", "script": "Also today. Something else.", "source": "X", "visualCuts": []},
    ]
}


class DailyShortTest(unittest.TestCase):
    def test_spec_uses_the_lead_story(self):
        spec = make_short.spec_from_episode(EPISODE, "2026-10-15")
        self.assertEqual(spec["headline"], EPISODE["stories"][0]["headline"])
        self.assertEqual([i["label"] for i in spec["images"]], ["CUT 1", "CUT 2", "CUT 3"])
        self.assertEqual(spec["storiesToday"], 2)

    def test_script_drops_lead_in_stays_short_and_signs_off(self):
        script = make_short.spec_from_episode(EPISODE, "2026-10-15")["script"]
        self.assertFalse(script.startswith("Our lead story"))
        self.assertTrue(script.endswith(make_short.SIGN_OFF))
        self.assertLessEqual(len(script.replace(make_short.SIGN_OFF, "").split()), make_short.SHORT_MAX_WORDS)

    def test_platform_texts_link_the_full_episode(self):
        import tempfile
        spec = make_short.spec_from_episode(EPISODE, "2026-10-15")
        d = tempfile.mkdtemp()
        yt, ig = make_short.write_platform_texts(spec, "https://youtu.be/abc123", out_dir=d)
        yt_text, ig_text = open(yt, encoding="utf-8").read(), open(ig, encoding="utf-8").read()
        self.assertIn("#Shorts", yt_text.split("DESCRIPTION:")[0])
        self.assertIn("https://youtu.be/abc123", yt_text)
        self.assertIn("Link in bio", ig_text)


if __name__ == "__main__":
    unittest.main()
