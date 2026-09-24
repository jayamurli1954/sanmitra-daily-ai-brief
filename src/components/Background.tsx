import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export const Background: React.FC = () => {
  const frame = useCurrentFrame();

  // Subtle breathing animations for ambient light orbs
  const orb1Scale = interpolate(
    Math.sin(frame / 45),
    [-1, 1],
    [0.9, 1.15]
  );
  const orb2Scale = interpolate(
    Math.cos(frame / 60),
    [-1, 1],
    [0.85, 1.1]
  );
  const orb1X = interpolate(
    Math.sin(frame / 80),
    [-1, 1],
    [-40, 40]
  );
  const orb2Y = interpolate(
    Math.cos(frame / 70),
    [-1, 1],
    [-30, 30]
  );

  return (
    <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-950 overflow-hidden select-none pointer-events-none">
      {/* Dynamic Ambient Glow Orbs */}
      <div
        className="absolute w-[800px] h-[800px] rounded-full blur-[140px] opacity-25 bg-gradient-to-tr from-indigo-600 to-cyan-400"
        style={{
          top: "10%",
          left: "15%",
          transform: `translate(${orb1X}px, ${orb2Y}px) scale(${orb1Scale})`,
        }}
      />
      <div
        className="absolute w-[700px] h-[700px] rounded-full blur-[160px] opacity-20 bg-gradient-to-br from-violet-600 to-blue-500"
        style={{
          bottom: "10%",
          right: "15%",
          transform: `translate(${-orb1X}px, ${-orb2Y}px) scale(${orb2Scale})`,
        }}
      />

      {/* Cybernetic Tech Grid Overlay */}
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage: `
            linear-gradient(to right, #ffffff 1px, transparent 1px),
            linear-gradient(to bottom, #ffffff 1px, transparent 1px)
          `,
          backgroundSize: "60px 60px",
        }}
      />

      {/* Vignette border glow */}
      <div className="absolute inset-0 ring-1 ring-inset ring-white/10" />
      <div className="absolute inset-0 bg-radial from-transparent via-transparent to-black/60" />
    </div>
  );
};
