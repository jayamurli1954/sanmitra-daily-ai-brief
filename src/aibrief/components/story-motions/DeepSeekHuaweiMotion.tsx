import React from "react";
import { useCurrentFrame } from "remotion";

export const DeepSeekHuaweiMotion: React.FC = () => {
  const frame = useCurrentFrame();

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
      {/* Red/Purple Energy Glow */}
      <div
        style={{
          position: "absolute",
          top: "20%",
          left: "20%",
          width: 700,
          height: 700,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(239, 68, 68, 0.2) 0%, transparent 70%)",
          filter: "blur(80px)",
          pointerEvents: "none",
        }}
      />

      {/* LEFT: DEEPSEEK TRAINING CLUSTER GRAPHIC */}
      <div
        style={{
          width: 800,
          backgroundColor: "rgba(20, 10, 15, 0.85)",
          border: "2px solid #ef4444",
          borderRadius: 16,
          padding: "26px 32px",
          boxShadow: "0 16px 40px rgba(0,0,0,0.8), 0 0 24px rgba(239, 68, 68, 0.2)",
          backdropFilter: "blur(12px)",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ backgroundColor: "#ef4444", color: "#ffffff", padding: "4px 14px", borderRadius: 4, fontSize: 13, fontWeight: 900 }}>
              SILICON STACK
            </div>
            <span style={{ color: "#ffffff", fontSize: 20, fontWeight: 800 }}>DEEPSEEK TRAINING INFRASTRUCTURE</span>
          </div>
          <span style={{ color: "#ef4444", fontSize: 13, fontWeight: 800 }}>HUAWEI ASCEND 910</span>
        </div>

        {/* Dynamic Chip Matrix */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 20 }}>
          {Array.from({ length: 8 }).map((_, i) => {
            const isFlashing = (Math.floor(frame / 6) + i) % 4 === 0;
            return (
              <div
                key={i}
                style={{
                  backgroundColor: isFlashing ? "rgba(239, 68, 68, 0.3)" : "rgba(35, 15, 25, 0.9)",
                  border: `1px solid ${isFlashing ? "#ef4444" : "rgba(239, 68, 68, 0.3)"}`,
                  borderRadius: 8,
                  padding: "12px",
                  textAlign: "center",
                  boxShadow: isFlashing ? "0 0 12px #ef4444" : "none",
                }}
              >
                <div style={{ color: "#94a3b8", fontSize: 10, fontWeight: 700 }}>DIE #{i + 1}</div>
                <div style={{ color: "#ffffff", fontSize: 13, fontWeight: 900, margin: "4px 0" }}>ASCEND 910</div>
                <div style={{ color: isFlashing ? "#ef4444" : "#10b981", fontSize: 10, fontWeight: 800 }}>
                  {isFlashing ? "TRAINING" : "LOCKED"}
                </div>
              </div>
            );
          })}
        </div>

        <div style={{ borderTop: "1px solid rgba(239, 68, 68, 0.2)", paddingTop: 14, display: "flex", justifyContent: "space-between" }}>
          <div>
            <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 700 }}>COMPUTE INTERCONNECT</div>
            <div style={{ color: "#ffffff", fontSize: 15, fontWeight: 800 }}>Native CANN Stack Architecture</div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 700 }}>SOVEREIGN SUPPLY CHAIN</div>
            <div style={{ color: "#ef4444", fontSize: 15, fontWeight: 800 }}>Non-Nvidia Independent</div>
          </div>
        </div>
      </div>

      {/* RIGHT: STRATEGIC SHIFT CALLOUT */}
      <div style={{ width: 700, display: "flex", flexDirection: "column", gap: 16 }}>
        <div
          style={{
            backgroundColor: "rgba(15, 23, 42, 0.9)",
            border: "1px solid rgba(255,255,255,0.15)",
            borderRadius: 14,
            padding: "24px 28px",
          }}
        >
          <div style={{ color: "#f59e0b", fontSize: 12, fontWeight: 800, letterSpacing: 1.5, marginBottom: 6 }}>
            SEMICONDUCTOR SOVEREIGNTY
          </div>
          <div style={{ color: "#ffffff", fontSize: 22, fontWeight: 900, marginBottom: 8 }}>
            Overcoming US Export Controls
          </div>
          <p style={{ color: "#94a3b8", fontSize: 14, lineHeight: 1.5, margin: 0 }}>
            DeepSeek's decision to scale next-gen models on domestic Huawei clusters validates China's capability to train cutting-edge LLMs without American GPUs.
          </p>
        </div>

        <div
          style={{
            backgroundColor: "rgba(15, 23, 42, 0.9)",
            border: "2px solid #ef4444",
            borderRadius: 14,
            padding: "24px 28px",
          }}
        >
          <div style={{ color: "#ef4444", fontSize: 12, fontWeight: 800, letterSpacing: 1.5, marginBottom: 6 }}>
            INDUSTRY MILESTONE
          </div>
          <div style={{ color: "#ffffff", fontSize: 22, fontWeight: 900, marginBottom: 8 }}>
            Hardware-Software Co-Design
          </div>
          <p style={{ color: "#94a3b8", fontSize: 14, lineHeight: 1.5, margin: 0 }}>
            Demonstrates algorithmic optimization to extract peak performance from domestic semiconductor architectures.
          </p>
        </div>
      </div>
    </div>
  );
};
