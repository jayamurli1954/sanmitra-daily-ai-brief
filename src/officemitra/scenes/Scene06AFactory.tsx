import React from "react";
import { Audio, staticFile, useCurrentFrame } from "remotion";
import { AccountingFactoryFlow } from "../components/AccountingFactoryFlow";
import { BackgroundBed } from "../components/BackgroundBed";
import { JournalEntryStream } from "../components/JournalEntryStream";
import { SubtitleDisplay } from "../components/SubtitleDisplay";
import { ThroughputCounter } from "../components/ThroughputCounter";

export const Scene06AFactory: React.FC = () => {
  const frame = useCurrentFrame();

  // Part 1 (frames 0 - 160): Conveyor flow + Real Journal Postings
  // Part 2 (frames 160 - 300): Throughput scaling counter
  const showThroughput = frame >= 170;

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
      <Audio src={staticFile("audio/officemitra/om_s06a_factory.mp3")} volume={1.0} />
      <BackgroundBed intensity="intense" />

      {/* Header */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          marginBottom: 18,
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
          The Accounting Factory
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
          From Raw Source Documents to Balanced Double-Entry Ledgers
        </h3>
      </div>

      {/* Top Conveyor Pipeline */}
      <div style={{ zIndex: 20, marginBottom: 20 }}>
        <AccountingFactoryFlow />
      </div>

      {/* Center Dynamic Switch: Real Journal Entries or Throughput Scale */}
      <div style={{ zIndex: 20, width: "100%", display: "flex", justifyContent: "center" }}>
        {!showThroughput ? <JournalEntryStream /> : <ThroughputCounter />}
      </div>

      <SubtitleDisplay
        text="Every document becomes structured accounting intelligence automatically. Real double-entry books. Reconciled before review."
        highlightWord="Real double-entry books"
      />
    </div>
  );
};
