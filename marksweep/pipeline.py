"""The sweep: photo in, evidence record out.

1. SAM 3.1 finds every candidate mark (one request per concept phrase, e.g. "brand logo", "printed label").
2. Boxes are merged, filtered and cropped from the original photo; each crop is hashed.
3. Muse Spark reads each crop together with the client's registered marks and returns the six
   global-assessment sub-scores (Sabel v Puma line) with rationales, plus what it actually sees.
4. The record is written: photo hash, crops, masks, scores, model ledger. The lawyer decides.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageOps

from . import config, meta, registry
from .ledger import Ledger
from .scoring import DIMENSIONS, band_for, roll_up

CONCEPTS = ["brand logo", "printed brand name", "repeating pattern on a bag"]
VLM_CONCEPT = "brand logo, printed brand name, or repeating monogram pattern"

ASSESS_SCHEMA = {
    "type": "object",
    "properties": {
        "seen": {"type": "string", "description": "what the crop shows, 1 sentence, no conclusions"},
        "text_read": {"type": "string"},
        "candidate_marks": {"type": "array", "items": {"type": "string"},
                            "description": "ids of client marks this crop could be confused with, [] if none"},
        "sub_scores": {
            "type": "object",
            "properties": {k: {"type": "object", "properties": {
                "score": {"type": "integer", "minimum": 0, "maximum": 100},
                "rationale": {"type": "string"},
                "na": {"type": "boolean"}}, "required": ["score", "rationale"]} for k in [d["key"] for d in DIMENSIONS]},
            "required": [d["key"] for d in DIMENSIONS]},
        "narrative": {"type": "string"},
        "primary_match": {"type": "string"},
    },
    "required": ["seen", "candidate_marks", "sub_scores", "narrative", "primary_match"],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _iou(a, b) -> float:
    ix = max(0, min(a["right"], b["right"]) - max(a["left"], b["left"]))
    iy = max(0, min(a["bottom"], b["bottom"]) - max(a["top"], b["top"]))
    inter = ix * iy
    if not inter:
        return 0.0
    area = lambda r: (r["right"] - r["left"]) * (r["bottom"] - r["top"])
    return inter / (area(a) + area(b) - inter)


def merge_boxes(results: list[dict], img_w: int, img_h: int, min_side: int = 24, iou_thresh: float = 0.6) -> list[dict]:
    """Union of all SAM boxes across concepts, dropping duplicates and specks."""
    out: list[dict] = []
    for res in results:
        for b in res["boxes"]:
            box = {k: int(round(b[k])) for k in ("left", "top", "right", "bottom")}
            box["left"], box["top"] = max(0, box["left"]), max(0, box["top"])
            box["right"], box["bottom"] = min(img_w, box["right"]), min(img_h, box["bottom"])
            if box["right"] - box["left"] < min_side or box["bottom"] - box["top"] < min_side:
                continue
            box["concept"] = res["concept"]
            box["object_id"] = b.get("object_id")
            box["confidence"] = b.get("confidence")
            if any(_iou(box, o) > iou_thresh for o in out):
                continue
            out.append(box)
    out.sort(key=lambda r: (r["top"] // 50, r["left"]))
    return out


def crop(photo: Image.Image, box: dict, out: Path, pad: float = 0.12) -> Path:
    w, h = box["right"] - box["left"], box["bottom"] - box["top"]
    px, py = int(w * pad), int(h * pad)
    region = photo.crop((max(0, box["left"] - px), max(0, box["top"] - py),
                         min(photo.width, box["right"] + px), min(photo.height, box["bottom"] + py)))
    if max(region.size) < 256:
        region = ImageOps.contain(region.resize((region.width * 2, region.height * 2), Image.LANCZOS), (1024, 1024))
    region.convert("RGB").save(out, "JPEG", quality=92)
    return out


def assess_prefix(client: dict, context: dict) -> str:
    marks = registry.digest(client)
    return f"""You are the assessment engine of Marksweep, assisting (not replacing) an IP enforcement lawyer.
ACTING FOR: {client["name"]} ({client["short"]}), enforcement matter. Jurisdictions: {context.get("jurisdictions") or client.get("jurisdictions")}.
Goods seen: {context.get("goods") or "not stated"}. Field notes: {context.get("notes") or "(none)"}.

CLIENT MARKS (the next image is a numbered contact sheet of their official register drawings):
{marks}

