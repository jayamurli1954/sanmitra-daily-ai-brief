import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SponsorConfig } from "../types";
import { TechBackground } from "./TechBackground";

interface SponsorSlotProps {
  sponsor: SponsorConfig;
}

export const SponsorSlot: React.FC<SponsorSlotProps> = ({ sponsor }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  return (
    <div
      style={{
        position: "relative",
        width: 1920,
        height: 1080,
        backgroundColor: "#030712",
        overflow: "hidden",
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      <TechBackground tintColor="#10b981" />

      {/* Sponsor Banner Card */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: 1100,
          backgroundColor: "rgba(15, 23, 42, 0.94)",
          border: "2px solid #10b981",
          borderRadius: 24,
          padding: "50px 60px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          boxShadow: "0 20px 60px rgba(0, 0, 0, 0.8)",
          opacity: entrance,
          scale: `${0.9 + entrance * 0.1}`,
          zIndex: 25,
        }}
      >
        <div
          style={{
            backgroundColor: "rgba(16, 185, 129, 0.15)",
            border: "1px solid #10b981",
            color: "#10b981",
            padding: "6px 20px",
            borderRadius: 20,
            fontSize: 14,
            fontWeight: 800,
            letterSpacing: 2.5,
            marginBottom: 20,
          }}
        >
          BROUGHT TO YOU BY
        </div>

        <h1
          style={{
            color: "#ffffff",
            fontSize: 54,
            fontWeight: 900,
            letterSpacing: -1,
            margin: "0 0 16px 0",
          }}
        >
          {sponsor.sponsorName}
        </h1>

        <p
          style={{
            color: "#34d399",
            fontSize: 24,
            fontWeight: 700,
            margin: "0 0 28px 0",
            maxWidth: 800,
          }}
        >
          {sponsor.tagline}
        </p>

        <div
          style={{
            backgroundColor: "#10b981",
            color: "#ffffff",
            padding: "12px 32px",
            borderRadius: 30,
            fontSize: 18,
            fontWeight: 800,
            letterSpacing: 1.5,
            boxShadow: "0 0 24px rgba(16, 185, 129, 0.5)",
          }}
        >
          {sponsor.callToAction.toUpperCase()}
        </div>
      </div>
    </div>
  );
};
