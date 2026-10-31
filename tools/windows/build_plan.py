"""Arguments shared by the GUI and its tests; no commands run through cmd /c."""
import os
import re
from pathlib import Path

ACTIONS = ("diagnose", "dependencies", "toolchain", "shaders", "sdk", "samples", "project")


def msys_path(value):
    value = str(value).replace("\\", "/")
    match = re.fullmatch(r"([A-Za-z]):/(.*)", value)
    if not match or any(c in value for c in "\n\r\x00"):
        raise ValueError("Elige una ruta local de Windows, por ejemplo C:/xsdk")
    return "/" + match[1].lower() + "/" + match[2]


def plan(msys, sdk, prefix, work, jobs, action, project=""):
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
    if action == "project":
        args.append(msys_path(project))
    env = dict(os.environ, MSYSTEM="UCRT64", CHERE_INVOKING="1")
    return args, env
