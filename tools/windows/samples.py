"""Build upstream CMake samples with Windows paths passed as separate arguments."""
import json
import os
import subprocess
import sys
from pathlib import Path

from options import BUILD_TYPES, cmake_options


def build(sdk, prefix, jobs, build_type, sdl="", *extra):
    if build_type not in BUILD_TYPES or not str(jobs).isdigit() or not 1 <= int(jobs) <= 64:
        raise ValueError("Invalid build configuration")
    extra = cmake_options(json.dumps(list(extra)))
    sdk = Path(sdk).resolve()
    prefix = Path(prefix).resolve()
    for name in ("hello", "triangle", "cube", "sound", "sdl3", "template"):
        output = sdk / "build/samples" / name
        args = ["cmake", "-S", str(sdk / "samples" / name), "-B", str(output), "-G", "Ninja",
                "-DCMAKE_TOOLCHAIN_FILE=" + str(sdk / "cmake/xsdk.cmake"),
                "-DXSDK_TOOLCHAIN=" + str(prefix), "-DCMAKE_BUILD_TYPE=" + build_type]
        if os.environ.get("XSDK_GLSLANG_OVERRIDE"):
            args.append("-DXSDK_GLSLANG=" + os.environ["XSDK_GLSLANG_OVERRIDE"])
        if sdl and name == "sdl3":
            args.append("-DSDL3_DIR=" + str(Path(sdl).resolve()))
        subprocess.run(args + extra, check=True)
        subprocess.run(["cmake", "--build", str(output), "--parallel", str(jobs)], check=True)
        if name != "sdl3" and not (output / (name + ".xex")).is_file():
            raise ValueError("Missing sample output: " + name)
        if name == "sdl3" and sdl and not (output / "sdl3.xex").is_file():
            raise ValueError("SDL3 was requested but its sample was not built; check SDL3_DIR")


if __name__ == "__main__":
    try:
        build(*sys.argv[1:])
    except (ValueError, TypeError, OSError, subprocess.SubprocessError) as error:
        raise SystemExit(str(error)) from error
