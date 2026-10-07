#!/usr/bin/env python3
"""Small, dependency-free entry point for the security baseline."""

from __future__ import annotations

import argparse
from collections import Counter
import contextlib
import csv
import json
import re
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config
import console
import manifest
import register
import scanning
import sources
import runtime

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "baseline" / "controls.json"
STATUSES = {"implemented", "partial", "missing", "not_applicable"}
INVENTORY_FIELDS = {"asset_id", "asset_type", "name", "environment", "owner",
                    "criticality", "internet_exposed", "data_classification"}


def read_json(path: Path) -> dict:
    return runtime.read_json(path)


def parse_date(value: object, label: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"{label}: expected YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label}: expected YYYY-MM-DD") from exc


def assess(input_path: Path, include_extended: bool, output_format: str) -> int:
    catalog = read_json(CATALOG)
    assessment = read_json(input_path)
    entries = catalog.get("controls")
    records = assessment.get("controls")
    if not isinstance(entries, list) or not isinstance(records, dict):
        raise ValueError("Invalid catalog or assessment: controls must be a list or object")
    as_of = parse_date(assessment.get("as_of"), "as_of")
    if as_of > datetime.now(timezone.utc).date():
        raise ValueError("as_of cannot be in the future")
    if (datetime.now(timezone.utc).date() - as_of).days > 7:
        raise ValueError("as_of is older than 7 days; refresh the assessment")
    ids = [entry.get("id") for entry in entries if isinstance(entry, dict)]
    if len(ids) != len(entries) or len(ids) != len(set(ids)):
        raise ValueError("Catalog has missing or duplicate control IDs")
    unknown = sorted(set(records) - set(ids))
    if unknown:
        raise ValueError("Unknown control IDs: " + ", ".join(unknown))

    results = []
    for entry in entries:
        if entry.get("tier") == "extended" and not include_extended:
            continue
        control_id = entry["id"]
        record = records.get(control_id)
        issues = []
        if not isinstance(record, dict):
            status = "unassessed"
            issues.append("no assessment")
        else:
            status = record.get("status")
            if not isinstance(status, str) or status not in STATUSES:
                issues.append("invalid status")
            if not isinstance(record.get("owner"), str) or not record["owner"].strip():
                issues.append("missing owner")
            try:
                reviewed = parse_date(record.get("reviewed_on"), f"{control_id}.reviewed_on")
                if reviewed > as_of:
                    issues.append("review date after as_of")
                elif (as_of - reviewed).days > entry["review_days"]:
                    issues.append("stale review")
            except ValueError:
                issues.append("missing or invalid review date")
            if status == "implemented" and not nonempty_text(record.get("evidence")):
                issues.append("implemented without evidence")
            if status == "not_applicable" and not nonempty_text(record.get("note")):
                issues.append("not_applicable without reason")
            if isinstance(status, str) and status in {"partial", "missing"}:
                issues.append(status)
            if not isinstance(status, str):
                status = "invalid"
        results.append({
            "id": control_id,
            "domain": entry["domain"],
            "title": entry["title"],
            "status": status,
            "issues": issues,
        })

    counts = {key: sum(item["status"] == key for item in results)
              for key in sorted(STATUSES | {"unassessed"})}
    failing = [item for item in results if item["issues"]]
    report = {"organization": assessment.get("organization"),
              "as_of": as_of.isoformat(), "counts": counts,
              "gaps": failing, "assessed": len(results)}
    if output_format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"{report['organization'] or 'Assessment'} — {as_of} — {len(results)} controls")
        print(" ".join(f"{key}={value}" for key, value in counts.items()))
        for item in failing:
            print(f"{item['id']} [{item['domain']}]: {', '.join(item['issues'])} — {item['title']}")
    return 1 if failing else 0


