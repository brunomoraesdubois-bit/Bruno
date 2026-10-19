# Gera os áudios da fala (um por slide e um completo) com a voz masculina brasileira do Kokoro.
# Uso: python3 gerar_audio.py <kokoro-v1.0.onnx> <voices-v1.0.bin> [voz=pm_alex] [velocidade=0.95]
# Lê FALA e TRANSIÇÃO das notas de cada slide (deck/slides/<id>.html, na ordem de deck.json) e
# converte siglas, números e unidades para a forma falada antes da síntese.
import sys, re, json, html, os, subprocess
import numpy as np, soundfile as sf
from num2words import num2words
from kokoro_onnx import Kokoro

AQUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(AQUI, "..", "deck")
modelo, vozes = sys.argv[1], sys.argv[2]
VOZ = sys.argv[3] if len(sys.argv) > 3 else "pm_alex"
VEL = float(sys.argv[4]) if len(sys.argv) > 4 else 0.9
SAIDA = os.path.join(AQUI, VOZ)
os.makedirs(SAIDA, exist_ok=True)

SIGLAS = [  # (padrão, forma falada); ordem importa
 (r"\bα1\b", "alfa §1"), (r"\bβ1\b", "beta §1"), (r"\bβ2\b", "beta §2"), (r"\bD1\b", "dê um"), (r"\bV1\b", "vê um"), (r"\bAT1\b", "á tê um"),
 (r"α-agonista", "alfa-agonista"), (r"\bα\b", "alfa"), (r"\bβ\b", "beta"),
 (r"\bPAM\b", "pãm"), (r"\bRVS\b", "érre vê ésse"), (r"\bRVP\b", "érre vê pê"), (r"\bDC\b", "dê cê"), (r"\bVD\b", "vê dê"), (r"\bVE\b", "vê é"),
 (r"\bFC\b", "éfe cê"), (r"\bPVC\b", "pê vê cê"), (r"\bCEC\b", "céc"), (r"\bETE\b", "ecocardiografia transesofágica"), (r"\bPDE3\b", "pê dê é três"),
 (r"\bAMPc\b", "a ême pê cíclico"), (r"5′-AMP", "cinco linha a ême pê"), (r"\bAMP\b", "a ême pê"), (r"\bPKA\b", "pê cá á"), (r"\bGs\b", "gê ésse"), (r"\bSERCA2a\b", "serca dois a"),
 (r"\bSurviving Sepsis Campaign\b", "Survaiving Sépsis Campeim"), (r"\bSSC\b", "ésse ésse cê"), (r"\bSOAP II\b", "sôup dois"), (r"\bOPTIME-CHF\b", "óptime cê agá éfe"), (r"\bPOISE-3\b", "poise três"), (r"\bIMPROVE-multi\b", "improve multi"),
 (r"\bVASSPR\b", "vás-pê-érre"), (r"\bPOQI\b", "póqui"), (r"\bESICM\b", "diretriz europeia de terapia intensiva de"), (r"\bANZICS\b", "anzics"), (r"\bANZAAG\b", "anzág"), (r"\bANZCA\b", "anzca"),
 (r"\bTAPSE\b", "tápsi"), (r"\bVTI\b", "vê tê i"), (r"\bPAS\b", "pê á ésse"), (r"\bAV\b", "á vê"), (r"\bAVC\b", "a vê cê"), (r"\bEV\b", "endovenosos"), (r"\bIM\b", "intramuscular"),
 (r"\bIECA\b", "iéca"), (r"\bBRA\b", "bê érre á"), (r"\bNA\b", "noradrenalina"), (r"\bUFRJ\b", "u éfe érre jota"), (r"\bQR code\b", "código quê érre"),
 (r"\bPLoS One\b", "plós uan"), (r"\bJAMA\b", "jama"), (r"\bHISTAP\b", "ristap"), (r"\bDOREMI\b", "doremi"), (r"\bVPP\b", "vê pê pê"), (r"\bVVS\b", "vê vê ésse"), (r"\bSNC\b", "ésse ene cê"),
 (r"mcg/kg/min", "microgramas por quilo por minuto"), (r"mcg/kg", "microgramas por quilo"), (r"U/min", "unidades por minuto"), (r"mg/dia", "miligramas por dia"),
 (r"\bmmHg\b", "milímetros de mercúrio"), (r"\bmcg\b", "microgramas"), (r"\bmg\b", "miligramas"), (r"\bkg\b", "quilo"), (r"\bmin\b", "minutos"),
 (r"“The hidden cost of hypotension”, de Lineburger e colaboradores,", "de Lineburguer e colaboradores sobre o custo oculto da hipotensão,"),
 (r"\bPersichini\b", "Persiquini"), (r"\bGouvêa\b", "Govêa"), (r"\b[Mm]ilrinona\b", "miurinona"),
 (r"≥", "maior ou igual a "), (r"[“”]", ""), (r"\s*▸\s*", " "),
]
def numero(m):
    s = m.group(0).replace(".", "")
    if "," in s:
        i, d = s.split(",")
        if not d.strip("0"): return num2words(int(i), lang="pt_BR")  # 33,0 → trinta e três
        return num2words(int(i), lang="pt_BR") + " vírgula " + ("zero " * (len(d) - len(d.lstrip("0")))) + num2words(int(d), lang="pt_BR")
    return num2words(int(s), lang="pt_BR")
