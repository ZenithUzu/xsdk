"""Prepare a private Xbox game folder from a verified local CoopDX build."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

FORBIDDEN = set('<>:"/\\|?*=;+,')
BLOCKED = {'.exe', '.dll', '.elf', '.z64', '.n64', '.v64', '.xex', '.pdb'}


def digest(path, algorithm='sha256'):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def package_game(project, build, output, pc='', include_mods=False, cancelled=lambda: False):
    project, build, output = Path(project).resolve(), Path(build).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError('Choose a NEW output folder; existing games and saves are never overwritten.')
    image, rom = build / 'sm64coopdx.xex', project / 'baserom.us.z64'
    if pc and not Path(pc).is_dir():
        raise ValueError('The selected CoopDX PC folder does not exist.')
    report = json.loads((build / 'build-info.json').read_text(encoding='utf-8-sig'))
    if not image.is_file() or image.read_bytes()[:4] != b'XEX2':
        raise ValueError('Build the Xbox XEX first; a desktop executable cannot replace it.')
    if report.get('sha256', {}).get(image.name) != digest(image):
        raise ValueError('The XEX does not match its build-info.json. Rebuild before packaging.')
    expected = (project / 'sm64.us.sha1').read_text().split()[0].lower()
    if digest(rom, 'sha1') != expected:
        raise ValueError('The local ROM does not match sm64.us.sha1.')
    sources = [(image, Path(image.name)), (rom, Path(rom.name))]
    origins = {}
    for folder in ['lang', 'palettes'] + (['mods', 'dynos'] if include_mods else []):
        candidates = ([Path(pc).resolve() / folder] if pc else []) + [project / folder]
        source = next((path for path in candidates if path.is_dir()), None)
        if source is None:
            if folder in ('lang', 'palettes'):
                raise ValueError('Missing runtime folder: ' + folder)
            continue
        if output.is_relative_to(source) or source.is_relative_to(output):
            raise ValueError('The output must be separate from runtime inputs.')
        origins[folder] = str(source)
        for path in source.rglob('*'):
            if cancelled():
                raise InterruptedError('Packaging cancelled.')
            if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
                raise ValueError('Linked runtime paths are not supported: ' + str(path))
            relative = Path(folder) / path.relative_to(source)
            if any(len(part) > 42 or any(char in FORBIDDEN or ord(char) < 32 for char in part)
                   or part.endswith((' ', '.')) for part in relative.parts):
                raise ValueError('Invalid FATX path; shorten or rename it: ' + str(relative))
            if path.is_file() and path.suffix.lower() not in BLOCKED:
                sources.append((path, relative))
    destinations = [str(relative).casefold() for _, relative in sources]
    if len(destinations) != len(set(destinations)):
        raise ValueError('Runtime contains names that collide on a case-insensitive filesystem.')
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.coopdx-package-', dir=output.parent))
    try:
        files = {}
        for source, relative in sources:
            if cancelled():
                raise InterruptedError('Packaging cancelled.')
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            files[relative.as_posix()] = digest(target)
        for folder in ('mods', 'dynos', 'lang', 'palettes'):
            (stage / folder).mkdir(exist_ok=True)
        shutil.copy2(build / 'build-info.json', stage / 'build-info.json')
        metadata = {'schema': 1, 'hardware_validation': 'not-run', 'optional_mods': include_mods,
                    'runtime_origins': origins, 'sha256': files}
        (stage / 'package-info.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        (stage / 'PACKAGE-README.txt').write_text(
            'Private local build. Copy this folder to your Xbox with the game closed.\n'
            'Launch sm64coopdx.xex in Aurora. This package has not been tested on hardware.\n'
            'Keep your existing save folder when updating; this tool does not overwrite it.\n'
            'Optional mods/DynOS packs require separate compatibility testing.\n'
            'No reference XEX or desktop EXE is merged into this build.\n', encoding='utf-8')
        stage.rename(output)
    except BaseException:
        shutil.rmtree(stage)
        raise
    return output, len(files)
