# Gera o guia de fala (HTML) a partir das notas dos slides principais
import json, re, base64, io, html
from PIL import Image
S = "/tmp/claude-0/-home-user-Bruno/82e201e1-5baf-5943-97e1-cc467015b7d6/scratchpad"
notas = json.load(open(S + "/v20/notas.json", encoding="utf-8"))
import os
prints = sorted(os.listdir(S + "/v23/webfull"))

G = json.load(open(S + "/guia/guia.json", encoding="utf-8"))
dados = G["slides"]; total = G["total"]
NUM = {x["id"]: i + 1 for i, x in enumerate(dados)}
def N(*ids): return [NUM[i] for i in ids]
deck = json.load(open(S + "/artifact-files/351a25a9-1efc-412b-9232-d1cf8f2e53fe/project/deck.json", encoding="utf-8"))
titulos = {}
for x in dados:
    t_ = open(f"{S}/artifact-files/351a25a9-1efc-412b-9232-d1cf8f2e53fe/project/slides/{x['id']}.html", encoding="utf-8").read()
    titulos[x["id"]] = html.unescape(re.sub("<[^>]+>", "", re.search(r"<h[12][^>]*>(.*?)</h[12]>", t_, re.S).group(1)))
def mmss(s): return f"{s//60}:{s%60:02d}"
def dur(s): return " ".join(v for v in ((f"{s//60} min" if s >= 60 else ""), (f"{s%60} s" if s % 60 else "")) if v)
def thumb(i):
    im = Image.open(f"{S}/v23/webfull/{prints[i]}").convert("RGB").resize((640, 360), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=72, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
e = html.escape
blocos = []
for i, x in enumerate(dados):
    n = i + 1
    blocos.append(f'''
<article class="slide" id="s{n}">
  <div class="cab"><span class="num">{n:02d}</span><h2>{e(titulos[x["id"]])}</h2><span class="tempo"><b>{mmss(x["ini"])}</b> → {mmss(x["fim"])} · {dur(x["seg"])}{f" · {x['fala'].count(chr(9656))} cliques" if x["fala"].count(chr(9656)) > 1 else (" · 1 clique" if x["fala"].count(chr(9656)) == 1 else "")}</span></div>
  <div class="corpo">
    <img src="{thumb(i)}" alt="Miniatura do slide {n}: {e(titulos[x["id"]])}" loading="lazy">
    <div class="texto">
      <p class="chave">{e(x["chave"])}</p>
      <p class="fala">{e(x["fala"]).replace("▸", '<span class="clique" title="clique">▸</span>')}</p>
      {f'<p class="trans"><span>Transição</span> {e(x["trans"])}</p>' if x["trans"] else ''}
      {f'<details><summary>Se perguntarem</summary><p>{e(x["manga"])}</p></details>' if x["manga"] else ''}
    </div>
  </div>
</article>''')
notas = [dict(n=i+1, titulo=titulos[x["id"]]) for i, x in enumerate(dados)]

PERGUNTAS = [
 ("Por que não milrinona sempre que o paciente usa betabloqueador?",
  f"Porque o benefício é teórico. A milrinona age depois do receptor e mantém efeito no betabloqueado, mas na subanálise do DOREMI (93 pacientes betabloqueados) não houve vantagem clínica. Slide {N("milrdobu")[0]}."),
 ("O DOREMI não mostrou que as duas são iguais?",
  "Não houve diferença significativa (49% vs. 54%; RR 0,90; IC 95% 0,69–1,19; n = 192), mas o intervalo é largo: o estudo não prova equivalência. Arritmia, hipotensão sustentada e necessidade de vasopressor também não diferiram."),
 ("Milrinona no choque séptico?",
  "A SSC 2026 não encontrou dados para comparar com a dobutamina. Em um ECR de 2025 (Tongyoo, 64 pacientes), a milrinona aumentou o débito em 6 h, sem diferença de mortalidade (50% vs. 50%). Débito maior não é desfecho melhor."),
 ("Então quando a milrinona tem indicação?",
  f"Disfunção ventricular com baixo débito que exige inotrópico, sobretudo VD com hipertensão pulmonar e dificuldade de saída de CEC; com noradrenalina se a PAM cair. Sem baixo débito, considerar vasoplegia: a droga é o vasopressor. Slides {N("milrinona")[0]} a {N("condutavd")[0]}."),
 ("Quando associar vasopressina?",
  f"SSC 2026: quando a dose de noradrenalina está subindo, sem limiar definido; na enquete dos painelistas, mediana de 0,3 mcg/kg/min. Antecipar como política (VASSPR) não reduziu mortalidade. Slide {N("ssc2026")[0]}."),
 ("Qual o alvo de PAM no intraoperatório?",
  f"POQI 2024: PAM ≥60 mmHg em pacientes de risco como piso, maior com pressão venosa ou compartimental alta. HISTAP favoreceu ≥80 em hipertensos de alto risco; IMPROVE-multi e POISE-3 foram neutros. Slide {N("pamintraop")[0]}."),
 ("Noradrenalina em veia periférica é segura?",
  "Na metanálise de Tran, complicações em 7% (combinada 8,6%), 96% leves; menos com protocolo de segurança. A SSC 2026 sugere iniciar por veia periférica. Reserva “Início precoce e via periférica”."),
 ("Fenilefrina ou noradrenalina na cesárea?",
  "O consenso de 2018 recomenda vasopressor α-agonista em infusão profilática. A noradrenalina causa menos bradicardia materna (Sharkey, 10,7% vs. 37,5% de bradicardia). Reserva “Fenilefrina”."),
 ("E na hipotensão da reperfusão do transplante hepático?",
  f"No estudo do nosso serviço (Gouvêa, Diaz et al., PLoS One 2022; 19 pacientes, ETE), a função do VD foi normal em todas as fases, inclusive após a reperfusão. O eco ajuda a separar vasoplegia de disfunção ventricular; na vasoplegia refratária, vasopressina e, como resgate, azul de metileno. Slide {N("intraop")[0]}."),
 ("Dopamina em dose renal?",
  "Não protege o rim: no ANZICS (n = 328), sem diferença em creatinina, diálise ou mortalidade."),
 ("E o azul de metileno?",
  "Resgate na vasoplegia refratária (pós-CEC, reperfusão hepática), com evidência limitada; interfere na oximetria e pode causar síndrome serotoninérgica."),
 ("Dose de noradrenalina em base ou em sal?",
  "No Brasil, a ampola de hemitartarato de 2 mg/mL tem 1 mg/mL de base; em sal, o número é o dobro. Registrar na prescrição. Reserva “Início precoce e via periférica”."),
 ("Como a PKA aumenta a corrente de cálcio?",
  "Parte do efeito passa pela fosforilação da proteína Rad, que deixa de inibir o canal tipo L (Liu, Nature 2020). A sinalização do AMPc é compartimentalizada em nanodomínios (Zaccolo e Kovanich, Physiol Rev 2025)."),
]
import sys; sys.path.insert(0, S + "/guia")
from reserva_notas import RESERVA as RES_NOTAS
ordem = deck["order"]; res_ordem = json.load(open("/home/user/Bruno/apresentacao/deck/reserva.json", encoding="utf-8"))["order"] if os.path.exists("/home/user/Bruno/apresentacao/deck/reserva.json") else []
def titulo_de(id_):
    if id_ == "divisor": return "Slides de reserva para perguntas"
    t_ = open(f"{S}/artifact-files/351a25a9-1efc-412b-9232-d1cf8f2e53fe/project/slides/{id_}.html", encoding="utf-8").read()
    return html.unescape(re.sub("<[^>]+>", "", re.search(r"<h[12][^>]*>(.*?)</h[12]>", t_, re.S).group(1)))
def campo(linhas, rotulo):
    for l in linhas:
        if l.startswith(rotulo + ":"): return l[len(rotulo) + 1:].strip()
    return ""
blocos_res = []
for k, id_ in enumerate(res_ordem, len(ordem) + 1):
    L = RES_NOTAS[id_]; manga = campo(L, "SE PERGUNTAREM")
    blocos_res.append(f'''<article class="slide res" id="s{k}">
  <div class="cab"><span class="num">{k:02d}</span><h2>{e(titulo_de(id_))}</h2><span class="tempo">oculto</span></div>
  <div class="corpo"><img src="{thumb(k - 1)}" alt="Miniatura do slide {k}: {e(titulo_de(id_))}" loading="lazy">
    <div class="texto"><p class="uso"><span>Quando mostrar</span> {e(campo(L, "USO"))}</p><p class="chave">{e(campo(L, "PONTO-CHAVE"))}</p><p class="fala">{e(campo(L, "FALA"))}</p>
      {f'<details><summary>Se perguntarem</summary><p>{e(manga)}</p></details>' if manga else ''}</div></div>
</article>''')

perguntas = "".join(f'<details class="q"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in PERGUNTAS)
reserva = "".join(blocos_res)
secao_reserva = ('''<h2 class="secao">Slides ocultos de reserva</h2>
<p style="margin:0;color:var(--suave)">Ficam no PowerPoint depois do Obrigado, ocultos: não aparecem na apresentação. Para mostrar um, digite o número do slide e Enter. Cada um tem uma fala curta, para responder perguntas sem voltar à apresentação principal.</p>
{reserva}''') if res_ordem else ''
marcos = [(NUM["receptores"], "fim da farmacologia básica"), (NUM["condutavd"], "fim de milrinona, dobutamina e falência de VD"), (NUM["intraop"], "fim da escolha no intraoperatório")]
acum = [0] + [x['fim'] for x in dados]
marcos_html = "".join(f'<li><b>{mmss(acum[k])}</b> ao fim do slide {k} — {m}</li>' for k, m in marcos)
indice = "".join(f'<a href="#s{x["n"]}"><span>{x["n"]:02d}</span>{e(x["titulo"])}</a>' for x in notas)

page = f'''<title>Guia de fala das aminas vasoativas</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap">
<style>
/* Guia de leitura em coluna: índice, marcos de tempo, um bloco por slide, perguntas no fim */
:root {{
  --bg: #f4f2ed; --papel: #fffdf9; --tinta: #1b2a3a; --suave: #56606b; --linha: #e2ddd2; --acento: #b9581a; --acento2: #f3e3d3;
  --serif: "Source Serif 4", Georgia, serif; --sans: "Source Sans 3", "Segoe UI", Calibri, sans-serif;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #141b23; --papel: #1b2530; --tinta: #e8e4dc; --suave: #a9b2bc; --linha: #2c3846; --acento: #e49a5c; --acento2: #3a2a1e; color-scheme: dark }} }}
:root[data-theme="dark"] {{ --bg: #141b23; --papel: #1b2530; --tinta: #e8e4dc; --suave: #a9b2bc; --linha: #2c3846; --acento: #e49a5c; --acento2: #3a2a1e; color-scheme: dark }}
body {{ background: var(--bg); color: var(--tinta); font-family: var(--sans); font-size: 17px; line-height: 1.55;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 32px 64px }}
main {{ max-width: 1040px; margin: 0 auto; display: flex; flex-direction: column; gap: 28px }}
header h1 {{ font-family: var(--serif); font-weight: 500; font-size: clamp(30px, 5vw, 44px); line-height: 1.1; margin: 0; text-wrap: balance }}
.eyebrow {{ font-size: 13px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: var(--acento); margin: 0 0 8px }}
header p {{ margin: 8px 0 0; color: var(--suave); max-width: 68ch }}
.painel {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px }}
.painel section {{ background: var(--papel); border: 1px solid var(--linha); border-radius: 12px; padding: 18px 20px; min-width: 0 }}
.painel h3 {{ margin: 0 0 8px; font-size: 15px; letter-spacing: 1.5px; text-transform: uppercase; color: var(--suave) }}
.painel ul {{ margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 4px }}
.total {{ font-family: var(--serif); font-size: 40px; color: var(--acento); line-height: 1 }}
nav.indice {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 4px 16px }}
nav.indice a {{ color: var(--tinta); text-decoration: none; font-size: 15px; display: flex; gap: 8px; padding: 2px 0 }}
nav.indice a span {{ color: var(--acento); font-variant-numeric: tabular-nums; font-weight: 600 }}
nav.indice a:hover, nav.indice a:focus-visible {{ text-decoration: underline; outline: none }}
.slide {{ background: var(--papel); border: 1px solid var(--linha); border-radius: 12px; overflow: hidden; scroll-margin-top: 16px }}
.cab {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px 14px; padding: 14px 20px; border-bottom: 1px solid var(--linha) }}
.cab .num {{ font-family: var(--serif); font-size: 26px; color: var(--acento); font-variant-numeric: tabular-nums }}
.cab h2 {{ font-family: var(--serif); font-weight: 500; font-size: 22px; margin: 0; flex: 1 1 260px; text-wrap: balance }}
.cab .tempo {{ font-size: 14px; color: var(--suave); font-variant-numeric: tabular-nums; white-space: nowrap }}
.cab .tempo b {{ color: var(--tinta) }}
.corpo {{ display: grid; grid-template-columns: minmax(0, 300px) minmax(0, 1fr); gap: 20px; padding: 18px 20px }}
.corpo img {{ width: 100%; border-radius: 6px; border: 1px solid var(--linha); align-self: start }}
.texto {{ display: flex; flex-direction: column; gap: 10px; min-width: 0 }}
.chave {{ margin: 0; font-weight: 700; font-size: 18px; border-left: 3px solid var(--acento); padding-left: 12px }}
.fala {{ margin: 0; max-width: 72ch }}
.clique {{ color: var(--acento); font-weight: 700; margin: 0 3px }}
.pausa {{ margin: 0; font-weight: 600; color: var(--acento) }}
.trans {{ margin: 0; color: var(--suave); font-style: italic }}
.uso {{ margin: 0; color: var(--suave) }}
.uso span {{ font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-right: 6px; color: var(--acento) }}
.trans span {{ font-style: normal; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-right: 6px; color: var(--acento) }}
details {{ background: var(--acento2); border-radius: 8px; padding: 8px 14px }}
details summary {{ cursor: pointer; font-weight: 600 }}
details summary:focus-visible {{ outline: 2px solid var(--acento); outline-offset: 2px }}
details p {{ margin: 8px 0 4px; font-size: 16px }}
h2.secao {{ font-family: var(--serif); font-weight: 500; font-size: 30px; margin: 16px 0 0 }}
.q {{ background: var(--papel); border: 1px solid var(--linha); padding: 12px 18px }}
ol.reserva {{ list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 6px 16px }}
ol.reserva span {{ display: inline-block; min-width: 28px; color: var(--acento); font-weight: 600; font-variant-numeric: tabular-nums }}
@media (max-width: 640px) {{ .corpo {{ grid-template-columns: 1fr }} .corpo img {{ max-width: 420px }} body {{ font-size: 16px }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ scroll-behavior: auto }} }}
html {{ scroll-behavior: smooth }}
</style>
<main>
<header>
  <p class="eyebrow">Sessão clínica · Anestesiologia · UFRJ</p>
  <h1>Guia de fala das aminas vasoativas</h1>
  <p>O que dizer em cada slide, com o relógio acumulado, a frase-chave, a transição para o próximo e o que guardar para as perguntas. O mesmo texto está nas notas do apresentador de cada slide.</p>
  <p>Referências completas da aula: <a href="https://github.com/brunomoraesdubois-bit/Bruno/blob/claude/aminas-vasoativas-project-w6qsns/apresentacao/referencias.md">apresentacao/referencias.md</a> (o mesmo endereço do QR code do último slide).</p>
</header>
<div class="painel">
  <section><h3>Tempo previsto</h3><p class="total">{mmss(total)}</p><p style="margin:6px 0 0;color:var(--suave)">{len(dados)} slides. Ensaiar com cronômetro mirando 15 minutos.</p></section>
  <section><h3>Marcos no cronômetro</h3><ul>{marcos_html}</ul></section>
  <section><h3>Durante a fala</h3><ul><li>Diga a frase-chave de cada slide, mesmo que corte o resto.</li><li>Os slides aparecem prontos, sem cliques internos: um avanço por slide.</li><li>Números de estudos só se perguntarem.</li><li>No slide {N("intraop")[0]}, cite o estudo de Gouvêa e Diaz (PLoS One 2022) como dado do serviço.</li></ul></section>
</div>
<nav class="indice" aria-label="Slides">{indice}</nav>
{"".join(blocos)}
<h2 class="secao">Perguntas prováveis</h2>
{perguntas}
{secao_reserva}
</main>
'''
open(S + "/guia/guia-de-fala.html", "w", encoding="utf-8").write(page)
print(total, len(page)//1024, "KB")
