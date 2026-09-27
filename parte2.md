## 5. Caminho rápido — instalador automático (Fases 2 a 5)

### 5.1 Comando

Abra um terminal **na pasta onde está este arquivo** e rode (funciona em PowerShell, cmd e bash):

```
python -c "t=open('skill-conhecimento-PASSO-A-PASSO.md',encoding='utf-8').read();a='#'*3+' INSTALADOR';exec(t[t.index(a+' INICIO'):t.index(a+' FIM')])"
```

- **Arquivo renomeado:** troque o nome dentro do comando.
- **Sem `python` no PATH:** use `py -3 -c "..."` ou `python3 -c "..."`. Esse Python é o que os hooks vão usar (§3.3).
- **Por que `'#'*3`:** o comando monta o marcador em tempo de execução para não achar a si mesmo dentro deste documento.

### 5.2 O que o instalador faz, na ordem

1. **Grava as skills.** Lê cada bloco do Apêndice A marcado com o comentário invisível `kb-arquivo` e grava em `<skills>\<caminho>`: 19 arquivos das skills `kb`, `kb-buscar`, `kb-salvar`, `kb-mapear` e `token-efficiency`. A gravação é byte a byte: UTF-8 sem BOM, LF e quebra de linha final. Arquivo igual é mantido; arquivo diferente vai antes para `<config>\backup-kb\<data-hora>\skills\…`.
2. **Registra os hooks do graphify.** Só acontece se o comando `graphify` estiver no PATH. Acrescenta em `config.json → hooks → PreToolUse` os 2 grupos da §8.2, se ainda não houver nenhum hook com `graphify hook-guard`. Isso vem antes dos hooks do kb, como na origem. O `config.json` original vai antes para o backup.
3. **Cria a base global.** Roda `kb.py init`, que cria ou completa `<kb-global>` (§7).
4. **Registra os hooks do kb.** Roda `kb.py instalar-hooks` a partir da cópia instalada (§8.3).
5. **Completa o `AGENTS.md`.** Se o arquivo não existe ou está vazio, grava o conteúdo integral ({{A:@AGENTS.md}}). Se já existe, acrescenta no fim só os blocos que faltarem: `# Regras globais` (reconhecido pelo texto ``GitHub CLI (`gh`)``), `## graphify` e `## kb`. O arquivo original vai antes para o backup.
6. **Roda o verificador** (Apêndice C) e mostra o resultado.

Pode rodar de novo quantas vezes quiser: nada é duplicado.

### 5.3 Saída esperada (numa máquina limpa, com graphify)

```
Destino das skills: C:\Users\<você>\AppData\Roaming\devin\skills
gravado : C:\Users\<você>\AppData\Roaming\devin\skills\kb\SKILL.md
gravado : C:\Users\<você>\AppData\Roaming\devin\skills\kb\references\schema.md
… (19 linhas "gravado :" no total)
graphify: hooks PreToolUse registrados em C:\Users\<você>\AppData\Roaming\devin\config.json
global : C:\Users\<você>\kb — .kb/, pessoas/, equipes/, sistemas/, projetos/, bugs/, padroes/, decisoes/, processos/, reunioes/, conceitos/, fontes/, memoria/, diario/, _INDEX.md, LESSONS.md
Instalados hooks kb em C:\Users\<você>\AppData\Roaming\devin\config.json (backup: config.json.bak)
Confira numa sessão nova com /hooks.
AGENTS.md: criado em C:\Users\<você>\AppData\Roaming\devin\AGENTS.md

== Arquivos das skills (C:\Users\<você>\AppData\Roaming\devin\skills)
OK     95a64f130a2c4bfe  kb/SKILL.md
… (uma linha por arquivo; os 16 primeiros caracteres do SHA-256 conferem com a tabela da §6.4)
== Regras globais (AGENTS.md)
OK     # Regras globais
OK     ## graphify
OK     ## kb
== Hooks (config.json)
OK     SessionStart -> kb.py hook session
OK     UserPromptSubmit -> kb.py hook prompt
OK     PostToolUse -> kb.py hook track
OK     Stop -> kb.py hook stop
OK     PreToolUse -> graphify hook-guard search/read (2)
== Teste do comando registrado no UserPromptSubmit (via shell)
OK     rc=0  [kb] Sem candidatos nas bases para esta mensagem (0 notas no total).
== Base global
OK     C:\Users\<você>\kb

RESULTADO: tudo certo. Feche e reabra o Devin (sessão nova) e confira com /hooks.
```

