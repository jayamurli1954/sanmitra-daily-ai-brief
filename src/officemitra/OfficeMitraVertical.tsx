import React from "react";
import { Img, staticFile } from "remotion";
import { OfficeMitraVideo } from "./OfficeMitraVideo";
import { OM_BRAND } from "./types";

export const OfficeMitraVertical: React.FC = () => {
  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        backgroundColor: "#070b16",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "space-between",
        position: "relative",
        padding: "60px 0",
      }}
    >
      {/* Top Header Bar for Mobile Feed */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 12,
          zIndex: 30,
        }}
      >
        <Img
          src={staticFile("officemitra/officemitra-logo-banner.png")}
          style={{ height: 60, objectFit: "contain" }}
        />
        <span
          style={{
            fontSize: 16,
            fontWeight: 700,
            fontFamily: "Inter, sans-serif",
            color: "#38bdf8",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            backgroundColor: "rgba(56, 189, 248, 0.15)",
            padding: "4px 16px",
            borderRadius: 20,
            border: "1px solid rgba(56, 189, 248, 0.3)",
          }}
        >
          {OM_BRAND.taglinePrimary}
        </span>
      </div>

      {/* Centered Main Video Player (16:9 widescreen in center) */}
      <div
        style={{
          width: 1080,
          height: 607.5,
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderTop: "2px solid rgba(56, 189, 248, 0.3)",
          borderBottom: "2px solid rgba(56, 189, 248, 0.3)",
          boxShadow: "0 0 50px rgba(0, 0, 0, 0.9)",
          backgroundColor: "#000000",
        }}
      >
        <div
          style={{
            width: 1920,
            height: 1080,
            transform: "scale(0.5625)",
            transformOrigin: "center center",
          }}
        >
          <OfficeMitraVideo />
        </div>
      </div>

      {/* Bottom CTA for Mobile Feed */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 16,
          zIndex: 30,
        }}
      >
        <div
          style={{
            display: "flex",
            gap: 16,
            alignItems: "center",
            backgroundColor: "rgba(16, 185, 129, 0.15)",
            border: "1px solid rgba(16, 185, 129, 0.4)",
            borderRadius: 999,
            padding: "12px 28px",
          }}
        >
          <span style={{ fontSize: 20 }}>💬</span>
          <span
            style={{
              fontSize: 18,
              fontWeight: 700,
              fontFamily: "JetBrains Mono, monospace",
              color: "#34d399",
            }}
          >
            WhatsApp: {OM_BRAND.whatsapp}
          </span>
        </div>

        <span
          style={{
            fontSize: 16,
            fontWeight: 600,
            fontFamily: "Inter, sans-serif",
            color: "#94a3b8",
          }}
        >
          {OM_BRAND.website} • {OM_BRAND.email}
        </span>
      </div>
    </div>
  );
};
