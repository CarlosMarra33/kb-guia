# Testa o instalador (Apêndice B) e o verificador (Apêndice C) de ../skill-conhecimento-PASSO-A-PASSO.md
# em sandboxes isoladas: APPDATA, USERPROFILE e TEMP apontam para uma pasta temporária, apagada no fim.
# A configuração real só é lida (cenário 7 roda o verificador nela). Uso: python testar.py
import hashlib, json, os, shutil, subprocess, sys, tempfile

sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.dirname(AQUI)
DOC = "skill-conhecimento-PASSO-A-PASSO.md"
REAL = os.path.join(os.environ["APPDATA"], "devin")
ONE = "t=open('%s',encoding='utf-8').read();a='#'*3+' %s';exec(t[t.index(a+' INICIO'):t.index(a+' FIM')])"
BASE = tempfile.mkdtemp(prefix="kb-guia-teste-")
res = []


def check(nome, cond):
    res.append((nome, bool(cond)))
    print(("PASSOU " if cond else "FALHOU ") + nome)


def sandbox(nome):
    s = os.path.join(BASE, nome)
    d = {k: os.path.join(s, k) for k in ("appdata", "home", "tmp")}
    for p in d.values():
        os.makedirs(p)
    env = dict(os.environ, APPDATA=d["appdata"], USERPROFILE=d["home"], HOME=d["home"], TEMP=d["tmp"], TMP=d["tmp"])
    env.pop("KB_HOME", None)
    return s, d, env


