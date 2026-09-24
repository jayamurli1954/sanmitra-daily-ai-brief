import React from "react";
import { Audio, Series, staticFile } from "remotion";
import { AIBriefEpisode, Story } from "./types";
import episodeData from "./data/active_episode.json";
import rawTimings from "./data/timings.json";
import { BroadcastHeader } from "./components/BroadcastHeader";
import { DynamicTicker } from "./components/DynamicTicker";
import { SourceWatermark } from "./components/SourceWatermark";
import { StoryCard } from "./components/StoryCard";
import { IntroScene } from "./scenes/IntroScene";
import { OutroScene } from "./scenes/OutroScene";
import { SectionTransition } from "./components/SectionTransition";
import { HeadlinesRecapScene } from "./scenes/HeadlinesRecapScene";
import { AIMarketSnapshotScene } from "./scenes/AIMarketSnapshotScene";
import { BurnInCaptions } from "./components/BurnInCaptions";
import { SponsorSlot } from "./components/SponsorSlot";

interface TimingsData {
  [key: string]: {
    audioFile: string;
    audioDurationSeconds: number;
    sceneDurationSeconds: number;
    durationInFrames: number;
    title: string;
  };
}

const timings = rawTimings as unknown as TimingsData;
const episode = episodeData as unknown as AIBriefEpisode;

