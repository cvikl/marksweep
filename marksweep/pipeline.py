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


def assess_prompt(client: dict, element_index: int, n_elements: int, context: dict) -> str:
    marks = registry.digest(client)
    return f"""You are the assessment engine of Marksweep, assisting (not replacing) an IP enforcement
lawyer. The FIRST image is one element cut out of a photograph taken in the field (a market stall, shop
shelf or online listing). The images AFTER it are the official register drawings of the client's marks,
in the order listed below. Compare the element with the client's registered marks only.

ACTING FOR: {client["name"]} ({client["short"]}), enforcement matter. Jurisdictions in scope: {context.get("jurisdictions") or client.get("jurisdictions")}.
Field notes from the investigator: {context.get("notes") or "(none)"}. Goods seen: {context.get("goods") or "not stated"}.

CLIENT MARKS (register image follows the element image, same order):
{marks}

Element {element_index} of {n_elements}. First say what you actually see ("seen", one sentence, no legal
words) and transcribe any text ("text_read"). Then list the client mark ids that the element could be
confused with ("candidate_marks", [] if the element has nothing to do with the client's marks).

Score each dimension 0-100 (0 = no concern, 100 = maximal concern) with a one or two sentence rationale
grounded only in what is visible and the register data above; never invent registrations:
1. "visual": line structure, proportions, arrangement, colourway, dominant elements against the closest
   client mark, comparing the SPECIFIC get-up. Sharing only a genus (any red square, any flower, any
   checkerboard) is low (<= 35). A near copy of the specific device is high.
2. "aural": phonetic similarity of any word element to the client's word marks; "na": true when the
   element is purely figurative.
3. "conceptual": the idea conveyed; commonplace ideas count for little; the same specific stylised
   concept counts for much.
4. "goods_services": proximity of the goods seen to the Nice classes of the matched client marks;
   identical goods high, neighbouring moderate, distant low unless the mark's fame makes free riding
   plausible and the sign is close.
5. "distinctiveness": reputation of the MATCHED client mark; only when a client mark is meaningfully
   similar (visual or conceptual > 35). If nothing matches, <= 25 and say so.
6. "bad_faith": signs of deliberate imitation visible in the element itself (altered letters that keep
   the look, "LEPIN" for LEGO style substitutions, copied trade dress with a changed name). Low if none.

If "candidate_marks" is empty, every score must be <= 25 and the narrative must say the element is not
the client's concern. Never write "infringes" or any legal conclusion; use "highly concerning", "worth
checking" or "low concern", pending the lawyer's view. No em dashes.

Return ONLY JSON matching the schema: seen, text_read, candidate_marks, sub_scores (visual, aural,
conceptual, goods_services, distinctiveness, bad_faith each with score, rationale, na), narrative
(2 to 4 sentences), primary_match (one client mark id or "")."""


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
        "models": {"segment": config.SAM_MODEL, "assess": config.SPARK_MODEL},
        "mode": "fixture" if fixture else "live",
        "elements": [], "status": "running",
    }

    concepts = concepts or CONCEPTS
    sam_results = []
    for concept in concepts:
        say("segment", {"concept": concept})
        if fixture:
            res = fixture["segment"].get(concept) or {"concept": concept, "outcome": "completed", "boxes": [], "masks": []}
            with ledger.call(config.SAM_MODEL, "segment", concept=concept, replay=True) as e:
                e["objects"] = len(res["boxes"])
        else:
            res = meta.segment(saved, concept, ledger)
        sam_results.append(res)
        say("segmented", {"concept": concept, "objects": len(res["boxes"])})
    (sdir / "sam.json").write_text(json.dumps(sam_results, indent=1))

    boxes = merge_boxes(sam_results, photo.width, photo.height)
    say("elements", {"count": len(boxes)})

    mark_images = registry.mark_images(client)
    for i, box in enumerate(boxes, 1):
        cpath = crop(photo, box, sdir / "crops" / f"element-{i:02d}.jpg")
        el = {"index": i, "box": {k: box[k] for k in ("left", "top", "right", "bottom")},
              "found_as": box["concept"], "sam_confidence": box.get("confidence"),
              "crop": f"crops/{cpath.name}", "crop_sha256": sha256(cpath)}
        say("assess", {"index": i, "of": len(boxes)})
        try:
            if fixture:
                out = fixture["assess"][i - 1]
                with ledger.call(config.SPARK_MODEL, "assess", replay=True):
                    pass
            else:
                out = meta.spark_json(assess_prompt(client, i, len(boxes), context), [cpath, *mark_images],
                                      ASSESS_SCHEMA, ledger, purpose="assess")
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
