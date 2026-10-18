#!/usr/bin/env node
// Converte o deck (deck.json + slides/<id>.html, no formato do tipo Slides do Claude)
// em um .pptx editável.
//
// Cada slide é renderizado no Chromium (Playwright) com Calibri e Georgia, as fontes que
// o PowerPoint vai usar, e o layout medido vira formas, caixas de texto, tabelas nativas
// e notas do apresentador via pptxgenjs.
//
// Uso: node html_para_pptx.js <pasta-do-deck> <saida.pptx> [--prints <pasta>]
'use strict';

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { chromium } = require('playwright');
const PptxGenJS = require('pptxgenjs');
const JSZip = require('jszip');

const PX = 1 / 144; // polegadas por px: 1920 px = 13,333 pol (LAYOUT_WIDE)
const PT = 0.5; // pontos por px
const FONTE_TITULO = 'Georgia';
const FONTE_TEXTO = 'Calibri';
// A Georgia tem algarismos de estilo antigo ("0,03" vira "o,o3"): números serifados fora dos
// títulos saem em Cambria, que tem algarismos alinhados
const FONTE_NUMEROS = 'Cambria';

const TEMA = {
  nome: 'Aminas Vasoativas',
  cores: {
    dk1: '1B2A3A', lt1: 'FFFDF8', dk2: '2C3A48', lt2: 'F5F3EE',
    accent1: 'B9581A', accent2: '2E5E8C', accent3: '56606B',
    accent4: 'E49A5C', accent5: '33475E', accent6: 'E2DDD2',
    hlink: '2E5E8C', folHlink: '56606B',
  },
};

// ---------------------------------------------------------------------------
// Fontes usadas na medição: Georgia (Gelasio) e Calibri (Carlito), com as mesmas métricas

function arquivoFonte(padrao) {
  try {
    const f = execSync(`fc-match -f "%{file}" "${padrao}"`, { encoding: 'utf8' }).trim();
    return f && fs.existsSync(f) ? f : null;
  } catch {
    return null;
  }
}

function cssFontes() {
  const gelasio = path.join(path.dirname(require.resolve('@fontsource/gelasio/package.json')), 'files');
  const faces = [];
  for (const [peso, faixa] of [[400, '100 549'], [700, '550 900']]) {
    for (const estilo of ['normal', 'italic']) {
      const url = 'file://' + path.join(gelasio, `gelasio-latin-${peso}-${estilo}.woff2`);
      faces.push(`@font-face{font-family:"Georgia";src:url("${url}");font-weight:${faixa};font-style:${estilo}}`);
    }
  }
  const carlito = [
    ['Carlito:style=Regular', '100 549', 'normal'],
    ['Carlito:style=Bold', '550 900', 'normal'],
    ['Carlito:style=Italic', '100 549', 'italic'],
    ['Carlito:style=Bold Italic', '550 900', 'italic'],
  ];
  for (const [padrao, faixa, estilo] of carlito) {
    const f = arquivoFonte(padrao);
    if (f && /carlito/i.test(f)) {
      faces.push(`@font-face{font-family:"Calibri";src:url("file://${f}");font-weight:${faixa};font-style:${estilo}}`);
    }
  }
  return faces.join('\n');
}

// Padrões do runtime do tipo Slides (reference/format.md): div sem display = coluna,
// border-box, p com line-height 1,4, h1–h3 com tamanhos e pesos próprios, células 0,35em 0,6em.
// Kerning desligado deixa a medição um pouco mais larga que o PowerPoint, nunca mais estreita.
const CSS_BASE = `
*{margin:0;padding:0;box-sizing:border-box;font-kerning:none;font-variant-ligatures:none;font-synthesis:none}
html,body{width:1920px;height:1080px;overflow:hidden;background:#fff}
section{position:relative;width:1920px;height:1080px;overflow:hidden;display:flex;flex-direction:column;font-size:32px}
div:not([style*="display"]){display:flex;flex-direction:column}
h1{font-size:96px;font-weight:600;line-height:1.1}
h2{font-size:64px;font-weight:600;line-height:1.15}
h3{font-size:44px;font-weight:600;line-height:1.2}
p{line-height:1.4}
table{border-collapse:collapse;border-spacing:0}
td,th{padding:.35em .6em;line-height:1.4;text-align:left}
th{font-weight:700}
b,strong{font-weight:700}
aside{display:none}
x-shape,x-icon{display:block}
`;

