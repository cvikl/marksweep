# Marksweep, Cerebral Valley submission text (draft, 4 Nov 2026)

**Project name:** Marksweep
**Tagline:** Google Lens tells you what a logo is. Marksweep tells a lawyer why it might be infringing: a score, a reason, and a chain of evidence. A photo from the market stall in, a trademark evidence record out.
**Track:** Startups. **Theme:** Build for Your World.
**Live:** https://meta.vantapointlabs.com  **Repo:** https://github.com/cvikl/marksweep  **Video:** (link)

## What it does
Brand owners lose the fight against copies at the stall, not in court. Investigators photograph markets and shelves; paralegals then sort hundreds of photos by hand and nothing records which mark was compared with which, on what basis, or when. Marksweep turns one field photo into a hashed evidence record in about a minute: SAM 3.1 isolates every logo, label and pattern; Muse Spark 1.3 reads each crop next to the office drawings of the client's registered marks and returns six sub-scores with rationales on the likelihood-of-confusion global assessment (Sabel v Puma line); the record keeps photo and crop hashes, boxes, masks, scores, rationales, field notes and a ledger of every model call. Every number is a research signal for the supervising lawyer, never a conclusion.

## How we used Meta's models
- SAM 3.1 (Model API, Responses API, streamed, meta_sam_parser): open-vocabulary segmentation from three noun phrases, so the investigator never draws a box; masks become the evidence crops; stable object ids. 2 to 6 s per call.
- Muse Spark 1.3 (vision, json_schema, reasoning_effort low): one call per element with the four register drawings in context; schema-checked scores and one-sentence rationales. 9 to 20 s per call, about 2,100 prompt tokens.
- Muse Glimmer 30B (open weights, GGUF, llama.cpp on a laptop CPU): the same pipeline runs fully offline for firms whose photos must not leave the building; grounding and assessment by one model; tested on 4 Nov, about 2 tokens per second, so 15 to 25 minutes per photo. Selected by configuration.
- Measured on the four demo photos: 34 model calls, 3 min 33 s end to end on the API.

## Limits
One photo per sweep, up to 12 MB; elements per photo capped (6 in the demo, largest boxes first); no video yet although SAM 3.1 and the parser support it; the demo photos are public-domain customs seizure photographs and a CC BY-SA shop window (sources in the repo), the demo clients are real registrants whose marks are public records and not customers of this project.

## What is new in the hackathon
All code in the repository (pipeline, prompt and schema, roll-up, record, web app, deploy, scenes, video) was written on 4 Nov 2026. Reused and labelled: six dimension names and weights from public case law (also used in our product Signum) and eight public register drawings used as the demo clients' portfolios. No Signum code is included.

## Team
Timotej Cvikl (build), Bernard Liu (legal framing, submission). Vanta Point Labs, Cambridge and Ljubljana.
