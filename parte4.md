## Apêndice A — conteúdo integral dos arquivos

Cada bloco abaixo é o conteúdo **exato** de um arquivo, sem as cercas `~~~~`.

- **Título:** o caminho relativo a `<skills>`. A exceção é o {{A:@AGENTS.md}}, que vai em `<config>\AGENTS.md`.
- **Comentário invisível antes de cada bloco:** é o que o instalador e o verificador usam para achar o arquivo.
- **Formato de gravação:** UTF-8 sem BOM, LF e uma quebra de linha no fim.
- **Conferência:** o SHA-256 de cada arquivo está na tabela da §6.4.

{{ARQUIVOS}}

## Apêndice B — instalador automático

É este bloco que o comando da §5.1 executa. Ele lê os blocos do Apêndice A **deste mesmo arquivo**, grava as skills, registra os hooks, completa o `AGENTS.md` e roda o verificador do Apêndice C.

- **Idempotente:** pode rodar de novo sem duplicar nada.
- **Backup:** tudo o que for alterado vai antes para `<config>\backup-kb\<data-hora>\`.
- **Só biblioteca padrão.**

```python
### INSTALADOR INICIO
import json, os, re, shutil, subprocess, sys, tempfile, time
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
if os.name == "nt" and os.environ.get("APPDATA"):
    cfgdir = os.path.join(os.environ["APPDATA"], "devin")
else:
    cfgdir = os.path.join(os.path.expanduser("~"), ".config", "devin")
skills = os.path.join(cfgdir, "skills")
backup = os.path.join(cfgdir, "backup-kb", time.strftime("%Y%m%d-%H%M%S"))
print("Destino das skills:", skills)


def guardar(caminho, rel):
    destino = os.path.join(backup, *rel.split("/"))
    if not os.path.exists(destino):
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.copy2(caminho, destino)
        print("backup  :", destino)


# 1. Skills: grava cada bloco do Apêndice A, byte a byte (UTF-8 sem BOM, LF, quebra de linha final)
agents = None
for rel, _, conteudo in re.findall(r"<!-- kb-arquivo: (\S+) -->\n(~{4,})[^\n]*\n(.*?)\n\2\n", t, re.S):
    if rel == "@AGENTS.md":
        agents = conteudo
        continue
    destino = os.path.join(skills, *rel.split("/"))
    novo = (conteudo + "\n").encode("utf-8")
    if os.path.exists(destino):
        with open(destino, "rb") as f:
            if f.read() == novo:
                print("igual   :", destino)
                continue
        guardar(destino, "skills/" + rel)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "wb") as f:
        f.write(novo)
    print("gravado :", destino)

# 2. Hooks do graphify (PreToolUse), antes dos do kb — como na origem; só se o CLI estiver no PATH
cfg = os.path.join(cfgdir, "config.json")
if os.path.exists(cfg):
    guardar(cfg, "config.json")
if shutil.which("graphify"):
    dados = {}
    if os.path.exists(cfg):
        with open(cfg, encoding="utf-8-sig") as f:
            dados = json.load(f)
    pre = dados.setdefault("hooks", {}).setdefault("PreToolUse", [])
    if any("graphify hook-guard" in h.get("command", "") for g in pre for h in g.get("hooks", [])):
        print("graphify: hooks PreToolUse já registrados")
    else:
        pre.append({"matcher": "^(exec|grep)$",
                    "hooks": [{"type": "command", "command": "graphify hook-guard search"}]})
        pre.append({"matcher": "^(read|glob)$",
                    "hooks": [{"type": "command", "command": "graphify hook-guard read"}]})
        os.makedirs(cfgdir, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=cfgdir, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, cfg)
        print("graphify: hooks PreToolUse registrados em", cfg)
else:
    print("graphify: comando 'graphify' não encontrado no PATH — hooks do graphify NÃO registrados (Fase 1, §4).")

# 3. Base global e 4. hooks do kb (sempre a partir da cópia instalada)
kb = os.path.join(skills, "kb", "scripts", "kb.py")
sys.stdout.flush()
subprocess.run([sys.executable, kb, "init"], check=True)
sys.stdout.flush()
subprocess.run([sys.executable, kb, "instalar-hooks"], check=True)
sys.stdout.flush()