function trocarFontes(html) {
  return html.replace(/font-family:\s*([^;"]+)/g, (_, lista) => {
    const serif = /source serif|georgia|(^|,)\s*serif\s*$/i.test(lista.trim()) && !/sans-serif\s*$/i.test(lista.trim());
    return serif ? 'font-family:Georgia, serif' : 'font-family:Calibri, sans-serif';
  });
}

// ---------------------------------------------------------------------------
// Medição no navegador: devolve fundo, itens em ordem de pintura e notas

function extrairSlide() {
  const sec = document.querySelector('section');
  const S = sec.getBoundingClientRect();
  const hex = (c) => {
    const m = /rgba?\(([^)]+)\)/.exec(c || '');
    if (!m) return null;
    const v = m[1].split(/[ ,/]+/).filter(Boolean).map(Number);
    if (v.length > 3 && v[3] === 0) return null;
    return v.slice(0, 3).map((n) => Math.round(n).toString(16).padStart(2, '0')).join('').toUpperCase();
  };
  const caixa = (r) => ({ x: r.left - S.left, y: r.top - S.top, w: r.width, h: r.height });
  const lados = (cs) => ['Top', 'Right', 'Bottom', 'Left'].map((s) => ({
    w: cs[`border${s}Style`] === 'none' ? 0 : parseFloat(cs[`border${s}Width`]) || 0,
    c: hex(cs[`border${s}Color`]),
  }));
  const pintura = (cs) => {
    const bg = hex(cs.backgroundColor);
    const b = lados(cs);
    if (!bg && !b.some((l) => l.w > 0 && l.c)) return null;
    return { bg, bordas: b, raio: parseFloat(cs.borderTopLeftRadius) || 0 };
  };
  const recuos = (cs) => ['Top', 'Right', 'Bottom', 'Left'].map((s) =>
    (parseFloat(cs[`padding${s}`]) || 0) + (cs[`border${s}Style`] === 'none' ? 0 : parseFloat(cs[`border${s}Width`]) || 0));
  const alturaLinha = (cs) => {
    const fs = parseFloat(cs.fontSize);
    return cs.lineHeight === 'normal' ? fs * 1.15 : parseFloat(cs.lineHeight);
  };

  function trechos(el) {
    const out = [];
    const estilo = (node) => {
      const cs = getComputedStyle(node);
      return {
        cor: hex(cs.color),
        negrito: parseInt(cs.fontWeight, 10) >= 600,
        italico: cs.fontStyle === 'italic',
        sublinhado: cs.textDecorationLine.includes('underline'),
        tam: parseFloat(cs.fontSize),
        serif: /^\s*"?Georgia/i.test(cs.fontFamily),
        espaco: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing) || 0,
        maiusculas: cs.textTransform === 'uppercase',
        link: node.closest('a') ? node.closest('a').href : null,
      };
    };
    (function rec(node) {
      for (const ch of node.childNodes) {
        if (ch.nodeType === 3) {
          // Espaço inseparável (U+00A0) fica como está: o PowerPoint o respeita como não quebrável
          let t = ch.textContent.replace(/[ \t\r\n\f]+/g, ' ');
          if (!t) continue;
          const st = estilo(ch.parentElement);
          if (st.maiusculas) t = t.toUpperCase();
          out.push({ texto: t, ...st });
        } else if (ch.nodeType === 1) {
          if (ch.tagName === 'BR') out.push({ quebra: true });
          else rec(ch);
        }
      }
    })(el);
    // Espaços como o CSS: sem espaço no início/fim de linha nem duplicado entre trechos
    let anteriorTerminaEmEspaco = true;
    for (let i = 0; i < out.length; i++) {
      const r = out[i];
      if (r.quebra) {
        anteriorTerminaEmEspaco = true;
        for (let j = i - 1; j >= 0 && !out[j].quebra; j--) {
          out[j].texto = out[j].texto.replace(/ $/, '');
          if (out[j].texto) break;
        }
        continue;
      }
      if (anteriorTerminaEmEspaco) r.texto = r.texto.replace(/^ /, '');
      if (r.texto) anteriorTerminaEmEspaco = r.texto.endsWith(' ');
    }
    for (let j = out.length - 1; j >= 0 && !out[j].quebra; j--) {
      out[j].texto = out[j].texto.replace(/ $/, '');
      if (out[j].texto) break;
    }
    return out.filter((r) => r.quebra || r.texto);
  }

  const TAGS_TEXTO = new Set(['P', 'H1', 'H2', 'H3', 'H4', 'LI', 'TD', 'TH']);
  const ehTexto = (el) => TAGS_TEXTO.has(el.tagName)
    || [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());

  function bloco(el, cs) {
    const r = caixa(el.getBoundingClientRect());
    const rec = recuos(cs);
    const lh = alturaLinha(cs);
    const conteudoH = r.h - rec[0] - rec[2];
    return {
      tipo: 'texto',
      tag: el.tagName,
      caixa: r,
      recuos: rec,
      pintura: pintura(cs),
      trechos: trechos(el),
      alinhamento: ({ start: 'left', left: 'left', center: 'center', right: 'right', end: 'right', justify: 'justify' })[cs.textAlign] || 'left',
      vertical: cs.verticalAlign,
      lh,
      linhas: Math.max(1, Math.round(conteudoH / lh)),
      semQuebra: cs.whiteSpace === 'nowrap',
      // Item de lista: recuo do marcador = padding-left da lista
      marcador: el.tagName === 'LI' ? parseFloat(getComputedStyle(el.parentElement).paddingLeft) || 0 : 0,
      fixo: cs.position === 'absolute',
    };
  }

  function tabela(t) {
    return {
      tipo: 'tabela',
      caixa: caixa(t.getBoundingClientRect()),
      linhas: [...t.rows].map((tr) => {
        const fundoLinha = hex(getComputedStyle(tr).backgroundColor);
        return {
          h: tr.getBoundingClientRect().height,
          celulas: [...tr.cells].map((td) => {
            const cs = getComputedStyle(td);
            const b = bloco(td, cs);
            return {
              ...b,
              fundo: hex(cs.backgroundColor) || fundoLinha,
              bordas: lados(cs),
              recuos: ['Top', 'Right', 'Bottom', 'Left'].map((s) => parseFloat(cs[`padding${s}`]) || 0),
            };
          }),
        };
      }),
    };
  }

  const itens = [];
  function percorrer(el) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    if (el.tagName === 'X-SHAPE') {
      itens.push({ tipo: 'forma', tipoForma: el.getAttribute('kind'), caixa: caixa(el.getBoundingClientRect()), cor: hex(cs.backgroundColor) });
      return;
    }
    if (el.tagName === 'TABLE') {
      itens.push(tabela(el));
      return;
    }
    if (el.tagName === 'IMG') {
      itens.push({ tipo: 'imagem', caixa: caixa(el.getBoundingClientRect()), src: el.getAttribute('src') || '', alt: el.getAttribute('alt') || '' });
      return;
    }
    if (ehTexto(el)) {
      itens.push(bloco(el, cs));
      return;
    }
    const p = pintura(cs);
    if (p) itens.push({ tipo: 'caixa', caixa: caixa(el.getBoundingClientRect()), pintura: p });
    for (const ch of el.children) percorrer(ch);
  }
  for (const ch of sec.children) percorrer(ch);

  const aside = sec.querySelector(':scope > aside');
  return {
    fundo: hex(getComputedStyle(sec).backgroundColor) || 'FFFFFF',
    itens,
    // As notas do guia de fala vêm em blocos rotulados, um por linha
    notas: aside ? aside.textContent.split('\n').map((l) => l.replace(/\s+/g, ' ').trim()).filter(Boolean).join('\n') : '',
  };
}

