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
        """Construct a high-engagement, C-suite LinkedIn intelligence dispatch."""
        stories = self.episode.get("stories", [])
        lead = stories[0] if stories else {}

        # Bucket stories by bureau
        bureaus = {}
        for s in stories:
            reg = s.get("region", "WORLD").upper()
            if reg not in bureaus:
                bureaus[reg] = []
            bureaus[reg].append(s)

        lines = []
        lines.append(f"🤖 SANMITRA AI NEWS WIRE | EXECUTIVE BRIEF")
        lines.append(f"📅 Daily Intelligence Dispatch — {self.formatted_date} (IST)\n")
        lines.append("────────────────────────────────────────\n")

        # Top Macro Hook
        lines.append("📌 TODAY'S STRATEGIC OVERVIEW:")
        lines.append(
            f"The global AI infrastructure expansion is navigating a critical recalibration across sovereign compute, "
            f"clinical model safety, and autonomous defense systems. In our lead development today, "
            f"{lead.get('headline', 'major infrastructure developments are reshaping the market')}.\n"
        )

        # Regional Breakdown
        for reg in ["WORLD", "USA", "CHINA", "ASIA", "INDIA"]:
            if reg in bureaus and bureaus[reg]:
                flag_map = {"WORLD": "🌍", "USA": "🇺🇸", "CHINA": "🇨🇳", "ASIA": "🌏", "INDIA": "🇮🇳"}
                lines.append(f"{flag_map.get(reg, '🌐')} {reg} BUREAU:")
                for s in bureaus[reg]:
                    label = " (company announcement)" if s.get("sourceType") == "company" else ""
                    lines.append(f"• {s['headline']}")
                    lines.append(f"  Source: {s.get('source', '')}{label} {s.get('sourceUrl', '')}".rstrip())
                    if s.get("whyThisMatters"):
                        lines.append(f"  Context: {s['whyThisMatters']}")
                    lines.append("")

        # Strategic Analysis for Leaders
        lines.append("💡 STRATEGIC TAKEAWAY FOR LEADERSHIP:")
        lines.append(
            "Enterprise architects and policymakers are transitioning focus from raw capability benchmarks to "
            "verifiable security, sustainable unit economics, and resilient regional supply chains. "
            "Ensuring model governance and sovereign data control remains the core operational moat for 2026.\n"
        )

        lines.append("────────────────────────────────────────")
        lines.append("📺 Full Video Broadcast & Analysis: https://www.youtube.com/@SanMitraTechSolutions")
        lines.append("#ArtificialIntelligence #AIStrategy #SovereignAI #Semiconductors #EnterpriseAI #TechPolicy #SanMitraAI")

        article_content = "\n".join(lines)

        os.makedirs(os.path.join("out", "aibrief"), exist_ok=True)
        post_path = os.path.join("out", "aibrief", f"linkedin_post_{self.date_str}.txt")
        primary_post_path = os.path.join("out", "aibrief", "linkedin_post.txt")

        with open(post_path, "w", encoding="utf-8") as f:
            f.write(article_content)
        with open(primary_post_path, "w", encoding="utf-8") as f:
            f.write(article_content)

        logger.info(f"LinkedIn executive article written to {primary_post_path}")
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
