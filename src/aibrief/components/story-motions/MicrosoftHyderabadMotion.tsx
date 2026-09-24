import React from "react";
import { useCurrentFrame } from "remotion";

export const MicrosoftHyderabadMotion: React.FC = () => {
  const frame = useCurrentFrame();

  const pulseRing = (frame * 3) % 180;

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
      {/* Blue Glow */}
      <div
        style={{
          position: "absolute",
          top: "20%",
          left: "25%",
          width: 700,
          height: 700,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(0, 164, 239, 0.22) 0%, transparent 70%)",
          filter: "blur(80px)",
          pointerEvents: "none",
        }}
      />

      {/* LEFT: HYDERABAD HYPERSCALE HUB RADAR */}
      <div
        style={{
          width: 750,
          backgroundColor: "rgba(10, 20, 35, 0.85)",
          border: "2px solid #00a4ef",
          borderRadius: 16,
          padding: "26px 32px",
          boxShadow: "0 16px 40px rgba(0,0,0,0.8), 0 0 24px rgba(0, 164, 239, 0.2)",
          backdropFilter: "blur(12px)",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ backgroundColor: "#00a4ef", color: "#ffffff", padding: "4px 14px", borderRadius: 4, fontSize: 13, fontWeight: 900 }}>
              AZURE CLOUD
            </div>
            <span style={{ color: "#ffffff", fontSize: 20, fontWeight: 800 }}>INDIA SOUTH CENTRAL REGION</span>
          </div>
          <span style={{ color: "#10b981", fontSize: 13, fontWeight: 800 }}>● REGION LIVE</span>
        </div>

        {/* Radar Map Graphic with Radiating Pulse Rings */}
        <div style={{ height: 180, position: "relative", display: "flex", alignItems: "center", justifyContent: "center", border: "1px solid rgba(0, 164, 239, 0.2)", borderRadius: 12, backgroundColor: "rgba(6, 11, 23, 0.9)", marginBottom: 16 }}>
          {/* Hyderabad Core Ping */}
          <div style={{ width: 16, height: 16, borderRadius: "50%", backgroundColor: "#00a4ef", boxShadow: "0 0 16px #00a4ef", zIndex: 5 }} />
          
          {/* Animated Expanding Rings */}
          <div
            style={{
              position: "absolute",
              width: pulseRing * 2,
              height: pulseRing * 2,
              borderRadius: "50%",
              border: "1.5px solid #00a4ef",
              opacity: 1 - pulseRing / 180,
              pointerEvents: "none",
            }}
          />
          <div
            style={{
              position: "absolute",
              width: ((pulseRing + 60) % 180) * 2,
              height: ((pulseRing + 60) % 180) * 2,
              borderRadius: "50%",
              border: "1.5px solid #38bdf8",
              opacity: 1 - ((pulseRing + 60) % 180) / 180,
              pointerEvents: "none",
            }}
          />

          <div style={{ position: "absolute", bottom: 12, left: 16, color: "#94a3b8", fontSize: 12, fontWeight: 700 }}>
            COORDINATES: 17.3850° N, 78.4867° E (HYDERABAD)
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
          <div>
            <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 700 }}>INFRASTRUCTURE INVESTMENT</div>
            <div style={{ color: "#ffffff", fontSize: 18, fontWeight: 900 }}>Multi-Billion Dollar Capex</div>
          </div>
          <div>
            <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 700 }}>WORKLOAD CAPABILITY</div>
            <div style={{ color: "#00a4ef", fontSize: 18, fontWeight: 900 }}>Hyperscale AI Acceleration</div>
          </div>
        </div>
      </div>

      {/* RIGHT: STRATEGIC IMPACT CARDS */}
      <div style={{ width: 750, display: "flex", flexDirection: "column", gap: 16 }}>
        <div
          style={{
            backgroundColor: "rgba(15, 23, 42, 0.9)",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            borderRadius: 14,
            padding: "24px 28px",
          }}
        >
          <div style={{ color: "#00a4ef", fontSize: 12, fontWeight: 800, letterSpacing: 1.5, marginBottom: 6 }}>
            EXPANDED CAPACITY
          </div>
          <div style={{ color: "#ffffff", fontSize: 22, fontWeight: 900, marginBottom: 8 }}>
            India as Premier Global AI Corridor
          </div>
          <p style={{ color: "#94a3b8", fontSize: 14, lineHeight: 1.5, margin: 0 }}>
            The India South Central region bolsters Microsoft's global network, offering low-latency compute for enterprise AI, sovereign data storage, and startup innovation.
          </p>
        </div>

        <div
          style={{
            backgroundColor: "rgba(15, 23, 42, 0.9)",
            border: "2px solid #10b981",
            borderRadius: 14,
            padding: "24px 28px",
          }}
        >
          <div style={{ color: "#10b981", fontSize: 12, fontWeight: 800, letterSpacing: 1.5, marginBottom: 6 }}>
            ECOSYSTEM GROWTH
          </div>
          <div style={{ color: "#ffffff", fontSize: 22, fontWeight: 900, marginBottom: 8 }}>
            Sovereign & Enterprise AI Adoption
          </div>
          <p style={{ color: "#94a3b8", fontSize: 14, lineHeight: 1.5, margin: 0 }}>
            Empowers Indian financial institutions, public sector entities, and tech giants to train and deploy advanced foundation models locally with regulatory compliance.
          </p>
        </div>
      </div>
    </div>
  );
};
