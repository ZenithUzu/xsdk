"""Translations of the Windows interface; compiler output is kept verbatim."""

LANGUAGES = {"en": "English", "es": "Español", "pt": "Português"}

# Existing Spanish messages stay the keys so saved settings and backend errors remain compatible.
MESSAGES = [
    ("Listo. La información y el progreso aparecerán aquí.",
     "Ready. Information and progress will appear here.",
     "Pronto. Informações e progresso aparecerão aqui."),
    ("Configuración cargada: ",
     "Settings loaded: ",
     "Configurações carregadas: "),
    ("Rutas recuperadas de: ",
     "Paths recovered from: ",
     "Caminhos recuperados de: "),
    ("Recuperar rutas anteriores",
     "Recover previous paths",
     "Recuperar caminhos anteriores"),
    ("No se encontraron rutas anteriores adicionales.",
     "No additional previous paths found.",
     "Nenhum caminho anterior adicional encontrado."),
    ("Iniciando: ",
     "Starting: ",
     "Iniciando: "),
    ("Ruta seleccionada: ",
     "Selected path: ",
     "Caminho selecionado: "),
    ("Sigue en ejecución: ",
     "Still running: ",
     "Ainda em execução: "),
    ("Cancelación solicitada.",
     "Cancellation requested.",
     "Cancelamento solicitado."),

    ("Ver receta del compilador", "View compiler recipe", "Ver receita do compilador"),
    ("Fuentes y dependencias",
     "Sources and dependencies",
     "Fontes e dependências"),
    ("Repositorio xSDK Windows (HTTPS GitHub)",
     "xSDK Windows repository (HTTPS GitHub)",
     "Repositório xSDK Windows (HTTPS GitHub)"),
    ("Rama xSDK",
     "xSDK branch",
     "Branch xSDK"),
    ("Carpeta fuente xSDK",
     "xSDK source folder",
     "Pasta fonte xSDK"),
    ("Compilador instalado o destino NUEVO",
     "Installed compiler or NEW destination",
     "Compilador instalado ou NOVO destino"),
    ("Repositorio glslang-xenon",
     "glslang-xenon repository",
     "Repositório glslang-xenon"),
    ("Rama glslang",
     "glslang branch",
     "Branch glslang"),
    ("Repositorio SDL3 Xenon",
     "SDL3 Xenon repository",
     "Repositório SDL3 Xenon"),
    ("Rama SDL3",
     "SDL3 branch",
     "Branch SDL3"),
    ("Carpeta fuente SDL3",
     "SDL3 source folder",
     "Pasta fonte SDL3"),
    ("Carpeta compilada SDL3",
     "SDL3 build folder",
     "Pasta de compilação SDL3"),
    ("Carpeta adicional para buscar herramientas",
     "Additional tool search folder",
     "Pasta adicional para buscar ferramentas"),
    ("Abrir enlace",
     "Open link",
     "Abrir link"),
    ("Detectar rutas instaladas",
     "Detect installed paths",
     "Detectar caminhos instalados"),
    ("Descargar xSDK",
     "Download xSDK",
     "Baixar xSDK"),
    ("Descargar SDL3",
     "Download SDL3",
     "Baixar SDL3"),
    ("Construir xSDK",
     "Build xSDK",
     "Compilar xSDK"),
    ("Construir SDL3",
     "Build SDL3",
     "Compilar SDL3"),
    ("Preparar todo lo faltante",
     "Prepare missing components",
     "Preparar componentes ausentes"),
    ("Actualizar fuentes y reconstruir",
     "Update sources and rebuild",
     "Atualizar fontes e recompilar"),
    ("Construir compilador en destino nuevo",
     "Build compiler in new folder",
     "Compilar compilador em nova pasta"),
    ("Construir glslang",
     "Build glslang",
     "Compilar glslang"),
    ("Web de MSYS2",
     "MSYS2 website",
     "Site do MSYS2"),
    ("SDL3Config.cmake presente",
     "SDL3Config.cmake found",
     "SDL3Config.cmake encontrado"),
    ("Falta SDL3; usar Fuentes y dependencias",
     "SDL3 missing; use Sources and dependencies",
     "SDL3 ausente; use Fontes e dependências"),
    ("MSYS2 trabaja por detrás. Las descargas y compilaciones solo empiezan al pulsar un botón.",
     "MSYS2 runs in the background. Downloads and builds start only when you press a button.",
     "MSYS2 funciona em segundo plano. Downloads e compilações só começam ao clicar em um botão."),

    ("Consultar actualizaciones al abrir (sin instalar)",
     "Check updates on startup (never install)",
     "Consultar atualizações ao abrir (sem instalar)"),
    ("Elige una carpeta NUEVA de salida del juego en Rutas y proyecto.",
     "Choose a NEW game output folder in Paths and project.",
     "Escolha uma NOVA pasta de saída do jogo em Caminhos e projeto."),
    ("Elige una carpeta NUEVA; nunca se sobrescriben las existentes.",
     "Choose a NEW output folder; existing folders are never overwritten.",
     "Escolha uma NOVA pasta; pastas existentes nunca são sobrescritas."),
    ("Selecciona la raíz de CoopDX que contiene xsdk-project.json.",
     "Select the CoopDX repository root containing xsdk-project.json.",
     "Selecione a raiz do CoopDX que contém xsdk-project.json."),
    ("Construir y empaquetar juego", "Build and package game", "Compilar e empacotar jogo"),
    ("Empaquetar compilación existente", "Package existing build", "Empacotar compilação existente"),
    ("CoopDX PC local (opcional)", "Local CoopDX PC (optional)", "CoopDX PC local (opcional)"),
    ("Carpeta NUEVA del juego empaquetado", "NEW packaged game folder", "NOVA pasta do jogo empacotado"),
    ("Incluir mods y packs locales (compatibilidad sin confirmar)",
     "Include local mods and packs (compatibility unconfirmed)",
     "Incluir mods e packs locais (compatibilidade não confirmada)"),
    ("Disponible", "Available", "Disponível"),
    ("Construir SDK (reutiliza compilador y shaders)",
     "Build SDK (reuse compiler and shader tools)",
     "Compilar SDK (reutilizar compilador e ferramentas de shaders)"),
    (
        ("Restaurar entradas heredadas locales (solo con permiso para usarlas)"),
        ("Restore local inherited inputs (only with permission to use them)"),
        ("Restaurar entradas locais herdadas (apenas com permissão para usá-las)"),
    ),
    (
        ("xSDK para Windows — experimental"),
        ("xSDK for Windows — experimental"),
        ("xSDK para Windows — experimental"),
    ),
    (
        ("Port experimental — aún requiere validación completa en Windows"),
        ("Experimental port — full Windows validation still pending"),
        ("Port experimental — validação completa no Windows ainda pendente"),
    ),
    (
        ("Compilador PowerPC, shaders y ejemplos · sin Debian ni WSL"),
        ("PowerPC compiler, shaders and samples · no Debian or WSL"),
        ("Compilador PowerPC, shaders e exemplos · sem Debian ou WSL"),
    ),
    (
        ("Mis herramientas"),
        ("My tools"),
        ("Minhas ferramentas"),
    ),
    (
        ("Rutas y proyecto"),
        ("Paths and project"),
        ("Caminhos e projeto"),
    ),
    (
        ("Instalación y pruebas avanzadas"),
        ("Installation and advanced tests"),
        ("Instalação e testes avançados"),
    ),
    (
        ("Reutiliza tus herramientas. Compilar un proyecto no reconstruye GCC ni newlib."),
        ("Reuse your tools. Building a project does not rebuild GCC or newlib."),
        ("Reutilize suas ferramentas. Compilar um projeto não recompila GCC nem newlib."),
    ),
    (
        ("Componente"),
        ("Component"),
        ("Componente"),
    ),
    (
        ("Versión"),
        ("Version"),
        ("Versão"),
    ),
    (
        ("Estado"),
        ("Status"),
        ("Estado"),
    ),
    (
        ("Detectar / comprobar"),
        ("Detect / check"),
        ("Detectar / verificar"),
    ),
    (
        ("Buscar actualizaciones"),
        ("Check for updates"),
        ("Buscar atualizações"),
    ),
    (
        ("Instalar / actualizar seleccionado"),
        ("Install / update selected"),
        ("Instalar / atualizar selecionado"),
    ),
    (
        ("Compilar proyecto"),
        ("Build project"),
        ("Compilar projeto"),
    ),
    (
        ("Comprobar receta del port"),
        ("Check port recipe"),
        ("Verificar receita do port"),
    ),
    (
        ("Reconstruir solo SDK"),
        ("Rebuild SDK only"),
        ("Recompilar apenas o SDK"),
    ),
    (
        ("Código de xSDK"),
        ("xSDK source"),
        ("Código do xSDK"),
    ),
    (
        ("Compilador instalado (carpeta raíz)"),
        ("Installed compiler (root folder)"),
        ("Compilador instalado (pasta raiz)"),
    ),
    (
        ("Carpeta de trabajo"),
        ("Work folder"),
        ("Pasta de trabalho"),
    ),
    (
        ("glslang.exe instalado (opcional)"),
        ("Installed glslang.exe (optional)"),
        ("glslang.exe instalado (opcional)"),
    ),
    (
        ("Proyecto CMake"),
        ("CMake project"),
        ("Projeto CMake"),
    ),
    (
        ("Proyecto CMake o raíz del port"),
        ("CMake project or port root"),
        ("Projeto CMake ou raiz do port"),
    ),
    (
        ("ROM privada del proyecto (opcional)"),
        ("Project private ROM (optional)"),
        ("ROM privada do projeto (opcional)"),
    ),
    (
        ("SDL3_DIR (opcional)"),
        ("SDL3_DIR (optional)"),
        ("SDL3_DIR (opcional)"),
    ),
    (
        ("Configuración CMake"),
        ("CMake build type"),
        ("Configuração do CMake"),
    ),
    (
        ("Opciones CMake (lista JSON)"),
        ("CMake options (JSON list)"),
        ("Opções do CMake (lista JSON)"),
    ),
    (
        ("Prueba avanzada"),
        ("Advanced test"),
        ("Teste avançado"),
    ),
    (
        ("Trabajos simultáneos"),
        ("Parallel jobs"),
        ("Tarefas simultâneas"),
    ),
    (
        ("Elegir…"),
        ("Browse…"),
        ("Escolher…"),
    ),
    (
        ("Actualizar automáticamente al abrir (solo copias Git limpias)"),
        ("Update on startup (clean Git checkouts only)"),
        ("Atualizar ao abrir (apenas cópias Git limpas)"),
    ),
    (
        ("Diagnóstico"),
        ("Diagnostics"),
        ("Diagnóstico"),
    ),
    (
        ("1. Dependencias"),
        ("1. Dependencies"),
        ("1. Dependências"),
    ),
    (
        ("Construir compilador (lento)"),
        ("Build compiler (slow)"),
        ("Compilar compilador (lento)"),
    ),
    (
        ("Construir shaders"),
        ("Build shader tools"),
        ("Compilar ferramentas de shaders"),
    ),
    (
        ("4. Construir SDK"),
        ("4. Build SDK"),
        ("4. Compilar SDK"),
    ),
    (
        ("5. Ejemplos"),
        ("5. Samples"),
        ("5. Exemplos"),
    ),
    (
        ("Verificar herramientas"),
        ("Verify tools"),
        ("Verificar ferramentas"),
    ),
    (
        ("Construir prueba avanzada"),
        ("Build advanced test"),
        ("Compilar teste avançado"),
    ),
    (
        ("Actualizar código"),
        ("Update source"),
        ("Atualizar código"),
    ),
    (
        ("Crear paquete portable"),
        ("Create portable bundle"),
        ("Criar pacote portátil"),
    ),
    (
        ("Cancelar"),
        ("Cancel"),
        ("Cancelar"),
    ),
    (
        ("Abrir resultados"),
        ("Open results"),
        ("Abrir resultados"),
    ),
    (
        ("Abrir logs"),
        ("Open logs"),
        ("Abrir logs"),
    ),
    (
        ("Créditos"),
        ("Credits"),
        ("Créditos"),
    ),
    (
        ("Consultar actualizaciones"),
        ("Checking updates"),
        ("Consultando atualizações"),
    ),
    (
        ("Detectar herramientas"),
        ("Detecting tools"),
        ("Detectando ferramentas"),
    ),
    (
        ("No se pudo inspeccionar: "),
        ("Could not inspect: "),
        ("Não foi possível inspecionar: "),
    ),
    (
        ("Consulta sin compilación; vuelve a comprobar después de actualizar"),
        ("Read-only check; check again after updating"),
        ("Consulta sem compilação; verifique novamente após atualizar"),
    ),
    (
        ("Componentes"),
        ("Components"),
        ("Componentes"),
    ),
    (
        ("Selecciona una fila para instalar o actualizar solo ese componente"),
        ("Select a row to install or update only that component"),
        ("Selecione uma linha para instalar ou atualizar apenas esse componente"),
    ),
    (
        ("Actualizar compilador"),
        ("Update compiler"),
        ("Atualizar compilador"),
    ),
    (
        ("Esto reconstruye GCC y newlib y puede tardar bastante. Para usar tus herramientas actuales "
         "basta con indicar su ruta. ¿Quieres construir un compilador nuevo sin reemplazar el "
         "existente?"),
        ("This rebuilds GCC and newlib and may take a long time. To reuse existing tools, just select "
         "their path. Build a new compiler without replacing the existing one?"),
        ("Isso recompila GCC e newlib e pode demorar. Para usar suas ferramentas atuais, basta indicar"
         " o caminho. Compilar um novo compilador sem substituir o existente?"),
    ),
    (
        ("Carpeta NUEVA del compilador"),
        ("NEW compiler folder"),
        ("NOVA pasta do compilador"),
    ),
    (
        ("Compilador"),
        ("Compiler"),
        ("Compilador"),
    ),
    (
        ("Elige una ruta que todavía no exista"),
        ("Choose a path that does not exist yet"),
        ("Escolha um caminho que ainda não exista"),
    ),
    (
        ("Preferencias"),
        ("Preferences"),
        ("Preferências"),
    ),
    (
        ("Ejecutable"),
        ("Executable"),
        ("Executável"),
    ),
    (
        ("Indica tu compilador existente en Rutas y proyecto, o instala el componente faltante"),
        ("Select your existing compiler in Paths and project, or install the missing component"),
        ("Indique seu compilador em Caminhos e projeto ou instale o componente ausente"),
    ),
    (
        ("Instala y actualiza MSYS2 desde https://www.msys2.org/ y elige su carpeta"),
        ("Install and update MSYS2 from https://www.msys2.org/ and select its folder"),
        ("Instale e atualize o MSYS2 em https://www.msys2.org/ e escolha sua pasta"),
    ),
    (
        ("La carpeta seleccionada no contiene este port de xSDK"),
        ("The selected folder does not contain this xSDK port"),
        ("A pasta selecionada não contém este port do xSDK"),
    ),
    (
        ("Configuración"),
        ("Settings"),
        ("Configuração"),
    ),
    (
        ("Ejecutando: "),
        ("Running: "),
        ("Executando: "),
    ),
    (
        ("Etapa terminada"),
        ("Stage completed"),
        ("Etapa concluída"),
    ),
    (
        ("Error/cancelación ("),
        ("Error/cancelled ("),
        ("Erro/cancelado ("),
    ),
    (
        (" · Consulta los logs"),
        (" · Check the logs"),
        (" · Consulte os logs"),
    ),
    (
        ("Resultados"),
        ("Results"),
        ("Resultados"),
    ),
    (
        ("Los ejemplos todavía no están construidos"),
        ("The samples have not been built yet"),
        ("Os exemplos ainda não foram compilados"),
    ),
    (
        ("Proceso activo"),
        ("Process running"),
        ("Processo ativo"),
    ),
    (
        ("Cancela la tarea o espera a que termine antes de cerrar"),
        ("Cancel the task or wait for it to finish before closing"),
        ("Cancele a tarefa ou aguarde sua conclusão antes de fechar"),
    ),
    (
        ("Elige un proyecto CMake"),
        ("Select a CMake project"),
        ("Escolha um projeto CMake"),
    ),
    (
        ("Acción desconocida"),
        ("Unknown action"),
        ("Ação desconhecida"),
    ),
    (
        ("Tipo de compilación desconocido"),
        ("Unknown build type"),
        ("Tipo de compilação desconhecido"),
    ),
    (
        ("Prueba avanzada desconocida"),
        ("Unknown advanced test"),
        ("Teste avançado desconhecido"),
    ),
    (
        ("Usa de 1 a 64 trabajos"),
        ("Use 1 to 64 jobs"),
        ("Use de 1 a 64 tarefas"),
    ),
    (
        ("Usa rutas sin espacios para xSDK, compilador y trabajo"),
        ("Use paths without spaces for xSDK, compiler and work"),
        ("Use caminhos sem espaços para xSDK, compilador e trabalho"),
    ),
    (
        ("Usa los campos de la interfaz para las rutas y el tipo de compilación"),
        ("Use the interface fields for paths and build type"),
        ("Use os campos da interface para caminhos e tipo de compilação"),
    ),
    (
        ("Solo se aceptan opciones -DNOMBRE=valor"),
        ("Only -DNAME=value options are accepted"),
        ("Somente opções -DNOME=valor são aceitas"),
    ),
    (
        ("Las opciones CMake deben ser una lista de textos"),
        ("CMake options must be a list of strings"),
        ("As opções do CMake devem ser uma lista de textos"),
    ),
    (
        ("Opciones CMake: usa una lista JSON, por ejemplo [\"-DFEATURE=ON\"]"),
        ("CMake options: use a JSON list, for example [\"-DFEATURE=ON\"]"),
        ("Opções do CMake: use uma lista JSON, por exemplo [\"-DFEATURE=ON\"]"),
    ),
    (
        ("Elige una ruta local de Windows, por ejemplo C:/xsdk"),
        ("Choose a local Windows path, for example C:/xsdk"),
        ("Escolha um caminho local do Windows, por exemplo C:/xsdk"),
    ),
    (
        ("Falta o no se puede ejecutar"),
        ("Missing or not executable"),
        ("Ausente ou não executável"),
    ),
    (
        ("Faltan: "),
        ("Missing: "),
        ("Ausentes: "),
    ),
    (
        ("Compilador C/C++"),
        ("C/C++ compiler"),
        ("Compilador C/C++"),
    ),
    (
        ("Dependencias MSYS2"),
        ("MSYS2 dependencies"),
        ("Dependências MSYS2"),
    ),
    (
        ("Versión sin identificar"),
        ("Unidentified version"),
        ("Versão não identificada"),
    ),
    (
        ("Construcción registrada con este código"),
        ("Build recorded with this source"),
        ("Compilação registrada com este código"),
    ),
    (
        ("Receta registrada"),
        ("Recorded recipe"),
        ("Receita registrada"),
    ),
    (
        ("Receta cambió: revisar actualización (reconstrucción larga)"),
        ("Recipe changed: review update (long rebuild)"),
        ("Receita alterada: revise a atualização (recompilação longa)"),
    ),
    (
        ("Bibliotecas presentes; comprobar o reconstruir solo el SDK"),
        ("Libraries present; check or rebuild the SDK only"),
        ("Bibliotecas presentes; verifique ou recompile apenas o SDK"),
    ),
    (
        ("Herramientas host encontradas; no se reinstalan"),
        ("Host tools found; no reinstall"),
        ("Ferramentas host encontradas; não serão reinstaladas"),
    ),
    (
        ("Incluida en el toolchain; no se reconstruye por compilar un proyecto"),
        ("Included in toolchain; not rebuilt when building a project"),
        ("Incluída no toolchain; não é recompilada ao compilar um projeto"),
    ),
    (
        ("Disponible; parches sin registro (no se reconstruye automáticamente)"),
        ("Available; patches unrecorded (no automatic rebuild)"),
        ("Disponível; patches sem registro (sem recompilação automática)"),
    ),
    (
        ("Disponible; versión no demuestra que sea glslang-xenon"),
        ("Available; version does not prove it is glslang-xenon"),
        ("Disponível; a versão não comprova que seja glslang-xenon"),
    ),
    (
        ("Incompatible: target "),
        ("Incompatible target: "),
        ("Target incompatível: "),
    ),
    (
        ("Falta g++ o no se puede ejecutar; comprobar compilador"),
        ("g++ missing or not executable; check compiler"),
        ("g++ ausente ou não executável; verifique o compilador"),
    ),
    (
        ("Versión distinta; receta pide "),
        ("Different version; recipe requires "),
        ("Versão diferente; a receita exige "),
    ),
    (
        ("Remoto coincide"),
        ("Remote matches"),
        ("Remoto corresponde"),
    ),
    (
        ("Remoto distinto: actualizar disponible"),
        ("Remote differs: update available"),
        ("Remoto diferente: atualização disponível"),
    ),
    (
        ("No se pudo consultar el remoto"),
        ("Could not query remote"),
        ("Não foi possível consultar o remoto"),
    ),
    (
        ("Remoto consultado; instalación sin registro para comparar"),
        ("Remote checked; no installation record to compare"),
        ("Remoto consultado; instalação sem registro para comparar"),
    ),
    (
        ("Consulta los logs"),
        ("Check the logs"),
        ("Consulte os logs"),
    ),
    (
        ("Port experimental para Windows e interfaz: ZenithUzu, con asistencia de OpenAI Codex."),
        ("Experimental Windows port and interface: ZenithUzu, with OpenAI Codex assistance."),
        ("Port experimental para Windows e interface: ZenithUzu, com assistência do OpenAI Codex."),
    ),
    (
        ("Se conservan LICENSE y THIRD_PARTY_NOTICES.md."),
        ("LICENSE and THIRD_PARTY_NOTICES.md are preserved."),
        ("LICENSE e THIRD_PARTY_NOTICES.md foram preservados."),
    ),
    (
        ("Xenia y libxenon: componentes BSD según los avisos originales."),
        ("Xenia and libxenon: BSD components under their original notices."),
        ("Xenia e libxenon: componentes BSD conforme os avisos originais."),
    ),
    (
        ("GCC, binutils, newlib, glslang-xenon y MSYS2 conservan sus propias licencias."),
        ("GCC, binutils, newlib, glslang-xenon and MSYS2 retain their own licenses."),
        ("GCC, binutils, newlib, glslang-xenon e MSYS2 mantêm suas próprias licenças."),
    ),
    (
        ("No es un producto oficial de Microsoft ni de xenosworks."),
        ("Not an official Microsoft or xenosworks product."),
        ("Não é um produto oficial da Microsoft nem da xenosworks."),
    ),
    (
        ("No amplía el compilador de VS2010 y no requiere el XDK de Microsoft."),
        ("Does not extend the VS2010 compiler or require Microsoft XDK."),
        ("Não amplia o compilador do VS2010 nem exige o XDK da Microsoft."),
    ),
]

_CANONICAL = {value: row[0] for row in MESSAGES for value in row}


def translate(text, language="en"):
    if language not in LANGUAGES:
        language = "en"
    column = {"es": 0, "en": 1, "pt": 2}[language]
    if "\n" in text:
        return "\n".join(translate(line, language) for line in text.split("\n"))
    canonical = _CANONICAL.get(text, text)
    for row in MESSAGES:
        if row[0] == canonical:
            return row[column]
    # Only translate UI prefixes; leave paths, compiler logs and unknown text untouched.
    if " · Log: " in text:
        head, tail = text.split(" · Log: ", 1)
        return translate(head, language) + " · Log: " + tail
    if " · " in text:
        return " · ".join(translate(part, language) for part in text.split(" · "))
    for row in sorted(MESSAGES, key=lambda entry: max(map(len, entry)), reverse=True):
        for previous in row:
            if previous and text.startswith(previous) and len(previous) >= 6:
                return row[column] + text[len(previous):]
    return text
