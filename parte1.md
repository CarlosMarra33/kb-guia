# Memória funcional do agente — passo a passo completo de instalação

> **Para quê:** este arquivo é um roteiro para um agente de IA recriar, em outra máquina, **exatamente** o sistema de memória persistente montado aqui para o Devin CLI:
>
> - as bases de conhecimento em Markdown, uma global e uma por projeto;
> - as 4 skills `kb` (`kb`, `kb-buscar`, `kb-salvar`, `kb-mapear`) e a skill `token-efficiency`;
> - o motor `kb.py`;
> - os 6 hooks globais: 4 do kb e 2 do graphify;
> - as regras globais (`AGENTS.md`);
> - o graphify.
>
> **Autossuficiente:** o conteúdo integral de cada arquivo está no Apêndice A, com o hash SHA-256 de cada um. O Apêndice B instala tudo com um comando e o Apêndice C confere a instalação. Nenhum outro arquivo é necessário.
>
> Gerado em {{DATA}} a partir das cópias instaladas e em uso na máquina de origem. Os documentos de projeto (`skill-conhecimento-DECISOES.md`, `skill-conhecimento-POSSIBILIDADES.md`, `skill-conhecimento-PACOTE.md` e `graphify-ANALISE.md`) contam a história e as alternativas, mas não são necessários para instalar.

## Sumário

{{SUMARIO}}

## 0. Leia primeiro — instruções para o agente executor

### 0.1 Objetivo e critério de pronto

Recrie nesta máquina o sistema descrito aqui, idêntico ao da origem. A instalação só está pronta quando **todos** os itens abaixo forem verdadeiros:

1. O verificador (Apêndice C) termina com `RESULTADO: tudo certo`.
2. Numa sessão **nova** do Devin, `/hooks` lista os 4 hooks do kb (`SessionStart`, `UserPromptSubmit`, `PostToolUse` e `Stop`) e, se o graphify foi instalado, os 2 `PreToolUse` dele.
3. Na sessão nova, o agente recebe no contexto o bloco `[kb] Bases de conhecimento` no início. A cada mensagem com conteúdo, recebe também `[kb] Candidatos…` ou `[kb] Sem candidatos…`.
4. Ao digitar `/` aparecem `/kb`, `/kb-buscar`, `/kb-salvar`, `/kb-mapear` e `/token-efficiency`.
5. O teste ponta a ponta da seção 10.3 passa.

### 0.2 Regras de execução (obrigatórias)

