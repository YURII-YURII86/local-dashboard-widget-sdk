from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def renderer_name(contract: dict) -> str:
    renderer = contract.get("renderer")
    if isinstance(renderer, dict):
        return str(renderer.get("kind", "unknown"))
    return str(renderer or "unknown")


def main() -> int:
    widgets = []
    presets = []
    for path in sorted((ROOT / "examples" / "widgets").glob("*.json")):
        raw = read_json(path)
        widgets.append({"path": path.relative_to(ROOT).as_posix(), "contract": raw})
    for path in sorted((ROOT / "examples" / "presets").glob("*.json")):
        raw = read_json(path)
        presets.append({"path": path.relative_to(ROOT).as_posix(), "contract": raw})
    catalog = {
        "schema": "local-dashboard-widget-sdk.catalog-viewer-data.v1",
        "generatedFrom": ["examples/widgets", "examples/presets"],
        "summary": {
            "widgets": len(widgets),
            "presets": len(presets),
            "renderers": sorted({renderer_name(item["contract"]) for item in widgets + presets}),
        },
        "widgets": widgets,
        "presets": presets,
    }
    out = ROOT / "examples" / "catalog-viewer" / "catalog-data.js"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("window.LDW_CATALOG = " + json.dumps(catalog, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} widgets={len(widgets)} presets={len(presets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
