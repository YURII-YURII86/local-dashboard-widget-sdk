from __future__ import annotations

from typing import Any

from .core import VALID_LEVELS, VALID_RENDERERS, VALID_SOURCE_KINDS, VALID_STATUSES

ID_PATTERN = r"^[a-z][a-z0-9-]{1,62}$"
SEMVER_PATTERN = r"^\d+\.\d+\.\d+([-+][A-Za-z0-9.-]+)?$"
SCHEMA_ID = "https://example.com/schemas/local-dashboard-widget-sdk.contracts.v1.schema.json"


def string_schema(*, pattern: str | None = None, min_length: int = 1, enum: set[str] | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {"type": "string", "minLength": min_length}
    if pattern:
        out["pattern"] = pattern
    if enum:
        out["enum"] = sorted(enum)
    return out


def layout_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["minW", "minH", "defaultW", "defaultH"],
        "properties": {
            "minW": {"type": "integer", "minimum": 1},
            "minH": {"type": "integer", "minimum": 1},
            "defaultW": {"type": "integer", "minimum": 1},
            "defaultH": {"type": "integer", "minimum": 1},
        },
    }


def source_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": True,
        "required": ["kind"],
        "properties": {
            "kind": string_schema(enum=VALID_SOURCE_KINDS),
            "path": string_schema(),
            "url": string_schema(),
            "refreshMs": {"type": "integer", "minimum": 250},
        },
        "allOf": [
            {"if": {"properties": {"kind": {"const": "local-json"}}}, "then": {"required": ["path"]}},
            {"if": {"properties": {"kind": {"const": "computed"}}}, "then": {"required": ["path"]}},
            {"if": {"properties": {"kind": {"const": "http-json"}}}, "then": {"required": ["path", "url"]}},
        ],
    }


def threshold_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["level"],
        "properties": {
            "level": string_schema(enum=VALID_LEVELS),
            "gte": {"type": "number"},
            "lte": {"type": "number"},
            "label": string_schema(),
        },
        "anyOf": [{"required": ["gte"]}, {"required": ["lte"]}],
    }


def renderer_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": True,
        "required": ["kind"],
        "properties": {
            "kind": string_schema(enum=VALID_RENDERERS),
            "valuePath": string_schema(),
            "unit": {"type": "string"},
            "thresholds": {"type": "array", "items": threshold_schema()},
            "columns": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["key", "label"],
                    "properties": {"key": string_schema(), "label": string_schema()},
                },
            },
            "seriesPath": string_schema(),
            "xPath": string_schema(),
            "yPath": string_schema(),
            "itemsPath": string_schema(),
            "component": string_schema(),
        },
        "allOf": [
            {"if": {"properties": {"kind": {"enum": ["stat", "gauge"]}}}, "then": {"required": ["valuePath"]}},
            {"if": {"properties": {"kind": {"const": "table"}}}, "then": {"required": ["columns"]}},
            {"if": {"properties": {"kind": {"const": "timeseries"}}}, "then": {"required": ["seriesPath", "xPath", "yPath"]}},
            {"if": {"properties": {"kind": {"enum": ["log-timeline", "status-history"]}}}, "then": {"required": ["itemsPath"]}},
            {"if": {"properties": {"kind": {"const": "custom"}}}, "then": {"required": ["component"]}},
        ],
    }


def widget_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": True,
        "required": ["id", "title", "version", "status", "source", "renderer", "layout"],
        "properties": {
            "id": string_schema(pattern=ID_PATTERN),
            "title": string_schema(),
            "version": string_schema(pattern=SEMVER_PATTERN),
            "status": string_schema(enum=VALID_STATUSES),
            "source": {"$ref": "#/$defs/source"},
            "renderer": {"$ref": "#/$defs/renderer"},
            "layout": {"$ref": "#/$defs/layout"},
            "tags": {"type": "array", "items": string_schema(pattern=ID_PATTERN)},
        },
    }


def preset_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": True,
        "required": ["id", "title", "renderer"],
        "properties": {
            "id": string_schema(pattern=ID_PATTERN),
            "title": string_schema(),
            "kind": {"const": "preset"},
            "renderer": string_schema(enum=VALID_RENDERERS),
            "layout": {"$ref": "#/$defs/layout"},
            "defaults": {"type": "object"},
        },
    }


def contract_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": SCHEMA_ID,
        "title": "Local Dashboard Widget SDK Contracts",
        "description": "Widget manifest and preset contracts for local dashboard/kiosk panels.",
        "oneOf": [{"$ref": "#/$defs/widget"}, {"$ref": "#/$defs/preset"}],
        "$defs": {
            "widget": widget_schema(),
            "preset": preset_schema(),
            "source": source_schema(),
            "renderer": renderer_schema(),
            "layout": layout_schema(),
            "threshold": threshold_schema(),
        },
    }
