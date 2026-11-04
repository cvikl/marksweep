"""Thin client over the Meta Model API (https://api.meta.ai/v1).

Three models, three jobs:
  sam-3.1          finds and masks every candidate mark in the photo (Responses API, streamed, decoded by meta_sam_parser)
  muse-spark-1.3   reads each crop with the client's registered marks and scores the six global-assessment dimensions
  muse-image-1.0   (optional) renders the synthetic demo scenes
"""
from __future__ import annotations

import asyncio
import base64
import json
import mimetypes
from contextlib import aclosing
from pathlib import Path
from typing import Any, AsyncIterable, AsyncIterator

from openai import AsyncOpenAI, OpenAI

from . import config
from .ledger import Ledger


def _client() -> OpenAI:
    return OpenAI(base_url=config.BASE_URL, api_key=config.api_key())


def _aclient() -> AsyncOpenAI:
    return AsyncOpenAI(base_url=config.BASE_URL, api_key=config.api_key())


def data_url(path: Path) -> str:
    mt = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    return f"data:{mt};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


# ----------------------------------------------------------------------------- SAM 3.1

async def _events(stream: AsyncIterable[Any]) -> AsyncIterator[dict]:
    """SDK events -> plain dicts; synthesise response.output_text.done from content_part.done
    (the API streams the latter, the parser closes a lane on the former)."""
    done: set[tuple] = set()
    async for ev in stream:
        d = ev.model_dump() if hasattr(ev, "model_dump") else dict(ev)
        lane = (d.get("item_id"), d.get("output_index"), d.get("content_index"))
        if d.get("type") == "response.output_text.done":
            if lane not in done:
                done.add(lane)
                yield d
            continue
        yield d
        part = d.get("part")
        if d.get("type") == "response.content_part.done" and lane not in done and isinstance(part, dict) \
                and part.get("type") == "output_text" and isinstance(part.get("text"), str):
            done.add(lane)
            yield {"type": "response.output_text.done", "item_id": d.get("item_id"),
                   "output_index": d.get("output_index"), "content_index": d.get("content_index"),
                   "text": part["text"]}


async def _segment_async(image: Path, concept: str) -> dict:
    from meta_sam_parser import image_segmentation_format, parse_responses_stream
    async with _aclient() as api:
        stream = await api.responses.create(
            model=config.SAM_MODEL, stream=True,
            input=[{"type": "message", "role": "user",
                    "content": [{"type": "input_text", "text": concept},
                                {"type": "input_image", "image_url": data_url(image)}]}],
        )
        async with stream, aclosing(_events(stream)) as evs:
            result = await parse_responses_stream(evs, image_segmentation_format()).final_result()
    return _sam_result_to_dict(result, concept)


def _sam_result_to_dict(result, concept: str) -> dict:
    """Keep boxes and mask payloads; masks stay encoded (decode on demand with meta_sam_parser)."""
    boxes, masks = [], []
    for rec in result.records:
        if rec.kind == "box":
            boxes.append({"object_id": str(rec.object_id), "left": rec.left, "top": rec.top,
                          "right": rec.right, "bottom": rec.bottom,
                          "confidence": getattr(rec, "confidence", None)})
        elif rec.kind == "mask":
            m = rec.mask
            masks.append({"object_id": str(rec.object_id), "encoding": m.encoding, "width": m.width,
                          "height": m.height, "payload": m.payload,
                          "confidence": getattr(rec, "confidence", None)})
    media = result.media
    return {"concept": concept, "outcome": result.outcome.status,
            "media": {"width": getattr(media, "width", None), "height": getattr(media, "height", None)},
            "boxes": boxes, "masks": masks,
            "diagnostics": [{"severity": d.severity, "code": d.code, "message": d.message} for d in result.diagnostics]}


def segment(image: Path, concept: str, ledger: Ledger | None = None) -> dict:
    """One SAM 3.1 request: a short noun phrase names the thing to find ("brand logo")."""
    ledger = ledger or Ledger()
    with ledger.call(config.SAM_MODEL, "segment", concept=concept, image=image.name) as entry:
        out = asyncio.run(_segment_async(image, concept))
        entry["objects"] = len(out["boxes"])
        entry["outcome"] = out["outcome"]
        return out


