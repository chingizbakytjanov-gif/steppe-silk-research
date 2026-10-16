#!/usr/bin/env python3
"""Generate the static Steppe & Silk Research site into the given folder.

Run:  python3 tools/build_site.py "$PWD"
Then: node tools/render_og.js "$PWD"   (redraws the link-preview images in og/)
"""
import csv, json, os, sys
from html import escape

OUT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://steppesilk.com"
AUTHOR = "Chingiz Bakytzhanov"
EMAIL = "chingiz.bakytjanov@gmail.com"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500'
         '&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400'
         '&display=swap" rel="stylesheet">')

INK, GREY, ACCENT, MUTED = "#14202e", "#cfc6b8", "#0b6e79", "#6f7884"
CHART_FONT = "IBM Plex Sans,Arial"

NAV = [("research.html", "Research"), ("data.html", "Data"), ("about.html", "About")]

FAVICON = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<rect width="32" height="32" fill="{INK}"/><rect x="6" y="18" width="5" height="8" fill="#fff"/>
<rect x="13.5" y="12" width="5" height="14" fill="#fff"/><rect x="21" y="6" width="5" height="20" fill="{ACCENT}"/></svg>'''


def write(path, text):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    with open(full, "w") as f:
        f.write(text)


def page(path, title, body, active, desc, og="og/home.png", kind="website", ld=None):
    pre = "../" * path.count("/")
    url = SITE + "/" + ("" if path == "index.html" else path)
    nav = "".join(f'<a href="{pre}{h}"{" class=\"active\"" if h == active else ""}>{n}</a>' for h, n in NAV)
    foot_nav = "".join(f'<a href="{pre}{h}">{n}</a>' for h, n in NAV)
    ld_tag = f'<script type="application/ld+json">{json.dumps(ld)}</script>\n' if ld else ""
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="d7XHlEAizrVEeJg0uOvRMYoe6iXHknmiZpDfU_INxrk">
<meta name="google-site-verification" content="rOkVrHh45H8W7YMARKQRI90o3m_RzjbPe74PImvKOU8">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="Steppe &amp; Silk Research">
<meta property="og:type" content="{kind}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:image" content="{SITE}/{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}/{og}">
{ld_tag}{FONTS}
<link rel="stylesheet" href="{pre}assets/style.css">
<link rel="icon" href="{pre}assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{pre}assets/apple-touch-icon.png">
<script src="{pre}assets/site.js" defer></script>
</head>
<body>
<div id="progress"></div>
<header class="site-header"><div class="wrap">
<a class="brand" href="{pre}index.html">Steppe &amp; Silk Research</a>
<nav class="nav">{nav}</nav>
</div></header>
<main>
{body}
</main>
<footer class="site-footer"><div class="wrap">
<div class="foot-main"><div class="foot-brand">Steppe &amp; Silk Research</div>
<p>Reports on Kazakh companies and on Kazakhstan's trade with China. Not investment advice.</p></div>
<div class="foot-links"><nav>{foot_nav}</nav><a href="mailto:{EMAIL}">{EMAIL}</a><span><a href="{pre}terms.html">Terms</a> &middot; <a href="{pre}privacy.html">Privacy</a> &middot; &copy; 2026 {AUTHOR}</span></div>
</div></footer>
</body>
</html>
'''
    write(path, html)


def redirect(path, target):
    write(path, f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={target}">'
                f'<link rel="canonical" href="{target}"><a href="{target}">Moved</a>\n')


# ---------- Charts ----------

def columns(series, labels, w=480, h=250, fmt="{:.1f}", unit="", top=None, hi=None, desc=""):
    """Column chart. series = [(name, colour, values)]; one series highlights column `hi` in the accent colour."""
    n, k = len(labels), len(series)
    top = top or max(max(v) for _, _, v in series) * 1.15
    legend = k > 1
    pad_b, pad_t = 28, 46 if legend else 24
    gw = w / n
    bw = gw * (0.56 if k == 1 else 0.68) / k
    out = [f'<svg class="chart" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(desc)}">']
    if legend:
        x = 0
        for name, col, _ in series:
            out.append(f'<rect x="{x}" y="4" width="12" height="12" fill="{col}"/>'
                       f'<text x="{x+18}" y="15" font-size="14" font-family="{CHART_FONT}" fill="#444">{name}</text>')
            x += 18 + len(name) * 7.6 + 24
    out.append(f'<line x1="0" y1="{h-pad_b}" x2="{w}" y2="{h-pad_b}" stroke="{INK}"/>')
    for i, lab in enumerate(labels):
        cx = i * gw + gw / 2
        x0 = cx - bw * k / 2 - (k - 1)
        for j, (_, col, vals) in enumerate(series):
            v = vals[i]
            bh = (h - pad_b - pad_t) * v / top
            x = x0 + j * (bw + 2)
            y = h - pad_b - bh
            c = ACCENT if (k == 1 and i == hi) else col
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{c}"/>')
            fs = 14 if k == 1 else 12
            out.append(f'<text x="{x+bw/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-size="{fs}" '
                       f'font-family="{CHART_FONT}" fill="{INK}" font-weight="500">{fmt.format(v)}{unit}</text>')
        out.append(f'<text x="{cx:.1f}" y="{h-8}" text-anchor="middle" font-size="13" font-family="{CHART_FONT}" fill="{MUTED}">{lab}</text>')
    out.append('</svg>')
    return "".join(out)


def hbars(rows, unit="", colour=GREY, fmt="{:.2f}"):
    """Horizontal bars in HTML, so long labels stay readable on phones."""
    top = max(v for _, v in rows)
    items = "".join(
        f'<div class="hbar"><div class="hbar-label">{lab}</div>'
        f'<div class="hbar-track"><span style="width:{v/top*100:.1f}%;background:{colour}"></span></div>'
        f'<div class="hbar-val">{fmt.format(v)}{unit}</div></div>' for lab, v in rows)
    return f'<div class="hbars">{items}</div>'


def table(head, rows, num_from=1, cls=""):
    th = "".join(f'<th{" class=\"num\"" if i >= num_from else ""}>{h}</th>' for i, h in enumerate(head))
    trs = ""
    for r in rows:
        strong = r[0].startswith("**")
        cells = []
        for i, c in enumerate(r):
            c = str(c).replace("**", "")
            cells.append(f'<td{" class=\"num\"" if i >= num_from else ""}>{c}</td>')
        trs += f'<tr{" class=\"total\"" if strong else ""}>{"".join(cells)}</tr>'
    return f'<div class="table-wrap"><table class="data-table {cls}"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


# ---------- Data ----------

YEARS = ["2020", "2021", "2022", "2023", "2024", "2025"]
EXPORTS = [9.0, 9.9, 13.2, 14.7, 14.9, 15.2]
IMPORTS = [6.4, 8.3, 11.0, 16.8, 15.2, 18.9]
TURNOVER = [15.4, 18.2, 24.2, 31.5, 30.1, 34.1]
BALANCE = [2.6, 1.6, 2.2, -2.1, -0.3, -3.7]
CN_IMPORTS_FROM_KZ = [9.74, 11.27, 14.82, 16.32, 15.86, 18.98]
CN_EXPORTS_TO_KZ = [11.71, 13.98, 16.17, 24.70, 27.96, 29.70]
CN_TURNOVER = [21.5, 25.2, 31.0, 41.0, 43.8, 48.7]
TOP_EXPORTS = [("Ores, slag and ash", 3.94), ("Oil and mineral fuels", 3.28), ("Copper", 2.69),
               ("Inorganic chemicals (incl. uranium)", 1.78), ("Iron and steel", 1.10)]
TOP_IMPORTS = [("Machinery and equipment", 3.70), ("Electrical and electronic equipment", 2.39), ("Vehicles", 2.31),
               ("Clothing (not knitted)", 0.61), ("Articles of iron or steel", 0.58)]

K_YEARS = ["2023", "2024", "2025"]
K_PAY = [478684, 587097, 658726]
K_MKT = [448223, 732943, 1931472]
K_FIN = [1026721, 1281827, 1542934]
K_REV = [1913490, 2532156, 4046074]
K_NI = [848770, 1056834, 1067707]
K_MARGIN = [44.4, 41.7, 26.4]
K_MKT_SHARE = [22.9, 28.3, 47.1]


def n0(v):
    return f"{v:,.0f}"


