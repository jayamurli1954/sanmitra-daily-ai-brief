import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adopt_editor_brief import adopt

EDITOR = "AI Brief — Tuesday, 20 October 2026 (IST)\n\n# WORLD\n\n### A story\nSource: Reuters https://www.reuters.com/x-2026/\n\nBody.\n"
PIPELINE = "# SanMitra AI News Wire\n\n## Daily AI Brief — Tuesday, 20 October 2026 (IST)\n\n# WORLD\n\n### A story\nBody.\n"


class AdoptEditorBriefTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.p = os.path.join(self.dir, "prompts")
        os.makedirs(self.p)

    def write(self, rel, text):
        path = os.path.join(self.p, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_editor_brief_in_prompts_is_moved(self):
        self.write("2026-10-20.md", EDITOR)
        self.assertEqual(adopt("2026-10-20", self.p), "moved")
        self.assertFalse(os.path.exists(os.path.join(self.p, "2026-10-20.md")))
        with open(os.path.join(self.p, "editor", "2026-10-20.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), EDITOR)
        self.assertTrue(os.path.exists(os.path.join(self.p, "editor", "2026-10-20.saved-in-prompts.bak")))

    def test_pipeline_brief_is_left_alone(self):
        self.write("2026-10-20.md", PIPELINE)
        self.assertEqual(adopt("2026-10-20", self.p), "pipeline")
        self.assertTrue(os.path.exists(os.path.join(self.p, "2026-10-20.md")))
        self.assertFalse(os.path.exists(os.path.join(self.p, "editor", "2026-10-20.md")))

    def test_existing_editor_file_wins(self):
        self.write("2026-10-20.md", EDITOR)
        self.write(os.path.join("editor", "2026-10-20.md"), EDITOR.replace("A story", "Editor's own"))
        self.assertEqual(adopt("2026-10-20", self.p), "editor-exists")
        with open(os.path.join(self.p, "editor", "2026-10-20.md"), encoding="utf-8") as f:
            self.assertIn("Editor's own", f.read())

    def test_editor_brief_with_a_pasted_pipeline_section_is_still_moved(self):
        pasted = EDITOR + "\n\n# SanMitra AI News Wire\n## Daily AI Brief - copy\n\n### Pasted\nBody.\n"
        self.write("2026-10-20.md", pasted)
        self.assertEqual(adopt("2026-10-20", self.p), "moved")

    def test_nothing_saved(self):
        self.assertEqual(adopt("2026-10-20", self.p), "none")


if __name__ == "__main__":
    unittest.main()
