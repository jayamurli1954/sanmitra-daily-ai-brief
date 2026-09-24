import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

interface DeadlineCountdownProps {
  resolved?: boolean;
}

export const DeadlineCountdown: React.FC<DeadlineCountdownProps> = ({ resolved = false }) => {
  const frame = useCurrentFrame();

  const pulse = Math.sin(frame / 6) * 0.2 + 0.8;

  const deadlines = [
    { title: "GSTR-3B Filing", days: "02h 14m", penalty: "Late Fee Risk", urgent: true },
    { title: "TDS Challan 281", days: "14h 32m", penalty: "Interest Accrual", urgent: true },
    { title: "Tax Audit (Sec 44AB)", days: "3 Days", penalty: "Sec 271B Penalty", urgent: true },
    { title: "ROC AOC-4 / MGT-7", days: "5 Days", penalty: "Daily ₹100 Fine", urgent: false },
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(4, 1fr)",
        gap: 16,
        width: "100%",
        maxWidth: 1080,
      }}
    >
      {deadlines.map((d, i) => {
        const stagger = i * 4;
        const opacity = interpolate(frame, [stagger, stagger + 12], [0, 1], {
          extrapolateRight: "clamp",
        });

        return (
          <div
            key={d.title}
            style={{
              opacity,
              backgroundColor: resolved ? "rgba(6, 78, 59, 0.4)" : "rgba(30, 41, 59, 0.7)",
              border: resolved
                ? "1px solid rgba(16, 185, 129, 0.5)"
                : d.urgent
                ? `1px solid rgba(239, 68, 68, ${0.4 + pulse * 0.4})`
                : "1px solid rgba(245, 158, 11, 0.4)",
              borderRadius: 12,
              padding: "16px 18px",
              boxShadow: resolved
                ? "0 0 20px rgba(16, 185, 129, 0.2)"
                : d.urgent
                ? `0 0 ${15 * pulse}px rgba(239, 68, 68, 0.25)`
                : "none",
              display: "flex",
              flexDirection: "column",
              gap: 8,
              backdropFilter: "blur(12px)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span
                style={{
                  fontSize: 13,
                  fontWeight: 600,
                  fontFamily: "Inter, sans-serif",
                  color: "#cbd5e1",
                  letterSpacing: "0.02em",
                }}
              >
                {d.title}
              </span>
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  backgroundColor: resolved ? "#10b981" : d.urgent ? "#ef4444" : "#f59e0b",
                  boxShadow: `0 0 8px ${resolved ? "#10b981" : d.urgent ? "#ef4444" : "#f59e0b"}`,
                }}
              />
            </div>

            <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
              <span
                style={{
                  fontSize: 22,
                  fontWeight: 700,
                  fontFamily: "JetBrains Mono, monospace",
                  color: resolved ? "#34d399" : d.urgent ? "#f87171" : "#fbbf24",
                }}
              >
                {resolved ? "COMPLIED ✓" : d.days}
              </span>
            </div>

            <span
              style={{
                fontSize: 11,
                fontFamily: "Inter, sans-serif",
                color: resolved ? "#6ee7b7" : "#94a3b8",
                fontWeight: 500,
              }}
            >
              {resolved ? "Automated Reconciliation" : d.penalty}
            </span>
          </div>
        );
      })}
    </div>
  );
};
