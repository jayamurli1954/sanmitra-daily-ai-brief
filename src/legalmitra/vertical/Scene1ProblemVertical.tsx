import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { KineticText } from "../../components/KineticText";

export const Scene1ProblemVertical: React.FC = () => {
  const frame = useCurrentFrame();

  const chamberScale = interpolate(frame, [0, 210], [1.0, 1.06]);
  const chamberOpacity = interpolate(frame, [0, 25, 185, 210], [0, 0.42, 0.42, 0]);

  return (
    // Mobile Safe Area: pt-[250px] pb-[350px]
    <div className="absolute inset-0 flex flex-col items-center justify-center overflow-hidden px-10 pt-[250px] pb-[350px]">
      {/* Background Advocate Research Desk */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          transform: `scale(${chamberScale})`,
          opacity: chamberOpacity,
        }}
      >
        <Img
          src={staticFile("legalmitra/advocate-vertical-research.jpg")}
          className="w-full h-full object-cover filter brightness-90 contrast-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#030712] via-[#030712]/75 to-[#030712]/85" />
      </div>

      <div className="flex flex-col items-center justify-center w-full max-w-[920px] text-center">
        <KineticText delay={5} exitFrame={195}>
          <div className="inline-flex items-center gap-3 px-6 py-2.5 rounded-full border border-amber-500/40 bg-[#0c1c33]/90 backdrop-blur-xl mb-10 shadow-xl">
            <span className="w-3 h-3 rounded-full bg-rose-500 animate-ping" />
            <span className="text-sm font-mono font-bold tracking-widest text-amber-300 uppercase">
              The Legal Practice Bottleneck
            </span>
          </div>
        </KineticText>

        {/* Big Bold Vertical Hooks */}
        <div className="space-y-4 mb-10">
          <KineticText delay={12} exitFrame={195} initialScale={0.9}>
            <h1 className="text-7xl md:text-8xl font-black tracking-tight text-white leading-tight">
              RESEARCH <br />
              <span className="text-slate-400 font-light">TAKES HOURS.</span>
            </h1>
          </KineticText>

          <KineticText delay={24} exitFrame={195} initialScale={0.9}>
            <h1 className="text-7xl md:text-8xl font-black tracking-tight text-white leading-tight">
              DEADLINES <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-rose-400 to-amber-300">
                CAN'T WAIT.
              </span>
            </h1>
          </KineticText>
        </div>

        {/* Floating Urgency Alert Card */}
        <KineticText delay={42} exitFrame={195} initialY={40}>
          <div className="w-full p-6 rounded-3xl border border-rose-500/40 bg-slate-950/90 shadow-2xl backdrop-blur-2xl text-left">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono font-bold text-rose-300 uppercase tracking-wider">
                Limitation Warning
              </span>
              <span className="px-3 py-1 rounded-md bg-rose-950/80 border border-rose-500/50 text-xs font-mono font-bold text-rose-300">
                48h Remaining
              </span>
            </div>
            <div className="text-xl font-bold text-white mb-1">Commercial Appeal Brief</div>
            <div className="text-sm text-slate-400">High Court of Karnataka • Draft Pending</div>
          </div>
        </KineticText>
      </div>
    </div>
  );
};
