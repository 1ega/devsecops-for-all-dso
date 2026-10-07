#!/usr/bin/env python3
"""Opt-in image acceptance: scan public, vulnerable Alpine 3.18.0 twice.

The digest selects linux/arm64 explicitly, so both scanners inspect the same image.
Scanners fetch image contents for analysis; the target image is never executed.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scanning
from smoke import check

IMAGE = ('docker.io/library/alpine:3.18.0@sha256:'
         '30e6d35703c578ee703230b9dc87ada2ba958c1928615ac8a674fcbbcbb0f281')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=('native', 'docker'), default='docker')
    args = parser.parse_args()

    def progress(event, step, detail=None):
        if event == 'done':
            print(json.dumps({'step': step, 'status': detail.get('status')}), flush=True)

    baseline = None
    for attempt in range(2):
        report = scanning.scan_image(IMAGE, engine=args.engine, timeout=600,
                                     project='synthetic-image-smoke', progress=progress)
        check(report['complete'], json.dumps(report['runs']))
        scanning.validate_report(report)
        gate = scanning.gate(report)
        check(gate['exit_code'] == 1, 'vulnerable image passed the gate')
        for plugin in report['coverage']['plugins']:
            check(any(f['plugin'] == plugin for f in gate['blocking']),
                  f'{plugin} did not report a blocking image vulnerability')
        if baseline is not None:
            check(scanning.gate(report, baseline)['exit_code'] == 0,
                  'repeat image scan added findings against its baseline')
            check(report['findings'] == baseline['findings'], 'repeat image findings changed')
        baseline = report
        print(json.dumps({'attempt': attempt + 1, 'runs': report['runs']}), flush=True)
    print(json.dumps({'status': 'passed', 'engine': args.engine,
                      'plugins': baseline['coverage']['plugins'], 'repeat_findings': len(baseline['findings'])}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