async function medirDeck(pastaDeck, deck, pastaPrints) {
  const harness = `<!doctype html><html><head><meta charset="utf-8"><style>${cssFontes()}\n${CSS_BASE}</style></head><body></body></html>`;
  const arqHarness = path.join(require('os').tmpdir(), `harness-${process.pid}.html`);
  fs.writeFileSync(arqHarness, harness);
  const navegador = await chromium.launch();
  const pagina = await navegador.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await pagina.goto('file://' + arqHarness);
  await pagina.evaluate(() => Promise.all(['Georgia', 'Calibri'].flatMap((f) =>
    ['400', '700', 'italic 400', 'italic 700'].map((v) => document.fonts.load(`${v} 32px ${f}`)))));
  const slides = [];
  for (const id of deck.order) {
    const arq = path.join(pastaDeck, 'slides', `${id}.html`);
    if (!fs.existsSync(arq)) continue;
    const html = trocarFontes(fs.readFileSync(arq, 'utf8'));
    await pagina.evaluate(async (h) => {
      document.body.innerHTML = h;
      void document.body.offsetHeight;
      await document.fonts.ready;
    }, html);
    const medido = await pagina.evaluate(extrairSlide);
    if (pastaPrints) {
      fs.mkdirSync(pastaPrints, { recursive: true });
      await pagina.screenshot({ path: path.join(pastaPrints, `${String(slides.length + 1).padStart(2, '0')}-${id}.png`) });
    }
    slides.push({ id, ...medido });
  }
  await navegador.close();
  fs.unlinkSync(arqHarness);
  return slides;
}

// ---------------------------------------------------------------------------
// Montagem do .pptx

const SOBRE = { '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁺': '+', '⁻': '-' };
const SOB = { '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9' };

