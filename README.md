# Steppe & Silk Research

Independent student research on companies and trade in Kazakhstan, Central Asia and China, by Chingiz Bakytzhanov.

The site is plain static HTML and CSS, deployed on Vercel. Report PDFs live in `reports/`.

`tools/build_site.py` regenerates the HTML pages and copies `tools/style.css` and `tools/site.js` into `assets/` (run `python3 tools/build_site.py "$PWD"`). Adding a new report means adding its entry there, placing the PDF in `reports/`, and rebuilding.
