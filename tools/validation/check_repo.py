#!/usr/bin/env python3
"""Repository contracts, YAML/JSON syntax and relative Markdown links.

This does not evaluate Falco conditions. Use rules/falco/validate.sh for that.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[2]


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def script_errors(value, location):
    """Catch YAML comments/mappings accidentally used as GitLab commands."""
    errors = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"script", "before_script", "after_script"}:
                pending = [item]
                while pending:
                    command = pending.pop()
                    if isinstance(command, list):
                        pending.extend(command)
                    elif not isinstance(command, str) or not command.strip():
                        errors.append(f"{location}: {key} command must be nonempty text")
            else:
                errors.extend(script_errors(item, location))
    elif isinstance(value, list):
        for item in value:
            errors.extend(script_errors(item, location))
    return errors


def check(root=ROOT):
    errors = []
    imported = {path.parent for path in root.rglob("SOURCE.md")}
    for path in root.rglob("*"):
        if any(directory in path.parents for directory in imported):
            continue
        if any(part in {".git", ".venv", "reports", "evidence", "__pycache__"}
               for part in path.relative_to(root).parts) or not path.is_file():
            continue
        try:
            if path.suffix in {".yml", ".yaml"}:
                list(yaml.load_all(path.read_text(), Loader=UniqueLoader))
            elif path.suffix == ".json":
                json.loads(path.read_text())
            elif path.suffix == ".md":
                markdown = path.read_text()
                for block in re.finditer(r"^```(?:yaml|yml)[ \t]*\n(.*?)^```[ \t]*$",
                                         markdown, flags=re.M | re.S):
                    line = markdown[:block.start()].count("\n") + 1
                    location = f"{path.relative_to(root)}:{line}"
                    try:
                        for document in yaml.load_all(block[1], Loader=UniqueLoader):
                            errors.extend(script_errors(document, location))
                    except (ValueError, yaml.YAMLError) as exc:
                        errors.append(f"{location}: {exc}")
                text = re.sub(r"```[^\n]*\n.*?```", "", markdown, flags=re.S)
                for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^\s)]+)\)", text):
                    if re.match(r"[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                        continue
                    destination = unquote(target.split("#")[0])
                    if destination and not (path.parent / destination).exists():
                        errors.append(f"{path.relative_to(root)}: broken link {target}")
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")

    falco = root / "rules" / "falco"
    definitions = yaml.load((falco / "dso-runtime.yaml").read_text(), Loader=UniqueLoader)
    rules = [item for item in definitions if "rule" in item]
    names = [item["rule"] for item in rules]
    catalog = json.loads((falco / "rule-catalog.json").read_text())["rules"]
    scenarios = json.loads((falco / "tests" / "scenarios.json").read_text())["scenarios"]
    if len(names) != len(set(names)):
        errors.append("Falco: duplicate rule name")
    ids = [item["id"] for item in catalog]
    if len(ids) != len(set(ids)):
        errors.append("Falco: duplicate rule ID")
    if sorted(names) != sorted(item["rule"] for item in catalog):
        errors.append("Falco: rule/catalog mismatch")
    if sorted(names) != sorted(item["rule"] for item in scenarios):
        errors.append("Falco: missing or duplicate scenario contract")
    by_name = {item["rule"]: item for item in catalog}
    for rule in rules:
        for field in ("desc", "condition", "output", "priority", "source", "tags", "exceptions"):
            if not rule.get(field):
                errors.append(f"{rule['rule']}: missing {field}")
        if rule.get("source") != "syscall" or rule.get("skip-if-unknown-filter", False):
            errors.append(f"{rule['rule']}: source/unknown-filter contract violated")
        metadata = by_name.get(rule["rule"], {})
        if metadata.get("priority") != rule["priority"]:
            errors.append(f"{rule['rule']}: priority mismatch")
        for field in ("limitations", "response", "references", "confidence", "source", "license"):
            if not metadata.get(field):
                errors.append(f"{rule['rule']}: missing metadata {field}")
        if metadata.get("response") and not (root / metadata["response"]).is_file():
            errors.append(f"{rule['rule']}: response file absent")
    for case in scenarios:
        if not case.get("positive") or not case.get("negative"):
            errors.append(f"{case['rule']}: positive/negative scenario absent")
        if case.get("expected_positive") is not True or case.get("expected_negative") is not False:
            errors.append(f"{case['rule']}: incorrect scenario expectations")
    return errors


if __name__ == "__main__":
    problems = check()
    for problem in problems:
        print(problem, file=sys.stderr)
    print(f"Repository contracts: {len(problems)} errors")
    sys.exit(bool(problems))