// "Ca²⁺" e "O₂" viram sobrescrito/subscrito de verdade: nem toda fonte tem esses glifos
function separarIndices(texto) {
  const partes = [];
  let atual = { texto: '', sobre: false, sob: false };
  for (const ch of texto) {
    const sobre = ch in SOBRE;
    const sob = ch in SOB;
    if (sobre !== atual.sobre || sob !== atual.sob) {
      if (atual.texto) partes.push(atual);
      atual = { texto: '', sobre, sob };
    }
    atual.texto += sobre ? SOBRE[ch] : sob ? SOB[ch] : ch;
  }
  if (atual.texto) partes.push(atual);
  return partes;
}

function montarTrechos(trechos, tag = '') {
  const titulo = /^H[12]$/.test(tag);
  const out = [];
  let quebrarAntes = false;
  for (const r of trechos) {
    if (r.quebra) {
      quebrarAntes = true;
      continue;
    }
    for (const parte of separarIndices(r.texto)) {
      const op = {
        fontFace: r.serif ? (!titulo && /\d/.test(r.texto) ? FONTE_NUMEROS : FONTE_TITULO) : FONTE_TEXTO,
        fontSize: +(r.tam * PT).toFixed(1),
        color: r.cor || '000000',
        bold: r.negrito,
        italic: r.italico,
        lang: 'pt-BR',
      };
      if (r.sublinhado) op.underline = { style: 'sng' };
      if (r.espaco) op.charSpacing = +(r.espaco * PT).toFixed(2);
      if (parte.sobre) op.superscript = true;
      if (parte.sob) op.subscript = true;
      if (r.link) op.hyperlink = { url: r.link };
      if (quebrarAntes) {
        op.softBreakBefore = true;
        quebrarAntes = false;
      }
      out.push({ text: parte.texto, options: op });
    }
  }
  return out;
}

function resumo(trechos) {
  return trechos.filter((r) => !r.quebra).map((r) => r.texto).join('').slice(0, 40);
}

// Polígono de um retângulo arredondado (convexo), em px relativos à caixa
function poligonoArredondado(w, h, r) {
  const pts = [];
  const cantos = [[w - r, r, -90], [w - r, h - r, 0], [r, h - r, 90], [r, r, 180]];
  for (const [cx, cy, a0] of cantos) {
    for (let k = 0; k <= 8; k++) {
      const a = ((a0 + (90 * k) / 8) * Math.PI) / 180;
      pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
    }
  }
  return pts;
}

// Recorte de polígono convexo por semiplano (Sutherland–Hodgman)
function recortar(pts, dentro, intersecao) {
  const out = [];
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i];
    const b = pts[(i + 1) % pts.length];
    const da = dentro(a);
    const db = dentro(b);
    if (da) out.push(a);
    if (da !== db) out.push(intersecao(a, b));
  }
  return out;
}

function faixaDeBorda(caixa, raio, lado, largura) {
  const { w, h } = caixa;
  const r = Math.min(raio, w / 2, h / 2);
  const poli = r > 0.5 ? poligonoArredondado(w, h, r) : [[0, 0], [w, 0], [w, h], [0, h]];
  const corteY = (lim, menor) => [
    (p) => (menor ? p[1] <= lim : p[1] >= lim),
    (a, b) => [a[0] + ((lim - a[1]) * (b[0] - a[0])) / (b[1] - a[1]), lim],
  ];
  const corteX = (lim, menor) => [
    (p) => (menor ? p[0] <= lim : p[0] >= lim),
    (a, b) => [lim, a[1] + ((lim - a[0]) * (b[1] - a[1])) / (b[0] - a[0])],
  ];
  const corte = { 0: corteY(largura, true), 1: corteX(w - largura, false), 2: corteY(h - largura, false), 3: corteX(largura, true) }[lado];
  return recortar(poli, ...corte);
}

function bordaBase(bordas) {
  const visiveis = bordas.filter((b) => b.w > 0 && b.c);
  if (!visiveis.length) return null;
  const contagem = new Map();
  for (const b of visiveis) {
    const k = `${b.w}|${b.c}`;
    contagem.set(k, (contagem.get(k) || 0) + 1);
  }
  const [k] = [...contagem.entries()].sort((a, b) => b[1] - a[1] || parseFloat(a[0]) - parseFloat(b[0]))[0];
  const [w, c] = k.split('|');
  return { w: parseFloat(w), c };
}

function opcoesForma(pres, caixa, pintura) {
  const raio = Math.min(pintura.raio, caixa.w / 2, caixa.h / 2);
  const base = bordaBase(pintura.bordas);
  const op = {
    x: caixa.x * PX, y: caixa.y * PX, w: caixa.w * PX, h: caixa.h * PX,
    fill: pintura.bg ? { color: pintura.bg } : { type: 'none' },
    line: base ? { color: base.c, width: base.w * PT } : { type: 'none' },
  };
  const forma = raio > 0.5 ? pres.ShapeType.roundRect : pres.ShapeType.rect;
  if (raio > 0.5) op.rectRadius = raio * PX;
  return { forma, op, base };
}

