"""Regressions for console-free processes and read-only startup checks."""
import ast
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/windows'))
from processes import hidden_options
from manager import command


class ProcessTests(unittest.TestCase):
    @unittest.skipUnless(os.name == 'nt', 'Windows process flags')
    def test_windows_children_hide_console_but_keep_output(self):
        options = hidden_options()
        self.assertEqual(options['creationflags'] & subprocess.CREATE_NO_WINDOW, subprocess.CREATE_NO_WINDOW)
        self.assertTrue(options['startupinfo'].dwFlags & subprocess.STARTF_USESHOWWINDOW)
        self.assertEqual(options['startupinfo'].wShowWindow, subprocess.SW_HIDE)
        self.assertEqual(options['stdin'], subprocess.DEVNULL)
        result = command([sys.executable, '-c', 'print("captured output")'])
        self.assertEqual(result, 'captured output')

    @unittest.skipUnless(os.name == 'nt', 'Windows inherited output handles')
    def test_nested_powershell_preserves_the_gui_log_pipe(self):
        powershell = str(Path(os.environ.get('SystemRoot', 'C:/Windows')) /
                         'System32/WindowsPowerShell/v1.0/powershell.exe')
        arguments = [powershell, '-NoProfile', '-NonInteractive', '-Command',
                     '[Console]::WriteLine("nested-log-ok")']
        payload = (f'import sys; sys.path.insert(0, {str(ROOT / "tools/windows")!r}); '
                   'import subprocess; from processes import hidden_options; '
                   f'subprocess.run({arguments!r}, check=True, **hidden_options())')
        self.assertIn('nested-log-ok', command([sys.executable, '-c', payload]))

    def test_non_windows_does_not_receive_windows_flags(self):
        with patch('processes.os.name', 'posix'):
            self.assertEqual(hidden_options(), {})

    def test_all_windows_subprocess_calls_use_the_console_policy(self):
        for path in (ROOT / 'tools/windows').glob('*.py'):
            tree = ast.parse(path.read_text(encoding='utf-8-sig'))
            for call in ast.walk(tree):
                if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
                    continue
                if not isinstance(call.func.value, ast.Name) or call.func.value.id != 'subprocess':
                    continue
                if call.func.attr not in ('run', 'check_output', 'Popen'):
                    continue
                self.assertTrue(any(keyword.arg is None and isinstance(keyword.value, ast.Call)
                                    and isinstance(keyword.value.func, ast.Name)
                                    and keyword.value.func.id == 'hidden_options' for keyword in call.keywords),
                                f'{path.name}:{call.lineno}: missing no-console policy')
                self.assertFalse(any(keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant)
                                     and keyword.value.value for keyword in call.keywords))

    @unittest.skipUnless(sys.platform == 'win32', 'Windows Tk interface')
    def test_startup_update_option_only_checks_and_never_installs(self):
        from gui import App
        app = object.__new__(App)
        app.busy = False
        app.scan, app.start = Mock(), Mock()
        app.auto_update()
        app.scan.assert_called_once_with(True)
        app.start.assert_not_called()


if __name__ == '__main__':
    unittest.main()
