import React from "react";
import {
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Region } from "../types";

interface SectionTransitionProps {
  region: Region;
  title: string;
  display?: string;
  count?: number;
}

const REGION_COLORS: Record<Region, string> = {
  WORLD: "#38bdf8",
  USA: "#60a5fa",
  CHINA: "#ef4444",
  ASIA: "#34d399",
  INDIA: "#f59e0b",
  GLOBAL: "#a855f7",
};

export const SectionTransition: React.FC<SectionTransitionProps> = ({
  region,
  title,
  display,
  count,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 120 },
  });

  const strobe = interpolate(frame, [0, 3, 8], [0.8, 0.3, 0], {
    extrapolateRight: "clamp",
  });

  const accentColor = REGION_COLORS[region] || "#38bdf8";
  const mainDisplayText = display || title;

  return (
    <div
      style={{
        position: "relative",
        width: 1920,
        height: 1080,
        overflow: "hidden",
        backgroundColor: "#030712",
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      {/* 0. SECTION TRANSITION ENVIRONMENT */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          overflow: "hidden",
          zIndex: 0,
        }}
      >
        <Img
          src={staticFile("aibrief/backgrounds/ai_chips.jpg")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${interpolate(frame, [0, 60], [1.0, 1.05], { extrapolateRight: "clamp" })})`,
            filter: "brightness(0.35) contrast(1.2)",
          }}
        />

        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "radial-gradient(ellipse at center, rgba(3, 7, 18, 0.6) 0%, rgba(3, 7, 18, 0.92) 100%)",
          }}
        />
      </div>

      {/* Opening transition strobe */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: "#ffffff",
          opacity: strobe,
          zIndex: 50,
          pointerEvents: "none",
        }}
      />

      {/* CENTER STAGE BANNER */}
      <div
        style={{
          position: "absolute",
          top: 72,
          left: 0,
          right: 0,
          bottom: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 20,
        }}
      >
        <div
          style={{
            textAlign: "center",
            backgroundColor: "rgba(10, 18, 35, 0.94)",
            border: `2px solid ${accentColor}`,
            borderRadius: 20,
            padding: "40px 72px",
            boxShadow: `0 24px 60px rgba(0, 0, 0, 0.9), 0 0 40px ${accentColor}33`,
            opacity: entrance,
            transform: `scale(${0.9 + entrance * 0.1})`,
          }}
        >
          {/* Header Pill */}
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 10,
              backgroundColor: `${accentColor}22`,
              border: `1px solid ${accentColor}`,
              color: accentColor,
              padding: "6px 20px",
              borderRadius: 20,
              fontSize: 13,
              fontWeight: 900,
              letterSpacing: 2,
              marginBottom: 16,
            }}
          >
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                backgroundColor: accentColor,
                boxShadow: `0 0 10px ${accentColor}`,
              }}
            />
            <span>SANMITRA WIRE • CONTINENTAL DESK</span>
          </div>

          <h1
            style={{
              color: "#ffffff",
              fontSize: 56,
              fontWeight: 950,
              letterSpacing: 3,
              lineHeight: 1.1,
              margin: "0 0 12px 0",
              textShadow: "0 4px 20px rgba(0,0,0,0.8)",
            }}
          >
            {mainDisplayText}
          </h1>

          <p
            style={{
              color: "#94a3b8",
              fontSize: 17,
              fontWeight: 700,
              letterSpacing: 1.2,
              margin: 0,
              textTransform: "uppercase",
            }}
          >
            Specialized Regional & Sector Analysis
          </p>
        </div>
      </div>
    </div>
  );
};
