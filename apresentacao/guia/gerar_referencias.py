# Gera apresentacao/referencias.md (página aberta pelo QR code do último slide) a partir das
# referências conferidas em fonte (JSON produzido na sessão: autores, título, periódico, ano,
# volume/páginas e DOI). Uso: python3 gerar_referencias.py <refs.json> [reconferidas.json]
import json, sys, re
refs = json.load(open(sys.argv[1], encoding="utf-8"))
extra = {r["chave"].split(" ·")[0]: r for r in json.load(open(sys.argv[2], encoding="utf-8"))} if len(sys.argv) > 2 else {}
for r in refs:  # segunda conferência: completa o DOI das que ficaram sem confirmação
    k = r["chave"].split(" ·")[0]
    if r["veredito"] == "nao_confirmado" and k in extra and extra[k]["veredito"] in ("ok", "corrigido"):
        r.update({c: extra[k][c] for c in ("autores", "titulo", "periodico", "ano", "volume_paginas", "doi")}); r["veredito"] = "ok"

SECOES = [
 ("Diretrizes, consensos e declarações", ["Prescott", "Monnet", "Kinsella", "Saugel · POQI", "ANZCA", "Cecconi · consenso", "Konstam"]),
 ("Ensaios clínicos randomizados", ["De Backer", "Russell", "Gordon", "Peltan", "Lamontagne", "Endo", "Permpikul", "Annane · CATS", "Myburgh", "Levy", "Mathew", "Cuffe", "Hajjar", "Khanna", "Tongyoo", "Bellomo", "Venkatesh", "Annane · APROCCHSS", "Marcucci", "Saugel · IMPROVE", "Cecconi · HISTAP"]),
 ("Estudos observacionais, subanálises, revisões e cartas", ["Di Santo", "Gouvêa", "Sharkey", "Park", "Lineburger", "Salmasi", "Tran", "Kattan", "Overgaard", "Persichini", "Zaccolo", "Liu"]),
 ("Livro-texto", ["Miller"]),
]
def acha(prefixo):
    for r in refs:
        if r["chave"].startswith(prefixo): return r
    raise KeyError(prefixo)
APELIDO = {"De Backer": "SOAP II", "Russell": "VASST", "Gordon": "VANISH", "Peltan": "VASSPR", "Lamontagne": "65 trial", "Endo": "OPTPRESS", "Permpikul": "CENSER", "Annane · CATS": "CATS", "Myburgh": "CAT", "Levy": "OptimaCC", "Mathew": "DOREMI", "Cuffe": "OPTIME-CHF", "Hajjar": "VANCS", "Khanna": "ATHOS-3", "Bellomo": "ANZICS, dopamina em dose baixa", "Venkatesh": "ADRENAL", "Annane · APROCCHSS": "APROCCHSS", "Marcucci": "POISE-3", "Saugel · IMPROVE": "IMPROVE-multi", "Cecconi · HISTAP": "HISTAP", "Di Santo": "DOREMI, subanálise por betabloqueador", "Gouvêa": "transplante hepático, UFRJ", "Prescott": "Surviving Sepsis Campaign 2026", "Monnet": "ESICM 2025", "Saugel · POQI": "POQI", "Cecconi · consenso": "ESICM 2014", "Konstam": "AHA"}
def fmt(prefixo):
    r = acha(prefixo)
    autores = r["autores"].rstrip(".")
    nomes = [a.strip() for a in autores.split(",") if a.strip()]
    if len(nomes) > 4 and "(eds" not in autores and ";" not in autores: autores = ", ".join(nomes[:3]) + ", et al"
    partes = [autores + ".", r["titulo"].rstrip(".") + "."]
    if r["periodico"] == "Elsevier": partes.append(f"Elsevier; {r['ano']}.")
    elif r["periodico"] == "ANZCA/ANZAAG": partes.append(f"ANZCA e ANZAAG; {r['ano']}. Disponível em anzca.edu.au.")
    else:
        vp = f";{r['volume_paginas']}" if r["volume_paginas"] else ". Publicado online"
        partes.append(f"*{r['periodico']}*. {r['ano']}{vp}.")
    if r["doi"]: partes.append(f"doi: [{r['doi']}](https://doi.org/{r['doi']})")
    ap = APELIDO.get(prefixo)
    return ("**" + ap + ".** " if ap else "") + " ".join(partes)

linhas = ["# Aminas vasoativas: referências", "",
 "Sessão clínica de Anestesiologia, UFRJ. Bruno Dubois; orientadores: Marcelo Bandeira e Glauber Gouvêa.", "",
 "Lista das referências citadas na apresentação e nas notas, com DOI conferido em fonte. Cada estudo citado na fala está resumido nas notas do apresentador (população, contexto, comparação e resultado).", ""]
n = 0
for titulo, chaves in SECOES:
    linhas += [f"## {titulo}", ""]
    for c in chaves:
        n += 1; linhas.append(f"{n}. {fmt(c)}")
    linhas.append("")
sem_doi = [r["chave"].split(" ·")[0] for r in refs if not r["doi"] and r["periodico"] not in ("Elsevier", "ANZCA/ANZAAG")]
if sem_doi: linhas += ["> Sem DOI confirmado nesta lista: " + ", ".join(sem_doi) + ".", ""]
open("/home/user/Bruno/apresentacao/referencias.md", "w", encoding="utf-8").write("\n".join(linhas))
print(n, "referências;", len(sem_doi), "sem DOI:", sem_doi)
