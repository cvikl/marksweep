# Marksweep

**Field enforcement for trademark lawyers, on Meta's models.** An investigator photographs a market stall, a shop
window or an online listing. A Meta vision model finds every logo, label and pattern, then reads each one next to the
client's registered marks and scores the six questions of the likelihood-of-confusion global assessment. The result is
a hashed evidence record with crops, rationales and a ledger of every model call. The lawyer decides.

Two model routes, chosen by configuration:

- **Open weights, on the investigator's own machine (what the demo runs).** Muse Glimmer 30B (Apache 2.0,
  `meta-models/Muse-Glimmer-30B-GGUF`) served by llama.cpp on a laptop CPU does both jobs: grounding (boxes for every
  mark in the photo) and assessment. Client photos never leave the firm. `scripts/glimmer-server.sh`.
- **Meta Model API.** SAM 3.1 for segmentation with lossless masks and Muse Spark 1.3 for assessment, `MARKSWEEP_SEGMENTER=sam`
  and the default base URL. Same code, same record format.

Built for the [Meta Global AI Developer Hackathon](https://cerebralvalley.ai/e/meta-ai-developer-hackathon) (Cerebral
Valley, 26 Oct to 4 Nov 2026), Startups track, theme Build for Your World. Live: https://meta.vantapointlabs.com

> Signum, our case-assessment product, starts from one uploaded image of an accused product. Marksweep starts one step
> earlier, at the stall.

## What it does

| Step | What happens | Model |
|---|---|---|
| **Segment** | Open-weights route: one grounding call asks the vision model for the box of every "brand logo, printed brand name, or repeating monogram pattern" as fractions of the image. API route: three short noun phrases go to SAM 3.1 with the photo and every box and lossless mask comes back with a stable object id. Either way boxes are merged (IoU 0.6) and cut from the original photo with 12% padding; each crop is hashed. | `muse-glimmer-30B` (local) or `sam-3.1` (Responses API, streamed, decoded with `meta_sam_parser`) |
| **Assess** | Each crop is sent with the office drawings of the client's registered marks (a numbered contact sheet on the local route, the separate drawings on the API route). The model returns schema-checked JSON: what it sees, the text it reads, candidate client marks, six sub-scores with rationales, a narrative in "highly concerning / worth checking / low concern" language, the single most relevant registration. | `muse-glimmer-30B` (local) or `muse-spark-1.3`, chat completions, vision, `response_format: json_schema` |
| **Record** | Photo hash, crop hashes, boxes, masks, scores, rationales, field notes and the model ledger (model, purpose, latency, tokens) in one JSON per sweep, served read-only with click-through links to USPTO TSDR, EUIPO eSearch and WIPO Madrid Monitor. | none |
| **Demo photos** | Four freely licensed photographs (public-domain customs seizures and a CC BY-SA shop window), sources in `fixtures/demos/SOURCES.md`; no seller is identified. | none |

The six dimensions and their weights are the ones Signum uses (visual 0.30, aural 0.10, conceptual 0.15, goods and
services 0.15, distinctiveness 0.15, imitation signals 0.15). The roll-up is a weighted mean with not-applicable
weights redistributed; red at 65, amber at 40. If no client mark is a candidate, every score is capped at 25 and the
narrative says the element is not the client's concern. Nothing here is a legal conclusion.

## Run it

```bash
uv venv && uv pip install -e ".[dev]"            # Python 3.11+
cp .env.example .env                              # local Glimmer (default below) or MODEL_API_KEY from https://dev.meta.ai
scripts/glimmer-server.sh &                       # llama.cpp + Muse Glimmer 30B GGUF on :8080 (see the script for the weights)
.venv/bin/marksweep ping                          # one tiny call to whichever model is configured
.venv/bin/marksweep serve                         # http://localhost:8000
.venv/bin/marksweep sweep photo.jpg --client lego --goods "brick sets" --jurisdictions "Hong Kong"
.venv/bin/marksweep sweep photo.jpg --client lego --demo lego-stall     # replay a recorded run, no key needed
.venv/bin/marksweep render "<scene prompt>" out.png                     # muse-image
env -u PYTHONPATH .venv/bin/pytest                                      # unit tests, offline
```

Without `MODEL_API_KEY` the app runs in fixture mode: the recorded demo sweeps (real SAM 3.1 and Muse Spark outputs)
replay with their ledgers marked "replayed", and new photos are refused with a clear message. On a public host set
`MARKSWEEP_TOKEN`; new sweeps then need `?token=` so strangers cannot spend the key.

## Layout

| Path | What |
|---|---|
| `marksweep/meta.py` | The Meta Model API client: SAM 3.1 streaming + parser, Muse Spark vision JSON, Muse Image |
| `marksweep/pipeline.py` | The sweep: segment, merge, crop, assess, record |
| `marksweep/scoring.py` | Dimensions, weights, bands, roll-up |
| `marksweep/registry.py` | The two demo clients' registered marks with office numbers and links |
| `marksweep/app.py` | FastAPI app: upload, server-sent progress, record viewer, read-only files |
| `marksweep/fixtures.py`, `fixtures/demos/` | Recorded runs for replay |
| `static/` | Upload page and record page (plain HTML, no build step) |
| `deploy/` | Dockerfile, compose, Caddy drop-in, `publish.sh` for the shared box |

## Hackathon work and prior work

Everything in this repository was written during the hackathon on 4 Nov 2026: the SAM 3.1 segmentation and crop
pipeline, the Muse Spark assessment prompt and schema, merge and roll-up logic, record format and ledger, web app and
record viewer, deploy bundle, demo scenes and video.

Reused from before the hackathon, and labelled here: the six dimension names and default weights (public case law,
Sabel v Puma line, also used in Signum), and the office drawings of eight publicly registered marks (LEGO Juris A/S and
Louis Vuitton Malletier; `fixtures/marks/`, numbers verified on the office registers in Aug 2026) that stand in for the
demo clients' portfolios. No Signum code is included.

## Honesty statements

The demo clients are real registrants whose marks are public register records; they are not customers of this project.
The stall photos are synthetic. Scores are research signals for the supervising lawyer's own global assessment, not
findings. Built with Claude Code; the model inference is Meta's.

## Licence

MIT, see `LICENSE`.
