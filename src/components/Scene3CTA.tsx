import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { KineticText } from "./KineticText";

export const Scene3CTA: React.FC = () => {
  const frame = useCurrentFrame();

  // Button glow sweep animation
  const glowSweep = interpolate(
    (frame % 70) / 70,
    [0, 1],
    [-100, 200]
  );

  return (
    <div className="absolute inset-0 flex items-center justify-center overflow-hidden px-8">
      {/* Radiant Glow Behind CTA */}
      <div className="absolute w-[850px] h-[550px] rounded-full bg-gradient-to-r from-indigo-500/20 via-cyan-500/20 to-violet-500/20 blur-[140px] pointer-events-none" />

      <div className="relative z-10 flex flex-col items-center justify-center max-w-4xl text-center">
        {/* Top Tagline */}
        <KineticText delay={5}>
          <div className="inline-flex items-center gap-2 px-5 py-2 rounded-full border border-indigo-400/30 bg-indigo-950/60 backdrop-blur-xl mb-6 shadow-lg shadow-indigo-950/50">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span className="text-xs font-mono font-bold tracking-widest text-cyan-300 uppercase">
              Experience Flawless Continuity
            </span>
          </div>
        </KineticText>

        {/* Main Headline */}
        <KineticText delay={15} initialScale={0.88} damping={12} stiffness={120}>
          <h2 className="text-6xl md:text-8xl font-black tracking-tight text-white leading-none">
            SECURE YOUR <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400">
              WORKFLOW TODAY.
            </span>
          </h2>
        </KineticText>

        {/* Supporting Subtext */}
        <KineticText delay={30}>
          <p className="mt-6 text-2xl text-slate-300 font-light max-w-2xl leading-relaxed">
            Stop gambling with local storage. Download the mobile app and get instant, automatic cloud sync forever.
          </p>
        </KineticText>

        {/* Prominent CTA Button with animated border and sheen */}
        <KineticText delay={45} initialScale={0.85} damping={11} stiffness={130}>
          <div className="mt-10 relative group">
            {/* Glow Aura */}
            <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-cyan-500 via-indigo-500 to-purple-600 opacity-80 blur-xl group-hover:opacity-100 transition duration-500 animate-pulse" />

            <div className="relative px-12 py-5 rounded-2xl bg-gradient-to-r from-cyan-500 to-indigo-600 font-extrabold text-white text-2xl tracking-wide shadow-2xl flex items-center gap-4 overflow-hidden border border-white/20">
              {/* Shimmer sweep effect */}
              <div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent skew-x-12 pointer-events-none"
                style={{
                  transform: `translateX(${glowSweep}%)`,
                }}
              />
              <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>DOWNLOAD NOW</span>
            </div>
          </div>
        </KineticText>

        {/* Platform badges & Trust indicators */}
        <KineticText delay={65} initialY={30}>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-6 text-sm text-slate-400 font-medium">
            <span className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              iOS & Android
            </span>
            <span className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              macOS & Windows
            </span>
            <span className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
              End-to-End Encrypted
            </span>
            <span className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
              Free 14-Day Pro Trial
            </span>
          </div>
        </KineticText>
      </div>
    </div>
  );
};
