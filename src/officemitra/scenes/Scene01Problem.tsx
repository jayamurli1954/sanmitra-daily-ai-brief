import React from "react";
import { Audio, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BackgroundBed } from "../components/BackgroundBed";
import { DeadlineCountdown } from "../components/DeadlineCountdown";
import { SubtitleDisplay } from "../components/SubtitleDisplay";

export const Scene01Problem: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSpring = spring({ frame: frame - 5, fps, config: { damping: 14 } });

  const badges = [
    { text: "Unreconciled GSTR-2B", top: "18%", left: "10%", color: "#ef4444" },
    { text: "WhatsApp Invoices", top: "26%", right: "12%", color: "#f59e0b" },
    { text: "Fragmented Excel Sheets", top: "72%", left: "12%", color: "#ef4444" },
    { text: "Missing Bank Statements", top: "70%", right: "10%", color: "#f59e0b" },
  ];

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#080c16",
        overflow: "hidden",
      }}
    >
      <Audio src={staticFile("audio/officemitra/om_s01_problem.mp3")} volume={1.0} />
      <BackgroundBed intensity="dark" />

      {/* Floating chaos badges */}
      {badges.map((b, i) => {
        const bSpring = spring({
          frame: frame - 15 - i * 8,
          fps,
          config: { damping: 12 },
        });
        const floatY = Math.sin((frame + i * 20) / 12) * 5;

        return (
          <div
            key={b.text}
            style={{
              position: "absolute",
              top: b.top,
              left: b.left,
              right: b.right,
              transform: `translateY(${interpolate(bSpring, [0, 1], [30, 0]) + floatY}px)`,
              opacity: interpolate(bSpring, [0, 1], [0, 0.85]),
              backgroundColor: "rgba(15, 23, 42, 0.85)",
              border: `1px solid ${b.color}`,
              boxShadow: `0 0 15px ${b.color}40`,
              borderRadius: 999,
              padding: "6px 16px",
              display: "flex",
              alignItems: "center",
              gap: 8,
              backdropFilter: "blur(10px)",
              zIndex: 10,
            }}
          >
            <div style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: b.color }} />
            <span
              style={{
                fontSize: 12,
                color: "#e2e8f0",
                fontFamily: "Inter, sans-serif",
                fontWeight: 600,
              }}
            >
              {b.text}
            </span>
          </div>
        );
      })}

      {/* Center Narrative Header */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          marginBottom: 40,
          zIndex: 20,
          opacity: interpolate(titleSpring, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleSpring, [0, 1], [25, 0])}px)`,
        }}
      >
        <span
          style={{
            fontSize: 13,
            fontFamily: "JetBrains Mono, monospace",
            fontWeight: 700,
            color: "#ef4444",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            marginBottom: 10,
            backgroundColor: "rgba(239, 68, 68, 0.15)",
            padding: "4px 14px",
            borderRadius: 6,
            border: "1px solid rgba(239, 68, 68, 0.3)",
          }}
        >
          The Compliance Challenge
        </span>

        <h1
          style={{
            fontSize: 54,
            fontWeight: 800,
            fontFamily: "Inter, sans-serif",
            letterSpacing: "-0.03em",
            color: "#f8fafc",
            lineHeight: 1.15,
            margin: "0 0 16px 0",
            maxWidth: 1000,
          }}
        >
          Too Many Clients. Too Many Deadlines.
          <br />
          <span
            style={{
              background: "linear-gradient(135deg, #f87171 0%, #fb923c 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Too Little Time.
          </span>
        </h1>

        <p
          style={{
            fontSize: 18,
            fontFamily: "Inter, sans-serif",
            color: "#94a3b8",
            maxWidth: 680,
            margin: 0,
            lineHeight: 1.5,
          }}
        >
          Every month Indian CA firms face compressed statutory timelines with exploding document volumes.
        </p>
      </div>

      {/* Realistic Statutory Deadline Timers */}
      <div style={{ zIndex: 20, width: "80%", maxWidth: 1080 }}>
        <DeadlineCountdown resolved={false} />
      </div>

      <SubtitleDisplay
        text="Modern CA firms face an impossible challenge. More compliance. More documents. Strict statutory deadlines. Yet the same limited time."
        highlightWord="statutory deadlines"
      />
    </div>
  );
};
