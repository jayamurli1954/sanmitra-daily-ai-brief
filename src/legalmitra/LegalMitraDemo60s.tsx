import React from "react";
import { Audio, Img, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import { KineticText } from "../components/KineticText";
import { LegalBackground } from "./LegalBackground";

export const LegalMitraDemo60s: React.FC = () => {
  const frame = useCurrentFrame();
  const sheen = interpolate((frame % 60) / 60, [0, 1], [-100, 220]);

  return (
    <div className="relative w-full h-full bg-[#030712] overflow-hidden select-none font-sans text-white">
      <LegalBackground />

      {/* Background Score with Smooth Fade Out at 60s */}
      <Audio
        src={staticFile("audio/legalmitra_score.wav")}
        volume={(f) => {
          if (f < 30) return interpolate(f, [0, 30], [0, 0.65]);
          if (f > 1750) return interpolate(f, [1750, 1800], [0.65, 0]);
          return 0.65;
        }}
      />

      {/* Top Persistent Brand Nav */}
      <div className="absolute top-8 left-14 right-14 z-50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl p-1 bg-gradient-to-tr from-amber-400 to-yellow-600 flex items-center justify-center">
            <Img src={staticFile("legalmitra/legalmitra-logo.png")} className="w-8 h-8 object-contain rounded-lg" />
          </div>
          <span className="text-xl font-bold font-serif text-white">
            Legal<span className="text-amber-400">Mitra</span>
          </span>
        </div>
        <div className="flex items-center gap-4">
          <div className="px-3.5 py-1 rounded-full border border-amber-400/30 bg-[#0d223f]/80 text-xs font-mono text-amber-300">
            PRACTICE DEMO • 60 SECONDS
          </div>
        </div>
      </div>

      {/* Beat 1 (0-10s / frames 0-300): The Chamber Reality & Fragmented Research */}
      <Sequence durationInFrames={300} name="Chamber Bottleneck">
        {/* Advocate Chamber Photo Background */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            transform: `scale(${interpolate(frame, [0, 300], [1.0, 1.06])})`,
            opacity: interpolate(frame, [0, 25, 275, 300], [0, 0.42, 0.42, 0]),
          }}
        >
          <Img
            src={staticFile("legalmitra/advocate-researcher.jpg")}
            className="w-full h-full object-cover filter brightness-90 contrast-110"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#030712] via-[#030712]/75 to-[#030712]/85" />
        </div>

        <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-14">
          <KineticText delay={8} exitFrame={285}>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-amber-400/30 bg-[#0d223f]/80 mb-4">
              <span className="text-xs font-mono font-bold text-amber-300 uppercase tracking-wider">
                The Advocate Chamber Reality
              </span>
            </div>
          </KineticText>

          <KineticText delay={16} exitFrame={285} initialScale={0.92}>
            <h1 className="text-5xl md:text-6xl font-black text-white tracking-tight leading-tight mb-4">
              Legal Research Takes Hours. <br />
              <span className="text-rose-400">Statutory Deadlines Can't Wait.</span>
            </h1>
          </KineticText>

          <KineticText delay={26} exitFrame={285}>
            <p className="text-xl text-slate-300 font-light max-w-2xl mb-8">
              Navigating India's new criminal laws with traditional fragmented tools creates bottlenecks across research, limitation dates, and client records.
            </p>
          </KineticText>

          {/* Side-by-Side Comparison */}
          <div className="grid grid-cols-2 gap-8 w-full max-w-3xl text-left">
            <KineticText delay={36} exitFrame={285} initialY={20}>
              <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/80">
                <div className="text-xs font-mono font-bold text-slate-400 uppercase mb-2">Traditional Research</div>
                <div className="text-sm text-slate-300 space-y-1">
                  <div>✕ Scattered PDF judgments</div>
                  <div>✕ Manual IPC ➔ BNS crosswalk</div>
                  <div>✕ Disconnected matter notes</div>
                </div>
              </div>
            </KineticText>

            <KineticText delay={46} exitFrame={285} initialY={20}>
              <div className="p-4 rounded-xl border border-amber-400/40 bg-[#0d223f]/90 shadow-xl">
                <div className="text-xs font-mono font-bold text-amber-300 uppercase mb-2">LegalMitra Workspace</div>
                <div className="text-sm text-white space-y-1">
                  <div>✓ Verified citations &amp; audit trails</div>
                  <div>✓ Instant BNS / BNSS / BSA mapping</div>
                  <div>✓ Unified matter &amp; limitation watch</div>
                </div>
              </div>
            </KineticText>
          </div>
        </div>
      </Sequence>

      {/* Beat 2 (10-25s / frames 300-750): Grounded Research & BNS Crosswalk */}
      <Sequence from={300} durationInFrames={450} name="Grounded Research Demo">
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-14">
          <KineticText delay={6} exitFrame={435}>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-emerald-500/40 bg-[#0c1f36]/80 mb-3">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-mono font-bold text-emerald-300 uppercase tracking-wider">
                Module 01 • Grounded Research &amp; BNS Crosswalk
              </span>
            </div>
          </KineticText>

          <KineticText delay={14} exitFrame={435} initialScale={0.94}>
            <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-2">
              Find Relevant Judgments <span className="text-amber-400">In Minutes.</span>
            </h2>
            <p className="text-slate-300 text-sm font-light mb-4">
              Verified bare acts, instant statutory crosswalk, and high-confidence citations.
            </p>
          </KineticText>

          {/* Research Screenshot */}
          <KineticText delay={24} exitFrame={435} initialY={25}>
            <div className="w-[840px] rounded-2xl overflow-hidden border border-amber-400/40 shadow-2xl bg-slate-950">
              <Img src={staticFile("legalmitra/legalmitra-screen-research.png")} className="w-full h-auto object-cover" />
            </div>
          </KineticText>
        </div>
      </Sequence>

      {/* Beat 3 (25-40s / frames 750-1200): Compliance & Limitation Tracker */}
      <Sequence from={750} durationInFrames={450} name="Compliance Tracker Demo">
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-14">
          <KineticText delay={6} exitFrame={435}>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-amber-400/30 bg-[#0c1f36]/80 mb-3">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
              <span className="text-xs font-mono font-bold text-amber-300 uppercase tracking-wider">
                Module 02 • Proactive Limitation &amp; Compliance Tracker
              </span>
            </div>
          </KineticText>

          <KineticText delay={14} exitFrame={435} initialScale={0.94}>
            <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-2">
              Never Miss A <span className="text-amber-400">Critical Court Deadline.</span>
            </h2>
            <p className="text-slate-300 text-sm font-light mb-4">
              Automated statutory limitation watches and morning cause-list alerts for your team.
            </p>
          </KineticText>

          {/* Tracker Screenshot */}
          <KineticText delay={24} exitFrame={435} initialY={25}>
            <div className="w-[840px] rounded-2xl overflow-hidden border border-amber-400/40 shadow-2xl bg-slate-950">
              <Img src={staticFile("legalmitra/legalmitra-screen-tracker.png")} className="w-full h-auto object-cover" />
            </div>
          </KineticText>
        </div>
      </Sequence>

      {/* Beat 4 (40-52s / frames 1200-1560): Legal Drafting Templates & Confidentiality */}
      <Sequence from={1200} durationInFrames={360} name="Drafting Templates Demo">
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-14">
          <KineticText delay={6} exitFrame={345}>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-indigo-400/30 bg-[#0c1f36]/80 mb-3">
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
              <span className="text-xs font-mono font-bold text-indigo-300 uppercase tracking-wider">
                Module 03 • Standardized Legal Drafting &amp; Confidentiality
              </span>
            </div>
          </KineticText>

          <KineticText delay={14} exitFrame={345} initialScale={0.94}>
            <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-2">
              Draft Confidently With <span className="text-amber-400">Vetted Templates.</span>
            </h2>
            <p className="text-slate-300 text-sm font-light mb-4">
              Bail applications, quashing petitions, and notices. Designed for confidential legal work.
            </p>
          </KineticText>

          {/* Templates Screenshot */}
          <KineticText delay={24} exitFrame={345} initialY={25}>
            <div className="w-[840px] rounded-2xl overflow-hidden border border-amber-400/40 shadow-2xl bg-slate-950">
              <Img src={staticFile("legalmitra/legalmitra-screen-templates.png")} className="w-full h-auto object-cover" />
            </div>
          </KineticText>
        </div>
      </Sequence>

      {/* Beat 5 (52-60s / frames 1560-1800): Unified Workspace & Conversion Lockup */}
      <Sequence from={1560} durationInFrames={240} name="Conversion CTA">
        {/* Collaborative Advocates Conference Photo Background */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            transform: `scale(${interpolate(frame - 1560, [0, 240], [1.0, 1.05])})`,
            opacity: interpolate(frame - 1560, [0, 25], [0, 0.38]),
          }}
        >
          <Img
            src={staticFile("legalmitra/advocates-team-conference.jpg")}
            className="w-full h-full object-cover filter brightness-85 contrast-110"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#030712] via-[#030712]/80 to-[#030712]/90" />
        </div>

        <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-14">
          <KineticText delay={6}>
            <div className="inline-flex items-center gap-3 px-6 py-2 rounded-full border border-amber-400/40 bg-[#0e213b]/90 backdrop-blur-xl mb-4">
              <span className="text-sm font-mono font-bold tracking-widest text-amber-300 uppercase">
                One Search • One Matter Record • One Workspace
              </span>
            </div>
          </KineticText>

          <KineticText delay={14} initialScale={0.92}>
            <h2 className="text-5xl font-black text-white tracking-tight leading-tight mb-3">
              Research Smarter. Manage Better. <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-300 via-yellow-200 to-amber-500">
                Practice Confidently.
              </span>
            </h2>
            <p className="text-xl text-slate-300 font-light mb-8">
              Transform your advocate chamber, law firm, or corporate legal department today.
            </p>
          </KineticText>

          {/* CTA Button */}
          <KineticText delay={24} initialScale={0.88}>
            <div className="relative group inline-block">
              <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-amber-500 via-yellow-400 to-amber-600 opacity-75 blur-xl group-hover:opacity-100 transition duration-500 animate-pulse" />
              <div className="relative px-12 py-5 rounded-2xl bg-gradient-to-r from-amber-500 via-yellow-500 to-amber-600 font-extrabold text-[#050b14] text-2xl tracking-wider shadow-2xl flex items-center gap-4 overflow-hidden border border-white/30">
                <div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent skew-x-12 pointer-events-none"
                  style={{ transform: `translateX(${sheen}%)` }}
                />
                <span>START FREE TODAY</span>
                <span className="font-bold">➔</span>
              </div>
            </div>
          </KineticText>

          {/* Contact Bar */}
          <KineticText delay={34} initialY={15}>
            <div className="mt-6 flex items-center gap-8 px-8 py-3 rounded-2xl bg-slate-950/90 border border-amber-400/30 backdrop-blur-xl shadow-xl">
              <span className="text-lg font-mono font-bold text-amber-300">
                legalmitra.sanmitratech.in
              </span>
              <span className="w-px h-5 bg-white/20" />
              <span className="text-base font-mono text-emerald-400 font-semibold">
                WhatsApp: +91 7904942915
              </span>
              <span className="w-px h-5 bg-white/20" />
              <span className="text-xs font-mono text-slate-400">
                No Credit Card Required • Book Private Chamber Demo
              </span>
            </div>
          </KineticText>
        </div>
      </Sequence>
    </div>
  );
};
