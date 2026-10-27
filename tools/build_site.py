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
         '&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400'
         '&display=swap" rel="stylesheet">')

INK, GREY, ACCENT, MUTED = "#14202e", "#bfc3c9", "#0b6e79", "#5f6873"
CHART_HI = "#1f2d3d"  # charts: neutral grey bars, dark slate for the highlight and the second series
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
            c = CHART_HI if (k == 1 and i == hi) else col
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
# GACC monthly bulletin, table (2), December issue of each year, US$ thousand
CN_KZ_RAW = [(21446707, 11707318, 9739389), (25250692, 13981061, 11269630), (31174483, 16355236, 14819247),
             (41021166, 24697397, 16323769), (43819657, 27964080, 15855577), (48675864, 29695302, 18980562)]
CN_TURNOVER = [round(a / 1e6, 2) for a, _, _ in CN_KZ_RAW]
CN_EXPORTS_TO_KZ = [round(b / 1e6, 2) for _, b, _ in CN_KZ_RAW]
CN_IMPORTS_FROM_KZ = [round(c / 1e6, 2) for _, _, c in CN_KZ_RAW]
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
     "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001985487&type=20-F"),
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
    ("General Administration of Customs of China, Monthly Bulletin, table (2) Imports and Exports by Country (Region) of Origin/Destination, December 2025",
     "http://english.customs.gov.cn/Statics/ef1a478f-8a43-4b51-9690-fb975762a2c2.html", "GACC monthly bulletin"),
]


def src_link(i, srcs, pre="../"):
    name, url = srcs[i][:2]
    short = srcs[i][2] if len(srcs[i]) > 2 else name.split(",")[0]
    return f'<a href="{url}" rel="noopener">{short}</a>'


KASPI = dict(
    slug="kaspi-hepsiburada",
    logos=[("kaspi", "Kaspi.kz"), ("hepsiburada", "Hepsiburada")],
    sector="Banks & fintech",
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
    mark="KZ &middot; CN",
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
    og_chart=columns([("Exports", GREY, EXPORTS), ("Imports", CHART_HI, IMPORTS)], YEARS, w=420, h=260, top=22),
)
REPORTS = [TRADE, KASPI]  # newest first; the first one is featured on the home page


def pdf_link(r, pre=""):
    if not r.get("pdf"):
        return ""
    return f'<a class="pdf-link" href="{pre}{r["pdf"]}" download>PDF <span>{r["pages"]} pp.</span></a>'


def kind_label(r):
    """Company notes carry their sector, e.g. "Company note · Banks & fintech"."""
    return r["kind"] + (f' &middot; {r["sector"]}' if r.get("sector") else "")


def row_mark(r, pre=""):
    """Left of each article in a list: the company's logo, or the countries a trade brief covers."""
    if r.get("logos"):
        l, n = r["logos"][0]
        return f'<img class="row-logo" src="{pre}assets/logos/{l}.svg" alt="{escape(n)} logo">'
    return f'<span class="row-mark">{r["mark"]}</span>' if r.get("mark") else ""


def row(r, pre=""):
    return f'''<div class="row" data-type="{r["tag"].lower()}">
<div class="row-date">{row_mark(r, pre)}<time datetime="{r["iso"]}">{r["date"]}</time></div>
<div class="row-main"><div class="label">{kind_label(r)}</div><h3><a class="row-link" href="{pre}{r["url"]}">{r["title"]}</a></h3><p>{r["line"]}</p>
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

def report(r, sections, facts, sources, disclaimer=False, meta=None):
    """Company notes open with five fact tiles. Trade briefs are statistical bulletins: a box describing
    the data (meta) and a table of key indicators (facts = (head, rows)) instead of the tiles."""
    pre = "../"
    if meta:
        head, rows = facts
        kv = ('<div class="bulletin-head"><dl class="meta">' + "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in meta) + '</dl>'
              f'<div class="table-title">Key indicators</div>{table(head, rows)}</div>')
    else:
        kv = "".join(f'<div class="fact"><div class="fact-num">{v}</div><div class="fact-label">{k}</div></div>' for k, v in facts)
        kv = f'<div class="facts">{kv}</div>' 
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
{"".join(f'<img class="report-logo" src="{pre}assets/logos/{l}.svg" alt="{escape(n)} logo">' for l, n in r.get("logos", []))}
<div class="label"><a href="{pre}research.html#{r["tag"].lower()}">{kind_label(r)}</a></div>
<h1>{r["title"]}</h1>
<p class="dek">{r["line"]}</p>
<div class="byline">By <a href="{pre}about.html">{AUTHOR}</a> &middot; Published <time datetime="{r["iso"]}">{r["date_long"]}</time></div>
{dl}
</header>
{kv}
<div class="report-body">
<h2>{"1. " if meta else ""}Summary</h2><p>{r["summary"]}</p>
{sections}
{warn}
<h2>{"Methodology" if meta else "Notes and method"}</h2>{r["notes"]}
<h2>Sources</h2><ol class="sources">{srcs}</ol>
<h2>Download</h2>{dl}
<div class="cite"><div class="label">How to cite</div><p>{cite}</p></div>
<p class="corrections">Found an error? Email <a href="mailto:{EMAIL}">{EMAIL}</a>. Corrections are listed here with their date.</p>
{"".join(f'<p class="corrections"><b>Correction, {d}:</b> {c}</p>' for d, c in r.get("corrections", []))}
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
     columns([("Revenue", GREY, [v/1e6 for v in K_REV]), ("Net income", CHART_HI, [v/1e6 for v in K_NI])], K_YEARS,
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
<li>Kazakh series: Bureau of National Statistics, Ministry of Trade and Integration and State Revenue Committee, as published by government bodies and national media. Figures for 2020 and 2021 come from news reports citing these bodies and are less reliable than later years. Turnover for 2022 is the sum of exports and imports. The 2023 import figure ($16.8 billion) is an early estimate, later revised to about $15.4 billion.</li>
<li>Chinese series: General Administration of Customs of China (GACC), monthly bulletin table "Imports and Exports by Country (Region) of Origin/Destination", December issue of each year, converted from US$ thousand to US$ billion.</li>
<li>Product groups: Kazakhstan's figures reported to UN Comtrade, 2024.</li>
<li>The two national series are shown side by side and never combined. Changes and shares are calculated by the author.</li>
</ul>'''
TRADE["notes"] = trade_notes
TRADE["corrections"] = [("23 October 2026",
    "China's exports to Kazakhstan in 2022 were $16.4 billion, not $16.2 billion, and total trade in Chinese data was "
    "$31.2 billion in 2022, $21.4 billion in 2020 and $25.3 billion in 2021. Figures are now taken directly from the "
    "GACC monthly bulletin. The Kazakh series and the conclusions are unchanged.")]

trade_sections = f'''<h2>2. Main results</h2><ol>
<li>Trade turnover grew from $15.4 billion in 2020 to $34.1 billion in 2025, by 121%.</li>
<li>China's share of Kazakhstan's foreign trade rose from 18.1% to 23.7%.</li>
<li>Kazakhstan exports mainly ores, oil, copper and uranium, and imports machinery, electronics and vehicles.</li>
<li>The balance moved from a surplus of $2.6 billion in 2020 to a deficit of $3.7 billion in 2025.</li></ol>
<h2>3. Trade by year</h2>
{fig(1, "Kazakhstan's exports to and imports from China, $ billion (Kazakh data)",
     columns([("Exports to China", GREY, EXPORTS), ("Imports from China", CHART_HI, IMPORTS)], YEARS, w=560, h=260, top=22,
             desc="Exports grew from 9.0 to 15.2 billion dollars; imports from 6.4 to 18.9 billion"),
     "Kazakh official statistics, sources 1-6", TRADE["data"])}
<div class="table-title">Table 1. Kazakhstan's goods trade with China, $ billion (Kazakh data)</div>
{table(["", *YEARS],
       [["Exports to China", *EXPORTS], ["Imports from China", *IMPORTS], ["**Total trade", *TURNOVER],
        ["Balance", *[f"{v:+.1f}".replace("-", "−") for v in BALANCE]]])}
<p class="table-note">Sources: {src_link(0, SRC_TRADE)}; {src_link(1, SRC_TRADE)}; {src_link(2, SRC_TRADE)}; {src_link(3, SRC_TRADE)}; {src_link(4, SRC_TRADE)}; {src_link(5, SRC_TRADE)}.</p>
<p>Imports from China nearly tripled, from $6.4 billion to $18.9 billion. Exports rose by about two thirds, from $9.0 billion to $15.2 billion. The balance changed sign in 2023. In 2025 imports grew by 24% and exports by 2%.</p>
<h2>4. Structure of trade</h2>
<figure class="figure"><div class="fig-title">Figure 2. Top five product groups in Kazakhstan's trade with China, 2024, $ billion</div>
<div class="hbars-grid"><div><div class="hbars-head">Exports to China</div>{hbars(TOP_EXPORTS)}</div>
<div><div class="hbars-head">Imports from China</div>{hbars(TOP_IMPORTS, colour=CHART_HI)}</div></div>
<figcaption>Source: {src_link(7, SRC_TRADE)} (Kazakhstan's data reported to UN Comtrade). <a href="../{TRADE["data"]}.xlsx" download>Download the data (XLSX)</a></figcaption></figure>
<p>All five main exports are raw materials or products of primary processing, and their value depends on world commodity prices. All five main imports are finished or semi-finished goods.</p>
<h2>5. Kazakh and Chinese statistics</h2>
<p>The two countries record the same trade differently. In 2025 China reports $48.7 billion of trade with Kazakhstan, and Kazakhstan reports $34.1 billion. Most of the difference is in goods leaving China: $29.7 billion in Chinese data against $18.9 billion arriving in Kazakh data.</p>
<div class="table-title">Table 2. The same trade in two sets of statistics, $ billion</div>
{table(["", *YEARS],
       [["Total trade, Kazakh data", *TURNOVER], ["Total trade, Chinese data", *[f"{v:.1f}" for v in CN_TURNOVER]],
        ["Goods from China, Chinese data", *[f"{v:.1f}" for v in CN_EXPORTS_TO_KZ]], ["Goods from China, Kazakh data", *IMPORTS]])}
<p class="table-note">Sources: Kazakh data, sources 1-6; Chinese data, {src_link(8, SRC_TRADE)}. Differences of this kind usually come from goods passing through third countries, different valuation methods and under-declared imports.</p>
<h2>6. Author's comment</h2><blockquote class="view">{open(os.path.join(HERE, "view2.txt")).read().strip()}</blockquote>'''


report(KASPI, kaspi_sections,
       [("Revenue growth, 2025", "+60%"), ("Net income growth, 2025", "+1%"), ("Net margin, 2024", "41.7%"),
        ("Net margin, 2025", "26.4%"), ("Stake in Hepsiburada", "85%")], SRC_KASPI, disclaimer=True)
report(TRADE, trade_sections,
       (["Indicator, $ billion", "2024", "2025", "Change"],
        [["Total trade, Kazakh data", "30.1", "34.1", "+13.3%"], ["Exports to China", "14.9", "15.2", "+2.0%"],
         ["Imports from China", "15.2", "18.9", "+24.3%"], ["Balance", "−0.3", "−3.7", ""],
         ["Total trade, Chinese data", f"{CN_TURNOVER[4]:.1f}", f"{CN_TURNOVER[5]:.1f}", f"+{(CN_TURNOVER[5] / CN_TURNOVER[4] - 1) * 100:.1f}%"]]),
       SRC_TRADE,
       meta=[("Subject", "Goods trade between Kazakhstan and China"), ("Period", "2020-2025, calendar years"),
             ("Unit", "US$ billion, current prices"),
             ("Data", "Bureau of National Statistics of Kazakhstan; General Administration of Customs of China"),
             ("Published", "8 October 2026; revised 23 October 2026"), ("Format", "Trade brief")])


# ---------- New reports, October 2026 ----------

def view(name):
    """The author's own "My view" text. The section is left out until the file has text in it."""
    path = os.path.join(HERE, name)
    text = open(path).read().strip() if os.path.exists(path) else ""
    return f'<h2>My view</h2><blockquote class="view">{text}</blockquote>' if text else ""


# Halyk Bank: consolidated results for 2023-2025 and the first half of 2026
H_YEARS = ["2023", "2024", "2025"]
H_NI = [693.4, 921.0, 1058.4]      # net income attributable to common shareholders, ₸ billion
H_ROAE = [32.1, 34.0, 32.6]        # return on average equity, %
H_NIM = [6.1, 7.2, 7.1]            # net interest margin, % (2023 as restated in the 2024 release)
H_CI = [19.2, 17.6, 17.5]          # cost-to-income ratio, %
H_H1 = dict(ni=(528.6, 447.6), nim=(7.3, 6.8), ci=(17.2, 19.2))

