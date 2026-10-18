#!/usr/bin/env node
// Confere se cada slide cabe no quadro de 1920×1080 com as fontes do deck no Claude
// (Inter e Source Serif 4): conteúdo dentro da margem inferior, rodapé sem sobreposição,
// títulos em uma linha e nenhuma palavra estourando a caixa.
//
// Uso: node verificar_layout.js <pasta-do-deck>
'use strict';

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { CSS_BASE } = require('./html_para_pptx');

function linksFontes() {
  const css = [];
  for (const [pacote, pesos] of [['@fontsource/inter', [400, 500, 600, 700]], ['@fontsource/source-serif-4', [400, 500, 600, 700]]]) {
    const dir = path.dirname(require.resolve(`${pacote}/package.json`));
    for (const p of pesos) css.push(`<link rel="stylesheet" href="file://${path.join(dir, `${p}.css`)}">`);
  }
  return css.join('');
}

function problemasDoSlide() {
  const sec = document.querySelector('section');
  const cs = getComputedStyle(sec);
  const limite = 1080 - parseFloat(cs.paddingBottom);
  const problemas = [];
  let fundo = 0;
  const fixos = [];
  for (const ch of sec.children) {
    if (ch.tagName === 'ASIDE') continue;
    if (getComputedStyle(ch).position === 'absolute') fixos.push(ch);
    else fundo = Math.max(fundo, ch.getBoundingClientRect().bottom);
  }
  if (fundo > limite + 1) problemas.push(`conteúdo termina em ${Math.round(fundo)} px, limite ${limite}`);
  for (const f of fixos) {
    const r = f.getBoundingClientRect();
    if (r.top < fundo) problemas.push(`rodapé sobreposto ao conteúdo (${Math.round(r.top)} < ${Math.round(fundo)})`);
    if (r.bottom > 1080) problemas.push('rodapé passa da borda do slide');
  }
  for (const el of sec.querySelectorAll('h1, h2')) {
    const lh = parseFloat(getComputedStyle(el).lineHeight);
    const linhas = Math.round(el.getBoundingClientRect().height / lh);
    if (linhas > 1) problemas.push(`título em ${linhas} linhas: "${el.textContent.slice(0, 50)}"`);
  }
  for (const el of sec.querySelectorAll('p, h1, h2, h3, td, th')) {
    if (el.closest('aside')) continue;
    if (el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).whiteSpace !== 'nowrap') {
      problemas.push(`texto mais largo que a caixa: "${el.textContent.slice(0, 50)}"`);
    }
    const r = el.getBoundingClientRect();
    if (r.right > 1920 || r.bottom > 1080) problemas.push(`fora do slide: "${el.textContent.slice(0, 50)}"`);
  }
  return { fundo: Math.round(fundo), limite, problemas };
}

async function main() {
  const pastaDeck = process.argv[2];
  if (!pastaDeck) {
    console.error('Uso: node verificar_layout.js <pasta-do-deck>');
    process.exit(1);
  }
  const deck = JSON.parse(fs.readFileSync(path.join(pastaDeck, 'deck.json'), 'utf8'));
  const harness = path.join(require('os').tmpdir(), `verificar-${process.pid}.html`);
  fs.writeFileSync(harness, `<!doctype html><html><head><meta charset="utf-8">${linksFontes()}<style>${CSS_BASE}</style></head><body></body></html>`);
  const navegador = await chromium.launch();
  const pagina = await navegador.newPage({ viewport: { width: 1920, height: 1080 } });
  await pagina.goto('file://' + harness);
  let total = 0;
  for (const id of deck.order) {
    const html = fs.readFileSync(path.join(pastaDeck, 'slides', `${id}.html`), 'utf8');
    await pagina.evaluate(async (h) => {
      document.body.innerHTML = h;
      void document.body.offsetHeight;
      await document.fonts.ready;
    }, html);
    const { fundo, limite, problemas } = await pagina.evaluate(problemasDoSlide);
    total += problemas.length;
    console.log(`${problemas.length ? '✗' : '✓'} ${id.padEnd(14)} conteúdo até ${fundo}/${limite} px`);
    for (const p of problemas) console.log(`    ${p}`);
  }
  await navegador.close();
  fs.unlinkSync(harness);
  process.exit(total ? 1 : 0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
