# Antigravity AI News Production Guidelines & Permanent Rules

These rules are permanently enforced across all future SanMitra AI News Wire and YouTube video creation workflows in this workspace.

---

## 🚫 1. PERMANENTLY BANNED OVERUSED STOCK IMAGERY

Never use these exhausted stock visuals:
* ❌ Obama on the phone (`gov_white_house.jpg`)
* ❌ UN emblem / logo full-screen (`gov_un_chamber.jpg`, `un_declaration.png`)
* ❌ Gateway of India (`gov_india_delhi.jpg`)
* ❌ Earth-at-night satellite image (`tech_neural_globe.jpg`)
* ❌ Generic politician podium / microphone clusters
* ❌ Generic AI robot faces / glowing android skulls
* ❌ OpenAI logo on plain blue background
* ❌ Generic hacker in a dark hoodie
* ❌ Circuit board closeups without editorial context
* ❌ Repetitive data center corridors without authentic story context

---

## 🧠 2. VISUAL MEMORY SYSTEM (14-DAY ROLLING WINDOW)

* Maintain the persistent log at `src/aibrief/data/visual_memory.json`.
* **Zero Repeats within 14 Days**: Do not reuse the same hero image, specific landmark, or stock photo within 14 days.
* **Target**: Minimum **80% visual freshness** day-to-day.
* Before rendering, ensure `download_daily_editorial_visuals.py --date <YYYY-MM-DD>` is executed to fetch fresh, story-specific 1920x1080 images into `public/aibrief/assets/editorial/<YYYY-MM-DD>/`.

---

## 🎯 3. STORY-BASED VISUAL ARCHITECTURE

Never use broad topic tags (e.g. "India" -> Gateway of India, "UN" -> UN logo). Every story must use 3-4 distinct cuts (4–6 seconds each):
* **Primary Visual (Cut 1: 0–6s)**: Direct contextual representation of the event (e.g., situation room, corporate campus, keynote stage).
* **Alternative Visual A (Cut 2: 6–12s)**: Operational or engineering angle (e.g., SOC threat operations, semiconductor cleanroom, code audit).
* **Alternative Visual B (Cut 3: 12–18s)**: Hardware, infrastructure, or human impact (e.g., GPU cluster corridor, research scientists in lab, municipal terminal).

### Rotate Across 5 Professional Styles:
1. **Newsroom Style**: Live telemetry dashboards, data walls, trading desks.
2. **Documentary Style**: Real facilities, corporate headquarters, semiconductor fabs.
3. **Strategic Briefing Style**: Situation rooms, cyber defense SOCs, command consoles.
4. **Infographic Style**: High-tech network topologies, architecture diagrams, satellite links.
5. **Cinematic Style**: Skylines, illuminated technology corridors, supercomputing clusters.

---

## 🎙️ 4. BROADCAST AUDIO & SCRIPT CONSTRAINTS

* **Tone**: Calm, authoritative CNBC / Bloomberg / Reuters broadcast delivery (voice: `en-US-ChristopherNeural`).
* **NEVER Speak**:
  - Hashtags or bullet points
  - Section names ("World", "USA", "Story 1", "Item 1", "Breaking News")
  - Source URLs (e.g., "https://reuters.com")
  - Markdown symbols (`#`, `**`, `_`)
* **Deduplication**: Never repeat the same story in multiple regions. Consolidate into a single master story under its primary bureau.