SRC_HALYK = [
    ("Halyk Bank, Consolidated financial results for the FY 2025 (London Stock Exchange RNS, March 2026)",
     "https://www.investegate.co.uk/announcement/rns/jsc-halyk-bank--37qb/consolidated-financial-results-for-the-fy-2025/9481568",
     "Halyk Bank, FY 2025 results"),
    ("Halyk Bank, Consolidated financial results for the FY 2024 (London Stock Exchange RNS)",
     "https://www.investegate.co.uk/announcement/rns/jsc-halyk-bank--37qb/consolidated-financial-results-for-the-fy-2024/8800201",
     "FY 2024 results"),
    ("Halyk Bank, Consolidated financial results for the FY 2023 (London Stock Exchange RNS)",
     "https://www.investegate.co.uk/announcement/rns/jsc-halyk-bank--37qb/consolidated-financial-results-for-the-fy-2023-/8090484",
     "FY 2023 results"),
    ("Halyk Bank, Interim consolidated results for 1H 2026, press release (18 August 2026)",
     "https://halykbank.com/storage/830/Press-Release.pdf", "1H 2026 results"),
    ("Halyk Bank, Consolidated financial results for the 1Q 2026 (London Stock Exchange RNS, May 2026)",
     "https://www.investegate.co.uk/announcement/rns/jsc-halyk-bank--37qb/consolidated-financial-results-for-the-1q-2026/9572733",
     "1Q 2026 results"),
]

HALYK = dict(
    slug="halyk-bank-2026",
    logos=[("halyk", "Halyk Bank")],
    sector="Banks & fintech",
    url="research/halyk-bank-2026.html",
    tag="Companies",
    kind="Company note",
    title="A Record Year, Then a Squeeze: Halyk Bank in 2025-2026",
    date="17 Oct 2026", date_long="17 October 2026", iso="2026-10-17",
    line="Net income passed ₸1 trillion in 2025, then fell 15% in the first half of 2026.",
    summary=("Halyk Bank, Kazakhstan's largest bank by assets, earned ₸1,058 billion in 2025, 15% more than in 2024, "
             "with a return on equity of 32.6%. In the first half of 2026 net income fell 15.3%. Stricter reserve "
             "requirements from the National Bank, tighter rules on consumer loans and dearer deposits cut the "
             "net interest margin from 7.3% to 6.8%."),
    art=columns([("Net income", GREY, H_NI)], H_YEARS, w=300, h=150, hi=2, top=1250, fmt="{:,.0f}",
                desc="Halyk Bank net income, ₸ billion: 693 in 2023, 921 in 2024, 1,058 in 2025"),
    art_title="Net income, ₸ bn",
    pdf="reports/halyk-bank-2026.pdf", pages=2,
    data="data/halyk-bank-2023-2026",
    og_num="−15%", og_cap="net income in 1H 2026, after a record 2025",
    og_chart=columns([("Net income", GREY, H_NI)], H_YEARS, w=420, h=260, hi=2, top=1250, fmt="{:,.0f}"),
)
HALYK["feat"] = (H_YEARS, "Halyk Bank net income, ₸ billion",
                 columns([("Net income", GREY, H_NI)], H_YEARS, w=520, h=270, hi=2, top=1250, fmt="{:,.0f}",
                         desc="Net income 2023 to 2025"), "Halyk Bank results releases")

data_files(HALYK["data"], "Halyk Bank key figures, 2023 to first half of 2026",
           ["Sources: Halyk Bank consolidated results releases for FY 2023, FY 2024, FY 2025, 1Q 2026 and 1H 2026 (IFRS).",
            "Net income is attributable to common shareholders, in ₸ billion (rounded from ₸ million).",
            "Net interest margin for 2023 is the figure restated in the FY 2024 release (6.1%); the FY 2023 release gave 6.2%.",
            "Half-year ratios are those reported by the bank for the six months, not annualised by the author."],
           [("Annual", ["Indicator", *H_YEARS],
             [["Net income, ₸ billion", *H_NI], ["Return on average equity, %", *H_ROAE],
              ["Net interest margin, %", *H_NIM], ["Cost-to-income ratio, %", *H_CI]]),
            ("First half", ["Indicator", "1H2025", "1H2026"],
             [["Net income, ₸ billion", *H_H1["ni"]], ["Net interest margin, %", *H_H1["nim"]],
              ["Cost-to-income ratio, %", *H_H1["ci"]]])])

HALYK["notes"] = '''<ul class="notes">
<li>All figures come from Halyk Bank's consolidated IFRS results, listed under Sources. Net income is attributable to common shareholders.</li>
<li>Net interest margin is the bank's own measure: net interest income divided by average interest-earning assets. The 2023 figure is the restated 6.1% from the FY 2024 release.</li>
<li>Half-year figures are compared with the same half of 2025, as the bank reports them. Percentage changes are calculated by the author.</li>
</ul>'''

halyk_sections = f'''<h2>Key findings</h2><ol>
<li>Net income rose from ₸693 billion in 2023 to ₸1,058 billion in 2025, up 53% in two years.</li>
<li>Return on average equity stayed above 32% in all three years, peaking at 34.0% in 2024.</li>
<li>In 2025 interest expense grew faster than interest income, 32% against 24%, and the margin slipped from 7.2% to 7.1%.</li>
<li>In the first half of 2026 net income fell 15.3%, to ₸448 billion, and the margin dropped to 6.8%.</li></ol>
{fig(1, "Net income attributable to common shareholders, ₸ billion",
     columns([("Net income", GREY, H_NI)], H_YEARS, hi=2, top=1250, fmt="{:,.0f}",
             desc="Net income rose from 693 billion tenge in 2023 to 921 in 2024 and 1,058 in 2025"),
     src_link(0, SRC_HALYK) + "; " + src_link(1, SRC_HALYK) + "; " + src_link(2, SRC_HALYK), HALYK["data"])}
<h2>How Halyk got to ₸1 trillion</h2>
<p>Halyk earns most of its money the way a classic bank does: it lends at a higher rate than it pays on deposits. In 2025 its interest income grew 24%, to ₸2,695 billion, and its net loans reached ₸13.1 trillion, while customers kept ₸14.3 trillion with the bank.</p>
<p>It is also cheap to run. Operating costs took 17.5% of income in 2025, down from 19.2% in 2023. Together with a margin above 7%, that gave a return on equity of 32.6%.</p>
<p>The warning sign came in the same year. Interest expense grew by 32%, to ₸1,407 billion, faster than interest income, because the bank had to pay more for deposits.</p>
<div class="table-title">Table 1. Halyk Bank key figures</div>
{table(["", *H_YEARS, "1H 2025", "1H 2026"],
       [["**Net income, ₸ billion", *[f"{v:,.0f}" for v in H_NI], *[f"{v:,.0f}" for v in H_H1["ni"]]],
        ["Return on average equity", *[f"{v}%" for v in H_ROAE], "", ""],
        ["Net interest margin", *[f"{v}%" for v in H_NIM], *[f"{v}%" for v in H_H1["nim"]]],
        ["Cost-to-income ratio", *[f"{v}%" for v in H_CI], *[f"{v}%" for v in H_H1["ci"]]]])}
<p class="table-note">2023 margin as restated in the FY 2024 release. Sources: {src_link(0, SRC_HALYK)}; {src_link(1, SRC_HALYK)}; {src_link(2, SRC_HALYK)}; {src_link(3, SRC_HALYK)}.</p>
<h2>What changed in 2026</h2>
<p>Net income for the first six months of 2026 was ₸447.6 billion, against ₸528.6 billion a year earlier. The bank names three causes.</p>
<p>First, the National Bank of Kazakhstan raised minimum reserve requirements, so banks must keep more money at the central bank, where it earns little. Another increase started in April 2026. Halyk says that without this effect its margin would have been 7.2% instead of 6.8%.</p>
<p>Second, the regulator tightened the rules on retail lending. Third, the average rate Halyk pays on customer accounts rose while the average rate on its loans stayed flat. Net interest income grew only 2.6%, to ₸657.6 billion, while interest expense rose 21.6%.</p>
{fig(2, "Net interest margin, %",
     columns([("Net interest margin", GREY, H_NIM + [H_H1["nim"][1]])], H_YEARS + ["1H 2026"], hi=3, top=8.5, fmt="{:.1f}", unit="%",
             desc="Net interest margin 6.1% in 2023, 7.2% in 2024, 7.1% in 2025 and 6.8% in the first half of 2026"),
     src_link(1, SRC_HALYK) + "; " + src_link(0, SRC_HALYK) + "; " + src_link(3, SRC_HALYK), HALYK["data"])}
<p>Costs also took a bigger share: the cost-to-income ratio rose from 17.2% to 19.2%. Lending kept growing, with gross loans up 13.2% over the year to June 2026, and the cost of risk stayed at 1.4%, which the bank calls a normal level. So the fall in profit comes from the price of money, not from bad loans.</p>
<h2>Risks</h2><ol>
<li>The National Bank kept its base rate at 18% in March 2026. If rates stay high longer, deposits stay expensive and the margin stays under pressure.</li>
<li>Further limits on consumer lending would slow the bank's retail loan book.</li>
<li>A slowdown in Kazakhstan's economy would raise the cost of risk, which is now low.</li></ol>
{view("view_halyk.txt")}'''

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
    mark="CN &middot; CA",
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
    pdf="reports/china-central-asia-2025.pdf", pages=2,
    data="data/china-central-asia-trade-2025",
    og_num="$106.3 bn", og_cap="China's trade with Central Asia in 2025",
    og_chart=columns([("China's data", GREY, [r[1] for r in CA_ROWS])], ["KZ", "KG", "UZ", "TM", "TJ"], w=420, h=260, top=56, fmt="{:.1f}"),
)
CA["feat"] = (None, "Trade with China in 2025, $ billion: China's figure and the country's own",
              columns([("China's data", GREY, [r[1] for r in CA_ROWS if r[5]]), ("Country's own data", CHART_HI, [r[5] for r in CA_ROWS if r[5]])],
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
     columns([("China's data", GREY, [r[1] for r in CA_ROWS if r[5]]), ("Country's own data", CHART_HI, [r[5] for r in CA_ROWS if r[5]])],
             [r[0] for r in CA_ROWS if r[5]], w=560, h=260, top=56, fmt="{:.1f}",
             desc="Kazakhstan 48.7 vs 34.1; Kyrgyzstan 27.2 vs 5.0; Uzbekistan 16.1 vs 17.2; Tajikistan 4.3 vs 2.8"),
     src_link(1, SRC_CA) + "; " + src_link(3, SRC_CA) + "; " + src_link(4, SRC_CA) + "; " + src_link(5, SRC_CA), CA["data"])}
