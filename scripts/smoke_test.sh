#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m py_compile src/local_dashboard_widget_sdk/*.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m local_dashboard_widget_sdk.cli self-test
PYTHONPATH=src python3 -m local_dashboard_widget_sdk.cli validate examples/widgets examples/presets
PYTHONPATH=src python3 -m local_dashboard_widget_sdk.cli catalog examples/widgets --json >/tmp/ldw-catalog.json
python3 - <<'PY'
import json
data=json.load(open('/tmp/ldw-catalog.json'))
assert data['total'] == 2
assert data['byKind']['widget'] == 2
print('catalog ok')
PY
rm -f /tmp/ldw-scaffold.json
PYTHONPATH=src python3 -m local_dashboard_widget_sdk.cli scaffold demo-widget --title 'Demo Widget' --renderer stat --source local-json --output /tmp/ldw-scaffold.json
PYTHONPATH=src python3 -m local_dashboard_widget_sdk.cli validate /tmp/ldw-scaffold.json
echo 'smoke ok'
