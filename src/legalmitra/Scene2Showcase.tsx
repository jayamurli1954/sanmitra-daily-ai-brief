import React from "react";
import { Img, staticFile, useCurrentFrame } from "remotion";
import { KineticText } from "../components/KineticText";

export const Scene2Showcase: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <div className="absolute inset-0 flex items-center justify-center overflow-hidden px-14">
      {/* Background Gold Ambient Bloom */}
      <div className="absolute w-[950px] h-[550px] rounded-full bg-amber-500/10 blur-[170px] pointer-events-none" />

      {/* Part 1: Logo, Trust Layer & Traditional vs Unified Workspace (frames 0 - 110, approx 3.5s) */}
      {frame < 115 && (
        <div className="flex flex-col items-center justify-center max-w-5xl text-center">
          {/* Logo & Trust Layer */}
          <KineticText delay={3} exitFrame={108}>
            <div className="flex items-center gap-3 mb-2.5">
              <div className="w-13 h-13 rounded-2xl p-1 bg-gradient-to-tr from-amber-500/30 via-yellow-400/20 to-transparent border border-amber-400/40 shadow-xl flex items-center justify-center">
                <Img
                  src={staticFile("legalmitra/legalmitra-logo.png")}
                  className="w-12 h-12 object-contain filter drop-shadow-md rounded-xl"
                />
              </div>
              <span className="text-2xl font-black font-serif tracking-tight text-white">
                Legal<span className="text-amber-400">Mitra</span>
              </span>
            </div>
          </KineticText>

          <KineticText delay={10} exitFrame={108}>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-amber-400/30 bg-[#0d223f]/80 backdrop-blur-xl mb-3 shadow-lg">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              <span className="text-xs font-mono font-bold tracking-wider text-amber-300 uppercase">
                Designed For Indian Legal &amp; Compliance Practice
              </span>
            </div>
          </KineticText>

          <KineticText delay={16} exitFrame={108} initialScale={0.92}>
            <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight leading-tight mb-5">
              Beyond Fragmented{" "}
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-300 via-yellow-200 to-amber-500">
                Chamber Research.
              </span>
            </h2>
          </KineticText>

          {/* Side-by-Side Comparison: Traditional Workflows vs LegalMitra */}
          <div className="grid grid-cols-2 gap-7 w-full max-w-4xl text-left">
            {/* Left: Traditional Legal Research */}
            <KineticText delay={24} exitFrame={108} initialY={20}>
              <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5 backdrop-blur-xl shadow-lg">
                <div className="text-xs font-mono font-bold uppercase tracking-widest text-slate-400 mb-2.5 flex items-center justify-between">
                  <span>Traditional Workflows</span>
                  <span className="text-rose-400/80 font-normal">Fragmented</span>
                </div>
                <div className="space-y-2 text-slate-300 text-sm">
                  <div className="flex items-center gap-2.5">
                    <span className="text-rose-400 font-bold">✕</span>
                    <span>Scattered PDF judgments &amp; statute books</span>
                  </div>
                  <div className="flex items-center gap-2.5">
                    <span className="text-rose-400 font-bold">✕</span>
                    <span>Manual, error-prone BNS/IPC crosswalk</span>
                  </div>
                  <div className="flex items-center gap-2.5">
                    <span className="text-rose-400 font-bold">✕</span>
                    <span>Disconnected spreadsheets &amp; paper diaries</span>
                  </div>
                </div>
              </div>
            </KineticText>

            {/* Right: LegalMitra Unified Workspace */}
            <KineticText delay={34} exitFrame={108} initialY={20}>
              <div className="rounded-2xl border border-amber-400/50 bg-[#0d223f]/90 p-5 backdrop-blur-xl shadow-2xl ring-1 ring-amber-400/30">
                <div className="text-xs font-mono font-bold uppercase tracking-widest text-amber-300 mb-2.5 flex items-center justify-between">
                  <span>LegalMitra Workspace</span>
                  <span className="text-emerald-400 font-semibold">Unified</span>
                </div>
                <div className="space-y-2 text-white text-sm font-medium">
                  <div className="flex items-center gap-2.5">
                    <span className="text-emerald-400 font-bold">✓</span>
                    <span>Verified research &amp; citation audit trail</span>
                  </div>
                  <div className="flex items-center gap-2.5">
                    <span className="text-emerald-400 font-bold">✓</span>
                    <span>Instant BNS, BNSS &amp; BSA auto-crosswalk</span>
                  </div>
                  <div className="flex items-center gap-2.5">
                    <span className="text-emerald-400 font-bold">✓</span>
                    <span>Integrated matter records &amp; limitation watch</span>
                  </div>
                </div>
              </div>
            </KineticText>
          </div>
        </div>
      )}

      {/* Part 2: Visual BNS / BNSS / BSA Auto-Crosswalk & "One Workspace" Anchor (frames 110 - 310) */}
      {frame >= 110 && (
        <div className="flex flex-col items-center justify-center max-w-5xl text-center">
          {/* Unifying Anchor Banner */}
          <KineticText delay={115} exitFrame={295}>
            <div className="inline-flex items-center gap-3 px-6 py-2 rounded-full border-2 border-amber-400/50 bg-[#0e213b]/95 backdrop-blur-xl mb-3 shadow-xl">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping" />
              <span className="text-xs font-mono font-black tracking-widest text-amber-300 uppercase">
                INDIA'S NEW CRIMINAL LAWS • HERO STATUTORY CROSSWALK
              </span>
            </div>
          </KineticText>

          <KineticText delay={122} exitFrame={295} initialScale={0.92}>
            <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight leading-tight mb-2">
              Old Acts <span className="text-slate-400">➔</span>{" "}
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-300 via-yellow-200 to-amber-500">
                New Criminal Sanhitas
              </span>
            </h2>
            <p className="text-slate-200 text-base font-normal mb-5">
              Search by old or new sections — LegalMitra auto-maps both instantly with relevant judicial precedents.
            </p>
          </KineticText>

          {/* 3 High-Impact Hero Crosswalk Cards */}
          <div className="grid grid-cols-3 gap-6 w-full max-w-5xl mb-5">
            {/* Card 1: IPC -> BNS */}
            <KineticText delay={132} exitFrame={295} initialY={25}>
              <div className="rounded-2xl border-2 border-slate-700 bg-slate-950/90 p-5 backdrop-blur-xl shadow-2xl relative overflow-hidden">
                <div className="text-xs font-mono text-slate-400 uppercase tracking-widest font-semibold mb-1">Old Penal Code</div>
                <div className="text-2xl font-black text-slate-300">IPC (1860)</div>
                <div className="my-3 flex items-center justify-center">
                  <div className="px-4 py-1 rounded-full bg-amber-500/25 border border-amber-400/50 text-amber-300 text-xs font-mono font-bold shadow-md flex items-center gap-1.5">
                    <span>↓</span>
                    <span>AUTO-MAPPED</span>
                    <span>↓</span>
                  </div>
                </div>
                <div className="text-xs font-mono text-amber-400 uppercase tracking-widest font-bold mb-1">New Enactment</div>
                <div className="text-2xl font-black text-white">BNS 2023</div>
                <div className="text-[11px] font-mono text-slate-400 mt-1">Bharatiya Nyaya Sanhita</div>
              </div>
            </KineticText>

            {/* Card 2: CrPC -> BNSS (Center Hero with Gold Halo) */}
            <KineticText delay={142} exitFrame={295} initialY={25}>
              <div className="rounded-2xl border-2 border-amber-400 bg-[#0d223f]/95 p-5 backdrop-blur-xl shadow-2xl ring-2 ring-amber-400/40 relative overflow-hidden">
                <div className="absolute top-2 right-2 px-2 py-0.5 rounded-full bg-amber-400 text-black text-[9px] font-mono font-black">
                  PROCEDURE
                </div>
                <div className="text-xs font-mono text-slate-300 uppercase tracking-widest font-semibold mb-1">Old Procedure</div>
                <div className="text-2xl font-black text-slate-200">CrPC (1973)</div>
                <div className="my-3 flex items-center justify-center">
                  <div className="px-4 py-1 rounded-full bg-amber-400 text-black text-xs font-mono font-black shadow-lg flex items-center gap-1.5 animate-pulse">
                    <span>↓</span>
                    <span>INSTANT CROSSWALK</span>
                    <span>↓</span>
                  </div>
                </div>
                <div className="text-xs font-mono text-amber-300 uppercase tracking-widest font-black mb-1">New Procedure</div>
                <div className="text-2xl font-black text-amber-300">BNSS 2023</div>
                <div className="text-[11px] font-mono text-amber-200 mt-1 font-medium">Bhartiya Nagarik Suraksha</div>
              </div>
            </KineticText>

            {/* Card 3: Evidence Act -> BSA */}
            <KineticText delay={152} exitFrame={295} initialY={25}>
              <div className="rounded-2xl border-2 border-slate-700 bg-slate-950/90 p-5 backdrop-blur-xl shadow-2xl relative overflow-hidden">
                <div className="text-xs font-mono text-slate-400 uppercase tracking-widest font-semibold mb-1">Old Evidence Law</div>
                <div className="text-2xl font-black text-slate-300">IEA (1872)</div>
                <div className="my-3 flex items-center justify-center">
                  <div className="px-4 py-1 rounded-full bg-amber-500/25 border border-amber-400/50 text-amber-300 text-xs font-mono font-bold shadow-md flex items-center gap-1.5">
                    <span>↓</span>
                    <span>AUTO-MAPPED</span>
                    <span>↓</span>
                  </div>
                </div>
                <div className="text-xs font-mono text-amber-400 uppercase tracking-widest font-bold mb-1">New Evidence Law</div>
                <div className="text-2xl font-black text-white">BSA 2023</div>
                <div className="text-[11px] font-mono text-slate-400 mt-1">Bharatiya Sakshya Adhiniyam</div>
              </div>
            </KineticText>
          </div>

          {/* Compliant & Safe Proof Point Strip */}
          <KineticText delay={170} exitFrame={295} initialY={15}>
            <div className="flex items-center justify-center gap-6 px-8 py-2.5 rounded-xl border border-amber-400/30 bg-slate-950/90 backdrop-blur-md shadow-lg">
              <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 font-bold">
                <span>✓</span>
                <span>Dual-Statute Case Search</span>
              </div>
              <span className="w-1 h-1 rounded-full bg-slate-500" />
              <div className="flex items-center gap-2 text-xs font-mono text-amber-300 font-bold">
                <span>✓</span>
                <span>Extensive Citation Coverage</span>
              </div>
              <span className="w-1 h-1 rounded-full bg-slate-500" />
              <div className="flex items-center gap-2 text-xs font-mono text-white font-bold">
                <span>✓</span>
                <span>Source Citations Included</span>
              </div>
            </div>
          </KineticText>
        </div>
      )}
    </div>
  );
};
