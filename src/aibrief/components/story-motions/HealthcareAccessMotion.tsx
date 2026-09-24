import React from "react";
import { useCurrentFrame } from "remotion";

export const HealthcareAccessMotion: React.FC = () => {
  const frame = useCurrentFrame();

  const pulse = Math.sin(frame * 0.1) * 0.2 + 0.8;

  // Representative coordinates on world map
  const globalPointers = [
    { x: 260, y: 190, name: "Sub-Saharan Africa Desk" },
    { x: 310, y: 170, name: "South Asia Regional Hub" },
    { x: 360, y: 220, name: "Southeast Asia Clinics" },
    { x: 190, y: 210, name: "Latin America Field Network" },
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
      }}
    >
      {/* Background Cyan/Emerald Clinical Atmosphere */}
      <div
        style={{
          position: "absolute",
          top: "10%",
          left: "30%",
          width: 800,
          height: 800,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(16, 185, 129, 0.16) 0%, rgba(6, 182, 212, 0.12) 50%, transparent 70%)",
          filter: "blur(90px)",
          pointerEvents: "none",
        }}
      />

      {/* LEFT: GLOBAL CLINICAL ACCESS MAP (100 NATIONS) */}
      <div
        style={{
          width: 900,
          height: 560,
          backgroundColor: "rgba(6, 11, 23, 0.94)",
          border: "1px solid rgba(16, 185, 129, 0.35)",
          borderRadius: 16,
          padding: "24px 28px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          boxShadow: "0 20px 50px rgba(0, 0, 0, 0.75)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: "#10b981", boxShadow: "0 0 10px #10b981" }} />
            <span style={{ color: "#10b981", fontSize: 13, fontWeight: 900, letterSpacing: 2 }}>
              GLOBAL CLINICAL EQUITY NETWORK
            </span>
          </div>
          <span style={{ backgroundColor: "rgba(16, 185, 129, 0.15)", color: "#34d399", padding: "4px 12px", borderRadius: 6, fontSize: 12, fontWeight: 800 }}>
            ~100 LMIC NATIONS
          </span>
        </div>

        {/* Global Map Stylization */}
        <div style={{ position: "relative", width: "100%", height: 380, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <svg viewBox="0 0 500 300" width="100%" height="100%">
            <defs>
              <radialGradient id="healthGrad" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#059669" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#030712" stopOpacity="0.1" />
              </radialGradient>
            </defs>

            {/* Stylized Continents Outlines */}
            {/* Americas */}
            <path d="M 80 80 Q 120 70 140 100 T 130 160 T 160 210 T 140 270" fill="none" stroke="#1e3a5f" strokeWidth="1.5" strokeDasharray="3 3" />
            {/* EMEA */}
            <path d="M 230 70 Q 280 60 290 100 T 260 180 T 270 250" fill="none" stroke="#1e3a5f" strokeWidth="1.5" strokeDasharray="3 3" />
            {/* Asia & Pacific */}
            <path d="M 320 80 Q 400 70 430 110 T 380 190 T 430 260" fill="none" stroke="#1e3a5f" strokeWidth="1.5" strokeDasharray="3 3" />

            {/* Glowing Healthcare Access Nodes */}
            {Array.from({ length: 45 }).map((_, i) => {
              const x = 120 + ((i * 37) % 320);
              const y = 90 + ((i * 29) % 170);
              const nodePulse = Math.sin((frame + i * 15) * 0.1) * 0.3 + 0.7;
              return (
                <g key={i}>
                  <circle cx={x} cy={y} r="3" fill="#10b981" opacity={nodePulse} />
                </g>
              );
            })}

            {/* Hub Callouts */}
            {globalPointers.map((p, i) => (
              <g key={i}>
                <circle cx={p.x} cy={p.y} r="12" fill="none" stroke="#34d399" strokeWidth="1.5" opacity={pulse} />
                <circle cx={p.x} cy={p.y} r="4" fill="#10b981" />
                <text x={p.x + 8} y={p.y - 6} fill="#f1f5f9" fontSize="9" fontWeight="800">
                  {p.name}
                </text>
              </g>
            ))}
          </svg>
        </div>

        {/* Access Metrics Bar */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
          <div style={{ backgroundColor: "rgba(15, 23, 42, 0.8)", padding: "10px 14px", borderRadius: 8, border: "1px solid rgba(16, 185, 129, 0.2)" }}>
            <div style={{ color: "#94a3b8", fontSize: 10, fontWeight: 700 }}>COVERAGE SCOPE</div>
            <div style={{ color: "#34d399", fontSize: 18, fontWeight: 900 }}>100 Countries</div>
          </div>
          <div style={{ backgroundColor: "rgba(15, 23, 42, 0.8)", padding: "10px 14px", borderRadius: 8, border: "1px solid rgba(16, 185, 129, 0.2)" }}>
            <div style={{ color: "#94a3b8", fontSize: 10, fontWeight: 700 }}>TARGET USERS</div>
            <div style={{ color: "#ffffff", fontSize: 18, fontWeight: 900 }}>Frontline MDs</div>
          </div>
          <div style={{ backgroundColor: "rgba(15, 23, 42, 0.8)", padding: "10px 14px", borderRadius: 8, border: "1px solid rgba(16, 185, 129, 0.2)" }}>
            <div style={{ color: "#94a3b8", fontSize: 10, fontWeight: 700 }}>SUBSIDY MODEL</div>
            <div style={{ color: "#38bdf8", fontSize: 18, fontWeight: 900 }}>Pro Bono Access</div>
          </div>
        </div>
      </div>

      {/* RIGHT: OPENEVIDENCE CLINICAL DECISION SUPPORT ARCHITECTURE */}
      <div style={{ width: 780, display: "flex", flexDirection: "column", gap: 16 }}>
        {/* Core Card */}
        <div
          style={{
            backgroundColor: "rgba(15, 23, 42, 0.94)",
            border: "1px solid rgba(56, 189, 248, 0.35)",
            borderRadius: 16,
            padding: "24px 28px",
            boxShadow: "0 16px 40px rgba(0, 0, 0, 0.7)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
            <span style={{ color: "#38bdf8", fontSize: 12, fontWeight: 900, letterSpacing: 2 }}>
              CLINICAL AI TELEMETRY
            </span>
            <span style={{ color: "#10b981", fontSize: 11, fontWeight: 800 }}>PEER-REVIEWED CORPUS</span>
          </div>

          <h3 style={{ color: "#ffffff", fontSize: 24, fontWeight: 900, margin: "0 0 10px 0" }}>
            OpenEvidence + Anthropic Claude Core
          </h3>
          <p style={{ color: "#cbd5e1", fontSize: 14, lineHeight: 1.45, margin: "0 0 20px 0" }}>
            Combines OpenEvidence's medically verified clinical database with Claude's advanced multi-modal diagnostic reasoning, delivering evidence-backed guidance directly to mobile devices in remote clinics.
          </p>

          {/* Process Flow */}
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, backgroundColor: "rgba(10, 18, 35, 0.7)", padding: "10px 16px", borderRadius: 8 }}>
              <div style={{ width: 24, height: 24, borderRadius: "50%", backgroundColor: "rgba(56, 189, 248, 0.2)", border: "1px solid #38bdf8", display: "flex", alignItems: "center", justifyContent: "center", color: "#38bdf8", fontSize: 12, fontWeight: 900 }}>1</div>
              <div style={{ color: "#f8fafc", fontSize: 13, fontWeight: 700 }}>Physician enters patient clinical parameters & symptoms</div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 12, backgroundColor: "rgba(10, 18, 35, 0.7)", padding: "10px 16px", borderRadius: 8 }}>
              <div style={{ width: 24, height: 24, borderRadius: "50%", backgroundColor: "rgba(16, 185, 129, 0.2)", border: "1px solid #10b981", display: "flex", alignItems: "center", justifyContent: "center", color: "#10b981", fontSize: 12, fontWeight: 900 }}>2</div>
              <div style={{ color: "#f8fafc", fontSize: 13, fontWeight: 700 }}>OpenEvidence indexes 35M+ peer-reviewed medical publications</div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 12, backgroundColor: "rgba(10, 18, 35, 0.7)", padding: "10px 16px", borderRadius: 8 }}>
              <div style={{ width: 24, height: 24, borderRadius: "50%", backgroundColor: "rgba(217, 119, 6, 0.2)", border: "1px solid #d97706", display: "flex", alignItems: "center", justifyContent: "center", color: "#d97706", fontSize: 12, fontWeight: 900 }}>3</div>
              <div style={{ color: "#f8fafc", fontSize: 13, fontWeight: 700 }}>Claude synthesizes differential diagnosis with citations</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
