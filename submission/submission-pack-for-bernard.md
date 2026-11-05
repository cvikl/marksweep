# Marksweep: what to submit on Cerebral Valley

Form: https://cerebralvalley.ai/e/meta-ai-developer-hackathon/hackathon/submit (your login, ncl31@cam.ac.uk). Deadline 4 Nov 9:00 PM ET = 5 Nov 02:00 London. Every answer below is paste-ready, in the form's order. The three links are live.

**Team Name:** Vanta Point Labs

**Track:** Startups Track

**Problem statement:** Build for Your World

**Most Viral Track X post link:** leave empty

**Project Description** (3,000 max; 2,034 used):

Marksweep: a photo from the market stall in, a trademark evidence record out. Google Lens tells you what a logo is; Marksweep tells a lawyer why it might be infringing, with a score, a reason and a chain of evidence.

Brand owners lose the fight against copies at the point of sale. Investigators photograph markets, shop windows and shelves; paralegals then sort hundreds of photos by hand, and nothing records which mark was compared with which, on what basis, or when. Marksweep turns one field photo into a hashed evidence record in under a minute: SAM 3.1 isolates every logo, label and pattern (boxes and lossless masks with stable object ids); Muse Spark 1.3 reads each crop next to the office drawings of the client's registered marks and returns schema-checked JSON with six sub-scores and one-sentence rationales on the likelihood-of-confusion global assessment (visual, aural, conceptual, goods, distinctiveness, imitation signals), a short narrative and the single most relevant registration. The record keeps the photo and crop hashes, boxes, scores, rationales, field notes and a ledger of every model call (model, purpose, latency, tokens), with click-through links to USPTO, EUIPO and WIPO. Every number is a research signal for the supervising lawyer; the tool never says "infringes". If no client mark is a candidate, every score is capped at 25 and the narrative says so (see the control demo).

Marksweep is the field-intake module of Signum, our AI-assisted IP case assessment piloting with a Hong Kong IP firm. Live demo: https://meta.vantapointlabs.com (four recorded sweeps replay instantly; an operator token runs new photos live). Everything in the repo was built on 4 November 2026; reused and labelled: six dimension names and weights from public case law and eight public register drawings used as the demo clients' portfolios. Demo photos are public-domain customs seizure photographs and a CC BY-SA shop window.

Team: Timotej Cvikl (build) and Bernard Liu (legal framing, submission), Vanta Point Labs.

**Public GitHub Repository:** https://github.com/cvikl/marksweep

**3-Minute Demo Video:** https://meta.vantapointlabs.com/static/marksweep-demo.mp4

**Describe your use of Meta products to build the submitted project:**

SAM 3.1 via the Meta Model API (Responses API, streamed, decoded with meta_sam_parser): three noun-phrase prompts per photo ("brand logo", "printed brand name", "repeating pattern on a bag"); boxes merged across prompts, crops cut from the original and hashed; 2 to 6 s per call. Muse Spark 1.3 via chat completions with vision and response_format json_schema, reasoning_effort low: one call per element with the client's register drawings in context, about 2,100 prompt tokens, 9 to 20 s. Four demo photos: 34 model calls, 3 min 33 s end to end. Muse Glimmer 30B open weights (GGUF, llama.cpp on a laptop CPU, no cloud) runs the same pipeline fully offline for firms whose photos must not leave the building, doing grounding and assessment in one model; tested on 4 Nov at about 2 tokens per second (15 to 25 minutes per photo), selected by configuration.

**Why are Meta's models important to your solution?**

Open-vocabulary segmentation from a text phrase means the investigator never draws a box and the segmenter, not a person, decides what is evidence; the lossless masks and stable object ids become the crops a court can check against the hash. Muse Spark's vision plus schema-guaranteed JSON gives us six auditable scores per element with a one-sentence reason each, which is the shape a lawyer's global assessment takes. And because Muse Glimmer ships as open weights under Apache 2.0, the same pipeline can run on hardware the firm controls, which is what a law firm's confidentiality duty wants.

**Feedback on partner technologies** (150 max):

Not used for inference. Modal refuses GPU functions without a payment method, so we could not host Muse Glimmer there.

**Survey:**
- How likely to build with Meta Model API: Very likely
- Overall opinion of Meta Model API: Somewhat favorable
- Consent box: tick
- Recommend Meta Model API (0 to 5): 4
- Recommend Muse Code (0 to 5): 3
- Biggest obstacle: Getting access or setting up our account
- Compared with other models: Somewhat better
- What matters most: Data privacy and terms of use
- Hardest to switch: Our product is tuned to our current model's behavior and prompts
- What would stop production use: How our data and our users' data would be stored or used

Note: the form is already filled with exactly this on your login in Tim's browser; if you submit from your own device, the fields will be empty there and need this pasted in.
