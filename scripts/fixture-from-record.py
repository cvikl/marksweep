"""Re-save a demo fixture from an existing sweep record: python scripts/fixture-from-record.py <sweep_id> <demo_name>"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from marksweep import config
from marksweep.fixtures import record_fixture

sweep_id, name = sys.argv[1], sys.argv[2]
sdir = config.data_dir() / "sweeps" / sweep_id
rec = json.loads((sdir / "record.json").read_text())
sam = json.loads((sdir / "sam.json").read_text())
assess = [{"seen": e.get("seen"), "text_read": e.get("text_read"), "candidate_marks": e.get("candidate_marks"),
           "sub_scores": {b["key"]: {"score": b["score"], "rationale": b["rationale"], "na": b["na"]} for b in e.get("breakdown", [])},
           "narrative": e.get("narrative"), "primary_match": e.get("primary_match")} for e in rec["elements"]]
boxes = [{**e["box"], "concept": e.get("found_as"), "label": e.get("found_as"), "kind": e.get("kind"),
          "object_id": str(e["index"]), "confidence": e.get("sam_confidence")} for e in rec["elements"]]
d = record_fixture(name, sdir / rec["photo"]["file"], sam, assess,
                   {"recorded_from": rec["id"], "models": rec["models"], "boxes": boxes,
                    "ledger": [{k: l.get(k) for k in ("model", "purpose", "ms", "prompt_tokens", "completion_tokens", "timings")} for l in rec["ledger"]]})
print("fixture", d, len(assess), "elements")