- **Sem graphify:** aparece `graphify: comando 'graphify' não encontrado no PATH…` e o verificador mostra `INFO` na linha do graphify. Não é falha.
- **Se já havia `config.json` ou `AGENTS.md`:** aparecem linhas `backup  :` e `AGENTS.md: acrescentado …`.

### 5.4 Depois do instalador

Vá para a Fase 6 (§10). As seções §6 a §9 explicam em detalhe o que o instalador fez. Leia-as se algo falhar ou se o usuário pedir explicação.

## 6. Fase 2 — arquivos das skills (caminho manual)

### 6.1 Árvore final

```
<skills>\
├── kb\
│   ├── SKILL.md
│   ├── references\
│   │   ├── schema.md
│   │   └── operacoes.md
│   ├── scripts\
│   │   └── kb.py
│   └── templates\
│       ├── bug.md
│       ├── decisao.md
│       ├── mapa.md
│       ├── memoria.md
│       ├── modulo.md
│       ├── nota.md
│       ├── padrao.md
│       ├── processo.md
│       ├── projeto.md
│       ├── regra.md
│       └── reuniao.md
├── kb-buscar\
│   └── SKILL.md
├── kb-salvar\
│   └── SKILL.md
├── kb-mapear\
│   └── SKILL.md
└── token-efficiency\
    └── SKILL.md
```

