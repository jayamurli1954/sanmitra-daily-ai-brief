export type Region = "WORLD" | "ASIA" | "USA" | "CHINA" | "INDIA" | "GLOBAL";
export type ImpactLevel = "Critical" | "High" | "Medium";

export interface VisualCut {
  image: string;
  badge: string;
  panDirection: "zoomIn" | "zoomOut" | "panLeft" | "panRight";
  isPortrait?: boolean;
  personName?: string;
  personTitle?: string;
  companyTag?: string;
  quote?: string;
}

export interface Story {
  id: string;
  region: Region;
  category?: string;
  categoryTag?: string;
  historicalContext?: string;
  whyThisMatters?: string;
  significance?: string;
  impact?: ImpactLevel;
  headline: string;
  subheadline?: string;
  importanceScore: number;
  durationSeconds: number;
  source: string;
  sourceUrl: string;
  sourceType?: "company" | "reporting";
  script: string;
  keyPoints: string[];
  visualAsset?: string;
  visualCuts?: VisualCut[];
}

export interface TransitionItem {
  id: string;
  region: Region;
  title: string;
  display: string;
  durationSeconds: number;
}

export interface TransitionConfig {
  durationSeconds: number;
  headline: string;
  subheadline?: string;
  script?: string;
}

export interface MarketSnapshotEntity {
  name: string;
  update: string;
  tag: string;
  color: string;
}

export interface MarketSnapshotConfig {
  durationSeconds: number;
  headline: string;
  subheadline: string;
  script: string;
  entities: MarketSnapshotEntity[];
}

export interface RecapConfig {
  durationSeconds: number;
  headline: string;
  script?: string;
  items?: string[];
}

export interface IntroConfig {
  durationSeconds: number;
  headline: string;
  subheadline: string;
  script: string;
}

export interface OutroConfig {
  durationSeconds: number;
  headline: string;
  subheadline?: string;
  script: string;
  cta?: string;
  bureaus?: string[];
  channels?: string[];
}

export interface SponsorConfig {
  enabled: boolean;
  sponsorName: string;
  tagline: string;
  callToAction: string;
  script: string;
  durationSeconds: number;
  logo?: string;
}

export interface ThumbnailVariant {
  mainHeadline: string;
  badge: string;
  secondaryHeadline: string;
  subTag: string;
}

export interface ThumbnailConfig {
  brand: string;
  date: string;
  mainHeadline: string;
  secondaryHeadline: string;
  subTag: string;
  badge: string;
  variants?: {
    A: ThumbnailVariant;
    B: ThumbnailVariant;
    C: ThumbnailVariant;
  };
}

export interface AIBriefEpisode {
  date: string; // YYYY-MM-DD
  formattedDate: string; // e.g. 23 September 2026
  title: string;
  intro: IntroConfig;
  sponsor?: SponsorConfig;
  transitions?: TransitionItem[];
  stories: Story[];
  midTransition?: TransitionConfig;
  marketSnapshot?: MarketSnapshotConfig;
  recap?: RecapConfig;
  outro: OutroConfig;
  thumbnail?: ThumbnailConfig;
  ticker: string[];
  youtubeMetadata?: {
    title: string;
    descriptionIntro: string;
    tags: string[];
  };
}

export interface TimingMap {
  [sceneId: string]: {
    durationInFrames: number;
    durationInSeconds: number;
    audioFile: string;
    title: string;
  };
}