def inventory(input_path: Path, output_format: str) -> int:
    try:
        with input_path.open(newline="", encoding="utf-8-sig") as source:
            reader = csv.DictReader(source, strict=True)
            if not reader.fieldnames or not INVENTORY_FIELDS.issubset(reader.fieldnames):
                raise ValueError("Inventory is missing required columns: " +
                                 ", ".join(sorted(INVENTORY_FIELDS - set(reader.fieldnames or []))))
            if len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise ValueError("Duplicate CSV headers")
            rows = list(reader)
            for row in rows:
                for field in INVENTORY_FIELDS:
                    if isinstance(row.get(field), str):
                        row[field] = row[field].strip()
                for field in ("criticality", "internet_exposed"):
                    if isinstance(row.get(field), str):
                        row[field] = row[field].lower()
    except OSError as exc:
        raise ValueError(f"Cannot read {input_path}: {exc}") from exc

    seen = set()
    issues = []
    for number, row in enumerate(rows, start=2):
        if None in row:
            issues.append(f"row {number}: extra columns")
        for field in INVENTORY_FIELDS:
            if not (row.get(field) or "").strip():
                issues.append(f"row {number}: missing {field}")
        asset_id = (row.get("asset_id") or "").strip()
        if asset_id:
            if asset_id in seen:
                issues.append(f"row {number}: duplicate asset_id {asset_id}")
            seen.add(asset_id)
        if row.get("criticality") not in {"low", "medium", "high", "critical"}:
            issues.append(f"row {number}: invalid criticality")
        if row.get("internet_exposed") not in {"true", "false"}:
            issues.append(f"row {number}: internet_exposed must be true or false")
    if not rows:
        issues.append("inventory has no assets")
    report = {"assets": len(rows), "issues": issues}
    if output_format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"Inventory: {len(rows)} assets, {len(issues)} issues")
        for issue in issues:
            print(issue)
    return 1 if issues else 0


def nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def exceptions(input_path: Path, output_format: str) -> int:
    """Check a private exception register: structure, owners, approvers and expiry."""
    data = read_json(input_path)
    issues = [message for _, message in register.problems(data)]
    report = {"exceptions": len(data["exceptions"]), "issues": issues}
    if output_format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"Exceptions: {len(data['exceptions'])} entries, {len(issues)} issues")
        for issue in issues:
            print(issue)
    return 1 if issues else 0


def triage(args: argparse.Namespace, style: console.Style) -> int:
    """Walk through the issues that block a report and record exceptions for the accepted ones."""
    if not console.interactive():
        raise ValueError("triage asks questions; run it in a terminal")
    report = read_json(args.input)
    scanning.validate_report(report)
    entries = register.read(args.exceptions)
    added = console.triage(style, input, report, entries, args.exceptions, args.fail_on)
    result = scanning.gate(report, exceptions=register.read(args.exceptions), fail_on=args.fail_on)
    console.gate_summary(style, result, args.fail_on, cards_shown=False)
    style.write(f"  {style.paint('Register', 'dim')}  {console.short(args.exceptions)} · {added} added · "
                f"keep it private and review it with dso exceptions")
    return result["exit_code"]


DESCRIPTION = """\
DSO, DevSecOps for all: scan a local project or public GitHub repositories with
pinned, reviewed scanners (secrets, code, dependencies), keep a private
normalized report, and gate it by severity and against an approved baseline.
Code stays on this machine.

Run dso without arguments in a terminal for the interactive menu."""

EPILOG = """\
examples:
  dso                                   interactive menu
  dso scan https://github.com/owner/repo
  dso scan ~/src/app                    a folder, or one file
  dso scan alpine:3.20                  an image; the tag is pinned to its digest
  dso doctor                            are the pinned scanners installed?
  dso scan repo . --project team/app --output ~/.dso/reports/app.json
  dso scan repo . --project team/app --output r.json --plugins gitleaks
  dso scan repo https://github.com/owner/repo --output ~/.dso/reports/repo.json
  dso scan org https://github.com/owner --output-dir ~/.dso/reports/owner
  dso scan image docker.io/library/alpine:3.20@sha256:<digest> --output alpine.json
  dso gate --input ~/.dso/reports/app.json --fail-on high
  dso gate --input new.json --baseline approved.json --exceptions /private/exceptions.json
  dso triage --input new.json --exceptions /private/exceptions.json

exit codes:
  0  completed, or the gate passed     2  incomplete scan or invalid input
  1  blocking findings or gaps         130 interrupted

Plugins and profiles: tools/dso/plugins.json. Guide: tools/dso/README.md."""

