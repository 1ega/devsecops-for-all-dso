import hashlib
import importlib.util
import io
import json
from pathlib import Path
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

    def test_all_platforms_have_reviewed_pins(self):
        manifest = json.loads(installer.MANIFEST.read_text())['platforms']
        self.assertEqual(set(manifest), {'linux/amd64', 'linux/arm64', 'darwin/amd64', 'darwin/arm64'})
        for assets in manifest.values():
            for name, asset in assets.items():
                self.assertRegex(asset['sha256'], '^[a-f0-9]{64}$')
                self.assertTrue(asset['url'].startswith('https://github.com/'))
                self.assertIn('/v' + asset['version'] + '/', asset['url'])


if __name__ == '__main__':
    unittest.main()
