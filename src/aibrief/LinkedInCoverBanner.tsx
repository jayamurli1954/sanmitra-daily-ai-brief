import React from "react";
import { Img, staticFile } from "remotion";
import episodeData from "./data/active_episode.json";

const ep = episodeData as any;

interface BureauStoryConfig {
  region: string;
  badge: string;
  badgeColor: string;
  flag: string;
  fallbackHeadline: string;
  fallbackSummary: string;
  fallbackImage: string;
}

const BUREAUS: BureauStoryConfig[] = [
  {
    region: "WORLD",
    badge: "WORLD",
    badgeColor: "#dc2626",
    flag: "🇺🇦",
    fallbackHeadline: "Autonomous AI Defends Against Drones",
    fallbackSummary: "Ukraine deploys AI-powered turrets to intercept Geran-5 drones as autonomous defense systems scale globally.",
    fallbackImage: "aibrief/assets/editorial/2026-10-07/s1_cut1.jpg",
  },
  {
    region: "USA",
    badge: "USA",
    badgeColor: "#2563eb",
    flag: "🇺🇸",
    fallbackHeadline: "Google's MedGemma Advances Medical AI",
    fallbackSummary: "MedGemma medical vision models published in Nature Medicine. EmbeddingGemma 2 released for multimodal AI.",
    fallbackImage: "aibrief/assets/editorial/2026-10-07/s2_cut1.jpg",
  },
  {
    region: "CHINA",
    badge: "CHINA",
    badgeColor: "#b91c1c",
    flag: "🇨🇳",
    fallbackHeadline: "AI Giants Expand Infrastructure",
    fallbackSummary: "Alibaba, Tencent, DeepSeek and ByteDance accelerate compute and next-generation model development.",
    fallbackImage: "aibrief/assets/editorial/2026-10-07/s4_cut1.jpg",
  },
  {
    region: "ASIA",
    badge: "ASIA",
    badgeColor: "#d97706",
    flag: "🇦🇺",
    fallbackHeadline: "Autonomous Systems Gain Momentum",
    fallbackSummary: "Shield AI and Innovaero partner to integrate Hivemind autonomy in OWL drones, showcasing multi-drone operations.",
    fallbackImage: "aibrief/assets/editorial/2026-10-07/s13_cut1.jpg",
  },
  {
    region: "INDIA",
    badge: "INDIA",
    badgeColor: "#059669",
    flag: "🇮🇳",
    fallbackHeadline: "National AI Council to Guide Sovereign AI",
    fallbackSummary: "ElevenLabs commits hundreds of millions of dollars to India; sovereign compute and regional voice ecosystems scale.",
    fallbackImage: "aibrief/assets/editorial/2026-10-07/s6_cut1.jpg",
  },
];

const TAXONOMY = [
  {
    icon: "💡",
    title: "AI BREAKTHROUGHS",
    desc: "New frontiers in research and real-world use",
    color: "#38bdf8",
  },
  {
    icon: "⚙️",
    title: "NEW MODELS & TOOLS",
    desc: "Latest models, tools and platforms",
    color: "#06b6d4",
  },
  {
    icon: "📈",
    title: "INDUSTRY & STARTUP NEWS",
    desc: "Investments, products and market moves",
    color: "#10b981",
  },
  {
    icon: "🛡️",
    title: "POLICY & REGULATIONS",
    desc: "Governance, laws and global actions",
    color: "#f43f5e",
  },
  {
    icon: "🗄️",
    title: "TECHNOLOGY TRENDS",
    desc: "Compute, infrastructure and real-world adoption",
    color: "#eab308",
  },
];

