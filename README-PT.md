<div align="center">
  <img src="assets/xsdk.png" alt="xSDK" width="640">
</div>

<p align="center">
  <a href="README.md"><img src="assets/languages/english.svg" alt="Read in English" width="140" height="36"></a>
  <a href="README-ES.md"><img src="assets/languages/espanol.svg" alt="Leer en español" width="140" height="36"></a>
  <a href="README-PT.md"><img src="assets/languages/portugues.svg" alt="Ler em português" width="140" height="36"></a>
</p>

# xSDK para Windows

**Crie homebrew para Xbox 360 no Windows. Gerencie suas ferramentas, compile shaders e transforme projetos C/C++ compatíveis em títulos `.xex` por uma interface gráfica.**

Este fork experimental do [xenosworks/xsdk](https://github.com/xenosworks/xsdk) usa **MSYS2 UCRT64**. A interface oferece **inglês, espanhol e português**. Use a branch **`main`**.

[Baixar ZIP](https://github.com/ZenithUzu/xsdk/archive/refs/heads/main.zip) · [Manual do Windows — espanhol](README-WINDOWS.md) · [Receitas — EN / ES / PT](README-PROJECTS.md) · [README original](README-UPSTREAM.md) · [Estado das compilações](https://github.com/ZenithUzu/xsdk/actions)

## Recursos

- Detecta e reutiliza ferramentas instaladas, sem reconstruir o compilador a cada projeto.
- Mostra versões de GCC/G++, binutils, newlib, ferramentas de shaders e bibliotecas do SDK.
- Permite configurar caminhos de MSYS2, compilador PowerPC, xSDK, glslang e SDL3 Xenon.
- Compila projetos CMake compatíveis, exemplos e ports com receitas `xsdk-project.json`.
- Verifica os requisitos da receita antes de compilar; ROM e assets continuam como entradas privadas locais.
- Oferece Release, Debug, RelWithDebInfo e MinSizeRel, com controle de tarefas simultâneas.
- Alterna entre inglês, espanhol e português e salva o idioma e os caminhos.
- Exibe logs ao vivo, permite cancelar tarefas e abrir resultados.
- Consulta atualizações e atualiza componentes separadamente. A atualização automática do código é opcional e vem desativada.
- Gera pacotes portáteis com fontes correspondentes, licenças e checksums SHA-256.

Abrir a interface apenas verifica as ferramentas; não reconstrói GCC, newlib ou shaders automaticamente. Encontrar uma versão não comprova que ela contém os patches necessários para Xenon.

## Requisitos

| Componente | Finalidade |
| --- | --- |
| Windows 10/11 de 64 bits | Sistema do computador |
| Python 3.11+ com tkinter | Interface; inicializador `py` ou Python UCRT64 no caminho padrão |
| MSYS2 UCRT64 | Ambiente e ferramentas de compilação |
| GCC/G++ PowerPC do xSDK, binutils e newlib | Compilar e vincular código para Xbox 360 |
| glslang-xenon e bibliotecas compiladas do xSDK | Shaders e runtime |
| SDL3 Xenon compilado | Apenas para projetos que usam SDL3 |

A receita usa GCC 15.3.0, binutils 2.47 e newlib 4.6.0.20260123 com os patches do xSDK. GCC PowerPC genérico e SDL de desktop não substituem essas ferramentas. Este fluxo não exige Debian/WSL, VS2010 ou Microsoft XDK.

## Instalação

### Já tem as ferramentas?

1. Baixe `main` para um caminho sem espaços, como `C:\xsdk-windows`. Preserve suas pastas de compilador e trabalho.
2. Abra **Iniciar-Windows.cmd** e selecione **Português** no topo.
3. Use **Detectar / verificar**. Configure os caminhos ausentes em **Caminhos e projeto**.
4. Se atualizou o runtime do SDK, use **Recompilar apenas o SDK** e recompile o projeto.
5. Escolha o projeto, selecione **Release** para comparar desempenho e use **Compilar projeto**.

### Começando do zero

1. Instale [Python](https://www.python.org/downloads/windows/) com tkinter e o inicializador `py`.
2. Instale [MSYS2](https://www.msys2.org/), abra **UCRT64** e execute `pacman -Syu`. Se solicitado, reinicie o terminal e repita.
3. Baixe ou clone este repositório para um caminho sem espaços e abra **Iniciar-Windows.cmd**.
4. Em **Instalação e testes avançados**, execute uma etapa por vez: **Dependências → Compilar compilador → Compilar ferramentas de shaders → Compilar SDK → Exemplos**.
5. Espere cada etapa terminar com sucesso. Compile SDL3 separadamente se o projeto precisar dele.

Construir o compilador pode demorar bastante; pule essa etapa se já possui ferramentas compatíveis. [Instalar-Windows.ps1](Instalar-Windows.ps1) prepara uma cópia Git em uma pasta nova, mas não instala Python ou MSYS2.

## Uso

| Campo | Valor habitual |
| --- | --- |
| MSYS2 | `C:/msys64` |
| Código do xSDK | `C:/xsdk-windows` |
| Raiz do compilador instalado | `C:/xsdk-tools/compiler` |
| Pasta de trabalho | `C:/xsdk-tools/work` |
| Executável glslang | `C:/xsdk-tools/compiler/bin/glslang.exe` |
| SDL3_DIR | `C:/SDL-xenon/build-xsdk`, se necessário |

Para um **projeto CMake genérico**, selecione a pasta com seu `CMakeLists.txt` compatível. Comece com Release, opções adicionais `[]` e quatro tarefas.

Para **CoopDX360**, selecione a **raiz do repositório** com `xsdk-project.json`. Indique o SDL3 Xenon compilado e, opcionalmente, sua ROM privada dos EUA. Use **Verificar receita do port** e depois **Compilar projeto**. A restauração de entradas herdadas é explícita e vem desativada; use apenas com permissão para essas entradas. Veja a [documentação de receitas](README-PROJECTS.md).

Os resultados das receitas ficam em `<trabalho>/projects/<nome-do-repositório>/`. **Abrir resultados** abre essa pasta; projetos genéricos e exemplos usam o diretório de compilação do SDK. A receita CoopDX gera `build-info.json` local com configuração, revisão do código e hashes dos executáveis. Não há transferência ou execução automática no console.

## Compilar SDL3 Xenon

Compile xSDK primeiro. Abra **MSYS2 UCRT64**, adapte os caminhos e clone para uma pasta nova:

```bash
git clone --branch xenon https://github.com/xenosworks/SDL-xenon.git /c/SDL-xenon
cmake -S C:/SDL-xenon -B C:/SDL-xenon/build-xsdk -G Ninja -DCMAKE_TOOLCHAIN_FILE=C:/xsdk-windows/cmake/xsdk.cmake -DXSDK_TOOLCHAIN=C:/xsdk-tools/compiler -DCMAKE_BUILD_TYPE=Release
cmake --build C:/SDL-xenon/build-xsdk --parallel 4
```

Depois de compilar com sucesso, coloque `C:/SDL-xenon/build-xsdk` em **SDL3_DIR**. A pasta deve conter `SDL3Config.cmake`. Use SDL3 para Xbox, não SDL3 de desktop.

SDL-xenon fornece áudio, controles, threads e temporizadores. Essa adaptação não fornece um driver próprio de vídeo/render para Xbox; cada projeto usa seu backend gráfico. Preencher SDL3_DIR não adiciona chamadas SDL ao código do projeto. Consulte o [manual do Windows](README-WINDOWS.md#sdl3-opcional) e a [documentação SDL-xenon](https://github.com/xenosworks/SDL-xenon/blob/xenon/docs/README-xsdk.md).

## Atualizações

| Componente alterado | Próximo passo |
| --- | --- |
| Interface ou documentação | Atualizar o código e reabrir a interface |
| Runtime/GPU do xSDK | Atualizar, recompilar o SDK e os projetos afetados |
| Código do projeto | Recompilar o projeto |
| Compilador de shaders | Atualizar/compilar as ferramentas de shaders e os projetos afetados |
| GCC, binutils, newlib ou seus patches | Revisar e construir explicitamente um compilador novo |

Uma instalação sem registro não está automaticamente desatualizada. Metadados e versões têm limites; a ferramenta não certifica todos os patches do compilador nem todas as funções do SDK.

## Exemplos e validação

Os exemplos incluem `hello`, `triangle`, `cube`, `sound`, `template` e `sdl3`, quando SDL-xenon está disponível. As variantes `break` são propositalmente defeituosas e devem falhar nas verificações.

Em 3 de novembro de 2026, **26 testes locais no computador passaram**, incluindo troca de idioma e compatibilidade das receitas entre Windows PowerShell 5 e PowerShell 7. Uma pasta de saída nova do CoopDX compilou shaders e objetos do jogo e gerou o XEX e o relatório local. Isso não comprova desempenho nem funcionamento correto no console.

O hardware precisa de testes separados. A estática na entrada/saída continua pendente de validação, e um workflow de pacote não significa que exista um pacote completo pré-compilado disponível. Consulte [Actions](https://github.com/ZenithUzu/xsdk/actions), [observações de hardware](docs/HARDWARE.md) e o [estado detalhado em espanhol](README-ES.md#estado-y-límites). Não há garantia de FPS.

## Documentação e créditos

- [Manual do Windows, SDL3, opções e solução de problemas — espanhol](README-WINDOWS.md)
- [Receitas de ports — English / Español / Português](README-PROJECTS.md)
- [README original](README-UPSTREAM.md), [guia de programação](docs/GUIDE.md) e [recursos disponíveis](docs/PARITY.md)
- [Licença MIT](LICENSE) e [avisos de terceiros](THIRD_PARTY_NOTICES.md)

**xSDK original:** Mena / xenosworks e colaboradores. Os créditos e avisos originais, incluindo Xenia e libxenon, foram preservados. **Adaptação para Windows:** ZenithUzu, com assistência do OpenAI Codex. GCC, binutils, newlib, glslang e MSYS2 mantêm suas próprias licenças. Este fork não é uma publicação oficial da Microsoft nem da xenosworks.
