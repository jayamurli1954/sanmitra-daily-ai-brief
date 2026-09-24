import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { KineticText } from "../components/KineticText";

export const Scene1Problem: React.FC = () => {
  const frame = useCurrentFrame();

  // Subtle slow zoom into advocate researcher photo
  const chamberScale = interpolate(frame, [0, 210], [1.0, 1.06]);
  const chamberOpacity = interpolate(frame, [0, 25, 185, 210], [0, 0.42, 0.42, 0]);

  return (
    <div className="absolute inset-0 flex items-center justify-center overflow-hidden px-14">
      {/* Advocate Chamber Background Image with atmospheric vignette */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          transform: `scale(${chamberScale})`,
          opacity: chamberOpacity,
        }}
      >
        <Img
          src={staticFile("legalmitra/advocate-researcher.jpg")}
          className="w-full h-full object-cover filter brightness-90 contrast-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#030712] via-[#030712]/75 to-[#030712]/85" />
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center max-w-5xl text-center">
        {/* Top Challenge Badge */}
        <KineticText delay={5} exitFrame={195}>
          <div className="inline-flex items-center gap-2.5 px-5 py-2 rounded-full border border-amber-500/40 bg-[#0c1c33]/80 backdrop-blur-xl mb-6 shadow-xl shadow-black/60">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
            <span className="text-xs font-mono font-bold tracking-widest text-amber-300 uppercase">
              The Modern Legal Bottleneck
            </span>
          </div>
        </KineticText>

        {/* 3 Outcome Pain Points */}
        <div className="space-y-2 mb-6">
          <KineticText delay={12} exitFrame={195} initialScale={0.9}>
            <h1 className="text-6xl md:text-7xl font-black tracking-tight text-white leading-tight">
              RESEARCH <span className="text-slate-400 font-light">TAKES HOURS.</span>
            </h1>
          </KineticText>

          <KineticText delay={24} exitFrame={195} initialScale={0.9}>
            <h1 className="text-6xl md:text-7xl font-black tracking-tight text-white leading-tight">
              DEADLINES <span className="bg-clip-text text-transparent bg-gradient-to-r from-rose-400 to-amber-300">CAN'T WAIT.</span>
            </h1>
          </KineticText>

          <KineticText delay={36} exitFrame={195} initialScale={0.9}>
            <h1 className="text-6xl md:text-7xl font-black tracking-tight text-white leading-tight">
              MATTERS <span className="text-slate-400 font-light">KEEP GROWING.</span>
            </h1>
          </KineticText>
        </div>

        {/* Floating Urgency Case Card */}
        <KineticText delay={50} exitFrame={195} initialY={30}>
          <div className="mt-4 inline-flex items-center gap-6 px-8 py-3.5 rounded-2xl border border-rose-500/40 bg-slate-950/90 shadow-2xl backdrop-blur-2xl">
            <div className="flex items-center gap-3 border-r border-white/15 pr-6 text-left">
              <div className="w-10 h-10 rounded-xl bg-rose-500/15 border border-rose-500/40 flex items-center justify-center text-rose-400">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <div className="text-xs font-mono text-rose-300 font-bold uppercase tracking-wider">Limitation Alert</div>
                <div className="text-sm font-semibold text-white">Commercial Appeal #482/2026</div>
              </div>
            </div>
            <div className="text-left">
              <span className="inline-block px-3 py-1 rounded-md bg-rose-950/80 border border-rose-500/50 text-xs font-mono font-bold text-rose-300">
                EXPIRES IN 48 HOURS
              </span>
            </div>
          </div>
        </KineticText>
      </div>
    </div>
  );
};
