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

  return (
    <div
      style={{
        position: "absolute",
        top: 740,
        left: "50%",
        transform: "translateX(-50%)",
        backgroundColor: "rgba(6, 11, 23, 0.94)",
        border: "1px solid rgba(56, 189, 248, 0.5)",
        padding: "6px 22px",
        borderRadius: 20,
        boxShadow: "0 4px 16px rgba(0, 0, 0, 0.8)",
        zIndex: 48,
        maxWidth: 1200,
        textAlign: "center",
        pointerEvents: "none",
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      <span
        style={{
          color: "#f8fafc",
          fontSize: 20,
          fontWeight: 700,
          letterSpacing: 0.5,
          textShadow: "0 2px 8px rgba(0,0,0,0.9)",
        }}
      >
        {activeCue.text}
      </span>
    </div>
  );
};
