"""
The day's LinkedIn article, written by Claude in the SanMitra AI News Wire format.

    python src/aibrief/write_linkedin_article.py --json src/aibrief/data/aired/2026-11-01.json --video-url https://youtu.be/...

run_autonomous_brief.py calls write_article() after the YouTube upload. Claude
writes the analysis (theme, introduction, each story with "Why it matters",
the big picture, key takeaways, closing thought); the header, counts, video
link, source links, footer and hashtags are filled in here from the episode,
so no link or date can be invented.

Writes, in out/aibrief/:
  linkedin_article_<date>.html  open it, press "Copy title" and "Copy article",
                                paste into LinkedIn's article editor
  linkedin_article_<date>.md    the same article as text
LinkedIn's API cannot publish articles: the editor publishes it as an
individual article (not in a newsletter) and schedules it for 9:30 AM.

Needs ANTHROPIC_API_KEY. Without it, or if the call fails, the template
article from generate_linkedin_article.py stays in place.
"""

import argparse
import html
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.aibrief.generate_linkedin_article import CHANNEL_URL, HASHTAGS

MODEL = "claude-opus-5-5"
REGIONS = ["WORLD", "USA", "CHINA", "ASIA", "INDIA"]
REGION_HEADINGS = {"WORLD": "🌍 WORLD", "USA": "🇺🇸 USA", "CHINA": "🇨🇳 CHINA", "ASIA": "🌏 ASIA", "INDIA": "🇮🇳 INDIA"}
REGION_NAMES = {"WORLD": "World", "USA": "USA", "CHINA": "China", "ASIA": "Asia", "INDIA": "India"}

SYSTEM = """You are the editor of SanMitra AI News Wire, a daily AI news briefing for business leaders, published as a LinkedIn article under the editor's own name.

You receive the stories that aired in today's video, numbered in the order they will appear. Write the analysis that goes around them.

Facts
- Use only facts that are in the supplied stories: no new numbers, names, dates, products, quotes or events. General background that any informed reader knows is fine; specific claims are not.
- Attribute claims to whoever made them. Company benchmarks, prices and performance figures are "the company's own claims". Reports citing sources are reports, not established facts. Government projections are projections, not results. When a study was run by the maker of the product studied, say so.
- If a story's text is thin, write a shorter entry rather than padding it.

Style
- Calm, authoritative business-news voice (Reuters, Bloomberg, the Financial Times). British spelling (organisation, analyse).
- Short paragraphs of one to three sentences. Plain words. No hype, no exclamation marks, no rhetorical questions in the body.
- "Why it matters" explains the practical meaning for businesses, professionals and policymakers, in two to four short paragraphs, and ends on what to watch or the real test.
- Write plain text only: no Markdown, no bullet characters, no hashtags, no emoji, no URLs, no "Story 1" labels.

Structure
- theme_headline: one line naming the thread that connects the day's stories (e.g. "AI's next phase: Trust, infrastructure and the race to build practical intelligence").
- intro_paragraphs: four to seven short paragraphs that set out the theme, mention the two or three most significant stories, and end with a sentence such as "Here are the ten developments that deserve attention." using the actual number of stories.
- stories: one entry per supplied story, same numbers, in order. title: a clear factual headline (not a copy of the source's clickbait). body_paragraphs: what happened, two to five short paragraphs. why_it_matters: as above.
- big_picture_intro, big_picture_points (three or four trends, each naming the stories that show it), big_picture_closing (one or two sentences, may be empty).
- takeaways: five or six practical takeaways for business leaders, each a short label and one sentence.
- closing_thought: three to five short paragraphs ending on a memorable line.
- extra_hashtags: two to four topic hashtags specific to these stories, without the # sign (e.g. AIAgents, VoiceAI)."""

