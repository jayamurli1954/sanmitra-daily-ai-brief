import React from "react";
import { Img, staticFile } from "remotion";
import episodeData from "./data/active_episode.json";

const ep = episodeData as any;

// Infographic cover in the style of the daily LinkedIn brief: header, one column
// per bureau with numbered story cards, an optional takeaways strip and a footer.
// Everything printed comes from the episode JSON, so the cover can never show a
// story, number or source that is not in the day's brief.

const FONT = "'Segoe UI', 'Inter', -apple-system, Roboto, sans-serif";
const INK = "#0f172a";
const MUTED = "#475569";
const BRAND_BLUE = "#0b63b6";

const REGIONS: Record<string, { label: string; code: string; from: string; to: string }> = {
  WORLD: { label: "WORLD", code: "WLD", from: "#1e3a8a", to: "#2563eb" },
  USA: { label: "USA", code: "US", from: "#be123c", to: "#4338ca" },
  CHINA: { label: "CHINA", code: "CN", from: "#dc2626", to: "#a21caf" },
  ASIA: { label: "ASIA", code: "AS", from: "#047857", to: "#0d9488" },
  INDIA: { label: "INDIA", code: "IN", from: "#15803d", to: "#0f766e" },
};
const REGION_ORDER = ["WORLD", "USA", "CHINA", "ASIA", "INDIA"];

// GLOBAL and any region without its own column go under WORLD, so every
// story counted in the header also gets a card.
const bureauOf = (s: any): string => {
  const r = (s.region || "WORLD").toUpperCase();
  return REGION_ORDER.includes(r) ? r : "WORLD";
};

const TOPICS = [
  { title: "AI Breakthroughs & Models", color: "#38bdf8" },
  { title: "Industry & Startup News", color: "#34d399" },
  { title: "Technology Trends", color: "#facc15" },
  { title: "Policy & Regulation", color: "#fb7185" },
  { title: "Real-World Impact", color: "#a78bfa" },
];

const TAKEAWAY_COLORS = ["#dc2626", "#2563eb", "#7c3aed", "#16a34a", "#ea580c"];

export type CoverTakeaway = { title: string; text: string };
export type LinkedInCoverProps = { takeaways?: CoverTakeaway[] };

// Short spoken transitions the scriptwriter puts before each story.
const LEAD_IN = /^(our lead story today|turning to [\w\s]{1,30}|in (china|asia|india|europe|the united states)|around the world|also today|in other news|next|elsewhere|meanwhile)\.?$/i;

const words = (t: string) =>
  new Set(
    t
      .toLowerCase()
      .replace(/\$/g, " dollars ")
      .split(/[^a-z0-9]+/)
      .filter((w) => w.length > 2),
  );

const overlap = (a: string, b: string) => {
  const wa = words(a);
  const wb = words(b);
  if (!wa.size || !wb.size) return 0;
  let n = 0;
  wa.forEach((w) => wb.has(w) && n++);
  return n / Math.min(wa.size, wb.size);
};