def rodar(modo, env, via="python"):
    code = ONE % (DOC, modo)
    if via == "powershell":
        cmd = ["powershell", "-NoProfile", "-Command", 'python -c "%s"' % code]
    elif via == "cmd":
        cmd = 'cmd /c python -c "%s"' % code
    else:
        cmd = [sys.executable, "-c", code]
    r = subprocess.run(cmd, cwd=DOC_DIR, env=env, capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def arvore_hash(raiz):
    return {os.path.relpath(os.path.join(p, a), raiz).replace(os.sep, "/"): sha(os.path.join(p, a))
            for p, _, arqs in os.walk(raiz) for a in arqs}


def ler_json(caminho):
    with open(caminho, encoding="utf-8-sig") as f:
        return json.load(f)


def main():
    real_skills = arvore_hash(os.path.join(REAL, "skills"))
    with open(os.path.join(REAL, "AGENTS.md"), "rb") as f:
        real_agents = f.read()
    real_hooks = ler_json(os.path.join(REAL, "config.json"))["hooks"]

    print("\n##### 1. instalação limpa (PowerShell, comando exato do guia)")
    s, d, env = sandbox("limpa")
    dv = os.path.join(d["appdata"], "devin")
    rc, out = rodar("INSTALADOR", env, via="powershell")
    print(out)
    check("1 rc=0", rc == 0)
    check("1 resultado tudo certo", "RESULTADO: tudo certo" in out)
    sk = arvore_hash(os.path.join(dv, "skills"))
    check("1 skills idênticas às reais", sk == {k: v for k, v in real_skills.items() if k in sk} and len(sk) == 19)
    with open(os.path.join(dv, "AGENTS.md"), "rb") as f:
        check("1 AGENTS.md idêntico ao real", f.read() == real_agents)
    cfg = ler_json(os.path.join(dv, "config.json"))
    h = cfg["hooks"]
    check("1 ordem dos eventos igual à origem", list(h) == list(real_hooks))
    troca = d["appdata"].replace("\\", "/")
    norm = json.loads(json.dumps(h).replace(troca, "C:/Users/carlos/AppData/Roaming"))
    check("1 hooks iguais à origem (trocando só o caminho do APPDATA)", norm == real_hooks)
    check("1 config só com a chave hooks", list(cfg) == ["hooks"])
    check("1 base global criada", os.path.isfile(os.path.join(d["home"], "kb", "_INDEX.md")))

    print("\n##### 2. reinstalação (cmd)")
    rc, out = rodar("INSTALADOR", env, via="cmd")
    print(out[-1500:])
    check("2 rc=0 e tudo certo", rc == 0 and "RESULTADO: tudo certo" in out)
    check("2 nenhum arquivo regravado", "gravado :" not in out and out.count("igual   :") == 19)
    check("2 graphify já registrado", "graphify: hooks PreToolUse já registrados" in out)
    check("2 AGENTS mantido", "já tem os 3 blocos" in out)
    check("2 hooks sem duplicata", ler_json(os.path.join(dv, "config.json"))["hooks"] == h)

    print("\n##### 3. verificador")
    rc, out = rodar("VERIFICADOR", env)
    print(out)
    check("3 verificador tudo certo", rc == 0 and "RESULTADO: tudo certo" in out)

    print("\n##### 4. verificador com problemas")
    alvo = os.path.join(dv, "skills", "kb-buscar", "SKILL.md")
    with open(alvo, "rb") as f:
        b = f.read()
    with open(alvo, "wb") as f:
        f.write(b.replace(b"\n", b"\r\n"))
    os.remove(os.path.join(dv, "skills", "kb", "templates", "nota.md"))
    rc, out = rodar("VERIFICADOR", env)
    print(out[-900:])
    check("4 detecta CRLF", "CRLF   " in out and "kb-buscar/SKILL.md" in out)
    check("4 detecta FALTA", "FALTA  " in out)
    check("4 resultado com pendências", "RESULTADO: 2 pendência(s)" in out)
    rc, out = rodar("INSTALADOR", env)
    check("4 instalador corrige e faz backup", "RESULTADO: tudo certo" in out and "backup  :" in out
          and os.path.isdir(os.path.join(dv, "backup-kb")))

    print("\n##### 5. merge com config/AGENTS existentes e skill antiga")
    s, d, env = sandbox("merge")
    dv = os.path.join(d["appdata"], "devin")
    os.makedirs(os.path.join(dv, "skills", "kb"))
    with open(os.path.join(dv, "skills", "kb", "SKILL.md"), "w", encoding="utf-8") as f:
        f.write("versao antiga\n")
    cfg0 = {"version": 1, "theme_mode": "dark", "permissions": {"allow": ["Exec(git status)"]},
            "hooks": {"PreToolUse": [{"matcher": "^exec$", "hooks": [{"type": "command", "command": "echo outro"}]}]}}
    with open(os.path.join(dv, "config.json"), "w", encoding="utf-8-sig") as f:
        f.write(json.dumps(cfg0, indent=2))
    ag0 = "# Minhas regras\n\n- Use pnpm.\n\n## kb\n\nversao antiga da secao kb\n"
    with open(os.path.join(dv, "AGENTS.md"), "w", encoding="utf-8") as f:
        f.write(ag0)
    rc, out = rodar("INSTALADOR", env)
    print(out)
    cfg = ler_json(os.path.join(dv, "config.json"))
    check("5 rc=0", rc == 0)
    check("5 chaves do usuário preservadas", cfg["version"] == 1 and cfg["theme_mode"] == "dark"
          and cfg["permissions"] == cfg0["permissions"])
    pre = [x["hooks"][0]["command"] for x in cfg["hooks"]["PreToolUse"]]
    check("5 hook do usuário preservado + graphify",
          pre == ["echo outro", "graphify hook-guard search", "graphify hook-guard read"])
    check("5 hooks kb presentes", all(e in cfg["hooks"] for e in ("SessionStart", "UserPromptSubmit", "PostToolUse", "Stop")))
    with open(os.path.join(dv, "AGENTS.md"), encoding="utf-8") as f:
        ag = f.read()
    check("5 AGENTS: conteúdo antigo mantido", ag.startswith(ag0))
    check("5 AGENTS: acrescentou regras gh e graphify, não duplicou ## kb", "GitHub CLI (`gh`)" in ag
          and ag.count("\n## graphify\n") == 1 and ag.count("## kb") == 1)
    check("5 verificador acusa ## kb divergente", "FALTA  ## kb" in out and "RESULTADO: 1 pendência(s)" in out)
    bk = os.path.join(dv, "backup-kb")
    itens = sorted(os.path.relpath(os.path.join(p, a), bk) for p, _, aa in os.walk(bk) for a in aa)
    print("backup:", itens)
    check("5 backup de config, AGENTS e skill antiga", any(i.endswith("config.json") for i in itens)
          and any(i.endswith("AGENTS.md") for i in itens)
          and any(i.endswith(os.path.join("kb", "SKILL.md")) for i in itens))

    print("\n##### 6. sem graphify no PATH")
    s, d, env = sandbox("semgraphify")
    env["PATH"] = os.path.join(os.environ["SystemRoot"], "System32") + os.pathsep + os.environ["SystemRoot"]
    rc, out = rodar("INSTALADOR", env)
    print(out[-1200:])
    cfg = ler_json(os.path.join(d["appdata"], "devin", "config.json"))
    check("6 rc=0 e tudo certo", rc == 0 and "RESULTADO: tudo certo" in out)
    check("6 aviso do graphify", "não encontrado no PATH" in out and "INFO   graphify fora do PATH" in out)
    check("6 sem PreToolUse", list(cfg["hooks"]) == ["SessionStart", "UserPromptSubmit", "PostToolUse", "Stop"])

    print("\n##### 7. verificador na instalação REAL (só leitura, exceto o índice derivado)")
    rc, out = rodar("VERIFICADOR", dict(os.environ))
    print(out)
    check("7 instalação real passa no verificador", rc == 0 and "RESULTADO: tudo certo" in out)


try:
    main()
finally:
    shutil.rmtree(BASE, ignore_errors=True)
print("\n==== %d/%d passaram" % (sum(ok for _, ok in res), len(res)))
for nome, ok in res:
    if not ok:
        print("FALHOU:", nome)
sys.exit(0 if res and all(ok for _, ok in res) else 1)
