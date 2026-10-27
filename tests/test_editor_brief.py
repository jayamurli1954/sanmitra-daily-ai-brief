import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.aibrief.crew.editor_brief import merge_editor_brief, parse_stories

EDITOR = """# WORLD

### UK AI minister says AI cyber-attack like Medicare breach is likely
Source: The Guardian
https://www.theguardian.com/technology/2026/oct/12/cyber-attack-uk

UK AI minister Kanishka Narayan warned that an agent-driven attack is likely, citing the Medicare breach.

# INDIA

### HCLTech signs pact with Anthropic to set up dedicated AI business unit
Source: Hindustan Times
https://www.hindustantimes.com/hcl-anthropic

HCLTech will set up a unit for agentic AI with Anthropic.
"""

COLLECTOR = """# USA

### AI minister warns 'likely' UK's cyber defences will be breached
Source: BBC
https://www.bbc.co.uk/news/uk-cyber

In a speech, Kanishka Narayan said the government's cyber defences could be breached.

### Intel, Broadcom CEOs warn capital crunch could become AI's biggest bottleneck
Source: CNBC
https://www.cnbc.com/intel-broadcom

The CEOs warned about capital.

# INDIA

### HCLTech to set up dedicated business unit for agentic AI solutions
Source: Economic Times
https://www.hindustantimes.com/hcl-anthropic

Same link as the editor's story.
"""


class EditorBriefTest(unittest.TestCase):
    def test_editor_wins_and_duplicates_become_also_sources(self):
        merged, report = merge_editor_brief(EDITOR, COLLECTOR, "2026-10-13", 15)
        self.assertEqual(report["editor"], 2)
        self.assertEqual(report["added"], 1)
        self.assertEqual(len(report["duplicates"]), 2)
        stories = parse_stories(merged)
        self.assertEqual([s["headline"] for s in stories][:2],
                         ["UK AI minister says AI cyber-attack like Medicare breach is likely",
                          "Intel, Broadcom CEOs warn capital crunch could become AI's biggest bottleneck"])
        self.assertIn("Also: BBC https://www.bbc.co.uk/news/uk-cyber", merged)
        self.assertNotIn("In a speech, Kanishka Narayan", merged)
        # Same link already present: no extra Also line for it.
        self.assertEqual(merged.count("https://www.hindustantimes.com/hcl-anthropic"), 1)

    def test_cap_fills_with_editor_stories_first(self):
        merged, report = merge_editor_brief(EDITOR, COLLECTOR, "2026-10-13", 2)
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["dropped_for_space"],
                         ["Intel, Broadcom CEOs warn capital crunch could become AI's biggest bottleneck"])

    def test_editor_stories_beyond_cap_are_dropped_in_order(self):
        merged, report = merge_editor_brief(EDITOR, COLLECTOR, "2026-10-13", 1)
        self.assertEqual([s["headline"] for s in parse_stories(merged)],
                         ["UK AI minister says AI cyber-attack like Medicare breach is likely"])
        self.assertIn("HCLTech signs pact with Anthropic to set up dedicated AI business unit", report["dropped_for_space"])

    def test_builder_reads_the_merged_brief(self):
        from build_episode_from_prompt import parse_markdown_prompt
        merged, _ = merge_editor_brief(EDITOR, COLLECTOR, "2026-10-13", 15)
        episode = parse_markdown_prompt(merged)
        heads = [s["headline"] for s in episode["stories"]]
        self.assertEqual(len(heads), 3)
        self.assertIn("Tuesday, 13 October 2026", merged)


if __name__ == "__main__":
    unittest.main()
