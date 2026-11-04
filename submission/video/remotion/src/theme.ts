import { staticFile } from "remotion";
export const C = { bg: "#F7F6F2", ink: "#1C1B18", mute: "#6B6760", line: "#E3DFD6", red: "#B4232C", amber: "#B7791F", green: "#2F7A4A", navy: "#1A2B4A", paper: "#FFFDF9" };
export const sans = '"IBM Plex Sans", sans-serif';
export const cond = '"IBM Plex Sans Condensed", sans-serif';
export const mono = '"IBM Plex Mono", Menlo, monospace';
export const fontCss = `
@font-face { font-family: "IBM Plex Mono"; font-weight: 400; src: url("${staticFile("fonts/ibm-plex-mono-400.woff2")}") format("woff2"); }
@font-face { font-family: "IBM Plex Mono"; font-weight: 500; src: url("${staticFile("fonts/ibm-plex-mono-500.woff2")}") format("woff2"); }
@font-face { font-family: "IBM Plex Sans"; font-weight: 500; src: url("${staticFile("fonts/ibm-plex-sans-500.woff2")}") format("woff2"); }
@font-face { font-family: "IBM Plex Sans Condensed"; font-weight: 700; src: url("${staticFile("fonts/ibm-plex-sans-condensed-700.woff2")}") format("woff2"); }`;
