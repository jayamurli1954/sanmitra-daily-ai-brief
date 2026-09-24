import React from "react";
import { Audio, Sequence, staticFile } from "remotion";
import { SCENE_TIMINGS } from "../types";

export const VoiceOver: React.FC = () => {
  return (
    <>
      {/* Scene 1 Narration: Starts at frame 10 */}
      <Sequence from={SCENE_TIMINGS.SCENE_1.START + 10} name="VO - Scene 1">
        <Audio src={staticFile("audio/scene1_vo.mp3")} volume={1.0} />
      </Sequence>

      {/* Scene 2 Narration: Starts at frame 310 */}
      <Sequence from={SCENE_TIMINGS.SCENE_2.START + 10} name="VO - Scene 2">
        <Audio src={staticFile("audio/scene2_vo.mp3")} volume={1.0} />
      </Sequence>

      {/* Scene 3 Narration: Starts at frame 760 */}
      <Sequence from={SCENE_TIMINGS.SCENE_3.START + 10} name="VO - Scene 3">
        <Audio src={staticFile("audio/scene3_vo.mp3")} volume={1.0} />
      </Sequence>
    </>
  );
};
