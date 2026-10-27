import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

/**
 * Animated finance charts for the OfficeMitra Finance Insights channel.
 * All values are passed in by the episode; frames are local to the chart's Sequence.
 */

export const PALETTE = {
  navy: "#1d3557",
  orange: "#e8862a",
  green: "#2a9d8f",
  red: "#d1495b",
  grid: "#e6dccb",
  ink: "#1f2430",
  muted: "#7b6f60",
  card: "#fffaf2",
};
const FONT = "'Segoe UI', system-ui, -apple-system, Roboto, sans-serif";

const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);

export const ChartCard: React.FC<{
  title: string;
  subtitle?: string;
  enter: number;
  width: number;
  height: number;
  children: React.ReactNode;
}> = ({ title, subtitle, enter, width, height, children }) => (
  <div
    style={{
      width,
      height,
      background: PALETTE.card,
      borderRadius: 26,
      boxShadow: "0 30px 60px rgba(60,40,20,0.22)",
      padding: "28px 36px",
      boxSizing: "border-box",
      fontFamily: FONT,
      color: PALETTE.ink,
      opacity: enter,
      transform: `translateY(${(1 - enter) * 50}px) scale(${0.94 + 0.06 * enter})`,
      position: "relative",
    }}
  >
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
      <div style={{ fontSize: 34, fontWeight: 800 }}>{title}</div>
      <div style={{ fontSize: 18, fontWeight: 700, color: PALETTE.muted, letterSpacing: 2 }}>ILLUSTRATIVE</div>
    </div>
    {subtitle && <div style={{ fontSize: 22, color: PALETTE.muted, marginTop: 4 }}>{subtitle}</div>}
    {children}
  </div>
);

// ------------------------------------------------------------------ bar chart with a line overlay

export const BarLineChart: React.FC<{
  labels: string[];
  bars: number[];
  line: number[];
  max: number;
  start: number; // frame the bars begin to grow
  barLabel: string;
  lineLabel: string;
  width?: number;
  height?: number;
}> = ({ labels, bars, line, max, start, barLabel, lineLabel, width = 760, height = 420 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const padL = 70;
  const padB = 50;
  const plotW = width - padL - 20;
  const plotH = height - padB - 20;
  const step = plotW / bars.length;
  const y = (v: number) => 20 + plotH - (v / max) * plotH;
  const lineStart = start + bars.length * 12 + 10;
  const lineT = easeOut(interpolate(frame, [lineStart, lineStart + 40], [0, 1], clamp));
  const pts = line.map((v, i) => [padL + step * i + step / 2, y(v)] as const);
  const path = pts.map(([px, py], i) => `${i ? "L" : "M"}${px} ${py}`).join(" ");
  const len = pts.reduce((acc, p, i) => (i ? acc + Math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1]) : 0), 0);
  const last = bars.length - 1;
  const glow = spring({ frame: frame - (start + last * 12 + 14), fps, config: { damping: 8, stiffness: 120 } });
  return (
    <svg width={width} height={height} style={{ marginTop: 14 }}>
      {[0, 0.25, 0.5, 0.75, 1].map((g) => (
        <g key={g}>
          <line x1={padL} x2={width - 20} y1={y(max * g)} y2={y(max * g)} stroke={PALETTE.grid} strokeWidth={2} />
          <text x={padL - 12} y={y(max * g) + 7} textAnchor="end" fontSize={20} fill={PALETTE.muted} fontFamily={FONT}>
            {Math.round(max * g)}
          </text>
        </g>
      ))}
      {bars.map((v, i) => {
        const g = spring({ frame: frame - (start + i * 12), fps, config: { damping: 14, stiffness: 90 } });
        const h = (v / max) * plotH * g;
        const x = padL + step * i + step * 0.18;
        const isLast = i === last;
        return (
          <g key={i}>
            <rect x={x} y={20 + plotH - h} width={step * 0.64} height={h} rx={8} fill={isLast ? PALETTE.navy : "#6f8fb3"} />
            {isLast && (
              <rect x={x - 6} y={20 + plotH - h - 6} width={step * 0.64 + 12} height={h + 6} rx={12} fill="none" stroke={PALETTE.orange} strokeWidth={5} opacity={glow} />
            )}
            <text x={x + step * 0.32} y={height - 18} textAnchor="middle" fontSize={22} fill={PALETTE.muted} fontFamily={FONT}>
              {labels[i]}
            </text>
          </g>
        );
      })}
      <path d={path} fill="none" stroke={PALETTE.green} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={len} strokeDashoffset={len * (1 - lineT)} />
      {pts.map(([px, py], i) => (
        <circle key={i} cx={px} cy={py} r={9} fill="#fff" stroke={PALETTE.green} strokeWidth={5} opacity={lineT > (i + 0.5) / pts.length ? 1 : 0} />
      ))}
      <g fontFamily={FONT} fontSize={22} fontWeight={700}>
        <rect x={padL + 4} y={24} width={22} height={22} rx={4} fill="#6f8fb3" />
        <text x={padL + 34} y={42} fill={PALETTE.ink}>{barLabel}</text>
        <circle cx={padL + 240} cy={35} r={10} fill="#fff" stroke={PALETTE.green} strokeWidth={5} />
        <text x={padL + 258} y={42} fill={PALETTE.ink}>{lineLabel}</text>
      </g>
    </svg>
  );
};

// ------------------------------------------------------------------ two diverging lines

