import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

interface SubtitleSegment {
  start: number;
  end: number;
  text: string;
}

const SUBTITLES: SubtitleSegment[] = [
  // Scene 1: 0 - 210
  {
    start: 10,
    end: 105,
    text: "Every missed deadline and misplaced brief costs your practice time.",
  },
  {
    start: 110,
    end: 200,
    text: "Wasted research hours are slowing down your legal outcomes.",
  },

  // Scene 2: 210 - 520
  {
    start: 215,
    end: 330,
    text: "Meet LegalMitra. Not another generic AI chatbot.",
  },
  {
    start: 335,
    end: 510,
    text: "A professional intelligence workspace with instant BNS, BNSS & BSA crosswalk.",
  },

  // Scene 3: 520 - 810
  {
    start: 525,
    end: 660,
    text: "Find relevant case law in minutes. Manage every matter in one place.",
  },
  {
    start: 665,
    end: 800,
    text: "Never miss a deadline — while your client data stays strictly private.",
  },

  // Scene 4: 810 - 1140
  {
    start: 815,
    end: 960,
    text: "Research smarter. Manage better. Practice confidently.",
  },
  {
    start: 965,
    end: 1120,
    text: "Visit legalmitra.sanmitratech.in and start free today.",
  },
];

export const LegalSubtitles: React.FC = () => {
  const frame = useCurrentFrame();

  const current = SUBTITLES.find(
    (sub) => frame >= sub.start && frame <= sub.end
  );

  if (!current) {
    return null;
  }

  const fadeIn = interpolate(frame, [current.start, current.start + 6], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(frame, [current.end - 6, current.end], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <div
      className="absolute bottom-10 inset-x-0 flex justify-center pointer-events-none z-50 px-8"
      style={{ opacity }}
    >
      <div className="max-w-4xl px-7 py-3 rounded-full bg-[#050b14]/90 border border-amber-400/30 backdrop-blur-xl shadow-2xl flex items-center gap-3">
        <span className="w-2.5 h-2.5 rounded-full bg-[#e7c77c] animate-pulse flex-shrink-0" />
        <p className="text-base md:text-lg font-medium tracking-wide text-amber-50 text-center drop-shadow-md">
          {current.text}
        </p>
      </div>
    </div>
  );
};
