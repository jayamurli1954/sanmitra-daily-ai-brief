import React from "react";
import {
  Audio,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import episodeData from "./data/active_episode.json";
import { AIBriefEpisode } from "./types";

const episode = episodeData as unknown as AIBriefEpisode;

const SPEECH_SECONDS = 45.74;
const SPEECH_FRAMES = Math.round(SPEECH_SECONDS * 30);
export const JENNY_SHORT_FRAMES = SPEECH_FRAMES + 18;
const CUT_FRAMES = 150;
const AUDIO_FILE = "audio/aibrief/short_jenny_synthid_2026-10-02.mp3";
const HEADLINE = "DeepMind Introduces Watermarking for AI-Generated Biology";

const CAPTION_LINES = [
  "From the SanMitra newsroom, this is today's lead story.",
  "Google DeepMind has introduced SynthID Bio, a watermark for AI-generated protein sequences and molecular structures.",
  "The mark is meant to show whether a sequence came from a trusted AI system, while leaving the biological function intact.",
  "DeepMind says the signature is designed to stay with the sequence, so a later check can tell an AI-proposed design from other laboratory work.",
  "As models begin proposing proteins, drugs, and enzymes, that signature is being presented as an early biosecurity layer for AI-designed biology.",
  "The announcement comes from Google DeepMind.",
  "The full desk is on the channel.",
];

const captionCues = (() => {
  const closerFrames = 84;
  const bodyFrames = JENNY_SHORT_FRAMES - closerFrames;
  const bodyLines = CAPTION_LINES.slice(0, -1);
  const bodyChars = bodyLines.reduce((sum, line) => sum + line.length, 0);
  let cursor = 0;
  const cues = bodyLines.map((text) => {
    const span = Math.round((text.length / bodyChars) * bodyFrames);
    const cue = { text, start: cursor, end: cursor + span };
    cursor += span;
    return cue;
  });
  cues.push({
    text: CAPTION_LINES[CAPTION_LINES.length - 1],
    start: cursor,
    end: JENNY_SHORT_FRAMES,
  });
  return cues;
})();

const ShortCaptions: React.FC = () => {
  const frame = useCurrentFrame();
  const active = captionCues.find((cue) => frame >= cue.start && frame < cue.end);
  if (!active) return null;

  return (
    <div
      style={{
        position: "absolute",
        left: 48,
        right: 48,
        bottom: 360,
        backgroundColor: "rgba(6, 11, 23, 0.92)",
        border: "1px solid rgba(56, 189, 248, 0.45)",
        padding: "22px 28px",
        borderRadius: 18,
        zIndex: 48,
        textAlign: "center",
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      <span
        style={{
          color: "#f8fafc",
          fontSize: 34,
          fontWeight: 700,
          lineHeight: 1.35,
        }}
      >
        {active.text}
      </span>
    </div>
  );
};

export const JennyShort: React.FC = () => {
  const frame = useCurrentFrame();
  const story = episode.stories[0];
  const cuts = story.visualCuts && story.visualCuts.length > 0
    ? story.visualCuts
    : [];
  const cutIndex = cuts.length === 0 ? 0 : Math.floor(frame / CUT_FRAMES) % cuts.length;
  const cut = cuts[cutIndex];
  const local = frame % CUT_FRAMES;
  const scale = interpolate(local, [0, CUT_FRAMES], [1.08, 1.16], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "relative",
        width: 1080,
        height: 1920,
        backgroundColor: "#030712",
        overflow: "hidden",
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      <Audio src={staticFile("audio/aibrief_theme.wav")} volume={0.05} loop />
      <Audio
        src={staticFile(AUDIO_FILE)}
        volume={1}
      />

      {cut && (
        <Img
          src={staticFile(cut.image)}
          style={{
            position: "absolute",
            width: 1080,
            height: 1920,
            objectFit: "cover",
            transform: `scale(${scale})`,
          }}
        />
      )}

      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(180deg, rgba(3,7,18,0.88) 0%, rgba(3,7,18,0.15) 28%, rgba(3,7,18,0.2) 48%, rgba(3,7,18,0.92) 72%, rgba(3,7,18,0.96) 100%)",
        }}
      />

      <div style={{ position: "absolute", top: 88, left: 48, right: 48, zIndex: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 18 }}>
          <div
            style={{
              width: 16,
              height: 16,
              borderRadius: 99,
              backgroundColor: "#ef4444",
            }}
          />
          <span style={{ color: "#fecaca", fontSize: 22, fontWeight: 800, letterSpacing: 3 }}>
            SANMITRA AI NEWS WIRE
          </span>
        </div>
        <div style={{ color: "#94a3b8", fontSize: 24, fontWeight: 700, letterSpacing: 1.4 }}>
          {episode.formattedDate.toUpperCase()}  ·  {story.region}
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          left: 48,
          right: 48,
          bottom: 760,
          zIndex: 20,
        }}
      >
        <div
          style={{
            display: "inline-block",
            backgroundColor: "#dc2626",
            color: "#ffffff",
            fontSize: 18,
            fontWeight: 900,
            letterSpacing: 2,
            padding: "8px 14px",
            marginBottom: 18,
          }}
        >
          LEAD STORY
        </div>
        <div
          style={{
            color: "#f8fafc",
            fontSize: 44,
            fontWeight: 800,
            lineHeight: 1.15,
            textShadow: "0 8px 24px rgba(0,0,0,0.8)",
          }}
        >
          {HEADLINE}
        </div>
        <div style={{ marginTop: 22, color: "#7dd3fc", fontSize: 24, fontWeight: 700 }}>
          {story.source}
        </div>
      </div>

      <ShortCaptions />
    </div>
  );
};
