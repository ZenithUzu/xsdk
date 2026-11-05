"""Settings recovery and visible GUI information; no builds or external tools."""
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/windows'))
from settings import recover


class SettingsTests(unittest.TestCase):
    def test_new_portable_recovers_bat_settings_without_importing_actions(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            sdk = root / 'old-sdk'
            (sdk / 'cmake').mkdir(parents=True)
            (sdk / 'cmake/xsdk.cmake').touch()
            project = root / 'port'
            (project / 'platform/xsdk').mkdir(parents=True)
            (project / 'xsdk-project.json').write_text('{}')
            old = root / 'old.json'
            old.write_text(json.dumps({'sdk': str(sdk), 'project': str(project / 'platform/xsdk'),
                                       'language': 'es', 'auto_update': '1', 'restore_inputs': '1'}))
            original = old.read_bytes()
            values, origins = recover({'sdk': 'C:/default', 'project': '', 'language': 'en',
                                       'auto_update': '0', 'restore_inputs': '0'}, root / 'new.json', [old])
            self.assertEqual(values['sdk'], str(sdk))
            self.assertEqual(values['project'], str(project))
            self.assertEqual(values['language'], 'es')
            self.assertEqual(values['auto_update'], '0')
            self.assertEqual(values['restore_inputs'], '0')
            self.assertTrue(origins)
            self.assertEqual(old.read_bytes(), original)
            self.assertFalse((root / 'new.json').exists())

    def test_explicit_saved_paths_win_and_invalid_ones_can_be_recovered(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ('chosen', 'old'):
                (root / name / 'cmake').mkdir(parents=True)
                (root / name / 'cmake/xsdk.cmake').touch()
            current, old = root / 'current.json', root / 'legacy.json'
            current.write_text(json.dumps({'sdk': str(root / 'chosen')}))
            old.write_text(json.dumps({'sdk': str(root / 'old')}))
            values, _ = recover({'sdk': ''}, current, [old])
            self.assertEqual(values['sdk'], str(root / 'chosen'))
            values, _ = recover({'sdk': ''}, current, [old], replace_invalid=True,
                                 saved_override={'sdk': str(root / 'missing')})
            self.assertEqual(values['sdk'], str(root / 'old'))

    def test_bom_and_corrupt_profiles(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            current, old = root / 'current.json', root / 'old.json'
            current.write_text('broken')
            old.write_text(json.dumps({'work': str(root)}), encoding='utf-8-sig')
            values, origins = recover({'work': ''}, current, [old])
            self.assertEqual(values['work'], str(root))
            self.assertTrue(origins)


@unittest.skipUnless(sys.platform == 'win32', 'Windows GUI source checks')
class VisibleInformationTests(unittest.TestCase):
    def test_white_output_box_receives_detection_and_completion(self):
        import tkinter as tk
        from gui import App, CREDITS
        root = tk.Tk()
        root.withdraw()
        self.addCleanup(root.destroy)
        with patch.object(root, 'after'), patch.object(App, 'save_preferences'):
            app = App(root)
            app.active_action = 'Detectar herramientas'
            app.started_at = time.monotonic()
            app.events.put({'rows': [{'key': 'sdk', 'name': 'xSDK', 'version': 'test-version',
                                     'status': 'Disponible', 'path': 'C:/detected-sdk'}]})
            app.events.put((0, 'C:/test.log'))
            app.poll()
            text = app.output.get('1.0', 'end')
            self.assertIn('test-version', text)
            self.assertIn('C:/detected-sdk', text)
            self.assertIn('C:/test.log', text)
            self.assertIn('ZenithUzu', CREDITS)
            self.assertNotIn('Axel', CREDITS)
            self.assertEqual(str(app.output.cget('state')), 'disabled')
