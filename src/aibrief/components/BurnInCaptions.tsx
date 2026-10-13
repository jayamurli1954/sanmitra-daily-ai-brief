import React from "react";
import { useCurrentFrame } from "remotion";
import rawCaptions from "../data/captions.json";

interface CaptionCue {
  index: number;
  sceneId: string;
  startFrame: number;
  endFrame: number;
  startSeconds: number;
  endSeconds: number;
  text: string;
}

const captions = rawCaptions as unknown as CaptionCue[];

interface BurnInCaptionsProps {
  enabled?: boolean;
}

export const BurnInCaptions: React.FC<BurnInCaptionsProps> = ({
  enabled = true,
}) => {
  const frame = useCurrentFrame();

  if (!enabled) return null;

  // Find active cue
  const activeCue = captions.find(
    (c) => frame >= c.startFrame && frame < c.endFrame
  );

  if (!activeCue || !activeCue.text.trim()) {
    return null;
  }

  const isStoryScene = /^s\d+_/.test(activeCue.sceneId || "");

  return (
    <div
      style={{
        position: "absolute",
        // Story scenes: the gap above the lower third (which starts at y=810).
        // Intro, recap and outro fill the middle of the frame with cards, so
        // their captions sit just above the ticker instead.
        top: isStoryScene ? 734 : 940,
        left: "50%",
        transform: "translateX(-50%)",
        backgroundColor: "rgba(0, 0, 0, 0.88)",
        border: "2px solid rgba(250, 204, 21, 0.85)",
        padding: "8px 30px",
        borderRadius: 10,
        boxShadow: "0 6px 20px rgba(0, 0, 0, 0.85)",
        zIndex: 48,
        maxWidth: 1700,
        whiteSpace: "nowrap",
        textAlign: "center",
        pointerEvents: "none",
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      <span
        style={{
          color: "#ffffff",
          fontSize: 38,
          fontWeight: 800,
          lineHeight: 1.25,
          letterSpacing: 0.3,
          textShadow: "0 2px 6px rgba(0,0,0,1)",
        }}
      >
        {activeCue.text}
      </span>
    </div>
  );
};
