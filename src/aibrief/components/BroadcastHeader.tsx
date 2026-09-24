import React from "react";
import { useCurrentFrame } from "remotion";
import { Region } from "../types";

interface BroadcastHeaderProps {
  date: string;
  region?: Region;
  isSpecialReport?: boolean;
  storyIndex?: number;
  totalStories?: number;
}

const REGION_COLORS: Record<Region, string> = {
  WORLD: "#38bdf8",
  ASIA: "#10b981",
  USA: "#3b82f6",
  CHINA: "#ef4444",
  INDIA: "#f59e0b",
  GLOBAL: "#a855f7",
};

export const BroadcastHeader: React.FC<BroadcastHeaderProps> = ({
  date,
  region = "GLOBAL",
  isSpecialReport = true,
  storyIndex,
  totalStories = 6,
}) => {
  const frame = useCurrentFrame();

  // Blinking red dot every 20 frames (approx. 0.66s)
  const isBlinkOn = Math.floor(frame / 20) % 2 === 0;

  // Running broadcast timecode
  const totalSeconds = Math.floor(frame / 30);
  const mins = Math.floor(totalSeconds / 60);
  const secs = totalSeconds % 60;
  const frames = frame % 30;
  const timecode = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}:${String(frames).padStart(2, "0")}`;

  const regionColor = REGION_COLORS[region] || "#38bdf8";

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: 1920,
        height: 72,
        backgroundColor: "rgba(6, 11, 23, 0.96)",
        borderBottom: "1px solid rgba(56, 189, 248, 0.3)",
        boxShadow: "0 4px 24px rgba(0, 0, 0, 0.7)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 48px",
        zIndex: 50,
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      {/* Left: Brand Identity */}
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <div
          style={{
            backgroundColor: "#dc2626",
            color: "#ffffff",
            padding: "4px 12px",
            fontSize: 15,
            fontWeight: 900,
            letterSpacing: 2,
            borderRadius: 4,
            boxShadow: "0 0 16px rgba(220, 38, 38, 0.5)",
          }}
        >
          AI WIRE
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          <span
            style={{
              color: "#f8fafc",
              fontSize: 14,
              fontWeight: 900,
              letterSpacing: 1.5,
              textTransform: "uppercase",
            }}
          >
            SANMITRA AI NEWS WIRE
          </span>
          <span
            style={{
              color: "#94a3b8",
              fontSize: 10,
              fontWeight: 700,
              letterSpacing: 1,
            }}
          >
            GLOBAL AI INTELLIGENCE DESK
          </span>
        </div>
      </div>

      {/* Center: Date & Region */}
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <span
          style={{
            color: "#cbd5e1",
            fontSize: 13,
            fontWeight: 800,
            letterSpacing: 1.5,
            textTransform: "uppercase",
          }}
        >
          {date}
        </span>

        <div
          style={{
            width: 1,
            height: 20,
            backgroundColor: "rgba(255, 255, 255, 0.2)",
          }}
        />

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            backgroundColor: "rgba(15, 23, 42, 0.9)",
            border: `1px solid ${regionColor}`,
            padding: "4px 12px",
            borderRadius: 16,
          }}
        >
          <div
            style={{
              width: 7,
              height: 7,
              borderRadius: "50%",
              backgroundColor: regionColor,
              boxShadow: `0 0 8px ${regionColor}`,
            }}
          />
          <span
            style={{
              color: "#ffffff",
              fontSize: 12,
              fontWeight: 900,
              letterSpacing: 1.5,
            }}
          >
            REGION: {region}
          </span>
        </div>
      </div>

      {/* Right: Story Progress Indicator, Live Status & Timecode */}
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        {/* Story Progress Indicator (e.g. Story 1 of 6) */}
        {storyIndex !== undefined && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              backgroundColor: "rgba(14, 165, 233, 0.15)",
              border: "1px solid rgba(56, 189, 248, 0.4)",
              padding: "4px 12px",
              borderRadius: 6,
            }}
          >
            <span style={{ color: "#38bdf8", fontSize: 12, fontWeight: 900, letterSpacing: 1 }}>
              STORY {storyIndex} OF {totalStories}
            </span>
          </div>
        )}

        {/* Live Indicator */}
        <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
          <div
            style={{
              width: 9,
              height: 9,
              borderRadius: "50%",
              backgroundColor: isBlinkOn ? "#ef4444" : "#7f1d1d",
              boxShadow: isBlinkOn ? "0 0 10px #ef4444" : "none",
            }}
          />
          <span
            style={{
              color: "#ef4444",
              fontSize: 12,
              fontWeight: 900,
              letterSpacing: 1.5,
            }}
          >
            {isSpecialReport ? "SPECIAL REPORT" : "LIVE"}
          </span>
        </div>

        {/* Timecode */}
        <div
          style={{
            color: "#94a3b8",
            fontSize: 12,
            fontWeight: 700,
            fontFamily: "monospace",
            backgroundColor: "rgba(15, 23, 42, 0.9)",
            padding: "3px 8px",
            borderRadius: 4,
            border: "1px solid rgba(148, 163, 184, 0.2)",
          }}
        >
          {timecode}
        </div>
      </div>
    </div>
  );
};
