import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { C, cond, mono, sans } from "../theme";
import { Rise, Wordmark, useT, ramp } from "../lib";

const Big: React.FC<{ at: number; children: React.ReactNode; color?: string }> = ({ at, children, color = C.ink }) => (
  <Rise at={at}><div style={{ font: `700 88px/1.05 ${cond}`, color, letterSpacing: "-0.01em" }}>{children}</div></Rise>
);

/** Block 1 (20.5 s): the problem, then the one-line promise. */
export const Title: React.FC = () => {
  const t = useT();
  const act1 = 1 - ramp(t, 14.6, 0.5);
  const act2 = ramp(t, 15.0, 0.5);
  return (
    <AbsoluteFill style={{ background: C.bg, color: C.ink, fontFamily: sans }}>
      <div style={{ position: "absolute", left: 120, top: 70 }}><Wordmark size={34} /></div>
      <div style={{ position: "absolute", right: 120, top: 76, font: `500 18px ${mono}`, letterSpacing: ".12em", textTransform: "uppercase", color: C.mute }}>Trademark enforcement · from the field photo</div>

      <div style={{ position: "absolute", left: 120, top: 230, right: 120, opacity: act1 }}>
        <Big at={0.2}>Copies are sold at the stall,</Big>
        <Big at={1.6}>not in court.</Big>
        <Rise at={4.6} style={{ marginTop: 50, display: "flex", gap: 40, alignItems: "stretch" }}>
          <div style={{ width: 6, background: C.red, borderRadius: 3 }} />
          <div style={{ font: `500 38px/1.3 ${sans}`, maxWidth: 1250 }}>
            An investigator photographs markets, windows, shelves.<br />
            <span style={{ opacity: ramp(t, 7.4, 0.5) }}>Then someone sorts hundreds of photos by hand.</span><br />
            <span style={{ opacity: ramp(t, 10.6, 0.5), color: C.red }}>Nothing records which mark was compared with which, or why.</span>
          </div>
        </Rise>
        <div style={{ position: "absolute", right: 0, top: 0, width: 520, height: 390, borderRadius: 12, overflow: "hidden", boxShadow: "0 24px 60px rgba(28,27,24,.18)", opacity: ramp(t, 4.6, 0.8), transform: `rotate(${2 - ramp(t, 4.6, 0.8) * 2}deg)` }}>
          <Img src={staticFile("demo-lego-shop.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </div>
      </div>

      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", opacity: act2 }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ font: `700 150px/1 ${cond}`, letterSpacing: "-0.02em" }}>Marksweep</div>
          <div style={{ font: `500 40px/1.3 ${sans}`, marginTop: 26, color: C.mute }}>a photo from the field in, <span style={{ color: C.ink }}>a trademark evidence record out</span></div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
