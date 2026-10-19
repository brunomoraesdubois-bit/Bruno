# Monta o guia de fala nas notas dos slides principais (TEMPO, PONTO-CHAVE, FALA, TRANSIÇÃO, SE PERGUNTAREM)
# e gera a mesma informação em guia-de-fala.html. Fonte da fala: as notas da versão anterior (v21/antes).
import json, re, html, os, io, base64
S = "/tmp/claude-0/-home-user-Bruno/82e201e1-5baf-5943-97e1-cc467015b7d6/scratchpad"
P = S + "/artifact-files/351a25a9-1efc-412b-9232-d1cf8f2e53fe/project"
ANTES = S + "/v21/antes"
deck = json.load(open(P + "/deck.json", encoding="utf-8"))
principal = deck["order"]

G = {  # id: (segundos, ponto-chave, transição)
 "cover": (25, "A aula nasceu de uma pergunta prática: quando a milrinona tem indicação?", "Começo pelos objetivos."),
 "objetivos": (30, "Qual componente da PAM está falhando?", "Para responder, precisamos entender de que depende a pressão arterial média."),
 "fisiologia": (60, "Vasoplegia pede vasopressor; bomba fraca, inotrópico; pré-carga baixa, volume.", "Mas uma PAM normal não basta."),
 "perfusao": (45, "Inotrópico se decide por hipoperfusão e débito, não apenas pela pressão.", "Definido o problema, as ferramentas: os receptores."),
 "receptores": (50, "Cada droga tem um perfil de receptores; vasopressina e milrinona usam outras vias.", "Começo pela noradrenalina."),
 "noradrenalina": (40, "α1 potente com β1 modesto: sobe a PAM com débito em geral mantido.", "A adrenalina é parecida na estrutura, mas tem outro perfil."),
 "adrenalina": (45, "Dose baixa, β; dose alta, α. Droga da anafilaxia; terceira droga no choque séptico.", "Passando à dobutamina e, em uma frase, à dopamina."),
 "dopadobuta": (45, "Dobutamina para baixo débito com hipoperfusão; dopamina fora da primeira linha.", "Para entender a diferença entre dobutamina e milrinona, um esquema."),
 "sinalizacao": (65, "Dobutamina aumenta a produção de AMPc; milrinona impede a degradação.", "Com esse mecanismo, a milrinona fica fácil de entender."),
 "milrinona": (45, "Inodilatador pós-receptor β para a disfunção ventricular com baixo débito; meia-vida longa e eliminação renal.", "E a pergunta prática que motivou a aula: quando escolher cada uma?"),
 "milrdobu": (80, "Primeiro a indicação; depois a escolha é farmacológica, sem superioridade demonstrada em desfecho.", "Um cenário em que essa diferença farmacológica realmente importa é a falência de ventrículo direito. Como abordá-la?"),
 "condutavd": (50, "Na falência de VD, a milrinona entra na contratilidade, com noradrenalina; com débito preservado e RVS baixa, considerar vasoplegia.", "Saindo dos inotrópicos, as drogas de bolus do centro cirúrgico."),
 "fenilefedrina": (50, "Fenilefrina: tônus baixo com FC alta. Efedrina: tônus baixo com bradicardia.", "E quando a via adrenérgica não basta?"),
 "vasorefrat": (45, "Vasopressina age por outra via (V1) e poupa catecolamina; no refratário, somar mecanismos: hidrocortisona, angiotensina II e azul de metileno.", "Juntando tudo no choque séptico."),
 "ssc2026": (50, "Noradrenalina, depois vasopressina, depois adrenalina; PAM inicial de 65 mmHg.", "No centro cirúrgico, o raciocínio é o mesmo, com outras causas."),
 "intraop": (70, "Afastar causas, identificar o mecanismo, escolher a droga.", "E quanto de PAM é suficiente no intraoperatório?"),
 "pamintraop": (60, "PAM de 60–65 mmHg como piso; alvo maior apenas em selecionados.", "Para terminar, as mensagens da aula."),
 "mensagens": (35, "A droga certa corrige o componente que falha, na menor dose e pelo menor tempo.", "Com isso, chego ao fim."),
 "obrigado": (10, "Referências completas no QR code; abrir para perguntas.", ""),
}
FALA = {  # fala completa de cada slide; cada ▸ é um clique: o elemento correspondente aparece
 "cover": "Bom dia. Sou Bruno Dubois; meus orientadores são Marcelo Bandeira e Glauber Gouvêa. O tema é aminas vasoativas, e a aula nasceu de uma pergunta prática: quando a milrinona tem indicação, e quando a dobutamina ou um vasopressor seriam a escolha.",
 "objetivos": "Quatro objetivos. ▸ Distinguir vasoplegia, falência de bomba e pré-carga baixa. ▸ Ligar o perfil de receptores de cada droga ao seu efeito hemodinâmico. ▸ Conhecer doses e cuidados, e quando preferir milrinona ou dobutamina. ▸ Aplicar isso no choque séptico e no centro cirúrgico. ▸ A pergunta que organiza a aula: qual componente da pressão arterial média está falhando?",
 "fisiologia": "A PAM é o produto do débito cardíaco pela resistência vascular sistêmica, somado à pressão venosa central, que pesa quando está alta, porque reduz a pressão de perfusão. ▸ Na vasoplegia o problema é o tônus arterial: sepse, anestesia geral, bloqueio de neuroeixo, anafilaxia, saída de CEC; as causas anestésicas e a anafilaxia somam venodilatação. ▸ Na falência de bomba o débito é baixo, em geral com resistência alta; na sepse, a disfunção miocárdica pode coexistir com vasoplegia. ▸ Na pré-carga baixa, a hipovolemia pede volume; e o α1 também contrai veias, recruta volume não estressado e aumenta o retorno venoso: Persichini, em 16 pacientes com choque séptico, reduziu a noradrenalina e viu caírem a pressão sistêmica média e o retorno venoso. ▸ Para diferenciar: eco precoce, parâmetros dinâmicos e perfusão seriada.",
 "perfusao": "Pressão não é fluxo: uma resistência alta pode manter a PAM com débito baixo. Por isso a decisão de usar inotrópico depende de sinais de hipoperfusão e de uma estimativa do débito. ▸ Os sinais estão no slide. ▸ Antes da droga, perguntar se o débito responde a volume; o eco mostra o VTI e a função dos ventrículos. ▸ E a ressalva oposta: aumentar o débito com a droga não é melhorar o desfecho; é a lição dos ensaios com inotrópico em quem não tinha indicação.",
 "receptores": "α1 contrai artérias e veias; α2, pré-sináptico, reduz a liberação de noradrenalina e, pós-sináptico no vaso, também contrai. ▸ β1 aumenta contratilidade e frequência; β2 dilata vasos e brônquios e eleva glicemia e lactato. ▸ D1 dilata os leitos renal e mesentérico. ▸ V1 e PDE3 entram na tabela porque vasopressina e milrinona não dependem do adrenoceptor. ▸ Dois pontos práticos: as catecolaminas têm meia-vida de minutos, o que favorece a infusão contínua; fenilefrina e efedrina, sem o anel catecol, duram mais e costumam ir em bolus. E, com uso prolongado, os adrenoceptores se dessensibilizam, um dos fundamentos para associar uma droga de outra via.",
 "noradrenalina": "É a droga de primeira linha no choque séptico, com ação α1 potente e β1 modesta: ▸ sobe a PAM pela resistência e pela venoconstrição, com débito em geral mantido, podendo cair pela pós-carga, e frequência estável ou menor, por reflexo. ▸ Dose de 0,01 a 0,5 microgramas por quilo por minuto, sem teto fixo no choque refratário; no centro cirúrgico, bolus de 5 a 10 microgramas; pode começar em veia periférica calibrosa. Riscos: isquemia digital e esplâncnica, além de extravasamento.",
 "adrenalina": "Adrenalina: potente em α1, β1 e β2. ▸ O efeito depende da dose: em dose baixa predominam β1 e β2, com débito alto e resistência que pode cair; em dose alta prevalece o α1. É a droga da anafilaxia e, no choque séptico, a terceira droga. ▸ Na anafilaxia em ambiente monitorizado, bolus endovenosos titulados, conforme a diretriz australiana e neozelandesa (ANZCA/ANZAAG 2022); se forem necessários mais de três bolus, infusão; sem acesso venoso, 0,5 mg intramuscular. O lactato pode subir por efeito β2, e isso não autoriza ignorar hipoperfusão.",
 "dopadobuta": "Dobutamina: inotrópico β1 com vasodilatação β2; sobe o débito, baixa um pouco a resistência e pode baixar a PAM. ▸ Indicada no baixo débito com hipoperfusão, de 2,5 a 20 microgramas por quilo por minuto; se a PAM cair, associar vasopressor; taquicardia e arritmia limitam a dose. ▸ Sobre a dopamina, uma frase apenas: efeito dose-dependente e pouco previsível, de D1 a α1, com mais arritmia que a noradrenalina; a SSC 2026 recomenda contra o uso como primeira linha, e hoje o uso é residual.",
 "sinalizacao": "A dobutamina estimula o receptor β1; pela proteína Gs, a adenilato ciclase produz AMPc, que ativa a PKA. A PKA aumenta a entrada de cálcio pelo canal tipo L, que dispara a liberação pelo RyR2 do retículo, com mais cálcio na sístole; e fosforila o fosfolambam, que deixa de inibir a SERCA2a: a recaptação acelera, o que relaxa mais rápido e carrega mais o retículo para a sístole seguinte. ▸ A milrinona inibe a PDE3, a enzima que degrada o AMPc: não depende do receptor β, mas precisa de alguma produção de AMPc; por isso mantém efeito com betabloqueio, embora isso seja fundamento farmacológico, não benefício demonstrado. No músculo liso vascular, a mesma via inibe a quinase da cadeia leve da miosina e o vaso relaxa: a milrinona é inodilatadora e pode baixar a PAM.",
 "milrinona": "A milrinona é um inodilatador: aumenta contratilidade e relaxamento e reduz as resistências sistêmica e pulmonar. ▸ A indicação é a disfunção ventricular com baixo débito que exige inotrópico, incluindo a saída difícil de CEC. ▸ Dose: ataque de 50 microgramas por quilo em 10 minutos, muitas vezes omitido, e manutenção de 0,375 a 0,75 microgramas por quilo por minuto. Por ser vasodilatadora, costuma exigir noradrenalina; tem eliminação renal e meia-vida bem mais longa que a da dobutamina, e acumula na insuficiência renal.",
 "milrdobu": "▸ Primeiro, a indicação: inotrópico quando há disfunção ventricular com baixo débito e hipoperfusão, depois de otimizar volume e PAM. Se a hipotensão é por vasoplegia, a droga é o vasopressor; um inodilatador baixa ainda mais a pressão. ▸ A tabela resume os perfis esperados: meia-vida, circulação pulmonar, frequência e pressão, e resposta com betabloqueador. O ensaio de referência é o DOREMI: 192 pacientes com choque cardiogênico, randomizados, em duplo-cego, para milrinona ou dobutamina. O desfecho composto de morte, parada cardíaca revertida, transplante ou suporte circulatório mecânico, infarto, AVC ou diálise ocorreu em 49% com milrinona e 54% com dobutamina, sem diferença estatisticamente significativa; arritmia, hipotensão e necessidade de vasopressor também não diferiram; nos 93 pacientes betabloqueados, a milrinona não teve vantagem. Isso não comprova equivalência, mas a escolha fica farmacológica. ▸ Milrinona no VD com hipertensão pulmonar, como na saída de CEC, e quando taquicardia ou betabloqueio limitam a dobutamina. ▸ Dobutamina se houver hipotensão associada, insuficiência renal ou necessidade de titulação rápida.",
 "condutavd": "Na falência de VD, quatro frentes. ▸ Pressão de perfusão: o VD pode ficar isquêmico quando a PAM cai; noradrenalina e, se houver vasoplegia, vasopressina. ▸ Resistência pulmonar: corrigir hipóxia, hipercapnia e acidose; se preciso, vasodilatador inalado. ▸ Contratilidade: a milrinona faz sentido porque é inotrópica e reduz a resistência pulmonar; a dobutamina é alternativa; adrenalina no choque grave. ▸ Volume e ritmo: o VD dilatado tolera mal a sobrecarga de volume. ▸ A milrinona não substitui o diagnóstico: com débito preservado e resistência baixa, pensar em vasoplegia, e nesse caso a droga é o vasopressor.",
 "fenilefedrina": "Fenilefrina: agonista α1 direto, praticamente sem ação β; a PAM sobe pela resistência e a frequência cai por reflexo. ▸ Em bolus de 50 a 100 microgramas, é útil quando a taquicardia é indesejável, mas pode reduzir o débito quando ele depende da frequência; na cesárea, o consenso de 2018 recomenda vasopressor α-agonista em infusão profilática. ▸ Efedrina: α1 e β1 moderados; sobe pressão, frequência e débito. ▸ Ação mista, direta e indireta, liberando noradrenalina: bolus de 5 a 10 mg na hipotensão com bradicardia; perde efeito com doses repetidas e, na cesárea, associa-se a mais acidose fetal.",
 "vasorefrat": "A vasopressina age no receptor V1, fora da via adrenérgica: poupa catecolamina e costuma manter efeito em acidose; no choque séptico há deficiência relativa do hormônio endógeno. Dose fixa, em geral 0,03 unidades por minuto. Indicações: choque séptico com noradrenalina em escalada, vasoplegia após CEC e hipotensão refratária com IECA ou BRA. Riscos: isquemia digital e mesentérica. Antes de somar drogas, corrigir causas tratáveis. ▸ Adjuvantes: a hidrocortisona restaura a resposta às catecolaminas, 200 mg por dia; ▸ a angiotensina II poupa catecolamina, mas é pouco disponível; ▸ o azul de metileno fica como resgate na vasoplegia refratária.",
 "ssc2026": "A SSC 2026 organiza os vasopressores em sequência. ▸ Noradrenalina primeiro, cedo, mesmo por veia periférica. ▸ Vasopressina quando a dose de noradrenalina sobe, sem limiar definido. ▸ Adrenalina se a PAM continuar inadequada. ▸ Alvo inicial de 65 mmHg, ou 60 a 65 a partir dos 65 anos. Sobre o momento da vasopressina, o VASSPR, de outubro de 2026: 3.959 pacientes com choque séptico, em 13 hospitais que alternaram, por sorteio, iniciá-la com 0,1 ou com 0,4 microgramas por quilo por minuto de noradrenalina ou equivalente; mortalidade semelhante, 31,8 contra 33,0%. ▸ Na disfunção cardíaca com hipoperfusão, dobutamina com noradrenalina, ou adrenalina; hidrocortisona sugerida.",
 "intraop": "Antes da droga, afastar causas tratáveis: plano profundo, hipovolemia, compressão aortocava, pneumotórax e anafilaxia, que pede adrenalina. Se persistir, avaliar a resposta a volume e fazer eco. A escolha segue o mecanismo: ▸ tônus baixo com frequência normal ou alta pede agonista α1; ▸ bradicardia associada pede ação β1, efedrina ou, se grave, adrenalina; ▸ baixo débito pede inotrópico, e a milrinona ajuda no VD com hipertensão pulmonar; ▸ vasoplegia refratária às catecolaminas, como após CEC, com IECA ou BRA ou na reperfusão do enxerto hepático, pode responder à vasopressina, com azul de metileno como resgate; ▸ e pré-carga baixa pede volume, não amina. ▸ Um dado do nosso serviço: Gouvêa, Diaz e colaboradores avaliaram por ETE o VD de 19 pacientes selecionados em cinco momentos do transplante hepático; TAPSE e variação fracional de área permaneceram normais, inclusive após a reperfusão. Mais um motivo para identificar o mecanismo antes de presumir falência de VD.",
 "pamintraop": "A hipotensão intraoperatória, mesmo breve, associa-se a lesão renal aguda, lesão miocárdica, delirium e mortalidade: é a mensagem do editorial de Lineburger e colaboradores, com Rodrigo Diaz entre os autores. ▸ O POQI 2024 trata PAM de 60 em pacientes de risco como limite mínimo; com pressão venosa ou compartimental alta, o alvo sobe. ▸ Acima do piso, o ensaio positivo mais recente é o HISTAP: 630 hipertensos com 60 anos ou mais, em cirurgia abdominal maior, randomizados para PAM de pelo menos 80 ou de pelo menos 65; morte ou disfunção orgânica em 38 contra 49%, sobretudo por menos lesão renal aguda. Outros ensaios, como o POISE-3 e o IMPROVE-multi, foram neutros. ▸ Daí a proposta: monitorização contínua, manejo proativo e metas individualizadas.",
 "mensagens": "Voltando à pergunta do início: qual componente da PAM está falhando? ▸ Vasoplegia: noradrenalina e, quando a dose sobe, vasopressina. ▸ Baixo débito com hipoperfusão: inotrópico, com a milrinona sobretudo no VD com hipertensão pulmonar. ▸ Hipotensão anestésica com bradicardia: efedrina. ▸ Com taquicardia: fenilefrina. ▸ Anafilaxia: adrenalina. ▸ No intraoperatório, tratar cedo, com PAM mínima de 60 a 65. A droga certa corrige o componente que falha, na menor dose eficaz e pelo menor tempo.",
 "obrigado": "Obrigado pela atenção. As referências completas da aula estão no QR code. Fico à disposição para perguntas.",
}
TROCAS = {
 "classificacao": [
  [
   "As catecolaminas têm meia-vida de minutos e são usadas em infusão; sem o anel catecol, fenilefrina e efedrina duram mais e servem para bolus.",
   "A curta duração das catecolaminas facilita a titulação por infusão contínua; fenilefrina e efedrina, sem o anel catecol, duram mais e costumam ser usadas em bolus na hipotensão transitória, embora a fenilefrina também possa ser infundida."
  ]
 ],
 "sinalizacao": [
  [
   "Ela não depende da ativação do receptor β, mas depende de alguma produção de AMPc para ter o que preservar.",
   "Ela não depende do receptor β, mas precisa de alguma produção de AMPc."
  ],
  [
   "A PKA fosforila três alvos: o canal de cálcio tipo L e o RyR2, o que aumenta o cálcio na sístole, ou seja, inotropismo; e o fosfolambam, que deixa de inibir a SERCA2a e acelera a recaptação do cálcio na diástole: lusitropismo.",
   "A sinalização pela PKA aumenta a disponibilidade de cálcio na sístole, pela fosforilação do canal de cálcio tipo L, favorecendo a contração; na diástole, a fosforilação do fosfolambam reduz a inibição da SERCA2a e acelera a recaptação de cálcio, melhorando o relaxamento."
  ]
 ],
 "milrdobu": [
  [
   "Entre as duas, nenhuma é superior em desfecho; a escolha é farmacológica, e as diferenças da tabela são perfis esperados, não diferenças demonstradas em ensaio.",
   "O DOREMI não demonstrou superioridade de uma droga sobre a outra, o que não comprova equivalência; a escolha é farmacológica, e as diferenças da tabela são perfis esperados, não demonstrados em ensaio."
  ],
  [
   "o benefício seja teórico e a subanálise negativa do DOREMI não prove equivalência.",
   "o benefício seja teórico."
  ]
 ],
 "objetivos": [
  [
   " e num caso de falência de VD após CEC",
   ""
  ],
  [
   "no choque séptico, no centro cirúrgico",
   "no choque séptico e no centro cirúrgico"
  ]
 ],
 "perfusao": [
  [
   "Na clínica, enchimento capilar, livedo e temperatura das extremidades; no laboratório, lactato, saturação venosa central e gap de CO₂; e ainda diurese e consciência.",
   "Na clínica, enchimento capilar e temperatura das extremidades; no laboratório, lactato e saturação venosa central."
  ],
  [
   "Antes da droga, vale perguntar se o débito responde a volume, com parâmetros dinâmicos ou com um teste de volume medindo o débito; o eco mostra o VTI e a função dos dois ventrículos.",
   "Antes da droga, vale perguntar se o débito responde a volume, com parâmetros dinâmicos ou um teste de volume medindo o débito; o eco mostra o VTI e a função dos ventrículos."
  ]
 ],
 "fisiologia": [
  [
   "Hipovolemia se trata com volume. O α1",
   "O α1"
  ],
  [
   ", com temperatura e livedo da pele.",
   "."
  ]
 ],
 "ssc2026": [
  [
   "(recomendação forte em relação à dopamina; a preferência em relação à vasopressina e à angiotensina II passou a ser condicional)",
   "(forte em relação à dopamina)"
  ]
 ],
 "intraop": [
  [
   "Um dado do nosso serviço: Gouvêa, Diaz e colaboradores avaliaram a função do VD por ecocardiografia transesofágica em 19 pacientes selecionados durante o transplante hepático; a função permaneceu preservada nos momentos avaliados, inclusive após a reperfusão (PLoS One 2022). Isso reforça a importância de identificar o mecanismo da hipotensão, sem presumir que exista falência de VD.",
   "Um dado do nosso serviço: Gouvêa, Diaz e colaboradores, por ETE em 19 pacientes selecionados, encontraram função do VD preservada em todas as fases do transplante hepático, inclusive após a reperfusão: mais um motivo para identificar o mecanismo antes de presumir falência de VD."
  ],
  [
   "Um dado do nosso serviço: Gouvêa, Diaz e colaboradores avaliaram o VD por ETE em 19 transplantes hepáticos, e a função foi normal em todas as fases, inclusive após a reperfusão (PLoS One 2022). Na hipotensão da reperfusão, o eco ajuda a separar vasoplegia de disfunção ventricular antes de escolher entre vasopressor e inotrópico.",
   "Um dado do nosso serviço: Gouvêa, Diaz e colaboradores avaliaram a função do VD por ecocardiografia transesofágica em 19 pacientes selecionados durante o transplante hepático; a função permaneceu preservada nos momentos avaliados, inclusive após a reperfusão (PLoS One 2022). Isso reforça a importância de identificar o mecanismo da hipotensão, sem presumir que exista falência de VD."
  ],
  [
   "Se a hipotensão persistir, avaliar a resposta a volume com parâmetros dinâmicos e fazer eco. ",
   "Se persistir, avaliar a resposta a volume e fazer eco. "
  ],
  [
   "Bolus na hipotensão transitória e infusão na persistente. ",
   ""
  ]
 ]
}
MANGA_FIXA = {
 "intraop": "Gouvêa G, Feiner J, Joshi S, Diaz R, et al., PLoS One 2022;17(10):e0275301: estudo observacional, 19 adultos de 18 a 65 anos, TAPSE e variação fracional de área do VD em cinco fases (basal, fase de hepatectomia, fase anepática, pós-reperfusão e fechamento); função sistólica do VD preservada nas cinco fases; excluídos hipertensão portopulmonar, síndrome hepatopulmonar, doença cardiopulmonar e insuficiência hepática fulminante. População selecionada: o estudo não permite concluir que toda hipotensão na reperfusão seja vasoplegia. TAPSE e variação fracional de área dependem da carga, e o TAPSE mede apenas a excursão longitudinal do anel lateral; normais sob anestesia, com pós-carga baixa, afastam disfunção sistólica evidente nos momentos avaliados, não medem reserva contrátil.",
 "fisiologia": "o esquema cobre os determinantes da PAM; a obstrução (tamponamento, embolia pulmonar, pneumotórax hipertensivo, auto-PEEP) é o quarto tipo de choque da classificação da ESICM 2014: o eco precoce a identifica, e o tratamento é da causa, não com amina. No intraoperatório, pneumotórax e compressão aortocava estão entre as causas a afastar (slide 16).",
 "perfusao": "no OPTIME-CHF (Cuffe, JAMA 2002; 951 pacientes com IC descompensada sem indicação clara de inotrópico), milrinona vs. placebo por 48 h: sem benefício, com mais hipotensão sustentada e arritmia atrial. Em um ECR de 2025 (Tongyoo, Ann Med; 64 pacientes em choque séptico), a milrinona aumentou o débito em 6 horas em relação ao placebo, mas a mortalidade em 28 dias foi de 50% nos dois grupos. Na sepse a SvcO₂ pode estar normal ou alta apesar da hipoperfusão (defeito de extração e shunt microcirculatório); nesse caso, a diferença venoarterial de CO₂ acima de 6 mmHg indica fluxo insuficiente para remover o CO₂ produzido (Vallée, Intensive Care Med 2008). Limites de VPP e VVS: ventilação controlada sem esforço espontâneo, volume corrente de pelo menos 8 mL/kg, ritmo regular, tórax fechado, sem disfunção de VD nem hipertensão intra-abdominal; com volume corrente baixo a sensibilidade cai. Fora dessas condições: elevação passiva das pernas ou minidesafio hídrico com medida direta do débito (ESICM 2025).",
 "sinalizacao": "a sinalização do AMPc é compartimentalizada, com PKA e fosfodiesterases ancoradas por AKAPs em nanodomínios (Zaccolo e Kovanich, Physiol Rev 2025); e parte do efeito da PKA sobre o canal tipo L passa pela fosforilação da proteína Rad, que deixa de inibir o canal (Liu, Nature 2020). O cálcio que entra pelo canal L é o gatilho da liberação pelo RyR2 (liberação induzida por cálcio), e a maior parte do cálcio da sístole vem do retículo; a fosforilação do fosfolambam, ao acelerar a SERCA2a, também aumenta a carga de cálcio do retículo. A contribuição funcional da fosforilação do RyR2 pela PKA ainda é debatida; por isso a figura não desenha seta da PKA para o RyR2 e mostra apenas os dois alvos bem estabelecidos, o canal tipo L e o fosfolambam.",
 "vasorefrat": "no VANCS (Hajjar, Anesthesiology 2017, InCor), na vasoplegia pós-CEC, a vasopressina teve menos morte ou complicação grave que a noradrenalina (32% vs. 49%); é uma população de cirurgia cardíaca, e o resultado não deve ser extrapolado para o choque séptico. Hidrocortisona: 200 mg/dia (50 mg de 6/6 h ou em infusão). Angiotensina II: no ATHOS-3, a resposta da PAM em 3 h ocorreu em 69,9% vs. 23,4% dos pacientes, sem diferença de mortalidade; é pouco disponível. Azul de metileno: inibe a óxido nítrico sintase e a guanilato ciclase solúvel; resgate na vasoplegia pós-CEC e na reperfusão do enxerto hepático, com evidência limitada. Contraindicado na deficiência de G6PD (hemólise); subestima a SpO₂ na oximetria de pulso e reduz o BIS; síndrome serotoninérgica com ISRS e outros serotoninérgicos, por inibir a MAO-A.",
 "ssc2026": "o VASSPR (JAMA 2026, n = 3.959; 13 hospitais, desenho cluster-crossover com ordem sorteada) comparou políticas hospitalares de iniciar a vasopressina com 0,1 vs. 0,4 mcg/kg/min de noradrenalina-equivalente; a vasopressina foi usada em 52,4% vs. 32,9%, e a mortalidade foi 31,8% vs. 33,0%. A antecipação sistemática não trouxe benefício, o que não exclui ganho em pacientes selecionados. No OPTPRESS, alvo de 80–85 mmHg em idosos aumentou a mortalidade."
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
        tempo += f". Total previsto: {mmss(TOTAL).replace(':', ' min ')} s nos {len(dados)} slides principais; ensaiar mirando 15 minutos."
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
