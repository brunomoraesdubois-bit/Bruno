// Renderiza figura.svg em PNG (2x) com a Source Sans 3
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const dir = path.dirname(require.resolve('@fontsource/source-sans-3/package.json'));
  const css = [600, 700].map((p) => `<link rel="stylesheet" href="file://${dir}/${p}.css">`).join('');
  const svg = fs.readFileSync(process.argv[2], 'utf8');
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1664, height: 520 }, deviceScaleFactor: 2 });
  const html = path.join(path.dirname(process.argv[3]), 'figura.html');
  fs.writeFileSync(html, `<!doctype html><html><head><meta charset="utf-8">${css}<style>body{margin:0;background:#f5f3ee}</style></head><body>${svg}</body></html>`);
  await pg.goto('file://' + html);
  await pg.evaluate(async () => { await Promise.all(['600 22px "Source Sans 3"', '700 22px "Source Sans 3"'].map((f) => document.fonts.load(f))); await document.fonts.ready; });
  await pg.waitForTimeout(300);
  await pg.locator('svg').screenshot({ path: process.argv[3], omitBackground: true });
  await b.close();
})();
