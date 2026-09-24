import React from "react";
import { Img, staticFile } from "remotion";
import episodeData from "./data/active_episode.json";

interface ThumbnailProps {
  variant?: "A" | "B" | "C";
  headline?: string;
  subheadline?: string;
  dateStr?: string;
  storyHighlights?: string[];
}

const ep = episodeData as any;

export const AIBriefThumbnail: React.FC<ThumbnailProps> = ({
  headline = ep.thumbnail?.headline || "BIGGEST AI NEWS",
  subheadline = ep.thumbnail?.subheadline || "TODAY",
  dateStr = ep.thumbnail?.date || "22 SEP 2026",
  storyHighlights = ep.thumbnail?.storyHighlights || [
    "Meta Security Alert",
    "US–China AI Talks",
    "Microsoft Expands in India",
  ],
}) => {
  const bulletColors = ["#ef4444", "#38bdf8", "#10b981"];

  return (
    <div
      style={{
        position: "relative",
        width: 1920,
        height: 1080,
        backgroundColor: "#030712",
        overflow: "hidden",
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      {/* 1. THREE-WAY SPLIT PHOTOGRAPHIC BACKGROUND (Security + Silicon + Global Network) */}
      <div style={{ position: "absolute", inset: 0, display: "flex", overflow: "hidden" }}>
        {/* Left 33%: Cybersecurity Operations Center */}
        <div style={{ position: "relative", width: "34%", height: "100%", overflow: "hidden" }}>
          <Img
            src={staticFile("aibrief/backgrounds/ai_security.jpg")}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: "scale(1.08)",
              filter: "contrast(1.2) brightness(0.85)",
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 0,
              right: 0,
              bottom: 0,
              width: 3,
              background: "linear-gradient(to bottom, transparent, #38bdf8, transparent)",
              boxShadow: "0 0 15px #38bdf8",
              zIndex: 5,
            }}
          />
        </div>

        {/* Center 33%: AI Silicon Wafer & Datacenter */}
        <div style={{ position: "relative", width: "33%", height: "100%", overflow: "hidden" }}>
          <Img
            src={staticFile("aibrief/backgrounds/ai_chips.jpg")}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: "scale(1.08)",
              filter: "contrast(1.2) brightness(0.82)",
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 0,
              right: 0,
              bottom: 0,
              width: 3,
              background: "linear-gradient(to bottom, transparent, #ef4444, transparent)",
              boxShadow: "0 0 15px #ef4444",
              zIndex: 5,
            }}
          />
        </div>

        {/* Right 33%: Global Intelligence Satellite Network */}
        <div style={{ position: "relative", width: "33%", height: "100%", overflow: "hidden" }}>
          <Img
            src={staticFile("aibrief/backgrounds/outro_network.jpg")}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: "scale(1.08)",
              filter: "contrast(1.2) brightness(0.85)",
            }}
          />
        </div>
      </div>

      {/* 2. HIGH-CONTRAST BROADCAST GRADIENT SCRIMS (Guarantee 100% Typography Readability) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(90deg, rgba(3, 7, 18, 0.88) 0%, rgba(3, 7, 18, 0.74) 48%, rgba(3, 7, 18, 0.50) 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(180deg, rgba(3, 7, 18, 0.80) 0%, rgba(3, 7, 18, 0.20) 40%, rgba(3, 7, 18, 0.90) 100%)",
        }}
      />

      {/* Outer Cyan Broadcast Border Frame */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          border: "4px solid rgba(56, 189, 248, 0.4)",
          pointerEvents: "none",
          zIndex: 30,
        }}
      />

      {/* 3. TOP BRAND BAR */}
      <div
        style={{
          position: "absolute",
          top: 60,
          left: 80,
          right: 80,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          zIndex: 25,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          {/* Brand Logo Tag */}
          <div
            style={{
              backgroundColor: "#dc2626",
              color: "#ffffff",
              padding: "10px 24px",
              fontSize: 26,
              fontWeight: 950,
              letterSpacing: 3,
              borderRadius: 8,
              boxShadow: "0 0 30px rgba(220, 38, 38, 0.7)",
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            <span>SANMITRA AI NEWS WIRE</span>
          </div>

          {/* Daily AI Brief Pill */}
          <div
            style={{
              backgroundColor: "rgba(56, 189, 248, 0.15)",
              border: "2px solid #38bdf8",
              color: "#38bdf8",
              padding: "8px 20px",
              borderRadius: 8,
              fontSize: 20,
              fontWeight: 900,
              letterSpacing: 2,
              backdropFilter: "blur(10px)",
            }}
          >
            DAILY AI BRIEF
          </div>
        </div>

        {/* Live Broadcast / Special Report Badge */}
        <div
          style={{
            backgroundColor: "rgba(220, 38, 38, 0.2)",
            border: "2px solid #ef4444",
            color: "#f87171",
            padding: "8px 24px",
            borderRadius: 8,
            fontSize: 20,
            fontWeight: 900,
            letterSpacing: 2.5,
            display: "flex",
            alignItems: "center",
            gap: 10,
          }}
        >
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: "50%",
              backgroundColor: "#ef4444",
              boxShadow: "0 0 12px #ef4444",
            }}
          />
          <span>GLOBAL BRIEFING</span>
        </div>
      </div>

      {/* 4. CENTER DOMINANT HOOK: "BIGGEST AI NEWS TODAY" (Ultra-Bold, High CTR) */}
      <div
        style={{
          position: "absolute",
          top: 240,
          left: 80,
          right: 80,
          zIndex: 25,
        }}
      >
        <h1
          style={{
            fontSize: 122,
            fontWeight: 950,
            letterSpacing: -2,
            lineHeight: 0.95,
            margin: 0,
            textTransform: "uppercase",
            textShadow: "0 8px 30px rgba(0, 0, 0, 0.95)",
          }}
        >
          <span style={{ color: "#ffffff", display: "block" }}>{headline}</span>
          <span
            style={{
              color: "#fbbf24",
              display: "block",
              marginTop: 12,
              textShadow:
                "0 8px 30px rgba(0, 0, 0, 0.95), 0 0 50px rgba(251, 191, 36, 0.4)",
            }}
          >
            {subheadline}
          </span>
        </h1>
      </div>

      {/* 5. BOTTOM 3 CRITICAL STORY PILLS */}
      <div
        style={{
          position: "absolute",
          bottom: 70,
          left: 80,
          zIndex: 25,
          display: "flex",
          flexDirection: "column",
          gap: 14,
        }}
      >
        {storyHighlights.slice(0, 3).map((story: string, i: number) => (
          <div
            key={i}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 16,
              backgroundColor: "rgba(10, 18, 35, 0.92)",
              border: `2px solid ${bulletColors[i] || "#38bdf8"}`,
              padding: "12px 28px",
              borderRadius: 12,
              boxShadow: "0 8px 24px rgba(0, 0, 0, 0.8)",
              backdropFilter: "blur(12px)",
            }}
          >
            {/* Glowing bullet */}
            <div
              style={{
                width: 14,
                height: 14,
                borderRadius: "50%",
                backgroundColor: bulletColors[i] || "#38bdf8",
                boxShadow: `0 0 14px ${bulletColors[i] || "#38bdf8"}`,
                flexShrink: 0,
              }}
            />
            <span
              style={{
                color: "#ffffff",
                fontSize: 30,
                fontWeight: 900,
                letterSpacing: 0.5,
              }}
            >
              {story}
            </span>
          </div>
        ))}
      </div>

      {/* 6. BOTTOM RIGHT: DATE BADGE */}
      <div
        style={{
          position: "absolute",
          bottom: 70,
          right: 80,
          zIndex: 25,
          backgroundColor: "rgba(15, 23, 42, 0.94)",
          border: "2px solid rgba(56, 189, 248, 0.5)",
          borderRadius: 14,
          padding: "16px 36px",
          textAlign: "center",
          boxShadow: "0 12px 32px rgba(0, 0, 0, 0.85)",
          backdropFilter: "blur(12px)",
        }}
      >
        <div style={{ color: "#38bdf8", fontSize: 13, fontWeight: 800, letterSpacing: 2, marginBottom: 4 }}>
          BROADCAST DATE
        </div>
        <div style={{ color: "#ffffff", fontSize: 32, fontWeight: 950, letterSpacing: 2 }}>
          {dateStr}
        </div>
      </div>

      {/* 7. RED BOTTOM ACCENT STRIP */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 12,
          backgroundColor: "#dc2626",
          boxShadow: "0 0 20px #dc2626",
          zIndex: 35,
        }}
      />
    </div>
  );
};
