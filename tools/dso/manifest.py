"""Plugin manifest: the single source of DSO scanner pins, metadata and profiles."""
from __future__ import annotations

import functools
import importlib
from pathlib import Path
import re

from runtime import read_json, text

ROOT = Path(__file__).resolve().parents[2]
PATH = Path(__file__).with_name('plugins.json')
SEVERITIES = {'info': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4, 'unknown': -1}
CATEGORIES = ('secret', 'sast', 'sca', 'iac', 'cicd', 'malware', 'dast', 'cloud', 'runtime')
TARGET_TYPES = ('repo', 'image', 'sbom', 'artifact', 'url', 'cloud', 'cluster', 'host')
PLATFORMS = ('darwin/amd64', 'darwin/arm64', 'linux/amd64', 'linux/arm64')
# Plugins only reference kit content that stays usable without DSO.
KIT_DIRS = ('rules', 'policies', 'scanners')
PLUGIN_FIELDS = {'adapter', 'tool', 'executable', 'version', 'version_args', 'image', 'image_command',
                 'image_entrypoint', 'install', 'targets', 'category', 'network', 'credentials', 'database',
                 'exit_codes', 'severity', 'cwe', 'manual', 'playbook'}
# Plugins sharing one tool must also share its pins.
TOOL_FIELDS = ('executable', 'version', 'version_args', 'image', 'install')
IMAGE = re.compile(r'[a-z0-9][a-z0-9./_-]*:([A-Za-z0-9_.-]+)@sha256:[a-f0-9]{64}')
NAME = re.compile(r'[a-z][a-z0-9-]{0,39}')
CWE = re.compile(r'CWE-[1-9][0-9]{0,4}')


def check(condition, message):
    if not condition:
        raise ValueError('Plugin manifest: ' + message)


def strings(value, minimum, maximum, pattern=r'[A-Za-z0-9_.-]+'):
    return (isinstance(value, list) and minimum <= len(value) <= maximum and len(set(value)) == len(value) and
            all(isinstance(v, str) and re.fullmatch(pattern, v) for v in value))


def kit_path(value, kind):
    """A trusted kit file or directory that is part of a standalone package."""
    text(value, 'kit path', 512)
    path = Path(value)
    check(not path.is_absolute() and '..' not in path.parts and path.parts[0] in KIT_DIRS,
          f'{value} must be a relative path inside {", ".join(KIT_DIRS)}')
    resolved = ROOT / path
    check(not any(p.is_symlink() for p in [resolved, *resolved.parents] if p.is_relative_to(ROOT)),
          f'{value} must not be a symlink')
    check(resolved.is_file() if kind == 'file' else resolved.is_dir(), f'{value} is missing')
    return value


def validate_plugin(name, spec):
    where = f'plugin {name}'
    check(isinstance(name, str) and NAME.fullmatch(name), f'{where}: invalid ID')
    check(isinstance(spec, dict) and set(spec) == PLUGIN_FIELDS, f'{where}: unexpected fields')
    check(isinstance(spec['adapter'], str) and re.fullmatch(r'[a-z][a-z0-9_]{0,39}', spec['adapter']) and
          Path(__file__).with_name('plugins').joinpath(spec['adapter'] + '.py').is_file(), f'{where}: unknown adapter')
    check(isinstance(spec['tool'], str) and NAME.fullmatch(spec['tool']), f'{where}: invalid tool')
    check(isinstance(spec['executable'], str) and NAME.fullmatch(spec['executable']), f'{where}: invalid executable')
    version = spec['version']
    check(isinstance(version, str) and re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version), f'{where}: version must be X.Y.Z')
    check(strings(spec['version_args'], 1, 3, r'-{0,2}[a-z][a-z-]*'), f'{where}: invalid version_args')
    if spec['image'] is None:
        # No reviewed upstream image: the plugin runs only with the native engine.
        check(spec['image_command'] == [] and spec['image_entrypoint'] is None, f'{where}: no image, so no image command')
    else:
        image = IMAGE.fullmatch(spec['image']) if isinstance(spec['image'], str) else None
        check(image and image[1] in (version, 'v' + version), f'{where}: image must be pinned by version tag and digest')
    check(strings(spec['image_command'], 0, 3), f'{where}: invalid image_command')
    check(spec['image_entrypoint'] is None or isinstance(spec['image_entrypoint'], str) and
          re.fullmatch(r'/[A-Za-z0-9._/-]+', spec['image_entrypoint']), f'{where}: invalid image_entrypoint')
    install = spec['install']
    check(isinstance(install, dict) and len(install) == 1 and set(install) <= {'binaries', 'pip'}, f'{where}: invalid install')
    if 'pip' in install:
        check(isinstance(install['pip'], str) and NAME.fullmatch(install['pip']), f'{where}: invalid pip package')
    else:
        binaries = install['binaries']
        check(isinstance(binaries, dict) and binaries and set(binaries) <= set(PLATFORMS), f'{where}: invalid binary platforms')
        for platform, asset in binaries.items():
            check(isinstance(asset, dict) and set(asset) == {'url', 'sha256'} and isinstance(asset['url'], str) and
                  asset['url'].startswith('https://github.com/') and f'/v{version}/' in asset['url'] and
                  isinstance(asset['sha256'], str) and re.fullmatch('[a-f0-9]{64}', asset['sha256']),
                  f'{where}: invalid {platform} binary pin')
    check(strings(spec['targets'], 1, len(TARGET_TYPES)) and set(spec['targets']) <= set(TARGET_TYPES), f'{where}: invalid targets')
    check(spec['category'] in CATEGORIES, f'{where}: invalid category')
    check(type(spec['network']) is bool and type(spec['credentials']) is bool, f'{where}: network and credentials are booleans')
    database = spec['database']
    # A vulnerability database the scanner downloads into the DSO cache; sizes are reviewed approximations.
    check(database is None or isinstance(database, dict) and set(database) == {'name', 'path', 'download_mb', 'disk_mb', 'note'} and
          isinstance(database['name'], str) and 0 < len(database['name']) <= 80 and
          isinstance(database['path'], str) and re.fullmatch(r'[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*', database['path']) and
          '..' not in database['path'].split('/') and
          all(type(database[k]) is int and 0 < database[k] <= 100000 for k in ('download_mb', 'disk_mb')) and
          (database['note'] is None or isinstance(database['note'], str) and len(database['note']) <= 200),
          f'{where}: invalid database')
    codes = spec['exit_codes']
    check(isinstance(codes, dict) and set(codes) == {'clean', 'findings'} and
          all(type(c) is int and 0 <= c <= 255 for c in codes.values()), f'{where}: invalid exit_codes')
    severity = spec['severity']
    check(isinstance(severity, dict) and len(severity) == 1 and set(severity) <= {'fixed', 'map'}, f'{where}: invalid severity')
    if 'fixed' in severity:
        check(severity['fixed'] in SEVERITIES, f'{where}: invalid fixed severity')
    else:
        check(isinstance(severity['map'], dict) and severity['map'] and
              all(isinstance(k, str) and k and v in SEVERITIES for k, v in severity['map'].items()),
              f'{where}: invalid severity map')
    check(strings(spec['cwe'], 0, 10, CWE.pattern), f'{where}: invalid cwe')
    # Existence is checked by tools/validation/check_repo.py; images ship without manuals.
    check(isinstance(spec['manual'], str) and re.fullmatch(r'manuals/[a-z0-9-]+\.md', spec['manual']), f'{where}: invalid manual')
    check(spec['playbook'] is None or isinstance(spec['playbook'], str) and
          re.fullmatch(r'playbooks/[a-z0-9-]+\.md', spec['playbook']), f'{where}: invalid playbook')


