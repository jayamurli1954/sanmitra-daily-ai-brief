import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from build_episode_from_prompt import parse_markdown_prompt
from src.aibrief.crew.editor_brief import merge_editor_brief

BODY = ("The company said the system is now in use across several states. Officials described the rollout as "
        "a first step and said more details would follow next month after a review of early results.")

EDITOR = f"""# INDIA

### SquadStack launches Arth V2 speech model for Indian sales calls
Source: ETEnterpriseAI
https://enterpriseai.economictimes.indiatimes.com/news/squadstack-arth-v2/134895943

{BODY}

# WORLD

### Airbus flies the Valkyrie uncrewed combat jet in Europe
Source: Airbus
https://www.airbus.com/en/newsroom/press-releases/2026-10-valkyrie

{BODY}
"""

COLLECTOR = f"""# USA

### Microsoft unveils Maia 300 chip for its AI services
Lead: yes
Source: TechCrunch
https://techcrunch.com/2026/10/09/microsoft-maia-300

{BODY}
"""


class LeadStoryTest(unittest.TestCase):
    def episode(self):
        merged, _ = merge_editor_brief(EDITOR, COLLECTOR, "2026-10-15", 9)
        return merged, parse_markdown_prompt(merged)

    def test_editor_first_story_leads_whatever_its_region(self):
        merged, ep = self.episode()
        self.assertEqual(ep["stories"][0]["headline"], "SquadStack launches Arth V2 speech model for Indian sales calls")
        self.assertEqual(merged.count("Lead: yes"), 1)

    def test_intro_opens_on_the_lead_and_the_mark_is_not_spoken(self):
        _, ep = self.episode()
        self.assertTrue(ep["intro"]["script"].startswith("Breaking this morning: SquadStack launches Arth V2"))
        self.assertTrue(all("Lead" not in s["script"] for s in ep["stories"]))

    def test_without_editor_the_collector_lead_opens(self):
        ep = parse_markdown_prompt(COLLECTOR + "\n# WORLD\n\n### Airbus flies the Valkyrie uncrewed combat jet in Europe\n"
                                   "Source: Airbus\nhttps://www.airbus.com/en/newsroom/press-releases/2026-10-valkyrie\n\n" + BODY)
        self.assertEqual(ep["stories"][0]["headline"], "Microsoft unveils Maia 300 chip for its AI services")


if __name__ == "__main__":
    unittest.main()
