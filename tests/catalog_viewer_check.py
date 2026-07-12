from __future__ import annotations

import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def extract_catalog_data(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    prefix = "window.LDW_CATALOG = "
    if not text.startswith(prefix) or not text.rstrip().endswith(";"):
        raise SystemExit("catalog-data.js must assign window.LDW_CATALOG")
    return json.loads(text[len(prefix):].rstrip().rstrip(";"))


def png_size(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()
    if len(raw) < 33 or not raw.startswith(PNG_SIGNATURE):
        raise SystemExit("catalog screenshot is not valid PNG")
    if raw[12:16] != b"IHDR":
        raise SystemExit("catalog screenshot missing IHDR")
    return struct.unpack(">II", raw[16:24])


def main() -> int:
    viewer = ROOT / "examples" / "catalog-viewer"
    for rel in ["index.html", "viewer.css", "viewer.js", "catalog-data.js"]:
        if not (viewer / rel).is_file():
            raise SystemExit(f"missing examples/catalog-viewer/{rel}")
    html = (viewer / "index.html").read_text(encoding="utf-8")
    for marker in ["catalog-data.js", "viewer.js", "catalog-grid", "detail-json", "renderer-filter"]:
        if marker not in html:
            raise SystemExit(f"viewer html missing {marker}")
    js = (viewer / "viewer.js").read_text(encoding="utf-8")
    for marker in ["window.LDW_CATALOG", "window.LDW_CATALOG_VIEWER", "renderCards", "selectCard"]:
        if marker not in js:
            raise SystemExit(f"viewer js missing {marker}")
    data = extract_catalog_data(viewer / "catalog-data.js")
    if data.get("schema") != "local-dashboard-widget-sdk.catalog-viewer-data.v1":
        raise SystemExit("bad catalog viewer data schema")
    if data.get("summary", {}).get("widgets") < 2 or data.get("summary", {}).get("presets") < 1:
        raise SystemExit("catalog viewer data should include example widgets and presets")
    ids = {item["contract"]["id"] for item in data["widgets"] + data["presets"]}
    if {"cpu-load", "service-table", "stat-compact"} - ids:
        raise SystemExit(f"catalog viewer data missing expected ids: {ids}")
    screenshot = ROOT / "docs" / "assets" / "catalog-viewer-demo.png"
    width, height = png_size(screenshot)
    if width < 1000 or height < 700 or screenshot.stat().st_size < 50_000:
        raise SystemExit(f"bad catalog screenshot: {width}x{height} bytes={screenshot.stat().st_size}")
    print(f"catalog viewer ok widgets={data['summary']['widgets']} presets={data['summary']['presets']} screenshot={width}x{height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
