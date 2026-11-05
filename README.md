<div align="center">
  <img src="assets/xsdk.png" alt="xSDK" width="640">
</div>

<p align="center">
  <a href="README.md"><img src="assets/languages/english.svg" alt="Read in English" width="140" height="36"></a>
  <a href="README-ES.md"><img src="assets/languages/espanol.svg" alt="Leer en español" width="140" height="36"></a>
  <a href="README-PT.md"><img src="assets/languages/portugues.svg" alt="Ler em português" width="140" height="36"></a>
</p>

# xSDK for Windows

**Build Xbox 360 homebrew from Windows. Manage your tools, compile shaders and turn compatible C/C++ projects into `.xex` titles with a desktop interface.**

This experimental Windows fork of [xenosworks/xsdk](https://github.com/xenosworks/xsdk) uses **MSYS2 UCRT64**. The interface supports **English, Spanish and Portuguese**. Use the **`main`** branch.

[Source code ZIP](https://github.com/ZenithUzu/xsdk/archive/refs/heads/main.zip) · [Windows manual — Spanish](README-WINDOWS.md) · [Port recipes — EN / ES / PT](README-PROJECTS.md) · [Original README](README-UPSTREAM.md) · [Build status](https://github.com/ZenithUzu/xsdk/actions)

## Download and quick start

**[Download xSDK Windows Portable v3.3.1 — ZIP](https://github.com/ZenithUzu/xsdk/releases/download/windows-portable-v3.3.1/xSDK-Windows-Portable-v3.3.1.zip)** · [Release notes and SHA-256](https://github.com/ZenithUzu/xsdk/releases/tag/windows-portable-v3.3.1)

1. Extract the **entire ZIP** into a writable folder. Keep `_internal/`, `sdk/` and the license files beside **xSDK-Windows.exe**. Open that EXE; no separate Python installation is required for the interface.
2. Install [MSYS2](https://www.msys2.org/) if missing and update it from UCRT64 with `pacman -Syu`. MSYS2 remains the external build environment, not a bundled compiler.
3. Choose your language and open **Sources and dependencies**. Use **Detect installed paths**, or choose an additional search folder. Review the results; valid saved selections are kept.
4. Set the GitHub source URLs, branches and local destinations for xSDK Windows, SDL3 Xenon and glslang. Defaults are provided. Use paths without spaces for xSDK, compiler and work.
5. Use **Prepare missing components**. It installs missing MSYS2 packages and builds missing components behind the interface, while reusing available tools. Commands and errors remain in the output panel. A fresh compiler build can take hours. Use the separate component buttons when you only need one step.
6. For CoopDX360, choose its repository root, your private US ROM, SDL3 build and a **NEW** game output folder under **Paths and project**. Keep Release and extra CMake options `[]`; use **Build and package game**. Private inputs still need preparation as documented by the port.
7. Copy the completed game folder to Xbox yourself with the game closed. Keep your existing saves when updating. The tool does not deploy or launch titles automatically.

Settings/logs stay in `data/`. Use **Update sources and rebuild** for explicit dependency updates; local changes are protected and existing compiler destinations are not rebuilt automatically. See [the dependency guide](README-DEPENDENCIES.md) and [portable instructions](README-PORTABLE.md).

**What the download contains:** the GUI/runtime, public SDK and application source, license notices, runtime hashes and validation/antivirus reports. **Not included:** MSYS2, a prebuilt PowerPC compiler, ROMs, private game assets or a ready-to-play game. The dependency panel can prepare the build tools after MSYS2 is installed.

The same app can now integrate original xSDK updates while retaining Windows changes; see [the upstream update workflow](README-DEPENDENCIES.md#actualizaciones-del-xsdk-original-desde-la-misma-herramienta). It also fixes cancellation and offers in-place dependency updates with backups.

## Features

- Detect and reuse installed tools instead of rebuilding the compiler for every project.
- Inspect GCC/G++, binutils, newlib, shader tools and SDK libraries from one window.
- Set custom paths for MSYS2, the PowerPC compiler, xSDK, glslang and SDL3 Xenon.
- Build compatible CMake projects, SDK examples and ports with `xsdk-project.json` recipes.
- Check recipe prerequisites before building; keep your ROM and assets as local private inputs.
- Choose Release, Debug, RelWithDebInfo or MinSizeRel and control parallel jobs.
- Switch between English, Spanish and Portuguese; keep your language and paths saved.
- Read live compiler logs, cancel tasks and open build outputs.
- Check for updates and update individual components. Optional startup update checks are read-only and off by default.
- Build portable tool packages with corresponding sources, licenses and SHA-256 checksums.

Opening the interface scans your tools. It does not automatically rebuild GCC, newlib or shaders. A detected version does not prove that a tool contains the required Xenon patches.

## Requirements

| Component | Purpose |
| --- | --- |
| 64-bit Windows 10/11 | Host system |
| Python 3.11+ with tkinter | Only for running the source interface; included in the portable EXE |
| MSYS2 UCRT64 | Host tools and build environment |
| xSDK PowerPC GCC/G++, binutils and newlib | Compile and link Xbox 360 code |
| glslang-xenon and built xSDK libraries | Shader compilation and runtime |
| Built SDL3 Xenon | Only for projects that use SDL3 |

The toolchain recipe uses GCC 15.3.0, binutils 2.47 and newlib 4.6.0.20260123 with the xSDK patches. Generic PowerPC GCC and desktop SDL are not replacements. This Windows workflow does not require Debian/WSL, VS2010 or Microsoft XDK.

## Portable EXE

The GUI can be packaged as a Windows EXE with Python/Tkinter included. It also prepares a private CoopDX game folder from your local source build and ROM. MSYS2, the compiler, built SDK and SDL3 remain external prerequisites. See [portable usage and build instructions](README-PORTABLE.md). [Sources / Fuentes / Fontes](README-DEPENDENCIES.md).

## Running from source (optional)

### Already have the tools?

1. Download `main` into a path without spaces, such as `C:\xsdk-windows`. Keep your existing compiler and work folders.
2. Open **Iniciar-Windows.cmd** and select **English** at the top.
3. Use **Detect / check**. Set missing paths under **Paths and project**.
4. If you updated the SDK runtime sources, use **Rebuild SDK only**, then rebuild your project.
5. Choose your project, select **Release** for performance comparisons and use **Build project**.

### Starting from scratch

1. Install [Python](https://www.python.org/downloads/windows/) with tkinter and the `py` launcher.
2. Install [MSYS2](https://www.msys2.org/), open **UCRT64** and run `pacman -Syu`. Restart the terminal and repeat if requested.
3. Download or clone this repository into a path without spaces. Open **Iniciar-Windows.cmd**.
4. Under **Installation and advanced tests**, run these stages one at a time: **Dependencies → Build compiler → Build shader tools → Build SDK → Samples**.
5. Wait for each stage to succeed before starting the next. Build SDL3 separately if your project needs it.

Compiler construction can take a long time; skip it if you already have compatible tools. [Instalar-Windows.ps1](Instalar-Windows.ps1) can prepare a Git checkout in a new directory; it does not install Python or MSYS2.

## Usage

| Field | Typical value |
| --- | --- |
| MSYS2 | `C:/msys64` |
| xSDK source | `C:/xsdk-windows` |
| Installed compiler root | `C:/xsdk-tools/compiler` |
| Work folder | `C:/xsdk-tools/work` |
| glslang executable | `C:/xsdk-tools/compiler/bin/glslang.exe` |
| SDL3_DIR | `C:/SDL-xenon/build-xsdk`, if needed |

For a **generic CMake project**, select the directory containing its compatible `CMakeLists.txt`. Start with Release, extra CMake options `[]` and four jobs.

For **CoopDX360**, select the **repository root** containing `xsdk-project.json`. Select the SDL3 Xenon build and optionally your private US ROM, use **Check port recipe**, then **Build project**. Inherited-input restoration is explicit and off by default; use it only with permission to use those inputs. Follow the [recipe guide](README-PROJECTS.md) for private-input preparation and details.

Recipe outputs go to `<work>/projects/<repository-name>/`. **Open results** opens that folder; generic projects and SDK examples use the SDK build directory. The CoopDX recipe generates a local `build-info.json` with configuration, source revision and output hashes. No console transfer or launch happens automatically.

## Build SDL3 Xenon

Build xSDK first. Open **MSYS2 UCRT64**, adjust the paths and clone into a new directory:

```bash
git clone --branch xenon https://github.com/xenosworks/SDL-xenon.git /c/SDL-xenon
cmake -S C:/SDL-xenon -B C:/SDL-xenon/build-xsdk -G Ninja -DCMAKE_TOOLCHAIN_FILE=C:/xsdk-windows/cmake/xsdk.cmake -DXSDK_TOOLCHAIN=C:/xsdk-tools/compiler -DCMAKE_BUILD_TYPE=Release
cmake --build C:/SDL-xenon/build-xsdk --parallel 4
```

After a successful build, set **SDL3_DIR** to `C:/SDL-xenon/build-xsdk`. It should contain `SDL3Config.cmake`. Use the Xbox-targeted SDL3 build, not desktop SDL3.

SDL-xenon provides audio, controllers, threads and timers. This adaptation does not supply an Xbox video/render driver; projects provide their graphics backend. Selecting SDL3_DIR does not add SDL calls to a project's source. See the [Windows guide](README-WINDOWS.md#sdl3-opcional) and [SDL-xenon documentation](https://github.com/xenosworks/SDL-xenon/blob/xenon/docs/README-xsdk.md).

## Upstream integration

This Windows fork integrates [upstream `5f6dc72`](https://github.com/xenosworks/xsdk/commit/5f6dc726f65f6d171493a3628c2415c03551f27b), including 26 commits after its original `8c58c7a` base. New POSIX support covers files, memory, clocks, pthreads and interface information. [Integration notes](docs/WINDOWS-UPSTREAM.md) distinguish compiled Windows checks from the original author's console results. The USB Ethernet milestone is a scope document, not a working adapter driver.

## Updates

| Changed component | Next step |
| --- | --- |
| Interface or documentation | Update source and reopen the interface |
| xSDK runtime/GPU source | Update, rebuild the SDK and rebuild affected projects |
| Project source | Rebuild that project |
| Shader compiler | Update/build shader tools and rebuild affected projects |
| GCC, binutils, newlib or their patches | Review and explicitly build a new compiler |

An unrecorded installation is not automatically outdated. Existing toolchain metadata and version checks have limits; the tool does not certify every compiler patch or SDK capability.

## Examples and validation

Examples include `hello`, `triangle`, `cube`, `sound`, `template` and `sdl3` when SDL-xenon is available. Deliberately broken `break` variants are expected to fail their checks.

On November 3, 2026, **26 local host tests passed**, including live language switching and Windows PowerShell 5/7 recipe compatibility. A fresh CoopDX output directory built shaders and game objects and produced a local XEX and build report. These results do not establish performance or correctness on a console.

Hardware behavior still needs separate testing. Startup/exit static remains pending validation, and a complete prebuilt tool package is not assumed available merely because its workflow exists. See [Actions](https://github.com/ZenithUzu/xsdk/actions), [hardware observations](docs/HARDWARE.md) and the [detailed Spanish status](README-ES.md#estado-y-límites). No FPS guarantee is made.

## Documentation and credits

- [Windows installation, SDL3, options and troubleshooting — Spanish](README-WINDOWS.md)
- [Port recipes — English / Español / Português](README-PROJECTS.md)
- [Original SDK README](README-UPSTREAM.md), [programming guide](docs/GUIDE.md) and [capabilities](docs/PARITY.md)
- [MIT license](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md)

**Original xSDK:** Mena / xenosworks and contributors. Original credits and notices, including Xenia and libxenon, are preserved. **Windows adaptation:** ZenithUzu, with OpenAI Codex assistance. GCC, binutils, newlib, glslang and MSYS2 retain their own licenses. This is not an official Microsoft or xenosworks release.

### Portable v3.3.1 repair fix

Cached compiler repair now restores the selected compiler in PATH for Newlib and recursive make processes. This fixes `powerpc-xsdk-elf-gcc: command not found` without deleting the SDK, compiler cache or game projects. After repair, `PASS: native tools, powerpc-xsdk-elf C/C++23 compilation and C++ headers` confirms the toolchain check succeeded; it does not validate the full game build.