// Bordas mais grossas ou de outra cor (ex.: border-top colorido de um cartão) viram uma faixa
function adicionarFaixas(slide, pres, caixa, pintura, base) {
  pintura.bordas.forEach((b, lado) => {
    if (!(b.w > 0 && b.c)) return;
    if (base && b.w <= base.w && b.c === base.c) return;
    const poli = faixaDeBorda(caixa, pintura.raio, lado, b.w);
    if (poli.length < 3) return;
    const xs = poli.map((p) => p[0]);
    const ys = poli.map((p) => p[1]);
    const x0 = Math.min(...xs);
    const y0 = Math.min(...ys);
    const pontos = poli.map((p, i) => ({ x: (p[0] - x0) * PX, y: (p[1] - y0) * PX, ...(i === 0 ? { moveTo: true } : {}) }));
    pontos.push({ close: true });
    slide.addShape(pres.ShapeType.custGeom, {
      x: (caixa.x + x0) * PX, y: (caixa.y + y0) * PX,
      w: (Math.max(...xs) - x0) * PX, h: (Math.max(...ys) - y0) * PX,
      points: pontos, fill: { color: b.c }, line: { type: 'none' },
      objectName: 'Borda de destaque',
    });
  });
}

function adicionarCaixa(slide, pres, it) {
  const { forma, op, base } = opcoesForma(pres, it.caixa, it.pintura);
  slide.addShape(forma, { ...op, objectName: 'Cartão' });
  adicionarFaixas(slide, pres, it.caixa, it.pintura, base);
}

// Ascendente e descendente (em em) de Georgia e Calibri, para alinhar a linha de base
const METRICAS = { serif: [0.917, 0.219], sans: [0.952, 0.269] };

// O CSS centraliza o glifo na altura da linha; com espaçamento exato o PowerPoint põe a
// linha de base a 80% da altura da linha. Devolve quanto subir (negativo) ou descer a caixa.
function ajusteLinhaDeBase(it) {
  const r = it.trechos.find((t) => !t.quebra);
  if (!r) return 0;
  const [asc, desc] = METRICAS[r.serif ? 'serif' : 'sans'];
  const baseCss = (it.lh - (asc + desc) * r.tam) / 2 + asc * r.tam;
  return baseCss - 0.8 * it.lh;
}

function adicionarTexto(slide, pres, it, opcoesExtra = {}) {
  const trechos = montarTrechos(it.trechos, it.tag);
  if (!trechos.length) return;
  const umaLinha = it.linhas === 1 || it.semQuebra;
  const comum = {
    align: it.alinhamento,
    lineSpacing: +(it.lh * PT).toFixed(2),
    paraSpaceBefore: 0,
    paraSpaceAfter: 0,
    wrap: !umaLinha,
    objectName: resumo(it.trechos),
  };
  if (it.pintura) {
    // Pílula ou bloco pintado: uma forma só, com o texto dentro
    const { forma, op, base } = opcoesForma(pres, it.caixa, it.pintura);
    const [t, r, b, l] = it.recuos;
    // Pílula de uma linha com recuo simétrico: centralizar dá o mesmo resultado e
    // absorve pequenas diferenças de largura de texto entre programas
    const pilula = umaLinha && Math.abs(l - r) < 1 && it.alinhamento === 'left';
    slide.addText(trechos, {
      ...op, ...comum, shape: forma,
      ...(pilula ? { align: 'center' } : {}),
      margin: [l * PT, r * PT, b * PT, t * PT],
      valign: umaLinha ? 'middle' : 'top',
      ...opcoesExtra,
    });
    adicionarFaixas(slide, pres, it.caixa, it.pintura, base);
    return;
  }
  const [t, r, b, l] = it.recuos;
  let x = it.caixa.x + l;
  let w = it.caixa.w - l - r;
  const y = it.caixa.y + t + ajusteLinhaDeBase(it);
  const h = it.caixa.h - t - b;
  // Folga mínima para arredondamentos; mais que isso muda as quebras de linha do original
  const folga = 3;
  if (it.alinhamento === 'center') x -= folga / 2;
  else if (it.alinhamento === 'right') x -= folga;
  w += folga;
  // Item de lista: a caixa começa no marcador e o texto fica recuado, como no navegador
  const marcador = it.marcador ? { bullet: { indent: +(it.marcador * PT).toFixed(1) } } : {};
  if (it.marcador) {
    x -= it.marcador;
    w += it.marcador;
    // Com vários trechos (ex.: "CO₂"), o pptxgenjs repete o pPr em cada trecho; sem o marcador
    // em todos, o último pPr (sem marcador) prevalece
    for (const tr of trechos) tr.options = { ...tr.options, ...marcador };
  }
  slide.addText(trechos, {
    x: x * PX, y: y * PX, w: w * PX, h: h * PX,
    margin: 0, valign: 'top', isTextBox: true, fit: 'none',
    ...comum, ...marcador, ...opcoesExtra,
  });
}