1. **Siga as fases na ordem.** Cada fase termina com uma verificação. Não avance se ela falhar: corrija antes (a seção 16.1 lista os problemas conhecidos).
2. **Arquivos idênticos, byte a byte.** O conteúdo está no Apêndice A. Grave em UTF-8 **sem BOM**, com fim de linha **LF** (não CRLF) e exatamente **uma** quebra de linha no fim. Não traduza, não reformate e não "corrija" nada, nem o que parecer erro de digitação. O instalador (Apêndice B) grava tudo exatamente assim; prefira-o a digitar arquivo por arquivo.
3. **Nunca sobrescreva configuração existente.** O `config.json` e o `AGENTS.md` podem já ter conteúdo do usuário, como hooks de outras ferramentas ou outras regras: faça merge. O instalador guarda uma cópia de tudo o que alterar em `<config>\backup-kb\<data-hora>\`.
4. **Não copie valores específicos da origem.** Caminhos como `C:/Users/aquin/.../python.exe` e `C:/Users/carlos/...`, e o `org_id` do `config.json`, pertencem à máquina de origem. Os comandos dos hooks do kb são gerados por `kb.py instalar-hooks` com os caminhos da máquina atual.
5. **Rode o `instalar-hooks` sempre a partir da cópia instalada** (`<skills>\kb\scripts\kb.py`). Os hooks apontam para o script que executou o comando. Se ele rodar de uma pasta temporária, os hooks vão apontar para um arquivo que vai sumir.
6. **As 4 pastas `kb*` ficam lado a lado** no mesmo diretório de skills, porque `kb-buscar`, `kb-salvar` e `kb-mapear` leem `../kb/references/schema.md` e `../kb/templates/`.
7. **Nunca grave segredos:** nada de senhas, tokens, chaves ou connection strings em nenhuma base nem em qualquer arquivo deste processo.
8. **Pergunte ao usuário antes de:** instalar pacotes (o graphify, via `pip`), mexer em arquivos que não fazem parte deste sistema ou apagar qualquer coisa que você não criou. Criar os arquivos e diretórios deste guia não precisa de confirmação.
9. **Hooks e regras só carregam em sessão nova.** Ao terminar, peça ao usuário para fechar e reabrir o Devin e siga a seção 10.2 na sessão nova.
10. **Entregue um relatório final ao usuário** com o que foi instalado, o resultado do verificador, as pendências e o que ele precisa fazer: abrir uma sessão nova, conferir com `/hooks` e rodar `/kb-mapear` no primeiro projeto.

### 0.3 Três caminhos

| Caminho | Quando usar | Sequência |
|---|---|---|
| **Rápido (recomendado)** | Há Python no PATH | Fase 0 (§3) → Fase 1, graphify, se o usuário quiser (§4) → instalador (§5), que faz as Fases 2 a 5 → Fase 6, verificação (§10) → Fase 7 (§11) |
| **Manual** | Não é permitido rodar o instalador, ou você quer entender cada peça | Fases 0 a 7 na ordem: §3, §4, §6, §7, §8, §9, §10 e §11 |
| **Sem Python** (modo só-prompt) | Python proibido na máquina | Crie os arquivos (§6), crie a base à mão (§7.2), pule os hooks do kb (§8.3) e mantenha as regras (§9). As notas funcionam igual, mas sem automação: não há bloco `[kb]` nem lembrete de salvar |

Os caminhos rápido e manual chegam ao mesmo resultado, conferido pelo mesmo verificador.

### 0.4 O que confirmar com o usuário antes de começar

| Pergunta | Resposta padrão (como na origem) |
|---|---|
| Instalar o graphify (CLI, skill, 2 hooks e regra)? Exige `pip` e acesso ao PyPI | Sim |
| Tornar `/graphify` visível no Windows, copiando a skill para `%APPDATA%\devin\skills\graphify`? | Não. Na origem a skill ficou num caminho que o Devin no Windows não lê (§4.3 e §17). Recomende "sim" se o usuário quiser usar o `/graphify` |
| Guardar a base global em outro lugar (`KB_HOME`)? | Não: fica em `%USERPROFILE%\kb` |

## 1. O que é o sistema

### 1.1 Componentes

É uma memória persistente para o agente, feita de notas Markdown no estilo Obsidian. **O texto é a fonte da verdade:** o índice é derivado e pode ser apagado a qualquer momento. Nenhuma lib externa: o motor usa só a biblioteca padrão do Python. O agente é o operador principal da base: pesquisa, escreve, liga e mantém as notas. O humano pode ler e editar no Obsidian, se quiser.

| Peça | Onde fica (Windows) | Para que serve |
|---|---|---|
| Base global | `%USERPROFILE%\kb` | Conhecimento comum a todos os projetos: bugs e correções, padrões técnicos, stack, pessoas, equipes, processos, reuniões, decisões transversais e um hub por projeto |
| Base do projeto | `<repo>\docs\kb` | Regras de negócio, glossário do domínio, fluxos, módulos, decisões do projeto e `_MAPA.md`. É versionada com o código |
| Skill `kb` | `<skills>\kb\` | Núcleo: schema das notas, 11 templates, o motor `kb.py` e os comandos manuais `/kb …` |
| Skill `kb-buscar` | `<skills>\kb-buscar\` | Como consultar as bases antes de agir, na ordem que a intenção pede |
| Skill `kb-salvar` | `<skills>\kb-salvar\` | Quando, onde e como salvar o que foi aprendido |
| Skill `kb-mapear` | `<skills>\kb-mapear\` | Primeira varredura de um projeto, ou varredura incremental |
| Skill `token-efficiency` | `<skills>\token-efficiency\` | Hábitos de economia de tokens. É complementar e anterior ao kb |
| `kb.py` | `<skills>\kb\scripts\kb.py` | Motor em Python stdlib: resolve as bases, cria as bases, faz o inventário, busca, indexa, trata os hooks e instala os hooks |
| 4 hooks do kb | `config.json` global do Devin | Tornam automáticos a busca a cada mensagem e o lembrete de salvar |
| graphify (CLI) | pacote PyPI `graphifyy` | Grafo de conhecimento do código de um projeto (`graphify-out/`), consultado com `graphify query`, `path` e `explain` |
| 2 hooks do graphify | `config.json` global do Devin | Antes de `exec`, `grep`, `read` e `glob`, lembram de consultar o grafo quando ele existe |
| Skill `graphify` | `%USERPROFILE%\.config\devin\skills\graphify\` | Pipeline `/graphify`, instalada pelo próprio graphify (§4.3) |
| Regras globais | `%APPDATA%\devin\AGENTS.md` | Sempre no contexto: usar o `gh` para o GitHub, quando usar o graphify e como usar as bases kb |

`<skills>` é `%APPDATA%\devin\skills` no Windows e `~/.config/devin/skills` no Linux/macOS (tabela completa em §3.1).

### 1.2 Como as peças conversam numa sessão

```
Sessão nova
  ├─ AGENTS.md global entra no contexto (regras gh / graphify / kb)
  └─ SessionStart ──► kb.py hook session ──► "[kb] Bases de conhecimento…"
                                              bases ativas, nº de notas, se o projeto foi mapeado, lições

