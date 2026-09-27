# Captura as saídas reais do kb.py (init, bases, inventario, buscar, indexar, hooks, instalar/remover-hooks)
# numa sandbox temporária, apagada no fim; a configuração real não é tocada. Foram essas saídas que viraram
# os exemplos do guia. Para salvar em UTF-8 no Windows PowerShell 5.1, redirecione pelo cmd:
#   cmd /c "python captura.py > captura.txt 2>&1"
import json, os, shutil, stat, subprocess, sys, tempfile

sys.stdout.reconfigure(encoding="utf-8")
S = tempfile.mkdtemp(prefix="kb-guia-captura-")
APPDATA, HOME, TMP = (os.path.join(S, n) for n in ("appdata", "home", "tmp"))
KB = os.path.join(APPDATA, "devin", "skills", "kb", "scripts", "kb.py")
env = dict(os.environ, APPDATA=APPDATA, USERPROFILE=HOME, HOME=HOME, TEMP=TMP, TMP=TMP, PYTHONIOENCODING="utf-8")
env.pop("KB_HOME", None)
env.pop("DEVIN_PROJECT_DIR", None)


def run(titulo, args, cwd=S, stdin=None, extra=None):
    e = dict(env, **(extra or {}))
    r = subprocess.run([sys.executable, KB] + args, cwd=cwd, env=e, input=stdin, capture_output=True,
                       text=True, encoding="utf-8")
    print("=== %s (rc=%d)" % (titulo, r.returncode))
    print(r.stdout.rstrip())
    if r.stderr.strip():
        print("--- stderr:", r.stderr.rstrip())


def show(titulo, caminho):
    print("=== %s" % titulo)
    with open(caminho, encoding="utf-8") as f:
        print(f.read().rstrip("\n"))


def tree(raiz):
    for pasta, dirs, arqs in os.walk(raiz):
        dirs.sort()
        rel = os.path.relpath(pasta, raiz)
        print(("." if rel == "." else rel.replace(os.sep, "/")) + "/", sorted(arqs))


REGRA = """---
tipo: regra
resumo: "Pedidos acima de R$ 500 recebem 5% de desconto; acima de R$ 1.000, 10%."
tags: [dominio/vendas]
status: vigente
codigo: [src/vendas/desconto.py::calcular_desconto]
atualizado: 2026-09-26
---
# Desconto progressivo por valor do pedido

**Regra:** pedido com total acima de R$ 500 ganha 5%; acima de R$ 1.000 ganha 10%. Não acumula com cupom.

## Histórico
- 2026-09-26 — registrada (fonte: teste test_desconto_faixas).

## Relações
- aplica_a:: [[Pedido]] (EXTRACTED)
"""
BUG = """---
tipo: bug
resumo: "print de texto acentuado quebra no console do Windows — causa: stdout em cp1252; correção: sys.stdout.reconfigure(encoding='utf-8')."
tags: [tech/python, tech/windows]
status: corrigido
atualizado: 2026-09-26
---
# UnicodeEncodeError cp1252 ao imprimir acentos no Windows

**Sintoma:** `UnicodeEncodeError: 'charmap' codec can't encode character`

## Relações
- ocorre_em:: [[loja]] (EXTRACTED)
"""


