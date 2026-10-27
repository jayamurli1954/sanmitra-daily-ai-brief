import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Pose, poseAt, Ramesh } from "./characters/Ramesh";
import { BarLineChart, ChartCard, DivergingLines, PALETTE, Waterfall } from "./charts";
import timingsData from "./styleTestTimings.json";
import mouthData from "./styleTestMouth.json";

/**
 * Style test for the finance channel (OfficeMitra Finance Insights):
 * flat 2D illustration drawn in code, a posable character with lip sync,
 * camera moves, and animated finance charts.
 * Story and figures from "Profit is Vanity, Cash is Reality" (Issue #1);
 * the month-by-month series are illustrative.
 */

type Timing = { id: string; audio: string; seconds: number; text: string };
const timings = timingsData as Timing[];
const mouth = mouthData as Record<string, number[]>;
export const FT_FPS = 30;
export const styleTestFrames = () => timings.reduce((n, t) => n + Math.round(t.seconds * FT_FPS), 0);

const STARTS = timings.reduce<number[]>((acc, t, i) => [...acc, i ? acc[i - 1] + Math.round(timings[i - 1].seconds * FT_FPS) : 0], []);
const [S1, S2, S3] = STARTS;
const END = styleTestFrames();
const TITLE_AT = END - 120;

const C = { wall: "#f3eadb", wallShade: "#eadcc6", floor: "#d9c3a5", desk: "#8d5a3b", deskTop: "#a86b45" };
const FONT = "'Segoe UI', system-ui, -apple-system, Roboto, sans-serif";
const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

// ------------------------------------------------------------------ Ramesh's performance

const REST = { shoulder: 20, elbow: -123 };
const BASE: Pose = { mood: 0, mouth: 0, headTurn: 0, lookX: 0, lookY: 0, lean: 0, left: REST, right: REST, phone: 0 };
const POINT = { shoulder: 80, elbow: 40 };
const CHEER = { shoulder: 160, elbow: 15 };
const PHONE = { shoulder: -35, elbow: -163 };
const FOREHEAD = { shoulder: -158, elbow: -8 };

const KEYS: [number, Partial<Pose>][] = [
  [0, {}],
  [S1 + 30, { headTurn: 0.35, lookX: 0.9, lookY: -0.2 }], // looks at the chart
  [S1 + 120, { right: POINT, lean: 2 }], // points at the bars
  [S1 + 175, { right: POINT }],
  [S1 + 200, { right: CHEER, lean: -3, headTurn: 0, lookX: 0, lookY: -0.4 }], // "best month ever"
  [S1 + 215, { right: { shoulder: 150, elbow: 30 } }],
  [S1 + 230, { right: CHEER }],
  [S1 + 270, { right: REST, lean: 0, lookY: 0 }],
  [S2 + 8, { right: REST }],
  [S2 + 34, { right: PHONE, phone: 1, headTurn: 0.25, lookX: 0.55, lookY: 0.6 }], // checks the phone
  [S2 + 70, { mood: 0.2 }],
  [S2 + 95, { mood: 1, lean: -2 }], // only five lakh
  [S2 + 140, { left: REST }],
  [S2 + 170, { left: FOREHEAD, lookY: 0.2 }], // salaries due on Friday
  [S2 + 235, { left: FOREHEAD }],
  [S2 + 262, { left: REST, headTurn: 0.4, lookX: 0.9, lookY: 0 }],
  [S3 + 10, { right: PHONE, phone: 1 }],
  [S3 + 36, { right: REST, phone: 0 }],
  [S3 + 60, { headTurn: 0.45, lookX: 1, lean: 1 }],
];

const performance = (frame: number): Pose => {
  const p = poseAt(frame, KEYS, BASE);
  // Lip sync from the narration's loudness.
  const sceneIdx = frame >= S3 ? 2 : frame >= S2 ? 1 : 0;
  const env = mouth[timings[sceneIdx].id] || [];
  const m = env[frame - STARTS[sceneIdx]] ?? 0;
  // A slow head shake while the ₹45 lakh sinks in.
  const shake = frame > S3 + 70 && frame < S3 + 150 ? Math.sin((frame - S3) / 5) * 0.25 : 0;
  return { ...p, mouth: m * 0.9, headTurn: p.headTurn + shake };
};

