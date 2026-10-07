import hashlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'mcp/dso/install_scanners.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def test_checksum_regular_binary_and_no_archive_path_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            archive = root / 'archive.tgz'
            with tarfile.open(archive, 'w:gz') as bundle:
                for name in ('gitleaks', '../escape'):
                    member = tarfile.TarInfo(name)
                    member.size = 4
                    bundle.addfile(member, io.BytesIO(b'test'))
            checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):
                installer.install_archive(archive, '0' * 64, 'gitleaks', root)
            self.assertFalse((root / 'gitleaks').exists())
            installer.install_archive(archive, checksum, 'gitleaks', root)
            self.assertEqual((root / 'gitleaks').read_bytes(), b'test')
            self.assertEqual((root / 'gitleaks').stat().st_mode & 0o777, 0o755)
            self.assertEqual(sorted(p.name for p in root.iterdir()), ['archive.tgz', 'gitleaks'])

    def test_plain_binary_asset_is_checksummed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            download = root / 'download'
            download.write_bytes(b'binary')
            with self.assertRaises(ValueError):
                installer.install_binary(download, '0' * 64, 'osv-scanner', root)
            installer.install_binary(download, hashlib.sha256(b'binary').hexdigest(), 'osv-scanner', root)
            self.assertEqual(((root / 'osv-scanner').read_bytes(), (root / 'osv-scanner').stat().st_mode & 0o777),
                             (b'binary', 0o755))

    def test_symlink_binary_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder) / 'archive.tgz'
            with tarfile.open(archive, 'w:gz') as bundle:
                member = tarfile.TarInfo('trivy')
                member.type = tarfile.SYMTYPE
                member.linkname = '/tmp/other'
                bundle.addfile(member)
            with self.assertRaises(ValueError):
                installer.install_archive(archive, hashlib.sha256(archive.read_bytes()).hexdigest(),
                                          'trivy', Path(folder))

    def test_launcher_runs_the_cli_with_quoted_paths(self):
        with tempfile.TemporaryDirectory(prefix="dso bin's ; ") as folder:
            folder = Path(folder)
            python = folder / 'python'
            python.symlink_to(sys.executable)
            launcher = installer.write_launcher(folder, python)
            self.assertEqual(launcher.stat().st_mode & 0o777, 0o755)
            result = subprocess.run([str(launcher), 'scan', 'repo', '--help'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('--profile', result.stdout)
            self.assertEqual(sorted(p.name for p in folder.iterdir()), ['dso', 'python'])

    def test_all_platforms_have_reviewed_pins(self):
        binaries = {spec['tool'] for spec in installer.manifest.plugins().values() if 'binaries' in spec['install']}
        self.assertTrue({'gitleaks', 'trivy', 'trufflehog', 'yara-x', 'grype', 'osv-scanner', 'poutine'} <= binaries)
        for platform in installer.manifest.PLATFORMS:
            assets = installer.assets(platform)
            self.assertEqual(set(assets), binaries, platform)
            for name, asset in assets.items():
                self.assertRegex(asset['sha256'], '^[a-f0-9]{64}$')
                self.assertTrue(asset['url'].startswith('https://github.com/'))
                self.assertIn('/v' + asset['version'] + '/', asset['url'])


if __name__ == '__main__':
    unittest.main()
