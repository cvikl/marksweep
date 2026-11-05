import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { C, cond, mono, sans } from "../theme";
import { Rise, Wordmark, useT, ramp } from "../lib";

type P = { name: string; img: string; role: string; facts: string[]; at: number };
const people: P[] = [
  { name: "Timotej Cvikl", img: "timotej.jpg", role: "Co-founder, technical lead · built Marksweep", at: 4.6, facts: [
    "Co-founded his first software company at 19; 10+ industrial clients",
    "Accelerate Cambridge, Cambridge Judge Business School",
    "Winner, Luminance challenge, Hack the Law 2026 · winner, AIxPravo 2026",
    "Computer science, AI track, University of Ljubljana" ] },
  { name: "Bernard Liu", img: "bernard.jpg", role: "Co-founder, legal and regulatory lead", at: 9.4, facts: [
    "PhD researcher, University of Cambridge: technology governance and IP",
    "First place overall and White & Case challenge, Hack the Law 2026",
    "IP practice in Hong Kong; LSE, UCL, Cambridge, Oxford",
    "Formerly AWS solutions architecture" ] },
];

/** Block 8: where it sits, who built it, where to find it. */
export const End: React.FC = () => {
  const t = useT();
  return (
    <AbsoluteFill style={{ background: C.bg, color: C.ink, fontFamily: sans }}>
      <div style={{ position: "absolute", left: 120, top: 70 }}><Wordmark size={34} /></div>
      <Rise at={0.2} style={{ position: "absolute", left: 120, top: 150, font: `700 56px/1.1 ${cond}` }}>The field-intake module of <span style={{ color: C.navy }}>Signum</span>.</Rise>
      <div style={{ position: "absolute", left: 120, right: 120, top: 250, display: "flex", gap: 48 }}>
        {people.map((p) => (
          <Rise key={p.name} at={p.at} style={{ flex: 1, display: "flex", gap: 26, alignItems: "flex-start" }}>
            <div style={{ width: 210, height: 262, borderRadius: 8, overflow: "hidden", flex: "none", boxShadow: "0 18px 40px -20px rgba(28,27,24,.5)" }}>
              <Img src={staticFile(p.img)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            </div>
            <div>
              <div style={{ font: `700 40px/1.05 ${cond}` }}>{p.name}</div>
              <div style={{ font: `500 19px/1.3 ${sans}`, color: C.navy, margin: "8px 0 14px" }}>{p.role}</div>
              {p.facts.map((f, i) => (
                <div key={f} style={{ font: `400 20px/1.35 ${sans}`, color: C.mute, padding: "6px 0", borderTop: i ? `1px solid ${C.line}` : "none", opacity: ramp(t, p.at + 0.6 + i * 0.35, 0.4) }}>{f}</div>
              ))}
            </div>
          </Rise>
        ))}
      </div>
      <Rise at={16.4} style={{ position: "absolute", left: 120, right: 120, bottom: 70 }}>
        <div style={{ height: 2, background: C.line, marginBottom: 22 }} />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 40 }}>
          <div style={{ font: `500 22px/1.4 ${sans}`, maxWidth: 1100 }}><span style={{ font: `500 16px ${mono}`, letterSpacing: ".12em", textTransform: "uppercase", color: C.mute, display: "block", marginBottom: 6 }}>Meta Global AI Developer Hackathon · 4 Nov 2026</span>SAM 3.1 and Muse Spark 1.3 on the Meta Model API; Muse Glimmer 30B open weights on a laptop, by configuration. Code, record and film built during the hackathon.</div>
          <div style={{ textAlign: "right", font: `500 26px/1.5 ${mono}`, color: C.navy, whiteSpace: "nowrap" }}>meta.vantapointlabs.com<br />github.com/cvikl/marksweep</div>
        </div>
      </Rise>
    </AbsoluteFill>
  );
};
