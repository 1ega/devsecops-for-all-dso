#!/usr/bin/env python3
"""Install reviewed scanner binaries from the DSO plugin manifest and a `dso` launcher into a private bin directory."""
import argparse
import hashlib
import os
from pathlib import Path
import platform
import shlex
import shutil
import sys
import tarfile
import tempfile
import urllib.request

KIT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT / 'tools/dso'))
import manifest  # noqa: E402


def install_archive(archive, checksum, name, destination):
    checksum_state = hashlib.sha256()
    with archive.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            checksum_state.update(block)
    if checksum_state.hexdigest() != checksum:
        raise ValueError(f'{name}: archive SHA256 mismatch')
    # Extract only the named regular binary; never unpack paths/symlinks from tar.
    with tarfile.open(archive, 'r:gz') as bundle:
        members = [m for m in bundle.getmembers() if m.name in (name, './' + name)]
        if len(members) != 1 or not members[0].isfile():
            raise ValueError(f'{name}: expected exactly one regular binary')
        with bundle.extractfile(members[0]) as source:
            descriptor, temporary = tempfile.mkstemp(prefix='.dso-install-', dir=destination)
            try:
                with os.fdopen(descriptor, 'wb') as output:
                    shutil.copyfileobj(source, output)
                os.chmod(temporary, 0o755)
                os.replace(temporary, destination / name)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)


def install_binary(download, checksum, name, destination):
    """A release asset that is the executable itself."""
    if hashlib.sha256(download.read_bytes()).hexdigest() != checksum:
        raise ValueError(f'{name}: binary SHA256 mismatch')
    descriptor, temporary = tempfile.mkstemp(prefix='.dso-install-', dir=destination)
    try:
        with os.fdopen(descriptor, 'wb') as output, download.open('rb') as source:
            shutil.copyfileobj(source, output)
        os.chmod(temporary, 0o755)
        os.replace(temporary, destination / name)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_launcher(bin_dir, python=None):
    """A `dso` command that runs this kit's CLI with this environment's Python and scanners."""
    # Not resolved: a virtual environment's interpreter must keep its own path to find its packages.
    python = os.path.abspath(python or sys.executable)
    content = ('#!/bin/sh\n'
               '# Written by mcp/dso/install_scanners.py; rerun the installer if the kit or this environment moves.\n'
               f'exec {shlex.quote(python)} {shlex.quote(str(KIT / "tools/dso/dso.py"))} "$@"\n')
    descriptor, temporary = tempfile.mkstemp(prefix='.dso-install-', dir=bin_dir)
    try:
        with os.fdopen(descriptor, 'w') as output:
            output.write(content)
        os.chmod(temporary, 0o755)
        os.replace(temporary, bin_dir / 'dso')
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return bin_dir / 'dso'


def assets(key):
    """One reviewed binary per tool for a platform; pip-installed tools come from the lock file."""
    result = {}
    for spec in manifest.plugins().values():
        binary = spec['install'].get('binaries', {}).get(key)
        if binary:
            result[spec['tool']] = dict(binary, version=spec['version'], executable=spec['executable'])
    return dict(sorted(result.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bin-dir', type=Path, required=True)
    args = parser.parse_args()
    arch = {'x86_64': 'amd64', 'aarch64': 'arm64', 'arm64': 'arm64'}.get(platform.machine())
    key = f'{platform.system().lower()}/{arch}'
    if key not in manifest.PLATFORMS:
        parser.error('Supported platforms: Linux/macOS amd64/arm64')
    args.bin_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='dso-install-') as folder:
        for name, asset in assets(key).items():
            download = Path(folder) / name
            with urllib.request.urlopen(asset['url'], timeout=300) as response, download.open('wb') as output:
                shutil.copyfileobj(response, output)
            if asset['url'].endswith('.tar.gz'):
                install_archive(download, asset['sha256'], asset['executable'], args.bin_dir)
            else:
                install_binary(download, asset['sha256'], asset['executable'], args.bin_dir)
            print(f'Installed {name} {asset["version"]} (SHA256 verified)')
    print(f'Installed dso launcher: {write_launcher(args.bin_dir.resolve())}')


if __name__ == '__main__':
    main()
