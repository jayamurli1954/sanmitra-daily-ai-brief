import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { KineticText } from "./KineticText";

export const Scene1Hook: React.FC = () => {
  const frame = useCurrentFrame();

  // Glitch / crash shake effect occurring between frame 80 and 130
  const isCrashing = frame >= 80 && frame <= 140;
  const shakeX = isCrashing
    ? Math.sin(frame * 0.9) * interpolate(frame, [80, 95, 140], [2, 14, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;
  const shakeY = isCrashing
    ? Math.cos(frame * 1.1) * interpolate(frame, [80, 95, 140], [2, 10, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;

  // Flash red on crash
  const redFlash = interpolate(frame, [85, 95, 125, 145], [0, 0.4, 0.15, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Battery depletion animation
  const batteryLevel = interpolate(frame, [50, 90], [84, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      className="absolute inset-0 flex items-center justify-center overflow-hidden"
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
        <div className="absolute inset-0 flex flex-col items-center justify-center px-8">
          <KineticText delay={5} exitFrame={80}>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-950/60 backdrop-blur-md mb-6">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-mono tracking-widest text-indigo-200 uppercase">
                Late Night Session • 4 Hours Deep
              </span>
            </div>
          </KineticText>

          <KineticText delay={15} exitFrame={80} initialScale={0.92}>
            <h1 className="text-7xl md:text-8xl font-black text-center tracking-tight text-white max-w-5xl leading-none">
              YOU'RE IN <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-indigo-200 to-indigo-400">THE ZONE.</span>
            </h1>
          </KineticText>

          <KineticText delay={30} exitFrame={80}>
            <p className="mt-6 text-2xl text-indigo-200/80 font-light tracking-wide max-w-2xl text-center">
              Hours of intense creative flow, shaping your biggest project yet.
            </p>
          </KineticText>

          {/* Floating Mock Editor Preview */}
          <KineticText delay={42} exitFrame={80} initialY={40}>
            <div className="mt-10 w-[720px] rounded-xl border border-white/10 bg-slate-900/80 p-5 shadow-2xl backdrop-blur-xl">
              <div className="flex items-center justify-between pb-3 border-b border-white/10">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                  <span className="ml-2 text-xs font-mono text-slate-400">Draft_Final_v3.canvas</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1.5 text-xs font-mono text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                    <span>{Math.max(0, Math.round(batteryLevel))}% Battery</span>
                  </div>
                  <span className="text-xs font-mono text-amber-300 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                    Unsaved Changes (1,482 edits)
                  </span>
                </div>
              </div>
              <div className="py-4 space-y-2 font-mono text-sm text-slate-400">
                <div className="h-3 bg-indigo-400/20 rounded w-5/6 animate-pulse" />
                <div className="h-3 bg-indigo-400/15 rounded w-3/4" />
                <div className="h-3 bg-indigo-400/25 rounded w-4/5" />
              </div>
            </div>
          </KineticText>
        </div>
      )}

      {/* Part 2: The Sudden Crash & Catastrophe (frames 90 - 300) */}
      {frame >= 85 && (
        <div className="absolute inset-0 flex flex-col items-center justify-center px-8">
          {/* Warning Glitch Badge */}
          <KineticText delay={88} exitFrame={285} initialScale={0.8}>
            <div className="inline-flex items-center gap-2.5 px-5 py-2 rounded-full border border-rose-500/60 bg-rose-950/80 text-rose-300 backdrop-blur-xl shadow-lg shadow-rose-950/60 mb-6">
              <svg className="w-5 h-5 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span className="text-sm font-bold font-mono tracking-widest uppercase">
                SYSTEM CRASH DETECTED • LOCAL MEMORY DUMP
              </span>
            </div>
          </KineticText>

          {/* Giant Impact Headline */}
          <KineticText delay={96} exitFrame={285} initialScale={0.85} damping={11} stiffness={130}>
            <h2 className="text-7xl md:text-9xl font-black text-center tracking-tighter text-white max-w-6xl leading-none drop-shadow-2xl">
              EVERYTHING <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-rose-500 via-orange-400 to-rose-600">
                VANISHES.
              </span>
            </h2>
          </KineticText>

          {/* Loss Metric Box */}
          <KineticText delay={120} exitFrame={285} initialY={30}>
            <div className="mt-8 flex items-center gap-6 px-8 py-4 rounded-2xl border border-rose-500/30 bg-slate-950/90 shadow-2xl backdrop-blur-2xl">
              <div className="text-center border-r border-white/10 pr-6">
                <div className="text-4xl font-extrabold text-rose-400 font-mono">0 KB</div>
                <div className="text-xs text-slate-400 uppercase tracking-wider mt-0.5">Recovered Data</div>
              </div>
              <div className="text-center pl-2">
                <div className="text-4xl font-extrabold text-amber-400 font-mono">4.5 hrs</div>
                <div className="text-xs text-slate-400 uppercase tracking-wider mt-0.5">Lost Forever</div>
              </div>
            </div>
          </KineticText>

          {/* Kinetic Punchline */}
          <KineticText delay={150} exitFrame={285}>
            <p className="mt-8 text-2xl md:text-3xl text-slate-300 font-medium tracking-wide text-center max-w-3xl">
              Local storage shouldn't mean living on the edge of disaster.
            </p>
          </KineticText>
        </div>
      )}
    </div>
  );
};
