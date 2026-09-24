import React from "react";
import { Audio, staticFile } from "remotion";
import { BackgroundBed } from "../components/BackgroundBed";
import { CommandMetricTiles } from "../components/CommandMetricTiles";
import { SubtitleDisplay } from "../components/SubtitleDisplay";

export const Scene10CommandCenter: React.FC = () => {
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
      <Audio src={staticFile("audio/officemitra/om_s10_commandcenter.mp3")} volume={1.0} />
      <BackgroundBed intensity="intense" />

      {/* Header */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          marginBottom: 24,
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
          Practice Scaling & Command Center
        </span>

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
          From Compliance-Driven to Intelligence-Driven
        </h3>
      </div>

      {/* Executive Command HUD Tiles and Success Narrative */}
      <div style={{ zIndex: 20, width: "100%", display: "flex", justifyContent: "center" }}>
        <CommandMetricTiles />
      </div>

      <SubtitleDisplay
        text="Manage hundreds of clients through a single intelligent operating system. From a compliance-driven practice to an intelligence-driven firm."
        highlightWord="intelligence-driven firm"
      />
    </div>
  );
};
