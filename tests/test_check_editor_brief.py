import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import check_editor_brief as c

BODY = ("The company said the system is now in use across several states. Officials described the rollout as a "
        "first step and said more details would follow next month after a review of early results and costs.")


def run(md):
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "2026-10-15.md"), "w", encoding="utf-8") as f:
        f.write(md)
    out = io.StringIO()
    with redirect_stdout(out):
        code = c.check("2026-10-15", editor_dir=d)
    return code, out.getvalue()


class CheckEditorBriefTest(unittest.TestCase):
    def test_good_brief_passes_and_names_the_lead(self):
        code, out = run(f"# WORLD\n\n### Nvidia commits $250 million to UK AI safety\n"
                        f"Source: NVIDIA https://nvidianews.nvidia.com/news/uk-safety\n\n{BODY}\n")
        self.assertEqual(code, 0, out)
        self.assertIn("Lead story (opens the episode and becomes the Short): Nvidia commits", out)

    def test_story_without_link_is_flagged(self):
        code, out = run(f"# WORLD\n\n### Scientists call for international AI body\nSource: The Indian Express\n\n{BODY}\n")
        self.assertEqual(code, 1)
        self.assertIn("no link", out)

    def test_stock_market_headline_is_flagged(self):
        _, out = run(f"# ASIA\n\n### Chip stocks slide after Broadcom remarks\n"
                     f"Source: The Guardian https://www.theguardian.com/business/chip-stocks\n\n{BODY}\n")
        self.assertIn("stock-market headline", out)

    def test_subscription_site_link_is_flagged(self):
        code, out = run(f"# USA\n\n### OpenAI claims its models disproved a complexity hypothesis\n"
                        f"Source: The Verge https://www.theverge.com/ai-artificial-intelligence/1019143/openai-eth\n"
                        f"Also: Decrypt https://decrypt.co/381956/openai-eth-false\n\n{BODY}\n")
        self.assertEqual(code, 1)
        self.assertIn("subscription site (theverge.com)", out)

    def test_free_form_layout_explains_the_format(self):
        code, out = run("AI Brief\n1. World - AI safety\nNvidia pledges $250 million\nSource: Reuters - headline\n")
        self.assertEqual(code, 1)
        self.assertIn("No stories found", out)
        self.assertIn("### Headline of the story", out)


if __name__ == "__main__":
    unittest.main()
