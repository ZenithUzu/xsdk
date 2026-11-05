> **Portable v3.3.1:** [descarga el ZIP del Release](https://github.com/ZenithUzu/xsdk/releases/download/windows-portable-v3.3.1/xSDK-Windows-Portable-v3.3.1.zip) y abre `xSDK-Windows.exe` tras extraerlo completo. No necesitas Python externo para la interfaz. Usa **Fuentes y dependencias** para detectar, descargar y construir herramientas. [Guía del portable](README-PORTABLE.md) · [Guía de enlaces y dependencias](README-DEPENDENCIES.md).

# Guía de xSDK para Windows

La rama mantenida de este fork es [main](https://github.com/ZenithUzu/xsdk/tree/main).
La interfaz administra instalaciones existentes y permite construir proyectos con xSDK en Windows mediante MSYS2 UCRT64.
No requiere WSL/Debian ni el XDK de Microsoft. Tampoco es un complemento que amplíe el compilador de VS2010.

[Características, componentes y estado](README.md) · [Documentación original](README-UPSTREAM.md)

## Requisitos y componentes

| Componente | Instalación o función |
|---|---|
| Windows 10/11 de 64 bits | Host del port |
| Python 3.11+ con tkinter y lanzador `py` | Interfaz y scripts; [descarga oficial](https://www.python.org/downloads/windows/) |
| MSYS2 UCRT64 | Shell y herramientas host; [descarga oficial](https://www.msys2.org/) |
| Toolchain xSDK para Windows | `powerpc-xsdk-elf-gcc.exe`, `g++.exe`, binutils y newlib adaptados |
| glslang-xenon para Windows | Shaders GLSL/HLSL para el flujo de xSDK |
| Código de xSDK y sus bibliotecas construidas | `build/libxsdk.a` y `build/host/libxsc.dll` |
| SDL-xenon, opcional | SDL3 compilado para xSDK; no es SDL3 para PC |

La receta del repositorio fija GCC 15.3.0, binutils 2.47 y newlib 4.6.0.20260123, con sus hashes y parches.
La versión de glslang por sí sola no identifica la variante xenon: Khronos puede reportar la misma versión.
La consola necesita poder ejecutar los XEX homebrew; los comandos de esta guía solo construyen archivos.

**Dependencias** instala los siguientes paquetes de MSYS2; no ejecuta una actualización completa del sistema:

```text
base-devel texinfo git curl patch tar xz
mingw-w64-ucrt-x86_64-gcc
mingw-w64-ucrt-x86_64-gmp
mingw-w64-ucrt-x86_64-mpfr
mingw-w64-ucrt-x86_64-mpc
mingw-w64-ucrt-x86_64-python
mingw-w64-ucrt-x86_64-cmake
mingw-w64-ucrt-x86_64-ninja
```

El Python de Windows abre la interfaz; el Python de UCRT64 ejecuta las tareas dentro de MSYS2.
Necesitas conexión para descargar fuentes, dependencias y consultar actualizaciones. El primer bootstrap puede tardar
bastante y ocupar espacio amplio. No se han fijado tiempos ni tamaños garantizados para todos los equipos.

## Si ya tienes las herramientas

1. Cierra la interfaz antes de reemplazar su código.
2. Descarga [main en ZIP](https://github.com/ZenithUzu/xsdk/archive/refs/heads/main.zip) y extrae el código en una ruta
   sin espacios, por ejemplo `C:\xsdk-windows`. Conserva tus carpetas de compilador y trabajo.
3. Abre `Iniciar-Windows.cmd` y pulsa **Detectar / comprobar** en **Mis herramientas**.
4. En **Rutas y proyecto**, corrige cualquier ruta que no corresponda a tu instalación.
5. Si cambió el código de las bibliotecas de xSDK, pulsa **Reconstruir solo SDK**.
6. Selecciona el proyecto compatible con xSDK y pulsa **Compilar proyecto**.

No repitas Dependencias, Compilador o Shaders cuando ya funcionan y no necesitas actualizarlos.
La detección busca en rutas guardadas, ubicaciones habituales, `XSDK_TOOLCHAIN` y PATH; no recorre todo el disco.
Las rutas guardadas tienen prioridad si contienen las herramientas. Consultar el estado no descarga ni construye.

## Instalación desde cero

### Preparar Python y MSYS2

Instala Python con tkinter y el lanzador `py`. Desde PowerShell puedes comprobarlo:

```powershell
py -3 --version
py -3 -m tkinter
```

El segundo comando debe abrir una ventana que puedes cerrar. Instala MSYS2, por ejemplo en `C:\msys64`.
Abre **MSYS2 UCRT64** y actualiza:

```bash
pacman -Syu
```

Si MSYS2 pide cerrar/reabrir la terminal, hazlo y vuelve a ejecutar la actualización antes de continuar.

### Obtener el código

Descarga el ZIP de `main` o, con Git instalado, clona:

```bash
git clone --branch main https://github.com/ZenithUzu/xsdk.git /c/xsdk-windows
```

No clones encima de una carpeta existente. El ZIP permite usar la herramienta; una copia Git facilita las actualizaciones.

### Construir lo que falta

Abre `Iniciar-Windows.cmd`, revisa las rutas y entra en **Instalación y pruebas avanzadas**.
Ejecuta las etapas necesarias en este orden y espera a que termine cada una:

| Etapa | Resultado |
|---|---|
| Dependencias | Paquetes de construcción dentro de MSYS2 |
| Construir compilador (lento) | GCC/G++, binutils y newlib con host Windows y target `powerpc-xsdk-elf` |
| Construir shaders | glslang-xenon, normalmente en `compiler/bin/glslang.exe` |
| Construir SDK | `libxsdk.a`, `libxsc.dll` y títulos de prueba |
| Ejemplos | XEX de los ejemplos; SDL3 se omite si no está disponible |

Un error detiene su etapa. No pulses otra vez Compilador si sigue ejecutándose; consulta los logs.
No cambies o borres las fuentes y carpetas de trabajo durante una construcción.

## Rutas y proyecto

| Campo | Ejemplo | Qué selecciona |
|---|---|---|
| MSYS2 | `C:/msys64` | Instalación con `usr/bin/bash.exe` y entorno UCRT64 |
| Código de xSDK | `C:/xsdk-windows` | Código, Makefile y `cmake/xsdk.cmake` del fork |
| Compilador instalado | `C:/xsdk-tools/compiler` | Carpeta raíz; no selecciones `bin` ni el ejecutable |
| Carpeta de trabajo | `C:/xsdk-tools/work` | Fuentes, logs, metadatos y trabajo de bootstrap |
| glslang.exe | `C:/xsdk-tools/compiler/bin/glslang.exe` | Ejecutable existente; puede estar separado del compilador |
| Proyecto CMake | `<tu-proyecto>/platform/xsdk` para xDS360 | Carpeta con el `CMakeLists.txt` de ese port |
| SDL3_DIR | Vacío o `C:/SDL-xenon/build-xsdk` | Construcción opcional de SDL-xenon |

Las rutas de SDK, compilador y trabajo no admiten espacios, por las limitaciones del bootstrap/Makefile.
Los proyectos y sus argumentos se pasan por separado, sin convertirlos en una orden de shell.
Un proyecto XDK/VS2010 no se convierte automáticamente en proyecto xSDK.

## Opciones de la interfaz

### Mis herramientas

La tabla muestra GCC/C++, binutils, newlib, glslang, bibliotecas de xSDK y dependencias host.
Los comandos de versión tienen tiempo límite y se ejecutan fuera del hilo de la interfaz.

- **Detectar / comprobar:** consulta rutas y versiones locales. No instala ni compila.
- **Buscar actualizaciones:** consulta commits remotos de xSDK y glslang-xenon y compara versiones locales del
  toolchain con la receta incluida. No instala nada. Un commit distinto puede ser un fork personalizado, no necesariamente más antiguo.
- **Instalar / actualizar seleccionado:** actúa sobre la fila elegida.
- **Reconstruir solo SDK:** usa tu toolchain existente para reconstruir bibliotecas y títulos del SDK.
- **Compilar proyecto:** configura y construye el proyecto elegido con las herramientas actuales.

Estados que requieren interpretación:

| Mensaje | Significado |
|---|---|
| Disponible | Se encontró el componente; no certifica todas sus funciones |
| Sin registro / parches sin registro | La instalación no tiene metadatos suficientes para comparar sus parches |
| Versión distinta | No coincide con la receta del código local; revisar antes de decidir reconstruir |
| Receta cambió | Cambió el registro comparado; revisar si necesitas actualizar |
| Bibliotecas presentes; comprobar o reconstruir solo SDK | Hay archivos, pero su correspondencia con el código no está registrada |
| Remoto sin registro para comparar | No se puede afirmar si el binario instalado corresponde al commit remoto |

Los registros se guardan en `work/components.json` tras construcciones exitosas. **No tener registro no obliga a
reconstruir** una instalación que ya funciona. Las dependencias host se comprueban por presencia; no se garantiza
que todos los paquetes de MSYS2 sean los más recientes.

### Configuración de proyectos y ejemplos

| Configuración CMake | Uso |
|---|---|
| Release | Optimización para uso habitual y rendimiento |
| Debug | Diagnóstico; puede ser más lento |
| RelWithDebInfo | Optimización e información de depuración |
| MinSizeRel | Prioriza tamaño |

Estas opciones se aplican a proyectos y ejemplos CMake. La construcción del SDK mediante Make conserva sus flags originales.
**Trabajos simultáneos** limita las tareas de compilación, no cambia los FPS del título. Cuatro es un punto de partida.

**Opciones CMake** recibe una lista JSON de definiciones del proyecto:

```json
["-DFEATURE=ON", "-DNAME=mi proyecto"]
```

`FEATURE` y `NAME` son ejemplos, no opciones que todos los proyectos tengan. Usa `[]` si no necesitas ninguna.
Las rutas del toolchain, tipo de compilación, glslang y SDL3_DIR tienen sus campos propios y no se reemplazan desde esta lista.

## Actualizar sin reconstruir todo

| Componente seleccionado | Acción |
|---|---|
| GCC/C++, binutils o newlib | Ofrece reconstrucción larga en una carpeta NUEVA; conserva el compilador anterior y usa trabajo nuevo |
| Shaders | Actualiza el checkout xenon limpio, si existe, y reconstruye solo glslang |
| xSDK en copia Git | Actualiza por avance directo si la copia está limpia y corresponde al fork |
| xSDK en copia ZIP | Clona una copia Git nueva en `work/sdk-updates`; conserva la carpeta original y cambia la ruta seleccionada |
| Dependencias | Instala paquetes host necesarios, sin reconstruir el compilador PowerPC |

Después de actualizar código, abre la interfaz de la carpeta actualizada. Si cambió el runtime/GPU, reconstruye solo
SDK y tu proyecto. No reconstruyas GCC/newlib por un cambio de README o de interfaz.
La casilla de actualización al abrir es opcional y viene apagada; actualiza código, no todo el toolchain.
El actualizador Git se detiene ante cambios locales o archivos sin seguimiento. No los descarta.

## SDL3 opcional

[SDL-xenon, rama xenon](https://github.com/xenosworks/SDL-xenon/tree/xenon) es SDL3 adaptado a xSDK.
La [guía del proyecto original](https://github.com/xenosworks/SDL-xenon/blob/xenon/docs/README-xsdk.md)
es la referencia de su backend. Proporciona audio, hasta cuatro controles, hilos, temporizadores y rutas.
Esta adaptación no incluye un driver de vídeo/render/GPU propio: los títulos dibujan con xSDK o vulkan4xenon.

Primero construye xSDK. Desde **MSYS2 UCRT64**, descarga SDL-xenon en una carpeta nueva:

```bash
git clone --branch xenon https://github.com/xenosworks/SDL-xenon.git /c/SDL-xenon
```

Configura y construye con tus rutas. Los comandos se muestran en una sola línea para facilitar el pegado:

```bash
cmake -S C:/SDL-xenon -B C:/SDL-xenon/build-xsdk -G Ninja -DCMAKE_TOOLCHAIN_FILE=C:/xsdk-windows/cmake/xsdk.cmake -DXSDK_TOOLCHAIN=C:/xsdk-tools/compiler -DCMAKE_BUILD_TYPE=Release
```

```bash
cmake --build C:/SDL-xenon/build-xsdk --parallel 4
```

Si termina sin errores y vuelve el prompt, coloca `C:/SDL-xenon/build-xsdk` en **SDL3_DIR** y pulsa **Ejemplos**.
La biblioteca debe estar construida para xSDK, no para Windows. La presencia de la carpeta por sí sola no demuestra
una construcción correcta. El usuario reportó que estos comandos terminaron sin errores en su equipo;
la integración del ejemplo y su funcionamiento en consola aún requieren comprobación.

Con SDL3 disponible, se espera `build/samples/sdl3/sdl3.xex`. Rellenar el campo no modifica el código de xDS360
ni incorpora SDL3 a proyectos que no lo usan. Sin SDL3, puedes compilar los demás ejemplos y proyectos compatibles.

## Ejemplos y pruebas avanzadas

| Ejemplo | Propósito |
|---|---|
| hello | Inicio y funciones básicas |
| triangle / cube | Dibujo y gráficos |
| sound | Audio |
| template | Punto de partida para otro proyecto |
| sdl3 | Integración de SDL-xenon cuando está disponible |

**Verificar herramientas** comprueba binarios Windows y target, compila una unidad C++23 con encabezados de la
biblioteca estándar, construye `cmake_check` y carga `libxsc.dll` con un shader de prueba. No ejecuta los XEX.

En **Prueba avanzada** puedes seleccionar objetivos originales: `cmake_check`, pruebas de CPU, XAM, lanzamientos,
archivos, sistema, MSAA, HiZ, instancing y otros. **Construir prueba avanzada** genera los títulos o ejecuta la
comprobación host que ese objetivo defina. Algunas pruebas requieren otros elementos de hardware o red;
consulta su fuente y la documentación original antes de interpretarlas.
Las variantes `sample_breaks` y `cmake_check_break` están rotas a propósito para probar que sus comprobaciones fallan.
Un build terminado no equivale a una prueba de consola aprobada.

## Resultados y registros

| Archivo o carpeta | Contenido |
|---|---|
| `build/libxsdk.a` | Biblioteca de xSDK para títulos |
| `build/host/libxsc.dll` | Compilador host de shaders de xSDK |
| `build/xsdk_test.xex` | Título de comprobaciones del SDK |
| `build/samples/<ejemplo>/<ejemplo>.xex` | Ejemplos construidos |
| `<proyecto>/build-xsdk-windows` | Resultado del proyecto seleccionado |
| `%LOCALAPPDATA%\xsdk-windows` | Preferencias y logs de la interfaz |
| `<trabajo>/toolchain/logs` | Logs del bootstrap inicial |
| `<trabajo>/toolchain-updates/<fecha>/logs` | Logs de reconstrucciones nuevas del compilador |
| `<trabajo>/components.json` | Recetas registradas por componente |

**Abrir resultados** abre todo `build` del SDK. **Abrir logs** abre los logs iniciales de toolchain cuando existen;
los de la interfaz permanecen en `%LOCALAPPDATA%\xsdk-windows`. Los errores del bootstrap muestran el archivo
activo y sus últimas 40 líneas. La falta de nuevas líneas en la ventana no significa que el bootstrap haya terminado.

## Errores comunes

- **Aparece `^[[200~` antes del comando:** se pegaron secuencias de terminal. Pulsa Ctrl+C, escribe `cmake ` a mano
  y pega el resto, sin `~` al final. No es un error de SDL ni del compilador.
- **`makeinfo` no encontrado:** instala `texinfo` desde UCRT64; después reintenta la etapa fallida.
- **Falta un compilador o se detecta un ELF de Linux:** selecciona las herramientas `.exe` para Windows de xSDK.
- **Falta libxsdk/libxsc:** construye solo el SDK antes de proyectos o ejemplos.
- **SDL3 no encontrado:** comprueba SDL3_DIR y que contenga `SDL3Config.cmake` de una construcción para xSDK.
- **El actualizador detecta cambios locales:** conserva o resuelve esos cambios antes de actualizar; no borres tu trabajo.
- **Apareció una carpeta, pero no sabes si terminó:** espera al prompt y revisa que no haya `FAILED` o errores.

## Instalador y paquete portable

`Instalar-Windows.ps1` prepara una copia Git en una carpeta nueva. Requiere MSYS2 con Git y no instala Python/MSYS2:

```powershell
powershell -File .\Instalar-Windows.ps1 -Destination C:\xsdk-instalado
```

**Crear paquete portable** requiere una copia Git del SDK, herramientas nativas construidas y las fuentes
correspondientes en la carpeta de trabajo. Genera `xsdk-windows-portable.zip` y `.zip.sha256` allí.
Incluye el compilador, glslang, código del SDK, fuentes y avisos. Sigue necesitando MSYS2 UCRT64 para el entorno host.

Si ya tienes un paquete y su checksum de una fuente que conoces, puedes instalar su compilador en una carpeta nueva:

```powershell
powershell -File .\Instalar-Windows.ps1 -Destination C:\xsdk-instalado -Compiler C:\xsdk-tools\compiler-nuevo -Bundle C:\descargas\xsdk-windows-portable.zip
```

El instalador verifica el checksum y no reemplaza carpetas existentes. Después configura esa ruta y construye SDK/proyectos.
No se anuncia un instalador autónomo que incluya Python y MSYS2.

El flujo de [GitHub Actions](https://github.com/ZenithUzu/xsdk/actions) permite solicitar `build_native` manualmente;
también admite un commit de `main` marcado con `[native-bundle]`. Construye toolchain, shaders, SDK, ejemplos y
comprobaciones antes de subir ZIP y checksum como artefactos. El precompilado no es necesario para usar herramientas
ya instaladas y no se considera aprobado hasta que la construcción y validación terminen.

## Estado y créditos

El [README en español](README-ES.md#estado-y-límites) registra los resultados conocidos y las limitaciones.
La apertura de la interfaz y la DLL pasaron en Windows; la suite registrada sigue fallando en la prueba de configuración
del toolchain. La estática reportada en Xbox sigue pendiente de reproducción/validación. Las comprobaciones host no
certifican la temporización del display ni todas las funciones de consola.

xSDK original por **Mena / xenosworks y colaboradores**; adaptación Windows por **Axel, con asistencia de OpenAI Codex**.
Se conservan [LICENSE](LICENSE), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) y la documentación original.
GCC, binutils, newlib, glslang, SDL y MSYS2 conservan sus propias licencias. El fork no es una publicación oficial
de Microsoft ni de xenosworks. Al distribuir binarios, conserva los avisos y fuentes requeridos por sus licencias.


## Interfaz EN / ES / PT y recetas de ports

La selección de idioma se guarda automáticamente. Para compilar CoopDX desde la raíz del repositorio con `xsdk-project.json`, consulta [la guía de recetas](README-PROJECTS.md). La herramienta reutiliza xSDK, GCC y SDL3 instalados, comprueba requisitos y genera el XEX local. Las correcciones del motor siguen en las fuentes del port.
