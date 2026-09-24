import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { MarketSnapshotConfig } from "../types";

interface AIMarketSnapshotSceneProps {
  marketSnapshot?: MarketSnapshotConfig;
}

const DEFAULT_ENTITIES = [
  { name: "OpenAI", update: "GPT-6 Sol & Luna Launch", tag: "FRONTIER EFFICIENCY", color: "#10a37f" },
  { name: "Anthropic", update: "Claude Opus 5.5 & Global Clinical AI", tag: "ENTERPRISE REASONING", color: "#d97706" },
  { name: "Google", update: "Multimodal Infrastructure Scaling", tag: "SYSTEMS ACCELERATION", color: "#4285f4" },
  { name: "Meta", update: "Open Ecosystem & Agent Permissions", tag: "SANDBOX SECURITY", color: "#0668e1" },
  { name: "DeepSeek", update: "UN Security Council Briefing", tag: "GLOBAL DIPLOMACY", color: "#0ea5e9" },
  { name: "Alibaba", update: "Zhenwu V900 Sovereign Silicon", tag: "DOMESTIC HARDWARE", color: "#f97316" },
  { name: "Microsoft", update: "Hyperscale Cloud & Datacenters", tag: "INFRASTRUCTURE", color: "#00a4ef" },
];

export const AIMarketSnapshotScene: React.FC<AIMarketSnapshotSceneProps> = ({
  marketSnapshot,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 90 },
  });

  const entities = marketSnapshot?.entities || DEFAULT_ENTITIES;

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
      {/* Background Newsroom / Market Terminal Backdrop */}
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
            transform: `scale(${interpolate(frame, [0, 500], [1.02, 1.06], { extrapolateRight: "clamp" })})`,
            filter: "brightness(0.38) contrast(1.2)",
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
      </div>

      {/* Main Container */}
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
          padding: "36px 80px",
          zIndex: 20,
        }}
      >
        {/* Header Tag & Title */}
        <div style={{ textAlign: "center", marginBottom: 28 }}>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 10,
              backgroundColor: "rgba(14, 165, 233, 0.2)",
              border: "1px solid #38bdf8",
              color: "#38bdf8",
              padding: "6px 20px",
              borderRadius: 6,
              fontSize: 13,
              fontWeight: 900,
              letterSpacing: 2,
              marginBottom: 10,
              boxShadow: "0 0 20px rgba(56, 189, 248, 0.3)",
              transform: `scale(${0.92 + titleSpring * 0.08})`,
            }}
          >
            <span>● 15-SECOND INTELLIGENCE</span>
            <span>•</span>
            <span>STRATEGIC TELEMETRY</span>
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
            GLOBAL AI MARKET SNAPSHOT
          </h2>
          <div style={{ color: "#94a3b8", fontSize: 15, fontWeight: 600, marginTop: 4 }}>
            Key strategic shifts across the 7 frontier technology leaders
          </div>
        </div>

        {/* 7 Market Entities Grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))",
            gap: "14px 20px",
            width: "100%",
            maxWidth: 1640,
          }}
        >
          {entities.map((item, i) => {
            const delay = i * 3;
            const itemSpring = spring({
              frame: frame - delay,
              fps,
              config: { damping: 14, stiffness: 110 },
            });

            return (
              <div
                key={item.name}
                style={{
                  backgroundColor: "rgba(15, 23, 42, 0.9)",
                  border: `1px solid ${item.color}44`,
                  borderLeft: `4px solid ${item.color}`,
                  borderRadius: 12,
                  padding: "16px 22px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  boxShadow: "0 10px 28px rgba(0, 0, 0, 0.5)",
                  opacity: itemSpring,
                  transform: `translateY(${(1 - itemSpring) * 16}px)`,
                }}
              >
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                    <span
                      style={{
                        color: "#ffffff",
                        fontSize: 20,
                        fontWeight: 950,
                        letterSpacing: 0.5,
                      }}
                    >
                      {item.name}
                    </span>
                    <span
                      style={{
                        backgroundColor: `${item.color}22`,
                        color: item.color,
                        padding: "2px 8px",
                        borderRadius: 4,
                        fontSize: 10,
                        fontWeight: 900,
                        letterSpacing: 1,
                      }}
                    >
                      {item.tag}
                    </span>
                  </div>

                  <div
                    style={{
                      color: "#cbd5e1",
                      fontSize: 15,
                      fontWeight: 700,
                      lineHeight: 1.25,
                    }}
                  >
                    {item.update}
                  </div>
                </div>

                <div
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: "50%",
                    backgroundColor: item.color,
                    boxShadow: `0 0 10px ${item.color}`,
                    flexShrink: 0,
                    marginLeft: 16,
                  }}
                />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
