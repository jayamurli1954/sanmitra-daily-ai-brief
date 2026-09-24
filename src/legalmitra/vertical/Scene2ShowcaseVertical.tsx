import React from "react";
import { Img, staticFile, useCurrentFrame } from "remotion";
import { KineticText } from "../../components/KineticText";

export const Scene2ShowcaseVertical: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    // Mobile Safe Area: pt-[250px] pb-[350px]
    <div className="absolute inset-0 flex flex-col items-center justify-center overflow-hidden px-10 pt-[250px] pb-[350px]">
      <div className="absolute w-[800px] h-[600px] rounded-full bg-amber-500/10 blur-[150px] pointer-events-none" />

      {/* Part 1: Logo, Trust Layer & Traditional vs Unified Workspace (frames 0 - 110) */}
      {frame < 115 && (
        <div className="flex flex-col items-center justify-center w-full max-w-[920px] text-center">
          <KineticText delay={3} exitFrame={108}>
            <div className="flex items-center gap-3 mb-3">
              <div className="w-14 h-14 rounded-2xl p-1 bg-gradient-to-tr from-amber-500/30 via-yellow-400/20 to-transparent border border-amber-400/40 shadow-xl flex items-center justify-center">
                <Img
                  src={staticFile("legalmitra/legalmitra-logo.png")}
                  className="w-12 h-12 object-contain rounded-xl"
                />
              </div>
              <span className="text-3xl font-black font-serif tracking-tight text-white">
                Legal<span className="text-amber-400">Mitra</span>
              </span>
            </div>
          </KineticText>

          <KineticText delay={10} exitFrame={108}>
            <div className="inline-flex items-center gap-2 px-5 py-2 rounded-full border border-amber-400/30 bg-[#0d223f]/80 backdrop-blur-xl mb-5">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              <span className="text-xs font-mono font-bold tracking-wider text-amber-300 uppercase">
                Designed For Indian Legal Practice
              </span>
            </div>
          </KineticText>

          <KineticText delay={16} exitFrame={108} initialScale={0.92}>
            <h2 className="text-4xl font-black text-white tracking-tight leading-tight mb-6">
              Beyond Fragmented <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-300 via-yellow-200 to-amber-500">
                Chamber Research.
              </span>
            </h2>
          </KineticText>

          {/* Vertical Comparison Stack */}
          <div className="flex flex-col gap-3.5 w-full">
            {/* Traditional Workflows */}
            <KineticText delay={24} exitFrame={108} initialY={15}>
              <div className="rounded-2xl border border-slate-800 bg-slate-950/85 p-4 text-left backdrop-blur-xl">
                <div className="text-xs font-mono font-bold uppercase tracking-widest text-slate-400 mb-1.5 flex items-center justify-between">
                  <span>Traditional Workflows</span>
                  <span className="text-rose-400/80">Fragmented</span>
                </div>
                <div className="space-y-1 text-slate-300 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-rose-400 font-bold">✕</span>
                    <span>Scattered PDFs &amp; manual BNS crosswalk</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-rose-400 font-bold">✕</span>
                    <span>Disconnected notes &amp; paper diaries</span>
                  </div>
                </div>
              </div>
            </KineticText>

            {/* LegalMitra */}
            <KineticText delay={34} exitFrame={108} initialY={15}>
              <div className="rounded-2xl border border-amber-400/50 bg-[#0d223f]/95 p-4 text-left backdrop-blur-xl shadow-xl ring-1 ring-amber-400/30">
                <div className="text-xs font-mono font-bold uppercase tracking-widest text-amber-300 mb-1.5 flex items-center justify-between">
                  <span>LegalMitra Workspace</span>
                  <span className="text-emerald-400 font-semibold">Unified</span>
                </div>
                <div className="space-y-1 text-white text-xs font-medium">
                  <div className="flex items-center gap-2">
                    <span className="text-emerald-400 font-bold">✓</span>
                    <span>Verified research &amp; instant BNS crosswalk</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-emerald-400 font-bold">✓</span>
                    <span>Complete matter records &amp; limitation watch</span>
                  </div>
                </div>
              </div>
            </KineticText>
          </div>
        </div>
      )}

      {/* Part 2: Visual BNS / BNSS / BSA Crosswalk & Anchor (frames 110 - 310) */}
      {frame >= 110 && (
        <div className="flex flex-col items-center justify-center w-full max-w-[920px] text-center">
          {/* Unifying Anchor Banner */}
          <KineticText delay={115} exitFrame={295}>
            <div className="inline-flex items-center gap-2 px-5 py-2 rounded-full border-2 border-amber-400/50 bg-[#0e213b]/95 backdrop-blur-xl mb-4 shadow-xl">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
              <span className="text-xs font-mono font-black tracking-widest text-amber-300 uppercase">
                NEW CRIMINAL LAWS • HERO CROSSWALK
              </span>
            </div>
          </KineticText>

          <KineticText delay={122} exitFrame={295} initialScale={0.92}>
            <h2 className="text-4xl font-black text-white tracking-tight leading-tight mb-2">
              Old Acts <span className="text-slate-400">➔</span> <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-300 via-yellow-200 to-amber-500">
                New Criminal Sanhitas
              </span>
            </h2>
            <p className="text-slate-200 text-xs font-normal mb-5 max-w-sm">
              Search by old or new sections — LegalMitra auto-maps both instantly with verified case law.
            </p>
          </KineticText>

          {/* Stacked High-Impact Vertical Hero Conversion Cards */}
          <div className="flex flex-col gap-3.5 w-full mb-5">
            {/* Row 1: IPC -> BNS */}
            <KineticText delay={132} exitFrame={295} initialY={15}>
              <div className="flex items-center justify-between px-5 py-4 rounded-2xl border-2 border-slate-700 bg-slate-950/90 backdrop-blur-xl shadow-xl">
                <div className="text-left">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Old Penal Code</div>
                  <div className="text-xl font-black text-slate-200 font-mono">IPC (1860)</div>
                </div>
                <div className="px-3 py-1 rounded-full bg-amber-500/25 border border-amber-400/50 text-amber-300 text-xs font-mono font-bold">
                  ➔ MAPPED ➔
                </div>
                <div className="text-right">
                  <div className="text-[10px] font-mono text-amber-400 uppercase font-bold">New Law</div>
                  <div className="text-xl font-black text-white font-mono">BNS 2023</div>
                </div>
              </div>
            </KineticText>

            {/* Row 2: CrPC -> BNSS (Hero Row with Gold Ring) */}
            <KineticText delay={142} exitFrame={295} initialY={15}>
              <div className="flex items-center justify-between px-5 py-4 rounded-2xl border-2 border-amber-400 bg-[#0d223f]/95 backdrop-blur-xl ring-2 ring-amber-400/40 shadow-2xl">
                <div className="text-left">
                  <div className="text-[10px] font-mono text-slate-300 uppercase">Old Procedure</div>
                  <div className="text-xl font-black text-slate-200 font-mono">CrPC (1973)</div>
                </div>
                <div className="px-3 py-1 rounded-full bg-amber-400 text-black text-xs font-mono font-black animate-pulse shadow-md">
                  ➔ CROSSWALK ➔
                </div>
                <div className="text-right">
                  <div className="text-[10px] font-mono text-amber-300 uppercase font-black">Procedure</div>
                  <div className="text-xl font-black text-amber-300 font-mono">BNSS 2023</div>
                </div>
              </div>
            </KineticText>

            {/* Row 3: Evidence Act -> BSA */}
            <KineticText delay={152} exitFrame={295} initialY={15}>
              <div className="flex items-center justify-between px-5 py-4 rounded-2xl border-2 border-slate-700 bg-slate-950/90 backdrop-blur-xl shadow-xl">
                <div className="text-left">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Old Evidence</div>
                  <div className="text-xl font-black text-slate-200 font-mono">IEA (1872)</div>
                </div>
                <div className="px-3 py-1 rounded-full bg-amber-500/25 border border-amber-400/50 text-amber-300 text-xs font-mono font-bold">
                  ➔ MAPPED ➔
                </div>
                <div className="text-right">
                  <div className="text-[10px] font-mono text-amber-400 uppercase font-bold">New Law</div>
                  <div className="text-xl font-black text-white font-mono">BSA 2023</div>
                </div>
              </div>
            </KineticText>
          </div>

          {/* Proof Point Pill */}
          <KineticText delay={170} exitFrame={295} initialY={15}>
            <div className="flex items-center justify-center gap-3 px-6 py-2 rounded-xl border border-amber-400/30 bg-slate-950/90 backdrop-blur-md shadow-md">
              <span className="text-xs font-mono text-emerald-400 font-bold">✓ Dual-Statute Citations</span>
              <span className="text-slate-500">•</span>
              <span className="text-xs font-mono text-amber-300 font-bold">✓ Supreme Court &amp; HC</span>
            </div>
          </KineticText>
        </div>
      )}
    </div>
  );
};
