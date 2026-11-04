#!/usr/bin/env bash
# Pad under the rendered film, music ducked under speech. Run from submission/video.
set -euo pipefail
cd "$(dirname "$0")"
OUT="${1:-out/marksweep-demo.mp4}"; mkdir -p out
ffmpeg -loglevel error -y -i remotion/out/film.mp4 -i remotion/public/pad.wav -filter_complex \
 "[1:a]apad[pad];[0:a]asplit[v1][v2];[pad][v2]sidechaincompress=threshold=0.04:ratio=8:attack=15:release=500[duck];[v1][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest "$OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
