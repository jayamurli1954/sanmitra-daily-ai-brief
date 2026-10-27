import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { PALETTE } from "./charts";
import { FONT, usePop } from "./graphics";

/**
 * Shared building blocks for OfficeMitra Finance Insights episodes: the picture
 * moves, chips, speaker tag, subtitles, OfficeMitra moment, end card and the
 * scene sequencer. Each episode supplies its timings.json and a scene -> art map.
 */

export type Line = { speaker: string; name: string; text: string; audio: string; start: number; seconds: number };
export type Scene = { id: string; seconds: number; lines: Line[] };
export const EP_FPS = 30;
export const frames = (s: number) => Math.round(s * EP_FPS);
export const episodeFrames = (scenes: Scene[]) => scenes.reduce((n, s) => n + frames(s.seconds), 0);

/**
 * Scene-local frame where a narration line starts, plus `frac` of the way through it,
 * so graphics land on the words without hand-timed frame numbers.
 */
export const cueFor = (scenes: Scene[]) => (id: string, line: number, frac = 0) => {
  const l = scenes.find((s) => s.id === id)!.lines[line];
  return frames(l.start + l.seconds * frac);
};

const ART = "finance/ramesh";
const FADE = 14;
const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const ROLE: Record<string, string> = { Lata: "Accountant", Vikram: "Sales head", "Mr. Mehta": "Biggest customer", Kapoor: "Supplier" };

// ------------------------------------------------------------------ pictures

export type Shot =
  | { kind: "still"; src: string; zoom?: [number, number]; origin?: string; panX?: [number, number]; gray?: number }
  | { kind: "clip"; src: string; seconds: number; still: string }
  | { kind: "stillThenClip"; still: string; clip: string; clipSeconds: number }
  | { kind: "split"; left: string; right: string }
  | { kind: "stage" };