def main():
    for d in (APPDATA, HOME, TMP):
        os.makedirs(d)
    shutil.copytree(os.path.join(os.environ["APPDATA"], "devin", "skills"), os.path.join(APPDATA, "devin", "skills"))

    run("init", ["init"])
    print("=== arvore global")
    tree(os.path.join(HOME, "kb"))
    show("_INDEX.md global", os.path.join(HOME, "kb", "_INDEX.md"))
    show("LESSONS.md", os.path.join(HOME, "kb", "LESSONS.md"))
    print("=== .kb/index.json existe apos init?", os.path.exists(os.path.join(HOME, "kb", ".kb", "index.json")))
    run("init de novo (idempotente)", ["init"])
    run("bases (sem projeto)", ["bases"])
    show(".kb/index.json apos bases", os.path.join(HOME, "kb", ".kb", "index.json"))

    # repo de exemplo
    loja = os.path.join(S, "dev", "loja")
    os.makedirs(os.path.join(loja, "src", "vendas"))
    os.makedirs(os.path.join(loja, "tests"))
    with open(os.path.join(loja, "src", "vendas", "desconto.py"), "w", encoding="utf-8") as f:
        f.write("def calcular_desconto(total):\n    # TODO: cupom\n    return 0.10 if total > 1000 else 0.05 if total > 500 else 0\n")
    with open(os.path.join(loja, "tests", "test_desconto.py"), "w", encoding="utf-8") as f:
        f.write("def test_desconto_faixas():\n    pass\n")
    with open(os.path.join(loja, "README.md"), "w", encoding="utf-8") as f:
        f.write("# Loja\n")
    for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"],
                 ["remote", "add", "origin", "https://github.com/exemplo/loja.git"], ["add", "."],
                 ["commit", "-q", "-m", "fix: desconto"]):
        subprocess.run(["git", "-C", loja] + args, capture_output=True, text=True, env=env)
    run("bases (repo sem base)", ["bases"], cwd=loja)
    run("init --projeto", ["init", "--projeto"], cwd=loja)
    print("=== arvore projeto")
    tree(os.path.join(loja, "docs", "kb"))
    show("_INDEX.md projeto", os.path.join(loja, "docs", "kb", "_INDEX.md"))
    show("_MAPA.md projeto", os.path.join(loja, "docs", "kb", "_MAPA.md"))
    show(".gitignore projeto", os.path.join(loja, "docs", "kb", ".gitignore"))
    run("inventario", ["inventario"], cwd=loja)
    run("bases (repo com base)", ["bases"], cwd=loja)
    run("bases --json", ["bases", "--json"], cwd=loja)

    # notas de exemplo
    os.makedirs(os.path.join(loja, "docs", "kb", "regras"), exist_ok=True)
    with open(os.path.join(loja, "docs", "kb", "regras", "Desconto progressivo por valor do pedido.md"), "w", encoding="utf-8") as f:
        f.write(REGRA)
    with open(os.path.join(HOME, "kb", "bugs", "UnicodeEncodeError cp1252 ao imprimir acentos no Windows.md"), "w", encoding="utf-8") as f:
        f.write(BUG)
    run("buscar desconto pedido", ["buscar", "desconto", "pedido"], cwd=loja)
    run("buscar unicode acentos --base global", ["buscar", "erro unicode ao imprimir acentos", "--base", "global"], cwd=loja)
    run("buscar --tipo bug", ["buscar", "windows", "--tipo", "bug"], cwd=loja)
    run("indexar", ["indexar"], cwd=loja)

    # hooks
    run("instalar-hooks", ["instalar-hooks"], cwd=loja)
    show("config.json apos instalar", os.path.join(APPDATA, "devin", "config.json"))
    run("instalar-hooks de novo", ["instalar-hooks"], cwd=loja)
    with open(os.path.join(APPDATA, "devin", "config.json"), encoding="utf-8") as f:
        h = json.load(f)["hooks"]
    print("=== contagem de hooks por evento apos 2 instalacoes:", {k: sum(len(g["hooks"]) for g in v) for k, v in h.items()})

    x = {"DEVIN_PROJECT_DIR": loja}
    edit = lambda caminho, pid, ferramenta="edit": json.dumps({
        "tool_name": ferramenta, "tool_input": {"file_path": caminho}, "tool_response": {"success": True},
        "session_id": "s1", "prompt_id": pid})
    stop = lambda pid: json.dumps({"stop_hook_active": False, "session_id": "s1", "prompt_id": pid})
    run("hook session", ["hook", "session"], cwd=loja, extra=x,
        stdin=json.dumps({"hook_event_name": "SessionStart", "source": "startup", "session_id": "s1"}))
    run("hook prompt (com candidatos)", ["hook", "prompt"], cwd=loja, extra=x,
        stdin=json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": "qual o desconto para pedido acima de 500?",
                          "session_id": "s1", "prompt_id": "p1"}))
    run("hook prompt (sem candidatos)", ["hook", "prompt"], cwd=loja, extra=x,
        stdin=json.dumps({"prompt": "configurar pipeline kubernetes", "session_id": "s1", "prompt_id": "p2"}))
    run("hook prompt (trivial)", ["hook", "prompt"], cwd=loja, extra=x,
        stdin=json.dumps({"prompt": "ok, valeu", "session_id": "s1", "prompt_id": "p3"}))
    run("hook prompt (slash)", ["hook", "prompt"], cwd=loja, extra=x,
        stdin=json.dumps({"prompt": "/kb-mapear", "session_id": "s1", "prompt_id": "p4"}))
    run("hook track (codigo)", ["hook", "track"], cwd=loja, extra=x,
        stdin=edit(os.path.join(loja, "src", "vendas", "desconto.py"), "p1"))
    run("hook stop (1a vez: lembra)", ["hook", "stop"], cwd=loja, extra=x, stdin=stop("p1"))
    run("hook stop (2a vez: silencio)", ["hook", "stop"], cwd=loja, extra=x, stdin=stop("p1"))
    run("hook prompt (regra ditada)", ["hook", "prompt"], cwd=loja, extra=x,
        stdin=json.dumps({"prompt": "regra: pedido cancelado nao pode ser reaberto", "session_id": "s1", "prompt_id": "p5"}))
    run("hook stop (regra ditada, nada salvo)", ["hook", "stop"], cwd=loja, extra=x, stdin=stop("p5"))
    run("hook track (nota na base)", ["hook", "track"], cwd=loja, extra=x,
        stdin=edit(os.path.join(loja, "docs", "kb", "regras", "X.md"), "p6", "write"))
    run("hook stop (salvou na base: silencio)", ["hook", "stop"], cwd=loja, extra=x, stdin=stop("p6"))
    run("hook com JSON invalido (nunca falha)", ["hook", "prompt"], cwd=loja, extra=x, stdin="{nao json")
    print("=== estado", sorted(os.listdir(os.path.join(TMP, "devin-kb-hook"))))
    show("s1.log", os.path.join(TMP, "devin-kb-hook", "s1.log"))
    run("remover-hooks", ["remover-hooks"], cwd=loja)
    show("config.json apos remover", os.path.join(APPDATA, "devin", "config.json"))
    run("sem argumentos", [], cwd=loja)


try:
    main()
finally:
    for pasta, _, arqs in os.walk(S):  # o git grava objetos somente-leitura, que o rmtree não apaga no Windows
        for a in arqs:
            try:
                os.chmod(os.path.join(pasta, a), stat.S_IWRITE)
            except OSError:
                pass
    shutil.rmtree(S, ignore_errors=True)
