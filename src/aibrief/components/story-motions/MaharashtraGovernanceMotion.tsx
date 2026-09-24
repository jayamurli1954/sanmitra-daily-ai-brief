import React from "react";
import { useCurrentFrame } from "remotion";

export const MaharashtraGovernanceMotion: React.FC = () => {
  const frame = useCurrentFrame();

  const metricsCount = Math.min(2400000, Math.floor(frame * 35000));

  const governanceNodes = [
    { title: "University Academic Telemetry", metric: "65+ Universities", color: "#fbbf24", desc: "Curricular standard alignment & automated accreditation monitoring" },
    { title: "Student Predictive Retention", metric: "2.4M Students", color: "#10b981", desc: "Early intervention analytics identifying academic distress indicators" },
    { title: "Institutional Resource Allocation", metric: "4,200 Colleges", color: "#38bdf8", desc: "Automated faculty workload & laboratory infrastructure distribution" },
    { title: "Agentic Public Governance", metric: "Statewide API", color: "#f59e0b", desc: "Inter-departmental dashboard interoperability across Mumbai & Pune" },
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
      {/* Background Amber/Emerald Indian Tech Glow */}
      <div
        style={{
          position: "absolute",
          top: "15%",
          right: "20%",
          width: 800,
          height: 800,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(245, 158, 11, 0.16) 0%, rgba(16, 185, 129, 0.12) 50%, transparent 70%)",
          filter: "blur(90px)",
          pointerEvents: "none",
        }}
      />

      {/* LEFT: SMART STATE COMMAND CENTER & MAHARASHTRA HIGHER EDUCATION HUB */}
      <div
        style={{
          width: 700,
          backgroundColor: "rgba(15, 23, 42, 0.94)",
          border: "1px solid rgba(245, 158, 11, 0.4)",
          borderRadius: 16,
          padding: "26px 30px",
          boxShadow: "0 20px 50px rgba(0, 0, 0, 0.75)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#fbbf24", boxShadow: "0 0 10px #fbbf24" }} />
            <span style={{ color: "#fbbf24", fontSize: 13, fontWeight: 900, letterSpacing: 2 }}>
              INDIAN PUBLIC SECTOR AI DESK
            </span>
          </div>
          <span style={{ backgroundColor: "rgba(245, 158, 11, 0.2)", color: "#fde68a", padding: "4px 12px", borderRadius: 6, fontSize: 11, fontWeight: 800 }}>
            GOVT OF MAHARASHTRA
          </span>
        </div>

        <h3 style={{ color: "#ffffff", fontSize: 26, fontWeight: 900, margin: "0 0 8px 0" }}>
          AI, Data Analytics & Dashboard Governance Committee
        </h3>
        <div style={{ color: "#38bdf8", fontSize: 14, fontWeight: 800, marginBottom: 14 }}>
          Mandate: Institutionalizing Agentic AI in Higher Education Administration
        </div>
        <p style={{ color: "#94a3b8", fontSize: 14, lineHeight: 1.45, margin: "0 0 24px 0" }}>
          Maharashtra formalizes an apex governmental framework deploying real-time telemetry dashboards, student outcome models, and AI administrative assistance across all state-affiliated higher education institutions.
        </p>

        {/* Live Metrics Counter */}
        <div style={{ backgroundColor: "rgba(10, 18, 35, 0.8)", padding: "16px 20px", borderRadius: 10, border: "1px solid rgba(245, 158, 11, 0.25)" }}>
          <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 700, marginBottom: 4 }}>
            DIGITAL STUDENT ENROLLMENT UNDER AI GOVERNANCE PIPELINE
          </div>
          <div style={{ color: "#fbbf24", fontSize: 32, fontWeight: 950, letterSpacing: -0.5 }}>
            {metricsCount.toLocaleString()}+ Students
          </div>
          <div style={{ color: "#64748b", fontSize: 11, marginTop: 4 }}>
            Interfacing Mumbai University, SPPU Pune, and 4,000+ collegiate institutions
          </div>
        </div>
      </div>

      {/* RIGHT: 4 GOVERNANCE TIERS */}
      <div style={{ width: 950, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        {governanceNodes.map((n, i) => (
          <div
            key={i}
            style={{
              backgroundColor: "rgba(15, 23, 42, 0.92)",
              border: "1px solid rgba(56, 189, 248, 0.3)",
              borderRadius: 14,
              padding: "20px 22px",
              boxShadow: "0 10px 30px rgba(0, 0, 0, 0.6)",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
            }}
          >
            <div>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
                <span style={{ color: n.color, fontSize: 11, fontWeight: 900, letterSpacing: 1.5 }}>
                  TIER 0{i + 1} ARCHITECTURE
                </span>
                <span style={{ backgroundColor: "rgba(255, 255, 255, 0.08)", color: "#f8fafc", padding: "2px 8px", borderRadius: 4, fontSize: 11, fontWeight: 800 }}>
                  {n.metric}
                </span>
              </div>
              <div style={{ color: "#ffffff", fontSize: 18, fontWeight: 800, marginBottom: 8 }}>
                {n.title}
              </div>
              <div style={{ color: "#94a3b8", fontSize: 12, lineHeight: 1.4 }}>
                {n.desc}
              </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, borderTop: "1px solid rgba(255,255,255,0.08)", paddingTop: 10, marginTop: 14 }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: n.color }} />
              <span style={{ color: "#cbd5e1", fontSize: 11, fontWeight: 700 }}>Active State Mandate</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
