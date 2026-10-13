import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate_subtitles import align_to_script, group_caption_words


def heard(text, start=0.0, step=0.5):
    return [{"word": w, "start": start + i * step, "end": start + (i + 1) * step} for i, w in enumerate(text.split())]


class SubtitleTest(unittest.TestCase):
    def test_script_spelling_replaces_misheard_names(self):
        h = heard("chair Joe Briski and liberal senator John O 'Donne I .M., sent the letter")
        words = align_to_script(h, "chair Jo Briskey and Liberal senator Jonno Duniam sent the letter")
        self.assertEqual(" ".join(w["word"] for w in words),
                         "chair Jo Briskey and Liberal senator Jonno Duniam sent the letter")
        self.assertEqual(words[0]["start"], 0.0)
        self.assertEqual(words[-1]["end"], h[-1]["end"])
        self.assertTrue(all(a["end"] <= b["start"] + 1e-6 for a, b in zip(words, words[1:])))

    def test_unheard_script_words_fill_the_gap(self):
        words = align_to_script(heard("the minister spoke today"), "the UK minister spoke today")
        self.assertEqual([w["word"] for w in words], ["the", "UK", "minister", "spoke", "today"])
        self.assertLessEqual(words[1]["end"], words[2]["end"])

    def test_phrases_fit_one_line_and_break_at_pauses(self):
        text = ("Notes on the letter to Albanese, seen by Guardian Australia, show a senior adviser "
                "made multiple edits and wrote fine on some content. Some edits were made late.")
        groups = [" ".join(w["word"] for w in g) for g in group_caption_words(heard(text))]
        self.assertTrue(all(len(g) <= 56 for g in groups))
        self.assertEqual(groups[0], "Notes on the letter to Albanese,")
        self.assertTrue(groups[3].endswith("content."))


if __name__ == "__main__":
    unittest.main()
