# xSDK Windows Portable — EXE

## Español

Descomprime el ZIP completo en una carpeta con permiso de escritura y abre **xSDK-Windows.exe**. Conserva la carpeta `_internal/` junto al EXE: contiene las dependencias visibles y evita autoextraerlas a temporales al arrancar. La interfaz incluye su propio Python/Tkinter; no necesitas instalar Python para abrirla. Elige **Español** arriba. Las preferencias y logs se guardan en `data/`, junto al EXE. No se solicitan permisos de administrador.

**Portable no significa que el compilador venga incluido.** El paquete incluye la interfaz, sus fuentes, las fuentes públicas de xSDK y las licencias. Para construir XEX necesitas MSYS2 UCRT64, el compilador PowerPC, las bibliotecas construidas de xSDK y SDL3 Xenon, igual que con la versión fuente. Selecciona sus rutas en la interfaz. Si faltan bibliotecas del SDK, usa **Reconstruir solo SDK**. La [guía de Windows](https://github.com/ZenithUzu/xsdk/blob/main/README-WINDOWS.md) y los README de `sdk/` explican su preparación.

### Preparar CoopDX para Xbox

1. En **Rutas y proyecto**, selecciona la raíz del port con `xsdk-project.json`, tu ROM de EE. UU., SDL3 Xenon y una carpeta de trabajo. Conserva **Release** y opciones CMake `[]`.
2. Selecciona **Carpeta NUEVA del juego empaquetado**. El selector crea un nombre nuevo dentro de la carpeta elegida. No selecciones una carpeta con partidas existentes.
3. CoopDX para PC es opcional: si lo seleccionas, se tomarán sus carpetas `lang` y `palettes`; si faltan, se usan las del port. Deja desactivados los mods/packs en la primera prueba. Esos recursos no quedan certificados como compatibles por copiarlos.
4. Pulsa **Construir y empaquetar juego**. Construye las fuentes corregidas, prepara los assets y shaders y crea la carpeta del juego. También está **Empaquetar compilación existente**, que usa el XEX y `build-info.json` de `<trabajo>/projects/<repositorio>/`.
5. Con el juego cerrado, copia la carpeta generada al HDD/USB de la Xbox y abre `sm64coopdx.xex` desde Aurora. No hay transferencia ni lanzamiento automático.

El paquete local contiene el XEX, tu ROM, `lang/`, `palettes/`, carpetas para mods/DynOS, el reporte de construcción y `package-info.json` con hashes. La herramienta comprueba la ROM, la correspondencia entre XEX y reporte y los nombres FATX. No sobrescribe destinos existentes. Los errores dejan el log en `data/`; una cancelación durante la copia elimina la carpeta temporal.

No se fusionan ejecutables de PC ni el XEX de otro port. La herramienta compila los arreglos que ya están en las fuentes de CoopDX360. Los inputs privados heredados siguen requiriendo preparación según la documentación del port. La restauración es explícita y solo corresponde si puedes usar esos archivos. No se incluye ROM, assets ni juego empaquetado en este ZIP o en el repositorio. La carpeta del juego que generes es privada.

La creación del paquete no comprueba FPS, audio, gráficos, mods o conexión en Xbox. La guía de salida `PACKAGE-README.txt` lo recuerda; `hardware_validation` queda en `not-run`.

## English

Extract the whole ZIP into a writable folder and open **xSDK-Windows.exe**. Keep `_internal/` beside the EXE. This folder build includes Python/Tkinter and does not self-extract on startup. Select **English** at the top. Settings and logs stay in `data/` beside the EXE.

MSYS2 UCRT64, the PowerPC compiler, built xSDK libraries and SDL3 Xenon remain external build prerequisites. Public SDK source is included in `sdk/`; choose your installed tools or build the missing SDK component. See the Windows and project guides inside `sdk/`.

For CoopDX, select its repository root, your private US ROM, the SDL3 build, Release and a NEW package output folder. **Build and package game** compiles the corrected source and stages the local Xbox folder. **Package existing build** uses the XEX/report in `<work>/projects/<repository-name>/`. Optional PC files supply `lang` and `palettes`; mods and packs are opt-in and need their own compatibility checks. Existing outputs and saves are not overwritten. Copy the completed folder to the Xbox yourself with the game closed.

No ROM, game assets, desktop executable or reference XEX is bundled. Producing a folder does not validate console behavior or guarantee FPS.

## Português

Extraia o ZIP completo para uma pasta com permissão de escrita e abra **xSDK-Windows.exe**. Mantenha `_internal/` ao lado do EXE. A pasta inclui Python/Tkinter e não usa autoextração ao abrir. Selecione **Português** no topo. Configurações e logs ficam em `data/`, ao lado do EXE.

MSYS2 UCRT64, compilador PowerPC, bibliotecas compiladas do xSDK e SDL3 Xenon continuam como requisitos externos. As fontes públicas do SDK estão em `sdk/`; indique suas ferramentas ou compile o componente ausente. Consulte os guias dentro de `sdk/`.

Para CoopDX, selecione a raiz do repositório, sua ROM privada dos EUA, SDL3 compilado, Release e uma NOVA pasta de saída. **Compilar e empacotar jogo** compila as fontes corrigidas e prepara a pasta local para Xbox. **Empacotar compilação existente** usa o XEX e relatório em `<trabalho>/projects/<nome-do-repositório>/`. Os arquivos opcionais de PC fornecem `lang` e `palettes`; mods e packs são opcionais e exigem testes próprios. Pastas existentes e saves não são sobrescritos. Copie o resultado para o Xbox com o jogo fechado.

Não há ROM, assets do jogo, executável de desktop ou XEX de referência neste pacote. Gerar a pasta não comprova funcionamento no console nem garante FPS.

## Build this EXE from source

Build-only dependency: the pinned PyInstaller version in `tools/windows/requirements-exe.txt`. Use Windows CPython with tkinter. PyInstaller freezes the GUI; no third-party Python package is required when running the source interface.

```powershell
python -m venv build/exe-env
.\build\exe-env\Scripts\python.exe -m pip install -r tools/windows/requirements-exe.txt
.\build\exe-env\Scripts\python.exe tools/windows/build_exe.py --output C:/build/xSDK-Windows-Portable
```

Choose a new output directory. The builder packages Git-indexed source files only, plus the GUI executable and runtime license notices. No local SDK binaries, game inputs or saved preferences are copied. Review staged sources before building. Use `xSDK-Windows.exe --self-test C:/build/portable-smoke.json` to run a hidden Tk/language smoke test of the frozen runtime.

Keep `LICENSE`, `THIRD_PARTY_NOTICES.md`, `licenses/` and `sdk/` with the portable distribution. The executable uses a PyInstaller bootloader; its license and distribution exception are included. The tool's original credits remain in the source and the Credits dialog.


## Console windows and security review

Native subprocesses use `CREATE_NO_WINDOW` and hidden startup-window settings on Windows. The output is still captured in the visible UI/logs. Startup detection queries local tools; optional startup update checks are read-only and never install updates. Install/build actions require selecting their button.

The default builder uses a folder layout (`--onedir`), so dependencies remain visible in `_internal/`. A single self-extracting EXE remains an explicit build option with `--onefile`. Preserve the whole portable folder. Hashes for the EXE and its runtime dependencies are in `SHA256SUMS.txt`; a ZIP checksum is supplied alongside the downloadable archive.

See [the source-review scope](SECURITY-REVIEW.md). Local antivirus results apply only to the tested artifact and definitions; neither a scan nor a hash guarantees absence of malware. This build is not Authenticode-signed. No antivirus exclusions, protection changes or administrator startup are requested.


## Fuentes, enlaces y preparación

La nueva pestaña **Fuentes y dependencias / Sources and dependencies / Fontes e dependências** permite detectar rutas, configurar URLs GitHub y construir o actualizar dependencias desde la interfaz. Consulta [la guía EN/ES/PT](README-DEPENDENCIES.md). MSYS2 es el requisito inicial; sus comandos trabajan por detrás con salida visible.
