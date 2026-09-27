# Gera ../skill-conhecimento-PASSO-A-PASSO.md a partir de parte1..4.md, embutindo byte a byte os arquivos
# instalados em %APPDATA%\devin (skills, AGENTS.md, hooks do config.json e o plugin token-efficiency).
# Uso: python gerar.py [--saida ARQUIVO]
import hashlib, importlib.util, json, os, re, sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")
sys.dont_write_bytecode = True
AQUI = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(os.environ["APPDATA"], "devin")
SKILLS = os.path.join(CFG, "skills")
SAIDA = os.path.join(os.path.dirname(AQUI), "skill-conhecimento-PASSO-A-PASSO.md")
if "--saida" in sys.argv:
    SAIDA = os.path.abspath(sys.argv[sys.argv.index("--saida") + 1])
DATA = date.today().isoformat()

ARQUIVOS = [
    ("kb/SKILL.md", "Skill núcleo (`/kb`): as duas bases, a tabela de comandos, as 7 regras fixas, o bootstrap e a automação por hooks. Aponta para `references/`, `templates/` e `scripts/`."),
    ("kb/references/schema.md", "Contrato canônico das notas, igual nas duas bases: onde fica cada base, anatomia da nota, 14 tipos (pasta = tipo), campos por tipo, 15 relações de vocabulário fechado, links entre as bases, escala de confiança, regras de nome, arquivos especiais e como renomear."),
    ("kb/references/operacoes.md", "Playbooks dos comandos manuais do `/kb`: `anota`, `nova`, `ingest`, `lint`, `relatorio` e `memoria`."),
    ("kb/templates/bug.md", "Template do tipo `bug` (global): sintoma literal, causa raiz, correção, como evitar e ambiente, mais a relação `ocorre_em`."),
    ("kb/templates/decisao.md", "Template do tipo `decisao` (nas duas bases): decisão, motivo e alternativas, mais `decidido_em` e `substitui`."),
    ("kb/templates/mapa.md", "Template do `_MAPA.md` da base do projeto. O `kb.py init --projeto` usa este arquivo e troca `<Projeto>` e `AAAA-MM-DD`."),
    ("kb/templates/memoria.md", "Template do tipo `memoria` (global), usado por `/kb memoria`: pergunta, outcome, correção e notas consultadas."),
    ("kb/templates/modulo.md", "Template do tipo `modulo` (projeto): responsabilidade, onde fica e conceitos, mais `parte_de`, `depende_de` e `integra_com`."),
    ("kb/templates/nota.md", "Template genérico, para os tipos sem template próprio: conceito, sistema, pessoa, equipe e fonte."),
    ("kb/templates/padrao.md", "Template do tipo `padrao` (global): regra técnica, por quê, como aplicar e quando não se aplica."),
    ("kb/templates/processo.md", "Template do tipo `processo` (nas duas bases): gatilho, passos, resultado e regras envolvidas."),
    ("kb/templates/projeto.md", "Template do hub `projetos/<Projeto>.md` na base global: repo sem credenciais, caminho local e `kb_projeto`."),
    ("kb/templates/regra.md", "Template do tipo `regra` (projeto): enunciado normativo, condições e exceções, exemplos, onde está implementada, origem e `## Histórico`."),
    ("kb/templates/reuniao.md", "Template do tipo `reuniao` (global): participantes, pontos discutidos e decisões."),
    ("kb/scripts/kb.py", "Motor em Python stdlib (§13): `bases`, `init`, `inventario`, `buscar`, `indexar`, `hook`, `instalar-hooks` e `remover-hooks`."),
    ("kb-buscar/SKILL.md", "Skill de busca automática: passo 0 (aproveitar o bloco `[kb]`), ordem das bases pela intenção, busca do mais barato ao mais caro e uso do resultado."),
    ("kb-salvar/SKILL.md", "Skill de salvamento automático: quando salvar e quando não salvar, onde (tabela de roteamento) e como (dedupe, template, relações, `_INDEX.md` e aviso de uma linha). O frontmatter tem `permissions.allow` para escrever nas bases."),
    ("kb-mapear/SKILL.md", "Skill de mapeamento inicial ou incremental: preparar, ler o panorama, extrair, dividir entre subagentes, gravar e entregar o relatório."),
    ("token-efficiency/SKILL.md", "Skill complementar, anterior ao kb: hábitos de economia de tokens."),
    ("@AGENTS.md", "Regras globais completas da origem. Vão em `<config>\\AGENTS.md` (§9). Numa máquina que já tem `AGENTS.md`, acrescente só os blocos que faltarem."),
]


def origem(rel):
    return os.path.join(CFG, "AGENTS.md") if rel == "@AGENTS.md" else os.path.join(SKILLS, *rel.split("/"))


def ler(rel):
    b = open(origem(rel), "rb").read()
    assert b"\r" not in b, rel + ": tem CR"
    assert not b.startswith(b"\xef\xbb\xbf"), rel + ": tem BOM"
    assert b.endswith(b"\n") and not b.endswith(b"\n\n"), rel + ": final de arquivo inesperado"
    texto = b.decode("utf-8")
    for l in texto.split("\n"):
        assert not l.startswith("~~~"), rel + ": linha com ~~~"
    assert "kb-arquivo:" not in texto, rel + ": contém marcador"
    return b, texto[:-1]


