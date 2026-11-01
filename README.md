# xSDK para Windows — port experimental

Este es un derivado del **xSDK original de Mena / xenosworks**, basado en el
commit `8c58c7a3fb37bb261c5a11a8a1f4fa8a8bfd0d28` de
https://github.com/xenosworks/xsdk. El código del SDK, su runtime, su compilador
PowerPC y su compilador de shaders siguen siendo trabajo de ese proyecto y sus
colaboradores. No es un SDK nuevo ni una publicación oficial de xenosworks.

**Estado: implementación inicial para probar, no una versión Windows validada.**
Se añadieron rutas de construcción MSYS2/UCRT64, carga de DLL, GUI y comprobaciones.
No se ha completado todavía un bootstrap GCC → xSDK → XEX en Windows, ni se ha
probado un XEX de este port en consola. No contiene compiladores preconstruidos.

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

- Ocho tests de rutas, argumentos, selección DLL/SO, host de GCC y plan Make.
- Sintaxis de los scripts bash y de los módulos Python.
- Construcción del compilador host existente como SO, con cero warnings según
  `-Wall -Wextra -Werror`, y resolución de un fixture SPIR-V real.
- Prueba upstream `test_xsc_resolve.py`: doce comprobaciones pasan.

Eso comprueba la lógica portable y que se preservó la ruta Linux. **No prueba**
que MinGW construya GCC completo ni que la DLL o GUI funcionen en Windows.
La interfaz no se ha ejecutado visualmente en Windows en esta entrega.

`.github/workflows/windows-host.yml` prepara una comprobación real de DLL en
`windows-latest` con MSYS2. Puede ejecutarse después de publicar este fork.
El bootstrap completo y las pruebas `hello`/`triangle` en la Xbox siguen siendo
necesarios. No se ha iniciado una ejecución de GitHub Actions desde este entorno.

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

## Fork en GitHub

Esta carpeta contiene un derivado local del repositorio original. Para mantener
su relación con upstream, crea el fork desde:
https://github.com/xenosworks/xsdk/fork

El paquete incluye `windows-native.patch`. Sobre una copia limpia del commit
base, se puede aplicar con:

```bash
git switch -c windows-native 8c58c7a3fb37bb261c5a11a8a1f4fa8a8bfd0d28
git apply --check windows-native.patch
git apply windows-native.patch
```

No lo apliques encima del código ya modificado del ZIP: esa copia ya contiene
los cambios. El ZIP no crea ni publica por sí mismo un repositorio en GitHub.