export const DivergingLines: React.FC<{
  labels: string[];
  up: number[];
  down: number[];
  max: number;
  start: number;
  upLabel: string;
  downLabel: string;
  width?: number;
  height?: number;
}> = ({ labels, up, down, max, start, upLabel, downLabel, width = 760, height = 420 }) => {
  const frame = useCurrentFrame();
  const padL = 70;
  const padB = 50;
  const plotW = width - padL - 210; // room for the end labels
  const plotH = height - padB - 30;
  const x = (i: number) => padL + (plotW / (labels.length - 1)) * i;
  const y = (v: number) => 30 + plotH - (v / max) * plotH;
  const t = easeOut(interpolate(frame, [start, start + 70], [0, 1], clamp));
  const shown = t * (labels.length - 1);
  const partial = (vals: number[]) => {
    const out: [number, number][] = [];
    for (let i = 0; i <= Math.floor(shown); i++) out.push([x(i), y(vals[i])]);
    const k = Math.floor(shown);
    if (k < vals.length - 1) {
      const f = shown - k;
      out.push([x(k) + (x(k + 1) - x(k)) * f, y(vals[k] + (vals[k + 1] - vals[k]) * f)]);
    }
    return out;
  };
  const toPath = (p: [number, number][]) => p.map(([px, py], i) => `${i ? "L" : "M"}${px} ${py}`).join(" ");
  const pu = partial(up);
  const pd = partial(down);
  const area = pu.length > 1 ? `${toPath(pu)} ${[...pd].reverse().map(([px, py]) => `L${px} ${py}`).join(" ")} Z` : "";
  const endT = interpolate(frame, [start + 70, start + 90], [0, 1], clamp);
  const lastU = pu[pu.length - 1];
  const lastD = pd[pd.length - 1];
  return (
    <svg width={width} height={height} style={{ marginTop: 14 }}>
      {[0, 0.5, 1].map((g) => (
        <g key={g}>
          <line x1={padL} x2={padL + plotW} y1={y(max * g)} y2={y(max * g)} stroke={PALETTE.grid} strokeWidth={2} />
          <text x={padL - 12} y={y(max * g) + 7} textAnchor="end" fontSize={20} fill={PALETTE.muted} fontFamily={FONT}>
            {Math.round(max * g)}
          </text>
        </g>
      ))}
      {labels.map((l, i) => (
        <text key={l} x={x(i)} y={height - 16} textAnchor="middle" fontSize={22} fill={PALETTE.muted} fontFamily={FONT}>
          {l}
        </text>
      ))}
      {area && <path d={area} fill={PALETTE.orange} opacity={0.12} />}
      <path d={toPath(pd)} fill="none" stroke={PALETTE.red} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" />
      <path d={toPath(pu)} fill="none" stroke={PALETTE.green} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" />
      {lastU && <circle cx={lastU[0]} cy={lastU[1]} r={10} fill={PALETTE.green} />}
      {lastD && <circle cx={lastD[0]} cy={lastD[1]} r={10} fill={PALETTE.red} />}
      <g opacity={endT} fontFamily={FONT} fontWeight={800} fontSize={26}>
        <text x={x(labels.length - 1) + 18} y={y(up[up.length - 1]) + 8} fill={PALETTE.green}>{upLabel}</text>
        <text x={x(labels.length - 1) + 18} y={y(down[down.length - 1]) + 8} fill={PALETTE.red}>{downLabel}</text>
      </g>
    </svg>
  );
};

// ------------------------------------------------------------------ waterfall

export const Waterfall: React.FC<{
  steps: { label: string; value: number; kind: "total" | "plus" | "minus" | "result"; color: string; caption: string; at?: number }[];
  max: number;
  start: number;
  width?: number;
  height?: number;
}> = ({ steps, max, start, width = 760, height = 420 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const padB = 56;
  const plotH = height - padB - 50;
  const step = width / steps.length;
  const y = (v: number) => 50 + plotH - (v / max) * plotH;
  let running = 0;
  return (
    <svg width={width} height={height} style={{ marginTop: 14 }}>
      <line x1={0} x2={width} y1={y(0)} y2={y(0)} stroke={PALETTE.grid} strokeWidth={3} />
      {steps.map((s, i) => {
        const g = spring({ frame: frame - (s.at ?? start + i * 22), fps, config: { damping: 14, stiffness: 80 } });
        let top: number;
        let bottom: number;
        if (s.kind === "total") {
          top = s.value;
          bottom = 0;
          running = s.value;
        } else if (s.kind === "plus") {
          top = running + s.value;
          bottom = running;
          running = top;
        } else if (s.kind === "minus") {
          top = running;
          bottom = running - s.value;
          running = bottom;
        } else {
          top = s.value;
          bottom = 0;
        }
        const yTop = y(top);
        const yBot = y(bottom);
        const h = (yBot - yTop) * g;
        const x = step * i + step * 0.18;
        const w = step * 0.64;
        // A "minus" bar falls from the top of the previous bar.
        const drawY = s.kind === "minus" ? yTop : yBot - h;
        return (
          <g key={i} fontFamily={FONT}>
            {i > 0 && <line x1={step * (i - 1) + step * 0.82} x2={x} y1={yTop} y2={yTop} stroke={PALETTE.muted} strokeDasharray="6 6" strokeWidth={2} opacity={g} />}
            <rect x={x} y={drawY} width={w} height={Math.max(0, h)} rx={8} fill={s.color} />
            <text x={x + w / 2} y={yTop - 14} textAnchor="middle" fontSize={34} fontWeight={900} fill={s.color} opacity={g}>
              {s.kind === "minus" ? `−₹${s.value}L` : s.kind === "plus" ? `+₹${s.value}L` : `₹${s.value}L`}
            </text>
            <text x={x + w / 2} y={height - 26} textAnchor="middle" fontSize={24} fontWeight={800} fill={PALETTE.ink}>
              {s.label}
            </text>
            <text x={x + w / 2} y={height - 2} textAnchor="middle" fontSize={18} fill={PALETTE.muted}>
              {s.caption}
            </text>
          </g>
        );
      })}
    </svg>
  );
};
