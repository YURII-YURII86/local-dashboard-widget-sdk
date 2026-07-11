from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import ContractError, catalog, scaffold_widget, validate_paths


def cmd_validate(args: argparse.Namespace) -> int:
    results = validate_paths([Path(p) for p in args.paths])
    print(f"contracts ok: {len(results)}")
    for r in results:
        print(f"  {r.kind:6} {r.status:10} {r.id:24} {r.path}")
    return 0


def cmd_catalog(args: argparse.Namespace) -> int:
    data = catalog([Path(p) for p in args.paths])
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"total: {data['total']}")
        print("by kind: " + json.dumps(data["byKind"], sort_keys=True))
        print("by status: " + json.dumps(data["byStatus"], sort_keys=True))
        for item in data["items"]:
            print(f"  {item['kind']:6} {item['status']:10} {item['id']:24} {item['path']}")
    return 0


def cmd_scaffold(args: argparse.Namespace) -> int:
    data = scaffold_widget(args.widget_id, args.title, args.renderer, args.source)
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(text, end="")
    return 0


def cmd_self_test(args: argparse.Namespace) -> int:
    widget = scaffold_widget("self-test-widget", "Self Test Widget", "stat", "local-json")
    # validate the in-memory object by writing through catalog-style validator manually
    from .core import validate_widget
    result = validate_widget(widget)
    assert result.id == "self-test-widget"
    print("self-test ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ldw", description="Local Dashboard Widget SDK contract tools.")
    parser.add_argument("--version", action="version", version="local-dashboard-widget-sdk 0.1.0")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("validate", help="validate widget/preset JSON files or directories")
    p.add_argument("paths", nargs="+")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("catalog", help="print a catalog summary")
    p.add_argument("paths", nargs="+")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_catalog)

    p = sub.add_parser("scaffold", help="create a starter widget manifest")
    p.add_argument("widget_id")
    p.add_argument("--title", required=True)
    p.add_argument("--renderer", default="stat")
    p.add_argument("--source", default="local-json")
    p.add_argument("--output")
    p.set_defaults(func=cmd_scaffold)

    p = sub.add_parser("self-test", help="run internal self-test")
    p.set_defaults(func=cmd_self_test)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ContractError as exc:
        print(f"contract error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
