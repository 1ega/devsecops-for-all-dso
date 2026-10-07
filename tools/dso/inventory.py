"""What the snapshot contains, so "no findings" can be told from "nothing to check".

The classification is DSO's own, by file name with a small content sniff for YAML and JSON, and
never a scanner's claim about itself. It records source languages, dependency lockfiles by
ecosystem, manifests that have no lockfile beside them (scanners skip those), IaC files and CI
pipelines. Paths are target-relative; lists are sorted and bounded like every other report field.
"""
from __future__ import annotations

import os
from pathlib import Path
import re

FIELDS = ('languages', 'dependency_files', 'unlocked', 'iac_files', 'ci_files')
LANGUAGES = {'.py': 'python', '.js': 'javascript', '.mjs': 'javascript', '.cjs': 'javascript', '.jsx': 'javascript',
             '.ts': 'typescript', '.tsx': 'typescript', '.go': 'go', '.java': 'java', '.kt': 'kotlin', '.kts': 'kotlin',
             '.swift': 'swift', '.m': 'objective-c', '.mm': 'objective-c', '.c': 'c', '.h': 'c', '.cc': 'cpp',
             '.cpp': 'cpp', '.cxx': 'cpp', '.hpp': 'cpp', '.cs': 'csharp', '.rb': 'ruby', '.php': 'php', '.rs': 'rust',
             '.scala': 'scala', '.sh': 'shell', '.bash': 'shell', '.dart': 'dart'}
# Files the dependency scanners read, by ecosystem.
LOCKFILES = {'requirements.txt': 'pip', 'Pipfile.lock': 'pip', 'poetry.lock': 'pip', 'uv.lock': 'pip', 'pdm.lock': 'pip',
             'package-lock.json': 'npm', 'npm-shrinkwrap.json': 'npm', 'yarn.lock': 'npm', 'pnpm-lock.yaml': 'npm',
             'bun.lock': 'npm', 'go.mod': 'go', 'pom.xml': 'maven', 'gradle.lockfile': 'gradle',
             'buildscript-gradle.lockfile': 'gradle', 'Gemfile.lock': 'rubygems', 'Cargo.lock': 'cargo',
             'composer.lock': 'composer', 'packages.lock.json': 'nuget', 'packages.config': 'nuget',
             'pubspec.lock': 'pub', 'Podfile.lock': 'cocoapods', 'Package.resolved': 'swift', 'mix.lock': 'hex',
             'conan.lock': 'conan'}
LOCKFILE_PATTERNS = ((re.compile(r'requirements[-_.\w]*\.txt'), 'pip'), (re.compile(r'.+\.deps\.json'), 'nuget'))
# Manifests that declare dependencies without pinning them; without one of the lockfiles beside
# them, the dependency scanners have nothing to resolve and report nothing.
MANIFESTS = {'package.json': ('npm', ('package-lock.json', 'npm-shrinkwrap.json', 'yarn.lock', 'pnpm-lock.yaml', 'bun.lock')),
             'Pipfile': ('pip', ('Pipfile.lock',)),
             'pyproject.toml': ('pip', ('poetry.lock', 'uv.lock', 'pdm.lock', 'requirements.txt')),
             'Gemfile': ('rubygems', ('Gemfile.lock',)), 'Cargo.toml': ('cargo', ('Cargo.lock',)),
             'composer.json': ('composer', ('composer.lock',)),
             'build.gradle': ('gradle', ('gradle.lockfile',)), 'build.gradle.kts': ('gradle', ('gradle.lockfile',)),
             'pubspec.yaml': ('pub', ('pubspec.lock',)), 'Podfile': ('cocoapods', ('Podfile.lock',)),
             'mix.exs': ('hex', ('mix.lock',))}
ECOSYSTEMS = sorted({*LOCKFILES.values(), *(e for _, e in LOCKFILE_PATTERNS), *(e for e, _ in MANIFESTS.values())})
IAC = ('cloudformation', 'compose', 'dockerfile', 'helm', 'kubernetes', 'terraform')
CI = ('azure-pipelines', 'github-actions', 'gitlab-ci', 'tekton')
MAX_PATHS = 100
SNIFF = 8192
KUBERNETES = re.compile(rb'^\s*(apiVersion|kind)\s*:', re.M)
CLOUDFORMATION = re.compile(rb'AWSTemplateFormatVersion|"?Type"?\s*:\s*"?AWS::')


def iac_kind(name, parts, head):
    if name == 'Dockerfile' or name.startswith('Dockerfile.') or name.endswith('.Dockerfile'):
        return 'dockerfile'
    if name.endswith(('.tf', '.tfvars')):
        return 'terraform'
    if name == 'Chart.yaml':
        return 'helm'
    if re.fullmatch(r'(docker-)?compose(\.[\w-]+)?\.ya?ml', name):
        return 'compose'
    if name.endswith(('.yaml', '.yml', '.json')):
        if name.endswith(('.yaml', '.yml')) and len(KUBERNETES.findall(head)) >= 2:
            return 'kubernetes'
        if CLOUDFORMATION.search(head):
            return 'cloudformation'
    return None


