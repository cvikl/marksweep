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
    from .scoring import DIMENSIONS, band_for, roll_up
    out = []
    for d in sorted(demos_dir().glob("*/")):
        meta = d / "demo.json"
        if not meta.exists():
            continue
        m = json.loads(meta.read_text())
        m["name"] = d.name
        photo = next((p for p in d.glob("photo.*")), None)
        m["photo"] = photo.name if photo else None
        if photo:
            from PIL import Image
            with Image.open(photo) as im:
                m["width"], m["height"] = im.size
        elements = []
        if (d / "assess.json").exists():
            assess = json.loads((d / "assess.json").read_text())
            for i, (box, a) in enumerate(zip(m.get("boxes") or [], assess), 1):
                subs = a.get("sub_scores") or {}
                bd = [{"key": k["key"], "weight": k["weight"], "score": int((subs.get(k["key"]) or {}).get("score", 0) or 0),
                       "na": bool((subs.get(k["key"]) or {}).get("na"))} for k in DIMENSIONS]
                sc = roll_up(bd)
                elements.append({"index": i, "box": {k: box[k] for k in ("left", "top", "right", "bottom")},
                                 "score": sc, "band": band_for(sc), "text_read": a.get("text_read"), "seen": a.get("seen")})
        m["elements"] = elements
        m["bands"] = {b: sum(1 for e in elements if e["band"] == b) for b in ("red", "amber", "green")}
        m.pop("ledger", None); m.pop("boxes", None)
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
    meta = json.loads((d / "demo.json").read_text()) if (d / "demo.json").exists() else {}
    return {"segment": {r["concept"]: r for r in sam}, "assess": json.loads((d / "assess.json").read_text()),
            "boxes": meta.get("boxes") or [], "meta": meta}


def record_fixture(name: str, photo: Path, sam_results: list[dict], assessments: list[dict], meta: dict) -> Path:
    d = demos_dir() / name
    d.mkdir(parents=True, exist_ok=True)
    import shutil
    if photo.resolve() != (d / ("photo" + photo.suffix.lower())).resolve():
        shutil.copy(photo, d / ("photo" + photo.suffix.lower()))
    (d / "sam.json").write_text(json.dumps(sam_results, indent=1))
    (d / "assess.json").write_text(json.dumps(assessments, indent=1, ensure_ascii=False))
    existing = json.loads((d / "demo.json").read_text()) if (d / "demo.json").exists() else {}
    existing.update(meta)
    (d / "demo.json").write_text(json.dumps(existing, indent=1, ensure_ascii=False))
    return d
