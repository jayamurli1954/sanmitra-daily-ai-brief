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
  // 1. If explicit visualCuts are provided in the episode data, prioritize them
  if (story.visualCuts && story.visualCuts.length > 0) {
    return story.visualCuts;
  }

  // 2. Pre-defined story visual treatments
  switch (story.id) {
    case "gpt6_astra_launch":
      return [
        {
          image: "aibrief/assets/story1_openai_stage.jpg",
          badge: "OPENAI KEYNOTE AUDITORIUM • GLOBAL PREVIEW",
          panDirection: "zoomIn",
        },
        {
          image: "aibrief/assets/editorial/person_sam_altman.jpg",
          badge: "LEADERSHIP BRIEFING • FRONTIER LAB",
          panDirection: "zoomIn",
          isPortrait: true,
          personName: "SAM ALTMAN",
          personTitle: "CHIEF EXECUTIVE OFFICER, OPENAI",
          companyTag: "OPENAI • SAN FRANCISCO, CA",
          quote: "Frontier systems are transitioning from conversational assistants to goal-directed autonomous agents operating across enterprise environments.",
        },
        {
          image: "aibrief/assets/story1_code_agents.jpg",
          badge: "AUTONOMOUS RUNTIME • MULTI-STEP WORKFLOWS",
          panDirection: "panRight",
        },
        {
          image: "aibrief/backgrounds/ai_chips.jpg",
          badge: "NEURAL ACCELERATOR FABRICATION • ENTERPRISE SCALE",
          panDirection: "zoomOut",
        },
        {
          image: "aibrief/assets/story1_datacenter.jpg",
          badge: "HYPERSCALE COMPUTE CORRIDOR • DEVDAY ROADMAP",
          panDirection: "panLeft",
        },
        {
          image: "aibrief/assets/story6_network_grid.jpg",
          badge: "ENTERPRISE AUTOMATION BENCHMARK • 2026",
          panDirection: "zoomIn",
        },
      ];

    case "anthropic_accenture_safety":
      return [
        {
          image: "aibrief/assets/story2_cyber_defense.jpg",
          badge: "CYBER DEFENSE OPERATIONS • $1B ALLIANCE",
          panDirection: "zoomIn",
        },
        {
          image: "aibrief/assets/editorial/person_dario_amodei.jpg",
          badge: "AI SAFETY ARCHITECTURE • LEADERSHIP",
          panDirection: "zoomIn",
          isPortrait: true,
          personName: "DARIO AMODEI",
          personTitle: "CHIEF EXECUTIVE OFFICER, ANTHROPIC",
          companyTag: "ANTHROPIC • SAN FRANCISCO, CA",
          quote: "As agentic AI models acquire system authority, verifiable mathematical safety guardrails become the foundational imperative for global industry.",
        },
        {
          image: "aibrief/backgrounds/ai_security.jpg",
          badge: "INTELLIGENCE DESK • EMBEDDED EVALUATOR SQUADS",
          panDirection: "panLeft",
        },
        {
          image: "aibrief/assets/story2_security_audit.jpg",
          badge: "THREAT INTELLIGENCE • DISRUPTED EXPLOIT VECTORS",
          panDirection: "zoomOut",
        },
        {
          image: "aibrief/assets/story2_corporate_boardroom.jpg",
          badge: "ACCENTURE GLOBAL DEPLOYMENT • 5-YEAR PACT",
          panDirection: "panRight",
        },
      ];

    case "gemini_live_thinking":
      return [
        {
          image: "aibrief/assets/story3_deepmind_lab.jpg",
          badge: "GOOGLE DEEPMIND • ADVANCED REASONING LAB",
          panDirection: "zoomIn",
        },
        {
          image: "aibrief/assets/editorial/person_sundar_pichai.jpg",
          badge: "EXECUTIVE STRATEGY • SYSTEMS SCALING",
          panDirection: "zoomIn",
          isPortrait: true,
          personName: "SUNDAR PICHAI",
          personTitle: "CHIEF EXECUTIVE OFFICER, ALPHABET & GOOGLE",
          companyTag: "GOOGLE DEEPMIND • MOUNTAIN VIEW, CA",
          quote: "By coupling real-time multimodal reasoning with deep reflection loops, frontier intelligence can solve problems previously beyond algorithmic reach.",
        },
        {
          image: "aibrief/assets/story3_neural_network.jpg",
          badge: "MULTIMODAL ARCHITECTURE • EXTENDED THINKING",
          panDirection: "zoomOut",
        },
        {
          image: "aibrief/assets/story3_economic_data.jpg",
          badge: "AI & ECONOMY ATLAS • LABOR MARKET TRANSFORMATION",
          panDirection: "panRight",
        },
        {
          image: "aibrief/backgrounds/cloud_infrastructure.jpg",
          badge: "AI HYPERCOMPUTER TPU FABRIC • CLOUD SCALE",
          panDirection: "panLeft",
        },
      ];

    case "nvidia_isaac_quantum":
      return [
        {
          image: "aibrief/assets/story4_nvidia_robotics.jpg",
          badge: "PHYSICAL AI • INDUSTRIAL ROBOTICS AUTOMATION",
          panDirection: "zoomIn",
        },
        {
          image: "aibrief/assets/editorial/person_jensen_huang.jpg",
          badge: "ACCELERATED COMPUTING • FOUNDER & CEO",
          panDirection: "zoomIn",
          isPortrait: true,
          personName: "JENSEN HUANG",
          personTitle: "PRESIDENT & CEO, NVIDIA",
          companyTag: "NVIDIA • SANTA CLARA, CA",
          quote: "The next wave of artificial intelligence is Physical AI. Robotics and digital twins running on accelerated computing will redefine modern manufacturing.",
        },
        {
          image: "aibrief/assets/story4_quantum_qpu.jpg",
          badge: "IONQ ALLIANCE • QUANTUM PROCESSING UNIT",
          panDirection: "panRight",
        },
        {
          image: "aibrief/assets/story4_autonomous_robot.jpg",
          badge: "ISAAC ROS 5.0 • AUTONOMOUS AGENT PIPELINE",
          panDirection: "zoomOut",
        },
        {
          image: "aibrief/backgrounds/ai_chips.jpg",
          badge: "TENSOR CORE HARDWARE • DSX READY STANDARD",
          panDirection: "panLeft",
        },
      ];

    case "us_senate_agent_probe":
      return [
        {
          image: "aibrief/assets/editorial/gov_canberra_parliament.jpg",
          badge: "PARLIAMENT HOUSE • BIPARTISAN OVERSIGHT",
          panDirection: "zoomIn",
        },
        {
          image: "aibrief/assets/story5_hearing_room.jpg",
          badge: "SENATE COMMITTEE CHAMBER • INCIDENT DISCLOSURE",
          panDirection: "panLeft",
        },
        {
          image: "aibrief/assets/story5_cyber_alert.jpg",
          badge: "NETWORK ACCESS AUDIT • AGENT CREDENTIAL PERMISSIONS",
          panDirection: "zoomOut",
        },
        {
          image: "aibrief/backgrounds/ai_standards.jpg",
          badge: "CONGRESSIONAL DELIBERATIONS • CISO TESTIMONY",
          panDirection: "panRight",
        },
        {
          image: "aibrief/backgrounds/global_policy.jpg",
          badge: "MANDATORY REPORTING PROTOCOLS • 2026 STANDARDS",
          panDirection: "zoomIn",
        },
      ];

    case "india_ai_sovereign_gpus":
      return [
        {
          image: "aibrief/assets/story6_datacenter_servers.jpg",
          badge: "SOVEREIGN COMPUTE • 38,000+ GPUS ONBOARDED",
          panDirection: "zoomIn",
        },
        {
          image: "aibrief/assets/story6_network_grid.jpg",
          badge: "MINISTRY OF ELECTRONICS & IT • NEW DELHI",
          panDirection: "zoomOut",
        },
        {
          image: "aibrief/backgrounds/cloud_infrastructure.jpg",
          badge: "HYDERABAD TECH CORRIDOR • ASIA CLOUD REGION",
          panDirection: "panRight",
        },
        {
          image: "aibrief/assets/story6_indian_engineers.jpg",
          badge: "INDIAAI MISSION • RESEARCH PUBLIC UTILITY",
          panDirection: "zoomIn",
        },
        {
          image: "aibrief/assets/story6_network_grid.jpg",
          badge: "NATIONAL AI INFRASTRUCTURE & SEMICON INDIA",
          panDirection: "panLeft",
        },
      ];

    // Archived stories
    case "un_deepseek":
      return [
        {
          image: "aibrief/backgrounds/global_policy.jpg",
          badge: "UN GENERAL ASSEMBLY • NEW YORK HEADQUARTERS",
          panDirection: "zoomIn",
        },
        {
          image: "aibrief/assets/editorial/person_sam_altman.jpg",
          badge: "UNSC EXPERT WITNESS • OPENAI",
          panDirection: "zoomIn",
          isPortrait: true,
          personName: "SAM ALTMAN",
          personTitle: "CEO, OPENAI",
          companyTag: "UNITED NATIONS SECURITY COUNCIL",
        },
        {
          image: "aibrief/assets/editorial/person_dario_amodei.jpg",
          badge: "UNSC EXPERT WITNESS • ANTHROPIC",
          panDirection: "zoomIn",
          isPortrait: true,
          personName: "DARIO AMODEI",
          personTitle: "CEO, ANTHROPIC",
          companyTag: "UNITED NATIONS SECURITY COUNCIL",
        },
        {
          image: "aibrief/backgrounds/ai_standards.jpg",
          badge: "SECURITY COUNCIL CONSULTATIONS",
          panDirection: "panRight",
        },
      ];

    default: {
      const text = `${story.headline} ${story.script} ${story.keyPoints?.join(" ") || ""} ${story.category || ""} ${story.region}`.toLowerCase();
      const dynamicCuts: VisualCut[] = [];

      // 1. VIP Person mentions
      if (text.includes("sam altman") || text.includes("altman")) {
        dynamicCuts.push({
          image: "aibrief/assets/editorial/person_sam_altman.jpg",
          badge: "LEADERSHIP BRIEFING • FRONTIER LAB",
          panDirection: "zoomIn",
          isPortrait: true,
          personName: "SAM ALTMAN",
          personTitle: "CHIEF EXECUTIVE OFFICER, OPENAI",
          companyTag: "OPENAI • SAN FRANCISCO, CA",
        });
      } else if (text.includes("dario amodei") || text.includes("amodei")) {
        dynamicCuts.push({
          image: "aibrief/assets/editorial/person_dario_amodei.jpg",
          badge: "AI SAFETY ARCHITECTURE • LEADERSHIP",
          panDirection: "zoomIn",
          isPortrait: true,
          personName: "DARIO AMODEI",
          personTitle: "CHIEF EXECUTIVE OFFICER, ANTHROPIC",
          companyTag: "ANTHROPIC • SAN FRANCISCO, CA",
        });
      } else if (text.includes("jensen huang") || text.includes("jensen")) {
        dynamicCuts.push({
          image: "aibrief/assets/editorial/person_jensen_huang.jpg",
          badge: "ACCELERATED COMPUTING • FOUNDER & CEO",
          panDirection: "zoomIn",
          isPortrait: true,
          personName: "JENSEN HUANG",
          personTitle: "PRESIDENT & CEO, NVIDIA",
          companyTag: "NVIDIA • SANTA CLARA, CA",
        });
      } else if (text.includes("sundar pichai") || text.includes("pichai")) {
        dynamicCuts.push({
          image: "aibrief/assets/editorial/person_sundar_pichai.jpg",
          badge: "EXECUTIVE STRATEGY • SYSTEMS SCALING",
          panDirection: "zoomIn",
          isPortrait: true,
          personName: "SUNDAR PICHAI",
          personTitle: "CHIEF EXECUTIVE OFFICER, ALPHABET & GOOGLE",
          companyTag: "GOOGLE DEEPMIND • MOUNTAIN VIEW, CA",
        });
      }

      // 2. Robotics / Physical AI
      if (text.includes("robot") || text.includes("physical ai") || text.includes("humanoid") || text.includes("automation")) {
        dynamicCuts.push({
          image: "aibrief/assets/story4_nvidia_robotics.jpg",
          badge: "PHYSICAL AI • INDUSTRIAL ROBOTICS AUTOMATION",
          panDirection: "zoomIn",
        });
        dynamicCuts.push({
          image: "aibrief/assets/story4_quantum_qpu.jpg",
          badge: "AUTONOMOUS ASSEMBLY CORRIDOR • FACTORY TELEMETRY",
          panDirection: "panRight",
        });
        dynamicCuts.push({
          image: "aibrief/assets/story4_autonomous_robot.jpg",
          badge: "AGENTIC ROBOTICS SENSING PIPELINE",
          panDirection: "zoomOut",
        });
      }

      // 3. Chips / Silicon / Hardware
      if (text.includes("chip") || text.includes("gpu") || text.includes("semiconductor") || text.includes("silicon") || text.includes("hardware") || text.includes("tsmc")) {
        dynamicCuts.push({
          image: "aibrief/backgrounds/ai_chips.jpg",
          badge: "NEURAL ACCELERATOR WAFER • ADVANCED PACKAGING",
          panDirection: "zoomOut",
        });
        dynamicCuts.push({
          image: "aibrief/backgrounds/cloud_infrastructure.jpg",
          badge: "TENSOR CORE HARDWARE TELEMETRY",
          panDirection: "panLeft",
        });
      }

      // 4. Government / UN / Policy
      if (text.includes("united nations") || text.includes("security council") || text.includes("un ") || text.includes("multilateral")) {
        dynamicCuts.push({
          image: "aibrief/assets/editorial/fin_tokyo_district.jpg",
          badge: "UNITED NATIONS HEADQUARTERS • NEW YORK",
          panDirection: "zoomIn",
        });
        dynamicCuts.push({
          image: "aibrief/backgrounds/global_policy.jpg",
          badge: "MULTILATERAL AI GOVERNANCE FRAMEWORK",
          panDirection: "panRight",
        });
      } else if (text.includes("senate") || text.includes("congress") || text.includes("capitol") || text.includes("hearing") || text.includes("oversight") || text.includes("regulation") || text.includes("policy")) {
        dynamicCuts.push({
          image: "aibrief/assets/editorial/gov_canberra_parliament.jpg",
          badge: "PARLIAMENT HOUSE • LEGISLATIVE OVERSIGHT",
          panDirection: "zoomIn",
        });
        dynamicCuts.push({
          image: "aibrief/assets/editorial/fin_tokyo_district.jpg",
          badge: "CONGRESSIONAL DELIBERATIONS & STANDARDS",
          panDirection: "panLeft",
        });
      }

      // 5. India / Asia
      if (text.includes("india") || text.includes("indiaai") || text.includes("delhi") || text.includes("meity") || text.includes("hyderabad")) {
        dynamicCuts.push({
          image: "aibrief/assets/story6_network_grid.jpg",
          badge: "MINISTRY OF ELECTRONICS & IT • NEW DELHI",
          panDirection: "zoomOut",
        });
        dynamicCuts.push({
          image: "aibrief/assets/story6_indian_engineers.jpg",
          badge: "NATIONAL AI RESEARCH & INDIGENOUS COMPUTE",
          panDirection: "panRight",
        });
      }

      // 6. Cyber / Security / Threat Intelligence
      if (text.includes("cyber") || text.includes("security") || text.includes("breach") || text.includes("defense") || text.includes("hack") || text.includes("vulnerability")) {
        dynamicCuts.push({
          image: "aibrief/assets/story2_cyber_defense.jpg",
          badge: "CYBER THREAT OPERATIONS • LIVE DEFENSE FEED",
          panDirection: "zoomIn",
        });
        dynamicCuts.push({
          image: "aibrief/backgrounds/ai_security.jpg",
          badge: "AGENTIC RED-TEAMING & PERMISSIONS AUDIT",
          panDirection: "panLeft",
        });
      }

      // 7. General Lab / Compute / Code / Telemetry fallback cuts to ensure minimum 5 distinct cuts
      const generalPool: VisualCut[] = [
        {
          image: "aibrief/assets/story6_datacenter_servers.jpg",
          badge: "HYPERSCALE COMPUTE CORRIDOR • CLOUD REGION",
          panDirection: "zoomIn",
        },
        {
          image: "aibrief/assets/story1_code_agents.jpg",
          badge: "AUTONOMOUS SYSTEM TELEMETRY & RUNTIME",
          panDirection: "panRight",
        },
        {
          image: "aibrief/assets/story4_quantum_qpu.jpg",
          badge: "RESEARCH LABORATORY • INSTRUMENT FLOOR",
          panDirection: "zoomOut",
        },
        {
          image: "aibrief/assets/story6_network_grid.jpg",
          badge: "ENTERPRISE AUTOMATION BENCHMARK • 2026",
          panDirection: "panLeft",
        },
        {
          image: "aibrief/backgrounds/cloud_infrastructure.jpg",
          badge: "DISTRIBUTED CLUSTER FABRIC • HIGH THROUGHPUT",
          panDirection: "zoomIn",
        },
      ];

      for (const poolCut of generalPool) {
        if (dynamicCuts.length >= 6) break;
        if (!dynamicCuts.some((c) => c.image === poolCut.image)) {
          dynamicCuts.push(poolCut);
        }
      }

      return dynamicCuts;
    }
  }
};

