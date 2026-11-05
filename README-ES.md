<div align="center">
  <img src="assets/xsdk.png" alt="xSDK" width="640">
</div>

<p align="center">
  <a href="README.md"><img src="assets/languages/english.svg" alt="Read in English" width="140" height="36"></a>
  <a href="README-ES.md"><img src="assets/languages/espanol.svg" alt="Leer en español" width="140" height="36"></a>
  <a href="README-PT.md"><img src="assets/languages/portugues.svg" alt="Ler em português" width="140" height="36"></a>
</p>

# xSDK para Windows

Herramienta con interfaz en **inglés, español y portugués** para **detectar, administrar y reutilizar tus herramientas de xSDK** y
compilar proyectos `.xex` para Xbox 360 desde Windows, mediante MSYS2 UCRT64. La rama de uso es **`main`**.

Fork de [xenosworks/xsdk](https://github.com/xenosworks/xsdk), creado por **Mena / xenosworks y colaboradores**.
Se conservan el SDK original, su documentación, ejemplos, licencias y créditos. La base original es `8c58c7a`.

[Descargar main en ZIP](https://github.com/ZenithUzu/xsdk/archive/refs/heads/main.zip) ·
[Instalación y uso completos](README-WINDOWS.md) ·
[README original](README-UPSTREAM.md) ·
[Estado de las construcciones](https://github.com/ZenithUzu/xsdk/actions)

[Recetas de proyectos y guía EN / ES / PT](README-PROJECTS.md)

## Características

- Detecta instalaciones en las rutas guardadas, ubicaciones habituales, `XSDK_TOOLCHAIN` y PATH.
- Permite indicar manualmente las rutas de MSYS2, compilador, xSDK y un `glslang.exe` separado.
- Muestra las versiones de GCC/C++, binutils, newlib y glslang, y el estado de las dependencias y bibliotecas.
- Compila proyectos y ejemplos reutilizando las herramientas elegidas.
- Reconoce recetas `xsdk-project.json`: comprobación previa, ROM local opcional y construcción del port en Release.
- Guarda idioma y rutas; conserva los logs originales del compilador.
- Consulta actualizaciones del código del SDK y de glslang-xenon, sin instalarlas al consultar.
- Actualiza componentes por separado; una actualización del compilador se construye en una carpeta nueva.
- Ofrece Debug, Release, RelWithDebInfo, MinSizeRel, opciones CMake y SDL3_DIR opcional.
- Conserva el acceso a pruebas avanzadas del SDK, logs, cancelación y resultados de construcción.
- Incluye un instalador PowerShell y un generador de paquetes portables con fuentes, licencias y SHA-256.

**Al abrir, detecta y comprueba; no reconstruye GCC, newlib ni shaders.** La consulta de actualizaciones al abrir es opcional, viene desactivada y no instala cambios. No necesitas esperar un paquete precompilado para usar tus herramientas actuales.

## EXE portable

La interfaz se empaqueta como EXE con Python/Tkinter incluido y permite construir y preparar la carpeta privada de CoopDX para Xbox. MSYS2, compilador, SDK construido y SDL3 siguen siendo requisitos externos. Consulta [uso y construcción del portable](README-PORTABLE.md). [Sources / Fuentes / Fontes](README-DEPENDENCIES.md).

## Componentes necesarios

| Componente | Para qué sirve | Cuándo se necesita |
|---|---|---|
| Windows 10/11 de 64 bits | Sistema host del port | Para usar la interfaz de Windows |
| Python 3.11 o posterior con tkinter | Ejecuta la interfaz mediante `py`; el lanzador también admite Python UCRT64 en la ruta predeterminada | Siempre para la interfaz |
| MSYS2 UCRT64 | Entorno de construcción nativo de Windows | Para ejecutar las tareas de construcción |
| GCC/G++ `powerpc-xsdk-elf`, binutils y newlib de xSDK | Compilan C/C++ para Xbox 360 | Para construir SDK y proyectos |
| glslang-xenon para Windows | Prepara los shaders | Para proyectos o pruebas que compilan shaders |
| Código y bibliotecas de xSDK | Runtime y acceso al sistema/GPU de la consola | Para enlazar los proyectos |
| SDL-xenon | SDL3 adaptado a xSDK | Solo si el proyecto lo utiliza |

La receta incluida usa **GCC 15.3.0, binutils 2.47 y newlib 4.6.0.20260123**, con los parches originales de xSDK.
Un GCC PowerPC genérico o SDL para PC no sustituyen esas versiones adaptadas.
MSYS2 aporta Make, CMake, Ninja, Git, Python host y las dependencias para construir las herramientas.
No se requiere Debian/WSL, VS2010 ni el SDK de Microsoft.

## Uso con herramientas instaladas

1. Descarga `main` y extrae el código, por ejemplo en `C:\xsdk-windows`. Conserva `C:\xsdk-tools`.
2. Abre **Iniciar-Windows.cmd** y entra en **Mis herramientas**.
3. Pulsa **Detectar / comprobar**. Si falta una ruta, indícala en **Rutas y proyecto**.
4. Si acabas de actualizar el código de xSDK, pulsa **Reconstruir solo SDK**.
5. Selecciona la carpeta CMake de tu proyecto y pulsa **Compilar proyecto**.

Valores habituales:

| Campo | Ejemplo |
|---|---|
| MSYS2 | `C:/msys64` |
| Código de xSDK | `C:/xsdk-windows` |
| Compilador instalado, carpeta raíz | `C:/xsdk-tools/compiler` |
| Carpeta de trabajo | `C:/xsdk-tools/work` |
| glslang.exe instalado | `C:/xsdk-tools/compiler/bin/glslang.exe` |
| Proyecto CMake | Carpeta del proyecto que contiene `CMakeLists.txt` compatible con xSDK |
| SDL3_DIR | Vacío, o `C:/SDL-xenon/build-xsdk` si ya lo construiste y lo necesitas |

Para proyectos CMake genéricos, elige la carpeta con `CMakeLists.txt`. Para **CoopDX360**, elige la **raíz del repositorio** con `xsdk-project.json`; consulta [la guía de recetas](README-PROJECTS.md).
Usa **Release**, opciones **`[]`** y **4 trabajos** como punto de partida.

## Instalación desde cero

1. Instala [Python para Windows](https://www.python.org/downloads/windows/) con tkinter y el lanzador `py`.
2. Instala [MSYS2](https://www.msys2.org/) y actualízalo con `pacman -Syu` desde **UCRT64**.
   Si solicita reiniciar la terminal, hazlo y repite la actualización.
3. Descarga el código de `main` en una ruta sin espacios y abre **Iniciar-Windows.cmd**.
4. En **Instalación y pruebas avanzadas**, ejecuta en orden:
   **Dependencias → Construir compilador (lento) → Construir shaders → Construir SDK → Ejemplos**.
5. Espera a que cada etapa termine correctamente antes de continuar.

Esto construye las herramientas desde sus fuentes y puede tardar bastante. **Solo es necesario si no las tienes**.
El [instalador PowerShell](Instalar-Windows.ps1) también puede preparar una copia Git en una carpeta nueva;
no instala Python/MSYS2 ni convierte la interfaz en una aplicación autónoma con todo incluido.

## Integración del original

Este fork integra [upstream `5f6dc72`](https://github.com/xenosworks/xsdk/commit/5f6dc726f65f6d171493a3628c2415c03551f27b): 26 commits posteriores a la base `8c58c7a`, con nuevas funciones POSIX de archivos, memoria, tiempos, pthreads e información de interfaces. Las [notas de integración](docs/WINDOWS-UPSTREAM.md) separan la compilación en Windows de las pruebas de consola del autor original. El hito de USB Ethernet es un documento de alcance, todavía no un controlador funcional.

## Actualizaciones y mejoras

| Qué cambió | Acción habitual |
|---|---|
| Solo la interfaz o su documentación | Actualizar código y reiniciar la interfaz |
| Código del runtime/GPU de xSDK | Actualizar código, reconstruir solo SDK y recompilar el proyecto |
| Tu proyecto | Compilar proyecto |
| glslang-xenon | Actualizar/construir shaders y reconstruir los proyectos afectados |
| GCC, binutils, newlib o sus parches | Revisar y construir el compilador nuevo; es una tarea larga y explícita |

**“Sin registro” no significa “desactualizado”.** La interfaz no puede certificar los parches de instalaciones
anteriores que no tengan metadatos. Encontrar una versión tampoco certifica que toda la compilación funcione.

Las mejoras de este fork incluyen rutas y herramientas host para Windows, `libxsc.dll`, diagnósticos de bootstrap,
una interfaz que procesa los logs sin bloquearse y comprobaciones de primera presentación y cierre. Si falla una
espera de GPU o la restauración de pantalla, la presentación conserva sus buffers y registra el error.
**La estática reportada al arrancar y salir sigue pendiente de validación en la Xbox del usuario.**

## Construir SDL3 Xenon

SDL3 se construye aparte para PowerPC con xSDK; la versión SDL de Windows no sirve para enlazar el juego. Primero construye xSDK y luego ejecuta esto desde **MSYS2 UCRT64**, adaptando las rutas. El clon debe ir en una carpeta nueva:

```bash
git clone --branch xenon https://github.com/xenosworks/SDL-xenon.git /c/SDL-xenon
cmake -S C:/SDL-xenon -B C:/SDL-xenon/build-xsdk -G Ninja -DCMAKE_TOOLCHAIN_FILE=C:/xsdk-windows/cmake/xsdk.cmake -DXSDK_TOOLCHAIN=C:/xsdk-tools/compiler -DCMAKE_BUILD_TYPE=Release
cmake --build C:/SDL-xenon/build-xsdk --parallel 4
```

Cuando termine correctamente, pon `C:/SDL-xenon/build-xsdk` en **SDL3_DIR**. Debe contener `SDL3Config.cmake`; una carpeta vacía no basta. Consulta la [guía detallada de SDL3](README-WINDOWS.md#sdl3-opcional) para integración y errores.

La [adaptación SDL-xenon](https://github.com/xenosworks/SDL-xenon/tree/xenon) aporta audio, controles, hilos y temporizadores. No añade un renderizador propio de Xbox: el proyecto necesita su backend gráfico. Rellenar SDL3_DIR tampoco modifica automáticamente el código de un proyecto.

## Ejemplos y uso

Los ejemplos incluyen `hello`, `triangle`, `cube`, `sound`, `template` y, cuando está disponible SDL-xenon, `sdl3`.
**Abrir resultados** muestra `build` para ejemplos y proyectos genéricos, o `<trabajo>/projects/<repositorio>/` para recetas de ports. Construir un XEX no equivale a probarlo
correctamente en una consola. Las variantes `break` están rotas a propósito y deben fallar sus comprobaciones.

## Estado y límites

| Comprobación | Resultado registrado |
|---|---|
| Suite host local de la integración de Windows y recetas (3 de noviembre de 2026) | 26 pruebas aprobadas, incluido el cambio de idioma y la compatibilidad PowerShell 5/7 |
| Recuperación de pantalla con registros simulados en Linux | Pasó; no demuestra comportamiento de pantalla real |
| Apertura y disposición de la interfaz en un runner Windows | Pasó |
| Construcción y carga de `libxsc.dll` en Windows | Pasó, incluida resolución de un shader de prueba |
| Compilación del port con receta | Shaders y juego construidos en una carpeta de salida nueva; XEX y reporte local generados |
| SDL-xenon con las rutas del usuario | El usuario reportó compilación terminada sin errores; ejemplo SDL y consola pendientes |
| Paquete precompilado completo y estática en consola | Validación pendiente |

Consulta [Actions](https://github.com/ZenithUzu/xsdk/actions) para el estado actual. Los resultados anteriores son
registros de una revisión, no una promesa de que todas las funciones del SDK estén validadas en Windows.
El paquete precompilado es una vía opcional de instalación; no se da por disponible ni aprobado por existir su workflow.

## Documentación y créditos

- [Guía de Windows: componentes, instalación, SDL3, opciones y errores](README-WINDOWS.md)
- [Documentación original](README-UPSTREAM.md), [guía de programación](docs/GUIDE.md) y [funciones disponibles](docs/PARITY.md)
- [Resultados y observaciones de hardware](docs/HARDWARE.md)
- [Licencia MIT](LICENSE) y [avisos de terceros](THIRD_PARTY_NOTICES.md)

**xSDK original:** Mena / xenosworks y colaboradores. Se conservan sus créditos y los de Xenia, libxenon y demás
proyectos originales. **Adaptación de Windows:** ZenithUzu, con asistencia de OpenAI Codex.
GCC, binutils, newlib, glslang y MSYS2 conservan sus propias licencias. Este fork no es una publicación oficial
de xenosworks ni de Microsoft. Los resultados históricos del SDK original no validan automáticamente los cambios del fork.
