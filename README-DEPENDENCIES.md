# Fuentes, rutas y preparación de dependencias

## Español

La pestaña **Fuentes y dependencias** reúne los enlaces GitHub, las ramas y las carpetas locales. Está traducida al inglés y portugués. MSYS2 se ejecuta por detrás: los comandos, descargas, errores y resultados aparecen en el panel de salida y en el log. No se abren ventanas CMD para estas consultas.

### Si ya tienes herramientas

1. Pulsa **Detectar rutas instaladas**. Se revisan las rutas guardadas, variables de entorno, PATH y ubicaciones habituales de unidades locales. Las selecciones válidas se conservan.
2. Si falta algo, elige una **Carpeta adicional para buscar herramientas** y vuelve a detectar. La búsqueda tiene límites: hasta 600 carpetas, tres niveles y 300 entradas por carpeta. No recorre enlaces/junctions ni unidades de red. No es un inventario completo de todos los discos.
3. Revisa las carpetas encontradas: MSYS2, xSDK, compilador, glslang, fuente SDL3 y SDL3 compilado. Encontrar archivos no certifica su versión o ABI.
4. Pulsa **Preparar todo lo faltante**. Verifica el compilador con una pequeña prueba C++23 y reutiliza los componentes existentes; no reconstruye el compilador ni SDL3 cuando ya están disponibles. **Construir xSDK** y **Construir SDL3** fuerzan la construcción del componente elegido.

### Desde cero con enlaces

MSYS2 debe estar instalado; el botón **Web de MSYS2** abre su sitio oficial. No se descarga ni ejecuta un instalador de Windows al abrir la aplicación.

1. Selecciona la carpeta de MSYS2. Si faltan Python UCRT64 u otros paquetes del entorno, una acción de preparación explícita puede instalarlos mediante pacman. Debe completarse primero la actualización de MSYS2 si pacman lo solicita.
2. Pega los enlaces y elige las ramas. Valores predeterminados:

| Componente | Repositorio | Rama |
| --- | --- | --- |
| xSDK para Windows | `https://github.com/ZenithUzu/xsdk.git` | `main` |
| SDL3 Xenon | `https://github.com/xenosworks/SDL-xenon.git` | `xenon` |
| glslang-xenon | `https://github.com/xenosworks/glslang-xenon.git` | `xenon` |

3. Elige las carpetas destino. xSDK, compilador y trabajo deben estar en rutas sin espacios. El compilador nuevo necesita un destino que todavía no exista. Los botones de descarga conservan los archivos existentes y rechazan un checkout con otro origen.
4. Pulsa **Preparar todo lo faltante**: prepara paquetes MSYS2 si hacen falta, obtiene xSDK, obtiene SDL3, construye un compilador faltante desde su receta, prepara glslang, construye las bibliotecas SDK faltantes y construye SDL3. Cada etapa debe terminar correctamente antes de seguir. La primera construcción del compilador puede tardar horas.
5. La ruta SDL3 resultante se selecciona en la interfaz. Configura tu repo del port, ROM y carpeta nueva de salida; usa **Construir y empaquetar juego**.

También hay botones independientes para **Descargar xSDK**, **Descargar SDL3**, **Construir xSDK**, **Construir SDL3**, **Construir glslang** y **Construir compilador en destino nuevo**. Este último propone una carpeta nueva cuando ya hay compilador, para conservar el anterior. **Cancelar** detiene el árbol del proceso activo; una descarga interrumpida puede dejar una carpeta incompleta que necesita revisión o un destino nuevo.

**El enlace del compilador es la receta del xSDK elegido**, no una descarga de GCC genérico: **Ver receta del compilador** abre `tools/toolchain/build.sh` en ese repositorio y rama. La receta fija versiones y hashes de fuentes GNU/newlib. El SDK original de xenosworks por sí solo no tiene esta integración de Windows: utiliza este fork o uno que conserve sus archivos y cambios de compatibilidad. Los enlaces aceptan repositorios HTTPS de GitHub y la forma `/tree/rama`; no aceptan credenciales, comandos, enlaces de archivos ni descargas de releases. Validar una URL no valida la seguridad del código que contiene: usa fuentes que hayas revisado.

