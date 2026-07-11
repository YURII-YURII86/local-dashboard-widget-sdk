# Renderer contracts

Built-in renderer kinds:

- `stat`: single value with optional unit and thresholds.
- `table`: list of rows with explicit columns.
- `timeseries`: points with x/y paths.
- `gauge`: value with thresholds.
- `log-timeline`: ordered log-like items.
- `status-history`: status events over time.
- `custom`: project-specific renderer hook.

Renderer contracts make dashboards validate a panel before it reaches production.