def falado(t):
    t = html.unescape(t)
    for p, r in SIGLAS: t = re.sub(p, r, t)
    t = re.sub(r"(\d)\s*[–-]\s*(\d)", r"\1 a \2", t)                   # 60–65 → 60 a 65
    t = re.sub(r"(\d+(?:,\d+)?)\s*%", r"\1 por cento", t)              # 48,5% → ... por cento
    t = re.sub(r"(?<!§)\d{1,3}(?:\.\d{3})+(?:,\d+)?|(?<!§)\d+(?:,\d+)?", numero, t)  # números por extenso (exceto após §)
    t = t.replace("§", "").replace("  ", " ")  # § protege o algarismo de alfa 1 / beta 1 (lido com pausa mais clara)
    return t.strip()

deck = json.load(open(os.path.join(DECK, "deck.json"), encoding="utf-8"))
def notas(id_):
    t = open(os.path.join(DECK, "slides", f"{id_}.html"), encoding="utf-8").read()
    n = html.unescape(re.search(r"<aside>(.*?)</aside>", t, re.S).group(1))
    c = dict(re.findall(r"^([A-ZÇÃÕ\- ]+): ?(.*)$", n, re.M))
    titulo = re.search(r"<h[12][^>]*>(.*?)</h[12]>", t, re.S); titulo = html.unescape(re.sub("<[^>]+>", "", titulo.group(1))) if titulo else id_
    return titulo, c.get("FALA", ""), c.get("TRANSIÇÃO", "")

k = Kokoro(modelo, vozes)
def sintetizar(texto):
    audio, sr = k.create(texto, voice=VOZ, speed=VEL, lang="pt-br"); return audio.astype(np.float32), sr
pausa = lambda s, sr: np.zeros(int(s * sr), dtype=np.float32)
roteiro = []; completo = []; sr = 24000
for n, id_ in enumerate(deck["order"], 1):
    titulo, fala, trans = notas(id_)
    texto = f"Slide {num2words(n, lang='pt_BR')}. {falado(titulo)}. " + falado(fala) + (" " + falado(trans) if trans else "")
    audio, sr = sintetizar(texto)
    nome = f"{n:02d} - {re.sub(r'[^\w\s-]', '', titulo).strip()[:60]}"
    sf.write(os.path.join(SAIDA, nome + ".wav"), audio, sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(SAIDA, nome + ".wav"), "-ac", "1", "-b:a", "80k",
                    "-metadata", f"title={n:02d} {titulo}", "-metadata", f"track={n}", "-metadata", "album=Aminas vasoativas: fala", "-metadata", "artist=Bruno Dubois",
                    os.path.join(SAIDA, nome + ".mp3")], check=True)
    os.remove(os.path.join(SAIDA, nome + ".wav"))
    completo += [audio, pausa(1.0, sr)]
    roteiro.append({"slide": n, "id": id_, "titulo": titulo, "segundos": round(len(audio) / sr, 1), "texto": texto})
    print(f"{n:02d} {titulo[:40]:40s} {len(audio)/sr:6.1f} s", flush=True)
tudo = np.concatenate(completo)
sf.write(os.path.join(SAIDA, "completo.wav"), tudo, sr)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(SAIDA, "completo.wav"), "-ac", "1", "-b:a", "80k",
                "-metadata", "title=Aminas vasoativas: fala completa", "-metadata", "album=Aminas vasoativas: fala", "-metadata", "artist=Bruno Dubois",
                os.path.join(SAIDA, "00 - Aminas vasoativas - fala completa.mp3")], check=True)
os.remove(os.path.join(SAIDA, "completo.wav"))
json.dump(roteiro, open(os.path.join(SAIDA, "roteiro.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("total", round(len(tudo) / sr / 60, 1), "min")