# ----------------------------------------------------------------------------- Muse Spark

def spark_json(prompt: str, images: list[Path] | None = None, schema: dict | None = None,
               ledger: Ledger | None = None, purpose: str = "assess", max_tokens: int = 1800,
               reasoning_effort: str | None = None) -> dict:
    """Vision + structured JSON from Muse Spark through the chat completions surface."""
    ledger = ledger or Ledger()
    content: list[dict] = [{"type": "text", "text": prompt}]
    for p in images or []:
        content.append({"type": "image_url", "image_url": {"url": data_url(p)}})
    kwargs: dict[str, Any] = {"model": config.SPARK_MODEL,
                              "messages": [{"role": "user", "content": content}],
                              "max_tokens": max_tokens}
    if schema:
        kwargs["response_format"] = {"type": "json_schema",
                                     "json_schema": {"name": "marksweep", "schema": schema, "strict": False}}
    else:
        kwargs["response_format"] = {"type": "json_object"}
    if reasoning_effort:
        kwargs["reasoning_effort"] = reasoning_effort
    with ledger.call(config.SPARK_MODEL, purpose, images=len(images or [])) as entry:
        resp = _client().chat.completions.create(**kwargs)
        ledger.usage(entry, resp)
        text = resp.choices[0].message.content or ""
        return _loads(text)


def _loads(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):]
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


# ----------------------------------------------------------------------------- Muse Image

def generate_image(prompt: str, out: Path, ledger: Ledger | None = None) -> Path:
    ledger = ledger or Ledger()
    with ledger.call(config.IMAGE_MODEL, "render-scene") as entry:
        resp = _client().images.generate(model=config.IMAGE_MODEL, prompt=prompt, n=1)
        item = resp.data[0]
        if getattr(item, "b64_json", None):
            out.write_bytes(base64.b64decode(item.b64_json))
        elif getattr(item, "url", None):
            import httpx
            out.write_bytes(httpx.get(item.url, timeout=120).content)
        else:
            raise RuntimeError("image response had neither b64_json nor url")
        entry["bytes"] = out.stat().st_size
    return out


# ----------------------------------------------------------------------------- VLM grounding fallback

GROUND_SCHEMA = {
    "type": "object",
    "properties": {"elements": {"type": "array", "items": {"type": "object", "properties": {
        "label": {"type": "string"}, "kind": {"type": "string", "enum": ["logo", "brand name", "pattern", "label"]},
        "box": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4,
                "description": "[left, top, right, bottom] as fractions 0..1 of the image width and height"}},
        "required": ["label", "kind", "box"]}}},
    "required": ["elements"],
}


def segment_vlm(image: Path, concept: str, ledger: Ledger | None = None, size: tuple[int, int] | None = None) -> dict:
    """When SAM 3.1 is not reachable: ask the vision model for the boxes of every <concept> in the photo.
    Returns the same shape as segment(): boxes in pixel coordinates, no masks."""
    ledger = ledger or Ledger()
    if size is None:
        from PIL import Image
        with Image.open(image) as im:
            size = im.size
    w, h = size
    prompt = (f"Find every \"{concept}\" in this photograph. Return JSON {{\"elements\": [{{\"label\", \"kind\", \"box\"}}]}} "
              f"where box is [left, top, right, bottom] as fractions of the image width and height (0 to 1), tight around "
              f"the element. Include every instance, even partly hidden or small ones. Nothing else.")
    out = spark_json(prompt, [image], GROUND_SCHEMA, ledger, purpose="ground", max_tokens=1200)
    boxes = []
    for i, e in enumerate(out.get("elements") or [], 1):
        try:
            l, t, r, b = [float(x) for x in e["box"]]
        except Exception:  # noqa: BLE001
            continue
        if max(l, t, r, b) > 1.5:  # model answered in pixels
            l, t, r, b = l / w, t / h, r / w, b / h
        boxes.append({"object_id": str(i), "left": l * w, "top": t * h, "right": r * w, "bottom": b * h,
                      "confidence": None, "label": e.get("label"), "kind": e.get("kind")})
    return {"concept": concept, "outcome": "completed", "media": {"width": w, "height": h}, "boxes": boxes,
            "masks": [], "diagnostics": [], "method": "vlm-grounding"}
