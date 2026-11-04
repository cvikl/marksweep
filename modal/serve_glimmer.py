"""Serve Meta's open-weight Muse Glimmer 30B (GGUF, Apache 2.0) with llama.cpp on a Modal GPU, OpenAI-compatible.

    modal run modal/serve_glimmer.py::download      # once: pulls the two GGUF files into a Volume (~18 GB)
    modal deploy modal/serve_glimmer.py             # web endpoint https://<workspace>--marksweep-glimmer-serve.modal.run/v1

The endpoint takes `Authorization: Bearer $GLIMMER_TOKEN` (Modal secret `marksweep-glimmer`). Marksweep points at it with
MARKSWEEP_BASE_URL=https://.../v1  MARKSWEEP_SPARK_MODEL=muse-glimmer-30B  MODEL_API_KEY=<token>.
"""
from __future__ import annotations

import os
import subprocess
import time

import modal

APP = "marksweep-glimmer"
REPO = "meta-models/Muse-Glimmer-30B-GGUF"
TEXT = "Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf"
MMPROJ = "mmproj-Muse-Glimmer-30B-Q4_K_M.gguf"
LLAMA_RELEASE = "b10600"  # any build >= b10353 registers the muse_glimmer architecture

vol = modal.Volume.from_name("marksweep-glimmer-weights", create_if_missing=True)
app = modal.App(APP)

image = (
    modal.Image.from_registry("nvidia/cuda:12.6.3-devel-ubuntu24.04", add_python="3.12")
    .apt_install("git", "cmake", "build-essential", "curl", "libcurl4-openssl-dev", "libgomp1", "ninja-build")
    .pip_install("huggingface_hub[hf_transfer]")
    .run_commands(
        "git clone --depth 1 https://github.com/ggml-org/llama.cpp /opt/llama.cpp",
        "grep -c LLM_ARCH_MUSE_GLIMMER /opt/llama.cpp/src/llama-arch.cpp",
        "cd /opt/llama.cpp && cmake -B build -G Ninja -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES='89;90' -DLLAMA_CURL=ON "
        "&& cmake --build build --config Release -j --target llama-server llama-mtmd-cli && cp build/bin/llama-server /usr/local/bin/ && ls -la /usr/local/bin/llama-server",
    )
)


@app.function(image=image, volumes={"/weights": vol}, timeout=60 * 60)
def download():
    from huggingface_hub import hf_hub_download
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    for f in (TEXT, MMPROJ):
        if not os.path.exists(f"/weights/{f}"):
            hf_hub_download(REPO, f, local_dir="/weights")
            vol.commit()
    print(os.listdir("/weights"))


@app.function(image=image, gpu="A10G", volumes={"/weights": vol}, timeout=60 * 60, scaledown_window=240,
              secrets=[modal.Secret.from_name("marksweep-glimmer")])
@modal.concurrent(max_inputs=2)
@modal.web_server(8080, startup_timeout=600)
def serve():
    cmd = ["llama-server", "-m", f"/weights/{TEXT}", "--mmproj", f"/weights/{MMPROJ}", "-a", "muse-glimmer-30B",
           "-ngl", "99", "-c", "12288", "-np", "1", "-fa", "on", "--host", "0.0.0.0", "--port", "8080", "--jinja",
           "--temp", "0.2", "--top-p", "0.95", "--top-k", "64", "--api-key", os.environ["GLIMMER_TOKEN"]]
    subprocess.Popen(cmd)
    time.sleep(1)
