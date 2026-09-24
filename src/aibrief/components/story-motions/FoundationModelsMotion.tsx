import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export const FoundationModelsMotion: React.FC = () => {
  const frame = useCurrentFrame();

  const pulse = Math.sin(frame * 0.1) * 0.15 + 0.85;
  const graphProgress = interpolate(frame, [0, 90], [0.1, 1.0], { extrapolateRight: "clamp" });

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
      {/* Background Amber/Blue Ambient Command Center Lighting */}
      <div
        style={{
          position: "absolute",
          top: "10%",
          right: "20%",
          width: 700,
          height: 700,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(16, 163, 127, 0.14) 0%, rgba(217, 119, 6, 0.12) 50%, transparent 70%)",
          filter: "blur(90px)",
          pointerEvents: "none",
        }}
      />

      {/* LEFT: CLAUDE OPUS 5.5 COMMAND PANEL */}
      <div
        style={{
          width: 580,
          backgroundColor: "rgba(15, 23, 42, 0.94)",
          border: "1px solid rgba(217, 119, 6, 0.4)",
          borderRadius: 16,
          padding: "24px 28px",
          boxShadow: "0 16px 40px rgba(0, 0, 0, 0.7)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#d97706", boxShadow: "0 0 10px #d97706" }} />
            <span style={{ color: "#d97706", fontSize: 13, fontWeight: 900, letterSpacing: 2 }}>
              ANTHROPIC FRONTIER TIER
            </span>
          </div>
          <span style={{ backgroundColor: "rgba(217, 119, 6, 0.2)", color: "#fbbf24", padding: "3px 10px", borderRadius: 4, fontSize: 11, fontWeight: 800 }}>
            OPUS 5.5
          </span>
        </div>

        <h3 style={{ color: "#ffffff", fontSize: 26, fontWeight: 900, margin: "0 0 12px 0" }}>
          Claude Opus 5.5
        </h3>
        <p style={{ color: "#94a3b8", fontSize: 14, lineHeight: 1.4, margin: "0 0 20px 0" }}>
          Engineered specifically for complex enterprise workflows, multi-step agent reasoning, and autonomous code execution at 60% lower cost.
        </p>

        {/* Telemetry Metrics */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div style={{ backgroundColor: "rgba(10, 18, 35, 0.8)", padding: "12px 14px", borderRadius: 8, border: "1px solid rgba(217, 119, 6, 0.25)" }}>
            <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 700 }}>REASONING EFFICIENCY</div>
            <div style={{ color: "#fbbf24", fontSize: 20, fontWeight: 900 }}>+42% / Dollar</div>
          </div>
          <div style={{ backgroundColor: "rgba(10, 18, 35, 0.8)", padding: "12px 14px", borderRadius: 8, border: "1px solid rgba(217, 119, 6, 0.25)" }}>
            <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 700 }}>ENTERPRISE TARGET</div>
            <div style={{ color: "#ffffff", fontSize: 20, fontWeight: 900 }}>Fortune 500</div>
          </div>
        </div>
      </div>

      {/* CENTER: COMPUTATIONAL TELEMETRY & COST CURVES */}
      <div
        style={{
          width: 500,
          height: 520,
          backgroundColor: "rgba(6, 11, 23, 0.95)",
          border: "1px solid rgba(56, 189, 248, 0.35)",
          borderRadius: 16,
          padding: "20px 24px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          boxShadow: "0 20px 50px rgba(0, 0, 0, 0.8)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ color: "#38bdf8", fontSize: 12, fontWeight: 900, letterSpacing: 1.5 }}>
            ENTERPRISE ROI TELEMETRY
          </span>
          <span style={{ color: "#64748b", fontSize: 11, fontWeight: 700 }}>TOKEN EFFICIENCY</span>
        </div>

        {/* Cost vs Performance Graph */}
        <div style={{ position: "relative", width: "100%", height: 260 }}>
          <svg viewBox="0 0 400 240" width="100%" height="100%">
            {/* Grid */}
            <line x1="40" y1="20" x2="40" y2="200" stroke="#1e293b" strokeWidth="1" />
            <line x1="40" y1="200" x2="380" y2="200" stroke="#1e293b" strokeWidth="1" />
            <line x1="40" y1="140" x2="380" y2="140" stroke="#1e293b" strokeWidth="0.8" strokeDasharray="3 3" />
            <line x1="40" y1="80" x2="380" y2="80" stroke="#1e293b" strokeWidth="0.8" strokeDasharray="3 3" />

            {/* Previous Gen Curve (Grey) */}
            <path
              d="M 50 180 Q 200 130 360 40"
              fill="none"
              stroke="#475569"
              strokeWidth="2"
              strokeDasharray="4 4"
            />
            <text x="360" y="32" fill="#64748b" fontSize="10" textAnchor="end">Previous Gen Cost Curve</text>

            {/* Next Gen Sol & Opus 5.5 Curve (Cyan/Green Glow) */}
            <path
              d="M 50 190 Q 200 170 360 90"
              fill="none"
              stroke="#38bdf8"
              strokeWidth="3.5"
              strokeDasharray="400"
              strokeDashoffset={400 * (1 - graphProgress)}
            />
            <circle cx="360" cy="90" r="5" fill="#38bdf8" opacity={pulse} />
            <text x="360" y="80" fill="#38bdf8" fontSize="11" fontWeight="800" textAnchor="end">
              2026 Enterprise Efficiency Frontier
            </text>
          </svg>
        </div>

        {/* Summary Footer */}
        <div style={{ backgroundColor: "rgba(15, 23, 42, 0.8)", padding: "10px 14px", borderRadius: 8, textAlign: "center" }}>
          <span style={{ color: "#f1f5f9", fontSize: 13, fontWeight: 700 }}>
            Macro Shift: Transition from Raw Size to <span style={{ color: "#38bdf8" }}>Measurable Enterprise ROI</span>
          </span>
        </div>
      </div>

      {/* RIGHT: OPENAI GPT-6 SOL & LUNA COMMAND PANEL */}
      <div
        style={{
          width: 580,
          backgroundColor: "rgba(15, 23, 42, 0.94)",
          border: "1px solid rgba(16, 185, 129, 0.4)",
          borderRadius: 16,
          padding: "24px 28px",
          boxShadow: "0 16px 40px rgba(0, 0, 0, 0.7)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#10b981", boxShadow: "0 0 10px #10b981" }} />
            <span style={{ color: "#10b981", fontSize: 13, fontWeight: 900, letterSpacing: 2 }}>
              OPENAI DUAL RELEASE
            </span>
          </div>
          <span style={{ backgroundColor: "rgba(16, 185, 129, 0.2)", color: "#34d399", padding: "3px 10px", borderRadius: 4, fontSize: 11, fontWeight: 800 }}>
            GPT-6 SOL & LUNA
          </span>
        </div>

        <h3 style={{ color: "#ffffff", fontSize: 26, fontWeight: 900, margin: "0 0 12px 0" }}>
          GPT-6 Sol & Luna
        </h3>
        <p style={{ color: "#94a3b8", fontSize: 14, lineHeight: 1.4, margin: "0 0 20px 0" }}>
          Dual-tier architecture offering Sol for deep reasoning and Luna for high-frequency, low-latency microservices with dramatic token cost reductions.
        </p>

        {/* Telemetry Metrics */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div style={{ backgroundColor: "rgba(10, 18, 35, 0.8)", padding: "12px 14px", borderRadius: 8, border: "1px solid rgba(16, 185, 129, 0.25)" }}>
            <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 700 }}>LUNA INFERENCE SPEED</div>
            <div style={{ color: "#34d399", fontSize: 20, fontWeight: 900 }}>180 Tokens/sec</div>
          </div>
          <div style={{ backgroundColor: "rgba(10, 18, 35, 0.8)", padding: "12px 14px", borderRadius: 8, border: "1px solid rgba(16, 185, 129, 0.25)" }}>
            <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 700 }}>COST REDUCTION</div>
            <div style={{ color: "#ffffff", fontSize: 20, fontWeight: 900 }}>-65% vs Predecessor</div>
          </div>
        </div>
      </div>
    </div>
  );
};
