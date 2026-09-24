import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export const LegalBackground: React.FC = () => {
  const frame = useCurrentFrame();

  const glow1X = interpolate(Math.sin(frame / 60), [-1, 1], [-30, 30]);
  const glow2Y = interpolate(Math.cos(frame / 75), [-1, 1], [-25, 25]);
  const glowScale = interpolate(Math.sin(frame / 50), [-1, 1], [0.95, 1.08]);

  return (
    <div className="absolute inset-0 bg-gradient-to-br from-[#050b14] via-[#08172c] to-[#0d213d] overflow-hidden select-none pointer-events-none">
      {/* Antique Gold Ambient Light Pools */}
      <div
        className="absolute w-[800px] h-[800px] rounded-full blur-[160px] opacity-20 bg-gradient-to-tr from-amber-600 via-yellow-500 to-amber-200"
        style={{
          top: "10%",
          left: "20%",
          transform: `translate(${glow1X}px, ${glow2Y}px) scale(${glowScale})`,
        }}
      />
      <div
        className="absolute w-[700px] h-[700px] rounded-full blur-[180px] opacity-15 bg-gradient-to-br from-blue-700 via-indigo-600 to-slate-900"
        style={{
          bottom: "15%",
          right: "15%",
          transform: `translate(${-glow1X}px, ${-glow2Y}px) scale(${glowScale})`,
        }}
      />

      {/* Prestige Legal Grid Lines */}
      <div
        className="absolute inset-0 opacity-[0.035]"
        style={{
          backgroundImage: `
            linear-gradient(to right, #e7c77c 1px, transparent 1px),
            linear-gradient(to bottom, #e7c77c 1px, transparent 1px)
          `,
          backgroundSize: "75px 75px",
        }}
      />

      {/* Luxury Vignette */}
      <div className="absolute inset-0 ring-1 ring-inset ring-amber-500/10" />
      <div className="absolute inset-0 bg-radial from-transparent via-transparent to-black/70" />
    </div>
  );
};
