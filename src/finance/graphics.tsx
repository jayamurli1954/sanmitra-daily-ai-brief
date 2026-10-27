import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { PALETTE } from "./charts";

/**
 * Explainer graphics for OfficeMitra Finance Insights episodes. Frames are
 * local to the scene; `at` values say when each part appears.
 */

export const FONT = "'Segoe UI', system-ui, -apple-system, Roboto, sans-serif";
const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

export const usePop = (at: number, stiffness = 120) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - at, fps, config: { damping: 14, stiffness } });
};

export const Panel: React.FC<{ title?: string; tag?: string; children: React.ReactNode; enter: number; width: number; padding?: string }> = ({
  title,
  tag,
  children,
  enter,
  width,
  padding = "26px 34px",
}) => (
  <div
    style={{
      width,
      background: PALETTE.card,
      borderRadius: 24,
      boxShadow: "0 28px 60px rgba(30,20,10,0.28)",
      padding,
      boxSizing: "border-box",
      fontFamily: FONT,
      color: PALETTE.ink,
      opacity: enter,
      transform: `translateY(${(1 - enter) * 40}px) scale(${0.95 + 0.05 * enter})`,
    }}
  >
    {(title || tag) && (
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 14 }}>
        {title && <div style={{ fontSize: 32, fontWeight: 800 }}>{title}</div>}
        {tag && <div style={{ fontSize: 17, fontWeight: 700, color: PALETTE.muted, letterSpacing: 2 }}>{tag}</div>}
      </div>
    )}
    {children}
  </div>
);

/** Items that appear one by one: bills, warning signs, actions. */
export const ItemList: React.FC<{ items: { icon: string; text: string; at: number; color?: string }[]; size?: number }> = ({ items, size = 32 }) => (
  <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
    {items.map((it) => (
      <Item key={it.text} {...it} size={size} />
    ))}
  </div>
);
const Item: React.FC<{ icon: string; text: string; at: number; color?: string; size: number }> = ({ icon, text, at, color = PALETTE.navy, size }) => {
  const e = usePop(at);
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 18,
        opacity: e,
        transform: `translateX(${(1 - e) * 60}px)`,
        background: "#fff",
        borderLeft: `8px solid ${color}`,
        borderRadius: 12,
        padding: "12px 18px",
        boxShadow: "0 6px 16px rgba(0,0,0,0.08)",
      }}
    >
      <div style={{ fontSize: size * 1.1 }}>{icon}</div>
      <div style={{ fontSize: size, fontWeight: 700 }}>{text}</div>
    </div>
  );
};

/** Invoice day 0 -> profit counted -> cash arrives 30/60/90 days later. */
export const InvoiceTimeline: React.FC<{ start: number }> = ({ start }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [start + 20, start + 220], [0, 1], clamp);
  const stops = [
    { x: 0.12, label: "Invoice sent", sub: "Day 0", color: PALETTE.navy, at: start + 10 },
    { x: 0.12, label: "Profit counted", sub: "in the P&L today", color: PALETTE.green, at: start + 60, dy: 1 },
    { x: 0.47, label: "Cash?", sub: "Day 30", color: PALETTE.orange, at: start + 230 },
    { x: 0.67, label: "Cash?", sub: "Day 60", color: PALETTE.orange, at: start + 290 },
    { x: 0.87, label: "Cash arrives", sub: "Day 90", color: PALETTE.red, at: start + 350 },
  ];
  const W = 740;
  return (
    <div style={{ position: "relative", width: W, height: 300, fontFamily: FONT }}>
      <div style={{ position: "absolute", left: 20, right: 20, top: 130, height: 10, borderRadius: 5, background: "#e7dccb" }} />
      <div style={{ position: "absolute", left: 20, top: 130, height: 10, borderRadius: 5, width: (W - 40) * progress, background: PALETTE.orange }} />
      {stops.map((s, i) => {
        const e = usePop(s.at);
        const x = 20 + (W - 40) * s.x;
        const above = !s.dy;
        return (
          <div key={i} style={{ position: "absolute", left: x, top: above ? 18 : 168, transform: `translateX(-50%) scale(${e})`, textAlign: "center", width: 200 }}>
            {!above && <div style={{ width: 4, height: 24, background: s.color, margin: "-30px auto 6px" }} />}
            <div style={{ fontSize: 28, fontWeight: 900, color: s.color }}>{s.label}</div>
            <div style={{ fontSize: 22, color: PALETTE.muted, fontWeight: 600 }}>{s.sub}</div>
            {above && <div style={{ width: 22, height: 22, borderRadius: 11, background: s.color, margin: "14px auto 0", border: "4px solid #fff" }} />}
          </div>
        );
      })}
    </div>
  );
};