SCHEMA = {
    "type": "object",
    "properties": {
        "theme_headline": {"type": "string"},
        "intro_paragraphs": {"type": "array", "items": {"type": "string"}},
        "stories": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "number": {"type": "integer"},
                "title": {"type": "string"},
                "body_paragraphs": {"type": "array", "items": {"type": "string"}},
                "why_it_matters": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["number", "title", "body_paragraphs", "why_it_matters"],
            "additionalProperties": False,
        }},
        "big_picture_intro": {"type": "string"},
        "big_picture_points": {"type": "array", "items": {
            "type": "object",
            "properties": {"heading": {"type": "string"}, "paragraphs": {"type": "array", "items": {"type": "string"}}},
            "required": ["heading", "paragraphs"],
            "additionalProperties": False,
        }},
        "big_picture_closing": {"type": "string"},
        "takeaways": {"type": "array", "items": {
            "type": "object",
            "properties": {"label": {"type": "string"}, "text": {"type": "string"}},
            "required": ["label", "text"],
            "additionalProperties": False,
        }},
        "closing_thought": {"type": "array", "items": {"type": "string"}},
        "extra_hashtags": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["theme_headline", "intro_paragraphs", "stories", "big_picture_intro", "big_picture_points",
                 "big_picture_closing", "takeaways", "closing_thought", "extra_hashtags"],
    "additionalProperties": False,
}


def ordered_stories(ep: Dict) -> List[Dict]:
    """Stories grouped by bureau (World, USA, China, Asia, India), keeping the
    episode's order within each; the article numbers them in this order."""
    stories = ep.get("stories", [])
    known = [s for r in REGIONS for s in stories if s.get("region", "WORLD").upper() == r]
    return known + [s for s in stories if s.get("region", "WORLD").upper() not in REGIONS]


def _day(dt: datetime) -> str:
    return f"{dt.strftime('%A')}, {dt.day} {dt.strftime('%B %Y')}"


def header(ep: Dict, video_url: str) -> Dict:
    dt = datetime.strptime(ep["date"], "%Y-%m-%d")
    stories = ordered_stories(ep)
    weekly = bool(ep.get("weekly"))
    outlets = {s.get("source", "").strip() for s in stories if s.get("source")}
    regions = [REGION_NAMES[r] for r in REGIONS if any(s.get("region", "").upper() == r for s in stories)]
    yesterday = dt - timedelta(days=1)
    if weekly:
        title = f"🌐 Weekly AI Round-up — {_day(dt)} (IST)"
        period = [f"Reporting period: {_day(dt - timedelta(days=6)).replace(dt.strftime(' %Y'), '')} – {_day(yesterday)}"]
        count = f"{len(stories)} important AI stories"
        watch = f"▶️ Watch this week's round-up: {video_url}"
    else:
        title = f"🌐 Daily AI News Brief — {_day(dt)} (IST)"
        period = [f"Reporting window: {_day(yesterday)}", f"Publication: {_day(dt)}"]
        count = f"{len(stories)} AI stories"
        watch = f"▶️ Watch today's video brief: {video_url}"
    return {"title": title, "period": period, "counts": f"{count} | {len(outlets)} news outlets | {' • '.join(regions)}",
            "watch": watch, "weekly": weekly}


def story_input(ep: Dict) -> str:
    lines = []
    for i, s in enumerate(ordered_stories(ep), 1):
        lines += [f"<story number=\"{i}\" region=\"{REGION_NAMES.get(s.get('region', '').upper(), s.get('region', ''))}\">",
                  f"Headline: {s.get('headline', '').strip()}",
                  f"Source: {s.get('source', '').strip()}",
                  f"Summary: {s.get('whyThisMatters', '').strip()}",
                  f"Broadcast script: {s.get('script', '').strip()}",
                  "</story>", ""]
    return "\n".join(lines)


