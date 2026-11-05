"""Explicit GitHub dependency setup; no action is run merely by opening the GUI."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import urlsplit

from processes import hidden_options

ACTIONS = ('fetch_sdk', 'fetch_sdl', 'build_sdk', 'build_sdl', 'prepare', 'update_all',
           'build_compiler', 'build_shaders')
SOURCE_FIELDS = ('sdk_repo', 'sdk_ref', 'sdl_repo', 'sdl_ref', 'sdl_source', 'shader_repo', 'shader_ref', 'search_root')
DEFAULTS = {'sdk_repo': 'https://github.com/ZenithUzu/xsdk.git', 'sdk_ref': 'main',
            'sdl_repo': 'https://github.com/xenosworks/SDL-xenon.git', 'sdl_ref': 'xenon',
            'shader_repo': 'https://github.com/xenosworks/glslang-xenon.git', 'shader_ref': 'xenon',
            'sdl_source': 'C:/SDL-xenon', 'search_root': ''}


def github_source(url, branch):
    parsed = urlsplit(url.strip())
    parts = parsed.path.strip('/').split('/')
    if (parsed.scheme != 'https' or parsed.netloc.lower() != 'github.com' or parsed.query or parsed.fragment
            or len(parts) < 2 or any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', item) for item in parts[:2])):
        raise ValueError('Use an HTTPS GitHub repository URL without credentials, query or fragment.')
    if len(parts) > 2:
        if parts[2] != 'tree' or len(parts) < 4:
            raise ValueError('Use a repository URL or a /tree/branch URL, not a file or release link.')
        branch = '/'.join(parts[3:])
    if (not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]*', branch) or '..' in branch
            or '//' in branch or branch.endswith(('/', '.', '.lock'))):
        raise ValueError('Invalid Git branch.')
    return 'https://github.com/' + parts[0] + '/' + parts[1].removesuffix('.git') + '.git', branch


def dependency_plan(action, values, script_root):
    if action not in ACTIONS:
        raise ValueError('Unknown dependency action.')
    for url, branch in [('sdk_repo', 'sdk_ref'), ('sdl_repo', 'sdl_ref'), ('shader_repo', 'shader_ref')]:
        github_source(values[url], values[branch])
    if not 1 <= int(values['jobs']) <= 64:
        raise ValueError('Use 1 to 64 jobs.')
    msys = Path(values['msys'])
    bash = msys / 'usr/bin/bash.exe'
    if not bash.is_file():
        raise ValueError('Install MSYS2 first and select its root folder. Setup will install missing UCRT64 packages.')
    if (action in ('fetch_sdl', 'build_sdl', 'prepare', 'update_all')
            and (not values.get('sdl_source') or not values.get('sdl'))):
        raise ValueError('Choose SDL source and SDL build folders in Sources and dependencies.')
    bootstrap = str(Path(script_root).resolve() / 'tools/windows/bootstrap-dependencies.sh').replace('\\', '/')
    if len(bootstrap) > 2 and bootstrap[1] == ':':
        bootstrap = '/' + bootstrap[0].lower() + bootstrap[2:]
    command = [str(bash), '--login', bootstrap, str(Path(script_root) / 'tools/windows/dependencies.py'), action]
    for name in ('msys', 'sdk', 'prefix', 'work', 'sdl', 'jobs', 'glslang', *SOURCE_FIELDS):
        if name == 'search_root':
            continue
        command.extend(['--' + name.replace('_', '-'), str(values.get(name, ''))])
    environment = dict(os.environ, MSYSTEM='UCRT64', CHERE_INVOKING='1')
    environment['PATH'] = os.pathsep.join([str(msys / 'ucrt64/bin'), str(msys / 'usr/bin'),
                                         str(Path(values['prefix']) / 'bin'), environment.get('PATH', '')])
    environment['GIT_TERMINAL_PROMPT'] = '0'
    return command, environment


def execute(command, cwd=None, capture=False):
    print('> ' + subprocess.list2cmdline(list(map(str, command))), flush=True)
    if capture:
        return subprocess.check_output(list(map(str, command)), cwd=cwd, text=True, **hidden_options()).strip()
    subprocess.run(list(map(str, command)), cwd=cwd, check=True, **hidden_options())
    return ''


def checkout(git, path, url, branch, update=False):
    url, branch = github_source(url, branch)
    path = Path(path).resolve()
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        execute([git, 'clone', '--branch', branch, '--', url, path])
    elif not path.is_dir():
        raise ValueError('The source destination is not a folder: ' + str(path))
    elif update:
        if not (path / '.git').exists():
            raise ValueError('Updating requires a Git checkout. Choose a NEW source folder for this ZIP installation.')
        origin = execute([git, '-C', path, 'remote', 'get-url', 'origin'], capture=True)
        if github_source(origin, branch)[0] != url:
            raise ValueError('The existing source origin differs from the selected URL; choose a NEW folder.')
        if execute([git, '-C', path, 'status', '--porcelain', '--untracked-files=normal'], capture=True):
            raise ValueError('Local changes found; save them before updating: ' + str(path))
        if execute([git, '-C', path, 'branch', '--show-current'], capture=True) != branch:
            raise ValueError('Select the matching branch or a NEW source folder.')
        execute([git, '-C', path, 'fetch', 'origin', branch])
        execute([git, '-C', path, 'merge', '--ff-only', 'refs/remotes/origin/' + branch])
    if not update and (path / '.git').exists():
        origin = execute([git, '-C', path, 'remote', 'get-url', 'origin'], capture=True)
        if github_source(origin, branch)[0] != url:
            raise ValueError('Existing source uses a different URL. Keep its URL or choose a NEW destination.')
        if execute([git, '-C', path, 'branch', '--show-current'], capture=True) != branch:
            raise ValueError('Existing source uses a different branch. Keep its branch or choose a NEW destination.')
    print('Using source folder: ' + str(path), flush=True)
    return path


def setup(action, values):
    msys = Path(values['msys']).resolve()
    bash, git = msys / 'usr/bin/bash.exe', msys / 'usr/bin/git.exe'
    sdk, prefix, work = (Path(values[key]).resolve() for key in ('sdk', 'prefix', 'work'))
    source, build = Path(values['sdl_source']).resolve(), Path(values['sdl']).resolve()
    if any(' ' in str(path) for path in (sdk, prefix, work)):
        raise ValueError('Use paths without spaces for xSDK, compiler and work.')
    if action == 'build_compiler' and prefix.exists():
        raise ValueError('Compiler construction needs a NEW compiler destination; existing tools are kept.')
    needed = ['usr/bin/git.exe', 'usr/bin/make.exe', 'ucrt64/bin/cmake.exe', 'ucrt64/bin/ninja.exe',
              'ucrt64/bin/gcc.exe', 'ucrt64/bin/python.exe']
    if any(not (msys / name).is_file() for name in needed):
        packages = ('pacman -S --needed --noconfirm base-devel texinfo git curl patch tar xz '
                    'mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-gmp mingw-w64-ucrt-x86_64-mpfr '
                    'mingw-w64-ucrt-x86_64-mpc mingw-w64-ucrt-x86_64-python '
                    'mingw-w64-ucrt-x86_64-cmake mingw-w64-ucrt-x86_64-ninja')
        execute([bash, '--login', '-c', packages])
    update = action == 'update_all'
    stamp = time.strftime('%Y%m%d-%H%M%S')
    if update and sdk.exists() and not (sdk / '.git').exists():
        sdk = work / 'sdk-updates' / ('xsdk-' + stamp)
        print('ZIP installation kept; cloning an updated SDK to a NEW folder.', flush=True)
    if update and source.exists() and not (source / '.git').exists():
        source = work / 'sdl-updates' / ('SDL-xenon-' + stamp)
        build = work / 'sdl-builds' / stamp
    checkout(git, sdk, values['sdk_repo'], values['sdk_ref'], update)
    if not (sdk / 'tools/windows/run.sh').is_file() or not (sdk / 'cmake/xsdk.cmake').is_file():
        raise ValueError('Choose an xSDK Windows-compatible fork. '
                         'The original SDK alone lacks this Windows integration.')
    print('XSDK_NEW_ROOT=' + str(sdk), flush=True)
    if action == 'fetch_sdk':
        return
    if action in ('fetch_sdl', 'build_sdl', 'prepare', 'update_all'):
        checkout(git, source, values['sdl_repo'], values['sdl_ref'], update)
        if not (source / 'include/SDL3/SDL.h').is_file():
            raise ValueError('The selected repository is not an SDL3 source tree.')
        if action == 'fetch_sdl':
            return
    def stage(name):
        # Positional arguments, never shell interpolation of user URLs or paths.
        def unix(path):
            path = str(path).replace('\\', '/')
            return '/' + path[0].lower() + path[2:] if len(path) > 2 and path[1] == ':' else path
        execute([bash, '--login', unix(sdk / 'tools/windows/run.sh'), name, unix(sdk), unix(prefix),
                 unix(work), values['jobs']])
    if not (prefix / 'bin/powerpc-xsdk-elf-g++.exe').is_file() or action == 'build_compiler':
        if prefix.exists() and action != 'build_compiler':
            raise ValueError('Compiler folder exists but is incomplete; select a NEW compiler destination.')
        stage('dependencies')
        stage('toolchain_fresh')
    execute([msys / 'ucrt64/bin/python.exe', sdk / 'tools/windows/check_tools.py', prefix])
    if action == 'build_compiler':
        return
    shader = Path(values.get('glslang') or prefix / 'bin/glslang.exe')
    if not shader.is_file() or update or action == 'build_shaders':
        checkout(git, work / 'glslang', values['shader_repo'], values['shader_ref'], update)
        stage('shaders')
        shader = prefix / 'bin/glslang.exe'
        print('XSDK_PATHS=' + json.dumps({'glslang': str(shader)}), flush=True)
    if action == 'build_shaders':
        return
    if (not (sdk / 'build/libxsdk.a').is_file() or not (sdk / 'build/host/libxsc.dll').is_file()
            or action in ('build_sdk', 'update_all')):
        stage('sdk')
    if action == 'prepare' and (build / 'SDL3Config.cmake').is_file() and (build / 'libSDL3.a').is_file():
        print('Existing SDL3 build kept; no rebuild requested.', flush=True)
        return
    if action in ('build_sdl', 'prepare', 'update_all'):
        cmake, ninja = msys / 'ucrt64/bin/cmake.exe', msys / 'ucrt64/bin/ninja.exe'
        execute([cmake, '-S', source, '-B', build, '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release',
                 '-DCMAKE_MAKE_PROGRAM=' + str(ninja), '-DCMAKE_TOOLCHAIN_FILE=' + str(sdk / 'cmake/xsdk.cmake'),
                 '-DXSDK_TOOLCHAIN=' + str(prefix)])
        execute([cmake, '--build', build, '--parallel', values['jobs']])
        if not (build / 'SDL3Config.cmake').is_file():
            raise ValueError('SDL build finished without SDL3Config.cmake; inspect the log.')
        print('XSDK_PATHS=' + json.dumps({'sdl': str(build), 'sdl_source': str(source)}), flush=True)
    print('Dependencies ready. Choose your game source/ROM and use Build and package game.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=ACTIONS)
    for name in ('msys', 'sdk', 'prefix', 'work', 'sdl', 'jobs', 'glslang', *SOURCE_FIELDS[:-1]):
        parser.add_argument('--' + name.replace('_', '-'), required=True)
    args = vars(parser.parse_args())
    action = args.pop('action')
    setup(action, args)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise SystemExit(str(error)) from error
