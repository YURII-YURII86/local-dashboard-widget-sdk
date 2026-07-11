# Widget manifest contract

A widget manifest is a portable JSON description of one dashboard panel.

Required fields:

- `id`: kebab-case stable id.
- `title`: display title.
- `version`: semver version like `0.1.0`.
- `status`: `draft`, `lab`, `production`, or `deprecated`.
- `source`: data source contract.
- `renderer`: renderer contract.
- `layout`: layout constraints.

The manifest describes what the widget expects. It does not render by itself.
