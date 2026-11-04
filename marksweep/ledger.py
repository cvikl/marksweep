"""Run ledger: every model call with model, latency, tokens and purpose, so the
record shows exactly which Meta model did what."""
from __future__ import annotations

import json
import time
from contextlib import contextmanager
from pathlib import Path


class Ledger:
    def __init__(self, path: Path | None = None):
        self.path = path
        self.entries: list[dict] = []

    @contextmanager
    def call(self, model: str, purpose: str, **meta):
        t0 = time.perf_counter()
        entry = {"model": model, "purpose": purpose, "started": time.time(), **meta}
        try:
            yield entry
            entry["status"] = "ok"
        except Exception as exc:  # noqa: BLE001
            entry["status"] = "error"
            entry["error"] = f"{type(exc).__name__}: {exc}"[:400]
            raise
        finally:
            entry["ms"] = round((time.perf_counter() - t0) * 1000)
            self.entries.append(entry)
            if self.path:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with self.path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def usage(self, entry: dict, response) -> None:
        u = getattr(response, "usage", None)
        if u is None:
            return
        for k in ("input_tokens", "output_tokens", "prompt_tokens", "completion_tokens", "total_tokens"):
            v = getattr(u, k, None)
            if v is not None:
                entry[k] = v
