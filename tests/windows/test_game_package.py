"""Private game packaging checks, using synthetic fixtures only."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/windows'))
from game_package import package_game


class GamePackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project, self.build = self.root / 'source', self.root / 'build'
        self.project.mkdir()
        self.build.mkdir()
        self.output = self.root / 'ready'
        rom = b'private ROM fixture, not a game'
        (self.project / 'baserom.us.z64').write_bytes(rom)
        (self.project / 'sm64.us.sha1').write_text(hashlib.sha1(rom).hexdigest())
        image = b'XEX2synthetic fixture, not executable'
        (self.build / 'sm64coopdx.xex').write_bytes(image)
        self.report = {'sha256': {'sm64coopdx.xex': hashlib.sha256(image).hexdigest()}}
        (self.build / 'build-info.json').write_text(json.dumps(self.report))
        for folder in ('lang', 'palettes', 'mods', 'dynos'):
            (self.project / folder).mkdir()
            (self.project / folder / 'sample.txt').write_text('local fixture')

    def package(self, **kwargs):
        return package_game(self.project, self.build, self.output, **kwargs)

    def test_package_is_new_and_mods_are_opt_in(self):
        destination, count = self.package()
        self.assertEqual(destination, self.output)
        self.assertEqual(count, 4)
        self.assertFalse((destination / 'mods/sample.txt').exists())
        self.assertTrue((destination / 'dynos').is_dir())
        self.assertEqual(json.loads((destination / 'package-info.json').read_text())['hardware_validation'], 'not-run')
        with self.assertRaises(ValueError):
            self.package()

    def test_corrupt_image_or_rom_rejected(self):
        for file in (self.build / 'sm64coopdx.xex', self.project / 'baserom.us.z64'):
            original = file.read_bytes()
            file.write_bytes(b'wrong')
            with self.assertRaises(ValueError):
                self.package()
            file.write_bytes(original)
        self.assertFalse(self.output.exists())

    def test_optional_pc_resources_exclude_executables(self):
        pc = self.root / 'pc'
        (pc / 'lang').mkdir(parents=True)
        (pc / 'lang/English.ini').write_text('PC fixture')
        (pc / 'lang/desktop.dll').write_bytes(b'MZ')
        self.package(pc=pc, include_mods=True)
        self.assertEqual((self.output / 'lang/English.ini').read_text(), 'PC fixture')
        self.assertFalse((self.output / 'lang/desktop.dll').exists())
        self.assertTrue((self.output / 'mods/sample.txt').exists())

    def test_fatx_and_cancellation_fail_without_partial_package(self):
        file = self.project / 'mods' / ('x' * 43)
        file.write_text('too long')
        with self.assertRaisesRegex(ValueError, 'FATX'):
            self.package(include_mods=True)
        file.unlink()
        with self.assertRaises(InterruptedError):
            self.package(cancelled=lambda: True)
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.root.glob('.coopdx-package-*')))

    def test_runtime_destination_overlap_rejected(self):
        with self.assertRaises(ValueError):
            package_game(self.project, self.build, self.project / 'lang/output')


if __name__ == '__main__':
    unittest.main()