export const LinkedInCoverBanner: React.FC = () => {
  const stories: any[] = ep?.stories || [];

  // Resolve top story for each of the 5 regional bureaus
  const bureauCards = BUREAUS.map((cfg) => {
    const match = stories.find(
      (s) => (s.region || "").toUpperCase() === cfg.region.toUpperCase()
    );

    let headline = cfg.fallbackHeadline;
    let summary = cfg.fallbackSummary;
    let imageSrc = cfg.fallbackImage;

    if (match) {
      if (match.headline) {
        headline = match.headline.length > 55 ? match.headline.slice(0, 52) + "..." : match.headline;
      }
      if (match.script) {
        const firstSentence = match.script.split(".")[0];
        summary = firstSentence.length > 120 ? firstSentence.slice(0, 117) + "..." : firstSentence + ".";
      }
      if (match.visualCuts?.[0]?.image) {
        imageSrc = match.visualCuts[0].image;
      } else if (match.visual) {
        imageSrc = match.visual;
      }
    }

    return {
      ...cfg,
      headline,
      summary,
      imageSrc,
    };
  });

  const formattedDate = ep?.formattedDate ? `${ep.formattedDate.toUpperCase()} (IST)` : "07 OCTOBER 2026 (IST)";

  return (
    <div
      style={{
        position: "relative",
        width: 1920,
        height: 1080,
        backgroundColor: "#020617",
        overflow: "hidden",
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        color: "#ffffff",
      }}
    >
      {/* =========================================================================
          ROW 1: TOP 5 REGIONAL BUREAU STORY PANELS
         ========================================================================= */}
      <div
        style={{
          display: "flex",
          gap: "10px",
          padding: "16px 20px 8px 20px",
          height: "480px",
          boxSizing: "border-box",
        }}
      >
        {bureauCards.map((b, idx) => (
          <div
            key={`bureau_${idx}`}
            style={{
              flex: 1,
              height: "100%",
              borderRadius: "14px",
              overflow: "hidden",
              position: "relative",
              border: "1.5px solid rgba(56, 189, 248, 0.4)",
              boxShadow: "0 10px 25px rgba(0, 0, 0, 0.6)",
              backgroundColor: "#090d16",
            }}
          >
            {/* Background Story Image */}
            <Img
              src={staticFile(b.imageSrc)}
              style={{
                position: "absolute",
                inset: 0,
                width: "100%",
                height: "100%",
                objectFit: "cover",
                filter: "brightness(0.72) contrast(1.1)",
              }}
            />

            {/* Cinematic Gradient Vignette */}
            <div
              style={{
                position: "absolute",
                inset: 0,
                background:
                  "linear-gradient(180deg, rgba(2,6,23,0.35) 0%, rgba(2,6,23,0.15) 30%, rgba(2,6,23,0.85) 68%, rgba(2,6,23,0.98) 100%)",
              }}
            />

            {/* Top Badge & Flag Header */}
            <div
              style={{
                position: "relative",
                zIndex: 2,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "12px 14px",
              }}
            >
              <div
                style={{
                  backgroundColor: b.badgeColor,
                  color: "#ffffff",
                  padding: "5px 14px",
                  borderRadius: "5px",
                  fontSize: "16px",
                  fontWeight: 900,
                  letterSpacing: "0.06em",
                  textTransform: "uppercase",
                  boxShadow: "0 2px 10px rgba(0,0,0,0.6)",
                }}
              >
                {b.badge}
              </div>

              <div
                style={{
                  fontSize: "26px",
                  filter: "drop-shadow(0 2px 6px rgba(0,0,0,0.8))",
                }}
              >
                {b.flag}
              </div>
            </div>

            {/* Bottom Headline & Description */}
            <div
              style={{
                position: "absolute",
                zIndex: 2,
                bottom: 0,
                left: 0,
                right: 0,
                padding: "16px 14px 18px 14px",
              }}
            >
              <div
                style={{
                  fontSize: "20px",
                  fontWeight: 900,
                  color: "#fde047",
                  lineHeight: "1.25",
                  marginBottom: "8px",
                  letterSpacing: "-0.01em",
                  textShadow: "0 2px 8px rgba(0,0,0,0.95)",
                }}
              >
                {b.headline}
              </div>
              <div
                style={{
                  fontSize: "13px",
                  fontWeight: 500,
                  color: "#e2e8f0",
                  lineHeight: "1.4",
                  textShadow: "0 1px 4px rgba(0,0,0,0.95)",
                }}
              >
                {b.summary}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* =========================================================================
          ROW 2: CENTER HIGH-TECH NEWSROOM COMMAND BAR
         ========================================================================= */}
      <div
        style={{
          position: "relative",
          height: "260px",
          margin: "4px 20px",
          borderRadius: "16px",
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background:
            "radial-gradient(ellipse at 50% 50%, #034870 0%, #02233c 50%, #011425 100%)",
          border: "2px solid #0284c7",
          boxShadow: "0 0 40px rgba(2, 132, 199, 0.4), inset 0 0 25px rgba(56, 189, 248, 0.2)",
        }}
      >
        {/* Left Holographic Globe Visual */}
        <div
          style={{
            position: "relative",
            width: "280px",
            height: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            paddingLeft: "30px",
          }}
        >
          <div
            style={{
              position: "relative",
              width: "200px",
              height: "200px",
              borderRadius: "50%",
              overflow: "hidden",
              border: "2px solid #38bdf8",
              boxShadow: "0 0 35px rgba(56, 189, 248, 0.6)",
            }}
          >
            <Img
              src={staticFile("aibrief/assets/story3_neural_network.jpg")}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                filter: "hue-rotate(185deg) brightness(1.2)",
              }}
            />
            {/* Glowing ring overlay */}
            <div
              style={{
                position: "absolute",
                inset: 0,
                border: "1px dashed rgba(255,255,255,0.7)",
                borderRadius: "50%",
              }}
            />
          </div>
        </div>

        {/* Center Title and Identity */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            textAlign: "center",
            flex: 1,
            zIndex: 2,
          }}
        >
          {/* Top Brand Tag */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              fontSize: "28px",
              fontWeight: 800,
              color: "#ffffff",
              letterSpacing: "0.03em",
              textShadow: "0 2px 8px rgba(0,0,0,0.6)",
            }}
          >
            <span>SanMitra</span>
            <span
              style={{
                backgroundColor: "#ef4444",
                color: "#ffffff",
                padding: "2px 10px",
                borderRadius: "6px",
                fontSize: "24px",
                fontWeight: 900,
              }}
            >
              AI
            </span>
            <span>News Wire</span>
          </div>

          {/* Giant AI BRIEF */}
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: "14px",
              marginTop: "4px",
              lineHeight: 1,
            }}
          >
            <span
              style={{
                fontSize: "92px",
                fontWeight: 950,
                color: "#ffffff",
                letterSpacing: "-0.02em",
                textShadow: "0 0 30px rgba(255,255,255,0.5)",
              }}
            >
              AI
            </span>
            <span
              style={{
                fontSize: "92px",
                fontWeight: 950,
                color: "#facc15",
                letterSpacing: "-0.02em",
                textShadow: "0 0 35px rgba(250,204,21,0.6)",
              }}
            >
              BRIEF
            </span>
          </div>

          {/* Golden Date Bar */}
          <div
            style={{
              backgroundColor: "#f59e0b",
              color: "#0f172a",
              fontWeight: 950,
              fontSize: "22px",
              letterSpacing: "0.08em",
              padding: "4px 38px",
              borderRadius: "6px",
              textTransform: "uppercase",
              marginTop: "6px",
              boxShadow: "0 2px 14px rgba(245,158,11,0.5)",
            }}
          >
            {formattedDate}
          </div>

          {/* Navigation Bureaus */}
          <div
            style={{
              fontSize: "16px",
              fontWeight: 700,
              color: "#bae6fd",
              letterSpacing: "0.08em",
              marginTop: "8px",
            }}
          >
            Global AI Developments • World • USA • China • Asia • India
          </div>
        </div>

        {/* Right Cybernetic Profile / Telemetry Screen */}
        <div
          style={{
            position: "relative",
            width: "280px",
            height: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            paddingRight: "30px",
          }}
        >
          <div
            style={{
              position: "relative",
              width: "200px",
              height: "200px",
              borderRadius: "50%",
              overflow: "hidden",
              border: "2px solid #38bdf8",
              boxShadow: "0 0 35px rgba(56, 189, 248, 0.6)",
            }}
          >
            <Img
              src={staticFile("aibrief/backgrounds/ai_chips.jpg")}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                filter: "hue-rotate(170deg) brightness(1.2)",
              }}
            />
            {/* Glowing AI Chip Badge */}
            <div
              style={{
                position: "absolute",
                top: 20,
                right: 20,
                backgroundColor: "#0284c7",
                color: "#ffffff",
                padding: "4px 10px",
                borderRadius: "6px",
                fontSize: "14px",
                fontWeight: 900,
                border: "1px solid #38bdf8",
              }}
            >
              AI
            </div>
          </div>
        </div>
      </div>

      {/* =========================================================================
          ROW 3: 5 TAXONOMY CATEGORY CARDS
         ========================================================================= */}
      <div
        style={{
          display: "flex",
          gap: "12px",
          padding: "6px 20px",
          height: "160px",
          boxSizing: "border-box",
        }}
      >
        {TAXONOMY.map((item, idx) => (
          <div
            key={`tax_${idx}`}
            style={{
              flex: 1,
              height: "100%",
              backgroundColor: "rgba(15, 23, 42, 0.8)",
              border: "1.5px solid rgba(56, 189, 248, 0.3)",
              borderRadius: "12px",
              padding: "16px 14px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              boxShadow: "0 4px 15px rgba(0, 0, 0, 0.4)",
              position: "relative",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
              <span style={{ fontSize: "24px" }}>{item.icon}</span>
              <span
                style={{
                  fontSize: "14px",
                  fontWeight: 900,
                  color: item.color,
                  letterSpacing: "0.04em",
                  textTransform: "uppercase",
                }}
              >
                {item.title}
              </span>
            </div>
            <div
              style={{
                fontSize: "13px",
                fontWeight: 500,
                color: "#94a3b8",
                lineHeight: "1.35",
              }}
            >
              {item.desc}
            </div>
          </div>
        ))}
      </div>

      {/* =========================================================================
          ROW 4: PROFESSIONAL BRANDING FOOTER
         ========================================================================= */}
      <div
        style={{
          height: "70px",
          padding: "0 36px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          backgroundColor: "#010814",
          borderTop: "1px solid rgba(56, 189, 248, 0.25)",
          boxSizing: "border-box",
        }}
      >
        {/* Left OfficeMitra Branding */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div>
            <span style={{ fontSize: "30px", fontWeight: 950, color: "#38bdf8", letterSpacing: "-0.02em" }}>
              Office
            </span>
            <span style={{ fontSize: "30px", fontWeight: 950, color: "#ffffff", letterSpacing: "-0.02em" }}>
              Mitra
            </span>
          </div>

          <div style={{ height: "24px", width: "2px", backgroundColor: "#334155" }} />

          <span style={{ fontSize: "18px", fontWeight: 600, color: "#cbd5e1" }}>
            Your Daily View of <strong style={{ color: "#ffffff" }}>Global AI Developments</strong>
          </span>
        </div>

        {/* Right SanMitra Technologies Branding */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div style={{ height: "24px", width: "2px", backgroundColor: "#ef4444" }} />

          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <div
              style={{
                width: "28px",
                height: "28px",
                backgroundColor: "#ef4444",
                borderRadius: "6px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 900,
                fontSize: "16px",
                color: "#ffffff",
              }}
            >
              S
            </div>
            <div style={{ textAlign: "left" }}>
              <div
                style={{
                  fontSize: "11px",
                  fontWeight: 600,
                  color: "#64748b",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                }}
              >
                Powered by
              </div>
              <div
                style={{
                  fontSize: "17px",
                  fontWeight: 800,
                  color: "#ffffff",
                  letterSpacing: "0.02em",
                }}
              >
                SanMitra Technologies
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
