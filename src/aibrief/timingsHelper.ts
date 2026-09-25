import rawTimings from "./data/timings.json";
import rawEpisode from "./data/active_episode.json";
import { AIBriefEpisode, Story, TransitionItem } from "./types";

interface TimingItem {
  audioFile?: string;
  audioDurationSeconds?: number;
  sceneDurationSeconds?: number;
  durationInFrames: number;
  title?: string;
}

export type SceneType =
  | "intro"
  | "sponsor"
  | "transition"
  | "story"
  | "recap"
  | "market_snapshot"
  | "outro";

export interface TimelineScene {
  id: string;
  type: SceneType;
  story?: Story;
  storyIndex?: number;
  totalStories?: number;
  transition?: TransitionItem;
  durationInFrames: number;
  audioFile?: string;
}

export const getBroadcastScenes = (
  episode: AIBriefEpisode = rawEpisode as unknown as AIBriefEpisode,
  timings: Record<string, TimingItem> = rawTimings as unknown as Record<string, TimingItem>
): TimelineScene[] => {
  const scenes: TimelineScene[] = [];
  const stories = episode.stories || [];

  // 1. Intro
  scenes.push({
    id: "intro",
    type: "intro",
    durationInFrames: timings["intro"]?.durationInFrames ?? 450,
    audioFile: timings["intro"]?.audioFile || "audio/aibrief/s0_intro.mp3",
  });

  // Optional Sponsor
  if (episode.sponsor?.enabled) {
    scenes.push({
      id: "sponsor",
      type: "sponsor",
      durationInFrames: (episode.sponsor.durationSeconds || 6) * 30,
    });
  }

  // Transitions lookup by region
  const transitionsByRegion: Record<string, TransitionItem> = {};
  episode.transitions?.forEach((t) => {
    transitionsByRegion[t.region] = t;
  });

  // 2. Stories with regional transitions
  stories.forEach((story, idx) => {
    if (idx > 0 && stories[idx - 1].region !== story.region) {
      const trans = transitionsByRegion[story.region];
      if (trans) {
        const transFrames =
          timings[trans.id]?.durationInFrames ??
          (trans.durationSeconds ? trans.durationSeconds * 30 : 60);
        scenes.push({
          id: trans.id,
          type: "transition",
          transition: trans,
          durationInFrames: transFrames,
        });
      }
    }

    const storyIndex = idx + 1;
    const timing = timings[story.id];
    const durationFrames = timing?.durationInFrames ?? 600;
    const audioFile =
      timing?.audioFile || `audio/aibrief/s${storyIndex}_${story.id}.mp3`;

    scenes.push({
      id: story.id,
      type: "story",
      story,
      storyIndex,
      totalStories: stories.length,
      durationInFrames: durationFrames,
      audioFile,
    });
  });

  // 3. Recap
  scenes.push({
    id: "recap",
    type: "recap",
    durationInFrames: timings["recap"]?.durationInFrames ?? 300,
    audioFile: timings["recap"]?.audioFile || "audio/aibrief/s_recap.mp3",
  });

  // 4. Market Snapshot
  scenes.push({
    id: "market_snapshot",
    type: "market_snapshot",
    durationInFrames: timings["market_snapshot"]?.durationInFrames ?? 450,
    audioFile:
      timings["market_snapshot"]?.audioFile || "audio/aibrief/s_market_snapshot.mp3",
  });

  // 5. Outro
  scenes.push({
    id: "outro",
    type: "outro",
    durationInFrames: timings["outro"]?.durationInFrames ?? 390,
    audioFile: timings["outro"]?.audioFile || "audio/aibrief/s_outro.mp3",
  });

  return scenes;
};

export const getAIBriefTotalFrames = (): number => {
  try {
    const scenes = getBroadcastScenes();
    return scenes.reduce((sum, s) => sum + s.durationInFrames, 0);
  } catch {
    return 4990;
  }
};
