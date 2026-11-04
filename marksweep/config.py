from __future__ import annotations

import os
from pathlib import Path



def _load_dotenv() -> None:
    """Read ./.env (or MARKSWEEP_ENV) into the environment without a shell; existing variables win."""
    p = Path(os.environ.get("MARKSWEEP_ENV", Path(__file__).resolve().parent.parent / ".env"))
    if not p.is_file():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"'))


_load_dotenv()

BASE_URL = os.environ.get("MARKSWEEP_BASE_URL", "https://api.meta.ai/v1")
SPARK_MODEL = os.environ.get("MARKSWEEP_SPARK_MODEL", "muse-spark-1.3")
SAM_MODEL = "sam-3.1"
IMAGE_MODEL = "muse-image-1.0"


def api_key() -> str:
    return os.environ.get("MODEL_API_KEY", "").strip()


def fixture_mode() -> bool:
    return os.environ.get("MARKSWEEP_FIXTURE", "0") in {"1", "true", "yes"} or not api_key()


def data_dir() -> Path:
    p = Path(os.environ.get("MARKSWEEP_DATA", "./data")).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def root_dir() -> Path:
    """Project root holding static/ and fixtures/: MARKSWEEP_ROOT, else the checkout, else the working directory."""
    env = os.environ.get("MARKSWEEP_ROOT")
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve().parent.parent
    return here if (here / "static").is_dir() else Path.cwd()


def fixtures_dir() -> Path:
    return root_dir() / "fixtures"


def public_token() -> str:
    return os.environ.get("MARKSWEEP_TOKEN", "").strip()


def segmenter() -> str:
    """"sam" (SAM 3.1 on the Meta Model API) or "vlm" (bounding boxes from the vision model itself)."""
    return os.environ.get("MARKSWEEP_SEGMENTER", "sam")


def prefill_reasoning() -> bool:
    """Close the model's thinking channel before the answer (local Muse Glimmer route). Off for the Meta Model API."""
    v = os.environ.get("MARKSWEEP_PREFILL_REASONING")
    if v is not None:
        return v in {"1", "true", "yes"}
    return "127.0.0.1" in BASE_URL or "localhost" in BASE_URL
