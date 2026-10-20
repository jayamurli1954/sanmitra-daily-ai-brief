import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import timingsData from "./demoTimings.json";

/**
 * OfficeMitra product demo built on real screenshots of the shipped app
 * (github.com/jayamurli1954/SSDV) running on its sample company.
 * Narration and scene lengths come from generate_officemitra_demo_vo.py.
 */

type Timing = { id: string; audio: string; seconds: number; text: string };
const timings = timingsData as Timing[];

export const FPS = 30;
export const totalDemoFrames = () => timings.reduce((n, t) => n + Math.round(t.seconds * FPS), 0);

const NAVY = "#0f2a47";
const NAVY_DEEP = "#081a2e";
const ORANGE = "#e8862a";
const PAPER = "#f6f2ea";
const FONT = "'Segoe UI', system-ui, -apple-system, Roboto, sans-serif";

type Shot = {
  image: string;
  title: string;
  focus: [number, number]; // zoom target, as fractions of the image
  zoom: number;
};
type Callout = { text: string; at: number }; // at = fraction of the scene

type SceneSpec =
  | { kind: "hook" }
  | { kind: "intro" }
  | { kind: "screens"; shots: Shot[]; callouts: Callout[]; label: string }
  | { kind: "firms" }
  | { kind: "close" };

const SCENES: Record<string, SceneSpec> = {
  s01_hook: { kind: "hook" },
  s02_intro: { kind: "intro" },
  s03_connect: {
    kind: "screens",
    label: "Connect",
    shots: [{ image: "officemitra/connect-01-data-source.png", title: "OfficeMitra · Connect your accounts data", focus: [0.55, 0.35], zoom: 1.18 }],
    callouts: [
      { text: "Tally · Zoho Books · Busy · any ERP", at: 0.12 },
      { text: "Read-only: never changes a voucher", at: 0.48 },
      { text: "Runs on your own PC", at: 0.72 },
    ],
  },
  s04_ceo: {
    kind: "screens",
    label: "CEO pack",
    shots: [{ image: "officemitra/ceo-01-kpi-tiles.png", title: "OfficeMitra · CEO pack", focus: [0.58, 0.78], zoom: 1.32 }],
    callouts: [
      { text: "Growth · margin · cash · working capital", at: 0.2 },
      { text: "Plain notes on what needs attention", at: 0.6 },
    ],
  },
  s05_cfo: {
    kind: "screens",
    label: "CFO pack",
    shots: [
      { image: "officemitra/cfo-01-kpi-tiles.png", title: "OfficeMitra · CFO pack", focus: [0.62, 0.72], zoom: 1.25 },
      { image: "officemitra/cfo-02-cash-forecast.png", title: "OfficeMitra · CFO pack · Cash forecast", focus: [0.5, 0.62], zoom: 1.15 },
    ],
    callouts: [
      { text: "Debtor days · inventory · GST position", at: 0.12 },
      { text: "30 / 60 / 90-day cash forecast", at: 0.56 },
    ],
  },
  s06_aging: {
    kind: "screens",
    label: "CFO pack",
    shots: [
      { image: "officemitra/cfo-03-aging-donuts.png", title: "OfficeMitra · Receivables and payables aging", focus: [0.3, 0.62], zoom: 1.2 },
      { image: "officemitra/demo-cfo-overdue-customers.png", title: "OfficeMitra · Top overdue customers", focus: [0.4, 0.4], zoom: 1.15 },
    ],
    callouts: [
      { text: "How long customers have owed you", at: 0.15 },
      { text: "Who owes the most, for how long", at: 0.58 },
    ],
  },
  s07_board: {
    kind: "screens",
    label: "Board pack",
    shots: [
      { image: "officemitra/board-01-red-flags.png", title: "OfficeMitra · Board pack · Red flags", focus: [0.62, 0.8], zoom: 1.3 },
      { image: "officemitra/board-03-policy-scorecard.png", title: "OfficeMitra · Board pack · Policy scorecard", focus: [0.5, 0.75], zoom: 1.15 },
    ],
    callouts: [
      { text: "Red flags raised automatically", at: 0.15 },
      { text: "Board pack as PDF or Excel", at: 0.62 },
    ],
  },
  s08_why: {
    kind: "screens",
    label: "Why",
    shots: [{ image: "officemitra/ceo-06-why-ai.png", title: "OfficeMitra · Why (from posted books)", focus: [0.5, 0.62], zoom: 1.28 }],
    callouts: [
      { text: "Explains every movement from the books", at: 0.15 },
      { text: "Ask questions in plain English (local AI)", at: 0.58 },
    ],
  },
  s09_firms: { kind: "firms" },
  s10_close: { kind: "close" },
};

