import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import evidenceData from "../data/evidence_cards.json";

/**
 * On-screen evidence for what the anchor is saying, timed to the word
 * (built by generate_evidence_cards.py). Two tracks:
 *   tags  - dateline and name tags, top left under the LIVE FEED slug
 *   cards - a reported clipping, a quote, a stat or a comparison, in the
 *           middle of the frame over a darkened picture
 * Every card comes from the story's own script and source.
 */

type Card =
  | { type: "dateline"; place: string; date?: string | null; start: number; end: number }
  | { type: "name"; name: string; role: string; start: number; end: number }
  | { type: "reported"; text: string; highlight?: string | null; source: string; start: number; end: number }
  | { type: "quote"; text: string; speaker?: string | null; source: string; start: number; end: number }
  | { type: "stat"; shown: string; label: string; start: number; end: number }
  | {
      type: "compare";
      items: { shown: string; value: number; label: string }[];
      start: number;
      end: number;
    };

const allCards = evidenceData as unknown as Record<string, Card[]>;

const FONT = "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
const SERIF = "Georgia, 'Times New Roman', serif";
const CARD_TOP = 250;
const TAG_TOP = 176;
const LEFT = 96;

const useCardMotion = (start: number, end: number) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const from = Math.round(start * fps);
  const to = Math.round(end * fps);
  const local = frame - from;
  const enter = spring({ frame: local, fps, config: { damping: 16, stiffness: 120 } });
  const exit = interpolate(frame, [to - 10, to], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return { local, fps, opacity: Math.min(enter, exit), rise: (1 - enter) * 36, progress: local / Math.max(1, to - from) };
};

const domainOf = (url?: string) => {
  try {
    return url ? new URL(url).hostname.replace(/^www\./, "") : "";
  } catch {
    return "";
  }
};

const Kicker: React.FC<{ color: string; children: React.ReactNode }> = ({ color, children }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 18 }}>
    <div style={{ width: 10, height: 10, backgroundColor: color, borderRadius: 2 }} />
    <div style={{ color, fontSize: 18, fontWeight: 900, letterSpacing: 3 }}>{children}</div>
  </div>
);

