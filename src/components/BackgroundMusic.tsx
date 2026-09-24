import React from "react";
import { Audio, interpolate, staticFile } from "remotion";

export const BackgroundMusic: React.FC = () => {
  return (
    <Audio
      src={staticFile("audio/bg_music.wav")}
      volume={(f) =>
        interpolate(
          f,
          [
            0, 20,         // Smooth entry
            240, 290,      // Scene 1 crash transition swell
            310,           // Scene 2 voiceover
            710, 750,      // Scene 2 -> Scene 3 CTA transition swell
            770,           // Scene 3 voiceover
            990, 1030,     // Outro swell
            1075, 1080     // Outro fade out
          ],
          [
            0.40, 0.65,    // Clear and audible right from the start
            0.65, 0.85,    // Swell on Scene 1 crash
            0.55,          // Scene 2 solution
            0.55, 0.85,    // Swell on Scene 3 CTA transition
            0.60,          // Scene 3 CTA
            0.65, 0.90,    // Final punch
            0.35, 0.0      // Clean outro
          ],
          {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }
        )
      }
    />
  );
};
