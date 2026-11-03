import json
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from build_episode_from_prompt import parse_markdown_prompt
from src.aibrief.crew.story_rewriter import MARKER, rewrite_prompt_stories

PROMPT = """# SanMitra AI News Wire

## Daily AI Brief — Tuesday, 03 November 2026 (IST)

---

# WORLD

### Palantir AI tech little used by 29 NHS trusts
Lead: yes
Source: The Guardian
https://www.theguardian.com/technology/2026/nov/02/palantir-nhs

Exclusive: More than two dozen hospital trusts are not using the platform, the Guardian can reveal.
The 29 trusts listed by NHS England said the £330m system is not live.

# ASIA

### HSBC to open Hong Kong AI Institute
Source: The Economic Times
https://economictimes.indiatimes.com/tech/artificial-intelligence/hsbc-to-open-hong-kong-ai-institute/articleshow/135443900.cms

HSBC will open an AI institute in Hong Kong after Singapore.

---
"""


def fake_client(*replies):
    """A client whose beta.messages.create returns each reply ({id: text}) in turn."""
    responses = [SimpleNamespace(
        stop_reason="end_turn",
        content=[SimpleNamespace(type="text", text=json.dumps(
            {"stories": [{"id": i, "text": t} for i, t in r.items()]}))])
        for r in replies]
    create = mock.Mock(side_effect=responses)
    return SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(create=create))), create


class StoryRewriterTest(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".md")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(PROMPT)

    def tearDown(self):
        os.remove(self.path)

    def read(self):
        with open(self.path, encoding="utf-8") as f:
            return f.read()

    def test_bodies_are_replaced_and_links_kept(self):
        client, create = fake_client({
            0: "The Guardian reports that 29 trusts named by NHS England say the £330m platform is not live.",
            1: "HSBC plans an AI institute in Hong Kong, The Economic Times reports.",
        })
        self.assertEqual(rewrite_prompt_stories(self.path, client=client), [])
        md = self.read()
        self.assertNotIn("can reveal", md)
        self.assertIn("Source: The Guardian\nhttps://www.theguardian.com/technology/2026/nov/02/palantir-nhs", md)
        self.assertIn("Lead: yes", md)
        self.assertIn(MARKER, md)
        sent = json.loads(create.call_args.kwargs["messages"][0]["content"])["stories"]
        self.assertEqual([s["source"] for s in sent], ["The Guardian", "The Economic Times"])
        self.assertEqual(sent[1]["words"], 11)  # a short text asks for a short story
        stories = parse_markdown_prompt(md)["stories"]
        self.assertEqual(len(stories), 2)
        self.assertIn("HSBC plans an AI institute", " ".join(s["script"] for s in stories))

    def test_a_new_figure_is_retried_then_the_original_kept(self):
        client, create = fake_client(
            {0: "The Guardian says 31 trusts are not using it.", 1: "HSBC plans a Hong Kong institute."},
            {0: "The Guardian says 31 trusts are not using it."},
        )
        warnings = rewrite_prompt_stories(self.path, client=client)
        self.assertEqual(create.call_count, 2)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Palantir", warnings[0])
        md = self.read()
        self.assertIn("The 29 trusts listed by NHS England", md)
        self.assertIn("HSBC plans a Hong Kong institute.", md)

    def test_a_rewritten_prompt_is_not_sent_again(self):
        client, create = fake_client({0: "One.", 1: "Two."})
        rewrite_prompt_stories(self.path, client=client)
        self.assertEqual(rewrite_prompt_stories(self.path, client=client), [])
        self.assertEqual(create.call_count, 1)

    def test_api_failure_leaves_the_prompt_unchanged(self):
        create = mock.Mock(side_effect=RuntimeError("overloaded"))
        client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(create=create)))
        warnings = rewrite_prompt_stories(self.path, client=client)
        self.assertIn("NOT rewritten", warnings[0])
        self.assertEqual(self.read(), PROMPT)

    def test_no_api_key_is_a_warning(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            warnings = rewrite_prompt_stories(self.path)
        self.assertIn("no ANTHROPIC_API_KEY", warnings[0])
        self.assertEqual(self.read(), PROMPT)


if __name__ == "__main__":
    unittest.main()
