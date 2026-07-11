from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

VALID_STATUSES = {"draft", "lab", "production", "deprecated"}
VALID_SOURCE_KINDS = {"local-json", "http-json", "static", "computed", "custom"}
VALID_RENDERERS = {"stat", "table", "timeseries", "gauge", "log-timeline", "status-history", "custom"}
VALID_LEVELS = {"ok", "info", "warn", "bad"}
ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,62}$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+([-+][A-Za-z0-9.-]+)?$")


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class ValidationResult:
    path: str
    kind: str
    id: str
    status: str


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"{path}: invalid JSON: {exc}") from exc


def require_obj(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    return value


def require_str(obj: dict[str, Any], key: str, *, label: str = "object") -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label}.{key} must be a non-empty string")
    return value.strip()


def require_int(obj: dict[str, Any], key: str, *, label: str = "object", default: int | None = None, min_value: int | None = None) -> int:
    if key not in obj:
        if default is not None:
            return default
        raise ContractError(f"{label}.{key} is required")
    value = obj[key]
    if not isinstance(value, int):
        raise ContractError(f"{label}.{key} must be an integer")
    if min_value is not None and value < min_value:
        raise ContractError(f"{label}.{key} must be >= {min_value}")
    return value


def validate_id(value: str, label: str = "id") -> None:
    if not ID_RE.fullmatch(value):
        raise ContractError(f"{label} must match {ID_RE.pattern}: {value}")


