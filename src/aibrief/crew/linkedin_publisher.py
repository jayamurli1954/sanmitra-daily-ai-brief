"""
LinkedInPublisher Agent - SanMitra AI News Wire v7.0
Autonomous generation of executive LinkedIn dispatches.
"""

import logging
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LinkedInPublisher")


class LinkedInPublisher:
    """Produces the formatted LinkedIn executive newsletter."""

    def __init__(self, episode_payload):
        self.episode = episode_payload
        self.date_str = episode_payload.get("date", "")
        self.formatted_date = episode_payload.get("formattedDate", "")

    def generate_article_text(self):
        """The LinkedIn article, built only from the episode's stories.

        This used to add fixed paragraphs ("navigating a critical recalibration
        across sovereign compute, clinical model safety...") whatever the news.
        The video link is added after upload (run_autonomous_brief.py)."""
        from src.aibrief.generate_linkedin_article import build_linkedin_article
        primary_post_path = os.path.join("out", "aibrief", "linkedin_post.txt")
        build_linkedin_article(episode=self.episode,
                               output_article_path=os.path.join("out", "aibrief", "linkedin_article.md"),
                               output_post_path=primary_post_path)
        logger.info(f"LinkedIn article written to {primary_post_path}")
        return primary_post_path

    def publish_deliverables(self):
        """Generate the article text. No cover image: the editor makes the
        LinkedIn cover by hand (AIBriefLinkedInCover can still be rendered
        manually with `npx remotion still`)."""
        return {"article": self.generate_article_text()}
