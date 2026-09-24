import React from "react";
import { Audio, staticFile } from "remotion";
import { BackgroundBed } from "../components/BackgroundBed";
import { ProductScreenFrame } from "../components/ProductScreenFrame";
import { SubtitleDisplay } from "../components/SubtitleDisplay";

export const Scene04Portal: React.FC = () => {
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
      <Audio src={staticFile("audio/officemitra/om_s04_portal.mp3")} volume={1.0} />
      <BackgroundBed intensity="cyan" />

      {/* Top Header */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          marginBottom: 20,
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
          Smart Client Portal
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
          Zero-Friction Document Intake & Multi-Source Connectors
        </h3>
      </div>

      {/* Real Product Screen Frame */}
      <div style={{ zIndex: 20 }}>
        <ProductScreenFrame
          imageSrc={staticFile("officemitra/connect-01-data-source.png")}
          title="OfficeMitra Data Connect — Read-Only Intake"
          badge="TallyPrime XML • CSV • GSTR-2B"
          width={1050}
          height={540}
          scale={0.96}
        />
      </div>

      <SubtitleDisplay
        text="Collect documents seamlessly. Automatically classify, organize, and prepare data for processing without chasing clients."
        highlightWord="Collect documents seamlessly"
      />
    </div>
  );
};
