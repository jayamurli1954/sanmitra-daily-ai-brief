import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const TrustLayerBadges: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const trustItems = [
    { name: "Source Document", desc: "Original Tax Invoice / GSTR-2B" },
    { name: "Posted Voucher", desc: "Balanced Double-Entry Journal" },
    { name: "General Ledger", desc: "Unbroken Transaction Lineage" },
    { name: "Trial Balance", desc: "Mathematical Parity Verified" },
    { name: "Working Paper", desc: "Cross-Referenced Audit Evidence" },
  ];

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 8,
        width: 380,
        backgroundColor: "rgba(15, 23, 42, 0.9)",
        border: "1px solid rgba(16, 185, 129, 0.4)",
        borderRadius: 16,
        padding: "18px 20px",
        boxShadow: "0 20px 40px rgba(0, 0, 0, 0.5), 0 0 20px rgba(16, 185, 129, 0.15)",
        backdropFilter: "blur(14px)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
        <div
          style={{
            width: 10,
            height: 10,
            borderRadius: "50%",
            backgroundColor: "#10b981",
            boxShadow: "0 0 10px #10b981",
          }}
        />
        <span
          style={{
            fontSize: 14,
            fontWeight: 700,
            color: "#f8fafc",
            fontFamily: "Inter, sans-serif",
            letterSpacing: "0.02em",
          }}
        >
          SSDV EVIDENCE TRUST LAYER
        </span>
      </div>

      {trustItems.map((item, idx) => {
        const itemSpring = spring({
          frame: frame - idx * 10,
          fps,
          config: { damping: 14 },
        });

        const opacity = interpolate(itemSpring, [0, 1], [0, 1]);
        const translateX = interpolate(itemSpring, [0, 1], [20, 0]);

        return (
          <div
            key={item.name}
            style={{
              opacity,
              transform: `translateX(${translateX}px)`,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "8px 12px",
              backgroundColor: "rgba(30, 41, 59, 0.6)",
              borderRadius: 8,
              border: "1px solid rgba(148, 163, 184, 0.15)",
            }}
          >
            <div style={{ display: "flex", flexDirection: "column" }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: "#f1f5f9", fontFamily: "Inter, sans-serif" }}>
                {item.name}
              </span>
              <span style={{ fontSize: 10, color: "#94a3b8", fontFamily: "Inter, sans-serif" }}>
                {item.desc}
              </span>
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: 22,
                height: 22,
                borderRadius: "50%",
                backgroundColor: "rgba(16, 185, 129, 0.2)",
                color: "#10b981",
                fontWeight: 700,
                fontSize: 13,
                border: "1px solid rgba(16, 185, 129, 0.5)",
              }}
            >
              ✓
            </div>
          </div>
        );
      })}
    </div>
  );
};