FORMAT_HELP = "text in a terminal, JSON otherwise (default: auto)"


LIMIT_HELP = {"max_report_mb": "largest report to write or read, 20-1024 MiB (default from dso config: %(default)s)",
              "max_findings": "most findings in one report, 1000-1000000 (default from dso config: %(default)s)"}


def limit_options(target_parser, settings):
    target_parser.add_argument("--max-report-mb", type=int, default=settings["max_report_mb"], metavar="MB",
                               help=LIMIT_HELP["max_report_mb"])
    target_parser.add_argument("--max-findings", type=int, default=settings["max_findings"], metavar="N",
                               help=LIMIT_HELP["max_findings"])


def build_parser(plugins: list[str], profiles: list[str], settings: dict) -> argparse.ArgumentParser:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(prog="dso", description=DESCRIPTION, epilog=EPILOG, formatter_class=formatter)
    parser.add_argument("--version", action="version", version=f"dso {scanning.VERSION} (" + ", ".join(
        f"{name} {manifest.plugin(name)['version']}" for name in plugins) + ")")
    commands = parser.add_subparsers(dest="command", metavar="<command>", title="commands")

    scan_parser = commands.add_parser(
        "scan", help="scan a folder, file, GitHub URL or image and save a private report", formatter_class=formatter,
        description="Scan a target with the plugins of a profile and write a normalized v3 report.\n\n"
                    "dso scan TARGET works out what TARGET is (folder, file, GitHub repository or account URL,\n"
                    "image name) and picks the project ID, the most complete profile whose scanners are all\n"
                    "installed, and a report file in ~/.dso/reports. Any option below still overrides them.",
        epilog="examples:\n  dso scan https://github.com/we45/Vulnerable-Flask-App\n  dso scan . --profile ci-blocking\n"
               "  dso scan ghcr.io/owner/app:1.2\n  dso scan repo . --project team/app --output report.json")
    scan_commands = scan_parser.add_subparsers(dest="scan_type", required=True, metavar="<target>", title="targets")
    def scan_options(target_parser, default_profile=scanning.DEFAULT_PROFILE):
        target = manifest.profile(default_profile)["target"]
        target_parser.add_argument("--profile", default=default_profile,
                                   choices=[name for name in profiles if manifest.profile(name)["target"] == target],
                                   help="plugin and rule selection from tools/dso/plugins.json (default: %(default)s)")
        target_parser.add_argument("--plugins", "--tools", dest="plugins", nargs="+", choices=plugins, metavar="PLUGIN",
                                   help="run only these plugins of the profile: " + ", ".join(plugins))
        target_parser.add_argument("--engine", choices=("native", "docker"), default=settings["engine"],
                                   help="native: scanners on this machine; docker: pinned scanner images (default: %(default)s)")
        target_parser.add_argument("--timeout", type=int, default=settings["timeout"], metavar="SECONDS",
                                   help="per-plugin limit, 1-1800 (default: %(default)s)")
        limit_options(target_parser, settings)
        target_parser.add_argument("--exclude", action="append", default=[], metavar="PATH",
                                   help="reviewed path inside the target to leave out; repeatable, recorded in the report")
        target_parser.add_argument("--format", choices=("auto", "text", "json"), default="auto", help=FORMAT_HELP)

    repo_parser = scan_commands.add_parser(
        "repo", help="a project directory or a public GitHub repository URL", formatter_class=formatter,
        description="Scan a local directory, or fetch the default branch of a public GitHub repository\n"
                    "(anonymously, without running anything from it) and scan that. DSO copies the tree into a\n"
                    "private snapshot; ignore files and inline allow comments are not honoured. Exit 0 when every\n"
                    "plugin completed (findings or not), 2 when the scan is incomplete. Use dso gate to enforce.",
        epilog="examples:\n  dso scan repo ~/src/app --project team/app --output ~/.dso/reports/app.json\n"
               "  dso scan repo https://github.com/owner/repo --output ~/.dso/reports/repo.json")
    repo_parser.add_argument("path", metavar="PATH_OR_URL", help="project directory, or https://github.com/OWNER/REPO")
    repo_parser.add_argument("--project", help="stable project ID shared by local and CI scans, e.g. owner/repository; "
                                               "required for a directory, github.com/OWNER/REPO for a URL")
    repo_parser.add_argument("--output", type=Path, required=True,
                             help="report file; written atomically with mode 0600 and kept private")
    scan_options(repo_parser)

    image_parser = scan_commands.add_parser(
        "image", help="a container image from a public registry, pinned by digest", formatter_class=formatter,
        description="Scan a container image for OS and language package vulnerabilities. The scanners pull it\n"
                    "from its registry anonymously, so the image must be public and pinned by digest. Exit 0 when\n"
                    "every plugin completed, 2 when the scan is incomplete.",
        epilog="example:\n  dso scan image docker.io/library/alpine:3.20@sha256:<digest> --output ~/.dso/reports/alpine.json")
    image_parser.add_argument("path", metavar="IMAGE", help="registry/name[:tag]@sha256:<64 hex>")
    image_parser.add_argument("--project", help="stable project ID (default: the image name without tag or digest)")
    image_parser.add_argument("--output", type=Path, required=True,
                              help="report file; written atomically with mode 0600 and kept private")
    scan_options(image_parser, scanning.DEFAULT_IMAGE_PROFILE)

    org_parser = scan_commands.add_parser(
        "org", help="every public repository of a GitHub organization or user", formatter_class=formatter,
        description="List the public repositories of a GitHub organization or user (forks and archived ones\n"
                    "are skipped unless asked), fetch and scan each, and write one report per repository plus\n"
                    "summary.json. Anonymous GitHub API use allows 60 requests per hour. Exit 0 when every\n"
                    "repository was scanned completely, 2 otherwise.",
        epilog="example:\n  dso scan org https://github.com/owner --output-dir ~/.dso/reports/owner --limit 20")
    org_parser.add_argument("url", metavar="URL", help="https://github.com/OWNER")
    org_parser.add_argument("--output-dir", type=Path, required=True, help="private directory for the reports (mode 0700)")
    org_parser.add_argument("--limit", type=int, default=50, help="scan at most this many repositories (default: %(default)s)")
    org_parser.add_argument("--include-forks", action="store_true", help="also scan forks")
    org_parser.add_argument("--include-archived", action="store_true", help="also scan archived repositories")
    scan_options(org_parser)

    gate_parser = commands.add_parser(
        "gate", help="pass or block a report, optionally against an approved baseline", formatter_class=formatter,
        description="Without a baseline every finding at or above the threshold blocks. With one, only new or\n"
                    "escalated findings block. Unknown severity always blocks. Exit 0 pass, 1 blocked,\n"
                    "2 incomplete or incomparable (different project, or an incomplete scan).",
        epilog="examples:\n  dso gate --input report.json\n  dso gate --input report.json --baseline approved.json --fail-on critical")
    gate_parser.add_argument("--input", type=Path, required=True, help="report from dso scan")
    gate_parser.add_argument("--baseline", type=Path, help="approved earlier report of the same project")
    gate_parser.add_argument("--exceptions", type=Path, metavar="REGISTER",
                             help="private exception register (dso exceptions); active entries stop their findings from blocking")
    gate_parser.add_argument("--fail-on", choices=[s for s in scanning.SEVERITIES if s != "unknown"], default="high",
                             help="lowest severity that blocks (default: %(default)s)")
    gate_parser.add_argument("--format", choices=("auto", "text", "json"), default="auto", help=FORMAT_HELP)
    limit_options(gate_parser, settings)

    triage_parser = commands.add_parser(
        "triage", help="walk through blocking issues and record exceptions", formatter_class=formatter,
        description="Show each issue that blocks the report, one at a time, and record a time-boxed exception\n"
                    "(owner, a different approver, reason, compensating control, ticket, 1-90 days) for the\n"
                    "ones you accept. Entries are appended to the register; dso gate --exceptions applies them.",
        epilog="examples:\n  dso triage --input report.json --exceptions /private/path/exceptions.json")
    triage_parser.add_argument("--input", type=Path, required=True, help="report from dso scan")
    triage_parser.add_argument("--exceptions", type=Path, required=True, metavar="REGISTER",
                               help="exception register to add to; created when missing")
    triage_parser.add_argument("--fail-on", choices=[s for s in scanning.SEVERITIES if s != "unknown"], default="high",
                               help="lowest severity that blocks (default: %(default)s)")
    triage_parser.add_argument("--format", choices=("auto", "text"), default="auto", help="text only; triage asks questions")
    limit_options(triage_parser, settings)

    config_parser = commands.add_parser(
        "config", help="show the effective settings and where they come from", formatter_class=formatter,
        description="Settings come from, in rising precedence, built-in defaults, ~/.dso/config.json (or DSO_CONFIG),\n"
                    "environment variables (DSO_REPORTS_DIR, DSO_CACHE_DIR, DSO_MAX_REPORT_MB, DSO_MAX_FINDINGS) and\n"
                    "command-line options. The file is never read from a scanned directory.",
        epilog="examples:\n  dso config\n  dso config init\n  dso config --format json")
    config_parser.add_argument("action", nargs="?", choices=("show", "init"), default="show",
                               help="show the settings, or init: write a file with every default (default: show)")
    config_parser.add_argument("--force", action="store_true", help="init: replace an existing file")
    config_parser.add_argument("--format", choices=("auto", "text", "json"), default="auto", help=FORMAT_HELP)

    doctor_parser = commands.add_parser(
        "doctor", help="check that the pinned scanners are installed", formatter_class=formatter,
        description="native: check each scanner's path and version. docker: check the daemon and whether each\n"
                    "pinned image is present locally (a scan pulls missing ones). Installs nothing.")
    doctor_parser.add_argument("--engine", choices=("native", "docker"), default="native", help="(default: %(default)s)")
    doctor_parser.add_argument("--profile", choices=profiles, default=scanning.DEFAULT_PROFILE,
                               help="check the scanners of this profile (default: %(default)s)")
    doctor_parser.add_argument("--format", choices=("auto", "text", "json"), default="auto", help=FORMAT_HELP)

    for name, summary, description, label in (
            ("assess", "check security baseline evidence and show gaps",
             "Validate a private assessment against baseline/controls.json: owners, review dates and evidence.",
             "private assessment JSON"),
            ("inventory", "check the asset ownership inventory",
             "Validate a private asset inventory CSV: required columns, owners, criticality and exposure.",
             "private inventory CSV"),
            ("exceptions", "check exception owners, approvers and expiry",
             "Validate a private exception register: owner differs from approver, expiry within 1-90 days.",
             "private exception register JSON")):
        register = commands.add_parser(name, help=summary, description=description, formatter_class=formatter)
        register.add_argument("--input", type=Path, required=True, help=label)
        if name == "assess":
            register.add_argument("--all", action="store_true", help="include extended controls")
        register.add_argument("--format", choices=("text", "json"), default="text", help="(default: %(default)s)")
    return parser


