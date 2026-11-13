import React from "react";
import { Audio, Series, staticFile } from "remotion";
import { AIBriefEpisode } from "./types";
import episodeData from "./data/active_episode.json";
import rawTimings from "./data/timings.json";
import { CleanStoryCard } from "./components/CleanStoryCard";
import { BurnInCaptions } from "./components/BurnInCaptions";
import { CleanIntroScene } from "./scenes/CleanIntroScene";
import { OutroScene } from "./scenes/OutroScene";
import { SectionTransition } from "./components/SectionTransition";
import { HeadlinesRecapScene } from "./scenes/HeadlinesRecapScene";
import { AIMarketSnapshotScene } from "./scenes/AIMarketSnapshotScene";
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
        src={staticFile("audio/aibrief_theme.mp3")}
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
                  <CleanIntroScene
                    formattedDate={episode.formattedDate}
                    headlines={
                      ((episode.intro as any)?.headlines as string[] | undefined) ??
                      episode.stories.map((s) => s.headline)
                    }
                    leadImage={episode.stories[0]?.visualCuts?.[0]?.image}
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
                  <CleanStoryCard story={scene.story} />
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
                </Series.Sequence>
              );

            default:
              return null;
          }
        })}
      </Series>

      {/* Captions: the episode's only captions (no subtitle file is uploaded) */}
      <BurnInCaptions enabled={true} />

    </div>
  );
};