export const Picture: React.FC<{ shot: Shot; len: number; dim?: number }> = ({ shot, len, dim = 0 }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [0, len], [0, 1], clamp);
  const e = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  let body: React.ReactNode = null;
  if (shot.kind === "still") {
    const [z0, z1] = shot.zoom || [1.0, 1.08];
    const [p0, p1] = shot.panX || [0, 0];
    body = (
      <Img
        src={staticFile(`${ART}/${shot.src}`)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `translateX(${p0 + (p1 - p0) * e}px) scale(${z0 + (z1 - z0) * e})`,
          transformOrigin: shot.origin || "30% 40%",
          filter: shot.gray ? `grayscale(${shot.gray}) sepia(${shot.gray * 0.25})` : undefined,
        }}
      />
    );
  } else if (shot.kind === "clip") {
    // Fit the clip to the scene: play it a little slower; if it would need to go below 75% speed,
    // play at 80% and crossfade into the matching still with a slow push-in rather than freezing.
    const fit = shot.seconds / (len / 30);
    // Down to 75% speed the clip simply fills the scene; beyond that, 80% speed plus the still.
    const rate = fit >= 0.75 ? Math.min(1, fit) : 0.8;
    const clipLen = Math.floor((shot.seconds / rate) * 30) - 2;
    // Only a clip that ends before the scene hands over to the still.
    const handover = clipLen < len;
    const hand = handover ? interpolate(frame, [clipLen - 14, clipLen], [0, 1], clamp) : 0;
    const after = handover ? interpolate(frame, [clipLen - 14, len], [0, 1], clamp) : 0;
    body = (
      <>
        {(frame < clipLen || !handover) && (
          <OffthreadVideo src={staticFile(`${ART}/${shot.src}`)} muted playbackRate={rate} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        )}
        {handover && hand > 0 && (
          <AbsoluteFill style={{ opacity: hand }}>
            <Img src={staticFile(`${ART}/${shot.still}`)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1.02 + 0.06 * after})`, transformOrigin: "40% 40%" }} />
          </AbsoluteFill>
        )}
      </>
    );
  } else if (shot.kind === "stillThenClip") {
    // The clip plays at the end of the scene, so its action lands on the closing line.
    const clipAt = Math.max(0, len - Math.round(shot.clipSeconds * 30));
    const fade = interpolate(frame, [clipAt, clipAt + 12], [0, 1], clamp);
    body = (
      <>
        <Img src={staticFile(`${ART}/${shot.still}`)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1 + 0.06 * e})`, transformOrigin: "40% 40%" }} />
        {frame >= clipAt - 1 && (
          <AbsoluteFill style={{ opacity: fade }}>
            <Sequence from={clipAt} layout="none">
              <OffthreadVideo src={staticFile(`${ART}/${shot.clip}`)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            </Sequence>
          </AbsoluteFill>
        )}
      </>
    );
  } else if (shot.kind === "split") {
    const half = (src: string, side: "left" | "right") => (
      <div style={{ position: "absolute", top: 0, bottom: 0, [side]: 0, width: "50%", overflow: "hidden", borderLeft: side === "right" ? "6px solid #fff" : undefined }}>
        <Img src={staticFile(`${ART}/${src}`)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: side === "left" ? "12% 50%" : "30% 50%", transform: `scale(${1 + 0.06 * e})` }} />
      </div>
    );
    body = (
      <>
        {half(shot.left, "left")}
        {half(shot.right, "right")}
      </>
    );
  } else {
    body = <AbsoluteFill style={{ background: `radial-gradient(ellipse at 30% 20%, #18365a 0%, #0b1b2e 70%)` }} />;
  }
  return (
    <AbsoluteFill>
      {body}
      {dim > 0 && <AbsoluteFill style={{ background: `rgba(11,27,46,${dim})` }} />}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ overlays

export const At: React.FC<{ left: number; top: number; children: React.ReactNode }> = ({ left, top, children }) => (
  <div style={{ position: "absolute", left, top }}>{children}</div>
);

export const RIGHT = { left: 1060, top: 110 };

export const Chip: React.FC<{ at: number; children: React.ReactNode; color: string; left: number; top: number }> = ({ at, children, color, left, top }) => {
  const e = usePop(at);
  return (
    <div
      style={{
        position: "absolute",
        left,
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
        boxShadow: "0 12px 26px rgba(0,0,0,0.25)",
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </div>
  );
};

export const OfficeMitraMoment: React.FC<{ screen: string; caption: string; points: string[] }> = ({ screen, caption, points }) => {
  const e = usePop(10);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", fontFamily: FONT }}>
      <div style={{ display: "flex", gap: 50, alignItems: "center", opacity: e }}>
        <div
          style={{
            width: 1150,
            height: 690,
            borderRadius: 18,
            overflow: "hidden",
            background: "#f6f2ea",
            boxShadow: "0 40px 90px rgba(0,0,0,0.55)",
            transform: `translateY(${(1 - e) * 40}px)`,
          }}
        >
          <div style={{ height: 40, background: "#e9e3d8", display: "flex", alignItems: "center", gap: 8, padding: "0 16px" }}>
            {["#ef5f57", "#f6bd2f", "#29c840"].map((c) => (
              <div key={c} style={{ width: 12, height: 12, borderRadius: 6, background: c }} />
            ))}
            <div style={{ marginLeft: 14, color: "#5b5446", fontSize: 17, fontWeight: 600 }}>{caption}</div>
          </div>
          <Img src={staticFile(`officemitra/${screen}`)} style={{ width: "100%", height: 650, objectFit: "contain" }} />
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 18, width: 520 }}>
          <Img src={staticFile("officemitra/officemitra-logo.png")} style={{ width: 120, height: 120, borderRadius: 26 }} />
          <div style={{ color: "#fff", fontSize: 56, fontWeight: 900 }}>
            Office<span style={{ color: PALETTE.orange }}>Mitra</span>
          </div>
          {points.map((t, i) => {
            const p = usePop(60 + i * 60);
            return (
              <div key={t} style={{ opacity: p, transform: `translateX(${(1 - p) * 40}px)`, background: PALETTE.orange, color: "#fff", fontSize: 28, fontWeight: 800, padding: "12px 22px", borderRadius: 12 }}>
                {t}
              </div>
            );
          })}
        </div>
      </div>
      <div style={{ position: "absolute", bottom: 130, color: "rgba(255,255,255,0.5)", fontSize: 20 }}>Screen shows a sample company with synthetic data.</div>
    </AbsoluteFill>
  );
};

