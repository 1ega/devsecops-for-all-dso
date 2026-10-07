#!/usr/bin/env python3
"""Download reviewed scanner binaries from the DSO plugin manifest into a private bin directory."""
import argparse
import hashlib
import os
from pathlib import Path
import platform
import shutil
import sys
import tarfile
import tempfile
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/dso'))
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


def assets(key):
    """One reviewed binary per tool for a platform; pip-installed tools come from the lock file."""
    result = {}
    for spec in manifest.plugins().values():
        binary = spec['install'].get('binaries', {}).get(key)
        if binary:
            result[spec['tool']] = dict(binary, version=spec['version'])
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
            archive = Path(folder) / (name + '.tar.gz')
            with urllib.request.urlopen(asset['url'], timeout=120) as response, archive.open('wb') as output:
                shutil.copyfileobj(response, output)
            install_archive(archive, asset['sha256'], name, args.bin_dir)
            print(f'Installed {name} {asset["version"]} (SHA256 verified)')


if __name__ == '__main__':
    main()
