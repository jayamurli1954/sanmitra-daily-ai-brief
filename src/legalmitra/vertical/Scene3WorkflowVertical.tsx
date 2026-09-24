import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { KineticText } from "../../components/KineticText";

export const Scene3WorkflowVertical: React.FC = () => {
  const frame = useCurrentFrame();

  const workflowSteps = [
    { num: "01", label: "Client Matter" },
    { num: "02", label: "Research & Citations" },
    { num: "03", label: "Brief Summary" },
    { num: "04", label: "Matter Workspace" },
    { num: "05", label: "Deadline Tracking" },
    { num: "06", label: "Daily Brief" },
  ];

  const currentStepIdx = Math.max(
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

  const currentIdxSafe = (curr: number) => curr;

  return (
    // Mobile Safe Area: pt-[250px] pb-[350px]
    <div className="absolute inset-0 flex flex-col items-center justify-center overflow-hidden px-10 pt-[250px] pb-[350px]">
      <div className="absolute w-[800px] h-[600px] rounded-full bg-blue-600/10 blur-[160px] pointer-events-none" />

      {/* Part 1: Grounded Research Screen (frames 0 - 150) */}
      {frame < 155 && (
        <div className="flex flex-col items-center justify-center w-full max-w-[920px] text-center">
          <KineticText delay={4} exitFrame={145}>
            <div className="inline-flex items-center gap-2 px-5 py-2 rounded-full border border-amber-400/30 bg-[#0c1f36]/85 backdrop-blur-md mb-3">
              <span className="text-xs font-mono font-bold text-amber-300 uppercase tracking-wider">
                Practice Outcome #1 • Verifiable Case Law
              </span>
            </div>
          </KineticText>

          <KineticText delay={12} exitFrame={145} initialScale={0.92}>
            <h2 className="text-5xl font-black text-white tracking-tight leading-tight mb-3">
              Find Relevant Judgments <br />
              <span className="text-amber-400">Faster.</span>
            </h2>
          </KineticText>

          {/* Mobile Large Animated Sequential Stage Indicator */}
          <KineticText delay={18} exitFrame={145}>
            <div className="flex items-center gap-3 px-5 py-2 rounded-xl bg-slate-950/90 border border-amber-400/40 mb-4 shadow-xl">
              <span className="px-2.5 py-0.5 rounded-lg bg-amber-500/25 text-amber-300 font-mono text-xs font-black border border-amber-400/40">
                STAGE {workflowSteps[currentStepIdx].num}/06
              </span>
              <span className="text-base font-mono font-bold text-white">
                {workflowSteps[currentStepIdx].label}
              </span>
              <div className="flex items-center gap-1.5 ml-1">
                {workflowSteps.map((_, i) => (
                  <div
                    key={i}
                    className={`h-2 rounded-full transition-all duration-300 ${
                      i === currentStepIdx ? "w-6 bg-amber-400" : i < currentIdxSafe(currentStepIdx) ? "w-1.5 bg-amber-400/50" : "w-1.5 bg-slate-700"
                    }`}
                  />
                ))}
              </div>
            </div>
          </KineticText>

          {/* Zoomed-in Screenshot in Mobile Frame */}
          <KineticText delay={28} exitFrame={145} initialY={25}>
            <div className="w-full h-[400px] rounded-2xl overflow-hidden border-2 border-amber-400/50 shadow-2xl shadow-black/80 ring-1 ring-white/10 bg-slate-950 relative">
              <div
                className="w-full h-full relative"
                style={{
                  transformOrigin: "56% 56%",
                  transform: `scale(${interpolate(frame, [25, 80, 145], [1.6, 1.9, 2.0])})`,
                }}
              >
                <Img
                  src={staticFile("legalmitra/legalmitra-screen-research.png")}
                  className="w-full h-auto object-cover"
                />
              </div>

              {/* Mobile Callout Badges */}
              <div className="absolute top-3 left-3 right-3 flex items-center justify-between px-3 py-1.5 rounded-lg bg-slate-950/95 border border-amber-400/40 backdrop-blur-xl">
                <span className="text-amber-400 font-bold text-xs">🔍 BNSS 482 Precedents</span>
                <span className="text-emerald-300 font-mono text-xs font-bold">14 Judgments</span>
              </div>
            </div>
          </KineticText>
        </div>
      )}

      {/* Part 2: Limitation & Privacy Outcomes (frames 150 - 290) */}
      {frame >= 150 && (
        <div className="flex flex-col items-center justify-center w-full max-w-[920px] text-center">
          <KineticText delay={155} exitFrame={275}>
            <div className="inline-flex items-center gap-2 px-5 py-2 rounded-full border border-emerald-500/40 bg-emerald-950/60 backdrop-blur-md mb-4">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-mono font-bold text-emerald-300 uppercase tracking-wider">
                Practice Outcomes #2 &amp; #3 • Active Control
              </span>
            </div>
          </KineticText>

          <KineticText delay={165} exitFrame={275} initialScale={0.92}>
            <h2 className="text-5xl font-black text-white tracking-tight leading-tight mb-6">
              Never Miss A <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-300 to-yellow-500">
                Critical Deadline.
              </span>
            </h2>
          </KineticText>

          {/* Stacked Outcome Cards */}
          <div className="flex flex-col gap-3.5 w-full text-left">
            <KineticText delay={180} exitFrame={275} initialY={20}>
              <div className="flex items-center gap-4 rounded-2xl border border-white/10 bg-slate-950/90 p-4 backdrop-blur-xl">
                <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-400/30 flex items-center justify-center text-amber-400 flex-shrink-0">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-base font-bold text-white mb-0.5">Never Lose Track of a Matter</h4>
                  <p className="text-xs text-slate-300">Client briefs and case history in unified records.</p>
                </div>
              </div>
            </KineticText>

            <KineticText delay={195} exitFrame={275} initialY={20}>
              <div className="flex items-center gap-4 rounded-2xl border border-amber-400/50 bg-[#0d223f]/95 p-4 backdrop-blur-xl shadow-xl ring-1 ring-amber-400/20">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-400/30 flex items-center justify-center text-emerald-400 flex-shrink-0">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-base font-bold text-amber-300 mb-0.5">Never Miss a Deadline</h4>
                  <p className="text-xs text-slate-300">Proactive limitation watches and morning briefs.</p>
                </div>
              </div>
            </KineticText>

            <KineticText delay={210} exitFrame={275} initialY={20}>
              <div className="flex items-center gap-4 rounded-2xl border border-white/10 bg-slate-950/90 p-4 backdrop-blur-xl">
                <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-400/30 flex items-center justify-center text-indigo-400 flex-shrink-0">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-base font-bold text-white mb-0.5">Keep Information Secure</h4>
                  <p className="text-xs text-slate-300">Designed for confidential legal work.</p>
                </div>
              </div>
            </KineticText>
          </div>
        </div>
      )}
    </div>
  );
};
