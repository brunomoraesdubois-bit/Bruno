# Monta o guia de fala nas notas dos slides principais (TEMPO, PONTO-CHAVE, FALA, TRANSIÇÃO, SE PERGUNTAREM)
# e gera a mesma informação em guia-de-fala.html. Fonte da fala: as notas da versão anterior (v21/antes).
import json, re, html, os, io, base64
S = "/tmp/claude-0/-home-user-Bruno/82e201e1-5baf-5943-97e1-cc467015b7d6/scratchpad"
P = S + "/artifact-files/351a25a9-1efc-412b-9232-d1cf8f2e53fe/project"
ANTES = S + "/v21/antes"
deck = json.load(open(P + "/deck.json", encoding="utf-8"))
principal = deck["order"]

G = {  # id: (segundos, ponto-chave, transição)
 "cover": (30, "A aula nasceu de uma pergunta prática: quando a milrinona tem indicação?", "A pergunta que vai orientar a aula é: qual componente da pressão arterial está falhando?"),
 "objetivos": (25, "Qual componente da PAM está falhando?", "Para responder, precisamos entender de que depende a pressão arterial média."),
 "fisiologia": (60, "Vasoplegia pede vasopressor; bomba fraca, inotrópico; pré-carga baixa, volume.", "Mas PAM normal não basta: pressão não é perfusão."),
 "perfusao": (65, "Inotrópico se decide por hipoperfusão e débito, não só pela pressão.", "Definido o problema, as ferramentas: os receptores."),
 "receptores": (45, "Cada droga tem um perfil de receptores; vasopressina e milrinona usam outras vias.", "Antes das drogas, uma classificação rápida."),
 "classificacao": (35, "Catecolaminas: meia-vida curta, infusão titulável; fenilefrina e efedrina: bolus na hipotensão transitória.", "Começo pela droga de primeira linha."),
 "noradrenalina": (45, "α1 potente com β1 modesto: sobe a PAM e preserva o débito.", "A adrenalina é parecida na estrutura, mas tem outro perfil."),
 "adrenalina": (45, "Dose baixa, β; dose alta, α. Droga da anafilaxia; terceira droga no choque séptico.", "Passando à dopamina e à dobutamina, duas catecolaminas com aplicações muito diferentes."),
 "dopadobuta": (65, "Dopamina fora da primeira linha; dobutamina para baixo débito com hipoperfusão.", "Para entender a diferença entre dobutamina e milrinona, um esquema."),
 "sinalizacao": (85, "Dobutamina aumenta a produção de AMPc; milrinona impede a degradação.", "Com esse mecanismo, a milrinona fica fácil de entender."),
 "milrinona": (50, "Inodilatador de meia-vida longa e eliminação renal.", "E a pergunta central: quando escolher cada uma."),
 "milrdobu": (100, "Primeiro a indicação; depois a escolha é farmacológica, sem superioridade em desfecho.", "Um cenário em que essa diferença farmacológica realmente importa é a falência de ventrículo direito. Como abordá-la?"),
 "condutavd": (55, "Na falência de VD, a milrinona entra na contratilidade, com noradrenalina; com débito preservado e RVS baixa, considerar vasoplegia.", "Saindo dos inotrópicos, as drogas de bolus do centro cirúrgico."),
 "fenilefedrina": (50, "Fenilefrina: tônus baixo com FC alta. Efedrina: tônus baixo com bradicardia.", "E quando as catecolaminas não bastam?"),
 "vasorefrat": (55, "Vasopressina age por outra via (V1) e poupa catecolamina.", "Juntando tudo no choque séptico."),
 "ssc2026": (65, "Noradrenalina, depois vasopressina, depois adrenalina; PAM inicial de 65 mmHg.", "No centro cirúrgico, o raciocínio é o mesmo, com outras causas."),
 "intraop": (85, "Afastar causas, identificar o mecanismo, escolher a droga.", "E quanto de PAM é suficiente no intraoperatório?"),
 "pamintraop": (70, "PAM de 60–65 mmHg como piso; alvo maior apenas em selecionados.", "Para terminar, voltamos à pergunta do início: qual é o mecanismo do distúrbio hemodinâmico?"),
 "mensagens": (35, "A droga certa corrige o componente que falha, na menor dose e pelo menor tempo.", "Com isso, chego ao fim."),
 "obrigado": (10, "Referências completas no QR code; abrir para perguntas.", ""),
}
FALA = {
 "cover": "Bom dia. Sou Bruno Dubois; meus orientadores são Marcelo Bandeira e Glauber Gouvêa. O tema é aminas vasoativas. A aula nasceu de uma discussão em sala sobre o uso de milrinona: quando ela tem indicação, e quando a dobutamina ou um vasopressor seriam a escolha. Vou partir da fisiologia, passar pelas drogas e terminar no choque séptico e no centro cirúrgico.",
 'fisiologia': 'A PAM depende do débito cardíaco e da resistência vascular, e a PVC pesa quando está alta. Na vasoplegia o problema é o tônus: sepse, anestesia geral, neuroeixo, anafilaxia, saída de CEC. Na falência de bomba o débito é baixo, em geral com resistência alta; na sepse, a disfunção miocárdica pode coexistir com vasoplegia. O α1 também contrai veias, recruta volume não estressado e aumenta o retorno venoso: Persichini e colaboradores mostraram, em pacientes com choque séptico, que reduzir a dose de noradrenalina diminui a pressão sistêmica média, o retorno venoso e o débito cardíaco. Para diferenciar, a ESICM 2025 recomenda eco como primeira imagem, parâmetros dinâmicos antes de mais volume e perfusão seriada pelo tempo de enchimento capilar.',
 'perfusao': 'Pressão não é fluxo: uma resistência alta pode manter a PAM com o débito baixo. Por isso, a decisão de usar inotrópico depende de sinais de hipoperfusão e de uma estimativa do débito, e não apenas da pressão. Os sinais estão no slide. Antes da droga, vale perguntar se o débito responde a volume, com parâmetros dinâmicos ou um teste de volume medindo o débito; o eco mostra o VTI e a função dos ventrículos. O inverso também vale: aumentar o débito com uma droga não é o mesmo que melhorar o desfecho. No OPTIME-CHF, 951 pacientes internados por insuficiência cardíaca descompensada, sem indicação clara de inotrópico, receberam milrinona ou placebo por 48 horas: não houve benefício, e a milrinona causou mais hipotensão sustentada, 10,7 contra 3,2%, e mais arritmia atrial.',
 'dopadobuta': 'Dopamina: o efeito muda com a dose, primeiro D1, depois β1 e, em doses altas, α1, mas a resposta varia muito entre pacientes. A dose “renal” não protege o rim: no ensaio da ANZICS, 328 pacientes críticos com disfunção renal inicial receberam dopamina em 2 mcg/kg/min ou placebo, sem diferença no pico de creatinina, na diálise ou na mortalidade. No SOAP II, 1.679 pacientes em choque receberam dopamina ou noradrenalina como primeira droga: mortalidade em 28 dias semelhante, 52,5 contra 48,5%, com o dobro de arritmias; por isso a SSC 2026 recomenda não usar a dopamina como primeira linha. Dobutamina: inotropismo β1 com queda discreta da resistência, indicada no baixo débito com hipoperfusão. Se a PAM cair, associar vasopressor para sustentar a pressão de perfusão.',
 'sinalizacao': 'Este é o mecanismo que separa as duas drogas. A dobutamina estimula o receptor β1; pela proteína Gs, a adenilato ciclase produz AMPc, que ativa a PKA. A sinalização pela PKA aumenta a disponibilidade de cálcio na sístole, pela fosforilação do canal de cálcio tipo L, favorecendo a contração; na diástole, a fosforilação do fosfolambam reduz a inibição da SERCA2a e acelera a recaptação de cálcio, melhorando o relaxamento. A milrinona entra em outro ponto: inibe a PDE3, a enzima que degrada o AMPc em 5′-AMP. Ela não depende do receptor β, mas precisa de alguma produção de AMPc. Por isso mantém efeito com betabloqueio ou com receptores dessensibilizados. Mas isso é fundamento farmacológico, não benefício demonstrado, como vamos ver no DOREMI daqui a dois slides. No músculo liso vascular, a mesma via AMPc–PKA inibe a quinase da cadeia leve da miosina, a MLCK, e o vaso relaxa: por isso a milrinona é inodilatadora e pode baixar a PAM. E, como as duas aumentam AMPc e cálcio, as duas podem causar arritmias.',
 'milrdobu': 'Esta é a pergunta prática da aula. Primeiro, a indicação: inotrópico se justifica quando há disfunção ventricular com baixo débito ou hipoperfusão, depois de otimizar volume e PAM. Se a hipotensão é por vasoplegia, a droga é o vasopressor, e um inodilatador baixa ainda mais a pressão. O único ensaio que comparou as duas é o DOREMI: randomizado e duplo-cego, 192 pacientes com choque cardiogênico receberam milrinona ou dobutamina. O desfecho composto, que incluía morte, parada ressuscitada, suporte mecânico ou transplante, infarto, AVC e diálise nova, ocorreu em 49% com milrinona e 54% com dobutamina, sem diferença; arritmia, hipotensão sustentada e necessidade de vasopressor também não diferiram. Na subanálise dos 93 pacientes que usavam betabloqueador antes do choque, a milrinona não teve vantagem. Isso não comprova equivalência; a escolha fica farmacológica, e as diferenças da tabela são perfis esperados. A milrinona faz sentido no VD com hipertensão pulmonar, como na saída de CEC, porque reduz a resistência pulmonar, e quando a taquicardia ou o betabloqueio limitam a dobutamina. Quando há indicação de inotrópico, a dobutamina pode ser mais conveniente se houver hipotensão associada, insuficiência renal, porque a milrinona acumula, ou necessidade de titulação rápida.',
 'ssc2026': 'A SSC 2026 organiza os vasopressores em sequência. Noradrenalina primeiro, iniciada cedo e, se preciso, por veia periférica. Vasopressina quando a dose de noradrenalina está subindo; a diretriz não define um limiar, e na enquete dos painelistas a mediana foi 0,3 mcg/kg/min. Adrenalina se a PAM continuar inadequada. Alvo inicial de 65 mmHg, ou 60 a 65 a partir dos 65 anos. Sobre o momento da vasopressina, o VASSPR, publicado neste mês: 3.959 pacientes com choque séptico em hospitais sorteados para iniciar a vasopressina com noradrenalina em 0,1 ou em 0,4 mcg/kg/min; a mortalidade foi igual, 31,8 contra 33,0%. Antecipar como regra não trouxe ganho. Na disfunção cardíaca com hipoperfusão apesar de volume e PAM adequados, dobutamina com noradrenalina, ou adrenalina; hidrocortisona sugerida; levosimendana e terlipressina, contra.',
 'intraop': 'Antes da droga, afastar causas tratáveis: plano anestésico profundo, hipovolemia, compressão aortocava, pneumotórax, anafilaxia. Se persistir, avaliar a resposta a volume e fazer eco. A escolha segue o mecanismo: tônus baixo com frequência preservada pede α1; bradicardia associada pede ação β1, com efedrina ou, se grave, adrenalina; baixo débito pede inotrópico, e a milrinona tem a vantagem de reduzir a resistência pulmonar. A vasoplegia que não responde às catecolaminas, como após CEC, com uso crônico de IECA ou BRA ou na reperfusão do enxerto hepático, pode responder à vasopressina, que age por outra via; o azul de metileno fica como resgate. Na cesárea, fenilefrina profilática, com a noradrenalina como alternativa. Na anafilaxia, adrenalina. Um dado do nosso serviço: Gouvêa, Diaz e colaboradores avaliaram por ETE a função do VD de 19 pacientes selecionados em cinco momentos do transplante hepático, do basal ao fechamento; TAPSE e fração de variação de área permaneceram normais, inclusive após a reperfusão. Mais um motivo para identificar o mecanismo da hipotensão antes de presumir falência de VD.',
 'pamintraop': 'É a mensagem do editorial “The hidden cost of hypotension”, de Lineburger e colaboradores, com Rodrigo Diaz entre os autores: a hipotensão intraoperatória, mesmo por períodos curtos, se associa a lesão renal aguda, lesão miocárdica, delirium e mortalidade; o editorial defende monitorização contínua, manejo proativo e metas individualizadas. O POQI 2024 trata PAM de 60 em pacientes de risco como limite mínimo, não como garantia de perfusão; com pressão venosa ou compartimental alta, o alvo tende a ser maior. Acima do piso, o único ensaio positivo é o HISTAP: 630 pacientes com 60 anos ou mais, hipertensos, em cirurgia abdominal maior, randomizados para PAM de pelo menos 80 ou de pelo menos 65; morte ou disfunção orgânica em 38 contra 49%, sobretudo por menos lesão renal aguda. Os outros ensaios com alvos mais altos foram neutros.',
 "condutavd": "Na falência de VD, quatro frentes andam juntas. Primeiro, a pressão de perfusão: o VD fica isquêmico quando a PAM cai, então noradrenalina para sustentar a PAM e, conforme a vasoplegia associada, vasopressina. Segundo, a resistência pulmonar: corrigir hipóxia, hipercapnia e acidose e, se preciso, vasodilatador pulmonar inalado. Terceiro, a contratilidade: aqui a milrinona faz sentido, porque é inotrópica e reduz a resistência pulmonar; a dobutamina é alternativa. Quarto, volume e ritmo: o VD dilatado tolera mal mais volume. A milrinona pode baixar a PAM e não substitui o diagnóstico: com débito preservado e resistência baixa, considerar vasoplegia, e aí a droga é o vasopressor.",
 "mensagens": "Voltando à pergunta do início: qual componente da PAM está falhando? Vasoplegia pede noradrenalina e, quando a dose sobe, vasopressina; baixo débito com hipoperfusão pede inotrópico, com a milrinona reservada sobretudo para o VD com hipertensão pulmonar; na hipotensão anestésica com bradicardia, efedrina; anafilaxia, adrenalina. A droga certa é a que corrige esse componente, na menor dose eficaz e pelo menor tempo.",
 "obrigado": "Obrigado pela atenção. As referências completas da aula estão no QR code. Fico à disposição para perguntas.",
}
TROCAS = {
 "classificacao": [("As catecolaminas têm meia-vida de minutos e são usadas em infusão; sem o anel catecol, fenilefrina e efedrina duram mais e servem para bolus.", "A curta duração das catecolaminas facilita a titulação por infusão contínua; fenilefrina e efedrina, sem o anel catecol, duram mais e costumam ser usadas em bolus na hipotensão transitória, embora a fenilefrina também possa ser infundida.")],
 "sinalizacao": [("Ela não depende da ativação do receptor β, mas depende de alguma produção de AMPc para ter o que preservar.", "Ela não depende do receptor β, mas precisa de alguma produção de AMPc."), ("A PKA fosforila três alvos: o canal de cálcio tipo L e o RyR2, o que aumenta o cálcio na sístole, ou seja, inotropismo; e o fosfolambam, que deixa de inibir a SERCA2a e acelera a recaptação do cálcio na diástole: lusitropismo.", "A sinalização pela PKA aumenta a disponibilidade de cálcio na sístole, pela fosforilação do canal de cálcio tipo L, favorecendo a contração; na diástole, a fosforilação do fosfolambam reduz a inibição da SERCA2a e acelera a recaptação de cálcio, melhorando o relaxamento.")],
 "milrdobu": [("Entre as duas, nenhuma é superior em desfecho; a escolha é farmacológica, e as diferenças da tabela são perfis esperados, não diferenças demonstradas em ensaio.", "O DOREMI não demonstrou superioridade de uma droga sobre a outra, o que não comprova equivalência; a escolha é farmacológica, e as diferenças da tabela são perfis esperados, não demonstrados em ensaio."), ("o benefício seja teórico e a subanálise negativa do DOREMI não prove equivalência.", "o benefício seja teórico.")],
 "objetivos": [(" e num caso de falência de VD após CEC", ""), ("no choque séptico, no centro cirúrgico", "no choque séptico e no centro cirúrgico")],
 "perfusao": [("Na clínica, enchimento capilar, livedo e temperatura das extremidades; no laboratório, lactato, saturação venosa central e gap de CO₂; e ainda diurese e consciência.", "Na clínica, enchimento capilar e temperatura das extremidades; no laboratório, lactato e saturação venosa central."), ("Antes da droga, vale perguntar se o débito responde a volume, com parâmetros dinâmicos ou com um teste de volume medindo o débito; o eco mostra o VTI e a função dos dois ventrículos.", "Antes da droga, vale perguntar se o débito responde a volume, com parâmetros dinâmicos ou um teste de volume medindo o débito; o eco mostra o VTI e a função dos ventrículos.")],
 "fisiologia": [("Hipovolemia se trata com volume. O α1", "O α1"), (", com temperatura e livedo da pele.", ".")],
 "ssc2026": [("(recomendação forte em relação à dopamina; a preferência em relação à vasopressina e à angiotensina II passou a ser condicional)", "(forte em relação à dopamina)")],
 "intraop": [("Um dado do nosso serviço: Gouvêa, Diaz e colaboradores avaliaram a função do VD por ecocardiografia transesofágica em 19 pacientes selecionados durante o transplante hepático; a função permaneceu preservada nos momentos avaliados, inclusive após a reperfusão (PLoS One 2022). Isso reforça a importância de identificar o mecanismo da hipotensão, sem presumir que exista falência de VD.", "Um dado do nosso serviço: Gouvêa, Diaz e colaboradores, por ETE em 19 pacientes selecionados, encontraram função do VD preservada em todas as fases do transplante hepático, inclusive após a reperfusão: mais um motivo para identificar o mecanismo antes de presumir falência de VD."), ("Um dado do nosso serviço: Gouvêa, Diaz e colaboradores avaliaram o VD por ETE em 19 transplantes hepáticos, e a função foi normal em todas as fases, inclusive após a reperfusão (PLoS One 2022). Na hipotensão da reperfusão, o eco ajuda a separar vasoplegia de disfunção ventricular antes de escolher entre vasopressor e inotrópico.", "Um dado do nosso serviço: Gouvêa, Diaz e colaboradores avaliaram a função do VD por ecocardiografia transesofágica em 19 pacientes selecionados durante o transplante hepático; a função permaneceu preservada nos momentos avaliados, inclusive após a reperfusão (PLoS One 2022). Isso reforça a importância de identificar o mecanismo da hipotensão, sem presumir que exista falência de VD."), ("Se a hipotensão persistir, avaliar a resposta a volume com parâmetros dinâmicos e fazer eco. ", "Se persistir, avaliar a resposta a volume e fazer eco. "), ("Bolus na hipotensão transitória e infusão na persistente. ", "")],
}
MANGA_FIXA = {
 "intraop": "Gouvêa G, Feiner J, Joshi S, Diaz R, et al., PLoS One 2022;17(10):e0275301: estudo observacional, 19 adultos de 18 a 65 anos, TAPSE e variação fracional de área do VD em cinco fases (basal, hepatectomia, anepática, pós-reperfusão e fechamento); função sistólica do VD preservada em todas; excluídos hipertensão portopulmonar, síndrome hepatopulmonar, doença cardiopulmonar e insuficiência hepática fulminante. População selecionada: o estudo não permite concluir que toda hipotensão na reperfusão seja vasoplegia.",
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
        if a in fala: fala = fala.replace(a, b)  # trocas idempotentes: o texto antigo some depois de aplicadas
    if id_ in EXTRA_MANGA and EXTRA_MANGA[id_] not in manga: manga = (manga + " " + EXTRA_MANGA[id_]).strip()
    if id_ in MANGA_FIXA: manga = MANGA_FIXA[id_]
    if id_ == "cover": manga = ""
    ini = relogio; relogio += seg
    dados.append(dict(id=id_, seg=seg, ini=ini, fim=relogio, chave=chave, trans=trans, fala=fala, manga=manga))
TOTAL = relogio

for i, x in enumerate(dados, 1):
    tempo = f"TEMPO: {dur(x['seg'])} ({mmss(x['ini'])} → {mmss(x['fim'])})"
    if x["id"] == "cover":
        tempo += f". Total previsto: {mmss(TOTAL).replace(':', ' min ')} s nos {len(dados)} slides principais; ensaiar em cerca de 17 minutos e meio, sem passar de 18."
    linhas = [f"FALA: {x['fala']}"] + ([f"TRANSIÇÃO: {x['trans']}"] if x["trans"] else []) + [tempo, f"PONTO-CHAVE: {x['chave']}"]
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
    if not os.path.exists(f"{P}/slides/{id_}.html"): continue
    linhas = sorted(linhas, key=lambda l: ORDEM.index(l.split(":")[0]))
    nota = "\n".join(linhas); assert len(nota) <= 4000, (id_, len(nota))
    p = f"{P}/slides/{id_}.html"; t = open(p, encoding="utf-8").read()
    assert t.count("<aside>") == 1, id_
    t = re.sub(r"<aside>.*?</aside>", lambda m: "<aside>" + html.escape(nota, quote=False) + "</aside>", t, flags=re.S)
    open(p, "w", encoding="utf-8").write(t)
json.dump(dict(total=TOTAL, slides=dados), open(S + "/guia/guia.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(TOTAL, mmss(TOTAL), max(len(x["fala"]) for x in dados))
