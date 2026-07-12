# Local Dashboard Widget SDK

[![CI](https://github.com/YURII-YURII86/local-dashboard-widget-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/YURII-YURII86/local-dashboard-widget-sdk/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](pyproject.toml)

A small **Contract-first** SDK for local dashboards and kiosk panels.

It helps you define dashboard widgets as portable JSON manifests with explicit data sources, field contracts, renderer contracts, layout hints, and reusable presets.

```text
widget manifest
  ↓ validate
source contract + renderer contract + field config
  ↓ catalog / preset / scaffold
local dashboard / kiosk / browser shell
```

## Why this exists

Local dashboards often start as hardcoded cards: weather here, status there, table there. After a few iterations it becomes hard to know:

- what data shape a widget expects;
- what renderer type it uses;
- whether a widget is safe for a production grid;
- which widgets belong to lab/demo/production;
- how to reuse panel presets without copying code.

This SDK makes those contracts explicit before the widget reaches a dashboard.

## What it provides

- JSON widget manifest validation.
- Data source contract validation.
- Renderer contract validation.
- Panel preset validation.
- Catalog summary generation.
- Widget scaffold generator.
- Example widgets and presets.
- CLI and Python API.
- CI-friendly smoke tests.

## Install from source

```bash
git clone https://github.com/YURII-YURII86/local-dashboard-widget-sdk.git
cd local-dashboard-widget-sdk
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Quick start

Validate examples:

```bash
ldw validate examples/widgets examples/presets
```

Print catalog:

```bash
ldw catalog examples/widgets --json
```

Create a new widget manifest:

```bash
ldw scaffold my-widget --title "My Widget" --renderer stat --source local-json --output examples/widgets/my-widget.json
```

Run self-test:

```bash
ldw self-test
```

## JSON Schema and TypeScript

Export the machine-readable contract used by validators and downstream tooling:

```bash
ldw schema --output schemas/contracts.schema.json
ldw typescript --output types/contracts.d.ts
```

The generated files are committed in this repository:

```text
schemas/contracts.schema.json
types/contracts.d.ts
```

This makes the SDK useful outside Python: browser shells, TypeScript apps, config editors, and CI pipelines can consume the same contract.

## Widget manifest example

```json
{
  "id": "cpu-load",
  "title": "CPU Load",
  "version": "0.1.0",
  "status": "production",
  "source": {
    "kind": "local-json",
    "path": "system.load",
    "refreshMs": 5000
  },
  "renderer": {
    "kind": "stat",
    "valuePath": "value",
    "unit": "%",
    "thresholds": [
      {"level": "warn", "gte": 75},
      {"level": "bad", "gte": 90}
    ]
  },
  "layout": {
    "minW": 1,
    "minH": 1,
    "defaultW": 2,
    "defaultH": 1
  },
  "tags": ["system", "production"]
}
```

## Renderer kinds

Built-in renderer contract kinds:

- `stat`
- `table`
- `timeseries`
- `gauge`
- `log-timeline`
- `status-history`
- `custom`

## Commands

```bash
ldw validate <paths...>
ldw catalog <paths...> [--json]
ldw scaffold <widget-id> --title "Title" [--renderer stat] [--source local-json] [--output widget.json]
ldw schema [--output schemas/contracts.schema.json]
ldw typescript [--output types/contracts.d.ts]
ldw self-test
```

## Documentation

- `docs/manifest.md` — widget manifest contract.
- `docs/renderers.md` — renderer contracts.
- `docs/presets.md` — panel presets.
- `docs/integration.md` — how to integrate with a local dashboard shell.

## Current verification status

Verified in this standalone repository:

- manifest/source/renderer/preset validation;
- scaffold generation;
- catalog summary;
- JSON Schema export;
- TypeScript definitions export;
- fresh-clone smoke tests;
- GitHub Actions CI.

Not yet extracted from Slane as a drop-in replacement. This repo is a clean generic SDK inspired by Slane Stik's internal widget contracts, not a dump of Slane private configs.

## Repository quality gate

Run publication-readiness checks locally:

```bash
./scripts/repo_quality_gate.sh
```

The gate verifies version consistency, entry points, smoke tests, schema/type exports, required docs sections, local Markdown links, privacy/publication cleanliness, and CI workflow hygiene.

## Test

```bash
./scripts/smoke_test.sh
```

## Part of Linux Kiosk Stack

This project is one layer of the [Linux Kiosk Stack](https://github.com/YURII-YURII86/linux-kiosk-stack): a local-first toolkit for Linux TV kiosks, dashboards, signage screens, and appliance panels.

## Roadmap

- Browser catalog viewer.
- Lab → production promotion gate.
- Dashboard layout draft validation.
- More examples for real kiosk shells.

## License

MIT.
