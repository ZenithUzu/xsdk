"""Update an unmodified checkout from the fork, with fast-forward merges only."""
import subprocess
import sys
import time
from pathlib import Path

from processes import hidden_options

REPOSITORY = "https://github.com/ZenithUzu/xsdk.git"


def update(folder, component="sdk", copies=""):
    if component not in ("sdk", "shaders"):
        raise ValueError("Unknown component")
    repository = REPOSITORY if component == "sdk" else "https://github.com/xenosworks/glslang-xenon.git"
    branch = "main" if component == "sdk" else "xenon"
    folder = Path(folder)
    if not (folder / ".git").exists() and component == "sdk" and copies:
        destination = Path(copies) / ("xsdk-" + time.strftime("%Y%m%d-%H%M%S"))
        if destination.exists():
            raise ValueError("La carpeta de actualización ya existe")
        destination.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--branch", "main", REPOSITORY, str(destination)], check=True, **hidden_options())
        print("XSDK_NEW_ROOT=" + str(destination.resolve()), flush=True)
        print("Copia nueva instalada. La copia ZIP original se conserva. Abre Iniciar-Windows.cmd de la nueva carpeta.")
        return
    if not (folder / ".git").exists():
        raise ValueError("Esta copia es ZIP. Usa Instalar-Windows.ps1 en una carpeta nueva para tener actualizaciones Git.")

    def git(*args):
        return subprocess.check_output(["git", "-C", str(folder), *args], text=True, **hidden_options()).strip()

    origin = git("remote", "get-url", "origin").rstrip("/")
    if origin not in (repository, repository.removesuffix(".git"), repository.replace("https://github.com/", "git@github.com:")):
        raise ValueError("El origen no coincide con el componente; no se cambió el repositorio")
    if git("status", "--porcelain", "--untracked-files=normal"):
        raise ValueError("Hay cambios locales o archivos sin seguimiento. Guárdalos antes de actualizar")
    if git("branch", "--show-current") not in (("main", "windows-native") if component == "sdk" else ("xenon",)):
        raise ValueError("Selecciona main o windows-native antes de actualizar")
    git("fetch", "origin", branch)
    git("merge", "--ff-only", "refs/remotes/origin/" + branch)
    print("Código actualizado: " + git("rev-parse", "--short", "HEAD"))
    print("Cierra y abre de nuevo la interfaz. Reconstruye SDK y proyectos; las herramientas no se actualizan solas.")


if __name__ == "__main__":
    try:
        update(*sys.argv[1:])
    except (IndexError, ValueError, OSError, subprocess.SubprocessError) as error:
        raise SystemExit(str(error)) from error
