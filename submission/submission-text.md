# Marksweep, Cerebral Valley submission text (draft, 4 Nov 2026)

**Project name:** Marksweep
**Tagline:** A photo from the market stall in, a trademark evidence record out. SAM 3.1 finds every mark, Muse Spark assesses it against the client's registrations, the lawyer decides.
**Track:** Startups. **Theme:** Build for Your World.
**Live:** https://meta.vantapointlabs.com  **Repo:** https://github.com/cvikl/marksweep  **Video:** (link)

## What it does
Brand owners lose the fight against copies at the stall, not in court. Investigators photograph markets and shelves; paralegals then sort hundreds of photos by hand and nothing records which mark was compared with which, on what basis, or when. Marksweep turns one field photo into a hashed evidence record in about a minute: SAM 3.1 isolates every logo, label and pattern; Muse Spark 1.3 reads each crop next to the office drawings of the client's registered marks and returns six sub-scores with rationales on the likelihood-of-confusion global assessment (Sabel v Puma line); the record keeps photo and crop hashes, boxes, masks, scores, rationales, field notes and a ledger of every model call. Every number is a research signal for the supervising lawyer, never a conclusion.

## How we used Meta's models
- SAM 3.1 (Model API, Responses API, streamed, meta_sam_parser): open-vocabulary segmentation from three noun phrases, so the investigator never draws a box; masks become the evidence crops; stable object ids.
- Muse Spark 1.3 (vision, json_schema): one call per element with up to four register drawings in context; schema-checked scores and rationales; the 1M context lets the whole portfolio ride along.
- Muse Image 1.0: the synthetic stall scenes, so no real seller is pictured.

## What is new in the hackathon
All code in the repository (pipeline, prompt and schema, roll-up, record, web app, deploy, scenes, video) was written on 4 Nov 2026. Reused and labelled: six dimension names and weights from public case law (also used in our product Signum) and eight public register drawings used as the demo clients' portfolios. No Signum code is included.

## Team
Timotej Cvikl (build), Bernard Liu (legal framing, submission). Vanta Point Labs, Cambridge and Ljubljana.
