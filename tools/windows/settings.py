"""Recover known local settings from older launchers/portable folders, without executing them."""
import json
import os
from pathlib import Path
from itertools import islice

PATHS = ('msys', 'sdk', 'prefix', 'work', 'glslang', 'project', 'sdl', 'sdl_source', 'rom', 'pc_game')


def read_profile(path):
    try:
        value = json.loads(Path(path).read_text(encoding='utf-8-sig'))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def legacy_profiles(current):
    current = Path(current).absolute()
    shared = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'xsdk-windows/settings.json'
    candidates = [shared, Path('C:/xsdk-windows/data/settings.json'), Path('C:/xsdk-windows/settings.json')]
    roots = [Path('C:/'), Path('C:/tools'), Path.home() / 'Downloads', current.parent.parent.parent]
    extra = []
    for root in roots:
        try:
            for folder in islice(root.iterdir(), 200):
                if (not folder.name.casefold().replace('-', '').replace('_', '').replace(' ', '').startswith('xsdk')
                        or folder.is_symlink() or (hasattr(folder, 'is_junction') and folder.is_junction())):
                    continue
                for relative in ('data/settings.json', 'settings.json'):
                    candidate = folder / relative
                    if candidate.is_file():
                        extra.append(candidate)
        except OSError:
            continue
    extra.sort(key=lambda path: path.stat().st_mtime if path.exists() else 0, reverse=True)
    result, seen = [], {str(current).casefold()}
    for path in candidates + extra:
        identity = str(path.absolute()).casefold()
        if identity not in seen and path.is_file():
            result.append(path)
            seen.add(identity)
    return result


def normalized_path(key, value):
    path = Path(str(value))
    if key == 'project' and path.name == 'xsdk' and path.parent.name == 'platform':
        root = path.parent.parent
        if (root / 'xsdk-project.json').is_file():
            return str(root)
    return str(value)


def usable_path(key, value):
    if not value or any(char in str(value) for char in '\r\n\x00') or str(value).startswith(('\\\\', '//')):
        return False
    path = Path(normalized_path(key, value))
    markers = {'msys': 'usr/bin/bash.exe', 'sdk': 'cmake/xsdk.cmake',
               'prefix': 'bin/powerpc-xsdk-elf-gcc.exe', 'sdl': 'SDL3Config.cmake',
               'sdl_source': 'include/SDL3/SDL.h'}
    if key in markers:
        return (path / markers[key]).is_file()
    if key in ('glslang', 'rom'):
        return path.is_file()
    if key == 'project':
        return (path / 'xsdk-project.json').is_file() or (path / 'CMakeLists.txt').is_file()
    return path.is_dir()


def recover(defaults, current, candidates=None, replace_invalid=False, saved_override=None):
    saved = dict(saved_override) if saved_override is not None else read_profile(current)
    values = dict(defaults)
    values.update({key: str(value) for key, value in saved.items()
                   if key in values and isinstance(value, (str, int)) and not isinstance(value, bool)})
    origins = []
    profiles = legacy_profiles(current) if candidates is None else candidates
    for profile in profiles:
        previous = read_profile(profile)
        imported = []
        for key in PATHS:
            if key not in values:
                continue
            # Defaults in a new portable are not explicit choices. Existing nonempty settings win.
            explicit = key in saved and bool(saved[key])
            if explicit and not (replace_invalid and not usable_path(key, values[key])):
                continue
            candidate = previous.get(key)
            if isinstance(candidate, str) and usable_path(key, candidate):
                values[key] = normalized_path(key, candidate)
                saved[key] = values[key]
                imported.append(key)
        if 'language' not in saved and previous.get('language') in ('en', 'es', 'pt'):
            values['language'] = previous['language']
            saved['language'] = values['language']
        if imported:
            origins.append((str(profile), imported))
    if values.get('project'):
        values['project'] = normalized_path('project', values['project'])
    return values, origins