def run_scan(args: argparse.Namespace, image: bool, remote: tuple[str, str] | None, progress) -> dict:
    if image:
        if args.exclude:
            raise ValueError("--exclude applies to directories, not images")
        return scanning.scan_image(args.path, args.plugins, args.engine, args.timeout, args.project,
                                   profile=args.profile, progress=progress)
    fetched = (sources.checkout(*remote, exclusions=args.exclude, progress=progress) if remote
               else contextlib.nullcontext((args.path, None)))
    with fetched as (path, origin):
        return scanning.scan_repo(path, args.plugins, args.engine, args.timeout, args.project,
                                  exclusions=args.exclude, profile=args.profile, progress=progress, origin=origin)


def scan_repositories(args, owner, repositories, plugins, output_dir, view):
    """Fetch and scan each repository; a failed fetch is recorded and the next one runs."""
    entries = []
    for index, metadata in enumerate(repositories, 1):
        name = metadata['name']
        started = time.monotonic()
        entry = {"repository": f"{owner}/{name}", "report": None, "complete": False, "commit": None,
                 "findings": {}, "issues": 0, "gate": None, "blocking": 0}
        if view:
            view.start(index, name)
        try:
            with sources.checkout(owner, name, args.exclude, progress=view.step if view else None,
                                  metadata=metadata) as (path, origin):
                report = scanning.scan_repo(path, args.plugins, args.engine, args.timeout, sources.project_id(owner, name),
                                            exclusions=args.exclude, profile=args.profile, origin=origin,
                                            progress=view.step if view else None)
            scanning.write_report(output_dir / "repos" / f"{name}.json", report)
            result = scanning.gate(report)
            entry.update(report=f"repos/{name}.json", complete=report["complete"], commit=origin["commit"],
                         findings=dict(Counter(f["severity"] for f in report["findings"])),
                         issues=len(scanning.issues(report["findings"])),
                         gate=result["status"], blocking=len(result["blocking_issues"]))
            failed = [r for r in report["runs"] if r["status"] != "complete"]
            if failed:
                entry.update(error_code=failed[0]["error_code"], error=f"{failed[0]['plugin']}: {failed[0]['error']}")
        except runtime.Cancelled:
            raise
        except runtime.ScanError as exc:
            entry.update(error_code=exc.code, error=str(exc))
        entries.append(entry)
        if view:
            view.done(index, entry, time.monotonic() - started)
    return entries