export const EndCard: React.FC<{ question: string }> = ({ question }) => {
  const a = usePop(5);
  const b = usePop(60);
  const c = usePop(100);
  const contact = (icon: string, text: string) => (
    <div style={{ display: "flex", alignItems: "center", gap: 12, background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.22)", borderRadius: 14, padding: "14px 24px" }}>
      <span style={{ fontSize: 30 }}>{icon}</span>
      <span style={{ color: "#fff", fontSize: 30, fontWeight: 800 }}>{text}</span>
    </div>
  );
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: 120, fontFamily: FONT, textAlign: "center" }}>
      <div style={{ opacity: a }}>
        <div style={{ color: "#fff", fontSize: 72, fontWeight: 900 }}>
          OfficeMitra <span style={{ color: PALETTE.orange }}>Finance Insights</span>
        </div>
        <div style={{ color: "rgba(255,255,255,0.85)", fontSize: 36, fontWeight: 700, marginTop: 16 }}>Real stories on cash, controls and decisions</div>
      </div>
      <div style={{ opacity: b, marginTop: 50, display: "flex", gap: 24 }}>
        <div style={{ background: PALETTE.red, color: "#fff", fontSize: 34, fontWeight: 900, padding: "16px 40px", borderRadius: 14 }}>▶ Subscribe</div>
        <div style={{ background: "rgba(255,255,255,0.12)", color: "#fff", fontSize: 30, fontWeight: 700, padding: "16px 30px", borderRadius: 14 }}>
          {question}
        </div>
      </div>
      <div style={{ opacity: c, transform: `translateY(${(1 - c) * 30}px)`, marginTop: 56, display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <Img src={staticFile("officemitra/sanmitra-logo.png")} style={{ width: 64, height: 64, borderRadius: 12 }} />
          <div style={{ color: "rgba(255,255,255,0.85)", fontSize: 28, fontWeight: 700 }}>SanMitra Tech Solutions</div>
        </div>
        <div style={{ display: "flex", gap: 18 }}>
          {contact("🌐", "www.sanmitratech.in")}
          {contact("✉️", "contact@sanmitratech.in")}
          {contact("📱", "Call / WhatsApp +91 79049 42915")}
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 130,
          width: 1560,
          color: "#ffffff",
          fontSize: 28,
          fontWeight: 600,
          lineHeight: 1.45,
          background: "rgba(0,0,0,0.55)",
          border: "1px solid rgba(255,255,255,0.25)",
          borderRadius: 14,
          padding: "18px 30px",
        }}
      >
        <span style={{ color: PALETTE.orange, fontWeight: 900, letterSpacing: 2 }}>DISCLAIMER </span>
        For education only; not accounting, tax, legal or investment advice. Characters, businesses and month-by-month figures are illustrative. Narration uses AI voices; pictures are AI-generated.
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ speaker tag + subtitles

const NameTag: React.FC<{ name: string }> = ({ name }) => {
  const e = usePop(0, 160);
  return (
    <div style={{ position: "absolute", left: 60, bottom: 130, display: "flex", fontFamily: FONT, transform: `translateX(${(1 - e) * -40}px)`, opacity: e }}>
      <div style={{ width: 8, background: PALETTE.orange }} />
      <div style={{ background: "rgba(11,27,46,0.9)", padding: "8px 18px 10px" }}>
        <div style={{ color: "#fff", fontSize: 30, fontWeight: 900 }}>{name}</div>
        <div style={{ color: "#f5c58e", fontSize: 18, fontWeight: 700, letterSpacing: 1.5, textTransform: "uppercase" }}>{ROLE[name]}</div>
      </div>
    </div>
  );
};

const Subtitle: React.FC<{ text: string; len: number; quote: boolean }> = ({ text, len, quote }) => {
  const frame = useCurrentFrame();
  const words = text.split(" ");
  const chunks: string[] = [];
  for (let i = 0; i < words.length; i += 9) chunks.push(words.slice(i, i + 9).join(" "));
  let acc = 0;
  const idx = chunks.findIndex((c) => {
    acc += c.split(" ").length;
    return frame < (acc / words.length) * len;
  });
  const line = chunks[idx === -1 ? chunks.length - 1 : idx];
  return (
    <div style={{ position: "absolute", bottom: 40, left: 0, right: 0, display: "flex", justifyContent: "center", fontFamily: FONT }}>
      <div style={{ background: "rgba(14,20,30,0.84)", color: quote ? "#ffe2b8" : "#fff", fontSize: 34, fontWeight: 600, padding: "10px 26px", borderRadius: 10, fontStyle: quote ? "italic" : "normal" }}>
        {line}
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ composition

export type SceneArt = Record<string, { shot: Shot; dim?: number; graphic?: (len: number) => React.ReactNode }>;

const SceneView: React.FC<{ scene: Scene; len: number; art: SceneArt }> = ({ scene, len, art: arts }) => {
  const frame = useCurrentFrame();
  const art = arts[scene.id];
  const opacity = interpolate(frame, [0, FADE], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ opacity }}>
      <Picture shot={art.shot} len={len} dim={art.dim} />
      {art.graphic?.(len)}
      {scene.lines.map((l, i) => {
        const from = frames(l.start);
        const dur = frames(l.seconds) + 8;
        return (
          <Sequence key={i} from={from} durationInFrames={dur} layout="none">
            <Audio src={staticFile(l.audio)} />
            {l.name && <NameTag name={l.name} />}
            <Subtitle text={l.text} len={frames(l.seconds)} quote={!!l.name} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

export const Episode: React.FC<{ scenes: Scene[]; art: SceneArt }> = ({ scenes, art }) => {
  let from = 0;
  return (
    <AbsoluteFill style={{ background: "#0b1b2e" }}>
      <Audio src={staticFile("audio/officemitra_theme.wav")} volume={0.045} loop />
      {scenes.map((s) => {
        const len = frames(s.seconds);
        const start = from;
        from += len;
        return (
          <Sequence key={s.id} from={start} durationInFrames={len + FADE}>
            <SceneView scene={s} len={len} art={art} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
