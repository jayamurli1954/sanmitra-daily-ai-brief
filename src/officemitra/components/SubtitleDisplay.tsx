import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

interface SubtitleDisplayProps {
  text: string;
  leadInFrames?: number;
  highlightWord?: string;
}

export const SubtitleDisplay: React.FC<SubtitleDisplayProps> = ({
  text,
  leadInFrames = 8,
  highlightWord,
}) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, leadInFrames], [0, 1], {
    extrapolateRight: "clamp",
  });

  const translateY = interpolate(frame, [0, leadInFrames], [15, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 50,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
        zIndex: 50,
        opacity,
        transform: `translateY(${translateY}px)`,
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(11, 15, 25, 0.85)",
          border: "1px solid rgba(56, 189, 248, 0.3)",
          backdropFilter: "blur(12px)",
          borderRadius: 999,
          padding: "12px 32px",
          maxWidth: "85%",
          textAlign: "center",
          boxShadow: "0 10px 25px rgba(0, 0, 0, 0.6)",
        }}
      >
        <span
          style={{
            color: "#f1f5f9",
            fontSize: 20,
            fontWeight: 500,
            fontFamily: "Inter, sans-serif",
            letterSpacing: "-0.01em",
            lineHeight: 1.4,
          }}
        >
          {highlightWord ? (
            text.split(new RegExp(`(${highlightWord})`, "gi")).map((part, i) =>
              part.toLowerCase() === highlightWord.toLowerCase() ? (
                <span key={i} style={{ color: "#38bdf8", fontWeight: 700 }}>
                  {part}
                </span>
              ) : (
                part
              )
            )
          ) : (
            text
          )}
        </span>
      </div>
    </div>
  );
};
