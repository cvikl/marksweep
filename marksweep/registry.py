"""The client's registered marks: the only thing an element is compared with.

Each record carries the office's own numbering so the lawyer can click through to the register. Every
number below was confirmed on the office register (USPTO TSDR, EUIPO eSearch, WIPO Madrid Monitor);
the drawings in fixtures/marks are the office images. Nothing here is invented. In production this is
the firm's own mark portfolio for the matter; here it is two demo clients."""
from __future__ import annotations

from pathlib import Path

from . import config

CLIENTS: dict[str, dict] = {
    "lego": {
        "name": "LEGO Juris A/S", "short": "LEGO", "jurisdictions": "Hong Kong, EU, US",
        "marks": [
            {"id": "lego_logo_uspto_73032292", "mark": "LEGO red square logo (white LEGO on red, yellow and black border)",
             "office": "USPTO", "number": "1026871", "classes": [28], "type": "figurative", "fame": "exceptional",
             "image": "lego_logo_uspto_73032292.png",
             "url": "https://tsdr.uspto.gov/#caseNumber=73032292&caseType=SERIAL_NO&searchType=statusSearch"},
            {"id": "lego_logo_wo_869258", "mark": "LEGO logo (international)", "office": "WIPO", "number": "869258",
             "classes": [9, 16, 25, 28, 41], "type": "figurative", "fame": "exceptional", "image": "lego_logo_wo_869258.jpg",
             "url": "https://www3.wipo.int/madrid/monitor/en/showData.jsp?ID=ROM.869258"},
            {"id": "lego_word_uspto_73369522", "mark": "LEGO (word)", "office": "USPTO", "number": "1248936",
             "classes": [16, 20, 22, 25], "type": "word", "fame": "exceptional", "image": "lego_word_uspto_73369522.png",
             "url": "https://tsdr.uspto.gov/#caseNumber=73369522&caseType=SERIAL_NO&searchType=statusSearch"},
            {"id": "lego_minifigure_em_000050450", "mark": "LEGO minifigure (3-D shape mark)", "office": "EUIPO",
             "number": "000050450", "classes": [9, 25, 28], "type": "3-D", "fame": "exceptional",
             "image": "lego_minifigure_em_000050450.png",
             "url": "https://euipo.europa.eu/eSearch/#details/trademarks/000050450"},
        ],
    },
    "lv": {
        "name": "Louis Vuitton Malletier", "short": "LV", "jurisdictions": "Hong Kong, EU, US",
        "marks": [
            {"id": "lv_flower_em_000311985", "mark": "LV Monogram four-petal flower device", "office": "EUIPO",
             "number": "000311985", "classes": [14, 18, 25], "type": "figurative", "fame": "exceptional",
             "image": "lv_flower_em_000311985.png", "url": "https://euipo.europa.eu/eSearch/#details/trademarks/000311985"},
            {"id": "lv_letters_uspto_1938808", "mark": "LV interlocking letters device", "office": "USPTO",
             "number": "1938808", "classes": [14], "type": "figurative", "fame": "exceptional",
             "image": "lv_letters_uspto_1938808.png",
             "url": "https://tsdr.uspto.gov/#caseNumber=74618480&caseType=SERIAL_NO&searchType=statusSearch"},
            {"id": "lv_monogram_canvas_uspto_1770131", "mark": "LV Monogram canvas (repeating LV, flowers, quatrefoils)",
             "office": "USPTO", "number": "1770131", "classes": [25], "type": "trade dress", "fame": "exceptional",
             "image": "lv_monogram_canvas_uspto_1770131.png",
             "url": "https://tsdr.uspto.gov/#caseNumber=74148017&caseType=SERIAL_NO&searchType=statusSearch"},
            {"id": "lv_word_uspto_1045932", "mark": "LOUIS VUITTON (word)", "office": "USPTO", "number": "1045932",
             "classes": [18], "type": "word", "fame": "high", "image": "lv_word_uspto_1045932.png",
             "url": "https://tsdr.uspto.gov/#caseNumber=73060441&caseType=SERIAL_NO&searchType=statusSearch"},
        ],
    },
}


def client(client_id: str) -> dict:
    if client_id not in CLIENTS:
        raise KeyError(f"unknown client {client_id!r}; known: {sorted(CLIENTS)}")
    return CLIENTS[client_id]


def marks_dir() -> Path:
    return config.fixtures_dir() / "marks"


def mark_images(c: dict) -> list[Path]:
    return [marks_dir() / m["image"] for m in c["marks"]]


def digest(c: dict) -> str:
    lines = []
    for i, m in enumerate(c["marks"], 1):
        lines.append(f'{i}. id={m["id"]}: {m["mark"]}; {m["office"]} {m["number"]}; Nice classes {m["classes"]}; '
                     f'{m["type"]} mark; distinctiveness {m["fame"]}')
    return "\n".join(lines)


def public() -> list[dict]:
    return [{"id": k, "name": v["name"], "short": v["short"], "jurisdictions": v["jurisdictions"],
             "marks": [{k2: m[k2] for k2 in ("id", "mark", "office", "number", "classes", "type", "fame", "image", "url")}
                       for m in v["marks"]]} for k, v in CLIENTS.items()]


def mark_sheet(c: dict, out_dir: Path | None = None) -> Path:
    """One labelled contact sheet of the client's register drawings (numbered as in digest())."""
    from PIL import Image, ImageDraw, ImageOps
    out_dir = out_dir or (config.data_dir() / "sheets")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{c['short'].lower()}-marks.jpg"
    if out.exists():
        return out
    tiles = []
    for i, m in enumerate(c["marks"], 1):
        im = Image.open(marks_dir() / m["image"]).convert("RGB")
        im = ImageOps.contain(im, (360, 300))
        tile = Image.new("RGB", (400, 360), "white")
        tile.paste(im, ((400 - im.width) // 2, 20 + (300 - im.height) // 2))
        d = ImageDraw.Draw(tile)
        d.text((12, 8), f"{i}. {m['office']} {m['number']}", fill="black")
        d.text((12, 336), m["mark"][:48], fill="black")
        tiles.append(tile)
    sheet = Image.new("RGB", (400 * len(tiles), 360), "white")
    for i, t in enumerate(tiles):
        sheet.paste(t, (400 * i, 0))
    sheet.save(out, "JPEG", quality=90)
    return out
