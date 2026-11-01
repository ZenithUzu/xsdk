"""Build choices accepted by both the Windows interface and its runner."""
import json

BUILD_TYPES = ("Debug", "Release", "RelWithDebInfo", "MinSizeRel")
MAKE_TARGETS = (
    "cmake_check", "sample_breaks", "cmake_check_break", "cpu_probes", "xam_probes",
    "launch_probes", "store_probes", "system_probes", "drive_probes", "hiz_pass_probes",
    "msaa_probes", "skin_probe", "occlusion_tries", "tiles_probe", "loop_break_probes",
    "instancing_probes", "m55_flush_check", "m55_heap_check", "store_catalogue_check",
)


def cmake_options(value):
    try:
        args = json.loads(value or "[]")
    except ValueError as error:
        raise ValueError('Opciones CMake: usa una lista JSON, por ejemplo ["-DFEATURE=ON"]') from error
    if not isinstance(args, list) or any(not isinstance(arg, str) for arg in args):
        raise ValueError("Las opciones CMake deben ser una lista de textos")
    reserved = ("CMAKE_TOOLCHAIN_FILE", "CMAKE_BUILD_TYPE", "XSDK_TOOLCHAIN", "SDL3_DIR")
    for arg in args:
        if not arg.startswith("-D") or "=" not in arg or any(c in arg for c in "\n\r\x00"):
            raise ValueError("Solo se aceptan opciones -DNOMBRE=valor")
        name = arg[2:].split("=", 1)[0].split(":", 1)[0]
        if not name or name in reserved:
            raise ValueError("Usa los campos de la interfaz para las rutas y el tipo de compilación")
    return args