/** Single line, e.g. debtor days creeping up. */
export const TrendLine: React.FC<{ labels: string[]; values: number[]; max: number; start: number; color: string; unit: string; width?: number; height?: number }> = ({
  labels,
  values,
  max,
  start,
  color,
  unit,
  width = 740,
  height = 360,
}) => {
  const frame = useCurrentFrame();
  const padL = 60;
  const padB = 46;
  const plotW = width - padL - 90;
  const plotH = height - padB - 30;
  const x = (i: number) => padL + (plotW / (values.length - 1)) * i;
  const y = (v: number) => 30 + plotH - (v / max) * plotH;
  const t = interpolate(frame, [start, start + 60], [0, 1], clamp);
  const shown = t * (values.length - 1);
  const pts: [number, number][] = [];
  for (let i = 0; i <= Math.floor(shown); i++) pts.push([x(i), y(values[i])]);
  const k = Math.floor(shown);
  if (k < values.length - 1) {
    const f = shown - k;
    pts.push([x(k) + (x(k + 1) - x(k)) * f, y(values[k] + (values[k + 1] - values[k]) * f)]);
  }
  const d = pts.map(([px, py], i) => `${i ? "L" : "M"}${px} ${py}`).join(" ");
  const last = pts[pts.length - 1];
  return (
    <svg width={width} height={height}>
      {[0, 0.5, 1].map((g) => (
        <g key={g}>
          <line x1={padL} x2={padL + plotW} y1={y(max * g)} y2={y(max * g)} stroke={PALETTE.grid} strokeWidth={2} />
          <text x={padL - 10} y={y(max * g) + 7} textAnchor="end" fontSize={20} fill={PALETTE.muted} fontFamily={FONT}>{Math.round(max * g)}</text>
        </g>
      ))}
      {labels.map((l, i) => (
        <text key={l} x={x(i)} y={height - 14} textAnchor="middle" fontSize={21} fill={PALETTE.muted} fontFamily={FONT}>{l}</text>
      ))}
      <path d={d} fill="none" stroke={color} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" />
      {pts.slice(0, Math.floor(shown) + 1).map(([px, py], i) => (
        <g key={i}>
          <circle cx={px} cy={py} r={9} fill="#fff" stroke={color} strokeWidth={5} />
          <text x={px} y={py - 18} textAnchor="middle" fontSize={22} fontWeight={800} fill={color} fontFamily={FONT}>{values[i]}{unit}</text>
        </g>
      ))}
      {last && <circle cx={last[0]} cy={last[1]} r={6} fill={color} />}
    </svg>
  );
};

