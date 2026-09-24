import React from "react";
import { Img, Sequence, staticFile } from "remotion";
import { LegalAudio } from "./LegalAudio";
import { LegalBackground } from "./LegalBackground";
import { LegalSubtitles } from "./LegalSubtitles";
import { Scene1Problem } from "./Scene1Problem";
import { Scene2Showcase } from "./Scene2Showcase";
import { Scene3Workflow } from "./Scene3Workflow";
import { Scene4ContactCTA } from "./Scene4ContactCTA";
import { LEGAL_SCENE_TIMINGS } from "./types";

export const LegalMitraVideo: React.FC = () => {
  return (
    <div className="relative w-full h-full font-sans antialiased overflow-hidden select-none">
      {/* Background with Deep Midnight Navy & Legal Gold */}
      <LegalBackground />

      {/* Top Header Branding */}
      <div className="absolute top-10 inset-x-0 flex justify-between items-center px-14 z-50 pointer-events-none">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl p-0.5 bg-gradient-to-tr from-amber-400 to-yellow-600 shadow-md">
            <Img
              src={staticFile("legalmitra/legalmitra-logo.png")}
              className="w-full h-full object-contain rounded-lg"
            />
          </div>
          <span className="text-base font-black tracking-wider text-white font-serif">
            LEGAL<span className="text-amber-400">MITRA</span>
          </span>
        </div>

        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/5 border border-amber-400/20 backdrop-blur-md">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-mono text-amber-200">INTELLIGENCE WORKSPACE</span>
        </div>
      </div>

      {/* Scene 1: The Challenge (0 - 7s | 0 - 210 frames) */}
      <Sequence
        from={LEGAL_SCENE_TIMINGS.SCENE_1_HOOK.START}
        durationInFrames={LEGAL_SCENE_TIMINGS.SCENE_1_HOOK.DURATION}
        name="Scene 1 - The Challenge"
      >
        <Scene1Problem />
      </Sequence>

      {/* Scene 2: Differentiator & New Criminal Laws (7s - 17.33s | 210 - 520 frames) */}
      <Sequence
        from={LEGAL_SCENE_TIMINGS.SCENE_2_DIFFERENTIATOR.START}
        durationInFrames={LEGAL_SCENE_TIMINGS.SCENE_2_DIFFERENTIATOR.DURATION}
        name="Scene 2 - Not An AI Chatbot & New Laws"
      >
        <Scene2Showcase />
      </Sequence>

      {/* Scene 3: Outcomes & Real Workflow (17.33s - 27s | 520 - 810 frames) */}
      <Sequence
        from={LEGAL_SCENE_TIMINGS.SCENE_3_WORKFLOW.START}
        durationInFrames={LEGAL_SCENE_TIMINGS.SCENE_3_WORKFLOW.DURATION}
        name="Scene 3 - Outcomes & Workflow"
      >
        <Scene3Workflow />
      </Sequence>

      {/* Scene 4: Streamlined High-Converting CTA (27s - 38s | 810 - 1140 frames) */}
      <Sequence
        from={LEGAL_SCENE_TIMINGS.SCENE_4_CTA.START}
        durationInFrames={LEGAL_SCENE_TIMINGS.SCENE_4_CTA.DURATION}
        name="Scene 4 - Contact & CTA"
      >
        <Scene4ContactCTA />
      </Sequence>

      {/* Burned-in Subtitles for Silent Viewing */}
      <LegalSubtitles />

      {/* Full Sound Design: Orchestral Score + Neural Voiceover */}
      <LegalAudio />
    </div>
  );
};
