import React from "react";
import { Audio, staticFile } from "remotion";
import { BackgroundBed } from "../components/BackgroundBed";
import { ProductScreenFrame } from "../components/ProductScreenFrame";
import { SubtitleDisplay } from "../components/SubtitleDisplay";
import { TrustLayerBadges } from "../components/TrustLayerBadges";

export const Scene07Review: React.FC = () => {
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
      <Audio src={staticFile("audio/officemitra/om_s07_review.mp3")} volume={1.0} />
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
            Review Intelligence
          </span>
          <span
            style={{
              fontSize: 13,
              fontFamily: "JetBrains Mono, monospace",
              fontWeight: 700,
              color: "#10b981",
              letterSpacing: "0.05em",
              backgroundColor: "rgba(16, 185, 129, 0.15)",
              padding: "3px 12px",
              borderRadius: 6,
              border: "1px solid rgba(16, 185, 129, 0.3)",
            }}
          >
            Quality Score: 98.4 / 100
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
          Automated GSTR-2B ITC Reconciliation & Quality Gate
        </h3>
      </div>

      {/* Split layout: Real Product Screen on left, Evidence Trust Layer on right */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 28,
          width: "90%",
          maxWidth: 1380,
          zIndex: 20,
        }}
      >
        <div style={{ flex: 1 }}>
          <ProductScreenFrame
            imageSrc={staticFile("officemitra/board-01-red-flags.png")}
            title="SSDV Review Gate — Red Flags & GSTR-2B Recon"
            badge="Quality Gate Cleared"
            width={780}
            height={460}
            scale={1.0}
          />
        </div>

        <div style={{ width: 380 }}>
          <TrustLayerBadges />
        </div>
      </div>

      <SubtitleDisplay
        text="Review faster with AI-assisted risk detection and automated GSTR-2B ITC reconciliation. Complete traceability from source document to working paper."
        highlightWord="Complete traceability"
      />
    </div>
  );
};
