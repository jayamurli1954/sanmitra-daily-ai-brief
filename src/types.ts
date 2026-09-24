export const VIDEO_FPS = 30;
export const VIDEO_WIDTH = 1920;
export const VIDEO_HEIGHT = 1080;
export const VERTICAL_WIDTH = 1080;
export const VERTICAL_HEIGHT = 1920;

// 36 seconds total = 1080 frames
export const VIDEO_DURATION_IN_FRAMES = 1080;

export const SCENE_TIMINGS = {
  SCENE_1: {
    START: 0,
    DURATION: 300, // 0 - 10s (0 - 300)
  },
  SCENE_2: {
    START: 300,
    DURATION: 450, // 10 - 25s (300 - 750)
  },
  SCENE_3: {
    START: 750,
    DURATION: 330, // 25 - 36s (750 - 1080)
  },
} as const;
