#!/usr/bin/env python3
"""Small, dependency-free entry point for the security baseline."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import manifest
import scanning
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
    """Check a private risk register; never apply scanner suppressions."""
    register = read_json(input_path)
    entries = register.get("exceptions")
    if not isinstance(entries, list):
        raise ValueError("exceptions must be a list")
    issues = []
    seen = set()
    scopes = set()
    for number, entry in enumerate(entries, start=1):
        label = f"exception {number}"
        if not isinstance(entry, dict):
            raise ValueError(f"{label}: expected an object")
        for field in ("id", "tool", "rule_id", "asset_id", "owner", "approver",
                      "reason", "compensating_control", "ticket"):
            if not nonempty_text(entry.get(field)):
                issues.append(f"{label}: missing {field}")
        exception_id = entry.get("id")
        if nonempty_text(exception_id):
            exception_id = exception_id.strip().casefold()
        if nonempty_text(entry.get("owner")) and nonempty_text(entry.get("approver")) and entry["owner"].strip().casefold() == entry["approver"].strip().casefold():
            issues.append(f"{label}: owner and approver must differ")
        if nonempty_text(exception_id):
            if exception_id in seen:
                issues.append(f"{label}: duplicate id {exception_id}")
            seen.add(exception_id)
        scope = tuple(str(entry.get(k, "")).strip().casefold() for k in ("tool", "rule_id", "asset_id"))
        if scope in scopes:
            issues.append(f"{label}: duplicate exception scope")
        scopes.add(scope)
        try:
            created = parse_date(entry.get("created_on"), f"{label}.created_on")
            expires = parse_date(entry.get("expires_on"), f"{label}.expires_on")
            if created > datetime.now(timezone.utc).date():
                issues.append(f"{label}: creation date in future")
            if expires <= datetime.now(timezone.utc).date():
                issues.append(f"{label}: expired")
            if expires <= created or (expires - created).days > 90:
                issues.append(f"{label}: expiry must be 1–90 days after creation")
        except ValueError as exc:
            issues.append(str(exc))
    report = {"exceptions": len(entries), "issues": issues}
    if output_format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"Exceptions: {len(entries)} entries, {len(issues)} issues")
        for issue in issues:
            print(issue)
    return 1 if issues else 0


def main() -> int:
    try:
        plugins, profiles = sorted(manifest.plugins()), sorted(manifest.profiles())
    except (ValueError, OSError) as exc:
        print(f"dso: {exc}", file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(prog="dso")
    commands = parser.add_subparsers(dest="command", required=True)
    assess_parser = commands.add_parser("assess", help="validate baseline evidence and show gaps")
    assess_parser.add_argument("--input", type=Path, required=True, help="private assessment JSON")
    assess_parser.add_argument("--all", action="store_true", help="include extended controls")
    assess_parser.add_argument("--format", choices=("text", "json"), default="text")
    inventory_parser = commands.add_parser("inventory", help="validate asset ownership inventory")
    inventory_parser.add_argument("--input", type=Path, required=True, help="private inventory CSV")
    inventory_parser.add_argument("--format", choices=("text", "json"), default="text")
    exception_parser = commands.add_parser("exceptions", help="check exception ownership and expiry")
    exception_parser.add_argument("--input", type=Path, required=True, help="private exception register JSON")
    exception_parser.add_argument("--format", choices=("text", "json"), default="text")
    doctor_parser = commands.add_parser("doctor", help="check reviewed scanner versions or Docker availability")
    doctor_parser.add_argument("--engine", choices=("native", "docker"), default="native")
    scan_parser = commands.add_parser("scan", help="run scanners and emit a normalized report")
    scan_commands = scan_parser.add_subparsers(dest="scan_type", required=True)
    repo_parser = scan_commands.add_parser("repo")
    repo_parser.add_argument("path")
    repo_parser.add_argument("--profile", choices=profiles, default=scanning.DEFAULT_PROFILE,
                             help="plugin and rule selection from tools/dso/plugins.json; recorded in coverage")
    repo_parser.add_argument("--plugins", "--tools", dest="plugins", nargs="+", choices=plugins,
                             help="run only these plugins of the profile")
    repo_parser.add_argument("--engine", choices=("native", "docker"), default="native")
    repo_parser.add_argument("--timeout", type=int, default=300)
    repo_parser.add_argument("--project", required=True, help="explicit stable project ID")
    repo_parser.add_argument("--exclude", action="append", default=[], help="reviewed target-relative path exclusion; recorded in coverage")
    repo_parser.add_argument("--output", type=Path, required=True)
    gate_parser = commands.add_parser("gate", help="block findings or new/escalated findings against a baseline")
    gate_parser.add_argument("--input", type=Path, required=True)
    gate_parser.add_argument("--baseline", type=Path)
    gate_parser.add_argument("--fail-on", choices=[s for s in scanning.SEVERITIES if s != "unknown"], default="high")
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            report = scanning.doctor(args.engine)
            print(json.dumps(report, indent=2))
            return 0 if report["ready"] else 2
        if args.command == "scan":
            scanning.prepare_output(args.output)
            report = scanning.scan_repo(args.path, args.plugins, args.engine, args.timeout, args.project,
                                        exclusions=args.exclude, profile=args.profile)
            scanning.write_report(args.output, report)
            print(json.dumps({"complete": report["complete"], "findings": len(report["findings"]),
                              "report": str(args.output)}))
            return 0 if report["complete"] else 2
        if args.command == "gate":
            result = scanning.gate(read_json(args.input),
                                   read_json(args.baseline) if args.baseline else None, args.fail_on)
            print(json.dumps(result, indent=2))
            return result["exit_code"]
        if args.command == "assess":
            return assess(args.input, args.all, args.format)
        if args.command == "inventory":
            return inventory(args.input, args.format)
        if args.command == "exceptions":
            return exceptions(args.input, args.format)
    except runtime.Cancelled:
        print("dso: operation cancelled", file=sys.stderr)
        return 130
    except (ValueError, OSError, csv.Error, RecursionError, KeyError, TypeError) as exc:
        print(f"dso: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    with runtime.signals():
        sys.exit(main())
