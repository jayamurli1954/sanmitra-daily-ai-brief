import React from "react";
import {
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Story } from "../types";
import { UNSecurityCouncilMotion } from "./story-motions/UNSecurityCouncilMotion";
import { FoundationModelsMotion } from "./story-motions/FoundationModelsMotion";
import { HealthcareAccessMotion } from "./story-motions/HealthcareAccessMotion";
import { YouthAISafetyMotion } from "./story-motions/YouthAISafetyMotion";
import { AlibabaZhenwuMotion } from "./story-motions/AlibabaZhenwuMotion";
import { MaharashtraGovernanceMotion } from "./story-motions/MaharashtraGovernanceMotion";
import { MetaMuseMotion } from "./story-motions/MetaMuseMotion";
import { USChinaMotion } from "./story-motions/USChinaMotion";
import { UNDeclarationMotion } from "./story-motions/UNDeclarationMotion";
import { OpenAIStandardsMotion } from "./story-motions/OpenAIStandardsMotion";
import { DeepSeekHuaweiMotion } from "./story-motions/DeepSeekHuaweiMotion";
import { MicrosoftHyderabadMotion } from "./story-motions/MicrosoftHyderabadMotion";

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

/**
 * High-Density Multi-Cut Television Sequence (4-Second Cuts).
 * Strictly complies with:
 * • 75% Representative Visuals (People, Corporate HQs, Keynotes, Infrastructure)
 * • 15% Motion Graphics (Live camera slugs, HUD telemetry)
 * • 10% Text (Crisp lower third, no cluttered slides)
 * • Rapid scene transitions every 4.0 seconds (120 frames)
 */
export const getStoryVisualCuts = (story: Story): VisualCut[] => {
  // 1. If explicit visualCuts are provided in the episode data, strictly prioritize the single hero cut
  if (story.visualCuts && story.visualCuts.length > 0) {
    return [story.visualCuts[0]];
  }

  // 2. If heroImage or image is provided directly
  const heroImg = (story as any).heroImage || (story as any).image;
  if (heroImg) {
    return [
      {
        image: heroImg,
        badge: story.categoryTag || "SPECIAL REPORT",
        panDirection: "zoomIn",
      },
    ];
  }

  // 3. Fall back strictly to approved universal AI textures (NO random landmarks or stock people)
  return [
    {
      image: "aibrief/assets/fallbacks/default_ai_brain_ai.jpg",
      badge: `${story.region || "GLOBAL"} • AI INTELLIGENCE WIRE`,
      panDirection: "zoomIn",
    },
  ];
};

interface StoryCardProps {
  story: Story;
}

export const getStoryEntityLogo = (story: Story): { name: string; logo: string } | null => {
  const text = `${story.headline} ${story.script || ""} ${story.source || ""}`.toLowerCase();
  if (text.includes("openai") || text.includes("chatgpt")) {
    return { name: "OPENAI", logo: "aibrief/assets/logos/openai.svg" };
  }
  if (text.includes("hugging face") || text.includes("huggingface")) {
    return { name: "HUGGING FACE", logo: "aibrief/assets/logos/huggingface.svg" };
  }
  if (text.includes("nvidia")) {
    return { name: "NVIDIA", logo: "aibrief/assets/logos/nvidia.svg" };
  }
  if (text.includes("qantas")) {
    return { name: "QANTAS", logo: "aibrief/assets/logos/qantas.svg" };
  }
  if (text.includes("anthropic") || text.includes("claude")) {
    return { name: "ANTHROPIC", logo: "aibrief/assets/logos/anthropic.svg" };
  }
  if (text.includes("google") || text.includes("deepmind") || text.includes("gemini")) {
    return { name: "GOOGLE", logo: "aibrief/assets/logos/google.svg" };
  }
  if (text.includes("microsoft")) {
    return { name: "MICROSOFT", logo: "aibrief/assets/logos/microsoft.svg" };
  }
  if (text.includes("apple")) {
    return { name: "APPLE", logo: "aibrief/assets/logos/apple.svg" };
  }
  if (text.includes("meta") || text.includes("llama")) {
    return { name: "META", logo: "aibrief/assets/logos/meta.svg" };
  }
  if (text.includes("red hat") || text.includes("openshift")) {
    return { name: "RED HAT", logo: "aibrief/assets/logos/redhat.svg" };
  }
  if (text.includes("australia") || text.includes("australian") || text.includes("canberra")) {
    return { name: "AUSTRALIA", logo: "aibrief/assets/logos/australia.svg" };
  }
  if (text.includes("tencent")) {
    return { name: "TENCENT", logo: "aibrief/assets/logos/tencent.svg" };
  }
  if (text.includes("korea") || text.includes("seoul")) {
    return { name: "REPUBLIC OF KOREA", logo: "aibrief/assets/logos/south_korea.svg" };
  }
  if (text.includes("sarvam")) {
    return { name: "SARVAM AI", logo: "aibrief/assets/logos/sarvam.svg" };
  }
  if (text.includes("citi") || text.includes("citibank")) {
    return { name: "CITIBANK", logo: "aibrief/assets/logos/citibank.svg" };
  }
  if (text.includes("siemens")) {
    return { name: "SIEMENS", logo: "aibrief/assets/logos/siemens.svg" };
  }
  return null;
};

