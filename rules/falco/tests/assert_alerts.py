#!/usr/bin/env python3
"""Assert all 16 rules matched the positive container and none the quiet one."""
import json
import sys
from pathlib import Path

if len(sys.argv) != 4:
    sys.exit('Usage: assert_alerts.py alerts.jsonl positive-container-id negative-container-id')
observed = {"positive": set(), "negative": set()}
for line in Path(sys.argv[1]).read_text().splitlines():
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        continue  # Startup diagnostics may be plain text.
    if not isinstance(event, dict) or not str(event.get('rule', '')).startswith('DSO '):
        continue
    container = str(event.get('output_fields', {}).get('container.id', ''))
    for mode, identity in zip(('positive', 'negative'), sys.argv[2:]):
        if len(container) >= 12 and identity.startswith(container):
            observed[mode].add(event['rule'])
expected = {rule['rule'] for rule in json.loads(
    (Path(__file__).resolve().parents[1] / 'rule-catalog.json').read_text())['rules']}
missing = expected - observed['positive']
unexpected = observed['negative']
print(f'Runtime: {len(observed["positive"] & expected)}/{len(expected)} positive rules; '
      f'{len(unexpected)} unexpected negative alerts')
if missing:
    print('Missing:', ', '.join(sorted(missing)))
if unexpected:
    print('Unexpected:', ', '.join(sorted(unexpected)))
sys.exit(bool(missing or unexpected))
