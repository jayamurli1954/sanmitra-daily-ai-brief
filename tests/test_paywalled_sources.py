import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from build_episode_from_prompt import extract_attribution, parse_markdown_prompt
from src.aibrief.breaking_wire import WIRE_FEEDS
from src.aibrief.crew.news_harvester import FEEDS
from src.aibrief.crew.text_utils import is_paywalled_url

BODY = ("The company said the system is now in use across several states. Officials described the rollout as a "
        "first step and said more details would follow next month after a review of early results and costs.")


class PaywalledSourcesTest(unittest.TestCase):
    def test_subscription_sites(self):
        for u in ["https://www.theverge.com/ai-artificial-intelligence/1019143/openai-eth",
                  "https://www.thehindu.com/news/national/karnataka/ciil/article71631788.ece",
                  "https://www.scmp.com/tech/article/3371925/ai-engineer", "https://asia.nikkei.com/x/y",
                  "https://economictimes.indiatimes.com/prime/technology/ai-story/primearticleshow/1.cms"]:
            self.assertTrue(is_paywalled_url(u), u)
        for u in ["https://techcrunch.com/2026/10/27/general-compute/", "https://decrypt.co/381956/openai-eth",
                  "https://www.hindustantimes.com/india-news/sarvam-101793088900459.html",
                  "https://economictimes.indiatimes.com/tech/artificial-intelligence/up-park/articleshow/1.cms",
                  "https://www.theverge.com.example.org/x", ""]:
            self.assertFalse(is_paywalled_url(u), u)

    def test_collectors_use_no_subscription_feeds(self):
        for feed in FEEDS + WIRE_FEEDS:
            self.assertFalse(is_paywalled_url(feed["url"]), feed["url"])

    def test_free_also_link_replaces_a_subscription_source(self):
        srcs, url, _ = extract_attribution("Head\nSource: The Verge https://www.theverge.com/ai/1019143/openai-eth\n"
                                           "Also: Decrypt https://decrypt.co/381956/openai-eth-false\n")
        self.assertEqual((srcs, url), (["Decrypt"], "https://decrypt.co/381956/openai-eth-false"))
        srcs, url, _ = extract_attribution("Head\nSource: TechCrunch https://techcrunch.com/2026/10/27/a-b/\n"
                                           "Also: The Verge https://www.theverge.com/ai/1019143/x\n")
        self.assertEqual((srcs, url), (["TechCrunch"], "https://techcrunch.com/2026/10/27/a-b/"))

    def test_story_with_only_subscription_links_is_left_out(self):
        md = (f"# INDIA\n\n### CIIL releases open-source speech AI\n"
              f"Source: The Hindu https://www.thehindu.com/news/national/ciil/article71631788.ece\n\n{BODY}\n\n"
              f"### Sarvam signs a deal with the armed forces\n"
              f"Source: Hindustan Times https://www.hindustantimes.com/india-news/sarvam-101793088900459.html\n\n{BODY}\n")
        heads = [s["headline"] for s in parse_markdown_prompt(md)["stories"]]
        self.assertEqual(heads, ["Sarvam signs a deal with the armed forces"])


if __name__ == "__main__":
    unittest.main()
