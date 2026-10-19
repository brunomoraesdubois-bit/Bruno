# Aplica os capítulos do Miller's Anesthesia, 10ª ed., nas citações dos slides e na referência 43.
# Preencha CAPITULOS com a numeração conferida no sumário do livro (número: título) e rode:
#   python3 aplicar_capitulos.py            (só mostra o que faria)
#   python3 aplicar_capitulos.py --aplicar  (edita deck/slides/*.html e o projeto do Claude, se existir)
# Depois: regenerar notas (montar_guia.py), prints, PPTX e referencias.md como nas versões anteriores.
import re, sys, os, glob
CAPITULOS = {  # número confirmado: título em inglês (deixe None enquanto não conferir)
 "Cardiac Physiology": None,
 "Basic Principles of Pharmacology": None,
 "Cardiovascular Pharmacology": None,   # se existir como capítulo; é o mais pertinente para os slides de drogas
 "Perioperative Echocardiography and Point-of-Care Ultrasound": None,
 "Perioperative Fluid and Electrolyte Therapy": None,
 "Anesthesia for Cardiac Surgical Procedures": None,
 "Anesthesia for Abdominal Organ Transplantation": None,
 "Anesthesia for Obstetrics": None,
 "Critical Care Anesthesiology": None,
}
# slide → capítulos pertinentes (títulos acima); a citação vira "Miller’s Anesthesia, 10ª ed. (2025), cap. N[, M]"
POR_SLIDE = {
 "fisiologia": ["Cardiac Physiology", "Perioperative Fluid and Electrolyte Therapy"],
 "receptores": ["Basic Principles of Pharmacology", "Cardiovascular Pharmacology"],
 "classificacao": ["Basic Principles of Pharmacology", "Cardiovascular Pharmacology"],
 "noradrenalina": ["Cardiovascular Pharmacology", "Critical Care Anesthesiology"],
 "dopadobuta": ["Cardiovascular Pharmacology"],
 "sinalizacao": ["Cardiac Physiology", "Cardiovascular Pharmacology"],
 "milrinona": ["Cardiovascular Pharmacology", "Anesthesia for Cardiac Surgical Procedures"],
 "condutavd": ["Cardiac Physiology", "Anesthesia for Cardiac Surgical Procedures"],
 "fenilefedrina": ["Cardiovascular Pharmacology", "Anesthesia for Obstetrics"],
 "efedrina": ["Cardiovascular Pharmacology", "Anesthesia for Obstetrics"],
 "intraop": ["Perioperative Echocardiography and Point-of-Care Ultrasound", "Anesthesia for Abdominal Organ Transplantation"],
 "roteiro": [],
}
BASE = "Miller’s Anesthesia, 10ª ed. (2025)"
aplicar = "--aplicar" in sys.argv
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pastas = [os.path.join(raiz, "deck", "slides")]
for extra in glob.glob("/tmp/claude-0/*/scratchpad/artifact-files/*/project/slides"): pastas.append(extra)
for pasta in pastas:
    for id_, caps in POR_SLIDE.items():
        p = os.path.join(pasta, id_ + ".html")
        if not os.path.exists(p): continue
        nums = [CAPITULOS[c] for c in caps if CAPITULOS.get(c)]
        if not nums: print(f"{id_}: sem capítulo confirmado, citação mantida"); continue
        novo = BASE + ", cap. " + ", ".join(str(n) for n in sorted(set(nums)))
        t = open(p, encoding="utf-8").read()
        if BASE + ", cap." in t: t = re.sub(re.escape(BASE) + r", cap\. [0-9, ]+", novo, t)
        else: t = t.replace(BASE, novo)
        print(f"{id_}: {novo}")
        if aplicar: open(p, "w", encoding="utf-8").write(t)
print("aplicado" if aplicar else "simulação; use --aplicar para gravar")
