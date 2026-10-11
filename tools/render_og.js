// Renders the link-preview cards (tools/og/*.html, written by build_site.py) to og/*.png at 1200x630.
// Usage: node tools/render_og.js <site folder>   (needs the playwright package)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const out = process.argv[2] || process.cwd();
  const src = path.join(__dirname, 'og');
  fs.mkdirSync(path.join(out, 'og'), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  for (const f of fs.readdirSync(src).filter(f => f.endsWith('.html'))) {
    await page.goto('file://' + path.join(src, f));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(out, 'og', f.replace('.html', '.png')) });
    console.log('og/' + f.replace('.html', '.png'));
  }
  await browser.close();
})();
