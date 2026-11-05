"""Replace managed source files in place while preserving build caches and local backups."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
import uuid

PROTECTED = {'.git', 'build', 'build-xsdk', 'build-windows', 'data', 'local'}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def checked(root, relative):
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts or not relative.parts:
        raise ValueError('Unsafe source path.')
    target = root / relative
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('Linked source path escapes its destination: ' + str(relative))
    for item in [target, *target.parents]:
        if item == root.parent:
            break
        if item.is_symlink() or (hasattr(item, 'is_junction') and item.is_junction()):
            raise ValueError('Linked source paths cannot be overwritten: ' + str(relative))
    return target


def overlay(snapshot, target, names, backup, revision):
    snapshot, target, backup = Path(snapshot).resolve(), Path(target).resolve(), Path(backup).resolve()
    if backup.is_relative_to(target) or snapshot.is_relative_to(target):
        raise ValueError('Use a work/backup folder separate from the source destination.')
    marker = target / '.xsdk-managed-source.json'
    try:
        previous = json.loads(marker.read_text(encoding='utf-8'))['files']
    except (OSError, ValueError, KeyError):
        previous = {}
    if not isinstance(previous, dict):
        previous = {}
    files, changed = {}, 0
    backup.mkdir(parents=True, exist_ok=False)
    print('Source backup: ' + str(backup), flush=True)
    for name in names:
        relative = Path(name)
        if relative.parts and relative.parts[0] in PROTECTED:
            continue
        source, destination = checked(snapshot, relative), checked(target, relative)
        if not source.is_file():
            raise ValueError('Snapshot contains a non-file source entry: ' + str(relative))
        digest = sha(source)
        files[relative.as_posix()] = digest
        if destination.is_file() and sha(destination) == digest:
            continue
        if destination.exists():
            if not destination.is_file():
                raise ValueError('A source file collides with a directory: ' + str(relative))
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, saved)
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix='.xsdk-update-', dir=destination.parent)
        os.close(descriptor)
        try:
            shutil.copy2(source, temporary)
            # Changed bytes must be newer than objects compiled from local edits.
            os.utime(temporary, None)
            os.replace(temporary, destination)
        finally:
            if Path(temporary).exists():
                Path(temporary).unlink()
        changed += 1
    for name in previous.keys() - files.keys():
        if not Path(name).parts:
            raise ValueError('Invalid managed-source record.')
        if Path(name).parts[0] in PROTECTED:
            continue
        old = checked(target, name)
        if old.is_file():
            saved = backup / name
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old, saved)
            old.unlink()
            changed += 1
    marker.write_text(json.dumps({'schema': 1, 'revision': revision, 'files': files}, indent=2), encoding='utf-8')
    print(f'Source update complete: {changed} changed files; existing build directories kept.', flush=True)
    return changed


def update_zip_source(git, target, url, branch, work, component, execute):
    identity = hashlib.sha256((url + '#' + branch).encode()).hexdigest()[:12]
    cache = Path(work) / 'source-cache' / (component + '-' + identity)
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        execute([git, 'clone', '--branch', branch, '--', url, cache])
    else:
        if execute([git, '-C', cache, 'status', '--porcelain'], capture=True):
            raise ValueError('The source cache was modified; keep it or select another work folder.')
        execute([git, '-C', cache, 'fetch', 'origin', branch])
        execute([git, '-C', cache, 'merge', '--ff-only', 'refs/remotes/origin/' + branch])
    marker = {'sdk': 'cmake/xsdk.cmake', 'sdl': 'include/SDL3/SDL.h',
              'shaders': 'glslang/Public/ShaderLang.h'}[component]
    if not (Path(target) / marker).is_file() or not (cache / marker).is_file():
        raise ValueError('Source type does not match the selected destination; existing files kept.')
    if component == 'sdk' and not (cache / 'tools/windows/run.sh').is_file():
        raise ValueError('The snapshot does not contain Windows SDK integration.')
    revision = execute([git, '-C', cache, 'rev-parse', 'HEAD'], capture=True)
    names = execute([git, '-C', cache, 'ls-files', '-z'], capture=True).split('\0')
    backup = Path(work) / 'source-backups' / (component + '-' + time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6])
    return overlay(cache, target, [name for name in names if name], backup, revision)
