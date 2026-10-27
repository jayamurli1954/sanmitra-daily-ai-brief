import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

/**
 * Ramesh: owner of a trading business. Flat 2D character drawn in SVG so he
 * looks identical in every frame and every episode. Fully posable:
 * jointed arms (shoulder + elbow), head turn, eye direction, lean, mood,
 * mouth driven by the narration's loudness, and an optional phone in hand.
 */

export type ArmPose = { shoulder: number; elbow: number }; // degrees, 0 = hanging straight down
export type Pose = {
  mood: number; // 0 happy .. 1 worried
  mouth: number; // 0 closed .. 1 wide open
  headTurn: number; // -1 left .. 1 right
  lookX: number; // -1 .. 1
  lookY: number; // -1 .. 1
  lean: number; // degrees
  left: ArmPose; // viewer's left arm
  right: ArmPose;
  phone: number; // 0 hidden .. 1 in right hand
};

export const SKIN = "#c68a5e";
const SKIN_SHADE = "#a96f47";
const HAIR = "#2f2f33";
const HAIR_GREY = "#8c8c92";
const VEST = "#1d3557";
const SHIRT = "#a8d0e6";
const SHIRT_SHADE = "#8fbcd6";
const INK = "#1f2430";

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

const UPPER = 118;
const FORE = 108;

const Arm: React.FC<{ x: number; y: number; pose: ArmPose; mirror: boolean; phone?: number }> = ({ x, y, pose, mirror, phone = 0 }) => {
  const s = mirror ? -1 : 1;
  return (
    <g transform={`translate(${x} ${y}) rotate(${s * pose.shoulder})`}>
      <rect x={-22} y={-10} width={44} height={UPPER + 16} rx={22} fill={SHIRT} />
      <rect x={-22} y={UPPER - 30} width={44} height={14} rx={6} fill={SHIRT_SHADE} opacity={0.6} />
      <g transform={`translate(0 ${UPPER}) rotate(${s * pose.elbow})`}>
        <rect x={-19} y={-8} width={38} height={FORE + 8} rx={19} fill={SHIRT} />
        <rect x={-18} y={FORE - 14} width={36} height={12} rx={5} fill="#ffffff" />
        <g transform={`translate(0 ${FORE + 10})`}>
          <ellipse cx={0} cy={6} rx={21} ry={22} fill={SKIN} />
          <ellipse cx={s * -14} cy={0} rx={8} ry={12} fill={SKIN_SHADE} />
          {phone > 0 && (
            <g opacity={phone} transform={`translate(${s * 4} -36) rotate(${s * -8})`}>
              <rect x={-26} y={-52} width={52} height={92} rx={9} fill="#20232b" />
              <rect x={-21} y={-44} width={42} height={74} rx={5} fill="#e7f3ec" />
              <rect x={-14} y={-30} width={28} height={8} rx={3} fill="#2a9d8f" />
              <rect x={-14} y={-14} width={20} height={6} rx={3} fill="#9aa5ad" />
              <rect x={-14} y={-2} width={24} height={6} rx={3} fill="#d1495b" />
            </g>
          )}
        </g>
      </g>
    </g>
  );
};

