export const LEGAL_FPS = 30;
export const LEGAL_WIDTH = 1920;
export const LEGAL_HEIGHT = 1080;
export const LEGAL_VERTICAL_WIDTH = 1080;
export const LEGAL_VERTICAL_HEIGHT = 1920;

// 38 seconds total = 1140 frames
export const LEGAL_DURATION_IN_FRAMES = 1140;

export const LEGAL_SCENE_TIMINGS = {
  SCENE_1_HOOK: {
    START: 0,
    DURATION: 210, // 0s - 7s
  },
  SCENE_2_DIFFERENTIATOR: {
    START: 210,
    DURATION: 310, // 7s - 17.33s (BNS/BNSS crosswalk + Not An AI Chatbot)
  },
  SCENE_3_WORKFLOW: {
    START: 520,
    DURATION: 290, // 17.33s - 27s (Outcomes & Real UI Workflow)
  },
  SCENE_4_CTA: {
    START: 810,
    DURATION: 330, // 27s - 38s (Streamlined High-Converting CTA)
  },
} as const;