Cada mensagem do usuário
  └─ UserPromptSubmit ──► kb.py hook prompt ──► "[kb] Candidatos nas bases…" (até 4 por base)
                                                 ou "[kb] Sem candidatos…"; nada em "ok"/"valeu" e em /comandos
                                                 marca "hint" se a mensagem parece regra ou decisão

O agente decide (skill kb-buscar) quais notas abrir e em que ordem, e trabalha:
  ├─ exec / grep  ──► PreToolUse ──► graphify hook-guard search ─┐ lembrete se existir
  ├─ read / glob  ──► PreToolUse ──► graphify hook-guard read   ─┘ graphify-out/graph.json
  └─ edit / write / apply_patch / notebook_edit
                  ──► PostToolUse ──► kb.py hook track ──► marca "code" (código) ou "kb" (nota numa base)

O agente vai encerrar
  └─ Stop ──► kb.py hook stop ──► se houve "code" ou "hint" e nenhum "kb" nesta rodada:
                                  pede UMA vez para avaliar a skill kb-salvar

kb-salvar grava a nota na base certa, atualiza o _INDEX.md e avisa numa linha:
  kb: + [[Nota nova]] (global) · ~ [[Nota atualizada]] (projeto)
```

### 1.3 As duas bases

| Base | Onde | O que guarda | Versionada? |
|---|---|---|---|
| **Global** | `%USERPROFILE%\kb` (ou `KB_HOME`) | Bugs e correções, padrões técnicos, stack e sistemas, pessoas, equipes, processos de trabalho, reuniões, decisões transversais e um hub por projeto | Não, é pessoal |
| **Projeto** | `<raiz do repo>\docs\kb` | Regras de negócio, glossário do domínio, fluxos de negócio, módulos, decisões do projeto e `_MAPA.md` | Sim, vai para o git junto com o código |

- **Regra de roteamento:** "isso serve para outro projeto?" Se serve, vai para a global. Se só faz sentido neste domínio, vai para o projeto. Um bug vai para a global mesmo que só tenha acontecido num projeto, com `ocorre_em:: [[Projeto]]`.
- **A base do projeto existe** quando há `docs/kb/_INDEX.md` no repo. Ela é compartilhada com o time, então não pode ter nada pessoal, sensível ou opinativo sobre pessoas, nem caminhos da sua máquina.
- **Links entre bases:** `[[Título]]` resolve primeiro na base atual e depois na outra. No Obsidian, os links para a outra base aparecem como não resolvidos, e isso é esperado.

### 1.4 As três camadas do "automático"

| Camada | Garante? | Papel |
|---|---|---|
| **Hooks** (`config.json`) | Sim: rodam sempre, fora do modelo | Entregam os candidatos a cada mensagem e lembram de salvar |
| **Regras** (`AGENTS.md`) | Quase: estão sempre no contexto, mas dependem de o modelo obedecer | Dizem "consulte antes, salve na hora" e apontam as skills |
| **Skills** | Não: o modelo decide carregar (trigger `model`) ou o usuário chama com `/nome` | Trazem o passo a passo detalhado |

Por isso os hooks entraram já na primeira entrega (decisão D15): só eles garantem o "sempre".

## 2. Inventário exato da máquina de origem

### 2.1 O que faz parte do sistema (recriar)

| # | Caminho na origem | Criado por | Conteúdo |
|---|---|---|---|
| 1 | `%APPDATA%\devin\skills\kb\` | à mão (Apêndice A) | `SKILL.md`, `references\` (2 arquivos), `templates\` (11) e `scripts\kb.py`: 15 arquivos |
| 2 | `%APPDATA%\devin\skills\kb-buscar\SKILL.md` | à mão | Skill de busca |
| 3 | `%APPDATA%\devin\skills\kb-salvar\SKILL.md` | à mão | Skill de salvamento |
| 4 | `%APPDATA%\devin\skills\kb-mapear\SKILL.md` | à mão | Skill de mapeamento |
| 5 | `%APPDATA%\devin\skills\token-efficiency\SKILL.md` | à mão, antes do kb | Skill de economia de tokens |
| 6 | `%APPDATA%\devin\config.json`, chave `hooks` | `kb.py instalar-hooks` (4) e à mão (2 do graphify) | 6 hooks (§8.4) |
| 7 | `%APPDATA%\devin\AGENTS.md` | à mão | 3 blocos: `# Regras globais` (gh), `## graphify` e `## kb` ({{A:@AGENTS.md}}) |
| 8 | `%USERPROFILE%\kb\` | `kb.py init` | Base global: 13 pastas, `.kb\`, `_INDEX.md` e `LESSONS.md`. Tinha 0 notas na origem |
| 9 | graphify 0.9.55 | `python -m pip install graphifyy` | `graphify.exe` em `<Python>\Scripts` |
| 10 | `%USERPROFILE%\.config\devin\skills\graphify\` | `graphify devin install` | `SKILL.md` (63.697 bytes) e `.graphify_version` (`0.9.55`) |

Gerados sozinhos durante o uso (não recrie):

- `%APPDATA%\devin\config.json.bak`: backup automático feito pelo `instalar-hooks`.
- `%TEMP%\devin-kb-hook\`: estado dos hooks por sessão e `erros.log`. É descartável.
- `<base>\.kb\index.json`: índice derivado de cada base.

### 2.2 Fora do escopo (não recrie)

- **Demais chaves do `config.json` da origem:** `version`, `devin.org_id`, `shell.setup_complete`, `theme_mode`, `agent.model` e `permissions` (`Exec(devin plugins)`). São da conta e da máquina; o `config.json` da máquina nova já tem as dele.
- **`%APPDATA%\devin\mcp_config.json`** (servidor MCP de terceiros) e **`credentials.toml`:** não têm relação com a memória.
- **`%USERPROFILE%\.codeium\windsurf\memories\global_rules.md`:** regras globais do Windsurf. Estava vazio na origem.
- **`%TEMP%\kb-skill-anterior-2026-09-26\`:** backup da versão antiga da skill `kb`.
- **O plugin local `token-efficiency`:** está inativo (§2.4).
- **Plugins gerenciados pela conta do Devin** (`%APPDATA%\devin\cli\plugins\`): são definidos pela organização, não pelo usuário.
- **A pasta de trabalho do projeto:** os documentos de decisão, o `skill-conhecimento-PACOTE.md` e o clone do graphify em `graphify/`, que serviu só para a análise.

### 2.3 Ambiente de origem (versões testadas)

| Item | Na origem | Exigência |
|---|---|---|
| Sistema | Windows, PowerShell 5.1 | Windows, Linux ou macOS |
| Devin CLI | 3000.6.14 | Versão com skills e hooks |
| Python | 3.13.5 (SQLite 3.49.1) | 3.7 ou superior no PATH; o kb usa só a stdlib |
| git | 2.43.0.windows.1 | Recomendado: raiz do repo, nome do projeto e inventário |
| GitHub CLI `gh` | 2.100.0 | Exigido pela regra global de GitHub |
| graphify (`graphifyy`) | 0.9.55 | Opcional |
| Node | 22.13.1 | Não é usado |

### 2.4 Plugin local `token-efficiency` (existe na origem, mas inativo)

A origem tem também `%APPDATA%\devin\plugins\token-efficiency\`, a fonte de um plugin do Devin criado junto com a skill `token-efficiency`. São 3 arquivos:

- `.devin-plugin\plugin.json`;
- `AGENTS.md`, a regra always-on do plugin;
- `skills\token-efficiency\SKILL.md`, idêntico a {{A:token-efficiency/SKILL.md}}.

O plugin **não está instalado**:

- o registro de plugins do CLI (`%APPDATA%\devin\cli\plugins\lock.json`) não o lista entre os resolvidos;
- a regra dele não aparece nas sessões;
- a skill ativa é a global.

Por isso **não o recrie** por padrão.

Se o usuário quiser o plugin e aceitar a regra dele em toda sessão:

1. Crie os 3 arquivos: os dois abaixo e a cópia de {{A:token-efficiency/SKILL.md}}.
2. Rode `devin plugins install "$env:APPDATA\devin\plugins\token-efficiency"`, que exige `devin auth login`.
3. A skill passa a aparecer também como `/token-efficiency:token-efficiency`.

`plugin.json`:

```json
{{PLUGIN_JSON}}
```

`AGENTS.md` do plugin:

```markdown
{{PLUGIN_AGENTS}}
```

## 3. Fase 0 — pré-requisitos e preparação

### 3.1 Caminhos por sistema operacional

| Nome neste guia | Windows | Linux/macOS |
|---|---|---|
| `<config>` (config do Devin) | `%APPDATA%\devin` (em geral `C:\Users\<você>\AppData\Roaming\devin`) | `~/.config/devin` |
| `<skills>` (skills globais) | `%APPDATA%\devin\skills` | `~/.config/devin/skills` |
| Hooks globais | `%APPDATA%\devin\config.json`, chave `hooks` | `~/.config/devin/config.json` |
| Regras globais | `%APPDATA%\devin\AGENTS.md` | `~/.config/devin/AGENTS.md` |
| `<kb-global>` (base global) | `%USERPROFILE%\kb` ou `KB_HOME` | `~/kb` ou `$KB_HOME` |
| Base do projeto | `<repo>\docs\kb` | `<repo>/docs/kb` |
| Estado dos hooks | `%TEMP%\devin-kb-hook\` | `<tmp>/devin-kb-hook/` (em geral `/tmp`) |
| Skill do graphify (`graphify devin install`) | `%USERPROFILE%\.config\devin\skills\graphify` (o Devin no Windows **não lê**) | `~/.config/devin/skills/graphify` (lido) |

Nos comandos PowerShell deste guia, `%APPDATA%` vira `$env:APPDATA` e `%USERPROFILE%` vira `$env:USERPROFILE`. No Linux/macOS, troque `python` por `python3` se for o caso.

### 3.2 Verificar as ferramentas

PowerShell:

```powershell
devin --version
python --version
python -c "import sys, sqlite3; print(sys.executable); print(sqlite3.sqlite_version)"
git --version
gh --version
gh auth status
```

bash (Linux/macOS):

```bash
devin --version; python3 --version; python3 -c "import sys; print(sys.executable)"; git --version; gh --version
```

Confira:

- **Python 3.7 ou superior.** O `sys.executable` impresso é o Python que os hooks vão usar.
- **git e gh presentes.** Sem git, o kb funciona, mas não detecta a raiz do repo sozinho: use `--raiz` nos comandos. Sem gh, a regra global manda pedir confirmação antes de usar qualquer alternativa para o GitHub. Instale-o se o usuário trabalha com GitHub.
- **Devin CLI presente.** As skills e os hooks são deste cliente. Para outro agente, veja o Apêndice D.

### 3.3 Armadilhas conhecidas do Python

- **Alias da Microsoft Store:** se `python --version` não imprime nada ou abre a Store, não há Python de verdade instalado. Instale o Python (python.org, marcando "Add python.exe to PATH") e abra um terminal novo. Se só existir o launcher `py`, use `py -3` no lugar de `python`.
- **Espaço no caminho do Python** (por exemplo, `C:\Users\João Silva\...`): o `instalar-hooks` grava só `python` no comando para evitar problema de aspas. Nesse caso, `python` precisa estar no PATH do shell que o Devin usa.
- **Python trocado ou reinstalado:** rode `kb.py instalar-hooks` de novo, porque o caminho do Python fica gravado nos hooks.
- **Pipe do PowerShell 5.1 em ASCII:** texto acentuado passado por `|` vira `?`. Nos testes manuais de hook (§8.6) use só ASCII no JSON.
- **Console em cp1252 ou cp850:** o `kb.py` força UTF-8 na saída e os hooks respondem em JSON ASCII. Acentos estranhos no terminal são só cosméticos.
- **ExecutionPolicy do PowerShell:** não afeta nada, porque o sistema não usa `.ps1`.

### 3.4 Backup do que já existe

O instalador faz backup sozinho. No caminho manual, faça antes:

```powershell
$cfg = "$env:APPDATA\devin"
$bk  = "$cfg\backup-kb\manual-$(Get-Date -Format yyyyMMdd-HHmmss)"
New-Item -ItemType Directory -Force "$bk\skills" | Out-Null
foreach ($f in 'config.json', 'AGENTS.md') { if (Test-Path "$cfg\$f") { Copy-Item "$cfg\$f" $bk } }
foreach ($s in 'kb', 'kb-buscar', 'kb-salvar', 'kb-mapear', 'token-efficiency') {
  if (Test-Path "$cfg\skills\$s") { Copy-Item -Recurse "$cfg\skills\$s" "$bk\skills\$s" }
}
"backup em $bk"
```

Veja também se já existe uma base global com notas (`Test-Path "$env:USERPROFILE\kb\_INDEX.md"`). Se existir, **mantenha**: o `kb.py init` nunca sobrescreve notas, só completa o que falta.

**Verificação da Fase 0:** as ferramentas respondem, o Python é real e o backup foi feito (ou não havia nada a guardar).

## 4. Fase 1 — graphify (opcional; faz parte da origem)

O graphify transforma o código de um projeto num grafo persistente em `graphify-out/graph.json`. Com `--code-only`, a extração é local (AST), sem chave de API. O agente consulta o grafo com `graphify query`, `path` e `explain` em vez de reler arquivos brutos.

Neste setup ele complementa o kb: o kb guarda **conhecimento** (regras, bugs, decisões) e o graphify mapeia a **estrutura do código**. As skills `kb-buscar` e `kb-mapear` usam o `graphify-out/` quando ele existe, mas nunca geram o grafo sem o usuário pedir.

**Faça esta fase antes do instalador (§5)**, para que ele registre os hooks do graphify. Se instalar o graphify depois, basta rodar o instalador de novo.

### 4.1 Instalar o CLI

```powershell
python -m pip install graphifyy==0.9.55
graphify --version
```

Saída esperada do segundo comando: `graphify 0.9.55`.

- O pacote tem **dois "y"** (`graphifyy`); o comando é `graphify`.
- **`graphify` não encontrado:** a pasta de scripts do Python não está no PATH. Descubra qual é com `python -c "import sysconfig; print(sysconfig.get_path('scripts'))"`, inclua-a no PATH do usuário e abra um terminal novo. Com `pip install --user`, a pasta é outra (`%APPDATA%\Python\Python3XX\Scripts`).
- **Alternativas isoladas:** `uv tool install graphifyy==0.9.55` ou `pipx install graphifyy==0.9.55`. A documentação do graphify recomenda essas duas para evitar divergência de interpretador. A origem usou `pip`.
- Existem versões mais novas, mas não foram testadas com este setup.

### 4.2 Registrar a skill no Devin

```powershell
graphify devin install
```

Na versão 0.9.55, esse comando **só** copia a skill para `~/.config/devin/skills/graphify/SKILL.md` e grava `.graphify_version` com `0.9.55`. A saída termina com `Done. Open your AI coding assistant and type:` seguido de `/graphify .`.

Ele **não** registra hooks nem mexe no `AGENTS.md`. Isso é feito em §8.2 e §9. Existe também `graphify devin install --project`, que instala em `.devin/skills/graphify/` do projeto atual e cria `.windsurf/rules/graphify.md`, mas a origem não usou.

Verificação:

```powershell
Test-Path "$HOME\.config\devin\skills\graphify\SKILL.md"
Get-Content "$HOME\.config\devin\skills\graphify\.graphify_version"
```

Saída esperada: `True` e `0.9.55`.

### 4.3 (Opcional, não feito na origem) Tornar `/graphify` visível no Windows

No Windows, o Devin lê as skills globais de `%APPDATA%\devin\skills\`, e não de `~/.config/devin/skills/`. Por isso, na origem, `/graphify` **não aparece** como skill. A regra do `AGENTS.md` e os hooks continuam funcionando, porque usam o CLI. Se o usuário quiser a skill:

```powershell
Copy-Item -Recurse -Force "$HOME\.config\devin\skills\graphify" "$env:APPDATA\devin\skills\graphify"
```

O frontmatter dessa skill tem `model: sonnet` e `allowed-tools: read, grep, glob, exec`. Depois de atualizar o graphify, repita a cópia. No Linux/macOS não há nada a fazer, porque o caminho padrão já é lido.

### 4.4 O que o graphify acrescenta nas próximas fases

- **§8.2:** 2 hooks `PreToolUse`, `graphify hook-guard search` e `graphify hook-guard read`. O instalador registra os dois sozinho se o comando `graphify` estiver no PATH.
- **§9:** a seção `## graphify` do `AGENTS.md`. O instalador acrescenta sempre, porque ela só age quando existe `graphify-out/`.

### 4.5 Uso por projeto (referência rápida)

```powershell
cd <repo>
graphify extract . --code-only        # indexa o código localmente (AST, sem chave de API) → graphify-out/
graphify query "como a autenticação chega ao banco?"
graphify path "UserService" "DatabasePool"
graphify explain "RateLimiter"
graphify update .                     # depois de mudar código: só AST, sem custo
graphify hook install                 # opcional: git hooks post-commit/post-checkout que atualizam o grafo
```

Os artefatos ficam em `graphify-out/`: `graph.json`, `GRAPH_REPORT.md`, `graph.html`, `cache/` e `manifest.json`. `.graphify_root` e `.graphify_python` são locais e não devem ser commitados. Para compartilhar com o time: `git add -f graphify-out/graph.json graphify-out/GRAPH_REPORT.md`.

**Verificação da Fase 1:** `graphify --version` mostra `graphify 0.9.55` e a skill existe em `~/.config/devin/skills/graphify/`.
