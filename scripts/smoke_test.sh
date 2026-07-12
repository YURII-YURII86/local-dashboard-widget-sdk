#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m py_compile src/local_dashboard_widget_sdk/*.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m local_dashboard_widget_sdk.cli self-test
PYTHONPATH=src python3 -m local_dashboard_widget_sdk.cli validate examples/widgets examples/presets
PYTHONPATH=src python3 -m local_dashboard_widget_sdk.cli catalog examples/widgets --json >/tmp/ldw-catalog.json
PYTHONPATH=src python3 -m local_dashboard_widget_sdk.cli schema --output /tmp/ldw-contracts.schema.json
PYTHONPATH=src python3 -m local_dashboard_widget_sdk.cli typescript --output /tmp/ldw-contracts.d.ts
python3 - <<'PY'
import json
schema=json.load(open('/tmp/ldw-contracts.schema.json'))
assert schema['$schema'] == 'https://json-schema.org/draft/2020-12/schema'
assert 'widget' in schema['$defs']
types=open('/tmp/ldw-contracts.d.ts').read()
assert 'DashboardWidgetManifest' in types
assert 'DashboardContract' in types
catalog=json.load(open('/tmp/ldw-catalog.json'))
assert catalog['total'] >= 1
print('exports ok')
PY
cmp -s schemas/contracts.schema.json /tmp/ldw-contracts.schema.json
cmp -s types/contracts.d.ts /tmp/ldw-contracts.d.ts
echo 'smoke ok'
