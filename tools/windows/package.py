"""Package a built Windows toolchain with corresponding sources and notices."""
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

from check_tools import check


def package(sdk, prefix, output):
    sdk, prefix, output = Path(sdk), Path(prefix), Path(output)
    check(prefix)
    work = output.parent
    archives = sorted((work / "toolchain/src").glob("*.tar.*"))
    if len(archives) < 3 or not (work / "glslang/CMakeLists.txt").is_file():
        raise ValueError("Conserva las fuentes del toolchain y glslang en la carpeta de trabajo para distribuirlas")
    if not (prefix / "bin/glslang.exe").is_file():
        raise ValueError("Construye Shaders primero")
    tracked = subprocess.check_output(["git", "-C", str(sdk), "ls-files", "-z"]).split(b"\0")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".zip.partial")
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
            for name in tracked:
                if name:
                    relative = name.decode("utf-8")
                    archive.write(sdk / relative, "sdk/" + relative)
            for path in prefix.rglob("*"):
                if path.is_file():
                    archive.write(path, "compiler/" + path.relative_to(prefix).as_posix())
            for path in archives:
                archive.write(path, "sources/" + path.name)
            source = work / "glslang"
            repositories = [source] + [path.parent for path in source.rglob(".git")
                                       if path.parent != source and not any(
                                           part.startswith("build") for part in path.relative_to(source).parts)]
            written = set()
            for repository in repositories:
                names = subprocess.check_output(["git", "-C", str(repository), "ls-files", "-z"]).split(b"\0")
                for name in names:
                    if not name:
                        continue
                    path = repository / name.decode("utf-8")
                    if not path.is_file() or path.is_symlink():
                        continue
                    relative = path.relative_to(source).as_posix()
                    if relative not in written:
                        archive.write(path, "sources/glslang/" + relative)
                        written.add(relative)
            archive.writestr("LEEME.txt", "Herramientas experimentales para Windows. Requieren MSYS2 UCRT64.\n"
                              "Usa Instalar-Windows.ps1 -Bundle <zip>, o configura compiler en la interfaz.\n"
                              "sdk/LICENSE y sdk/THIRD_PARTY_NOTICES.md conservan los avisos originales.\n"
                              "sources/ contiene las fuentes; sdk/tools/toolchain contiene los parches y scripts.\n"
                              "Conserva estas fuentes y licencias al redistribuir. No incluye validación de consola.\n")
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    with output.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    Path(str(output) + ".sha256").write_text(digest + "  " + output.name + "\n", encoding="ascii")
    print("Paquete y checksum: " + str(output))


if __name__ == "__main__":
    try:
        package(*sys.argv[1:])
    except (ValueError, TypeError, OSError, subprocess.SubprocessError) as error:
        raise SystemExit(str(error)) from error