def scan_org(args: argparse.Namespace, style: console.Style) -> int:
    """Fetch and scan every selected public repository; one report each plus summary.json."""
    owner, name = sources.parse(args.url)
    if name:
        raise ValueError("that is a repository URL; use dso scan repo for one repository")
    plugins = scanning.selected_plugins(args.plugins, args.profile)
    output_dir = args.output_dir.expanduser()
    if output_dir.is_symlink() or (output_dir.exists() and not output_dir.is_dir()):
        raise ValueError("--output-dir must be a directory, not a symlink or file")
    output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    repositories, skipped = sources.repositories(owner, args.include_forks, args.include_archived, args.limit)
    names = [metadata['name'] for metadata in repositories]
    view = console.OrgView(style, args, owner, names, skipped, plugins) if human(args) else None
    if view:
        view.session()
    try:
        entries = scan_repositories(args, owner, repositories, plugins, output_dir, view)
    finally:
        if view:
            view.close()
    summary = {"source": f"https://github.com/{owner}", "created_at": datetime.now(timezone.utc).isoformat(),
               "profile": args.profile, "plugins": plugins, "engine": args.engine, "skipped": skipped,
               "repositories": entries}
    scanning.write_report(output_dir / "summary.json", summary)
    complete = bool(entries) and all(entry["complete"] for entry in entries)
    if view:
        view.summary(entries, output_dir)
    else:
        print(json.dumps({"complete": complete, "repositories": len(entries),
                          "summary": str(output_dir / "summary.json")}))
    return 0 if complete else 2


