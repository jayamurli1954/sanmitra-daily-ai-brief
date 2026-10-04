import React from "react";
import {
  Audio,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";

const SPEECH_SECONDS = 62.38;
const SPEECH_FRAMES = Math.round(SPEECH_SECONDS * 30);
export const UKRAINE_WIDE_FRAMES = SPEECH_FRAMES + 18;
const CUT_FRAMES = 160;
const AUDIO_FILE = "audio/aibrief/short_jenny_ukraine_2026-10-03.mp3";
const HEADLINE = "Ukraine tests faster drone interceptors";
const CUTS = [
  "aibrief/assets/editorial/2026-10-03/s1_cut1.jpg",
  "aibrief/assets/editorial/2026-10-03/s1_cut2.jpg",
  "aibrief/assets/editorial/2026-10-03/s1_cut3.jpg",
];

const CAPTION_LINES = [
  "From the SanMitra newsroom, this is today's lead.",
  "Ukraine is using electronic warfare and artificial intelligence to steer incoming Russian drones into narrower corridors, while defense makers train AI to help guide a new class of interceptors.",
  "President Zelensky told the Financial Times that Ukraine is testing five high-speed interceptor models, and that one of them could reach production of about 400 units by the end of October.",
  "The Associated Press reported from Kyiv that the interceptors now in service are still too slow for Russia's newest jet-powered drones.",
  "Manufacturers told the Associated Press that fielding enough of the new interceptors, and training the crews, could take months.",
  "Zelensky said the constraint is engines. Ukraine still imports most of them.",
  "The reporting is from the Financial Times and the Associated Press.",
  "The full desk is on the channel.",
];

const captionCues = (() => {
  const closerFrames = 90;
  const bodyFrames = UKRAINE_WIDE_FRAMES - closerFrames;
  const bodyLines = CAPTION_LINES.slice(0, -1);
  const bodyChars = bodyLines.reduce((sum, line) => sum + line.length, 0);
  let cursor = 0;
  const cues = bodyLines.map((text) => {
    const span = Math.max(1, Math.round((text.length / bodyChars) * bodyFrames));
    const cue = { text, start: cursor, end: cursor + span };
    cursor += span;
    return cue;
  });
  cues.push({
    text: CAPTION_LINES[CAPTION_LINES.length - 1],
    start: cursor,
    end: UKRAINE_WIDE_FRAMES,
  });
  return cues;
})();

const WideCaptions: React.FC = () => {
  const frame = useCurrentFrame();
  const active = captionCues.find((cue) => frame >= cue.start && frame < cue.end);
  if (!active) return null;

  return (
    <div
      style={{
        position: "absolute",
        left: 80,
        right: 80,
        bottom: 48,
        backgroundColor: "rgba(6, 11, 23, 0.92)",
        border: "1px solid rgba(56, 189, 248, 0.45)",
        padding: "16px 28px",
        borderRadius: 14,
        zIndex: 48,
        textAlign: "center",
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      <span
        style={{
          color: "#f8fafc",
          fontSize: 32,
          fontWeight: 700,
          lineHeight: 1.3,
        }}
      >
        {active.text}
      </span>
    </div>
  );
};

export const UkraineWide: React.FC = () => {
  const frame = useCurrentFrame();
  const cutIndex = Math.floor(frame / CUT_FRAMES) % CUTS.length;
  const local = frame % CUT_FRAMES;
  const scale = interpolate(local, [0, CUT_FRAMES], [1.04, 1.12], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "relative",
        width: 1920,
        height: 1080,
        backgroundColor: "#030712",
        overflow: "hidden",
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      <Audio src={staticFile("audio/aibrief_theme.wav")} volume={0.05} loop />
      <Audio src={staticFile(AUDIO_FILE)} volume={1} />

      <Img
        src={staticFile(CUTS[cutIndex])}
        style={{
          position: "absolute",
          width: 1920,
          height: 1080,
          objectFit: "cover",
          transform: `scale(${scale})`,
        }}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(180deg, rgba(3,7,18,0.82) 0%, rgba(3,7,18,0.12) 32%, rgba(3,7,18,0.18) 58%, rgba(3,7,18,0.9) 100%)",
        }}
      />

      <div style={{ position: "absolute", top: 48, left: 64, right: 64, zIndex: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: 99,
              backgroundColor: "#ef4444",
            }}
          />
          <span style={{ color: "#fecaca", fontSize: 22, fontWeight: 800, letterSpacing: 3 }}>
            SANMITRA AI NEWS WIRE
          </span>
          <span style={{ color: "#94a3b8", fontSize: 20, fontWeight: 700, letterSpacing: 1.2 }}>
            03 OCTOBER 2026  ·  WORLD
          </span>
        </div>
      </div>

      <div style={{ position: "absolute", left: 64, right: 64, bottom: 168, zIndex: 20 }}>
        <div
          style={{
            display: "inline-block",
            backgroundColor: "#dc2626",
            color: "#ffffff",
            fontSize: 16,
            fontWeight: 900,
            letterSpacing: 2,
            padding: "6px 12px",
            marginBottom: 12,
          }}
        >
          LEAD STORY
        </div>
        <div
          style={{
            color: "#f8fafc",
            fontSize: 54,
            fontWeight: 800,
            lineHeight: 1.1,
            textShadow: "0 8px 24px rgba(0,0,0,0.8)",
          }}
        >
          {HEADLINE}
        </div>
        <div style={{ marginTop: 12, color: "#7dd3fc", fontSize: 22, fontWeight: 700 }}>
          Financial Times · Associated Press
        </div>
      </div>

      <WideCaptions />
    </div>
  );
};
