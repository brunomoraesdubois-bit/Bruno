# Esquema do cardiomiócito: via β1–Gs–AC–AMPc–PKA e PDE3 (dobutamina × milrinona)
W, H = 1664, 520
NAVY, LARANJA, CLARO, CINZA, MEMB = "#1b2a3a", "#b9581a", "#e49a5c", "#56606b", "#e9dfcc"
F = "font-family:'Source Sans 3';"
s = []
def t(x, y, txt, size=22, cor=NAVY, peso=600, anc="middle", estilo=""):
    s.append(f'<text x="{x}" y="{y}" text-anchor="{anc}" style="{F}font-size:{size}px;font-weight:{peso};fill:{cor};{estilo}">{txt}</text>')
def seta(x1, y1, x2, y2, cor=NAVY, tr=""):
    s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{cor}" stroke-width="4" marker-end="url(#p{cor[1:]})" {tr}/>')
def bloqueio(x1, y1, x2, y2, cor=CINZA):
    import math
    s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{cor}" stroke-width="4"/>')
    dx, dy = x2 - x1, y2 - y1; n = math.hypot(dx, dy); px, py = -dy / n * 14, dx / n * 14
    s.append(f'<line x1="{x2-px:.1f}" y1="{y2-py:.1f}" x2="{x2+px:.1f}" y2="{y2+py:.1f}" stroke="{cor}" stroke-width="5"/>')
def caixa(x, y, w, h, txt, fundo=NAVY, cor="#f5f3ee", borda="none", size=22, rx=12):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fundo}" stroke="{borda}" stroke-width="2.5"/>')
    t(x + w / 2, y + h / 2 + size * 0.35, txt, size, cor, 700)

marcadores = "".join(f'<marker id="p{c[1:]}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for c in (NAVY, LARANJA, CINZA))
# fundo e membrana
s.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="12" fill="#fffdf8" stroke="#e2ddd2" stroke-width="2"/>')
s.append(f'<rect x="1" y="118" width="{W-2}" height="34" fill="{MEMB}"/>')
s.append(f'<line x1="1" y1="118" x2="{W-1}" y2="118" stroke="#c9b99a" stroke-width="3"/><line x1="1" y1="152" x2="{W-1}" y2="152" stroke="#c9b99a" stroke-width="3"/>')
t(W - 24, 40, "MEIO EXTRACELULAR", 18, CINZA, 600, "end", "letter-spacing:2px;")
t(W - 24, 300, "CITOPLASMA DO CARDIOMIÓCITO", 18, CINZA, 600, "end", "letter-spacing:2px;")
# receptor β1, dobutamina e betabloqueador
caixa(250, 96, 100, 78, "β1", size=28)
t(300, 205, "Receptor β1")
caixa(220, 22, 160, 42, "Dobutamina", LARANJA, size=22, rx=21)
seta(300, 66, 300, 92, LARANJA)
caixa(24, 22, 176, 42, "Betabloqueador", "#8a98a8", size=22, rx=21)
bloqueio(200, 60, 246, 96)
# Gs e adenilato ciclase
s.append(f'<ellipse cx="452" cy="196" rx="44" ry="28" fill="#33475e"/>'); t(452, 204, "Gs", 24, "#f5f3ee", 700)
seta(352, 166, 404, 186); seta(498, 186, 546, 166)
caixa(548, 96, 210, 78, "Adenilato ciclase", size=22)
# ATP → AMPc → PKA
seta(653, 176, 653, 214)
t(672, 202, "ATP → AMPc", 20, CINZA, 600, "start")
s.append(f'<circle cx="653" cy="262" r="44" fill="{LARANJA}"/>'); t(653, 270, "AMPc", 24, "#fffdf8", 700)
seta(699, 262, 796, 262)
caixa(800, 232, 120, 60, "PKA", size=26)
# PDE3 e milrinona
seta(653, 308, 653, 360)
t(672, 342, "degradação", 20, CINZA, 600, "start")
caixa(593, 364, 120, 56, "PDE3", "#fffdf8", NAVY, NAVY, 24)
seta(715, 392, 790, 392, CINZA)
t(798, 400, "5′-AMP (inativo)", 20, CINZA, 600, "start")
caixa(330, 371, 170, 42, "Milrinona", LARANJA, size=22, rx=21)
bloqueio(502, 392, 588, 392, LARANJA)
t(545, 380, "inibe", 18, CINZA, 600)
# canal de cálcio tipo L
s.append(f'<rect x="1046" y="96" width="24" height="78" rx="8" fill="{NAVY}"/><rect x="1094" y="96" width="24" height="78" rx="8" fill="{NAVY}"/>')
t(1136, 52, "Canal de Ca²⁺ tipo L", 22, NAVY, 700, "start")
seta(1082, 70, 1082, 222, LARANJA)
t(1082, 250, "Ca²⁺", 22, LARANJA, 700)
# retículo sarcoplasmático
s.append(f'<rect x="1000" y="376" width="620" height="118" rx="40" fill="#f6e6d5" stroke="{CLARO}" stroke-width="2.5"/>')
t(1310, 478, "Retículo sarcoplasmático", 22, NAVY, 700)
caixa(1040, 354, 120, 44, "RyR2", size=22)
t(1100, 428, "libera Ca²⁺", 20, CINZA, 600)
caixa(1330, 354, 250, 44, "SERCA2a · fosfolambam", size=21)
t(1455, 428, "recapta Ca²⁺", 20, CINZA, 600)
# fosforilação pela PKA
for (x2, y2) in ((1044, 178), (1452, 350)):
    s.append(f'<line x1="922" y1="262" x2="{x2}" y2="{y2}" stroke="{LARANJA}" stroke-width="3" stroke-dasharray="9 7" marker-end="url(#p{LARANJA[1:]})"/>')
t(860, 322, "PKA fosforila →", 20, LARANJA, 700)
# resultado
t(1170, 214, "↑ Ca²⁺ sistólico: inotropismo", 23, NAVY, 700, "start")
t(1170, 250, "↑ recaptação diastólica: lusitropismo", 23, NAVY, 700, "start")
s.append(f'<rect x="24" y="440" width="930" height="64" rx="12" fill="#eef1f4" stroke="#8a98a8" stroke-width="2" stroke-dasharray="8 6"/>')
t(44, 479, "MÚSCULO LISO VASCULAR", 18, CINZA, 600, "start", "letter-spacing:2px;")
t(300, 480, "AMPc → PKA", 22, NAVY, 700, "start")
bloqueio(428, 472, 486, 472, NAVY)
t(498, 480, "MLCK → relaxamento: vasodilatação", 22, NAVY, 700, "start")
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{marcadores}</defs>{"".join(s)}</svg>'
open(__import__("os").path.join(__import__("os").path.dirname(__file__), "figura-ampc.svg"), "w", encoding="utf-8").write(svg)
print("ok")