SCAN_TYPES = ("repo", "org", "image")


def expand_scan(argv: list[str], settings: dict | None = None) -> tuple[list[str], tuple[str, str] | None]:
    """dso scan TARGET [options]: classify TARGET and fill in the target type, project, profile and output."""
    settings = settings or config.load()[0]
    if len(argv) < 2 or argv[0] != "scan" or argv[1] in SCAN_TYPES or argv[1].startswith("-"):
        return argv, None
    kind, value = sources.classify(argv[1])
    rest = argv[2:]
    scan_type = {"directory": "repo", "file": "repo", "repository": "repo", "account": "org", "image": "image"}[kind]
    if kind == "image":
        name = scanning.image_project(value)
    elif kind in ("repository", "account"):
        name = value.split("github.com/", 1)[1]
    else:
        name = Path(value).name
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def given(option):
        return any(arg == option or arg.startswith(option + "=") for arg in rest)
    added = []
    if scan_type != "org" and not given("--project"):
        added += ["--project", sources.project_id(*name.split("/", 1)) if kind == "repository" else name]
    if not given("--profile"):
        configured = settings.get("profile") if kind != "image" else None
        added += ["--profile", configured or scanning.preferred_profile("image" if kind == "image" else "repo")]
    reports = Path(settings["reports_dir"]).expanduser()
    if scan_type == "org" and not given("--output-dir"):
        added += ["--output-dir", str(reports / f"{console.slug(name)}-{stamp}")]
    if scan_type != "org" and not given("--output"):
        added += ["--output", str(reports / f"{console.slug(name)}-{stamp}.json")]
    return ["scan", scan_type, value, *rest, *added], (kind, value)