// Abbreviations whose full stop does not end a sentence ("8:11 a.m. to ...").
const SENTENCE_END = /(?<!\b(?:a\.m|p\.m|No|Mr|Mrs|Ms|Dr|St|vs|Inc|Ltd|Co|U\.S|U\.K)\.)(?<=[.!?])\s+(?=["A-Z])/;
// A sentence opening with a pronoun reads badly on its own, away from the script.
const PRONOUN_OPENER = /^(they|it|he|she|this|that|these|those|its|their)/i;

// The first sentence of the script that adds detail: not a lead-in, not a
// restatement of the headline or the one-line hook. Tall cards have room for
// the sentence after it too.
export const storySummary = (s: any, maxChars = 230): string => {
  const sentences: string[] = (s.script || "")
    .split(SENTENCE_END)
    .map((x: string) => x.trim())
    .filter(Boolean);
  const why = s.whyThisMatters || "";
  // A short sentence that mostly repeats the headline or hook is a restatement;
  // a long one that also covers the headline is the detail we want.
  const restates = (x: string, ref: string) => x.length < 120 && overlap(x, ref) >= 0.6;
  const usable = (x: string) =>
    !LEAD_IN.test(x) && x.length > 40 && !restates(x, s.headline || "") && !restates(x, why);
  let at = sentences.findIndex((x) => usable(x) && !PRONOUN_OPENER.test(x));
  if (at < 0) at = sentences.findIndex(usable);
  let pick = at >= 0 ? sentences[at] : why;
  const next = at >= 0 ? sentences[at + 1] : undefined;
  if (next && !LEAD_IN.test(next) && pick.length + next.length + 1 <= maxChars) pick += " " + next;
  return pick.length > maxChars ? pick.slice(0, maxChars - 3).replace(/\s+\S*$/, "") + "..." : pick;
};

const longDate = (iso: string, offsetDays = 0) => {
  const d = new Date(`${iso}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + offsetDays);
  return {
    weekday: d.toLocaleDateString("en-GB", { weekday: "long", timeZone: "UTC" }),
    date: d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }),
  };
};

export const LinkedInCoverBanner: React.FC<LinkedInCoverProps> = ({ takeaways }) => {
  const stories: any[] = ep?.stories || [];
  const notes: CoverTakeaway[] = (takeaways || ep?.coverTakeaways || []).slice(0, 5);

  // Columns in bureau order; stories numbered down each column, left to right.
  // Two or fewer stories per column leaves tall cards: photo on top, more text.
  const rows = Math.max(1, ...REGION_ORDER.map((r) => stories.filter((s) => bureauOf(s) === r).length));
  const tall = rows <= 2;

  let n = 0;
  const columns = REGION_ORDER.map((region) => ({
    region,
    style: REGIONS[region],
    items: stories
      .filter((s) => bureauOf(s) === region)
      .map((s) => ({
        num: ++n,
        headline: (s.headline || "").replace(/\s+,/g, ","),
        summary: storySummary(s, tall ? 300 : 230),
        source: s.source || "",
        image: s.visualCuts?.[0]?.image || s.visual || "aibrief/backgrounds/ai_chips.jpg",
      })),
  })).filter((c) => c.items.length);

  const outlets = new Set(stories.map((s) => (s.source || "").trim()).filter(Boolean)).size;
  const iso = ep?.date || "";
  const air = iso ? longDate(iso) : null;
  const covering = iso ? longDate(iso, -1) : null;
  const hero = stories[0]?.visualCuts?.[1]?.image || stories[0]?.visualCuts?.[0]?.image;

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        background: "linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%)",
        fontFamily: FONT,
        color: INK,
        display: "flex",
        flexDirection: "column",
        padding: "14px 18px 10px",
        boxSizing: "border-box",
        gap: 12,
        overflow: "hidden",
      }}
    >
      {/* ===== HEADER ===== */}
      <div style={{ height: 200, display: "flex", gap: 22, flexShrink: 0 }}>
        {/* Brand */}
        <div style={{ width: 520, display: "flex", flexDirection: "column", justifyContent: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <Img src={staticFile("aibrief/brand/sanmitra_mark.png")} style={{ width: 46, height: 44 }} />
            <span style={{ fontSize: 62, fontWeight: 800, color: BRAND_BLUE, letterSpacing: "-0.02em", lineHeight: 1 }}>
              SanMitra
            </span>
          </div>
          <div style={{ fontSize: 66, fontWeight: 800, letterSpacing: "-0.025em", lineHeight: 1.05, marginTop: 4 }}>
            AI News Wire
          </div>
          <div style={{ fontSize: 24, color: MUTED, marginTop: 8 }}>Your Daily Brief on What's Next in AI</div>
        </div>

        <div style={{ width: 2, background: "#cbd5e1", margin: "24px 0" }} />

        {/* Date + count */}
        <div style={{ width: 520, display: "flex", flexDirection: "column", justifyContent: "center", gap: 12 }}>
          {air && (
            <div>
              <div style={{ fontSize: 28, fontWeight: 500, lineHeight: 1.15 }}>{air.weekday},</div>
              <div style={{ fontSize: 38, fontWeight: 800, lineHeight: 1.15 }}>{air.date} (IST)</div>
              <div style={{ fontSize: 21, color: MUTED, marginTop: 2 }}>
                Covering {covering!.weekday}, {covering!.date}
              </div>
            </div>
          )}
          <div
            style={{
              background: "#dbeafe",
              border: "1.5px solid #bfdbfe",
              borderRadius: 12,
              padding: "10px 18px",
              fontSize: 25,
              fontWeight: 800,
              color: "#1e3a8a",
            }}
          >
            {stories.length} key AI stories from {outlets} news outlets
          </div>
        </div>

        {/* Lead-story photo with the topic legend */}
        <div style={{ flex: 1, position: "relative", borderRadius: 16, overflow: "hidden", background: "#0b1530" }}>
          {hero && (
            <Img
              src={staticFile(hero)}
              style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }}
            />
          )}
          <div
            style={{
              position: "absolute",
              inset: 0,
              background: "linear-gradient(90deg, rgba(8,20,48,0.92) 0%, rgba(8,20,48,0.75) 55%, rgba(8,20,48,0.35) 100%)",
            }}
          />
          <div
            style={{
              position: "relative",
              height: "100%",
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              alignContent: "center",
              gap: "14px 24px",
              padding: "0 30px",
            }}
          >
            {TOPICS.map((t) => (
              <div key={t.title} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div
                  style={{
                    width: 14,
                    height: 14,
                    borderRadius: 7,
                    background: t.color,
                    boxShadow: `0 0 12px ${t.color}`,
                    flexShrink: 0,
                  }}
                />
                <span style={{ fontSize: 19, fontWeight: 800, color: "#fff", textTransform: "uppercase", letterSpacing: "0.02em", whiteSpace: "nowrap" }}>
                  {t.title}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ===== BUREAU COLUMNS ===== */}
      <div style={{ flex: 1, display: "flex", gap: 10, minHeight: 0 }}>
        {columns.map((col) => (
          <div
            key={col.region}
            style={{
              flex: 1,
              minWidth: 0,
              display: "flex",
              flexDirection: "column",
              background: "#ffffff",
              borderRadius: 14,
              border: "1px solid #dbe3ee",
              boxShadow: "0 4px 14px rgba(15,23,42,0.06)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                height: 64,
                flexShrink: 0,
                background: `linear-gradient(100deg, ${col.style.from}, ${col.style.to})`,
                color: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 14,
              }}
            >
              <div
                style={{
                  border: "2px solid rgba(255,255,255,0.85)",
                  borderRadius: 8,
                  padding: "1px 8px",
                  fontSize: 17,
                  fontWeight: 800,
                }}
              >
                {col.style.code}
              </div>
              <span style={{ fontSize: 34, fontWeight: 800, letterSpacing: "0.02em" }}>{col.style.label}</span>
              <span style={{ fontSize: 17, fontWeight: 600, opacity: 0.85 }}>
                {col.items.length} {col.items.length === 1 ? "story" : "stories"}
              </span>
            </div>

            <div style={{ flex: 1, display: "grid", gridTemplateRows: `repeat(${rows}, 1fr)`, padding: "4px 10px", minHeight: 0 }}>
              {col.items.map((it, i) => (
                <div
                  key={it.num}
                  style={{
                    display: "flex",
                    flexDirection: tall ? "column" : "row",
                    gap: tall ? 10 : 12,
                    padding: "10px 0",
                    borderTop: i ? "1px solid #e2e8f0" : "none",
                    minHeight: 0,
                  }}
                >
                  <div
                    style={{
                      position: "relative",
                      width: tall ? "100%" : "36%",
                      height: tall ? "40%" : undefined,
                      flexShrink: 0,
                      borderRadius: 10,
                      overflow: "hidden",
                    }}
                  >
                    <Img
                      src={staticFile(it.image)}
                      style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }}
                    />
                    <div
                      style={{
                        position: "absolute",
                        top: 6,
                        left: 6,
                        width: 34,
                        height: 34,
                        borderRadius: 17,
                        background: col.style.from,
                        border: "2px solid #fff",
                        color: "#fff",
                        fontSize: 18,
                        fontWeight: 800,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        boxShadow: "0 2px 6px rgba(0,0,0,0.35)",
                      }}
                    >
                      {it.num}
                    </div>
                  </div>
                  <div style={{ flex: 1, minWidth: 0, minHeight: 0, display: "flex", flexDirection: "column", gap: 5 }}>
                    <div
                      style={{
                        fontSize: tall ? 20 : 18,
                        fontWeight: 800,
                        lineHeight: 1.18,
                        flexShrink: 0,
                        display: "-webkit-box",
                        WebkitLineClamp: tall ? 3 : 4,
                        WebkitBoxOrient: "vertical",
                        overflow: "hidden",
                      }}
                    >
                      {it.headline}
                    </div>
                    <div
                      style={{
                        fontSize: tall ? 15.5 : 14.5,
                        color: MUTED,
                        lineHeight: 1.32,
                        display: "-webkit-box",
                        WebkitLineClamp: tall ? 4 : rows > 3 ? 2 : 3,
                        WebkitBoxOrient: "vertical",
                        overflow: "hidden",
                      }}
                    >
                      {it.summary}
                    </div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: "#1d4ed8", marginTop: "auto" }}>
                      Source: {it.source}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* ===== KEY TAKEAWAYS (only when the editor supplied them) ===== */}
      {notes.length > 0 && (
        <div
          style={{
            height: 104,
            flexShrink: 0,
            display: "flex",
            alignItems: "center",
            background: "#ffffff",
            borderRadius: 14,
            border: "1px solid #dbe3ee",
            padding: "0 18px",
            gap: 18,
          }}
        >
          <div style={{ fontSize: 24, fontWeight: 800, color: "#1e3a8a", lineHeight: 1.1, width: 160, flexShrink: 0 }}>
            KEY
            <br />
            TAKEAWAYS
          </div>
          <div style={{ width: 2, alignSelf: "stretch", margin: "18px 0", background: "#cbd5e1" }} />
          {notes.map((t, i) => (
            <div key={i} style={{ flex: 1, display: "flex", gap: 12, alignItems: "center", minWidth: 0 }}>
              <div
                style={{
                  width: 42,
                  height: 42,
                  borderRadius: 21,
                  flexShrink: 0,
                  background: TAKEAWAY_COLORS[i % TAKEAWAY_COLORS.length],
                  color: "#fff",
                  fontWeight: 800,
                  fontSize: 20,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {i + 1}
              </div>
              <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: 17, fontWeight: 800, color: "#1e3a8a", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{t.title}</div>
                <div style={{ fontSize: 14.5, color: MUTED, lineHeight: 1.3 }}>{t.text}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ===== FOOTER ===== */}
      <div style={{ height: 46, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 6px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <Img src={staticFile("aibrief/brand/sanmitra_mark.png")} style={{ width: 30, height: 29 }} />
          <span style={{ fontSize: 24, fontWeight: 800, color: BRAND_BLUE }}>SanMitra</span>
          <span style={{ fontSize: 17, color: MUTED, marginLeft: 8 }}>
            Tech Solutions &nbsp;|&nbsp; AI NEWS WIRE &nbsp;|&nbsp; GLOBAL INSIGHTS. BIGGER PERSPECTIVE.
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: 20, color: INK }}>Follow for your daily AI briefing</span>
          <div
            style={{
              width: 34,
              height: 34,
              borderRadius: 6,
              background: "#0a66c2",
              color: "#fff",
              fontWeight: 800,
              fontSize: 20,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            in
          </div>
        </div>
      </div>
    </div>
  );
};
