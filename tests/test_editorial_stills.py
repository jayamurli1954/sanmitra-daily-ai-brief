import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from download_daily_editorial_visuals import STORY_MANIFEST, stills_match_episode


class StillsMatchTest(unittest.TestCase):
    def folder(self, headlines, stories_on_disk):
        d = tempfile.mkdtemp()
        for i in range(1, stories_on_disk + 1):
            for c in (1, 2, 3):
                open(os.path.join(d, f"s{i}_cut{c}.jpg"), "wb").close()
        if headlines is not None:
            with open(os.path.join(d, STORY_MANIFEST), "w", encoding="utf-8") as f:
                json.dump(headlines, f)
        return d

    def test_same_stories_reuse_stills(self):
        heads = ["A", "B"]
        self.assertTrue(stills_match_episode(self.folder(heads, 2), heads))

    def test_different_story_list_downloads_again(self):
        self.assertFalse(stills_match_episode(self.folder(["A", "B"], 2), ["C", "B"]))

    def test_old_folder_without_manifest_downloads_again(self):
        self.assertFalse(stills_match_episode(self.folder(None, 9), ["A"] * 9))

    def test_missing_cuts_for_longer_episode(self):
        heads = ["A"] * 15
        self.assertFalse(stills_match_episode(self.folder(heads, 9), heads))


if __name__ == "__main__":
    unittest.main()