def ask_claude(ep: Dict, client=None) -> Dict:
    import anthropic
    client = client or anthropic.Anthropic()
    kind = "weekly round-up of stories that did not make the daily episodes" if ep.get("weekly") else "daily brief"
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=64000,
        system=SYSTEM,
        thinking={"type": "adaptive"},
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": SCHEMA}},
        # If a safety classifier declines, the API reruns the request on the
        # model it recommends. Passed as extra_body: the installed SDK (0.84)
        # predates the fallbacks parameter.
        betas=["server-side-fallback-2026-07-01"],
        extra_body={"fallbacks": "default"},
        messages=[{"role": "user", "content": f"Today's {kind}, {ep['date']}:\n\n{story_input(ep)}"}],
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason != "end_turn":
        raise RuntimeError(f"Claude stopped with {msg.stop_reason}")
    return json.loads(next(b.text for b in msg.content if b.type == "text"))


def hashtags(extra: List[str]) -> str:
    tags = HASHTAGS.split()
    for t in extra:
        t = "#" + "".join(ch for ch in t if ch.isalnum())
        if len(t) > 1 and t.lower() not in {x.lower() for x in tags}:
            tags.insert(-2, t)  # SanMitra's own tags stay last
    return " ".join(tags)


def sections(ep: Dict, video_url: str, a: Dict) -> List[tuple]:
    """The article as (kind, payload) blocks, rendered to Markdown and HTML."""
    h = header(ep, video_url)
    written = {s["number"]: s for s in a["stories"]}
    out = [("meta", h["period"] + [h["counts"]]), ("watch", h["watch"]), ("h2", a["theme_headline"])]
    out += [("p", p) for p in a["intro_paragraphs"]]
    region = None
    for i, s in enumerate(ordered_stories(ep), 1):
        r = s.get("region", "WORLD").upper()
        if r != region:
            region = r
            out.append(("h2", REGION_HEADINGS.get(r, r)))
        w = written.get(i) or {"title": s.get("headline", ""), "body_paragraphs": [s.get("whyThisMatters", "")],
                               "why_it_matters": []}
        out.append(("h3", f"{i}. {w['title']}"))
        out += [("p", p) for p in w["body_paragraphs"]]
        if w["why_it_matters"]:
            out.append(("label", "Why it matters"))
            out += [("p", p) for p in w["why_it_matters"]]
        if s.get("sourceUrl"):
            out.append(("source", (f"{s.get('source', '').strip()} — {s.get('headline', '').strip()}", s["sourceUrl"])))
    out += [("h2", "THE BIG PICTURE"), ("p", a["big_picture_intro"])]
    for n, pt in enumerate(a["big_picture_points"], 1):
        out.append(("label", f"{n}. {pt['heading']}"))
        out += [("p", p) for p in pt["paragraphs"]]
    if a["big_picture_closing"]:
        out.append(("p", a["big_picture_closing"]))
    out += [("h2", "KEY TAKEAWAYS FOR BUSINESS LEADERS"), ("bullets", [(t["label"], t["text"]) for t in a["takeaways"]])]
    out.append(("h2", "CLOSING THOUGHT"))
    out += [("p", p) for p in a["closing_thought"]]
    out += [("label", "SANMITRA AI NEWS WIRE — From AI breakthroughs to real-world impact."),
            ("watch", h["watch"]),
            ("p", "🔔 Get the daily AI brief every morning at 9:30 AM IST."),
            ("link", ("▶️ Watch and subscribe: ", CHANNEL_URL)),
            ("p", "Follow me and tap the 🔔 bell on my profile for daily AI briefings covering the most important "
                  "developments across World, USA, China, Asia and India."),
            ("p", hashtags(a["extra_hashtags"]))]
    return out


def to_markdown(title: str, blocks: List[tuple]) -> str:
    md = [f"# {title}", ""]
    for kind, v in blocks:
        if kind == "meta":
            md += [*v, ""]
        elif kind == "h2":
            md += [f"## {v}", ""]
        elif kind == "h3":
            md += [f"### {v}", ""]
        elif kind == "label":
            md += [f"**{v}**", ""]
        elif kind == "source":
            md += [f"Source: [{v[0]}]({v[1]})", ""]
        elif kind == "link":
            md += [f"{v[0]}{v[1]}", ""]
        elif kind == "bullets":
            md += [f"* **{label}:** {text}" for label, text in v] + [""]
        else:
            md += [v, ""]
    return "\n".join(md).rstrip() + "\n"