const ReportedCard: React.FC<{ card: Extract<Card, { type: "reported" }>; sourceUrl?: string }> = ({ card, sourceUrl }) => {
  const { opacity, rise, local, fps } = useCardMotion(card.start, card.end);
  // Highlighter sweeps across the claim while it is being read.
  const sweep = interpolate(local, [0.35 * fps, 1.6 * fps], [0, 100], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const h = card.highlight && card.text.includes(card.highlight) ? card.highlight : null;
  const [pre, post] = h ? card.text.split(h, 2) : [card.text, ""];
  const domain = domainOf(sourceUrl);
  return (
    <div
      style={{
        position: "absolute",
        top: CARD_TOP,
        left: LEFT,
        width: 1060,
        opacity,
        transform: `translateY(${rise}px)`,
        backgroundColor: "#fbfaf7",
        borderRadius: 14,
        boxShadow: "0 30px 70px rgba(0,0,0,0.65)",
        padding: "30px 40px 26px",
        fontFamily: FONT,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ color: "#0f172a", fontSize: 22, fontWeight: 900, letterSpacing: 0.5 }}>{card.source}</div>
        <div
          style={{
            color: "#b91c1c",
            fontSize: 14,
            fontWeight: 900,
            letterSpacing: 2.5,
            border: "2px solid #b91c1c",
            borderRadius: 4,
            padding: "3px 10px",
          }}
        >
          AS REPORTED
        </div>
      </div>
      <div style={{ height: 2, backgroundColor: "#e5e2da", margin: "16px 0 20px" }} />
      <div style={{ color: "#1f2937", fontSize: 36, lineHeight: 1.42, fontFamily: SERIF }}>
        {pre}
        {h && (
          <span
            style={{
              backgroundImage: "linear-gradient(#fde047, #fde047)",
              backgroundRepeat: "no-repeat",
              backgroundSize: `${sweep}% 100%`,
              boxDecorationBreak: "clone",
              WebkitBoxDecorationBreak: "clone",
              padding: "0 4px",
              color: "#0f172a",
              fontWeight: 700,
            }}
          >
            {h}
          </span>
        )}
        {post}
      </div>
      {domain && (
        <div style={{ marginTop: 20, color: "#6b7280", fontSize: 15, fontWeight: 800, letterSpacing: 2 }}>
          SOURCE • {domain.toUpperCase()}
        </div>
      )}
    </div>
  );
};

const QuoteCard: React.FC<{ card: Extract<Card, { type: "quote" }> }> = ({ card }) => {
  const { opacity, rise } = useCardMotion(card.start, card.end);
  return (
    <div
      style={{
        position: "absolute",
        top: CARD_TOP,
        left: LEFT,
        width: 1060,
        opacity,
        transform: `translateY(${rise}px)`,
        fontFamily: FONT,
        borderLeft: "6px solid #fbbf24",
        paddingLeft: 36,
      }}
    >
      <div style={{ color: "#fbbf24", fontSize: 140, lineHeight: 0.6, fontFamily: SERIF, height: 60 }}>“</div>
      <div style={{ color: "#ffffff", fontSize: 52, fontWeight: 700, lineHeight: 1.25, fontStyle: "italic" }}>
        {card.text}
      </div>
      <div style={{ marginTop: 24, color: "#cbd5e1", fontSize: 24, fontWeight: 700, letterSpacing: 1 }}>
        — {card.speaker ? `${card.speaker}, via ${card.source}` : card.source}
      </div>
    </div>
  );
};

const splitNumber = (shown: string) => {
  const m = shown.match(/^([^\d]*)([\d,]+(?:\.\d+)?)(.*)$/);
  if (!m) return null;
  return { prefix: m[1], value: parseFloat(m[2].replace(/,/g, "")), decimals: (m[2].split(".")[1] || "").length, suffix: m[3] };
};

const CountUp: React.FC<{ shown: string; local: number; fps: number }> = ({ shown, local, fps }) => {
  const parts = splitNumber(shown);
  if (!parts) return <>{shown}</>;
  const t = interpolate(local, [0, 0.9 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const eased = 1 - Math.pow(1 - t, 3);
  const n = parts.value * eased;
  const text = n.toLocaleString("en-US", { minimumFractionDigits: parts.decimals, maximumFractionDigits: parts.decimals });
  return (
    <>
      {parts.prefix}
      {text}
      {/* "×" and "+" hug the number; words like TRILLION get a space. */}
      <span style={{ fontSize: "0.55em", marginLeft: /^[×+%]/.test(parts.suffix) ? 2 : 14 }}>{parts.suffix.trim()}</span>
    </>
  );
};

const StatCard: React.FC<{ card: Extract<Card, { type: "stat" }> }> = ({ card }) => {
  const { opacity, rise, local, fps } = useCardMotion(card.start, card.end);
  return (
    <div
      style={{
        position: "absolute",
        top: CARD_TOP + 20,
        left: LEFT,
        width: 1000,
        opacity,
        transform: `translateY(${rise}px)`,
        fontFamily: FONT,
        borderLeft: "6px solid #fbbf24",
        paddingLeft: 36,
      }}
    >
      <Kicker color="#fbbf24">BY THE NUMBERS</Kicker>
      <div style={{ color: "#ffffff", fontSize: 150, fontWeight: 900, lineHeight: 1, letterSpacing: -4 }}>
        <CountUp shown={card.shown} local={local} fps={fps} />
      </div>
      <div style={{ marginTop: 18, color: "#e2e8f0", fontSize: 40, fontWeight: 600, lineHeight: 1.25, maxWidth: 940 }}>
        {card.label}
      </div>
    </div>
  );
};

const CompareCard: React.FC<{ card: Extract<Card, { type: "compare" }> }> = ({ card }) => {
  const { opacity, rise, local, fps } = useCardMotion(card.start, card.end);
  const max = Math.max(...card.items.map((i) => i.value), 1);
  const colors = ["#fbbf24", "#64748b"];
  return (
    <div
      style={{
        position: "absolute",
        top: CARD_TOP + 20,
        left: LEFT,
        width: 1100,
        opacity,
        transform: `translateY(${rise}px)`,
        fontFamily: FONT,
      }}
    >
      <Kicker color="#fbbf24">BY THE NUMBERS</Kicker>
      {card.items.map((item, i) => {
        const grow = spring({ frame: local - 8 - i * 8, fps, config: { damping: 18, stiffness: 90 } });
        const width = Math.max(14, (item.value / max) * 860) * grow;
        return (
          <div key={i} style={{ marginBottom: 34 }}>
            <div style={{ display: "flex", alignItems: "baseline", gap: 20, marginBottom: 10 }}>
              <div style={{ color: "#ffffff", fontSize: 64, fontWeight: 900, letterSpacing: -1.5 }}>{item.shown}</div>
              <div style={{ color: "#cbd5e1", fontSize: 28, fontWeight: 600 }}>{item.label}</div>
            </div>
            <div style={{ height: 26, width, backgroundColor: colors[i % 2], borderRadius: 4 }} />
          </div>
        );
      })}
    </div>
  );
};

const DatelineTag: React.FC<{ card: Extract<Card, { type: "dateline" }> }> = ({ card }) => {
  const { opacity, rise } = useCardMotion(card.start, card.end);
  return (
    <div
      style={{
        position: "absolute",
        top: TAG_TOP,
        left: 56,
        opacity,
        transform: `translateX(${-rise}px)`,
        display: "flex",
        alignItems: "center",
        gap: 14,
        backgroundColor: "rgba(3, 7, 18, 0.88)",
        border: "1px solid rgba(255,255,255,0.18)",
        borderRadius: 6,
        padding: "8px 18px",
        fontFamily: FONT,
      }}
    >
      <div style={{ color: "#94a3b8", fontSize: 15, fontWeight: 900, letterSpacing: 2.5 }}>DATELINE</div>
      <div style={{ width: 2, height: 22, backgroundColor: "#ef4444" }} />
      <div style={{ color: "#ffffff", fontSize: 24, fontWeight: 900, letterSpacing: 2 }}>
        {card.place}
        {card.date ? <span style={{ color: "#7dd3fc" }}> • {card.date}</span> : null}
      </div>
    </div>
  );
};

const NameTag: React.FC<{ card: Extract<Card, { type: "name" }> }> = ({ card }) => {
  const { opacity, rise } = useCardMotion(card.start, card.end);
  return (
    <div
      style={{
        position: "absolute",
        top: TAG_TOP,
        left: 56,
        opacity,
        transform: `translateX(${-rise}px)`,
        display: "flex",
        fontFamily: FONT,
        boxShadow: "0 12px 30px rgba(0,0,0,0.6)",
      }}
    >
      <div style={{ width: 8, backgroundColor: "#38bdf8" }} />
      <div style={{ backgroundColor: "rgba(3, 7, 18, 0.92)", padding: "10px 22px 12px" }}>
        <div style={{ color: "#ffffff", fontSize: 32, fontWeight: 900, letterSpacing: 1 }}>{card.name}</div>
        <div style={{ color: "#7dd3fc", fontSize: 19, fontWeight: 700, letterSpacing: 1.5, textTransform: "uppercase" }}>
          {card.role}
        </div>
      </div>
    </div>
  );
};

const BIG = new Set(["reported", "quote", "stat", "compare"]);

export const EvidenceLayer: React.FC<{ storyId: string; sourceUrl?: string }> = ({ storyId, sourceUrl }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const cards = allCards[storyId] || [];
  const visible = cards.filter((c) => t >= c.start && t < c.end);
  if (!visible.length) return null;

  // Darken the picture behind a big card so the text reads like a clean graphic.
  const big = visible.find((c) => BIG.has(c.type));
  const dim = big
    ? Math.min(
        interpolate(t, [big.start, big.start + 0.35], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        interpolate(t, [big.end - 0.35, big.end], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
      )
    : 0;

  return (
    <div style={{ position: "absolute", inset: 0, pointerEvents: "none", zIndex: 30 }}>
      {dim > 0 && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: 810,
            opacity: dim,
            background:
              "linear-gradient(90deg, rgba(3,7,18,0.92) 0%, rgba(3,7,18,0.82) 45%, rgba(3,7,18,0.45) 75%, rgba(3,7,18,0.25) 100%)",
          }}
        />
      )}
      {visible.map((c, i) => {
        switch (c.type) {
          case "dateline":
            return <DatelineTag key={i} card={c} />;
          case "name":
            return <NameTag key={i} card={c} />;
          case "reported":
            return <ReportedCard key={i} card={c} sourceUrl={sourceUrl} />;
          case "quote":
            return <QuoteCard key={i} card={c} />;
          case "stat":
            return <StatCard key={i} card={c} />;
          case "compare":
            return <CompareCard key={i} card={c} />;
          default:
            return null;
        }
      })}
    </div>
  );
};
