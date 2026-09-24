import React from "react";
import { Audio, staticFile } from "remotion";
import { BackgroundBed } from "../components/BackgroundBed";
import { ProductScreenFrame } from "../components/ProductScreenFrame";
import { SubtitleDisplay } from "../components/SubtitleDisplay";

export const Scene06SSDV: React.FC = () => {
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
      <Audio src={staticFile("audio/officemitra/om_s06_ssdv.mp3")} volume={1.0} />
      <BackgroundBed intensity="intense" />

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
        <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 6 }}>
          <span
            style={{
              fontSize: 13,
              fontFamily: "JetBrains Mono, monospace",
              fontWeight: 700,
              color: "#38bdf8",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
              backgroundColor: "rgba(56, 189, 248, 0.15)",
              padding: "3px 12px",
              borderRadius: 6,
              border: "1px solid rgba(56, 189, 248, 0.3)",
            }}
          >
            The Intelligence Engine
          </span>
          <span
            style={{
              fontSize: 13,
              fontFamily: "JetBrains Mono, monospace",
              fontWeight: 700,
              color: "#34d399",
              letterSpacing: "0.05em",
              backgroundColor: "rgba(16, 185, 129, 0.15)",
              padding: "3px 12px",
              borderRadius: 6,
              border: "1px solid rgba(16, 185, 129, 0.3)",
            }}
          >
            Double-Entry Validated
          </span>
        </div>

        <h3
          style={{
            fontSize: 38,
            fontWeight: 800,
            fontFamily: "Inter, sans-serif",
            color: "#f8fafc",
            margin: 0,
            letterSpacing: "-0.02em",
          }}
        >
          SSDV: Synthetic Data Vault Core
        </h3>
      </div>

      {/* Real Product Screen Frame */}
      <div style={{ zIndex: 20 }}>
        <ProductScreenFrame
          imageSrc={staticFile("officemitra/chart-01-activity-sales-cogs.png")}
          title="SSDV Intelligence Core — Activity & Sales/COGS Posting"
          badge="Balanced Double-Entry Engine"
          width={1050}
          height={530}
          scale={0.96}
        />
      </div>

      <SubtitleDisplay
        text="At the core lies SSDV. An intelligent accounting engine that transforms raw extractions into structured, immutable double-entry records."
        highlightWord="intelligent accounting engine"
      />
    </div>
  );
};
