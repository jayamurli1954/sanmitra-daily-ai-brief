import React from "react";
import { Series } from "remotion";
import { AudioMixer } from "./components/AudioMixer";
import { Scene00Prologue } from "./scenes/Scene00Prologue";
import { Scene01Problem } from "./scenes/Scene01Problem";
import { Scene02Chaos } from "./scenes/Scene02Chaos";
import { Scene03Intro } from "./scenes/Scene03Intro";
import { Scene04Portal } from "./scenes/Scene04Portal";
import { Scene05Extraction } from "./scenes/Scene05Extraction";
import { Scene06SSDV } from "./scenes/Scene06SSDV";
import { Scene06AFactory } from "./scenes/Scene06AFactory";
import { Scene07Review } from "./scenes/Scene07Review";
import { Scene08WorkingPapers } from "./scenes/Scene08WorkingPapers";
import { Scene09Advisory } from "./scenes/Scene09Advisory";
import { Scene10CommandCenter } from "./scenes/Scene10CommandCenter";
import { Scene11Finale } from "./scenes/Scene11Finale";
import {
  SCENE_00_PROLOGUE_FRAMES,
  SCENE_01_PROBLEM_FRAMES,
  SCENE_02_CHAOS_FRAMES,
  SCENE_03_INTRO_FRAMES,
  SCENE_04_PORTAL_FRAMES,
  SCENE_05_EXTRACTION_FRAMES,
  SCENE_06_SSDV_FRAMES,
  SCENE_06A_FACTORY_FRAMES,
  SCENE_07_REVIEW_FRAMES,
  SCENE_08_WORKING_PAPERS_FRAMES,
  SCENE_09_ADVISORY_FRAMES,
  SCENE_10_COMMAND_CENTER_FRAMES,
  SCENE_11_FINALE_FRAMES,
} from "./types";

export const OfficeMitraVideo: React.FC = () => {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#070b16",
        position: "relative",
      }}
    >
      <AudioMixer />

      <Series>
        {/* Scene 00: Opening Prologue (3s) */}
        <Series.Sequence durationInFrames={SCENE_00_PROLOGUE_FRAMES}>
          <Scene00Prologue />
        </Series.Sequence>

        {/* Scene 01: Compliance Blitz & Deadlines (13s) */}
        <Series.Sequence durationInFrames={SCENE_01_PROBLEM_FRAMES}>
          <Scene01Problem />
        </Series.Sequence>

        {/* Scene 02: Document Chaos (8s) */}
        <Series.Sequence durationInFrames={SCENE_02_CHAOS_FRAMES}>
          <Scene02Chaos />
        </Series.Sequence>

        {/* Scene 03: Introducing OfficeMitra (8.5s) */}
        <Series.Sequence durationInFrames={SCENE_03_INTRO_FRAMES}>
          <Scene03Intro />
        </Series.Sequence>

        {/* Scene 04: Smart Client Portal (9.5s) */}
        <Series.Sequence durationInFrames={SCENE_04_PORTAL_FRAMES}>
          <Scene04Portal />
        </Series.Sequence>

        {/* Scene 05: AI Extraction & Understanding (9s) */}
        <Series.Sequence durationInFrames={SCENE_05_EXTRACTION_FRAMES}>
          <Scene05Extraction />
        </Series.Sequence>

        {/* Scene 06: Enter SSDV Engine (10.5s) */}
        <Series.Sequence durationInFrames={SCENE_06_SSDV_FRAMES}>
          <Scene06SSDV />
        </Series.Sequence>

        {/* Scene 06A: The Accounting Factory "Aha" (10s) */}
        <Series.Sequence durationInFrames={SCENE_06A_FACTORY_FRAMES}>
          <Scene06AFactory />
        </Series.Sequence>

        {/* Scene 07: Review Intelligence & Trust Layer (12.5s) */}
        <Series.Sequence durationInFrames={SCENE_07_REVIEW_FRAMES}>
          <Scene07Review />
        </Series.Sequence>

        {/* Scene 08: Working Papers & Audit Trail (8.5s) */}
        <Series.Sequence durationInFrames={SCENE_08_WORKING_PAPERS_FRAMES}>
          <Scene08WorkingPapers />
        </Series.Sequence>

        {/* Scene 09: Compliance to Advisory (11.5s) */}
        <Series.Sequence durationInFrames={SCENE_09_ADVISORY_FRAMES}>
          <Scene09Advisory />
        </Series.Sequence>

        {/* Scene 10: Modern CA Command Center & Scale (10s) */}
        <Series.Sequence durationInFrames={SCENE_10_COMMAND_CENTER_FRAMES}>
          <Scene10CommandCenter />
        </Series.Sequence>

        {/* Scene 11: Visionary Finale & Contact (10s) */}
        <Series.Sequence durationInFrames={SCENE_11_FINALE_FRAMES}>
          <Scene11Finale />
        </Series.Sequence>
      </Series>
    </div>
  );
};
