# Integration

A local dashboard shell can load validated widget manifests, match each `renderer.kind` to a component, and resolve each `source` against its own data hub.

Typical flow:

1. Keep widget JSON in a `widgets/` folder.
2. Run `ldw validate widgets/ presets/` in CI.
3. Run `ldw catalog widgets/ --json` to produce a catalog.
4. Let the dashboard shell render only `production` widgets by default.
5. Keep `draft` and `lab` widgets visible only in development/audit views.
