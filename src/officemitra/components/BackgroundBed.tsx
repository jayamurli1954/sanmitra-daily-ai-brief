import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

interface BackgroundBedProps {
  intensity?: "normal" | "dark" | "intense" | "cyan";
}

export const BackgroundBed: React.FC<BackgroundBedProps> = ({ intensity = "normal" }) => {
  const frame = useCurrentFrame();

  const glowShiftX = interpolate(frame % 300, [0, 150, 300], [-80, 80, -80]);
  const glowShiftY = interpolate(frame % 240, [0, 120, 240], [-40, 40, -40]);

  const primaryGlow =
    intensity === "dark"
      ? "radial-gradient(ellipse at 50% 30%, rgba(30, 58, 138, 0.22) 0%, rgba(15, 23, 42, 0.95) 75%)"
      : intensity === "cyan"
      ? "radial-gradient(ellipse at 50% 40%, rgba(6, 182, 212, 0.28) 0%, rgba(15, 23, 42, 0.98) 75%)"
      : intensity === "intense"
      ? "radial-gradient(ellipse at 50% 35%, rgba(59, 130, 246, 0.35) 0%, rgba(15, 23, 42, 0.98) 80%)"
      : "radial-gradient(ellipse at 50% 40%, rgba(37, 99, 235, 0.25) 0%, rgba(11, 15, 25, 0.98) 80%)";

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        backgroundColor: "#080c16",
        background: primaryGlow,
        overflow: "hidden",
        pointerEvents: "none",
      }}
    >
      {/* Subtle perspective grid */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `
            linear-gradient(to right, rgba(255, 255, 255, 0.04) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.04) 1px, transparent 1px)
          `,
          backgroundSize: "64px 64px",
          opacity: 0.75,
          maskImage: "radial-gradient(circle at 50% 50%, black 30%, transparent 80%)",
          WebkitMaskImage: "radial-gradient(circle at 50% 50%, black 30%, transparent 80%)",
        }}
      />

      {/* Floating accent light orb */}
      <div
        style={{
          position: "absolute",
          top: "20%",
          left: "50%",
          width: 700,
          height: 400,
          transform: `translate(-50%, -50%) translate(${glowShiftX}px, ${glowShiftY}px)`,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(56, 189, 248, 0.15) 0%, transparent 70%)",
          filter: "blur(60px)",
        }}
      />
    </div>
  );
};
