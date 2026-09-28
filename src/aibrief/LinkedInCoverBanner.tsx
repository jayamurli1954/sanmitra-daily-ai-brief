import React from "react";
import { Img, staticFile } from "remotion";
import episodeData from "./data/active_episode.json";

interface LinkedInCoverProps {
  headlineTop?: string;
  headlineBottom?: string;
  subtitle?: string;
  stickyNoteText?: string;
  badgeSeries?: string;
  leadStory?: string;
  pillars?: Array<{ title: string; subtitle: string; color: string; icon: string }>;
}

const ep = episodeData as any;

export const LinkedInCoverBanner: React.FC<LinkedInCoverProps> = ({
  headlineTop = "The Question of",
  headlineBottom = "Control",
  subtitle = "Over the past 24 hours, global powers and frontier labs face a common challenge: How do we govern autonomous AI without halting innovation?",
  stickyNoteText = "Big models.\nBold claims.\nBut can they\nactually be\ncontrolled?",
  badgeSeries = `AI Insights #${ep.date ? ep.date.replace(/-/g, "").slice(4) : "028"} • Global AI Brief`,
  pillars = [
    { title: "AI Diplomacy", subtitle: "US–China Hotline", color: "#0284c7", icon: "🌐" },
    { title: "Sandbox Escapes", subtitle: "Training Paused", color: "#dc2626", icon: "🛡️" },
    { title: "Sovereign Silicon", subtitle: "RTX PRO 5500", color: "#059669", icon: "⚡" },
    { title: "Critical Defense", subtitle: "National Benchmarks", color: "#d97706", icon: "🏛️" },
  ],
}) => {
  return (
    <div
      style={{
        position: "relative",
        width: 1920,
        height: 1080,
        backgroundColor: "#f8fafc",
        overflow: "hidden",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      {/* 1. EDITORIAL BACKGROUND WITH SOFT BLUR & HIGH-KEY LIGHTING */}
      <div style={{ position: "absolute", inset: 0, opacity: 0.45 }}>
        <Img
          src={staticFile("aibrief/assets/editorial/2026-09-28/s1_cut1.jpg")}
          style={{ width: "100%", height: "100%", objectFit: "cover", filter: "blur(2px)" }}
        />
      </div>

      {/* Gradient Wash from Left for crisp reading */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "linear-gradient(90deg, rgba(255,255,255,0.96) 0%, rgba(255,255,255,0.92) 55%, rgba(255,255,255,0.4) 100%)",
        }}
      />

      {/* 2. TOP HEADER BRANDING BAR */}
      <div
        style={{
          position: "absolute",
          top: 60,
          left: 90,
          right: 90,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          {/* OfficeMitra Logo & Branding */}
          <Img
            src={staticFile("officemitra/officemitra-logo-banner.png")}
            style={{ height: 62, objectFit: "contain" }}
          />
          <div style={{ height: 40, width: 2, backgroundColor: "#cbd5e1" }} />
          <div>
            <div style={{ fontSize: 20, fontWeight: 800, color: "#002b5c", letterSpacing: "0.02em" }}>
              SanMitra AI News Wire
            </div>
            <div style={{ fontSize: 14, fontWeight: 600, color: "#64748b" }}>
              Global Institutional Briefings
            </div>
          </div>
        </div>

        {/* Series Badge */}
        <div
          style={{
            padding: "10px 22px",
            backgroundColor: "#e0f2fe",
            border: "1.5px solid #0284c7",
            borderRadius: 30,
            fontSize: 16,
            fontWeight: 800,
            color: "#0369a1",
            letterSpacing: "0.04em",
            textTransform: "uppercase",
          }}
        >
          {badgeSeries}
        </div>
      </div>

      {/* 3. HERO EDITORIAL HEADLINE & PROVOCATION (LEFT 65%) */}
      <div
        style={{
          position: "absolute",
          top: 210,
          left: 90,
          width: 1050,
        }}
      >
        <div
          style={{
            fontSize: 22,
            fontWeight: 800,
            color: "#0284c7",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            marginBottom: 12,
          }}
        >
          AI Intelligence • Executive Analysis
        </div>

        <div
          style={{
            fontSize: 86,
            fontWeight: 900,
            color: "#0f172a",
            lineHeight: 1.05,
            letterSpacing: "-0.03em",
          }}
        >
          {headlineTop}
        </div>

        <div
          style={{
            fontSize: 98,
            fontWeight: 950,
            color: "#dc2626",
            lineHeight: 1.05,
            letterSpacing: "-0.03em",
            marginBottom: 26,
          }}
        >
          {headlineBottom}
        </div>

        <div
          style={{
            fontSize: 26,
            fontWeight: 500,
            color: "#334155",
            lineHeight: 1.45,
            maxWidth: 960,
          }}
        >
          {subtitle}
        </div>
      </div>

      {/* 4. REALISTIC STICKY NOTE CALLOUT (CENTER-RIGHT) */}
      <div
        style={{
          position: "absolute",
          top: 240,
          right: 140,
          width: 380,
          minHeight: 340,
          backgroundColor: "#fef08a",
          borderRadius: 4,
          padding: "36px 32px",
          boxShadow: "0 25px 45px rgba(0,0,0,0.18), 0 10px 18px rgba(0,0,0,0.10)",
          transform: "rotate(-3deg)",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          borderTop: "8px solid rgba(234, 179, 8, 0.4)",
        }}
      >
        <div
          style={{
            fontSize: 32,
            fontWeight: 800,
            color: "#713f12",
            lineHeight: 1.35,
            whiteSpace: "pre-line",
          }}
        >
          {stickyNoteText}
        </div>

        <div
          style={{
            fontSize: 14,
            fontWeight: 800,
            color: "#a16207",
            textTransform: "uppercase",
            letterSpacing: "0.06em",
            borderTop: "1.5px dashed #ca8a04",
            paddingTop: 14,
          }}
        >
          📌 Editorial Provocation
        </div>
      </div>

      {/* 5. BOTTOM 4-PILLAR TAKEAWAY FOOTER BAR */}
      <div
        style={{
          position: "absolute",
          bottom: 50,
          left: 90,
          right: 90,
          height: 120,
          backgroundColor: "#ffffff",
          borderRadius: 20,
          boxShadow: "0 12px 30px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.05)",
          border: "1px solid #e2e8f0",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-around",
          padding: "0 20px",
        }}
      >
        {pillars.map((pill, idx) => (
          <div
            key={idx}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 16,
              flex: 1,
              justifyContent: "center",
              borderRight: idx < pillars.length - 1 ? "1.5px solid #f1f5f9" : "none",
            }}
          >
            {/* Round Icon Badge */}
            <div
              style={{
                width: 62,
                height: 62,
                borderRadius: "50%",
                backgroundColor: pill.color,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 28,
                color: "#ffffff",
                boxShadow: `0 6px 14px ${pill.color}40`,
              }}
            >
              {pill.icon}
            </div>

            <div>
              <div style={{ fontSize: 20, fontWeight: 800, color: "#0f172a" }}>
                {pill.title}
              </div>
              <div style={{ fontSize: 15, fontWeight: 600, color: "#64748b" }}>
                {pill.subtitle}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
