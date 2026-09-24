import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export const YouthAISafetyMotion: React.FC = () => {
  const frame = useCurrentFrame();

  const auditProgress = interpolate(frame, [0, 80], [0, 100], { extrapolateRight: "clamp" });

  const safetyPillars = [
    { name: "Cognitive Guardrails", status: "VERIFIED", score: "96%", desc: "Age-adaptive conversational boundaries & emotional dependence mitigation" },
    { name: "Algorithmic Exploitation Audit", status: "ACTIVE", score: "92%", desc: "Prohibition of hyper-targeted behavioral micro-persuasion loops" },
    { name: "Curricular AI Integrity", status: "STANDARDIZED", score: "94%", desc: "Fact verification & pedagogical safety for educational integrations" },
    { name: "Independent Red Teaming", status: "MANDATORY", score: "100%", desc: "Pre-deployment third-party certification independent of frontier lab claims" },
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
      {/* Background Cyan/Indigo Public Policy Aura */}
      <div
        style={{
          position: "absolute",
          top: "15%",
          right: "25%",
          width: 750,
          height: 750,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(56, 189, 248, 0.1) 50%, transparent 70%)",
          filter: "blur(90px)",
          pointerEvents: "none",
        }}
      />

      {/* LEFT: COMMON SENSE MEDIA / TOM SIEGEL INSTITUTE PROFILE */}
      <div
        style={{
          width: 700,
          backgroundColor: "rgba(15, 23, 42, 0.94)",
          border: "1px solid rgba(99, 102, 241, 0.4)",
          borderRadius: 16,
          padding: "26px 30px",
          boxShadow: "0 20px 50px rgba(0, 0, 0, 0.75)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#818cf8", boxShadow: "0 0 10px #818cf8" }} />
            <span style={{ color: "#818cf8", fontSize: 13, fontWeight: 900, letterSpacing: 2 }}>
              POLICY & CHILD WELLBEING
            </span>
          </div>
          <span style={{ backgroundColor: "rgba(99, 102, 241, 0.18)", color: "#a5b4fc", padding: "4px 12px", borderRadius: 6, fontSize: 11, fontWeight: 800 }}>
            INDEPENDENT WATCHDOG
          </span>
        </div>

        <h3 style={{ color: "#ffffff", fontSize: 26, fontWeight: 900, margin: "0 0 10px 0" }}>
          Youth AI Safety Institute
        </h3>
        <div style={{ color: "#38bdf8", fontSize: 14, fontWeight: 800, marginBottom: 16 }}>
          Appointment: Tom Siegel (Former Google Trust & Safety Chief)
        </div>
        <p style={{ color: "#94a3b8", fontSize: 14, lineHeight: 1.45, margin: "0 0 24px 0" }}>
          Established by Common Sense Media to formulate binding, objective benchmarks evaluating generative AI models before release into classrooms and domestic youth software ecosystems.
        </p>

        {/* Audit Status Card */}
        <div style={{ backgroundColor: "rgba(10, 18, 35, 0.8)", padding: "16px 20px", borderRadius: 10, border: "1px solid rgba(99, 102, 241, 0.25)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
            <span style={{ color: "#f8fafc", fontSize: 13, fontWeight: 800 }}>INDEPENDENT AUDIT BENCHMARK RIGOR</span>
            <span style={{ color: "#818cf8", fontSize: 14, fontWeight: 900 }}>{Math.floor(auditProgress)}%</span>
          </div>
          <div style={{ width: "100%", height: 8, backgroundColor: "rgba(255,255,255,0.1)", borderRadius: 4, overflow: "hidden" }}>
            <div style={{ width: `${auditProgress}%`, height: "100%", backgroundColor: "#818cf8", borderRadius: 4 }} />
          </div>
        </div>
      </div>

      {/* RIGHT: 4 INDEPENDENT SAFETY AUDIT PILLARS */}
      <div style={{ width: 950, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        {safetyPillars.map((p, i) => (
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
                <span style={{ color: "#38bdf8", fontSize: 11, fontWeight: 900, letterSpacing: 1.5 }}>
                  PILLAR 0{i + 1}
                </span>
                <span style={{ backgroundColor: "rgba(16, 185, 129, 0.2)", color: "#10b981", padding: "2px 8px", borderRadius: 4, fontSize: 10, fontWeight: 800 }}>
                  {p.status}
                </span>
              </div>
              <div style={{ color: "#ffffff", fontSize: 18, fontWeight: 800, marginBottom: 8 }}>
                {p.name}
              </div>
              <div style={{ color: "#94a3b8", fontSize: 12, lineHeight: 1.4 }}>
                {p.desc}
              </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", borderTop: "1px solid rgba(255,255,255,0.08)", paddingTop: 10, marginTop: 14 }}>
              <span style={{ color: "#64748b", fontSize: 11, fontWeight: 700 }}>COMPLIANCE THRESHOLD</span>
              <span style={{ color: "#f8fafc", fontSize: 15, fontWeight: 900 }}>{p.score}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
