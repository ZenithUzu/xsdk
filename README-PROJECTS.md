# xSDK project recipes / Recetas / Receitas

The Windows interface supports **English, Español and Português**. Select the language at the top; it is saved with your paths. Compiler and build-script output remains verbatim so diagnostics can be searched and shared.

## English

1. Open `Iniciar-Windows.cmd`. Select the installed MSYS2 UCRT64, xSDK source, PowerPC compiler and work folders. Build missing SDK components first; the project button reuses existing components.
2. Select the **port repository root** containing `xsdk-project.json`, not its `platform/xsdk` subfolder. Select the built **SDL3 Xenon** package in SDL3_DIR and optionally your private US ROM.
3. Keep **Release** selected for performance testing. Clear generic extra CMake options (`[]`): the port recipe owns its configuration.
4. Use **Check port recipe** to validate installed prerequisites without downloads or builds. This check does not validate ROM contents, private assets, tool ABI compatibility or console behavior.
5. Supply the port's private build inputs as explained by its documentation. The explicit restore checkbox runs the port's inherited-input helper only if you have permission to use those files; it is off by default.
6. Use **Build project**. Results are in `<work>/projects/<repository-name>/`, including the locally generated XEX and `build-info.json`. **Open results** opens that folder.

The port's source recipe prepares host tools, ROM assets, generated assets, specialized material shaders and the optimized CMake target. ROMs, assets and generated binaries are local inputs/outputs, not files supplied by xSDK. Microsoft XDK and VS2010 are not needed for this build route. No console transfer or game launch is automatic.

## Español

1. Abre `Iniciar-Windows.cmd`, elige **Español** y configura tus carpetas de MSYS2 UCRT64, xSDK, compilador PowerPC y trabajo. Construye primero los componentes que falten; compilar el proyecto reutiliza los existentes.
2. Elige la **raíz del repositorio del port**, donde está `xsdk-project.json`, el paquete compilado de **SDL3 Xenon** y, opcionalmente, tu ROM privada de EE. UU.
3. Usa **Release** para comparar rendimiento y deja las opciones CMake adicionales en `[]`.
4. Pulsa **Comprobar receta del port**: comprueba archivos de herramientas, sin compilar ni descargar. No valida la ROM, los assets privados, la compatibilidad ABI o el funcionamiento en consola.
5. Proporciona las entradas privadas indicadas por la documentación del port. Restaurar entradas heredadas es una opción explícita, desactivada al inicio, y solo corresponde si tienes permiso para usarlas.
6. Pulsa **Compilar proyecto**. El XEX local y `build-info.json` quedan en `<trabajo>/projects/<nombre-del-repositorio>/`. **Abrir resultados** abre esa carpeta.

La receta prepara las herramientas de assets, la extracción de tu ROM, los assets generados, los shaders especializados y el objetivo optimizado del juego. No incluye ROM, assets, XEX ni SDK de Microsoft. No copia ni ejecuta el juego en la consola.

## Português

1. Abra `Iniciar-Windows.cmd`, selecione **Português** e configure as pastas do MSYS2 UCRT64, xSDK, compilador PowerPC e trabalho. Compile os componentes ausentes primeiro; o projeto reutiliza os existentes.
2. Selecione a **raiz do repositório do port**, que contém `xsdk-project.json`, o pacote compilado do **SDL3 Xenon** e, opcionalmente, sua ROM privada dos EUA.
3. Use **Release** para comparar desempenho e mantenha as opções adicionais do CMake em `[]`.
4. Use **Verificar receita do port**: verifica as ferramentas sem compilar ou baixar. Não valida a ROM, os assets privados, a compatibilidade ABI ou a execução no console.
5. Forneça as entradas privadas descritas na documentação do port. A restauração de entradas herdadas é explícita e desativada por padrão; use apenas com permissão para esses arquivos.
6. Use **Compilar projeto**. O XEX local e `build-info.json` ficam em `<trabalho>/projects/<nome-do-repositório>/`. **Abrir resultados** abre essa pasta.

A receita prepara as ferramentas de assets, a extração da ROM, os assets gerados, os shaders especializados e o alvo otimizado do jogo. Não inclui ROM, assets, XEX ou SDK da Microsoft. Não transfere nem inicia o jogo automaticamente no console.

## Recipe contract

Schema 1 supports `kind: powershell-port`, an existing `build_script` inside the selected repository, and optional `requires_sdl3`. A recipe is executable project code: use repositories you trust. The runner calls the script with an argument list, without shell interpolation:

```text
-Game -XsdkRoot <sdk> -Toolchain <compiler> -MsysRoot <msys>
-OutDir <work>/projects/<name> -Jobs <1..64> -BuildType <configuration>
[-SdlBuild <SDL3>] [-RomPath <private-ROM>] [-Glslang <shader-compiler>]
[-RestoreInheritedInputs]
```

Only `-RestoreInheritedInputs` enables inherited-input restoration. The generic CMake workflow remains available for projects without a recipe. The preflight lists missing components instead of rebuilding the entire toolchain.

## Scope and validation

These changes improve the Windows workflow. They do not replace the xSDK kernel/GPU implementation. The CoopDX source owns its byte-order fixes, DMA-safe GPU memory, command-buffer synchronization, audio, USB input, presentation, networking and specialized shaders. Its recipe builds the current implementations together, instead of distributing an opaque reference XEX or applying binary patches.

Release avoids accidental Debug comparisons; it cannot guarantee 30/60 FPS. Measure the same map, camera, resolution, mods and game settings on hardware. `build-info.json` records build type, commit and output hashes; a successful build is not a console validation.

Host regression tests: `python -m unittest discover -s tests/windows -v`. Windows Tk smoke tests switch all three languages without starting a build. Actual console rendering, audio, USB and network compatibility require separate hardware tests.

The recipe runner also isolates Windows PowerShell 5 module lookup from PowerShell 7 inherited through Python. This prevents a completed build from failing at Get-FileHash when creating its report.
