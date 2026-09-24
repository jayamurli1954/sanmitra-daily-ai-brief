import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { KineticText } from "./KineticText";

export const Scene2Solution: React.FC = () => {
  const frame = useCurrentFrame();

  // Pulse animation for cloud sync rings
  const pulse = (frame % 40) / 40;
  const ringScale = interpolate(pulse, [0, 1], [1, 1.8]);
  const ringOpacity = interpolate(pulse, [0, 0.5, 1], [0.8, 0.3, 0]);

  // Orbit rotation
  const orbitAngle = (frame * 2.5) % 360;

  return (
    <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
      {/* Dynamic Cyan/Indigo Energy Glow behind the scene */}
      <div className="absolute w-[900px] h-[900px] rounded-full bg-cyan-500/15 blur-[160px] pointer-events-none" />

      {/* Part 1: Reveal & Headline (frames 0 - 150) */}
      {frame < 160 && (
        <div className="absolute inset-0 flex flex-col items-center justify-center px-8">
          <KineticText delay={5} exitFrame={145}>
            <div className="inline-flex items-center gap-2.5 px-5 py-2 rounded-full border border-cyan-400/30 bg-cyan-950/50 backdrop-blur-xl shadow-lg shadow-cyan-900/30 mb-6">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
              </span>
              <span className="text-xs font-mono font-bold tracking-widest text-cyan-300 uppercase">
                The Next Generation Workflow
              </span>
            </div>
          </KineticText>

          <KineticText delay={18} exitFrame={145} initialScale={0.88} damping={12} stiffness={120}>
            <h2 className="text-6xl md:text-8xl font-black text-center tracking-tight text-white max-w-5xl leading-none">
              NEVER HIT <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-300">
                SAVE AGAIN.
              </span>
            </h2>
          </KineticText>

          <KineticText delay={38} exitFrame={145}>
            <p className="mt-6 text-2xl md:text-3xl text-indigo-100 font-light text-center max-w-3xl leading-relaxed">
              Introducing <strong className="font-semibold text-white">Instant Cloud Syncing</strong>.
              <br />
              <span className="text-cyan-300/90 text-xl font-normal">Real-time background sync that never sleeps.</span>
            </p>
          </KineticText>
        </div>
      )}

      {/* Part 2: Cloud Sync Architecture & Visual Showcase (frames 140 - 450) */}
      {frame >= 140 && (
        <div className="absolute inset-0 flex flex-col items-center justify-center px-8">
          {/* Top Label */}
          <KineticText delay={145} exitFrame={435}>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-emerald-500/30 bg-emerald-950/50 backdrop-blur-md mb-8">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-mono font-semibold text-emerald-300 tracking-wider">
                LIVE REPLICATION ACTIVE • 0.01s LATENCY
              </span>
            </div>
          </KineticText>

          {/* Central Cloud Node Graphic */}
          <KineticText delay={155} exitFrame={435} initialScale={0.7} damping={13} stiffness={100}>
            <div className="relative flex items-center justify-center my-4">
              {/* Expanding Pulse Wave */}
              <div
                className="absolute w-44 h-44 rounded-full border border-cyan-400/40 pointer-events-none"
                style={{
                  transform: `scale(${ringScale})`,
                  opacity: ringOpacity,
                }}
              />

              {/* Cloud Icon Container */}
              <div className="relative z-10 w-36 h-36 rounded-3xl bg-gradient-to-tr from-cyan-500/20 to-indigo-500/30 border border-cyan-400/40 shadow-2xl shadow-cyan-500/30 backdrop-blur-2xl flex items-center justify-center">
                <svg
                  className="w-20 h-20 text-cyan-300 drop-shadow-[0_0_20px_rgba(34,211,238,0.6)]"
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
                  className="absolute w-4 h-4 rounded-full bg-cyan-400 shadow-[0_0_12px_#38bdf8]"
                  style={{
                    top: "50%",
                    left: "50%",
                    transform: `rotate(${orbitAngle}deg) translate(85px) rotate(-${orbitAngle}deg)`,
                  }}
                />
              </div>
            </div>
          </KineticText>

          {/* Key Feature Benefit Pillars */}
          <div className="grid grid-cols-3 gap-6 max-w-5xl mt-8">
            <KineticText delay={175} exitFrame={435} initialY={40}>
              <div className="rounded-2xl border border-white/10 bg-slate-900/80 p-6 backdrop-blur-xl hover:border-cyan-500/40 transition-colors">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-400/30 flex items-center justify-center text-cyan-400 mb-4">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h4 className="text-lg font-bold text-white mb-1">Instant Mirroring</h4>
                <p className="text-sm text-slate-300 leading-relaxed">
                  Every keystroke and cursor stroke is broadcast to the cloud in sub-milliseconds.
                </p>
              </div>
            </KineticText>

            <KineticText delay={195} exitFrame={435} initialY={40}>
              <div className="rounded-2xl border border-white/10 bg-slate-900/80 p-6 backdrop-blur-xl hover:border-cyan-500/40 transition-colors">
                <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-400/30 flex items-center justify-center text-indigo-400 mb-4">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h4 className="text-lg font-bold text-white mb-1">Zero Data Loss</h4>
                <p className="text-sm text-slate-300 leading-relaxed">
                  Decentralized redundancy ensures your files survive crashes, outages, and restarts.
                </p>
              </div>
            </KineticText>

            <KineticText delay={215} exitFrame={435} initialY={40}>
              <div className="rounded-2xl border border-white/10 bg-slate-900/80 p-6 backdrop-blur-xl hover:border-cyan-500/40 transition-colors">
                <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-400/30 flex items-center justify-center text-purple-400 mb-4">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <h4 className="text-lg font-bold text-white mb-1">Universal Sync</h4>
                <p className="text-sm text-slate-300 leading-relaxed">
                  Pick up on your phone exactly where you left off on your desktop instantly.
                </p>
              </div>
            </KineticText>
          </div>
        </div>
      )}
    </div>
  );
};
