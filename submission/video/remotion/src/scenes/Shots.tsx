import React from "react";
import { C } from "../theme";
import { Caption, PageShot, Rect } from "../lib";
import formR from "../../public/rects-form.json";
import logR from "../../public/rects-log.json";
import recR from "../../public/rects-record.json";
import ctlR from "../../public/rects-control.json";

type RJ = Record<string, number[]>;
const r = (j: RJ, k: string, fallback: Rect = [0, 0, 1900, 1000]): Rect => (j[k] ? (j[k] as Rect) : fallback);
const F = formR as RJ, L = logR as RJ, R = recR as RJ, K = ctlR as RJ;
const page = (j: RJ): Rect => [0, 0, (j.__page?.[0] ?? 1905), Math.min(j.__page?.[1] ?? 1080, 1080)];

/** Block 2 (10.8 s): the upload form, client, notes, run. */
export const Upload: React.FC = () => (
  <PageShot src="form.png" keys={[
    { t: 0, rect: page(F), hl: null, max: 1.0 },
    { t: 1.6, rect: r(F, "form"), hl: r(F, "demos"), max: 1.25 },
    { t: 4.2, rect: r(F, "form"), hl: r(F, "marks"), max: 1.25 },
    { t: 6.6, rect: r(F, "form"), hl: r(F, "notes"), max: 1.25 },
    { t: 9.0, rect: r(F, "run"), hl: r(F, "run"), max: 1.6, pad: 160 },
  ]}>
    <Caption from={1.9} to={4.0} text="A field photo: shop window, stall or listing" />
    <Caption from={4.5} to={6.4} text="The client's registered marks, with office numbers" />
    <Caption from={6.9} to={8.8} text="Goods seen, jurisdiction, two lines of notes" />
  </PageShot>
);

/** Block 3 (18.8 s): the run log while the model finds the marks. */
export const Segment: React.FC = () => (
  <PageShot src="log.png" keys={[
    { t: 0, rect: r(L, "log"), hl: null, max: 1.5, pad: 80 },
    { t: 6.0, rect: r(L, "log"), hl: r(L, "log"), max: 1.5, pad: 80 },
  ]}>
    <Caption from={0.6} to={5.6} kicker="SAM 3.1" text='"brand logo" · "printed brand name" · "repeating pattern on a bag"' />
    <Caption from={6.4} to={12.0} text="Every answer is a box and a lossless mask; merged, cut from the original, hashed" />
    <Caption from={12.6} to={18.2} text="No person decided what to look at" />
  </PageShot>
);

/** Block 4 (23.5 s): one element's six questions. */
export const Assess: React.FC = () => (
  <PageShot src="record.png" keys={[
    { t: 0, rect: r(R, "element-1"), hl: null, max: 1.3, pad: 60 },
    { t: 5.4, rect: r(R, "element-1"), hl: r(R, "element-1"), max: 1.3, pad: 60 },
    { t: 11.0, rect: r(R, "breakdown-1"), hl: r(R, "breakdown-1"), max: 1.5, pad: 60 },
  ]}>
    <Caption from={0.5} to={5.0} kicker="Muse Spark 1.3" text="each crop next to the register drawings of the client's marks" />
    <Caption from={5.8} to={10.6} text="What it sees, the text it reads, the candidate registrations" />
    <Caption from={11.6} to={17.5} text="Visual · aural · conceptual · goods · distinctiveness · imitation signals" />
    <Caption from={18.0} to={23.0} text="The same six questions a court asks" />
  </PageShot>
);

/** Block 5 (21.7 s): the record page. */
export const Record: React.FC = () => (
  <PageShot src="record.png" keys={[
    { t: 0, rect: r(R, "headline"), hl: null, max: 1.2, pad: 80 },
    { t: 2.2, rect: r(R, "photo"), hl: r(R, "photo"), max: 1.2, pad: 40 },
    { t: 8.0, rect: r(R, "element-2", r(R, "element-1")), hl: r(R, "element-2", r(R, "element-1")), max: 1.3, pad: 60 },
    { t: 13.0, rect: r(R, "recordcard"), hl: r(R, "recordcard"), max: 1.4, pad: 60 },
  ]}>
    <Caption from={2.6} to={7.6} text="Red highly concerning · amber worth checking · green low concern" />
    <Caption from={8.4} to={12.6} text="Crop, score, rationales, candidate marks" />
    <Caption from={13.4} to={17.4} text="Click a mark: the office record on USPTO, EUIPO or WIPO" />
    <Caption from={17.8} to={21.4} text="Research signals for the lawyer. Never a verdict." />
  </PageShot>
);

/** Block 6 (11.9 s): the control sweep, nothing matches. */
export const Control: React.FC = () => (
  <PageShot src="control.png" keys={[
    { t: 0, rect: r(K, "photo"), hl: null, max: 1.2, pad: 40 },
    { t: 4.0, rect: r(K, "element-1"), hl: r(K, "element-1"), max: 1.3, pad: 60 },
  ]}>
    <Caption from={0.5} to={3.6} text="Another house's monogram, same client" />
    <Caption from={4.4} to={11.5} text="No candidate mark: every score capped at 25, and it says so" />
  </PageShot>
);

/** Block 7 (19.1 s): the ledger. */
export const Ledger: React.FC = () => (
  <PageShot src="record.png" keys={[
    { t: 0, rect: r(R, "ledger"), hl: null, max: 1.4, pad: 60 },
    { t: 3.0, rect: r(R, "ledger"), hl: r(R, "ledger"), max: 1.4, pad: 60 },
  ]}>
    <Caption from={0.5} to={6.5} text="Every model call: model id, purpose, latency, tokens" />
    <Caption from={7.0} to={12.5} kicker="Meta Model API" text="4 photos · 34 calls · 3 min 33 s end to end" />
    <Caption from={13.0} to={18.8} kicker="Muse Glimmer 30B" text="open weights on a laptop CPU, by configuration" />
  </PageShot>
);