def _a(url: str, text: str = None) -> str:
    return f'<a href="{html.escape(url)}">{html.escape(text or url)}</a>'


def to_html(title: str, blocks: List[tuple]) -> str:
    e = html.escape
    body = []
    for kind, v in blocks:
        if kind == "meta":
            body.append("<p>" + "<br>".join(e(x) for x in v) + "</p>")
        elif kind == "h2":
            body.append(f"<h2>{e(v)}</h2>")
        elif kind == "h3":
            body.append(f"<h3>{e(v)}</h3>")
        elif kind == "label":
            body.append(f"<p><strong>{e(v)}</strong></p>")
        elif kind == "source":
            body.append(f"<p>Source: {_a(v[1], v[0])}</p>")
        elif kind in ("watch", "link"):
            text, url = (v.rsplit(" ", 1)[0] + " ", v.rsplit(" ", 1)[1]) if kind == "watch" else v
            body.append(f"<p>{e(text)}{_a(url)}</p>")
        elif kind == "bullets":
            body.append("<ul>" + "".join(f"<li><strong>{e(l)}:</strong> {e(t)}</li>" for l, t in v) + "</ul>")
        else:
            body.append(f"<p>{e(v)}</p>")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<style>
body {{ font: 17px/1.6 Georgia, serif; max-width: 760px; margin: 0 auto; padding: 16px; color: #1d1d1f; background: #fff; }}
.bar {{ position: sticky; top: 0; background: #eef3f8; padding: 12px; border-radius: 8px; font: 14px/1.4 system-ui, sans-serif; }}
.bar button {{ font: inherit; padding: 6px 12px; margin-right: 8px; cursor: pointer; }}
h2 {{ margin-top: 1.6em; }}
</style></head><body>
<div class="bar">
  <button onclick="copy('title')">Copy title</button><button onclick="copy('article')">Copy article</button>
  <span id="msg">Paste into LinkedIn: Write article. Publish as an individual article, not in a newsletter, scheduled for 9:30 AM.</span>
</div>
<h1 id="title">{e(title)}</h1>
<div id="article">
{chr(10).join(body)}
</div>
<script>
async function copy(id) {{
  const el = document.getElementById(id);
  try {{
    await navigator.clipboard.write([new ClipboardItem({{
      "text/html": new Blob([el.innerHTML], {{type: "text/html"}}),
      "text/plain": new Blob([el.innerText], {{type: "text/plain"}})}})]);
  }} catch (err) {{
    const r = document.createRange(); r.selectNodeContents(el);
    const s = getSelection(); s.removeAllRanges(); s.addRange(r); document.execCommand("copy"); s.removeAllRanges();
  }}
  document.getElementById("msg").textContent = (id === "title" ? "Title" : "Article") + " copied.";
}}
</script>
</body></html>
"""


def write_article(ep: Dict, video_url: str, out_dir: str = os.path.join("out", "aibrief"), client=None) -> str:
    """Writes the HTML and Markdown article; returns the HTML path."""
    a = ask_claude(ep, client)
    title = header(ep, video_url)["title"]
    blocks = sections(ep, video_url, a)
    os.makedirs(out_dir, exist_ok=True)
    md = to_markdown(title, blocks)
    for name in ("linkedin_article.md", f"linkedin_article_{ep['date']}.md"):
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
            f.write(md)
    path = os.path.join(out_dir, f"linkedin_article_{ep['date']}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(to_html(title, blocks))
    print(f"[+] LinkedIn article written by Claude: {path}")
    return path


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Write the LinkedIn article for an episode with Claude")
    parser.add_argument("--json", default="src/aibrief/data/active_episode.json", help="Episode JSON")
    parser.add_argument("--video-url", required=True, help="The episode's YouTube link")
    args = parser.parse_args()
    with open(args.json, "r", encoding="utf-8") as f:
        write_article(json.load(f), args.video_url)
