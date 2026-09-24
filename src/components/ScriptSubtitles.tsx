import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

interface SubtitleSegment {
  start: number;
  end: number;
  text: string;
}

const SUBTITLES: SubtitleSegment[] = [
  // Scene 1: 0 - 300 (0s - 10s)
  {
    start: 10,
    end: 85,
    text: "Late night flow... and then a sudden crash.",
  },
  {
    start: 90,
    end: 175,
    text: "Everything you built vanishes in an instant.",
  },
  {
    start: 180,
    end: 275,
    text: "Local storage shouldn't mean living on the edge.",
  },

  // Scene 2: 300 - 750 (10s - 25s)
  {
    start: 310,
    end: 445,
    text: "Never hit save again. Meet Instant Cloud Syncing.",
  },
  {
    start: 450,
    end: 590,
    text: "Every keystroke mirrored silently to encrypted cloud storage in sub-milliseconds.",
  },
  {
    start: 595,
    end: 735,
    text: "Accessible across phone, tablet, and desktop without skipping a beat.",
  },

  // Scene 3: 750 - 1080 (25s - 36s)
  {
    start: 760,
    end: 905,
    text: "Your ideas deserve total security. Stop gambling with your data.",
  },
  {
    start: 910,
    end: 1055,
    text: "Download now and secure your data workflow with pure peace of mind.",
  },
];

export const ScriptSubtitles: React.FC = () => {
  const frame = useCurrentFrame();

  const currentSubtitle = SUBTITLES.find(
    (sub) => frame >= sub.start && frame <= sub.end
  );

  if (!currentSubtitle) {
    return null;
  }

  // Smooth fade in & out for each subtitle segment
  const fadeIn = interpolate(
    frame,
    [currentSubtitle.start, currentSubtitle.start + 8],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const fadeOut = interpolate(
    frame,
    [currentSubtitle.end - 8, currentSubtitle.end],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <div
      className="absolute bottom-10 inset-x-0 flex justify-center pointer-events-none z-50 px-8"
      style={{ opacity }}
    >
      <div className="max-w-4xl px-6 py-2.5 rounded-full bg-slate-950/85 border border-white/15 backdrop-blur-xl shadow-2xl flex items-center gap-3">
        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse flex-shrink-0" />
        <p className="text-base md:text-lg font-medium tracking-wide text-slate-100 text-center drop-shadow-md">
          {currentSubtitle.text}
        </p>
      </div>
    </div>
  );
};