function adicionarTabela(slide, it) {
  const colW = it.linhas[0].celulas.map((c) => c.caixa.w * PX);
  const rowH = it.linhas.map((l) => l.h * PX);
  const linhas = it.linhas.map((l) => l.celulas.map((c) => {
    const margemPt = c.recuos.map((v) => v * PT);
    const margem = margemPt[0] >= 1 ? margemPt : c.recuos.map((v) => v * PX);
    const op = {
      border: c.bordas.map((b) => (b.w > 0 && b.c ? { type: 'solid', pt: b.w * PT, color: b.c } : { type: 'none' })),
      margin: margem,
      align: c.alinhamento,
      valign: c.vertical === 'top' ? 'top' : c.vertical === 'bottom' ? 'bottom' : 'middle',
      lineSpacing: +(c.lh * PT).toFixed(2),
    };
    if (c.fundo) op.fill = { color: c.fundo };
    return { text: montarTrechos(c.trechos), options: op };
  }));
  slide.addTable(linhas, {
    x: it.caixa.x * PX, y: it.caixa.y * PX, w: colW.reduce((a, b) => a + b, 0),
    colW, rowH, autoPage: false, objectName: 'Tabela',
  });
}

const FORMAS = {
  'arrow-right': 'rightArrow', 'arrow-left': 'leftArrow', 'arrow-up': 'upArrow', 'arrow-down': 'downArrow',
  ellipse: 'ellipse', diamond: 'diamond', rect: 'rect', rounded: 'roundRect',
};

function adicionarForma(slide, it) {
  const tipo = FORMAS[it.tipoForma];
  if (!tipo) return;
  slide.addShape(tipo, {
    x: it.caixa.x * PX, y: it.caixa.y * PX, w: it.caixa.w * PX, h: it.caixa.h * PX,
    fill: it.cor ? { color: it.cor } : { type: 'none' }, line: { type: 'none' },
    objectName: 'Seta',
  });
}

// Largura e altura de um PNG ou JPEG, lidas do cabeçalho do arquivo
function tamanhoImagem(arquivo) {
  const b = fs.readFileSync(arquivo);
  if (b.readUInt32BE(0) === 0x89504e47) return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
  for (let i = 2; i < b.length - 9;) {
    const marcador = b.readUInt16BE(i);
    if (marcador >= 0xffc0 && marcador <= 0xffc3) return { w: b.readUInt16BE(i + 7), h: b.readUInt16BE(i + 5) };
    i += 2 + b.readUInt16BE(i + 2);
  }
  return null;
}

