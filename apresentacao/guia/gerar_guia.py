# Gera o guia de fala (HTML) a partir das notas dos slides principais
import json, re, base64, io, html
from PIL import Image
S = "/tmp/claude-0/-home-user-Bruno/82e201e1-5baf-5943-97e1-cc467015b7d6/scratchpad"
notas = json.load(open(S + "/v20/notas.json", encoding="utf-8"))
import os
prints = sorted(os.listdir(S + "/v20/webfull"))

TEMPO = [20, 30, 60, 60, 45, 30, 75, 60, 60, 75, 45, 75, 60, 60, 60, 75, 45, 60, 75, 45]
CHAVE = [
 "A aula nasceu de uma pergunta prática: quando a milrinona tem indicação?",
 "Qual componente da PAM está falhando?",
 "Vasoplegia pede vasopressor; bomba fraca, inotrópico; pré-carga baixa, volume.",
 "Inotrópico se decide por hipoperfusão e débito, não só pela pressão.",
 "Cada droga tem um perfil de receptores; vasopressina e milrinona usam outras vias.",
 "Catecolamina: infusão titulável. Não catecolamina: bolus.",
 "α1 potente com β1 modesto: sobe a PAM e preserva o débito.",
 "Dose baixa, β; dose alta, α. Droga da anafilaxia; terceira droga no choque séptico.",
 "Dopamina fora da primeira linha; dobutamina para baixo débito com hipoperfusão.",
 "Dobutamina aumenta a produção de AMPc; milrinona impede a degradação.",
 "Inodilatador de meia-vida longa e eliminação renal.",
 "Primeiro a indicação; depois a escolha é farmacológica, sem superioridade em desfecho.",
 "Fenilefrina: tônus baixo com FC alta. Efedrina: tônus baixo com bradicardia.",
 "Vasopressina age por outra via (V1) e poupa catecolamina.",
 "Noradrenalina, depois vasopressina, depois adrenalina; PAM inicial de 65 mmHg.",
 "Afastar causas, identificar o mecanismo, escolher a droga.",
 "PAM de 60–65 mmHg como piso; alvo maior só em selecionados.",
 "Pausa de alguns segundos: falência de VD ou vasoplegia?",
 "Na falência de VD com hipertensão pulmonar, a milrinona tem fundamento; na vasoplegia, a droga é o vasopressor.",
 "A droga certa corrige o componente que falha, na menor dose e pelo menor tempo.",
]
TRANS = [
 "Para responder, o objetivo da aula.",
 "Primeiro, de que depende a PAM.",
 "Mas PAM normal não basta: pressão não é perfusão.",
 "Definido o problema, as ferramentas: os receptores.",
 "Antes das drogas, uma classificação rápida.",
 "Começo pela droga de primeira linha.",
 "A adrenalina é parecida na estrutura, mas tem outro perfil.",
 "Agora os dois inotrópicos clássicos.",
 "Para entender a diferença entre dobutamina e milrinona, um esquema.",
 "Com esse mecanismo, a milrinona fica fácil de entender.",
 "E a pergunta central: quando escolher cada uma.",
 "Saindo dos inotrópicos, as drogas de bolus do centro cirúrgico.",
 "E quando as catecolaminas não bastam?",
 "Juntando tudo no choque séptico.",
 "No centro cirúrgico, o raciocínio é o mesmo, com outras causas.",
 "E quanto de PAM é suficiente no intraoperatório?",
 "Agora, um caso para aplicar tudo isso.",
 "A resposta e a conduta.",
 "Para fechar.",
 "Obrigado. Fico à disposição para perguntas.",
]
FALA_CAPA = ("Bom dia. Sou Bruno Dubois; meus orientadores são Marcelo Bandeira e Glauber Gouvea. "
 "O tema é aminas vasoativas. A aula nasceu de uma discussão em sala sobre o uso de milrinona: "
 "quando ela tem indicação, e quando a dobutamina ou um vasopressor seriam a escolha. "
 "Vou partir da fisiologia, passar pelas drogas e terminar com um caso.")