São 19 arquivos. O nome da pasta é o identificador da skill e vira o comando: `<skills>\kb-buscar\` corresponde a `/kb-buscar`.

### 6.2 Como gravar cada arquivo

Ordem sugerida: `kb/scripts/kb.py`, `kb/references/*`, `kb/templates/*`, `kb/SKILL.md`, `kb-buscar`, `kb-salvar`, `kb-mapear` e `token-efficiency`. O conteúdo de cada um é o bloco correspondente do Apêndice A, **sem** as linhas de cerca `~~~~`.

Regras de gravação:

- **Codificação:** UTF-8 sem BOM. O texto tem acentos e travessões.
- **Fim de linha:** LF. Não salve com CRLF.
- **Final do arquivo:** exatamente uma quebra de linha, a do fim da última linha do bloco.
- **Crie as pastas antes.** Exemplo no PowerShell: `New-Item -ItemType Directory -Force "$env:APPDATA\devin\skills\kb\templates"`.

Se o arquivo saiu com CRLF ou BOM, corrija com:

```
python -c "import sys;p=sys.argv[1];b=open(p,'rb').read().replace(b'\r\n',b'\n');b=b[3:] if b.startswith(b'\xef\xbb\xbf') else b;open(p,'wb').write(b)" "<caminho do arquivo>"
```

### 6.3 Papel de cada skill e o frontmatter

| Skill | `triggers` | `argument-hint` | `permissions` | Papel |
|---|---|---|---|---|
| `kb` | user, model | `[nova\|anota\|ingest\|lint\|relatorio\|memoria] [args]` | — | Núcleo: as duas bases, comandos manuais, regras fixas, bootstrap e hooks. Aponta para `references/` e `templates/` |
| `kb-buscar` | user, model | `[pergunta ou termos]` | — | Aproveita o bloco `[kb]`, escolhe a ordem das bases pela intenção e busca do mais barato ao mais caro |
| `kb-salvar` | user, model | `[fato, regra, bug ou decisão]` | `allow: Write(docs/kb/**)`, `Write(~/kb/**)` | Quando salvar, quando não salvar, onde, como (dedupe, template, relações, índice) e o aviso de uma linha |
| `kb-mapear` | user, model | `[caminho do projeto] [--foco <pasta ou área>]` | as mesmas de `kb-salvar` | Prepara, lê o panorama, extrai, divide entre subagentes (projetos médios e grandes), grava e entrega um relatório |
| `token-efficiency` | model, user | — | — | Minimiza a saída das ferramentas: grep antes de read, offset/limit, `--stat` e assim por diante |

Campos do frontmatter no Devin:

- **`name`:** nome exibido. O identificador do comando é o nome da pasta.
- **`description`:** aparece no autocomplete e é o que o modelo usa para decidir se carrega a skill sozinho. As descrições são longas de propósito, cheias de palavras-gatilho: "antes de qualquer tarefa", "bug resolvido", "regra de negócio"…
- **`argument-hint`:** dica mostrada depois do `/comando`.
- **`triggers`:** `user` permite `/nome`; `model` permite que o agente invoque sozinho.
- **`permissions.allow`:** escopos aprovados automaticamente enquanto a skill roda, somados às permissões da sessão. `Write(~/kb/**)` não cobre uma base global fora de `~/kb` (§7.3).

### 6.4 Conferência por hash

SHA-256 dos arquivos da origem (em minúsculas; o `Get-FileHash` mostra em maiúsculas, e dá no mesmo):

{{TABELA_HASHES}}

Como conferir:

- **PowerShell:** `Get-FileHash -Algorithm SHA256 "$env:APPDATA\devin\skills\kb\scripts\kb.py"`
- **bash:** `sha256sum ~/.config/devin/skills/kb/scripts/kb.py`
- **Todos de uma vez:** rode o verificador (§10.1).

**Verificação da Fase 2:** os 19 arquivos existem e os hashes batem.

## 7. Fase 3 — base global

### 7.1 Criar

```powershell
python "$env:APPDATA\devin\skills\kb\scripts\kb.py" init
```

Saída esperada numa máquina sem base:

```
global : C:\Users\<você>\kb — .kb/, pessoas/, equipes/, sistemas/, projetos/, bugs/, padroes/, decisoes/, processos/, reunioes/, conceitos/, fontes/, memoria/, diario/, _INDEX.md, LESSONS.md
```

Se a base já existe e está completa, a saída é `global : C:\Users\<você>\kb — já completa`. O comando é idempotente: nunca apaga nem sobrescreve nota, e só cria o que falta, inclusive seções que faltarem no `_INDEX.md`, inseridas na ordem canônica.

### 7.2 Estrutura criada e conteúdo exato

```
<kb-global>\
├── .kb\            ← dados derivados; o index.json aparece na primeira busca ou hook
├── bugs\  conceitos\  decisoes\  diario\  equipes\  fontes\  memoria\
├── padroes\  pessoas\  processos\  projetos\  reunioes\  sistemas\
├── _INDEX.md
└── LESSONS.md
```

`_INDEX.md`:

```markdown
# Índice da base global kb

Uma linha por nota: `- [[Título]] — resumo`. Atualizar ao criar, renomear ou mudar resumo de uma nota.

## pessoas

## equipes

## sistemas

## projetos

## bugs

## padroes

## decisoes

## processos

## reunioes

## conceitos

## fontes
```

`LESSONS.md`:

```markdown
# Lições da base kb

Agregado dos registros em `memoria/` (outcomes `useful` / `dead_end` / `corrected`; sinais recentes pesam mais; "preferida" exige 2+ confirmações). Regenerado por `/kb memoria`/`/kb relatorio` — não edite à mão.

## Fontes preferidas

## Tentativas

## Contestadas

## Becos sem saída conhecidos

## Correções
```

`.kb\index.json` é criado na primeira busca, no primeiro hook ou no primeiro `kb.py bases`, com `{"versao": 1, "notas": {}}`.

**Sem Python** (modo só-prompt): crie as 13 pastas, `.kb\` e esses dois arquivos à mão, com exatamente esse conteúdo.

Na origem, o `_INDEX.md` foi criado por uma versão anterior e o título é `# Índice do vault kb`. Numa instalação nova sai o título acima. As duas versões funcionam igual (§17).

### 7.3 Base global em outro lugar (`KB_HOME`, opcional)

```powershell
[Environment]::SetEnvironmentVariable("KB_HOME", "D:\kb", "User")   # depois reabra o terminal e o Devin
```

- **Carregamento:** o `kb.py` e os hooks leem `KB_HOME` do ambiente do processo do Devin, então é preciso reabrir o Devin.
- **Permissões das skills:** as skills `kb-salvar` e `kb-mapear` só aprovam sozinhas a escrita em `~/kb/**`. Com `KB_HOME`, aprove "sempre permitir" para a pasta nova na primeira gravação.
- **Base existente:** para aproveitar uma base de outra máquina, copie a pasta inteira. O `.kb\` é opcional, porque o índice é refeito sozinho.

### 7.4 Conferir

```powershell
python "$env:APPDATA\devin\skills\kb\scripts\kb.py" bases
```

Saída esperada fora de um repositório:

```
Global : C:\Users\<você>\kb — 0 notas
Projeto: nenhum repositório git a partir de C:\Users\<você>
```

**Verificação da Fase 3:** `kb.py bases` mostra a global com `0 notas` (ou a contagem real, se a base foi copiada).

## 8. Fase 4 — hooks globais (`config.json`)

### 8.1 Como o Devin trata hooks

- **Onde ficam:** os hooks globais estão em `<config>\config.json`, sob a chave `"hooks"`. O Devin também lê hooks de projeto (`.devin/hooks.v1.json` e `.devin/config.json`) e os de Claude Code (`~/.claude/settings.json`), mas este sistema usa só o global.
- **Estrutura:** cada evento aponta para uma lista de grupos no formato `{ "matcher": "<regex sobre tool_name>", "hooks": [ { "type": "command", "command": "...", "timeout": <segundos> } ] }`. Com matcher vazio, o grupo vale para tudo. Em eventos sem ferramenta (`SessionStart`, `UserPromptSubmit`, `Stop`), use `""`.
- **Entrada:** o comando recebe JSON no **stdin**, sempre com `session_id`. `prompt_id` muda a cada mensagem e não existe no `SessionStart`. Cada evento traz seus campos: `prompt` no `UserPromptSubmit`; `tool_name`, `tool_input` e `tool_response` no `PostToolUse`; `stop_hook_active` no `Stop`. O Devin define a variável `DEVIN_PROJECT_DIR`.
- **Saída:** JSON no **stdout**.
  - Para injetar texto no contexto: `{"hookSpecificOutput": {"hookEventName": "<evento>", "additionalContext": "<texto>"}}`. É o que o kb usa em `SessionStart` e `UserPromptSubmit`.
  - Para bloquear: `{"decision": "block", "reason": "<texto>"}`. No `Stop`, isso faz o agente continuar com o `reason` como instrução.
- **Código de saída:** `0` segue normalmente; **`2` bloqueia a ação**; qualquer outro valor é erro registrado que não bloqueia.
- **Quando carregam:** só no início da sessão. `/hooks` lista os hooks carregados e de onde vieram.

### 8.2 Hooks do graphify (`PreToolUse`)

Na origem, estes 2 grupos foram escritos à mão, porque o `graphify devin install` não registra hooks no Devin. Acrescente dentro de `"hooks"` (o instalador faz isso sozinho se o `graphify` estiver no PATH):

```json
"PreToolUse": [
  {
    "matcher": "^(exec|grep)$",
    "hooks": [
      {
        "type": "command",
        "command": "graphify hook-guard search"
      }
    ]
  },
  {
    "matcher": "^(read|glob)$",
    "hooks": [
      {
        "type": "command",
        "command": "graphify hook-guard read"
      }
    ]
  }
]
```

- **Comportamento:** o `graphify hook-guard` lê a chamada da ferramenta no stdin. Se existir `graphify-out/graph.json` no diretório atual, imprime `{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"MANDATORY: graphify-out/graph.json exists. You MUST run graphify query …"}}`.
  - `search`: dispara na ferramenta `grep` ou num `exec` cujo comando executa busca (grep, rg…).
  - `read`: dispara ao ler um arquivo-fonte dentro do projeto. Se o grafo está desatualizado para aquele arquivo, o aviso é mais brando.
  - Sem grafo, não imprime nada.
- **Nunca bloqueia:** sai sempre com código 0 (fail-open).
- **Sem `timeout` e com comando `graphify` sem caminho**, exatamente como na origem. Por isso o `graphify` precisa estar no PATH do shell do Devin.
- **Efeito não verificado:** a documentação do Devin lista `additionalContext` para `UserPromptSubmit`, `SessionStart` e `PostToolUse`. No `PreToolUse`, o efeito do lembrete não foi confirmado (§17).
- **Sem graphify instalado, não registre estes hooks.** O comando falharia antes de cada `exec`, `grep`, `read` e `glob` (erro que não bloqueia, mas polui).

Se editar à mão, mantenha o JSON válido e confira com `python -m json.tool "$env:APPDATA\devin\config.json"`.

### 8.3 Hooks do kb — `kb.py instalar-hooks`

```powershell
python "$env:APPDATA\devin\skills\kb\scripts\kb.py" instalar-hooks
```

Saída esperada:

```
Instalados hooks kb em C:\Users\<você>\AppData\Roaming\devin\config.json (backup: config.json.bak)
Confira numa sessão nova com /hooks.
```

O `(backup: …)` só aparece se o `config.json` já existia.

O que o comando faz, passo a passo:

1. **Escolhe o arquivo:** `--config <arquivo>`, se informado. Senão, `%APPDATA%\devin\config.json` no Windows ou `~/.config/devin/config.json` nos outros sistemas.
2. **Faz backup:** se o arquivo existe, lê como UTF-8, tolerando BOM, e copia para `config.json.bak`, sobrescrevendo o `.bak` anterior.
3. **Remove as versões antigas dos hooks do kb:** tira de **todos** os eventos os hooks cujo `command` contém `kb.py` e ` hook `. Grupos e eventos que ficarem vazios são removidos. Os outros hooks, inclusive os do graphify, ficam intactos.
4. **Acrescenta um grupo por evento** no fim da lista de cada um, com `timeout` de 10 s:

   | Evento | `matcher` | Comando termina em |
   |---|---|---|
   | `SessionStart` | `""` | `hook session` |
   | `UserPromptSubmit` | `""` | `hook prompt` |
   | `PostToolUse` | `^(edit\|write\|apply_patch\|notebook_edit)$` | `hook track` |
   | `Stop` | `""` | `hook stop` |

5. **Grava de forma atômica:** arquivo temporário e `os.replace`, com indentação 2 e UTF-8.
6. **Avisa** se o `kb.py` que rodou não está dentro de `<pasta do config>\skills`, porque os hooks apontariam para uma cópia fora do lugar.

É idempotente: rodar de novo não duplica nada. `kb.py remover-hooks` faz os mesmos passos 1 a 3 sem o 4 e remove a chave `hooks` se ela ficar vazia.

### 8.4 `config.json` esperado

Chave `"hooks"` da origem, exatamente como está lá (as outras chaves do arquivo são da conta e não entram):

```json
{{HOOKS_ORIGEM}}
```

Numa máquina nova o resultado é o mesmo, com duas trocas:

- `C:/Users/aquin/AppData/Local/Programs/Python/Python313/python.exe` vira o `sys.executable` local, com barras normais;
- `C:/Users/carlos/AppData/Roaming/devin/skills/kb/scripts/kb.py` vira o caminho local do `kb.py`, também com barras normais.

Modelo do comando dos hooks do kb:

```
<PYTHON> -c "import runpy; runpy.run_path('<SKILLS>/kb/scripts/kb.py', run_name='__main__')" hook <session|prompt|track|stop>
```

A ordem das chaves segue a da origem: `PreToolUse` primeiro, porque o graphify foi configurado antes. A ordem não muda o funcionamento.

### 8.5 Por que o comando tem esse formato (não "simplifique")

| Detalhe | Motivo |
|---|---|
| **Barras normais** (`C:/...`) | O mesmo texto funciona no cmd.exe, no PowerShell e no Git Bash. Foi testado nos três |
| **`runpy.run_path(...)` em vez de `python kb.py`** | Se o script sumir, `python kb.py` sai com código **2**, que o Devin trata como **bloquear** o prompt ou o Stop. Com `runpy`, a falha sai com código 1, erro que não bloqueia |
| **Caminho absoluto do Python** | Os hooks não dependem do PATH do shell do Devin. Se o caminho tiver espaço, o `instalar-hooks` grava só `python` |
| **`timeout: 10`** | Um hook lento nunca trava a sessão. Na prática cada hook leva de dezenas a centenas de milissegundos |
| **Saída JSON só em ASCII** (`\u00e3` etc.) | A codificação do console (cp1252, cp850) não corrompe o JSON |
| **Nunca sai com código ≠ 0** | Qualquer exceção vai para `%TEMP%\devin-kb-hook\erros.log` e o hook sai com 0. JSON inválido na entrada também não quebra nada |

### 8.6 Testes manuais de cada hook

PowerShell. Use só ASCII no JSON, porque o pipe do PowerShell 5.1 estraga acentos:

```powershell
$kb = "$env:APPDATA\devin\skills\kb\scripts\kb.py"

'{"hook_event_name":"SessionStart","session_id":"teste"}' | python $kb hook session
# → {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "[kb] Bases de conhecimento\n- Global: ... \u2014 0 notas (bugs, padr\u00f5es, ...)..."}}

'{"prompt":"como configurar o pipeline de deploy","session_id":"teste","prompt_id":"p1"}' | python $kb hook prompt
# → {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "[kb] Sem candidatos nas bases para esta mensagem (0 notas no total)."}}

'{"prompt":"ok, valeu","session_id":"teste","prompt_id":"p2"}' | python $kb hook prompt
# → (nada: mensagem trivial)

'{"prompt":"/kb-mapear","session_id":"teste","prompt_id":"p3"}' | python $kb hook prompt
# → (nada: slash command)

'{"tool_name":"edit","tool_input":{"file_path":"C:/tmp/app.py"},"tool_response":{"success":true},"session_id":"teste","prompt_id":"p1"}' | python $kb hook track
# → (nada; grava "p1<TAB>code" em %TEMP%\devin-kb-hook\teste.log)

'{"stop_hook_active":false,"session_id":"teste","prompt_id":"p1"}' | python $kb hook stop
# → {"decision": "block", "reason": "[kb] Antes de encerrar: esta rodada alterou arquivos e nada foi salvo nas bases. ..."}

'{"stop_hook_active":false,"session_id":"teste","prompt_id":"p1"}' | python $kb hook stop
# → (nada: o lembrete dispara no máximo uma vez por rodada)

'{nao e json' | python $kb hook prompt; "rc=$LASTEXITCODE"
# → rc=0 (o erro vai para %TEMP%\devin-kb-hook\erros.log)

Remove-Item "$env:TEMP\devin-kb-hook\teste.log", "$env:TEMP\devin-kb-hook\erros.log" -ErrorAction SilentlyContinue
```

graphify (fora de um projeto com `graphify-out/`):

```powershell
'{"tool_name":"grep","tool_input":{"pattern":"x"}}' | graphify hook-guard search; "rc=$LASTEXITCODE"
# → só "rc=0"; dentro de um projeto com graphify-out/graph.json, imprime o JSON "MANDATORY: ..."
```

bash:

```bash
kb="$HOME/.config/devin/skills/kb/scripts/kb.py"   # no Git Bash do Windows: kb="$APPDATA/devin/skills/kb/scripts/kb.py"
echo '{"prompt":"como configurar o pipeline de deploy"}' | python3 "$kb" hook prompt
```

**Verificação da Fase 4:** o `config.json` é JSON válido, tem exatamente 1 hook do kb em cada um dos 4 eventos, tem os 2 do graphify (se instalado) e os testes acima respondem como indicado.

## 9. Fase 5 — regras globais (`AGENTS.md`)

### 9.1 Conteúdo e estratégia de merge

O arquivo é `<config>\AGENTS.md`. O conteúdo integral da origem está em **{{A:@AGENTS.md}}**, com três blocos:

1. `# Regras globais`: uso obrigatório do GitHub CLI (`gh`);
2. `## graphify`: quando e como consultar o grafo;
3. `## kb`: como usar as bases.

Como aplicar:

- **O arquivo não existe ou está vazio:** crie com o conteúdo integral de {{A:@AGENTS.md}}.
- **O arquivo existe:** mantenha o que houver e acrescente no fim **só** os blocos que faltarem, separados por uma linha em branco.
  - O bloco 1 está presente se o arquivo já contém ``GitHub CLI (`gh`)``.
  - Os blocos 2 e 3 estão presentes se existe uma linha exatamente `## graphify` ou `## kb`.
  - Nunca duplique um bloco. Se já existir com outro texto, mostre a diferença ao usuário e pergunte antes de trocar.

O Devin carrega o `AGENTS.md` global no início de toda sessão, em qualquer projeto. A documentação recomenda regras curtas que apontam para skills, e é o que estas fazem.

### 9.2 Papel de cada bloco

| Bloco | O que manda o agente fazer | Por quê |
|---|---|---|
| `# Regras globais` | Usar o `gh` para qualquer operação no GitHub (repos, PRs, issues, releases, workflows) e confirmar antes de usar uma alternativa | Preferência do usuário, anterior ao kb |
| `## graphify` | Se existe `graphify-out/graph.json`, começar perguntas de arquitetura por `graphify query/path/explain`; navegar por `graphify-out/wiki/index.md` se existir; ler o `GRAPH_REPORT.md` só para visão ampla; rodar `graphify update .` depois de mudar código | Economiza tokens e mantém o grafo atual. É a regra do graphify para o Devin, traduzida |
| `## kb` | Consultar as bases antes de qualquer tarefa (bloco `[kb]` + `kb-buscar`), salvar na hora pelo `kb-salvar`, oferecer `/kb-mapear` em projeto sem `docs/kb/`, citar `[[Título]]`, não inventar relações, não gravar segredos | É a camada de regra do "automático" (§1.4) |

**Verificação da Fase 5:** o `AGENTS.md` contém os 3 blocos, e o verificador mostra `OK` nas três linhas.

## 10. Fase 6 — verificação final

### 10.1 Verificador automático

Na pasta deste arquivo:

```
python -c "t=open('skill-conhecimento-PASSO-A-PASSO.md',encoding='utf-8').read();a='#'*3+' VERIFICADOR';exec(t[t.index(a+' INICIO'):t.index(a+' FIM')])"
```

O verificador confere, sem mexer em configuração (no máximo o índice derivado `.kb/index.json` é criado):

1. cada um dos 19 arquivos das skills, byte a byte, contra o Apêndice A (`OK`, `FALTA`, `CRLF` ou `DIFERE`);
2. os 3 blocos do `AGENTS.md`;
3. os 4 hooks do kb: um por evento, com o matcher certo e apontando para o `kb.py` instalado;
4. os 2 hooks do graphify, quando ele está no PATH;
5. o comando registrado no `UserPromptSubmit`, executado de verdade pelo shell com um JSON de teste (código 0 e resposta começando com `[kb]`);
6. a estrutura da base global.

Tudo certo quando a última linha é `RESULTADO: tudo certo…`. Se não for, corrija o que aparece como pendência e rode de novo.

### 10.2 Checklist numa sessão nova (com o usuário)

1. **Feche e reabra o Devin** numa pasta qualquer; de preferência, um repositório.
2. **`/hooks`:** devem aparecer `SessionStart`, `UserPromptSubmit`, `PostToolUse` (`^(edit|write|apply_patch|notebook_edit)$`) e `Stop` com o comando do `kb.py`, mais os 2 `PreToolUse` do graphify, todos com origem no `config.json` global.
3. **Pergunte ao agente** "qual bloco [kb] você recebeu no início da sessão?". Ele deve citar `[kb] Bases de conhecimento`, a global com a contagem de notas e, num repo sem base, `sem base (…) — ofereça ao usuário /kb-mapear`.
4. **Mande uma mensagem com conteúdo** (por exemplo, "como faço o deploy deste projeto?"). O agente recebe `[kb] Sem candidatos…` ou a lista de candidatos.
5. **Digite `/`:** aparecem `/kb`, `/kb-buscar`, `/kb-salvar`, `/kb-mapear` e `/token-efficiency` (e `/graphify`, se fez §4.3).
6. **`%TEMP%\devin-kb-hook\erros.log`** não existe ou não tem entradas novas.

### 10.3 Teste ponta a ponta

**a) Pelo agente executor, na sessão atual.** Os hooks não estão carregados nela, então o teste é simulado:

```powershell
$kb = "$env:APPDATA\devin\skills\kb\scripts\kb.py"
$nota = "$env:USERPROFILE\kb\padroes\Teste de instalacao do kb.md"
@"
---
tipo: padrao
resumo: "Nota temporaria para validar a instalacao do kb."
tags: [tech/teste]
atualizado: 2026-01-01
---
# Teste de instalacao do kb

**Regra técnica:** nota de teste; pode apagar.

## Relações
- (nenhuma registrada)
"@ | Set-Content -Encoding UTF8 $nota
python $kb buscar "teste instalacao kb" --base global
'{"prompt":"o que a base sabe sobre teste de instalacao do kb","session_id":"t","prompt_id":"t1"}' | python $kb hook prompt
Remove-Item $nota; python $kb indexar
```

Resultado esperado:

- o `buscar` lista `- [[Teste de instalacao do kb]] (padrao) — Nota temporaria para validar a instalacao do kb. · padroes/Teste de instalacao do kb.md`;
- o `hook prompt` devolve `[kb] Candidatos nas bases …` com a mesma linha;
- depois da limpeza, o `indexar` volta a mostrar 0 notas.

- `Set-Content -Encoding UTF8` do PowerShell 5.1 grava com BOM; o `kb.py` tolera BOM nas notas.
- Com `KB_HOME`, troque `$env:USERPROFILE\kb` pelo caminho dela.

**b) Com o usuário, na sessão nova.** Peça: `/kb-salvar padrão de teste "Teste de instalação do kb": nota temporária para validar a instalação`. O agente deve:

1. criar `<kb-global>\padroes\Teste de instalação do kb.md` a partir do template `padrao`;
2. acrescentar a linha em `_INDEX.md`, na seção `## padroes`;
3. terminar com `kb: + [[Teste de instalação do kb]] (global)`.

Na mensagem seguinte ("o que a base sabe sobre teste de instalação?"), o bloco `[kb]` deve trazer a nota. Depois, peça para apagar a nota e a linha do índice.

**Verificação da Fase 6:** o verificador está OK e os itens de 10.2 e 10.3 passaram.
