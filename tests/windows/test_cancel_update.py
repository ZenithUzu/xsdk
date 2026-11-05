"""Cancel real dummy process trees and update synthetic sources without building tools."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/windows'))
from process_tree import ProcessTree
from processes import hidden_options
from source_update import overlay
from manager import command


@unittest.skipUnless(os.name == 'nt', 'Windows Job Objects')
class CancellationTests(unittest.TestCase):
    def test_cancel_kills_child_after_launcher_has_exited(self):
        script = ('import subprocess,sys,time;time.sleep(.3); '
                  'p=subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"]); '
                  'print(p.pid,flush=True)')
        process = subprocess.Popen([sys.executable, '-c', script], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, **hidden_options())
        tree = ProcessTree()
        try:
            self.assertTrue(tree.assign(process))
            self.assertTrue(process.stdout.readline().strip().isdigit())
            process.wait(timeout=5)
            start = time.monotonic()
            tree.stop(process)
            process.communicate(timeout=3)
            self.assertLess(time.monotonic() - start, 3)
        finally:
            tree.stop(process)
            tree.close()
            process.stdout.close()
            process.stderr.close()

    @unittest.skipUnless(Path('C:/msys64/usr/bin/bash.exe').is_file(), 'MSYS2 optional integration')
    def test_cancel_msys_launcher_and_its_native_child(self):
        with tempfile.TemporaryDirectory() as folder:
            script = Path(folder) / 'sleep_tree.py'
            script.write_text('import subprocess,sys,time;time.sleep(.3);'
                              'p=subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"]);'
                              'print(p.pid,flush=True)')
            process = subprocess.Popen(['C:/msys64/usr/bin/bash.exe', '-c',
                                        'exec /ucrt64/bin/python.exe "$1"', 'xsdk-test', str(script)],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **hidden_options())
            tree = ProcessTree()
            try:
                self.assertTrue(tree.assign(process))
                self.assertTrue(process.stdout.readline().strip().isdigit())
                process.wait(timeout=5)
                tree.stop(process)
                process.communicate(timeout=3)
            finally:
                tree.stop(process)
                tree.close()
                process.stdout.close()
                process.stderr.close()

    def test_cancel_stops_a_detection_query_promptly(self):
        cancelled = threading.Event()
        timer = threading.Timer(.3, cancelled.set)
        timer.start()
        try:
            start = time.monotonic()
            self.assertEqual(command([sys.executable, '-c', 'import time;time.sleep(60)'],
                                     cancelled=cancelled.is_set), '')
            self.assertLess(time.monotonic() - start, 3)
        finally:
            timer.cancel()


class SourceUpdateTests(unittest.TestCase):
    def test_inplace_update_preserves_cache_and_unchanged_mtimes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            snapshot, target, backup = root / 'snapshot', root / 'sdk', root / 'backup'
            for path in (snapshot, target):
                (path / 'src').mkdir(parents=True)
            (snapshot / 'src/unchanged.c').write_text('same')
            (target / 'src/unchanged.c').write_text('same')
            before = (target / 'src/unchanged.c').stat().st_mtime_ns
            (snapshot / 'src/update.c').write_text('new')
            os.utime(snapshot / 'src/update.c', (100, 100))
            (target / 'src/update.c').write_text('local edit')
            (target / 'build').mkdir()
            (target / 'build/cached.o').write_bytes(b'cached object')
            (target / 'personal.txt').write_text('keep')
            count = overlay(snapshot, target, ['src/unchanged.c', 'src/update.c'], backup, 'revision')
            self.assertEqual(count, 1)
            self.assertEqual((target / 'src/unchanged.c').stat().st_mtime_ns, before)
            self.assertEqual((target / 'build/cached.o').read_bytes(), b'cached object')
            self.assertEqual((backup / 'src/update.c').read_text(), 'local edit')
            self.assertEqual((target / 'src/update.c').read_text(), 'new')
            self.assertGreater((target / 'src/update.c').stat().st_mtime, 100)
            self.assertEqual((target / 'personal.txt').read_text(), 'keep')
            self.assertEqual(json.loads((target / '.xsdk-managed-source.json').read_text())['revision'], 'revision')

    def test_only_previously_managed_removed_files_are_pruned_with_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            snapshot, target = root / 'snapshot', root / 'target'
            snapshot.mkdir()
            target.mkdir()
            (snapshot / 'old.c').write_text('old source')
            (target / 'my-notes.txt').write_text('personal')
            overlay(snapshot, target, ['old.c'], root / 'backup1', 'first')
            (snapshot / 'old.c').unlink()
            overlay(snapshot, target, [], root / 'backup2', 'second')
            self.assertFalse((target / 'old.c').exists())
            self.assertEqual((root / 'backup2/old.c').read_text(), 'old source')
            self.assertEqual((target / 'my-notes.txt').read_text(), 'personal')

    def test_path_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'snapshot').mkdir()
            (root / 'sdk').mkdir()
            with self.assertRaises(ValueError):
                overlay(root / 'snapshot', root / 'sdk', ['../outside'], root / 'backup', 'rev')
            self.assertFalse((root / 'outside').exists())