FALA_MENSAGENS = ("Voltando à pergunta do início: qual componente da PAM está falhando? Vasoplegia pede noradrenalina e, "
 "quando a dose sobe, vasopressina; baixo débito com hipoperfusão pede inotrópico, com a milrinona reservada sobretudo para o VD "
 "com hipertensão pulmonar; bradicardia pede efedrina; anafilaxia, adrenalina. A droga certa é a que corrige esse componente, "
 "na menor dose eficaz e pelo menor tempo. Para discutir com o grupo: no nosso serviço, como documentamos o baixo débito antes "
 "do inotrópico, e quando associamos vasopressina?")

def limpar(n):
    n = re.sub(r"^(Trinta segundos|Quarenta e cinco segundos|Um minuto e quinze|Um minuto|Vinte segundos)\.\s*", "", n.strip())
    partes = n.split("Se perguntarem:")
    fala = partes[0].strip()
    manga = ("Se perguntarem:".join(partes[1:])).strip() if len(partes) > 1 else ""
    fala = fala.replace("Deixar a pergunta para a plateia por alguns segundos antes de passar.", "").strip()
    return fala, manga

def mmss(s): return f"{s//60}:{s%60:02d}"
def dur(s): return (f"{s//60} min " if s >= 60 else "") + (f"{s%60} s" if s % 60 else "").strip()

