<div align="center">
  <img src="assets/xsdk.png" alt="xSDK" width="640">
</div>

# xSDK para Windows

Fork de [xenosworks/xsdk](https://github.com/xenosworks/xsdk), creado por **Mena / xenosworks y colaboradores**.
Permite preparar herramientas PowerPC y construir aplicaciones `.xex` para Xbox 360 desde Windows con
**MSYS2 UCRT64**, con una interfaz Python en español. La rama de uso es **`main`**.

[Descargar main en ZIP](https://github.com/ZenithUzu/xsdk/archive/refs/heads/main.zip) ·
[Guía de Windows](README-WINDOWS.md) · [Documentación original](README-UPSTREAM.md)

## Empezar en Windows

1. Instala Python 3.11 o posterior con tkinter y el lanzador `py`.
2. Instala MSYS2 en `C:\msys64` y completa `pacman -Syu` desde UCRT64.
3. Extrae el código en una carpeta sin espacios, por ejemplo `C:\xsdk-windows`.
4. Abre **Iniciar-Windows.cmd**.
5. Ejecuta **Dependencias → Compilador → Shaders → Construir SDK → Ejemplos**, esperando a que termine cada etapa.

La [guía completa](README-WINDOWS.md) explica las rutas, requisitos, actualización y solución de errores.
**Abrir resultados** muestra `build`, con los ejemplos y títulos de prueba.
**Verificar herramientas** comprueba los binarios de Windows, C++23 y la integración CMake/HLSL.
**Abrir logs** permite consultar los registros cuando una construcción tarda o falla.

## Qué se conserva y qué añade el fork

Se conservan el código, runtime C/C++, GPU, audio, red, herramientas, ejemplos y pruebas de la base original
`8c58c7a`. El port añade la construcción host para Windows, `libxsc.dll`, rutas compatibles con Windows,
la interfaz y diagnósticos. La construcción original de Linux también permanece disponible.
SDL3 sigue siendo opcional y requiere SDL-xenon, como en upstream.

Las correcciones de pantalla comprueban la primera presentación y conservan los buffers cuando la GPU
no termina o la devolución de pantalla al sistema falla. Los errores se registran para poder diagnosticarlos.
**La estática reportada al arrancar y salir aún requiere comprobación en consola.**

## Estado de las comprobaciones

Port experimental. Las pruebas portables, la recuperación de pantalla con registros simulados y la construcción
del compilador de shaders en Linux pasan. GitHub Actions comprueba la DLL real en Windows y las pruebas portables.
Estos resultados no prueban una compilación completa del toolchain ni el comportamiento de pantalla en Xbox.
Los resultados históricos del proyecto original están en [docs/HARDWARE.md](docs/HARDWARE.md);
no equivalen a validar automáticamente esta revisión del fork.

## Documentación y créditos

- [Instalación y actualización en Windows](README-WINDOWS.md)
- [README original de xSDK](README-UPSTREAM.md)
- [Guía de programación](docs/GUIDE.md) y [ejemplos](samples/)
- [Funciones disponibles y pendientes](docs/PARITY.md)
- [Licencia MIT](LICENSE) y [avisos de terceros](THIRD_PARTY_NOTICES.md)

**xSDK original:** Mena / xenosworks y colaboradores. Se mantienen sus créditos y licencias, y los de
Xenia, libxenon y demás dependencias. **Adaptación de Windows:** Axel, con asistencia de OpenAI Codex.
Este fork no es una publicación oficial de xenosworks ni de Microsoft.
