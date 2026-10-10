import React from "react";
import { Composition } from "remotion";
import "./index.css";
import { Video } from "./Video";
import { VideoVertical } from "./VideoVertical";
import { LegalMitraVideo } from "./legalmitra/LegalMitraVideo";
import { LegalMitraVideoVertical } from "./legalmitra/LegalMitraVideoVertical";
import { LegalMitraWebsiteHero } from "./legalmitra/LegalMitraWebsiteHero";
import { LegalMitraDemo60s } from "./legalmitra/LegalMitraDemo60s";
import { AIBriefVideo } from "./aibrief/AIBriefVideo";
import { JENNY_SHORT_FRAMES, JennyShort } from "./aibrief/JennyShort";
import { UKRAINE_WIDE_FRAMES, UkraineWide } from "./aibrief/UkraineWide";
import { AIBriefThumbnail } from "./aibrief/AIBriefThumbnail";
import { LinkedInCoverBanner } from "./aibrief/LinkedInCoverBanner";
import { getAIBriefTotalFrames } from "./aibrief/timingsHelper";
import {
  LEGAL_DURATION_IN_FRAMES,
  LEGAL_FPS,
  LEGAL_HEIGHT,
  LEGAL_VERTICAL_HEIGHT,
  LEGAL_VERTICAL_WIDTH,
  LEGAL_WIDTH,
} from "./legalmitra/types";
import {
  VERTICAL_HEIGHT,
  VERTICAL_WIDTH,
  VIDEO_DURATION_IN_FRAMES,
  VIDEO_FPS,
  VIDEO_HEIGHT,
  VIDEO_WIDTH,
} from "./types";
import { OfficeMitraVideo } from "./officemitra/OfficeMitraVideo";
import { OfficeMitraSquare } from "./officemitra/OfficeMitraSquare";
import { OfficeMitraVertical } from "./officemitra/OfficeMitraVertical";
import {
  OM_FPS,
  OM_HEIGHT,
  OM_SQUARE_SIZE,
  OM_TOTAL_FRAMES,
  OM_VERTICAL_HEIGHT,
  OM_VERTICAL_WIDTH,
  OM_WIDTH,
} from "./officemitra/types";
import { BhajanVideo } from "../Bhajans/src/BhajanVideo";
import { KrishnaBhajan13MinVideo } from "../Bhajans/src/KrishnaBhajan13MinVideo";
import { GanapathiShlokaVideo } from "../Bhajans/src/GanapathiShlokaVideo";
import { GaneshBhajanVideo } from "../Bhajans/src/GaneshBhajanVideo";
import { BHAJAN_TOTAL_FRAMES } from "../Bhajans/src/Root";
import { KRISHNA_BHAJAN_TOTAL_FRAMES } from "../Bhajans/src/data/krishnaBhajanData";
import { GANAPATHI_TOTAL_FRAMES } from "../Bhajans/src/data/ganapathiData";
import { GANESH_BHAJAN_TOTAL_FRAMES } from "../Bhajans/src/data/ganeshBhajanData";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* --- OfficeMitra + SSDV Product Commercials --- */}
      {/* OfficeMitra 16:9 Widescreen Master (1920x1080, 124s) */}
      <Composition
        id="OfficeMitraMaster16x9"
        component={OfficeMitraVideo}
        durationInFrames={OM_TOTAL_FRAMES}
        fps={OM_FPS}
        width={OM_WIDTH}
        height={OM_HEIGHT}
      />

      {/* OfficeMitra 1:1 Square Feed (1080x1080, LinkedIn/Social) */}
      <Composition
        id="OfficeMitraSquare1x1"
        component={OfficeMitraSquare}
        durationInFrames={OM_TOTAL_FRAMES}
        fps={OM_FPS}
        width={OM_SQUARE_SIZE}
        height={OM_SQUARE_SIZE}
      />

      {/* OfficeMitra 9:16 Vertical Mobile (1080x1920, Reels/Shorts) */}
      <Composition
        id="OfficeMitraVertical9x16"
        component={OfficeMitraVertical}
        durationInFrames={OM_TOTAL_FRAMES}
        fps={OM_FPS}
        width={OM_VERTICAL_WIDTH}
        height={OM_VERTICAL_HEIGHT}
      />

      {/* --- LegalMitra Campaigns --- */}
      {/* LegalMitra LinkedIn 16:9 Widescreen (1920x1080) */}
      <Composition
        id="LegalMitraLinkedIn"
        component={LegalMitraVideo}
        durationInFrames={LEGAL_DURATION_IN_FRAMES}
        fps={LEGAL_FPS}
        width={LEGAL_WIDTH}
        height={LEGAL_HEIGHT}
      />

      {/* LegalMitra Instagram 9:16 Vertical (1080x1920) */}
      <Composition
        id="LegalMitraInstagram"
        component={LegalMitraVideoVertical}
        durationInFrames={LEGAL_DURATION_IN_FRAMES}
        fps={LEGAL_FPS}
        width={LEGAL_VERTICAL_WIDTH}
        height={LEGAL_VERTICAL_HEIGHT}
      />

      {/* LegalMitra Website Hero 15-second cutdown (1920x1080, 450 frames) */}
      <Composition
        id="LegalMitraWebsiteHero"
        component={LegalMitraWebsiteHero}
        durationInFrames={450}
        fps={LEGAL_FPS}
        width={LEGAL_WIDTH}
        height={LEGAL_HEIGHT}
      />

      {/* LegalMitra 60-second Sales Presentation & Demo (1920x1080, 1800 frames) */}
      <Composition
        id="LegalMitraDemo60s"
        component={LegalMitraDemo60s}
        durationInFrames={1800}
        fps={LEGAL_FPS}
        width={LEGAL_WIDTH}
        height={LEGAL_HEIGHT}
      />

      {/* --- InstantCloudSync Baseline --- */}
      <Composition
        id="InstantCloudSync"
        component={Video}
        durationInFrames={VIDEO_DURATION_IN_FRAMES}
        fps={VIDEO_FPS}
        width={VIDEO_WIDTH}
        height={VIDEO_HEIGHT}
      />

      <Composition
        id="InstantCloudSyncVertical"
        component={VideoVertical}
        durationInFrames={VIDEO_DURATION_IN_FRAMES}
        fps={VIDEO_FPS}
        width={VERTICAL_WIDTH}
        height={VERTICAL_HEIGHT}
      />

      {/* --- AI Brief Daily Faceless YouTube Newsroom --- */}
      {/* 16:9 Widescreen Master (1920x1080 @ 30fps) */}
      <Composition
        id="AIBriefMaster16x9"
        component={AIBriefVideo}
        durationInFrames={getAIBriefTotalFrames()}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* 16:9 Jenny short: Ukraine interceptor drones, 3 October */}
      <Composition
        id="AIBriefUkraineWide"
        component={UkraineWide}
        durationInFrames={UKRAINE_WIDE_FRAMES}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* 9:16 Jenny short of the current lead story */}
      <Composition
        id="AIBriefJennyShort"
        component={JennyShort}
        durationInFrames={JENNY_SHORT_FRAMES}
        fps={30}
        width={1080}
        height={1920}
      />

      {/* 16:9 High-Contrast Breaking News Thumbnail Master & A/B/C Variants */}
      <Composition
        id="AIBriefThumbnail"
        component={AIBriefThumbnail}
        defaultProps={{ variant: "A" as const }}
        durationInFrames={30}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="AIBriefThumbnailA"
        component={AIBriefThumbnail}
        defaultProps={{ variant: "A" as const }}
        durationInFrames={30}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="AIBriefThumbnailB"
        component={AIBriefThumbnail}
        defaultProps={{ variant: "B" as const }}
        durationInFrames={30}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="AIBriefThumbnailC"
        component={AIBriefThumbnail}
        defaultProps={{ variant: "C" as const }}
        durationInFrames={30}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* 16:9 LinkedIn Article Cover Banner (1920x1080) */}
      <Composition
        id="AIBriefLinkedInCover"
        component={LinkedInCoverBanner}
        durationInFrames={30}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* --- Devotional Bhajan Video Compilation (Kannada & Hindi Classics, 14.5 mins) --- */}
      <Composition
        id="BhajanCompilation16x9"
        component={BhajanVideo}
        durationInFrames={BHAJAN_TOTAL_FRAMES}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* --- Dedicated 13-Minute Full Krishna Bhajan (॥ श्रीकृष्ण भजन ॥) --- */}
      <Composition
        id="KrishnaBhajan13Min"
        component={KrishnaBhajan13MinVideo}
        durationInFrames={KRISHNA_BHAJAN_TOTAL_FRAMES}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* --- Auspicious Maiden Channel Video: Ganapathi Shloka (॥ श्री गणेश स्तोत्रम् ॥) --- */}
      <Composition
        id="GanapathiShloka"
        component={GanapathiShlokaVideo}
        durationInFrames={GANAPATHI_TOTAL_FRAMES}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* --- Full 6.5-Minute Hindi Ganesh Bhajan: हे गणनायक, आओ मेरे द्वार --- */}
      <Composition
        id="GaneshBhajan6Min"
        component={GaneshBhajanVideo}
        durationInFrames={GANESH_BHAJAN_TOTAL_FRAMES}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
