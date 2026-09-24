import React from "react";
import { useCurrentFrame } from "remotion";

export const AccountingFactoryFlow: React.FC = () => {
  const frame = useCurrentFrame();

  const stages = [
    { label: "Tax Invoice", type: "PDF / Scan", color: "#38bdf8", icon: "📄" },
    { label: "Voucher", type: "Normalized", color: "#818cf8", icon: "📑" },
    { label: "Journal Entry", type: "Double-Entry", color: "#a855f7", icon: "⚖️" },
    { label: "General Ledger", type: "Multi-Account", color: "#ec4899", icon: "📚" },
    { label: "Trial Balance", type: "Reconciled", color: "#10b981", icon: "📊" },
    { label: "Working Papers", type: "Audit Ready", color: "#06b6d4", icon: "🛡️" },
  ];

  // Active pulsing position across conveyor
  const activeIndex = Math.floor((frame / 12) % stages.length);

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 12,
        width: "100%",
        maxWidth: 1160,
        position: "relative",
      }}
    >
      {stages.map((st, i) => {
        const isCurrent = i === activeIndex;
        const hasPassed = i < activeIndex;

        const scale = isCurrent ? 1.06 : 1.0;
        const borderGlow = isCurrent
          ? `0 0 25px ${st.color}`
          : hasPassed
          ? "0 0 10px rgba(16, 185, 129, 0.2)"
          : "none";

        return (
          <React.Fragment key={st.label}>
            {/* Stage Box */}
            <div
              style={{
                flex: 1,
                minWidth: 155,
                backgroundColor: isCurrent ? "rgba(30, 41, 59, 0.9)" : "rgba(15, 23, 42, 0.75)",
                border: isCurrent
                  ? `2px solid ${st.color}`
                  : hasPassed
                  ? "1px solid rgba(16, 185, 129, 0.4)"
                  : "1px solid rgba(148, 163, 184, 0.2)",
                borderRadius: 14,
                padding: "16px 12px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                textAlign: "center",
                gap: 6,
                transform: `scale(${scale})`,
                boxShadow: borderGlow,
                backdropFilter: "blur(12px)",
                transition: "transform 0.2s ease",
              }}
            >
              <span style={{ fontSize: 24 }}>{st.icon}</span>
              <span
                style={{
                  fontSize: 14,
                  fontWeight: 700,
                  fontFamily: "Inter, sans-serif",
                  color: isCurrent ? "#ffffff" : "#cbd5e1",
                  letterSpacing: "-0.01em",
                }}
              >
                {st.label}
              </span>
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 600,
                  fontFamily: "JetBrains Mono, monospace",
                  color: isCurrent ? st.color : hasPassed ? "#34d399" : "#64748b",
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                }}
              >
                {hasPassed ? "COMPLETED ✓" : st.type}
              </span>
            </div>

            {/* Connecting Flow Arrow */}
            {i < stages.length - 1 && (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: i <= activeIndex ? "#38bdf8" : "#475569",
                  fontSize: 18,
                  fontWeight: 700,
                  transform: `translateX(${Math.sin((frame + i * 8) / 6) * 3}px)`,
                }}
              >
                ➔
              </div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
