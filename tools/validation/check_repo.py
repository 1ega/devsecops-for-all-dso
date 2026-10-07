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
sys.path.insert(0, str(ROOT / "tools" / "dso"))
import manifest  # noqa: E402

KIT = ("rules", "policies", "scanners")
SKIPPED = {".git", ".venv", "reports", "evidence", "__pycache__", "node_modules"}
# Dated research notes keep the versions they actually tested; DSO tests hold deliberate drift.
PIN_EXEMPT = ("docs/research/", "tools/dso/tests/")
TEXT = {"", ".md", ".yml", ".yaml", ".json", ".sh", ".py", ".toml", ".txt", ".lock", ".js"}


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
    errors.extend(dso_errors(root, imported))
    return errors


def text_files(root, imported):
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if (not path.is_file() or path.suffix not in TEXT or SKIPPED & set(relative.parts)
                or any(directory in path.parents for directory in imported)
                or relative.as_posix().startswith(PIN_EXEMPT)):
            continue
        try:
            yield relative.as_posix(), path.read_text()
        except UnicodeDecodeError:
            continue


def pin_patterns(plugins):
    """(regex, expected, label): each match's first group must equal expected."""
    tools = {}
    for spec in plugins.values():
        tools.setdefault(spec["tool"], spec)
    patterns = []
    for tool, spec in tools.items():
        version = spec["version"]
        if spec["image"]:
            repository, reference = spec["image"].split(":", 1)
            patterns.append((r"(?<![\w.-])" + re.escape(repository) + r":([\w.-]+(?:@sha256:[a-f0-9]{64})?)",
                             reference, f"{tool} image"))
        patterns.append((re.escape(tool) + r"/v[0-9]+/version\.Version=v([0-9][\w.-]*)", version, f"{tool} build version"))
        if "pip" in spec["install"]:
            patterns.append((r"(?<![\w-])" + re.escape(spec["install"]["pip"]) + r"==([0-9][\w.]*)", version, f"{tool} package"))
            continue
        project = re.escape(re.match(r"https://github\.com/([\w.-]+/[\w.-]+)/",
                                     next(iter(spec["install"]["binaries"].values()))["url"])[1])
        patterns += [(r"github\.com/" + project + r"/releases/(?:download|tag)/v([0-9][\w.-]*?)(?=[/\"')\s]|$)", version, f"{tool} release"),
                     (r"--branch v([0-9][\w.-]*) https://github\.com/" + project + r"\b", version, f"{tool} source tag"),
                     (r"repo:\s*https://github\.com/" + project + r"\s*\n\s*rev:\s*v?([0-9][\w.-]*)", version, f"{tool} hook")]
    return [(re.compile(p), expected, label) for p, expected, label in patterns]


def dso_errors(root, imported):
    """One pin per DSO tool, and kit packages that keep working without DSO."""
    try:
        plugins = manifest.plugins()
    except (ValueError, OSError) as exc:
        return [f"tools/dso/plugins.json: {exc}"]
    errors = []
    for name, spec in plugins.items():
        for field in ("manual", "playbook"):
            if spec[field] and not (root / spec[field]).is_file():
                errors.append(f"tools/dso/plugins.json: {name} {field} {spec[field]} is missing")
    patterns = pin_patterns(plugins)
    for relative, content in text_files(root, imported):
        for pattern, expected, label in patterns:
            for match in pattern.finditer(content):
                if match[1] != expected and not expected.startswith(match[1] + "@"):
                    line = content.count("\n", 0, match.start()) + 1
                    errors.append(f"{relative}:{line}: {label} {match[1]} differs from tools/dso/plugins.json ({expected})")
                elif "@" in expected and "@" not in match[1] and label.endswith("image"):
                    line = content.count("\n", 0, match.start()) + 1
                    errors.append(f"{relative}:{line}: {label} must be pinned by digest ({expected})")
    # The standalone image copies DSO modules one by one; a module missing there fails at import time.
    dockerfile = (root / "mcp" / "dso" / "Dockerfile").read_text()
    for module in sorted(path.name for path in (root / "tools" / "dso").glob("*.py")):
        if f"tools/dso/{module}" not in dockerfile:
            errors.append(f"mcp/dso/Dockerfile: tools/dso/{module} is not copied into the image")
    binaries = {spec["tool"]: spec["install"].get("binaries", {}) for spec in plugins.values()}
    for name, asset in json.loads((root / "tools" / "versions.json").read_text())["binary_assets"].items():
        pin = binaries.get(name, {}).get(asset.get("platform"))
        if name in binaries and (not pin or (asset.get("url"), asset.get("sha256")) != (pin["url"], pin["sha256"])):
            errors.append(f"tools/versions.json: binary_assets.{name} differs from tools/dso/plugins.json")
    return errors + package_errors(root, imported)


def package_errors(root, imported):
    """Rules, policies and scanner configs need a README, a license and no DSO internals."""
    errors = []
    for directory in sorted(imported):
        if directory.relative_to(root).parts[0] in KIT and not any(
                p.is_file() and p.name.upper().startswith(("LICENSE", "COPYING")) for p in directory.iterdir()):
            errors.append(f"{directory.relative_to(root)}: imported package has no license file")
    for top in KIT:
        for package in sorted(p for p in (root / top).iterdir() if p.is_dir()):
            if not (package / "README.md").is_file():
                errors.append(f"{package.relative_to(root)}: missing README.md with a command that works without DSO")
    for relative, content in text_files(root, imported):
        if relative.startswith(tuple(k + "/" for k in KIT)) and re.search(r"tools/dso|plugins\.json", content):
            errors.append(f"{relative}: kit packages must not depend on DSO; put DSO metadata in tools/dso/plugins.json")
    for value in manifest.kit_paths():
        path = root / value
        directory = path if path.is_dir() else path.parent
        top = root.joinpath(*Path(value).parts[:2])
        # The path itself or a directory containing it, named in a shell block of a README on the way up.
        covering = {Path(value), *(p for p in Path(value).parents if (root / p).is_relative_to(top))}
        readmes = [d / "README.md" for d in [directory, *directory.parents]
                   if d.is_relative_to(top) and (d / "README.md").is_file()]
        tokens = {Path(word.rsplit(":", 1)[-1].rstrip("/")) for readme in readmes
                  for block in re.findall(r"```(?:bash|sh|shell|console)[ \t]*\n(.*?)```", readme.read_text(), re.S)
                  for word in block.split()}
        if not covering & tokens:
            errors.append(f"{value}: used by a DSO profile, but no README up to {top.relative_to(root)} "
                          "shows a shell command that uses it without DSO")
    return errors


if __name__ == "__main__":
    problems = check()
    for problem in problems:
        print(problem, file=sys.stderr)
    print(f"Repository contracts: {len(problems)} errors")
    sys.exit(bool(problems))
