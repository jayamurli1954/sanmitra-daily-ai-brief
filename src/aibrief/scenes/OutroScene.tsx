import React from "react";
import {
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { OutroConfig } from "../types";

interface OutroSceneProps {
  outro: OutroConfig;
}

export const OutroScene: React.FC<OutroSceneProps> = ({ outro }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 13, stiffness: 85 },
  });

  const pulse = Math.sin(frame * 0.1) * 0.04 + 1.0;

  const bureaus = [
    { name: "WORLD", status: "ONLINE", tag: "AI GOVERNANCE & UN SECURITY", color: "#38bdf8" },
    { name: "USA", status: "ONLINE", tag: "FRONTIER EFFICIENCY & STANDARDS", color: "#60a5fa" },
    { name: "CHINA", status: "ONLINE", tag: "SOVEREIGN SILICON & FABRICATION", color: "#f87171" },
    { name: "ASIA", status: "ONLINE", tag: "BILATERAL SAFETY PROTOCOLS", color: "#34d399" },
    { name: "INDIA", status: "ONLINE", tag: "PUBLIC SECTOR & STATE GOVERNANCE", color: "#fbbf24" },
  ];

  const channelList = outro.bureaus || outro.channels || ["WORLD", "USA", "CHINA", "ASIA", "INDIA"];

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
      {/* 0. BASE PHOTOGRAPHIC GLOBAL NETWORK BACKGROUND */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          overflow: "hidden",
          zIndex: 0,
        }}
      >
        <Img
          src={staticFile("aibrief/backgrounds/outro_network.jpg")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${interpolate(frame, [0, 600], [1.0, 1.06], { extrapolateRight: "clamp" })})`,
            filter: "brightness(0.6) contrast(1.1)",
          }}
        />

        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "radial-gradient(ellipse at center, rgba(3, 7, 18, 0.65) 0%, rgba(3, 7, 18, 0.92) 100%)",
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

      {/* SPLIT OUTRO STAGE */}
      <div
        style={{
          position: "absolute",
          top: 72,
          left: 0,
          right: 0,
          bottom: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 80px",
          zIndex: 20,
        }}
      >
        {/* LEFT: GLOBAL COVERAGE INTELLIGENCE TERMINAL */}
        <div
          style={{
            position: "relative",
            width: 720,
            height: 620,
            borderRadius: 24,
            overflow: "hidden",
            border: "2px solid rgba(56, 189, 248, 0.4)",
            boxShadow: "0 24px 60px rgba(0, 0, 0, 0.8)",
            backgroundColor: "rgba(10, 18, 35, 0.95)",
            padding: "36px 40px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
          }}
        >
          {/* Top Terminal Bar */}
          <div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                borderBottom: "1px solid rgba(56, 189, 248, 0.3)",
                paddingBottom: 16,
                marginBottom: 24,
              }}
            >
              <div>
                <div style={{ color: "#ffffff", fontSize: 20, fontWeight: 900, letterSpacing: 1 }}>
                  SANMITRA GLOBAL NETWORK
                </div>
                <div style={{ color: "#38bdf8", fontSize: 12, fontWeight: 700, letterSpacing: 1.5 }}>
                  CONTINUOUS AI INTELLIGENCE FEED
                </div>
              </div>
              <div
                style={{
                  backgroundColor: "rgba(16, 185, 129, 0.15)",
                  border: "1px solid #10b981",
                  color: "#10b981",
                  fontSize: 12,
                  fontWeight: 900,
                  padding: "4px 12px",
                  borderRadius: 6,
                  letterSpacing: 1,
                }}
              >
                ACTIVE
              </div>
            </div>

            {/* Bureau List */}
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              {bureaus.map((b, i) => {
                const itemStagger = spring({
                  frame: frame - i * 4,
                  fps,
                  config: { damping: 12, stiffness: 100 },
                });
                return (
                  <div
                    key={b.name}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      backgroundColor: "rgba(15, 23, 42, 0.8)",
                      border: "1px solid rgba(148, 163, 184, 0.15)",
                      borderRadius: 10,
                      padding: "12px 18px",
                      opacity: itemStagger,
                      transform: `translateX(${(1 - itemStagger) * -20}px)`,
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                      <div
                        style={{
                          width: 8,
                          height: 8,
                          borderRadius: "50%",
                          backgroundColor: b.color,
                          boxShadow: `0 0 10px ${b.color}`,
                        }}
                      />
                      <span style={{ color: "#ffffff", fontSize: 16, fontWeight: 900, letterSpacing: 1 }}>
                        {b.name}
                      </span>
                      <span style={{ color: "#94a3b8", fontSize: 12, fontWeight: 600 }}>
                        {b.tag}
                      </span>
                    </div>
                    <span
                      style={{
                        color: "#10b981",
                        fontSize: 11,
                        fontWeight: 800,
                        letterSpacing: 1,
                      }}
                    >
                      {b.status}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Bottom Transmission Status Bar */}
          <div
            style={{
              backgroundColor: "rgba(15, 23, 42, 0.9)",
              border: "1px solid rgba(56, 189, 248, 0.3)",
              borderRadius: 12,
              padding: "12px 20px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div>
              <div style={{ color: "#ffffff", fontSize: 14, fontWeight: 800 }}>
                DAILY TRANSMISSION CYCLE
              </div>
              <div style={{ color: "#38bdf8", fontSize: 11, fontWeight: 600 }}>
                PUBLISHED EVERY MORNING • SANMITRA WIRE
              </div>
            </div>
            <div
              style={{
                backgroundColor: "#10b981",
                color: "#ffffff",
                fontSize: 11,
                fontWeight: 900,
                padding: "4px 10px",
                borderRadius: 4,
                letterSpacing: 1,
              }}
            >
              COMPLETE
            </div>
          </div>
        </div>

        {/* RIGHT: SUBSCRIBE CTA & COVERAGE PILLARS */}
        <div
          style={{
            width: 880,
            backgroundColor: "rgba(15, 23, 42, 0.94)",
            border: "1px solid rgba(56, 189, 248, 0.4)",
            borderRadius: 24,
            padding: "48px 52px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            textAlign: "center",
            boxShadow: "0 24px 64px rgba(0, 0, 0, 0.8)",
            opacity: entrance,
            transform: `scale(${0.9 + entrance * 0.1})`,
          }}
        >
          {/* Brand Tag */}
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 14 }}>
            <div
              style={{
                backgroundColor: "#dc2626",
                color: "#ffffff",
                padding: "6px 16px",
                fontSize: 20,
                fontWeight: 900,
                borderRadius: 6,
              }}
            >
              SANMITRA
            </div>
            <span style={{ color: "#ffffff", fontSize: 26, fontWeight: 900, letterSpacing: 3 }}>
              AI NEWS WIRE
            </span>
          </div>

          <h2
            style={{
              color: "#38bdf8",
              fontSize: 30,
              fontWeight: 900,
              letterSpacing: 1,
              margin: "0 0 10px 0",
            }}
          >
            Daily Global AI Intelligence
          </h2>

          <p
            style={{
              color: "#94a3b8",
              fontSize: 16,
              fontWeight: 500,
              lineHeight: 1.5,
              maxWidth: 680,
              margin: "0 0 28px 0",
            }}
          >
            Delivering verified artificial intelligence intelligence across global developments in the US, China, Asia, India, and multilateral security policy.
          </p>

          {/* Big Subscribe CTA Button */}
          <div
            style={{
              backgroundColor: "#dc2626",
              color: "#ffffff",
              display: "flex",
              alignItems: "center",
              gap: 14,
              padding: "16px 40px",
              borderRadius: 40,
              fontSize: 19,
              fontWeight: 900,
              letterSpacing: 2,
              boxShadow: "0 0 30px rgba(220, 38, 38, 0.6)",
              transform: `scale(${pulse})`,
              marginBottom: 32,
              cursor: "pointer",
            }}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
            SUBSCRIBE FOR DAILY AI UPDATES
          </div>

          {/* Bureau Desks Row */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 16,
              borderTop: "1px solid rgba(148, 163, 184, 0.2)",
              paddingTop: 20,
              width: "100%",
              justifyContent: "center",
            }}
          >
            {channelList.map((channel, i) => (
              <div
                key={i}
                style={{
                  color: "#38bdf8",
                  fontSize: 13,
                  fontWeight: 800,
                  letterSpacing: 2,
                  textTransform: "uppercase",
                }}
              >
                {channel} {i < channelList.length - 1 && "•"}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
