#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

printf 'repo quality gate: local-dashboard-widget-sdk\n'
fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }

printf '\n[1/9] tracked generated/private files\n'
tracked_bad="$(git ls-files | grep -E '(^|/)(__pycache__|\.ai_context|AGENTS\.md|CLAUDE\.md|\.egg-info|debug.*\.jsonl)' || true)"
if [[ -n "$tracked_bad" ]]; then printf '%s\n' "$tracked_bad"; fail 'tracked generated/private files found'; fi
printf 'ok\n'

printf '\n[2/9] version consistency\n'
python3 - <<'PY'
import re
from pathlib import Path
pyproject=Path('pyproject.toml').read_text()
version=re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.M)
assert version, 'project version missing'
project_version=version.group(1)
init=Path('src/local_dashboard_widget_sdk/__init__.py').read_text()
match=re.search(r'__version__\s*=\s*"([^"]+)"', init)
assert match, '__version__ missing'
assert match.group(1) == project_version, (match.group(1), project_version)
assert f'## {project_version}' in Path('CHANGELOG.md').read_text(), 'CHANGELOG missing current version section'
print('ok', project_version)
PY

printf '\n[3/9] entry points import\n'
PYTHONPATH=src python3 - <<'PY'
import importlib
import re
from pathlib import Path
text=Path('pyproject.toml').read_text()
block=re.search(r'\[project\.scripts\](.*?)(?:\n\[|\Z)', text, re.S)
assert block, 'project.scripts missing'
scripts={}
for line in block.group(1).splitlines():
    line=line.strip()
    if not line or line.startswith('#'): continue
    key,value=line.split('=',1)
    scripts[key.strip()]=value.strip().strip('"')
for name,target in scripts.items():
    mod,func=target.split(':')
    obj=getattr(importlib.import_module(mod), func)
    assert callable(obj), (name,target)
print('ok', len(scripts))
PY

printf '\n[4/9] smoke test\n'
./scripts/smoke_test.sh

printf '\n[5/9] schema/type export freshness\n'
PYTHONPATH=src python3 -m local_dashboard_widget_sdk.cli schema --output /tmp/ldw-quality-schema.json
PYTHONPATH=src python3 -m local_dashboard_widget_sdk.cli typescript --output /tmp/ldw-quality-types.d.ts
cmp -s schemas/contracts.schema.json /tmp/ldw-quality-schema.json
cmp -s types/contracts.d.ts /tmp/ldw-quality-types.d.ts
python3 - <<'PY'
import json
schema=json.load(open('schemas/contracts.schema.json'))
assert schema['$schema'] == 'https://json-schema.org/draft/2020-12/schema'
assert 'widget' in schema['$defs'] and 'preset' in schema['$defs']
types=open('types/contracts.d.ts').read()
assert 'DashboardWidgetManifest' in types
assert 'DashboardContract' in types
print('ok')
PY

printf '\n[6/9] README/docs required sections\n'
python3 - <<'PY'
from pathlib import Path
readme=Path('README.md').read_text()
required=['Why this exists','Quick start','JSON Schema and TypeScript','Commands','Current verification status','Part of Linux Kiosk Stack','Roadmap']
missing=[x for x in required if x not in readme]
assert not missing, missing
for path, markers in {
    'docs/manifest.md':['Machine-readable schema'],
    'docs/integration.md':['TypeScript integration'],
    'docs/renderers.md':['Renderer contracts'],
    'docs/presets.md':['Panel presets'],
}.items():
    text=Path(path).read_text()
    for marker in markers:
        assert marker in text, (path, marker)
print('ok')
PY

printf '\n[7/9] local markdown links\n'
python3 - <<'PY'
from pathlib import Path
import re
root=Path('.').resolve(); errors=[]
for p in root.rglob('*'):
    if not p.is_file() or '.git' in p.parts or '.ai_context' in p.parts or '__pycache__' in p.parts: continue
    if p.suffix.lower() != '.md' and not p.name.startswith('README') and p.name != 'CHANGELOG.md': continue
    text=p.read_text(errors='replace')
    for m in re.finditer(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', text):
        target=m.group(1).strip().split()[0].strip('<>')
        if not target or target.startswith(('#','http://','https://','mailto:','tel:')): continue
        rel=target.split('#',1)[0]
        if rel and not (p.parent/rel).resolve().exists():
            errors.append(f'{p}:{text.count(chr(10),0,m.start())+1}:{target}')
if errors:
    print('\n'.join(errors)); raise SystemExit(1)
print('ok')
PY

printf '\n[8/9] public privacy scan\n'
python3 - <<'PY'
from pathlib import Path
needles=['14'+':ab','tail'+'ad','/mnt/'+'slane','Мои '+'приложения','Сл'+'ейн','SL'+'ANE','slane'+'-stick','yu'+'rii','yu'+'rii86','gh'+'p_','Keen'+'etic']
hits=[]
for p in Path('.').rglob('*'):
    if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts or '.ai_context' in p.parts or p.name in {'AGENTS.md','CLAUDE.md'}: continue
    text=p.read_text(errors='ignore')
    for n in needles:
        if n in text: hits.append((str(p), n))
if hits:
    print('bad hits', hits[:50]); raise SystemExit(1)
print('ok')
PY

printf '\n[9/9] CI workflow hygiene\n'
grep -q 'permissions:' .github/workflows/ci.yml
grep -q 'contents: read' .github/workflows/ci.yml
grep -q 'ubuntu-24.04' .github/workflows/ci.yml
grep -q 'Repository quality gate' .github/workflows/ci.yml
printf 'ok\n'

printf '\nrepo quality gate ok\n'
