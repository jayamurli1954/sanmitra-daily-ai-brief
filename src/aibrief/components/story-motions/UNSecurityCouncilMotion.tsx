import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export const UNSecurityCouncilMotion: React.FC = () => {
  const frame = useCurrentFrame();

  // Subtle camera sweep & globe rotation
  const globeAngle = (frame * 0.7) % 360;
  const sweepX = interpolate(frame, [0, 900], [-30, 30], { extrapolateRight: "clamp" });
  const pulse = Math.sin(frame * 0.08) * 0.2 + 0.8;

  const delegates = [
    { country: "UNSC PRESIDENCY", role: "Special Session Chair", color: "#38bdf8", angle: 0 },
    { country: "UNITED STATES", role: "OpenAI Delegation", color: "#60a5fa", angle: 50 },
    { country: "CHINA", role: "DeepSeek Delegation", color: "#ef4444", angle: 110 },
    { country: "UNITED KINGDOM", role: "Safety Taskforce", color: "#38bdf8", angle: 170 },
    { country: "ANTHROPIC", role: "Frontier Lab Briefing", color: "#d97706", angle: 230 },
    { country: "FRANCE", role: "AI Governance Rapporteur", color: "#818cf8", angle: 290 },
  ];

  return (
    <div
      style={{
        position: "absolute",
        top: 72,
        left: 0,
        width: 1920,
        height: 760,
        overflow: "hidden",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 100px",
        transform: `translateX(${sweepX}px)`,
      }}
    >
      {/* Ambient Council Room Glow */}
      <div
        style={{
          position: "absolute",
          top: "15%",
          left: "20%",
          width: 800,
          height: 800,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(14, 165, 233, 0.18) 0%, transparent 70%)",
          filter: "blur(80px)",
          pointerEvents: "none",
        }}
      />

      {/* LEFT: UN SECURITY COUNCIL CHAMBER & CIRCULAR TABLE VISUALIZATION */}
      <div
        style={{
          width: 720,
          height: 620,
          position: "relative",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <svg viewBox="0 0 500 500" width="100%" height="100%">
          <defs>
            <radialGradient id="unCouncilGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#0369a1" stopOpacity="0.35" />
              <stop offset="70%" stopColor="#0c1e3d" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#030712" stopOpacity="0.95" />
            </radialGradient>
            <linearGradient id="unRingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38bdf8" />
              <stop offset="100%" stopColor="#0284c7" />
            </linearGradient>
          </defs>

          {/* Circular Council Floor */}
          <circle cx="250" cy="250" r="230" fill="url(#unCouncilGrad)" stroke="#1e3a5f" strokeWidth="2" />
          <circle cx="250" cy="250" r="185" fill="none" stroke="#38bdf8" strokeWidth="1.5" strokeDasharray="4 4" opacity="0.6" />

          {/* Central Rotating Digital Globe */}
          <circle cx="250" cy="250" r="110" fill="#040b19" stroke="url(#unRingGrad)" strokeWidth="2.5" />
          <ellipse
            cx="250"
            cy="250"
            rx={Math.abs(Math.sin((globeAngle * Math.PI) / 180) * 110)}
            ry="110"
            fill="none"
            stroke="#38bdf8"
            strokeWidth="1.8"
            opacity="0.8"
          />
          <ellipse cx="250" cy="250" rx="110" ry="40" fill="none" stroke="#38bdf8" strokeWidth="1.2" opacity="0.5" />
          <ellipse cx="250" cy="250" rx="110" ry="80" fill="none" stroke="#38bdf8" strokeWidth="1.2" opacity="0.5" />

          {/* Center UN Emblem Core */}
          <circle cx="250" cy="250" r="16" fill="#38bdf8" opacity={pulse * 0.9} />
          <text x="250" y="254" textAnchor="middle" fill="#030712" fontSize="9" fontWeight="900" fontFamily="sans-serif">
            UNSC
          </text>

          {/* Circular Table Seating Nodes & AI Network Beam Overlays */}
          {delegates.map((d, i) => {
            const rad = ((d.angle + frame * 0.2) * Math.PI) / 180;
            const x = 250 + Math.cos(rad) * 185;
            const y = 250 + Math.sin(rad) * 185;
            return (
              <g key={i}>
                <line x1="250" y1="250" x2={x} y2={y} stroke={d.color} strokeWidth="1.2" opacity="0.4" strokeDasharray="2 2" />
                <circle cx={x} cy={y} r="18" fill="#0f172a" stroke={d.color} strokeWidth="2.5" />
                <circle cx={x} cy={y} r="6" fill={d.color} />
              </g>
            );
          })}
        </svg>

        {/* Live Status Overlay Tag */}
        <div
          style={{
            position: "absolute",
            bottom: 20,
            left: 20,
            backgroundColor: "rgba(15, 23, 42, 0.9)",
            border: "1px solid #38bdf8",
            borderRadius: 6,
            padding: "6px 14px",
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <div style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: "#38bdf8", boxShadow: "0 0 8px #38bdf8" }} />
          <span style={{ color: "#f8fafc", fontSize: 11, fontWeight: 800, letterSpacing: 1.5 }}>
            UNSC CHAMBER • BRIEFING ON FRONTIER RISKS
          </span>
        </div>
      </div>

      {/* RIGHT: TRILATERAL BRIEFING MATRIX & MULTILATERAL TELEMETRY */}
      <div style={{ width: 880, display: "flex", flexDirection: "column", gap: 16 }}>
        {/* Banner Card */}
        <div
          style={{
            backgroundColor: "rgba(15, 23, 42, 0.92)",
            border: "1px solid rgba(56, 189, 248, 0.35)",
            borderRadius: 14,
            padding: "20px 28px",
            boxShadow: "0 16px 40px rgba(0, 0, 0, 0.6)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
            <span style={{ color: "#38bdf8", fontSize: 12, fontWeight: 900, letterSpacing: 2 }}>
              HISTORIC MULTILATERAL TESTIMONY
            </span>
            <span style={{ color: "#94a3b8", fontSize: 11, fontWeight: 700 }}>NEW YORK CITY • UN HEADQUARTERS</span>
          </div>
          <div style={{ color: "#ffffff", fontSize: 24, fontWeight: 900, lineHeight: 1.25, marginBottom: 8 }}>
            DeepSeek, OpenAI & Anthropic Address UN Security Council
          </div>
          <div style={{ color: "#cbd5e1", fontSize: 14, lineHeight: 1.4 }}>
            First time a Chinese frontier AI developer sits directly at the Security Council AI consultations table alongside leading Western laboratories.
          </div>
        </div>

        {/* 3 Delegation Columns */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
          {/* DeepSeek */}
          <div
            style={{
              backgroundColor: "rgba(15, 23, 42, 0.88)",
              border: "1px solid rgba(239, 68, 68, 0.4)",
              borderRadius: 12,
              padding: "16px 18px",
            }}
          >
            <div style={{ color: "#ef4444", fontSize: 11, fontWeight: 900, letterSpacing: 1.5, marginBottom: 6 }}>
              CHINA / DEEPSEEK
            </div>
            <div style={{ color: "#ffffff", fontSize: 16, fontWeight: 800, marginBottom: 4 }}>
              Frontier Multilateralism
            </div>
            <div style={{ color: "#94a3b8", fontSize: 12, lineHeight: 1.35 }}>
              Focus on sovereign AI capabilities, open-weight transparency, and non-discriminatory safety protocols.
            </div>
          </div>

          {/* OpenAI */}
          <div
            style={{
              backgroundColor: "rgba(15, 23, 42, 0.88)",
              border: "1px solid rgba(96, 165, 250, 0.4)",
              borderRadius: 12,
              padding: "16px 18px",
            }}
          >
            <div style={{ color: "#60a5fa", fontSize: 11, fontWeight: 900, letterSpacing: 1.5, marginBottom: 6 }}>
              USA / OPENAI
            </div>
            <div style={{ color: "#ffffff", fontSize: 16, fontWeight: 800, marginBottom: 4 }}>
              CBRN & Catastrophic Risk
            </div>
            <div style={{ color: "#94a3b8", fontSize: 12, lineHeight: 1.35 }}>
              Briefings on biosecurity boundaries, cyber-offensive containment, and pre-deployment red teaming.
            </div>
          </div>

          {/* Anthropic */}
          <div
            style={{
              backgroundColor: "rgba(15, 23, 42, 0.88)",
              border: "1px solid rgba(217, 119, 6, 0.4)",
              borderRadius: 12,
              padding: "16px 18px",
            }}
          >
            <div style={{ color: "#d97706", fontSize: 11, fontWeight: 900, letterSpacing: 1.5, marginBottom: 6 }}>
              USA / ANTHROPIC
            </div>
            <div style={{ color: "#ffffff", fontSize: 16, fontWeight: 800, marginBottom: 4 }}>
              Responsible Scaling
            </div>
            <div style={{ color: "#94a3b8", fontSize: 12, lineHeight: 1.35 }}>
              Frameworks for Responsible Scaling Policies (RSP) and verifiable safety guarantees across compute tiers.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
