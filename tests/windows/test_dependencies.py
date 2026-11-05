"""Local discovery and explicit dependency workflows, without real downloads."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/windows'))
from dependencies import DEFAULTS, checkout, dependency_plan, github_source, setup
from discovery import detect


class DiscoveryTests(unittest.TestCase):
    def test_finds_nested_components_without_executing_them(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = ['dev/sdk/cmake/xsdk.cmake', 'dev/compiler/bin/powerpc-xsdk-elf-gcc.exe',
                     'dev/compiler/bin/glslang.exe', 'dev/msys/usr/bin/bash.exe', 'dev/msys/usr/bin/pacman.exe',
                     'dev/SDL/include/SDL3/SDL.h', 'dev/SDL/build-xsdk/SDL3Config.cmake']
            for name in files:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            with patch('discovery.shutil.which', return_value=None), patch.dict(os.environ, {}, clear=True):
                found = detect({}, search_roots=[root])
            for key, expected in [('sdk', 'dev/sdk'), ('prefix', 'dev/compiler'), ('msys', 'dev/msys'),
                                  ('sdl_source', 'dev/SDL'), ('sdl', 'dev/SDL/build-xsdk')]:
                self.assertEqual(Path(found[key]), root / expected)
            explicit = root / 'chosen.exe'
            explicit.touch()
            with patch('discovery.shutil.which', return_value=None):
                self.assertEqual(detect({'glslang': str(explicit)}, search_roots=[root])['glslang'], str(explicit))

    def test_git_bash_is_not_mistaken_for_msys2(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            bash = root / 'Git/usr/bin/bash.exe'
            bash.parent.mkdir(parents=True)
            bash.touch()
            with patch('discovery.shutil.which', return_value=None), patch.dict(os.environ, {}, clear=True):
                self.assertFalse(detect({}, search_roots=[root])['msys'])

    def test_depth_limit_prevents_unbounded_search(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            marker = root / 'a/b/c/d/sdk/cmake/xsdk.cmake'
            marker.parent.mkdir(parents=True)
            marker.touch()
            with patch('discovery.shutil.which', return_value=None), patch.dict(os.environ, {}, clear=True):
                self.assertFalse(detect({}, search_roots=[root], depth=1)['sdk'])


class DependencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.values = dict(DEFAULTS, msys=str(self.root / 'msys'), sdk=str(self.root / 'sdk'),
                           prefix=str(self.root / 'compiler'), work=str(self.root / 'work'),
                           sdl=str(self.root / 'SDL/build-xsdk'), sdl_source=str(self.root / 'SDL'),
                           jobs='4', glslang='')
        for name in ['msys/usr/bin/bash.exe', 'msys/usr/bin/pacman.exe', 'msys/usr/bin/git.exe', 'msys/usr/bin/make.exe',
                     'msys/ucrt64/bin/cmake.exe', 'msys/ucrt64/bin/ninja.exe', 'msys/ucrt64/bin/gcc.exe',
                     'msys/ucrt64/bin/python.exe', 'sdk/cmake/xsdk.cmake', 'sdk/tools/windows/run.sh',
                     'sdk/build/libxsdk.a', 'sdk/build/host/libxsc.dll',
                     'compiler/bin/powerpc-xsdk-elf-g++.exe', 'compiler/bin/glslang.exe',
                     'SDL/include/SDL3/SDL.h', 'SDL/build-xsdk/SDL3Config.cmake', 'SDL/build-xsdk/libSDL3.a']:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()

    def test_github_urls_and_tree_branch_normalization(self):
        self.assertEqual(github_source('https://github.com/team/repo/tree/xenon', 'main'),
                         ('https://github.com/team/repo.git', 'xenon'))
        for url in ['file:///repo', 'https://user:token@github.com/team/repo', 'http://github.com/team/repo',
                    'https://evil.example/team/repo', 'https://github.com/team/repo?token=x',
                    'https://github.com/team/repo/blob/main/run.ps1', 'https://github.com/team/repo;run']:
            with self.assertRaises(ValueError):
                github_source(url, 'main')
        for branch in ['--upload-pack=bad', 'a..b', 'a//b', 'x\nrun']:
            with self.assertRaises(ValueError):
                github_source('https://github.com/team/repo', branch)

    def test_plan_keeps_urls_and_paths_as_arguments(self):
        command, environment = dependency_plan('prepare', self.values, self.root)
        self.assertEqual(command[1], '--login')
        self.assertNotIn('-c', command)
        self.assertIn(self.values['sdk_repo'], command)
        self.assertEqual(environment['MSYSTEM'], 'UCRT64')
        self.assertEqual(environment['GIT_TERMINAL_PROMPT'], '0')

    def test_prepare_reuses_installed_components_and_does_not_update(self):
        with patch('dependencies.execute', return_value='') as execute:
            setup('prepare', self.values)
        commands = [list(map(str, call.args[0])) for call in execute.call_args_list]
        self.assertEqual(len(commands), 1)
        self.assertIn('check_tools.py', commands[0][1])
        self.assertFalse(any('clone' in call or 'fetch' in call or '--build' in call for call in commands))

    def test_compiler_rebuild_requires_new_destination(self):
        with patch('dependencies.execute') as execute, self.assertRaises(ValueError):
            setup('build_compiler', self.values)
        execute.assert_not_called()

    def test_reinstall_reuses_matching_compiler_cache_in_current_prefix(self):
        from dependencies import fingerprint
        sdk, prefix = Path(self.values['sdk']), Path(self.values['prefix'])
        (prefix / 'bin/powerpc-xsdk-elf-gcc.exe').touch()
        cached = self.root / 'original-compiler-cache'
        for stage in ('binutils', 'newlib', 'gcc'):
            directory = cached / 'build' / stage
            directory.mkdir(parents=True)
            (directory / 'Makefile').write_text('prefix = ' + str(prefix) + '\n')
        state = {'toolchain': {'prefix': str(prefix.resolve()), 'recipe': fingerprint(sdk, 'toolchain'),
                               'source_work': str(cached)}}
        with patch('dependencies.load_state', return_value=state), patch('dependencies.execute') as execute:
            setup('repair_compiler', self.values)
        commands = [list(map(str, call.args[0])) for call in execute.call_args_list]
        self.assertEqual(sum('-C' in command for command in commands), 3)
        installs = [call for call in execute.call_args_list if '-C' in call.args[0]]
        for call in installs:
            self.assertEqual(call.kwargs['env']['PATH'].split(os.pathsep)[0], str(prefix / 'bin'))
            self.assertIn(str(Path(self.values['msys']) / 'usr/bin'), call.kwargs['env']['PATH'])
        self.assertFalse(any('toolchain_fresh' in command for command in commands))
        self.assertTrue(list((Path(self.values['work']) / 'compiler-backups').glob('compiler-*')))

    def test_update_refuses_dirty_checkout(self):
        source = self.root / 'checkout'
        (source / '.git').mkdir(parents=True)
        with patch('dependencies.execute', side_effect=['https://github.com/team/repo.git', ' M source.c']) as execute:
            with self.assertRaisesRegex(ValueError, 'Local changes'):
                checkout('git', source, 'https://github.com/team/repo', 'main', update=True)
        self.assertFalse(any('fetch' in call.args[0] for call in execute.call_args_list))

    def test_explicit_inplace_git_update_backs_up_tracked_edits_without_cleaning(self):
        source = self.root / 'checkout'
        (source / '.git').mkdir(parents=True)
        results = ['https://github.com/team/repo.git', ' M source.c', 'main', '', '', 'backup-stash', '']
        with patch('dependencies.execute', side_effect=results) as execute:
            checkout('git', source, 'https://github.com/team/repo', 'main', update=True, overwrite=True)
        commands = [call.args[0] for call in execute.call_args_list]
        self.assertTrue(any('stash' in command and 'push' in command for command in commands))
        self.assertTrue(any('--ff-only' in command for command in commands))
        self.assertFalse(any('clean' in command or '--hard' in command for command in commands))

    def test_download_refuses_overwriting_unrelated_checkout(self):
        source = self.root / 'checkout'
        (source / '.git').mkdir(parents=True)
        with patch('dependencies.execute', return_value='https://github.com/other/repo.git'):
            with self.assertRaisesRegex(ValueError, 'different URL'):
                checkout('git', source, 'https://github.com/team/repo', 'main')


if __name__ == '__main__':
    unittest.main()
