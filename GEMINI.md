# Antigravity AI News Production Guidelines & Permanent Rules

These rules are permanently enforced across all future SanMitra AI News Wire and YouTube video creation workflows in this workspace.

---

## 🚫 1. PERMANENTLY BANNED OVERUSED STOCK & DISCONNECTED IMAGERY

Never use these exhausted stock visuals or unrelated assets:
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
* ❌ **NO UNCONNECTED FALLBACKS**: Power lines, random lakes, cultural statues (e.g. Nataraja), or arbitrary world maps must never be used as fallback filler.

---

## 🏢 2. AUTHENTIC ENTITY VISUALS & ZERO RANDOM FALLBACKS (MANDATORY RULE)

* **Direct Story Relevance**: Every visual displayed on screen MUST have a direct, verified editorial connection to the story. No generic or random fallback imagery is permitted under any circumstances.
* **Image Sourcing Priority**:
  1. **Primary Sources**: Wikimedia Commons, Unsplash (`https://unsplash.com/`), Pixabay (`https://pixabay.com/`), and Pexels (`https://www.pexels.com/`) for authentic editorial, facility, or technology photos.
  2. **Corporate & Institutional Facilities**: When reporting on a company, agency, or institution (e.g., Google, Microsoft, OpenAI, Apple, Nvidia, Tencent, Citibank, Siemens, Ministry of Science), use:
     - The authentic corporate headquarters building or campus showing official signage/branding (e.g., Googleplex, Microsoft Redmond Building 92, Apple Park, 1515 Third Street, Tencent Seafront Towers, Citigroup 388 Greenwich).
     - The official verified corporate logo/emblem from Wikimedia Commons or official press kits.
  3. **Approved Universal Fallbacks (ONLY when no specific entity visual is available)**:
     - `public/aibrief/assets/fallbacks/default_ai_brain_ai.jpg` (Circuit brain with integrated AI branding)
     - `public/aibrief/assets/fallbacks/default_ai_network.jpg` (High-tech blue digital AI network interface)
     - *NEVER* fall back to disconnected real-world objects, landscapes, or cultural symbols.
* **Individual Person Rule**:
  - An individual person's portrait or photo may **ONLY** be displayed if that individual is explicitly named in the story text.
  - **Zero Person Bleed**: Never show an individual (e.g., Jensen Huang, Sam Altman, Sundar Pichai) on stories concerning another company or generic AI topics where they are not the named subject.
* **Single Authoritative Cut Architecture**: Prefer 1 authoritative, highly relevant hero image (e.g., verified facility with signage) displaying slow cinematic Ken Burns framing throughout the segment rather than multi-cut sequences that risk introducing irrelevant fallback B-roll.

---

## 🧠 3. VISUAL MEMORY SYSTEM (14-DAY ROLLING WINDOW)

* Maintain the persistent log at `src/aibrief/data/visual_memory.json`.
* **Zero Repeats within 14 Days**: Do not reuse the same hero image, specific landmark, or stock photo within 14 days.
* **Target**: Minimum **80% visual freshness** day-to-day.
* Before rendering, ensure `download_daily_editorial_visuals.py --date <YYYY-MM-DD>` is executed to fetch fresh, story-specific 1920x1080 images into `public/aibrief/assets/editorial/<YYYY-MM-DD>/`.

---

## 🎙️ 4. BROADCAST AUDIO & SCRIPT CONSTRAINTS

* **Tone**: Calm, authoritative CNBC / Bloomberg / Reuters broadcast delivery. Two anchors, one voice per segment:
  - **Christopher** (`en-US-ChristopherNeural`): Opens the show with the 1-line top news headlines for the day (excluding Research Desk papers), concludes with *"And now, the news in brief."*, reads even-numbered stories, the recap, and the close.
  - **Aria** (`en-US-AriaNeural`): Reads odd-numbered stories (starting with Story 1) and the market snapshot.
* **NEVER Speak**:
  - Hashtags or bullet points
  - Section names ("World", "USA", "Story 1", "Item 1", "Breaking News")
  - Source URLs (e.g., "https://reuters.com")
  - Markdown symbols (`#`, `**`, `_`)
* **Deduplication**: Never repeat the same story in multiple regions. Consolidate into a single master story under its primary bureau.

---

## ⚡ 5. CLOUD-FIRST GH AUTOMATION & STRICT CROSS-PLATFORM DEDUPLICATION

* **GitHub Actions is the Primary Broadcaster**:
  - Daily autonomous production runs automatically via GitHub Actions (`.github/workflows/cloud_fallback.yml`) at **7:00 PM IST (13:30 UTC)**.
  - GH claims the episode with `Auto: episode claim <YYYY-MM-DD> by cloud [skip ci]`, produces the broadcast, uploads to YouTube, and commits back:
    - `src/aibrief/data/aired/<YYYY-MM-DD>.json`
    - `src/aibrief/data/story_memory_ledger.json`
    - `src/aibrief/data/visual_memory.json`
    - `prompts/`
* **Local PC Stand-Down & Non-Duplication Rule**:
  - The local PC yields to GitHub Actions. If the PC is awake, `run_nightly_production.bat` first runs `git pull` and inspects `git log` and `src/aibrief/data/aired/`.
  - If GitHub Actions has claimed or already completed the episode, the local run SKIPS immediately.
* **Manual / Local Verification (Before Any Render)**:
  - If a production is ever run or tested on the local PC, the agent MUST:
    1. Run `git pull origin main` to fetch GH's latest claims and aired records.
    2. Check `src/aibrief/data/aired/` and `story_memory_ledger.json`.
    3. Ensure NO candidate story matches any story aired in the past 14 days or in any unreleased cloud claim. Zero duplicate stories permitted.

