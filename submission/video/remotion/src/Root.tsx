import React from "react";
import { Composition } from "remotion";
import { Film, TOTAL } from "./Film";
import { Thumb } from "./Thumb";

export const RemotionRoot: React.FC = () => (<>
  <Composition id="Film" component={Film} durationInFrames={Math.round(TOTAL * 30)} fps={30} width={1920} height={1080} />
  <Composition id="Thumb" component={Thumb} durationInFrames={1} fps={30} width={1920} height={1080} />
</>);