# Sources: every name links to the page the number came from.
SRC_KASPI = [
    ("Kaspi.kz JSC, Annual Report on Form 20-F for the fiscal year ended 31 December 2025 (U.S. SEC filing)",
     "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=kaspi&type=20-F"),
    ("Kaspi.kz investor relations", "https://ir.kaspi.kz"),
]
SRC_TRADE = [
    ("Embassy of Kazakhstan in China, Trade and economic cooperation (2024 data, SRC and GACC)",
     "https://www.gov.kz/memleket/entities/mfa-beijing/activities/2110?lang=en"),
    ("Association of Financiers of Kazakhstan, Kazakhstan-China commodity turnover, March 2026 (BNS data)",
     "https://afk.kz/2026/03/Kazakhstan-China-Commodity-Turnover-March2026.pdf"),
    ("Kazinform, Trade between Kazakhstan and China exceeded $31 billion in 2023",
     "https://www.inform.kz/ru/tovarooborot-mezhdu-kazahstanom-i-kitaem-v-2023-godu-previsil-31-mlrd-d0a0bc"),
    ("The Astana Times, Trade between China and Central Asian states reached $32.1 billion in 2022 (April 2023)",
     "https://astanatimes.com/2023/04/trade-between-china-central-asian-states-reach-32-1-billion-in-2022/"),
    ("Kapital.kz, Kazakhstan's foreign trade and trade with China in 2021",
     "https://kapital.kz/economic/104880/kak-razvivayut-sya-torgovyye-otnosheniya-kazakhstana-i-kitaya.html"),
    ("Inbusiness.kz, Trade growth, exports and the opening of the Chinese market for Kazakhstan",
     "https://inbusiness.kz/ru/news/rost-torgovli-eksport-i-otkrytie-kitajskogo-rynka-dlya-kazahstana-chto-govoryat-cifry"),
    ("PwC China, Invest in Kazakhstan (April 2026), citing the General Administration of Customs of China",
     "https://www.pwccn.com/zh/issues-based/invest-in-kazakhstan-apr2026.pdf"),
    ("Trading Economics, Kazakhstan exports to China and imports from China (UN Comtrade)",
     "https://tradingeconomics.com/kazakhstan/exports/china"),
]


def src_link(i, srcs, pre="../"):
    name, url = srcs[i][:2]
    short = srcs[i][2] if len(srcs[i]) > 2 else name.split(",")[0]
    return f'<a href="{url}" rel="noopener">{short}</a>'


KASPI = dict(
    slug="kaspi-hepsiburada",
    url="research/kaspi-hepsiburada.html",
    tag="Companies",
    kind="Company note",
    title="Bigger but Less Profitable: Kaspi.kz after the Hepsiburada Acquisition",
    date="8 Oct 2026", date_long="8 October 2026", iso="2026-10-08",
    line="Revenue grew 60% in 2025, but net income grew only 1%.",
    summary=("In January 2025 Kaspi.kz bought a controlling stake in Hepsiburada, a leading Turkish online "
             "marketplace. The deal lifted revenue by 60% in 2025 but left net income almost flat, cutting the "
             "net margin from 41.7% to 26.4%. The Kazakh business stayed highly profitable; the fall comes from Turkey."),
    art=columns([("Net margin", GREY, K_MARGIN)], K_YEARS, w=300, h=150, hi=2, unit="%", top=55,
                desc="Kaspi.kz net margin: 44.4% in 2023, 41.7% in 2024, 26.4% in 2025"),
    art_title="Net margin, %",
    pdf="reports/kaspi-hepsiburada-2026.pdf", pages=2,
    data="data/kaspi-financials-2023-2025",
    og_num="26.4%", og_cap="net margin in 2025, down from 41.7%",
    og_chart=columns([("Net margin", GREY, K_MARGIN)], K_YEARS, w=420, h=260, hi=2, unit="%", top=55),
)
TRADE = dict(
    slug="kazakhstan-china-trade",
    url="research/kazakhstan-china-trade.html",
    tag="Trade",
    kind="Trade brief",
    title="Raw Materials Out, Machines In: Kazakhstan's Trade with China, 2020-2025",
    date="8 Oct 2026", date_long="8 October 2026", iso="2026-10-08",
    line="Trade more than doubled in five years, and a surplus turned into a $3.7 billion deficit.",
    summary=("Trade between Kazakhstan and China more than doubled, from $15.4 billion to $34.1 billion. Kazakhstan "
             "still sells mostly raw materials and buys machinery, electronics and vehicles. Since 2023 it has run a "
             "trade deficit with China, which reached $3.7 billion in 2025."),
    art=columns([("Turnover", GREY, TURNOVER)], YEARS, w=300, h=150, hi=5, top=40, fmt="{:.0f}",
                desc="Kazakhstan-China trade turnover, $ billion, 2020 to 2025: 15, 18, 24, 32, 30, 34"),
    art_title="Trade turnover, $ bn",
    pdf="reports/kazakhstan-china-trade-2026.pdf", pages=3,
    data="data/kazakhstan-china-trade-2020-2025",
    og_num="−$3.7 bn", og_cap="Kazakhstan's trade balance with China in 2025",
    og_chart=columns([("Exports", GREY, EXPORTS), ("Imports", ACCENT, IMPORTS)], YEARS, w=420, h=260, top=22),
)
REPORTS = [TRADE, KASPI]  # newest first; the first one is featured on the home page


def pdf_link(r, pre=""):
    if not r.get("pdf"):
        return ""
    return f'<a class="pdf-link" href="{pre}{r["pdf"]}" download>PDF <span>{r["pages"]} pp.</span></a>'


def row(r, pre=""):
    return f'''<div class="row" data-type="{r["tag"].lower()}">
<div class="row-date"><time datetime="{r["iso"]}">{r["date"]}</time></div>
<div class="row-main"><div class="label">{r["kind"]}</div><h3><a class="row-link" href="{pre}{r["url"]}">{r["title"]}</a></h3><p>{r["line"]}</p>
<div class="row-actions"><a href="{pre}{r["url"]}">Read</a>{pdf_link(r, pre)}<a class="pdf-link" href="{pre}{r["data"]}.xlsx" download>Data <span>XLSX</span></a></div></div>
<div class="row-art"><div class="art-title">{r["art_title"]}</div>{r["art"]}</div></div>'''


# ---------- Data files (CSV + XLSX) ----------