/** Two series as paired bars, e.g. stock vs monthly sales. */
export const PairedBars: React.FC<{ labels: string[]; a: number[]; b: number[]; aLabel: string; bLabel: string; max: number; start: number; width?: number; height?: number }> = ({
  labels,
  a,
  b,
  aLabel,
  bLabel,
  max,
  start,
  width = 740,
  height = 380,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const padL = 56;
  const padB = 48;
  const plotH = height - padB - 50;
  const step = (width - padL - 10) / labels.length;
  const y = (v: number) => 50 + plotH - (v / max) * plotH;
  return (
    <svg width={width} height={height}>
      {[0, 0.5, 1].map((g) => (
        <g key={g}>
          <line x1={padL} x2={width - 10} y1={y(max * g)} y2={y(max * g)} stroke={PALETTE.grid} strokeWidth={2} />
          <text x={padL - 10} y={y(max * g) + 7} textAnchor="end" fontSize={20} fill={PALETTE.muted} fontFamily={FONT}>{Math.round(max * g)}</text>
        </g>
      ))}
      {labels.map((l, i) => {
        const g = spring({ frame: frame - (start + i * 10), fps, config: { damping: 14, stiffness: 90 } });
        const x0 = padL + step * i + step * 0.14;
        const bw = step * 0.34;
        return (
          <g key={l}>
            <rect x={x0} y={y(a[i] * g)} width={bw} height={(plotH * a[i] * g) / max} rx={6} fill={PALETTE.orange} />
            <rect x={x0 + bw + 4} y={y(b[i] * g)} width={bw} height={(plotH * b[i] * g) / max} rx={6} fill={PALETTE.navy} />
            <text x={x0 + bw} y={height - 16} textAnchor="middle" fontSize={21} fill={PALETTE.muted} fontFamily={FONT}>{l}</text>
          </g>
        );
      })}
      <g fontFamily={FONT} fontSize={22} fontWeight={700}>
        <rect x={padL} y={8} width={20} height={20} rx={4} fill={PALETTE.orange} />
        <text x={padL + 28} y={25} fill={PALETTE.ink}>{aLabel}</text>
        <rect x={padL + 230} y={8} width={20} height={20} rx={4} fill={PALETTE.navy} />
        <text x={padL + 258} y={25} fill={PALETTE.ink}>{bLabel}</text>
      </g>
    </svg>
  );
};

/** More sales -> more stock & credit -> cash out first. */
export const GrowthLoop: React.FC<{ start: number }> = ({ start }) => {
  const frame = useCurrentFrame();
  const nodes = [
    { label: "More sales", color: PALETTE.green, angle: -90 },
    { label: "More stock", color: PALETTE.orange, angle: 30 },
    { label: "More credit", color: PALETTE.orange, angle: 150 },
  ];
  const R = 165;
  const cx = 270;
  const cy = 225;
  const spin = interpolate(frame, [start, start + 400], [0, 360], clamp);
  const center = usePop(start + 120);
  return (
    <div style={{ position: "relative", width: 540, height: 460, fontFamily: FONT }}>
      <svg width={540} height={460} style={{ position: "absolute", inset: 0 }}>
        <circle cx={cx} cy={cy} r={R} fill="none" stroke="#e7dccb" strokeWidth={14} />
        <circle cx={cx} cy={cy} r={R} fill="none" stroke={PALETTE.orange} strokeWidth={14} strokeDasharray={`${(2 * Math.PI * R * Math.min(spin, 360)) / 360} 9999`} transform={`rotate(-90 ${cx} ${cy})`} strokeLinecap="round" />
      </svg>
      {nodes.map((n, i) => {
        const e = usePop(start + i * 25);
        const a = (n.angle * Math.PI) / 180;
        return (
          <div
            key={n.label}
            style={{
              position: "absolute",
              left: cx + R * Math.cos(a),
              top: cy + R * Math.sin(a),
              transform: `translate(-50%,-50%) scale(${e})`,
              background: n.color,
              color: "#fff",
              fontSize: 26,
              fontWeight: 800,
              padding: "10px 18px",
              borderRadius: 999,
              whiteSpace: "nowrap",
              boxShadow: "0 8px 18px rgba(0,0,0,0.15)",
            }}
          >
            {n.label}
          </div>
        );
      })}
      <div style={{ position: "absolute", left: cx, top: cy, transform: `translate(-50%,-50%) scale(${center})`, textAlign: "center", width: 170 }}>
        <div style={{ fontSize: 20, color: PALETTE.muted, fontWeight: 700 }}>all paid for</div>
        <div style={{ fontSize: 24, color: PALETTE.red, fontWeight: 900, lineHeight: 1.15 }}>before the cash comes back</div>
      </div>
    </div>
  );
};

/** Two big numbers side by side, e.g. bank today vs P&L per year. */
export const SplitCompare: React.FC<{ left: { label: string; value: string; color: string }; right: { label: string; value: string; color: string }; start: number }> = ({
  left,
  right,
  start,
}) => {
  const a = usePop(start);
  const b = usePop(start + 70);
  const col = (s: { label: string; value: string; color: string }, e: number) => (
    <div style={{ flex: 1, opacity: e, transform: `scale(${0.8 + 0.2 * e})`, textAlign: "center", background: "#fff", borderRadius: 18, padding: "22px 10px", borderTop: `10px solid ${s.color}` }}>
      <div style={{ fontSize: 26, fontWeight: 700, color: PALETTE.muted }}>{s.label}</div>
      <div style={{ fontSize: 76, fontWeight: 900, color: s.color, letterSpacing: -2 }}>{s.value}</div>
    </div>
  );
  return (
    <div style={{ display: "flex", gap: 22, fontFamily: FONT }}>
      {col(left, a)}
      {col(right, b)}
    </div>
  );
};

/** Eight-week cash forecast with the dip below zero highlighted. */
export const ForecastBars: React.FC<{ closing: number[]; start: number; width?: number; height?: number; highlight: number }> = ({ closing, start, width = 520, height = 300, highlight }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const min = Math.min(...closing, 0);
  const max = Math.max(...closing, 0);
  const span = max - min;
  const top = 34;
  const plotH = height - top - 40;
  const y = (v: number) => top + ((max - v) / span) * plotH;
  const step = width / closing.length;
  const pulse = 0.5 + 0.5 * Math.sin(frame / 5);
  return (
    <svg width={width} height={height}>
      <line x1={0} x2={width} y1={y(0)} y2={y(0)} stroke={PALETTE.ink} strokeWidth={2} />
      {closing.map((v, i) => {
        const g = spring({ frame: frame - (start + i * 8), fps, config: { damping: 14, stiffness: 100 } });
        const h = Math.abs(y(v) - y(0)) * g;
        const neg = v < 0;
        const x = step * i + step * 0.16;
        const w = step * 0.68;
        const isHi = i === highlight;
        return (
          <g key={i} fontFamily={FONT}>
            {isHi && <rect x={x - 6} y={y(0) - 4} width={w + 12} height={h + 10} rx={8} fill="none" stroke={PALETTE.red} strokeWidth={4} opacity={g * pulse} />}
            <rect x={x} y={neg ? y(0) : y(0) - h} width={w} height={h} rx={5} fill={neg ? PALETTE.red : PALETTE.green} />
            <text x={x + w / 2} y={neg ? y(0) + h + 22 : y(0) - h - 8} textAnchor="middle" fontSize={19} fontWeight={800} fill={neg ? PALETTE.red : PALETTE.green} opacity={g}>
              {v > 0 ? `+${v}` : v}
            </text>
            <text x={x + w / 2} y={height - 6} textAnchor="middle" fontSize={18} fill={PALETTE.muted}>W{i + 1}</text>
          </g>
        );
      })}
    </svg>
  );
};

/** A tiny receipts / payments / closing sheet. */
export const MiniSheet: React.FC<{ rows: [string, number, number, number][]; start: number }> = ({ rows, start }) => {
  const head = ["Week", "Receipts", "Payments", "Closing"];
  return (
    <div style={{ fontFamily: FONT, fontSize: 26, border: `2px solid ${PALETTE.grid}`, borderRadius: 12, overflow: "hidden" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.3fr 1.3fr 1.3fr", background: PALETTE.navy, color: "#fff", fontWeight: 800 }}>
        {head.map((h) => (
          <div key={h} style={{ padding: "10px 14px" }}>{h}</div>
        ))}
      </div>
      {rows.map((r, i) => (
        <SheetRow key={i} row={r} at={start + i * 14} />
      ))}
    </div>
  );
};
const SheetRow: React.FC<{ row: [string, number, number, number]; at: number }> = ({ row, at }) => {
  const e = usePop(at);
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1.3fr 1.3fr 1.3fr", opacity: e, borderTop: `1px solid ${PALETTE.grid}`, background: "#fff" }}>
      <div style={{ padding: "8px 14px", fontWeight: 700 }}>{row[0]}</div>
      <div style={{ padding: "8px 14px", color: PALETTE.green }}>₹{row[1]}L</div>
      <div style={{ padding: "8px 14px", color: PALETTE.red }}>₹{row[2]}L</div>
      <div style={{ padding: "8px 14px", fontWeight: 800, color: row[3] < 0 ? PALETTE.red : PALETTE.ink }}>₹{row[3]}L</div>
    </div>
  );
};

/** Big headline text for title and takeaway cards. */
export const BigLines: React.FC<{ lines: { text: string; color: string; at: number }[]; size?: number }> = ({ lines, size = 96 }) => (
  <div style={{ textAlign: "center", fontFamily: FONT }}>
    {lines.map((l) => (
      <BigLine key={l.text} {...l} size={size} />
    ))}
  </div>
);
const BigLine: React.FC<{ text: string; color: string; at: number; size: number }> = ({ text, color, at, size }) => {
  const e = usePop(at, 90);
  return <div style={{ color, fontSize: size, fontWeight: 900, lineHeight: 1.15, opacity: e, transform: `translateY(${(1 - e) * 30}px)` }}>{text}</div>;
};

/** A row of labelled boxes appearing one by one. */
export const Boxes: React.FC<{ items: { title: string; sub?: string; color: string; at: number }[]; width?: number }> = ({ items, width = 300 }) => (
  <div style={{ display: "flex", gap: 22, justifyContent: "center", fontFamily: FONT }}>
    {items.map((it) => (
      <Box key={it.title} {...it} width={width} />
    ))}
  </div>
);
const Box: React.FC<{ title: string; sub?: string; color: string; at: number; width: number }> = ({ title, sub, color, at, width }) => {
  const e = usePop(at);
  return (
    <div
      style={{
        width,
        opacity: e,
        transform: `translateY(${(1 - e) * 40}px)`,
        background: PALETTE.card,
        borderRadius: 20,
        borderTop: `10px solid ${color}`,
        padding: "22px 20px",
        boxShadow: "0 22px 44px rgba(0,0,0,0.3)",
        textAlign: "center",
        boxSizing: "border-box",
      }}
    >
      <div style={{ fontSize: 34, fontWeight: 900, color }}>{title}</div>
      {sub && <div style={{ fontSize: 24, fontWeight: 600, color: PALETTE.muted, marginTop: 8 }}>{sub}</div>}
    </div>
  );
};

/** Money spent on the left, money received on the right, the gap between them bracketed. */
export const GapBridge: React.FC<{ start: number; gapAt: number }> = ({ start, gapAt }) => {
  const a = usePop(start);
  const b = usePop(start + 25);
  const g = usePop(gapAt, 90);
  const end = (label: string, color: string, e: number, icon: string) => (
    <div style={{ width: 230, textAlign: "center", opacity: e, transform: `scale(${0.8 + 0.2 * e})` }}>
      <div style={{ fontSize: 64 }}>{icon}</div>
      <div style={{ fontSize: 30, fontWeight: 900, color }}>{label}</div>
    </div>
  );
  return (
    <div style={{ position: "relative", width: 740, height: 300, fontFamily: FONT }}>
      <div style={{ position: "absolute", left: 0, top: 40 }}>{end("Money spent", PALETTE.red, a, "💸")}</div>
      <div style={{ position: "absolute", right: 0, top: 40 }}>{end("Money received", PALETTE.green, b, "💰")}</div>
      <div style={{ position: "absolute", left: 235, right: 235, top: 92, height: 8, borderRadius: 4, background: "#e7dccb" }} />
      <div style={{ position: "absolute", left: 210, right: 210, top: 160, height: 60, borderLeft: `6px solid ${PALETTE.orange}`, borderRight: `6px solid ${PALETTE.orange}`, borderBottom: `6px solid ${PALETTE.orange}`, borderRadius: "0 0 18px 18px", opacity: g, transform: `scaleX(${g})` }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 232, textAlign: "center", opacity: g }}>
        <span style={{ fontSize: 34, fontWeight: 900, color: PALETTE.orange }}>the gap</span>
        <span style={{ fontSize: 26, fontWeight: 700, color: PALETTE.muted }}> · funded by working capital</span>
      </div>
    </div>
  );
};

/** One rupee's journey: day markers that appear on cue, and the stretch it is away highlighted. */
export const RupeeTimeline: React.FC<{ stops: { day: number; label: string; color: string; at: number }[]; awayFrom: number; awayTo: number; awayAt: number; lastDay: number }> = ({
  stops,
  awayFrom,
  awayTo,
  awayAt,
  lastDay,
}) => {
  const W = 740;
  // Keep the end labels inside the panel.
  const x = (d: number) => 110 + ((W - 220) * d) / lastDay;
  const band = usePop(awayAt, 90);
  return (
    <div style={{ position: "relative", width: W, height: 330, fontFamily: FONT }}>
      <div style={{ position: "absolute", left: 30, right: 30, top: 150, height: 10, borderRadius: 5, background: "#e7dccb" }} />
      <div style={{ position: "absolute", left: x(awayFrom), top: 138, height: 34, width: (x(awayTo) - x(awayFrom)) * band, borderRadius: 10, background: PALETTE.orange, opacity: 0.85 }} />
      <div style={{ position: "absolute", left: x(awayFrom), width: x(awayTo) - x(awayFrom), top: 96, textAlign: "center", opacity: band, fontSize: 30, fontWeight: 900, color: PALETTE.orange }}>
        {awayTo - awayFrom} days away
      </div>
      {stops.map((s, i) => {
        const e = usePop(s.at);
        // Alternate labels above and below the line so neighbouring days don't collide.
        const below = i % 2 === 1;
        return (
          <React.Fragment key={i}>
            <div style={{ position: "absolute", left: x(s.day), top: 144, width: 22, height: 22, borderRadius: 11, background: s.color, border: "4px solid #fff", transform: `translateX(-50%) scale(${e})` }} />
            <div style={{ position: "absolute", left: x(s.day), top: below ? 230 : 34, transform: `translateX(-50%) scale(${e})`, textAlign: "center", width: 230 }}>
              <div style={{ fontSize: 22, color: PALETTE.muted, fontWeight: 700 }}>Day {s.day}</div>
              <div style={{ fontSize: 24, fontWeight: 900, color: s.color, lineHeight: 1.15 }}>{s.label}</div>
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
};

/** The working capital cycle: cash -> inventory -> sales -> receivables -> cash, turning. */
export const CycleLoop: React.FC<{ start: number; centre?: string }> = ({ start, centre = "and again" }) => {
  const frame = useCurrentFrame();
  const nodes = [
    { label: "Cash", color: PALETTE.navy, angle: -90 },
    { label: "Inventory", color: PALETTE.orange, angle: 0 },
    { label: "Sales", color: PALETTE.green, angle: 90 },
    { label: "Receivables", color: PALETTE.red, angle: 180 },
  ];
  const R = 190;
  const cx = 300;
  const cy = 250;
  const sweep = interpolate(frame, [start, start + 120], [0, 360], clamp);
  const dot = ((frame - start) * 2.4 - 90) * (Math.PI / 180);
  const mid = usePop(start + 130);
  return (
    <div style={{ position: "relative", width: 600, height: 500, fontFamily: FONT }}>
      <svg width={600} height={500} style={{ position: "absolute", inset: 0 }}>
        <circle cx={cx} cy={cy} r={R} fill="none" stroke="rgba(255,255,255,0.18)" strokeWidth={14} />
        <circle cx={cx} cy={cy} r={R} fill="none" stroke={PALETTE.orange} strokeWidth={14} strokeDasharray={`${(2 * Math.PI * R * sweep) / 360} 9999`} transform={`rotate(-90 ${cx} ${cy})`} strokeLinecap="round" />
        {frame > start + 120 && <circle cx={cx + R * Math.cos(dot)} cy={cy + R * Math.sin(dot)} r={14} fill="#fff" stroke={PALETTE.orange} strokeWidth={5} />}
      </svg>
      {nodes.map((n, i) => {
        const e = usePop(start + i * 28);
        const a = (n.angle * Math.PI) / 180;
        return (
          <div
            key={n.label}
            style={{
              position: "absolute",
              left: cx + R * Math.cos(a),
              top: cy + R * Math.sin(a),
              transform: `translate(-50%,-50%) scale(${e})`,
              background: n.color,
              color: "#fff",
              fontSize: 30,
              fontWeight: 900,
              padding: "12px 22px",
              borderRadius: 999,
              whiteSpace: "nowrap",
              boxShadow: "0 10px 22px rgba(0,0,0,0.3)",
            }}
          >
            {n.label}
          </div>
        );
      })}
      <div style={{ position: "absolute", left: cx, top: cy, transform: `translate(-50%,-50%) scale(${mid})`, color: "#fff", fontSize: 30, fontWeight: 800, textAlign: "center", width: 220 }}>
        {centre}
      </div>
    </div>
  );
};
