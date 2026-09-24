import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { KineticText } from "../../components/KineticText";

export const Scene4ContactCTAVertical: React.FC = () => {
  const frame = useCurrentFrame();

  const sheen = interpolate((frame % 80) / 80, [0, 1], [-100, 220]);

  return (
    // Mobile Safe Area: pt-[250px] pb-[350px]
    <div className="absolute inset-0 flex flex-col items-center justify-center overflow-hidden px-10 pt-[250px] pb-[350px]">
      {/* Confident Vertical Advocates Background - Brightened & calibrated */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          transform: `scale(${interpolate(frame, [0, 330], [1.0, 1.05])})`,
          opacity: interpolate(frame, [0, 25], [0, 0.45]),
        }}
      >
        <Img
          src={staticFile("legalmitra/advocates-vertical-team.jpg")}
          className="w-full h-full object-cover filter brightness-105 contrast-105"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#030712]/95 via-[#030712]/55 to-[#030712]/65" />
      </div>

      <div className="absolute w-[850px] h-[650px] rounded-full bg-amber-400/20 blur-[150px] pointer-events-none" />

      <div className="flex flex-col items-center justify-center w-full max-w-[920px] text-center">
        {/* Official Brand Logo */}
        <KineticText delay={5}>
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-16 h-16 rounded-2xl p-1 bg-gradient-to-tr from-amber-300 via-yellow-400 to-amber-500 shadow-xl flex items-center justify-center ring-2 ring-amber-300/50">
              <Img
                src={staticFile("legalmitra/legalmitra-logo.png")}
                className="w-14 h-14 object-contain rounded-xl"
              />
            </div>
            <span className="text-4xl font-black font-serif tracking-tight text-white drop-shadow-md">
              Legal<span className="text-amber-400">Mitra</span>
            </span>
          </div>
        </KineticText>

        {/* Refined Final Tagline */}
        <KineticText delay={15} initialScale={0.88} damping={12} stiffness={120}>
          <h2 className="text-5xl md:text-6xl font-black text-white tracking-tight leading-tight drop-shadow-lg">
            Research Smarter. <br />
            Manage Better. <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-300 via-yellow-200 to-amber-400">
              Practice Confidently.
            </span>
          </h2>
        </KineticText>

        <KineticText delay={28}>
          <p className="mt-2 text-lg text-slate-200 font-normal max-w-md drop-shadow">
            One Workspace for Legal Research, Matters &amp; Compliance
          </p>
        </KineticText>

        {/* Primary Action Button */}
        <KineticText delay={42} initialScale={0.85} damping={11} stiffness={130}>
          <div className="mt-6 w-full max-w-md relative group">
            <div className="absolute -inset-1.5 rounded-3xl bg-gradient-to-r from-amber-400 via-yellow-300 to-amber-500 opacity-90 blur-xl group-hover:opacity-100 transition duration-500 animate-pulse" />
            <div className="relative w-full py-4 rounded-3xl bg-gradient-to-r from-amber-400 via-yellow-400 to-amber-500 font-black text-[#050b14] text-2xl tracking-wider shadow-2xl flex items-center justify-center gap-4 overflow-hidden border border-white/40">
              <div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/50 to-transparent skew-x-12 pointer-events-none"
                style={{ transform: `translateX(${sheen}%)` }}
              />
              <svg className="w-8 h-8 text-[#050b14]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.8} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
              <span>START FREE TODAY</span>
            </div>
          </div>
        </KineticText>

        {/* Prominent Website URL & WhatsApp Directly Under CTA */}
        <KineticText delay={58} initialY={25}>
          <div className="mt-4 flex flex-col items-center gap-2.5 w-full max-w-md">
            {/* Ultra-Prominent Website Display */}
            <div className="w-full py-3 px-4 rounded-2xl bg-black/90 border-2 border-amber-400 shadow-2xl shadow-amber-400/30 backdrop-blur-2xl flex items-center justify-center gap-2.5">
              <svg className="w-6 h-6 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
              </svg>
              <span className="text-2xl md:text-3xl font-black font-mono text-amber-300 tracking-wide">
                legalmitra.sanmitratech.in
              </span>
            </div>

            {/* Direct WhatsApp Line */}
            <div className="flex items-center gap-2 text-base font-mono text-emerald-300 font-bold bg-slate-950/85 px-5 py-1.5 rounded-full border border-emerald-400/40 backdrop-blur-md shadow-lg">
              <svg className="w-5 h-5 text-emerald-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.711 2.598 2.664-.698c.969.541 1.83.819 2.796.819 3.18 0 5.767-2.587 5.767-5.766.001-3.182-2.585-5.766-5.767-5.766zm3.374 8.167c-.145.408-.847.781-1.18.828-.314.043-.72.073-2.146-.519-1.823-.757-3.003-2.613-3.094-2.735-.091-.122-.74-1.025-.74-1.954 0-.928.473-1.385.642-1.573.169-.188.369-.235.492-.235.123 0 .246.002.353.008.113.006.264-.043.413.315.153.367.522 1.272.568 1.365.046.094.077.204.015.328-.061.125-.092.203-.184.312-.092.11-.194.246-.277.33-.092.094-.188.196-.081.38.107.184.476.786 1.021 1.272.704.628 1.297.822 1.482.914.184.092.293.078.401-.047.108-.125.462-.538.585-.722.123-.184.246-.154.415-.092.169.062 1.077.508 1.262.6.185.092.308.138.354.215.046.077.046.446-.099.854z" />
              </svg>
              <span>WhatsApp: +91 7904942915</span>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-2 text-xs font-mono text-slate-300">
              <span className="px-3 py-0.5 rounded-full bg-white/5 border border-white/10">✓ Start Free — No Credit Card Required</span>
            </div>
          </div>
        </KineticText>
      </div>
    </div>
  );
};
