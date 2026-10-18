# Monta o guia de fala nas notas dos slides principais (TEMPO, PONTO-CHAVE, FALA, TRANSIÇÃO, SE PERGUNTAREM)
# e gera a mesma informação em guia-de-fala.html. Fonte da fala: as notas da versão anterior (v21/antes).
import json, re, html, os, io, base64
S = "/tmp/claude-0/-home-user-Bruno/82e201e1-5baf-5943-97e1-cc467015b7d6/scratchpad"
P = S + "/artifact-files/351a25a9-1efc-412b-9232-d1cf8f2e53fe/project"
ANTES = S + "/v21/antes"
deck = json.load(open(P + "/deck.json", encoding="utf-8"))
principal = deck["order"][:deck["order"].index("divisor")]

G = {  # id: (segundos, ponto-chave, transição)
 "cover": (20, "A aula nasceu de uma pergunta prática: quando a milrinona tem indicação?", "Para responder, o objetivo da aula."),
 "objetivos": (30, "Qual componente da PAM está falhando?", "Primeiro, de que depende a PAM."),
 "fisiologia": (60, "Vasoplegia pede vasopressor; bomba fraca, inotrópico; pré-carga baixa, volume.", "Mas PAM normal não basta: pressão não é perfusão."),
 "perfusao": (60, "Inotrópico se decide por hipoperfusão e débito, não só pela pressão.", "Definido o problema, as ferramentas: os receptores."),
 "receptores": (45, "Cada droga tem um perfil de receptores; vasopressina e milrinona usam outras vias.", "Antes das drogas, uma classificação rápida."),
 "classificacao": (30, "Catecolamina: infusão titulável. Não catecolamina: bolus.", "Começo pela droga de primeira linha."),
 "noradrenalina": (75, "α1 potente com β1 modesto: sobe a PAM e preserva o débito.", "A adrenalina é parecida na estrutura, mas tem outro perfil."),
 "adrenalina": (60, "Dose baixa, β; dose alta, α. Droga da anafilaxia; terceira droga no choque séptico.", "Agora os dois inotrópicos clássicos."),
 "dopadobuta": (60, "Dopamina fora da primeira linha; dobutamina para baixo débito com hipoperfusão.", "Para entender a diferença entre dobutamina e milrinona, um esquema."),
 "sinalizacao": (75, "Dobutamina aumenta a produção de AMPc; milrinona impede a degradação.", "Com esse mecanismo, a milrinona fica fácil de entender."),
 "milrinona": (45, "Inodilatador de meia-vida longa e eliminação renal.", "E a pergunta central: quando escolher cada uma."),
 "milrdobu": (75, "Primeiro a indicação; depois a escolha é farmacológica, sem superioridade em desfecho.", "Saindo dos inotrópicos, as drogas de bolus do centro cirúrgico."),
 "fenilefedrina": (60, "Fenilefrina: tônus baixo com FC alta. Efedrina: tônus baixo com bradicardia.", "E quando as catecolaminas não bastam?"),
 "vasorefrat": (60, "Vasopressina age por outra via (V1) e poupa catecolamina.", "Juntando tudo no choque séptico."),
 "ssc2026": (60, "Noradrenalina, depois vasopressina, depois adrenalina; PAM inicial de 65 mmHg.", "No centro cirúrgico, o raciocínio é o mesmo, com outras causas."),
 "intraop": (75, "Afastar causas, identificar o mecanismo, escolher a droga.", "E quanto de PAM é suficiente no intraoperatório?"),
 "pamintraop": (45, "PAM de 60–65 mmHg como piso; alvo maior só em selecionados.", "Para fechar."),
 "mensagens": (45, "A droga certa corrige o componente que falha, na menor dose e pelo menor tempo.", "Obrigado. Fico à disposição para perguntas."),
}
FALA = {
 "cover": "Bom dia. Sou Bruno Dubois; meus orientadores são Marcelo Bandeira e Glauber Gouvea. O tema é aminas vasoativas. A aula nasceu de uma discussão em sala sobre o uso de milrinona: quando ela tem indicação, e quando a dobutamina ou um vasopressor seriam a escolha. Vou partir da fisiologia, passar pelas drogas e terminar no choque séptico e no centro cirúrgico.",
 "mensagens": "Voltando à pergunta do início: qual componente da PAM está falhando? Vasoplegia pede noradrenalina e, quando a dose sobe, vasopressina; baixo débito com hipoperfusão pede inotrópico, com a milrinona reservada sobretudo para o VD com hipertensão pulmonar; bradicardia pede efedrina; anafilaxia, adrenalina. A droga certa é a que corrige esse componente, na menor dose eficaz e pelo menor tempo. Para discutir com o grupo: no nosso serviço, como documentamos o baixo débito antes do inotrópico, e quando associamos vasopressina?",
}
TROCAS = {
 "objetivos": [(" e num caso de falência de VD após CEC", ""), ("no choque séptico, no centro cirúrgico", "no choque séptico e no centro cirúrgico")],
 "milrdobu": [("Para discutir o caso que motivou a aula:", "Na prática, três perguntas antes de escolher:")],
 "intraop": [("Na anafilaxia, adrenalina.", "Na anafilaxia, adrenalina. Um dado da casa: Gouvêa, Diaz e colaboradores avaliaram o VD por ETE em 19 transplantes hepáticos, e a função foi normal em todas as fases, inclusive após a reperfusão (PLoS One 2022). Na hipotensão da reperfusão, o eco ajuda a separar vasoplegia de disfunção ventricular antes de escolher entre vasopressor e inotrópico.")],
}
EXTRA_MANGA = {
 "intraop": "Gouvêa G, Feiner J, Joshi S, Diaz R et al., PLoS One 2022;17(10):e0275301: estudo observacional, 19 adultos, TAPSE e variação fracional de área do VD em cinco fases (basal, hepatectomia, anepática, pós-reperfusão e fechamento); função do VD normal ao longo do procedimento.",
}