export const StoryCard: React.FC<StoryCardProps> = ({ story }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const entityLogo = getStoryEntityLogo(story);

  // Entrance animation for lower-third banner
  const textEntrance = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 85 },
  });

  // Single Authoritative Hero Cut Standard (Zero Multi-Cut Switching)
  const cuts = getStoryVisualCuts(story);
  const cutDuration = 999999;
  const totalCuts = 1;
  const currentCutIndex = 0;
  const nextCutIndex = 0;
  const currentCut = cuts[0];

  // keyPoints usually holds a truncated headline and the outlet name, which the
  // lower third already shows. Only surface a point that adds information.
  const headlineLower = (story.headline || "").toLowerCase();
  const focusPoint = (story.keyPoints || []).find((k) => {
    const t = (k || "").trim().toLowerCase();
    return (
      t.length > 0 &&
      !headlineLower.startsWith(t.slice(0, 40)) &&
      t !== (story.source || "").trim().toLowerCase()
    );
  });
  const nextCut = cuts[nextCutIndex];

  // Local frame progress: continuous over entire story when single cut, or 4-second cycles when multi-cut
  const localCutProgress =
    totalCuts > 1
      ? (frame % cutDuration) / cutDuration
      : interpolate(frame, [0, sceneDurationInFrames || 900], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

  // Crossfade between cuts only when multiple cuts exist
  const crossfade =
    totalCuts > 1
      ? interpolate(frame % cutDuration, [cutDuration - 12, cutDuration], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      : 0;

  // Cinematic Ken Burns Pan/Zoom calculation
  const getKenBurnsTransform = (cut: VisualCut, progress: number) => {
    let scale = 1.0;
    let translateX = 0;
    let translateY = 0;

    switch (cut.panDirection) {
      case "zoomIn":
        scale = interpolate(progress, [0, 1], [1.0, 1.08]);
        translateY = interpolate(progress, [0, 1], [0, -10]);
        break;
      case "zoomOut":
        scale = interpolate(progress, [0, 1], [1.08, 1.0]);
        translateY = interpolate(progress, [0, 1], [-10, 0]);
        break;
      case "panLeft":
        scale = 1.04;
        translateX = interpolate(progress, [0, 1], [20, -20]);
        break;
      case "panRight":
        scale = 1.04;
        translateX = interpolate(progress, [0, 1], [-20, 20]);
        break;
    }

    return `scale(${scale}) translate(${translateX}px, ${translateY}px)`;
  };

  // Optional motion graphic telemetry overlay during cut index 3 (seconds 12–16)
  const renderOptionalMotionGraphic = () => {
    if (currentCutIndex !== 3) return null;

    switch (story.id) {
      case "un_deepseek":
        return <UNSecurityCouncilMotion />;
      case "claude_gpt6_launch":
        return <FoundationModelsMotion />;
      case "healthcare_openevidence":
        return <HealthcareAccessMotion />;
      case "youth_ai_safety":
        return <YouthAISafetyMotion />;
      case "alibaba_zhenwu_v900":
        return <AlibabaZhenwuMotion />;
      case "maharashtra_ai_governance":
        return <MaharashtraGovernanceMotion />;
      case "india_ai_sovereign_gpus":
      case "microsoft_hyderabad":
        return <MicrosoftHyderabadMotion />;
      case "meta_muse":
        return <MetaMuseMotion />;
      case "us_china_talks":
        return <USChinaMotion />;
      case "un_declaration":
        return <UNDeclarationMotion />;
      case "openai_standards":
        return <OpenAIStandardsMotion />;
      case "deepseek_huawei":
        return <DeepSeekHuaweiMotion />;
      default:
        return null;
    }
  };

  return (
    <div
      style={{
        position: "relative",
        width: 1920,
        height: 1080,
        overflow: "hidden",
        backgroundColor: "#030712",
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      {/* ============================================================ */}
      {/* 1. HERO VISUAL CANVAS (Upper 76% of screen)                  */}
      {/* Rapidly rotates every 4.0 seconds between real-world visuals */}
      {/* ============================================================ */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 240,
          overflow: "hidden",
          backgroundColor: "#050b14",
        }}
      >
        {/* Layer A: Active Cut */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            overflow: "hidden",
            opacity: 1 - crossfade,
          }}
        >
          {currentCut.isPortrait ? (
            /* VIP Person Broadcast Card Presentation (e.g. Sam Altman, Dario Amodei, Jensen Huang) */
            <div
              style={{
                position: "absolute",
                inset: 0,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "80px 140px 40px 100px",
                background:
                  "radial-gradient(ellipse at 70% 50%, rgba(15, 23, 42, 0.95) 0%, rgba(3, 7, 18, 0.98) 100%)",
              }}
            >
              {/* Left Side: Television Key Quote / Leadership Statement */}
              <div style={{ maxWidth: 860 }}>
                <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 20 }}>
                  <div
                    style={{
                      display: "inline-block",
                      backgroundColor: "rgba(56, 189, 248, 0.15)",
                      border: "1px solid #38bdf8",
                      color: "#38bdf8",
                      fontSize: 12,
                      fontWeight: 900,
                      letterSpacing: 2,
                      padding: "5px 14px",
                      borderRadius: 4,
                    }}
                  >
                    {currentCut.companyTag || "EXECUTIVE TELEMETRY"}
                  </div>
                  <div
                    style={{
                      display: "inline-block",
                      backgroundColor: "rgba(239, 68, 68, 0.15)",
                      border: "1px solid #ef4444",
                      color: "#f87171",
                      fontSize: 11,
                      fontWeight: 900,
                      letterSpacing: 1.5,
                      padding: "5px 10px",
                      borderRadius: 4,
                    }}
                  >
                    NEWSMAKER
                  </div>
                </div>

                <div
                  style={{
                    position: "relative",
                    paddingLeft: 22,
                    borderLeft: "4px solid #38bdf8",
                    marginBottom: 24,
                  }}
                >
                  <div
                    style={{
                      color: "#94a3b8",
                      fontSize: 12,
                      fontWeight: 800,
                      letterSpacing: 1.5,
                      textTransform: "uppercase",
                      marginBottom: 10,
                    }}
                  >
                    {currentCut.quote ? "ON THE RECORD" : "IN THE NEWS"}
                  </div>
                  <blockquote
                    style={{
                      color: "#f8fafc",
                      fontSize: 30,
                      fontWeight: 700,
                      lineHeight: 1.35,
                      letterSpacing: -0.3,
                      margin: 0,
                      fontStyle: currentCut.quote ? "italic" : "normal",
                      maxWidth: 820,
                    }}
                  >
                    {/* Only a quote supplied with the cut is shown in quotation marks.
                        Story text is never presented as something an executive said. */}
                    {currentCut.quote ? `"${currentCut.quote}"` : story.headline}
                  </blockquote>
                </div>

                <div style={{ display: "flex", gap: 14 }}>
                  <div
                    style={{
                      backgroundColor: "rgba(255, 255, 255, 0.04)",
                      border: "1px solid rgba(255, 255, 255, 0.1)",
                      borderRadius: 6,
                      padding: "8px 16px",
                    }}
                  >
                    <div style={{ color: "#64748b", fontSize: 10, fontWeight: 800, letterSpacing: 1 }}>KEY POSITION</div>
                    <div style={{ color: "#e2e8f0", fontSize: 14, fontWeight: 700 }}>{currentCut.personTitle || "Industry Leadership"}</div>
                  </div>
                  <div
                    style={{
                      backgroundColor: "rgba(255, 255, 255, 0.04)",
                      border: "1px solid rgba(255, 255, 255, 0.1)",
                      borderRadius: 6,
                      padding: "8px 16px",
                    }}
                  >
                    <div style={{ color: "#64748b", fontSize: 10, fontWeight: 800, letterSpacing: 1 }}>SECTOR FOCUS</div>
                    <div style={{ color: "#38bdf8", fontSize: 14, fontWeight: 700 }}>{story.category?.toUpperCase() || "FRONTIER AI"}</div>
                  </div>
                </div>
              </div>

              {/* Right Side: High-Resolution Framed VIP Portrait */}
              <div
                style={{
                  position: "relative",
                  width: 380,
                  height: 480,
                  borderRadius: 16,
                  overflow: "hidden",
                  border: "2px solid rgba(56, 189, 248, 0.6)",
                  boxShadow: "0 20px 50px rgba(0, 0, 0, 0.9), 0 0 30px rgba(56, 189, 248, 0.2)",
                  transform: `scale(${interpolate(localCutProgress, [0, 1], [1.0, 1.04])})`,
                }}
              >
                <Img
                  src={staticFile(currentCut.image)}
                  style={{
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                  }}
                />
                {/* Person Title Overlay Banner at Bottom of Portrait */}
                <div
                  style={{
                    position: "absolute",
                    bottom: 0,
                    left: 0,
                    right: 0,
                    background:
                      "linear-gradient(to top, rgba(3, 7, 18, 0.98) 0%, rgba(3, 7, 18, 0.8) 70%, transparent 100%)",
                    padding: "24px 16px 14px 16px",
                  }}
                >
                  <div
                    style={{
                      color: "#ffffff",
                      fontSize: 18,
                      fontWeight: 950,
                      letterSpacing: 1,
                    }}
                  >
                    {currentCut.personName}
                  </div>
                  <div
                    style={{
                      color: "#38bdf8",
                      fontSize: 11,
                      fontWeight: 800,
                      letterSpacing: 1,
                    }}
                  >
                    {currentCut.personTitle}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Full-Bleed 16:9 Cinematic Photo / Stock Footage Canvas */
            <Img
              src={staticFile(currentCut.image)}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                objectPosition: "center 20%",
                transform: getKenBurnsTransform(currentCut, localCutProgress),
              }}
            />
          )}
        </div>

        {/* Layer B: Incoming Cut (Crossfading) */}
        {crossfade > 0 && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              overflow: "hidden",
              opacity: crossfade,
            }}
          >
            {nextCut.isPortrait ? (
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "80px 140px 40px 100px",
                  background:
                    "radial-gradient(ellipse at 70% 50%, rgba(15, 23, 42, 0.95) 0%, rgba(3, 7, 18, 0.98) 100%)",
                }}
              >
                <div style={{ maxWidth: 860 }}>
                  <div
                    style={{
                      display: "inline-block",
                      backgroundColor: "rgba(56, 189, 248, 0.15)",
                      border: "1px solid #38bdf8",
                      color: "#38bdf8",
                      fontSize: 12,
                      fontWeight: 900,
                      letterSpacing: 2,
                      padding: "4px 14px",
                      borderRadius: 4,
                      marginBottom: 16,
                    }}
                  >
                    {nextCut.companyTag || "EXECUTIVE TELEMETRY"}
                  </div>
                  <h2
                    style={{
                      color: "#ffffff",
                      fontSize: 42,
                      fontWeight: 950,
                      lineHeight: 1.15,
                      letterSpacing: -0.5,
                      margin: "0 0 16px 0",
                    }}
                  >
                    {story.headline}
                  </h2>
                </div>
                <div
                  style={{
                    position: "relative",
                    width: 380,
                    height: 480,
                    borderRadius: 16,
                    overflow: "hidden",
                    border: "2px solid rgba(56, 189, 248, 0.6)",
                  }}
                >
                  <Img
                    src={staticFile(nextCut.image)}
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                </div>
              </div>
            ) : (
              <Img
                src={staticFile(nextCut.image)}
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  objectPosition: "center 20%",
                  transform: getKenBurnsTransform(nextCut, 0),
                }}
              />
            )}
          </div>
        )}

        {/* Television Vignette & Subtle Scanlines */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            pointerEvents: "none",
            background:
              "radial-gradient(ellipse at center, rgba(3, 7, 18, 0.05) 0%, rgba(3, 7, 18, 0.55) 100%)",
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            pointerEvents: "none",
            backgroundImage:
              "linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%)",
            backgroundSize: "100% 4px",
            opacity: 0.1,
          }}
        />

        {/* Television Gradients */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: 140,
            background:
              "linear-gradient(to bottom, rgba(3, 7, 18, 0.92) 0%, rgba(3, 7, 18, 0.3) 65%, transparent 100%)",
            pointerEvents: "none",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: 180,
            background:
              "linear-gradient(to top, rgba(3, 7, 18, 0.98) 0%, rgba(3, 7, 18, 0.4) 60%, transparent 100%)",
            pointerEvents: "none",
          }}
        />

        {/* ======================================================== */}
        {/* 2. BROADCAST TELEVISION SLUG & TELEMETRY                */}
        {/* ======================================================== */}
        <div
          style={{
            position: "absolute",
            top: 86,
            left: 56,
            display: "flex",
            flexDirection: "column",
            gap: 8,
            zIndex: 20,
          }}
        >
          {/* Live Feed Row */}
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                backgroundColor: "rgba(15, 23, 42, 0.88)",
                border: "1px solid rgba(56, 189, 248, 0.5)",
                borderRadius: 6,
                padding: "5px 14px",
                backdropFilter: "blur(12px)",
              }}
            >
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  backgroundColor: "#ef4444",
                  boxShadow: "0 0 10px #ef4444",
                }}
              />
              <span
                style={{
                  color: "#ffffff",
                  fontSize: 17,
                  fontWeight: 900,
                  letterSpacing: 2,
                }}
              >
                LIVE FEED
              </span>
            </div>

            {/* Dynamic Camera Cut Badge */}
            <div
              style={{
                backgroundColor: "rgba(4, 8, 18, 0.88)",
                border: "1px solid rgba(255, 255, 255, 0.2)",
                borderRadius: 6,
                padding: "5px 16px",
                backdropFilter: "blur(12px)",
              }}
            >
              <span
                style={{
                  color: "#7dd3fc",
                  fontSize: 17,
                  fontWeight: 800,
                  letterSpacing: 1.5,
                }}
              >
                {currentCut.badge}
              </span>
            </div>
          </div>

          {/* Key Intel Sub-Slug */}
          {focusPoint && (
            <div
              style={{
                backgroundColor: "rgba(15, 23, 42, 0.85)",
                border: "1px solid rgba(251, 191, 36, 0.4)",
                borderRadius: 6,
                padding: "4px 14px",
                backdropFilter: "blur(12px)",
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                maxWidth: 900,
              }}
            >
              <span style={{ color: "#fbbf24", fontSize: 16, fontWeight: 900 }}>
                ⚡ FOCUS:
              </span>
              <span
                style={{
                  color: "#ffffff",
                  fontSize: 17,
                  fontWeight: 700,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {focusPoint}
              </span>
            </div>
          )}
        </div>

        {/* On-Screen Television Brand / Entity Bug (Top Right) */}
        {entityLogo && (
          <div
            style={{
              position: "absolute",
              top: 86,
              right: 56,
              display: "flex",
              alignItems: "center",
              gap: 12,
              backgroundColor: "rgba(4, 8, 18, 0.9)",
              border: "1px solid rgba(56, 189, 248, 0.45)",
              borderRadius: 8,
              padding: "6px 16px",
              backdropFilter: "blur(14px)",
              zIndex: 25,
              boxShadow: "0 10px 30px rgba(0, 0, 0, 0.75)",
            }}
          >
            <Img
              src={staticFile(entityLogo.logo)}
              style={{
                height: 28,
                width: "auto",
                maxWidth: 90,
                objectFit: "contain",
              }}
            />
            <span
              style={{
                color: "#ffffff",
                fontSize: 16,
                fontWeight: 900,
                letterSpacing: 1.5,
              }}
            >
              {entityLogo.name}
            </span>
          </div>
        )}

        {/* Motion Graphic Overlay Layer (Layered during cut index 3) */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            zIndex: 15,
            pointerEvents: "none",
            opacity: 0.85,
          }}
        >
          {renderOptionalMotionGraphic()}
        </div>
      </div>

      {/* ============================================================ */}
      {/* 3. REUTERS / BLOOMBERG LOWER THIRD (y: 810 to 1020)          */}
      {/* ============================================================ */}
      <div
        style={{
          position: "absolute",
          top: 810,
          left: 0,
          right: 0,
          height: 210,
          backgroundColor: "rgba(4, 8, 18, 0.97)",
          borderTop: "2px solid rgba(56, 189, 248, 0.55)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 56px",
          zIndex: 35,
          boxShadow: "0 -16px 40px rgba(0, 0, 0, 0.95)",
          transform: `translateY(${(1 - textEntrance) * 20}px)`,
          opacity: textEntrance,
        }}
      >
        {/* Left Column: Category Pill, Headline, Context & Why This Matters */}
        <div style={{ maxWidth: focusPoint ? 1340 : 1800 }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              marginBottom: 6,
            }}
          >
            <div
              style={{
                backgroundColor: "#dc2626",
                color: "#ffffff",
                padding: "4px 14px",
                borderRadius: 4,
                fontSize: 16,
                fontWeight: 900,
                letterSpacing: 2,
              }}
            >
              {story.region}
            </div>

            {story.categoryTag && (
              <div
                style={{
                  backgroundColor: "rgba(56, 189, 248, 0.15)",
                  border: "1px solid #38bdf8",
                  color: "#7dd3fc",
                  padding: "4px 14px",
                  borderRadius: 4,
                  fontSize: 16,
                  fontWeight: 800,
                  letterSpacing: 1,
                }}
              >
                {story.categoryTag}
              </div>
            )}

            <div
              style={{
                color: "#e2e8f0",
                fontSize: 16,
                fontWeight: 700,
                letterSpacing: 0.8,
              }}
            >
              REPORTED BY:{" "}
              <span style={{ color: "#ffffff", fontWeight: 900 }}>
                {story.source}
              </span>
            </div>
          </div>

          <h1
            style={{
              color: "#ffffff",
              fontSize: 38,
              fontWeight: 950,
              letterSpacing: -0.5,
              lineHeight: 1.15,
              margin: "0 0 6px 0",
              textShadow: "0 2px 12px rgba(0,0,0,0.9)",
            }}
          >
            {story.headline}
          </h1>

          {story.historicalContext && (
            <div
              style={{
                color: "#f1f5f9",
                fontSize: 19,
                fontWeight: 600,
                lineHeight: 1.3,
                marginBottom: 6,
                display: "-webkit-box",
                WebkitLineClamp: 1,
                WebkitBoxOrient: "vertical",
                overflow: "hidden",
              }}
            >
              <span style={{ color: "#38bdf8", fontWeight: 800 }}>
                CONTEXT:{" "}
              </span>
              {story.historicalContext}
            </div>
          )}

          {story.whyThisMatters && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                backgroundColor: "rgba(245, 158, 11, 0.18)",
                borderLeft: "4px solid #f59e0b",
                padding: "5px 14px",
                borderRadius: "0 4px 4px 0",
              }}
            >
              <span
                style={{
                  color: "#fbbf24",
                  fontSize: 16,
                  fontWeight: 900,
                  letterSpacing: 1,
                  whiteSpace: "nowrap",
                }}
              >
                WHY THIS MATTERS:
              </span>
              <span
                style={{
                  color: "#fffbeb",
                  fontSize: 19,
                  fontWeight: 700,
                  display: "-webkit-box",
                  WebkitLineClamp: 1,
                  WebkitBoxOrient: "vertical",
                  overflow: "hidden",
                }}
              >
                {story.whyThisMatters}
              </span>
            </div>
          )}
        </div>

        {/* Right Column: Key Metric Callout Card */}
        {focusPoint && (
          <div
            style={{
              width: 380,
              backgroundColor: "rgba(15, 23, 42, 0.8)",
              border: "1px solid rgba(56, 189, 248, 0.3)",
              borderRadius: 8,
              padding: "14px 18px",
              display: "flex",
              flexDirection: "column",
              gap: 8,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <div
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  backgroundColor: "#38bdf8",
                }}
              />
              <span
                style={{
                  color: "#e2e8f0",
                  fontSize: 15,
                  fontWeight: 800,
                  letterSpacing: 1.5,
                }}
              >
                STRATEGIC FOCUS
              </span>
            </div>
            <div
              style={{
                color: "#ffffff",
                fontSize: 18,
                fontWeight: 700,
                lineHeight: 1.35,
              }}
            >
              {focusPoint}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
