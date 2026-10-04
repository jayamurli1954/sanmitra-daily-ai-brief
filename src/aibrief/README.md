# AI Brief – Daily Faceless YouTube News Production Suite

A fully automated, institutional-grade faceless newsroom video pipeline built with **Antigravity + Remotion Studio**. Designed in the visual and editorial style of **Bloomberg Technology, CNBC, and Reuters**.

---

## 🚀 One-Command Daily Production

To generate today's complete episode (voiceovers, visual assets, music bed, YouTube metadata, LinkedIn post, thumbnail, and Remotion preview):

```bash
python produce_daily_ai_brief.py --date 2026-09-22
```

To render the full 1080p MP4 broadcast video directly to disk:

```bash
python produce_daily_ai_brief.py --date 2026-09-22 --render-video
```

---

## 📅 Daily Workflow (Tomorrow's Episode)

To produce tomorrow's episode in under 2 minutes:

1. **Create the new day's JSON** in `src/aibrief/data/YYYY-MM-DD.json` (you can duplicate `2026-09-22.json`).
2. **Update the headlines, scripts, sources, and importance scores**:
   ```json
   {
     "date": "2026-09-23",
     "formattedDate": "23 September 2026",
     "title": "AI Brief – 23 September 2026",
     "stories": [
       {
         "id": "frontier_model_launch",
         "region": "USA",
         "headline": "NEW FRONTIER MODEL DEMOLISHES BENCHMARKS",
         "subheadline": "Breakthrough in Autonomous Multimodal Reasoning",
         "importanceScore": 96,
         "source": "Reuters",
         "sourceUrl": "https://reuters.com/...",
         "script": "...",
         "keyPoints": [ ... ],
         "visualAsset": "frontier_model.png"
       }
     ]
   }
   ```
3. **Run the master orchestrator**:
   ```bash
   python produce_daily_ai_brief.py --date 2026-09-23
   ```
4. **Output generated instantly**:
   - `out/aibrief/thumbnail_2026-09-23.png`: YouTube Thumbnail (CNBC/Bloomberg breaking news style).
   - `out/aibrief/youtube_metadata.txt`: Ready-to-paste YouTube Title, Description with exact source URLs, and automatically calculated Chapter timestamps.
   - `out/aibrief/linkedin_post.txt`: Formatted multi-platform executive LinkedIn dispatch.
   - `out/aibrief/AI_Brief_2026-09-23.mp4`: Final high-definition 1080p 30fps broadcast video.

---

## 🎨 Visual & Audio Architecture

1. **Two-anchor English broadcast voices**:
   - Powered by `edge-tts`. Christopher (`en-US-ChristopherNeural`) opens the show, reads odd-numbered stories, the recap, and the close. Aria (`en-US-AriaNeural`) reads even-numbered stories and the market snapshot.
   - Speech timings measured down to the millisecond using `mutagen`.
2. **Automated Importance Ranking**:
   - Stories are sorted automatically in descending order of `importanceScore`, ensuring the biggest breaking news always leads the broadcast.
3. **Persistent Source Attribution**:
   - Verified source watermark badge (`Source: Ars Technica`, `Source: Reuters`, etc.) displayed throughout each scene for full journalistic credibility.
4. **Dynamic Scrolling Ticker**:
   - Continuous marquee news ticker across the bottom displaying today's headlines and global AI stock/crypto index benchmarks.
5. **Procedural Newsroom Theme**:
   - Synthesized corporate technological pulse bed (`public/audio/aibrief_theme.wav`) mixed smoothly under voiceover.

---

## 🖥️ Live Preview in Remotion Studio

To interactively preview, scrub, and inspect the scenes:

```bash
npm run dev
```

Open your browser at `http://localhost:3000` and select:
- `AIBriefMaster16x9`: Full 16:9 widescreen broadcast with all scenes, transitions, and audio.
- `AIBriefThumbnail`: High-contrast breaking news thumbnail composition.
