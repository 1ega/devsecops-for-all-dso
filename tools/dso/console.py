"""What a person sees in a terminal: banner, interactive menu and readable results.

Machine output stays JSON (`--format json`, or whenever stdout is not a terminal).
Everything shown here comes from the report, the gate result and the plugin
manifest; scanner text is never printed, and target-controlled values are escaped.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
import os
from pathlib import Path
import re
import shlex
import shutil
import sys
import textwrap
import threading
import time

import config
import inventory
import manifest
import register
import reports
import runtime
import scanning
import sources

LOGO = ('██████╗ ███████╗ ██████╗ ',
        '██╔══██╗██╔════╝██╔═══██╗',
        '██║  ██║███████╗██║   ██║',
        '██║  ██║╚════██║██║   ██║',
        '██████╔╝███████║╚██████╔╝',
        '╚═════╝ ╚══════╝ ╚═════╝ ')
ASCII_LOGO = (' ____  ____   ___ ',
              '|  _ \\/ ___| / _ \\ ',
              '| | | \\___ \\| | | |',
              '| |_| |___) | |_| |',
              '|____/|____/ \\___/ ')
GRADIENT = ((199, 166, 255), (178, 172, 252), (152, 184, 246), (124, 202, 236), (104, 220, 226), (94, 234, 212))
PALETTE = {'accent': (94, 234, 212), 'dim': (125, 135, 155), 'ok': (74, 222, 128), 'bad': (248, 113, 113),
           'warn': (250, 204, 21), 'link': (96, 165, 250),
           'critical': (239, 68, 68), 'high': (248, 113, 113), 'unknown': (232, 121, 249),
           'medium': (250, 204, 21), 'low': (96, 165, 250), 'info': (148, 163, 184)}
ORDER = reports.ORDER
COMMANDS = (('scan', 'Scan a directory, GitHub repositories or an image'),
            ('gate', 'Pass or block a report, with an optional baseline'),
            ('doctor', 'Check that the pinned scanners are installed'),
            ('config', 'Show the effective settings and where they come from'),
            ('assess', 'Check security baseline evidence and show gaps'),
            ('inventory', 'Check the asset ownership inventory'),
            ('exceptions', 'Check exception owners, approvers and expiry'),
            ('triage', 'Walk through blocking issues and record exceptions'))
CARDS = 10
BACK = ('q', ':q')


class Back(Exception):
    """The person typed q at a question: return to the command choice."""


def interactive():
    return sys.stdin.isatty() and sys.stdout.isatty()


def reports_dir():
    return Path(config.load()[0]['reports_dir'])


def safe(value):
    """Paths and package names come from the target; they must not drive the terminal."""
    return ''.join(c if c.isprintable() else (f'\\x{ord(c):02x}' if ord(c) < 256 else f'\\u{ord(c):04x}')
                   for c in str(value))


def short(path):
    """Home-relative path for display."""
    path, home = str(path), str(Path.home())
    return '~' + path[len(home):] if path == home or path.startswith(home + os.sep) else path


def cube(rgb):
    """Nearest xterm-256 colour for terminals without truecolor."""
    return 16 + 36 * round(rgb[0] / 51) + 6 * round(rgb[1] / 51) + round(rgb[2] / 51)


def duration(seconds):
    if seconds < 1:
        return '<1s'
    if seconds < 60:
        return f'{seconds:.1f}s'
    return f'{int(seconds // 60)}m {int(seconds % 60):02d}s'


def megabytes(value):
    return f'{value / 1000:.1f} GB' if value >= 1000 else f'{value} MB'


def database_row(statuses, engine):
    """One line for the session box: what is cached and what this scan will download."""
    if not statuses:
        return 'none needed'
    missing = [d for d in statuses if not d['present']]
    download = megabytes(sum(d['download_mb'] for d in missing))
    if engine == 'docker' and scanning.cache_root() is None:
        return f'downloaded inside each container on every scan, about {megabytes(sum(d["download_mb"] for d in statuses))}'
    if not missing:
        return f'cached, {size(sum(d["bytes"] for d in statuses))} in {short(scanning.cache_root())}'
    return f'downloads about {download} now, about {megabytes(sum(d["disk_mb"] for d in missing))} on disk'


def database_notice(style, statuses, engine):
    """Say plainly before a first scan that vulnerability databases are large."""
    missing = [d for d in statuses if not d['present']]
    if not missing:
        return
    root = scanning.cache_root()
    style.write('  ' + style.paint(style.symbol('⚠', '!') + ' This scan first downloads vulnerability databases:', 'warn', bold=True))
    for d in missing:
        style.write(style.paint(f'    {d["name"].ljust(24)} {megabytes(d["download_mb"]).rjust(7)} download, '
                                f'{megabytes(d["disk_mb"])} on disk', 'warn'))
        if d['note']:
            for line in textwrap.wrap(d['note'], style.width - 8):
                style.write(style.paint('      ' + line, 'dim'))
    where = f'in {short(root)}' if root else 'only for this run (set DSO_CACHE_DIR to keep them)'
    for line in textwrap.wrap(f'They are kept {where} and refreshed about once a day. '
                              'The ci-blocking profile needs only the Trivy DB.', style.width - 6):
        style.write(style.paint('    ' + line, 'dim'))
    style.write('')


def plural(count, word):
    return f'{count:,} {word}{"" if count == 1 else "s"}'


def size(count):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if count < 1024 or unit == 'GB':
            return f'{count:.0f} {unit}' if unit == 'B' else f'{count:.1f} {unit}'
        count /= 1024


class Style:
    def __init__(self, stream=None):
        self.stream = stream or sys.stdout
        tty = self.stream.isatty()
        dumb = os.environ.get('TERM') == 'dumb'
        self.color = tty and not dumb and not os.environ.get('NO_COLOR')
        self.live = tty and not dumb
        self.truecolor = os.environ.get('COLORTERM', '').lower() in ('truecolor', '24bit')
        self.unicode = (getattr(self.stream, 'encoding', None) or '').lower().replace('-', '').startswith('utf')
        self.width = max(48, min(shutil.get_terminal_size((80, 24)).columns, 84))

    def paint(self, text, color=None, bold=False):
        if not self.color or (color is None and not bold):
            return text
        codes = ['1'] if bold else []
        if color:
            rgb = PALETTE.get(color, color)
            codes.append('38;2;{};{};{}'.format(*rgb) if self.truecolor else f'38;5;{cube(rgb)}')
        return f'\x1b[{";".join(codes)}m{text}\x1b[0m'

    def symbol(self, fancy, plain):
        return fancy if self.unicode else plain

    def write(self, text, end='\n'):
        try:
            self.stream.write(text + end)
        except UnicodeEncodeError:
            encoding = getattr(self.stream, 'encoding', None) or 'ascii'
            self.stream.write((text + end).encode(encoding, 'replace').decode(encoding))
        self.stream.flush()

    def paragraph(self, text, color=None):
        for line in textwrap.wrap(text, self.width - 2):
            self.write('  ' + self.paint(line, color))

    def clip(self, text, room, left=False):
        if len(text) <= room:
            return text
        mark = self.symbol('…', '~')
        return mark + text[len(text) - room + 1:] if left else text[:room - 1] + mark

    def box(self, title, rows, accent='accent', badge=None):
        """rows: (label, value, colour, clip from left); values are escaped, padded, then painted."""
        h, v, tl, tr, bl, br = (self.symbol('─', '-'), self.symbol('│', '|'), self.symbol('┌', '+'),
                                self.symbol('┐', '+'), self.symbol('└', '+'), self.symbol('┘', '+'))
        width = self.width - 2
        title = self.clip(title, width - 8)
        tail = len(f' {badge[0]} {tr}') if badge else len(tr)
        fill = max(1, width - len(f'{tl} {title} ') - tail)
        top = (self.paint(tl + ' ', 'dim') + self.paint(title, accent, bold=True) + ' ' + self.paint(h * fill, 'dim') +
               (' ' + self.paint(badge[0], badge[1], bold=True) + ' ' if badge else '') + self.paint(tr, 'dim'))
        self.write('  ' + top)
        room = width - 14
        for label, value, color, left in rows:
            text = self.clip(safe(value), room, left)
            self.write('  ' + self.paint(v, 'dim') + ' ' + self.paint(label.ljust(9)[:9], 'dim') + ' ' +
                       self.paint(text, color) + ' ' * (room - len(text)) + ' ' + self.paint(v, 'dim'))
        self.write('  ' + self.paint(bl + h * (width - 2) + br, 'dim'))


def banner(style):
    style.write('')
    logo = LOGO if style.unicode else ASCII_LOGO
    for row, rgb in zip(logo, GRADIENT):
        style.write('  ' + style.paint(row, rgb, bold=True))
    style.write('')
    title, version = 'DSO  DEVSECOPS FOR ALL', f'v{scanning.VERSION}'
    gap = max(2, style.width - 6 - len(title) - len(version))
    style.write('  ' + style.paint(style.symbol('◆', '*'), 'accent') + ' ' + style.paint(title, bold=True) +
                ' ' * gap + style.paint(version, 'dim'))
    style.write('  ' + style.paint(style.symbol('─', '-') * (style.width - 2), 'dim'))


def kit_panel(style):
    plugins = manifest.plugins()
    location = config.path()
    style.box('KIT', [('PROFILES', ', '.join(sorted(manifest.profiles())), None, False),
                      ('CONFIG', short(location) + ('' if location.is_file() else ' (none; dso config init)'), 'dim', True),
                      ('PLUGINS', ' · '.join(f'{n} {s["version"]}' for n, s in sorted(plugins.items())), None, False),
                      ('REPORTS', short(reports_dir()), 'dim', True),
                      ('CACHE', cache_summary(), 'dim', True),
                      ('CHECKOUT', short(manifest.ROOT), 'dim', True)])


def cache_summary():
    root = scanning.cache_root()
    if not root:
        return 'no persistent cache; databases are downloaded on every scan'
    used = scanning.disk_usage(root)
    largest = max(sum(d['disk_mb'] for d in scanning.database_status(spec['plugins']))
                  for spec in manifest.profiles().values())
    return f'{short(root)} · {size(used)} used' + ('' if used else f', databases need up to {megabytes(largest)}')


def question(ask, style, label, default='', choices=(), check=None, optional=False):
    hint = f' ({"/".join(choices)})' if choices else ''
    hint += f' [{short(default)}]' if default else (' [none]' if optional else '')
    while True:
        value = ask(f'  {style.paint("?", "accent", bold=True)} {label}{hint}: ').strip()
        if value.lower() in BACK:
            raise Back()
        value = value or default
        if not value:
            if optional:
                return ''
            style.write(style.paint('    A value is required.', 'warn'))
            continue
        if choices and value not in choices:
            style.write(style.paint('    Choose one of: ' + ', '.join(choices), 'warn'))
            continue
        problem = check(value) if check else None
        if problem:
            style.write(style.paint('    ' + problem, 'warn'))
            continue
        return value


def existing(kind):
    def check(value):
        path = Path(value).expanduser()
        return None if (path.is_dir() if kind == 'dir' else path.is_file()) else f'No such {"directory" if kind == "dir" else "file"}.'
    return check


def latest_report():
    try:
        candidates = [p for p in reports_dir().glob('*.json') if p.is_file()]
    except OSError:
        return ''
    return str(max(candidates, key=lambda p: p.stat().st_mtime)) if candidates else ''


def slug(value):
    return re.sub(r'[^A-Za-z0-9._-]+', '-', value).strip('-.') or 'project'


KINDS = {'directory': 'local folder', 'file': 'local file', 'repository': 'public GitHub repository',
         'account': 'all public repositories of a GitHub account', 'image': 'container image'}


def ask_scan(ask, style):
    """One question: DSO works out what the answer is and picks the rest."""
    found = {}

    def check(value):
        try:
            found['target'] = sources.classify(value)
        except ValueError as exc:
            return str(exc)
        return None
    question(ask, style, 'What to scan (folder, file, GitHub URL or image)', str(Path.cwd()), check=check)
    kind, value = found['target']
    style.write(f'    {style.paint("Detected:", "dim")} {KINDS[kind]}')
    return ['scan', value]


def ask_gate(ask, style):
    report = question(ask, style, 'Report to gate', latest_report(), check=existing('file'))
    baseline = question(ask, style, 'Approved baseline', optional=True, check=existing('file'))
    exceptions = question(ask, style, 'Exception register', optional=True, check=existing('file'))
    argv = ['gate', '--input', str(Path(report).expanduser())]
    argv += ['--baseline', str(Path(baseline).expanduser())] if baseline else []
    return argv + (['--exceptions', str(Path(exceptions).expanduser())] if exceptions else [])


def ask_triage(ask, style):
    report = question(ask, style, 'Report to triage', latest_report(), check=existing('file'))
    exceptions = question(ask, style, 'Exception register (created when missing)', str(reports_dir() / 'exceptions.json'))
    return ['triage', '--input', str(Path(report).expanduser()), '--exceptions', str(Path(exceptions).expanduser())]


def ask_doctor(ask, style):
    # The most thorough repository profile shows every scanner that is missing.
    largest = max((len(spec['plugins']), name) for name, spec in manifest.profiles().items() if spec['target'] == 'repo')[1]
    return ['doctor', '--profile', largest]


def ask_register(command, label):
    def flow(ask, style):
        return [command, '--input', str(Path(question(ask, style, label, check=existing('file'))).expanduser())]
    return flow


FLOWS = {'scan': ask_scan, 'gate': ask_gate, 'doctor': ask_doctor, 'config': lambda ask, style: ['config'],
         'assess': ask_register('assess', 'Assessment JSON'),
         'inventory': ask_register('inventory', 'Inventory CSV'),
         'exceptions': ask_register('exceptions', 'Exception register JSON'), 'triage': ask_triage}


def menu(style=None, ask=input):
    """Banner, command choice and its questions; returns CLI arguments, or None to quit."""
    style = style or Style()
    banner(style)
    style.paragraph('Secrets, code and dependencies in one run. Code stays on this machine; '
                    'scanners are pinned and checked, and reports are private files.')
    style.write('')
    kit_panel(style)
    style.write('')
    for number, (name, text) in enumerate(COMMANDS, 1):
        style.write(f'  {style.paint(str(number), "accent", bold=True)}  {style.paint(name.ljust(12), bold=True)}'
                    f'{style.paint(style.clip(text, style.width - 19), "dim")}')
    style.write(f'  {style.paint("q", "accent", bold=True)}  {style.paint("quit", bold=True)}')
    style.write('')
    style.paragraph('Enter keeps the value in [brackets], q goes back to this list, Ctrl-C quits. '
                    'dso --help lists every option.', 'dim')
    style.write('')
    names = [name for name, _ in COMMANDS]
    while True:
        choice = ask(f'  {style.paint(style.symbol("›", ">"), "accent", bold=True)} Command [1-{len(COMMANDS)}, q] [1]: ').strip().lower() or '1'
        if choice in ('q', 'quit', 'exit'):
            return None
        name = names[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(names) else choice
        if name not in FLOWS:
            style.write(style.paint(f'    Choose 1-{len(COMMANDS)} or q.', 'warn'))
            continue
        try:
            argv = FLOWS[name](ask, style)
            break
        except Back:
            style.write(style.paint('    Back to the command list.', 'dim'))
    style.write('')
    style.write('  ' + style.paint('Running: ', 'dim') + 'dso ' + shlex.join(argv))
    style.write('')
    return argv


class Spinner:
    """Redraws one status line from a background thread while a long step runs, so it never looks stuck."""

    def __init__(self, style, render):
        self.style, self.render = style, render
        self.stopped, self.thread, self.started = threading.Event(), None, time.monotonic()

    def start(self):
        self.started = time.monotonic()
        if self.style.live:
            self.stopped.clear()
            self.thread = threading.Thread(target=self.loop, daemon=True)
            self.thread.start()
        return self

    def loop(self):
        frames = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏' if self.style.unicode else '|/-\\'
        tick = 0
        while True:
            self.style.write('\r\x1b[2K' + self.render(frames[tick % len(frames)], time.monotonic() - self.started), end='')
            tick += 1
            if self.stopped.wait(0.12):
                return

    def stop(self):
        if self.thread:
            self.stopped.set()
            self.thread.join()
            self.thread = None
        return time.monotonic() - self.started


def ticking(seconds):
    """Whole seconds while a step runs; decimals would flicker."""
    seconds = int(seconds)
    return f'{seconds}s' if seconds < 60 else f'{seconds // 60}m {seconds % 60:02d}s'


class ScanView:
    """Session box, one live line per step, then the summary."""

    def __init__(self, style, args):
        self.style, self.args = style, args
        self.steps, self.spinner, self.total, self.finished = {}, None, 0, 0

    def session(self, plugins):
        style, args = self.style, self.args
        versions = ' · '.join(f'{n} {manifest.plugin(n)["version"]}' for n in plugins)
        style.write('')
        image = args.scan_type == 'image'
        remote = image or sources.is_remote(args.path)
        target = args.path if remote else short(Path(args.path).expanduser().resolve())
        detected = getattr(args, 'detected', None)
        # Plugins, plus the snapshot for trees, plus the fetch for GitHub repositories.
        self.total = len(plugins) + (0 if image else 1) + (1 if remote and not image else 0)
        databases = scanning.database_status(plugins, args.engine)
        style.box('SCAN SESSION', [('TARGET', target, None, True),
                                   *([('SOURCE', KINDS[detected[0]] + ' (detected)', 'accent', False)] if detected else []),
                                   ('PROJECT', args.project, None, False),
                                   ('PROFILE', args.profile, 'accent', False),
                                   ('ENGINE', args.engine, None, False),
                                   ('PLUGINS', versions, None, False),
                                   ('DATABASES', database_row(databases, args.engine), None, False),
                                   ('REPORT', short(args.output), 'dim', True)],
                  badge=(style.symbol('●', '*') + ' RUNNING', 'accent'))
        style.write('')
        database_notice(style, databases, args.engine)

    def bar(self):
        style = self.style
        width = 16
        filled = round(width * self.finished / self.total) if self.total else 0
        return (style.paint(style.symbol('━', '#') * filled, 'accent') + style.paint(style.symbol('─', '-') * (width - filled), 'dim') +
                style.paint(f' {self.finished}/{self.total}', 'dim'))

    def line(self, number, mark, color, name, state, note='', note_color=None, tail=''):
        style = self.style
        room = max(8, style.width - 34 - len(tail))
        note = style.clip(note, room)
        return (f'  {style.paint(f"{number:02d}", "dim")} {style.paint(mark, color, bold=True)} '
                f'{style.paint(name.ljust(12), bold=True)} {style.paint(state.ljust(9), color, bold=True)} '
                f'{style.paint(note, note_color)}{"  " + style.paint(tail, "dim") if tail else ""}')

    def progress(self, event, step, detail=None):
        style = self.style
        number = self.steps.setdefault(step, len(self.steps) + 1)
        if event == 'start':
            self.spinner = Spinner(style, lambda frame, elapsed: self.line(
                number, frame, 'accent', step, 'RUNNING', ticking(elapsed), 'accent') + '  ' + self.bar()).start()
            return
        elapsed = duration(self.spinner.stop() if self.spinner else 0)
        self.spinner = None
        self.finished += 1
        ok = detail['status'] == 'complete'
        if not ok:
            note, color = safe(detail['error_code']), 'bad'
        elif step == 'snapshot':
            note, color = f'{plural(detail["files"], "file")} · {size(detail["bytes"])}', 'dim'
        elif step == 'fetch':
            note, color = f'commit {detail["commit"][:12]} · {plural(detail["files"], "file")} · {size(detail["bytes"])}', 'dim'
        else:
            count = detail['finding_count']
            note, color = plural(count, 'finding'), 'warn' if count else 'ok'
        text = self.line(number, style.symbol('✓', '+') if ok else style.symbol('✗', 'x'), 'ok' if ok else 'bad',
                         step, 'DONE' if ok else 'FAILED', note, color, elapsed)
        style.write(('\r\x1b[2K' if style.live else '') + text)
        if ok and step == 'snapshot' and detail.get('inventory'):
            parts = inventory.summary(detail['inventory'])
            found = ' · '.join(safe(p) for p in parts) if parts else 'no source, dependency, IaC or CI files recognized'
            for line in textwrap.wrap(found, max(20, style.width - 6), break_long_words=False, break_on_hyphens=False):
                style.write('     ' + style.paint(line, 'dim'))

    def close(self):
        """Stop the live line if a scan ends early, so later messages start on a clean line."""
        if self.spinner:
            self.spinner.stop()
            self.spinner = None
            if self.style.live:
                self.style.write('')


def counts_line(style, findings):
    counts = Counter(f['severity'] for f in findings)
    return '  ' + style.paint(' · ', 'dim').join(
        style.paint(f'{s} {counts[s]}', s if counts[s] else 'dim', bold=bool(counts[s]))
        for s in ('critical', 'high', 'medium', 'low', 'info', 'unknown'))


def location(issue):
    where = ', '.join(issue['paths']) + (f':{issue["line"]}' if issue['line'] else '')
    if issue['package']:
        fix = ' or '.join(issue['fixed_versions']) or 'no fix yet'
        where += f'  {issue["package"]} {issue["installed_version"]} -> {fix}'
    return where


def card(style, issue):
    """One issue: the same problem as every tool that reported it saw it. A bare finding is accepted too."""
    if 'plugins' not in issue:
        issue = reports.issues([issue])[0]
    rows = [('RULE', ', '.join(issue['rules']), None, False), ('WHERE', location(issue), None, True)]
    if issue['cwe']:
        rows.append(('CWE', ', '.join(issue['cwe']), None, False))
    if issue['references']:
        rows.append(('REF', issue['references'][0], 'link', False))
    for label, key in (('PLAYBOOK', 'playbook'), ('MANUAL', 'manual')):
        value = next((manifest.plugin(p)[key] for p in issue['plugins'] if manifest.plugin(p)[key]), None)
        if value:
            rows.append((label, value, 'dim', False))
    style.box(f'{issue["severity"].upper()} · {issue["category"]} · {", ".join(issue["plugins"])}', rows, accent=issue['severity'])


def cards(style, issues, label):
    """Issues come ranked from reports.issues: what blocks first."""
    for issue in issues[:CARDS]:
        card(style, issue)
    if len(issues) > CARDS:
        style.write(style.paint(f'  {style.symbol("…", "...")} and {len(issues) - CARDS} more {label} in the report.', 'dim'))


def gap_lines(style, gaps):
    """Plugins that ran over nothing they could check: a zero-finding run is not a clean one."""
    for gap in gaps:
        paths = ''
        if gap['paths']:
            shown = gap['paths'][:3]
            paths = ': ' + ', '.join(safe(p) for p in shown) + (f' and {len(gap["paths"]) - 3} more' if len(gap['paths']) > 3 else '')
        style.write(style.paint(f'  {style.symbol("△", "!")} {", ".join(gap["plugins"])}: {gap["detail"]}{paths}', 'warn'))


def merged(style, findings, issues):
    """How many separate problems the findings describe, when tools overlap."""
    if len(issues) == len(findings):
        return ''
    return style.paint(f' · {plural(len(issues), "issue")} after merging tools', 'dim')


def gate_status(style, result):
    color = {'passed': 'ok', 'blocked': 'bad'}.get(result['status'], 'warn')
    return style.paint(result['status'].upper(), color, bold=True)


def scan_summary(style, report, output, result, fail_on='high'):
    findings = report['findings']
    issues = reports.issues(findings, report['target']['type'] == 'image')
    failed = [r for r in report['runs'] if r['status'] != 'complete']
    style.write('')
    state = style.paint('COMPLETE', 'ok', bold=True) if report['complete'] else style.paint('INCOMPLETE', 'warn', bold=True)
    style.write(f'  {style.paint("RESULT", "dim")}  {state} · {plural(len(findings), "finding")}{merged(style, findings, issues)}')
    style.write(counts_line(style, findings))
    categories = Counter(f['category'] for f in findings)
    if len(categories) > 1:
        style.write('  ' + style.paint(' · ', 'dim').join(f'{name} {count}' for name, count in sorted(categories.items())))
    for run in failed:
        style.write(style.paint(f'  {run["plugin"]}: {safe(run["error_code"])} - {safe(run["error"])}', 'warn'))
    gap_lines(style, result['gaps'])
    blocking = len(result['blocking_issues'])
    style.write(f'  {style.paint("GATE", "dim")}    {gate_status(style, result)} at {fail_on} · '
                f'{plural(blocking, "issue")} would block, without a baseline')
    style.write('')
    cards(style, issues, 'issues')
    style.write('')
    style.write(f'  {style.paint("Report", "dim")}  {short(output)} (private, mode 0600)')
    style.write(f'  {style.paint("Next", "dim")}    dso gate --input {shlex.quote(str(output))} [--baseline approved.json]')


def exception_lines(style, waived, today=None):
    """What the register did: who waived what until when, and what has lapsed."""
    today = today or date.today()
    for entry in waived['applied']:
        left = (date.fromisoformat(entry['expires_on']) - today).days
        style.write(style.paint(f'  {style.symbol("✓", "+")} exception {safe(entry["id"])} waives {plural(len(entry["findings"]), "finding")} '
                                f'until {entry["expires_on"]} ({plural(left, "day")} left)', 'warn' if left <= register.SOON else 'dim'))
    for entry in waived['expired']:
        style.write(style.paint(f'  {style.symbol("△", "!")} exception {safe(entry["id"])} expired on {entry["expires_on"]} and no longer '
                                f'covers {plural(len(entry["findings"]), "finding")}; renew it or fix the finding', 'warn'))
    if waived['unused']:
        style.write(style.paint(f'  {plural(len(waived["unused"]), "exception")} matched nothing in this report: '
                                + ', '.join(safe(i) for i in waived['unused'][:5]) + (' ...' if len(waived['unused']) > 5 else ''), 'dim'))


def gate_summary(style, result, fail_on, cards_shown=True):
    style.write('')
    blocking = ''
    if result['blocking']:
        blocking = f' · {plural(len(result["blocking_issues"]), "issue")} block'
        if len(result['blocking']) != len(result['blocking_issues']):
            blocking += style.paint(f' ({len(result["blocking"])} findings across tools)', 'dim')
    style.write(f'  {style.paint("GATE", "dim")}  {gate_status(style, result)} at {fail_on} · exit {result["exit_code"]}{blocking}')
    waived = result['exceptions']
    style.write(f'  {result["new_or_escalated"]} new or escalated · {result["existing"]} accepted by the baseline · '
                f'{len(result["resolved"])} resolved · {len(result["fix_changed"])} with a changed fix'
                + (f' · {result["exceptions"]["waived"]} waived by exceptions' if waived else ''))
    if waived:
        exception_lines(style, waived)
    identity = [k for k in result['mismatch'] if k in ('project', 'target')]
    if identity:
        style.write(style.paint('  Baseline is for a different ' + ' and '.join(identity) + '.', 'warn'))
    elif result['mismatch']:
        style.write(style.paint('  This scan covers less than the baseline (' + ', '.join(result['mismatch']) +
                                '); scan with the same plugins, profile and exclusions, or approve a new baseline.', 'warn'))
    if result['coverage_changes']:
        color = 'warn' if result['status'] == 'incomparable' else 'dim'
        style.write(style.paint('  Coverage changed since the baseline: ' + ', '.join(result['coverage_changes']), color))
        if result['status'] == 'incomparable' and not result['mismatch']:
            style.write(style.paint('  Review the changed coverage and approve a new baseline before gating.', 'warn'))
    if result['status'] == 'incomplete' and not result['mismatch']:
        style.write(style.paint('  A scan is incomplete, so the gate cannot pass. Fix the failed plugins and scan again.', 'warn'))
    gap_lines(style, result['gaps'])
    if cards_shown:
        style.write('')
        cards(style, result['blocking_issues'], 'blocking issues')


def plain(value):
    """Register text: bounded and without control characters, so the file validates later."""
    try:
        runtime.text(value, 'value', 512)
    except ValueError:
        return 'Keep it under 512 characters without control characters.'
    return None


def exception_entries(ask, style, issue, report, entries, last, today):
    """One register entry per rule of the issue, after the questions a reviewer must answer. A rule
    several tools report (one advisory from three dependency scanners) gets a single entry for any
    tool: the decision is about the vulnerability, not about who saw it."""
    owner = question(ask, style, 'Owner', last['owner'], check=plain)
    approver = question(ask, style, 'Approver (not the owner)', last['approver'],
                        check=lambda v: 'Owner and approver must differ.' if v.strip().casefold() == owner.strip().casefold() else plain(v))
    reason = question(ask, style, 'Reason', check=plain)
    control = question(ask, style, 'Compensating control', check=plain)
    ticket = question(ask, style, 'Ticket', last['ticket'], check=plain)
    days = question(ask, style, f'Days until expiry (1-{register.MAX_DAYS})', '30',
                    check=lambda v: None if v.isdigit() and 1 <= int(v) <= register.MAX_DAYS else f'Give a number from 1 to {register.MAX_DAYS}.')
    last.update(owner=owner, approver=approver, ticket=ticket)
    by_id = {f['id']: f for f in report['findings']}
    scopes = {(e['tool'].casefold(), e['rule_id'].casefold(), e['asset_id'].casefold()) for e in entries}
    reporters = {}
    for member in issue['findings']:
        reporters.setdefault(by_id[member]['rule_id'], set()).add(by_id[member]['plugin'])
    new = []
    for rule, plugins in sorted(reporters.items()):
        plugin = register.ANY if len(plugins) > 1 else next(iter(plugins))
        if (plugin.casefold(), rule.casefold(), report['project'].casefold()) in scopes:
            continue
        new.append({'id': register.next_id(entries + new, today), 'tool': plugin, 'rule_id': rule,
                    'asset_id': report['project'], 'owner': owner, 'approver': approver, 'reason': reason,
                    'compensating_control': control, 'ticket': ticket, 'created_on': today.isoformat(),
                    'expires_on': (today + timedelta(days=int(days))).isoformat()})
    return new


def triage(style, ask, report, entries, path, fail_on='high', today=None):
    """One blocking issue at a time: accept it with a time-boxed exception, skip it, or stop.
    Every accepted issue is written to the register at once, so stopping early loses nothing."""
    today = today or date.today()
    pending = reports.gate(report, fail_on=fail_on, exceptions=entries)['blocking_issues']
    style.write('')
    style.write(f'  {style.paint("TRIAGE", "dim")}  {plural(len(pending), "blocking issue")} in {safe(report["project"])} · '
                f'{plural(len(entries), "exception")} in the register')
    added, last = 0, {'owner': '', 'approver': '', 'ticket': ''}
    for number, issue in enumerate(pending, 1):
        style.write('')
        style.write(style.paint(f'  Issue {number} of {len(pending)}', 'dim'))
        card(style, issue)
        try:
            decision = question(ask, style, 'Decision: a = accept with an exception, s = skip, q = stop', 's',
                                choices=('a', 's', 'q'))
            if decision == 'q':
                break
            if decision == 's':
                continue
            new = exception_entries(ask, style, issue, report, entries, last, today)
        except Back:
            break
        if not new:
            style.write(style.paint('    The register already has an entry for every tool and rule of this issue.', 'dim'))
            continue
        entries.extend(new)
        register.write(path, entries)
        added += len(new)
        style.write(style.paint(f'    Recorded {", ".join(e["id"] for e in new)} until {new[0]["expires_on"]}.', 'ok'))
    return added


def doctor_table(style, report):
    style.write('')
    head = f'  {style.paint("ENGINE", "dim")}  {report["engine"]} · profile {report["profile"]}'
    if report.get('daemon_version'):
        head += style.paint(f' · Docker {safe(report["daemon_version"])}', 'dim')
    style.write(head)
    if report.get('error'):
        style.write(style.paint('  ' + report['error'], 'bad'))
    for tool in report['tools']:
        ok = tool['ready']
        mark = style.paint(style.symbol('✓', '+') if ok else style.symbol('✗', 'x'), 'ok' if ok else 'bad', bold=True)
        found = tool['detected_version'] or ('image present' if ok and tool['image'] else '-')
        style.write(f'  {mark} {style.paint(tool["tool"].ljust(12), bold=True)} expected {tool["expected_version"].ljust(9)} '
                    f'found {safe(found).ljust(13)} {style.paint(safe(tool.get("error") or ""), "warn")}')
    if report.get('databases'):
        style.write('')
        style.write(f'  {style.paint("DATABASES", "dim")}  {short(report["cache"]) if report.get("cache") else "no persistent cache"}')
        for d in report['databases']:
            if d['present']:
                mark = style.paint(style.symbol('✓', '+'), 'ok', bold=True)
                state = f'{size(d["bytes"])}, updated {d["updated"][:10]}'
            else:
                mark = style.paint('-', 'warn', bold=True)
                state = style.paint(f'not downloaded yet: about {megabytes(d["download_mb"])} download, '
                                    f'{megabytes(d["disk_mb"])} on disk', 'warn')
            style.write(f'  {mark} {style.paint(d["name"].ljust(24), bold=True)} {state}')
    style.write('')
    style.write('  ' + (style.paint('Ready to scan.', 'ok', bold=True) if report['ready'] else
                        style.paint('Not ready: install the pinned scanners with mcp/dso/install.sh or use --engine docker.', 'bad')))


class OrgView:
    """One line per repository while it runs, then the most exposed repositories."""

    def __init__(self, style, args, owner, names, skipped, plugins):
        self.style, self.args, self.owner, self.names, self.skipped, self.plugins = style, args, owner, names, skipped, plugins
        self.current, self.spinner, self.repo_started = None, None, time.monotonic()

    def session(self):
        style, args = self.style, self.args
        labels = {'fork': 'fork', 'archived': 'archived', 'empty': 'empty', 'over_limit': 'over the limit'}
        skipped = ', '.join(plural(count, labels[reason]) if reason == 'fork' else f'{count} {labels[reason]}'
                            for reason, count in self.skipped.items() if count)
        versions = ' · '.join(f'{n} {manifest.plugin(n)["version"]}' for n in self.plugins)
        databases = scanning.database_status(self.plugins, args.engine)
        style.write('')
        style.box('ORGANIZATION SCAN', [('ACCOUNT', f'https://github.com/{self.owner}', None, False),
                                        ('REPOS', f'{len(self.names)} to scan' + (f' · skipped {skipped}' if skipped else ''), None, False),
                                        ('PROFILE', args.profile, 'accent', False),
                                        ('ENGINE', args.engine, None, False),
                                        ('PLUGINS', versions, None, False),
                                        ('DATABASES', database_row(databases, args.engine), None, False),
                                        ('REPORTS', short(args.output_dir.expanduser()), 'dim', True)],
                  badge=(style.symbol('●', '*') + ' RUNNING', 'accent'))
        style.write('')
        database_notice(style, databases, args.engine)
        if not self.names:
            style.write(style.paint('  No public repositories to scan.', 'warn'))

    def prefix(self, index):
        width = len(str(len(self.names)))
        return self.style.paint(f'[{index:>{width}}/{len(self.names)}]', 'dim')

    def start(self, index, name):
        self.current = [index, name, 'fetch']
        self.repo_started = time.monotonic()
        style = self.style
        # The spinner shows the repository's elapsed time and the step it is in.
        self.spinner = Spinner(style, lambda frame, elapsed: (
            f'  {self.prefix(self.current[0])} {style.paint(frame, "accent", bold=True)} '
            f'{style.paint(safe(self.current[1]).ljust(24), bold=True)} {style.paint(self.current[2], "accent")}  '
            f'{style.paint(ticking(time.monotonic() - self.repo_started), "dim")}')).start()

    def step(self, event, step, detail=None):
        if event == 'start' and self.current:
            self.current[2] = step

    def close(self):
        if self.spinner:
            self.spinner.stop()
            self.spinner = None
            if self.style.live:
                self.style.write('')

    def done(self, index, entry, elapsed):
        style = self.style
        if self.spinner:
            self.spinner.stop()
            self.spinner = None
        name = safe(entry['repository'].split('/', 1)[1])
        ok = entry['complete']
        mark = style.paint(style.symbol('✓', '+') if ok else style.symbol('✗', 'x'), 'ok' if ok else 'bad', bold=True)
        if entry['report'] is None:
            note = style.paint(f'FAILED  {safe(entry["error_code"])}: {safe(entry["error"])}', 'bad')
        else:
            found = ' · '.join(style.paint(f'{s} {entry["findings"][s]}', s) for s in ORDER if entry['findings'].get(s))
            gate = {'passed': 'ok', 'blocked': 'bad'}.get(entry['gate'], 'warn')
            note = (found or style.paint('no findings', 'ok')) + '  ' + style.paint(entry['gate'].upper(), gate, bold=True)
            if not ok:
                note += style.paint(f'  incomplete: {safe(entry["error"])}', 'warn')
        style.write(('\r\x1b[2K' if style.live else '') +
                    f'  {self.prefix(index)} {mark} {style.paint(name.ljust(24), bold=True)} {note}  '
                    f'{style.paint(duration(elapsed), "dim")}')

    def summary(self, entries, output_dir):
        style = self.style
        scanned = [e for e in entries if e['report']]
        totals = Counter()
        for e in scanned:
            totals.update(e['findings'])
        style.write('')
        complete = sum(e['complete'] for e in entries)
        style.write(f'  {style.paint("RESULT", "dim")}  {len(entries)} repositories · '
                    f'{style.paint(f"{complete} complete", "ok" if entries and complete == len(entries) else "warn", bold=True)} · '
                    f'{len(entries) - len(scanned)} could not be fetched')
        style.write(counts_line(style, [{'severity': s} for s, n in totals.items() for _ in range(n)]))
        exposed = sorted((e for e in scanned if e['blocking']),
                         key=lambda e: tuple(-e['findings'].get(s, 0) for s in ORDER))
        if exposed:
            style.write('')
            style.write(f'  {style.paint("MOST EXPOSED", "dim")}')
            for e in exposed[:CARDS]:
                found = ' · '.join(style.paint(f'{s} {e["findings"][s]}', s) for s in ORDER if e['findings'].get(s))
                style.write(f'    {style.paint(safe(e["repository"]).ljust(32), bold=True)} {found}')
        style.write('')
        style.write(f'  {style.paint("Reports", "dim")} {short(output_dir)}/summary.json and repos/ (private)')
        if exposed:
            first = output_dir / exposed[0]['report']
            style.write(f'  {style.paint("Next", "dim")}    dso gate --input {shlex.quote(str(first))}')


def config_table(style, settings, sources, location):
    """Every setting, its value and where it came from."""
    style.write('')
    state = 'read' if location.is_file() else 'not found; dso config init writes one with the defaults'
    style.write(f'  {style.paint("CONFIG", "dim")}  {short(location)} ({state})')
    style.write(style.paint('  precedence: option > environment > file > default', 'dim'))
    style.write('')
    for key, value in settings.items():
        shown = 'auto' if value is None else short(value) if key.endswith('_dir') else str(value)
        source = sources[key]
        variable = config.ENVIRONMENT.get(key)
        origin = f'environment ({variable})' if source == 'environment' else source
        style.write(f'  {style.paint(key.ljust(15), bold=True)} {shown.ljust(28)[:28]} '
                    f'{style.paint(origin, "accent" if source != "default" else "dim")}')
    style.write('')
    style.paragraph('cache_dir auto means ~/.cache/dso when it is private to you. '
                    'max_report_mb and max_findings bound every report DSO writes or reads, including baselines in CI.', 'dim')
