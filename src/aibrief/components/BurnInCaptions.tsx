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
        // Story scenes: just above the clean lower-third bar. Intro, recap and
        // outro fill the middle of the frame, so captions sit near the bottom.
        bottom: isStoryScene ? 290 : 60,
        left: "50%",
        transform: "translateX(-50%)",
        backgroundColor: "rgba(0, 0, 0, 0.62)",
        padding: "6px 22px",
        borderRadius: 6,
        zIndex: 48,
        maxWidth: 1600,
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
          fontSize: 34,
          fontWeight: 600,
          lineHeight: 1.25,
        }}
      >
        {activeCue.text}
      </span>
    </div>
  );
};
