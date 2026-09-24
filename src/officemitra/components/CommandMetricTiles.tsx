import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const CommandMetricTiles: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({ frame, fps, config: { damping: 14 } });

  const metrics = [
    { label: "Active Practice Clients", value: "327", sub: "Multi-Client Roster", color: "#38bdf8" },
    { label: "Practice Compliance Score", value: "98.4%", sub: "Zero Late Filings", color: "#10b981" },
    { label: "Open Partner Reviews", value: "12", sub: "GSTR-2B Gate Cleared", color: "#fbbf24" },
    { label: "Critical Tax / Audit Risks", value: "0", sub: "Auditor Sign-off Ready", color: "#34d399" },
  ];

  // Transition to client success comparison at frame 110
  const showSuccessStory = frame >= 110;
  const successEntrance = spring({
    frame: frame - 110,
    fps,
    config: { damping: 15 },
  });

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 20,
        width: "100%",
        maxWidth: 1100,
        opacity: interpolate(entrance, [0, 1], [0, 1]),
      }}
    >
      {/* 4 Executive Metric HUD Tiles */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 16,
          width: "100%",
        }}
      >
        {metrics.map((m) => (
          <div
            key={m.label}
            style={{
              backgroundColor: "rgba(15, 23, 42, 0.85)",
              border: `1px solid rgba(148, 163, 184, 0.25)`,
              borderRadius: 14,
              padding: "18px 20px",
              display: "flex",
              flexDirection: "column",
              gap: 8,
              backdropFilter: "blur(14px)",
              boxShadow: "0 10px 25px rgba(0, 0, 0, 0.4)",
            }}
          >
            <span style={{ fontSize: 13, color: "#94a3b8", fontFamily: "Inter, sans-serif", fontWeight: 500 }}>
              {m.label}
            </span>
            <span
              style={{
                fontSize: 32,
                fontWeight: 800,
                color: m.color,
                fontFamily: "JetBrains Mono, monospace",
                letterSpacing: "-0.02em",
              }}
            >
              {m.value}
            </span>
            <span style={{ fontSize: 11, color: "#64748b", fontFamily: "Inter, sans-serif" }}>
              {m.sub}
            </span>
          </div>
        ))}
      </div>

      {/* Client Success Narrative Banner (Transforms from compliance to scale) */}
      {showSuccessStory && (
        <div
          style={{
            width: "100%",
            backgroundColor: "rgba(15, 23, 42, 0.95)",
            border: "2px solid rgba(56, 189, 248, 0.5)",
            borderRadius: 16,
            padding: "20px 32px",
            display: "flex",
            justifyContent: "space-around",
            alignItems: "center",
            boxShadow: "0 0 35px rgba(56, 189, 248, 0.25)",
            opacity: interpolate(successEntrance, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(successEntrance, [0, 1], [20, 0])}px)`,
          }}
        >
          {/* Before */}
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            <span
              style={{
                fontSize: 11,
                color: "#94a3b8",
                fontWeight: 700,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
              }}
            >
              Before OfficeMitra
            </span>
            <div style={{ display: "flex", gap: 20, alignItems: "baseline" }}>
              <span style={{ fontSize: 24, fontWeight: 700, color: "#cbd5e1" }}>
                52 <span style={{ fontSize: 14, color: "#94a3b8", fontWeight: 500 }}>Clients</span>
              </span>
              <span style={{ color: "#475569", fontSize: 18 }}>•</span>
              <span style={{ fontSize: 24, fontWeight: 700, color: "#cbd5e1" }}>
                14 <span style={{ fontSize: 14, color: "#94a3b8", fontWeight: 500 }}>Staff</span>
              </span>
            </div>
            <span style={{ fontSize: 12, color: "#f87171" }}>Manual bottlenecks & overtime</span>
          </div>

          {/* Dynamic Expansion Arrow */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 4,
            }}
          >
            <span style={{ fontSize: 24, color: "#38bdf8", fontWeight: 800 }}>➔</span>
            <span
              style={{
                fontSize: 11,
                color: "#38bdf8",
                fontWeight: 700,
                backgroundColor: "rgba(56, 189, 248, 0.15)",
                padding: "2px 10px",
                borderRadius: 20,
              }}
            >
              6.2× PRACTICE SCALE
            </span>
          </div>

          {/* After */}
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            <span
              style={{
                fontSize: 11,
                color: "#34d399",
                fontWeight: 700,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
              }}
            >
              After OfficeMitra + SSDV
            </span>
            <div style={{ display: "flex", gap: 20, alignItems: "baseline" }}>
              <span style={{ fontSize: 28, fontWeight: 800, color: "#38bdf8" }}>
                327 <span style={{ fontSize: 14, color: "#94a3b8", fontWeight: 500 }}>Clients</span>
              </span>
              <span style={{ color: "#475569", fontSize: 18 }}>•</span>
              <span style={{ fontSize: 28, fontWeight: 800, color: "#34d399" }}>
                16 <span style={{ fontSize: 14, color: "#94a3b8", fontWeight: 500 }}>Staff</span>
              </span>
            </div>
            <span style={{ fontSize: 12, color: "#34d399" }}>Automated double-entry & advisory</span>
          </div>
        </div>
      )}
    </div>
  );
};
