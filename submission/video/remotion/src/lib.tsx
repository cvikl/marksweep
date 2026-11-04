import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, cond, mono, sans } from "./theme";

export const useT = () => { const f = useCurrentFrame(); const { fps } = useVideoConfig(); return f / fps; };
export const ease = Easing.bezier(0.33, 0.0, 0.2, 1);
/** 0→1 over [a, a+d] seconds, eased */
export const ramp = (t: number, a: number, d = 0.5) => interpolate(t, [a, a + Math.max(d, 0.001)], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });

export type Rect = [number, number, number, number];
export type Key = { t: number; rect: Rect; hl?: Rect | null; pad?: number; max?: number };

const fit = (k: Key) => {
  const pad = k.pad ?? 60, [x, y, w, h] = k.rect;
  const s = Math.min(1920 / (w + pad * 2), 1080 / (h + pad * 2), k.max ?? 1.9);
  return { s, cx: x + w / 2, cy: y + h / 2 };
};
const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
const lerpRect = (a: Rect, b: Rect, p: number): Rect => [lerp(a[0], b[0], p), lerp(a[1], b[1], p), lerp(a[2], b[2], p), lerp(a[3], b[3], p)];

/** A full-page screenshot with a camera moving between keyframes and a spotlight on the narrated element. */
export const PageShot: React.FC<{ src: string; keys: Key[]; move?: number; children?: React.ReactNode }> = ({ src, keys, move = 0.9, children }) => {
  const t = useT();
  let i = 0; while (i + 1 < keys.length && t >= keys[i + 1].t) i++;
  const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)];
  // transition: from key i-1 to key i over `move` seconds starting at keys[i].t
  const prev = keys[Math.max(i - 1, 0)];
  const q = i === 0 ? 1 : ramp(t, a.t, move);
  const fa = fit(prev), fb = fit(a);
  const s = lerp(fa.s, fb.s, q), cx = lerp(fa.cx, fb.cx, q), cy = lerp(fa.cy, fb.cy, q);
  const hlPrev = prev.hl ?? null, hlNow = a.hl ?? null;
  const hlRect = hlPrev && hlNow ? lerpRect(hlPrev, hlNow, q) : hlNow ?? hlPrev;
  const hlOpacity = hlPrev && hlNow ? 1 : hlNow ? q : hlPrev ? 1 - q : 0;
  void b;
  return (
    <AbsoluteFill style={{ background: C.bg, overflow: "hidden" }}>
      <div style={{ position: "absolute", left: 0, top: 0, transformOrigin: "0 0", transform: `translate(${960 - cx * s}px, ${540 - cy * s}px) scale(${s})` }}>
        <Img src={staticFile(src)} style={{ display: "block", width: 1905 }} />
        {hlRect && (
          <div style={{ position: "absolute", left: hlRect[0] - 14, top: hlRect[1] - 10, width: hlRect[2] + 28, height: hlRect[3] + 20, borderRadius: 10, boxShadow: `0 0 0 9999px rgba(19,26,35,${0.42 * hlOpacity})`, outline: `${3 / s}px solid ${C.red}`, outlineOffset: 0, opacity: 1, transition: "none" }} />
        )}
      </div>
      {children}
    </AbsoluteFill>
  );
};

/** Bottom caption pill, shown between from and to (seconds). */
export const Caption: React.FC<{ from: number; to: number; text: string; kicker?: string }> = ({ from, to, text, kicker }) => {
  const t = useT();
  if (t < from || t > to) return null;
  const o = Math.min(ramp(t, from, 0.35), 1 - ramp(t, to - 0.35, 0.35));
  const y = (1 - ramp(t, from, 0.45)) * 18;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 64, display: "flex", justifyContent: "center", opacity: o, transform: `translateY(${y}px)` }}>
      <div style={{ background: C.ink, color: "#fff", borderRadius: 12, padding: "16px 26px", font: `500 26px/1.3 ${sans}`, boxShadow: "0 18px 40px rgba(19,26,35,.25)", display: "flex", alignItems: "center", gap: 18, maxWidth: 1300 }}>
        {kicker && <span style={{ font: `500 16px ${mono}`, letterSpacing: ".12em", textTransform: "uppercase", color: "#F2C265" }}>{kicker}</span>}
        <span>{text}</span>
      </div>
    </div>
  );
};

export const Wordmark: React.FC<{ size?: number; color?: string }> = ({ size = 30, color = C.ink }) => (
  <div style={{ display: "flex", alignItems: "baseline", gap: size * 0.45, color }}>
    <span style={{ font: `700 ${size}px ${cond}`, letterSpacing: "-0.01em" }}>Marksweep</span>
    <span style={{ font: `500 ${size * 0.45}px ${mono}`, letterSpacing: ".12em", textTransform: "uppercase", color: C.mute }}>field enforcement</span>
  </div>
);

/** Fades a scene in and out at its edges. */
export const Fade: React.FC<{ dur: number; children: React.ReactNode }> = ({ dur, children }) => {
  const t = useT();
  const o = Math.min(ramp(t, 0, 0.4), 1 - ramp(t, dur - 0.4, 0.4));
  return <AbsoluteFill style={{ opacity: o, background: C.bg }}>{children}</AbsoluteFill>;
};

/** Text that rises in at `at` seconds. */
export const Rise: React.FC<{ at: number; children: React.ReactNode; style?: React.CSSProperties; d?: number }> = ({ at, children, style, d = 0.6 }) => {
  const t = useT(); const p = ramp(t, at, d);
  return <div style={{ opacity: p, transform: `translateY(${(1 - p) * 26}px)`, ...style }}>{children}</div>;
};
