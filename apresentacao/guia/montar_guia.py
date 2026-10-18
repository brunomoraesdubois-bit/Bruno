# Monta o guia de fala nas notas dos slides principais (TEMPO, PONTO-CHAVE, FALA, TRANSIÇÃO, SE PERGUNTAREM)
# e gera a mesma informação em guia-de-fala.html. Fonte da fala: as notas da versão anterior (v21/antes).
import json, re, html, os, io, base64
S = "/tmp/claude-0/-home-user-Bruno/82e201e1-5baf-5943-97e1-cc467015b7d6/scratchpad"
P = S + "/artifact-files/351a25a9-1efc-412b-9232-d1cf8f2e53fe/project"
ANTES = S + "/v21/antes"
deck = json.load(open(P + "/deck.json", encoding="utf-8"))
principal = deck["order"][:deck["order"].index("divisor")]

G = {  # id: (segundos, ponto-chave, transição)
 "cover": (30, "A aula nasceu de uma pergunta prática: quando a milrinona tem indicação?", "A pergunta que vai orientar a aula é: qual componente da pressão arterial está falhando?"),
 "objetivos": (30, "Qual componente da PAM está falhando?", "Para responder, precisamos entender de que depende a pressão arterial média."),
 "fisiologia": (60, "Vasoplegia pede vasopressor; bomba fraca, inotrópico; pré-carga baixa, volume.", "Mas PAM normal não basta: pressão não é perfusão."),
 "perfusao": (60, "Inotrópico se decide por hipoperfusão e débito, não só pela pressão.", "Definido o problema, as ferramentas: os receptores."),
 "receptores": (45, "Cada droga tem um perfil de receptores; vasopressina e milrinona usam outras vias.", "Antes das drogas, uma classificação rápida."),
 "classificacao": (35, "Catecolaminas: meia-vida curta, infusão titulável; fenilefrina e efedrina: bolus na hipotensão transitória.", "Começo pela droga de primeira linha."),
 "noradrenalina": (60, "α1 potente com β1 modesto: sobe a PAM e preserva o débito.", "A adrenalina é parecida na estrutura, mas tem outro perfil."),
 "adrenalina": (50, "Dose baixa, β; dose alta, α. Droga da anafilaxia; terceira droga no choque séptico.", "Passando à dopamina e à dobutamina, duas catecolaminas com aplicações muito diferentes."),
 "dopadobuta": (60, "Dopamina fora da primeira linha; dobutamina para baixo débito com hipoperfusão.", "Para entender a diferença entre dobutamina e milrinona, um esquema."),
 "sinalizacao": (90, "Dobutamina aumenta a produção de AMPc; milrinona impede a degradação.", "Com esse mecanismo, a milrinona fica fácil de entender."),
 "milrinona": (50, "Inodilatador de meia-vida longa e eliminação renal.", "E a pergunta central: quando escolher cada uma."),
 "milrdobu": (80, "Primeiro a indicação; depois a escolha é farmacológica, sem superioridade em desfecho.", "Quando a milrinona faz sentido, o VD está em jogo: o que fazer na falência de VD."),
 "condutavd": (50, "Na falência de VD, a milrinona entra na contratilidade, com noradrenalina; com débito preservado e RVS baixa, considerar vasoplegia.", "Saindo dos inotrópicos, as drogas de bolus do centro cirúrgico."),
 "fenilefedrina": (55, "Fenilefrina: tônus baixo com FC alta. Efedrina: tônus baixo com bradicardia.", "E quando as catecolaminas não bastam?"),
 "vasorefrat": (60, "Vasopressina age por outra via (V1) e poupa catecolamina.", "Juntando tudo no choque séptico."),
 "ssc2026": (60, "Noradrenalina, depois vasopressina, depois adrenalina; PAM inicial de 65 mmHg.", "No centro cirúrgico, o raciocínio é o mesmo, com outras causas."),
 "intraop": (85, "Afastar causas, identificar o mecanismo, escolher a droga.", "E quanto de PAM é suficiente no intraoperatório?"),
 "pamintraop": (55, "PAM de 60–65 mmHg como piso; alvo maior apenas em selecionados.", "Para terminar, voltamos à pergunta do início: qual é o mecanismo do distúrbio hemodinâmico?"),
 "mensagens": (50, "A droga certa corrige o componente que falha, na menor dose e pelo menor tempo.", "Obrigado. Fico à disposição para perguntas."),
}
FALA = {
 "cover": "Bom dia. Sou Bruno Dubois; meus orientadores são Marcelo Bandeira e Glauber Gouvêa. O tema é aminas vasoativas. A aula nasceu de uma discussão em sala sobre o uso de milrinona: quando ela tem indicação, e quando a dobutamina ou um vasopressor seriam a escolha. Vou partir da fisiologia, passar pelas drogas e terminar no choque séptico e no centro cirúrgico.",
 "condutavd": "Na falência de VD, quatro frentes andam juntas. Primeiro, a pressão de perfusão: o VD fica isquêmico quando a PAM cai, então noradrenalina ou vasopressina. Segundo, a resistência pulmonar: corrigir hipóxia, hipercapnia e acidose e, se preciso, vasodilatador pulmonar inalado. Terceiro, a contratilidade: aqui a milrinona faz sentido, porque é inotrópica e reduz a resistência pulmonar; a dobutamina é alternativa. Quarto, volume e ritmo: o VD dilatado tolera mal mais volume. A milrinona pode baixar a PAM e não substitui o diagnóstico: com débito preservado e resistência baixa, considerar vasoplegia, e aí a droga é o vasopressor.",
 "mensagens": "Voltando à pergunta do início: qual componente da PAM está falhando? Vasoplegia pede noradrenalina e, quando a dose sobe, vasopressina; baixo débito com hipoperfusão pede inotrópico, com a milrinona reservada sobretudo para o VD com hipertensão pulmonar; na hipotensão anestésica com bradicardia, efedrina; anafilaxia, adrenalina. A droga certa é a que corrige esse componente, na menor dose eficaz e pelo menor tempo. Para discutir com o grupo: no nosso serviço, como documentamos o baixo débito antes do inotrópico, e quando associamos vasopressina?",
}
TROCAS = {
 "classificacao": [("As catecolaminas têm meia-vida de minutos e são usadas em infusão; sem o anel catecol, fenilefrina e efedrina duram mais e servem para bolus.", "A curta duração das catecolaminas facilita a titulação por infusão contínua; fenilefrina e efedrina, sem o anel catecol, duram mais e costumam ser usadas em bolus na hipotensão transitória, embora a fenilefrina também possa ser infundida.")],
 "sinalizacao": [("A PKA fosforila três alvos: o canal de cálcio tipo L e o RyR2, o que aumenta o cálcio na sístole, ou seja, inotropismo; e o fosfolambam, que deixa de inibir a SERCA2a e acelera a recaptação do cálcio na diástole: lusitropismo.", "A sinalização pela PKA aumenta a disponibilidade de cálcio na sístole, pela fosforilação do canal de cálcio tipo L, favorecendo a contração; na diástole, a fosforilação do fosfolambam reduz a inibição da SERCA2a e acelera a recaptação de cálcio, melhorando o relaxamento.")],
 "milrdobu": [("ainda que, no betabloqueado, o benefício seja teórico.", "ainda que, no betabloqueado, o benefício seja teórico e a subanálise negativa do DOREMI não prove equivalência.")],
 "objetivos": [(" e num caso de falência de VD após CEC", ""), ("no choque séptico, no centro cirúrgico", "no choque séptico e no centro cirúrgico")],
 "milrdobu": [("Para discutir o caso que motivou a aula:", "Na prática, três perguntas antes de escolher:")],
 "perfusao": [("Na clínica, enchimento capilar, livedo e temperatura das extremidades; no laboratório, lactato, saturação venosa central e gap de CO₂; e ainda diurese e consciência.", "Na clínica, enchimento capilar e temperatura das extremidades; no laboratório, lactato e saturação venosa central."), ("Antes da droga, vale perguntar se o débito responde a volume, com parâmetros dinâmicos ou com um teste de volume medindo o débito; o eco mostra o VTI e a função dos dois ventrículos.", "Antes da droga, vale perguntar se o débito responde a volume, com parâmetros dinâmicos ou um teste de volume medindo o débito; o eco mostra o VTI e a função dos ventrículos.")],
 "intraop": [("Um dado do nosso serviço: Gouvêa, Diaz e colaboradores avaliaram o VD por ETE em 19 transplantes hepáticos, e a função foi normal em todas as fases, inclusive após a reperfusão (PLoS One 2022). Na hipotensão da reperfusão, o eco ajuda a separar vasoplegia de disfunção ventricular antes de escolher entre vasopressor e inotrópico.", "Um dado do nosso serviço: Gouvêa, Diaz e colaboradores avaliaram a função do VD por ecocardiografia transesofágica em 19 pacientes selecionados durante o transplante hepático; a função permaneceu preservada nos momentos avaliados, inclusive após a reperfusão (PLoS One 2022). Isso reforça a importância de identificar o mecanismo da hipotensão, sem presumir que exista falência de VD."), ("Se a hipotensão persistir, avaliar a resposta a volume com parâmetros dinâmicos e fazer eco. ", "Se persistir, avaliar a resposta a volume e fazer eco. "), ("Bolus na hipotensão transitória e infusão na persistente. ", "")],
}
EXTRA_MANGA = {
 "sinalizacao": "A contribuição funcional da fosforilação do RyR2 pela PKA ainda é debatida; por isso a figura mostra apenas os dois alvos bem estabelecidos, o canal tipo L e o fosfolambam.",
 "intraop": "População selecionada; o estudo não permite concluir que toda hipotensão na reperfusão seja vasoplegia. Gouvêa G, Feiner J, Joshi S, Diaz R et al., PLoS One 2022;17(10):e0275301: estudo observacional, 19 adultos, TAPSE e variação fracional de área do VD em cinco fases (basal, hepatectomia, anepática, pós-reperfusão e fechamento); função do VD normal ao longo do procedimento.",
}