<p>For anyone using these numbers, the practical point is to say whose data they are. A headline of "$27 billion of trade with Kyrgyzstan" describes goods leaving China, and a large part of them may end up somewhere else.</p>
{view("view_central_asia.txt")}'''

# Kazatomprom: operating and financial reviews for 2023-2025 and the first half of 2026
U_YEARS = ["2023", "2024", "2025"]
U_PROD = [21112, 23270, 25839]          # production, tU, 100% basis
U_SALES = [18069, 16670, 18494]         # Group U3O8 sales, tU
U_PRICE = [55.09, 69.48, 65.32]         # Group average realized price, $/lb U3O8
U_SPOT = [60.53, 86.28, 72.75]          # average weekly spot price, $/lb U3O8
U_C1 = [13.27, 16.59, 18.06]            # C1 cash cost, attributable, $/lb
U_REV = [1435, 1813, 1803]              # revenue, ₸ billion
U_EBITDA = [829, 1097, 1133]            # adjusted EBITDA, ₸ billion
U_ADJ_NP = [None, 577, 570]             # adjusted net profit attributable to owners, ₸ billion
U_ASIA = [("Asia", 45, 50, 56), ("Americas", 26, 22, 25), ("Europe", 29, 28, 19)]  # % of Group U3O8 sales volume
U_H1 = dict(prod=(12242, 13291), sales=(7625, 7586), price=(58.54, 67.88), spot=(69.11, 85.98), c1=(17.86, 24.48),
            rev=(660.2, 717.8), np=(263.2, 240.4), owners=(202.1, 156.6), met=(59.9, 119.5))

SRC_KAP = [
    ("Kazatomprom, Operating and Financial Review for 2025 (March 2026)",
     "https://www.kazatomprom.kz/storage/86/fy2025_ofr_eng.pdf", "Kazatomprom, 2025 review"),
    ("Kazatomprom, Operating and Financial Review for the first half of 2026 (August 2026)",
     "https://www.kazatomprom.kz/storage/9f/6m_2026_ofr_eng.pdf", "first-half 2026 review"),
    ("Kazatomprom, Operating and Financial Review for 2024 (March 2025)",
     "https://www.kazatomprom.kz/storage/c0/fy2024_ofr_eng.pdf", "2024 review"),
    ("Kazatomprom, Operating and Financial Review for 2023 (March 2024)",
     "https://www.kazatomprom.kz/storage/29/fy2023_ofr_eng.pdf", "2023 review"),
    ("Kazatomprom, 1H2025 Results and 2026 Production Strategy (London Stock Exchange RNS, August 2025)",
     "https://www.investegate.co.uk/announcement/rns/joint-stock-company-national-atomic-company-kazatomprom--kap/kap-1h2025-results-and-2026-production-strategy-/9068901",
     "1H2025 results and 2026 strategy"),
]

KAP = dict(
    slug="kazatomprom-2025",
    logos=[("kazatomprom", "Kazatomprom")],
    sector="Mining & energy",
    url="research/kazatomprom-2025.html",
    tag="Companies",
    kind="Company note",
    title="More Uranium, Higher Costs: Kazatomprom in 2025-2026",
    date="23 Oct 2026", date_long="23 October 2026", iso="2026-10-23",
    line="Output rose 11% in 2025. In early 2026 a new tax and dearer acid raised the cost of each pound by 37%.",
    summary=("Kazatomprom, the world's largest uranium producer, mined 25,839 tonnes of uranium in 2025, 11% more than "
             "in 2024. Revenue still slipped 1%, to ₸1.80 trillion, because the average selling price fell 6% and a "
             "one-off sale of enriched uranium in 2024 did not repeat. In the first half of 2026 the price rose 16%, but "
             "a higher extraction tax, dearer sulphuric acid and a stronger tenge raised cash cost per pound by 37%, "
             "and profit attributable to shareholders fell 23%."),
    art=columns([("Production", GREY, [v / 1000 for v in U_PROD])], U_YEARS, w=300, h=150, hi=2, top=32, fmt="{:.1f}",
                desc="Kazatomprom production, thousand tonnes of uranium: 21.1 in 2023, 23.3 in 2024, 25.8 in 2025"),
    art_title="Production, thousand tU",
    pdf="reports/kazatomprom-2025.pdf", pages=3,
    data="data/kazatomprom-2023-2026",
    og_num="+37%", og_cap="cash cost per pound in 1H 2026, after 11% more uranium in 2025",
    og_chart=columns([("C1 cash cost", GREY, U_C1 + [U_H1["c1"][1]])], U_YEARS + ["1H 2026"], w=420, h=260, hi=3, top=28,
                     fmt="{:.1f}"),
)
KAP["feat"] = (U_YEARS, "Kazatomprom production, thousand tonnes of uranium",
               columns([("Production", GREY, [v / 1000 for v in U_PROD])], U_YEARS, w=520, h=270, hi=2, top=32, fmt="{:.1f}",
                       desc="Production 2023 to 2025"), "Kazatomprom operating and financial reviews")

data_files(KAP["data"], "Kazatomprom key figures, 2023 to first half of 2026",
           ["Sources: Kazatomprom operating and financial reviews for 2023, 2024, 2025 and the first half of 2026.",
            "Production is on a 100% basis (all mines the Group consolidates or holds a stake in, counted in full).",
            "Group sales and the Group average realized price cover U3O8 only, not enriched uranium or fuel pellets.",
            "Spot price is the average of weekly spot prices reported by Kazatomprom from third-party price providers.",
            "C1 cash cost is on an attributable basis, in US dollars per pound of U3O8, as reported by the company.",
            "Adjusted net profit attributable to owners excludes one-off items. It is not shown for 2023 because the 2023 report used a different adjusted measure.",
            "Sales by region are the company's own split by the domicile of the buyer's ultimate owner or decision-maker, in % of Group sales volume."],
           [("Annual", ["Indicator", *U_YEARS],
             [["Production, tU (100% basis)", *U_PROD], ["Group U3O8 sales, tU", *U_SALES],
              ["Group average realized price, $/lb", *U_PRICE], ["Average weekly spot price, $/lb", *U_SPOT],
              ["C1 cash cost (attributable), $/lb", *U_C1],
              ["Revenue, ₸ billion", *U_REV], ["Adjusted EBITDA, ₸ billion", *U_EBITDA],
              ["Adjusted net profit attributable to owners, ₸ billion", *["" if v is None else v for v in U_ADJ_NP]]]),
            ("First half", ["Indicator", "1H2025", "1H2026"],
             [["Production, tU (100% basis)", *U_H1["prod"]], ["Group U3O8 sales, tU", *U_H1["sales"]],
              ["Group average realized price, $/lb", *U_H1["price"]], ["Average weekly spot price, $/lb", *U_H1["spot"]],
              ["C1 cash cost (attributable), $/lb", *U_H1["c1"]], ["Revenue, ₸ billion", *U_H1["rev"]],
              ["Net profit, ₸ billion", *U_H1["np"]], ["Net profit attributable to owners, ₸ billion", *U_H1["owners"]],
              ["Mineral extraction tax, ₸ billion", *U_H1["met"]]]),
            ("Sales by region", ["Region, % of Group sales", *U_YEARS], [list(r) for r in U_ASIA])])

KAP["notes"] = '''<ul class="notes">
<li>All figures come from Kazatomprom's own operating and financial reviews, listed under Sources. Production is on a 100% basis, which counts every mine the company consolidates or holds a stake in at full volume.</li>
<li>Sales volumes and the average realized price cover natural uranium (U3O8) only. Enriched uranium sold to Ulba-FA in 2024 is in revenue but not in these volumes.</li>
<li>Reported net profit for 2024 includes a one-off gain of ₸296 billion from taking control of the Budenovskoye joint venture, so annual figures use the company's adjusted net profit attributable to owners.</li>
<li>"Revenue without enriched uranium" and the price-minus-cost comparison are calculated by the author from the reported figures, as are percentage changes.</li>
</ul>'''

kap_sections = f'''<h2>Key findings</h2><ol>
<li>Production rose 11% in 2025, to 25,839 tonnes of uranium (tU), and is 22% higher than in 2023.</li>
<li>Revenue slipped 1%, to ₸1,803 billion. Natural uranium sales grew 16%, but ₸252 billion of enriched uranium sold in 2024 did not repeat.</li>
<li>Asia took 56% of the uranium the Group sold in 2025, up from 45% in 2023.</li>
<li>In the first half of 2026 the realized price rose 16%, cash cost per pound rose 37%, and profit attributable to shareholders fell 23%.</li></ol>
{fig(1, "Production, thousand tonnes of uranium (100% basis)",
     columns([("Production", GREY, [v / 1000 for v in U_PROD])], U_YEARS, hi=2, top=32, fmt="{:.1f}",
             desc="Production rose from 21.1 thousand tonnes in 2023 to 23.3 in 2024 and 25.8 in 2025"),
     src_link(0, SRC_KAP) + "; " + src_link(2, SRC_KAP), KAP["data"])}
<h2>The world's largest producer is still growing</h2>
<p>Kazatomprom says its own share of output was 20% of the world's primary uranium supply in 2025, and that all mines in Kazakhstan together produced about 39% of global output, citing the consultancy UxC. It sold 18,494 tU of natural uranium in 2025, 11% more than a year earlier. That part of the business earned ₸1,638 billion, up 16%, and made up 91% of revenue against 78% in 2024.</p>
<p>The rest of the 2024 revenue was enriched uranium sold to Ulba-FA, a fuel plant in Ust-Kamenogorsk: ₸252 billion, or 14% of the total. In 2025 this line was zero. Without it, 2024 revenue would have been about ₸1,561 billion, and 2025 would show growth of about 15% instead of a 1% fall.</p>
<p>Adjusted profit attributable to shareholders was almost unchanged at ₸570 billion. In July 2026 the company paid ₸335 billion of dividends for 2025, about 59% of that profit.</p>
<h2>More of it goes to Asia</h2>
<p>Asia's share of the Group's sales rose from 45% in 2023 to 56% in 2025, while Europe's fell from 29% to 19% (Table 1). The company splits sales by where the buyer's owner or decision-maker is based, not by country, so it does not show China on its own. China is visible in other parts of the report. Uranium for China leaves by rail through Alashankou, on the Kazakh-Chinese border. And Ulba-FA, a joint venture with Chinese partners set up in 2021, delivered fuel assemblies with slightly more than 200 tonnes of low-enriched uranium to Chinese nuclear plants in 2025, its full design capacity.</p>
<div class="table-title">Table 1. Group uranium sales by region, % of volume</div>
{table(["", *U_YEARS], [[n, f"{a}%", f"{b}%", f"{c}%"] for n, a, b, c in U_ASIA])}
<p class="table-note">Region is the domicile of the buyer's ultimate owner or decision-maker. Source: {src_link(0, SRC_KAP)}.</p>
<p>Shipments to the West go another way. In 2025, 48% of Western-bound uranium from Kazakhstan travelled by the Trans-Caspian route through Aktau rather than through Russia.</p>
<h2>The company's price follows the market slowly</h2>
<p>Most of Kazatomprom's uranium is sold under long-term contracts, and many of them follow the spot price with a delay. When spot jumped in 2024, the company's price rose less, and when spot fell 16% in 2025, its price fell only 6% (Figure 2). In the first half of 2026 the gap opened again: spot averaged $85.98 per pound, while Kazatomprom received $67.88.</p>
{fig(2, "Kazatomprom's average realized price and the spot price, $ per pound of U3O8",
     columns([("Kazatomprom realized price", GREY, U_PRICE + [U_H1["price"][1]]), ("Spot price", CHART_HI, U_SPOT + [U_H1["spot"][1]])],
             U_YEARS + ["1H 2026"], w=560, h=260, top=100, fmt="{:.0f}",
             desc="Realized price 55, 69, 65 and 68 dollars per pound; spot 61, 86, 73 and 86"),
     src_link(0, SRC_KAP) + "; " + src_link(1, SRC_KAP), KAP["data"])}
