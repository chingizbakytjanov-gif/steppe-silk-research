// Prints tools/pdf/*.html (written by build_site.py) to reports/*.pdf on A4 with page numbers.
// Usage: node tools/render_pdf.js <site folder>   (needs the playwright package)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const out = process.argv[2] || process.cwd();
  const src = path.join(__dirname, 'pdf');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const f of fs.readdirSync(src).filter(f => f.endsWith('.html'))) {
    await page.goto('file://' + path.join(src, f));
    const file = path.join(out, 'reports', f.replace('.html', '.pdf'));
    await page.pdf({ path: file, format: 'A4', preferCSSPageSize: true, printBackground: true, displayHeaderFooter: true,
      headerTemplate: '<span></span>',
      footerTemplate: '<div style="width:100%;text-align:center;font-family:Liberation Serif,serif;font-size:9px;color:#444"><span class="pageNumber"></span></div>' });
    console.log('reports/' + f.replace('.html', '.pdf'));
  }
  await browser.close();
})();
