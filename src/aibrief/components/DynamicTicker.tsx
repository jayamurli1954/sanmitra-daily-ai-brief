import React from "react";
import { useCurrentFrame } from "remotion";

interface DynamicTickerProps {
  items?: string[];
}

const DEFAULT_TICKER_ITEMS = [
  "AI Governance",
  "AI Infrastructure",
  "Foundation Models",
  "Semiconductors",
  "Cloud Expansion",
  "DeepSeek UNSC Briefing Scheduled",
  "Claude Opus 5.5 & GPT-6 Sol Enterprise Rollout",
  "Alibaba Unveils Zhenwu V900 AI Accelerator",
  "Maharashtra Forms AI Governance Panel",
];

export const DynamicTicker: React.FC<DynamicTickerProps> = ({ items }) => {
  const frame = useCurrentFrame();

  const tickerList = items && items.length > 0 ? items : DEFAULT_TICKER_ITEMS;

  // Smooth continuous scroll (2.2 pixels per frame at 30fps)
  const tickerString = tickerList.join("   ■   ");
  const speed = 2.2;
  const loopWidth = tickerString.length * 15;
  const offset = (frame * speed) % Math.max(loopWidth, 2400);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        width: 1920,
        height: 60,
        backgroundColor: "#030712",
        borderTop: "2px solid #dc2626",
        display: "flex",
        alignItems: "center",
        zIndex: 50,
        overflow: "hidden",
        boxShadow: "0 -4px 20px rgba(0, 0, 0, 0.7)",
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      {/* Fixed Left Tag */}
      <div
        style={{
          height: "100%",
          backgroundColor: "#dc2626",
          color: "#ffffff",
          display: "flex",
          alignItems: "center",
          padding: "0 28px",
          fontWeight: 900,
          fontSize: 14,
          letterSpacing: 2,
          zIndex: 10,
          boxShadow: "6px 0 16px rgba(0,0,0,0.6)",
          flexShrink: 0,
        }}
      >
        SANMITRA WIRE
      </div>

      {/* Marquee Content */}
      <div
        style={{
          display: "flex",
          whiteSpace: "nowrap",
          transform: `translateX(-${offset}px)`,
          willChange: "transform",
        }}
      >
        <span
          style={{
            color: "#f1f5f9",
            fontSize: 15,
            fontWeight: 700,
            letterSpacing: 1.2,
            paddingLeft: 40,
          }}
        >
          {tickerString} &nbsp;&nbsp;&nbsp;■&nbsp;&nbsp;&nbsp; {tickerString}
        </span>
      </div>
    </div>
  );
};
