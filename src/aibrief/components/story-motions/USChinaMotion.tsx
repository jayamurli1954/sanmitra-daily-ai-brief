import React from "react";
import { useCurrentFrame } from "remotion";

export const USChinaMotion: React.FC = () => {
  const frame = useCurrentFrame();

  // Oscillating waveform bars
  const waveBars = [0.4, 0.8, 0.6, 1.0, 0.7, 0.9, 0.5, 0.8, 0.3, 0.9, 0.7, 0.5];

  // Camera slow pan & drift
  const panY = Math.sin(frame * 0.03) * 6;
  const gridOffset = (frame * 0.8) % 50;

  // Blinking emergency status
  const isBlink = Math.floor(frame / 15) % 2 === 0;

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
        transform: `translateY(${panY}px)`,
      }}
    >
      {/* Background Cyber Grid with Forward Motion */}
      <svg
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          opacity: 0.18,
          transform: `translate(${gridOffset}px, ${gridOffset}px)`,
        }}
      >
        <defs>
          <pattern id="usChinaGrid" width="50" height="50" patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#38bdf8" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="2100" height="900" fill="url(#usChinaGrid)" />
      </svg>

      {/* Glow Orbs behind USA (Blue) and China (Red) */}
      <div
        style={{
          position: "absolute",
          left: "15%",
          top: "30%",
          width: 500,
          height: 500,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(2, 132, 199, 0.25) 0%, transparent 70%)",
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          right: "15%",
          top: "30%",
          width: 500,
          height: 500,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(220, 38, 38, 0.25) 0%, transparent 70%)",
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />

      {/* Main Motion Graphic Layout */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          width: 1720,
          zIndex: 10,
        }}
      >
        {/* LEFT CARD: USA DELEGATION */}
        <div
          style={{
            width: 540,
            height: 380,
            backgroundColor: "rgba(10, 20, 40, 0.85)",
            border: "2px solid #38bdf8",
            borderRadius: 16,
            padding: "24px 28px",
            boxShadow: "0 16px 40px rgba(0, 0, 0, 0.7), inset 0 0 20px rgba(56, 189, 248, 0.15)",
            backdropFilter: "blur(12px)",
            position: "relative",
            overflow: "hidden",
          }}
        >
          {/* Top Scanline Bar */}
          <div
            style={{
              position: "absolute",
              top: (frame * 3) % 380,
              left: 0,
              right: 0,
              height: 2,
              backgroundColor: "rgba(56, 189, 248, 0.6)",
              boxShadow: "0 0 8px #38bdf8",
            }}
          />

          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div
                style={{
                  backgroundColor: "#1d4ed8",
                  color: "#ffffff",
                  padding: "6px 16px",
                  borderRadius: 6,
                  fontSize: 18,
                  fontWeight: 900,
                  letterSpacing: 2,
                }}
              >
                USA
              </div>
              <span style={{ color: "#f8fafc", fontSize: 22, fontWeight: 800 }}>WASHINGTON D.C.</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: "#38bdf8", boxShadow: "0 0 10px #38bdf8" }} />
              <span style={{ color: "#38bdf8", fontSize: 13, fontWeight: 800 }}>CHANNEL ONLINE</span>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 20, marginTop: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <span style={{ color: "#38bdf8", fontSize: 20 }}>▶</span>
              <span style={{ color: "#ffffff", fontSize: 20, fontWeight: 700 }}>Formal Bilateral Dialogue</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <span style={{ color: "#38bdf8", fontSize: 20 }}>▶</span>
              <span style={{ color: "#ffffff", fontSize: 20, fontWeight: 700 }}>Emergency Incident Protocol</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <span style={{ color: "#38bdf8", fontSize: 20 }}>▶</span>
              <span style={{ color: "#ffffff", fontSize: 20, fontWeight: 700 }}>Frontier Model Risk Framework</span>
            </div>
          </div>

          {/* Bottom Telemetry Gauge */}
          <div style={{ position: "absolute", bottom: 24, left: 28, right: 28 }}>
            <div style={{ display: "flex", justifyContent: "space-between", color: "#94a3b8", fontSize: 12, fontWeight: 800, marginBottom: 6 }}>
              <span>DIPLOMATIC BANDWIDTH</span>
              <span style={{ color: "#38bdf8" }}>ACTIVE ENCRYPTION</span>
            </div>
            <div style={{ width: "100%", height: 8, backgroundColor: "rgba(255,255,255,0.1)", borderRadius: 4, overflow: "hidden" }}>
              <div style={{ width: "88%", height: "100%", backgroundColor: "#38bdf8", borderRadius: 4, boxShadow: "0 0 8px #38bdf8" }} />
            </div>
          </div>
        </div>

        {/* CENTER INTERACTIVE BRIDGE & HOTLINE NODE */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            width: 440,
            position: "relative",
          }}
        >
          {/* Laser Bridge Lines */}
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: -80,
              right: -80,
              height: 4,
              background: "linear-gradient(90deg, #38bdf8 0%, #f59e0b 50%, #ef4444 100%)",
              boxShadow: "0 0 12px rgba(245, 158, 11, 0.8)",
              zIndex: 1,
            }}
          />

          {/* Moving Data Packet across bridge */}
          <div
            style={{
              position: "absolute",
              top: "calc(50% - 7px)",
              left: `${(frame * 1.5) % 110 - 5}%`,
              width: 18,
              height: 18,
              borderRadius: "50%",
              backgroundColor: "#ffffff",
              boxShadow: "0 0 16px #ffffff, 0 0 30px #f59e0b",
              zIndex: 2,
            }}
          />

          {/* Central Holographic Hub */}
          <div
            style={{
              width: 340,
              backgroundColor: "rgba(15, 23, 42, 0.95)",
              border: "2px solid #f59e0b",
              borderRadius: 20,
              padding: "24px 28px",
              boxShadow: "0 16px 40px rgba(0, 0, 0, 0.8), 0 0 30px rgba(245, 158, 11, 0.3)",
              zIndex: 5,
              textAlign: "center",
              backdropFilter: "blur(16px)",
            }}
          >
            <div
              style={{
                backgroundColor: isBlink ? "#dc2626" : "rgba(220, 38, 38, 0.4)",
                color: "#ffffff",
                fontSize: 12,
                fontWeight: 900,
                letterSpacing: 2,
                padding: "4px 12px",
                borderRadius: 12,
                display: "inline-block",
                marginBottom: 10,
              }}
            >
              ACTIVE HOTLINE
            </div>

            <div style={{ color: "#ffffff", fontSize: 22, fontWeight: 900, letterSpacing: 0.5, marginBottom: 6 }}>
              AI INCIDENT CHANNEL
            </div>
            <div style={{ color: "#f59e0b", fontSize: 13, fontWeight: 800, letterSpacing: 1.5, marginBottom: 16 }}>
              BILATERAL DE-ESCALATION PACT
            </div>

            {/* Live Audio / Signal Waveform */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6, height: 40, marginBottom: 16 }}>
              {waveBars.map((val, i) => {
                const dynamicHeight = Math.max(10, Math.sin(frame * 0.2 + i) * 16 + val * 24);
                return (
                  <div
                    key={i}
                    style={{
                      width: 6,
                      height: dynamicHeight,
                      backgroundColor: i < 6 ? "#38bdf8" : "#ef4444",
                      borderRadius: 3,
                      boxShadow: `0 0 8px ${i < 6 ? "#38bdf8" : "#ef4444"}`,
                    }}
                  />
                );
              })}
            </div>

            <div style={{ borderTop: "1px solid rgba(255, 255, 255, 0.1)", paddingTop: 10, color: "#94a3b8", fontSize: 12, fontWeight: 700 }}>
              ESTABLISHED: GENEVA TALKS • 2026
            </div>
          </div>
        </div>

        {/* RIGHT CARD: CHINA DELEGATION */}
        <div
          style={{
            width: 540,
            height: 380,
            backgroundColor: "rgba(35, 15, 20, 0.85)",
            border: "2px solid #ef4444",
            borderRadius: 16,
            padding: "24px 28px",
            boxShadow: "0 16px 40px rgba(0, 0, 0, 0.7), inset 0 0 20px rgba(239, 68, 68, 0.15)",
            backdropFilter: "blur(12px)",
            position: "relative",
            overflow: "hidden",
          }}
        >
          {/* Top Scanline Bar */}
          <div
            style={{
              position: "absolute",
              top: (frame * 3 + 120) % 380,
              left: 0,
              right: 0,
              height: 2,
              backgroundColor: "rgba(239, 68, 68, 0.6)",
              boxShadow: "0 0 8px #ef4444",
            }}
          />

          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div
                style={{
                  backgroundColor: "#b91c1c",
                  color: "#ffffff",
                  padding: "6px 16px",
                  borderRadius: 6,
                  fontSize: 18,
                  fontWeight: 900,
                  letterSpacing: 2,
                }}
              >
                PRC
              </div>
              <span style={{ color: "#f8fafc", fontSize: 22, fontWeight: 800 }}>BEIJING / SHENZHEN</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: "#ef4444", boxShadow: "0 0 10px #ef4444" }} />
              <span style={{ color: "#ef4444", fontSize: 13, fontWeight: 800 }}>SUMMIT CONFIRMED</span>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 20, marginTop: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <span style={{ color: "#ef4444", fontSize: 20 }}>▶</span>
              <span style={{ color: "#ffffff", fontSize: 20, fontWeight: 700 }}>Shenzhen Summit in 60 Days</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <span style={{ color: "#ef4444", fontSize: 20 }}>▶</span>
              <span style={{ color: "#ffffff", fontSize: 20, fontWeight: 700 }}>Cross-Border Risk Auditing</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <span style={{ color: "#ef4444", fontSize: 20 }}>▶</span>
              <span style={{ color: "#ffffff", fontSize: 20, fontWeight: 700 }}>Cooperation Despite Chip Curbs</span>
            </div>
          </div>

          {/* Bottom Telemetry Gauge */}
          <div style={{ position: "absolute", bottom: 24, left: 28, right: 28 }}>
            <div style={{ display: "flex", justifyContent: "space-between", color: "#94a3b8", fontSize: 12, fontWeight: 800, marginBottom: 6 }}>
              <span>COUNTDOWN TO SHENZHEN</span>
              <span style={{ color: "#ef4444" }}>T-MINUS 60 DAYS</span>
            </div>
            <div style={{ width: "100%", height: 8, backgroundColor: "rgba(255,255,255,0.1)", borderRadius: 4, overflow: "hidden" }}>
              <div style={{ width: "70%", height: "100%", backgroundColor: "#ef4444", borderRadius: 4, boxShadow: "0 0 8px #ef4444" }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