// ----------------------------------------------------------------- shared pieces

const Stage: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ background: `radial-gradient(ellipse at 30% 20%, ${NAVY} 0%, ${NAVY_DEEP} 70%)`, fontFamily: FONT }}>
    <AbsoluteFill
      style={{
        backgroundImage:
          "linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)",
        backgroundSize: "64px 64px",
      }}
    />
    {children}
  </AbsoluteFill>
);

const useEnter = (delay = 0) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - delay, fps, config: { damping: 18, stiffness: 110 } });
};

const Subtitle: React.FC<{ text: string; frames: number }> = ({ text, frames }) => {
  const frame = useCurrentFrame();
  // Spelled out for the voice; shown as written.
  const words = text.replace("sanmitratech dot in", "sanmitratech.in").split(" ");
  const chunks: string[] = [];
  for (let i = 0; i < words.length; i += 9) chunks.push(words.slice(i, i + 9).join(" "));
  const speaking = frames - 0.6 * FPS; // the scene ends with a short pause
  const total = words.length;
  let acc = 0;
  const idx = chunks.findIndex((c) => {
    acc += c.split(" ").length;
    return frame < (acc / total) * speaking;
  });
  const line = chunks[idx === -1 ? chunks.length - 1 : idx];
  return (
    <div style={{ position: "absolute", bottom: 46, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
      <div
        style={{
          background: "rgba(5, 15, 28, 0.82)",
          color: "#fff",
          fontSize: 34,
          fontWeight: 600,
          padding: "10px 28px",
          borderRadius: 10,
          maxWidth: 1500,
          textAlign: "center",
        }}
      >
        {line}
      </div>
    </div>
  );
};

const SampleTag: React.FC = () => (
  <div
    style={{
      position: "absolute",
      top: 34,
      right: 40,
      color: "rgba(255,255,255,0.7)",
      fontSize: 20,
      fontWeight: 600,
      letterSpacing: 1,
      border: "1px solid rgba(255,255,255,0.25)",
      borderRadius: 6,
      padding: "6px 14px",
    }}
  >
    SAMPLE COMPANY · SYNTHETIC DATA
  </div>
);

const Brand: React.FC = () => (
  <div style={{ position: "absolute", top: 28, left: 40, display: "flex", alignItems: "center", gap: 14 }}>
    <Img src={staticFile("officemitra/officemitra-logo.png")} style={{ width: 52, height: 52, borderRadius: 12 }} />
    <div style={{ color: "#fff", fontSize: 30, fontWeight: 800 }}>
      Office<span style={{ color: ORANGE }}>Mitra</span>
    </div>
  </div>
);

// ----------------------------------------------------------------- scene types

const AppWindow: React.FC<{ shot: Shot; frames: number; opacity: number }> = ({ shot, frames, opacity }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [0, frames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const eased = 1 - Math.pow(1 - t, 2);
  const scale = 1 + (shot.zoom - 1) * eased;
  const [fx, fy] = shot.focus;
  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        top: 116,
        width: 1300,
        height: 790,
        borderRadius: 18,
        overflow: "hidden",
        background: PAPER,
        boxShadow: "0 40px 90px rgba(0,0,0,0.55), 0 0 0 1px rgba(255,255,255,0.08)",
        opacity,
      }}
    >
      <div style={{ height: 44, background: "#e9e3d8", display: "flex", alignItems: "center", padding: "0 18px", gap: 9 }}>
        {["#ef5f57", "#f6bd2f", "#29c840"].map((c) => (
          <div key={c} style={{ width: 13, height: 13, borderRadius: "50%", background: c }} />
        ))}
        <div style={{ marginLeft: 18, color: "#5b5446", fontSize: 18, fontWeight: 600 }}>{shot.title}</div>
      </div>
      <div style={{ position: "absolute", top: 44, left: 0, right: 0, bottom: 0, overflow: "hidden" }}>
        <Img
          src={staticFile(shot.image)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "contain",
            transform: `scale(${scale})`,
            transformOrigin: `${fx * 100}% ${fy * 100}%`,
          }}
        />
      </div>
    </div>
  );
};

