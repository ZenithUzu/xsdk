# xSDK para Windows — port experimental

Este es un derivado del **xSDK original de Mena / xenosworks**, basado en el
commit `8c58c7a3fb37bb261c5a11a8a1f4fa8a8bfd0d28` de
https://github.com/xenosworks/xsdk. El código del SDK, su runtime, su compilador
PowerPC y su compilador de shaders siguen siendo trabajo de ese proyecto y sus
colaboradores. No es un SDK nuevo ni una publicación oficial de xenosworks.

**Estado: port experimental mantenido en `main`.**
Se añadieron rutas de construcción MSYS2/UCRT64, carga de DLL, GUI y comprobaciones.
Se ha reportado el compilador PowerPC funcionando en Windows y los ejemplos originales en consola.
La compilación completa de esta revisión y la corrección de la estática al cambiar de pantalla siguen
pendientes de validación en Windows y consola. No contiene compiladores preconstruidos.

## Qué cambia

- `tools/toolchain/build.sh` reconoce MSYS2 UCRT64 y solicita un host Windows
  `x86_64-w64-mingw32`, conservando el target `powerpc-xsdk-elf`, los parches y
  las pruebas de ABI originales. La ruta Linux permanece disponible.
- El compilador host de shaders se enlaza como **`build/host/libxsc.dll`** en
  Windows. Make, CMake y Python seleccionan la misma biblioteca.
- `Iniciar-Windows.cmd` abre una interfaz Python/tkinter para instalar
  dependencias, construir compilador y shaders, construir el SDK, sus ejemplos
  y un proyecto CMake compatible.
- Las tareas se ejecutan fuera del hilo de la interfaz; la salida se muestra
  y se guarda, los fallos se conservan y se puede cancelar el árbol de procesos.
- `check_tools.py` rechaza un compilador que no sea un PE de Windows o no tenga
  el target PowerPC de xSDK. No se usa un binario ELF de Debian a escondidas.
- Se conservan LICENSE, THIRD_PARTY_NOTICES.md y los archivos originales.

## Requisitos

1. Windows de 64 bits. El objetivo de esta primera versión es Windows 10/11.
2. Python **3.11 o posterior**, con tkinter y el lanzador `py`, instalado desde
   https://www.python.org/downloads/windows/.
3. MSYS2 en `C:\msys64`, instalado desde https://www.msys2.org/. Completa su
   actualización inicial (`pacman -Syu`), cerrando y abriendo la terminal si
   MSYS2 lo solicita, antes de usar la GUI.
4. Conexión a Internet y espacio libre amplio para las fuentes de GCC, sus
   objetos y glslang. Las cifras de tiempo y espacio del tutorial Linux no se
   han verificado para este host; no se promete una instalación pequeña.

MSYS2 es un entorno de herramientas para Windows: **no instala Debian, WSL ni
una máquina virtual Linux**. Se usa su shell para construir y ejecutar las
herramientas. Esta entrega todavía depende de MSYS2; no es un instalador
completamente autónomo que traiga todos los ejecutables listos.

El SDK de Microsoft y VS2010 no son necesarios. Este port no añade C++ moderno
al compilador del XDK ni mezcla su ABI con las bibliotecas de xSDK.

## Uso de la interfaz

1. Extrae/clona este código en una ruta sin espacios, por ejemplo `C:\xsdk-windows`.
2. Haz doble clic en **`Iniciar-Windows.cmd`**.
3. Comprueba las carpetas de MSYS2 y del código fuente. Los valores propuestos
   para compilador y trabajo son `C:\xsdk-tools\compiler` y `C:\xsdk-tools\work`.
4. Ejecuta los botones numerados en orden:
   - **Dependencias:** instala las herramientas de construcción en MSYS2.
   - **Compilador:** construye GCC/binutils/newlib para PowerPC con host Windows.
   - **Shaders:** construye glslang-xenon para Windows y lo coloca junto al compilador.
   - **Construir SDK:** genera `libxsdk.a`, la DLL host y los títulos de prueba.
   - **Ejemplos:** genera `hello.xex`, `triangle.xex` y los demás ejemplos.
