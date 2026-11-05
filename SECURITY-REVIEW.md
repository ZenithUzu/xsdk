# Windows portable security review — 2026-11-04

## Scope and findings

A source review covered the Windows GUI, discovery, process launching, source updates, build runner, project recipes, private game packaging, portable builder and PowerShell installer. No hidden persistence, credential collection, telemetry, antivirus exclusion, privilege escalation or backdoor was identified in those reviewed paths. This is a limited review, not a malware-free certification or a full reverse-engineering audit of Python, MSYS2, compiler binaries, all SDK console code or future upstream dependencies.

The reported CMD flashes were traced to local discovery commands launched without no-console flags: GCC/G++, binutils, glslang and Git version/status queries. Their output was captured, but Windows could still allocate a console. All subprocess calls in `tools/windows/` now use an explicit Windows no-console policy, including cancellation; stdout/stderr and errors remain available in the GUI/logs. No command output is hidden from the application log to disguise activity.

Optional startup updates now only query versions; they never fetch/merge/install source automatically. Local discovery runs without network commands. Manually selecting update/install/build can contact the documented repositories and download dependencies.

## Expected behavior

- Settings and logs are stored in `data/` beside a portable EXE, or the user's xSDK settings directory for source runs.
- Discovery executes the tools selected by the user with version or local Git queries. External executables must themselves be trusted; a version string cannot establish their integrity.
- User-selected build actions invoke MSYS2, compiler tools and project scripts. A project recipe is executable code from the selected repository; use reviewed sources.
- Update checks contact GitHub only when requested or enabled. Updates accept known component origins, reject dirty trees and use fast-forward merges. A ZIP SDK update is cloned to a new folder.
- Toolchain sources come from GNU/sourceware HTTPS URLs with pinned SHA256 checks. Shader sources and their dependencies use their own upstream Git/update mechanisms; those future dependencies are outside this review.
- Project scripts use process-scoped `RemoteSigned`, not `Bypass`; no global execution-policy setting is changed. Scripts marked as downloaded may require a trusted Git checkout or separate review by the user.
- Explicit dependency installation uses MSYS2/pacman. This is not performed merely by opening the GUI.
- Packaging copies private local inputs into a NEW game folder. No upload of ROM, assets or game packages is implemented.
- Windows Explorer is opened only through the output/log buttons. Cancellation terminates the active build process tree using the system taskkill executable.

## Distribution and verification

The default portable is a folder with `xSDK-Windows.exe`, visible `_internal/` dependencies, source, notices and hashes. It does not unpack its Python runtime into a temporary directory each time it starts. PyInstaller is a pinned build-only dependency; the source interface still uses standard-library Python. The executable is not Authenticode-signed, so Windows reputation prompts are still possible. Do not disable antivirus or add exclusions to run it.

`SHA256SUMS.txt` identifies the EXE and runtime dependencies. The ZIP checksum identifies the complete archive. These establish byte equality with the supplied files, not the identity or trustworthiness of a publisher. Local Microsoft Defender results, when available, apply to the specific tested files and signature set only. No files are uploaded to online scanning services by the tool or by this review.

## Regression checks

36 host tests passed, including captured output with Windows no-console flags, source coverage of subprocess launch options, read-only startup updates, three-language GUI switching, recipe validation and package safeguards. The custom-glslang argument was also moved to the generic CMake route so port recipes receive the shader override through their dedicated argument rather than a conflicting CMake extra option.

Frozen-runtime self-tests and the local discovery startup test accompany the distribution build. They do not validate console behavior, antivirus reputation on other computers, or absence of every possible supply-chain issue.

## Español

Se revisaron las rutas de ejecución de la herramienta de Windows y no se identificaron puertas traseras en ese alcance. Las ventanas CMD correspondían a consultas de herramientas sin las opciones de consola necesarias. La corrección conserva los logs visibles. El arranque no instala actualizaciones; las consultas de red son explícitas u opcionales. El análisis no certifica todo el software externo ni garantiza que otro antivirus no marque el EXE.

## Português

Foram revisados os caminhos de execução da ferramenta Windows e nenhuma backdoor foi identificada nesse escopo. As janelas CMD vinham das consultas às ferramentas sem opções de console. A correção preserva os logs visíveis. A inicialização não instala atualizações; consultas de rede são explícitas ou opcionais. A revisão não certifica todas as dependências nem garante a ausência de alertas em outros antivírus.


## Dependency panel extension

The dependency panel adds bounded filesystem discovery and explicit GitHub clone/build/update actions. Discovery skips network drives and linked directories, preserves valid choices and limits depth/count. It executes no shell commands. Version inspection still queries the selected local executables. GitHub URLs reject credentials, non-HTTPS origins, query/fragment, unsupported file/release links and invalid branch syntax; user values are passed as positional arguments. This limits argument injection and does not certify repository contents. Build actions intentionally execute code from user-selected sources.

A static MSYS2 bootstrap installs UCRT64 Python only if missing and only after a dependency action. The setup driver can install missing MSYS2 build packages through a fixed pacman command. No installer runs at application startup. Updates use origin/branch checks, dirty-tree rejection and fast-forward merges; ZIP sources are cloned into new locations. Existing compiler destinations are preserved. All Python subprocess launches retain the no-console policy and captured logs.

44 host tests passed after this extension. Real-laptop checks detected and reused existing components and configured/built SDL3 via CMake/Ninja, which reported no pending compilation. A fresh multi-hour compiler bootstrap was not repeated; it invokes the existing xSDK recipe. Frozen and antivirus results are specific to each portable artifact, not inherited from an earlier version.