const CalloutPill: React.FC<{ text: string; delay: number; index: number }> = ({ text, delay, index }) => {
  const enter = useEnter(delay);
  return (
    <div
      style={{
        position: "absolute",
        left: 1400,
        width: 470,
        top: 250 + index * 150,
        transform: `translateX(${(1 - enter) * 80}px)`,
        opacity: enter,
        background: ORANGE,
        color: "#fff",
        fontSize: 32,
        fontWeight: 700,
        lineHeight: 1.25,
        padding: "18px 26px",
        borderRadius: 14,
        boxShadow: "0 16px 40px rgba(0,0,0,0.4)",
        boxSizing: "border-box",
      }}
    >
      {text}
    </div>
  );
};

const ScreensScene: React.FC<{ spec: Extract<SceneSpec, { kind: "screens" }>; frames: number }> = ({ spec, frames }) => {
  const frame = useCurrentFrame();
  const per = frames / spec.shots.length;
  const fade = 14;
  return (
    <Stage>
      <Brand />
      <SampleTag />
      {spec.shots.map((shot, i) => {
        const from = Math.round(i * per);
        const to = Math.round((i + 1) * per);
        const opacity = Math.min(
          i === 0 ? 1 : interpolate(frame, [from, from + fade], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          i === spec.shots.length - 1 ? 1 : interpolate(frame, [to - fade, to], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        );
        if (frame < from - fade || frame > to + fade) return null;
        return (
          <Sequence key={shot.image} from={from} durationInFrames={to - from + fade} layout="none">
            <AppWindow shot={shot} frames={to - from} opacity={opacity} />
          </Sequence>
        );
      })}
      {spec.callouts.map((c, i) => (
        <CalloutPill key={c.text} text={c.text} delay={Math.round(c.at * frames)} index={i} />
      ))}
    </Stage>
  );
};

const HookScene: React.FC = () => {
  const a = useEnter(8);
  const b = useEnter(95);
  const c = useEnter(200);
  const card = (label: string, value: string, color: string, enter: number) => (
    <div
      style={{
        opacity: enter,
        transform: `translateY(${(1 - enter) * 40}px)`,
        background: "rgba(255,255,255,0.06)",
        border: `2px solid ${color}`,
        borderRadius: 20,
        padding: "34px 54px",
        minWidth: 520,
      }}
    >
      <div style={{ color: "rgba(255,255,255,0.75)", fontSize: 30, fontWeight: 600, letterSpacing: 2 }}>{label}</div>
      <div style={{ color, fontSize: 92, fontWeight: 900, marginTop: 6 }}>{value}</div>
    </div>
  );
  return (
    <Stage>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", gap: 50 }}>
        <div style={{ display: "flex", gap: 60 }}>
          {card("YOUR BOOKS SAY", "PROFIT", "#4ade80", a)}
          {card("YOUR BANK SAYS", "OVERDRAWN", "#f87171", b)}
        </div>
        <div style={{ opacity: c, color: "#fff", fontSize: 44, fontWeight: 700 }}>
          …and the monthly MIS arrives <span style={{ color: ORANGE }}>too late</span>.
        </div>
      </AbsoluteFill>
    </Stage>
  );
};

const IntroScene: React.FC = () => {
  const logo = useEnter(4);
  const words = useEnter(18);
  const by = useEnter(40);
  return (
    <Stage>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", gap: 30 }}>
        <Img
          src={staticFile("officemitra/officemitra-logo.png")}
          style={{ width: 230, height: 230, borderRadius: 48, transform: `scale(${0.6 + 0.4 * logo})`, opacity: logo }}
        />
        <div style={{ opacity: words, color: "#fff", fontSize: 96, fontWeight: 900 }}>
          Office<span style={{ color: ORANGE }}>Mitra</span>
        </div>
        <div style={{ opacity: words, color: "rgba(255,255,255,0.85)", fontSize: 40, fontWeight: 600 }}>Your AI CFO Dashboard</div>
        <div style={{ opacity: by, color: "rgba(255,255,255,0.6)", fontSize: 28, marginTop: 10 }}>by SanMitra Tech Solutions</div>
      </AbsoluteFill>
    </Stage>
  );
};

const FirmsScene: React.FC = () => {
  const head = useEnter(4);
  const cols = ["Revenue", "AR 90+", "Cash", "Working capital", "Quality score", "Reviewed"];
  return (
    <Stage>
      <Brand />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", gap: 40 }}>
        <div style={{ opacity: head, color: "#fff", fontSize: 76, fontWeight: 900 }}>All client books</div>
        <div style={{ opacity: head, color: "rgba(255,255,255,0.8)", fontSize: 36, fontWeight: 600 }}>
          One screen for your practice · one row per client
        </div>
        <div style={{ display: "flex", gap: 22, flexWrap: "wrap", justifyContent: "center", maxWidth: 1500 }}>
          {cols.map((c, i) => {
            const e = useEnter(30 + i * 10);
            return (
              <div
                key={c}
                style={{
                  opacity: e,
                  transform: `translateY(${(1 - e) * 30}px)`,
                  background: "rgba(255,255,255,0.08)",
                  border: "1px solid rgba(255,255,255,0.2)",
                  color: "#fff",
                  fontSize: 34,
                  fontWeight: 700,
                  padding: "18px 32px",
                  borderRadius: 14,
                }}
              >
                {c}
              </div>
            );
          })}
        </div>
        <div style={{ opacity: useEnter(110), color: ORANGE, fontSize: 34, fontWeight: 700 }}>CA Pack · 5, 20 or 50 companies</div>
      </AbsoluteFill>
    </Stage>
  );
};

const CloseScene: React.FC = () => {
  const a = useEnter(4);
  const b = useEnter(40);
  const c = useEnter(80);
  return (
    <Stage>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", gap: 26 }}>
        <Img src={staticFile("officemitra/officemitra-logo.png")} style={{ width: 170, height: 170, borderRadius: 36, opacity: a }} />
        <div style={{ opacity: a, color: "#fff", fontSize: 84, fontWeight: 900 }}>
          Office<span style={{ color: ORANGE }}>Mitra</span>
        </div>
        <div style={{ opacity: b, color: "#fff", fontSize: 44, fontWeight: 700 }}>
          Clear numbers · Early warnings · Better decisions
        </div>
        <div style={{ opacity: c, color: ORANGE, fontSize: 46, fontWeight: 800, marginTop: 14 }}>sanmitratech.in</div>
        <div style={{ opacity: c, color: "rgba(255,255,255,0.75)", fontSize: 30 }}>contact@sanmitratech.in</div>
        <div style={{ opacity: c, display: "flex", alignItems: "center", gap: 14, marginTop: 20 }}>
          <Img src={staticFile("officemitra/sanmitra-logo.png")} style={{ width: 70, height: 70, borderRadius: 12 }} />
          <div style={{ color: "rgba(255,255,255,0.7)", fontSize: 26 }}>A SanMitra Tech Solutions product</div>
        </div>
        <div style={{ position: "absolute", bottom: 130, color: "rgba(255,255,255,0.5)", fontSize: 22 }}>
          Screens show a sample company with synthetic data.
        </div>
      </AbsoluteFill>
    </Stage>
  );
};

// ----------------------------------------------------------------- composition

export const OfficeMitraDemo: React.FC = () => {
  let from = 0;
  return (
    <AbsoluteFill style={{ background: NAVY_DEEP }}>
      <Audio src={staticFile("audio/officemitra_theme.wav")} volume={0.07} loop />
      {timings.map((t) => {
        const frames = Math.round(t.seconds * FPS);
        const spec = SCENES[t.id];
        const start = from;
        from += frames;
        let body: React.ReactNode = null;
        if (spec.kind === "hook") body = <HookScene />;
        else if (spec.kind === "intro") body = <IntroScene />;
        else if (spec.kind === "screens") body = <ScreensScene spec={spec} frames={frames} />;
        else if (spec.kind === "firms") body = <FirmsScene />;
        else body = <CloseScene />;
        return (
          <Sequence key={t.id} from={start} durationInFrames={frames}>
            <Audio src={staticFile(t.audio)} />
            {body}
            <Subtitle text={t.text} frames={frames} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
