"""YARA-X: trusted rule packs over every snapshot file; any scan error makes the run incomplete."""
from __future__ import annotations

import shutil

from reports import finding, relative_path, severity

OPTIONS = {'rules': 'dirs'}
OUTPUT = 'stdout'
FORMAT = 'jsonl'
# yr reports unreadable files and timeouts on stderr and still exits 0.
ERRORS = (b'error:',)
# signature-base rules reference THOR's external variables; empty values keep them compiling.
EXTERNALS = ('filename', 'filepath', 'extension', 'filetype', 'owner')


def policy_files(options, root):
    return sorted(p for directory in options['rules'] for p in (root / directory).rglob('*')
                  if p.suffix in ('.yar', '.yara') and p.is_file())


def prepare(ctx):
    # Rules keep their kit paths, so each match names the rule file it came from.
    for rule in policy_files(ctx.options, ctx.root):
        target = ctx.config_host / 'rules' / rule.relative_to(ctx.root)
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        shutil.copyfile(rule, target)
    (ctx.config_host / 'yara-x.toml').write_text('')


def command(ctx):
    # Rule paths are relative to the working directory, which is the run directory in both engines.
    rules = [f'config/{ctx.plugin}/rules/{directory}' for directory in ctx.options['rules']]
    return ['--config', ctx.config + '/yara-x.toml', 'scan', '--disable-warnings', '--recursive',
            '--path-as-namespace', '--print-namespace', '--output-format', 'ndjson',
            *[value for name in EXTERNALS for value in ('--define', f'{name}=""')], *rules, ctx.source]


def parse(data, plugin, source):
    prefix = f'config/{plugin}/rules/'
    records = []
    for item in data:
        path = relative_path(item['path'], source)
        for rule in item['rules']:
            namespace = rule['namespace']
            if not namespace.startswith(prefix):
                raise ValueError('Match from an unexpected rule file')
            records.append(finding(plugin, namespace[len(prefix):] + ':' + rule['identifier'], path, severity(plugin)))
    return records