def human(args: argparse.Namespace) -> bool:
    return args.format == "text" or (args.format == "auto" and sys.stdout.isatty())


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        plugins, profiles = sorted(manifest.plugins()), sorted(manifest.profiles())
        settings, origins = config.load()
        config.apply(settings)
    except (ValueError, OSError) as exc:
        print(f"dso: {exc}", file=sys.stderr)
        return 2
    parser = build_parser(plugins, profiles, settings)
    try:
        if not argv:
            if not console.interactive():
                parser.print_usage(sys.stderr)
                print("dso: choose a command; dso --help lists them", file=sys.stderr)
                return 2
            argv = console.menu()
            if argv is None:
                return 0
        argv, detected = expand_scan(argv, settings)
        args = parser.parse_args(argv)
        args.detected = detected
        if args.command is None:
            parser.print_help()
            return 2
        if hasattr(args, "max_report_mb"):
            overrides = {key: getattr(args, key) for key in ("max_report_mb", "max_findings")}
            settings, origins = config.load({key: value for key, value in overrides.items()
                                             if value != settings[key] or origins[key] == "option"})
            config.apply(settings)
        style = console.Style()
        if args.command == "config":
            if args.action == "init":
                location = config.write_defaults(config.path(), args.force)
                print(f"Wrote {location}; edit it and run dso config to check")
                return 0
            if human(args):
                console.config_table(style, settings, origins, config.path())
            else:
                print(json.dumps({"path": str(config.path()), "settings": settings, "sources": origins}, indent=2))
            return 0
        if args.command == "doctor":
            report = scanning.doctor(args.engine, profile=args.profile)
            if human(args):
                console.doctor_table(style, report)
            else:
                print(json.dumps(report, indent=2))
            return 0 if report["ready"] else 2
        if args.command == "scan" and args.scan_type == "org":
            return scan_org(args, style)
        if args.command == "scan":
            image = args.scan_type == "image"
            remote = sources.parse(args.path) if not image and sources.is_remote(args.path) else None
            if remote and remote[1] is None:
                raise ValueError("that is an account URL; use dso scan org to scan all of its repositories")
            if image and not scanning.IMAGE_REFERENCE.fullmatch(args.path):
                raise ValueError("give an image pinned by digest, such as registry/name:tag@sha256:<64 hex>")
            args.project = args.project or (scanning.image_project(args.path) if image else
                                            sources.project_id(*remote) if remote else None)
            if not args.project:
                raise ValueError("--project is required when scanning a directory")
            scanning.prepare_output(args.output)
            view = console.ScanView(style, args) if human(args) else None
            if view:
                view.session(scanning.selected_plugins(args.plugins, args.profile))
            progress = view.progress if view else None
            try:
                report = run_scan(args, image, remote, progress)
            finally:
                if view:
                    view.close()
            scanning.write_report(args.output, report)
            if view:
                console.scan_summary(style, report, args.output, scanning.gate(report))
            else:
                print(json.dumps({"complete": report["complete"], "findings": len(report["findings"]),
                                  "issues": len(scanning.issues(report["findings"], image)), "report": str(args.output)}))
            return 0 if report["complete"] else 2
        if args.command == "gate":
            result = scanning.gate(read_json(args.input), read_json(args.baseline) if args.baseline else None,
                                   args.fail_on, register.load(args.exceptions) if args.exceptions else None)
            if human(args):
                console.gate_summary(style, result, args.fail_on)
            else:
                print(json.dumps(result, indent=2))
            return result["exit_code"]
        if args.command == "assess":
            return assess(args.input, args.all, args.format)
        if args.command == "inventory":
            return inventory(args.input, args.format)
        if args.command == "exceptions":
            return exceptions(args.input, args.format)
        if args.command == "triage":
            return triage(args, style)
    except (runtime.Cancelled, EOFError, KeyboardInterrupt):
        print("\ndso: operation cancelled", file=sys.stderr)
        return 130
    except (ValueError, OSError, csv.Error, RecursionError, KeyError, TypeError) as exc:
        print(f"dso: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    with runtime.signals():
        sys.exit(main())
