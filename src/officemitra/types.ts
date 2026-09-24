export const OM_FPS = 30;

// Dimensions
export const OM_WIDTH = 1920;
export const OM_HEIGHT = 1080;

export const OM_SQUARE_SIZE = 1080;

export const OM_VERTICAL_WIDTH = 1080;
export const OM_VERTICAL_HEIGHT = 1920;

// Scene frame durations (30 fps)
export const SCENE_00_PROLOGUE_FRAMES = 90;       // 3.0s  (0 - 3s)
export const SCENE_01_PROBLEM_FRAMES = 390;        // 13.0s (3 - 16s)
export const SCENE_02_CHAOS_FRAMES = 240;          // 8.0s  (16 - 24s)
export const SCENE_03_INTRO_FRAMES = 255;          // 8.5s  (24 - 32.5s)
export const SCENE_04_PORTAL_FRAMES = 285;         // 9.5s  (32.5 - 42s)
export const SCENE_05_EXTRACTION_FRAMES = 270;     // 9.0s  (42 - 51s)
export const SCENE_06_SSDV_FRAMES = 315;           // 10.5s (51 - 61.5s)
export const SCENE_06A_FACTORY_FRAMES = 300;       // 10.0s (61.5 - 71.5s)
export const SCENE_07_REVIEW_FRAMES = 375;         // 12.5s (71.5 - 84s)
export const SCENE_08_WORKING_PAPERS_FRAMES = 255; // 8.5s  (84 - 92.5s)
export const SCENE_09_ADVISORY_FRAMES = 345;       // 11.5s (92.5 - 104s)
export const SCENE_10_COMMAND_CENTER_FRAMES = 300; // 10.0s (104 - 114s)
export const SCENE_11_FINALE_FRAMES = 300;         // 10.0s (114 - 124s)

export const OM_TOTAL_FRAMES =
  SCENE_00_PROLOGUE_FRAMES +
  SCENE_01_PROBLEM_FRAMES +
  SCENE_02_CHAOS_FRAMES +
  SCENE_03_INTRO_FRAMES +
  SCENE_04_PORTAL_FRAMES +
  SCENE_05_EXTRACTION_FRAMES +
  SCENE_06_SSDV_FRAMES +
  SCENE_06A_FACTORY_FRAMES +
  SCENE_07_REVIEW_FRAMES +
  SCENE_08_WORKING_PAPERS_FRAMES +
  SCENE_09_ADVISORY_FRAMES +
  SCENE_10_COMMAND_CENTER_FRAMES +
  SCENE_11_FINALE_FRAMES; // 3720 frames = 124 seconds

// Official Brand & Contact
export const OM_BRAND = {
  name: "OfficeMitra + SSDV",
  taglinePrimary: "The AI Operating System for Modern CA Firms",
  taglineSupporting: "The Accounting Intelligence Platform for Chartered Accountants",
  pillars: ["Collect", "Account", "Review", "Advise"],
  email: "contact@sanmitratech.in",
  website: "www.sanmitratech.in",
  whatsapp: "+91 79049 42915",
};
