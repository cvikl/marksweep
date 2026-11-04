"""Recorded demo sweeps: the real SAM 3.1 and Muse Spark outputs for the demo photos, replayed when the
host has no key (and in tests). Each demo is a folder under fixtures/demos/<name>/ with photo.*, sam.json
(list of segment results) and assess.json (list of Muse Spark outputs, one per element, in element order)."""
from __future__ import annotations

import json
from pathlib import Path

from . import config


def demos_dir() -> Path:
    return config.fixtures_dir() / "demos"


def list_demos() -> list[dict]:
    out = []
    for d in sorted(demos_dir().glob("*/")):
        meta = d / "demo.json"
        if meta.exists():
            m = json.loads(meta.read_text())
            m["name"] = d.name
            photo = next((p for p in d.glob("photo.*")), None)
            m["photo"] = photo.name if photo else None
            out.append(m)
    return out


def demo_photo(name: str) -> Path | None:
    d = demos_dir() / Path(name).name
    return next((p for p in d.glob("photo.*")), None)


def load_fixture(name: str) -> dict | None:
    d = demos_dir() / Path(name).name
    if not (d / "sam.json").exists():
        return None
    sam = json.loads((d / "sam.json").read_text())
    return {"segment": {r["concept"]: r for r in sam}, "assess": json.loads((d / "assess.json").read_text()),
            "meta": json.loads((d / "demo.json").read_text()) if (d / "demo.json").exists() else {}}


def record_fixture(name: str, photo: Path, sam_results: list[dict], assessments: list[dict], meta: dict) -> Path:
    d = demos_dir() / name
    d.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy(photo, d / ("photo" + photo.suffix.lower()))
    (d / "sam.json").write_text(json.dumps(sam_results, indent=1))
    (d / "assess.json").write_text(json.dumps(assessments, indent=1, ensure_ascii=False))
    (d / "demo.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    return d