// ------------------------------------------------------------------ the set

const WallClock: React.FC = () => {
  const frame = useCurrentFrame();
  // Time speeds up once the cash problem appears.
  const minute = frame < S2 ? frame * 1.2 : S2 * 1.2 + (frame - S2) * 6;
  return (
    <g transform="translate(860 150)">
      <circle r={58} fill="#fff" stroke={PALETTE.navy} strokeWidth={8} />
      {[...Array(12)].map((_, i) => (
        <rect key={i} x={-2} y={-50} width={4} height={10} fill={PALETTE.navy} transform={`rotate(${i * 30})`} />
      ))}
      <rect x={-3} y={-28} width={6} height={30} rx={3} fill={PALETTE.navy} transform={`rotate(${minute / 12 + 300})`} />
      <rect x={-2} y={-42} width={4} height={44} rx={2} fill={PALETTE.orange} transform={`rotate(${minute})`} />
      <circle r={6} fill={PALETTE.navy} />
    </g>
  );
};

const Office: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <svg viewBox="0 0 1920 1080" width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
      <rect width={1920} height={1080} fill={C.wall} />
      <rect y={760} width={1920} height={320} fill={C.floor} />
      <rect y={748} width={1920} height={14} fill={C.wallShade} />
      <g transform="translate(60 110)">
        <rect width={460} height={360} rx={14} fill="#bfe3f2" stroke="#fff" strokeWidth={16} />
        {[[20, 190, 70], [100, 130, 60], [170, 220, 70], [250, 160, 70], [330, 110, 50], [390, 200, 60]].map(([x, h, w], i) => (
          <rect key={i} x={x} y={360 - h} width={w} height={h} fill={i % 2 ? "#7fa7c4" : "#5f86a6"} />
        ))}
        <rect x={222} y={0} width={16} height={360} fill="#fff" />
        <circle cx={60 + ((frame * 0.4) % 420)} cy={50} r={16} fill="#fff" opacity={0.8} />
      </g>
      <WallClock />
      <g transform="translate(1840 640)">
        <rect x={-40} y={60} width={80} height={90} rx={10} fill={PALETTE.orange} />
        {[-40, -15, 15, 40].map((r, i) => (
          <ellipse key={i} cx={0} cy={10} rx={22} ry={70} fill={i % 2 ? "#3f8f6b" : "#2f7a59"} transform={`rotate(${r + Math.sin(frame / 40 + i) * 3} 0 70)`} />
        ))}
      </g>
    </svg>
  );
};

const Desk: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <svg viewBox="0 0 1920 1080" width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
      <rect x={100} y={760} width={880} height={34} rx={8} fill={C.deskTop} />
      <rect x={130} y={794} width={820} height={286} fill={C.desk} />
      <rect x={160} y={830} width={280} height={90} rx={8} fill="#7a4c31" />
      <rect x={200} y={736} width={150} height={26} rx={4} fill="#fffaf2" transform="rotate(-6 275 749)" />
      <rect x={212} y={744} width={110} height={6} rx={3} fill="#d8cbb4" transform="rotate(-6 275 749)" />
      <rect x={760} y={700} width={100} height={64} rx={10} fill="#4a4e57" />
      <rect x={772} y={710} width={76} height={18} rx={4} fill="#b9e4c9" />
      <rect x={880} y={712} width={56} height={52} rx={10} fill="#ffffff" />
      <path d="M936 724 q22 4 0 26" stroke="#ffffff" strokeWidth={8} fill="none" />
      {[0, 1].map((i) => (
        <path
          key={i}
          d={`M${898 + i * 20} 700 q-10 -20 0 -40 q10 -20 0 -40`}
          stroke="#c9b9a1"
          strokeWidth={5}
          fill="none"
          opacity={0.35 + 0.25 * Math.sin(frame / 12 + i)}
          transform={`translate(0 ${-((frame / 2 + i * 15) % 20)})`}
        />
      ))}
    </svg>
  );
};

// ------------------------------------------------------------------ effects

