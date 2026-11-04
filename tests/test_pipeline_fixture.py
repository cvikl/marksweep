"""End-to-end in fixture mode: a synthetic photo, a recorded SAM result and two recorded assessments."""
import json
from pathlib import Path

from PIL import Image, ImageDraw

from marksweep import pipeline


def _photo(tmp: Path) -> Path:
    im = Image.new("RGB", (800, 600), (230, 225, 210))
    d = ImageDraw.Draw(im)
    d.rectangle((100, 100, 300, 300), fill=(200, 30, 30)); d.text((150, 190), "LEPIN", fill="white")
    d.rectangle((500, 350, 700, 420), fill=(20, 20, 20)); d.text((540, 380), "BRICKS", fill="white")
    p = tmp / "stall.jpg"; im.save(p, "JPEG"); return p


def _fixture():
    sam = {"brand logo": {"concept": "brand logo", "outcome": "completed", "media": {"width": 800, "height": 600},
                          "boxes": [{"object_id": "1", "left": 100, "top": 100, "right": 300, "bottom": 300, "confidence": 0.9}],
                          "masks": [], "diagnostics": []},
           "printed brand name": {"concept": "printed brand name", "outcome": "completed", "media": {},
                                  "boxes": [{"object_id": "1", "left": 110, "top": 180, "right": 290, "bottom": 220},
                                            {"object_id": "2", "left": 500, "top": 350, "right": 700, "bottom": 420}],
                                  "masks": [], "diagnostics": []}}
    def sub(v, na=False):
        return {"score": v, "rationale": "r", "na": na}
    a1 = {"seen": "red square with white letters", "text_read": "LEPIN", "candidate_marks": ["lego_logo_uspto_73032292"],
          "sub_scores": {"visual": sub(85), "aural": sub(70), "conceptual": sub(60), "goods_services": sub(90), "distinctiveness": sub(95), "bad_faith": sub(80)},
          "narrative": "Highly concerning.", "primary_match": "lego_logo_uspto_73032292"}
    a2 = {"seen": "black label reading BRICKS", "text_read": "BRICKS", "candidate_marks": [],
          "sub_scores": {"visual": sub(10), "aural": sub(0, True), "conceptual": sub(10), "goods_services": sub(20), "distinctiveness": sub(10), "bad_faith": sub(5)},
          "narrative": "Low concern.", "primary_match": ""}
    a3 = dict(a2)
    return {"segment": sam, "assess": [a1, a2, a3]}


def test_fixture_sweep_writes_record(tmp_path):
    photo = _photo(tmp_path)
    rec = pipeline.run_sweep(photo, "lego", {"goods": "brick sets", "jurisdictions": "Hong Kong"}, data_dir=tmp_path / "data", fixture=_fixture())
    assert rec["status"] == "complete" and rec["mode"] == "fixture"
    # 3 SAM boxes: the two overlapping ones (IoU < 0.6, different shapes) both survive, plus the label
    assert len(rec["elements"]) == 3
    e1 = rec["elements"][0]
    assert e1["band"] == "red" and e1["score"] > 65 and e1["primary_match"] == "lego_logo_uspto_73032292"
    assert (tmp_path / "data" / "sweeps" / rec["id"] / e1["crop"]).exists()
    assert len(rec["photo"]["sha256"]) == 64 and len(e1["crop_sha256"]) == 64
    assert rec["summary"]["bands"]["red"] == 1 and rec["summary"]["highest"]["index"] == 1
    assert [l["model"] for l in rec["ledger"]][:2] == ["sam-3.1", "sam-3.1"]
    saved = json.loads((tmp_path / "data" / "sweeps" / rec["id"] / "record.json").read_text())
    assert saved["id"] == rec["id"]
    assert pipeline.list_records(tmp_path / "data")[0]["id"] == rec["id"]
