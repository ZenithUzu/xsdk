"""Arguments shared by the GUI and its tests; no commands run through cmd /c."""
import os
import re
from pathlib import Path

from options import BUILD_TYPES, MAKE_TARGETS, cmake_options

ACTIONS = ("diagnose", "dependencies", "toolchain", "shaders", "sdk", "samples", "project", "validate", "advanced", "update", "bundle")


def msys_path(value):
    value = str(value).replace("\\", "/")
    match = re.fullmatch(r"([A-Za-z]):/(.*)", value)
    if not match or any(c in value for c in "\n\r\x00"):
        raise ValueError("Elige una ruta local de Windows, por ejemplo C:/xsdk")
    return "/" + match[1].lower() + "/" + match[2]


def plan(msys, sdk, prefix, work, jobs, action, project="", build_type="Release", sdl="",
         cmake_args="[]", target="cmake_check", auto_update="0"):
    if build_type not in BUILD_TYPES:
        raise ValueError("Tipo de compilación desconocido")
    if target not in MAKE_TARGETS:
        raise ValueError("Prueba avanzada desconocida")
    extra = cmake_options(cmake_args)
    if action not in ACTIONS:
        raise ValueError("Acción desconocida")
    if not 1 <= int(jobs) <= 64:
        raise ValueError("Usa de 1 a 64 trabajos")
    for value in (sdk, prefix, work):
        if " " in str(value):
            raise ValueError("Usa rutas sin espacios para xSDK, compilador y trabajo")
    bash = Path(msys) / "usr/bin/bash.exe"
    script = msys_path(sdk) + "/tools/windows/run.sh"
    args = [str(bash), "--login", script, action, msys_path(sdk), msys_path(prefix),
            msys_path(work), str(int(jobs))]
    args.extend([msys_path(project) if project else "", build_type, msys_path(sdl) if sdl else "", target])
    args.extend(extra)
    if action == "project" and not project:
        raise ValueError("Elige un proyecto CMake")
    env = dict(os.environ, MSYSTEM="UCRT64", CHERE_INVOKING="1")
    return args, env
