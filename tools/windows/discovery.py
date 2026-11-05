"""Bounded, filesystem-only discovery of local SDK components."""
from collections import deque
import os
from pathlib import Path
import shutil
from itertools import islice

SKIP = {'windows', '$recycle.bin', 'system volume information', 'node_modules', '.git', '_internal',
        'appdata', 'winsxs', 'windowsapps'}


def detect(values, search_roots=None, limit=600, depth=3):
    found = dict(values)
    for name in ('sdk', 'msys', 'prefix', 'glslang', 'sdl', 'sdl_source'):
        found.setdefault(name, '')
    explicit = {name: found[name] for name in ('sdk', 'msys', 'prefix', 'glslang', 'sdl', 'sdl_source')}
    def local(path):
        if str(path).startswith(('\\\\', '//')):
            return False
        if os.name == 'nt' and Path(path).drive:
            import ctypes
            return ctypes.windll.kernel32.GetDriveTypeW(Path(path).drive + '\\') != 4
        return True
    def valid(name, path):
        if not path or not local(path):
            return False
        path = Path(path)
        markers = {'sdk': 'cmake/xsdk.cmake', 'msys': 'usr/bin/bash.exe',
                   'prefix': 'bin/powerpc-xsdk-elf-gcc.exe', 'sdl': 'SDL3Config.cmake',
                   'sdl_source': 'include/SDL3/SDL.h'}
        return path.is_file() if name == 'glslang' else (path / markers[name]).is_file()
    locked = {name for name, path in explicit.items() if valid(name, path)}
    candidates = []
    for key, env in [('sdk', 'XSDK_ROOT'), ('msys', 'MSYS2_ROOT'), ('prefix', 'XSDK_TOOLCHAIN'),
                     ('sdl', 'SDL3_DIR'), ('sdl_source', 'SDL_XENON_SOURCE')]:
        if os.environ.get(env):
            candidates.append(Path(os.environ[env]))
    for binary, levels in [('powerpc-xsdk-elf-gcc.exe', 2), ('bash.exe', 3), ('glslang.exe', 1)]:
        location = shutil.which(binary)
        if location:
            path = Path(location)
            if binary == 'glslang.exe' and 'glslang' not in locked:
                found['glslang'] = str(path)
                locked.add('glslang')
            candidates.append(path.parents[levels - 1])
    if search_roots is None:
        roots = [Path.home() / 'Documents/GitHub', Path.home() / 'tools', Path.home() / 'Downloads']
        for letter in ('C', 'D', 'E', 'F'):
            drive = Path(letter + ':/')
            if os.name == 'nt':
                import ctypes
                if ctypes.windll.kernel32.GetDriveTypeW(str(drive)) not in (2, 3):
                    continue
            roots.extend([drive / 'tools', drive / 'dev', drive / 'GitHub'])
            candidates.extend([drive / 'xsdk-windows', drive / 'xsdk-tools/compiler', drive / 'msys64',
                               drive / 'SDL-xenon', drive / 'SDL-xenon/build-xsdk'])
        if values.get('search_root'):
            roots.insert(0, Path(values['search_root']))
    else:
        roots = list(map(Path, search_roots))
    candidates = [Path(path) for path in explicit.values() if path] + candidates
    visited = set()
    queue = deque((path, 0) for path in candidates + roots)
    while queue and len(visited) < limit:
        path, level = queue.popleft()
        try:
            if not local(path):
                continue
            if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
                continue
            resolved = str(path.absolute()).casefold()
            if resolved in visited or not path.is_dir():
                continue
            visited.add(resolved)
            for name in explicit:
                if name not in locked and valid(name, path):
                    found[name] = str(path)
                    locked.add(name)
            for child_name, name in [('build-xsdk', 'sdl'), ('bin/glslang.exe', 'glslang')]:
                child = path / child_name
                if name not in locked and valid(name, child):
                    found[name] = str(child)
                    locked.add(name)
            if len(locked) == len(explicit):
                break
            if level < depth:
                for child in islice(path.iterdir(), 300):
                    if (child.name.casefold() not in SKIP and not child.is_symlink()
                            and not (hasattr(child, 'is_junction') and child.is_junction()) and child.is_dir()):
                        queue.append((child, level + 1))
        except OSError:
            continue
    return found
