import React from "react";
import { Audio, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BackgroundBed } from "../components/BackgroundBed";
import { SubtitleDisplay } from "../components/SubtitleDisplay";

export const Scene05Extraction: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scanPos = interpolate(frame % 90, [0, 90], [0, 480]);

  const fields = [
    { label: "GSTIN", value: "27AABCT9981K1Z2", top: 110, left: 60, width: 260, delay: 10 },
    { label: "VENDOR", value: "Schneider Electric India Pvt Ltd", top: 180, left: 60, width: 380, delay: 20 },
    { label: "HSN / SAC", value: "85369090 (Switchgear)", top: 250, left: 60, width: 240, delay: 30 },
    { label: "TAXABLE VALUE", value: "₹ 4,50,000.00", top: 320, left: 60, width: 220, delay: 40 },
    { label: "CGST (9%)", value: "₹ 40,500.00", top: 320, left: 320, width: 170, delay: 50 },
    { label: "SGST (9%)", value: "₹ 40,500.00", top: 320, left: 520, width: 170, delay: 60 },
    { label: "TOTAL INVOICE", value: "₹ 5,31,000.00", top: 390, left: 450, width: 240, delay: 70, highlight: true },
  ];

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#070b16",
        overflow: "hidden",
      }}
    >
      <Audio src={staticFile("audio/officemitra/om_s05_extraction.mp3")} volume={1.0} />
      <BackgroundBed intensity="cyan" />

      {/* Header */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          marginBottom: 16,
          zIndex: 20,
        }}
      >
        <span
          style={{
            fontSize: 13,
            fontFamily: "JetBrains Mono, monospace",
            fontWeight: 700,
            color: "#38bdf8",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            marginBottom: 6,
            backgroundColor: "rgba(56, 189, 248, 0.15)",
            padding: "3px 12px",
            borderRadius: 6,
            border: "1px solid rgba(56, 189, 248, 0.3)",
          }}
        >
          AI Document Understanding
        </span>

        <h3
          style={{
            fontSize: 36,
            fontWeight: 800,
            fontFamily: "Inter, sans-serif",
            color: "#f8fafc",
            margin: 0,
            letterSpacing: "-0.02em",
          }}
        >
          Precision Extraction on Indian Invoices & Bank Feeds
        </h3>
      </div>

      {/* High-Tech Invoice HUD Scanner Frame */}
      <div
        style={{
          position: "relative",
          width: 820,
          height: 480,
          backgroundColor: "rgba(15, 23, 42, 0.9)",
          border: "1px solid rgba(56, 189, 248, 0.4)",
          borderRadius: 16,
          boxShadow: "0 20px 50px rgba(0, 0, 0, 0.7), 0 0 30px rgba(56, 189, 248, 0.15)",
          overflow: "hidden",
          zIndex: 20,
          backdropFilter: "blur(16px)",
        }}
      >
        {/* Laser scan bar */}
        <div
          style={{
            position: "absolute",
            top: scanPos,
            left: 0,
            right: 0,
            height: 3,
            backgroundColor: "#38bdf8",
            boxShadow: "0 0 15px #38bdf8, 0 0 30px #38bdf8",
            zIndex: 30,
          }}
        />

        {/* Invoice Top Watermark Header */}
        <div
          style={{
            padding: "16px 24px",
            borderBottom: "1px solid rgba(148, 163, 184, 0.15)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <span style={{ fontSize: 16 }}>📄</span>
            <span style={{ fontSize: 14, fontWeight: 700, color: "#f8fafc", fontFamily: "Inter, sans-serif" }}>
              TAX INVOICE — ORIGINAL FOR RECIPIENT
            </span>
          </div>
          <span
            style={{
              fontSize: 11,
              fontFamily: "JetBrains Mono, monospace",
              color: "#34d399",
              backgroundColor: "rgba(16, 185, 129, 0.15)",
              padding: "2px 8px",
              borderRadius: 4,
            }}
          >
            AI Confidence: 99.8%
          </span>
        </div>

        {/* Extracted Bounding Boxes */}
        {fields.map((f) => {
          const fSpring = spring({ frame: frame - f.delay, fps, config: { damping: 14 } });
          const isVisible = frame >= f.delay;

          return (
            <div
              key={f.label}
              style={{
                position: "absolute",
                top: f.top,
                left: f.left,
                width: f.width,
                opacity: isVisible ? interpolate(fSpring, [0, 1], [0, 1]) : 0,
                transform: `scale(${isVisible ? interpolate(fSpring, [0, 1], [0.95, 1]) : 0.95})`,
                backgroundColor: f.highlight ? "rgba(16, 185, 129, 0.15)" : "rgba(30, 41, 59, 0.8)",
                border: f.highlight ? "1px solid #10b981" : "1px solid rgba(56, 189, 248, 0.5)",
                borderRadius: 8,
                padding: "6px 12px",
                display: "flex",
                flexDirection: "column",
                boxShadow: f.highlight ? "0 0 15px rgba(16, 185, 129, 0.3)" : "none",
              }}
            >
              <span
                style={{
                  fontSize: 10,
                  fontFamily: "JetBrains Mono, monospace",
                  color: f.highlight ? "#34d399" : "#38bdf8",
                  fontWeight: 700,
                  letterSpacing: "0.05em",
                }}
              >
                {f.label} ✓
              </span>
              <span
                style={{
                  fontSize: f.highlight ? 16 : 13,
                  fontFamily: "Inter, sans-serif",
                  fontWeight: 600,
                  color: "#f8fafc",
                }}
              >
                {f.value}
              </span>
            </div>
          );
        })}
      </div>

      <SubtitleDisplay
        text="Built-in AI understands every document. Extracting critical tax and transactional data without manual data entry."
        highlightWord="without manual data entry"
      />
    </div>
  );
};
