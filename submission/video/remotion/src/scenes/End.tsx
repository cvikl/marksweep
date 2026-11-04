import React from "react";
import { AbsoluteFill } from "remotion";
import { C, cond, mono, sans } from "../theme";
import { Rise, Wordmark, useT, ramp } from "../lib";

/** Block 8 (17.7 s): where it sits, what was built, where to find it. */
export const End: React.FC = () => {
  const t = useT();
  return (
    <AbsoluteFill style={{ background: C.bg, color: C.ink, fontFamily: sans }}>
      <div style={{ position: "absolute", left: 120, top: 70 }}><Wordmark size={34} /></div>
      <div style={{ position: "absolute", left: 120, top: 230, right: 120 }}>
        <Rise at={0.2} style={{ font: `700 84px/1.12 ${cond}` }}>The field-intake module of <span style={{ color: C.navy }}>Signum</span>.</Rise>
        <Rise at={2.6} style={{ font: `500 36px/1.35 ${sans}`, color: C.mute, marginTop: 24, maxWidth: 1400 }}>Signum assesses one accused product; Marksweep starts one step earlier, at the stall, with the same six questions and the same rule: the lawyer decides.</Rise>
        <Rise at={7.0} style={{ display: "flex", gap: 24, marginTop: 56 }}>
          {["Vision pipeline and crops", "Assessment schema and roll-up", "Evidence record and ledger", "Web app, deploy, this film"].map((x) => (
            <div key={x} style={{ flex: 1, border: `2px solid ${C.line}`, borderRadius: 12, padding: "20px 24px", font: `500 24px/1.3 ${sans}`, background: C.paper }}><div style={{ font: `500 14px ${mono}`, letterSpacing: ".12em", textTransform: "uppercase", color: C.green, marginBottom: 8 }}>built 4 Nov 2026</div>{x}</div>
          ))}
        </Rise>
      </div>
      <Rise at={11.5} style={{ position: "absolute", left: 120, right: 120, bottom: 110 }}>
        <div style={{ height: 2, background: C.line, marginBottom: 32 }} />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <div>
            <div style={{ font: `500 18px ${mono}`, letterSpacing: ".12em", textTransform: "uppercase", color: C.mute }}>Meta Global AI Developer Hackathon</div>
            <div style={{ font: `500 30px/1.3 ${sans}`, marginTop: 8 }}>SAM 3.1 and Muse Spark 1.3 on the Meta Model API · Muse Glimmer 30B open weights on a laptop by configuration</div>
          </div>
          <div style={{ textAlign: "right", font: `500 26px/1.5 ${mono}`, color: C.navy, opacity: ramp(t, 13.5, 0.5) }}>meta.vantapointlabs.com<br />github.com/cvikl/marksweep</div>
        </div>
      </Rise>
    </AbsoluteFill>
  );
};
