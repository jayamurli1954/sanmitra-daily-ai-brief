import React from "react";
import {
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { IntroConfig } from "../types";

interface IntroSceneProps {
  intro: IntroConfig;
  formattedDate: string;
}

export const IntroScene: React.FC<IntroSceneProps> = ({
  intro,
  formattedDate,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Instant snap entrance (0 to 6 frames)
  const hookSpring = spring({
    frame,
    fps,
    config: { damping: 10, stiffness: 120 },
  });

  // White broadcast cut strobe
  const strobe = interpolate(frame, [0, 4, 10], [0.9, 0.4, 0], {
    extrapolateRight: "clamp",
  });

  // Cinematic subtle push-in on lead visual
  const visualScale = interpolate(frame, [0, 300], [1.0, 1.06], {
    extrapolateRight: "clamp",
  });

  // Scanline sweep
  const scanlineY = (frame * 6) % 680;

  // Radar pulse
  const radarPulse = Math.sin(frame * 0.1) * 0.3 + 0.7;

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
      {/* 0. BASE PHOTOGRAPHIC NEWSROOM SET */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          overflow: "hidden",
          zIndex: 0,
        }}
      >
        <Img
          src={staticFile("aibrief/backgrounds/intro_newsroom.jpg")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${interpolate(frame, [0, 600], [1.0, 1.05], { extrapolateRight: "clamp" })})`,
          }}
        />

        {/* Ambient Dark Scrims for broadcast readability */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "radial-gradient(ellipse at 30% 50%, rgba(3, 7, 18, 0.72) 0%, rgba(3, 7, 18, 0.88) 100%)",
          }}
        />
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: 120,
            background:
              "linear-gradient(to bottom, rgba(3, 7, 18, 0.95), transparent)",
          }}
        />
      </div>

      {/* Opening Flash */}
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

      {/* SPLIT STUDIO STAGE */}
      <div
        style={{
          position: "absolute",
          top: 72,
          left: 0,
          right: 0,
          bottom: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 80px",
          zIndex: 20,
        }}
      >
        {/* LEFT: HIGH-ENERGY BREAKING HOOK */}
        <div style={{ maxWidth: 840 }}>
          {/* Breaking Red Banner */}
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 10,
              backgroundColor: "#dc2626",
              color: "#ffffff",
              padding: "8px 24px",
              borderRadius: 6,
              fontSize: 18,
              fontWeight: 900,
              letterSpacing: 3,
              marginBottom: 20,
              boxShadow: "0 0 30px rgba(220, 38, 38, 0.7)",
              transform: `scale(${0.9 + hookSpring * 0.1})`,
            }}
          >
            <span>● BREAKING AI NEWS</span>
            <span>•</span>
            <span>SANMITRA WIRE</span>
          </div>

          <h1
            style={{
              color: "#ffffff",
              fontSize: 62,
              fontWeight: 950,
              letterSpacing: -1,
              lineHeight: 1.08,
              margin: "0 0 16px 0",
              textShadow: "0 4px 24px rgba(0,0,0,0.9)",
            }}
          >
            TODAY'S BIGGEST DEVELOPMENTS
          </h1>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 16,
              marginTop: 20,
            }}
          >
            <div
              style={{
                backgroundColor: "rgba(15, 23, 42, 0.9)",
                border: "1px solid #38bdf8",
                color: "#38bdf8",
                padding: "8px 20px",
                borderRadius: 8,
                fontSize: 18,
                fontWeight: 800,
                letterSpacing: 2,
              }}
            >
              {formattedDate}
            </div>
            <div
              style={{
                backgroundColor: "rgba(220, 38, 38, 0.18)",
                border: "1px solid #ef4444",
                color: "#f87171",
                padding: "8px 20px",
                borderRadius: 8,
                fontSize: 16,
                fontWeight: 800,
                letterSpacing: 1.5,
              }}
            >
              AI SECURITY • MAJOR DEVELOPMENT
            </div>
          </div>
        </div>

        {/* RIGHT: LEAD STORY WAR ROOM MONITOR (INSTITUTIONAL AI NEWS VISUAL) */}
        <div
          style={{
            position: "relative",
            width: 780,
            height: 640,
            borderRadius: 20,
            overflow: "hidden",
            border: "2px solid rgba(56, 189, 248, 0.6)",
            boxShadow:
              "0 24px 60px rgba(0, 0, 0, 0.9), 0 0 50px rgba(56, 189, 248, 0.25)",
            backgroundColor: "#0b1329",
          }}
        >
          {/* Lead Story Image with Cinematic Zoom */}
          <div
            style={{
              width: "100%",
              height: "100%",
              overflow: "hidden",
              position: "relative",
            }}
          >
            <Img
              src={staticFile("aibrief/backgrounds/ai_security.jpg")}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                transform: `scale(${visualScale})`,
              }}
            />

            {/* Glowing Scanline effect */}
            <div
              style={{
                position: "absolute",
                top: scanlineY,
                left: 0,
                right: 0,
                height: 3,
                background:
                  "linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.8), transparent)",
                boxShadow: "0 0 15px #38bdf8",
                pointerEvents: "none",
              }}
            />

            {/* Dark vignette overlay */}
            <div
              style={{
                position: "absolute",
                inset: 0,
                background:
                  "radial-gradient(circle at center, transparent 40%, rgba(3, 7, 18, 0.75) 100%)",
                pointerEvents: "none",
              }}
            />
          </div>

          {/* Top Telemetry Header */}
          <div
            style={{
              position: "absolute",
              top: 16,
              left: 20,
              right: 20,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              zIndex: 30,
            }}
          >
            <div
              style={{
                backgroundColor: "rgba(10, 18, 35, 0.92)",
                border: "1px solid rgba(220, 38, 38, 0.6)",
                padding: "6px 14px",
                borderRadius: 6,
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  backgroundColor: "#dc2626",
                  boxShadow: `0 0 10px rgba(220, 38, 38, ${radarPulse})`,
                }}
              />
              <span
                style={{
                  color: "#ffffff",
                  fontSize: 12,
                  fontWeight: 900,
                  letterSpacing: 1.5,
                }}
              >
                LEAD STORY TELEMETRY
              </span>
            </div>

            <div
              style={{
                backgroundColor: "rgba(10, 18, 35, 0.88)",
                border: "1px solid rgba(56, 189, 248, 0.4)",
                padding: "6px 12px",
                borderRadius: 6,
                color: "#38bdf8",
                fontSize: 11,
                fontWeight: 800,
                letterSpacing: 1,
              }}
            >
              SRC: ARS TECHNICA
            </div>
          </div>

          {/* Bottom Telemetry Card */}
          <div
            style={{
              position: "absolute",
              bottom: 20,
              left: 20,
              right: 20,
              backgroundColor: "rgba(10, 18, 35, 0.94)",
              border: "1px solid rgba(56, 189, 248, 0.4)",
              borderRadius: 12,
              padding: "12px 20px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              backdropFilter: "blur(12px)",
              zIndex: 30,
            }}
          >
            <div>
              <div
                style={{
                  color: "#f87171",
                  fontSize: 12,
                  fontWeight: 800,
                  letterSpacing: 1.5,
                  marginBottom: 2,
                }}
              >
                CRITICAL VULNERABILITY EXPOSED
              </div>
              <div
                style={{
                  color: "#ffffff",
                  fontSize: 18,
                  fontWeight: 900,
                  letterSpacing: 0.5,
                }}
              >
                META MUSE AGENT 0-DAY CRISIS
              </div>
            </div>

            <div
              style={{
                backgroundColor: "#dc2626",
                color: "#ffffff",
                fontSize: 12,
                fontWeight: 900,
                padding: "6px 14px",
                borderRadius: 6,
                letterSpacing: 1.5,
              }}
            >
              AMAZON BLOCKED
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
