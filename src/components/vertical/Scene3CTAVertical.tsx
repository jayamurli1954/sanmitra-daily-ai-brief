import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { KineticText } from "../KineticText";

export const Scene3CTAVertical: React.FC = () => {
  const frame = useCurrentFrame();

  const glowSweep = interpolate(
    (frame % 70) / 70,
    [0, 1],
    [-100, 200]
  );

  return (
    <div className="absolute inset-0 flex items-center justify-center overflow-hidden px-10">
      {/* Radiant Background Aura */}
      <div className="absolute w-[800px] h-[600px] rounded-full bg-gradient-to-r from-indigo-500/20 via-cyan-500/20 to-violet-500/20 blur-[150px] pointer-events-none" />

      <div className="flex flex-col items-center justify-center w-full max-w-[920px] text-center">
        {/* Top Tagline */}
        <KineticText delay={5}>
          <div className="inline-flex items-center gap-3 px-6 py-2.5 rounded-full border border-indigo-400/40 bg-indigo-950/70 backdrop-blur-xl mb-8 shadow-lg shadow-indigo-950/60">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
            <span className="text-sm font-mono font-bold tracking-widest text-cyan-300 uppercase">
              Flawless Mobile Continuity
            </span>
          </div>
        </KineticText>

        {/* Main Headline */}
        <KineticText delay={15} initialScale={0.88} damping={12} stiffness={120}>
          <h2 className="text-7xl md:text-8xl font-black tracking-tight text-white leading-none">
            SECURE YOUR <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400">
              WORKFLOW TODAY.
            </span>
          </h2>
        </KineticText>

        {/* Subtext */}
        <KineticText delay={30}>
          <p className="mt-8 text-2xl text-slate-300 font-light max-w-lg leading-relaxed">
            Stop gambling with local storage. Download the app now and get instant cloud sync forever.
          </p>
        </KineticText>

        {/* Primary CTA Button */}
        <KineticText delay={45} initialScale={0.85} damping={11} stiffness={130}>
          <div className="mt-12 w-full max-w-lg relative group">
            <div className="absolute -inset-1 rounded-3xl bg-gradient-to-r from-cyan-500 via-indigo-500 to-purple-600 opacity-80 blur-xl group-hover:opacity-100 transition duration-500 animate-pulse" />
            <div className="relative w-full py-6 rounded-3xl bg-gradient-to-r from-cyan-500 to-indigo-600 font-black text-white text-2xl tracking-wider shadow-2xl flex items-center justify-center gap-4 overflow-hidden border border-white/20">
              <div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent skew-x-12 pointer-events-none"
                style={{
                  transform: `translateX(${glowSweep}%)`,
                }}
              />
              <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>DOWNLOAD NOW</span>
            </div>
          </div>
        </KineticText>

        {/* Platform & Trust Badges */}
        <KineticText delay={65} initialY={30}>
          <div className="mt-12 flex flex-wrap items-center justify-center gap-4 text-base text-slate-300 font-medium max-w-xl">
            <span className="flex items-center gap-2.5 px-4 py-2 rounded-xl bg-white/5 border border-white/10">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              iOS & Android
            </span>
            <span className="flex items-center gap-2.5 px-4 py-2 rounded-xl bg-white/5 border border-white/10">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              macOS & Windows
            </span>
            <span className="flex items-center gap-2.5 px-4 py-2 rounded-xl bg-white/5 border border-white/10">
              <span className="w-2 h-2 rounded-full bg-cyan-400" />
              End-to-End Encrypted
            </span>
            <span className="flex items-center gap-2.5 px-4 py-2 rounded-xl bg-white/5 border border-white/10">
              <span className="w-2 h-2 rounded-full bg-cyan-400" />
              14-Day Free Pro Trial
            </span>
          </div>
        </KineticText>
      </div>
    </div>
  );
};