def data_files(base, title, source_note, sheets):
    """sheets = [(sheet name, header, rows)]. CSV holds the first sheet; XLSX holds all of them plus notes."""
    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
    name, head, rows = sheets[0]
    with open(os.path.join(OUT, base + ".csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(head)
        w.writerows(rows)
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font
    except ImportError:
        print("openpyxl missing: XLSX not rebuilt")
        return
    wb = Workbook()
    info = wb.active
    info.title = "About"
    for line in [title, "", "Steppe & Silk Research, " + SITE, f"Author: {AUTHOR}", ""] + source_note + [
            "", "Free to reuse with attribution: " + AUTHOR + ", Steppe & Silk Research (2026)."]:
        info.append([line])
    info["A1"].font = Font(bold=True, size=13)
    info.column_dimensions["A"].width = 110
    for sname, shead, srows in sheets:
        ws = wb.create_sheet(sname)
        ws.append(shead)
        for c in ws[1]:
            c.font = Font(bold=True)
        for r in srows:
            ws.append(r)
        ws.column_dimensions["A"].width = 44
        for col in "BCDEFGH":
            ws.column_dimensions[col].width = 13
    wb.save(os.path.join(OUT, base + ".xlsx"))


data_files(KASPI["data"], "Kaspi.kz key financials, 2023-2025 (₸ million unless stated)",
           ["Source: Kaspi.kz Form 20-F for 2025, segment and earnings notes (pp. F-33 to F-42).",
            "Segment revenue is before inter-segment eliminations and customer rewards, so segments do not add up exactly to total revenue.",
            "Growth rates, margins and shares are calculated from these figures."],
           [("Financials", ["Indicator", "2023", "2024", "2025"],
             [["Payments revenue", *K_PAY], ["Marketplace revenue", *K_MKT], ["Fintech revenue", *K_FIN],
              ["Total revenue", *K_REV], ["Net income", *K_NI],
              ["Net margin, %", *K_MARGIN], ["Marketplace share of segment revenue, %", *K_MKT_SHARE]]),
            ("Turkey 2025", ["2025, ₸ million", "Segment revenue", "Net income"],
             [["Turkey (Hepsiburada)", 1031592, -93018], ["Kazakhstan and other markets", 3070369, 1160725]])])

data_files(TRADE["data"], "Kazakhstan's goods trade with China, 2020-2025 ($ billion)",
           ["Kazakh data: Bureau of National Statistics, Ministry of Trade and Integration, State Revenue Committee, as published by government bodies and national media.",
            "2020-2021 figures come from news reports citing official bodies and are less reliable than later years.",
            "2022 turnover is the sum of exports and imports. The 2023 import figure is an early estimate, later revised to about $15.4 billion.",
            "Chinese data: General Administration of Customs of China (GACC). The two series differ and should not be mixed.",
            "Product groups: Kazakhstan's data reported to UN Comtrade, via Trading Economics."],
           [("Kazakh data", ["Indicator"] + YEARS,
             [["Exports to China", *EXPORTS], ["Imports from China", *IMPORTS],
              ["Total trade", *TURNOVER], ["Balance", *BALANCE]]),
            ("Chinese data", ["Indicator"] + YEARS,
             [["China's imports from Kazakhstan", *CN_IMPORTS_FROM_KZ], ["China's exports to Kazakhstan", *CN_EXPORTS_TO_KZ],
              ["Total trade (Chinese data)", *CN_TURNOVER]]),
            ("Top products 2024", ["Flow", "Product group", "$ billion"],
             [["Export to China", a, b] for a, b in TOP_EXPORTS] + [["Import from China", a, b] for a, b in TOP_IMPORTS])])


# ---------- Report pages ----------

def report(r, sections, facts, sources, disclaimer=False):
    pre = "../"
    kv = "".join(f'<div class="fact"><div class="fact-num">{v}</div><div class="fact-label">{k}</div></div>' for k, v in facts)
    srcs = "".join(f'<li><a href="{u}" rel="noopener">{escape(n)}</a></li>' for n, u, *_ in sources)
    cite = (f'{AUTHOR} (2026). <i>{r["title"]}</i>. Steppe &amp; Silk Research, {r["date_long"]}. '
            f'{SITE}/{r["url"]}')
    full = (f'<a href="{pre}{r["pdf"]}" download>Full report <span>PDF, {r["pages"]} pp.</span></a>' if r.get("pdf") else "")
    dl = (f'<div class="downloads">{full}'
          f'<a href="{pre}{r["data"]}.xlsx" download>Data <span>XLSX</span></a>'
          f'<a href="{pre}{r["data"]}.csv" download>Data <span>CSV</span></a></div>')
    warn = ('<p class="disclaimer">This note is independent research for information and learning. '
            'It is not investment advice or a recommendation to buy or sell any security.</p>') if disclaimer else ""
    body = f'''<article class="report"><div class="wrap">
<header class="report-head">
<div class="label"><a href="{pre}research.html#{r["tag"].lower()}">{r["kind"]}</a></div>
<h1>{r["title"]}</h1>
<p class="dek">{r["line"]}</p>
<div class="byline">By <a href="{pre}about.html">{AUTHOR}</a> &middot; Published <time datetime="{r["iso"]}">{r["date_long"]}</time></div>
{dl}
</header>
<div class="facts">{kv}</div>
<div class="report-body">
<h2>Summary</h2><p>{r["summary"]}</p>
{sections}
{warn}
<h2>Notes and method</h2>{r["notes"]}
<h2>Sources</h2><ol class="sources">{srcs}</ol>
<h2>Download</h2>{dl}
<div class="cite"><div class="label">How to cite</div><p>{cite}</p></div>
<p class="corrections">Found an error? Email <a href="mailto:{EMAIL}">{EMAIL}</a>. Corrections are listed here with their date.</p>
</div>
</div></article>'''
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": r["title"],
          "datePublished": r["iso"], "author": {"@type": "Person", "name": AUTHOR},
          "publisher": {"@type": "Organization", "name": "Steppe & Silk Research"},
          "image": f"{SITE}/og/{r['slug']}.png", "description": r["summary"]}
    page(r["url"], r["title"] + " · Steppe & Silk Research", body, "research.html",
         r["line"], og=f"og/{r['slug']}.png", kind="article", ld=ld)


def fig(n, title, chart, source_html, data_base):
    return (f'<figure class="figure"><div class="fig-title">Figure {n}. {title}</div>{chart}'
            f'<figcaption>Source: {source_html}. <a href="../{data_base}.csv" download>Download the data (CSV)</a></figcaption></figure>')


kaspi_notes = '''<ul class="notes">
<li>All figures come from Kaspi.kz's annual report on Form 20-F for 2025 (segment and earnings notes, pp. F-33 to F-42).</li>
<li>Segment revenue is shown before inter-segment eliminations and customer rewards, so the three segments do not add up exactly to total revenue.</li>
<li>Growth rates, net margin (net income divided by revenue) and segment shares are calculated by the author from the reported figures.</li>
<li>2025 is the first year that includes Hepsiburada, consolidated from 29 January 2025.</li>
</ul>'''
KASPI["notes"] = kaspi_notes

kaspi_sections = f'''<h2>Key findings</h2><ol>
<li>Revenue grew by 60% in 2025 after Hepsiburada was consolidated, up from 32% growth in 2024.</li>
<li>Net income rose by only 1%, so the net margin fell from 41.7% to 26.4%.</li>
<li>The Marketplace segment grew from 22.9% to 47.1% of segment revenue, mostly because of Turkey.</li>
<li>Kaspi bought 65.4% of Hepsiburada for about $1.13 billion and raised its stake to 85% by January 2026.</li></ol>
{fig(1, "Revenue and net income, ₸ trillion",
     columns([("Revenue", GREY, [v/1e6 for v in K_REV]), ("Net income", ACCENT, [v/1e6 for v in K_NI])], K_YEARS,
             top=4.8, fmt="{:.2f}", desc="Kaspi.kz revenue rose from 1.91 to 4.05 trillion tenge while net income went from 0.85 to 1.07 trillion"),
     src_link(0, SRC_KASPI), KASPI["data"])}
<h2>What changed in 2025</h2>
<p>On 29 January 2025 Kaspi bought 65.4% of Hepsiburada for about $1.13 billion. It raised its stake to 76% in December 2025 and signed an agreement in January 2026 that took it to 85%.</p>
<p>The acquisition explains almost all of the change. In 2025 the Turkish business added ₸1.03 trillion of segment revenue but made a net loss of ₸93 billion. Kazakhstan and Kaspi's other markets earned ₸1.16 trillion of net income on ₸3.07 trillion of segment revenue.</p>
{fig(2, "Net margin, %", columns([("Net margin", GREY, K_MARGIN)], K_YEARS, hi=2, unit="%", top=55,
                                  desc="Net margin 44.4% in 2023, 41.7% in 2024, 26.4% in 2025"),
     src_link(0, SRC_KASPI) + "; margin calculated by the author", KASPI["data"])}
<div class="table-title">Table 1. Kaspi.kz key financials, ₸ million</div>
{table(["", *K_YEARS],
       [["Payments", *map(n0, K_PAY)], ["Marketplace", *map(n0, K_MKT)], ["Fintech", *map(n0, K_FIN)],
        ["**Total revenue", *map(n0, K_REV)], ["**Net income", *map(n0, K_NI)],
        ["Revenue growth", "n/a", "+32.3%", "+59.8%"], ["Net income growth", "n/a", "+24.5%", "+1.0%"],
        ["Net margin", *[f"{v}%" for v in K_MARGIN]], ["Marketplace share of segment revenue", *[f"{v}%" for v in K_MKT_SHARE]]])}
<p class="table-note">Segment revenue is before inter-segment eliminations and customer rewards. Source: {src_link(0, SRC_KASPI)}.</p>
<h2>Risks</h2><ol>
<li>Hepsiburada still loses money. The key test for 2026 is whether these losses shrink.</li>
<li>Turkey has high inflation and a weak lira, and the deal was paid in U.S. dollars, which raises Kaspi's exchange-rate risk.</li>
<li>Integration may be difficult: Kaspi warns that its international expansion may fail, and before the deal Hepsiburada had reported weaknesses in its internal financial controls.</li></ol>
<h2>My view</h2><blockquote class="view">I don't consider the fall in margin a big problem. Large acquisitions and investments dilute margins at first, because the new business is not yet as profitable as the main one. In my opinion, it is a great tactic to grow Kaspi beyond Kazakhstan, because it gives the company more ways to make a profit. I would buy Kaspi shares as a long-term investment.</blockquote>'''

trade_notes = '''<ul class="notes">
<li>The main series are Kazakhstan's official statistics (Bureau of National Statistics, Ministry of Trade and Integration, State Revenue Committee), as published by government bodies and national media.</li>
<li>Figures for 2020 and 2021 come from news reports citing official bodies and are less reliable than later years. Turnover for 2022 is the sum of exports and imports.</li>
<li>The 2023 import figure ($16.8 billion) is an early estimate that was later revised to about $15.4 billion.</li>
<li>Product groups are Kazakhstan's figures reported to UN Comtrade. Chinese customs data are shown separately and never mixed with the Kazakh series.</li>
</ul>'''
TRADE["notes"] = trade_notes

trade_sections = f'''<h2>Key findings</h2><ol>
<li>Trade turnover grew from $15.4 billion in 2020 to $34.1 billion in 2025.</li>
<li>China's share of Kazakhstan's foreign trade rose from 18.1% to 23.7%.</li>
<li>Kazakhstan exports mainly ores, oil, copper and uranium, and imports machinery, electronics and vehicles.</li>
<li>A surplus of $2.6 billion in 2020 turned into a deficit of $3.7 billion in 2025.</li></ol>
{fig(1, "Kazakhstan's exports to and imports from China, $ billion",
     columns([("Exports to China", GREY, EXPORTS), ("Imports from China", ACCENT, IMPORTS)], YEARS, w=560, h=260, top=22,
             desc="Exports grew from 9.0 to 15.2 billion dollars; imports from 6.4 to 18.9 billion"),
     "Kazakh official statistics, see sources 1-6", TRADE["data"])}
<p>Imports from China nearly tripled, from $6.4 billion to $18.9 billion, while exports rose by about two thirds. The balance changed sign in 2023, and in 2025 the deficit reached $3.7 billion as imports grew by 24% and exports by only 2%.</p>
<div class="table-title">Table 1. Kazakhstan's goods trade with China, $ billion (Kazakh data)</div>
{table(["", *YEARS],
       [["Exports to China", *EXPORTS], ["Imports from China", *IMPORTS], ["**Total trade", *TURNOVER],
        ["Balance", *[f"{v:+.1f}".replace("-", "−") for v in BALANCE]]])}
<p class="table-note">Sources: {src_link(0, SRC_TRADE)}; {src_link(1, SRC_TRADE)}; {src_link(2, SRC_TRADE)}; {src_link(3, SRC_TRADE)}; {src_link(4, SRC_TRADE)}; {src_link(5, SRC_TRADE)}.</p>
<figure class="figure"><div class="fig-title">Figure 2. Top five product groups in Kazakhstan's trade with China, 2024, $ billion</div>
<div class="hbars-grid"><div><div class="hbars-head">Exports to China</div>{hbars(TOP_EXPORTS)}</div>
<div><div class="hbars-head">Imports from China</div>{hbars(TOP_IMPORTS, colour=ACCENT)}</div></div>
<figcaption>Source: {src_link(7, SRC_TRADE)} (Kazakhstan's data reported to UN Comtrade). <a href="../{TRADE["data"]}.xlsx" download>Download the data (XLSX)</a></figcaption></figure>
<p>All five main exports are raw materials or products of primary processing, so their value depends on world commodity prices. The main imports are finished goods.</p>
<h2>A note on the statistics</h2>
<p>The two countries record the same trade very differently. China reports $48.7 billion of trade with Kazakhstan in 2025, against $34.1 billion in Kazakhstan's own data. Most of the gap is on the Chinese export side.</p>
<div class="table-title">Table 2. The same trade in two sets of statistics, $ billion</div>
{table(["", *YEARS],
       [["Total trade, Kazakh data", *TURNOVER], ["Total trade, Chinese data", *CN_TURNOVER],
        ["Goods from China: Chinese data", *[f"{v:.1f}" for v in CN_EXPORTS_TO_KZ]], ["Goods from China: Kazakh data", *IMPORTS]])}
<p class="table-note">Sources: {src_link(0, SRC_TRADE)}; {src_link(6, SRC_TRADE)}. Such "mirror statistics" gaps usually come from goods passing through third countries, different valuation methods and under-declared imports.</p>
<h2>My view</h2><blockquote class="view">{open(os.path.join(HERE, "view2.txt")).read().strip()}</blockquote>'''

report(KASPI, kaspi_sections,
       [("Revenue growth, 2025", "+60%"), ("Net income growth, 2025", "+1%"), ("Net margin, 2024", "41.7%"),
        ("Net margin, 2025", "26.4%"), ("Stake in Hepsiburada", "85%")], SRC_KASPI, disclaimer=True)
report(TRADE, trade_sections,
       [("Turnover, 2025", "$34.1 bn"), ("Exports, 2025", "$15.2 bn"), ("Imports, 2025", "$18.9 bn"),
        ("Balance, 2025", "−$3.7 bn"), ("China's share of KZ trade", "23.7%")], SRC_TRADE)


# ---------- New reports, October 2026 ----------

def view(name):
    """The author's own "My view" text. The section is left out until the file has text in it."""
    path = os.path.join(HERE, name)
    text = open(path).read().strip() if os.path.exists(path) else ""
    return f'<h2>My view</h2><blockquote class="view">{text}</blockquote>' if text else ""


# Kazatomprom: company reports for 2023-2025 and the first half of 2026
U_YEARS = ["2023", "2024", "2025"]
U_PROD = [21112, 23270, 25839]          # tU, 100% basis
U_SALES = [18069, 16670, 18494]         # Group U3O8 sales, tU
U_PRICE = [55.09, 69.48, 65.32]         # Group average realized price, $/lb U3O8
U_SPOT = [60.53, 86.28, 72.75]          # average weekly spot price, $/lb U3O8
U_REV = [1435, 1813, 1803]              # revenue, ₸ billion
U_EBITDA = [829, 1097, 1133]            # adjusted EBITDA, ₸ billion
U_ADJ_NP = [None, 577, 570]             # adjusted net profit attributable to owners, ₸ billion
U_H1 = dict(rev=(660.2, 717.8), np=(263.2, 240.4), price=(58.54, 67.88), spot=(69.11, 85.98), sales=(7625, 7586))

SRC_KAP = [
    ("Kazatomprom, Operating and Financial Review for 2025 (20 March 2026)",
     "https://www.kazatomprom.kz/storage/86/fy2025_ofr_eng.pdf", "Kazatomprom, 2025 review"),
    ("Kazatomprom, Kazatomprom announces 2025 Full Year Financial Results (20 March 2026)",
     "https://www.kazatomprom.kz/en/media/view/announces_2025_full_year_financial_results_"),
    ("Kazatomprom, Operating and Financial Review for 2024 (19 March 2025)",
     "https://www.kazatomprom.kz/storage/c0/fy2024_ofr_eng.pdf", "2024 review"),
    ("Kazatomprom, Operating and Financial Review for 2023 (15 March 2024)",
     "https://www.kazatomprom.kz/storage/29/fy2023_ofr_eng.pdf", "2023 review"),
    ("Kazatomprom, Kazatomprom announces 1H2026 Financial Results (21 August 2026)",
     "https://www.kazatomprom.kz/en/media/view/Kazatomprom%20announces%201H2026%20Financial%20Results"),
    ("Kazatomprom, Operating and Financial Review for the first half of 2026 (21 August 2026)",
     "https://www.kazatomprom.kz/storage/9f/6m_2026_ofr_eng.pdf", "first-half 2026 review"),
    ("Kazatomprom, 1H2025 Results and 2026 Production Strategy (August 2025, London Stock Exchange RNS)",
     "https://www.investegate.co.uk/announcement/rns/joint-stock-company-national-atomic-company-kazatomprom--kap/kap-1h2025-results-and-2026-production-strategy-/9068901"),
    ("Kazatomprom, Kazatomprom informs on Changes to Mineral Extraction Tax Rate",
     "https://www.kazatomprom.kz/en/media/view/kazatomprom_soobshchaet_ob_izmenenii_stavki_naloga_na_dobichu_poleznih_iskopaemih"),
    ("Kazatomprom, Integrated Annual Report 2025",
     "https://www.kazatomprom.kz/storage/ef/kap_iar_2025_final_eng234.pdf"),
]

KAP = dict(
    slug="kazatomprom-2025",
    url="research/kazatomprom-2025.html",
    tag="Companies",
    kind="Company note",
    title="More Uranium, Same Profit: Kazatomprom in 2025",
    date="17 Oct 2026", date_long="17 October 2026", iso="2026-10-17",
    line="Output rose 11% in 2025, yet revenue fell 1% as the uranium price slipped.",
    summary=("Kazatomprom, the world's largest uranium producer, mined 25,839 tonnes of uranium in 2025, 11% more than "
             "in 2024. Revenue still fell 1%, to ₸1.80 trillion, because its average selling price dropped 6% and it sold "
             "no enriched uranium after ₸252 billion of such sales in 2024. In the first half of 2026 the price recovered, "
             "but a new extraction tax and dearer sulphuric acid are pushing costs up."),
    art=columns([("Production", GREY, [v / 1000 for v in U_PROD])], U_YEARS, w=300, h=150, hi=2, top=32, fmt="{:.1f}",
                desc="Kazatomprom production, thousand tonnes of uranium: 21.1 in 2023, 23.3 in 2024, 25.8 in 2025"),
    art_title="Production, thousand tU",
    pdf=None, pages=0,
    data="data/kazatomprom-2023-2026",
    og_num="+11%", og_cap="more uranium in 2025, with revenue down 1%",
    og_chart=columns([("Production", GREY, [v / 1000 for v in U_PROD])], U_YEARS, w=420, h=260, hi=2, top=32, fmt="{:.1f}"),
)
KAP["feat"] = (U_YEARS, "Kazatomprom production, thousand tonnes of uranium",
               columns([("Production", GREY, [v / 1000 for v in U_PROD])], U_YEARS, w=520, h=270, hi=2, top=32, fmt="{:.1f}",
                       desc="Production 2023 to 2025"), "Kazatomprom operating and financial reviews")

data_files(KAP["data"], "Kazatomprom key figures, 2023 to first half of 2026",
           ["Sources: Kazatomprom operating and financial reviews for 2023, 2024, 2025 and the first half of 2026; 2025 and 1H2026 results releases.",
            "Production is on a 100% basis (all mines the Group consolidates or holds a stake in, counted in full).",
            "Group sales and the Group average realized price cover U3O8 only, not enriched uranium or fuel pellets.",
            "Spot price is the average of weekly spot prices reported by Kazatomprom from third-party price providers.",
            "Adjusted net profit attributable to owners is the company's own measure, without one-off items. It is not shown for 2023 because the 2023 report used a different adjusted measure."],
           [("Annual", ["Indicator", *U_YEARS],
             [["Production, tU (100% basis)", *U_PROD], ["Group U3O8 sales, tU", *U_SALES],
              ["Group average realized price, $/lb", *U_PRICE], ["Average weekly spot price, $/lb", *U_SPOT],
              ["Revenue, ₸ billion", *U_REV], ["Adjusted EBITDA, ₸ billion", *U_EBITDA],
              ["Adjusted net profit attributable to owners, ₸ billion", *["" if v is None else v for v in U_ADJ_NP]]]),
            ("First half", ["Indicator", "1H2025", "1H2026"],
             [["Revenue, ₸ billion", *U_H1["rev"]], ["Net profit, ₸ billion", *U_H1["np"]],
              ["Group average realized price, $/lb", *U_H1["price"]], ["Average weekly spot price, $/lb", *U_H1["spot"]],
              ["Group U3O8 sales, tU", *U_H1["sales"]]])])

KAP["notes"] = '''<ul class="notes">
<li>All figures come from Kazatomprom's own reports, listed under Sources. Production is on a 100% basis, which counts every mine the company consolidates or holds a stake in at full volume.</li>
<li>Sales volumes and the average realized price cover natural uranium (U3O8) only. Enriched uranium sold to Ulba-FA in 2024 is in revenue but not in these volumes.</li>
<li>Reported net profit is distorted by one-off gains in 2024 and 2025 linked to taking control of the Budenovskoye joint venture, so this note uses the company's adjusted net profit attributable to owners.</li>
<li>Percentage changes are calculated by the author from the reported figures.</li>
</ul>'''

kap_sections = f'''<h2>Key findings</h2><ol>
<li>Production rose 11% in 2025, to 25,839 tonnes of uranium (tU), and is 22% higher than in 2023.</li>
<li>The average price Kazatomprom received fell 6%, to $65.32 per pound. The spot price fell further, by 16%.</li>
<li>Revenue slipped 1%, to ₸1,803 billion. Natural uranium sales grew 16%, but enriched uranium sales of ₸252 billion in 2024 did not repeat.</li>
<li>Adjusted net profit was almost unchanged at ₸570 billion. In the first half of 2026 revenue rose 9%, while net profit fell 9%.</li></ol>
{fig(1, "Production, thousand tonnes of uranium (100% basis)",
     columns([("Production", GREY, [v / 1000 for v in U_PROD])], U_YEARS, hi=2, top=32, fmt="{:.1f}",
             desc="Production rose from 21.1 thousand tonnes in 2023 to 23.3 in 2024 and 25.8 in 2025"),
     src_link(0, SRC_KAP) + "; " + src_link(2, SRC_KAP), KAP["data"])}
<h2>Where the extra uranium went</h2>
<p>Kazatomprom sold 18,494 tU of natural uranium in 2025, 11% more than a year earlier. That part of the business earned ₸1,638 billion, up 16%, and made up 91% of revenue against 78% in 2024.</p>
<p>The rest of the 2024 revenue was enriched uranium sold to Ulba-FA, a fuel plant in Ust-Kamenogorsk: ₸252 billion, or 14% of the total. In 2025 this line was zero. Without it, 2024 revenue would have been about ₸1,561 billion, and 2025 would show growth of about 15%.</p>
<p>Asia took 56% of the uranium the Group sold in 2025, up from 50% in 2024. The Americas took 25% and Europe 19% (Integrated Annual Report 2025). The company does not publish sales by country in its results.</p>
<h2>Why the price matters more than volume</h2>
<p>Most of Kazatomprom's uranium is sold under long-term contracts, and many of them follow the spot price with a delay. So when spot prices jumped in 2024, the company's price rose less, and when spot fell in 2025, its price fell less (Figure 2). In the first half of 2026 the gap opened again: spot averaged $85.98, while Kazatomprom received $67.88.</p>
{fig(2, "Kazatomprom's average realized price and the spot price, $ per pound of U3O8",
     columns([("Kazatomprom realized price", GREY, U_PRICE + [U_H1["price"][1]]), ("Spot price", ACCENT, U_SPOT + [U_H1["spot"][1]])],
             U_YEARS + ["1H 2026"], w=560, h=260, top=100, fmt="{:.0f}",
             desc="Realized price 55, 69, 65 and 68 dollars per pound; spot 61, 86, 73 and 86"),
     src_link(0, SRC_KAP) + "; " + src_link(5, SRC_KAP), KAP["data"])}
<div class="table-title">Table 1. Kazatomprom key figures</div>
{table(["", *U_YEARS],
       [["Production, tU", *map(n0, U_PROD)], ["Group sales, tU", *map(n0, U_SALES)],
        ["Realized price, $/lb", *[f"{v:.2f}" for v in U_PRICE]], ["Spot price, $/lb", *[f"{v:.2f}" for v in U_SPOT]],
        ["**Revenue, ₸ billion", *map(n0, U_REV)], ["Adjusted EBITDA, ₸ billion", *map(n0, U_EBITDA)],
        ["**Adjusted net profit, ₸ billion", "n/a", *map(n0, U_ADJ_NP[1:])]])}
<p class="table-note">Adjusted net profit is attributable to owners and excludes one-off items. Sources: {src_link(0, SRC_KAP)}; {src_link(2, SRC_KAP)}; {src_link(3, SRC_KAP)}.</p>
<h2>2026: better prices, higher costs</h2>
<p>In the first six months of 2026 revenue rose 9%, to ₸718 billion, because the average realized price climbed 16%. Net profit still fell 9%, to ₸240 billion. The company puts this down to foreign exchange losses and higher finance costs.</p>
<p>Costs are going up for three reasons the company names. From 2026 the mineral extraction tax depends on how much each deposit produces, from 4% for up to 500 tonnes a year to 18% above 4,000 tonnes, with an extra charge when uranium prices are high. Sulphuric acid, which is used to dissolve uranium underground, has become more expensive. And a stronger tenge makes local costs bigger in dollars. In August 2026 Kazatomprom raised its 2026 guidance for C1 cash cost from $23.50-25.00 to $25.50-27.00 per pound.</p>
<p>Kazatomprom is also choosing to grow more slowly. In August 2025 it cut the 2026 production level in its subsoil use agreements by about 10%, from 32,777 to 29,697 tU. Its 2026 guidance is 27,500 to 29,000 tU.</p>
<h2>Risks</h2><ol>
<li>Profit depends on the uranium price, which fell 16% in 2025 and rose again in 2026.</li>
<li>The new tax raises costs on the largest deposits most, and the top rate applies when prices are high.</li>
<li>The company says its 2026 production guidance depends on sulphuric acid being available.</li></ol>
{view("view_kazatomprom.txt")}'''

# China and Central Asia, 2025: Chinese customs data and each country's own figures, $ billion
CA_ROWS = [  # country, total (Chinese data), growth %, China's exports, China's imports, country's own total or None
    ("Kazakhstan", 48.7, 11, 29.7, 19.0, 34.1),
    ("Kyrgyzstan", 27.2, 20, 22.0, 5.2, 4.97),
    ("Uzbekistan", 16.1, 18, 14.2, 1.9, 17.2),
    ("Turkmenistan", 10.0, -5.6, 1.6, 8.4, None),
    ("Tajikistan", 4.3, 12, 3.7, 0.56, 2.82),
]
CA_TOTAL, CA_EXP, CA_IMP = 106.3, 71.2, 35.1

SRC_CA = [
    ("The State Council of the PRC (Xinhua), China-Central Asia economic, trade cooperation achieves remarkable progress in 2025 (18 January 2026)",
     "https://english.www.gov.cn/archive/statistics/202601/18/content_WS696c9e63c6d00ca5f9a08a1d.html", "Xinhua"),
    ("Eurasianet, China's trade surplus with Central Asia grows in 2025 (GACC data)",
     "https://eurasianet.org/chinas-trade-surplus-with-central-asia-grows-in-2025", "Eurasianet (GACC data)"),
    ("Eurasianet, China reinforces its trade dominance in Central Asia, but numbers don't always align (January 2026)",
     "https://eurasianet.org/china-reinforces-its-trade-dominance-in-central-asia-but-numbers-dont-always-align", "Eurasianet, January 2026"),
    ("RFE/RL, China-Kyrgyzstan trade gap widens as conflicting data raises transparency concerns (March 2026)",
     "https://www.rferl.org/a/china-kyrgyzstan-trade-export-statistics-transparency-corruption-central-asia/33716141.html"),
    ("UzDaily, Uzbekistan's foreign trade turnover reaches US$81.2 billion in 2025",
     "https://www.uzdaily.uz/en/uzbekistans-foreign-trade-turnover-reaches-us812-billion-in-2025-up-207/"),
    ("Association of Financiers of Kazakhstan, Kazakhstan-China commodity turnover, March 2026 (BNS data)",
     "https://afk.kz/2026/03/Kazakhstan-China-Commodity-Turnover-March2026.pdf", "Association of Financiers of Kazakhstan (BNS data)"),
]

CA = dict(
    slug="china-central-asia-2025",
    url="research/china-central-asia-2025.html",
    tag="Trade",
    kind="Trade brief",
    title="Counted Twice: China's Trade with Central Asia in 2025",
    date="17 Oct 2026", date_long="17 October 2026", iso="2026-10-17",
    line="China counts $27.2 billion of trade with Kyrgyzstan. Kyrgyzstan counts $5 billion.",
    summary=("China's trade with the five Central Asian states reached $106.3 billion in 2025, up 12%, according to "
             "Chinese customs. China sold the region twice as much as it bought, and only Turkmenistan, with its gas, "
             "sold China more than it bought. The countries' own statistics often show much less trade: Kyrgyzstan "
             "records less than a fifth of the figure China reports."),
    art=hbars([(c, t) for c, t, *_ in CA_ROWS], fmt="{:.1f}"),
    art_title="Trade with China, 2025, $ bn (Chinese data)",
    pdf=None, pages=0,
    data="data/china-central-asia-trade-2025",
    og_num="$106.3 bn", og_cap="China's trade with Central Asia in 2025",
    og_chart=columns([("China's data", GREY, [r[1] for r in CA_ROWS])], ["KZ", "KG", "UZ", "TM", "TJ"], w=420, h=260, top=56, fmt="{:.1f}"),
)
CA["feat"] = (None, "Trade with China in 2025, $ billion: China's figure and the country's own",
              columns([("China's data", GREY, [r[1] for r in CA_ROWS if r[5]]), ("Country's own data", ACCENT, [r[5] for r in CA_ROWS if r[5]])],
                      [r[0] for r in CA_ROWS if r[5]], w=520, h=270, top=56, fmt="{:.1f}",
                      desc="Kazakhstan 48.7 vs 34.1; Kyrgyzstan 27.2 vs 5.0; Uzbekistan 16.1 vs 17.2; Tajikistan 4.3 vs 2.8"),
              "Chinese customs via Xinhua and Eurasianet; national statistics")

data_files(CA["data"], "China's goods trade with Central Asia, 2025 ($ billion)",
           ["Chinese data: General Administration of Customs of China (GACC), as reported by Xinhua and Eurasianet.",
            "Country's own data: Kazakhstan, Bureau of National Statistics (via the Association of Financiers of Kazakhstan); "
            "Kyrgyzstan, official figure reported by RFE/RL; Uzbekistan, Statistics Agency (via UzDaily, 21.2% of $81.2 billion); "
            "Tajikistan, customs service (imports $2.3 billion plus exports $0.52 billion, via Eurasianet). Turkmenistan does not publish this figure.",
            "China's exports to the region are $71.2 billion in the Xinhua report and $71.3 billion in Eurasianet's.",
            "Growth is the year-on-year change reported with the Chinese data."],
           [("2025", ["Country", "Total trade, Chinese data", "Growth, %", "China's exports", "China's imports", "Total trade, country's own data"],
             [[c, t, g, e, i, "" if o is None else o] for c, t, g, e, i, o in CA_ROWS] +
             [["Central Asia", CA_TOTAL, 12, CA_EXP, CA_IMP, ""]])])

CA["notes"] = '''<ul class="notes">
<li>The main series is China's customs data (General Administration of Customs of China), as published by Xinhua and reported country by country by Eurasianet.</li>
<li>"Country's own data" is each Central Asian country's official figure for its trade with China, taken from the sources listed. Turkmenistan does not publish one.</li>
<li>For Tajikistan, the country's own total is the sum of imports from China ($2.3 billion) and exports to China ($0.52 billion) reported by its customs service.</li>
<li>China's exports to the region are $71.2 billion in Xinhua's report and $71.3 billion in Eurasianet's. This brief uses $71.2 billion. Shares and gaps are calculated by the author.</li>
</ul>'''

ca_rows_html = [[c, f"{t:.1f}", f"{g:+.1f}%".replace(".0%", "%").replace("-", "−"), f"{e:.1f}", f"{i:.1f}",
                 "n/a" if o is None else f"{o:.1f}"] for c, t, g, e, i, o in CA_ROWS]
ca_sections = f'''<h2>Key findings</h2><ol>
<li>China's trade with Central Asia reached $106.3 billion in 2025, up 12% and above $100 billion for the first time.</li>
<li>China exported $71.2 billion to the region and imported $35.1 billion, a surplus of $36.1 billion.</li>
<li>Kazakhstan accounts for 46% of the total. Kyrgyzstan is second with 26% and grew fastest, by 20%.</li>
<li>Kyrgyzstan's own statistics show $4.97 billion of trade with China, against $27.2 billion in Chinese data.</li></ol>
<figure class="figure"><div class="fig-title">Figure 1. China's trade with each Central Asian country, 2025, $ billion (Chinese data)</div>
{hbars([(c, t) for c, t, *_ in CA_ROWS], fmt="{:.1f}")}
<figcaption>Source: {src_link(1, SRC_CA)}; {src_link(2, SRC_CA)}. <a href="../{CA["data"]}.csv" download>Download the data (CSV)</a></figcaption></figure>
<h2>Four countries buy more than they sell</h2>
<p>China sells Central Asia about twice as much as it buys. Kazakhstan, Kyrgyzstan, Uzbekistan and Tajikistan all import more from China than they export to it. For Uzbekistan the ratio is more than seven to one: $14.2 billion of goods from China against $1.9 billion going the other way.</p>
<p>Turkmenistan is the exception. It sold China $8.4 billion of goods in 2025, almost all of it natural gas, and bought $1.6 billion. It was also the only country whose trade with China fell, by 5.6%.</p>
<div class="table-title">Table 1. China's trade with Central Asia, 2025, $ billion</div>
{table(["", "Total, China's data", "Growth", "China's exports", "China's imports", "Total, country's own data"],
       ca_rows_html + [["**Central Asia", f"{CA_TOTAL:.1f}", "+12%", f"{CA_EXP:.1f}", f"{CA_IMP:.1f}", ""]])}
<p class="table-note">Sources: {src_link(0, SRC_CA)}; {src_link(1, SRC_CA)}; {src_link(2, SRC_CA)}; {src_link(3, SRC_CA)}; {src_link(4, SRC_CA)}; {src_link(5, SRC_CA)}.</p>
<h2>The same trade, counted twice</h2>
<p>The countries' own statistics tell a different story (Figure 2). Kazakhstan records $34.1 billion of trade with China, $14.6 billion less than China does. The previous <a href="kazakhstan-china-trade.html">trade brief</a> looked at that gap in detail.</p>
<p>Kyrgyzstan's gap is bigger in absolute terms and far bigger in proportion. Its official figure of $4.97 billion is less than a fifth of China's $27.2 billion, and the difference grew from $17.1 billion in 2024 to about $22 billion in 2025 (RFE/RL). Kyrgyz customs officials told RFE/RL that China counts every shipment sent to or through Kyrgyzstan, while Kyrgyzstan counts only goods for its own use. Under-declared values, unregistered online purchases and goods arriving through Kazakhstan add to the gap.</p>
<p>In Tajikistan the two sides agree on exports to China but not on imports: China reports $3.7 billion of goods sent, Tajik customs $2.3 billion received. Eurasianet links the difference to Chinese goods entering without being recorded. Uzbekistan is the one case where the country's own figure, $17.2 billion, is higher than China's.</p>
{fig(2, "Trade with China in 2025: China's figure and the country's own, $ billion",
     columns([("China's data", GREY, [r[1] for r in CA_ROWS if r[5]]), ("Country's own data", ACCENT, [r[5] for r in CA_ROWS if r[5]])],
             [r[0] for r in CA_ROWS if r[5]], w=560, h=260, top=56, fmt="{:.1f}",
             desc="Kazakhstan 48.7 vs 34.1; Kyrgyzstan 27.2 vs 5.0; Uzbekistan 16.1 vs 17.2; Tajikistan 4.3 vs 2.8"),
     src_link(1, SRC_CA) + "; " + src_link(3, SRC_CA) + "; " + src_link(4, SRC_CA) + "; " + src_link(5, SRC_CA), CA["data"])}
<p>For anyone using these numbers, the practical point is to say whose data they are. A headline of "$27 billion of trade with Kyrgyzstan" describes goods leaving China, and a large part of them may end up somewhere else.</p>
{view("view_central_asia.txt")}'''

report(KAP, kap_sections,
       [("Production, 2025", "25,839 tU"), ("Production growth", "+11%"), ("Realized price, 2025", "$65.32/lb"),
        ("Revenue, 2025", "₸1.80 trn"), ("Asia's share of sales", "56%")], SRC_KAP, disclaimer=True)
report(CA, ca_sections,
       [("Trade, 2025", "$106.3 bn"), ("Growth", "+12%"), ("China's surplus", "$36.1 bn"),
        ("Kazakhstan's share", "46%"), ("Kyrgyzstan, own data", "$4.97 bn")], SRC_CA)

TRADE["feat"] = (YEARS, "Kazakhstan's exports to and imports from China, $ billion",
                 columns([("Exports", GREY, EXPORTS), ("Imports", ACCENT, IMPORTS)], YEARS, w=520, h=270, top=22,
                         desc="Exports and imports, 2020 to 2025"), "Kazakh official statistics")
REPORTS = [CA, KAP, TRADE, KASPI]  # newest first; the first one is featured on the home page


# ---------- Home ----------


# Companies and countries the research covers; every number comes from a report on the site.
COVERAGE = [
    dict(code="KSPI", tag="Company · Kazakhstan", name="Kaspi.kz", band="#d9352b",
         what="Payments, online shopping and loans in one app", r=KASPI,
         stats=[("Revenue, 2025", "₸4.05 trn"), ("Revenue growth", "+60%"), ("Net margin", "26.4%")]),
    dict(code="HEPS", tag="Company · Turkey", name="Hepsiburada", band="#e8590c",
         what="E-commerce marketplace, controlled by Kaspi since 2025", r=KASPI,
         stats=[("Segment revenue, 2025", "₸1.03 trn"), ("Net loss, 2025", "₸93 bn"), ("Kaspi's stake, Jan 2026", "85%")]),
    dict(code="KZ", tag="Country", name="Kazakhstan", band="#0a7f99",
         what="Sells raw materials to China, buys machinery", r=TRADE,
         stats=[("Trade with China, 2025", "$34.1 bn"), ("China's share of trade", "23.7%"), ("Balance with China", "−$3.7 bn")]),
    dict(code="KAP", tag="Company · Kazakhstan", name="Kazatomprom", band="#3f7d3a",
         what="World's largest uranium producer, listed in London and Astana", r=KAP,
         stats=[("Production, 2025", "25,839 tU"), ("Realized price", "$65.32/lb"), ("Revenue, 2025", "₸1.80 trn")]),
    dict(code="CA", tag="Region", name="Central Asia", band="#8a5a2b",
         what="Five states whose trade with China passed $100 billion in 2025", r=CA,
         stats=[("Trade with China, 2025", "$106.3 bn"), ("China's surplus", "$36.1 bn"), ("Kyrgyzstan, own data", "$4.97 bn")]),
    dict(code="CN", tag="Country", name="China", band="#b8261c",
         what="Kazakhstan's main trading partner in these reports", r=TRADE,
         stats=[("Goods to Kazakhstan, 2025", "$18.9 bn"), ("Same flow, Chinese data", "$29.7 bn"), ("Top buy from Kazakhstan", "Ores")]),
]


def card(c):
    return (f'<a class="card" href="{c["r"]["url"]}"><div class="card-band" style="background:{c["band"]}"><b>{c["code"]}</b><span>{c["tag"]}</span></div>'
            f'<div class="card-body"><h3>{c["name"]}</h3><p class="muted">{c["what"]}</p>'
            '<ul class="card-stats">' + "".join(f'<li><span>{k}</span><b>{v}</b></li>' for k, v in c["stats"]) + '</ul>'
            f'<span class="card-more">{c["r"]["kind"]}</span></div></a>')


F = REPORTS[0]
home = f'''<section class="masthead"><div class="wrap">
<h1>Research on Kazakhstan's companies and its trade with China</h1>
<p>Company notes and trade briefs based on company filings and official statistics. Current reports cover Kaspi.kz and Kazatomprom, Kazakhstan's trade with China, and China's trade with the five Central Asian states. Every source is cited, and the underlying data is available to download.</p>
</div></section>

<section class="block"><div class="wrap">
<div class="block-head"><h2>Latest</h2></div>
<div class="featured">
<div class="featured-text">
<div class="label">{F["kind"]} &middot; <time datetime="{F["iso"]}">{F["date"]}</time></div>
<h2><a href="{F["url"]}">{F["title"]}</a></h2>
<p class="dek">{F["line"]}</p>
<p>{F["summary"]}</p>
<div class="row-actions"><a href="{F["url"]}">Read the {F["kind"].split()[-1].lower()}</a>{pdf_link(F)}<a class="pdf-link" href="{F["data"]}.xlsx" download>Data <span>XLSX</span></a></div>
</div>
<figure class="figure featured-chart"><div class="fig-title">{F["feat"][1]}</div>
{F["feat"][2]}
<figcaption>Source: {F["feat"][3]}. From <a href="{F["url"]}">{F["title"].split(":")[0]}</a>.</figcaption></figure>
</div>
</div></section>

<section class="block"><div class="wrap">
<div class="block-head"><h2>Research</h2><a href="research.html">All research</a></div>
<div class="rows">{"".join(row(r) for r in REPORTS[1:])}</div>
</div></section>

<section class="block"><div class="wrap">
<div class="block-head"><h2>Coverage</h2><a href="research.html">All research</a></div>
<div class="cards">{"".join(card(c) for c in COVERAGE)}</div>
</div></section>

<section class="block block-tint"><div class="wrap">
<div class="block-head"><h2>Data</h2><a href="data.html">All data</a></div>
<p class="block-lead">Spreadsheets with the numbers used in each report.</p>
<div class="rows">{"".join(f'<div class="data-row"><div><b>{d["name"]}</b><span>{d["cover"]}</span></div><div class="data-links"><a href="{d["base"]}.xlsx" download>XLSX</a><a href="{d["base"]}.csv" download>CSV</a></div></div>' for d in [
    dict(name="China-Central Asia goods trade", cover="2025 · five countries · Chinese and national data", base=CA["data"]),
    dict(name="Kazatomprom key figures", cover="2023-1H2026 · production, prices, revenue, profit", base=KAP["data"]),
    dict(name="Kazakhstan-China goods trade", cover="2020-2025 · Kazakh and Chinese data · top products", base=TRADE["data"]),
    dict(name="Kaspi.kz key financials", cover="2023-2025 · revenue by segment, net income, margins", base=KASPI["data"])])}</div>
</div></section>'''
page("index.html", "Steppe & Silk Research", home, "",
     "Reports on Kazakh companies and on Kazakhstan's trade with China, with the data behind each chart.",
     ld={"@context": "https://schema.org", "@type": "WebSite", "name": "Steppe & Silk Research", "url": SITE})

# ---------- Research ----------

counts = {t: sum(r["tag"] == t for r in REPORTS) for t in ("Companies", "Trade")}
research = f'''<section class="page-head"><div class="wrap">
<h1>Research</h1>
<p><b>Company notes</b> look at how a company makes money and what has changed, based on its annual report.
<b>Trade briefs</b> look at what Kazakhstan and its neighbours sell and buy, based on official statistics.</p>
<div class="filters">
<button class="on" data-f="all">All <span>{len(REPORTS)}</span></button>
<button data-f="companies">Company notes <span>{counts["Companies"]}</span></button>
<button data-f="trade">Trade briefs <span>{counts["Trade"]}</span></button>
</div>
</div></section>
<section class="block"><div class="wrap"><div class="rows" id="rows">{"".join(row(r) for r in REPORTS)}</div></div></section>'''
page("research.html", "Research · Steppe & Silk Research", research, "research.html",
     "Company notes and trade briefs on Kazakhstan, Central Asia and China.")

# ---------- Data ----------

DATASETS = [
    dict(name="China-Central Asia goods trade", cover="2025", unit="$ billion",
         what="China's trade with Kazakhstan, Kyrgyzstan, Uzbekistan, Turkmenistan and Tajikistan: totals, growth, exports, imports, and each country's own figure.",
         src="GACC via Xinhua and Eurasianet; national statistics", base=CA["data"], r=CA),
    dict(name="Kazatomprom key figures", cover="2023-1H2026", unit="tU, $/lb, ₸ billion",
         what="Production, sales volume, realized and spot uranium prices, revenue, adjusted EBITDA and adjusted net profit; first half of 2025 and 2026.",
         src="Kazatomprom operating and financial reviews", base=KAP["data"], r=KAP),
    dict(name="Kazakhstan-China goods trade", cover="2020-2025", unit="$ billion",
         what="Exports, imports, turnover and balance (Kazakh data); the same trade in Chinese customs data; top five product groups in 2024.",
         src="Bureau of National Statistics of Kazakhstan; GACC; UN Comtrade", base=TRADE["data"], r=TRADE),
    dict(name="Kaspi.kz key financials", cover="2023-2025", unit="₸ million",
         what="Revenue by segment, total revenue, net income, net margin, Marketplace share; Turkey vs. other markets in 2025.",
         src="Kaspi.kz Form 20-F, 2025", base=KASPI["data"], r=KASPI),
]
drows = "".join(f'''<tr><td><b>{d["name"]}</b><br><span class="muted">{d["what"]}</span></td><td>{d["cover"]}</td><td>{d["unit"]}</td>
<td>{d["src"]}</td><td class="nowrap"><a href="{d["base"]}.xlsx" download>XLSX</a> &middot; <a href="{d["base"]}.csv" download>CSV</a></td>
<td><a href="{d["r"]["url"]}">{d["r"]["title"].split(":")[0]}</a></td></tr>''' for d in DATASETS)
data_page = f'''<section class="page-head"><div class="wrap">
<h1>Data</h1>
<p>The numbers used in each report. Every file lists its sources and what the numbers include. You can reuse them if you credit Steppe &amp; Silk Research.</p>
</div></section>
<section class="block"><div class="wrap">
<div class="table-wrap"><table class="data-table datasets"><thead><tr><th>Dataset</th><th>Years</th><th>Unit</th><th>Source</th><th>Download</th><th>Used in</th></tr></thead>
<tbody>{drows}</tbody></table></div>
</div></section>'''
page("data.html", "Data · Steppe & Silk Research", data_page, "data.html",
     "Download the data behind Steppe & Silk Research reports on Kazakhstan, Central Asia and China.")

# ---------- About ----------

about = f'''<section class="page-head"><div class="wrap"><h1>About</h1></div></section>
<section class="block"><div class="wrap"><div class="prose">
<p class="lead">Steppe &amp; Silk Research is an independent research publication covering companies in Kazakhstan and the country's trade with China. It was founded in 2026 by Chingiz Bakytzhanov.</p>
<p>The publication produces two formats. <b>Company notes</b> examine how a company earns its money and what has changed in its results, based on its annual report. <b>Trade briefs</b> analyse what Kazakhstan exports and imports, based on official statistics.</p>
<h2>Editorial standards</h2>
<ul>
<li>Figures are taken from company filings and official statistics, and every source is cited with a link.</li>
<li>The data behind each chart is published and can be <a href="data.html">downloaded</a>.</li>
<li>Where sources disagree, as Kazakh and Chinese trade statistics often do, each report states which figures it uses and why.</li>
<li>Analysis and opinion are kept separate. The author's own assessment appears only in the "My view" section of each report.</li>
<li>Nothing published here is investment advice.</li>
</ul>
<h2>Corrections</h2>
<p>Errors are corrected openly. Each correction is noted at the end of the report with its date. Readers who spot a mistake can contact the editor at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<h2>Founder and editor</h2>
<p>Chingiz Bakytzhanov is the founder and editor of Steppe &amp; Silk Research and the author of its reports. He is a student from Kazakhstan with a focus on finance, and he works in Kazakh, Russian and English. Before founding the publication he served as Director of Business and Finance at Earth Ambassadors, a youth organisation.</p>
<h2 id="contact">Contact</h2>
<p>For questions about the research, data requests, corrections or collaboration, contact the editor.</p>
<ul class="contact-list"><li><span>Email</span><a href="mailto:{EMAIL}">{EMAIL}</a></li></ul>
</div></div></section>'''
page("about.html", "About · Steppe & Silk Research", about, "about.html",
     "About Steppe & Silk Research, how its research is made, and its author.")


# ---------- Terms and Privacy ----------

terms = f'''<section class="page-head"><div class="wrap"><h1>Terms of use</h1><p>Last updated 11 October 2026</p></div></section>
<section class="block"><div class="wrap"><div class="prose">
<h2>Not investment advice</h2>
<p>Everything on Steppe &amp; Silk Research is published for information and education. It is not a recommendation to buy, sell or hold any security, and it does not take into account anyone's financial situation. Do your own research before making any investment decision.</p>
<h2>Accuracy</h2>
<p>The figures come from annual reports and official statistics, and each report links its sources. Mistakes can still happen, and sources are sometimes revised. The content is provided as it is, without any guarantee that it is complete or current. If you find an error, please write to <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<h2>Using the content</h2>
<p>You may quote the reports and reuse the downloadable data, including for commercial purposes, as long as you name Steppe &amp; Silk Research and link to the page you used. The reports themselves (text, charts and PDFs) may not be republished in full without permission.</p>
<h2>Third-party sources and links</h2>
<p>Company names and trademarks belong to their owners. Links to other websites are given as sources; Steppe &amp; Silk Research is not responsible for their content.</p>
<h2>Changes</h2>
<p>These terms may be updated. The date at the top shows the latest version.</p>
</div></div></section>'''
page("terms.html", "Terms of use · Steppe & Silk Research", terms, "",
     "Terms of use for Steppe & Silk Research.")

privacy = f'''<section class="page-head"><div class="wrap"><h1>Privacy policy</h1><p>Last updated 11 October 2026</p></div></section>
<section class="block"><div class="wrap"><div class="prose">
<p class="lead">This site does not use cookies, analytics or advertising trackers, and it has no accounts or forms.</p>
<h2>What is collected</h2>
<ul>
<li><b>Server logs.</b> The site is hosted by Vercel. Like any web host, Vercel records technical data such as your IP address, browser and the pages requested, to deliver the site and protect it from abuse.</li>
<li><b>Fonts.</b> The typefaces are loaded from Google Fonts, so your browser sends your IP address to Google when a page opens.</li>
<li><b>Email.</b> If you write to <a href="mailto:{EMAIL}">{EMAIL}</a>, your message and address are kept only to reply to you and are never shared or sold.</li>
</ul>
<h2>Your rights</h2>
<p>You can ask what information about you is held and ask for it to be deleted by writing to the address above.</p>
<h2>Changes</h2>
<p>If this policy changes, the date at the top will change too.</p>
</div></div></section>'''
page("privacy.html", "Privacy policy · Steppe & Silk Research", privacy, "",
     "Privacy policy for Steppe & Silk Research.")

# Old addresses keep working.
redirect("companies.html", "research.html#companies")
redirect("trade.html", "research.html#trade")
redirect("contact.html", "about.html#contact")

# ---------- Sitemap, assets, link-preview cards ----------

urls = ["", "research.html", "data.html", "about.html", "terms.html", "privacy.html"] + [r["url"] for r in REPORTS]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "".join(f"  <url><loc>{SITE}/{u}</loc><lastmod>2026-10-17</lastmod></url>\n" for u in urls) + "</urlset>\n")