### Actualizar

**Actualizar fuentes y reconstruir** descarga cambios únicamente al pulsar el botón, valida el origen y la rama, rechaza modificaciones locales y usa avances rápidos de Git. Reconstruye shaders, SDK y SDL3. No cambia de versión ni reconstruye un compilador válido automáticamente; para eso existe la acción explícita de destino nuevo.

Si el SDK instalado proviene de un ZIP, clona una copia Git en una carpeta nueva dentro de trabajo y conserva la anterior. Hace lo mismo con fuentes SDL3 sin historial, usando una carpeta de construcción nueva. Los cambios de ruta se reflejan en la interfaz. Un error puede detener el flujo después de etapas ya completadas; el log muestra qué terminó. No se realiza un restablecimiento destructivo de repositorios.

No hay instalaciones ni actualizaciones al arrancar. La detección inicial es local; la consulta remota de versiones sigue siendo opcional. Los botones de construcción ejecutan código de los repositorios seleccionados: no equivalen a una auditoría del contenido de terceros.

## English

Use **Sources and dependencies** to enter GitHub repository URLs, branches and local destinations for xSDK Windows, SDL3 Xenon and glslang-xenon. **Detect installed paths** preserves valid selections and checks saved paths, environment variables, PATH, common local folders and an optional search folder. The search is bounded and skips links, junctions and network drives.

Install MSYS2 first. **Prepare missing components** can install missing UCRT64 packages, clone sources and build missing tools behind the interface, with output in the command panel. It reuses existing compiler/SDK/SDL builds. There are separate download and build buttons. Compiler source comes from the selected xSDK toolchain recipe; use **View compiler recipe** to inspect it. The original upstream SDK needs Windows compatibility changes; choose this fork or a compatible one.

**Update sources and rebuild** verifies Git origins/branches, rejects dirty trees and uses fast-forward updates. ZIP installations are preserved and replaced by a new Git source folder. Existing compilers are not automatically rebuilt; use the new-folder compiler action explicitly. Cancel stops the process tree; interrupted downloads may leave incomplete source directories. Build stages completed before an error are kept and reported in the log.

Only HTTPS GitHub repository URLs are accepted, including `/tree/branch`. No credentials, arbitrary download URLs or file/release links. Repository syntax checks do not establish code safety. No download, installation or update starts merely by opening the interface. After dependencies are ready, configure your port/ROM and use **Build and package game**.

## Português

Em **Fontes e dependências**, indique URLs GitHub, branches e pastas para xSDK Windows, SDL3 Xenon e glslang-xenon. **Detectar caminhos instalados** preserva seleções válidas e procura nas configurações, variáveis de ambiente, PATH, pastas locais habituais e uma pasta adicional. A busca é limitada e ignora links, junctions e unidades de rede.

Instale MSYS2 primeiro. **Preparar componentes ausentes** instala pacotes UCRT64 ausentes, obtém as fontes e compila o necessário em segundo plano, mostrando a saída no painel. Reutiliza compilador/SDK/SDL já disponíveis. Há botões separados para baixar e compilar. O compilador usa a receita do xSDK escolhido; **Ver receita do compilador** permite inspecioná-la. Use este fork ou outro compatível com Windows, pois o upstream original sozinho não contém essa integração.

**Atualizar fontes e recompilar** verifica origem e branch, rejeita alterações locais e faz atualizações fast-forward. Instalações ZIP são preservadas, com novas fontes Git em outra pasta. Compiladores existentes não são reconstruídos automaticamente; use a ação explícita com novo destino. Cancelar interrompe a árvore de processos; downloads interrompidos podem deixar fontes incompletas. O log mostra as etapas concluídas antes de qualquer erro.

São aceitos apenas repositórios HTTPS do GitHub, incluindo `/tree/branch`, sem credenciais ou links de arquivos/releases. Validar a URL não comprova a segurança do código. Nenhuma instalação ou atualização acontece ao abrir a interface. Depois, configure o port/ROM e use **Compilar e empacotar jogo**.


## Recuperar configuración del BAT/CMD y portables anteriores

