# Windows fork: upstream integration

## Revision

Integrated xenosworks/xsdk main through [`5f6dc726f65f6d171493a3628c2415c03551f27b`](https://github.com/xenosworks/xsdk/commit/5f6dc726f65f6d171493a3628c2415c03551f27b), 26 commits after the fork's `8c58c7a` base. The merge retains upstream history, the Windows native host DLL, compiler orchestration, GUI, three-language READMEs and port recipes. No compiler bootstrap or glslang source update is required by this upstream range.

## Changes available to titles

- Files and paths: `access`, `rmdir`, `utime`, `utimes`, `chmod`, `fchmod`, `realpath`, `sync`, file identities in `stat`, and POSIX-style `fnmatch`.
- Memory: `posix_memalign`, `getpagesize`, `msync`, `mlock` and `munlock`, with upstream's documented semantics and limitations.
- Time and threads: `clock_getres`, `sleep`, `pthread_exit`, attribute getters and condition-variable clock handling.
- System and network information: `_SC_OPEN_MAX`, `uname`, `getifaddrs` and `freeifaddrs`.
- Tests: milestone 70 checks, deliberately broken variants and the original author's console logs.

FATX does not preserve all POSIX metadata. Upstream's console run showed read-only attributes being discarded, so chmod reads back the result and reports `EPERM` where the requested permission cannot be kept. Timestamp tests account for the observed two-second rounding. See [hardware evidence](HARDWARE.md#fatx-keeps-no-read-only-attribute-milestone-70-2026-10-31) and [capabilities](PARITY.md).

Mono-xenon is listed among external ported libraries; it is not bundled or installed by this Windows GUI. Milestone 69's USB Ethernet document describes planned work, not a working driver added by this merge. No GPU optimization or FPS improvement is claimed for this update.

## Existing ports

The updated SDK now supplies a strong `rmdir`. A port defining its own strong fallback can fail at link time with a duplicate symbol. CoopDX360's fallback is weak so the new SDK implementation wins, while older SDKs can still use the fallback. Both combinations were linked on Windows; the code was not executed on a console during this integration.

After changing SDK headers or libraries, rebuild dependent projects. Rebuild SDL3 as well if changes affect the interfaces it uses. Keep ABI-compatible SDK, compiler and library builds together.

## Windows validation

- Native Windows cross-build: `make -j4 TOOLCHAIN=<compiler>/bin/powerpc-xsdk-elf- PYTHON=python3 HOST_CC=gcc` completed, producing `libxsdk.a`, the test titles and `libxsc.dll`.
- All 26 Windows host tests passed.
- `tools/windows/check_xsc.py` loaded the new host DLL and resolved its shader fixture.
- The CoopDX POSIX compatibility probe linked with both the old and new SDK; symbol inspection selected the new SDK's strong `rmdir` and the old SDK fallback respectively.

The original console results are upstream evidence, not a new hardware run of this Windows build. There was no console deployment or new measurement of audio, graphics, networking or performance.

## Español

Se incorporaron las mejoras del original conservando la interfaz EN/ES/PT y las recetas de Windows. Para usarlas hay que reconstruir el SDK y los proyectos dependientes. Las pruebas anteriores validan la construcción y el enlace en Windows; no sustituyen una prueba en Xbox. El adaptador USB Ethernet sigue siendo trabajo planificado y Mono es una biblioteca externa.

## Português

As melhorias do upstream foram incorporadas preservando a interface EN/ES/PT e as receitas do Windows. Recompile o SDK e os projetos dependentes. Os testes acima validam compilação e linkedição no Windows, não a execução no Xbox. O adaptador USB Ethernet continua como trabalho planejado; Mono é uma biblioteca externa.
