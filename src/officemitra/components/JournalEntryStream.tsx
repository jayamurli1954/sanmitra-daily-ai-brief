import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const JournalEntryStream: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Reveal stages
  const spring1 = spring({ frame, fps, config: { damping: 14 } });
  const spring2 = spring({ frame: frame - 15, fps, config: { damping: 14 } });
  const spring3 = spring({ frame: frame - 30, fps, config: { damping: 14 } });
  const spring4 = spring({ frame: frame - 45, fps, config: { damping: 14 } });

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        width: "100%",
        maxWidth: 960,
      }}
    >
      {/* Active Voucher Header */}
      <div
        style={{
          width: "100%",
          backgroundColor: "#1e293b",
          borderTopLeftRadius: 14,
          borderTopRightRadius: 14,
          padding: "14px 24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          border: "1px solid rgba(148, 163, 184, 0.2)",
          borderBottom: "none",
        }}
      >
        <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
          <span
            style={{
              backgroundColor: "rgba(56, 189, 248, 0.2)",
              color: "#38bdf8",
              fontFamily: "JetBrains Mono, monospace",
              fontSize: 12,
              fontWeight: 700,
              padding: "3px 10px",
              borderRadius: 6,
              border: "1px solid rgba(56, 189, 248, 0.4)",
            }}
          >
            VOUCHER #PUR-2026-0841
          </span>
          <span style={{ fontSize: 13, color: "#94a3b8", fontFamily: "Inter, sans-serif" }}>
            Date: <strong style={{ color: "#f1f5f9" }}>24-Mar-2026</strong>
          </span>
          <span style={{ fontSize: 13, color: "#94a3b8", fontFamily: "Inter, sans-serif" }}>
            Entity: <strong style={{ color: "#f1f5f9" }}>ABC Industrial Supplies Pvt Ltd</strong>
          </span>
        </div>

        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <div style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: "#10b981" }} />
          <span style={{ fontSize: 12, color: "#34d399", fontWeight: 600, fontFamily: "Inter, sans-serif" }}>
            Double-Entry Balanced
          </span>
        </div>
      </div>

      {/* Main Journal Entry Table */}
      <div
        style={{
          width: "100%",
          backgroundColor: "rgba(15, 23, 42, 0.95)",
          border: "1px solid rgba(148, 163, 184, 0.2)",
          padding: "20px 24px",
          display: "flex",
          flexDirection: "column",
          gap: 12,
          fontFamily: "JetBrains Mono, monospace",
          boxShadow: "0 20px 40px rgba(0,0,0,0.6)",
        }}
      >
        {/* Table Header */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "3fr 1fr 1.5fr 1.5fr",
            paddingBottom: 8,
            borderBottom: "1px solid rgba(148, 163, 184, 0.15)",
            fontSize: 11,
            color: "#64748b",
            fontWeight: 700,
            letterSpacing: "0.05em",
          }}
        >
          <span>PARTICULARS (LEDGER ACCOUNT)</span>
          <span style={{ textAlign: "center" }}>TYPE</span>
          <span style={{ textAlign: "right" }}>DEBIT (DR)</span>
          <span style={{ textAlign: "right" }}>CREDIT (CR)</span>
        </div>

        {/* Row 1: Purchase A/c Dr */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "3fr 1fr 1.5fr 1.5fr",
            fontSize: 15,
            fontWeight: 600,
            opacity: interpolate(spring1, [0, 1], [0, 1]),
            transform: `translateX(${interpolate(spring1, [0, 1], [-20, 0])}px)`,
            color: "#f8fafc",
            alignItems: "center",
          }}
        >
          <span>Purchase A/c (Electrical Components)</span>
          <span style={{ textAlign: "center", color: "#38bdf8", fontSize: 12 }}>Dr</span>
          <span style={{ textAlign: "right", color: "#38bdf8" }}>₹ 4,50,000.00</span>
          <span style={{ textAlign: "right", color: "#475569" }}>—</span>
        </div>

        {/* Row 2: Input CGST Dr */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "3fr 1fr 1.5fr 1.5fr",
            fontSize: 15,
            fontWeight: 600,
            opacity: interpolate(spring2, [0, 1], [0, 1]),
            transform: `translateX(${interpolate(spring2, [0, 1], [-20, 0])}px)`,
            color: "#f8fafc",
            alignItems: "center",
          }}
        >
          <span>Input CGST @ 9%</span>
          <span style={{ textAlign: "center", color: "#38bdf8", fontSize: 12 }}>Dr</span>
          <span style={{ textAlign: "right", color: "#38bdf8" }}>₹ 40,500.00</span>
          <span style={{ textAlign: "right", color: "#475569" }}>—</span>
        </div>

        {/* Row 3: Input SGST Dr */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "3fr 1fr 1.5fr 1.5fr",
            fontSize: 15,
            fontWeight: 600,
            opacity: interpolate(spring3, [0, 1], [0, 1]),
            transform: `translateX(${interpolate(spring3, [0, 1], [-20, 0])}px)`,
            color: "#f8fafc",
            alignItems: "center",
          }}
        >
          <span>Input SGST @ 9%</span>
          <span style={{ textAlign: "center", color: "#38bdf8", fontSize: 12 }}>Dr</span>
          <span style={{ textAlign: "right", color: "#38bdf8" }}>₹ 40,500.00</span>
          <span style={{ textAlign: "right", color: "#475569" }}>—</span>
        </div>

        {/* Row 4: To Vendor A/c Cr */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "3fr 1fr 1.5fr 1.5fr",
            fontSize: 15,
            fontWeight: 600,
            opacity: interpolate(spring4, [0, 1], [0, 1]),
            transform: `translateX(${interpolate(spring4, [0, 1], [20, 0])}px)`,
            color: "#f8fafc",
            alignItems: "center",
          }}
        >
          <span style={{ paddingLeft: 28, color: "#cbd5e1" }}>To Schneider Electric India Cr</span>
          <span style={{ textAlign: "center", color: "#10b981", fontSize: 12 }}>Cr</span>
          <span style={{ textAlign: "right", color: "#475569" }}>—</span>
          <span style={{ textAlign: "right", color: "#10b981" }}>₹ 5,31,000.00</span>
        </div>

        {/* Total Summary Footer */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "3fr 1fr 1.5fr 1.5fr",
            marginTop: 8,
            paddingTop: 10,
            borderTop: "2px solid rgba(56, 189, 248, 0.4)",
            fontSize: 16,
            fontWeight: 700,
            color: "#38bdf8",
          }}
        >
          <span>TOTAL POSTING</span>
          <span style={{ textAlign: "center" }}></span>
          <span style={{ textAlign: "right" }}>₹ 5,31,000.00</span>
          <span style={{ textAlign: "right", color: "#10b981" }}>₹ 5,31,000.00</span>
        </div>
      </div>

      {/* Streaming ledger sub-strip showing high-speed posting */}
      <div
        style={{
          width: "100%",
          backgroundColor: "#0b0f19",
          borderBottomLeftRadius: 14,
          borderBottomRightRadius: 14,
          border: "1px solid rgba(148, 163, 184, 0.2)",
          borderTop: "none",
          padding: "10px 24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span style={{ fontSize: 12, color: "#64748b", fontFamily: "Inter, sans-serif" }}>
          Double-Entry Ledger Engine: <strong style={{ color: "#38bdf8" }}>SQLite Sidecar Vault</strong>
        </span>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <span style={{ fontSize: 12, color: "#10b981", fontFamily: "JetBrains Mono, monospace" }}>
            2,481 Vouchers Posted / 0 Suspense
          </span>
        </div>
      </div>
    </div>
  );
};
