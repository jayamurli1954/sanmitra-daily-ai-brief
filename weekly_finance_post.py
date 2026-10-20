"""
Monday's LinkedIn post for finance and accounting readers: "AI for Accountants".

    python weekly_finance_post.py --date 2026-10-26      # the Monday it is posted

Reads the episodes that aired in the seven days before that Monday
(src/aibrief/data/aired/<date>.json), picks the stories that matter most to
accountants, CFOs and auditors, and writes a ready-to-paste post to
out/aibrief/linkedin_finance_weekly_<monday>.md.

Each story keeps its own facts (headline, the script's opening sentence and
source). The "What it means" line is the channel's practical guidance for its
theme, never a claim about the story. Run by the nightly job every night; it
only writes on Mondays.
"""

import argparse
import glob
import json
import os
import re
from datetime import datetime, timedelta

from src.aibrief.crew.text_utils import contains_any, is_election_story, is_stock_market_story
from src.aibrief.generate_linkedin_article import clean_summary

AIRED_DIR = os.path.join("src", "aibrief", "data", "aired")
OUT_DIR = os.path.join("out", "aibrief")
CHANNEL_URL = "https://www.youtube.com/@SanMitraTechSolutions"
MAX_STORIES = 4
LINKEDIN_LIMIT = 3000

# Theme -> (keywords, what it means for accountants). First match wins, so the
# most specific themes come first.
THEMES = [
    ("access", ["ai agent", "ai agents", "agentic", "autonomous agent", "unauthorised", "unauthorized", "breach", "insider", "insiders",
                "credentials", "intrusion", "intrusions"],
     "Review what AI tools and automations can reach in your accounting and client systems. Give them the least access they need and keep access logs."),
    ("tax", ["tax", "gst", "tds", "income tax", "customs duty", "tariff", "trade marks registry", "filing", "filings"],
     "Tax and filing rules are starting to cover AI. Note where AI touches a return or a filing, and keep the working papers that show how each figure was reached."),
    ("audit", ["audit", "auditor", "auditors", "assurance", "traceability", "misalignment", "incident", "incidents", "disclosure"],
     "Auditors and regulators will ask how AI-produced numbers were checked. Keep every figure linked to its source document and record who reviewed it."),
    ("privacy", ["personal data", "privacy", "confidential", "data protection", "dpdp", "leak", "leaked"],
     "Do not paste confidential client data into public AI tools. Check where your AI vendor stores and trains on the data you upload."),
    ("software", ["erp", "sap", "oracle", "tally", "intuit", "quickbooks", "xero", "workday", "copilot", "excel", "spreadsheet",
                  "forecasting", "accounting software"],
     "Accounting and ERP software is gaining AI features. Trial them on a copy of real data and compare the output with your own before relying on it."),
    ("jobs", ["jobs", "hiring", "workforce", "entry-level", "skills", "employment", "workers", "staff"],
     "Routine entry-level work is changing first. Train junior staff in review, judgement and client communication, not only data entry."),
    ("payments", ["banks", "banking", "bank account", "bank accounts", "payment", "payments", "fintech", "upi", "rbi", "lending", "credit", "kyc", "invoice", "invoices"],
     "Banking and payment processes are adopting AI. Expect changes to reconciliation, KYC and invoice workflows, and keep manual checks on exceptions."),
    ("cost", ["price", "prices", "pricing", "cheaper", "cost", "costs", "budget", "subscription"],
     "AI prices are falling quickly. Budget for AI tools by usage and revisit the costs every quarter."),
    ("regulation", ["regulation", "regulator", "regulators", "rules", "law", "act", "framework", "guidelines", "standards", "compliance"],
     "New AI rules are arriving. Keep a simple register of the AI tools your firm uses, what data they see and who approved them."),
]
FUNDING = re.compile(r"\b(raises|raised|raising|funding round|valuation|series [a-f])\b", re.I)
FINANCE_WORDS = sorted({w for _, words, _ in THEMES for w in words} | {
    "accounting", "accountant", "accountants", "finance", "financial", "cfo", "chartered accountant", "ca firms",
    "business", "businesses", "enterprise", "enterprises", "company records", "records", "ledger", "bookkeeping"})


def _first_sentence(text, max_chars=300):
    text = re.sub(r"^(Turning to [^.]+\.|Now to [^.]+\.|In another development,?|Elsewhere,?)\s*", "", (text or "").strip())
    text = clean_summary(text)  # the anchor's spoken link-ins ("Expanding on ..., ")
    first = re.split(r"(?<=[.!?])\s+", text)[0] if text else ""
    return first if len(first) <= max_chars else first[:max_chars].rsplit(" ", 1)[0] + "…"