La interfaz fuente actual lee primero su configuración y, cuando faltan rutas, consulta la configuración compartida de `Iniciar-Windows.cmd` en `%LOCALAPPDATA%/xsdk-windows/settings.json`. También revisa ubicaciones conocidas y carpetas anteriores con nombre xSDK en `C:/`, `C:/tools`, Descargas y junto al portable. Es una búsqueda limitada de archivos JSON, sin ejecutar BAT/CMD ni programas antiguos y sin recorrer todo el disco.

Las rutas recuperadas deben existir y tener los archivos esperados. Se conservan las opciones actuales no vacías; el botón **Recuperar rutas anteriores** permite además sustituir rutas inválidas por otras válidas guardadas. No se importan acciones automáticas ni opciones de restauración de inputs/mods. Si el proyecto anterior apuntaba a `platform/xsdk`, se selecciona la raíz del port cuando existe `xsdk-project.json`.

El recuadro de información muestra de qué archivo se recuperaron las rutas, los resultados de la detección, el inicio y fin de operaciones y los comandos. Un aviso de actividad cada 15 segundos no es una estimación de porcentaje. Las salidas del compilador se conservan tal como llegan.

Estos cambios se aplicaron a las fuentes y al lanzador CMD local. No se recompiló ni reemplazó el EXE del Release v3.


## Actualizar o reinstalar en la ruta existente

En la versión nueva, **Instalar / actualizar seleccionado** usa la ruta actual para SDK, SDL3, glslang y compilador. **Actualizar en la misma ruta con respaldo** actualiza las fuentes de dependencias y reconstruye sobre sus directorios existentes.

- En instalaciones SDK/SDL procedentes de ZIP, se obtiene una copia Git en `trabajo/source-cache/` y se copian al destino solo los archivos de fuente que cambiaron. Los originales sustituidos quedan en `trabajo/source-backups/`. Se preservan `build/`, `build-xsdk/`, `build-windows/`, datos locales y archivos no administrados. Se conserva la fecha de los archivos idénticos para no forzar recompilaciones.
- En un checkout Git, se mantiene la comprobación de origen/rama y el avance rápido. En este modo explícito, las modificaciones de archivos rastreados se guardan en un **Git stash**, cuyo identificador aparece en el recuadro. No se descartan commits ni se ejecuta `reset --hard`/`clean`. Una colisión con un archivo no rastreado puede requerir intervención; no se borra automáticamente.
- **Actualizar/reinstalar compilador actual** respalda primero el compilador en `trabajo/compiler-backups/`. Si existen los Makefiles originales, coinciden la receta registrada y el destino configurado, reutiliza sus objetivos de instalación. Si no hay caché compatible, necesita construir el compilador en una caché nueva y conservar el mismo destino; esto sí puede tardar. No es posible evitar una reconstrucción real cuando cambian versión, parches u opciones incompatibles.
- Los programas hijos de la operación de Windows se agrupan en un Job Object. **Cancelar** termina ese grupo, aunque Bash ya haya salido, y no bloquea la interfaz. También se puede cancelar la detección de versiones. El estado final indica cancelación en lugar de éxito.

Si cancelas durante una descarga o sustitución de fuentes, puede quedar una etapa incompleta: vuelve a ejecutar la actualización antes de construir. Los respaldos se conservan y no se borran las cachés completas automáticamente. No se actualizaron ni construyeron dependencias reales para verificar este cambio: las pruebas usan procesos de espera y árboles de archivos sintéticos.

**English:** selected-component updates can keep their current destination. ZIP source overlays back up changed files and preserve build caches/unchanged timestamps. Explicit Git overwrite saves tracked edits in stash and retains fast-forward checks. Compiler repair reuses matching build caches or rebuilds when necessary, after a backup. Windows cancellation terminates the owned process group, including children left by an exited launcher.

**Português:** a atualização mantém o destino selecionado. Fontes ZIP são substituídas com backup dos arquivos alterados, preservando caches e datas dos arquivos iguais. Alterações Git rastreadas vão para stash no modo explícito. O compilador reutiliza cache compatível ou precisa de uma reconstrução, com backup. Cancelar termina o grupo de processos da operação no Windows.
