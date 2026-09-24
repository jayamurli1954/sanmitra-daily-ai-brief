import React from "react";
import { Audio, Img, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import { KineticText } from "../components/KineticText";
import { LegalBackground } from "./LegalBackground";

export const LegalMitraWebsiteHero: React.FC = () => {
  const frame = useCurrentFrame();
  const sheen = interpolate((frame % 60) / 60, [0, 1], [-100, 220]);

  return (
    <div className="relative w-full h-full bg-[#030712] overflow-hidden select-none font-sans text-white">
      {/* Dynamic Chamber Background */}
      <LegalBackground />

      {/* Audio Track with Smooth Fade Out at 15s */}
      <Audio
        src={staticFile("audio/legalmitra_score.wav")}
        volume={(f) => {
          if (f < 15) return interpolate(f, [0, 15], [0, 0.7]);
          if (f > 420) return interpolate(f, [420, 450], [0.7, 0]);
          return 0.7;
        }}
      />

      {/* Beat 1 (0–3s / frames 0 - 90): Problem Hook */}
      <Sequence durationInFrames={90} name="Beat 1 - Hook">
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-14">
          <KineticText delay={4} exitFrame={82}>
            <div className="flex items-center gap-3 mb-3">
              <div className="w-14 h-14 rounded-2xl p-1 bg-gradient-to-tr from-amber-400 to-yellow-600 shadow-xl flex items-center justify-center">
                <Img
                  src={staticFile("legalmitra/legalmitra-logo.png")}
                  className="w-full h-full object-contain rounded-xl"
                />
              </div>
              <span className="text-3xl font-black font-serif tracking-tight text-white">
                Legal<span className="text-amber-400">Mitra</span>
              </span>
            </div>
          </KineticText>

          <KineticText delay={10} exitFrame={82}>
            <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full border border-amber-400/30 bg-[#0d223f]/80 backdrop-blur-xl mb-3">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              <span className="text-xs font-mono font-bold tracking-wider text-amber-300 uppercase">
                Designed For Indian Legal Practice
              </span>
            </div>
          </KineticText>

          <KineticText delay={16} exitFrame={82} initialScale={0.92}>
            <h1 className="text-5xl md:text-6xl font-black text-white tracking-tight leading-tight">
              RESEARCH TAKES HOURS. <br />
              <span className="text-rose-400">DEADLINES CAN'T WAIT.</span>
            </h1>
          </KineticText>
        </div>
      </Sequence>

      {/* Beat 2 (3–7s / frames 90 - 210): Real Search Interface */}
      <Sequence from={90} durationInFrames={120} name="Beat 2 - Research UI">
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-14">
          <KineticText delay={4} exitFrame={112}>
            <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full border border-emerald-500/40 bg-[#0c1f36]/80 backdrop-blur-md mb-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-mono font-bold text-emerald-300 uppercase tracking-wider">
                Grounded Research • BNS &amp; BNSS Crosswalk
              </span>
            </div>
          </KineticText>

          <KineticText delay={10} exitFrame={112} initialScale={0.94}>
            <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-3">
              Find Relevant Judgments <span className="text-amber-400">Faster.</span>
            </h2>
          </KineticText>

          {/* Screenshot in Hero Frame */}
          <KineticText delay={16} exitFrame={112} initialY={25}>
            <div className="w-[820px] rounded-2xl overflow-hidden border border-amber-400/40 shadow-2xl shadow-black/80 ring-1 ring-white/10 bg-slate-950">
              <Img
                src={staticFile("legalmitra/legalmitra-screen-research.png")}
                className="w-full h-auto object-cover"
              />
            </div>
          </KineticText>
        </div>
      </Sequence>

      {/* Beat 3 (7–11s / frames 210 - 330): Limitation Deadline Alert */}
      <Sequence from={210} durationInFrames={120} name="Beat 3 - Limitation Alert">
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-14">
          <KineticText delay={4} exitFrame={112}>
            <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full border border-rose-500/40 bg-rose-950/60 backdrop-blur-md mb-3">
              <span className="w-2 h-2 rounded-full bg-rose-400 animate-pulse" />
              <span className="text-xs font-mono font-bold text-rose-300 uppercase tracking-wider">
                Proactive Limitation Watch
              </span>
            </div>
          </KineticText>

          <KineticText delay={10} exitFrame={112} initialScale={0.94}>
            <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-6">
              Never Miss A <span className="text-amber-400">Critical Deadline.</span>
            </h2>
          </KineticText>

          {/* Limitation Alert Card & Practice Workflow */}
          <KineticText delay={18} exitFrame={112} initialY={20}>
            <div className="w-[720px] p-6 rounded-2xl bg-[#0d223f]/90 border border-amber-400/40 backdrop-blur-xl shadow-2xl flex items-center justify-between">
              <div className="flex items-center gap-4 text-left">
                <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-400/30 flex items-center justify-center text-amber-400">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <div className="text-xs font-mono text-slate-400 uppercase tracking-wider">Limitation Alert • High Court Appeal</div>
                  <div className="text-xl font-bold text-white">Commercial Appeal #482/2026</div>
                </div>
              </div>
              <div className="px-4 py-2 rounded-xl bg-rose-500/20 border border-rose-500/40 text-rose-300 font-mono font-bold text-sm">
                EXPIRES IN 48 HOURS
              </div>
            </div>
          </KineticText>
        </div>
      </Sequence>

      {/* Beat 4 (11–15s / frames 330 - 450): Conversion CTA */}
      <Sequence from={330} durationInFrames={120} name="Beat 4 - Conversion CTA">
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-14">
          <KineticText delay={4}>
            <div className="flex items-center gap-3 mb-3">
              <div className="w-14 h-14 rounded-2xl p-1 bg-gradient-to-tr from-amber-400 to-yellow-600 shadow-xl flex items-center justify-center">
                <Img
                  src={staticFile("legalmitra/legalmitra-logo.png")}
                  className="w-full h-full object-contain rounded-xl"
                />
              </div>
              <span className="text-3xl font-black font-serif tracking-tight text-white">
                Legal<span className="text-amber-400">Mitra</span>
              </span>
            </div>
          </KineticText>

          <KineticText delay={10} initialScale={0.92}>
            <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight leading-tight mb-2">
              Research Smarter. Manage Better. <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-300 via-yellow-200 to-amber-500">
                Practice Confidently.
              </span>
            </h2>
            <p className="text-lg text-slate-300 font-light mb-6">
              One Workspace for Legal Research, Matters &amp; Compliance
            </p>
          </KineticText>

          {/* Primary CTA Button */}
          <KineticText delay={18} initialScale={0.88}>
            <div className="relative group inline-block">
              <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-amber-500 via-yellow-400 to-amber-600 opacity-75 blur-xl group-hover:opacity-100 transition duration-500 animate-pulse" />
              <div className="relative px-12 py-4 rounded-2xl bg-gradient-to-r from-amber-500 via-yellow-500 to-amber-600 font-extrabold text-[#050b14] text-xl tracking-wider shadow-2xl flex items-center gap-3 overflow-hidden border border-white/30">
                <div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent skew-x-12 pointer-events-none"
                  style={{ transform: `translateX(${sheen}%)` }}
                />
                <span>START FREE TODAY</span>
                <span className="font-bold">➔</span>
              </div>
            </div>
          </KineticText>

          {/* Contact Details */}
          <KineticText delay={26} initialY={15}>
            <div className="mt-5 flex items-center gap-6 px-8 py-2 rounded-xl bg-slate-950/90 border border-amber-400/30 backdrop-blur-xl">
              <span className="text-base font-mono font-bold text-amber-300">
                legalmitra.sanmitratech.in
              </span>
              <span className="w-px h-4 bg-white/20" />
              <span className="text-sm font-mono text-emerald-400 font-semibold">
                WhatsApp: +91 7904942915
              </span>
              <span className="w-px h-4 bg-white/20" />
              <span className="text-xs font-mono text-slate-400">
                No Credit Card Required
              </span>
            </div>
          </KineticText>
        </div>
      </Sequence>
    </div>
  );
};
