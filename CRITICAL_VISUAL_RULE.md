# CRITICAL VISUAL RULE: YouTube AI News Broadcast Standard v3.0

This is a television broadcast news video, NOT a PowerPoint presentation or static slideshow.

---

## 🚫 AVOID OVERUSED STOCK IMAGERY (PERMANENTLY BANNED)

Never use these exhausted generic stock visual tropes:
* ❌ Obama on the phone (`gov_white_house.jpg`)
* ❌ UN emblem / logo full-screen (`gov_un_chamber.jpg`, `un_declaration.png`)
* ❌ Gateway of India (`gov_india_delhi.jpg`)
* ❌ Earth-at-night satellite image (`tech_neural_globe.jpg`)
* ❌ Generic politician podium / microphone cluster
* ❌ Generic AI robot faces / glowing android skulls
* ❌ OpenAI logo on plain blue background
* ❌ Generic hacker in a dark hoodie
* ❌ Generic motherboard / circuit board macro without scale
* ❌ Repetitive data center corridors without authentic context

---

## 🧠 VISUAL MEMORY SYSTEM (14-DAY ROLLING WINDOW)

* Maintain a persistent rolling 14-day memory in `src/aibrief/data/visual_memory.json`.
* **Zero Repeats within 14 Days**: Do not reuse the same hero image, specific landmark, or stock photo within 14 days unless the news item is a direct continuation and no suitable alternative exists.
* **Target Metric**: Minimum **80% visual freshness** day-to-day.

---

## 🎯 CHANGE FROM TOPIC-BASED TO STORY-BASED VISUALS

Do not pick visuals based on broad keywords (e.g., "India" -> Gateway of India, "UN" -> UN Logo). Pick visuals based on the **specific narrative event**:

### Multi-Cut Formula Per Story:
1. **Primary Visual (Cut 1: 0–6s)**: Direct contextual representation of the event (e.g. situational conference room, facility exterior, corporate campus).
2. **Alternative Visual A (Cut 2: 6–12s)**: Operational or engineering context (e.g. SOC operations center, semiconductor cleanroom, code terminal, mobile platform).
3. **Alternative Visual B (Cut 3: 12–18s)**: Hardware, infrastructure, or human impact (e.g. liquid-cooled compute corridor, engineers in lab, municipal user terminal).

### Rotate Across 5 Professional Styles:
* **Newsroom Style**: Live telemetry dashboards, data walls, trading desks.
* **Documentary Style**: Real research facilities, corporate headquarters, semiconductor fabs.
* **Strategic Briefing Style**: Situation rooms, cyber defense SOCs, command consoles.
* **Infographic Style**: High-tech network topologies, architecture flowcharts, satellite links.
* **Cinematic Style**: High-rise skylines, illuminated technology corridors, supercomputing clusters.

---

## ⏱️ The 4–6 Second Television Rule

1. **Never leave any visual on screen longer than 4–6 seconds.**
2. Continuous Ken Burns motion on every cut (`zoomIn`, `panLeft`, `zoomOut`, `panRight`).
3. Lower-third banners must stay crisp and institutional (Navy glass `#071126` with Cyan `#00F2FE` and Amber `#FFB800` accents).
4. The viewer must feel they are watching **Bloomberg Technology, CNBC TechCheck, or Reuters AI Briefing**.
