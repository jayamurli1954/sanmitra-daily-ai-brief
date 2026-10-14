import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import shortData from "./data/short_episode.json";

// One-story vertical short (1080x1920) for Instagram Reels / YouTube Shorts.
// Content comes from src/aibrief/data/short_episode.json, so a new short is a
// new data file and voice track, not a new component.

interface ShortImage {
  src: string;
  label: string;
}
interface ShortCue {
  text: string;
  start: number;
  end: number;
}
interface ShortEpisode {
  dateLabel: string;
  kicker: string;
  headline: string;
  subhead: string;
  source: string;
  audioFile: string;
  voiceFrames: number;
  endCardFrames: number;
  images: ShortImage[];
  cues: ShortCue[];
  ctaTitle: string;
  ctaLine: string;
  ctaSub: string;
}

const data = shortData as unknown as ShortEpisode;
export const BREAKING_SHORT_FRAMES = data.voiceFrames + data.endCardFrames;

// Instagram draws its own UI over the top ~220px, the bottom ~400px and a
// column of buttons on the right; keep text inside this box.
const SAFE = { top: 230, bottom: 1500, left: 64, right: 150 };
const FONT = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif";

const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const per = Math.ceil(data.voiceFrames / data.images.length);
  const fade = 18;
  return (
    <AbsoluteFill style={{ backgroundColor: "#05070d" }}>
      {data.images.map((img, i) => {
        const start = i * per;
        const end = i === data.images.length - 1 ? BREAKING_SHORT_FRAMES : start + per + fade;
        if (frame < start - fade || frame > end) return null;
        const opacity = interpolate(frame, [start - fade, start, end - fade, end], [0, 1, 1, i === data.images.length - 1 ? 1 : 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const zoom = interpolate(frame, [start, end], [1.08, 1.2]);
        return (
          <AbsoluteFill key={img.src} style={{ opacity }}>
            <Img
              src={staticFile(img.src)}
              style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zoom})` }}
            />
          </AbsoluteFill>
        );
      })}
      {/* Darken top and bottom so white text stays readable on any photo. */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(3,6,14,0.92) 0%, rgba(3,6,14,0.55) 30%, rgba(3,6,14,0.15) 50%, rgba(3,6,14,0.6) 68%, rgba(3,6,14,0.95) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

const Header: React.FC = () => {
  const frame = useCurrentFrame();
  const pulse = 0.65 + 0.35 * Math.abs(Math.sin(frame / 9));
  const per = Math.ceil(data.voiceFrames / data.images.length);
  const label = data.images[Math.min(Math.floor(frame / per), data.images.length - 1)].label;
  const enter = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", top: SAFE.top, left: SAFE.left, right: SAFE.right, opacity: enter }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 26 }}>
        <div
          style={{
            backgroundColor: "#dc2626",
            color: "#fff",
            fontFamily: FONT,
            fontWeight: 900,
            fontSize: 38,
            letterSpacing: 4,
            padding: "8px 22px",
            borderRadius: 8,
            boxShadow: `0 0 ${24 * pulse}px rgba(239,68,68,${pulse})`,
          }}
        >
          ● {data.kicker}
        </div>
        <div style={{ color: "#e2e8f0", fontFamily: FONT, fontWeight: 800, fontSize: 26, letterSpacing: 2, lineHeight: 1.2 }}>
          SANMITRA AI NEWS WIRE
          <div style={{ color: "#fbbf24", fontSize: 22 }}>{data.dateLabel}</div>
        </div>
      </div>
      <div
        style={{
          color: "#ffffff",
          fontFamily: FONT,
          fontWeight: 900,
          // Long headlines step down so they stay within four lines.
          fontSize: data.headline.length > 90 ? 58 : data.headline.length > 60 ? 66 : 76,
          lineHeight: 1.08,
          letterSpacing: -1,
          textShadow: "0 4px 18px rgba(0,0,0,0.9)",
        }}
      >
        {data.headline}
      </div>
      <div
        style={{
          marginTop: 20,
          color: "#f1f5f9",
          fontFamily: FONT,
          fontWeight: 600,
          fontSize: 34,
          lineHeight: 1.3,
          textShadow: "0 2px 10px rgba(0,0,0,0.9)",
        }}
      >
        {data.subhead}
      </div>
      <div
        style={{
          display: "inline-block",
          marginTop: 24,
          backgroundColor: "rgba(3,6,14,0.75)",
          border: "1px solid rgba(125,211,252,0.6)",
          color: "#7dd3fc",
          fontFamily: FONT,
          fontWeight: 800,
          fontSize: 22,
          letterSpacing: 1.5,
          padding: "6px 14px",
          borderRadius: 6,
        }}
      >
        {label}
      </div>
    </div>
  );
};

const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = data.cues.find((c) => frame >= c.start && frame < c.end + 6);
  if (!cue || frame >= data.voiceFrames) return null;
  return (
    <div
      style={{
        position: "absolute",
        top: 1170,
        left: SAFE.left,
        right: SAFE.right,
        display: "flex",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(0,0,0,0.85)",
          border: "3px solid #facc15",
          borderRadius: 14,
          padding: "14px 26px",
          color: "#ffffff",
          fontFamily: FONT,
          fontWeight: 900,
          fontSize: 60,
          lineHeight: 1.15,
          textAlign: "center",
          textShadow: "0 2px 6px #000",
        }}
      >
        {cue.text}
      </div>
    </div>
  );
};

const Footer: React.FC = () => (
  <div
    style={{
      position: "absolute",
      top: SAFE.bottom - 60,
      left: SAFE.left,
      right: SAFE.right,
      color: "#cbd5e1",
      fontFamily: FONT,
      fontWeight: 700,
      fontSize: 26,
    }}
  >
    {data.source}
  </div>
);

const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame - data.voiceFrames;
  if (t < 0) return null;
  const appear = interpolate(t, [0, 12], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill
      style={{
        backgroundColor: `rgba(3,6,14,${0.9 * appear})`,
        alignItems: "center",
        justifyContent: "center",
        opacity: appear,
        paddingBottom: 180,
      }}
    >
      <div
        style={{
          width: 200,
          height: 140,
          borderRadius: 36,
          backgroundColor: "#ff0000",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginBottom: 44,
          transform: `scale(${interpolate(t, [0, 10, 18], [0.6, 1.08, 1], { extrapolateRight: "clamp" })})`,
        }}
      >
        <div
          style={{
            width: 0,
            height: 0,
            borderTop: "34px solid transparent",
            borderBottom: "34px solid transparent",
            borderLeft: "58px solid #ffffff",
            marginLeft: 12,
          }}
        />
      </div>
      <div style={{ color: "#ffffff", fontFamily: FONT, fontWeight: 900, fontSize: 70, textAlign: "center" }}>{data.ctaTitle}</div>
      <div style={{ color: "#fbbf24", fontFamily: FONT, fontWeight: 900, fontSize: 52, marginTop: 18 }}>{data.ctaLine}</div>
      <div style={{ color: "#e2e8f0", fontFamily: FONT, fontWeight: 700, fontSize: 38, marginTop: 22 }}>{data.ctaSub}</div>
    </AbsoluteFill>
  );
};

const Progress: React.FC = () => {
  const frame = useCurrentFrame();
  const width = interpolate(frame, [0, data.voiceFrames], [0, 100], { extrapolateRight: "clamp" });
  return <div style={{ position: "absolute", top: 0, left: 0, height: 10, width: `${width}%`, backgroundColor: "#dc2626" }} />;
};

export const BreakingShort: React.FC = () => (
  <AbsoluteFill>
    <Background />
    <Header />
    <Captions />
    <Footer />
    <EndCard />
    <Progress />
    <Audio src={staticFile(data.audioFile)} />
    <Audio src={staticFile("audio/aibrief_theme.wav")} volume={0.06} />
  </AbsoluteFill>
);
