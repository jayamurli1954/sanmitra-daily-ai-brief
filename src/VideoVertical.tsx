import React from "react";
import { Sequence } from "remotion";
import { Background } from "./components/Background";
import { BackgroundMusic } from "./components/BackgroundMusic";
import { Scene1HookVertical } from "./components/vertical/Scene1HookVertical";
import { Scene2SolutionVertical } from "./components/vertical/Scene2SolutionVertical";
import { Scene3CTAVertical } from "./components/vertical/Scene3CTAVertical";
import { ScriptSubtitlesVertical } from "./components/vertical/ScriptSubtitlesVertical";
import { VoiceOver } from "./components/VoiceOver";
import { SCENE_TIMINGS } from "./types";

export const VideoVertical: React.FC = () => {
  return (
    <div className="relative w-full h-full font-sans antialiased overflow-hidden select-none">
      {/* Background */}
      <Background />

      {/* Top Header Badge (formatted for vertical safe area) */}
      <div className="absolute top-16 inset-x-0 flex justify-between items-center px-10 z-50 pointer-events-none">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-400 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/30">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 00-9.78 2.096A4.001 4.001 0 003 15z" />
            </svg>
          </div>
          <span className="text-base font-black tracking-widest text-white/95 uppercase font-mono">
            SYNCFLOW<span className="text-cyan-400">OS</span>
          </span>
        </div>

        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-mono text-slate-300">CLOUD NODE: ONLINE</span>
        </div>
      </div>

      {/* Scene 1: The Hook (0 - 10s) */}
      <Sequence
        from={SCENE_TIMINGS.SCENE_1.START}
        durationInFrames={SCENE_TIMINGS.SCENE_1.DURATION}
        name="Vertical Scene 1 - The Hook"
      >
        <Scene1HookVertical />
      </Sequence>

      {/* Scene 2: The Solution (10s - 25s) */}
      <Sequence
        from={SCENE_TIMINGS.SCENE_2.START}
        durationInFrames={SCENE_TIMINGS.SCENE_2.DURATION}
        name="Vertical Scene 2 - The Solution"
      >
        <Scene2SolutionVertical />
      </Sequence>

      {/* Scene 3: Call to Action (25s - 36s) */}
      <Sequence
        from={SCENE_TIMINGS.SCENE_3.START}
        durationInFrames={SCENE_TIMINGS.SCENE_3.DURATION}
        name="Vertical Scene 3 - Call To Action"
      >
        <Scene3CTAVertical />
      </Sequence>

      {/* Synchronized Narration Subtitles */}
      <ScriptSubtitlesVertical />

      {/* Synchronized Voiceover Narration Audio */}
      <VoiceOver />

      {/* Dynamic Background Soundtrack */}
      <BackgroundMusic />
    </div>
  );
};
