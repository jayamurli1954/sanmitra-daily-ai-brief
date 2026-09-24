import React from "react";
import { Sequence } from "remotion";
import { Background } from "./components/Background";
import { BackgroundMusic } from "./components/BackgroundMusic";
import { Scene1Hook } from "./components/Scene1Hook";
import { Scene2Solution } from "./components/Scene2Solution";
import { Scene3CTA } from "./components/Scene3CTA";
import { ScriptSubtitles } from "./components/ScriptSubtitles";
import { VoiceOver } from "./components/VoiceOver";
import { SCENE_TIMINGS } from "./types";

export const Video: React.FC = () => {
  return (
    <div className="relative w-full h-full font-sans antialiased overflow-hidden select-none">
      {/* Persistent Premium Indigo/Slate Background */}
      <Background />

      {/* Top Header Badge */}
      <div className="absolute top-10 inset-x-0 flex justify-between items-center px-14 z-50 pointer-events-none">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-400 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/30">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 00-9.78 2.096A4.001 4.001 0 003 15z" />
            </svg>
          </div>
          <span className="text-sm font-black tracking-widest text-white/90 uppercase font-mono">
            SYNCFLOW<span className="text-cyan-400">OS</span>
          </span>
        </div>

        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-mono text-slate-300">CLOUD NODE: ONLINE</span>
        </div>
      </div>

      {/* Scene 1: The Hook (0s - 10s | 0 - 300 frames) */}
      <Sequence
        from={SCENE_TIMINGS.SCENE_1.START}
        durationInFrames={SCENE_TIMINGS.SCENE_1.DURATION}
        name="Scene 1 - The Hook"
      >
        <Scene1Hook />
      </Sequence>

      {/* Scene 2: The Solution (10s - 25s | 300 - 750 frames) */}
      <Sequence
        from={SCENE_TIMINGS.SCENE_2.START}
        durationInFrames={SCENE_TIMINGS.SCENE_2.DURATION}
        name="Scene 2 - The Solution"
      >
        <Scene2Solution />
      </Sequence>

      {/* Scene 3: Call to Action (25s - 36s | 750 - 1080 frames) */}
      <Sequence
        from={SCENE_TIMINGS.SCENE_3.START}
        durationInFrames={SCENE_TIMINGS.SCENE_3.DURATION}
        name="Scene 3 - Call To Action"
      >
        <Scene3CTA />
      </Sequence>

      {/* Timed Voiceover Script Subtitles Overlay */}
      <ScriptSubtitles />

      {/* Synchronized Voiceover Narration Audio */}
      <VoiceOver />

      {/* Dynamic Background Soundtrack */}
      <BackgroundMusic />
    </div>
  );
};
