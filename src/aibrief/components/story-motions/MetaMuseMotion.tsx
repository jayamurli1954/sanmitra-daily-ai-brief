import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";

export const MetaMuseMotion: React.FC = () => {
  const frame = useCurrentFrame();

  // Act 1: 0-330 (0-11s), Act 2: 330-720 (11-24s), Act 3: 720+ (24-35s)
  const isAct2 = frame >= 330 && frame < 720;
  const isAct3 = frame >= 720;

  // Slow continuous camera zoom
  const bgScale = interpolate(frame, [0, 1100], [1.0, 1.15], { extrapolateRight: "clamp" });
  const bgPanY = interpolate(frame, [0, 1100], [0, -40], { extrapolateRight: "clamp" });

  // Blinking alert
  const alertBlink = Math.floor(frame / 12) % 2 === 0;

  return (
    <div
      style={{
        position: "absolute",
        top: 72,
        left: 0,
        width: 1920,
        height: 720,
        overflow: "hidden",
      }}
    >
      {/* Background Graphic with Dynamic Motion */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `scale(${bgScale}) translateY(${bgPanY}px)`,
          filter: isAct2 || isAct3 ? "brightness(0.55) contrast(1.1)" : "brightness(0.9)",
          transition: "filter 0.5s ease",
        }}
      >
        <Img
          src={staticFile("aibrief/backgrounds/ai_security.jpg")}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </div>

      {/* Cyber Grid Overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(to top, rgba(3, 7, 18, 0.95) 0%, rgba(3, 7, 18, 0.2) 60%, rgba(3, 7, 18, 0.8) 100%)",
        }}
      />

      {/* ACT 1: LIVE CYBER BREACH HUD OVERLAY */}
      {!isAct2 && !isAct3 && (
        <div
          style={{
            position: "absolute",
            top: 40,
            left: 80,
            right: 340,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            zIndex: 15,
          }}
        >
          <div
            style={{
              backgroundColor: "rgba(15, 23, 42, 0.85)",
              border: "2px solid #ef4444",
              borderRadius: 12,
              padding: "16px 24px",
              boxShadow: "0 8px 30px rgba(220, 38, 38, 0.4)",
              backdropFilter: "blur(12px)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
              <div
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: "50%",
                  backgroundColor: alertBlink ? "#ef4444" : "#7f1d1d",
                  boxShadow: alertBlink ? "0 0 10px #ef4444" : "none",
                }}
              />
              <span style={{ color: "#ef4444", fontSize: 13, fontWeight: 900, letterSpacing: 2 }}>
                CRITICAL SYSTEM ALERT
              </span>
            </div>
            <div style={{ color: "#ffffff", fontSize: 22, fontWeight: 900 }}>
              META MUSE 0-DAY PRIVILEGE ESCALATION
            </div>
            <div style={{ color: "#94a3b8", fontSize: 13, fontWeight: 600 }}>
              DISCOVERED BY: PATRICK WARDLE (OBJECTIVE-SEE)
            </div>
          </div>

          <div
            style={{
              backgroundColor: "rgba(15, 23, 42, 0.85)",
              border: "1px solid rgba(56, 189, 248, 0.4)",
              borderRadius: 12,
              padding: "14px 20px",
              display: "flex",
              flexDirection: "column",
              gap: 4,
              fontFamily: "monospace",
              backdropFilter: "blur(12px)",
            }}
          >
            <div style={{ color: "#38bdf8", fontSize: 11, fontWeight: 700 }}>EXPLOIT VECTOR: LOCAL XPC RPC</div>
            <div style={{ color: "#f8fafc", fontSize: 13 }}>AUTH TOKEN LEAK: <span style={{ color: "#ef4444" }}>VULNERABLE</span></div>
            <div style={{ color: "#94a3b8", fontSize: 11 }}>OS PERMISSION: FULL TCC BYPASS</div>
          </div>
        </div>
      )}

      {/* ACT 2: ANIMATED EXPLOIT REVEAL TERMINAL (Wardle Research) */}
      {isAct2 && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: 900,
            backgroundColor: "rgba(6, 11, 23, 0.95)",
            border: "2px solid #ef4444",
            borderRadius: 16,
            padding: "24px 32px",
            boxShadow: "0 20px 60px rgba(0, 0, 0, 0.9), 0 0 30px rgba(239, 68, 68, 0.3)",
            zIndex: 20,
            backdropFilter: "blur(16px)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid rgba(239, 68, 68, 0.3)", paddingBottom: 12, marginBottom: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ color: "#ef4444", fontSize: 18 }}>⚠️</span>
              <span style={{ color: "#ffffff", fontSize: 18, fontWeight: 900, letterSpacing: 1 }}>
                SECURITY RESEARCH DISPATCH • PATRICK WARDLE
              </span>
            </div>
            <div style={{ backgroundColor: "#ef4444", color: "#ffffff", fontSize: 11, fontWeight: 900, padding: "3px 10px", borderRadius: 4 }}>
              EXPLOIT VERIFIED
            </div>
          </div>

          <div style={{ fontFamily: "monospace", color: "#e2e8f0", fontSize: 14, lineHeight: 1.6, marginBottom: 16 }}>
            <div><span style={{ color: "#38bdf8" }}>[CVE-2026-0922]</span> Target: com.meta.muse.daemon</div>
            <div><span style={{ color: "#f59e0b" }}>[MEM_DUMP]</span> 0x7FFF9A20: 4D 75 73 65 5F 54 6F 6B 65 6E 5F 41 75 74 68</div>
            <div><span style={{ color: "#ef4444" }}>[CRITICAL]</span> Unprivileged local application extracted authorization session token</div>
            <div><span style={{ color: "#10b981" }}>[IMPACT]</span> Full root/admin level operating system automation hijacked</div>
          </div>

          {/* Animated Memory Progress Bar */}
          <div style={{ width: "100%", height: 6, backgroundColor: "rgba(255,255,255,0.1)", borderRadius: 3, overflow: "hidden" }}>
            <div style={{ width: `${((frame * 2) % 100)}%`, height: "100%", backgroundColor: "#ef4444", boxShadow: "0 0 8px #ef4444" }} />
          </div>
        </div>
      )}

      {/* ACT 3: AMAZON BLOCKS MUSE ACCESS BARRIER */}
      {isAct3 && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: 860,
            backgroundColor: "rgba(20, 10, 15, 0.95)",
            border: "2px solid #dc2626",
            borderRadius: 16,
            padding: "28px 36px",
            boxShadow: "0 20px 60px rgba(0, 0, 0, 0.9), 0 0 40px rgba(220, 38, 38, 0.4)",
            zIndex: 20,
            textAlign: "center",
            backdropFilter: "blur(16px)",
          }}
        >
          <div
            style={{
              display: "inline-block",
              backgroundColor: "#dc2626",
              color: "#ffffff",
              padding: "6px 20px",
              fontSize: 14,
              fontWeight: 900,
              letterSpacing: 2,
              borderRadius: 6,
              marginBottom: 16,
              boxShadow: "0 0 20px rgba(220, 38, 38, 0.6)",
            }}
          >
            AMAZON.COM PLATFORM ENFORCEMENT
          </div>

          <h2 style={{ color: "#ffffff", fontSize: 32, fontWeight: 900, margin: "0 0 12px 0" }}>
            MUSE AGENT FORMALLY BLOCKED
          </h2>

          <p style={{ color: "#fca5a5", fontSize: 18, fontWeight: 600, lineHeight: 1.5, margin: "0 0 20px 0" }}>
            Amazon cites unauthorized web interaction and potential capture of customer shopping credentials.
          </p>

          <div style={{ display: "flex", justifyContent: "center", gap: 24, borderTop: "1px solid rgba(220, 38, 38, 0.3)", paddingTop: 16 }}>
            <div style={{ color: "#e2e8f0", fontSize: 13, fontWeight: 700 }}>STATUS: <span style={{ color: "#ef4444" }}>TRAFFIC REJECTED</span></div>
            <div style={{ color: "#e2e8f0", fontSize: 13, fontWeight: 700 }}>CREDENTIAL POLICY: <span style={{ color: "#ef4444" }}>ZERO TRUST</span></div>
          </div>
        </div>
      )}
    </div>
  );
};
