import React from "react";
import { Audio, interpolate, Sequence, staticFile } from "remotion";
import { LEGAL_SCENE_TIMINGS } from "./types";

export const LegalAudio: React.FC = () => {
  return (
    <>
      {/* Background Orchestral Score with Dynamic Ducking */}
      <Audio
        src={staticFile("audio/legalmitra_score.wav")}
        volume={(f) =>
          interpolate(
            f,
            [
              0, 20,         // Smooth entry
              190, 220,      // Scene 1 -> 2 transition swell
              240,           // Scene 2 voice duck
              490, 530,      // Scene 2 -> 3 transition swell
              550,           // Scene 3 voice duck
              780, 820,      // Scene 3 -> 4 CTA transition swell
              840,           // Scene 4 voice duck
              1080, 1110,    // Final CTA punch
              1135, 1140     // Smooth outro fade
            ],
            [
              0.35, 0.45,
              0.45, 0.65,
              0.40,
              0.40, 0.65,
              0.38,
              0.38, 0.68,
              0.42,
              0.42, 0.70,
              0.25, 0.0
            ],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }
          )
        }
      />

      {/* Scene 1 Narration */}
      <Sequence from={LEGAL_SCENE_TIMINGS.SCENE_1_HOOK.START + 5} name="VO - Scene 1">
        <Audio src={staticFile("audio/legalmitra_s1.mp3")} volume={1.0} />
      </Sequence>

      {/* Scene 2 Narration */}
      <Sequence from={LEGAL_SCENE_TIMINGS.SCENE_2_DIFFERENTIATOR.START + 5} name="VO - Scene 2">
        <Audio src={staticFile("audio/legalmitra_s2.mp3")} volume={1.0} />
      </Sequence>

      {/* Scene 3 Narration */}
      <Sequence from={LEGAL_SCENE_TIMINGS.SCENE_3_WORKFLOW.START + 5} name="VO - Scene 3">
        <Audio src={staticFile("audio/legalmitra_s3.mp3")} volume={1.0} />
      </Sequence>

      {/* Scene 4 Narration */}
      <Sequence from={LEGAL_SCENE_TIMINGS.SCENE_4_CTA.START + 5} name="VO - Scene 4">
        <Audio src={staticFile("audio/legalmitra_s4.mp3")} volume={1.0} />
      </Sequence>
    </>
  );
};
