import React from "react";
import { Audio, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BackgroundBed } from "../components/BackgroundBed";
import { SubtitleDisplay } from "../components/SubtitleDisplay";

export const Scene03Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const logoSpring = spring({ frame: frame - 5, fps, config: { damping: 14 } });
  const textSpring = spring({ frame: frame - 20, fps, config: { damping: 15 } });

  const pulseRing = Math.sin(frame / 10) * 0.15 + 0.85;

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
        backgroundColor: "#070b16",
        overflow: "hidden",
      }}
    >
      <Audio src={staticFile("audio/officemitra/om_s03_intro.mp3")} volume={1.0} />
      <BackgroundBed intensity="cyan" />

      {/* Halo energy ring */}
      <div
        style={{
          position: "absolute",
          width: 500,
          height: 500,
          borderRadius: "50%",
          border: "2px solid rgba(56, 189, 248, 0.3)",
          boxShadow: "0 0 60px rgba(56, 189, 248, 0.2)",
          transform: `scale(${pulseRing})`,
          pointerEvents: "none",
        }}
      />

      {/* Main Logo Reveal Card */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          zIndex: 20,
          opacity: interpolate(logoSpring, [0, 1], [0, 1]),
          transform: `scale(${interpolate(logoSpring, [0, 1], [0.85, 1])})`,
        }}
      >
        <div
          style={{
            backgroundColor: "rgba(15, 23, 42, 0.8)",
            border: "1px solid rgba(56, 189, 248, 0.4)",
            borderRadius: 24,
            padding: "24px 48px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            boxShadow: "0 25px 60px rgba(0, 0, 0, 0.7), 0 0 40px rgba(56, 189, 248, 0.2)",
            backdropFilter: "blur(16px)",
            marginBottom: 28,
          }}
        >
          <Img
            src={staticFile("officemitra/officemitra-logo-banner.png")}
            style={{
              height: 90,
              objectFit: "contain",
            }}
          />
        </div>

        {/* Brand Tagline Header */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            textAlign: "center",
            opacity: interpolate(textSpring, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(textSpring, [0, 1], [20, 0])}px)`,
          }}
        >
          <span
            style={{
              fontSize: 14,
              fontFamily: "JetBrains Mono, monospace",
              fontWeight: 700,
              color: "#38bdf8",
              letterSpacing: "0.2em",
              textTransform: "uppercase",
              marginBottom: 12,
              backgroundColor: "rgba(56, 189, 248, 0.15)",
              padding: "4px 16px",
              borderRadius: 20,
              border: "1px solid rgba(56, 189, 248, 0.3)",
            }}
          >
            Practice Operating System
          </span>

          <h2
            style={{
              fontSize: 44,
              fontWeight: 800,
              fontFamily: "Inter, sans-serif",
              letterSpacing: "-0.02em",
              color: "#ffffff",
              margin: "0 0 14px 0",
            }}
          >
            The Operating System for Modern Chartered Accountants
          </h2>

          {/* 4 Pillars Preview */}
          <div
            style={{
              display: "flex",
              gap: 16,
              marginTop: 10,
            }}
          >
            {["Smart Intake", "SSDV Engine", "Review Intelligence", "CFO Advisory"].map((p) => (
              <div
                key={p}
                style={{
                  backgroundColor: "rgba(30, 41, 59, 0.6)",
                  border: "1px solid rgba(148, 163, 184, 0.2)",
                  padding: "6px 14px",
                  borderRadius: 8,
                  fontSize: 13,
                  fontWeight: 600,
                  color: "#94a3b8",
                  fontFamily: "Inter, sans-serif",
                }}
              >
                {p}
              </div>
            ))}
          </div>
        </div>
      </div>

      <SubtitleDisplay
        text="Introducing OfficeMitra. The AI-powered operating system designed specifically for modern Chartered Accountants."
        highlightWord="OfficeMitra"
      />
    </div>
  );
};
