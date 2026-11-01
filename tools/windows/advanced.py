"""Build the original SDK's selected acceptance tests; XEX files run on the console."""
import subprocess
import sys
from pathlib import Path

from options import BUILD_TYPES, MAKE_TARGETS


def run(target, prefix, jobs, build_type="Release", sdl=""):
    if build_type not in BUILD_TYPES:
        raise ValueError("Invalid build type")
    if target not in MAKE_TARGETS:
        raise ValueError("Unknown SDK test target")
    if not str(jobs).isdigit() or not 1 <= int(jobs) <= 64:
        raise ValueError("Invalid job count")
    if target in ("sample_breaks", "cmake_check_break"):
        print("Negative tests: these deliberately broken XEX files must FAIL on the console.", flush=True)
    subprocess.run(["make", target, "-j" + str(jobs),
                    "TOOLCHAIN=" + str(Path(prefix) / "bin/powerpc-xsdk-elf-"),
                    "PYTHON=python3", "HOST_CC=gcc", "SAMPLE_BUILD_TYPE=" + build_type, "SDL3_DIR=" + sdl], check=True)
    print("Build complete. A successful build does not mean the console checks have passed.")


if __name__ == "__main__":
    try:
        run(*sys.argv[1:])
    except (ValueError, TypeError, OSError, subprocess.SubprocessError) as error:
        raise SystemExit(str(error)) from error