def mmss(s): return f"{s//60}:{s%60:02d}"
def dur(s): return " ".join(x for x in ((f"{s//60} min" if s >= 60 else ""), (f"{s%60} s" if s % 60 else "")) if x)

def base(id_):
    t = open(f"{ANTES}/slides/{id_}.html", encoding="utf-8").read()
    n = html.unescape(re.search(r"<aside>(.*?)</aside>", t, re.S).group(1)).strip()
    n = re.sub(r"^(Trinta segundos|Quarenta e cinco segundos|Um minuto e quinze|Um minuto)\.\s*", "", n)
    partes = n.split("Se perguntarem:")
    return partes[0].strip(), ("Se perguntarem:".join(partes[1:])).strip()

dados = []; relogio = 0
for id_ in principal:
    seg, chave, trans = G[id_]
    fala, manga = base(id_)
    fala = FALA.get(id_, fala)
    for a, b in TROCAS.get(id_, []):
        assert a in fala, (id_, a); fala = fala.replace(a, b)
    if id_ in EXTRA_MANGA: manga = (manga + " " + EXTRA_MANGA[id_]).strip()
    if id_ == "cover": manga = ""
    ini = relogio; relogio += seg
    dados.append(dict(id=id_, seg=seg, ini=ini, fim=relogio, chave=chave, trans=trans, fala=fala, manga=manga))
TOTAL = relogio

for i, x in enumerate(dados, 1):
    linhas = [f"TEMPO: {dur(x['seg'])} ({mmss(x['ini'])} → {mmss(x['fim'])})"]
    if x["id"] == "cover":
        linhas[0] += f". Total previsto: {mmss(TOTAL).replace(':', ' min ')} s nos {len(dados)} slides principais; ensaiar em 16 a 17 minutos, sem passar de 20."
    linhas += [f"PONTO-CHAVE: {x['chave']}", f"FALA: {x['fala']}", f"TRANSIÇÃO: {x['trans']}"]
    if x["manga"]: linhas.append(f"SE PERGUNTAREM: {x['manga']}")
    nota = "\n".join(linhas)
    assert len(nota) <= 4000, (x["id"], len(nota))
    p = f"{P}/slides/{x['id']}.html"; t = open(p, encoding="utf-8").read()
    t = re.sub(r"<aside>.*?</aside>", lambda m: "<aside>" + html.escape(nota, quote=False) + "</aside>", t, flags=re.S)
    open(p, "w", encoding="utf-8").write(t)
json.dump(dict(total=TOTAL, slides=dados), open(S + "/guia/guia.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(TOTAL, mmss(TOTAL), max(len(x["fala"]) for x in dados))
