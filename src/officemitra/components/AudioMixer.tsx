import React from "react";
import { Audio, interpolate, staticFile, useCurrentFrame } from "remotion";
import { SCENE_00_PROLOGUE_FRAMES } from "../types";

export const AudioMixer: React.FC = () => {
  const frame = useCurrentFrame();

  // Gentle volume ducking during voiceovers, louder during Scene 00 and Accounting Factory
  // Prologue: soft rise
  const prologueVol = interpolate(frame, [0, SCENE_00_PROLOGUE_FRAMES], [0.15, 0.35], {
    extrapolateRight: "clamp",
  });

  // Base background volume is around 0.28, ducking to 0.20 when narration is intense,
  // lifting to 0.40 during the Accounting Factory and finale
  const bgmVolume =
    frame < SCENE_00_PROLOGUE_FRAMES
      ? prologueVol
      : frame > 1800 && frame < 2200 // Factory scene energy
      ? 0.38
      : frame > 3400 // Finale resolve
      ? 0.45
      : 0.25;

  return (
    <>
      <Audio
        src={staticFile("audio/officemitra_theme.wav")}
        volume={bgmVolume}
      />
    </>
  );
};
