"""Reject Linux/WSL binaries accidentally selected for the Windows port."""
import subprocess
import sys
import tempfile
from pathlib import Path

from processes import hidden_options


def check(prefix):
    bin_dir = Path(prefix) / "bin"
    for name in ("gcc", "g++", "as", "ld", "ar", "ranlib", "objcopy", "objdump", "nm", "readelf", "strip"):
        tool = bin_dir / ("powerpc-xsdk-elf-" + name + ".exe")
        if not tool.is_file():
            raise RuntimeError(f"Missing native tool: {tool}")
        with tool.open("rb") as stream:
            if stream.read(2) != b"MZ":
                raise RuntimeError(f"Not a Windows PE executable: {tool}")
    compiler = bin_dir / "powerpc-xsdk-elf-gcc.exe"
    target = subprocess.check_output([str(compiler), "-dumpmachine"], text=True, **hidden_options()).strip()
    if target != "powerpc-xsdk-elf":
        raise RuntimeError(f"Wrong target compiler: {target}")
    subprocess.run([str(compiler), "--version"], check=True, **hidden_options())
    cxx = bin_dir / "powerpc-xsdk-elf-g++.exe"
    if subprocess.check_output([str(cxx), "-dumpmachine"], text=True, **hidden_options()).strip() != target:
        raise RuntimeError("C and C++ compilers target different platforms")
    with tempfile.TemporaryDirectory(prefix="xsdk-check-") as folder:
        source = Path(folder) / "check.cpp"
        output = Path(folder) / "check.o"
        source.write_text(
            "#include <atomic>\n#include <thread>\n#include <format>\n"
            "std::atomic<unsigned> value;\n"
            "int check() { try { throw 7; } catch (int x) { return x + value.load(); } }\n",
            encoding="utf-8")
        subprocess.run([str(cxx), "-std=c++23", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(output)], check=True, **hidden_options())
        subprocess.run([str(bin_dir / "powerpc-xsdk-elf-objdump.exe"), "-f", str(output)], check=True, **hidden_options())
    print("PASS: native tools, powerpc-xsdk-elf C/C++23 compilation and C++ headers")


if __name__ == "__main__":
    try:
        check(sys.argv[1])
    except (IndexError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        raise SystemExit(str(error)) from error