export const Ramesh: React.FC<{ pose: Pose; blinkOffset?: number }> = ({ pose, blinkOffset = 0 }) => {
  const frame = useCurrentFrame();
  const cycle = (frame + blinkOffset) % 96;
  const eyeScale = cycle < 4 ? interpolate(cycle, [0, 2, 4], [1, 0.1, 1]) : 1;
  const breathe = Math.sin(frame / 20) * 2.5;
  const { mood, mouth } = pose;

  const turn = pose.headTurn * 14; // features slide to fake a 3D turn
  const browInner = lerp(98, 84, mood);
  const browOuter = lerp(96, 102, mood);
  const lipCtrl = lerp(198, 176, mood);
  const lipEnds = lerp(184, 190, mood);
  const open = Math.max(0, Math.min(1, mouth));

  return (
    <svg viewBox="0 0 420 560" width="100%" height="100%" style={{ overflow: "visible" }}>
      <g transform={`translate(0 ${breathe}) rotate(${pose.lean} 210 520)`}>
        {/* Torso */}
        <path d="M70 560 C70 420 120 360 210 352 C300 360 350 420 350 560 Z" fill={SHIRT} />
        <path d="M70 560 C72 430 110 372 172 356 L196 470 L182 560 Z" fill={VEST} />
        <path d="M350 560 C348 430 310 372 248 356 L224 470 L238 560 Z" fill={VEST} />
        <path d="M172 356 L210 400 L248 356 L232 346 L210 372 L188 346 Z" fill="#ffffff" />
        {[430, 470, 510].map((y) => (
          <circle key={y} cx={198} cy={y} r={4} fill="#e9c46a" />
        ))}
        <rect x={186} y={300} width={48} height={60} rx={14} fill={SKIN_SHADE} />

        <g transform={`translate(0 30) rotate(${pose.headTurn * 4 + mood * 2} 210 260)`}>
          <ellipse cx={128 + turn * 0.5} cy={196} rx={16} ry={24} fill={SKIN_SHADE} />
          <ellipse cx={292 + turn * 0.5} cy={196} rx={16} ry={24} fill={SKIN_SHADE} />
          <ellipse cx={210} cy={190} rx={84} ry={100} fill={SKIN} />
          <path d="M126 168 C124 104 168 80 214 80 C262 80 298 106 294 168 C286 132 266 114 230 112 C200 118 170 116 150 128 C138 138 130 150 126 168 Z" fill={HAIR} />
          <path d="M126 168 C124 186 126 200 130 210 L136 172 Z" fill={HAIR_GREY} />
          <path d="M294 168 C296 186 294 200 290 210 L284 172 Z" fill={HAIR_GREY} />

          <g transform={`translate(${turn} 0)`}>
            <path d={`M154 ${browOuter} Q170 ${browOuter - 8} 188 ${browInner}`} stroke={HAIR} strokeWidth={7} strokeLinecap="round" fill="none" />
            <path d={`M266 ${browOuter} Q250 ${browOuter - 8} 232 ${browInner}`} stroke={HAIR} strokeWidth={7} strokeLinecap="round" fill="none" />
            <g transform={`translate(${pose.lookX * 7} ${pose.lookY * 5 + (126 - 126 * eyeScale)})`}>
              <ellipse cx={172} cy={126} rx={7} ry={9 * eyeScale} fill={INK} />
              <ellipse cx={248} cy={126} rx={7} ry={9 * eyeScale} fill={INK} />
            </g>
            <rect x={146} y={106} width={54} height={42} rx={14} stroke={INK} strokeWidth={5} fill="rgba(255,255,255,0.12)" />
            <rect x={220} y={106} width={54} height={42} rx={14} stroke={INK} strokeWidth={5} fill="rgba(255,255,255,0.12)" />
            <path d="M200 124 Q210 118 220 124" stroke={INK} strokeWidth={5} fill="none" />
            <path d="M210 138 Q218 160 206 166" stroke={SKIN_SHADE} strokeWidth={6} strokeLinecap="round" fill="none" />
            {/* Mouth: opens with the voice; the lip line carries the mood */}
            <ellipse cx={210} cy={188 + open * 6} rx={14 + open * 6} ry={2 + open * 13} fill="#5a2a22" />
            <ellipse cx={210} cy={194 + open * 10} rx={8 + open * 3} ry={open * 5} fill="#c85a54" opacity={open > 0.2 ? 1 : 0} />
            <path d={`M188 ${lipEnds} Q210 ${lipCtrl + open * 8} 232 ${lipEnds}`} stroke="#7a3b2e" strokeWidth={6} strokeLinecap="round" fill="none" />
            <path d="M172 178 Q190 166 210 174 Q230 166 248 178 Q232 186 210 182 Q188 186 172 178 Z" fill={HAIR} />
            <circle cx={156} cy={176} r={13} fill="#e07a5f" opacity={0.25 * (1 - mood)} />
            <circle cx={264} cy={176} r={13} fill="#e07a5f" opacity={0.25 * (1 - mood)} />
          </g>
          <path
            d="M300 120 Q312 140 300 150 Q288 140 300 120 Z"
            fill="#7fc8f8"
            opacity={interpolate(mood, [0.5, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
            transform={`translate(0 ${(frame % 40) * 0.6 * mood})`}
          />
        </g>

        {/* Arms last, so a hand can rise in front of the face */}
        <Arm x={118} y={400} pose={pose.left} mirror={false} />
        <Arm x={302} y={400} pose={pose.right} mirror={true} phone={pose.phone} />
      </g>
    </svg>
  );
};

// ------------------------------------------------------------------ pose timeline

const ease = (t: number) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);

/** Interpolate a pose between keyframes [frame, partial pose], holding the last values. */
export const poseAt = (frame: number, keys: [number, Partial<Pose>][], base: Pose): Pose => {
  const resolved: [number, Pose][] = [];
  let cur = base;
  for (const [f, p] of keys) {
    cur = {
      ...cur,
      ...p,
      left: { ...cur.left, ...(p.left || {}) },
      right: { ...cur.right, ...(p.right || {}) },
    };
    resolved.push([f, cur]);
  }
  if (frame <= resolved[0][0]) return resolved[0][1];
  for (let i = 0; i < resolved.length - 1; i++) {
    const [f0, a] = resolved[i];
    const [f1, b] = resolved[i + 1];
    if (frame <= f1) {
      const t = ease((frame - f0) / Math.max(1, f1 - f0));
      const mix = (x: number, y: number) => lerp(x, y, t);
      return {
        mood: mix(a.mood, b.mood),
        mouth: mix(a.mouth, b.mouth),
        headTurn: mix(a.headTurn, b.headTurn),
        lookX: mix(a.lookX, b.lookX),
        lookY: mix(a.lookY, b.lookY),
        lean: mix(a.lean, b.lean),
        phone: mix(a.phone, b.phone),
        left: { shoulder: mix(a.left.shoulder, b.left.shoulder), elbow: mix(a.left.elbow, b.left.elbow) },
        right: { shoulder: mix(a.right.shoulder, b.right.shoulder), elbow: mix(a.right.elbow, b.right.elbow) },
      };
    }
  }
  return resolved[resolved.length - 1][1];
};
