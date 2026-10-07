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
    parser.add_argument('--profile', choices=[name for name, spec in manifest.profiles().items()
                                             if spec['target'] == 'repo'], default=scanning.DEFAULT_PROFILE)
    parser.add_argument('--plugins', '--tools', dest='plugins', nargs='+', choices=sorted(manifest.plugins()))
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='dso-smoke-') as folder:
        target = Path(folder) / 'target'
        target.mkdir()
        target.joinpath('app.py').write_text('import requests\nrequests.get("https://example.invalid", verify=False)\n')
        target.joinpath('token.txt').write_text('github_token = "ghp_' + 'AbCdEf0123456789' * 2 + 'AbCdEf"\n')
        # Synthetic AWS-shaped pair, scanned with verification disabled; never a live credential.
        target.joinpath('aws.txt').write_text('aws_access_key_id = AKIAZ7Q4N2J6W3V5R8TB\n'
                                            'aws_secret_access_key = vM4uZ2hW8xN6jR3pQ9kL5sT7aB0cD1eF2gH3iJ4K\n')
        target.joinpath('requirements.txt').write_text('requests==2.19.1\n')
        # The EICAR test string, assembled so the literal is not in this repository; harmless by design.
        target.joinpath('eicar.txt').write_text('X5O!P%@AP[4\\PZX54(P^)7CC)7}$' + 'EICAR-STANDARD-ANTIVIRUS-TEST-FILE' + '!$H+H*\n')
        target.joinpath('pod.yaml').write_text('''apiVersion: v1
kind: Pod
metadata:
  name: smoke
spec:
  containers:
    - name: smoke
      image: alpine:3.18
      securityContext:
        privileged: true
''')
        workflows = target / '.github' / 'workflows'
        workflows.mkdir(parents=True)
        workflows.joinpath('ci.yml').write_text('''name: smoke
on: pull_request_target
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: npm install
      - run: echo "${{ github.event.pull_request.title }}"
''')
        def progress(event, step, detail=None):
            if event == 'done':
                print(json.dumps({'step': step, 'status': detail.get('status')}), flush=True)
        bad = scanning.scan_repo(target, args.plugins, args.engine, 600, 'synthetic-smoke',
                                 profile=args.profile, progress=progress)
        if not bad['complete']:
            print(json.dumps({'phase': 'bad', 'runs': bad['runs']}))
            return 2
        for plugin in scanning.selected_plugins(args.plugins, args.profile):
            check(any(f['plugin'] == plugin for f in bad['findings']), f'{plugin} did not detect the synthetic fixture')
            check(any(f['plugin'] == plugin for f in scanning.gate(bad)['blocking']), f'{plugin} finding did not block at high')
        check(scanning.gate(bad)['exit_code'] == 1, 'vulnerable fixture passed the gate')
        check(scanning.gate(bad, bad)['exit_code'] == 0, 'baseline did not accept existing findings')
        dependency_scanners = {p for p in bad['coverage']['plugins'] if manifest.plugin(p)['category'] == 'sca'}
        if len(dependency_scanners) > 1:
            check(any(set(i['plugins']) == dependency_scanners for i in scanning.issues(bad['findings'])),
                  'the dependency scanners did not agree on one issue for the vulnerable package')
        check('AbCdEf0123456789' not in json.dumps(bad), 'secret value leaked into the report')
        check('vM4uZ2hW8xN6' not in json.dumps(bad), 'AWS-shaped secret leaked into the report')
        target.joinpath('app.py').write_text('import requests\nrequests.get("https://example.invalid", timeout=10)\n')
        target.joinpath('token.txt').unlink()
        target.joinpath('aws.txt').unlink()
        target.joinpath('requirements.txt').unlink()
        target.joinpath('eicar.txt').unlink()
        target.joinpath('pod.yaml').unlink()
        workflows.joinpath('ci.yml').unlink()
        good = scanning.scan_repo(target, args.plugins, args.engine, 600, 'synthetic-smoke',
                                  profile=args.profile, progress=progress)
        check(good['complete'], json.dumps(good['runs']))
        check(not good['findings'], 'clean fixture unexpectedly has findings')
        check(scanning.gate(good, bad)['exit_code'] == 0, 'clean fixture failed against the baseline')
        print(json.dumps({'status': 'passed', 'engine': args.engine,
                          'plugins': bad['coverage']['plugins'], 'bad_findings': len(bad['findings']),
                          'bad_issues': len(scanning.issues(bad['findings'])), 'clean_findings': 0}))
        return 0


if __name__ == '__main__':
    sys.exit(main())
