import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { KineticText } from "../KineticText";

export const Scene1HookVertical: React.FC = () => {
  const frame = useCurrentFrame();

  // Glitch shake effect
  const isCrashing = frame >= 80 && frame <= 140;
  const shakeX = isCrashing
    ? Math.sin(frame * 0.9) * interpolate(frame, [80, 95, 140], [3, 16, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;
  const shakeY = isCrashing
    ? Math.cos(frame * 1.1) * interpolate(frame, [80, 95, 140], [3, 12, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;

  // Flash red on crash
  const redFlash = interpolate(frame, [85, 95, 125, 145], [0, 0.45, 0.15, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Battery drain
  const batteryLevel = interpolate(frame, [50, 90], [84, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      className="absolute inset-0 flex items-center justify-center overflow-hidden px-10"
      style={{
        transform: `translate(${shakeX}px, ${shakeY}px)`,
      }}
    >
      {/* Red Alert Flash */}
      <div
        className="absolute inset-0 bg-rose-600 pointer-events-none transition-opacity"
        style={{ opacity: redFlash }}
      />

      {/* Part 1: Deep in focus (frames 0 - 85) */}
      {frame < 95 && (
        <div className="flex flex-col items-center justify-center w-full max-w-[920px]">
          <KineticText delay={5} exitFrame={80}>
            <div className="inline-flex items-center gap-3 px-6 py-2.5 rounded-full border border-indigo-500/30 bg-indigo-950/70 backdrop-blur-md mb-8 shadow-lg">
              <span className="w-3 h-3 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-sm font-mono tracking-widest text-indigo-200 uppercase font-semibold">
                Late Night Session • 4 Hours Deep
              </span>
            </div>
          </KineticText>

          <KineticText delay={15} exitFrame={80} initialScale={0.9}>
            <h1 className="text-8xl font-black text-center tracking-tight text-white leading-none">
              YOU'RE IN <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400">
                THE ZONE.
              </span>
            </h1>
          </KineticText>

          <KineticText delay={28} exitFrame={80}>
            <p className="mt-8 text-3xl text-indigo-200/90 font-light tracking-wide text-center leading-snug max-w-xl">
              Hours of pure creative flow, shaping your biggest mobile project yet.
            </p>
          </KineticText>

          {/* Editor Mockup Card */}
          <KineticText delay={40} exitFrame={80} initialY={50}>
            <div className="mt-14 w-full rounded-2xl border border-white/10 bg-slate-900/85 p-6 shadow-2xl backdrop-blur-xl">
              <div className="flex items-center justify-between pb-4 border-b border-white/10">
                <div className="flex items-center gap-2.5">
                  <div className="w-3.5 h-3.5 rounded-full bg-rose-500/80" />
                  <div className="w-3.5 h-3.5 rounded-full bg-amber-500/80" />
                  <div className="w-3.5 h-3.5 rounded-full bg-emerald-500/80" />
                  <span className="ml-2 text-sm font-mono text-slate-400">app_screen_v4.canvas</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono text-slate-300">
                    {Math.max(0, Math.round(batteryLevel))}% Battery
                  </span>
                  <span className="text-xs font-mono text-amber-300 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-rose-400" />
                    1,482 Unsaved Edits
                  </span>
                </div>
              </div>
              <div className="py-6 space-y-3 font-mono text-base">
                <div className="h-4 bg-indigo-400/25 rounded w-5/6 animate-pulse" />
                <div className="h-4 bg-indigo-400/15 rounded w-3/4" />
                <div className="h-4 bg-indigo-400/30 rounded w-4/5" />
                <div className="h-4 bg-indigo-400/20 rounded w-2/3" />
              </div>
            </div>
          </KineticText>
        </div>
      )}

      {/* Part 2: Crash Catastrophe (frames 85 - 300) */}
      {frame >= 85 && (
        <div className="flex flex-col items-center justify-center w-full max-w-[920px]">
          <KineticText delay={88} exitFrame={285} initialScale={0.8}>
            <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full border border-rose-500/70 bg-rose-950/90 text-rose-300 backdrop-blur-xl shadow-xl shadow-rose-950/70 mb-8">
              <svg className="w-6 h-6 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span className="text-sm font-bold font-mono tracking-widest uppercase">
                SYSTEM CRASH • LOCAL MEMORY DUMP
              </span>
            </div>
          </KineticText>

          <KineticText delay={96} exitFrame={285} initialScale={0.82} damping={11} stiffness={130}>
            <h2 className="text-8xl md:text-9xl font-black text-center tracking-tighter text-white leading-none drop-shadow-2xl">
              EVERYTHING <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-rose-500 via-orange-400 to-rose-600">
                VANISHES.
              </span>
            </h2>
          </KineticText>

          {/* Loss Metric Box */}
          <KineticText delay={120} exitFrame={285} initialY={40}>
            <div className="mt-12 w-full grid grid-cols-2 gap-4 p-6 rounded-3xl border border-rose-500/30 bg-slate-950/90 shadow-2xl backdrop-blur-2xl">
              <div className="text-center p-4 border-r border-white/10">
                <div className="text-5xl font-black text-rose-400 font-mono">0 KB</div>
                <div className="text-sm text-slate-400 uppercase tracking-widest mt-2">Recovered</div>
              </div>
              <div className="text-center p-4">
                <div className="text-5xl font-black text-amber-400 font-mono">4.5 hrs</div>
                <div className="text-sm text-slate-400 uppercase tracking-widest mt-2">Lost Forever</div>
              </div>
            </div>
          </KineticText>

          <KineticText delay={148} exitFrame={285}>
            <p className="mt-12 text-3xl text-slate-200 font-medium tracking-wide text-center leading-relaxed max-w-xl">
              Local storage shouldn't mean living on the edge of disaster.
            </p>
          </KineticText>
        </div>
      )}
    </div>
  );
};
