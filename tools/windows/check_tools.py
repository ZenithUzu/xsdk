"""Reject Linux/WSL binaries accidentally selected for the Windows port."""
import subprocess
import sys
from pathlib import Path


def check(prefix):
    compiler = Path(prefix) / "bin" / "powerpc-xsdk-elf-gcc.exe"
    if not compiler.is_file():
        raise RuntimeError(f"Missing native compiler: {compiler}")
    with compiler.open("rb") as stream:
        if stream.read(2) != b"MZ":
            raise RuntimeError("The compiler is not a Windows PE executable")
    target = subprocess.check_output([str(compiler), "-dumpmachine"], text=True).strip()
    if target != "powerpc-xsdk-elf":
        raise RuntimeError(f"Wrong target compiler: {target}")
    subprocess.run([str(compiler), "--version"], check=True)
    print("PASS: Windows compiler, target powerpc-xsdk-elf")


if __name__ == "__main__":
    try:
        check(sys.argv[1])
    except (IndexError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        raise SystemExit(str(error)) from error
