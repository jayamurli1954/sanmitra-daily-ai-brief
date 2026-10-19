import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import upload_to_youtube as u
except ImportError:  # google client libraries not installed here
    u = None


@unittest.skipIf(u is None, "google client libraries not installed")
class DescriptionDisclaimerTest(unittest.TestCase):
    def test_disclaimer_closes_the_description(self):
        d = u.with_disclaimer("Top AI stories today.\nSource: Reuters")
        self.assertTrue(d.startswith("Top AI stories today."))
        self.assertTrue(d.endswith(u.DISCLAIMER))
        self.assertIn("contact@sanmitratech.in", d)
        self.assertIn("AI-generated voices", d)

    def test_long_description_is_trimmed_not_the_disclaimer(self):
        long = "\n".join(f"Line {i} " + "x" * 80 for i in range(200))
        d = u.with_disclaimer(long)
        self.assertLessEqual(len(d), u.MAX_DESCRIPTION)
        self.assertTrue(d.endswith(u.DISCLAIMER))

    def test_added_once_and_no_angle_brackets(self):
        once = u.with_disclaimer("Watch <now>")
        self.assertEqual(u.with_disclaimer(once).count("DISCLAIMER"), 1)
        self.assertNotIn("<", once)


if __name__ == "__main__":
    unittest.main()
