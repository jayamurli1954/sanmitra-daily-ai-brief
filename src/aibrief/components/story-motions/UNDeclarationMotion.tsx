import React from "react";
import { useCurrentFrame } from "remotion";

export const UNDeclarationMotion: React.FC = () => {
  const frame = useCurrentFrame();

  const globeRotation = (frame * 0.8) % 360;
  const count = Math.min(22, Math.floor(frame / 12) + 1);

  return (
    <div
      style={{
        position: "absolute",
        top: 72,
        left: 0,
        width: 1920,
        height: 720,
        overflow: "hidden",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 100px",
      }}
    >
      {/* Background Cyan Ambient Glow */}
      <div
        style={{
          position: "absolute",
          top: "20%",
          left: "25%",
          width: 700,
          height: 700,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(14, 165, 233, 0.22) 0%, transparent 70%)",
          filter: "blur(70px)",
          pointerEvents: "none",
        }}
      />

      {/* LEFT: ROTATING 3D WIREFRAME GLOBE WITH MEMBER PINS */}
      <div style={{ width: 600, height: 600, position: "relative", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <svg viewBox="0 0 400 400" width="100%" height="100%">
          <defs>
            <radialGradient id="unGlobeGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#0284c7" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#030712" stopOpacity="0.1" />
            </radialGradient>
          </defs>
          <circle cx="200" cy="200" r="170" fill="url(#unGlobeGrad)" stroke="#38bdf8" strokeWidth="2" />
          
          {/* Latitude Lines */}
          <ellipse cx="200" cy="200" rx="170" ry="60" fill="none" stroke="#38bdf8" strokeWidth="1.2" opacity="0.6" />
          <ellipse cx="200" cy="200" rx="170" ry="120" fill="none" stroke="#38bdf8" strokeWidth="1.2" opacity="0.5" />
          
          {/* Rotating Longitude */}
          <ellipse
            cx="200"
            cy="200"
            rx={Math.abs(Math.sin((globeRotation * Math.PI) / 180) * 170)}
            ry="170"
            fill="none"
            stroke="#0ea5e9"
            strokeWidth="2"
          />

          {/* Member Nation Glowing Nodes */}
          {[15, 45, 80, 110, 150, 190, 230, 270, 310, 340].map((deg, i) => {
            const rad = ((globeRotation + deg) * Math.PI) / 180;
            const cx = 200 + Math.cos(rad) * 140;
            const cy = 200 + Math.sin(rad) * 50;
            return (
              <circle
                key={i}
                cx={cx}
                cy={cy}
                r="5"
                fill="#38bdf8"
              />
            );
          })}
        </svg>

        {/* Center Live Tally Badge */}
        <div
          style={{
            position: "absolute",
            backgroundColor: "rgba(15, 23, 42, 0.95)",
            border: "2px solid #38bdf8",
            borderRadius: 16,
            padding: "16px 28px",
            textAlign: "center",
            boxShadow: "0 8px 32px rgba(0,0,0,0.8)",
          }}
        >
          <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 800, letterSpacing: 1.5 }}>
            RATIFIED SIGNATORIES
          </div>
          <div style={{ color: "#38bdf8", fontSize: 44, fontWeight: 900, lineHeight: 1 }}>
            {count} / 22
          </div>
          <div style={{ color: "#ffffff", fontSize: 12, fontWeight: 700, marginTop: 4 }}>
            UNITED NATIONS GENEVA
          </div>
        </div>
      </div>

      {/* RIGHT: 4 PILLARS OF THE DECLARATION */}
      <div style={{ width: 880, display: "flex", flexDirection: "column", gap: 14 }}>
        {[
          { title: "HUMAN OVERSIGHT MANDATE", desc: "Frontier autonomous systems must remain under verified human control.", color: "#38bdf8" },
          { title: "MANDATORY PRE-TESTING", desc: "Rigorous capability stress-testing before commercial release.", color: "#10b981" },
          { title: "INCIDENT REPORTING PROTOCOL", desc: "Standardized cross-border notification channel for systemic risks.", color: "#f59e0b" },
          { title: "INTERNATIONAL HARMONIZATION", desc: "Preventing fragmented regulatory regimes across jurisdictions.", color: "#a855f7" },
        ].map((pillar, idx) => {
          const isActive = frame >= idx * 45;
          return (
            <div
              key={idx}
              style={{
                backgroundColor: "rgba(15, 23, 42, 0.85)",
                border: `2px solid ${isActive ? pillar.color : "rgba(255,255,255,0.1)"}`,
                borderRadius: 12,
                padding: "16px 24px",
                display: "flex",
                alignItems: "center",
                gap: 18,
                boxShadow: isActive ? `0 8px 24px ${pillar.color}22` : "none",
                transform: `translateX(${isActive ? 0 : 20}px)`,
                opacity: isActive ? 1 : 0.4,
                transition: "all 0.3s ease",
              }}
            >
              <div
                style={{
                  backgroundColor: pillar.color,
                  color: "#ffffff",
                  fontSize: 14,
                  fontWeight: 900,
                  width: 32,
                  height: 32,
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                0{idx + 1}
              </div>
              <div style={{ display: "flex", flexDirection: "column" }}>
                <span style={{ color: "#ffffff", fontSize: 17, fontWeight: 800 }}>{pillar.title}</span>
                <span style={{ color: "#94a3b8", fontSize: 13, fontWeight: 500 }}>{pillar.desc}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
