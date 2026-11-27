import os
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.aibrief import breaking_wire as b


class WireWindowTest(unittest.TestCase):
    def tearDown(self):
        b._TARGET_DATE["date"] = None

    def test_window_follows_the_episode_date_not_the_clock(self):
        # 21:30 IST the day before to 21:30 IST on the day, whenever the run starts:
        # on 27 Nov a 22:25 run looked only at news since 21:30 that night.
        self.assertEqual(b.window_start("2026-11-27"), datetime(2026, 11, 26, 16, 0, tzinfo=timezone.utc))
        self.assertEqual(b.window_end("2026-11-27"), datetime(2026, 11, 27, 16, 0, tzinfo=timezone.utc))

    def test_collect_sets_the_date_for_the_feed_filter(self):
        b._TARGET_DATE["date"] = "2026-11-25"
        self.assertEqual(b.window_start(), datetime(2026, 11, 24, 16, 0, tzinfo=timezone.utc))
        b._TARGET_DATE["date"] = None
        self.assertIsNone(b.window_end())


if __name__ == "__main__":
    unittest.main()