# 5. Regras globais: cria o AGENTS.md ou acrescenta só os blocos que faltarem
if agents:
    arq = os.path.join(cfgdir, "AGENTS.md")
    atual = ""
    if os.path.exists(arq):
        with open(arq, encoding="utf-8") as f:
            atual = f.read()
    if not atual.strip():
        with open(arq, "w", encoding="utf-8", newline="\n") as f:
            f.write(agents + "\n")
        print("AGENTS.md: criado em", arq)
    else:
        faltando = []
        for bloco in re.split(r"(?m)^(?=## )", agents):
            b = bloco.strip("\n")
            if not b:
                continue
            titulo = b.split("\n", 1)[0].strip()
            if titulo.startswith("## "):
                presente = re.search(r"(?m)^" + re.escape(titulo) + r"[ \t]*$", atual)
            else:
                presente = "GitHub CLI (`gh`)" in atual
            if not presente:
                faltando.append(b)
        if faltando:
            guardar(arq, "AGENTS.md")
            with open(arq, "a", encoding="utf-8", newline="\n") as f:
                f.write(("\n" if atual.endswith("\n") else "\n\n") + "\n\n".join(faltando) + "\n")
            print("AGENTS.md: acrescentado", ", ".join(b.split("\n", 1)[0] for b in faltando), "em", arq)
        else:
            print("AGENTS.md: já tem os 3 blocos — mantido como está:", arq)

# 6. Verificação
print()
v = "#" * 3 + " VERIFICADOR"
exec(t[t.index(v + " INICIO"):t.index(v + " FIM")])
### INSTALADOR FIM
```

## Apêndice C — verificador

É este bloco que o comando da §10.1 executa (e que o instalador chama no fim). Ele só lê, com uma exceção: roda uma vez o comando registrado no `UserPromptSubmit` com um JSON de teste, o que pode criar o índice derivado `.kb/index.json` nas bases.

```python
### VERIFICADOR INICIO
import hashlib, json, os, re, shutil, subprocess, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
if os.name == "nt" and os.environ.get("APPDATA"):
    cfgdir = os.path.join(os.environ["APPDATA"], "devin")
else:
    cfgdir = os.path.join(os.path.expanduser("~"), ".config", "devin")
skills = os.path.join(cfgdir, "skills")
falhas = []

print("== Arquivos das skills (%s)" % skills)
agents_doc = ""
for rel, _, conteudo in re.findall(r"<!-- kb-arquivo: (\S+) -->\n(~{4,})[^\n]*\n(.*?)\n\2\n", t, re.S):
    if rel == "@AGENTS.md":
        agents_doc = conteudo
        continue
    destino = os.path.join(skills, *rel.split("/"))
    esperado = (conteudo + "\n").encode("utf-8")
    real = None
    if os.path.isfile(destino):
        with open(destino, "rb") as f:
            real = f.read()
    if real == esperado:
        estado = "OK"
    elif real is None:
        estado = "FALTA"
    elif real.replace(b"\r\n", b"\n") == esperado:
        estado = "CRLF"
    else:
        estado = "DIFERE"
    if estado != "OK":
        falhas.append(rel)
    print("%-6s %s  %s" % (estado, hashlib.sha256(real).hexdigest()[:16] if real else "-" * 16, rel))

print("== Regras globais (AGENTS.md)")
arq = os.path.join(cfgdir, "AGENTS.md")
atual = ""
if os.path.isfile(arq):
    with open(arq, encoding="utf-8") as f:
        atual = f.read()
for bloco in re.split(r"(?m)^(?=## )", agents_doc):
    b = bloco.strip("\n")
    if b:
        ok = b in atual
        print("%-6s %s" % ("OK" if ok else "FALTA", b.split("\n", 1)[0]))
        if not ok:
            falhas.append("AGENTS.md: " + b.split("\n", 1)[0])

print("== Hooks (config.json)")
cfg = os.path.join(cfgdir, "config.json")
hooks = {}
try:
    with open(cfg, encoding="utf-8-sig") as f:
        hooks = json.load(f).get("hooks") or {}
except (OSError, ValueError) as e:
    print("FALHA  config.json ausente ou inválido:", e)
    falhas.append("config.json")


def comandos(ev):
    return [(g.get("matcher", ""), h.get("command", ""))
            for g in (hooks.get(ev) or []) for h in (g.get("hooks") or [])]