def validate_profile(name, profile, plugins):
    where = f'profile {name}'
    check(isinstance(name, str) and NAME.fullmatch(name), f'{where}: invalid ID')
    check(isinstance(profile, dict) and set(profile) == {'target', 'description', 'plugins'}, f'{where}: unexpected fields')
    check(profile['target'] in TARGET_TYPES, f'{where}: invalid target')
    text(profile['description'], f'{where} description', 300)
    selection = profile['plugins']
    check(isinstance(selection, dict) and selection, f'{where}: select at least one plugin')
    for plugin, options in selection.items():
        check(plugin in plugins and profile['target'] in plugins[plugin]['targets'],
              f'{where}: {plugin} is not a plugin for target {profile["target"]}')
        fields = importlib.import_module('plugins.' + plugins[plugin]['adapter']).OPTIONS
        check(isinstance(options, dict) and set(options) == set(fields), f'{where}: invalid {plugin} options')
        for key, kind in fields.items():
            if kind == 'file':
                kit_path(options[key], 'file')
            else:
                check(strings(options[key], 1, 50, r'[A-Za-z0-9_./-]+'), f'{where}: {plugin}.{key} must list directories')
                for value in options[key]:
                    kit_path(value, 'dir')


def validate(data):
    check(isinstance(data, dict) and set(data) == {'schema_version', 'reviewed_on', 'note', 'probe_image', 'plugins', 'profiles'} and
          type(data['schema_version']) is int and data['schema_version'] == 1, 'unsupported format')
    text(data['reviewed_on'], 'reviewed_on', 10)
    text(data['note'], 'note', 500)
    # A small image with a shell proves the Docker daemon sees the private snapshot.
    check(isinstance(data['probe_image'], str) and IMAGE.fullmatch(data['probe_image']), 'probe_image must be pinned by digest')
    plugins, profiles = data['plugins'], data['profiles']
    check(isinstance(plugins, dict) and plugins and isinstance(profiles, dict) and profiles, 'plugins and profiles are required')
    tools = {}
    for name, spec in plugins.items():
        validate_plugin(name, spec)
        first = tools.setdefault(spec['tool'], spec)
        check(all(first[k] == spec[k] for k in TOOL_FIELDS), f'plugin {name}: pins differ from another {spec["tool"]} plugin')
    for name, profile in profiles.items():
        validate_profile(name, profile, plugins)
    return data


@functools.cache
def load():
    return validate(read_json(PATH))


def probe_image():
    return load()['probe_image']


def plugins():
    return load()['plugins']


def profiles():
    return load()['profiles']


def plugin(name):
    if not isinstance(name, str) or name not in plugins():
        raise ValueError('Unknown plugin; choose from: ' + ', '.join(sorted(plugins())))
    return plugins()[name]


def profile(name):
    if not isinstance(name, str) or name not in profiles():
        raise ValueError('Unknown profile; choose from: ' + ', '.join(sorted(profiles())))
    return profiles()[name]


def adapter(name):
    return importlib.import_module('plugins.' + plugin(name)['adapter'])


def kit_paths():
    """Every kit file or directory a profile hands to a scanner."""
    paths = set()
    for selection in profiles().values():
        for options in selection['plugins'].values():
            for value in options.values():
                paths.update([value] if isinstance(value, str) else value)
    return sorted(paths)