# módulo kb.py para contar constantes
spec = importlib.util.spec_from_file_location("kbmod", origem("kb/scripts/kb.py"))
kbmod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kbmod)

numero = {rel: "A.%d" % (i + 1) for i, (rel, _) in enumerate(ARQUIVOS)}
blocos, linhas_hash, conteudos = [], [], {}
for i, (rel, desc) in enumerate(ARQUIVOS):
    b, conteudo = ler(rel)
    conteudos[rel] = conteudo
    nome = "AGENTS.md" if rel == "@AGENTS.md" else rel
    lang = "python" if rel.endswith(".py") else "markdown"
    titulo = "### %s `%s`" % (numero[rel], nome)
    if rel == "@AGENTS.md":
        titulo += " — regras globais (vai em `<config>\\AGENTS.md`)"
    blocos.append("%s\n\n%s\n\n<!-- kb-arquivo: %s -->\n~~~~%s\n%s\n~~~~\n" % (titulo, desc, rel, lang, conteudo))
    obs = " (fica em `<config>`; o hash só bate se o arquivo não tinha outro conteúdo)" if rel == "@AGENTS.md" else ""
    linhas_hash.append("| %s | `%s`%s | %d | `%s` |" % (numero[rel], nome, obs, len(b), hashlib.sha256(b).hexdigest()))

tabela = "| # | Arquivo (relativo a `<skills>`) | Bytes | SHA-256 |\n|---|---|---|---|\n" + "\n".join(linhas_hash)
with open(os.path.join(CFG, "config.json"), encoding="utf-8-sig") as f:
    hooks_origem = json.dumps({"hooks": json.load(f)["hooks"]}, ensure_ascii=False, indent=2)

partes = []
for n in (1, 2, 3, 4):
    with open(os.path.join(AQUI, "parte%d.md" % n), encoding="utf-8") as f:
        partes.append(f.read().rstrip("\n") + "\n")
doc = "\n".join(partes)
doc = re.sub(r"\{\{A:([^}]+)\}\}", lambda m: numero[m.group(1)], doc)
PLUGIN = os.path.join(CFG, "plugins", "token-efficiency")


def ler_plugin(*partes):
    b = open(os.path.join(PLUGIN, *partes), "rb").read().replace(b"\r\n", b"\n")
    return b.decode("utf-8").rstrip("\n")


subs = {
    "{{DATA}}": DATA,
    "{{PLUGIN_JSON}}": ler_plugin(".devin-plugin", "plugin.json"),
    "{{PLUGIN_AGENTS}}": ler_plugin("AGENTS.md"),
    "{{TABELA_HASHES}}": tabela,
    "{{HOOKS_ORIGEM}}": hooks_origem,
    "{{LINHAS_KBPY}}": str(conteudos["kb/scripts/kb.py"].count("\n") + 1),
    "{{N_STOP}}": str(len(kbmod.STOP)),
    "{{N_CODIGO}}": str(len(kbmod.CODIGO)),
}
for k, v in subs.items():
    assert k in doc, k
    doc = doc.replace(k, v)
doc = doc.replace("{{ARQUIVOS}}", "\n".join(blocos).rstrip("\n"))


def ancora(h):
    return "#" + re.sub(r"[^\w\- ]", "", h.strip().lower()).replace(" ", "-")


titulos, cerca = [], None
for l in doc.split("\n"):
    m = re.match(r"^(`{3,}|~{3,})", l)
    if cerca is None and m:
        cerca = m.group(1)
        continue
    if cerca is not None:
        if l.strip() == cerca:
            cerca = None
        continue
    if l.startswith("## ") and l[3:].strip() != "Sumário":
        titulos.append(l[3:].strip())
sumario = "\n".join("- [%s](%s)" % (h, ancora(h)) for h in titulos)
doc = doc.replace("{{SUMARIO}}", sumario)

assert "{{" not in doc, re.findall(r"\{\{[^}]*\}\}", doc)[:5]
for marca in ("### INSTALADOR INICIO", "### INSTALADOR FIM", "### VERIFICADOR INICIO", "### VERIFICADOR FIM"):
    assert doc.count(marca) == 1, (marca, doc.count(marca))
achados = re.findall(r"<!-- kb-arquivo: (\S+) -->\n(~{4,})[^\n]*\n(.*?)\n\2\n", doc, re.S)
assert len(achados) == len(ARQUIVOS), len(achados)
for rel, _, c in achados:
    assert c == conteudos[rel], rel

with open(SAIDA, "w", encoding="utf-8", newline="\n") as f:
    f.write(doc)
print("gerado:", SAIDA)
print("bytes:", len(doc.encode("utf-8")), "linhas:", doc.count("\n"), "secoes:", len(titulos))
print("kb.py linhas:", subs["{{LINHAS_KBPY}}"], "stop:", subs["{{N_STOP}}"], "codigo:", subs["{{N_CODIGO}}"])
