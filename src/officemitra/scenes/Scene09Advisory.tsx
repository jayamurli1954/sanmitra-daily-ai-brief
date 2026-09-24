import React from "react";
import { Audio, staticFile } from "remotion";
import { BackgroundBed } from "../components/BackgroundBed";
import { ProductScreenFrame } from "../components/ProductScreenFrame";
import { SubtitleDisplay } from "../components/SubtitleDisplay";

export const Scene09Advisory: React.FC = () => {
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
      <Audio src={staticFile("audio/officemitra/om_s09_advisory.mp3")} volume={1.0} />
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
            From Compliance to Advisory
          </span>
          <span
            style={{
              fontSize: 13,
              fontFamily: "JetBrains Mono, monospace",
              fontWeight: 700,
              color: "#f59e0b",
              letterSpacing: "0.05em",
              backgroundColor: "rgba(245, 158, 11, 0.15)",
              padding: "3px 12px",
              borderRadius: 6,
              border: "1px solid rgba(245, 158, 11, 0.3)",
            }}
          >
            Virtual CFO Deliverables
          </span>
        </div>

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
          30 / 60 / 90-Day Cash Forecasts & Investor Board Packs
        </h3>
      </div>

      {/* Real Product Screen Frame */}
      <div style={{ zIndex: 20 }}>
        <ProductScreenFrame
          imageSrc={staticFile("officemitra/cfo-02-cash-forecast.png")}
          title="OfficeMitra CFO Suite — 30/60/90 Cash Runway & Collections"
          badge="Live Cash Position"
          width={1050}
          height={530}
          scale={0.96}
        />
      </div>

      <SubtitleDisplay
        text="Move beyond compliance. Transform accounting data into high-value CFO advisory, ninety-day cash forecasts, and investor-ready board packs."
        highlightWord="high-value CFO advisory"
      />
    </div>
  );
};