def relevance(story):
    head, body = story.get("headline", ""), story.get("script", "")
    hits = lambda text: sum(1 for w in FINANCE_WORDS if contains_any(text, [w]))
    return 3 * hits(head) + hits(body)


def theme_of(story):
    text = f"{story.get('headline', '')} {story.get('script', '')}"
    head = story.get("headline", "")
    # A theme named in the headline beats one only mentioned in the script.
    for scope in (head, text):
        for name, words, line in THEMES:
            if contains_any(scope, words):
                return name, line
    return None, None


def week_before(monday):
    day = datetime.strptime(monday, "%Y-%m-%d")
    return [(day - timedelta(days=n)).strftime("%Y-%m-%d") for n in range(7, 0, -1)]


def episode_link(date):
    """The day's episode link, from that day's LinkedIn article."""
    path = os.path.join(OUT_DIR, f"linkedin_article_{date}.md")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        m = re.search(r"https://youtu\.be/[\w-]{11}", f.read())
    return m.group(0) if m else None


def pick_stories(monday):
    rows = []
    for date in week_before(monday):
        path = os.path.join(AIRED_DIR, f"{date}.json")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            for s in json.load(f).get("stories", []):
                if is_stock_market_story(s.get("headline", "")) or is_election_story(s.get("headline", ""), s.get("script", "")):
                    continue
                if FUNDING.search(s.get("headline", "")):
                    continue  # who raised how much is investor news, not something accountants act on
                theme, line = theme_of(s)
                score = relevance(s)
                if theme and score >= 3:
                    rows.append({"date": date, "story": s, "theme": theme, "line": line, "score": score})
    rows.sort(key=lambda r: r["score"], reverse=True)
    picked, themes, heads = [], set(), set()
    for r in rows:  # one story per theme keeps the post varied
        head = r["story"]["headline"].lower()
        if r["theme"] in themes or head in heads:
            continue
        picked.append(r)
        themes.add(r["theme"])
        heads.add(head)
        if len(picked) == MAX_STORIES:
            break
    return sorted(picked, key=lambda r: r["date"])


def render(monday, picked):
    days = week_before(monday)
    first = datetime.strptime(days[0], "%Y-%m-%d")
    last = datetime.strptime(days[-1], "%Y-%m-%d")
    numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    lines = [
        f"🧾 AI for Accountants: the week of {first.day} to {last.day} {last.strftime('%B %Y')}",
        "",
        f"{len(picked)} AI developments from our daily SanMitra AI News Wire that matter for finance and accounting professionals:",
        "",
    ]
    for n, r in zip(numbers, picked):
        s = r["story"]
        # The summary comes from the script: whyThisMatters is stored already cut short.
        lines += [f"{n} {s['headline'].strip()}",
                  _first_sentence(s.get("script") or s.get("whyThisMatters", "")),
                  f"👉 What it means for accountants: {r['line']}"]
        if s.get("source"):
            source = re.sub(r"\s+,\s+", " / ", s["source"].strip())
            lines.append(f"Source: {source}")
        link = episode_link(r["date"])
        if link:
            lines.append(f"▶️ {link}")
        lines.append("")
    lines += [
        "Which of these is already showing up in your firm or finance team? I would like to hear in the comments.",
        "",
        f"🔔 The daily AI brief, every morning at 9:30 AM IST: {CHANNEL_URL}",
        "",
        "#Accounting #Finance #CharteredAccountants #AIinFinance #Audit #SanMitraAINewsWire",
    ]
    text = "\n".join(lines)
    while len(text) > LINKEDIN_LIMIT and len(picked) > 2:  # drop the last story rather than cut one short
        return render(monday, picked[:-1])
    return text


def build(monday, force=False):
    if not force and datetime.strptime(monday, "%Y-%m-%d").weekday() != 0:
        print(f"[*] {monday} is not a Monday; no weekly finance post.")
        return None
    picked = pick_stories(monday)
    if len(picked) < 2:
        print("[!] Fewer than two finance-relevant stories this week; no weekly finance post.")
        return None
    text = render(monday, picked)
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"linkedin_finance_weekly_{monday}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[+] Weekly finance post ({len(picked)} stories, {len(text)} chars): {path}")
    for r in picked:
        print(f"    {r['date']} [{r['theme']}] {r['story']['headline'][:70]}")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monday's 'AI for Accountants' LinkedIn post")
    parser.add_argument("--date", required=True, help="The Monday it is posted (YYYY-MM-DD)")
    parser.add_argument("--force", action="store_true", help="Write it even if the date is not a Monday")
    args = parser.parse_args()
    build(args.date, args.force)
