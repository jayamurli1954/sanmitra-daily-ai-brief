import rawTimings from "./data/timings.json";

interface TimingItem {
  durationInFrames: number;
}

export const getAIBriefTotalFrames = (): number => {
  try {
    const timings = rawTimings as unknown as Record<string, TimingItem>;
    const total = Object.values(timings).reduce(
      (sum, item) => sum + (item.durationInFrames || 0),
      0
    );
    return total > 0 ? total : 4990;
  } catch {
    return 4990;
  }
};
