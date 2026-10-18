# Marca os passos de aparecimento (data-passo="N") nos slides principais, na ordem da fala.
# Caminhos de índice = posição entre os filhos de cada elemento (como no dump estrutura.md).
import re, sys
from html.parser import HTMLParser
P = "/tmp/claude-0/-home-user-Bruno/82e201e1-5baf-5943-97e1-cc467015b7d6/scratchpad/artifact-files/351a25a9-1efc-412b-9232-d1cf8f2e53fe/project"
VAZIOS = {"br", "img", "hr", "x-shape", "x-icon", "x-connector"}

class N:
    def __init__(s, tag, pos): s.tag = tag; s.pos = pos; s.ch = []
class Pr(HTMLParser):
    def __init__(s, texto):
        super().__init__(); s.texto = texto
        s.inicio = [0]
        for i, c in enumerate(texto):
            if c == "\n": s.inicio.append(i + 1)
        s.root = N("root", -1); s.stack = [s.root]
    def abs(s): l, c = s.getpos(); return s.inicio[l - 1] + c
    def handle_starttag(s, tag, attrs):
        n = N(tag, s.abs()); s.stack[-1].ch.append(n)
        if tag not in VAZIOS: s.stack.append(n)
    def handle_startendtag(s, tag, attrs): s.handle_starttag(tag, attrs)
    def handle_endtag(s, tag):
        for i in range(len(s.stack) - 1, 0, -1):
            if s.stack[i].tag == tag: del s.stack[i:]; break

def marcar(id_, passos):
    """passos: lista de (caminho, n). caminho = tupla de índices a partir da <section>."""
    p = f"{P}/slides/{id_}.html"; t = open(p, encoding="utf-8").read()
    pr = Pr(t); pr.feed(t)
    sec = [c for c in pr.root.ch if c.tag == "section"][0]
    ins = []
    for cam, n in passos:
        el = sec
        for i in cam: el = el.ch[i]
        assert not t[el.pos:t.find('>', el.pos)].count('data-passo'), (id_, cam)
        ins.append((el.pos + 1 + len(el.tag), f' data-passo="{n}"'))
    for pos, s in sorted(ins, reverse=True): t = t[:pos] + s + t[pos:]
    open(p, "w", encoding="utf-8").write(t)
    return max(n for _, n in passos)

def tabela_em_blocos(id_, grupos, largura):
    """Divide a <table> do slide em várias tabelas empilhadas (uma por grupo de linhas),
    cada uma com data-passo quando indicado. grupos: lista de (n_linhas, passo ou None)."""
    p = f"{P}/slides/{id_}.html"; t = open(p, encoding="utf-8").read()
    m = re.search(r"<table([^>]*)>(.*?)</table>", t, re.S); assert m
    linhas = re.findall(r"<tr>.*?</tr>", m.group(2), re.S)
    assert sum(n for n, _ in grupos) == len(linhas), (len(linhas), grupos)
    larguras = re.findall(r'width:(\d+%)', linhas[0]); assert larguras
    blocos = []; k = 0
    for n, passo in grupos:
        grupo = linhas[k:k + n]; k += n
        if "<th" not in grupo[0]:  # largura das colunas na primeira linha de cada tabela
            cels = re.findall(r"<td[^>]*>", grupo[0]); assert len(cels) == len(larguras)
            for c, w in zip(cels, larguras):
                grupo[0] = grupo[0].replace(c, c.replace('style="', f'style="width:{w}; ', 1), 1)
        attr = f' data-passo="{passo}"' if passo else ""
        blocos.append(f"<table{attr}{m.group(1)}>{''.join(grupo)}</table>")
    novo = f'<div style="display:flex; flex-direction:column; gap:0; width:{largura}">' + "".join(blocos) + "</div>"
    t = t[:m.start()] + novo + t[m.end():]
    open(p, "w", encoding="utf-8").write(t)
    return max(p_ for _, p_ in grupos if p_)

ESPEC = {
 "objetivos": [((1, 0), 1), ((1, 1), 2), ((1, 2), 3), ((1, 3), 4), ((2,), 5)],
 "fisiologia": [((1, 0), 1), ((1, 1), 2), ((1, 2), 3), ((2,), 4)],
 "perfusao": [((1, 0), 1), ((1, 1), 2), ((2,), 3)],
 "classificacao": [((2, 0), 1), ((2, 1), 2)],
 "noradrenalina": [((1, 0), 1), ((1, 1), 2), ((1, 2), 3)],
 "adrenalina": [((1, 1), 1), ((1, 2), 2)],
 "dopadobuta": [((1, 0, 1), 1), ((1, 1, 0), 2), ((1, 1, 1), 3)],
 "sinalizacao": [((2,), 1)],
 "milrinona": [((1, 1, 0), 1), ((1, 1, 1), 2)],
 "milrdobu": [((1,), 1), ((2,), 2), ((3, 0), 3), ((3, 1), 4)],
 "condutavd": [((1, 0), 1), ((1, 1), 2), ((1, 2), 3), ((1, 3), 4), ((2,), 5)],
 "fenilefedrina": [((1, 0, 1), 1), ((1, 1, 0), 2), ((1, 1, 1), 3)],
 "vasorefrat": [((1, 1, 0), 1), ((1, 1, 1), 2), ((1, 1, 2), 3)],
 "ssc2026": [((1, 0, 0), 1), ((1, 0, 1), 2), ((1, 0, 2), 2), ((1, 0, 3), 3), ((1, 0, 4), 3), ((1, 1, 0), 4), ((1, 1, 1), 5)],
 "intraop": [((2, 0), 1), ((2, 1), 2), ((2, 2), 3), ((2, 3), 4), ((2, 4), 5), ((3,), 6), ((4,), 7)],
 "pamintraop": [((1, 1, 0), 1), ((1, 1, 1), 2), ((1, 1, 2), 3)],
}
if __name__ == "__main__":
    total = {}
    for id_, passos in ESPEC.items(): total[id_] = marcar(id_, passos)
    # tabelas linha a linha: receptores (cabeçalho+α1+α2 visíveis; β1+β2; D1; V1+PDE3) e mensagens
    total["receptores"] = max(tabela_em_blocos("receptores", [(3, None), (2, 1), (1, 2), (2, 3)], "1664px"), marcar("receptores", [((2,), 4)]))
    total["mensagens"] = tabela_em_blocos("mensagens", [(2, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6)], "1664px")
    print(total)
