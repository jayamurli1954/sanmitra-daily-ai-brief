import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Story, VisualCut } from "../types";
import { getStoryVisualCuts } from "./StoryCard";

/**
 * Clean story layout: one full-screen picture at a time, a single lower-third
 * bar (headline and source) and a small logo chip. No tickers,
 * badges, counters or data boxes on top of the picture.
 */

const FONT =
  "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
// AGENTS.md: each cut holds 4-6 seconds.
const CUT_FRAMES = 180;
const FADE_FRAMES = 18;

const kenBurns = (cut: VisualCut, p: number): string => {
  switch (cut.panDirection) {
    case "zoomOut":
      return `scale(${interpolate(p, [0, 1], [1.08, 1.0])})`;
    case "panLeft":
      return `scale(1.06) translateX(${interpolate(p, [0, 1], [18, -18])}px)`;
    case "panRight":
      return `scale(1.06) translateX(${interpolate(p, [0, 1], [-18, 18])}px)`;
    default:
      return `scale(${interpolate(p, [0, 1], [1.0, 1.08])})`;
  }
};

const isIllustration = (cut: VisualCut) => /illustration/i.test(cut.image);

const CutLayer: React.FC<{ cut: VisualCut; progress: number; opacity: number }> = ({
  cut,
  progress,
  opacity,
}) => (
  <AbsoluteFill style={{ overflow: "hidden", opacity }}>
    <Img
      src={staticFile(cut.image)}
      style={{
        width: "100%",
        height: "100%",
        objectFit: "cover",
        transform: kenBurns(cut, progress),
      }}
    />
  </AbsoluteFill>
);

export const CleanStoryCard: React.FC<{ story: Story }> = ({ story }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const cuts = getStoryVisualCuts(story);
  const total = Math.max(cuts.length, 1);

  const idx = Math.floor(frame / CUT_FRAMES) % total;
  const local = frame % CUT_FRAMES;
  const current = cuts[idx];
  const next = cuts[(idx + 1) % total];
  const fade =
    total > 1 && frame < durationInFrames - FADE_FRAMES
      ? interpolate(local, [CUT_FRAMES - FADE_FRAMES, CUT_FRAMES], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      : 0;

  const barIn = interpolate(frame, [6, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shownCut = fade > 0.5 ? next : current;

  return (
    <AbsoluteFill style={{ backgroundColor: "#05080f", fontFamily: FONT }}>
      {current && <CutLayer cut={current} progress={local / CUT_FRAMES} opacity={1} />}
      {next && fade > 0 && <CutLayer cut={next} progress={0} opacity={fade} />}

      {/* Soft shade at the bottom so the bar reads on any picture */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to top, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.0) 32%)",
        }}
      />

      {/* Logo chip, top right */}
      <div
        style={{
          position: "absolute",
          top: 40,
          right: 48,
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "10px 18px 10px 12px",
          borderRadius: 10,
          backgroundColor: "rgba(8, 20, 40, 0.82)",
        }}
      >
        <Img src={staticFile("aibrief/brand/sanmitra_mark.png")} style={{ width: 40, height: 40 }} />
        <div style={{ lineHeight: 1.05 }}>
          <div style={{ color: "#ffffff", fontSize: 20, fontWeight: 800, letterSpacing: 1.5 }}>SANMITRA</div>
          <div style={{ color: "#9cc3ff", fontSize: 14, fontWeight: 700, letterSpacing: 2 }}>AI NEWS</div>
        </div>
      </div>

      {/* Lower third */}
      <div
        style={{
          position: "absolute",
          left: 64,
          right: 64,
          bottom: 56,
          padding: "26px 36px 22px 36px",
          borderRadius: 8,
          backgroundColor: "rgba(10, 24, 48, 0.9)",
          borderLeft: "6px solid #3b82f6",
          opacity: barIn,
          transform: `translateY(${(1 - barIn) * 24}px)`,
        }}
      >
        <div
          style={{
            color: "#ffffff",
            fontSize: 50,
            fontWeight: 800,
            lineHeight: 1.12,
            letterSpacing: 0.2,
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          {story.headline}
        </div>
        {story.source && (
          <div style={{ marginTop: 10, color: "#a9c8f5", fontSize: 24, fontWeight: 600, letterSpacing: 0.3 }}>
            Source: {story.source}
          </div>
        )}
      </div>

      {shownCut && isIllustration(shownCut) && (
        <div
          style={{
            position: "absolute",
            left: 70,
            bottom: 26,
            color: "rgba(255,255,255,0.7)",
            fontSize: 15,
            fontWeight: 600,
            letterSpacing: 1.5,
          }}
        >
          ILLUSTRATION
        </div>
      )}
    </AbsoluteFill>
  );
};