const Confetti: React.FC<{ at: number }> = ({ at }) => {
  const frame = useCurrentFrame();
  const t = frame - at;
  if (t < 0 || t > 70) return null;
  const colors = [PALETTE.orange, PALETTE.green, "#e9c46a", PALETTE.navy];
  return (
    <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
      {[...Array(36)].map((_, i) => {
        const angle = (i / 36) * Math.PI * 2;
        const speed = 9 + (i % 5) * 2;
        const x = 1380 + Math.cos(angle) * speed * t;
        const y = 300 + Math.sin(angle) * speed * t + 0.25 * t * t;
        return (
          <rect key={i} x={x} y={y} width={14} height={8} fill={colors[i % 4]} opacity={1 - t / 70} transform={`rotate(${t * 9 + i * 20} ${x} ${y})`} />
        );
      })}
    </svg>
  );
};

/** Invoices leave the desk and pile up with customers. */
const FlyingInvoices: React.FC<{ at: number }> = ({ at }) => {
  const frame = useCurrentFrame();
  return (
    <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
      {[...Array(9)].map((_, i) => {
        const t = interpolate(frame, [at + i * 9, at + i * 9 + 45], [0, 1], clamp);
        if (t <= 0 || t >= 1) return null;
        const x = 300 + (1500 - 300) * t;
        const y = 730 - Math.sin(t * Math.PI) * 360 + (920 - 730) * t;
        return (
          <g key={i} transform={`translate(${x} ${y}) rotate(${t * 220 - 30})`}>
            <rect x={-28} y={-36} width={56} height={72} rx={5} fill="#fff" stroke="#d8cbb4" strokeWidth={3} />
            <rect x={-18} y={-24} width={36} height={6} rx={3} fill={PALETTE.orange} />
            <rect x={-18} y={-10} width={30} height={5} rx={2} fill="#cfc3ad" />
            <rect x={-18} y={2} width={34} height={5} rx={2} fill="#cfc3ad" />
            <text x={0} y={28} textAnchor="middle" fontSize={16} fontWeight={800} fill={PALETTE.ink} fontFamily={FONT}>₹</text>
          </g>
        );
      })}
      <g transform="translate(1500 900)" opacity={interpolate(frame, [at, at + 20], [0, 1], clamp)}>
        <rect x={-110} y={-20} width={220} height={70} rx={14} fill={PALETTE.orange} />
        <text x={0} y={25} textAnchor="middle" fontSize={30} fontWeight={800} fill="#fff" fontFamily={FONT}>Customers</text>
      </g>
    </svg>
  );
};

const Chip: React.FC<{ at: number; children: React.ReactNode; color: string; top: number }> = ({ at, children, color, top }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const e = spring({ frame: frame - at, fps, config: { damping: 12, stiffness: 120 } });
  return (
    <div
      style={{
        position: "absolute",
        left: 1080,
        top,
        transform: `scale(${e})`,
        transformOrigin: "left center",
        background: color,
        color: "#fff",
        fontFamily: FONT,
        fontSize: 32,
        fontWeight: 800,
        padding: "12px 26px",
        borderRadius: 999,
        boxShadow: "0 12px 26px rgba(0,0,0,0.18)",
      }}
    >
      {children}
    </div>
  );
};

// ------------------------------------------------------------------ charts per scene

const MONTHS = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"];

const ChartSlot: React.FC<{ from: number; to: number; children: (enter: number) => React.ReactNode }> = ({ from, to, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - from, fps, config: { damping: 16, stiffness: 100 } });
  const exit = interpolate(frame, [to - 12, to], [1, 0], clamp);
  if (frame < from - 1 || frame > to) return null;
  return <div style={{ position: "absolute", left: 1040, top: 140 }}>{children(Math.min(enter, exit))}</div>;
};

// ------------------------------------------------------------------ camera

const camera = (frame: number) => {
  const k: [number, number, number, number][] = [
    // frame, scale, focusX, focusY
    [0, 1, 960, 540],
    [S2 + 30, 1, 960, 540],
    [S2 + 70, 1.07, 1000, 470], // push in on Ramesh and his phone, chart still in frame
    [S2 + 240, 1.07, 1000, 470],
    [S3 - 4, 1, 960, 540],
    [S3 + 20, 1.06, 1300, 480], // drift towards the chart
    [TITLE_AT, 1.06, 1300, 480],
  ];
  let i = 0;
  while (i < k.length - 2 && frame > k[i + 1][0]) i++;
  const [f0, s0, x0, y0] = k[i];
  const [f1, s1, x1, y1] = k[i + 1];
  const t = interpolate(frame, [f0, f1], [0, 1], clamp);
  const e = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  return { s: s0 + (s1 - s0) * e, x: x0 + (x1 - x0) * e, y: y0 + (y1 - y0) * e };
};