def mmss(s): return f"{s//60}:{s%60:02d}"
def dur(s): return " ".join(x for x in ((f"{s//60} min" if s >= 60 else ""), (f"{s%60} s" if s % 60 else "")) if x)

def base(id_):
    # Lê as notas atuais do slide (já no formato do guia); se ainda estiverem no formato antigo, converte
    t = open(f"{P}/slides/{id_}.html", encoding="utf-8").read()
    n = html.unescape(re.search(r"<aside>(.*?)</aside>", t, re.S).group(1)).strip()
    if "FALA:" in n:
        campos = dict(re.findall(r"^([A-ZÇÃÕ\- ]+): ?(.*)$", n, re.M))
        return campos.get("FALA", "").strip(), campos.get("SE PERGUNTAREM", "").strip()
    n = re.sub(r"^(Trinta segundos|Quarenta e cinco segundos|Um minuto e quinze|Um minuto)\.\s*", "", n)
    partes = n.split("Se perguntarem:")
    return partes[0].strip(), ("Se perguntarem:".join(partes[1:])).strip()

dados = []; relogio = 0
for id_ in principal:
    seg, chave, trans = G[id_]
    fala, manga = base(id_)
    fala = FALA.get(id_, fala)
    for a, b in TROCAS.get(id_, []):
        if a in fala and (not b or b not in fala): fala = fala.replace(a, b)
    if id_ in EXTRA_MANGA and EXTRA_MANGA[id_] not in manga: manga = (manga + " " + EXTRA_MANGA[id_]).strip()
    if id_ == "cover": manga = ""
    ini = relogio; relogio += seg
    dados.append(dict(id=id_, seg=seg, ini=ini, fim=relogio, chave=chave, trans=trans, fala=fala, manga=manga))
