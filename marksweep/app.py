"""Marksweep web app: upload a field photo, watch the sweep run, read the record."""
from __future__ import annotations

import asyncio
import json
import queue
import shutil
import threading
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import __version__, config, pipeline, registry
from .fixtures import load_fixture

app = FastAPI(title="Marksweep", version=__version__)
STATIC = config.root_dir() / "static"
JOBS: dict[str, dict] = {}
MAX_UPLOAD = 12 * 1024 * 1024


def _check_token(request: Request) -> None:
    tok = config.public_token()
    if tok and request.headers.get("x-marksweep-token") != tok and request.query_params.get("token") != tok:
        raise HTTPException(401, "this host needs the operator token for new sweeps")


@app.get("/healthz")
def healthz():
    return {"ok": True, "version": __version__, "mode": "fixture" if config.fixture_mode() else "live",
            "models": {"segment": config.SAM_MODEL, "assess": config.SPARK_MODEL}}


@app.get("/api/clients")
def clients():
    return registry.public()


@app.get("/api/sweeps")
def sweeps():
    return pipeline.list_records()


@app.get("/api/sweeps/{sweep_id}")
def sweep(sweep_id: str):
    rec = pipeline.load_record(_safe(sweep_id))
    if not rec:
        raise HTTPException(404, "no such sweep")
    return rec


@app.get("/api/sweeps/{sweep_id}/file/{name:path}")
def sweep_file(sweep_id: str, name: str):
    base = (config.data_dir() / "sweeps" / _safe(sweep_id)).resolve()
    p = (base / name).resolve()
    if base not in p.parents or not p.is_file():
        raise HTTPException(404)
    return FileResponse(p)


@app.get("/marks/{name}")
def mark_image(name: str):
    p = registry.marks_dir() / Path(name).name
    if not p.is_file():
        raise HTTPException(404)
    return FileResponse(p)


@app.post("/api/sweeps")
async def start_sweep(request: Request, photo: UploadFile = File(...), client: str = Form(...),
                      notes: str = Form(""), goods: str = Form(""), jurisdictions: str = Form(""),
                      demo: str = Form("")):
    registry.client(client)
    fixture_for = load_fixture(demo) if demo else None
    if not fixture_for:  # replaying a recorded demo costs nothing; a new photo on a public host needs the operator token
        _check_token(request)
    tmpdir = config.data_dir() / "incoming"
    tmpdir.mkdir(parents=True, exist_ok=True)
    suffix = Path(photo.filename or "photo.jpg").suffix.lower() or ".jpg"
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(400, "jpg, png or webp only")
    tmp = tmpdir / f"{uuid.uuid4().hex}{suffix}"
    size = 0
    with tmp.open("wb") as fh:
        while chunk := await photo.read(1 << 20):
            size += len(chunk)
            if size > MAX_UPLOAD:
                fh.close(); tmp.unlink(missing_ok=True)
                raise HTTPException(413, "photo over 12 MB")
            fh.write(chunk)
    fixture = fixture_for
    if config.fixture_mode() and not fixture:
        raise HTTPException(503, "no MODEL_API_KEY on this host; run one of the recorded demo sweeps")
    job_id = uuid.uuid4().hex[:10]
    q: queue.Queue = queue.Queue()
    JOBS[job_id] = {"queue": q, "done": False, "sweep_id": None}
    ctx = {"notes": notes.strip(), "goods": goods.strip(), "jurisdictions": jurisdictions.strip(), "sweep_id": job_id}

    def work():
        try:
            rec = pipeline.run_sweep(tmp, client, ctx, progress=lambda ev, d: q.put({"event": ev, **d}), fixture=fixture)
            JOBS[job_id]["sweep_id"] = rec["id"]
        except Exception as exc:  # noqa: BLE001
            q.put({"event": "error", "message": f"{type(exc).__name__}: {exc}"[:400]})
        finally:
            tmp.unlink(missing_ok=True)
            JOBS[job_id]["done"] = True
            q.put(None)

    threading.Thread(target=work, daemon=True).start()
    return {"job": job_id}


@app.get("/api/jobs/{job_id}/events")
async def job_events(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404)

    async def gen():
        while True:
            try:
                item = job["queue"].get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.25)
                continue
            if item is None:
                yield f"data: {json.dumps({'event': 'closed', 'sweep_id': job['sweep_id']})}\n\n"
                return
            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/api/demos")
def demos():
    from .fixtures import list_demos
    return list_demos()


@app.get("/", response_class=HTMLResponse)
def index():
    return (STATIC / "index.html").read_text(encoding="utf-8")


@app.get("/sweeps/{sweep_id}", response_class=HTMLResponse)
def sweep_page(sweep_id: str):
    return (STATIC / "record.html").read_text(encoding="utf-8")


app.mount("/static/demos", StaticFiles(directory=str(config.fixtures_dir() / "demos")), name="demos")
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


def _safe(s: str) -> str:
    if not s or "/" in s or ".." in s:
        raise HTTPException(400)
    return s