// ------------------------------------------------------------------ subtitles

const Subtitle: React.FC<{ text: string; frames: number }> = ({ text, frames }) => {
  const frame = useCurrentFrame();
  const words = text.split(" ");
  const chunks: string[] = [];
  for (let i = 0; i < words.length; i += 8) chunks.push(words.slice(i, i + 8).join(" "));
  const speaking = frames - 0.7 * FT_FPS;
  let acc = 0;
  const idx = chunks.findIndex((c) => {
    acc += c.split(" ").length;
    return frame < (acc / words.length) * speaking;
  });
  return (
    <div style={{ position: "absolute", bottom: 40, left: 0, right: 0, display: "flex", justifyContent: "center", fontFamily: FONT }}>
      <div style={{ background: "rgba(31,36,48,0.85)", color: "#fff", fontSize: 34, fontWeight: 600, padding: "10px 26px", borderRadius: 10 }}>
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
    <AbsoluteFill style={{ background: `rgba(29,53,87,${0.94 * t})`, justifyContent: "center", alignItems: "center", fontFamily: FONT }}>
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

// ------------------------------------------------------------------ composition

export const FinanceStyleTest: React.FC = () => {
  const frame = useCurrentFrame();
  const pose = performance(frame);
  const cam = camera(frame);
  return (
    <AbsoluteFill style={{ background: C.wall, overflow: "hidden" }}>
      <Audio src={staticFile("audio/officemitra_theme.wav")} volume={0.05} loop />
      <AbsoluteFill style={{ transform: `scale(${cam.s})`, transformOrigin: `${cam.x}px ${cam.y}px` }}>
        <Office />
        <div style={{ position: "absolute", left: 260, top: 150, width: 520, height: 693 }}>
          <Ramesh pose={pose} />
        </div>
        <Desk />

        {/* Scene 1: six months of growth, the best month last */}
        <ChartSlot from={S1 + 20} to={S2}>
          {(enter) => (
            <ChartCard title="Sales and profit" subtitle="₹ lakh, last six months" enter={enter} width={820} height={560}>
              <BarLineChart labels={MONTHS} bars={[32, 36, 38, 41, 45, 50]} line={[5, 6, 6.5, 7, 8, 10]} max={60} start={S1 + 45} barLabel="Sales" lineLabel="Profit" />
            </ChartCard>
          )}
        </ChartSlot>
        <Confetti at={S1 + 200} />

        {/* Scene 2: profit keeps rising while collections fall */}
        <ChartSlot from={S2 + 40} to={S3}>
          {(enter) => (
            <ChartCard title="Profit vs cash collected" subtitle="₹ lakh per month" enter={enter} width={820} height={560}>
              <DivergingLines labels={MONTHS} up={[5, 6, 6.5, 7, 8, 10]} down={[30, 28, 22, 15, 9, 5]} max={32} start={S2 + 60} upLabel="Profit ₹10L" downLabel="Collected ₹5L" />
            </ChartCard>
          )}
        </ChartSlot>
        <Sequence from={S2} durationInFrames={S3 - S2} layout="none">
          <Chip at={175} color={PALETTE.red} top={730}>📅 Salaries due on Friday</Chip>
        </Sequence>

        {/* Scene 3: where this month's ₹50 lakh actually is */}
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
        <FlyingInvoices at={S3 + 70} />
      </AbsoluteFill>

      {timings.map((t, i) => (
        <Sequence key={t.id} from={STARTS[i]} durationInFrames={Math.round(t.seconds * FT_FPS)}>
          <Audio src={staticFile(t.audio)} />
          <Subtitle text={t.text} frames={Math.round(t.seconds * FT_FPS)} />
        </Sequence>
      ))}
      <TitleCard />
    </AbsoluteFill>
  );
};