TOTAL = relogio

for i, x in enumerate(dados, 1):
    tempo = f"TEMPO: {dur(x['seg'])} ({mmss(x['ini'])} → {mmss(x['fim'])})"
    if x["id"] == "cover":
        tempo += f". Total previsto: {mmss(TOTAL).replace(':', ' min ')} s nos {len(dados)} slides principais; ensaiar em cerca de 17 minutos e meio, sem passar de 18."
    linhas = [f"FALA: {x['fala']}", f"TRANSIÇÃO: {x['trans']}", tempo, f"PONTO-CHAVE: {x['chave']}"]
    if x["manga"]: linhas.append(f"SE PERGUNTAREM: {x['manga']}")
    nota = "\n".join(linhas)
    assert len(nota) <= 4000, (x["id"], len(nota))
    p = f"{P}/slides/{x['id']}.html"; t = open(p, encoding="utf-8").read()
    t = re.sub(r"<aside>.*?</aside>", lambda m: "<aside>" + html.escape(nota, quote=False) + "</aside>", t, flags=re.S)
    open(p, "w", encoding="utf-8").write(t)
from reserva_notas import RESERVA
ORDEM = ["FALA", "USO", "PONTO-CHAVE", "SE PERGUNTAREM"]
for id_, linhas in RESERVA.items():
    if id_ in principal: continue
    linhas = sorted(linhas, key=lambda l: ORDEM.index(l.split(":")[0]))
    nota = "\n".join(linhas); assert len(nota) <= 4000, (id_, len(nota))
    p = f"{P}/slides/{id_}.html"; t = open(p, encoding="utf-8").read()
    assert t.count("<aside>") == 1, id_
    t = re.sub(r"<aside>.*?</aside>", lambda m: "<aside>" + html.escape(nota, quote=False) + "</aside>", t, flags=re.S)
    open(p, "w", encoding="utf-8").write(t)
json.dump(dict(total=TOTAL, slides=dados), open(S + "/guia/guia.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(TOTAL, mmss(TOTAL), max(len(x["fala"]) for x in dados))
