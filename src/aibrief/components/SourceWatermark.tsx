import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

interface SourceWatermarkProps {
  source: string;
  sourceUrl?: string;
}

export const SourceWatermark: React.FC<SourceWatermarkProps> = ({
  source,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  const opacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        top: 96,
        right: 48,
        display: "flex",
        alignItems: "center",
        gap: 12,
        backgroundColor: "rgba(15, 23, 42, 0.88)",
        border: "1px solid rgba(56, 189, 248, 0.4)",
        padding: "8px 18px",
        borderRadius: 8,
        boxShadow: "0 8px 24px rgba(0,0,0,0.5)",
        opacity,
        transform: `translateY(${(1 - entrance) * -12}px)`,
        zIndex: 40,
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      {/* Verified Shield Icon */}
      <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#38bdf8"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        <path d="m9 12 2 2 4-4" />
      </svg>

      <div style={{ display: "flex", flexDirection: "column" }}>
        <span
          style={{
            color: "#94a3b8",
            fontSize: 10,
            fontWeight: 800,
            letterSpacing: 1.5,
            textTransform: "uppercase",
          }}
        >
          VERIFIED REPORTING
        </span>
        <span
          style={{
            color: "#f8fafc",
            fontSize: 14,
            fontWeight: 800,
            letterSpacing: 0.5,
          }}
        >
          Source: <span style={{ color: "#38bdf8" }}>{source}</span>
        </span>
      </div>
    </div>
  );
};
