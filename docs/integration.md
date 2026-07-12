# Integration

A local dashboard shell can load validated widget manifests, match each `renderer.kind` to a component, and resolve each `source` against its own data hub.

Typical flow:

1. Keep widget JSON in a `widgets/` folder.
2. Run `ldw validate widgets/ presets/` in CI.
3. Run `ldw catalog widgets/ --json` to produce a catalog.
4. Let the dashboard shell render only `production` widgets by default.
5. Keep `draft` and `lab` widgets visible only in development/audit views.


## TypeScript integration

Generate TypeScript definitions for browser apps and config editors:

```bash
ldw typescript --output types/contracts.d.ts
```

Use `DashboardWidgetManifest`, `DashboardPreset`, and `DashboardContract` in frontend/editor code so UI state follows the same contract as CI validation.


## Catalog viewer

Use `examples/catalog-viewer/` to inspect example widget and preset contracts in a browser without a backend or build step. Regenerate `catalog-data.js` with `python3 scripts/build_catalog_viewer.py`.
