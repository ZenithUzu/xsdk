"""Update an unmodified checkout from the fork, with fast-forward merges only."""
import subprocess
import sys
from pathlib import Path

REPOSITORY = "https://github.com/ZenithUzu/xsdk.git"


def update(folder):
    folder = Path(folder)
    if not (folder / ".git").exists():
        raise ValueError("Esta copia es ZIP. Usa Instalar-Windows.ps1 en una carpeta nueva para tener actualizaciones Git.")

    def git(*args):
        return subprocess.check_output(["git", "-C", str(folder), *args], text=True).strip()

    origin = git("remote", "get-url", "origin").rstrip("/")
    if origin not in (REPOSITORY, REPOSITORY.removesuffix(".git"), "git@github.com:ZenithUzu/xsdk.git"):
        raise ValueError("El origen no es ZenithUzu/xsdk; no se cambió el repositorio")
    if git("status", "--porcelain", "--untracked-files=normal"):
        raise ValueError("Hay cambios locales o archivos sin seguimiento. Guárdalos antes de actualizar")
    if git("branch", "--show-current") not in ("main", "windows-native"):
        raise ValueError("Selecciona main o windows-native antes de actualizar")
    git("fetch", "origin", "main")
    git("merge", "--ff-only", "refs/remotes/origin/main")
    print("Código actualizado: " + git("rev-parse", "--short", "HEAD"))
    print("Cierra y abre de nuevo la interfaz. Reconstruye SDK y proyectos; las herramientas no se actualizan solas.")


if __name__ == "__main__":
    try:
        update(sys.argv[1])
    except (IndexError, ValueError, OSError, subprocess.SubprocessError) as error:
        raise SystemExit(str(error)) from error
