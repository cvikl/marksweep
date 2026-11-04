from __future__ import annotations

import os
from pathlib import Path

BASE_URL = "https://api.meta.ai/v1"
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
    return Path(__file__).resolve().parent.parent


def fixtures_dir() -> Path:
    return root_dir() / "fixtures"


def public_token() -> str:
    return os.environ.get("MARKSWEEP_TOKEN", "").strip()
