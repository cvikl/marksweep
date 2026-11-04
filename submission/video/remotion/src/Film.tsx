import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { Fade } from "./lib";
import { fontCss } from "./theme";
import { Title } from "./scenes/Title";
import { End } from "./scenes/End";
import { Upload, Segment, Assess, Record, Control, Ledger } from "./scenes/Shots";

// narration block durations (s), from ffprobe on public/voice-0N.wav
const V = [26.93, 10.84, 18.81, 23.53, 21.74, 11.93, 19.07, 17.74];
const tail = 0.5;
export const scenes: { voice: number; dur: number; el: React.ReactNode }[] = [
  { voice: 1, dur: V[0] + tail, el: <Title /> },
  { voice: 2, dur: V[1] + tail, el: <Upload /> },
  { voice: 3, dur: V[2] + tail, el: <Segment /> },
  { voice: 4, dur: V[3] + tail, el: <Assess /> },
  { voice: 5, dur: V[4] + tail, el: <Record /> },
  { voice: 6, dur: V[5] + tail, el: <Control /> },
  { voice: 7, dur: V[6] + tail, el: <Ledger /> },
  { voice: 8, dur: V[7] + 1.5, el: <End /> },
];
export const TOTAL = scenes.reduce((a, s) => a + s.dur, 0);
const FPS = 30;

export const Film: React.FC = () => {
  let from = 0;
  return (
    <AbsoluteFill style={{ background: "#F7F6F2" }}>
      <style>{fontCss}</style>
      {scenes.map((s, i) => {
        const start = from; from += s.dur;
        return (
          <Sequence key={i} from={Math.round(start * FPS)} durationInFrames={Math.round(s.dur * FPS)}>
            <Fade dur={s.dur}>{s.el}</Fade>
            <Audio src={staticFile(`voice-0${s.voice}.wav`)} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
