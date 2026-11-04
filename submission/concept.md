# Marksweep concept

Vanta Point Labs, 4 November 2026. Meta Global AI Developer Hackathon, Startups track, theme Build for Your World.

## The problem

Brand owners lose the fight against copies at the point of sale, not in court. An investigator walks a market or a shop street, photographs stalls and shelves, and a paralegal later sorts hundreds of photos by hand: which logo is on which bag, which of the client's registered marks it resembles, and whether the evidence is good enough for a complaint, a raid request or a takedown notice.

That sorting is slow, inconsistent and undocumented. Today the photo is the evidence and the lawyer's memory is the method. Nothing records which mark was compared with which, on what basis, or when. Hong Kong IP firms doing this work for luxury and toy brands, the kind of matter Signum already assesses from a single uploaded image, have no tool that starts from the field photo itself.

## What Marksweep does

A photo from the stall goes in, a hashed evidence record comes out, in about a minute.

1. **Segment.** The vision model is asked for "brand logo", "printed brand name" and "repeating pattern on a bag" and returns a box for every candidate. The boxes are merged and cut from the original photo. No person chooses what to look at: the model finds everything that looks like a mark.
2. **Assess.** The model then sees each crop next to the official register drawings of the client's marks and returns schema-checked JSON: what it sees, the text it reads, which client marks are candidates, six sub-scores with one-sentence rationales, a short narrative in "highly concerning, worth checking, low concern" language, and the single most relevant registration.
3. **Record.** Photo hash, crop hashes, boxes, scores, rationales, field notes and a ledger of every model call (model, purpose, latency, tokens) land in one JSON record per sweep, served read-only with click-through links to USPTO TSDR, EUIPO eSearch and WIPO Madrid Monitor.

The lawyer opens the record, sees the photo with numbered, colour-banded boxes, reads the rationales and decides. Marksweep never says "infringes".

## Meta models

| Model | Job | Why |
|---|---|---|
| Muse Glimmer 30B (open weights, Apache 2.0, served with llama.cpp on a GPU we control) | Finds the marks in the photo and assesses each crop against the register drawings | A Meta vision model that runs on hardware the firm controls: client photos never go to a public API, which is what a law firm's confidentiality duty wants |
| SAM 3.1 and Muse Spark 1.3 (Meta Model API) | Same two jobs through the hosted API, selectable by configuration | Higher accuracy segmentation with lossless masks where the hosted route is available |

Every call is logged to the record's ledger with model id, purpose, latency and token counts.

## The record and the legal framing

Each element is scored on the six questions of the likelihood-of-confusion global assessment (Sabel v Puma line), the same six Signum uses, with the same weights and bands.

| Dimension | Weight | What the model is asked |
|---|---|---|
| Visual similarity | 0.30 | Specific get-up against the closest client mark; sharing only a genus stays low |
| Aural similarity | 0.10 | Word elements against the client's word marks; not applicable for figurative elements |
| Conceptual similarity | 0.15 | The idea conveyed; commonplace ideas count for little |
| Goods and services proximity | 0.15 | Goods seen against the Nice classes of the matched registrations |
| Distinctiveness of the client mark | 0.15 | Reputation of the matched mark, only when a mark is meaningfully similar |
| Imitation signals | 0.15 | Altered letters that keep the look, copied trade dress with a changed name |

Weighted mean, not-applicable weights redistributed. Red at 65 is "highly concerning", amber at 40 "worth checking", below that "low concern". Every number is a research signal for the supervising lawyer, never a conclusion. If no client mark is a candidate, every score is capped at 25.

## Fit with Signum and what is new

Marksweep is the field-intake module of Signum, Vanta Point Labs' AI-assisted IP case assessment, piloting with a Hong Kong IP firm. Signum starts from one uploaded image of an accused product; Marksweep starts one step earlier, at the stall. The same dimensions, bands and "lawyer decides" rule apply, so a Marksweep record can become a Signum matter without re-assessment.

New work built during the hackathon, all in the public repo github.com/cvikl/marksweep: the segmentation and crop pipeline, the assessment prompt and schema, merge and roll-up logic, record format and ledger, web app and record viewer, deploy bundle, Modal serving script, demo scenes and video. Reused and labelled: the six dimension names and weights (public case law, also used in Signum) and the office drawings of eight publicly registered marks (LEGO Juris A/S and Louis Vuitton Malletier) used as the demo clients' portfolios.

## Demo, deployment, team

Live run on meta.vantapointlabs.com: pick a stall photo (or drop your own), pick the client, press Run, watch the ledger, land on the record. Two demo clients: LEGO (toy stall, LEPIN-style boxes) and Louis Vuitton (handbag stall, monogram look-alikes). Repo github.com/cvikl/marksweep, MIT. Three-minute video from real screen captures. Submission on the Cerebral Valley platform by 4 Nov 21:00 ET (03:00 CET), Representative Bernard Liu. Team: Timotej Cvikl (build), Bernard Liu (legal framing, submission).

Status 21:30 CET, 4 Nov: the Meta Model API refuses calls without a card on file, so the live model is Muse Glimmer 30B served on Modal; the hosted route stays in the code for when a billed key exists.
