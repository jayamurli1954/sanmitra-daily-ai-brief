import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from build_episode_from_prompt import parse_markdown_prompt, strip_unspoken_metadata

BODY = ("French AI company Mistral has publicly released Large 4, a model designed to help organisations find and "
        "fix security flaws. The downloadable model can run on an organisation's own systems.")

# Shaped like the 30 Oct brief, whose Mistral script ended "(Themes: ...) ---" on air.
PROMPT = f"""# WORLD

### Mistral releases Large 4 with a cybersecurity focus
Source: Reuters https://www.reuters.com/technology/mistral-large-4-2026-10-29/

{BODY} (Themes: new AI models and tools; technology trends)

---

### Canada takes a stake of up to C$1.6 billion in Cohere
Source: CBC News https://www.cbc.ca/news/business/canada-cohere-ai-investment-9.7401367

{BODY} (Theme: AI policy and regulation)
"""


class UnspokenTagsTest(unittest.TestCase):
    def test_theme_tags_and_separators_are_not_spoken(self):
        for story in parse_markdown_prompt(PROMPT)["stories"]:
            self.assertNotIn("Theme", story["script"])
            self.assertNotIn("---", story["script"])
            self.assertIn("own systems", story["script"])

    def test_other_brackets_are_kept(self):
        text = strip_unspoken_metadata("The Telecom Regulatory Authority of India (TRAI) released draft rules.")
        self.assertIn("(TRAI)", text)


if __name__ == "__main__":
    unittest.main()
