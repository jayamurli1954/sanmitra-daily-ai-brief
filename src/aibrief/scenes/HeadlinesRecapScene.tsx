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

interface HeadlinesRecapSceneProps {
  stories?: Story[];
}

const RECAP_ITEMS = [
  { text: "DeepSeek at UN Security Council", source: "Reuters", tag: "GLOBAL SECURITY" },
  { text: "GPT-6 Sol & Luna Launch", source: "OpenAI / Fortune", tag: "FOUNDATION MODELS" },
  { text: "Claude Opus 5.5 Released", source: "Anthropic", tag: "ENTERPRISE AI" },
  { text: "AI Healthcare Expansion", source: "OpenEvidence / Reuters", tag: "GLOBAL HEALTH" },
  { text: "Youth AI Safety Push", source: "Mint / Reuters", tag: "AI SAFETY" },
  { text: "Alibaba Zhenwu V900", source: "TechNode / Fortune", tag: "SEMICONDUCTORS" },
  { text: "Maharashtra AI Governance Committee", source: "ET Education / IANS", tag: "DIGITAL GOVERNANCE" },
];

export const HeadlinesRecapScene: React.FC<HeadlinesRecapSceneProps> = ({ stories }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 90 },
  });

  const items =
    stories && stories.length > 0
      ? stories.map((s) => ({
          text: s.headline,
          source: s.source,
          tag: s.categoryTag || s.category || s.region,
        }))
      : RECAP_ITEMS;

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
      {/* 0. NEWSROOM RECAP DASHBOARD BACKGROUND */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          overflow: "hidden",
          zIndex: 0,
        }}
      >
        <Img
          src={staticFile("aibrief/backgrounds/intro_newsroom.jpg")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${interpolate(frame, [0, 300], [1.02, 1.06], { extrapolateRight: "clamp" })})`,
            filter: "brightness(0.42) contrast(1.18)",
          }}
        />

        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "radial-gradient(ellipse at center, rgba(3, 7, 18, 0.72) 0%, rgba(3, 7, 18, 0.96) 100%)",
          }}
        />
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: 120,
            background:
              "linear-gradient(to bottom, rgba(3, 7, 18, 0.95), transparent)",
          }}
        />
      </div>

      {/* STAGE CONTAINER */}
      <div
        style={{
          position: "absolute",
          top: 72,
          left: 0,
          right: 0,
          bottom: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          padding: "32px 80px",
          zIndex: 20,
        }}
      >
        {/* Header Tag & Title */}
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 10,
              backgroundColor: "#dc2626",
              color: "#ffffff",
              padding: "6px 20px",
              borderRadius: 6,
              fontSize: 13,
              fontWeight: 900,
              letterSpacing: 2,
              marginBottom: 8,
              boxShadow: "0 0 20px rgba(220, 38, 38, 0.5)",
              transform: `scale(${0.92 + titleSpring * 0.08})`,
            }}
          >
            <span>● 10-SECOND HEADLINES RECAP</span>
            <span>•</span>
            <span>SANMITRA AI NEWS WIRE</span>
          </div>

          <h2
            style={{
              color: "#ffffff",
              fontSize: 42,
              fontWeight: 950,
              letterSpacing: -0.5,
              margin: 0,
              textShadow: "0 4px 20px rgba(0,0,0,0.8)",
            }}
          >
            TODAY'S CRITICAL DEVELOPMENTS
          </h2>
        </div>

        {/* 7-Story Checklist Grid (2-column layout) */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "14px 24px",
            width: "100%",
            maxWidth: 1600,
          }}
        >
          {items.map((item, i) => {
            const delay = i * 3;
            const itemSpring = spring({
              frame: frame - delay,
              fps,
              config: { damping: 14, stiffness: 110 },
            });

            return (
              <div
                key={i}
                style={{
                  backgroundColor: "rgba(15, 23, 42, 0.92)",
                  border: "1px solid rgba(56, 189, 248, 0.35)",
                  borderRadius: 12,
                  padding: "14px 20px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  boxShadow: "0 10px 28px rgba(0, 0, 0, 0.55)",
                  opacity: itemSpring,
                  transform: `translateY(${(1 - itemSpring) * 16}px)`,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                  {/* Verified Checkmark Icon */}
                  <div
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: "50%",
                      backgroundColor: "rgba(16, 185, 129, 0.2)",
                      border: "2px solid #10b981",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "#10b981",
                      fontSize: 18,
                      fontWeight: 900,
                      flexShrink: 0,
                      boxShadow: "0 0 10px rgba(16, 185, 129, 0.4)",
                    }}
                  >
                    ✓
                  </div>

                  <div>
                    <div
                      style={{
                        color: "#38bdf8",
                        fontSize: 10,
                        fontWeight: 900,
                        letterSpacing: 1.5,
                        marginBottom: 2,
                      }}
                    >
                      {item.tag}
                    </div>
                    <div
                      style={{
                        color: "#ffffff",
                        fontSize: 17,
                        fontWeight: 800,
                        lineHeight: 1.25,
                      }}
                    >
                      {item.text}
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    backgroundColor: "rgba(10, 18, 35, 0.8)",
                    border: "1px solid rgba(148, 163, 184, 0.25)",
                    borderRadius: 6,
                    padding: "4px 10px",
                    color: "#cbd5e1",
                    fontSize: 11,
                    fontWeight: 700,
                    letterSpacing: 0.5,
                    flexShrink: 0,
                    marginLeft: 12,
                  }}
                >
                  {item.source}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
