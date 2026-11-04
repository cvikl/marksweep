#!/usr/bin/env bash
# Serve Meta's open-weight Muse Glimmer 30B (GGUF, Apache 2.0) with llama.cpp on the CPU, OpenAI-compatible on :8080.
# Weights: huggingface.co/meta-models/Muse-Glimmer-30B-GGUF (text Q4_K_M 16.8 GB + mmproj 1.4 GB). Needs ~20 GB RAM.
set -euo pipefail
M=${GLIMMER_DIR:-$HOME/models/glimmer}
BIN=${LLAMA_SERVER:-$HOME/src/llama.cpp/build/bin/llama-server}
DRAFT=()
[ -f "$M/dflash-Muse-Glimmer-30B-Q4_K_M.gguf" ] && DRAFT=(-md "$M/dflash-Muse-Glimmer-30B-Q4_K_M.gguf")
# Reasoning cannot be switched off in this template; "low" keeps the thinking channel short. Answers land in `content`,
# thinking in `reasoning_content`.
exec "$BIN" -m "$M/Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf" --mmproj "$M/mmproj-Muse-Glimmer-30B-Q4_K_M.gguf" \
  -a muse-glimmer-30B -c "${CTX:-8192}" -np 1 -t "${THREADS:-16}" --host 127.0.0.1 --port 8080 --jinja \
  --chat-template-kwargs '{"reasoning_strength":"'"${REASONING:-low}"'"}' \
  --temp 0.2 --top-p 0.95 --top-k 64 --no-warmup "${DRAFT[@]}" "$@"
