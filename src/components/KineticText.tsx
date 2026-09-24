import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

interface KineticTextProps {
  children: React.ReactNode;
  delay?: number;
  exitFrame?: number;
  className?: string;
  damping?: number;
  stiffness?: number;
  mass?: number;
  initialY?: number;
  initialScale?: number;
}

export const KineticText: React.FC<KineticTextProps> = ({
  children,
  delay = 0,
  exitFrame,
  className = "",
  damping = 14,
  stiffness = 110,
  mass = 0.8,
  initialY = 35,
  initialScale = 0.88,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Smooth Entrance Spring
  const entrance = spring({
    frame: frame - delay,
    fps,
    config: {
      damping,
      stiffness,
      mass,
    },
  });

  // Smooth Exit Spring (if configured)
  const exit =
    exitFrame !== undefined
      ? spring({
          frame: frame - exitFrame,
          fps,
          config: {
            damping: 14,
            stiffness: 120,
            mass: 0.8,
          },
        })
      : 0;

  const opacity =
    interpolate(entrance, [0, 1], [0, 1]) *
    (exitFrame !== undefined ? interpolate(exit, [0, 1], [1, 0]) : 1);

  const scale =
    interpolate(entrance, [0, 1], [initialScale, 1]) *
    (exitFrame !== undefined ? interpolate(exit, [0, 1], [1, 0.92]) : 1);

  const translateY =
    interpolate(entrance, [0, 1], [initialY, 0]) +
    (exitFrame !== undefined ? interpolate(exit, [0, 1], [0, -30]) : 0);

  if (frame < delay) {
    return null;
  }

  return (
    <div
      className={className}
      style={{
        opacity: Math.max(0, Math.min(1, opacity)),
        transform: `translateY(${translateY}px) scale(${scale})`,
        willChange: "transform, opacity",
      }}
    >
      {children}
    </div>
  );
};
