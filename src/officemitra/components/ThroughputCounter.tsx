import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export const ThroughputCounter: React.FC = () => {
  const frame = useCurrentFrame();

  const tiers = [
    {
      inVal: "1 Document",
      outVal: "1 Journal Voucher",
      time: "0.02 sec",
      activeAt: [0, 40],
    },
    {
      inVal: "100 Documents",
      outVal: "600 Journal Entries",
      time: "1.4 sec",
      activeAt: [40, 80],
    },
    {
      inVal: "10,000 Documents",
      outVal: "Fully Prepared Books & TB",
      time: "48 sec",
      activeAt: [80, 180],
    },
  ];

  return (
    <div
      style={{
        display: "flex",
        gap: 16,
        width: "100%",
        maxWidth: 960,
        justifyContent: "center",
      }}
    >
      {tiers.map((t, idx) => {
        const isCurrent = frame >= t.activeAt[0];
        const opacity = interpolate(frame, [t.activeAt[0], t.activeAt[0] + 12], [0.3, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

        return (
          <div
            key={t.inVal}
            style={{
              flex: 1,
              opacity,
              backgroundColor: isCurrent ? "rgba(15, 23, 42, 0.85)" : "rgba(15, 23, 42, 0.4)",
              border: isCurrent
                ? idx === 2
                  ? "2px solid #38bdf8"
                  : "1px solid rgba(56, 189, 248, 0.4)"
                : "1px solid rgba(148, 163, 184, 0.15)",
              borderRadius: 14,
              padding: "16px 20px",
              display: "flex",
              flexDirection: "column",
              gap: 8,
              boxShadow: isCurrent && idx === 2 ? "0 0 30px rgba(56, 189, 248, 0.25)" : "none",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 13, color: "#94a3b8", fontFamily: "Inter, sans-serif" }}>
                Intake Volume
              </span>
              <span
                style={{
                  fontSize: 11,
                  color: "#34d399",
                  fontFamily: "JetBrains Mono, monospace",
                  backgroundColor: "rgba(16, 185, 129, 0.15)",
                  padding: "2px 8px",
                  borderRadius: 6,
                }}
              >
                {t.time}
              </span>
            </div>

            <div style={{ fontSize: 16, fontWeight: 700, color: "#f8fafc", fontFamily: "Inter, sans-serif" }}>
              {t.inVal}
            </div>

            <div style={{ color: "#38bdf8", fontSize: 14, fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
              <span>➔</span>
              <span style={{ fontFamily: "JetBrains Mono, monospace" }}>{t.outVal}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