kbpy = os.path.abspath(os.path.join(skills, "kb", "scripts", "kb.py")).replace("\\", "/").lower()
for ev, matcher, sub in (("SessionStart", "", "session"), ("UserPromptSubmit", "", "prompt"),
                         ("PostToolUse", "^(edit|write|apply_patch|notebook_edit)$", "track"), ("Stop", "", "stop")):
    achados = [(m, c) for m, c in comandos(ev) if "kb.py" in c and c.rstrip().endswith(" hook " + sub)]
    ok = len(achados) == 1 and achados[0][0] == matcher
    print("%-6s %s -> kb.py hook %s%s" % ("OK" if ok else "FALHA", ev, sub,
                                          "" if ok else " (%d registro(s) válido(s))" % len(achados)))
    if not ok:
        falhas.append("hook " + ev)
    elif kbpy not in achados[0][1].lower():
        print("AVISO  o hook %s aponta para outro kb.py: %s" % (ev, achados[0][1]))
gr = [c for m, c in comandos("PreToolUse") if "graphify hook-guard" in c]
if shutil.which("graphify"):
    ok = len(gr) == 2
    print("%-6s PreToolUse -> graphify hook-guard search/read (%d)" % ("OK" if ok else "FALHA", len(gr)))
    if not ok:
        falhas.append("hooks do graphify")
else:
    print("INFO   graphify fora do PATH (opcional)%s" % (
        " — mas há hooks dele registrados: instale o graphify ou remova esses hooks" if gr else ""))

print("== Teste do comando registrado no UserPromptSubmit (via shell)")
reg = [c for m, c in comandos("UserPromptSubmit") if "kb.py" in c]
if reg:
    try:
        r = subprocess.run(reg[0], shell=True, input='{"prompt": "teste de verificacao da instalacao kb"}',
                           capture_output=True, text=True, timeout=60)
        ctx = ""
        if r.stdout.strip():
            ctx = (json.loads(r.stdout).get("hookSpecificOutput") or {}).get("additionalContext", "")
        ok = r.returncode == 0 and ctx.startswith("[kb]")
        print("%-6s rc=%s  %s" % ("OK" if ok else "FALHA", r.returncode, ctx.split("\n")[0] or r.stderr.strip()[-300:]))
    except Exception as e:
        ok = False
        print("FALHA ", repr(e))
    if not ok:
        falhas.append("teste do hook")
else:
    print("FALHA  nenhum hook do kb registrado no UserPromptSubmit")

print("== Base global")
kh = os.environ.get("KB_HOME")
base = os.path.abspath(os.path.expanduser(kh)) if kh else os.path.join(os.path.expanduser("~"), "kb")
faltam = [p for p in (".kb", "pessoas", "equipes", "sistemas", "projetos", "bugs", "padroes", "decisoes", "processos",
                      "reunioes", "conceitos", "fontes", "memoria", "diario") if not os.path.isdir(os.path.join(base, p))]
faltam += [a for a in ("_INDEX.md", "LESSONS.md") if not os.path.isfile(os.path.join(base, a))]
print("%-6s %s%s" % ("OK" if not faltam else "FALHA", base, (" — faltam: " + ", ".join(faltam)) if faltam else ""))
if faltam:
    falhas.append("base global")

print()
if falhas:
    print("RESULTADO: %d pendência(s): %s" % (len(falhas), "; ".join(falhas)))
else:
    print("RESULTADO: tudo certo. Feche e reabra o Devin (sessão nova) e confira com /hooks.")
### VERIFICADOR FIM
```

## Apêndice D — adaptação para outro agente (não testado)

O sistema foi feito e testado para o **Devin CLI**. As notas e as bases funcionam com qualquer agente que leia e escreva arquivos (modo só-prompt). Para outro cliente, os pontos de adaptação são:

- **Claude Code:**
  - skills em `~/.claude/skills/<nome>/SKILL.md`; campos de frontmatter que ele não conhece, como `triggers` e `permissions`, tendem a ser ignorados;
  - regras em `~/.claude/CLAUDE.md`;
  - hooks em `~/.claude/settings.json`, na mesma estrutura. Rode `kb.py instalar-hooks --config ~/.claude/settings.json` e troque o matcher do `PostToolUse` para os nomes de ferramenta dele (`Edit|Write|MultiEdit|NotebookEdit`);
  - como o Claude Code não envia `prompt_id`, o lembrete do `Stop` passa a valer por sessão, e não por rodada;
  - **atenção:** o Devin também lê `~/.claude/settings.json`. Não registre os hooks nos dois lugares na mesma máquina, ou eles rodam em dobro.
- **Agentes sem hooks:** copie o bloco `## kb` para as regras do agente e mantenha as skills como documentos de instrução. A busca e o salvamento passam a depender só do modelo seguir as regras (§1.4).
- **graphify:** tem instalador próprio para mais de 20 plataformas (`graphify install --platform <nome>`; lista em `graphify --help`).
