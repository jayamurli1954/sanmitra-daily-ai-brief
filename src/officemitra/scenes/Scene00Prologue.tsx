import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { BackgroundBed } from "../components/BackgroundBed";

export const Scene00Prologue: React.FC = () => {
  const frame = useCurrentFrame();

  const text1Opacity = interpolate(frame, [10, 30, 75, 90], [0, 1, 1, 0], {
    extrapolateRight: "clamp",
  });
  const text1Translate = interpolate(frame, [10, 40], [15, 0], {
    extrapolateRight: "clamp",
  });

  const text2Opacity = interpolate(frame, [35, 55, 75, 90], [0, 1, 1, 0], {
    extrapolateRight: "clamp",
  });
  const text2Translate = interpolate(frame, [35, 65], [15, 0], {
    extrapolateRight: "clamp",
  });

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
        backgroundColor: "#030712",
        overflow: "hidden",
      }}
    >
      <BackgroundBed intensity="dark" />

      {/* Subtle glowing horizontal rule */}
      <div
        style={{
          width: interpolate(frame, [15, 60], [0, 500], { extrapolateRight: "clamp" }),
          height: 1,
          background: "linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.6), transparent)",
          marginBottom: 32,
        }}
      />

      <div
        style={{
          opacity: text1Opacity,
          transform: `translateY(${text1Translate}px)`,
          color: "#94a3b8",
          fontSize: 32,
          fontWeight: 400,
          fontFamily: "Inter, sans-serif",
          letterSpacing: "0.04em",
          textAlign: "center",
          marginBottom: 12,
        }}
      >
        Every CA Firm Collects Data.
      </div>

      <div
        style={{
          opacity: text2Opacity,
          transform: `translateY(${text2Translate}px)`,
          color: "#f8fafc",
          fontSize: 48,
          fontWeight: 700,
          fontFamily: "Inter, sans-serif",
          letterSpacing: "-0.02em",
          textAlign: "center",
          textShadow: "0 0 30px rgba(56, 189, 248, 0.4)",
        }}
      >
        Few Convert It Into{" "}
        <span
          style={{
            background: "linear-gradient(135deg, #38bdf8 0%, #818cf8 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          Intelligence.
        </span>
      </div>
    </div>
  );
};
