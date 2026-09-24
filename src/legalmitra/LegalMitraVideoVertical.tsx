import React from "react";
import { Img, Sequence, staticFile } from "remotion";
import { LegalAudio } from "./LegalAudio";
import { LegalBackground } from "./LegalBackground";
import { LegalSubtitlesVertical } from "./LegalSubtitlesVertical";
import { Scene1ProblemVertical } from "./vertical/Scene1ProblemVertical";
import { Scene2ShowcaseVertical } from "./vertical/Scene2ShowcaseVertical";
import { Scene3WorkflowVertical } from "./vertical/Scene3WorkflowVertical";
import { Scene4ContactCTAVertical } from "./vertical/Scene4ContactCTAVertical";
import { LEGAL_SCENE_TIMINGS } from "./types";

export const LegalMitraVideoVertical: React.FC = () => {
  return (
    <div className="relative w-full h-full font-sans antialiased overflow-hidden select-none">
      {/* Background */}
      <LegalBackground />

      {/* Top Header Branding (Mobile Safe Area) */}
      <div className="absolute top-16 inset-x-0 flex justify-between items-center px-10 z-50 pointer-events-none">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl p-0.5 bg-gradient-to-tr from-amber-400 to-yellow-600 shadow-md">
            <Img
              src={staticFile("legalmitra/legalmitra-logo.png")}
              className="w-full h-full object-contain rounded-lg"
            />
          </div>
          <span className="text-lg font-black tracking-wider text-white font-serif">
            LEGAL<span className="text-amber-400">MITRA</span>
          </span>
        </div>

        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/5 border border-amber-400/20 backdrop-blur-md">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-mono text-amber-200">INTELLIGENCE</span>
        </div>
      </div>

      {/* Scene 1: Problem (0 - 7s | 0 - 210 frames) */}
      <Sequence
        from={LEGAL_SCENE_TIMINGS.SCENE_1_HOOK.START}
        durationInFrames={LEGAL_SCENE_TIMINGS.SCENE_1_HOOK.DURATION}
        name="Vertical Scene 1 - Challenge"
      >
        <Scene1ProblemVertical />
      </Sequence>

      {/* Scene 2: Not An AI Chatbot & New Laws (7s - 17.33s | 210 - 520 frames) */}
      <Sequence
        from={LEGAL_SCENE_TIMINGS.SCENE_2_DIFFERENTIATOR.START}
        durationInFrames={LEGAL_SCENE_TIMINGS.SCENE_2_DIFFERENTIATOR.DURATION}
        name="Vertical Scene 2 - Not An AI Chatbot & New Laws"
      >
        <Scene2ShowcaseVertical />
      </Sequence>

      {/* Scene 3: Outcomes & Workflow (17.33s - 27s | 520 - 810 frames) */}
      <Sequence
        from={LEGAL_SCENE_TIMINGS.SCENE_3_WORKFLOW.START}
        durationInFrames={LEGAL_SCENE_TIMINGS.SCENE_3_WORKFLOW.DURATION}
        name="Vertical Scene 3 - Outcomes & Workflow"
      >
        <Scene3WorkflowVertical />
      </Sequence>

      {/* Scene 4: High-Converting Contact CTA (27s - 38s | 810 - 1140 frames) */}
      <Sequence
        from={LEGAL_SCENE_TIMINGS.SCENE_4_CTA.START}
        durationInFrames={LEGAL_SCENE_TIMINGS.SCENE_4_CTA.DURATION}
        name="Vertical Scene 4 - Contact & CTA"
      >
        <Scene4ContactCTAVertical />
      </Sequence>

      {/* Elevated Subtitles for Instagram Reels Navigation Bar */}
      <LegalSubtitlesVertical />

      {/* Full Sound Design: Orchestral Score + Neural Voiceover */}
      <LegalAudio />
    </div>
  );
};
