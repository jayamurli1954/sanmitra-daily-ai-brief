import React from "react";

export const AlibabaZhenwuMotion: React.FC = () => {
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
      {/* Background Red/Orange Sovereign Compute Glow */}
      <div
        style={{
          position: "absolute",
          top: "15%",
          left: "20%",
          width: 800,
          height: 800,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(239, 68, 68, 0.16) 0%, rgba(249, 115, 22, 0.12) 50%, transparent 70%)",
          filter: "blur(90px)",
          pointerEvents: "none",
        }}
      />

      {/* LEFT: ZHENWU V900 SILICON DIE VISUALIZATION */}
      <div
        style={{
          width: 700,
          height: 600,
          position: "relative",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <svg viewBox="0 0 500 500" width="100%" height="100%">
          <defs>
            <linearGradient id="zhenwuSubstrate" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#1e293b" />
              <stop offset="100%" stopColor="#0f172a" />
            </linearGradient>
            <linearGradient id="goldTraces" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#f59e0b" />
              <stop offset="50%" stopColor="#ef4444" />
              <stop offset="100%" stopColor="#f59e0b" />
            </linearGradient>
          </defs>

          {/* Ceramic Substrate Package */}
          <rect x="70" y="70" width="360" height="360" rx="16" fill="url(#zhenwuSubstrate)" stroke="#ef4444" strokeWidth="2.5" />

          {/* Interconnect Pins */}
          {Array.from({ length: 18 }).map((_, i) => (
            <rect key={`pin-t-${i}`} x={95 + i * 18} y="55" width="8" height="15" fill="#f59e0b" rx="2" />
          ))}
          {Array.from({ length: 18 }).map((_, i) => (
            <rect key={`pin-b-${i}`} x={95 + i * 18} y="430" width="8" height="15" fill="#f59e0b" rx="2" />
          ))}

          {/* Dual Compute Chiplet Dies */}
          <rect x="110" y="110" width="130" height="280" rx="8" fill="#090d16" stroke="url(#goldTraces)" strokeWidth="2" />
          <rect x="260" y="110" width="130" height="280" rx="8" fill="#090d16" stroke="url(#goldTraces)" strokeWidth="2" />

          {/* High Bandwidth Memory (HBM) Stacks (4 Blocks) */}
          <rect x="125" y="125" width="100" height="50" rx="4" fill="#1e1b4b" stroke="#818cf8" strokeWidth="1.5" />
          <text x="175" y="155" textAnchor="middle" fill="#818cf8" fontSize="10" fontWeight="900">HBM3e STACK A</text>

          <rect x="125" y="325" width="100" height="50" rx="4" fill="#1e1b4b" stroke="#818cf8" strokeWidth="1.5" />
          <text x="175" y="355" textAnchor="middle" fill="#818cf8" fontSize="10" fontWeight="900">HBM3e STACK B</text>

          <rect x="275" y="125" width="100" height="50" rx="4" fill="#1e1b4b" stroke="#818cf8" strokeWidth="1.5" />
          <text x="325" y="155" textAnchor="middle" fill="#818cf8" fontSize="10" fontWeight="900">HBM3e STACK C</text>

          <rect x="275" y="325" width="100" height="50" rx="4" fill="#1e1b4b" stroke="#818cf8" strokeWidth="1.5" />
          <text x="325" y="355" textAnchor="middle" fill="#818cf8" fontSize="10" fontWeight="900">HBM3e STACK D</text>

          {/* Central Neural Processing Matrix */}
          <rect x="125" y="195" width="250" height="110" rx="6" fill="#180c0e" stroke="#ef4444" strokeWidth="2" />
          <text x="250" y="240" textAnchor="middle" fill="#ffffff" fontSize="16" fontWeight="950" letterSpacing="2">
            ZHENWU V900
          </text>
          <text x="250" y="265" textAnchor="middle" fill="#ef4444" fontSize="11" fontWeight="800" letterSpacing="1">
            ALIBABA CLOUD NPU TENSOR FABRIC
          </text>
          <text x="250" y="285" textAnchor="middle" fill="#94a3b8" fontSize="9">
            Sovereign High-Density Architecture
          </text>
        </svg>

        {/* Live Silicon Status Pill */}
        <div
          style={{
            position: "absolute",
            bottom: 20,
            left: 20,
            backgroundColor: "rgba(15, 23, 42, 0.9)",
            border: "1px solid #ef4444",
            borderRadius: 6,
            padding: "6px 14px",
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <div style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: "#ef4444", boxShadow: "0 0 8px #ef4444" }} />
          <span style={{ color: "#f8fafc", fontSize: 11, fontWeight: 800, letterSpacing: 1.5 }}>
            FABRICATION METRICS • DOMESTIC SOVEREIGN ACCELERATOR
          </span>
        </div>
      </div>

      {/* RIGHT: HARDWARE SPECS & SOVEREIGN TELEMETRY */}
      <div style={{ width: 900, display: "flex", flexDirection: "column", gap: 16 }}>
        {/* Header Card */}
        <div
          style={{
            backgroundColor: "rgba(15, 23, 42, 0.94)",
            border: "1px solid rgba(239, 68, 68, 0.35)",
            borderRadius: 16,
            padding: "24px 28px",
            boxShadow: "0 16px 40px rgba(0, 0, 0, 0.7)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
            <span style={{ color: "#ef4444", fontSize: 12, fontWeight: 900, letterSpacing: 2 }}>
              CHINA SOVEREIGN SILICON
            </span>
            <span style={{ color: "#f59e0b", fontSize: 11, fontWeight: 800 }}>ALIBABA T-HEAD LABS</span>
          </div>

          <h3 style={{ color: "#ffffff", fontSize: 26, fontWeight: 900, margin: "0 0 10px 0" }}>
            Zhenwu V900 AI Supercomputing Accelerator
          </h3>
          <p style={{ color: "#cbd5e1", fontSize: 14, lineHeight: 1.45, margin: "0 0 18px 0" }}>
            Unveiled as Alibaba's flagship enterprise processor to power domestic LLM training clusters, mitigating ongoing Western semiconductor restrictions with advanced packaging and custom high-speed interconnects.
          </p>

          {/* 4 Hardware Key Specs */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 12 }}>
            <div style={{ backgroundColor: "rgba(10, 18, 35, 0.8)", padding: "12px 14px", borderRadius: 8, border: "1px solid rgba(239, 68, 68, 0.2)" }}>
              <div style={{ color: "#94a3b8", fontSize: 10, fontWeight: 700 }}>COMPUTE DENSITY</div>
              <div style={{ color: "#ef4444", fontSize: 18, fontWeight: 900 }}>FP8 / INT8</div>
              <div style={{ color: "#64748b", fontSize: 9 }}>Petascale Throughput</div>
            </div>
            <div style={{ backgroundColor: "rgba(10, 18, 35, 0.8)", padding: "12px 14px", borderRadius: 8, border: "1px solid rgba(239, 68, 68, 0.2)" }}>
              <div style={{ color: "#94a3b8", fontSize: 10, fontWeight: 700 }}>MEMORY BANDWIDTH</div>
              <div style={{ color: "#ffffff", fontSize: 18, fontWeight: 900 }}>3.2 TB/s</div>
              <div style={{ color: "#64748b", fontSize: 9 }}>High-Density HBM3e</div>
            </div>
            <div style={{ backgroundColor: "rgba(10, 18, 35, 0.8)", padding: "12px 14px", borderRadius: 8, border: "1px solid rgba(239, 68, 68, 0.2)" }}>
              <div style={{ color: "#94a3b8", fontSize: 10, fontWeight: 700 }}>CLUSTER INTERCONNECT</div>
              <div style={{ color: "#f59e0b", fontSize: 18, fontWeight: 900 }}>800 Gbps</div>
              <div style={{ color: "#64748b", fontSize: 9 }}>Ultra-Ethernet Fabric</div>
            </div>
            <div style={{ backgroundColor: "rgba(10, 18, 35, 0.8)", padding: "12px 14px", borderRadius: 8, border: "1px solid rgba(239, 68, 68, 0.2)" }}>
              <div style={{ color: "#94a3b8", fontSize: 10, fontWeight: 700 }}>DEPLOYMENT STATUS</div>
              <div style={{ color: "#10b981", fontSize: 18, fontWeight: 900 }}>Production</div>
              <div style={{ color: "#64748b", fontSize: 9 }}>Hyperscale Datacenters</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
