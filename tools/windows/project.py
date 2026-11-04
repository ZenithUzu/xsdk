"""Run an explicit source-only port recipe with the installed tools."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def recipe_plan(project, sdk, compiler, msys, work, sdl="", rom="", jobs=4,
                build_type="Release", glslang="", restore_inputs=False):
    root = Path(project).resolve()
    manifest = json.loads((root / "xsdk-project.json").read_text(encoding="utf-8-sig"))
    if not isinstance(manifest, dict):
        raise ValueError("The project recipe must be a JSON object")
    if manifest.get("schema") != 1 or manifest.get("kind") != "powershell-port":
        raise ValueError("Unsupported xsdk-project.json recipe; expected schema 1 / powershell-port")
    if build_type not in ("Release", "RelWithDebInfo", "Debug", "MinSizeRel"):
        raise ValueError("Unknown build type")
    if not 1 <= int(jobs) <= 64:
        raise ValueError("Use 1 to 64 jobs")
    relative = manifest.get("build_script", "")
    script = (root / relative).resolve()
    if not relative or not script.is_relative_to(root) or script.suffix.lower() != ".ps1" or not script.is_file():
        raise ValueError("The recipe build script must be an existing .ps1 inside the selected project")
    sdk, compiler, msys = Path(sdk).resolve(), Path(compiler).resolve(), Path(msys).resolve()
    needed = [
        sdk / "cmake/xsdk.cmake", sdk / "src/xsdk.ld", sdk / "build/libxsdk.a",
        sdk / "build/host/libxsc.dll", sdk / "tools/build_shaders.py", sdk / "tools/elf2xex.py",
        compiler / "bin/powerpc-xsdk-elf-gcc.exe", compiler / "bin/powerpc-xsdk-elf-g++.exe",
        Path(glslang) if glslang else compiler / "bin/glslang.exe",
        msys / "ucrt64/bin/python.exe", msys / "ucrt64/bin/cmake.exe",
        msys / "ucrt64/bin/ninja.exe", msys / "usr/bin/make.exe",
    ]
    missing = [str(path) for path in needed if not path.is_file()]
    if missing:
        raise ValueError("Missing installed tools (build only the missing component):\n" + "\n".join(missing))
    if manifest.get("requires_sdl3", False) and (not sdl or not Path(sdl).is_dir()):
        raise ValueError("This port requires the SDL3 Xenon build folder in SDL3_DIR")
    if rom and not Path(rom).is_file():
        raise ValueError("The selected private ROM does not exist")
    output = Path(work).resolve() / "projects" / root.name
    system = Path(os.environ.get("SystemRoot", "C:/Windows"))
    powershell = system / "System32/WindowsPowerShell/v1.0/powershell.exe"
    command = [str(powershell), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
               "-Game", "-XsdkRoot", str(sdk), "-Toolchain", str(compiler), "-MsysRoot", str(msys),
               "-OutDir", str(output), "-Jobs", str(int(jobs)), "-BuildType", build_type]
    if restore_inputs:
        command.append("-RestoreInheritedInputs")
    if glslang:
        command.extend(["-Glslang", str(Path(glslang).resolve())])
    if sdl:
        command.extend(["-SdlBuild", str(Path(sdl).resolve())])
    if rom:
        command.extend(["-RomPath", str(Path(rom).resolve())])
    environment = dict(os.environ)
    # Windows PowerShell 5 must not inherit PowerShell 7 module manifests via a Python parent.
    environment["PSModulePath"] = str(system / "System32/WindowsPowerShell/v1.0/Modules")
    environment["PATH"] = os.pathsep.join(
        [str(msys / "ucrt64/bin"), str(msys / "usr/bin"), str(compiler / "bin"), environment.get("PATH", "")])
    return command, environment, output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    for name in ("sdk", "compiler", "msys", "work"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--sdl", default="")
    parser.add_argument("--rom", default="")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--build-type", default="Release")
    parser.add_argument("--glslang", default=os.environ.get("XSDK_GLSLANG_OVERRIDE", ""))
    parser.add_argument("--restore-inputs", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    command, environment, output = recipe_plan(
        args.project, args.sdk, args.compiler, args.msys, args.work, args.sdl, args.rom,
        args.jobs, args.build_type, args.glslang, args.restore_inputs)
    print("Port recipe: " + str(Path(args.project) / "xsdk-project.json"), flush=True)
    print("Build type: " + args.build_type + "; console FPS are not guaranteed", flush=True)
    print("Output: " + str(output), flush=True)
    if args.build_type == "Debug":
        print("Debug builds are for debugging, not performance comparisons.", flush=True)
    if args.check_only:
        print("PASS: recipe and installed prerequisites; no build or download performed")
        return 0
    if os.name != "nt":
        raise ValueError("This build recipe runs on Windows")
    return subprocess.run(command, env=environment, check=False).returncode


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error