export const AIBriefVideo: React.FC = () => {
  const stories: Story[] = episode.stories || [];

  const introFrames = timings["intro"]?.durationInFrames ?? 450;
  const recapFrames = timings["recap"]?.durationInFrames ?? 300;
  const marketSnapshotFrames = timings["market_snapshot"]?.durationInFrames ?? 450;
  const outroFrames = timings["outro"]?.durationInFrames ?? 390;

  // Split stories according to editorial prompt structure:
  // Block 1: Stories 1, 2, 3
  // Transition 1: NEXT: AI SAFETY & RESPONSIBLE USE (2s / 60 frames)
  // Block 2: Stories 4, 5
  // Transition 2: NEXT: INDIA (2s / 60 frames)
  // Block 3: Story 6
  const block1 = stories.slice(0, 3);
  const block2 = stories.slice(3, 5);
  const block3 = stories.slice(5, 6);

  const transitionSafetyFrames = timings["transition_safety"]?.durationInFrames ?? 60;
  const transitionIndiaFrames = timings["transition_india"]?.durationInFrames ?? 60;

  return (
    <div
      style={{
        position: "relative",
        width: 1920,
        height: 1080,
        backgroundColor: "#030712",
        overflow: "hidden",
      }}
    >
      {/* Ambient Newsroom Background Music Bed */}
      <Audio
        src={staticFile("audio/aibrief_theme.wav")}
        volume={0.05}
        loop
      />

      {/* Main Broadcast Scene Sequence */}
      <Series>
        {/* SCENE 0: INTRO HOOK */}
        <Series.Sequence durationInFrames={introFrames}>
          <Audio
            src={staticFile(timings["intro"]?.audioFile ?? "audio/aibrief/s0_intro.mp3")}
            volume={1.0}
          />
          <IntroScene
            intro={episode.intro}
            formattedDate={episode.formattedDate}
          />
          <BroadcastHeader
            date={episode.formattedDate}
            region="GLOBAL"
            isSpecialReport={true}
          />
        </Series.Sequence>

        {/* OPTIONAL SPONSOR SLOT */}
        {episode.sponsor?.enabled && (
          <Series.Sequence durationInFrames={(episode.sponsor.durationSeconds || 6) * 30}>
            <SponsorSlot sponsor={episode.sponsor} />
            <BroadcastHeader
              date={episode.formattedDate}
              region="GLOBAL"
              isSpecialReport={false}
            />
          </Series.Sequence>
        )}

        {/* BLOCK 1: STORIES 1, 2, 3 (WORLD / FOUNDATION MODELS / HEALTHCARE) */}
        {block1.map((story, idx) => {
          const storyIndex = idx + 1;
          const timing = timings[story.id];
          const durationFrames = timing?.durationInFrames ?? 600;
          const audioFile = timing?.audioFile ?? `audio/aibrief/s${storyIndex}_${story.id}.mp3`;

          return (
            <Series.Sequence key={story.id} durationInFrames={durationFrames}>
              <Audio src={staticFile(audioFile)} volume={1.0} />
              <StoryCard story={story} />
              <SourceWatermark
                source={story.source}
                sourceUrl={story.sourceUrl}
              />
              <BroadcastHeader
                date={episode.formattedDate}
                region={story.region}
                isSpecialReport={story.importanceScore >= 90}
                storyIndex={storyIndex}
                totalStories={stories.length}
              />
            </Series.Sequence>
          );
        })}

        {/* SECTION TRANSITION 1: NEXT: AI SAFETY & RESPONSIBLE USE (2 SECONDS) */}
        <Series.Sequence durationInFrames={transitionSafetyFrames}>
          <SectionTransition
            region={episode.transitions?.[0]?.region || "USA"}
            title={episode.transitions?.[0]?.title || "NEXT: INFRASTRUCTURE & ROBOTICS"}
            display={episode.transitions?.[0]?.display || "NEXT: INFRASTRUCTURE & ROBOTICS"}
          />
          <BroadcastHeader
            date={episode.formattedDate}
            region={episode.transitions?.[0]?.region || "USA"}
            isSpecialReport={false}
          />
        </Series.Sequence>

        {/* BLOCK 2: STORIES 4, 5 (YOUTH SAFETY & ALIBABA ZHENWU V900) */}
        {block2.map((story, idx) => {
          const storyIndex = idx + 4;
          const timing = timings[story.id];
          const durationFrames = timing?.durationInFrames ?? 600;
          const audioFile = timing?.audioFile ?? `audio/aibrief/s${storyIndex}_${story.id}.mp3`;

          return (
            <Series.Sequence key={story.id} durationInFrames={durationFrames}>
              <Audio src={staticFile(audioFile)} volume={1.0} />
              <StoryCard story={story} />
              <SourceWatermark
                source={story.source}
                sourceUrl={story.sourceUrl}
              />
              <BroadcastHeader
                date={episode.formattedDate}
                region={story.region}
                isSpecialReport={story.importanceScore >= 90}
                storyIndex={storyIndex}
                totalStories={stories.length}
              />
            </Series.Sequence>
          );
        })}

        {/* SECTION TRANSITION 2: NEXT: INDIA (2 SECONDS) */}
        <Series.Sequence durationInFrames={transitionIndiaFrames}>
          <SectionTransition
            region={episode.transitions?.[1]?.region || "INDIA"}
            title={episode.transitions?.[1]?.title || "NEXT: INDIA"}
            display={episode.transitions?.[1]?.display || "NEXT: INDIA"}
          />
          <BroadcastHeader
            date={episode.formattedDate}
            region={episode.transitions?.[1]?.region || "INDIA"}
            isSpecialReport={false}
          />
        </Series.Sequence>

        {/* BLOCK 3: STORY 6 (MAHARASHTRA AI GOVERNANCE) */}
        {block3.map((story) => {
          const storyIndex = 6;
          const timing = timings[story.id];
          const durationFrames = timing?.durationInFrames ?? 600;
          const audioFile = timing?.audioFile ?? `audio/aibrief/s${storyIndex}_${story.id}.mp3`;

          return (
            <Series.Sequence key={story.id} durationInFrames={durationFrames}>
              <Audio src={staticFile(audioFile)} volume={1.0} />
              <StoryCard story={story} />
              <SourceWatermark
                source={story.source}
                sourceUrl={story.sourceUrl}
              />
              <BroadcastHeader
                date={episode.formattedDate}
                region={story.region}
                isSpecialReport={story.importanceScore >= 90}
                storyIndex={storyIndex}
                totalStories={stories.length}
              />
            </Series.Sequence>
          );
        })}

        {/* HEADLINES RECAP SCENE (10 Seconds / 300 frames) */}
        <Series.Sequence durationInFrames={recapFrames}>
          <Audio
            src={staticFile(timings["recap"]?.audioFile ?? "audio/aibrief/s_recap.mp3")}
            volume={1.0}
          />
          <HeadlinesRecapScene stories={stories} />
          <BroadcastHeader
            date={episode.formattedDate}
            region="GLOBAL"
            isSpecialReport={true}
          />
        </Series.Sequence>

        {/* GLOBAL AI MARKET SNAPSHOT SCENE (15 Seconds / 450 frames) */}
        <Series.Sequence durationInFrames={marketSnapshotFrames}>
          <Audio
            src={staticFile(timings["market_snapshot"]?.audioFile ?? "audio/aibrief/s_market_snapshot.mp3")}
            volume={1.0}
          />
          <AIMarketSnapshotScene marketSnapshot={episode.marketSnapshot} />
          <BroadcastHeader
            date={episode.formattedDate}
            region="GLOBAL"
            isSpecialReport={false}
          />
        </Series.Sequence>

        {/* SCENE FINAL: OUTRO SCENE */}
        <Series.Sequence durationInFrames={outroFrames}>
          <Audio
            src={staticFile(timings["outro"]?.audioFile ?? "audio/aibrief/s_outro.mp3")}
            volume={1.0}
          />
          <OutroScene outro={episode.outro} />
          <BroadcastHeader
            date={episode.formattedDate}
            region="GLOBAL"
            isSpecialReport={false}
          />
        </Series.Sequence>
      </Series>

      {/* Burn-in Captions Overlay */}
      <BurnInCaptions enabled={true} />

      {/* Continuous Dynamic News Ticker */}
      <DynamicTicker items={episode.ticker} />
    </div>
  );
};
