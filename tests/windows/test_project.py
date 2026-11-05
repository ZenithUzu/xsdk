"""Recipe validation and live language switching without running a game or compiler."""
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/windows'))
from project import recipe_plan
from i18n import LANGUAGES, MESSAGES, translate


class RecipeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'port with space;literal'
        self.project.mkdir()
        (self.project / 'build.ps1').write_text('# source')
        self.manifest = {'schema': 1, 'kind': 'powershell-port', 'build_script': 'build.ps1', 'requires_sdl3': True}
        self.save_manifest()
        for group, paths in {
            'sdk': ['cmake/xsdk.cmake', 'src/xsdk.ld', 'build/libxsdk.a', 'build/host/libxsc.dll',
                    'tools/build_shaders.py', 'tools/elf2xex.py'],
            'compiler': ['bin/powerpc-xsdk-elf-gcc.exe', 'bin/powerpc-xsdk-elf-g++.exe', 'bin/glslang.exe'],
            'msys': ['ucrt64/bin/python.exe', 'ucrt64/bin/cmake.exe', 'ucrt64/bin/ninja.exe', 'usr/bin/make.exe'],
        }.items():
            for name in paths:
                file = self.root / group / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.touch()
        (self.root / 'sdl').mkdir()

    def save_manifest(self):
        (self.project / 'xsdk-project.json').write_text(json.dumps(self.manifest))

    def plan(self, **kwargs):
        options = dict(project=self.project, sdk=self.root / 'sdk', compiler=self.root / 'compiler',
                       msys=self.root / 'msys', work=self.root / 'work', sdl=str(self.root / 'sdl'))
        options.update(kwargs)
        return recipe_plan(**options)

    def test_argument_boundaries_and_release_default(self):
        with patch('subprocess.run', side_effect=AssertionError('validation must not run commands')):
            command, environment, output = self.plan()
        self.assertEqual(command[command.index('-File') + 1], str(self.project / 'build.ps1'))
        self.assertEqual(command[command.index('-BuildType') + 1], 'Release')
        self.assertEqual(command[command.index('-ExecutionPolicy') + 1], 'RemoteSigned')
        self.assertNotIn('Bypass', command)
        self.assertTrue(environment["PSModulePath"].endswith("Modules"))
        self.assertNotIn("PowerShell/Modules;", environment["PSModulePath"])
        self.assertNotIn('-RestoreInheritedInputs', command)
        self.assertEqual(output, self.root / 'work/projects' / self.project.name)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows PowerShell integration')
    def test_windows_powershell_modules_work_from_python_parent(self):
        with patch.dict('os.environ', {'PSModulePath': 'C:/fake-powershell7/Modules'}):
            command, environment, _ = self.plan()
        result = subprocess.run([command[0], '-NoProfile', '-Command',
                                 'Get-Command Get-FileHash -ErrorAction Stop | Out-Null'],
                                env=environment, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_restore_is_explicit_and_shader_override_is_used(self):
        (self.root / 'compiler/bin/glslang.exe').unlink()
        custom = self.root / 'custom shader.exe'
        custom.touch()
        command, _, _ = self.plan(glslang=str(custom), restore_inputs=True)
        self.assertIn('-RestoreInheritedInputs', command)
        self.assertEqual(command[command.index('-Glslang') + 1], str(custom))

    def test_reject_missing_dependency_sdl_and_invalid_jobs(self):
        for kwargs in ({'sdl': ''}, {'jobs': 0}, {'jobs': 65}, {'build_type': 'Fast'}):
            with self.assertRaises(ValueError):
                self.plan(**kwargs)
        (self.root / 'sdk/build/libxsdk.a').unlink()
        with self.assertRaisesRegex(ValueError, 'libxsdk.a'):
            self.plan()

    def test_script_cannot_escape_project(self):
        for script in ('../outside.ps1', 'build.cmd', ''):
            self.manifest['build_script'] = script
            self.save_manifest()
            with self.assertRaises(ValueError):
                self.plan()


class LanguageTests(unittest.TestCase):
    def test_all_catalog_entries_switch_both_directions(self):
        for row in MESSAGES:
            for previous in row:
                for code, column in (('es', 0), ('en', 1), ('pt', 2)):
                    self.assertEqual(translate(previous, code), row[column])

    def test_log_paths_are_preserved(self):
        path = r'C:/Compilador/Etapa terminada.log'
        self.assertEqual(translate('Etapa terminada · Log: ' + path, 'en'), 'Stage completed · Log: ' + path)
        self.assertEqual(translate(path, 'pt'), path)
        self.assertIn('Check the logs', translate('Ejecutando: project · 00:04 · Consulta los logs', 'en'))

    @unittest.skipUnless(sys.platform == 'win32', 'Windows UI smoke test')
    def test_live_gui_switch_keeps_settings_and_task_queue(self):
        import tkinter as tk
        from gui import App
        root = tk.Tk()
        root.withdraw()
        self.addCleanup(root.destroy)
        with patch.object(root, 'after'), patch.object(App, 'save_preferences'):
            app = App(root)
            app.fields['project'].set('C:/my-project')
            events = app.events
            for code, label in LANGUAGES.items():
                app.language_choice.set(label)
                app.change_language()
                self.assertEqual(app.fields['language'].get(), code)
                self.assertEqual(app.fields['project'].get(), 'C:/my-project')
                self.assertIs(app.events, events)
                self.assertEqual(root.title(), translate('xSDK para Windows — experimental', code))
            app.events.put({'rows': [{'key': 'sdk', 'name': 'Compilador', 'version': '1', 'status': 'Disponible'}]})
            app.poll()
            self.assertEqual(app.inventory.item('sdk', 'values')[0], translate('Compilador', 'pt'))


if __name__ == '__main__':
    unittest.main()