5. Un fallo detiene su etapa. Guarda el log y corrige ese error antes de continuar.
   Los logs de GUI están en `%LOCALAPPDATA%\xsdk-windows`.
6. **Abrir resultados** abre `build\samples` dentro de la carpeta de xSDK.

Las carpetas de SDK/compilador/trabajo no aceptan espacios: GNU bootstrap y el
Makefile original no están preparados para todas las combinaciones de rutas.
El proyecto CMake se pasa como argumento independiente, sin interpolarlo en
una orden de shell; puede incluir espacios.

Para un proyecto propio, elige la carpeta de su `CMakeLists.txt` que use xSDK.
El botón configura `build-xsdk-windows` y compila Release con Ninja. No convierte
un proyecto XDK/VS2010 automáticamente a xSDK.

## Pruebas y límites

Realizado en el entorno de desarrollo Linux:

- Nueve tests de rutas, argumentos, selección DLL/SO, host de GCC y plan Make.
- Sintaxis de los scripts bash y de los módulos Python.
- Construcción del compilador host existente como SO, con cero warnings según
  `-Wall -Wextra -Werror`, y resolución de un fixture SPIR-V real.
- Prueba upstream `test_xsc_resolve.py`: doce comprobaciones pasan.

Eso comprueba la lógica portable y que se preservó la ruta Linux. **No prueba**
que MinGW construya GCC completo ni que la DLL o GUI funcionen en Windows.
La interfaz no se ha ejecutado visualmente en Windows en esta entrega.

`.github/workflows/windows-host.yml` prepara una comprobación real de DLL en
`windows-latest` con MSYS2. Se ejecuta al publicar cambios en `main` o `windows-native`.
El bootstrap completo y las pruebas `hello`/`triangle` en la Xbox siguen siendo
necesarios para esta revisión. El estado de CI se consulta en la pestaña Actions del fork.

Comprobaciones portables:

```text
python -m unittest discover -s tests/windows -v
```

Desde UCRT64, tras construir la DLL:

```bash
python3 tools/windows/check_xsc.py
```

Los scripts originales pueden cambiar en upstream. Este port fija su punto de
partida y no afirma compatibilidad con futuras versiones sin revisarlas.

## Créditos y licencias

- **Mena / xenosworks y colaboradores:** xSDK original, runtime, GPU, importaciones,
  toolchain y compilador xost. Licencia MIT de `LICENSE`.
- **Xenia y libxenon:** código original bajo BSD-3-Clause según
  `THIRD_PARTY_NOTICES.md`; los avisos se mantienen completos.
- **GCC, binutils y newlib:** fuentes y licencias propias; se conservan los hashes
  y parches del toolchain original. Este paquete no redistribuye sus binarios.
- **glslang-xenon / Khronos:** compilador de shaders y dependencias, obtenidos
  desde sus repositorios originales por el paso de construcción.
- **MSYS2 / MinGW-w64:** entorno host nativo de Windows, obtenido por el usuario
  desde sus sitios oficiales; no se incorpora aquí como código propio.
- **Axel, con asistencia de OpenAI Codex:** adaptación host Windows, interfaz,
  scripts y pruebas de este port. Las adiciones conservan la licencia MIT.

Al distribuir títulos, acompaña los ejecutables con los avisos requeridos por
el SDK y por las demás bibliotecas que tu título use. La autoría y las licencias
de upstream no se sustituyen por las de esta interfaz.

## Obtener y actualizar el fork

