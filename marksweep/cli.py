"""marksweep CLI: serve, sweep, record a fixture, render a demo scene."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import config, pipeline


def _progress(ev: str, d: dict) -> None:
    line = {"photo": lambda: f"photo  sha256 {d['hash'][:16]}…  {d['size'][0]}x{d['size'][1]}",
            "segment": lambda: f"sam-3.1  looking for \"{d['concept']}\"",
            "segmented": lambda: f"         {d['objects']} object(s)",
            "elements": lambda: f"elements {d['count']} after merge",
            "assess": lambda: f"muse-spark  element {d['index']} of {d['of']}",
            "assessed": lambda: f"            {d.get('band')}  {d.get('score')}",
            "done": lambda: f"record {d['id']}"}.get(ev, lambda: f"{ev} {d}")()
    print(line, file=sys.stderr, flush=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="marksweep")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve"); s.add_argument("--port", type=int, default=8000); s.add_argument("--host", default="0.0.0.0")
    w = sub.add_parser("sweep", help="run one photo through the pipeline")
    w.add_argument("photo", type=Path); w.add_argument("--client", required=True)
    w.add_argument("--notes", default=""); w.add_argument("--goods", default=""); w.add_argument("--jurisdictions", default="")
    w.add_argument("--demo", default="", help="replay a recorded fixture instead of calling the API")
    w.add_argument("--save-fixture", default="", help="record this live run as fixtures/demos/<name>")
    w.add_argument("--concepts", default="", help="comma separated SAM phrases")
    r = sub.add_parser("render", help="render a synthetic demo scene with muse-image")
    r.add_argument("prompt"); r.add_argument("out", type=Path)
    a = ap.parse_args(argv)

    if a.cmd == "serve":
        import uvicorn
        uvicorn.run("marksweep.app:app", host=a.host, port=a.port, log_level="info")
        return 0
    if a.cmd == "render":
        from . import meta
        p = meta.generate_image(a.prompt, a.out)
        print(p)
        return 0
    if a.cmd == "sweep":
        fixture = None
        if a.demo:
            from .fixtures import load_fixture
            fixture = load_fixture(a.demo)
            if not fixture:
                print(f"no fixture {a.demo}", file=sys.stderr); return 2
        ctx = {"notes": a.notes, "goods": a.goods, "jurisdictions": a.jurisdictions}
        concepts = [c.strip() for c in a.concepts.split(",") if c.strip()] or None
        rec = pipeline.run_sweep(a.photo, a.client, ctx, progress=_progress, fixture=fixture, concepts=concepts)
        print(json.dumps(rec["summary"], indent=1))
        if a.save_fixture:
            from .fixtures import record_fixture
            sdir = config.data_dir() / "sweeps" / rec["id"]
            sam = json.loads((sdir / "sam.json").read_text())
            assess = [{"seen": e.get("seen"), "text_read": e.get("text_read"), "candidate_marks": e.get("candidate_marks"),
                       "sub_scores": {b["key"]: {"score": b["score"], "rationale": b["rationale"], "na": b["na"]} for b in e.get("breakdown", [])},
                       "narrative": e.get("narrative"), "primary_match": e.get("primary_match")} for e in rec["elements"]]
            d = record_fixture(a.save_fixture, sdir / rec["photo"]["file"], sam, assess,
                               {"client": a.client, "title": a.save_fixture, "notes": a.notes, "goods": a.goods,
                                "jurisdictions": a.jurisdictions, "recorded_from": rec["id"], "models": rec["models"]})
            print(f"fixture saved to {d}", file=sys.stderr)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