def validate_tags(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ContractError("tags must be a list")
    out: list[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ContractError(f"tags[{i}] must be a non-empty string")
        tag = item.strip()
        validate_id(tag, label=f"tags[{i}]")
        out.append(tag)
    return out


def validate_source(source: Any) -> None:
    obj = require_obj(source, "source")
    kind = require_str(obj, "kind", label="source")
    if kind not in VALID_SOURCE_KINDS:
        raise ContractError(f"source.kind must be one of {sorted(VALID_SOURCE_KINDS)}")
    if kind in {"local-json", "http-json", "computed"}:
        require_str(obj, "path", label="source")
    if kind == "http-json":
        require_str(obj, "url", label="source")
    if "refreshMs" in obj:
        require_int(obj, "refreshMs", label="source", min_value=250)


def validate_thresholds(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, list):
        raise ContractError("renderer.thresholds must be a list")
    for i, item in enumerate(value):
        obj = require_obj(item, f"renderer.thresholds[{i}]")
        level = require_str(obj, "level", label=f"renderer.thresholds[{i}]")
        if level not in VALID_LEVELS:
            raise ContractError(f"renderer.thresholds[{i}].level must be one of {sorted(VALID_LEVELS)}")
        if "gte" not in obj and "lte" not in obj:
            raise ContractError(f"renderer.thresholds[{i}] must define gte or lte")


def validate_renderer(renderer: Any) -> None:
    obj = require_obj(renderer, "renderer")
    kind = require_str(obj, "kind", label="renderer")
    if kind not in VALID_RENDERERS:
        raise ContractError(f"renderer.kind must be one of {sorted(VALID_RENDERERS)}")
    if kind in {"stat", "gauge"}:
        require_str(obj, "valuePath", label="renderer")
        validate_thresholds(obj.get("thresholds"))
    elif kind == "table":
        columns = obj.get("columns")
        if not isinstance(columns, list) or not columns:
            raise ContractError("renderer.columns must be a non-empty list for table")
        for i, col in enumerate(columns):
            c = require_obj(col, f"renderer.columns[{i}]")
            require_str(c, "key", label=f"renderer.columns[{i}]")
            require_str(c, "label", label=f"renderer.columns[{i}]")
    elif kind == "timeseries":
        require_str(obj, "seriesPath", label="renderer")
        require_str(obj, "xPath", label="renderer")
        require_str(obj, "yPath", label="renderer")
    elif kind in {"log-timeline", "status-history"}:
        require_str(obj, "itemsPath", label="renderer")


def validate_layout(layout: Any) -> None:
    obj = require_obj(layout, "layout")
    min_w = require_int(obj, "minW", label="layout", min_value=1)
    min_h = require_int(obj, "minH", label="layout", min_value=1)
    default_w = require_int(obj, "defaultW", label="layout", min_value=1)
    default_h = require_int(obj, "defaultH", label="layout", min_value=1)
    if default_w < min_w or default_h < min_h:
        raise ContractError("layout.defaultW/defaultH must be >= minW/minH")


def validate_widget(raw: Any, *, path: str = "<memory>") -> ValidationResult:
    obj = require_obj(raw, "widget")
    wid = require_str(obj, "id", label="widget")
    validate_id(wid, label="widget.id")
    require_str(obj, "title", label="widget")
    version = require_str(obj, "version", label="widget")
    if not SEMVER_RE.fullmatch(version):
        raise ContractError("widget.version must be semver like 0.1.0")
    status = require_str(obj, "status", label="widget")
    if status not in VALID_STATUSES:
        raise ContractError(f"widget.status must be one of {sorted(VALID_STATUSES)}")
    validate_source(obj.get("source"))
    validate_renderer(obj.get("renderer"))
    validate_layout(obj.get("layout"))
    validate_tags(obj.get("tags"))
    return ValidationResult(path=path, kind="widget", id=wid, status=status)


def validate_preset(raw: Any, *, path: str = "<memory>") -> ValidationResult:
    obj = require_obj(raw, "preset")
    pid = require_str(obj, "id", label="preset")
    validate_id(pid, label="preset.id")
    require_str(obj, "title", label="preset")
    renderer = require_str(obj, "renderer", label="preset")
    if renderer not in VALID_RENDERERS:
        raise ContractError(f"preset.renderer must be one of {sorted(VALID_RENDERERS)}")
    layout = obj.get("layout")
    if layout is not None:
        validate_layout(layout)
    defaults = obj.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ContractError("preset.defaults must be an object")
    return ValidationResult(path=path, kind="preset", id=pid, status="preset")


def discover_json_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == ".json":
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.json")))
        else:
            raise ContractError(f"path not found or not JSON: {path}")
    return sorted(files)


def validate_paths(paths: list[Path]) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    errors: list[str] = []
    for file in discover_json_files(paths):
        try:
            raw = read_json(file)
            if "source" in raw and "renderer" in raw:
                results.append(validate_widget(raw, path=str(file)))
            elif "defaults" in raw or raw.get("kind") == "preset":
                results.append(validate_preset(raw, path=str(file)))
            else:
                raise ContractError("unknown JSON contract type; expected widget or preset")
        except ContractError as exc:
            errors.append(f"{file}: {exc}")
    if errors:
        raise ContractError("\n".join(errors))
    return results


def catalog(paths: list[Path]) -> dict[str, Any]:
    results = validate_paths(paths)
    by_status: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    for r in results:
        by_status[r.status] = by_status.get(r.status, 0) + 1
        by_kind[r.kind] = by_kind.get(r.kind, 0) + 1
    return {
        "total": len(results),
        "byStatus": dict(sorted(by_status.items())),
        "byKind": dict(sorted(by_kind.items())),
        "items": [r.__dict__ for r in results],
    }


def scaffold_widget(widget_id: str, title: str, renderer_kind: str, source_kind: str) -> dict[str, Any]:
    validate_id(widget_id, label="widget.id")
    if renderer_kind not in VALID_RENDERERS:
        raise ContractError(f"renderer must be one of {sorted(VALID_RENDERERS)}")
    if source_kind not in VALID_SOURCE_KINDS:
        raise ContractError(f"source must be one of {sorted(VALID_SOURCE_KINDS)}")
    renderer: dict[str, Any] = {"kind": renderer_kind}
    if renderer_kind in {"stat", "gauge"}:
        renderer.update({"valuePath": "value", "unit": "", "thresholds": []})
    elif renderer_kind == "table":
        renderer["columns"] = [{"key": "name", "label": "Name"}, {"key": "value", "label": "Value"}]
    elif renderer_kind == "timeseries":
        renderer.update({"seriesPath": "points", "xPath": "ts", "yPath": "value"})
    elif renderer_kind in {"log-timeline", "status-history"}:
        renderer["itemsPath"] = "items"
    else:
        renderer["component"] = "CustomWidget"
    source: dict[str, Any] = {"kind": source_kind, "path": widget_id.replace("-", "."), "refreshMs": 5000}
    if source_kind == "http-json":
        source["url"] = "http://127.0.0.1:8000/data.json"
    return {
        "id": widget_id,
        "title": title,
        "version": "0.1.0",
        "status": "draft",
        "source": source,
        "renderer": renderer,
        "layout": {"minW": 1, "minH": 1, "defaultW": 2, "defaultH": 1},
        "tags": ["draft"],
    }
