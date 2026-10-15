import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validate_episode_sources import is_proper_article_url


class ArticleUrlTest(unittest.TestCase):
    def test_xinhua_links_are_articles(self):
        for url in ["https://www.news.cn/tech/20261015/85fa980638564c15a746cd5a7b704373/c.html",
                    "https://english.news.cn/20260514/0d4e1f2a3b5c4d6e8f9a0b1c2d3e4f5a/c.html"]:
            self.assertTrue(is_proper_article_url(url), url)

    def test_ordinary_articles_still_pass(self):
        for url in ["https://www.reuters.com/technology/microsoft-unveils-maia-300-chip-2026-10-14/",
                    "https://example.com/news?id=123456"]:
            self.assertTrue(is_proper_article_url(url), url)

    def test_homepages_and_cut_off_slugs_are_rejected(self):
        for url in ["", "https://reuters.com", "https://reuters.com/", "https://sanmitra.ai",
                    "https://www.news.cn/", "ftp://example.com/story-about-ai",
                    "https://www.theverge.com/ai/She", "https://www.news.cn/tech/c.html",
                    "https://www.news.cn/tech/20261015/She"]:
            self.assertFalse(is_proper_article_url(url), url)


if __name__ == "__main__":
    unittest.main()