def thumb(i):
    im = Image.open(f"{S}/v20/webfull/{prints[i]}").convert("RGB").resize((640, 360), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=72, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()

e = html.escape
blocos = []; relogio = 0
for i, x in enumerate(notas):
    fala, manga = limpar(x["notas"])
    if x["id"] == "cover": fala, manga = FALA_CAPA, ""
    if x["id"] == "mensagens": fala = FALA_MENSAGENS
    ini = relogio; relogio += TEMPO[i]
    pausa = '<p class="pausa">Pausa de 3 a 5 segundos antes de mostrar a resposta.</p>' if x["id"] == "casovd" else ""
    blocos.append(f'''
<article class="slide" id="s{x["n"]}">
  <div class="cab"><span class="num">{x["n"]:02d}</span><h2>{e(x["titulo"])}</h2><span class="tempo"><b>{mmss(ini)}</b> → {mmss(relogio)} · {dur(TEMPO[i])}</span></div>
  <div class="corpo">
    <img src="{thumb(i)}" alt="Miniatura do slide {x["n"]}: {e(x["titulo"])}" loading="lazy">
    <div class="texto">
      <p class="chave">{e(CHAVE[i])}</p>
      <p class="fala">{e(fala)}</p>{pausa}
      <p class="trans"><span>Transição</span> {e(TRANS[i])}</p>
      {f'<details><summary>Se perguntarem</summary><p>{e(manga)}</p></details>' if manga else ''}
    </div>
  </div>
</article>''')
total = relogio

PERGUNTAS = [
 ("Por que não milrinona sempre que o paciente usa betabloqueador?",
  "Porque o benefício é teórico. A milrinona age depois do receptor e mantém efeito no betabloqueado, mas na subanálise do DOREMI (93 pacientes betabloqueados) não houve vantagem clínica. Slides 10 e 12."),
 ("O DOREMI não mostrou que as duas são iguais?",
  "Não houve diferença significativa (49% × 54%; RR 0,90; IC 95% 0,69–1,19; n = 192), mas o intervalo é largo: o estudo não prova equivalência. Arritmia, hipotensão sustentada e necessidade de vasopressor também não diferiram."),
 ("Milrinona no choque séptico?",
  "A SSC 2026 não encontrou dados para comparar com a dobutamina. Num ECR de 2025 (Tongyoo, 64 pacientes), a milrinona aumentou o débito em 6 h, sem diferença de mortalidade (50% × 50%). Débito maior não é desfecho melhor."),
 ("Então quando a milrinona tem indicação?",
  "Disfunção ventricular com baixo débito que exige inotrópico, sobretudo VD com hipertensão pulmonar e dificuldade de saída de CEC; com noradrenalina se a PAM cair. Sem baixo débito, a hipotensão é vasoplegia e a droga é o vasopressor. Slides 12, 18 e 19."),
 ("Quando associar vasopressina?",
  "SSC 2026: quando a dose de noradrenalina está subindo, sem limiar definido; na enquete dos painelistas, mediana de 0,3 mcg/kg/min. Antecipar como política (VASSPR) não reduziu mortalidade. Slide 15 e reserva."),
 ("Qual o alvo de PAM no intraoperatório?",
  "POQI 2024: PAM ≥60 mmHg em pacientes de risco como piso, maior com pressão venosa ou compartimental alta. HISTAP favoreceu ≥80 em hipertensos de alto risco; IMPROVE-multi e POISE-3 foram neutros. Slide 17 e reserva."),
 ("Noradrenalina em veia periférica é segura?",
  "Na metanálise de Tran, complicações em 7% (combinada 8,6%), 96% leves; menos com protocolo de segurança. A SSC 2026 sugere iniciar por veia periférica. Reserva “Início precoce e via periférica”."),
 ("Fenilefrina ou noradrenalina na cesárea?",
  "O consenso de 2018 recomenda vasopressor α-agonista em infusão profilática. A noradrenalina causa menos bradicardia materna, com pH umbilical semelhante (Sharkey, 10,7% × 37,5% de bradicardia). Reserva “Fenilefrina”."),
 ("Dopamina em dose renal?",
  "Não protege o rim: no ANZICS (n = 328), sem diferença em creatinina, diálise ou mortalidade."),
 ("E o azul de metileno?",
  "Resgate na vasoplegia refratária (pós-CEC, reperfusão hepática), com evidência limitada; interfere na oximetria e pode causar síndrome serotoninérgica."),
 ("Dose de noradrenalina em base ou em sal?",
  "No Brasil, a ampola de hemitartarato de 2 mg/mL tem 1 mg/mL de base; em sal, o número é o dobro. Registrar na prescrição. Reserva “Início precoce e via periférica”."),
 ("Como a PKA aumenta a corrente de cálcio?",
  "Parte do efeito passa pela fosforilação da proteína Rad, que deixa de inibir o canal tipo L (Liu, Nature 2020). A sinalização do AMPc é compartimentalizada em nanodomínios (Zaccolo e Kovanich, Physiol Rev 2025)."),
]
RESERVA = ["Síntese das drogas", "Dopamina", "Dobutamina", "Fenilefrina", "Efedrina", "Vasopressina", "Choque refratário: adjuvantes",
           "Sequência de vasopressores na SSC 2026", "Alvo de PAM no choque séptico", "Início precoce e via periférica",
           "Alvo de PAM no intraoperatório: ensaios", "Roteiro", "Referências"]

perguntas = "".join(f'<details class="q"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in PERGUNTAS)
reserva = "".join(f'<li><span>{22+i}</span> {e(r)}</li>' for i, r in enumerate(RESERVA))
marcos = [(6, "fim da farmacologia básica"), (12, "fim de milrinona × dobutamina"), (17, "fim do intraoperatório")]
acum = [sum(TEMPO[:k]) for k in range(len(TEMPO)+1)]
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
.pausa {{ margin: 0; font-weight: 600; color: var(--acento) }}
.trans {{ margin: 0; color: var(--suave); font-style: italic }}
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
  <p>O que dizer em cada slide, com o relógio acumulado, a frase-chave, a transição para o próximo e o que guardar para as perguntas.</p>
</header>
<div class="painel">
  <section><h3>Tempo previsto</h3><p class="total">{mmss(total)}</p><p style="margin:6px 0 0;color:var(--suave)">20 slides principais. Ensaiar em 18 a 19 minutos, sem passar de 20.</p></section>
  <section><h3>Marcos no cronômetro</h3><ul>{marcos_html}</ul></section>
  <section><h3>Durante a fala</h3><ul><li>Diga a frase-chave de cada slide, mesmo que corte o resto.</li><li>Números de estudos só se perguntarem.</li><li>No caso (slide 18), faça a pausa e olhe para a plateia.</li></ul></section>
</div>
<nav class="indice" aria-label="Slides">{indice}</nav>
{"".join(blocos)}
<h2 class="secao">Perguntas prováveis</h2>
{perguntas}
<h2 class="secao">Slides de reserva</h2>
<p style="margin:0;color:var(--suave)">Depois do divisor (slide 21). Use para responder perguntas sem voltar à apresentação principal.</p>
<ol class="reserva">{reserva}</ol>
</main>
'''
open(S + "/guia/guia-de-fala.html", "w", encoding="utf-8").write(page)
print(total, len(page)//1024, "KB")