You will then get ONE element cut out of a photograph taken in the field. Compare it with the client's marks only.
Return ONLY JSON with these keys:
- "seen": what the element shows, one sentence, no legal words
- "text_read": any text visible on it, or ""
- "candidate_marks": list of client mark ids the element could be confused with, [] if none
- "sub_scores": for each of visual, aural, conceptual, goods_services, distinctiveness, bad_faith an object
  {{"score": 0-100 (0 no concern, 100 maximal), "rationale": one sentence, "na": true only for aural when purely figurative}}
  visual = the specific get-up against the closest client mark (sharing only a genus such as any red square or any flower is low, <= 35);
  aural = word elements against the client's word marks; conceptual = the idea conveyed; goods_services = goods seen against
  the matched marks' Nice classes; distinctiveness = reputation of the matched mark, only when a mark is meaningfully similar,
  else <= 25; bad_faith = signs of deliberate imitation (altered letters that keep the look, copied trade dress with a changed name).
- "narrative": 2 or 3 sentences for a lawyer using "highly concerning", "worth checking" or "low concern"; never "infringes"; no em dashes
- "primary_match": one client mark id or ""
If "candidate_marks" is empty, every score must be <= 25 and the narrative must say the element is not the client's concern."""


def assess_prompt(client: dict, element_index: int, n_elements: int, context: dict) -> list:
    """Ordered parts: static prefix + mark sheet first (same for every element, so the server reuses its KV cache),
    then the short per-element text and the crop."""
    return [assess_prefix(client, context), registry.mark_sheet(client),
            f"Element {element_index} of {n_elements}. Assess the following image and return the JSON."]


