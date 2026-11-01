import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import post_to_linkedin as li
from src.aibrief.generate_linkedin_article import build_linkedin_post

EPISODE = {
    "date": "2026-11-02",
    "stories": [
        {"region": "USA", "headline": "Intel, Broadcom CEOs warn capital crunch", "source": "CNBC",
         "script": "The CEOs of Intel and Broadcom warned about capital."},
        {"region": "INDIA", "headline": "How AI exposure varies across Indian states", "source": "Mint",
         "script": "Kerala leads."},
    ],
}
TOKEN = {"access_token": "t", "person_urn": "urn:li:person:abc"}


def utc(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)


class PostTextTest(unittest.TestCase):
    def test_short_post_has_link_and_headlines_but_not_summaries(self):
        text = build_linkedin_post(EPISODE, "https://youtu.be/abc")
        self.assertIn("AI Brief — Monday, 02 November 2026 (IST)", text)
        self.assertIn("▶️ Watch today's video brief: https://youtu.be/abc", text)
        self.assertIn("🔹 USA: Intel, Broadcom CEOs warn capital crunch.", text)
        self.assertNotIn("Kerala leads", text)
        self.assertTrue(text.endswith("#OfficeMitraAIInsights"))

    def test_long_brief_is_cut_to_the_limit_by_dropping_bureaus(self):
        ep = {"date": "2026-11-02", "stories": [
            {"region": r, "headline": f"{r} headline " + "x" * 300, "source": f"S{i}"}
            for i, r in enumerate(["WORLD", "USA", "CHINA", "ASIA", "INDIA"] * 2)]}
        text = build_linkedin_post(ep, "https://youtu.be/abc")
        self.assertLessEqual(len(text), 3000)
        self.assertIn("…and more in the video.", text)
        self.assertIn("https://youtu.be/abc", text)
        self.assertIn("Subscribe on YouTube", text)

    def test_little_text_escapes_markup_and_keeps_hashtags(self):
        out = li.to_little_text("Intel (INTC) beats @x_y. #AI #IndiaAI")
        self.assertEqual(out, r"Intel \(INTC\) beats \@x\_y. {hashtag|\#|AI} {hashtag|\#|IndiaAI}")


class QueueTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        for name, sub in (("QUEUE_DIR", "queue"), ("EDITOR_DIR", "editor")):
            p = mock.patch.object(li, name, os.path.join(self.tmp.name, sub))
            p.start()
            self.addCleanup(p.stop)
        li.queue_post(EPISODE, "https://youtu.be/abc", "2026-11-02T04:00:00Z")
        self.posted = []
        for target, value in (("video_is_public", lambda url: True), ("load_token", lambda now=None: TOKEN),
                              ("publish", lambda tok, meta, text, dry: self.posted.append(text) or "https://li/p")):
            p = mock.patch.object(li, target, side_effect=value)
            p.start()
            self.addCleanup(p.stop)

    def meta(self):
        with open(os.path.join(li.QUEUE_DIR, "2026-11-02.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_not_posted_before_the_video_goes_public(self):
        self.assertTrue(li.post_queued(now=utc("2026-11-02 03:59")))
        self.assertEqual(self.posted, [])

    def test_posted_once_when_due(self):
        li.post_queued(now=utc("2026-11-02 04:05"))
        li.post_queued(now=utc("2026-11-02 04:35"))
        self.assertEqual(len(self.posted), 1)
        self.assertIn("Watch today's video brief: https://youtu.be/abc", self.posted[0])
        self.assertEqual(self.meta()["posted_url"], "https://li/p")

    def test_edited_queue_text_is_what_gets_posted(self):
        with open(os.path.join(li.QUEUE_DIR, "2026-11-02.txt"), "w", encoding="utf-8") as f:
            f.write("My own words https://youtu.be/abc\n")
        li.post_queued(now=utc("2026-11-02 04:05"))
        self.assertEqual(self.posted, ["My own words https://youtu.be/abc"])

    def test_waits_while_youtube_has_not_published(self):
        li.video_is_public.side_effect = lambda url: False
        li.post_queued(now=utc("2026-11-02 04:05"))
        self.assertEqual(self.posted, [])
        self.assertNotIn("posted_url", self.meta())

    def test_a_day_late_is_skipped_unless_forced(self):
        li.post_queued(now=utc("2026-11-03 05:00"))
        self.assertEqual(self.posted, [])
        self.assertEqual(self.meta()["skipped"], "stale")
        li.post_queued(["2026-11-02"], now=utc("2026-11-03 05:00"), force=True)
        self.assertEqual(len(self.posted), 1)

    def test_failed_post_is_reported_and_retried(self):
        li.publish.side_effect = RuntimeError("boom")
        self.assertFalse(li.post_queued(now=utc("2026-11-02 04:05")))
        self.assertNotIn("posted_url", self.meta())

    def test_own_cover_is_posted_as_the_image(self):
        os.makedirs(li.EDITOR_DIR)
        cover = os.path.join(li.EDITOR_DIR, "2026-11-02_cover.jpg")
        open(cover, "wb").close()
        self.assertEqual(li.cover_image("2026-11-02"), cover)
        meta = self.meta()
        payload = li.build_payload(TOKEN, meta, "hi", "urn:li:image:1", as_cover=True)
        self.assertEqual(payload["content"], {"media": {"id": "urn:li:image:1",
                                                        "altText": "SanMitra AI News Wire, 2026-11-02"}})
        card = li.build_payload(TOKEN, meta, "hi", "urn:li:image:2")["content"]["article"]
        self.assertEqual(card["source"], "https://youtu.be/abc")
        self.assertEqual(card["thumbnail"], "urn:li:image:2")


class ApiVersionTest(unittest.TestCase):
    def test_versions_start_last_month_and_cross_the_year(self):
        self.assertEqual(list(li.api_versions(utc("2027-02-10 00:00"))), ["202701", "202612", "202611", "202610"])


if __name__ == "__main__":
    unittest.main()
