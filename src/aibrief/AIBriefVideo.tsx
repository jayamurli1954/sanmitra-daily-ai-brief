import React from "react";
import { Audio, Series, staticFile } from "remotion";
import { AIBriefEpisode } from "./types";
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
import { getBroadcastScenes, TimelineScene } from "./timingsHelper";

const episode = episodeData as unknown as AIBriefEpisode;
const timings = rawTimings as any;

export const AIBriefVideo: React.FC = () => {
  const scenes: TimelineScene[] = getBroadcastScenes(episode, timings);

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
        {scenes.map((scene, idx) => {
          switch (scene.type) {
            case "intro":
              return (
                <Series.Sequence
                  key={`intro_${idx}`}
                  durationInFrames={scene.durationInFrames}
                >
                  {scene.audioFile && (
                    <Audio src={staticFile(scene.audioFile)} volume={1.0} />
                  )}
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
              );

            case "sponsor":
              return episode.sponsor ? (
                <Series.Sequence
                  key={`sponsor_${idx}`}
                  durationInFrames={scene.durationInFrames}
                >
                  <SponsorSlot sponsor={episode.sponsor} />
                  <BroadcastHeader
                    date={episode.formattedDate}
                    region="GLOBAL"
                    isSpecialReport={false}
                  />
                </Series.Sequence>
              ) : null;

            case "transition":
              return (
                <Series.Sequence
                  key={`trans_${scene.id}_${idx}`}
                  durationInFrames={scene.durationInFrames}
                >
                  <SectionTransition
                    region={scene.transition?.region || "GLOBAL"}
                    title={scene.transition?.title || ""}
                    display={scene.transition?.display || ""}
                  />
                  <BroadcastHeader
                    date={episode.formattedDate}
                    region={scene.transition?.region || "GLOBAL"}
                    isSpecialReport={false}
                  />
                </Series.Sequence>
              );

            case "story":
              if (!scene.story) return null;
              return (
                <Series.Sequence
                  key={`story_${scene.id}_${idx}`}
                  durationInFrames={scene.durationInFrames}
                >
                  {scene.audioFile && (
                    <Audio src={staticFile(scene.audioFile)} volume={1.0} />
                  )}
                  <StoryCard story={scene.story} />
                  <SourceWatermark
                    source={scene.story.source}
                    sourceUrl={scene.story.sourceUrl}
                  />
                  <BroadcastHeader
                    date={episode.formattedDate}
                    region={scene.story.region}
                    isSpecialReport={scene.story.importanceScore >= 90}
                    storyIndex={scene.storyIndex}
                    totalStories={scene.totalStories}
                  />
                </Series.Sequence>
              );

            case "recap":
              return (
                <Series.Sequence
                  key={`recap_${idx}`}
                  durationInFrames={scene.durationInFrames}
                >
                  {scene.audioFile && (
                    <Audio src={staticFile(scene.audioFile)} volume={1.0} />
                  )}
                  <HeadlinesRecapScene stories={episode.stories} />
                  <BroadcastHeader
                    date={episode.formattedDate}
                    region="GLOBAL"
                    isSpecialReport={true}
                  />
                </Series.Sequence>
              );

            case "market_snapshot":
              return (
                <Series.Sequence
                  key={`market_${idx}`}
                  durationInFrames={scene.durationInFrames}
                >
                  {scene.audioFile && (
                    <Audio src={staticFile(scene.audioFile)} volume={1.0} />
                  )}
                  <AIMarketSnapshotScene
                    marketSnapshot={episode.marketSnapshot}
                  />
                  <BroadcastHeader
                    date={episode.formattedDate}
                    region="GLOBAL"
                    isSpecialReport={false}
                  />
                </Series.Sequence>
              );

            case "outro":
              return (
                <Series.Sequence
                  key={`outro_${idx}`}
                  durationInFrames={scene.durationInFrames}
                >
                  {scene.audioFile && (
                    <Audio src={staticFile(scene.audioFile)} volume={1.0} />
                  )}
                  <OutroScene outro={episode.outro} />
                  <BroadcastHeader
                    date={episode.formattedDate}
                    region="GLOBAL"
                    isSpecialReport={false}
                  />
                </Series.Sequence>
              );

            default:
              return null;
          }
        })}
      </Series>

      {/* Burn-in Captions Overlay */}
      <BurnInCaptions enabled={true} />

      {/* Continuous Dynamic News Ticker */}
      <DynamicTicker items={episode.ticker} />
    </div>
  );
};
