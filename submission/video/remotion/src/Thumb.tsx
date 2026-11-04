import React from "react";
import { AbsoluteFill } from "remotion";
import { C, cond, mono, sans, fontCss } from "./theme";
import { Wordmark } from "./lib";

// Safe area: Devpost crops the embed to about 4:3 and YouTube overlays the top 110 px and bottom 130 px.
export const Thumb: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg, color: C.ink, fontFamily: sans, alignItems: "center" }}>
    <style>{fontCss}</style>
    <div style={{ width: 1180, height: 1080, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", paddingTop: 20 }}>
      <Wordmark size={40} />
      <div style={{ font: `700 118px/1.02 ${cond}`, letterSpacing: "-0.01em", marginTop: 44 }}>
        <div>Your agent used a library.</div>
        <div style={{ color: C.red }}>It was poisoned.</div>
        <div>24 hours to file.</div>
      </div>
      <div style={{ font: `500 30px/1.35 ${sans}`, marginTop: 44, maxWidth: 1000 }}>An autonomous EU Cyber Resilience Act agent. Sentinel at commit time, CRA Watch at CVE time, a person at filing time.</div>
      <div style={{ font: `500 22px ${mono}`, letterSpacing: ".1em", textTransform: "uppercase", color: C.green, marginTop: 28 }}>Nebius Token Factory · Nemotron 3 Nano + Ultra · Tavily</div>
    </div>
  </AbsoluteFill>
);
