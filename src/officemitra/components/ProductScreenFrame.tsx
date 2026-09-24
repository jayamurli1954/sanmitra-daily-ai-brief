import React from "react";
import { Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

interface ProductScreenFrameProps {
  imageSrc: string;
  title?: string;
  badge?: string;
  tiltAngle?: number;
  scale?: number;
  width?: number | string;
  height?: number | string;
  glowColor?: string;
}

export const ProductScreenFrame: React.FC<ProductScreenFrameProps> = ({
  imageSrc,
  title = "OfficeMitra Desktop MIS",
  badge = "Posted Books Reconciled",
  tiltAngle = 4,
  scale = 1.0,
  width = 1100,
  height = 620,
  glowColor = "rgba(56, 189, 248, 0.25)",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 16, stiffness: 90 },
  });

  const opacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  const translateY = interpolate(entrance, [0, 1], [40, 0]);
  const subtleFloat = Math.sin(frame / 25) * 4;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        perspective: 1400,
        opacity,
        transform: `translateY(${translateY + subtleFloat}px) scale(${scale})`,
      }}
    >
      <div
        style={{
          width,
          height,
          transform: `rotateX(${tiltAngle}deg) rotateY(-${tiltAngle * 0.5}deg)`,
          borderRadius: 16,
          overflow: "hidden",
          backgroundColor: "#0f172a",
          border: "1px solid rgba(148, 163, 184, 0.25)",
          boxShadow: `
            0 25px 50px -12px rgba(0, 0, 0, 0.75),
            0 0 40px -5px ${glowColor}
          `,
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Top Window Chrome */}
        <div
          style={{
            height: 38,
            backgroundColor: "#1e293b",
            borderBottom: "1px solid rgba(148, 163, 184, 0.18)",
            display: "flex",
            alignItems: "center",
            padding: "0 16px",
            justifyContent: "space-between",
          }}
        >
          {/* Window dots */}
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <div style={{ width: 11, height: 11, borderRadius: "50%", backgroundColor: "#ef4444" }} />
            <div style={{ width: 11, height: 11, borderRadius: "50%", backgroundColor: "#f59e0b" }} />
            <div style={{ width: 11, height: 11, borderRadius: "50%", backgroundColor: "#10b981" }} />
            <span
              style={{
                marginLeft: 14,
                fontSize: 13,
                fontFamily: "Inter, sans-serif",
                color: "#94a3b8",
                fontWeight: 500,
              }}
            >
              {title}
            </span>
          </div>

          {/* Active status pill */}
          <div
            style={{
              backgroundColor: "rgba(16, 185, 129, 0.15)",
              border: "1px solid rgba(16, 185, 129, 0.35)",
              borderRadius: 20,
              padding: "2px 10px",
              display: "flex",
              alignItems: "center",
              gap: 6,
            }}
          >
            <div
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                backgroundColor: "#10b981",
                boxShadow: "0 0 8px #10b981",
              }}
            />
            <span
              style={{
                fontSize: 11,
                fontFamily: "Inter, sans-serif",
                color: "#34d399",
                fontWeight: 600,
                letterSpacing: "0.03em",
              }}
            >
              {badge}
            </span>
          </div>
        </div>

        {/* Screenshot Viewport */}
        <div
          style={{
            flex: 1,
            position: "relative",
            backgroundColor: "#090d16",
            overflow: "hidden",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Img
            src={imageSrc}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              objectPosition: "top center",
            }}
          />

          {/* Subtle glass reflection highlight */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              height: "40%",
              background: "linear-gradient(180deg, rgba(255, 255, 255, 0.05) 0%, transparent 100%)",
              pointerEvents: "none",
            }}
          />
        </div>
      </div>
    </div>
  );
};