def run_sweep(photo_path: Path, client_id: str, context: dict | None = None, data_dir: Path | None = None,
              concepts: list[str] | None = None, progress=None, fixture: dict | None = None) -> dict:
    """Full pipeline. `fixture` replays recorded API outputs (demo without a key, tests)."""
    context = context or {}
    data_dir = data_dir or config.data_dir()
    sweep_id = context.get("sweep_id") or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    sdir = data_dir / "sweeps" / sweep_id
    (sdir / "crops").mkdir(parents=True, exist_ok=True)
    ledger = Ledger(sdir / "ledger.jsonl")
    say = progress or (lambda *_: None)

    client = registry.client(client_id)
    photo = ImageOps.exif_transpose(Image.open(photo_path)).convert("RGB")
    saved = sdir / ("photo" + photo_path.suffix.lower().replace(".jpeg", ".jpg"))
    if saved.suffix not in {".jpg", ".png", ".webp"}:
        saved = sdir / "photo.jpg"
    photo.save(saved)
    photo_hash = sha256(saved)
    say("photo", {"hash": photo_hash, "size": photo.size})

    record = {
        "id": sweep_id, "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "client": {"id": client_id, "name": client["name"]}, "context": context,
        "photo": {"file": saved.name, "sha256": photo_hash, "width": photo.width, "height": photo.height},
        "models": {"segment": config.SAM_MODEL if config.segmenter() == "sam" else config.SPARK_MODEL + " (grounding)", "assess": config.SPARK_MODEL},
        "mode": "fixture" if fixture else "live",
        "elements": [], "status": "running",
    }

    concepts = concepts or (CONCEPTS if (fixture or config.segmenter() == "sam") else [VLM_CONCEPT])
    sam_results = []
    for concept in concepts:
        say("segment", {"concept": concept})
        if fixture:
            res = fixture["segment"].get(concept) or {"concept": concept, "outcome": "completed", "boxes": [], "masks": []}
            with ledger.call(config.SAM_MODEL, "segment", concept=concept, replay=True) as e:
                e["objects"] = len(res["boxes"])
        elif config.segmenter() == "sam":
            res = meta.segment(saved, concept, ledger)
        else:
            res = meta.segment_vlm(saved, concept, ledger, photo.size)
        sam_results.append(res)
        say("segmented", {"concept": concept, "objects": len(res["boxes"])})
    (sdir / "sam.json").write_text(json.dumps(sam_results, indent=1))

    boxes = merge_boxes(sam_results, photo.width, photo.height)
    if fixture and fixture.get("boxes"):  # replay exactly the elements that were assessed when the fixture was recorded
        boxes = [dict(b) for b in fixture["boxes"]]
    max_el = 0 if fixture else int(__import__("os").environ.get("MARKSWEEP_MAX_ELEMENTS", "0") or 0)
    if max_el and len(boxes) > max_el:
        boxes = sorted(boxes, key=lambda b: -(b["right"] - b["left"]) * (b["bottom"] - b["top"]))[:max_el]
        boxes.sort(key=lambda r: (r["top"] // 50, r["left"]))
    say("elements", {"count": len(boxes)})

    mark_images = registry.mark_images(client)
    for i, box in enumerate(boxes, 1):
        cpath = crop(photo, box, sdir / "crops" / f"element-{i:02d}.jpg")
        el = {"index": i, "box": {k: box[k] for k in ("left", "top", "right", "bottom")},
              "found_as": box.get("label") or box.get("concept"), "kind": box.get("kind"), "sam_confidence": box.get("confidence"),
              "crop": f"crops/{cpath.name}", "crop_sha256": sha256(cpath)}
        say("assess", {"index": i, "of": len(boxes)})
        try:
            if fixture:
                out = fixture["assess"][i - 1]
                with ledger.call(config.SPARK_MODEL, "assess", replay=True):
                    pass
            else:
                parts = assess_prompt(client, i, len(boxes), context)
                if config.segmenter() == "sam":  # API route: separate drawings instead of the sheet
                    parts = [parts[0].replace("the next image is a numbered contact sheet of their official register drawings",
                                              "the following images are their official register drawings, in this order"),
                             *mark_images, parts[2]]
                out = meta.spark_json(parts, [cpath], ASSESS_SCHEMA, ledger, purpose="assess",
                                      max_tokens=int(__import__("os").environ.get("MARKSWEEP_ASSESS_TOKENS", "3000")),
                                      prefix='{"seen": "', thought="I compare this element with the numbered client marks on the sheet "
                                      "and fill every key of the JSON with honest scores and one-sentence reasons.")
            el.update(_normalise(out))
        except Exception as exc:  # noqa: BLE001
            el["error"] = f"{type(exc).__name__}: {exc}"[:300]
            el["band"] = "unscored"
        record["elements"].append(el)
        say("assessed", {"index": i, "band": el.get("band"), "score": el.get("score")})

    record["summary"] = summarise(record["elements"])
    record["ledger"] = ledger.entries
    record["status"] = "complete"
    (sdir / "record.json").write_text(json.dumps(record, indent=1, ensure_ascii=False))
    say("done", {"id": sweep_id})
    return record


def _normalise(out: dict) -> dict:
    subs = out.get("sub_scores") or {}
    breakdown = []
    for d in DIMENSIONS:
        s = subs.get(d["key"]) or {}
        breakdown.append({"key": d["key"], "label": d["label"], "weight": d["weight"],
                          "score": max(0, min(100, int(s.get("score", 0) or 0))),
                          "rationale": str(s.get("rationale", "")), "na": bool(s.get("na", False))})
    score = roll_up(breakdown)
    return {"seen": out.get("seen", ""), "text_read": out.get("text_read", ""),
            "candidate_marks": out.get("candidate_marks") or [], "breakdown": breakdown,
            "score": score, "band": band_for(score), "narrative": out.get("narrative", ""),
            "primary_match": out.get("primary_match", "")}


def summarise(elements: list[dict]) -> dict:
    bands = {"red": 0, "amber": 0, "green": 0, "unscored": 0}
    for e in elements:
        bands[e.get("band", "unscored")] = bands.get(e.get("band", "unscored"), 0) + 1
    top = max((e for e in elements if "score" in e), key=lambda e: e["score"], default=None)
    return {"elements": len(elements), "bands": bands,
            "highest": {"index": top["index"], "score": top["score"], "band": top["band"]} if top else None}


def load_record(sweep_id: str, data_dir: Path | None = None) -> dict | None:
    p = (data_dir or config.data_dir()) / "sweeps" / sweep_id / "record.json"
    return json.loads(p.read_text()) if p.exists() else None


def list_records(data_dir: Path | None = None) -> list[dict]:
    base = (data_dir or config.data_dir()) / "sweeps"
    out = []
    for p in sorted(base.glob("*/record.json"), reverse=True):
        r = json.loads(p.read_text())
        out.append({k: r.get(k) for k in ("id", "created", "client", "summary", "mode", "status", "context")})
    return out
