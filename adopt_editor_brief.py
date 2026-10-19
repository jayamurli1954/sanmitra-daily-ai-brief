"""
Move an editor's brief saved in the wrong folder before the nightly run overwrites it.

    python adopt_editor_brief.py --date 2026-10-20

The editor's brief belongs in prompts/editor/<date>.md. When it is saved as
prompts/<date>.md instead, the collector would overwrite it with the night's
harvest. This moves it to prompts/editor/<date>.md first (keeping a .bak copy).

Files the pipeline wrote itself (collector, editor merge, weekly round-up) carry
a "## Daily AI Brief" or "## Weekly Round-up" heading and are left alone, so a
rerun never mistakes the night's own brief for the editor's.
"""

import argparse
import os
import re
import shutil
import sys

PIPELINE_HEADING = re.compile(r"(?im)^##\s*(Daily AI Brief|Weekly Round-up)\b")


def adopt(date, prompts_dir="prompts"):
    misplaced = os.path.join(prompts_dir, f"{date}.md")
    editor = os.path.join(prompts_dir, "editor", f"{date}.md")
    if not os.path.exists(misplaced):
        return "none"
    with open(misplaced, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    if PIPELINE_HEADING.search(text) or "### " not in text:
        return "pipeline"  # written by the run itself, or not a brief at all
    if os.path.exists(editor):
        print(f"[!] {misplaced} looks like an editor's brief, but {editor} already exists; using {editor}.")
        return "editor-exists"
    os.makedirs(os.path.dirname(editor), exist_ok=True)
    shutil.copyfile(misplaced, editor)
    shutil.copyfile(misplaced, os.path.join(prompts_dir, "editor", f"{date}.saved-in-prompts.bak"))
    os.remove(misplaced)
    print(f"[+] Moved the editor's brief {misplaced} -> {editor}")
    return "moved"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Move an editor's brief saved in prompts/ into prompts/editor/")
    parser.add_argument("--date", required=True, help="The episode date (YYYY-MM-DD)")
    adopt(parser.parse_args().date)
    sys.exit(0)