interface StoryCardProps {
  story: Story;
}

export const StoryCard: React.FC<StoryCardProps> = ({ story }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance animation for lower-third banner
  const textEntrance = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 85 },
  });

  // Fast-Paced 4.0-Second Cuts (120 frames @ 30 FPS)
  const cuts = getStoryVisualCuts(story);
  const cutDuration = 120; // Exactly 4.0 seconds per visual
  const totalCuts = cuts.length;
  const currentCutIndex = Math.floor(frame / cutDuration) % totalCuts;
  const nextCutIndex = (currentCutIndex + 1) % totalCuts;
  const currentCut = cuts[currentCutIndex];
  const nextCut = cuts[nextCutIndex];

  // Local frame progress within current 4-second cut [0.0 to 1.0]
  const localCutFrame = frame % cutDuration;
  const localCutProgress = localCutFrame / cutDuration;

  // 12-frame crossfade between cuts
  const crossfade = interpolate(localCutFrame, [cutDuration - 12, cutDuration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

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
                  color: "#f8fafc",
                  fontSize: 12,
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
                  color: "#38bdf8",
                  fontSize: 12,
                  fontWeight: 800,
                  letterSpacing: 1.5,
                }}
              >
                {currentCut.badge}
              </span>
            </div>
          </div>

          {/* Key Intel Sub-Slug */}
          {story.keyPoints && story.keyPoints.length > 0 && (
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
                maxWidth: 620,
              }}
            >
              <span style={{ color: "#fbbf24", fontSize: 11, fontWeight: 900 }}>
                ⚡ FOCUS:
              </span>
              <span
                style={{
                  color: "#f8fafc",
                  fontSize: 12,
                  fontWeight: 700,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {story.keyPoints[currentCutIndex % story.keyPoints.length]}
              </span>
            </div>
          )}
        </div>

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
        <div style={{ maxWidth: 1220 }}>
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
                padding: "3px 12px",
                borderRadius: 4,
                fontSize: 12,
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
                  color: "#38bdf8",
                  padding: "3px 12px",
                  borderRadius: 4,
                  fontSize: 12,
                  fontWeight: 800,
                  letterSpacing: 1,
                }}
              >
                {story.categoryTag}
              </div>
            )}

            <div
              style={{
                color: "#94a3b8",
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: 0.8,
              }}
            >
              REPORTED BY:{" "}
              <span style={{ color: "#f8fafc", fontWeight: 800 }}>
                {story.source}
              </span>
            </div>
          </div>

          <h1
            style={{
              color: "#ffffff",
              fontSize: 31,
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
                color: "#cbd5e1",
                fontSize: 13,
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
                backgroundColor: "rgba(245, 158, 11, 0.12)",
                borderLeft: "3px solid #f59e0b",
                padding: "3px 12px",
                borderRadius: "0 4px 4px 0",
              }}
            >
              <span
                style={{
                  color: "#fbbf24",
                  fontSize: 11,
                  fontWeight: 900,
                  letterSpacing: 1,
                }}
              >
                WHY THIS MATTERS:
              </span>
              <span
                style={{
                  color: "#fef3c7",
                  fontSize: 13,
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
        {story.keyPoints && story.keyPoints.length > 0 && (
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
                  color: "#94a3b8",
                  fontSize: 11,
                  fontWeight: 800,
                  letterSpacing: 1.5,
                }}
              >
                STRATEGIC FOCUS
              </span>
            </div>
            <div
              style={{
                color: "#f8fafc",
                fontSize: 13,
                fontWeight: 700,
                lineHeight: 1.35,
              }}
            >
              {story.keyPoints[0]}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
