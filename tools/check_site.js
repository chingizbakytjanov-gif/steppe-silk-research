// Checks every page before publishing and takes full-page screenshots.
// Usage: node tools/check_site.js <site folder> <screenshot folder>   (needs the playwright package)
// Screenshot folder should be outside the repo: everything in the repo is published.
// Desktop 1440x900, phone 390x844 with reduced motion. Exit code 1 if any check fails.
// Checks: horizontal scroll, text contrast (WCAG AA: 4.5:1, 3:1 for large text), em/en dashes
// and arrows in visible text, broken local links and downloads, console errors,
// characters per line in body text (target 45-75, warning only).
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const http = require('http');

const site = path.resolve(process.argv[2] || '.');
const out = path.resolve(process.argv[3] || path.join(require('os').tmpdir(), 'steppesilk-qa'));
fs.mkdirSync(out, { recursive: true });

const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.pdf': 'application/pdf', '.csv': 'text/csv', '.xml': 'text/xml', '.txt': 'text/plain',
  '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split(/[?#]/)[0]);
  if (p.endsWith('/')) p += 'index.html';
  const f = path.join(site, p);
  if (!f.startsWith(site) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
});

const REDIRECTS = ['companies.html', 'trade.html', 'contact.html'];
const pages = fs.readdirSync(site).filter(f => f.endsWith('.html') && !REDIRECTS.includes(f))
  .concat(fs.readdirSync(path.join(site, 'research')).filter(f => f.endsWith('.html')).map(f => 'research/' + f));

const VIEWS = [
  { name: 'desktop', viewport: { width: 1440, height: 900 }, reducedMotion: 'no-preference' },
  { name: 'phone', viewport: { width: 390, height: 844 }, reducedMotion: 'reduce', isMobile: true, hasTouch: true },
];

// Runs inside the page.
function audit() {
  const rgba = s => { const m = s.match(/[\d.]+/g) || [0, 0, 0, 0]; return m.map(Number).concat(m.length < 4 ? [1] : []).slice(0, 4); };
  const over = (top, bot) => { const a = top[3]; return [0, 1, 2].map(i => top[i] * a + bot[i] * (1 - a)).concat([1]); };
  const lum = c => { const v = c.slice(0, 3).map(x => { x /= 255; return x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4; }); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
  const bgOf = el => {
    const layers = [];
    for (let e = el; e; e = e.parentElement) { const c = rgba(getComputedStyle(e).backgroundColor); if (c[3] > 0) { layers.push(c); if (c[3] >= 1) break; } }
    return layers.reverse().reduce((acc, c) => over(c, acc), [255, 255, 255, 1]);
  };
  const visible = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0; };

  const res = { overflow: document.documentElement.scrollWidth - innerWidth, contrast: [], chars: [], measure: [] };
  const seen = new Set();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n; (n = walker.nextNode());) {
    const t = n.nodeValue.trim(); const el = n.parentElement;
    if (!t || !el || el.closest('svg, script, style, noscript') || !visible(el)) continue;
    const bad = t.match(/[—–←-⇿]/);
    if (bad) res.chars.push(`"${bad[0]}" in: ${t.slice(0, 80)}`);
    if (seen.has(el)) continue; seen.add(el);
    const s = getComputedStyle(el); const size = parseFloat(s.fontSize); const bold = +s.fontWeight >= 700;
    const fg = over(rgba(s.color), bgOf(el)); const r = ratio(fg, bgOf(el));
    const need = size >= 24 || (bold && size >= 18.66) ? 3 : 4.5;
    if (r < need) res.contrast.push(`${r.toFixed(2)} < ${need}: ${el.tagName.toLowerCase()}.${el.className} "${t.slice(0, 50)}"`);
  }
  // Characters per line: long paragraphs only, lines counted from the text's line boxes.
  for (const p of document.querySelectorAll('main p, main li, main blockquote')) {
    const t = p.innerText.trim(); if (t.length < 250 || !visible(p)) continue;
    const range = document.createRange(); range.selectNodeContents(p);
    const tops = new Set([...range.getClientRects()].map(r => Math.round(r.top)));
    const lines = tops.size; if (lines < 3) continue;
    res.measure.push(Math.round(t.length / lines));
  }
  res.links = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'));
  return res;
}

(async () => {
  await new Promise(r => server.listen(0, r));
  const base = `http://localhost:${server.address().port}/`;
  const browser = await chromium.launch();
  const fails = []; const warns = []; const links = new Set(); const measures = {};
  for (const v of VIEWS) {
    const ctx = await browser.newContext({ viewport: v.viewport, reducedMotion: v.reducedMotion, isMobile: !!v.isMobile, hasTouch: !!v.hasTouch, deviceScaleFactor: 1 });
    for (const pg of pages) {
      const page = await ctx.newPage(); const errs = [];
      page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
      page.on('pageerror', e => errs.push(e.message));
      await page.goto(base + pg, { waitUntil: 'networkidle' });
      await page.evaluate(() => document.fonts.ready);
      const r = await page.evaluate(audit);
      const tag = `[${v.name}] ${pg}`;
      if (r.overflow > 0) fails.push(`${tag}: page scrolls sideways by ${r.overflow}px`);
      r.contrast.forEach(c => fails.push(`${tag}: contrast ${c}`));
      if (v.name === 'desktop') r.chars.forEach(c => fails.push(`${pg}: banned character ${c}`));
      errs.filter(e => !/fonts\.(googleapis|gstatic)/.test(e)).forEach(e => fails.push(`${tag}: console error ${e}`));
      if (r.measure.length) {
        const max = Math.max(...r.measure); const avg = Math.round(r.measure.reduce((a, b) => a + b) / r.measure.length);
        measures[tag] = `${avg} avg, ${max} max chars/line`;
        if (v.name === 'desktop' && max > 75) warns.push(`${tag}: up to ${max} characters per line (target 45-75)`);
      }
      r.links.forEach(h => links.add(new URL(h, base + pg).href));
      await page.screenshot({ path: path.join(out, `${v.name}-${pg.replace(/\//g, '_').replace('.html', '')}.png`), fullPage: true });
      await page.close();
    }
    await ctx.close();
  }
  for (const href of links) {
    if (!href.startsWith(base)) continue;
    const code = await new Promise(r => http.get(href, res => { res.resume(); r(res.statusCode); }).on('error', () => r(0)));
    if (code !== 200) fails.push(`broken link ${href.replace(base, '/')} (${code})`);
  }
  await browser.close(); server.close();
  console.log(`Checked ${pages.length} pages x ${VIEWS.length} views. Screenshots: ${out}`);
  Object.entries(measures).forEach(([k, m]) => console.log(`  ${k}: ${m}`));
  warns.forEach(w => console.log('WARN ' + w));
  fails.forEach(f => console.log('FAIL ' + f));
  console.log(fails.length ? `${fails.length} problem(s)` : 'All checks passed');
  process.exit(fails.length ? 1 : 0);
})();
