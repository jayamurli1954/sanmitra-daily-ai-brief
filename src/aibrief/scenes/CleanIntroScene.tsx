import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

/**
 * Clean opening: the lead story's picture full screen, darkened, with the date
 * and the day's headlines appearing one by one as the anchor reads them.
 */

const FONT =
  "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";

export const CleanIntroScene: React.FC<{
  formattedDate: string;
  headlines: string[];
  leadImage?: string;
}> = ({ formattedDate, headlines, leadImage }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();
  const list = headlines.slice(0, 10);

  // "From the SanMitra Newsroom ... First, today's top headlines:" takes about
  // six seconds; the headlines then share the rest, ending ~3 s before the cut.
  const start = 6 * fps;
  const span = Math.max(durationInFrames - start - 3 * fps, list.length * fps);
  const step = span / Math.max(list.length, 1);

  const titleIn = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#05080f", fontFamily: FONT }}>
      {leadImage && (
        <Img
          src={staticFile(leadImage)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${interpolate(frame, [0, durationInFrames], [1.0, 1.08])})`,
          }}
        />
      )}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(90deg, rgba(4,10,22,0.94) 0%, rgba(4,10,22,0.86) 55%, rgba(4,10,22,0.55) 100%)",
        }}
      />

      {/* Logo chip, top right (same as the stories) */}
      <div
        style={{
          position: "absolute",
          top: 40,
          right: 48,
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "10px 18px 10px 12px",
          borderRadius: 10,
          backgroundColor: "rgba(8, 20, 40, 0.82)",
        }}
      >
        <Img src={staticFile("aibrief/brand/sanmitra_mark.png")} style={{ width: 40, height: 40 }} />
        <div style={{ lineHeight: 1.05 }}>
          <div style={{ color: "#ffffff", fontSize: 20, fontWeight: 800, letterSpacing: 1.5 }}>SANMITRA</div>
          <div style={{ color: "#9cc3ff", fontSize: 14, fontWeight: 700, letterSpacing: 2 }}>AI NEWS</div>
        </div>
      </div>

      <div style={{ position: "absolute", left: 110, top: 110, right: 420, opacity: titleIn }}>
        <div style={{ color: "#9cc3ff", fontSize: 26, fontWeight: 700, letterSpacing: 3 }}>
          DAILY AI BRIEF · {formattedDate.toUpperCase()}
        </div>
        <div style={{ color: "#ffffff", fontSize: 72, fontWeight: 800, marginTop: 10 }}>
          Today's headlines
        </div>
        <div style={{ width: 120, height: 6, backgroundColor: "#3b82f6", borderRadius: 3, marginTop: 18 }} />
      </div>

      <div style={{ position: "absolute", left: 110, top: 330, right: 300 }}>
        {list.map((h, i) => {
          const at = start + i * step;
          const o = interpolate(frame, [at, at + 12], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          return (
            <div
              key={i}
              style={{
                display: "flex",
                gap: 20,
                alignItems: "baseline",
                marginBottom: 16,
                opacity: o,
                transform: `translateX(${(1 - o) * -20}px)`,
              }}
            >
              <div style={{ color: "#3b82f6", fontSize: 30, fontWeight: 800, minWidth: 44 }}>
                {String(i + 1).padStart(2, "0")}
              </div>
              <div
                style={{
                  color: "#ffffff",
                  fontSize: 34,
                  fontWeight: 600,
                  lineHeight: 1.2,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {h}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