write("assets/favicon.svg", FAVICON)
for name in ("style.css", "site.js"):
    with open(os.path.join(HERE, name)) as a:
        write("assets/" + name, a.read())

# 1200x630 cards; tools/render_og.js turns them into og/*.png
OG_CSS = (f"body{{margin:0;width:1200px;height:630px;background:#faf7f2;font-family:'IBM Plex Sans',Arial;color:{INK};}}"
          ".c{box-sizing:border-box;width:1200px;height:630px;padding:56px 64px;display:flex;flex-direction:column;border-top:14px solid " + ACCENT + "}"
          ".top{display:flex;justify-content:space-between;font-family:'IBM Plex Mono',monospace;font-size:20px;letter-spacing:1px;text-transform:uppercase}"
          ".top b{color:" + ACCENT + ";font-weight:500}.mid{flex:1;display:flex;gap:48px;align-items:center}"
          "h1{font-family:'IBM Plex Serif',Georgia,serif;font-size:50px;line-height:1.15;margin:0 0 28px;font-weight:600}"
          ".num{font-family:'IBM Plex Serif',Georgia,serif;font-size:76px;font-weight:600;color:" + ACCENT + ";line-height:1}"
          ".cap{font-size:24px;color:#4a5562;margin-top:8px}.chart{width:420px;flex:none}"
          ".foot{display:flex;justify-content:space-between;font-size:22px;color:#4a5562;border-top:2px solid " + INK + ";padding-top:18px}")
