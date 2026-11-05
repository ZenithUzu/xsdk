"""Build the portable Windows GUI and bundle its source and runtime notices."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk

from processes import hidden_options

ROOT = Path(__file__).resolve().parents[2]


def assemble(output, executable):
    output = Path(output).resolve()
    (output / 'licenses').mkdir(exist_ok=True)
    source_files = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '-z'], **hidden_options()).split(b'\0')
    for name in source_files:
        if not name:
            continue
        relative = Path(name.decode('utf-8'))
        source, target = ROOT / relative, output / 'sdk' / relative
        if source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    base = Path(sys.base_prefix)
    shutil.copy2(base / 'LICENSE.txt', output / 'licenses/Python-LICENSE.txt')
    distribution = importlib.metadata.distribution('pyinstaller')
    for entry in distribution.files:
        if str(entry).replace('\\', '/').endswith('/licenses/COPYING.txt'):
            shutil.copy2(distribution.locate_file(entry), output / 'licenses/PyInstaller-COPYING.txt')
    window = tk.Tk()
    window.withdraw()
    try:
        for name, variable in (('Tcl', 'tcl_library'), ('Tk', 'tk_library')):
            library = window.tk.eval('set ' + variable)
            handle = window.tk.call('open', library + '/license.terms', 'r')
            text = window.tk.call('read', handle)
            window.tk.call('close', handle)
            (output / 'licenses' / (name + '-license.terms')).write_text(text, encoding='utf-8')
    finally:
        window.destroy()
    for name in ('LICENSE', 'THIRD_PARTY_NOTICES.md', 'README-PORTABLE.md', 'SECURITY-REVIEW.md'):
        shutil.copy2(ROOT / name, output / name)
    artifacts = [executable]
    artifacts.extend(path for path in (output / '_internal').rglob('*') if path.is_file())
    hashes = []
    for artifact in sorted(artifacts):
        with artifact.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        hashes.append(digest + '  ' + artifact.relative_to(output).as_posix())
    (output / 'SHA256SUMS.txt').write_text('\n'.join(hashes) + '\n', encoding='utf-8')
    metadata = {'python': sys.version.split()[0], 'pyinstaller': distribution.version,
                'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, **hidden_options()).strip(),
                'source_dirty': bool(subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain'], **hidden_options())),
                'game_files_included': False, 'compiler_included': False, 'sdk_source_included': True,
                'layout': 'folder' if (output / '_internal').is_dir() else 'onefile'}
    (output / 'portable-build.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--onefile', action='store_true', help='Opt in to a self-extracting single EXE')
    args = parser.parse_args()
    if os.name != 'nt':
        raise SystemExit('Build the Windows EXE on Windows with CPython and tkinter.')
    output = Path(args.output).resolve()
    if output.exists():
        raise SystemExit('Choose a NEW output directory.')
    importlib.metadata.version('pyinstaller')
    output.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix='xsdk-freeze-') as scratch:
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
                        '--onefile' if args.onefile else '--onedir', '--windowed',
                        '--name', 'xSDK-Windows', '--distpath', scratch + '/dist', '--workpath', scratch + '/work',
                        '--specpath', scratch + '/spec', str(ROOT / 'tools/windows/gui.py')], check=True, **hidden_options())
        built = Path(scratch) / 'dist'
        if args.onefile:
            shutil.copy2(built / 'xSDK-Windows.exe', output / 'xSDK-Windows.exe')
        else:
            for child in (built / 'xSDK-Windows').iterdir():
                shutil.move(str(child), str(output / child.name))
    assemble(output, output / 'xSDK-Windows.exe')
    shutil.make_archive(str(output), 'zip', root_dir=output)
    print('Portable folder and ZIP: ' + str(output))


if __name__ == '__main__':
    main()
