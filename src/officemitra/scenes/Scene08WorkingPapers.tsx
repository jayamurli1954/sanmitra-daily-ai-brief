import React from "react";
import { Audio, staticFile } from "remotion";
import { BackgroundBed } from "../components/BackgroundBed";
import { ProductScreenFrame } from "../components/ProductScreenFrame";
import { SubtitleDisplay } from "../components/SubtitleDisplay";

export const Scene08WorkingPapers: React.FC = () => {
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
      <Audio src={staticFile("audio/officemitra/om_s08_workingpapers.mp3")} volume={1.0} />
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
            Audit Ready
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
            Unbroken Audit Trail
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
          Automated Working Papers & Cross-Referenced Evidence
        </h3>
      </div>

      {/* Real Product Screen Frame */}
      <div style={{ zIndex: 20 }}>
        <ProductScreenFrame
          imageSrc={staticFile("officemitra/board-03-policy-scorecard.png")}
          title="SSDV Audit Trail — Policy Scorecard & Working Schedules"
          badge="Audit Sign-Off Ready"
          width={1050}
          height={530}
          scale={0.96}
        />
      </div>

      <SubtitleDisplay
        text="Generate audit-ready working papers automatically—complete with unbroken audit trails and source document verification."
        highlightWord="unbroken audit trails"
      />
    </div>
  );
};