og_dir = os.path.join(HERE, "og")
os.makedirs(og_dir, exist_ok=True)
cards = {r["slug"]: (f'<div class="top"><span>Steppe &amp; Silk Research</span><b>{r["kind"]}</b></div>'
                     f'<div class="mid"><div><h1>{r["title"]}</h1><div class="num">{r["og_num"]}</div><div class="cap">{r["og_cap"]}</div></div>'
                     f'<div class="chart">{r["og_chart"]}</div></div>'
                     f'<div class="foot"><span>{AUTHOR} &middot; {r["date_long"]}</span><span>steppesilk.com</span></div>')
         for r in REPORTS}
cards["home"] = ('<div class="top"><span>Steppe &amp; Silk Research</span><b>steppesilk.com</b></div>'
                 '<div class="mid"><div><h1 style="font-size:50px">Research on Kazakhstan\'s companies and its trade with China</h1>'
                 '<div class="cap">Company notes and trade briefs, with the data behind every chart.</div></div>'
                 '<div class="chart"><div class="cap" style="margin:0 0 6px;font-size:18px">Kazakhstan-China trade, $ billion</div>'
                 f'{columns([("Turnover", GREY, TURNOVER)], YEARS, w=420, h=280, hi=5, top=40, fmt="{:.0f}")}</div></div>'
                 f'<div class="foot"><span>{AUTHOR}</span><span>Kazakhstan &middot; Central Asia &middot; China</span></div>')
for slug, inner in cards.items():
    with open(os.path.join(og_dir, slug + ".html"), "w") as f:
        f.write(f'<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>{OG_CSS}</style></head>'
                f'<body><div class="c">{inner}</div></body></html>')
print("ok")