// Imagem encaixada na caixa medida, sem distorcer (object-fit: contain)
function adicionarImagem(slide, it, imagens, pastaDeck, idSlide) {
  const rel = imagens[it.src] || it.src;
  const arquivo = rel && path.resolve(pastaDeck, rel.replace(/^\//, ''));
  if (!arquivo || !fs.existsSync(arquivo)) {
    console.warn(`aviso: imagem "${it.src}" de "${idSlide}" sem arquivo local; ficou de fora`);
    return;
  }
  let { x, y, w, h } = it.caixa;
  const t = tamanhoImagem(arquivo);
  if (t) {
    const escala = Math.min(w / t.w, h / t.h);
    x += (w - t.w * escala) / 2;
    y += (h - t.h * escala) / 2;
    w = t.w * escala;
    h = t.h * escala;
  }
  slide.addImage({ path: arquivo, x: x * PX, y: y * PX, w: w * PX, h: h * PX, altText: it.alt, objectName: it.alt || 'Imagem' });
}

// Título = primeiro h1/h2 do slide (ou, sem eles, o primeiro texto); vira o placeholder
// de título do layout, para navegação e leitores de tela
function tituloDe(s) {
  const textos = s.itens.filter((it) => it.tipo === 'texto' && !it.pintura && it.trechos.some((r) => !r.quebra));
  return textos.find((it) => it.tag === 'H1' || it.tag === 'H2') || textos[0] || null;
}

// Um layout por fundo, tag do título e posição do título (um título em outra posição, como o do
// slide de encerramento, ganha layout próprio em vez de herdar a posição da capa)
function chaveLayout(s) {
  const t = tituloDe(s);
  return `${s.fundo}|${t ? `${t.tag}|${Math.round(t.caixa.x)},${Math.round(t.caixa.y)}` : '-'}`;
}

function definirLayouts(pres, slides) {
  const layouts = new Map();
  for (const s of slides) {
    const t = tituloDe(s);
    const chave = chaveLayout(s);
    if (!layouts.has(chave)) {
      const escuro = parseInt(s.fundo.slice(0, 2), 16) < 0x80;
      let nome = t && t.tag === 'H1' ? 'Capa'
        : t && t.tag === 'H2' ? (escuro ? 'Conteúdo escuro' : 'Conteúdo')
          : escuro ? 'Divisor' : 'Livre';
      const usados = [...layouts.values()].filter((l) => l.nome === nome || l.nome.startsWith(nome + ' ')).length;
      if (usados) nome = nome === 'Capa' && usados === 1 ? 'Encerramento' : `${nome} ${usados + 1}`;
      layouts.set(chave, { nome, fundo: s.fundo, titulo: t, slides: [] });
    }
    layouts.get(chave).slides.push(s);
  }
  for (const lay of layouts.values()) {
    const objetos = [];
    if (lay.titulo) {
      const t = lay.titulo;
      for (const s of lay.slides) {
        const ts = tituloDe(s);
        if (Math.abs(ts.caixa.x - t.caixa.x) > 2 || Math.abs(ts.caixa.y - t.caixa.y) > 2) {
          console.warn(`aviso: título de "${s.id}" fora da posição do layout ${lay.nome}`);
        }
      }
      const [rt, , rb] = t.recuos;
      // Altura para até duas linhas, ancorada no topo
      const h = Math.max(...lay.slides.map((s) => {
        const ts = tituloDe(s);
        return ts ? ts.caixa.h - rt - rb : 0;
      }), t.lh * 2);
      objetos.push({
        placeholder: {
          options: {
            name: 'title', type: 'title',
            x: (t.caixa.x + t.recuos[3]) * PX, y: (t.caixa.y + rt + ajusteLinhaDeBase(t)) * PX,
            w: (t.caixa.w - t.recuos[1] - t.recuos[3] + 24) * PX, h: h * PX,
            margin: 0, valign: 'top', align: 'left',
            fontFace: FONTE_TITULO, fontSize: +(t.trechos[0].tam * PT).toFixed(1), color: t.trechos[0].cor,
          },
          text: '',
        },
      });
    }
    pres.defineSlideMaster({ title: lay.nome, background: { color: lay.fundo }, objects: objetos });
  }
  return layouts;
}

async function posProcessar(arquivo) {
  const zip = await JSZip.loadAsync(fs.readFileSync(arquivo));
  const temas = Object.keys(zip.files).filter((f) => /^ppt\/theme\/theme\d+\.xml$/.test(f));
  for (const p of temas) {
    let xml = await zip.file(p).async('string');
    for (const [slot, cor] of Object.entries(TEMA.cores)) {
      xml = xml.replace(new RegExp(`<a:${slot}>[\\s\\S]*?</a:${slot}>`), `<a:${slot}><a:srgbClr val="${cor}"/></a:${slot}>`);
    }
    xml = xml.replace(/<a:clrScheme name="[^"]*"/, `<a:clrScheme name="${TEMA.nome}"`);
    zip.file(p, xml);
  }
  // Título como o PowerPoint grava (<p:ph type="title"/>, idx 0 implícito): o pptxgenjs usa
  // idx="100", que outras ferramentas e leitores de tela não reconhecem como título
  const comPlaceholder = Object.keys(zip.files).filter((f) => /^ppt\/(slides\/slide|slideLayouts\/slideLayout)\d+\.xml$/.test(f));
  for (const p of comPlaceholder) {
    const xml = await zip.file(p).async('string');
    const novo = xml.replace(/<p:ph\s+idx="\d+"\s+type="title"[^>]*\/>/g, '<p:ph type="title"/>');
    if (novo !== xml) zip.file(p, novo);
  }
  // Transição "esmaecer" em todos os slides, como no deck original
  const slidesXml = Object.keys(zip.files).filter((f) => /^ppt\/slides\/slide\d+\.xml$/.test(f));
  for (const p of slidesXml) {
    let xml = await zip.file(p).async('string');
    if (!xml.includes('<p:transition')) {
      xml = xml.includes('</p:clrMapOvr>')
        ? xml.replace('</p:clrMapOvr>', '</p:clrMapOvr><p:transition spd="med"><p:fade/></p:transition>')
        : xml.replace('</p:cSld>', '</p:cSld><p:transition spd="med"><p:fade/></p:transition>');
      zip.file(p, xml);
    }
  }
  // Notas: o pptxgenjs grava o texto inteiro em um parágrafo, com "\r\n" literal no meio;
  // cada linha do guia de fala vira um parágrafo próprio
  const notasXml = Object.keys(zip.files).filter((f) => /^ppt\/notesSlides\/notesSlide\d+\.xml$/.test(f));
  for (const p of notasXml) {
    const xml = await zip.file(p).async('string');
    const novo = xml.replace(/<a:p>(<a:pPr[^>]*\/>)?<a:r>(<a:rPr[^>]*\/>)<a:t>([^<]*(?:\r?\n)[^<]*)<\/a:t><\/a:r>(<a:endParaRPr[^>]*\/>)?<\/a:p>/g,
      (tudo, pPr = '', rPr, texto, fim = '') => texto.split(/\r?\n/).filter(Boolean)
        .map((l) => `<a:p>${pPr}<a:r>${rPr}<a:t>${l}</a:t></a:r>${fim}</a:p>`).join(''));
    if (novo !== xml) zip.file(p, novo);
  }
  fs.writeFileSync(arquivo, await zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' }));
}

async function main() {
  const args = process.argv.slice(2);
  const iPrints = args.indexOf('--prints');
  const pastaPrints = iPrints >= 0 ? args.splice(iPrints, 2)[1] : null;
  const [pastaDeck, saida] = args;
  if (!pastaDeck || !saida) {
    console.error('Uso: node html_para_pptx.js <pasta-do-deck> <saida.pptx> [--prints <pasta>]');
    process.exit(1);
  }
  const deck = JSON.parse(fs.readFileSync(path.join(pastaDeck, 'deck.json'), 'utf8'));
  // reserva.json (opcional): slides que entram no .pptx depois dos principais, ocultos
  // (não aparecem na apresentação; servem para responder perguntas)
  const arqReserva = path.join(pastaDeck, 'reserva.json');
  const reserva = fs.existsSync(arqReserva) ? JSON.parse(fs.readFileSync(arqReserva, 'utf8')) : null;
  const ocultos = new Set(reserva ? reserva.order : []);
  const deckCompleto = reserva ? { ...deck, order: [...deck.order, ...reserva.order] } : deck;
  const slides = await medirDeck(pastaDeck, deckCompleto, pastaPrints);

  const pres = new PptxGenJS();
  pres.layout = 'LAYOUT_WIDE';
  pres.author = 'Bruno Dubois';
  pres.title = deck.title;
  pres.subject = 'Sessão clínica';
  pres.theme = { headFontFace: FONTE_TITULO, bodyFontFace: FONTE_TEXTO };

  // imagens.json (opcional) liga cada src do deck (por exemplo /_blob/<id>) a um arquivo local
  const arqImagens = path.join(pastaDeck, 'imagens.json');
  const imagens = fs.existsSync(arqImagens) ? JSON.parse(fs.readFileSync(arqImagens, 'utf8')) : {};

  const layouts = definirLayouts(pres, slides);
  const inicioSecao = new Map(Object.values(deck.sections || {}).map((s) => [s.start, s.description]));
  if (reserva && reserva.order.length) inicioSecao.set(reserva.order[0], reserva.description || 'Slides ocultos de reserva');
  let secaoAtual = null;

  for (const s of slides) {
    if (inicioSecao.has(s.id)) {
      secaoAtual = inicioSecao.get(s.id);
      pres.addSection({ title: secaoAtual });
    }
    const t = tituloDe(s);
    const lay = layouts.get(chaveLayout(s));
    const slide = pres.addSlide({ masterName: lay.nome, ...(secaoAtual ? { sectionTitle: secaoAtual } : {}) });
    slide.background = { color: s.fundo };
    if (ocultos.has(s.id)) slide.hidden = true;
    for (const it of s.itens) {
      if (it.tipo === 'caixa') adicionarCaixa(slide, pres, it);
      else if (it.tipo === 'tabela') adicionarTabela(slide, it);
      else if (it.tipo === 'forma') adicionarForma(slide, it);
      else if (it.tipo === 'imagem') adicionarImagem(slide, it, imagens, pastaDeck, s.id);
      else if (it.tipo === 'texto') {
        if (it === t && !it.pintura) {
          // Com placeholder, o pptxgenjs só aplica espaçamento de linha vindo dos trechos
          const lineSpacing = +(it.lh * PT).toFixed(2);
          const trechos = montarTrechos(it.trechos, it.tag).map((r) => ({ ...r, options: { ...r.options, lineSpacing } }));
          slide.addText(trechos, { placeholder: 'title', lineSpacing, paraSpaceBefore: 0, paraSpaceAfter: 0 });
        } else {
          adicionarTexto(slide, pres, it);
        }
      }
    }
    if (s.notas) slide.addNotes(s.notas);
  }

  await pres.writeFile({ fileName: saida });
  await posProcessar(saida);
  console.log(`${slides.length} slides (${ocultos.size} ocultos) → ${saida}`);
}

module.exports = { CSS_BASE };

if (require.main === module) {
  main().catch((e) => {
    console.error(e);
    process.exit(1);
  });
}
