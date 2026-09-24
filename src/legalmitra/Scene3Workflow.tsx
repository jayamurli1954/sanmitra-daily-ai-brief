import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { KineticText } from "../components/KineticText";

export const Scene3Workflow: React.FC = () => {
  const frame = useCurrentFrame();

  const workflowSteps = [
    { num: "01", label: "Client Matter" },
    { num: "02", label: "Research & Citations" },
    { num: "03", label: "Brief Summary" },
    { num: "04", label: "Matter Workspace" },
    { num: "05", label: "Deadline Tracking" },
    { num: "06", label: "Daily Brief" },
  ];

  const stepIdx = Math.max(
    0,
    Math.min(
      workflowSteps.length - 1,
      Math.floor(
        interpolate(frame, [15, 135], [0, workflowSteps.length], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      )
    )
  );

  return (
    <div className="absolute inset-0 flex items-center justify-center overflow-hidden px-14">
      {/* Background Glow */}
      <div className="absolute w-[900px] h-[550px] rounded-full bg-blue-600/10 blur-[180px] pointer-events-none" />

      {/* Part 1: Real AI Legal Research Outcome & Workflow Bar (frames 0 - 150) */}
      {frame < 155 && (
        <div className="flex flex-col items-center justify-center w-full max-w-6xl text-center">
          <KineticText delay={4} exitFrame={145}>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-amber-400/30 bg-[#0c1f36]/80 backdrop-blur-md mb-3">
              <span className="text-xs font-mono font-bold text-amber-300 uppercase tracking-wider">
                Practice Outcome #1 • Verifiable Case Law
              </span>
            </div>
          </KineticText>

          <KineticText delay={12} exitFrame={145} initialScale={0.92}>
            <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-2">
              Find Relevant Judgments <span className="text-amber-400">Faster.</span>
            </h2>
          </KineticText>

          {/* Sequential Large Animated Workflow Step Banner */}
          <KineticText delay={18} exitFrame={145} initialY={15}>
            <div className="flex items-center gap-4 mb-4 px-6 py-2.5 rounded-2xl bg-slate-950/95 border-2 border-amber-400/40 shadow-2xl backdrop-blur-xl">
              <span className="px-3 py-1 rounded-xl bg-amber-500/25 text-amber-300 font-mono text-sm font-black border border-amber-400/40 tracking-wider">
                STAGE {workflowSteps[stepIdx].num} OF 06
              </span>
              <span className="text-2xl font-mono font-black text-white tracking-wide">
                {workflowSteps[stepIdx].label}
              </span>
              <div className="flex items-center gap-2 ml-2">
                {workflowSteps.map((_, i) => (
                  <div
                    key={i}
                    className={`h-2.5 rounded-full transition-all duration-300 ${
                      i === stepIdx ? "w-8 bg-amber-400 shadow-md shadow-amber-400/50" : i < stepIdx ? "w-2.5 bg-amber-400/60" : "w-2.5 bg-slate-700"
                    }`}
                  />
                ))}
              </div>
            </div>
          </KineticText>

          {/* Zoomed-in Product UI Viewport: Focusing on Search Quality, Citations & Results */}
          <KineticText delay={28} exitFrame={145} initialY={25}>
            <div className="w-[960px] h-[370px] rounded-2xl overflow-hidden border-2 border-amber-400/60 shadow-2xl shadow-black/90 ring-1 ring-white/10 bg-slate-950 relative">
              <div
                className="w-full h-full relative"
                style={{
                  transformOrigin: "58% 85%",
                  transform: `scale(${interpolate(frame, [25, 80, 145], [1.5, 1.75, 1.85])})`,
                }}
              >
                <Img
                  src={staticFile("legalmitra/legalmitra-screen-research.png")}
                  className="w-full h-auto object-cover"
                />
              </div>

              {/* High-Visibility Callout Badges Overlaid for Immediate Mobile Readability */}
              <div className="absolute top-4 left-4 flex items-center gap-2.5 px-4 py-2 rounded-xl bg-slate-950/95 border border-amber-400/50 backdrop-blur-xl shadow-xl">
                <span className="text-amber-400 font-bold text-sm">🔍 Query:</span>
                <span className="text-white font-mono text-sm font-semibold">"BNSS Section 482 Quashing Precedents"</span>
              </div>

              <div className="absolute bottom-4 right-4 flex items-center gap-2.5 px-5 py-2 rounded-xl bg-slate-950/95 border border-emerald-400/50 backdrop-blur-xl shadow-xl">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-emerald-300 font-mono text-sm font-bold">14 High-Court &amp; SC Judgments Verified</span>
              </div>
            </div>
          </KineticText>
        </div>
      )}

      {/* Part 2: Practice Intelligence, Matters, Alerts & Confidentiality (frames 150 - 290) */}
      {frame >= 150 && (
        <div className="flex flex-col items-center justify-center w-full max-w-6xl text-center">
          <KineticText delay={155} exitFrame={275}>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-emerald-500/40 bg-emerald-950/60 backdrop-blur-md mb-3">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-mono font-bold text-emerald-300 uppercase tracking-wider">
                Practice Outcomes #2 &amp; #3 • Active Control
              </span>
            </div>
          </KineticText>

          <KineticText delay={165} exitFrame={275} initialScale={0.92}>
            <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-2">
              Never Miss A <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-300 to-yellow-500">Critical Deadline.</span>
            </h2>
            <p className="text-base text-slate-300 font-light mb-6">
              Complete matter workspace, proactive limitation alerts, and chamber confidentiality.
            </p>
          </KineticText>

          {/* 3 Outcome Cards */}
          <div className="grid grid-cols-3 gap-6 w-full max-w-5xl">
            {/* Matters */}
            <KineticText delay={180} exitFrame={275} initialY={25}>
              <div className="rounded-2xl border border-white/10 bg-slate-950/85 p-6 text-left backdrop-blur-xl h-full flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-400/30 flex items-center justify-center text-amber-400 mb-4">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                  <h4 className="text-lg font-bold text-white mb-1">Never Lose Track of a Matter</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Client briefs, case history, orders, and documents organized into unified matter records.
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] font-mono text-amber-400/90">
                  ✓ Unified Matter Workspace
                </div>
              </div>
            </KineticText>

            {/* Alerts */}
            <KineticText delay={195} exitFrame={275} initialY={25}>
              <div className="rounded-2xl border border-amber-400/40 bg-[#0d223f]/90 p-6 text-left backdrop-blur-xl shadow-xl ring-1 ring-amber-400/20 h-full flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-400/30 flex items-center justify-center text-emerald-400 mb-4">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h4 className="text-lg font-bold text-amber-300 mb-1">Never Miss a Deadline</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Statutory limitation alarms and morning cause-list briefs notify your team days in advance.
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-amber-500/20 text-[11px] font-mono text-emerald-400">
                  ✓ Proactive Limitation Watch
                </div>
              </div>
            </KineticText>

            {/* Privacy */}
            <KineticText delay={210} exitFrame={275} initialY={25}>
              <div className="rounded-2xl border border-white/10 bg-slate-950/85 p-6 text-left backdrop-blur-xl h-full flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-400/30 flex items-center justify-center text-indigo-400 mb-4">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <h4 className="text-lg font-bold text-white mb-1">Keep Information Secure</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Designed for confidential legal work. Client briefs are never used as public training data.
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] font-mono text-indigo-300">
                  ✓ Confidential Architecture
                </div>
              </div>
            </KineticText>
          </div>
        </div>
      )}
    </div>
  );
};