<h2>In 2026 costs are rising faster than the price</h2>
<p>In the first six months of 2026 revenue rose 9%, to ₸718 billion, because the realized price climbed 16%. But the cash cost of producing a pound (C1, on the company's attributable basis) rose 37%, from $17.86 to $24.48 (Figure 3). Of the $9.34 gain in price, $6.62 went on higher costs.</p>
{fig(3, "C1 cash cost, $ per pound of U3O8 (attributable basis)",
     columns([("C1 cash cost", GREY, U_C1 + list(U_H1["c1"]))], U_YEARS + ["1H 2025", "1H 2026"], w=560, h=250, hi=4, top=28,
             fmt="{:.2f}", desc="C1 cash cost 13.27 in 2023, 16.59 in 2024, 18.06 in 2025, 17.86 in 1H 2025 and 24.48 in 1H 2026"),
     src_link(1, SRC_KAP) + "; " + src_link(0, SRC_KAP) + "; " + src_link(2, SRC_KAP), KAP["data"])}
<p>The company names three causes. From January 2026 the mineral extraction tax depends on how much each licence produces and on the uranium price; Kazatomprom's average rate rose from a flat 9% to 12.4%, and the tax it accrued doubled, to ₸120 billion. Sulphuric acid, which is pumped underground to dissolve the uranium, cost 39% more per tonne because of shortages in Kazakhstan. And a stronger tenge makes local costs bigger in dollars.</p>
<p>The acid problem will last longer than planned. Kazatomprom is building its own acid plant, but construction was suspended after possible paleontological finds on the site, and the start has moved from early 2027 to between the third quarter of 2027 and the first quarter of 2028.</p>
<p>Net profit fell 9%, to ₸240 billion, mostly because of exchange-rate losses and higher finance costs. The share left for Kazatomprom's own shareholders fell further, by 23%, to ₸157 billion, because more of the profit of partly owned mines went to their other owners. In August the company cut its 2026 revenue guidance from ₸2,200-2,300 billion to ₸2,100-2,200 billion and raised its C1 cost guidance to $25.50-27.00 per pound.</p>
<div class="table-title">Table 2. Kazatomprom key figures</div>
{table(["", *U_YEARS, "1H 2025", "1H 2026"],
       [["Production, tU", *map(n0, U_PROD), *map(n0, U_H1["prod"])],
        ["Group sales, tU", *map(n0, U_SALES), *map(n0, U_H1["sales"])],
        ["Realized price, $/lb", *[f"{v:.2f}" for v in U_PRICE], *[f"{v:.2f}" for v in U_H1["price"]]],
        ["C1 cash cost, $/lb", *[f"{v:.2f}" for v in U_C1], *[f"{v:.2f}" for v in U_H1["c1"]]],
        ["**Revenue, ₸ billion", *map(n0, U_REV), *[f"{v:.0f}" for v in U_H1["rev"]]],
        ["Adjusted EBITDA, ₸ billion", *map(n0, U_EBITDA), "363", "371"],
        ["**Profit to shareholders, ₸ billion", "n/a", *map(n0, U_ADJ_NP[1:]), *[f"{v:.0f}" for v in U_H1["owners"]]]])}
<p class="table-note">Annual profit to shareholders is adjusted for one-off items; half-year figures had none. Sources: {src_link(0, SRC_KAP)}; {src_link(1, SRC_KAP)}; {src_link(2, SRC_KAP)}; {src_link(3, SRC_KAP)}.</p>
<h2>Growing more slowly on purpose</h2>
<p>Kazatomprom is not trying to produce as much as its licences allow. In August 2025 it said its nominal 2026 production level would be about 10% lower, 29,697 tU instead of 32,777 tU. Its 2026 guidance is 27,500 to 29,000 tU, and the company says this depends on sulphuric acid being available.</p>
<h2>Risks</h2><ol>
<li>Profit depends on the uranium price, which fell 16% on the spot market in 2025 and rose again in 2026.</li>
<li>The new extraction tax rises with both output and price, so it takes a larger share when the market is strong.</li>
<li>Acid shortages could limit production until the company's own plant starts, now no earlier than late 2027.</li>
<li>A stronger tenge lowers revenue in tenge and raises costs in dollars.</li></ol>
{view("view_kazatomprom.txt")}'''


report(KAP, kap_sections,
       [("Production, 2025", "25,839 tU"), ("Production growth", "+11%"), ("Revenue, 2025", "₸1.80 trn"),
        ("Cash cost per lb, 1H 2026", "+37%"), ("Profit to shareholders, 1H 2026", "−23%")], SRC_KAP, disclaimer=True)
# China and Russia: GACC monthly bulletin, December issue of each year (US$ thousand -> $ billion)
RU_RAW = [(107765163, 50584583, 57180581), (146887244, 67565332, 79321912), (190271620, 76122649, 114148971),
          (240111548, 110972451, 129139097), (244819535, 115499179, 129320356), (228104895, 103309028, 124795867)]
RU_TOTAL = [round(a / 1e6, 1) for a, _, _ in RU_RAW]
RU_EXP = [round(b / 1e6, 1) for _, b, _ in RU_RAW]      # China's exports to Russia
RU_IMP = [round(c / 1e6, 1) for _, _, c in RU_RAW]      # China's imports from Russia
RU_BAL = [round((b - c) / 1e6, 1) for _, b, c in RU_RAW]
# Table (15)/(16), HS chapters, 2025, $ billion
RU_TOP_EXP = [("Machinery (HS 84)", 26.55), ("Electrical equipment (HS 85)", 14.76), ("Vehicles (HS 87)", 13.10),
              ("Plastics (HS 39)", 4.15), ("Optical and medical instruments (HS 90)", 3.45)]
RU_TOP_IMP = [("Oil, gas and coal (HS 27)", 78.73), ("Ores (HS 26)", 8.45), ("Aluminium (HS 76)", 5.90),
              ("Copper (HS 74)", 4.88), ("Precious metals and stones (HS 71)", 4.66)]
RU_CHANGE = [  # HS chapter, 2021, 2024, 2025
    ("Exports to Russia: vehicles (HS 87)", 4.28, 25.48, 13.10),
    ("Exports to Russia: machinery (HS 84)", 14.71, 27.31, 26.55),
    ("Imports from Russia: oil, gas and coal (HS 27)", 53.54, 95.00, 78.73),
    ("Imports from Russia: ores (HS 26)", None, 5.51, 8.45),
    ("Imports from Russia: aluminium (HS 76)", None, 3.58, 5.90),
    ("Imports from Russia: copper (HS 74)", None, 3.01, 4.88),
]

SRC_RU = [
    ("General Administration of Customs of China, Monthly Bulletin, table (2) Imports and Exports by Country (Region) of Origin/Destination, December 2025",
     "http://english.customs.gov.cn/Statics/ef1a478f-8a43-4b51-9690-fb975762a2c2.html", "GACC, table (2), 2025"),
    ("General Administration of Customs of China, Monthly Bulletin, table (2), December 2024",
     "http://english.customs.gov.cn/Statics/a5b4fa86-46e4-4195-a0c0-5c45ade1cb38.html", "table (2), 2024"),
    ("General Administration of Customs of China, Monthly Bulletin, table (15) Exports by Selected Countries (Regions) and by HS Divisions, December 2025",
     "http://english.customs.gov.cn/Statics/bdb2986b-8011-4df6-b54e-fdc487c23000.html", "GACC, table (15), 2025"),
    ("General Administration of Customs of China, Monthly Bulletin, table (16) Imports by Selected Countries (Regions) and by HS Divisions, December 2025",
     "http://english.customs.gov.cn/Statics/67b0f2b4-20f2-405b-bd3c-d82f58ca29f6.html", "GACC, table (16), 2025"),
    ("General Administration of Customs of China, Monthly Bulletin, tables (15) and (16), December 2024",
     "http://english.customs.gov.cn/Statics/7e3d455f-0c02-4821-bf96-d556fde0071e.html", "tables (15) and (16), 2024"),
    ("General Administration of Customs of China, Monthly Bulletin, archive of tables for 2020-2025",
     "http://english.customs.gov.cn/statics/report/monthly2025.html", "GACC archive"),
    ("Free Policy Briefs (FREE Network), Russia's Data Warfare (April 2023)",
     "https://freepolicybriefs.org/2023/04/18/russia-data-warfare/", "Free Policy Briefs"),
]

RU = dict(
    slug="china-russia-trade-2025",
    mark="CN &middot; RU",
    url="research/china-russia-trade-2025.html",
    tag="Trade",
    kind="Trade brief",
    title="Fewer Cars, Cheaper Oil: China's Trade with Russia, 2020-2025",
    date="23 Oct 2026", date_long="23 October 2026", iso="2026-10-23",
    line="Trade fell 6.9% in 2025, to $228.1 billion. China's car exports to Russia almost halved.",
    summary=("According to the General Administration of Customs of China, trade between China and Russia fell 6.9% in 2025, "
             "to $228.1 billion. It was the first fall since 2020. China's exports to Russia fell 10.4%, to $103.3 billion, "
             "and its imports from Russia fell 3.9%, to $124.8 billion. Vehicles explain almost all of the fall in exports: "
             "they dropped from $25.5 billion to $13.1 billion. On the import side, oil, gas and coal fell by $16.3 billion, "
             "while metals and ores rose. Russia has not published its own trade by country since 2022."),
    art=columns([("Total trade", GREY, RU_TOTAL)], YEARS, w=300, h=150, hi=5, top=270, fmt="{:.0f}",
                desc="China-Russia trade, $ billion, 2020 to 2025: 108, 147, 190, 240, 245, 228"),
    art_title="Trade, $ bn (Chinese data)",
    pdf="reports/china-russia-trade-2025.pdf", pages=2,
    data="data/china-russia-trade-2020-2025",
    og_num="−6.9%", og_cap="China-Russia trade in 2025, the first fall since 2020",
    og_chart=columns([("Total trade", GREY, RU_TOTAL)], YEARS, w=420, h=260, hi=5, top=270, fmt="{:.0f}"),
)
RU["feat"] = (YEARS, "China's trade with Russia, $ billion (Chinese customs data)",
              columns([("Exports to Russia", GREY, RU_EXP), ("Imports from Russia", CHART_HI, RU_IMP)], YEARS, w=520, h=270, top=140,
                      fmt="{:.0f}", desc="China's exports to and imports from Russia, 2020 to 2025"),
              "General Administration of Customs of China")

data_files(RU["data"], "China's goods trade with Russia, 2020-2025 ($ billion, Chinese customs data)",
           ["Source: General Administration of Customs of China (GACC), Monthly Bulletin, tables (2), (15) and (16), December issue of each year.",
            "Values converted by the author from US$ thousand to US$ billion. Balance = China's exports minus China's imports.",
            "Growth rates in the text are those reported by GACC, which compares with revised figures for the previous year; growth by product is calculated by the author.",
            "Russia's customs service has not published trade by partner country since 2022, so no Russian series is given."],
           [("Annual", ["Indicator", *YEARS],
             [["Total trade", *RU_TOTAL], ["China's exports to Russia", *RU_EXP], ["China's imports from Russia", *RU_IMP],
              ["Balance (China's exports minus imports)", *RU_BAL]]),
            ("Top products 2025", ["Flow", "Product group (HS chapter)", "$ billion"],
             [["China's export to Russia", a, b] for a, b in RU_TOP_EXP] + [["China's import from Russia", a, b] for a, b in RU_TOP_IMP]),
            ("Changes by product", ["Product group", "2021", "2024", "2025"],
             [[n, "" if a is None else a, b, c] for n, a, b, c in RU_CHANGE])])

RU["notes"] = '''<ul class="notes">
<li>All figures are China's customs data (General Administration of Customs of China, GACC), Monthly Bulletin, December issue of each year: table (2) for totals, tables (15) and (16) for product groups by HS chapter.</li>
<li>Values are converted from US$ thousand to US$ billion. Growth rates for totals are those published by GACC, which compares with revised data for the previous year, so they can differ slightly from a calculation on the figures shown. Growth by product and the comparison with Kazakhstan are calculated by the author.</li>
<li>Russia's Federal Customs Service stopped publishing trade by partner country in 2022, so this brief uses one source only. Chinese data record goods by country of origin and destination and may differ from what Russia would report.</li>
</ul>'''

_ru_view = os.path.join(HERE, "view_china_russia.txt")
_ru_view = open(_ru_view).read().strip() if os.path.exists(_ru_view) else ""
ru_sections = f'''<h2>2. Main results</h2><ol>
<li>Trade fell 6.9% in 2025, to $228.1 billion, after a record $244.8 billion in 2024.</li>
<li>China's exports of vehicles to Russia fell from $25.5 billion to $13.1 billion, a drop almost as large as the fall in all its exports to Russia.</li>
<li>China's imports of oil, gas and coal from Russia fell 17%, to $78.7 billion. They still made up 63% of everything China bought from Russia.</li>
<li>China's trade with Kazakhstan grew 11% in the same year, to $48.7 billion.</li></ol>
<h2>3. Trade by year</h2>
{fig(1, "China's exports to and imports from Russia, $ billion",
     columns([("China's exports to Russia", GREY, RU_EXP), ("China's imports from Russia", CHART_HI, RU_IMP)], YEARS, w=560, h=270, top=140,
             fmt="{:.0f}", desc="Exports grew from 51 to 115 billion dollars in 2024 and fell to 103 in 2025; imports grew from 57 to 129 and fell to 125"),
     src_link(5, SRC_RU), RU["data"])}
<div class="table-title">Table 1. China's goods trade with Russia, $ billion</div>
{table(["", *YEARS],
       [["China's exports to Russia", *[f"{v:.1f}" for v in RU_EXP]], ["China's imports from Russia", *[f"{v:.1f}" for v in RU_IMP]],
        ["**Total trade", *[f"{v:.1f}" for v in RU_TOTAL]], ["Balance", *[f"{v:+.1f}".replace("-", "−") for v in RU_BAL]]])}
<p class="table-note">Balance is China's exports minus China's imports; a negative figure means Russia sold China more than it bought. Sources: {src_link(0, SRC_RU)}; {src_link(1, SRC_RU)}; {src_link(5, SRC_RU)}.</p>
<p>Trade more than doubled between 2020 and 2024, from $107.8 billion to $244.8 billion, and most of the growth came in 2022 and 2023. China buys more from Russia than it sells: the gap was $21.5 billion in 2025. In 2025 Russia accounted for 3.6% of China's foreign trade.</p>
<h2>4. Structure of trade, 2025</h2>
<figure class="figure"><div class="fig-title">Figure 2. Top five product groups in China's trade with Russia, 2025, $ billion</div>
<div class="hbars-grid"><div><div class="hbars-head">China's exports to Russia</div>{hbars(RU_TOP_EXP)}</div>
<div><div class="hbars-head">China's imports from Russia</div>{hbars(RU_TOP_IMP, colour=CHART_HI)}</div></div>
<figcaption>Source: {src_link(2, SRC_RU)}; {src_link(3, SRC_RU)}. <a href="../{RU["data"]}.xlsx" download>Download the data (XLSX)</a></figcaption></figure>
<p>China sells Russia mainly machinery, electrical equipment and vehicles, which together made up 53% of its exports to Russia in 2025. It buys mainly fuel: oil, gas and coal were 63% of its imports from Russia. The pattern is the same as in Kazakhstan's trade with China, on a larger scale.</p>
<h2>5. What changed in 2025</h2>
<div class="table-title">Table 2. Selected product groups, $ billion</div>
{table(["", "2021", "2024", "2025", "Change, 2025"],
       [[n, "" if a is None else f"{a:.2f}", f"{b:.2f}", f"{c:.2f}", f"{(c / b - 1) * 100:+.0f}%".replace("-", "−")] for n, a, b, c in RU_CHANGE])}
<p class="table-note">HS chapters from GACC tables (15) and (16). Sources: {src_link(2, SRC_RU)}; {src_link(3, SRC_RU)}; {src_link(4, SRC_RU)}. 2021 shown for vehicles, machinery and fuel only.</p>
<p>China's vehicle exports to Russia grew six times between 2021 and 2024, from $4.3 billion to $25.5 billion, and then fell by almost half in 2025. The fall of $12.4 billion is about the same as the fall in all China's exports to Russia, $12.2 billion. Machinery, the largest export group, was almost unchanged.</p>
<p>On the import side, the value of oil, gas and coal fell by $16.3 billion. Imports of ores, aluminium and copper rose by more than 50% each, which kept the overall fall in imports to 3.9%.</p>
<h2>6. Comparison with Kazakhstan</h2>
<div class="table-title">Table 3. China's trade with Russia and Kazakhstan, $ billion (Chinese data)</div>
{table(["", "2020", "2024", "2025", "Change, 2025", "Change since 2020"],
       [["Russia", f"{RU_TOTAL[0]:.1f}", f"{RU_TOTAL[4]:.1f}", f"{RU_TOTAL[5]:.1f}", "−6.9%", f"+{(RU_TOTAL[5] / RU_TOTAL[0] - 1) * 100:.0f}%"],
        ["Kazakhstan", f"{CN_TURNOVER[0]:.1f}", f"{CN_TURNOVER[4]:.1f}", f"{CN_TURNOVER[5]:.1f}", "+11.0%", f"+{(CN_TURNOVER[5] / CN_TURNOVER[0] - 1) * 100:.0f}%"]])}
<p class="table-note">Change in 2025 as published by GACC. Source: {src_link(0, SRC_RU)}.</p>
<p>China's trade with Kazakhstan is about a fifth of its trade with Russia, but it has grown faster since 2020 and kept growing in 2025. For both neighbours China sells manufactured goods and buys raw materials.</p>
<h2>7. A note on the data</h2>
<p>This brief uses one set of statistics. Russia's Federal Customs Service stopped publishing trade by partner country in 2022 ({src_link(6, SRC_RU)}), so Chinese figures cannot be checked against Russian ones, as they were for Kazakhstan in an earlier brief. Chinese data show where goods were declared to go, not where they were finally used.</p>
{f'<h2>8. Author{chr(39)}s comment</h2><blockquote class="view">{_ru_view}</blockquote>' if _ru_view else ""}'''

report(RU, ru_sections,
       (["Indicator, $ billion", "2024", "2025", "Change"],
        [["Total trade", f"{RU_TOTAL[4]:.1f}", f"{RU_TOTAL[5]:.1f}", "−6.9%"],
         ["China's exports to Russia", f"{RU_EXP[4]:.1f}", f"{RU_EXP[5]:.1f}", "−10.4%"],
         ["China's imports from Russia", f"{RU_IMP[4]:.1f}", f"{RU_IMP[5]:.1f}", "−3.9%"],
         ["Balance", f"{RU_BAL[4]:+.1f}".replace("-", "−"), f"{RU_BAL[5]:+.1f}".replace("-", "−"), ""],
         ["Vehicles exported to Russia", "25.5", "13.1", "−49%"]]),
       SRC_RU,
       meta=[("Subject", "Goods trade between China and Russia"), ("Period", "2020-2025, calendar years"),
             ("Unit", "US$ billion, current prices"), ("Data", "General Administration of Customs of China"),
             ("Published", "23 October 2026"), ("Format", "Trade brief")])

# Geely Automobile Holdings (HKEX: 175): annual reports 2025, interim report 2026, monthly sales announcements
G_YEARS = ["2023", "2024", "2025"]
G_REV = [224.8, 275.9, 345.2]           # revenue, RMB billion (2023-2024 as restated in the 2025 report)
G_NP = [5.49, 16.81, 16.85]             # profit attributable to owners of the parent, RMB billion
G_CORE = [None, 10.61, 14.41]           # core profit attributable to owners, RMB billion (company measure)
G_UNITS = [1686516, 2176567, 3024567]   # total sales volume, units
G_H1 = dict(rev=(151.4, 173.6), np=(9.26, 9.09), core=(6.62, 9.68), units=(None, 1422958), gm=(16.3, 17.9),
            zeekr=(None, 178370), exports=(None, 474228))
G_9M = [  # brand, Jan-Sep 2025, Jan-Sep 2026 (units, unaudited)
    ("Geely brand", 1785117, 1750960), ("of which Galaxy", 874985, 877184), ("Lynk & Co", 241472, 196117),
    ("Zeekr", 143600, 288404), ("**Total", 2170189, 2235481), ("Exports (included above)", 296128, 797670)]

SRC_GEELY = [
    ("Geely Automobile Holdings, Annual Report 2025 (April 2026)",
     "https://www.geelyauto.com.hk/wp-content/uploads/2026/04/e00175_2025-annual-report.pdf", "Geely, Annual Report 2025"),
    ("Geely Automobile Holdings, Interim Report 2026 (August 2026)",
     "https://www.geelyauto.com.hk/wp-content/uploads/2026/08/e00175_2026-interim-report.pdf", "Interim Report 2026"),
    ("Geely Automobile Holdings, press release on the 2025 annual results (18 March 2026)",
     "https://www.geelyauto.com.hk/wp-content/uploads/2026/03/e_20260318_Press-Release_Geely_2025-Annual-Results.pdf", "2025 results release"),
    ("Geely Automobile Holdings, Unaudited sales volume in September 2026 (1 October 2026)",
     "https://www.geelyauto.com.hk/wp-content/uploads/2026/10/20261001-Geely-Sep-2026-Sales-Announcement_ENG.pdf", "September 2026 sales"),
]

GEELY = dict(
    slug="geely-2026",
    logos=[("geely", "Geely Automobile Holdings"), ("zeekr", "Zeekr")],
    url="research/geely-2026.html",
    sector="Manufacturing",
    tag="Companies",
    kind="Company note",
    title="Selling Abroad and Selling Up: Geely Auto and Zeekr in 2025-2026",
    date="23 Oct 2026", date_long="23 October 2026", iso="2026-10-23",
    line="China's car market fell by a quarter in early 2026. Geely's exports grew 158% and Zeekr's sales almost doubled.",
    summary=("Geely Automobile, the Hong Kong-listed carmaker that owns the Geely, Lynk & Co and Zeekr brands, sold 3.02 million "
             "cars in 2025, 39% more than in 2024, and its revenue rose 25% to RMB345 billion. In December 2025 it bought out the "
             "minority shareholders of Zeekr, its luxury electric brand, and took it off the New York Stock Exchange. In the "
             "first half of 2026, when car sales inside China fell 24%, Geely kept its total sales flat by selling abroad: "
             "exports grew 158% and Zeekr's sales 97%. Revenue rose 15% and core profit 46%, although reported profit fell 2%."),
    art=columns([("Revenue", GREY, G_REV)], G_YEARS, w=300, h=150, hi=2, top=400, fmt="{:.0f}",
                desc="Geely revenue, RMB billion: 225 in 2023, 276 in 2024, 345 in 2025"),
    art_title="Revenue, RMB bn",
    pdf="reports/geely-2026.pdf", pages=2,
    data="data/geely-2023-2026",
    og_num="+158%", og_cap="Geely's exports in 1H 2026, as car sales in China fell 24%",
    og_chart=columns([("Revenue", GREY, G_REV)], G_YEARS, w=420, h=260, hi=2, top=400, fmt="{:.0f}"),
)
GEELY["feat"] = (G_YEARS, "Geely Automobile revenue, RMB billion",
                 columns([("Revenue", GREY, G_REV)], G_YEARS, w=520, h=270, hi=2, top=400, fmt="{:.0f}",
                         desc="Revenue 2023 to 2025"), "Geely Automobile annual report 2025")

data_files(GEELY["data"], "Geely Automobile key figures, 2023 to September 2026",
           ["Sources: Geely Automobile Holdings Annual Report 2025, Interim Report 2026 and monthly sales announcements.",
            "Revenue for 2023 and 2024 is as restated in the 2025 annual report. Profit is attributable to owners of the parent.",
            "Core profit is the company's own measure: profit attributable to owners without foreign exchange gains or losses, impairment of non-financial assets and gains on disposals.",
            "Monthly sales figures are unaudited. Exports are sales outside mainland China, including Hong Kong, Macao and Taiwan."],
           [("Annual", ["Indicator", *G_YEARS],
             [["Revenue, RMB billion", *G_REV], ["Profit attributable to owners, RMB billion", *G_NP],
              ["Core profit attributable to owners, RMB billion", *["" if v is None else v for v in G_CORE]],
              ["Total sales volume, units", *G_UNITS]]),
            ("First half", ["Indicator", "1H2025", "1H2026"],
             [["Revenue, RMB billion", *G_H1["rev"]], ["Profit attributable to owners, RMB billion", *G_H1["np"]],
              ["Core profit attributable to owners, RMB billion", *G_H1["core"]], ["Gross margin, %", *G_H1["gm"]],
              ["Total sales volume, units", "", G_H1["units"][1]], ["Zeekr sales, units", "", G_H1["zeekr"][1]],
              ["Export sales, units", "", G_H1["exports"][1]]]),
            ("January-September", ["Brand", "Jan-Sep 2025", "Jan-Sep 2026"],
             [[n.replace("**", ""), a, b] for n, a, b in G_9M])])

GEELY["notes"] = '''<ul class="notes">
<li>All figures come from Geely Automobile Holdings' own reports, listed under Sources. Money is in Chinese yuan (RMB). Revenue for 2023 and 2024 is as restated in the 2025 annual report.</li>
<li>"Core profit" is the company's own measure. It removes foreign exchange gains and losses, impairment of non-financial assets and one-off gains on disposals. In 2024 reported profit included a gain of RMB9.35 billion on disposals.</li>
<li>Sales volumes for January to September are unaudited monthly figures. Zeekr no longer publishes its own accounts after leaving the New York Stock Exchange, so its sales volume is the only Zeekr figure available.</li>
<li>Percentage changes and the sales needed to meet the 2026 target are calculated by the author.</li>
</ul>'''

geely_sections = f'''<h2>Key findings</h2><ol>
<li>Geely sold 3.02 million cars in 2025, up 39%, and revenue rose 25%, to RMB345 billion. Reported profit was flat at RMB16.9 billion, while core profit rose 36%.</li>
<li>In December 2025 Geely bought the rest of Zeekr for about RMB5.3 billion in cash and 777 million new Geely shares.</li>
<li>In the first half of 2026 exports grew 158% and Zeekr sales 97%, while car sales inside China fell 24%.</li>
<li>After nine months of 2026 Geely had sold 2.24 million cars. To reach its target of 3.45 million it needs about 405,000 a month in the last quarter.</li></ol>
{fig(1, "Revenue, RMB billion",
     columns([("Revenue", GREY, G_REV)], G_YEARS, hi=2, top=400, fmt="{:.1f}",
             desc="Revenue rose from 224.8 billion yuan in 2023 to 275.9 in 2024 and 345.2 in 2025"),
     src_link(0, SRC_GEELY), GEELY["data"])}
<h2>A record year with flat profit</h2>
<p>Geely makes cars under three brands: Geely, whose electric and hybrid line is called Galaxy; Lynk &amp; Co in the middle of the market; and Zeekr at the top. In 2025 Galaxy sales rose 150%, to 1.24 million, and electric and plug-in hybrid cars made up 56% of all sales. Sales in China grew 48%, but exports grew only 1%, to 420,097 cars.</p>
<p>Reported profit attributable to shareholders was almost unchanged, RMB16.85 billion against RMB16.81 billion. The 2024 figure was lifted by a one-off gain of RMB9.35 billion on disposals. Without such items, the company's core profit rose 36%, to RMB14.41 billion. The gross margin stayed close to 16.6%, which the company links to fierce price competition in China. The dividend rose from HK$0.33 to HK$0.50 a share.</p>
{fig(2, "Reported and core profit attributable to shareholders, RMB billion",
     columns([("Reported profit", GREY, [G_NP[1], G_NP[2], G_H1["np"][0], G_H1["np"][1]]),
              ("Core profit", CHART_HI, [G_CORE[1], G_CORE[2], G_H1["core"][0], G_H1["core"][1]])],
             ["2024", "2025", "1H 2025", "1H 2026"], w=560, h=260, top=20, fmt="{:.1f}",
             desc="Reported profit 16.8, 16.9, 9.3 and 9.1 billion yuan; core profit 10.6, 14.4, 6.6 and 9.7"),
     src_link(0, SRC_GEELY) + "; " + src_link(1, SRC_GEELY), GEELY["data"])}
<h2>Why Geely bought out Zeekr</h2>
<p>Zeekr's shares traded in New York, while Geely kept a majority stake. In May 2025 Geely proposed to buy the remaining shares, and the deal closed on 22 December 2025. Zeekr shareholders could take US$2.687 in cash or 1.23 Geely shares for each Zeekr share. In the end Geely issued 777 million new shares and paid about RMB5.3 billion in cash, and Zeekr left the New York Stock Exchange.</p>
<p>Geely explains the deal by its "One Geely" plan: to stop its brands competing for the same buyers and to stop paying twice for the same factories and research. Before the deal Zeekr had also taken over Lynk &amp; Co. One sign of the change is in the balance sheet: the equity held by outside shareholders in Geely's subsidiaries fell from RMB7.5 billion to RMB1.2 billion in 2025.</p>
<p>Zeekr sold 224,133 cars in 2025, only 1% more than in 2024. In the first half of 2026 its sales rose 97%, to 178,370, helped by the Zeekr 9X, a large SUV priced above RMB500,000 that sold more than 46,000 units. Lynk &amp; Co went the other way: its sales fell 19% in the first nine months of 2026.</p>
<div class="table-title">Table 1. Sales by brand, January to September, units</div>
{table(["", "Jan-Sep 2025", "Jan-Sep 2026", "Change"],
       [[n, n0(a), n0(b), f"{(b / a - 1) * 100:+.0f}%".replace("-", "−")] for n, a, b in G_9M])}
<p class="table-note">Unaudited monthly figures. Source: {src_link(3, SRC_GEELY)}.</p>
<h2>2026: a smaller home market, more exports</h2>
<p>Sales of passenger cars inside China fell 24% in the first half of 2026, according to figures from the China Association of Automobile Manufacturers quoted in Geely's report. Geely's total sales still rose 1%, to 1.42 million, because exports grew 158%, to 474,228 cars. More than half of the exported cars were electric or plug-in hybrid.</p>
<p>The mix also became more expensive. The average price of a Geely car rose by RMB15,000, to RMB112,000, so revenue grew 15%, to RMB173.6 billion, and the gross margin rose from 16.3% to 17.9%. Reported profit fell 2%, to RMB9.09 billion, because a foreign exchange gain of RMB2.64 billion in the first half of 2025 turned into a loss of RMB550 million. Core profit rose 46%, to RMB9.68 billion.</p>
<div class="table-title">Table 2. Geely key figures</div>
{table(["", *G_YEARS, "1H 2025", "1H 2026"],
       [["**Revenue, RMB billion", *[f"{v:.1f}" for v in G_REV], *[f"{v:.1f}" for v in G_H1["rev"]]],
        ["Reported profit, RMB billion", *[f"{v:.2f}" for v in G_NP], *[f"{v:.2f}" for v in G_H1["np"]]],
        ["Core profit, RMB billion", "n/a", *[f"{v:.2f}" for v in G_CORE[1:]], *[f"{v:.2f}" for v in G_H1["core"]]],
        ["Cars sold, thousand", *[f"{v / 1000:,.0f}" for v in G_UNITS], "n/a", f"{G_H1['units'][1] / 1000:,.0f}"]])}
<p class="table-note">Profit is attributable to owners of the parent. Sources: {src_link(0, SRC_GEELY)}; {src_link(1, SRC_GEELY)}.</p>
<h2>Geely in Kazakhstan</h2>
<p>Kazakhstan appears twice in Geely's 2025 annual report. Geely makes cars with local partners at 12 plants outside China, and in 2025 the plant in Kazakhstan began producing both electric and petrol cars on two lines. Zeekr, which has 152 stores in about 50 countries outside mainland China, says it was among the top three luxury electric car brands in Kazakhstan. The report gives no sales figures for Kazakhstan itself.</p>
<h2>Risks</h2><ol>
<li>The 2026 target of 3.45 million cars needs about 1.21 million sales in October to December, around 405,000 a month. In September Geely sold 292,168.</li>
<li>The car market in China is shrinking and price competition remains fierce, which limits margins.</li>
<li>Growth now depends on exports, which face trade barriers and currency swings. A foreign exchange gain of RMB2.64 billion in the first half of 2025 became a loss of RMB550 million a year later.</li>
<li>Lynk &amp; Co's sales are falling, so the "One Geely" plan still has to prove that the three brands can grow together.</li></ol>
{view("view_geely.txt")}'''

report(GEELY, geely_sections,
       [("Revenue, 2025", "RMB345 bn"), ("Cars sold, 2025", "3.02 mn"), ("Exports, 1H 2026", "+158%"),
        ("Zeekr sales, 1H 2026", "+97%"), ("Core profit, 1H 2026", "+46%")], SRC_GEELY, disclaimer=True)

report(HALYK, halyk_sections,
       [("Net income, 2025", "₸1.06 trn"), ("Return on equity, 2025", "32.6%"), ("Net income, 1H 2026", "−15.3%"),
        ("Interest margin, 1H 2026", "6.8%"), ("Cost of risk, 1H 2026", "1.4%")], SRC_HALYK, disclaimer=True)
report(CA, ca_sections,
       [("Trade, 2025", "$106.3 bn"), ("Growth", "+12%"), ("China's surplus", "$36.1 bn"),
        ("Kazakhstan's share", "46%"), ("Kyrgyzstan, own data", "$4.97 bn")], SRC_CA)

TRADE["feat"] = (YEARS, "Kazakhstan's exports to and imports from China, $ billion",
                 columns([("Exports", GREY, EXPORTS), ("Imports", CHART_HI, IMPORTS)], YEARS, w=520, h=270, top=22,
                         desc="Exports and imports, 2020 to 2025"), "Kazakh official statistics")
REPORTS = [GEELY, RU, KAP, CA, HALYK, TRADE, KASPI]  # newest first; the first one is featured on the home page


# ---------- Home ----------


# Companies and countries the research covers; every number comes from a report on the site.
COVERAGE = [  # companies first, then countries; logo files are in assets/logos (credits on the Terms page)
    dict(code="KSPI", logo="kaspi", tag="Company · Kazakhstan", name="Kaspi.kz", band="#d9352b",
         what="Payments, online shopping and loans in one app", r=KASPI,
         stats=[("Revenue, 2025", "₸4.05 trn"), ("Revenue growth", "+60%"), ("Net margin", "26.4%")]),
    dict(code="HSBK", logo="halyk", tag="Company · Kazakhstan", name="Halyk Bank", band="#1f7a4d",
         what="Kazakhstan's largest bank by assets", r=HALYK,
         stats=[("Net income, 2025", "₸1.06 trn"), ("Return on equity", "32.6%"), ("Net income, 1H 2026", "−15.3%")]),
    dict(code="KAP", logo="kazatomprom", tag="Company · Kazakhstan", name="Kazatomprom", band="#3f5e6e",
         what="The world's largest uranium producer", r=KAP,
         stats=[("Production, 2025", "25,839 tU"), ("Sales to Asia, 2025", "56%"), ("Cost per lb, 1H 2026", "+37%")]),
    dict(code="0175", logo="geely", tag="Company · China", name="Geely Auto", band="#1d5fa8",
         what="Carmaker that owns Geely, Lynk & Co and Zeekr", r=GEELY,
         stats=[("Revenue, 2025", "RMB345 bn"), ("Exports, 1H 2026", "+158%"), ("Zeekr sales, 1H 2026", "+97%")]),
    dict(code="KZ", tag="Country", name="Kazakhstan", band="#0a7f99",
         what="Sells raw materials to China, buys machinery", r=TRADE,
         stats=[("Trade with China, 2025", "$34.1 bn"), ("China's share of trade", "23.7%"), ("Balance with China", "−$3.7 bn")]),
    dict(code="CA", tag="Region", name="Central Asia", band="#8a5a2b",
         what="Five states whose trade with China passed $100 billion in 2025", r=CA,
         stats=[("Trade with China, 2025", "$106.3 bn"), ("China's surplus", "$36.1 bn"), ("Kyrgyzstan, own data", "$4.97 bn")]),
    dict(code="RU", tag="Country", name="Russia", band="#4a5562",
         what="China's largest neighbour by trade, where cars fell sharply in 2025", r=RU,
         stats=[("Trade with China, 2025", "$228.1 bn"), ("Change, 2025", "−6.9%"), ("Chinese cars bought", "−49%")]),
    dict(code="CN", tag="Country", name="China", band="#b8261c",
         what="Kazakhstan's main trading partner in these reports", r=TRADE,
         stats=[("Goods to Kazakhstan, 2025", "$18.9 bn"), ("Same flow, Chinese data", "$29.7 bn"), ("Top buy from Kazakhstan", "Ores")]),
]


def card(c):
    mark = (f'<img src="assets/logos/{c["logo"]}.svg" alt="{escape(c["name"])} logo">' if c.get("logo")
            else f'<b style="color:{c["band"]}">{c["code"]}</b>')
    return (f'<a class="card" href="{c["r"]["url"]}"><div class="card-band" style="border-top-color:{c["band"]}">{mark}<span>{c["tag"]}</span></div>'
            f'<div class="card-body"><h3>{c["name"]}</h3><p class="muted">{c["what"]}</p>'
            '<ul class="card-stats">' + "".join(f'<li><span>{k}</span><b>{v}</b></li>' for k, v in c["stats"]) + '</ul>'
            f'<span class="card-more">{c["r"]["kind"]}</span></div></a>')


F = REPORTS[0]
HERO_CREDIT = ('Photo: Kazakhstan Temir Zholy freight train between Joloman and Saryozek, Almaty Region. '
               '<a href="https://commons.wikimedia.org/wiki/File:KTZ_TE33A_Joloman.jpg" rel="noopener">David Gubler</a>, '
               '<a href="https://creativecommons.org/licenses/by-sa/3.0/" rel="noopener">CC BY-SA 3.0</a>, cropped')
# Key numbers from the reports; each links to the report it comes from.
NUMBERS = [("$228.1 bn", "China-Russia trade, 2025", RU), ("$106.3 bn", "China-Central Asia trade, 2025", CA),
           ("$34.1 bn", "Kazakhstan-China trade, 2025", TRADE), ("25,839 t", "Uranium mined by Kazatomprom, 2025", KAP),
           ("+158%", "Geely exports, 1H 2026", GEELY), ("+60%", "Kaspi.kz revenue growth, 2025", KASPI)]
home = f'''<section class="masthead hero">
<img class="hero-img" src="assets/photos/hero-ktz-2400.jpg" srcset="assets/photos/hero-ktz-1200.jpg 1200w, assets/photos/hero-ktz-2400.jpg 2400w"
 sizes="100vw" width="2400" height="767" alt="A long freight train of Kazakhstan Temir Zholy crossing the steppe, with hills behind">
<div class="hero-shade"></div>
<div class="wrap">
<h1>Research on Kazakhstan's companies and its trade with China</h1>
<p>Company notes and trade briefs based on company filings and official statistics. Current reports cover Kaspi.kz, Halyk Bank, Kazatomprom and Geely, Kazakhstan's trade with China, and China's trade with Central Asia and Russia. Every source is cited, and the underlying data is available to download.</p>
</div>
<p class="hero-credit">{HERO_CREDIT}</p>
</section>
<section class="numbers"><div class="wrap"><div class="numbers-head">By the numbers</div><div class="numbers-row">
{"".join(f'<a class="number" href="{r["url"]}"><b>{v}</b><span>{k}</span></a>' for v, k, r in NUMBERS)}
</div></div></section>

<section class="block"><div class="wrap">
<div class="block-head"><h2>Latest</h2></div>
<div class="featured">
<div class="featured-text">
<div class="label">{kind_label(F)} &middot; <time datetime="{F["iso"]}">{F["date"]}</time></div>
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
    dict(name="Geely Automobile key figures", cover="2023-Sep 2026 · revenue, profit, sales by brand, exports", base=GEELY["data"]),
    dict(name="China-Russia goods trade", cover="2020-2025 · Chinese customs data · top products", base=RU["data"]),
    dict(name="Kazatomprom key figures", cover="2023-1H2026 · production, price, cost, profit, sales by region", base=KAP["data"]),
    dict(name="China-Central Asia goods trade", cover="2025 · five countries · Chinese and national data", base=CA["data"]),
    dict(name="Halyk Bank key figures", cover="2023-1H2026 · net income, margin, return on equity", base=HALYK["data"]),
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
    dict(name="Geely Automobile key figures", cover="2023-Sep 2026", unit="RMB billion, units, %",
         what="Revenue, reported and core profit, sales volume; first half of 2025 and 2026; sales by brand (Geely, Galaxy, Lynk & Co, Zeekr) and exports, January to September.",
         src="Geely Automobile Holdings reports and sales announcements", base=GEELY["data"], r=GEELY),
    dict(name="China-Russia goods trade", cover="2020-2025", unit="$ billion",
         what="China's exports to and imports from Russia, total and balance; top product groups in 2025; vehicles, machinery, fuel and metals in 2021, 2024 and 2025.",
         src="General Administration of Customs of China", base=RU["data"], r=RU),
    dict(name="Kazatomprom key figures", cover="2023-1H2026", unit="tU, $/lb, ₸ billion, %",
         what="Production, sales, realized and spot price, C1 cash cost, revenue, EBITDA, profit to shareholders; first half of 2025 and 2026; sales by region.",
         src="Kazatomprom operating and financial reviews", base=KAP["data"], r=KAP),
    dict(name="China-Central Asia goods trade", cover="2025", unit="$ billion",
         what="China's trade with Kazakhstan, Kyrgyzstan, Uzbekistan, Turkmenistan and Tajikistan: totals, growth, exports, imports, and each country's own figure.",
         src="GACC via Xinhua and Eurasianet; national statistics", base=CA["data"], r=CA),
    dict(name="Halyk Bank key figures", cover="2023-1H2026", unit="₸ billion, %",
         what="Net income, return on average equity, net interest margin and cost-to-income ratio; first half of 2025 and 2026.",
         src="Halyk Bank consolidated results (IFRS)", base=HALYK["data"], r=HALYK),
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
<p>Company names, logos and trademarks belong to their owners and are shown only to identify the companies discussed. Logo files: Kaspi.kz logo from Wikimedia Commons (CC BY-SA 4.0); Kazatomprom, Geely Automobile Holdings, Zeekr and Hepsiburada logos from Wikimedia Commons (public domain); Halyk Bank logo from halykbank.kz. Home page photo: David Gubler, via Wikimedia Commons, licensed CC BY-SA 3.0 (https://creativecommons.org/licenses/by-sa/3.0/), cropped; the cropped version is shared under the same licence.</p>
<p> Links to other websites are given as sources; Steppe &amp; Silk Research is not responsible for their content.</p>
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
      + "".join(f"  <url><loc>{SITE}/{u}</loc><lastmod>2026-10-23</lastmod></url>\n" for u in urls) + "</urlset>\n")

write("assets/favicon.svg", FAVICON)
for name in ("style.css", "site.js"):
    with open(os.path.join(HERE, name)) as a:
        write("assets/" + name, a.read())

# 1200x630 cards; tools/render_og.js turns them into og/*.png
OG_CSS = (f"body{{margin:0;width:1200px;height:630px;background:#faf7f2;font-family:'IBM Plex Sans',Arial;color:{INK};}}"
          ".c{box-sizing:border-box;width:1200px;height:630px;padding:56px 64px;display:flex;flex-direction:column;border-top:14px solid " + CHART_HI + "}"
          ".top{display:flex;justify-content:space-between;font-family:'IBM Plex Mono',monospace;font-size:20px;letter-spacing:1px;text-transform:uppercase}"
          ".top b{color:" + CHART_HI + ";font-weight:500}.mid{flex:1;display:flex;gap:48px;align-items:center}"
          "h1{font-family:'IBM Plex Sans',Arial,sans-serif;font-size:50px;line-height:1.15;margin:0 0 28px;font-weight:600}"
          ".num{font-family:'IBM Plex Sans',Arial,sans-serif;font-size:76px;font-weight:600;color:" + CHART_HI + ";line-height:1}"
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

# ---------- Academic PDFs for the October 2026 reports ----------
# tools/render_pdf.js turns tools/pdf/*.html into reports/*.pdf (A4, Times-style, as the earlier reports).

PDF_CSS = """@page{size:A4;margin:22mm 22mm 20mm}
body{font-family:'Liberation Serif','Times New Roman',serif;font-size:11pt;line-height:1.38;color:#111}
.title{text-align:center;margin-bottom:14px}.title h1{font-size:16pt;font-weight:bold;margin:0 0 6px;line-height:1.25}
.title .au{font-size:11pt}.title .dt{font-size:10pt;color:#333;font-style:italic}
.abs{margin:10px 18px 14px;font-size:10.2pt}.abs b{font-variant:small-caps}
h2{font-size:12pt;margin:14px 0 4px}p{margin:0 0 7px;text-align:justify}
.cap{font-size:9.6pt;margin:10px 0 3px}
table{width:100%;border-collapse:collapse;font-size:10pt;border-top:1.5px solid #000;border-bottom:1.5px solid #000}
th{font-weight:bold;text-align:right;padding:3px 6px;border-bottom:1px solid #000}th:first-child,td:first-child{text-align:left}
td{padding:2px 6px;text-align:right}.tn{font-size:8.8pt;color:#333;margin-top:3px}
.fig{margin:4px 0 2px;max-width:440px}.fig svg text{font-family:'Liberation Serif',serif}
ol.ref{font-size:9pt;padding-left:18px;margin:4px 0}ol.ref li{margin-bottom:2px;word-break:break-all}
.meth{font-size:9pt;font-style:italic;margin-top:10px}.keep{break-inside:avoid}"""
D1, L1 = "#3b3b3b", "#a9a9a9"


def ptable(head, rows, note):
    th = "".join(f"<th>{h}</th>" for h in head)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table><tr>{th}</tr>{trs}</table><div class="tn">{note}</div>'


def pfig(n, title, chart, note):
    return f'<div class="keep"><div class="cap"><b>Figure {n}.</b> {title}</div><div class="fig">{chart}</div><div class="tn">{note}</div></div>'


def pdf_doc(r, abstract, body, view_file, refs):
    path = os.path.join(HERE, view_file)
    view_text = open(path).read().strip() if os.path.exists(path) else ""
    refs_html = "".join(f"<li>{escape(n)}. {u}</li>" for n, u, *_ in refs)
    title = r["title"].replace(": ", ":<br>", 1)
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{PDF_CSS}</style></head><body>'
            f'<div class="title"><h1>{title}</h1><div class="au">{AUTHOR}</div>'
            f'<div class="dt">Steppe &amp; Silk Research, {r["date_long"]}</div></div>'
            f'<div class="abs"><b>Summary.</b> {abstract}</div>{body}'
            + (f'<h2>Author\'s view</h2><p>{view_text}</p>' if view_text else '') + f'<h2>References</h2><ol class="ref">{refs_html}</ol>'
            '<div class="meth">Figures are taken from the sources listed.</div></body></html>')


halyk_pdf = pdf_doc(HALYK, HALYK["summary"], f'''
<h2>1. Data</h2><p>All figures come from Halyk Bank's consolidated IFRS results for 2023, 2024 and 2025 and for the first half and first quarter of 2026 [1-5]. Net income is attributable to common shareholders. The 2023 net interest margin is the restated figure from the 2024 release (6.1%).</p>
<h2>2. Results for 2023-2025</h2>
<p>Net income rose from ₸693 billion in 2023 to ₸1,058 billion in 2025, an increase of 53% in two years. Return on average equity stayed above 32% in all three years and peaked at 34.0% in 2024. The bank is cheap to run: operating costs took 17.5% of income in 2025, down from 19.2% in 2023.</p>
{pfig(1, "Net income attributable to common shareholders, ₸ billion",
      columns([("Net income", D1, H_NI)], H_YEARS, w=440, h=200, top=1250, fmt="{:,.0f}"), "Sources: [1], [2], [3].")}
<p>The first warning sign appeared in 2025. Interest expense grew by 32%, to ₸1,407 billion, while interest income grew by 24%, to ₸2,695 billion, because deposits became more expensive. The margin slipped from 7.2% to 7.1%.</p>
<div class="keep"><div class="cap"><b>Table 1.</b> Halyk Bank key figures</div>
{ptable(["", *H_YEARS, "1H 2025", "1H 2026"],
        [["Net income, ₸ billion", *[f"{v:,.0f}" for v in H_NI], *[f"{v:,.0f}" for v in H_H1["ni"]]],
         ["Return on average equity", *[f"{v}%" for v in H_ROAE], "", ""],
         ["Net interest margin", *[f"{v}%" for v in H_NIM], *[f"{v}%" for v in H_H1["nim"]]],
         ["Cost-to-income ratio", *[f"{v}%" for v in H_CI], *[f"{v}%" for v in H_H1["ci"]]]],
        "Sources: [1]-[4].")}</div>
<h2>3. The first half of 2026</h2>
<p>Net income for the first six months of 2026 was ₸447.6 billion, 15.3% less than a year earlier. The bank names three causes [4]. The National Bank of Kazakhstan raised minimum reserve requirements, with another increase in April 2026 [5]; without this effect the margin would have been 7.2% instead of 6.8%. The regulator also tightened the rules on retail lending. And the average rate paid on customer accounts rose while the average rate on loans stayed flat, so net interest income grew only 2.6%, to ₸657.6 billion.</p>
<p>Lending kept growing, with gross loans up 13.2% over the year to June 2026, and the cost of risk stayed at 1.4%. The fall in profit therefore comes from the price of money, not from bad loans.</p>
<h2>4. Risks</h2>
<p>The base rate was kept at 18% in March 2026 [5]. If rates stay high for longer, deposits stay expensive and the margin stays under pressure. Further limits on consumer lending would slow the retail loan book, and a slowdown in the economy would raise the cost of risk from its current low level. This note is not investment advice.</p>''',
    "view_halyk.txt", SRC_HALYK)

ca_pdf = pdf_doc(CA, CA["summary"], f'''
<h2>1. Data</h2><p>The main series is China's customs data (General Administration of Customs of China), as published by Xinhua [1] and reported country by country by Eurasianet [2, 3]. Each Central Asian country's own figure comes from its statistics or customs service [3-6]. Turkmenistan does not publish one.</p>
<h2>2. Trade by country</h2>
<p>China's trade with Central Asia reached $106.3 billion in 2025, up 12% and above $100 billion for the first time. China exported $71.2 billion to the region and imported $35.1 billion, a surplus of $36.1 billion. Kazakhstan accounts for 46% of the total and Kyrgyzstan for 26%.</p>
<div class="keep"><div class="cap"><b>Table 1.</b> China's trade with Central Asia, 2025, $ billion</div>
{ptable(["", "Total, Chinese data", "Growth", "China's exports", "China's imports", "Total, own data"],
        ca_rows_html + [["Central Asia", f"{CA_TOTAL:.1f}", "+12%", f"{CA_EXP:.1f}", f"{CA_IMP:.1f}", ""]],
        "Tajikistan's own total is imports ($2.3 bn) plus exports ($0.52 bn) reported by its customs. Sources: [1]-[6].")}</div>
<p>Four of the five countries import more from China than they export to it. For Uzbekistan the ratio is more than seven to one. Turkmenistan is the exception: it sold China $8.4 billion of goods, almost all of it natural gas, and bought $1.6 billion. It was also the only country whose trade with China fell, by 5.6%.</p>
<h2>3. The same trade, counted twice</h2>
<p>The countries' own statistics often show much less trade (Figure 1). Kazakhstan records $34.1 billion, $14.6 billion less than China. Kyrgyzstan records $4.97 billion against China's $27.2 billion, and the gap grew from $17.1 billion in 2024 [4]. Kyrgyz customs officials say China counts every shipment sent to or through Kyrgyzstan, while Kyrgyzstan counts only goods for its own use; under-declared values, unregistered online purchases and goods arriving through Kazakhstan add to the gap [4]. In Tajikistan the two sides agree on exports but not on imports [3]. Uzbekistan is the one case where the country's own figure, $17.2 billion, is higher than China's [5].</p>
{pfig(1, "Trade with China in 2025: China's figure and the country's own, $ billion",
      columns([("China's data", D1, [r[1] for r in CA_ROWS if r[5]]), ("Country's own data", L1, [r[5] for r in CA_ROWS if r[5]])],
              [r[0] for r in CA_ROWS if r[5]], w=440, h=210, top=56, fmt="{:.1f}"), "Sources: [2]-[6].")}
<p>A headline figure of "$27 billion of trade with Kyrgyzstan" describes goods leaving China, and a large part of them may end up elsewhere. Any use of these numbers should say whose data they are.</p>''',
    "view_central_asia.txt", SRC_CA)

kap_pdf = pdf_doc(KAP, KAP["summary"], f'''
<h2>1. Data</h2><p>All figures come from Kazatomprom's operating and financial reviews for 2023, 2024 and 2025 and for the first half of 2026 [1-4], and from its August 2025 results announcement [5]. Production is on a 100% basis. Sales volumes and the average realized price cover natural uranium (U3O8) only. Annual profit to shareholders is the company's adjusted measure, which removes a one-off gain of ₸296 billion in 2024.</p>
<h2>2. Results for 2023-2025</h2>
<p>Production rose from 21,112 tU in 2023 to 25,839 tU in 2025, an increase of 22%. The company estimates that its attributable output was 20% of the world's primary uranium supply in 2025 [1]. Revenue fell 1% in 2025, to ₸1,803 billion, although natural uranium sales grew 16%: in 2024 the company had also sold ₸252 billion of enriched uranium to Ulba-FA, and this did not repeat. Without that item, revenue would have grown by about 15%. Adjusted profit attributable to shareholders was ₸570 billion, against ₸577 billion in 2024.</p>
{pfig(1, "Production, thousand tonnes of uranium (100% basis)",
      columns([("Production", D1, [v / 1000 for v in U_PROD])], U_YEARS, w=440, h=190, top=32, fmt="{:.1f}"), "Sources: [1], [3].")}
<p>Most uranium is sold under long-term contracts that follow the spot price with a delay. The realized price fell 6% in 2025, to $65.32 per pound, while the spot price fell 16%, to $72.75 [1].</p>
<h2>3. Sales by region</h2>
<p>Asia's share of Group sales rose from 45% in 2023 to 56% in 2025, and Europe's fell from 29% to 19% [1]. The company does not report China separately, but uranium for China is shipped by rail through Alashankou, and Ulba-FA, a joint venture with Chinese partners, supplied fuel assemblies containing slightly more than 200 tonnes of low-enriched uranium to Chinese nuclear plants in 2025 [1]. In the same year 48% of Western-bound shipments used the Trans-Caspian route rather than Russia [1].</p>
<div class="keep"><div class="cap"><b>Table 1.</b> Kazatomprom key figures</div>
{ptable(["", *U_YEARS, "1H 2025", "1H 2026"],
        [["Production, tU", *map(n0, U_PROD), *map(n0, U_H1["prod"])],
         ["Realized price, $/lb", *[f"{v:.2f}" for v in U_PRICE], *[f"{v:.2f}" for v in U_H1["price"]]],
         ["Spot price, $/lb", *[f"{v:.2f}" for v in U_SPOT], *[f"{v:.2f}" for v in U_H1["spot"]]],
         ["C1 cash cost, $/lb", *[f"{v:.2f}" for v in U_C1], *[f"{v:.2f}" for v in U_H1["c1"]]],
         ["Revenue, ₸ billion", *map(n0, U_REV), *[f"{v:.0f}" for v in U_H1["rev"]]],
         ["Profit to shareholders, ₸ billion", "n/a", *map(n0, U_ADJ_NP[1:]), *[f"{v:.0f}" for v in U_H1["owners"]]],
         ["Asia, % of Group sales", *[f"{v}%" for v in U_ASIA[0][1:]], "", ""]],
        "Annual profit to shareholders is adjusted for one-off items. Sources: [1]-[4].")}</div>
<h2>4. The first half of 2026</h2>
<p>Revenue rose 9%, to ₸718 billion, as the realized price climbed 16% to $67.88 [2]. C1 cash cost rose faster, by 37% to $24.48 per pound, so of the $9.34 gain in price $6.62 was absorbed by costs. The company gives three causes [2]: the mineral extraction tax, which since January 2026 depends on output and price, rose from a flat 9% to an average of 12.4% and doubled in money terms to ₸120 billion; sulphuric acid cost 39% more per tonne because of local shortages; and the tenge strengthened against the dollar. The company's own acid plant has been delayed to between the third quarter of 2027 and the first quarter of 2028 after possible paleontological finds on the site.</p>
{pfig(2, "C1 cash cost, $ per pound of U3O8 (attributable basis)",
      columns([("C1", D1, U_C1 + list(U_H1["c1"]))], U_YEARS + ["1H 2025", "1H 2026"], w=440, h=190, top=28, fmt="{:.2f}"),
      "Sources: [1]-[3].")}
<p>Net profit fell 9%, to ₸240 billion, mainly because of exchange-rate losses and higher finance costs, and profit attributable to shareholders fell 23%, to ₸157 billion, as a larger part went to minority owners of the mines [2]. The company lowered its 2026 revenue guidance to ₸2,100-2,200 billion and raised its C1 guidance to $25.50-27.00 per pound, while keeping production guidance at 27,500-29,000 tU [2]. In August 2025 it had already lowered its nominal 2026 production level by about 10%, to 29,697 tU [5].</p>
<h2>5. Risks</h2>
<p>Profit depends on the uranium price. The new extraction tax rises with output and price, so it takes a larger share in a strong market. Acid shortages could limit production until the new plant starts, and a stronger tenge lowers revenue in tenge while raising costs in dollars. This note is not investment advice.</p>''',
    "view_kazatomprom.txt", SRC_KAP)

ru_pdf = pdf_doc(RU, RU["summary"], f'''
<h2>1. Data</h2><p>All figures are China's customs statistics (General Administration of Customs of China, GACC), Monthly Bulletin, December issue of each year: table (2) for totals and tables (15) and (16) for product groups by HS chapter [1-6]. Values are converted from US$ thousand to US$ billion. Growth rates for totals are those published by GACC. Russia's customs service stopped publishing trade by partner country in 2022 [7], so no Russian series is available for comparison.</p>
<h2>2. Trade by year</h2>
<div class="keep"><div class="cap"><b>Table 1.</b> China's goods trade with Russia, $ billion</div>
{ptable(["", *YEARS],
        [["China's exports to Russia", *[f"{v:.1f}" for v in RU_EXP]], ["China's imports from Russia", *[f"{v:.1f}" for v in RU_IMP]],
         ["Total trade", *[f"{v:.1f}" for v in RU_TOTAL]], ["Balance", *[f"{v:+.1f}" for v in RU_BAL]]],
        "Balance is China's exports minus imports. Sources: [1], [2], [6].")}</div>
<p>Trade grew from $107.8 billion in 2020 to a record $244.8 billion in 2024 and fell 6.9% in 2025, to $228.1 billion. China's exports to Russia fell 10.4% and its imports from Russia 3.9%. Russia accounted for 3.6% of China's foreign trade in 2025.</p>
{pfig(1, "China's exports to and imports from Russia, $ billion",
      columns([("Exports", D1, RU_EXP), ("Imports", L1, RU_IMP)], YEARS, w=440, h=200, top=140, fmt="{:.0f}"),
      "Dark: China's exports to Russia; light: China's imports from Russia. Sources: [1], [6].")}
<h2>3. Structure and change by product</h2>
<p>In 2025 machinery, electrical equipment and vehicles made up 53% of China's exports to Russia, and oil, gas and coal made up 63% of its imports from Russia [3, 4].</p>
<div class="keep"><div class="cap"><b>Table 2.</b> Selected product groups, $ billion</div>
{ptable(["", "2021", "2024", "2025"],
        [[n, "" if a is None else f"{a:.2f}", f"{b:.2f}", f"{c:.2f}"] for n, a, b, c in RU_CHANGE],
        "HS chapters. Sources: [3], [4], [5].")}</div>
<p>China's vehicle exports to Russia grew from $4.3 billion in 2021 to $25.5 billion in 2024 and fell to $13.1 billion in 2025. The fall of $12.4 billion is about equal to the fall in all China's exports to Russia ($12.2 billion). The value of oil, gas and coal imports fell by $16.3 billion, while imports of ores, aluminium and copper each rose by more than 50%.</p>
<h2>4. Comparison with Kazakhstan</h2>
<p>In the same year China's trade with Kazakhstan grew 11.0%, to $48.7 billion [1]. It is about a fifth of China's trade with Russia but has grown faster since 2020 (127% against 112%). In both cases China sells manufactured goods and buys raw materials.</p>''',
    "view_china_russia.txt", SRC_RU)

geely_pdf = pdf_doc(GEELY, GEELY["summary"], f'''
<h2>1. Data</h2><p>All figures come from Geely Automobile Holdings' Annual Report 2025, Interim Report 2026 and monthly sales announcements [1-4]. Money is in Chinese yuan (RMB). Profit is attributable to owners of the parent. "Core profit" is the company's own measure without foreign exchange effects, impairments and one-off gains on disposals.</p>
<h2>2. Results for 2023-2025</h2>
<p>Revenue rose from RMB224.8 billion in 2023 to RMB345.2 billion in 2025, and sales from 1.69 million to 3.02 million cars [1]. In 2025 sales in China grew 48% and exports only 1%. Reported profit was flat at RMB16.85 billion because 2024 included a one-off gain of RMB9.35 billion; core profit rose 36%, to RMB14.41 billion. The gross margin was 16.6%.</p>
{pfig(1, "Revenue, RMB billion", columns([("Revenue", D1, G_REV)], G_YEARS, w=440, h=180, top=400, fmt="{:.1f}"), "Source: [1].")}
<h2>3. The privatisation of Zeekr</h2>
<p>On 22 December 2025 Geely completed the purchase of all Zeekr shares it did not already own, paying about RMB5.3 billion in cash and issuing 777 million new shares; Zeekr left the New York Stock Exchange [1]. Geely presents the deal as part of its "One Geely" plan to remove duplicated investment between its brands. Zeekr sold 224,133 cars in 2025 (+1%) and 178,370 in the first half of 2026 (+97%) [1, 2].</p>
<div class="keep"><div class="cap"><b>Table 1.</b> Sales by brand, January to September, units</div>
{ptable(["", "Jan-Sep 2025", "Jan-Sep 2026", "Change"],
        [[n.replace("**", ""), n0(a), n0(b), f"{(b / a - 1) * 100:+.0f}%"] for n, a, b in G_9M], "Unaudited. Source: [4].")}</div>
<h2>4. The first half of 2026</h2>
<p>Domestic passenger car sales in China fell 24%, but Geely's total sales rose 1% to 1.42 million because exports grew 158%, to 474,228 [2]. The average selling price rose by RMB15,000 to RMB112,000, revenue rose 15% to RMB173.6 billion and the gross margin rose from 16.3% to 17.9%. Reported profit fell 1.8%, to RMB9.09 billion, because of a swing from a foreign exchange gain to a loss; core profit rose 46%, to RMB9.68 billion [2].</p>
<h2>5. Kazakhstan</h2>
<p>In 2025 Geely's partner plant in Kazakhstan started producing both electric and petrol cars, and Zeekr reported being among the top three luxury electric brands in the country [1]. No sales figures for Kazakhstan are published.</p>
<h2>6. Risks</h2>
<p>To meet its 2026 target of 3.45 million cars, Geely must sell about 1.21 million in the fourth quarter, around 405,000 a month, against 292,168 in September [4]. The domestic market is shrinking, price competition remains strong, exports are exposed to trade barriers and currencies, and Lynk &amp; Co's sales fell 19% in the first nine months of 2026. This note is not investment advice.</p>''',
    "view_geely.txt", SRC_GEELY)

for slug, html_doc in (("geely-2026", geely_pdf), ("china-russia-trade-2025", ru_pdf), ("kazatomprom-2025", kap_pdf), ("halyk-bank-2026", halyk_pdf), ("china-central-asia-2025", ca_pdf)):
    os.makedirs(os.path.join(HERE, "pdf"), exist_ok=True)
    with open(os.path.join(HERE, "pdf", slug + ".html"), "w") as f:
        f.write(html_doc)
