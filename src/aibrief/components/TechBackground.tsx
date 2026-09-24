import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

interface TechBackgroundProps {
  tintColor?: string;
}

export const TechBackground: React.FC<TechBackgroundProps> = ({
  tintColor = "#0284c7",
}) => {
  const frame = useCurrentFrame();

  // Subtle grid translation
  const gridOffsetY = (frame * 0.4) % 60;
  const gridOffsetX = (frame * 0.2) % 60;

  // Globe wireframe rotation
  const globeAngle = (frame * 0.5) % 360;

  // Pulsing glow
  const glowOpacity = interpolate(
    Math.sin(frame * 0.05),
    [-1, 1],
    [0.18, 0.32]
  );

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: 1920,
        height: 1080,
        backgroundColor: "#060913",
        overflow: "hidden",
        zIndex: 0,
      }}
    >
      {/* Background Gradient Mesh */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(circle at 75% 25%, #0f2444 0%, #060b17 55%, #03060c 100%)",
        }}
      />

      {/* Cyber Grid Lines */}
      <svg
        style={{
          position: "absolute",
          inset: 0,
          width: 1920,
          height: 1080,
          opacity: 0.16,
          transform: `translate(${gridOffsetX}px, ${gridOffsetY}px)`,
        }}
      >
        <defs>
          <pattern
            id="cyberGrid"
            width="60"
            height="60"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 60 0 L 0 0 0 60"
              fill="none"
              stroke="#38bdf8"
              strokeWidth="0.8"
            />
          </pattern>
        </defs>
        <rect width="2100" height="1200" fill="url(#cyberGrid)" />
      </svg>

      {/* Animated Digital Wireframe Globe (Center-Right) */}
      <div
        style={{
          position: "absolute",
          right: 80,
          top: "50%",
          transform: "translateY(-50%)",
          width: 720,
          height: 720,
          opacity: 0.22,
          pointerEvents: "none",
        }}
      >
        <svg viewBox="0 0 400 400" width="100%" height="100%">
          <defs>
            <radialGradient id="globeGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor={tintColor} stopOpacity="0.4" />
              <stop offset="80%" stopColor="#0369a1" stopOpacity="0.1" />
              <stop offset="100%" stopColor="#000000" stopOpacity="0" />
            </radialGradient>
          </defs>
          <circle cx="200" cy="200" r="180" fill="url(#globeGlow)" />
          <circle
            cx="200"
            cy="200"
            r="170"
            fill="none"
            stroke="#38bdf8"
            strokeWidth="1.5"
            strokeDasharray="6 4"
          />
          {/* Latitude lines */}
          <ellipse
            cx="200"
            cy="200"
            rx="170"
            ry="60"
            fill="none"
            stroke="#38bdf8"
            strokeWidth="1.2"
            opacity="0.6"
          />
          <ellipse
            cx="200"
            cy="200"
            rx="170"
            ry="120"
            fill="none"
            stroke="#38bdf8"
            strokeWidth="1.2"
            opacity="0.5"
          />
          <ellipse
            cx="200"
            cy="200"
            rx="170"
            ry="160"
            fill="none"
            stroke="#38bdf8"
            strokeWidth="1"
            opacity="0.4"
          />
          {/* Rotating Longitude line */}
          <ellipse
            cx="200"
            cy="200"
            rx={Math.abs(Math.sin((globeAngle * Math.PI) / 180) * 170)}
            ry="170"
            fill="none"
            stroke="#0ea5e9"
            strokeWidth="1.8"
          />
          {/* Rotating node dots */}
          {[0, 60, 120, 180, 240, 300].map((deg, i) => {
            const rad = ((globeAngle + deg) * Math.PI) / 180;
            const cx = 200 + Math.cos(rad) * 150;
            const cy = 200 + Math.sin(rad) * 50;
            return (
              <circle
                key={i}
                cx={cx}
                cy={cy}
                r="4"
                fill="#38bdf8"
                opacity="0.8"
              />
            );
          })}
        </svg>
      </div>

      {/* Ambient Radial Spotlight */}
      <div
        style={{
          position: "absolute",
          top: "15%",
          left: "20%",
          width: 800,
          height: 800,
          background: `radial-gradient(circle, ${tintColor} 0%, rgba(2,132,199,0) 70%)`,
          opacity: glowOpacity,
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />

      {/* Scanline CRT overlay for subtle broadcast fidelity */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "repeating-linear-gradient(0deg, rgba(0,0,0,0.12) 0px, rgba(0,0,0,0.12) 1px, transparent 1px, transparent 3px)",
          pointerEvents: "none",
          opacity: 0.7,
        }}
      />
    </div>
  );
};
