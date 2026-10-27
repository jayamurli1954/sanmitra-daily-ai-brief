import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  OffthreadVideo,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { BarLineChart, ChartCard, DivergingLines, PALETTE, Waterfall } from "./charts";
import timingsData from "./styleTestTimings.json";

/**
 * Style test v3 for the finance channel: Ramesh as AI-generated stylised 3D
 * art (Gemini stills + one Gemini/Veo clip), brought to life with camera moves
 * and crossfades, with the animated finance charts on the empty wall.
 * Story and figures from "Profit is Vanity, Cash is Reality" (Issue #1);
 * the month-by-month series are illustrative.
 */

type Timing = { id: string; audio: string; seconds: number; text: string };
const timings = timingsData as Timing[];
export const FT_AI_FPS = 30;
export const styleTestAIFrames = () => timings.reduce((n, t) => n + Math.round(t.seconds * FT_AI_FPS), 0);

const STARTS = timings.reduce<number[]>((acc, _t, i) => [...acc, i ? acc[i - 1] + Math.round(timings[i - 1].seconds * FT_AI_FPS) : 0], []);
const [S1, S2, S3] = STARTS;
const END = styleTestAIFrames();
const TITLE_AT = END - 120;
const FADE = 18;
const FONT = "'Segoe UI', system-ui, -apple-system, Roboto, sans-serif";
const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const ART = "finance/ramesh/hd";

/** A still with a slow camera move; fades in and out at its edges. */
const Still: React.FC<{
  src: string;
  from: number;
  to: number;
  zoom: [number, number];
  origin: string;
  panX?: [number, number];
}> = ({ src, from, to, zoom, origin, panX = [0, 0] }) => {
  const frame = useCurrentFrame();
  if (frame < from - FADE || frame > to + FADE) return null;
  const t = interpolate(frame, [from - FADE, to + FADE], [0, 1], clamp);
  const e = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  const opacity = Math.min(
    interpolate(frame, [from - FADE, from], [0, 1], clamp),
    interpolate(frame, [to, to + FADE], [1, 0], clamp),
  );
  return (
    <AbsoluteFill style={{ opacity }}>
      <Img
        src={staticFile(`${ART}/${src}`)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `translateX(${panX[0] + (panX[1] - panX[0]) * e}px) scale(${zoom[0] + (zoom[1] - zoom[0]) * e})`,
          transformOrigin: origin,
        }}
      />
    </AbsoluteFill>
  );
};

const ChartSlot: React.FC<{ from: number; to: number; children: (enter: number) => React.ReactNode }> = ({ from, to, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - from, fps, config: { damping: 16, stiffness: 100 } });
  const exit = interpolate(frame, [to - 12, to], [1, 0], clamp);
  if (frame < from - 1 || frame > to) return null;
  return <div style={{ position: "absolute", left: 1040, top: 120 }}>{children(Math.min(enter, exit))}</div>;
};

const Chip: React.FC<{ at: number }> = ({ at }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const e = spring({ frame: frame - at, fps, config: { damping: 12, stiffness: 120 } });
  return (
    <div
      style={{
        position: "absolute",
        left: 1080,
        top: 712,
        transform: `scale(${e})`,
        transformOrigin: "left center",
        background: PALETTE.red,
        color: "#fff",
        fontFamily: FONT,
        fontSize: 32,
        fontWeight: 800,
        padding: "12px 26px",
        borderRadius: 999,
        boxShadow: "0 12px 26px rgba(0,0,0,0.25)",
      }}
    >
      📅 Salaries due on Friday
    </div>
  );
};

const Subtitle: React.FC<{ text: string; frames: number }> = ({ text, frames }) => {
  const frame = useCurrentFrame();
  const words = text.split(" ");
  const chunks: string[] = [];
  for (let i = 0; i < words.length; i += 8) chunks.push(words.slice(i, i + 8).join(" "));
  const speaking = frames - 0.7 * FT_AI_FPS;
  let acc = 0;
  const idx = chunks.findIndex((c) => {
    acc += c.split(" ").length;
    return frame < (acc / words.length) * speaking;
  });
  return (
    <div style={{ position: "absolute", bottom: 40, left: 0, right: 0, display: "flex", justifyContent: "center", fontFamily: FONT }}>
      <div style={{ background: "rgba(20,24,32,0.82)", color: "#fff", fontSize: 34, fontWeight: 600, padding: "10px 26px", borderRadius: 10 }}>
        {chunks[idx === -1 ? chunks.length - 1 : idx]}
      </div>
    </div>
  );
};

const TitleCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = spring({ frame: frame - TITLE_AT, fps, config: { damping: 18, stiffness: 90 } });
  if (frame < TITLE_AT - 1) return null;
  return (
    <AbsoluteFill style={{ background: `rgba(29,53,87,${0.93 * t})`, justifyContent: "center", alignItems: "center", fontFamily: FONT }}>
      <div style={{ opacity: t, transform: `translateY(${(1 - t) * 40}px)`, textAlign: "center" }}>
        <div style={{ color: "#ffffff", fontSize: 108, fontWeight: 900, lineHeight: 1.1 }}>Profit is Vanity.</div>
        <div style={{ color: PALETTE.orange, fontSize: 108, fontWeight: 900, lineHeight: 1.1 }}>Cash is Reality.</div>
        <div style={{ color: "rgba(255,255,255,0.75)", fontSize: 32, fontWeight: 700, marginTop: 34, letterSpacing: 3 }}>
          OFFICEMITRA FINANCE INSIGHTS
        </div>
      </div>
    </AbsoluteFill>
  );
};

const MONTHS = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"];

export const FinanceStyleTestAI: React.FC = () => {
  const frame = useCurrentFrame();
  // The Gemini clip covers scene 1, then hands over to the stills.
  const clipOpacity = interpolate(frame, [S2 - 6, S2 + 12], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ background: "#f3eadb", overflow: "hidden" }}>
      <Audio src={staticFile("audio/officemitra_theme.wav")} volume={0.05} loop />

      {/* Scene 1: the best month ever (animated clip) */}
      {frame < S2 + 14 && (
        <AbsoluteFill style={{ opacity: clipOpacity }}>
          <OffthreadVideo
            src={staticFile("finance/ramesh/clip2_celebrate.mp4")}
            muted
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </AbsoluteFill>
      )}

      {/* Scene 2: checks the phone, then the worry sets in */}
      <Still src="shot3_phone.jpg" from={S2} to={S2 + 120} zoom={[1.0, 1.08]} origin="25% 40%" />
      <Still src="shot4_worried.jpg" from={S2 + 120} to={S3} zoom={[1.04, 1.14]} origin="22% 35%" />

      {/* Scene 3: the unpaid invoices */}
      <Still src="shot5_invoices.jpg" from={S3} to={END} zoom={[1.02, 1.1]} origin="30% 45%" panX={[0, -30]} />

      <ChartSlot from={S1 + 25} to={S2}>
        {(enter) => (
          <ChartCard title="Sales and profit" subtitle="₹ lakh, last six months" enter={enter} width={820} height={560}>
            <BarLineChart labels={MONTHS} bars={[32, 36, 38, 41, 45, 50]} line={[5, 6, 6.5, 7, 8, 10]} max={60} start={S1 + 50} barLabel="Sales" lineLabel="Profit" />
          </ChartCard>
        )}
      </ChartSlot>
      <ChartSlot from={S2 + 40} to={S3}>
        {(enter) => (
          <ChartCard title="Profit vs cash collected" subtitle="₹ lakh per month" enter={enter} width={820} height={560}>
            <DivergingLines labels={MONTHS} up={[5, 6, 6.5, 7, 8, 10]} down={[30, 28, 22, 15, 9, 5]} max={32} start={S2 + 60} upLabel="Profit ₹10L" downLabel="Collected ₹5L" />
          </ChartCard>
        )}
      </ChartSlot>
      <Sequence from={S2} durationInFrames={S3 - S2} layout="none">
        <Chip at={175} />
      </Sequence>
      <ChartSlot from={S3 + 10} to={TITLE_AT + 10}>
        {(enter) => (
          <ChartCard title="Where this month's sales are" subtitle="₹ lakh" enter={enter} width={820} height={560}>
            <Waterfall
              max={55}
              start={S3 + 35}
              steps={[
                { label: "Sales", value: 50, kind: "total", color: PALETTE.navy, caption: "invoiced" },
                { label: "With customers", value: 45, kind: "minus", color: PALETTE.orange, caption: "not yet paid" },
                { label: "Collected", value: 5, kind: "result", color: PALETTE.green, caption: "cash in hand" },
              ]}
            />
          </ChartCard>
        )}
      </ChartSlot>

      {timings.map((t, i) => (
        <Sequence key={t.id} from={STARTS[i]} durationInFrames={Math.round(t.seconds * FT_AI_FPS)}>
          <Audio src={staticFile(t.audio)} />
          <Subtitle text={t.text} frames={Math.round(t.seconds * FT_AI_FPS)} />
        </Sequence>
      ))}
      <TitleCard />
    </AbsoluteFill>
  );
};
