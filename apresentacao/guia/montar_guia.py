# Monta o guia de fala nas notas dos slides principais (TEMPO, PONTO-CHAVE, FALA, TRANSIÇÃO, SE PERGUNTAREM)
# e gera a mesma informação em guia-de-fala.html. Fonte da fala: as notas da versão anterior (v21/antes).
import json, re, html, os, io, base64
S = "/tmp/claude-0/-home-user-Bruno/82e201e1-5baf-5943-97e1-cc467015b7d6/scratchpad"
P = S + "/artifact-files/351a25a9-1efc-412b-9232-d1cf8f2e53fe/project"
ANTES = S + "/v21/antes"
deck = json.load(open(P + "/deck.json", encoding="utf-8"))
principal = deck["order"]

G = {  # id: (segundos, ponto-chave, transição)
 "cover": (25, "A aula nasceu de uma pergunta prática: quando a milrinona tem indicação?", ""),
 "objetivos": (25, "Qual componente da PAM está falhando?", ""),
 "fisiologia": (60, "PAM ≈ DC × RVS + PVC: vasoplegia pede vasopressor; bomba fraca, inotrópico; pré-carga baixa, volume.", ""),
 "perfusao": (65, "Pressão não é fluxo: combinar eco, débito e marcadores de perfusão antes de decidir por inotrópico.", ""),
 "receptores": (50, "Cada droga tem um perfil de receptores; vasopressina e milrinona usam outras vias.", ""),
 "noradrenalina": (40, "α1 potente com β1 modesto: sobe a PAM com débito em geral mantido.", ""),
 "adrenalina": (35, "Dose baixa, β; dose alta, α. Droga da anafilaxia; terceira droga no choque séptico.", ""),
 "dopadobuta": (35, "Dobutamina para baixo débito com hipoperfusão; dopamina de uso restrito.", ""),
 "milrinona": (55, "Inodilatador que age depois do receptor β; meia-vida longa e eliminação renal; costuma exigir noradrenalina.", ""),
 "milrdobu": (75, "Primeiro a indicação; depois o perfil: milrinona para VD e circulação pulmonar com PAM sustentada; dobutamina com pressão baixa ou para titular rápido. Na sepse, dobutamina é preferência prática, não superioridade demonstrada.", ""),
 "fenilefedrina": (50, "Fenilefrina: hipotensão vasodilatadora com FC normal ou alta. Efedrina: com bradicardia.", ""),
 "vasorefrat": (55, "Fora das aminas: vasopressina (V1), hidrocortisona e azul de metileno, cada uma por um mecanismo diferente.", ""),
 "ssc2026": (30, "Noradrenalina, depois vasopressina, depois adrenalina; inotrópico apenas com disfunção cardíaca e hipoperfusão.", ""),
 "intraop": (75, "Afastar causas, identificar o mecanismo, escolher a droga; o eco separa vasoplegia de falência de VD.", ""),
 "mensagens": (30, "A droga certa corrige o componente que falha, na menor dose e pelo menor tempo.", ""),
 "obrigado": (10, "Referências completas no QR code; abrir para perguntas.", ""),
}
FALA = {  # fala completa de cada slide, sem cliques e sem antecipar o slide seguinte
 "cover": "Bom dia. Sou Bruno Dubois; meus orientadores são Marcelo Bandeira e Glauber Gouvêa. O tema é aminas vasoativas, e a aula nasceu de uma pergunta prática: quando a milrinona tem indicação, e quando a dobutamina ou um vasopressor seriam a escolha.",
 "objetivos": "Quatro objetivos. Distinguir vasoplegia, falência de bomba e pré-carga baixa. Ligar o perfil de receptores de cada droga ao seu efeito hemodinâmico. Conhecer doses, indicações e cuidados de cada droga. Aplicar isso no choque séptico e no centro cirúrgico. A pergunta que organiza a aula: qual componente da pressão arterial média está falhando?",
 "fisiologia": "Começo pela fisiologia. Na prática, a PAM é o débito cardíaco multiplicado pela resistência vascular sistêmica, somado à pressão venosa central. Como a PVC costuma ser baixa, a PAM depende sobretudo do débito e da resistência; quando a PVC sobe, o que cai é a perfusão, porque o órgão recebe a diferença entre a PAM e a PVC. Três situações. Na vasoplegia o problema é o tônus arterial, como na sepse, na anestesia geral e no bloqueio de neuroeixo: o alvo é o vasopressor. Na falência de bomba o débito é baixo e a resistência em geral alta: o alvo é a contratilidade. Na pré-carga baixa, a hipovolemia pede volume; o α1 contrai veias e recruta volume não estressado, mas não substitui a reposição.",
 "perfusao": "Mas pressão não é fluxo: uma resistência alta pode manter a PAM com débito baixo. No intraoperatório a perfusão raramente é medida de forma direta, então o caminho é combinar métodos. O eco, transesofágico ou à beira do leito, é o mais rápido para definir o tipo de choque: função dos ventrículos, volemia, pericárdio e o VTI na via de saída como estimativa do débito. Os monitores de débito, por contorno de pulso, termodiluição ou Doppler esofágico, dão o número e a resposta a volume, junto com VPP e VVS, elevação passiva das pernas ou um minidesafio hídrico. E os marcadores de perfusão tissular dizem se o fluxo está bastando: lactato e sua tendência, saturação venosa central, gap de CO₂, diurese, enchimento capilar e temperatura das extremidades. A decisão de usar inotrópico vem daí, não da pressão.",
 "receptores": "Uma revisão breve dos receptores, apenas o que importa para as drogas de hoje. α1 contrai artérias e veias: sobe a resistência e o retorno venoso. α2, pré-sináptico, reduz a liberação de noradrenalina; é o alvo da dexmedetomidina. β1 aumenta contratilidade e frequência. β2 dilata vasos e brônquios e eleva glicemia e lactato. D1 dilata os leitos renal e mesentérico. V1 e PDE3 estão na tabela porque vasopressina e milrinona não dependem do adrenoceptor. Dois pontos práticos: as catecolaminas têm meia-vida de minutos, por isso vão em geral em infusão; fenilefrina e efedrina duram mais e permitem bolus. E o uso prolongado dessensibiliza os receptores.",
 "noradrenalina": "Começo pela noradrenalina, a droga de primeira linha no choque séptico, com ação α1 potente e β1 modesta: sobe a PAM pela resistência e pela venoconstrição, com débito em geral mantido, podendo cair pela pós-carga, e frequência estável ou menor, por reflexo. Dose de 0,01 a 0,5 microgramas por quilo por minuto, sem teto fixo no choque refratário; no centro cirúrgico, bolus de 5 a 10 microgramas; pode começar em veia periférica calibrosa. Riscos: isquemia digital e esplâncnica, além de extravasamento.",
 "adrenalina": "Adrenalina: potente em α1, β1 e β2. O efeito depende da dose: em dose baixa predominam β1 e β2, com débito alto e resistência que pode cair; em dose alta prevalece o α1. É a droga da anafilaxia e, no choque séptico, a terceira droga. Na anafilaxia, bolus endovenosos pequenos e titulados, com infusão se for preciso repetir. O lactato pode subir por efeito β2, e isso não autoriza ignorar hipoperfusão.",
 "dopadobuta": "Dobutamina: inotrópico β1 com vasodilatação β2; sobe o débito, baixa um pouco a resistência e pode baixar a PAM. Indicada no baixo débito com hipoperfusão, de 2,5 a 20 microgramas por quilo por minuto; se a PAM cair, associar vasopressor; taquicardia e arritmia limitam a dose. A dopamina, em uma frase: efeito pouco previsível, risco de taquicardia e arritmias, e a chamada dose renal não protege o rim; hoje tem uso restrito.",
 "milrinona": "A milrinona chega ao mesmo ponto por outra via: a dobutamina aumenta a produção de AMPc pelo receptor β1; a milrinona inibe a PDE3, a enzima que degrada o AMPc, e por isso age depois do receptor. É um inodilatador: aumenta contratilidade e relaxamento e reduz as resistências sistêmica e pulmonar. A indicação é a disfunção ventricular com baixo débito que exige inotrópico, sobretudo quando há hipertensão pulmonar ou falência de VD. Dose: ataque de 50 microgramas por quilo em 10 minutos, muitas vezes omitido, e manutenção de 0,375 a 0,75 microgramas por quilo por minuto. Costuma exigir noradrenalina; tem eliminação renal e meia-vida bem mais longa que a da dobutamina, acumulando na insuficiência renal.",
 "milrdobu": "Então, quando escolher? Primeiro, a indicação: inotrópico quando há disfunção ventricular com baixo débito e hipoperfusão, depois de otimizar volume e PAM; se a hipotensão é por vasoplegia, a droga é o vasopressor, e um inodilatador baixa ainda mais a pressão. Depois, o perfil farmacológico, que está na tabela. Milrinona quando a circulação pulmonar e o VD são o problema, como na hipertensão pulmonar e na saída de CEC com resistência pulmonar alta, e quando o betabloqueio ou a taquicardia limitam a dobutamina; ela precisa de uma PAM sustentada, em geral com noradrenalina. Dobutamina quando a pressão está baixa ou há vasoplegia, em que a vasodilatação e a meia-vida longa da milrinona pesam contra; na insuficiência renal; e quando se quer titulação rápida, porque a meia-vida é de minutos. No choque séptico com disfunção miocárdica, a SSC 2026 sugere dobutamina associada à noradrenalina, ou adrenalina isolada, e reconhece que faltam dados para preferir a dobutamina à milrinona: é preferência prática, não superioridade demonstrada.",
 "fenilefedrina": "Agora duas aminas simpaticomiméticas que não são catecolaminas, as drogas de bolus do centro cirúrgico. Fenilefrina: agonista α1 direto, praticamente sem ação β; a PAM sobe pela resistência e a frequência cai por reflexo, o que pode reduzir o débito quando ele depende da frequência; é a escolha na hipotensão vasodilatadora com frequência normal ou alta. Efedrina: age diretamente em α e β e, sobretudo, libera noradrenalina das terminações; sobe pressão, frequência e débito, por isso é a escolha quando há bradicardia; perde efeito com doses repetidas, porque depleta a noradrenalina, e na cesárea atravessa a placenta e associa-se a mais acidose fetal que a fenilefrina.",
 "vasorefrat": "Quando a via adrenérgica não basta, três recursos além das aminas. A vasopressina age no receptor V1, fora da via adrenérgica: poupa catecolamina e costuma manter efeito em acidose; no choque séptico há deficiência relativa do hormônio endógeno. Dose fixa, em geral 0,03 unidades por minuto, no choque séptico com noradrenalina em escalada, na vasoplegia após CEC e na hipotensão refratária com IECA ou BRA; o risco é isquemia digital e mesentérica. A hidrocortisona restaura a resposta vascular às catecolaminas, 200 mg por dia no choque séptico. O azul de metileno inibe a via do óxido nítrico e fica como resgate na vasoplegia refratária, como após CEC ou na reperfusão do enxerto hepático.",
 "ssc2026": "No choque séptico, a Surviving Sepsis Campaign, a diretriz internacional de sepse, atualizada em 2026, organiza os vasopressores em sequência: noradrenalina primeiro, cedo, mesmo por veia periférica; vasopressina quando a dose de noradrenalina sobe, sem limiar definido; adrenalina se a PAM continuar inadequada. É o mesmo raciocínio da aula: tônus com noradrenalina, outra via com vasopressina, e inotrópico apenas se houver disfunção cardíaca com hipoperfusão.",
 "intraop": "No centro cirúrgico, antes da droga, afastar causas tratáveis: plano profundo, hipovolemia, compressão aortocava, pneumotórax e anafilaxia. Depois, o mecanismo: tônus baixo com frequência normal ou alta, agonista α1; bradicardia, efedrina ou, se grave, adrenalina; baixo débito, inotrópico; vasoplegia refratária às catecolaminas, como após CEC, com IECA ou BRA ou na reperfusão do enxerto hepático, vasopressina, com azul de metileno como resgate; pré-carga baixa, volume. Um dado do nosso serviço ajuda nessa decisão: Gouvêa, Diaz e colaboradores acompanharam por ecocardiografia transesofágica o ventrículo direito de 19 pacientes selecionados em cinco fases do transplante hepático, e a função sistólica do VD se manteve preservada nos momentos avaliados, inclusive trinta minutos após a reperfusão. O estudo não mediu os primeiros minutos da reperfusão, então não diz se a instabilidade aguda é vasoplegia ou disfunção transitória do VD. O que ele sustenta é o método: usar o eco para separar disfunção de VD de vasoplegia antes de escolher entre inotrópico e vasopressor.",
 "mensagens": "Voltando à pergunta do início: qual componente da PAM está falhando? Vasoplegia: noradrenalina e, quando a dose sobe, vasopressina. Baixo débito com hipoperfusão: inotrópico, com a milrinona sobretudo no VD com hipertensão pulmonar. Hipotensão vasodilatadora da anestesia com bradicardia: efedrina; com taquicardia: fenilefrina. Anafilaxia: adrenalina. A droga certa corrige o componente que falha, na menor dose eficaz e pelo menor tempo.",
 "obrigado": "Obrigado pela atenção. As referências completas da aula estão no QR code. Fico à disposição para perguntas.",
}
TROCAS = {}
MANGA_FIXA = {
 "intraop": "Gouvêa G, Feiner J, Joshi S, Diaz R, et al., PLoS One 2022;17(10):e0275301: estudo observacional, 19 adultos de 18 a 65 anos, TAPSE e variação fracional de área do VD em cinco fases (basal, fase de hepatectomia, fase anepática, 30 min após a reperfusão e fechamento); função sistólica do VD preservada nos cinco momentos; excluídos hipertensão portopulmonar, síndrome hepatopulmonar, doença cardiopulmonar e insuficiência hepática fulminante. População selecionada e medida feita 30 min depois da reperfusão: o estudo não mediu os primeiros minutos, quando ocorre a síndrome pós-reperfusão, não exclui disfunção transitória do VD nesse período e não permite atribuir a instabilidade aguda a vasoplegia. TAPSE e variação fracional de área dependem da carga, e o TAPSE mede apenas a excursão longitudinal do anel lateral; normais sob anestesia, com pós-carga baixa, afastam disfunção sistólica evidente nos momentos avaliados, não medem reserva contrátil.",
 "fisiologia": "A relação PAM = DC × RVS + PVC é a definição da RVS, não uma causa (Magder, Crit Care 2018): a RVS é calculada como (PAM − PVC)/DC. A pressão a jusante efetiva do leito arterial é uma pressão crítica de fechamento, acima da PVC; a PVC importa para a pressão de perfusão dos órgãos (PAM − PVC) e para o gradiente do retorno venoso (pressão sistêmica média − pressão de átrio direito). Persichini (Crit Care Med 2012; 16 pacientes com choque séptico): reduzir a dose de noradrenalina baixou a pressão sistêmica média e o retorno venoso, mais do que a resistência ao retorno venoso, com queda do débito; é a prova de que a venoconstrição α recruta volume não estressado. o esquema cobre os determinantes da PAM; a obstrução (tamponamento, embolia pulmonar, pneumotórax hipertensivo, auto-PEEP) é o quarto tipo de choque da classificação da ESICM 2014: o eco precoce a identifica, e o tratamento é da causa, não com amina. No intraoperatório, pneumotórax e compressão aortocava estão entre as causas a afastar (slide 16).",
 "perfusao": "no OPTIME-CHF (Cuffe, JAMA 2002; 951 pacientes com IC descompensada sem indicação clara de inotrópico), milrinona vs. placebo por 48 h: sem benefício, com mais hipotensão sustentada e arritmia atrial. Em um ECR de 2025 (Tongyoo, Ann Med; 64 pacientes em choque séptico), a milrinona aumentou o débito em 6 horas em relação ao placebo, mas a mortalidade em 28 dias foi de 50% nos dois grupos. Na sepse a SvcO₂ pode estar normal ou alta apesar da hipoperfusão (defeito de extração e shunt microcirculatório); nesse caso, a diferença venoarterial de CO₂ acima de 6 mmHg indica fluxo insuficiente para remover o CO₂ produzido (Vallée, Intensive Care Med 2008). Limites de VPP e VVS: ventilação controlada sem esforço espontâneo, volume corrente de pelo menos 8 mL/kg, ritmo regular, tórax fechado, sem disfunção de VD nem hipertensão intra-abdominal; com volume corrente baixo a sensibilidade cai. Fora dessas condições: elevação passiva das pernas ou minidesafio hídrico com medida direta do débito (ESICM 2025).",
 "vasorefrat": "no VANCS (Hajjar, Anesthesiology 2017, InCor), na vasoplegia pós-CEC, a vasopressina teve menos morte ou complicação grave que a noradrenalina (32% vs. 49%); é uma população de cirurgia cardíaca, e o resultado não deve ser extrapolado para o choque séptico. Hidrocortisona: 200 mg/dia (50 mg de 6/6 h ou em infusão). Angiotensina II: no ATHOS-3, a resposta da PAM em 3 h ocorreu em 69,9% vs. 23,4% dos pacientes, sem diferença de mortalidade; é pouco disponível. Azul de metileno: inibe a óxido nítrico sintase e a guanilato ciclase solúvel; resgate na vasoplegia pós-CEC e na reperfusão do enxerto hepático, com evidência limitada. Contraindicado na deficiência de G6PD (hemólise); subestima a SpO₂ na oximetria de pulso e reduz o BIS; síndrome serotoninérgica com ISRS e outros serotoninérgicos, por inibir a MAO-A.",
 "ssc2026": "o VASSPR (JAMA 2026, n = 3.959; 13 hospitais, desenho cluster-crossover com ordem sorteada) comparou políticas hospitalares de iniciar a vasopressina com 0,1 vs. 0,4 mcg/kg/min de noradrenalina-equivalente; a vasopressina foi usada em 52,4% vs. 32,9%, e a mortalidade foi 31,8% vs. 33,0%. A antecipação sistemática não trouxe benefício, o que não exclui ganho em pacientes selecionados. No OPTPRESS, alvo de 80–85 mmHg em idosos aumentou a mortalidade.",
 "noradrenalina": "no SOAP II (n = 1.679), a mortalidade em 28 dias foi semelhante à da dopamina (48,5% vs. 52,5%), com metade das arritmias (12,4% vs. 24,1%); a SSC 2026 recomenda a noradrenalina em vez da dopamina (forte, certeza alta). No Brasil, a ampola de hemitartarato de 2 mg/mL equivale a 1 mg/mL de base: registrar na prescrição se a dose está em base ou em sal. Início precoce (CENSER, Permpikul 2019: controle do choque em 6 h em 76% vs. 48%) e via periférica com protocolo (Tran 2020) estão nas referências. No extravasamento, fentolamina infiltrada no local. Afinidade por β1: a da noradrenalina é da mesma ordem da adrenalina; o que é modesto é o efeito cardíaco líquido, porque o barorreflexo e a pós-carga contêm a taquicardia e o aumento do débito; a ação β2 é pequena, por isso não há vasodilatação e o lactato sobe pouco."
}
EXTRA_MANGA = {
 "receptores": "O α2 pós-sináptico vascular explica a hipertensão transitória do bolus de dexmedetomidina ou clonidina.",
 "noradrenalina": "Afinidade por β1: a da noradrenalina é da mesma ordem da adrenalina; o que é modesto é o efeito cardíaco líquido, porque o barorreflexo e a pós-carga contêm a taquicardia e o aumento do débito; a ação β2 é pequena, por isso não há vasodilatação e o lactato sobe pouco.",
 "adrenalina": "Dose no choque séptico: a bula americana de epinefrina prevê infusão de 0,05–2 mcg/kg/min, titulada pela PAM. Cartão ANZAAG/ANZCA 2022 (adulto; 1 mg em 10 mL = 100 mcg/mL): grau 2, 10–20 mcg, e 50 mcg se não houver resposta; grau 3, 50–100 mcg, e 200 mcg se não houver resposta; repetir a cada 1–2 min; após mais de três bolus, infusão de 3 mg em 50 mL, de 3 a 40 mL/h; sem acesso venoso ou sem monitorização, 500 mcg IM na face lateral da coxa, repetível a cada 5 min."
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
    passos = {int(n) for n in re.findall(r'data-passo="(\d+)"', open(f"{P}/slides/{id_}.html", encoding="utf-8").read())}
    assert fala.count("▸") == len(passos) and passos == set(range(1, len(passos) + 1)), (id_, fala.count("▸"), sorted(passos))
    ini = relogio; relogio += seg
    dados.append(dict(id=id_, seg=seg, ini=ini, fim=relogio, chave=chave, trans=trans, fala=fala, manga=manga))
TOTAL = relogio

for i, x in enumerate(dados, 1):
    tempo = f"TEMPO: {dur(x['seg'])} ({mmss(x['ini'])} → {mmss(x['fim'])})"
    if x["id"] == "cover":
        tempo += f". Total previsto: {mmss(TOTAL).replace(':', ' min ')} s nos {len(dados)} slides; ensaiar mirando 12 minutos."
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
