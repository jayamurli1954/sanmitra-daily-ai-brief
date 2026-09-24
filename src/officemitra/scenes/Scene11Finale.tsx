import React from "react";
import { Audio, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BackgroundBed } from "../components/BackgroundBed";
import { SubtitleDisplay } from "../components/SubtitleDisplay";
import { OM_BRAND } from "../types";

export const Scene11Finale: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const logoSpring = spring({ frame: frame - 5, fps, config: { damping: 14 } });
  const textSpring = spring({ frame: frame - 20, fps, config: { damping: 15 } });
  const contactSpring = spring({ frame: frame - 40, fps, config: { damping: 16 } });

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
      <Audio src={staticFile("audio/officemitra/om_s11_finale.mp3")} volume={1.0} />
      <BackgroundBed intensity="cyan" />

      {/* Main Brand Lockup */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          zIndex: 20,
          opacity: interpolate(logoSpring, [0, 1], [0, 1]),
          transform: `scale(${interpolate(logoSpring, [0, 1], [0.88, 1])})`,
          marginBottom: 20,
        }}
      >
        <div
          style={{
            backgroundColor: "rgba(15, 23, 42, 0.85)",
            border: "1px solid rgba(56, 189, 248, 0.4)",
            borderRadius: 24,
            padding: "20px 48px",
            display: "flex",
            alignItems: "center",
            gap: 28,
            boxShadow: "0 25px 60px rgba(0, 0, 0, 0.7), 0 0 50px rgba(56, 189, 248, 0.2)",
            backdropFilter: "blur(16px)",
          }}
        >
          <Img
            src={staticFile("officemitra/officemitra-logo-banner.png")}
            style={{
              height: 75,
              objectFit: "contain",
            }}
          />
          <div style={{ height: 40, width: 1, backgroundColor: "rgba(148, 163, 184, 0.3)" }} />
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span
              style={{
                fontSize: 22,
                fontWeight: 800,
                fontFamily: "Inter, sans-serif",
                color: "#38bdf8",
                letterSpacing: "0.08em",
              }}
            >
              + SSDV
            </span>
            <span
              style={{
                fontSize: 10,
                fontWeight: 600,
                fontFamily: "JetBrains Mono, monospace",
                color: "#94a3b8",
                letterSpacing: "0.05em",
              }}
            >
              SYNTHETIC DATA VAULT
            </span>
          </div>
        </div>
      </div>

      {/* Taglines */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          zIndex: 20,
          opacity: interpolate(textSpring, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(textSpring, [0, 1], [20, 0])}px)`,
          marginBottom: 28,
        }}
      >
        <h2
          style={{
            fontSize: 42,
            fontWeight: 800,
            fontFamily: "Inter, sans-serif",
            color: "#ffffff",
            margin: "0 0 10px 0",
            letterSpacing: "-0.02em",
          }}
        >
          {OM_BRAND.taglinePrimary}
        </h2>

        <span
          style={{
            fontSize: 20,
            fontWeight: 600,
            fontFamily: "Inter, sans-serif",
            color: "#38bdf8",
            letterSpacing: "0.02em",
            marginBottom: 16,
          }}
        >
          {OM_BRAND.taglineSupporting}
        </span>

        {/* Four Pillars */}
        <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
          {OM_BRAND.pillars.map((pil, idx) => (
            <React.Fragment key={pil}>
              <span
                style={{
                  fontSize: 14,
                  fontWeight: 700,
                  fontFamily: "JetBrains Mono, monospace",
                  color: "#cbd5e1",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                }}
              >
                {pil}
              </span>
              {idx < OM_BRAND.pillars.length - 1 && (
                <span style={{ color: "#38bdf8", fontSize: 16 }}>•</span>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Official Verified Contact Bar */}
      <div
        style={{
          display: "flex",
          gap: 24,
          alignItems: "center",
          zIndex: 20,
          opacity: interpolate(contactSpring, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(contactSpring, [0, 1], [20, 0])}px)`,
        }}
      >
        {/* WhatsApp */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            backgroundColor: "rgba(16, 185, 129, 0.15)",
            border: "1px solid rgba(16, 185, 129, 0.4)",
            borderRadius: 999,
            padding: "10px 22px",
            boxShadow: "0 0 20px rgba(16, 185, 129, 0.2)",
          }}
        >
          <span style={{ fontSize: 16 }}>💬</span>
          <span
            style={{
              fontSize: 14,
              fontWeight: 700,
              fontFamily: "JetBrains Mono, monospace",
              color: "#34d399",
            }}
          >
            WhatsApp: {OM_BRAND.whatsapp}
          </span>
        </div>

        {/* Website */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            backgroundColor: "rgba(56, 189, 248, 0.15)",
            border: "1px solid rgba(56, 189, 248, 0.4)",
            borderRadius: 999,
            padding: "10px 22px",
            boxShadow: "0 0 20px rgba(56, 189, 248, 0.2)",
          }}
        >
          <span style={{ fontSize: 16 }}>🌐</span>
          <span
            style={{
              fontSize: 14,
              fontWeight: 700,
              fontFamily: "JetBrains Mono, monospace",
              color: "#38bdf8",
            }}
          >
            {OM_BRAND.website}
          </span>
        </div>

        {/* Email */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            backgroundColor: "rgba(30, 41, 59, 0.8)",
            border: "1px solid rgba(148, 163, 184, 0.3)",
            borderRadius: 999,
            padding: "10px 22px",
          }}
        >
          <span style={{ fontSize: 16 }}>✉️</span>
          <span
            style={{
              fontSize: 14,
              fontWeight: 600,
              fontFamily: "JetBrains Mono, monospace",
              color: "#e2e8f0",
            }}
          >
            {OM_BRAND.email}
          </span>
        </div>
      </div>

      <SubtitleDisplay
        text="OfficeMitra plus SSDV. Built for Chartered Accountants. Powered by Accounting Intelligence."
        highlightWord="Powered by Accounting Intelligence"
      />
    </div>
  );
};
