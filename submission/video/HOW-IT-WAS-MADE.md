# How the Marksweep demo video was made (4 to 5 Nov 2026)

Everything in it is generated from code and real captures; no video editor was used. Same method as the CRA Watch and
a16z films in this venture folder.

1. **Narration.** Eight blocks in `submission/narration.txt` (the opening line and the pitch sentence came from Bernard
   Liu's review of the concept on 4 Nov). Synthesised with edge-tts (voice en-GB-RyanNeural, +4%), trimmed and
   loudness-normalised with ffmpeg to `remotion/public/voice-0N.wav`. Replace with a human recording by overwriting
   those files and the durations in `src/Film.tsx`.
2. **Real runs.** The four demo photos were swept for real on the Meta Model API (SAM 3.1 + Muse Spark 1.3) on 4 Nov at
   23:23 to 23:26 UTC and recorded as fixtures (`fixtures/demos/*/sam.json`, `assess.json`); the records shown are
   `data/sweeps/20261104-232504-ae83c5` (customs seizure, LV) and `20261104-232601-116447` (control).
3. **UI captures.** `shot.mjs` drove a headless Chrome (puppeteer-core) at 1920 px against the local app, selected the
   demo, pressed Run, opened the two records, and saved full-page PNGs plus the bounding boxes of every `data-shot`
   element (`rects-*.json`) so the camera lands on exact elements.
4. **Remotion project** (`remotion/`, React + Remotion 4; `node_modules` is a symlink to the CRA Watch project's).
   `Film` sequences eight scenes, one per narration block: Title and End are animated typography on the product's
   design tokens (IBM Plex); the six screenshot scenes use the `PageShot` camera-and-spotlight component with caption
   pills naming the model doing the work. Render: `npx remotion render src/index.ts Film out/film.mp4`.
5. **Music bed and mix.** The D-minor pad from the earlier films (`pad.wav`), ducked under speech with a sidechain
   compressor (`mix.sh`), AAC 192 kb/s, video stream copied: `out/marksweep-demo.mp4`.
