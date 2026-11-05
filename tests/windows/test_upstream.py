"""Original-source merging on synthetic local Git repos; no network or SDK compilation."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/windows'))
from upstream import integrate_original
from processes import hidden_options


class UpstreamTests(unittest.TestCase):
    def git(self, *args):
        return subprocess.check_output(['git', '-c', 'user.name=SDK test', '-c', 'user.email=sdk-test@localhost',
                                        *map(str, args)], text=True, stderr=subprocess.STDOUT,
                                       **hidden_options()).strip()

    def executor(self, args, cwd=None, capture=False):
        result = subprocess.run(list(map(str, args)), cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, check=True, **hidden_options())
        return result.stdout.strip() if capture else ''

    def fixture(self, root, runtime_conflict=False):
        original, windows, target = root / 'original', root / 'windows', root / 'installed'
        original.mkdir()
        self.git('init', '-b', 'main', original)
        for name, content in [('README.md', 'Original base\n'), ('CODE_GUIDELINES.md', 'Base rules\n'),
                              ('src/runtime.c', 'int runtime = 1;\n'), ('cmake/xsdk.cmake', '# sdk\n')]:
            path = original / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        self.git('-C', original, 'add', '.')
        self.git('-C', original, 'commit', '-m', 'base')
        self.git('clone', original, windows)
        (windows / 'tools/windows').mkdir(parents=True)
        (windows / 'tools/windows/run.sh').write_text('# Windows compatibility\n')
        (windows / 'README.md').write_text('Windows interface guide\n')
        (windows / 'CODE_GUIDELINES.md').write_text('Base rules\nWindows exception\n')
        if runtime_conflict:
            (windows / 'src/runtime.c').write_text('int windows_runtime = 7;\n')
        self.git('-C', windows, 'add', '.')
        self.git('-C', windows, 'commit', '-m', 'Windows changes')
        (original / 'src/runtime.c').write_text('int runtime = 2;\n')
        (original / 'README.md').write_text('Original updated\n')
        (original / 'CODE_GUIDELINES.md').write_text('Base rules\nOriginal C++ exception\n')
        self.git('-C', original, 'add', '.')
        self.git('-C', original, 'commit', '-m', 'original update')
        (target / 'tools/windows').mkdir(parents=True)
        (target / 'tools/windows/run.sh').write_text('# existing Windows\n')
        (target / 'build').mkdir()
        (target / 'build/cached.o').write_bytes(b'keep cached object')
        return original, windows, target

    def test_original_updates_keep_windows_changes_and_build_cache(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            original, windows, target = self.fixture(root)
            state = integrate_original('git', target, str(windows), 'main', root / 'work', self.executor,
                                       upstream_url=str(original), upstream_branch='main')
            self.assertIn('runtime = 2', (target / 'src/runtime.c').read_text())
            self.assertIn('Windows interface', (target / 'README.md').read_text())
            self.assertIn('Original updated', (target / 'README-UPSTREAM.md').read_text())
            rules = (target / 'CODE_GUIDELINES.md').read_text()
            self.assertIn('Windows exception', rules)
            self.assertIn('Original C++ exception', rules)
            self.assertEqual((target / 'build/cached.o').read_bytes(), b'keep cached object')
            self.assertEqual(state['upstream_revision'], self.git('-C', original, 'rev-parse', 'HEAD'))

    def test_runtime_conflict_leaves_installed_sdk_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            original, windows, target = self.fixture(root, runtime_conflict=True)
            with self.assertRaisesRegex(ValueError, 'live SDK not changed'):
                integrate_original('git', target, str(windows), 'main', root / 'work', self.executor,
                                   upstream_url=str(original), upstream_branch='main')
            self.assertFalse((target / 'src/runtime.c').exists())
            self.assertEqual((target / 'build/cached.o').read_bytes(), b'keep cached object')