def ci_kind(name, parts):
    if len(parts) >= 3 and parts[0] == '.github' and parts[1] == 'workflows' and name.endswith(('.yml', '.yaml')):
        return 'github-actions'
    if name.endswith('.gitlab-ci.yml') or name == '.gitlab-ci.yml':
        return 'gitlab-ci'
    if name in ('azure-pipelines.yml', 'azure-pipelines.yaml') or (parts[0] == '.azure-pipelines' and name.endswith(('.yml', '.yaml'))):
        return 'azure-pipelines'
    if parts[0] == '.tekton' and name.endswith(('.yml', '.yaml')):
        return 'tekton'
    return None


def lockfile_ecosystem(name):
    if name in LOCKFILES:
        return LOCKFILES[name]
    return next((eco for pattern, eco in LOCKFILE_PATTERNS if pattern.fullmatch(name)), None)


def collect(root):
    """The inventory of a snapshot directory: files DSO copied, nothing else."""
    root = Path(root)
    languages, lockfiles, unlocked, iac, ci = {}, {}, {}, {}, {}
    manifests = []
    names_by_directory = {}
    for directory, folders, files in os.walk(root):
        folders.sort()
        relative = Path(directory).relative_to(root)
        names_by_directory[relative] = set(files)
        for name in sorted(files):
            rel = (relative / name).as_posix()
            parts = rel.split('/')
            if rel == '.semgrepignore':
                continue
            suffix = Path(name).suffix.lower()
            if suffix in LANGUAGES:
                languages[LANGUAGES[suffix]] = languages.get(LANGUAGES[suffix], 0) + 1
            ecosystem = lockfile_ecosystem(name)
            if ecosystem:
                lockfiles.setdefault(ecosystem, []).append(rel)
            elif name in MANIFESTS:
                manifests.append((relative, name, rel))
            kind = ci_kind(name, parts)
            if kind:
                ci[kind] = ci.get(kind, 0) + 1
                continue
            head = b''
            if name.endswith(('.yaml', '.yml', '.json')):
                with open(Path(directory) / name, 'rb') as stream:
                    head = stream.read(SNIFF)
            kind = iac_kind(name, parts, head)
            if kind:
                iac[kind] = iac.get(kind, 0) + 1
    for relative, name, rel in manifests:
        ecosystem, locks = MANIFESTS[name]
        if not names_by_directory[relative] & set(locks):
            unlocked.setdefault(ecosystem, []).append(rel)
    return {'languages': dict(sorted(languages.items())),
            'dependency_files': {k: sorted(v)[:MAX_PATHS] for k, v in sorted(lockfiles.items())},
            'unlocked': {k: sorted(v)[:MAX_PATHS] for k, v in sorted(unlocked.items())},
            'iac_files': dict(sorted(iac.items())), 'ci_files': dict(sorted(ci.items()))}


def check(inventory, files, relative_path):
    """Validate a stored inventory; relative_path is the report validator's path check."""
    if not isinstance(inventory, dict) or tuple(inventory) != FIELDS:
        raise ValueError('Unexpected inventory fields')
    for field, allowed in (('languages', set(LANGUAGES.values())), ('iac_files', set(IAC)), ('ci_files', set(CI))):
        counts = inventory[field]
        if not isinstance(counts, dict) or list(counts) != sorted(counts) or not set(counts) <= allowed:
            raise ValueError(f'Invalid inventory {field}')
        if any(type(v) is not int or not 1 <= v <= files for v in counts.values()):
            raise ValueError(f'Invalid inventory {field} counts')
    for field in ('dependency_files', 'unlocked'):
        listed = inventory[field]
        if not isinstance(listed, dict) or list(listed) != sorted(listed) or not set(listed) <= set(ECOSYSTEMS):
            raise ValueError(f'Invalid inventory {field}')
        for paths in listed.values():
            if not isinstance(paths, list) or not paths or len(paths) > MAX_PATHS or paths != sorted(set(paths)):
                raise ValueError(f'Invalid inventory {field} paths')
            for value in paths:
                if relative_path(value, Path('/unused')) != value or Path(value).is_absolute():
                    raise ValueError(f'Invalid inventory {field} path')
    return inventory


def summary(inventory):
    """Short labelled parts for a terminal line: languages, lockfiles, IaC and CI kinds."""
    parts = [f'{name} {count}' for name, count in inventory['languages'].items()]
    for ecosystem, paths in inventory['dependency_files'].items():
        shown = ', '.join(paths[:3]) + (f' and {len(paths) - 3} more' if len(paths) > 3 else '')
        parts.append(f'{ecosystem}: {shown}')
    parts += [f'{kind} {count}' for kind, count in inventory['iac_files'].items()]
    parts += [f'{kind} {count}' for kind, count in inventory['ci_files'].items()]
    return parts
