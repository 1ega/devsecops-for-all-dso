#!/usr/bin/env python3
"""Opt-in real scanner acceptance: isolated synthetic data, no application execution.

Run: python3 tools/dso/tests/smoke.py --engine docker
Downloads pinned images and Trivy databases. Temporary targets/reports are removed.
"""
import argparse
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import manifest
import scanning


def check(condition, message):
    # Explicit checks still run under python -O, unlike assert.
    if not condition:
        raise SystemExit(f'smoke failed: {message}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=('native', 'docker'), default='docker')
    parser.add_argument('--plugins', '--tools', dest='plugins', nargs='+', choices=sorted(manifest.plugins()))
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='dso-smoke-') as folder:
        target = Path(folder) / 'target'
        target.mkdir()
        target.joinpath('app.py').write_text('import requests\nrequests.get("https://example.invalid", verify=False)\n')
        target.joinpath('token.txt').write_text('github_token = "ghp_' + 'AbCdEf0123456789' * 2 + 'AbCdEf"\n')
        target.joinpath('requirements.txt').write_text('requests==2.19.1\n')
        bad = scanning.scan_repo(target, args.plugins, args.engine, 600, 'synthetic-smoke')
        if not bad['complete']:
            print(json.dumps({'phase': 'bad', 'runs': bad['runs']}))
            return 2
        for plugin in scanning.selected_plugins(args.plugins, scanning.DEFAULT_PROFILE):
            check(any(f['plugin'] == plugin for f in bad['findings']), f'{plugin} did not detect the synthetic fixture')
            check(any(f['plugin'] == plugin for f in scanning.gate(bad)['blocking']), f'{plugin} finding did not block at high')
        check(scanning.gate(bad)['exit_code'] == 1, 'vulnerable fixture passed the gate')
        check(scanning.gate(bad, bad)['exit_code'] == 0, 'baseline did not accept existing findings')
        check('AbCdEf0123456789' not in json.dumps(bad), 'secret value leaked into the report')
        target.joinpath('app.py').write_text('import requests\nrequests.get("https://example.invalid", timeout=10)\n')
        target.joinpath('token.txt').unlink()
        target.joinpath('requirements.txt').unlink()
        good = scanning.scan_repo(target, args.plugins, args.engine, 600, 'synthetic-smoke')
        check(good['complete'], json.dumps(good['runs']))
        check(not good['findings'], 'clean fixture unexpectedly has findings')
        check(scanning.gate(good, bad)['exit_code'] == 0, 'clean fixture failed against the baseline')
        print(json.dumps({'status': 'passed', 'engine': args.engine,
                          'plugins': bad['coverage']['plugins'], 'bad_findings': len(bad['findings']),
                          'clean_findings': 0}))
        return 0


if __name__ == '__main__':
    sys.exit(main())
