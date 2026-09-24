import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { KineticText } from "../KineticText";

export const Scene2SolutionVertical: React.FC = () => {
  const frame = useCurrentFrame();

  // Pulse animation for cloud sync rings
  const pulse = (frame % 40) / 40;
  const ringScale = interpolate(pulse, [0, 1], [1, 1.9]);
  const ringOpacity = interpolate(pulse, [0, 0.5, 1], [0.8, 0.3, 0]);

  // Orbit rotation
  const orbitAngle = (frame * 3) % 360;

  return (
    <div className="absolute inset-0 flex items-center justify-center overflow-hidden px-10">
      {/* Dynamic Glow */}
      <div className="absolute w-[800px] h-[800px] rounded-full bg-cyan-500/20 blur-[150px] pointer-events-none" />

      {/* Part 1: Headline Reveal (frames 0 - 150) */}
      {frame < 160 && (
        <div className="flex flex-col items-center justify-center w-full max-w-[920px]">
          <KineticText delay={5} exitFrame={145}>
            <div className="inline-flex items-center gap-3 px-6 py-2.5 rounded-full border border-cyan-400/40 bg-cyan-950/60 backdrop-blur-xl mb-8 shadow-lg shadow-cyan-950/60">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
              </span>
              <span className="text-sm font-mono font-bold tracking-widest text-cyan-300 uppercase">
                The Next Gen Workflow
              </span>
            </div>
          </KineticText>

          <KineticText delay={18} exitFrame={145} initialScale={0.88} damping={12} stiffness={120}>
            <h2 className="text-8xl md:text-9xl font-black text-center tracking-tight text-white leading-none">
              NEVER HIT <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-300">
                SAVE AGAIN.
              </span>
            </h2>
          </KineticText>

          <KineticText delay={38} exitFrame={145}>
            <p className="mt-8 text-3xl text-indigo-100 font-light text-center leading-relaxed max-w-xl">
              Introducing <strong className="font-bold text-white">Instant Cloud Syncing</strong>.
              <br />
              <span className="text-cyan-300/90 text-2xl">Real-time background sync that never sleeps.</span>
            </p>
          </KineticText>
        </div>
      )}

      {/* Part 2: Vertical Cloud Architecture & Stacked Feature Cards (frames 140 - 450) */}
      {frame >= 140 && (
        <div className="flex flex-col items-center justify-center w-full max-w-[920px]">
          {/* Top Status */}
          <KineticText delay={145} exitFrame={435}>
            <div className="inline-flex items-center gap-2.5 px-5 py-2 rounded-full border border-emerald-500/40 bg-emerald-950/60 backdrop-blur-md mb-6">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-mono font-bold text-emerald-300 tracking-wider uppercase">
                LIVE REPLICATION ACTIVE • 0.01s LATENCY
              </span>
            </div>
          </KineticText>

          {/* Central Cloud Node Graphic */}
          <KineticText delay={155} exitFrame={435} initialScale={0.75} damping={13} stiffness={100}>
            <div className="relative flex items-center justify-center my-4">
              <div
                className="absolute w-44 h-44 rounded-full border border-cyan-400/40 pointer-events-none"
                style={{
                  transform: `scale(${ringScale})`,
                  opacity: ringOpacity,
                }}
              />
              <div className="relative z-10 w-32 h-32 rounded-3xl bg-gradient-to-tr from-cyan-500/25 to-indigo-500/35 border border-cyan-400/40 shadow-2xl shadow-cyan-500/30 backdrop-blur-2xl flex items-center justify-center">
                <svg
                  className="w-16 h-16 text-cyan-300 drop-shadow-[0_0_20px_rgba(34,211,238,0.7)]"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 00-9.78 2.096A4.001 4.001 0 003 15z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 11v6m0 0l-2-2m2 2l2-2"
                  />
                </svg>
                {/* Orbiting Sync Particle */}
                <div
                  className="absolute w-3.5 h-3.5 rounded-full bg-cyan-400 shadow-[0_0_12px_#38bdf8]"
                  style={{
                    top: "50%",
                    left: "50%",
                    transform: `rotate(${orbitAngle}deg) translate(80px) rotate(-${orbitAngle}deg)`,
                  }}
                />
              </div>
            </div>
          </KineticText>

          {/* Stacked Vertical Benefit Cards */}
          <div className="flex flex-col gap-4 w-full mt-6">
            <KineticText delay={175} exitFrame={435} initialY={30}>
              <div className="flex items-center gap-5 rounded-2xl border border-white/10 bg-slate-900/85 p-5 backdrop-blur-xl">
                <div className="w-14 h-14 rounded-2xl bg-cyan-500/10 border border-cyan-400/30 flex-shrink-0 flex items-center justify-center text-cyan-400">
                  <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-xl font-bold text-white mb-0.5">Instant Mirroring</h4>
                  <p className="text-base text-slate-300 leading-snug">
                    Sub-millisecond background broadcast on every edit.
                  </p>
                </div>
              </div>
            </KineticText>

            <KineticText delay={195} exitFrame={435} initialY={30}>
              <div className="flex items-center gap-5 rounded-2xl border border-white/10 bg-slate-900/85 p-5 backdrop-blur-xl">
                <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-400/30 flex-shrink-0 flex items-center justify-center text-indigo-400">
                  <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-xl font-bold text-white mb-0.5">Zero Data Loss</h4>
                  <p className="text-base text-slate-300 leading-snug">
                    Military-grade encrypted redundancy protects your work.
                  </p>
                </div>
              </div>
            </KineticText>

            <KineticText delay={215} exitFrame={435} initialY={30}>
              <div className="flex items-center gap-5 rounded-2xl border border-white/10 bg-slate-900/85 p-5 backdrop-blur-xl">
                <div className="w-14 h-14 rounded-2xl bg-purple-500/10 border border-purple-400/30 flex-shrink-0 flex items-center justify-center text-purple-400">
                  <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-xl font-bold text-white mb-0.5">Universal Cross-Sync</h4>
                  <p className="text-base text-slate-300 leading-snug">
                    Pick up on phone, tablet, and desktop without skipping a beat.
                  </p>
                </div>
              </div>
            </KineticText>
          </div>
        </div>
      )}
    </div>
  );
};
