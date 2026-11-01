"""Read-only discovery and component status; builds run only when explicitly selected."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def command(args, env=None):
    try:
        result = subprocess.run([str(arg) for arg in args], env=env, capture_output=True, text=True,
                                errors="replace", timeout=15)
        return result.stdout.strip() if result.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def discover(values):
    found = dict(values)
    roots = {
        "msys": [values.get("msys", ""), "C:/msys64"],
        "prefix": [values.get("prefix", ""), os.environ.get("XSDK_TOOLCHAIN", ""),
                   "C:/xsdk-tools/compiler", str(Path.home() / "xsdk-gcc-windows")],
    }
    compiler = shutil.which("powerpc-xsdk-elf-gcc.exe")
    if compiler:
        roots["prefix"].append(str(Path(compiler).parent.parent))
    bash = shutil.which("bash.exe")
    if bash and Path(bash).parent.name == "bin" and Path(bash).parent.parent.name == "usr":
        roots["msys"].append(str(Path(bash).parents[2]))
    for key, candidates in roots.items():
        suffix = "usr/bin/bash.exe" if key == "msys" else "bin/powerpc-xsdk-elf-gcc.exe"
        for root in candidates:
            if root and (Path(root) / suffix).is_file():
                found[key] = str(Path(root))
                break
    shaders = [values.get("glslang", ""), str(Path(found["prefix"]) / "bin/glslang.exe"),
               shutil.which("glslang.exe") or ""]
    for shader in shaders:
        if shader and Path(shader).is_file():
            found["glslang"] = str(Path(shader))
            break
    return found


def fingerprint(sdk, component):
    sdk = Path(sdk)
    if component == "toolchain":
        files = [sdk / "tools/toolchain/build.sh", *sorted((sdk / "tools/toolchain").glob("*.patch"))]
    elif component == "sdk":
        files = [sdk / "Makefile", *sorted((sdk / "src").rglob("*")), *sorted((sdk / "include").rglob("*"))]
    else:
        files = [sdk / "tools/windows/run.sh"]
    digest = hashlib.sha256()
    for path in files:
        if path.is_file():
            digest.update(path.relative_to(sdk).as_posix().encode())
            digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()


def load_state(work):
    try:
        data = json.loads((Path(work) / "components.json").read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def mark(sdk, prefix, work, component, source_work=""):
    work = Path(work)
    state = load_state(work)
    state[component] = {"recipe": fingerprint(sdk, component), "prefix": str(Path(prefix).resolve())}
    if source_work:
        state[component]["source_work"] = str(Path(source_work).resolve())
    if component == "shaders":
        state[component]["source"] = command(["git", "-C", work / "glslang", "rev-parse", "HEAD"])
    work.mkdir(parents=True, exist_ok=True)
    temporary = work / "components.json.tmp"
    temporary.write_text(json.dumps(state, indent=2), encoding="utf-8")
    temporary.replace(work / "components.json")


def inspect(values, online=False):
    values = discover(values)
    sdk, prefix, work, msys = (Path(values[key]) for key in ("sdk", "prefix", "work", "msys"))
    shader = Path(values.get("glslang") or prefix / "bin/glslang.exe")
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join([str(prefix / "bin"), str(msys / "ucrt64/bin"),
                                   str(msys / "usr/bin"), env.get("PATH", "")])
    state = load_state(work)
    rows = []

    def row(key, name, path, version, detail):
        rows.append({"key": key, "name": name, "path": str(path), "version": version or "—", "status": detail})

    gcc = prefix / "bin/powerpc-xsdk-elf-gcc.exe"
    version = command([gcc, "-dumpfullversion"], env) if gcc.is_file() else ""
    machine = command([gcc, "-dumpmachine"], env) if version else ""
    recipe = (sdk / "tools/toolchain/build.sh").read_text(encoding="utf-8") if (sdk / "tools/toolchain/build.sh").is_file() else ""
    expected = re.search(r"^GCC=gcc-(.+)$", recipe, re.M)
    compiler_state = "Falta o no se puede ejecutar"
    if version:
        compiler_state = "Disponible; parches sin registro (no se reconstruye automáticamente)"
        if machine != "powerpc-xsdk-elf":
            compiler_state = "Incompatible: target " + machine
        elif expected and version != expected[1]:
            compiler_state = "Versión distinta; receta pide " + expected[1]
        elif state.get("toolchain", {}).get("prefix") == str(prefix.resolve()):
            compiler_state = ("Receta registrada" if state["toolchain"].get("recipe") == fingerprint(sdk, "toolchain")
                              else "Receta cambió: revisar actualización (reconstrucción larga)")
    row("toolchain", "Compilador C/C++", prefix, version, compiler_state)
    cxx = prefix / "bin/powerpc-xsdk-elf-g++.exe"
    cxx_version = command([cxx, "-dumpfullversion"], env) if cxx.is_file() else ""
    row("cxx", "C++", cxx, cxx_version,
        "Disponible" if cxx_version else "Falta g++ o no se puede ejecutar; comprobar compilador")
    linker = prefix / "bin/powerpc-xsdk-elf-ld.exe"
    linker_version = command([linker, "--version"], env) if linker.is_file() else ""
    expected_binutils = re.search(r"^BINUTILS=binutils-(.+)$", recipe, re.M)
    binutils_status = "Disponible" if linker_version else "Falta o no se puede ejecutar"
    if linker_version and expected_binutils and not re.search(r"\b" + re.escape(expected_binutils[1]) + r"\b", linker_version):
        binutils_status = "Versión distinta; receta pide " + expected_binutils[1]
    row("binutils", "Binutils", linker, linker_version.splitlines()[0] if linker_version else "", binutils_status)
    header = prefix / "powerpc-xsdk-elf/include/_newlib_version.h"
    text = header.read_text(errors="replace") if header.is_file() else ""
    match = re.search(r'#define\s+_NEWLIB_VERSION\s+"([^"]+)"', text)
    newlib_status = "Incluida en el toolchain; no se reconstruye por compilar un proyecto" if match else "Versión sin identificar"
    expected_newlib = re.search(r"^NEWLIB=newlib-(\d+\.\d+\.\d+)", recipe, re.M)
    if match and expected_newlib and not match[1].startswith(expected_newlib[1]):
        newlib_status = "Versión distinta; receta pide " + expected_newlib[1]
    row("newlib", "newlib", header, match[1] if match else "", newlib_status)
    shader_version = command([shader, "--version"], env) if shader.is_file() else ""
    row("shaders", "Shaders / glslang", shader, shader_version.splitlines()[0] if shader_version else "",
        "Disponible; versión no demuestra que sea glslang-xenon" if shader_version else "Falta o no se puede ejecutar")
    library = sdk / "build/libxsdk.a"
    if not library.is_file() or not (sdk / "build/host/libxsc.dll").is_file():
        sdk_status = "Construir SDK (reutiliza compilador y shaders)"
    elif state.get("sdk", {}).get("recipe") == fingerprint(sdk, "sdk"):
        sdk_status = "Construcción registrada con este código"
    else:
        sdk_status = "Bibliotecas presentes; comprobar o reconstruir solo el SDK"
    row("sdk", "xSDK", sdk, command(["git", "-C", sdk, "rev-parse", "--short", "HEAD"], env), sdk_status)
    missing = [name for name in ("make.exe", "cmake.exe", "ninja.exe", "gcc.exe", "git.exe", "python3.exe")
               if not shutil.which(name, path=env["PATH"])]
    row("dependencies", "Dependencias MSYS2", msys, "UCRT64",
        "Faltan: " + ", ".join(missing) if missing else "Herramientas host encontradas; no se reinstalan")
    if online:
        git = shutil.which("git.exe", path=env["PATH"]) or "git"
        for key, repository, branch, local in (
            ("sdk", "https://github.com/ZenithUzu/xsdk.git", "main",
             command([git, "-C", sdk, "rev-parse", "HEAD"], env)),
            ("shaders", "https://github.com/xenosworks/glslang-xenon.git", "xenon",
             state.get("shaders", {}).get("source", "")),
        ):
            remote = command([git, "ls-remote", repository, "refs/heads/" + branch], env)
            for item in rows:
                if item["key"] == key:
                    item["status"] += (" · No se pudo consultar el remoto" if not remote else
                                       " · Remoto coincide" if local and remote.split()[0] == local else
                                       " · Remoto distinto: actualizar disponible" if local else
                                       " · Remoto consultado; instalación sin registro para comparar")
    return {"paths": values, "rows": rows}


if __name__ == "__main__":
    if len(sys.argv) in (6, 7) and sys.argv[1] == "mark":
        mark(*sys.argv[2:])
    else:
        raise SystemExit("usage: manager.py mark <sdk> <prefix> <work> <component>")