El código mantenido está en [ZenithUzu/xsdk, rama main](https://github.com/ZenithUzu/xsdk/tree/main).
Descarga [el ZIP de main](https://github.com/ZenithUzu/xsdk/archive/refs/heads/main.zip) o clona:

```bash
git clone --branch main https://github.com/ZenithUzu/xsdk.git
```

Para una copia Git ya situada en `main`, guarda tus cambios locales y usa `git pull --ff-only`.
Si utilizas ZIP, cierra la interfaz y reemplaza el código de xSDK con el contenido del ZIP actualizado.
Conserva `C:\xsdk-tools`: contiene el compilador y los archivos de trabajo.
Después pulsa **Construir SDK**, **Ejemplos** y **Verificar herramientas**; recompila también tus proyectos.
No necesitas reconstruir GCC por los cambios de pantalla y documentación de esta revisión.
No hace falta aplicar ningún parche aparte.

## Revisión de arranque y salida

La revisión conserva los archivos del xSDK original de `xenosworks/xsdk` en `8c58c7a`.
El SDK, las pruebas y los ejemplos siguen usando sus objetivos originales de Make; no se sustituye el núcleo por
una implementación reducida. SDL3 sigue siendo opcional y requiere una construcción de SDL-xenon, como en el original.
Esto no afirma que todas las funciones hayan sido validadas en Windows.

Se corrigió un error de recuperación: se liberaban buffers aunque la devolución de pantalla al sistema agotase
su tiempo de espera. Ahora `xsdk_display_close()` devuelve `NTSTATUS`, registra el fallo y permite reintentar;
la presentación y el logo conservan sus buffers ante ese fallo. La presentación también espera la última fence
antes de liberarlos y devuelve un error si no puede mostrar el primer buffer.
Quien use directamente `xsdk_display_close()` debe comprobar su resultado antes de liberar la imagen mostrada.
Los proyectos deben recompilarse con los encabezados y la biblioteca actualizados.

Estas correcciones cubren fallos comprobables del código. La estática al arrancar o salir que reportó el usuario
sigue pendiente de reproducción y validación en su consola; no se declara resuelta por las pruebas del host.
`xsdk_test.xex` comprueba ahora que la pantalla del sistema se restaura antes de liberar sus buffers.

La interfaz añade **Verificar herramientas**, que ejecuta las pruebas portables, comprueba el compilador,
construye el ejemplo C++23/HLSL de `tests/cmake` y carga el compilador de shaders nativo.
No ejecuta el XEX ni reemplaza las pruebas de consola. **Abrir resultados** muestra ahora todo `build`,
incluidos los títulos de prueba; **Abrir logs** abre los registros de la herramienta.
Los errores del bootstrap muestran el archivo de log y sus últimas 40 líneas.

Para comprobar la transición: recompila SDK y ejemplos, prueba `hello.xex` y `triangle.xex`, sal de cada uno y
repite el arranque. Ejecuta también `xsdk_test.xex` y conserva su log. Anota si la estática aparece antes del logo,
durante el cambio a la aplicación o después de pulsar Back; estos momentos corresponden a transiciones distintas.
No hace falta reconstruir GCC para estos cambios.

## Opciones de la interfaz

- **Configuración CMake:** Debug, Release, RelWithDebInfo o MinSizeRel para proyectos y ejemplos.
  El SDK construido con Make conserva sus opciones originales de compilación.
- **SDL3_DIR:** selecciona la carpeta que contiene `SDL3Config.cmake` de tu construcción SDL-xenon.
  Se transmite a proyectos y ejemplos. No descarga ni construye SDL3 automáticamente.
- **Opciones CMake:** lista JSON de opciones `-D`, por ejemplo `["-DFEATURE=ON", "-DNAME=mi proyecto"]`.
  Se pasan como argumentos separados al configurar un proyecto. Las rutas de toolchain y configuración
  se eligen con los campos propios, para no reemplazarlas por accidente.
- **Prueba avanzada:** elige un objetivo original y pulsa **Construir prueba avanzada**.
  Los objetivos con `break` generan variantes rotas a propósito: sus comprobaciones deben fallar en consola.
  Los XEX de las otras pruebas también requieren ejecución real; construirlos no los declara aprobados.
- **Actualizar código:** actualiza el fork por Git con `--ff-only`. Se niega a sobrescribir cambios locales,
  archivos sin seguimiento u otros repositorios. La casilla de actualización al abrir es opcional y viene apagada.
  Reinicia la interfaz después de actualizar. Las copias ZIP se actualizan descargando una copia Git nueva en la carpeta de trabajo, conservando la original.

## Instalador y herramientas portables

`Instalar-Windows.ps1` instala una copia Git en una carpeta nueva; requiere MSYS2 actualizado y Python con tkinter.
Desde PowerShell, en la carpeta del código, ejecuta:

```powershell
powershell -File .\Instalar-Windows.ps1 -Destination C:\xsdk-instalado
```

Con herramientas construidas, **Crear paquete portable** genera `xsdk-windows-portable.zip` y su `.sha256`
en la carpeta de trabajo. Incluye el compilador, glslang, código del SDK, fuentes correspondientes y avisos;
se niega a empaquetar si faltan herramientas o fuentes. Requiere una copia Git del SDK. Sigue requiriendo MSYS2 UCRT64 para las dependencias host.
Se puede instalar ese compilador con `-Bundle C:\ruta\xsdk-windows-portable.zip`, conservando su checksum al lado.
El instalador no reemplaza carpetas existentes y comprueba el checksum antes de extraer las herramientas.
Después configura el compilador en la interfaz y construye el SDK y tu proyecto.

En GitHub Actions, el flujo **Windows host tools (experimental)** permite activar manualmente `build_native`.
También se solicita en `main` mediante un commit con `[native-bundle]` en su mensaje.
Construye toolchain, shaders, SDK, ejemplos y comprobaciones antes de subir el ZIP y checksum como artefactos.
Es una construcción larga; si falla, conserva los logs. Esto prepara la generación de binarios precompilados,
pero no significa que ya exista un paquete aprobado: hay que completar ese flujo en Windows.
No es todavía un instalador autónomo que incluya Python y MSYS2.

La estática sigue pendiente de validación en Xbox; ninguna opción de interfaz sustituye esa comprobación.

## Usar las herramientas que ya tienes

La pestaña **Mis herramientas** es ahora la pantalla inicial. Al abrirla se comprueban rutas habituales,
las rutas guardadas, `XSDK_TOOLCHAIN` y el PATH. No descarga paquetes ni compila GCC, newlib o shaders.
**Rutas y proyecto** permite indicar cualquier instalación existente y seleccionar un `glslang.exe` separado.
Los valores guardados tienen prioridad si contienen las herramientas. La detección no recorre todo el disco.

1. Abre **Iniciar-Windows.cmd** y pulsa **Detectar / comprobar**.
2. Si hace falta, indica MSYS2, la carpeta raíz del compilador, xSDK y glslang en **Rutas y proyecto**.
3. Selecciona tu proyecto y pulsa **Compilar proyecto**. Reutiliza las herramientas elegidas.
4. Si cambió xSDK, pulsa **Reconstruir solo SDK** y luego compila tu proyecto.

La tabla muestra GCC/C++, binutils, newlib, glslang, las bibliotecas del SDK y las dependencias host.
Los comandos de versión tienen tiempo límite y se ejecutan fuera del hilo de la interfaz.
Que un ejecutable responda no sustituye las pruebas de compilación y consola.

**Buscar actualizaciones** consulta los commits remotos del fork y de glslang-xenon, sin instalar ni construir.
También compara las versiones locales de GCC, binutils y newlib con la receta que trae tu código de xSDK.
Si los commits son distintos, no se presupone que un fork personalizado sea más antiguo.
Las instalaciones sin registro muestran que sus parches no están comprobados; no se marcan como obsoletas
solo por ser anteriores a esta interfaz. La versión de glslang por sí sola no demuestra que sea la variante xenon.

**Instalar / actualizar seleccionado** actúa únicamente sobre la fila elegida:

- **Compilador, binutils o newlib:** ofrece una construcción larga en una carpeta NUEVA y conserva el compilador
  anterior. No reutiliza los sellos de una construcción vieja. No ocurre al abrir ni al compilar un proyecto.
- **Shaders:** actualiza el checkout xenon, si existe, mediante avance directo, y construye solo shaders.
- **xSDK:** actualiza una copia Git limpia. Si venías de ZIP, descarga una copia Git nueva bajo
  `work/sdk-updates`, conserva la original y cambia la ruta elegida. Abre la interfaz de la nueva carpeta
  y reconstruye solo SDK/proyectos.
- **Dependencias:** instala los paquetes host requeridos en el MSYS2 elegido; no reconstruye el compilador PowerPC.
  La detección de dependencias comprueba presencia, no promete que todos los paquetes del sistema estén actualizados.

Las construcciones exitosas registran su receta en `components.json` dentro de la carpeta de trabajo.
No se necesita ni se espera a que termine el paquete precompilado de GitHub para usar este administrador.
