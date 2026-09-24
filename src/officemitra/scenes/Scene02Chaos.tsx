import React from "react";
import { Audio, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BackgroundBed } from "../components/BackgroundBed";
import { SubtitleDisplay } from "../components/SubtitleDisplay";

export const Scene02Chaos: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSpring = spring({ frame: frame - 5, fps, config: { damping: 14 } });

  const docNodes = [
    { title: "Bank Statement (ICICI).pdf", type: "PDF", x: -380, y: -160, rot: -8, delay: 0 },
    { title: "Purchase_Inv_8842.pdf", type: "Tax Invoice", x: 360, y: -180, rot: 12, delay: 5 },
    { title: "GSTR2B_27AABCT9981.json", type: "GST Portal", x: -420, y: 140, rot: 6, delay: 10 },
    { title: "WhatsApp_Bill_Photo.jpg", type: "Receipt", x: 380, y: 130, rot: -10, delay: 15 },
    { title: "DayBook_Export_2026.xlsx", type: "Excel", x: -200, y: 220, rot: -4, delay: 8 },
    { title: "Tally_Vouchers.xml", type: "XML", x: 220, y: 230, rot: 7, delay: 12 },
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
        backgroundColor: "#060913",
        overflow: "hidden",
      }}
    >
      <Audio src={staticFile("audio/officemitra/om_s02_chaos.mp3")} volume={1.0} />
      <BackgroundBed intensity="dark" />

      {/* Floating Converging Document Cards */}
      {docNodes.map((doc) => {
        const dSpring = spring({ frame: frame - doc.delay, fps, config: { damping: 12 } });
        // Cards drift inwards toward center as frame progresses
        const drift = interpolate(frame, [0, 240], [1, 0.4]);
        const currX = doc.x * drift;
        const currY = doc.y * drift;
        const opacity = interpolate(dSpring, [0, 1], [0, 0.85]);

        return (
          <div
            key={doc.title}
            style={{
              position: "absolute",
              transform: `translate(${currX}px, ${currY}px) rotate(${doc.rot}deg)`,
              opacity,
              backgroundColor: "rgba(30, 41, 59, 0.85)",
              border: "1px solid rgba(148, 163, 184, 0.3)",
              borderRadius: 12,
              padding: "12px 16px",
              display: "flex",
              alignItems: "center",
              gap: 12,
              boxShadow: "0 15px 30px rgba(0,0,0,0.6)",
              backdropFilter: "blur(10px)",
              zIndex: 10,
            }}
          >
            <div
              style={{
                backgroundColor: "rgba(56, 189, 248, 0.15)",
                color: "#38bdf8",
                fontSize: 10,
                fontWeight: 700,
                fontFamily: "JetBrains Mono, monospace",
                padding: "4px 8px",
                borderRadius: 6,
              }}
            >
              {doc.type}
            </div>
            <span
              style={{
                fontSize: 13,
                fontWeight: 500,
                fontFamily: "Inter, sans-serif",
                color: "#e2e8f0",
              }}
            >
              {doc.title}
            </span>
          </div>
        );
      })}

      {/* Center Gravitational Storm Statement */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          zIndex: 20,
          opacity: interpolate(titleSpring, [0, 1], [0, 1]),
          transform: `scale(${interpolate(titleSpring, [0, 1], [0.92, 1])})`,
        }}
      >
        <span
          style={{
            fontSize: 14,
            fontWeight: 700,
            fontFamily: "JetBrains Mono, monospace",
            color: "#f59e0b",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            marginBottom: 16,
            backgroundColor: "rgba(245, 158, 11, 0.12)",
            padding: "4px 14px",
            borderRadius: 6,
            border: "1px solid rgba(245, 158, 11, 0.3)",
          }}
        >
          Unstructured Ingestion
        </span>

        <h2
          style={{
            fontSize: 58,
            fontWeight: 900,
            fontFamily: "Inter, sans-serif",
            letterSpacing: "-0.03em",
            color: "#ffffff",
            margin: "0 0 16px 0",
            lineHeight: 1.1,
          }}
        >
          Documents Everywhere.
          <br />
          <span
            style={{
              background: "linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Data Nowhere.
          </span>
        </h2>

        <p
          style={{
            fontSize: 20,
            fontFamily: "Inter, sans-serif",
            color: "#94a3b8",
            maxWidth: 620,
            margin: 0,
            lineHeight: 1.5,
          }}
        >
          Without automated extraction and reconciliation, critical business insight stays locked away in file attachments.
        </p>
      </div>

      <SubtitleDisplay
        text="Client data arrives from everywhere. But meaningful insight remains buried inside unstructured documents."
        highlightWord="buried inside unstructured documents"
      />
    </div>
  );
};
