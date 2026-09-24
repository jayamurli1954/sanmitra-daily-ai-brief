import React from "react";
import { useCurrentFrame } from "remotion";

export const OpenAIStandardsMotion: React.FC = () => {
  const frame = useCurrentFrame();

  const scanOffset = (frame * 3) % 400;

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
        justifyContent: "center",
      }}
    >
      {/* Background Radial Glow */}
      <div
        style={{
          position: "absolute",
          width: 800,
          height: 800,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(16, 185, 129, 0.18) 0%, transparent 70%)",
          filter: "blur(80px)",
          pointerEvents: "none",
        }}
      />

      <div style={{ width: 1600, display: "flex", gap: 36, zIndex: 10 }}>
        {/* LEFT: OPENAI BENCHMARK HUD */}
        <div
          style={{
            flex: 1,
            backgroundColor: "rgba(10, 20, 30, 0.85)",
            border: "2px solid #10b981",
            borderRadius: 16,
            padding: "28px 32px",
            boxShadow: "0 16px 40px rgba(0,0,0,0.7), 0 0 20px rgba(16, 185, 129, 0.15)",
            backdropFilter: "blur(12px)",
            position: "relative",
            overflow: "hidden",
          }}
        >
          {/* Scanning Line */}
          <div
            style={{
              position: "absolute",
              top: scanOffset,
              left: 0,
              right: 0,
              height: 2,
              backgroundColor: "#10b981",
              boxShadow: "0 0 10px #10b981",
            }}
          />

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <div>
              <div style={{ color: "#10b981", fontSize: 13, fontWeight: 900, letterSpacing: 2 }}>
                PROPOSAL: TECHNICAL BLUEPRINT
              </div>
              <div style={{ color: "#ffffff", fontSize: 26, fontWeight: 900 }}>
                GLOBAL AI EVALUATION STANDARDS
              </div>
            </div>
            <div
              style={{
                backgroundColor: "rgba(16, 185, 129, 0.2)",
                border: "1px solid #10b981",
                color: "#10b981",
                padding: "6px 14px",
                borderRadius: 20,
                fontSize: 12,
                fontWeight: 800,
              }}
            >
              US LEADERSHIP MANDATE
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
            {[
              { label: "FRONTIER MODEL CAPABILITY BENCHMARKS", val: 88, color: "#10b981" },
              { label: "CATASTROPHIC RISK THRESHOLDS", val: 94, color: "#38bdf8" },
              { label: "PRE-DEPLOYMENT TESTING PROTOCOLS", val: 82, color: "#f59e0b" },
              { label: "INTERNATIONAL HARMONIZATION ALIGNMENT", val: 76, color: "#a855f7" },
            ].map((metric, i) => {
              const currentVal = Math.min(metric.val, (frame * 2) + 20);
              return (
                <div key={i}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <span style={{ color: "#e2e8f0", fontSize: 13, fontWeight: 700 }}>{metric.label}</span>
                    <span style={{ color: metric.color, fontSize: 13, fontWeight: 800, fontFamily: "monospace" }}>
                      {currentVal}% SPECIFIED
                    </span>
                  </div>
                  <div style={{ width: "100%", height: 8, backgroundColor: "rgba(255,255,255,0.08)", borderRadius: 4, overflow: "hidden" }}>
                    <div
                      style={{
                        width: `${currentVal}%`,
                        height: "100%",
                        backgroundColor: metric.color,
                        boxShadow: `0 0 8px ${metric.color}`,
                        borderRadius: 4,
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* RIGHT: REGULATORY COMPARISON CARDS */}
        <div style={{ width: 560, display: "flex", flexDirection: "column", gap: 16 }}>
          <div
            style={{
              backgroundColor: "rgba(15, 23, 42, 0.85)",
              border: "1px solid rgba(255, 255, 255, 0.15)",
              borderRadius: 14,
              padding: "22px 26px",
              boxShadow: "0 10px 30px rgba(0,0,0,0.6)",
            }}
          >
            <div style={{ color: "#ef4444", fontSize: 12, fontWeight: 800, letterSpacing: 1.5, marginBottom: 4 }}>
              CURRENT RISK: REGULATORY FRAGMENTATION
            </div>
            <div style={{ color: "#ffffff", fontSize: 18, fontWeight: 800, marginBottom: 8 }}>
              Balkanized National Rules
            </div>
            <p style={{ color: "#94a3b8", fontSize: 13, lineHeight: 1.5, margin: 0 }}>
              Conflicting tests across US, EU, and Asia risk slowing innovation while failing to catch systemic frontier risks.
            </p>
          </div>

          <div
            style={{
              backgroundColor: "rgba(15, 23, 42, 0.85)",
              border: "2px solid #10b981",
              borderRadius: 14,
              padding: "22px 26px",
              boxShadow: "0 10px 30px rgba(16, 185, 129, 0.15)",
            }}
          >
            <div style={{ color: "#10b981", fontSize: 12, fontWeight: 800, letterSpacing: 1.5, marginBottom: 4 }}>
              OPENAI PROPOSAL: HARMONIZED TESTING
            </div>
            <div style={{ color: "#ffffff", fontSize: 18, fontWeight: 800, marginBottom: 8 }}>
              Uniform Global Verification
            </div>
            <p style={{ color: "#94a3b8", fontSize: 13, lineHeight: 1.5, margin: 0 }}>
              Single technical evaluation standard adopted by key democracies to establish baseline frontier AI safety guarantees.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
