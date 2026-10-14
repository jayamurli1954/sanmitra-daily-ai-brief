"""
LinkedInPublisher Agent - SanMitra AI News Wire v7.0
Autonomous generation of executive LinkedIn dispatches and high-resolution cover banner rendering.
"""

import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LinkedInPublisher")


class LinkedInPublisher:
    """Produces the formatted LinkedIn executive newsletter and renders the 1920x1080 cover banner."""

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

    def render_cover_banner(self):
        """Render high-resolution 1920x1080 LinkedIn Cover Banner via Remotion."""
        out_banner = os.path.join("out", "aibrief", f"linkedin_cover_{self.date_str}.png")
        primary_banner = os.path.join("out", "aibrief", "linkedin_cover.png")

        cmd = f'npx remotion still AIBriefLinkedInCover {out_banner}'
        logger.info(f"Rendering LinkedIn cover banner: {cmd}")
        res = subprocess.run(cmd, shell=True)

        if res.returncode == 0 and os.path.exists(out_banner):
            import shutil
            shutil.copyfile(out_banner, primary_banner)
            logger.info(f"LinkedIn cover banner successfully generated: {primary_banner}")
            return primary_banner
        else:
            logger.warning(f"Failed to render Remotion LinkedIn cover banner (code: {res.returncode})")
            return None

    def publish_deliverables(self):
        """Generate both text article and visual banner."""
        text_file = self.generate_article_text()
        banner_file = self.render_cover_banner()
        return {"article": text_file, "banner": banner_file}
