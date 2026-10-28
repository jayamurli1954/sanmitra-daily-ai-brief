import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from build_episode_from_prompt import extract_attribution, parse_markdown_prompt
from src.aibrief.breaking_wire import AI_PATTERN, BREAKING_PATTERN, WIRE_FEEDS
from src.aibrief.crew.text_utils import is_non_english_url, is_stock_market_story, source_link_problem

BODY = ("The company said the system is now in use across several states. Officials described the rollout as a "
        "first step and said more details would follow next month after a review of early results and costs.")


class EnglishLinksTest(unittest.TestCase):
    def test_non_english_pages(self):
        for u in ["https://finance.eastmoney.com/a/202610283911774416.html", "https://news.aibase.cn/news/31918",
                  "https://www.news.cn/tech/20261027/8b2cddf82be14e7c9b11576cb17a6b4a/c.html",
                  "https://www.etnews.com/20261023000175", "https://36kr.com/p/3456789012345",
                  "https://example.com/news/%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD"]:
            self.assertTrue(is_non_english_url(u), u)
        for u in ["https://english.news.cn/asiapacific/20261027/8b2cddf82be14e7c9b11576cb17a6b4a/c.html",
                  "https://eu.36kr.com/en/p/4026608875360646", "https://technode.com/2026/10/27/tencent-model/",
                  "https://pandaily.com/ant-group-ling-3-1-flash-1019", "https://www.chinadaily.com.cn/a/202610/28/WS1.html",
                  "https://en.yna.co.kr/view/AEN20261028000300320", ""]:
            self.assertFalse(is_non_english_url(u), u)

    def test_link_problems(self):
        self.assertEqual(source_link_problem("https://www.straitstimes.com/tech/singapore-ai-pilot"), "subscription site")
        self.assertEqual(source_link_problem("https://news.aibase.cn/news/31918"), "not in English")
        self.assertEqual(source_link_problem("https://techcrunch.com/2026/10/28/korea-cyberattacks/"), "")

    def test_english_also_link_replaces_a_chinese_source(self):
        srcs, url, _ = extract_attribution("Head\nSource: AIbase https://news.aibase.cn/news/31918\n"
                                           "Also: Pandaily https://pandaily.com/ant-group-ling-3-1-flash-1019\n")
        self.assertEqual((srcs, url), (["Pandaily"], "https://pandaily.com/ant-group-ling-3-1-flash-1019"))

    def test_story_with_only_chinese_links_is_left_out(self):
        md = (f"# CHINA\n\n### DiffuSpace open-sources a 35B diffusion language model\n"
              f"Source: Eastmoney https://finance.eastmoney.com/a/202610283911774416.html\n\n{BODY}\n\n"
              f"### Tencent open-sources a real-time interpretation model\n"
              f"Source: TechNode https://technode.com/2026/10/27/tencent-open-sources-interpretation-model/\n\n{BODY}\n")
        heads = [s["headline"] for s in parse_markdown_prompt(md)["stories"]]
        self.assertEqual(heads, ["Tencent open-sources a real-time interpretation model"])


class StockMarketTest(unittest.TestCase):
    def test_stock_rally_and_ipo_slug(self):
        self.assertTrue(is_stock_market_story("Jim Cramer warns investors not to get fooled by the latest AI stock rally"))
        # The headline alone reads like AI industry news; the link says it is about the IPO.
        self.assertTrue(is_stock_market_story("Chart: Anthropic's cash pile towers over nearly every U.S. company",
                                              "https://www.cnbc.com/2026/10/27/anthropic-cash-investments-ipo.html"))
        self.assertFalse(is_stock_market_story("Microsoft unveils Maia 300 chip for its AI services",
                                               "https://techcrunch.com/2026/10/09/microsoft-maia-300-chip"))


class WireFeedsTest(unittest.TestCase):
    def test_free_china_asia_india_feeds(self):
        sources = {f["source"] for f in WIRE_FEEDS}
        self.assertTrue({"TechNode", "Pandaily", "Tech in Asia", "Inc42"} <= sources)

    def test_model_releases_count_as_ai_breaks(self):
        lead = "Ant Group Open-Sources Ling-3.1-flash-1019, a language model tuned for personal agents"
        self.assertTrue(AI_PATTERN.search(lead))
        self.assertTrue(BREAKING_PATTERN.search(lead))


if __name__ == "__main__":
    unittest.main()
