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
<p>Independent research on companies and trade in Kazakhstan, Central Asia and China. Nothing on this site is investment advice.</p></div>
<div class="foot-links"><nav>{foot_nav}</nav><a href="mailto:{EMAIL}">{EMAIL}</a><span>&copy; 2026 {AUTHOR}</span></div>
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


def hbars(rows, unit="", colour=GREY):
    """Horizontal bars in HTML, so long labels stay readable on phones."""
    top = max(v for _, v in rows)
    items = "".join(
        f'<div class="hbar"><div class="hbar-label">{lab}</div>'
        f'<div class="hbar-track"><span style="width:{v/top*100:.1f}%;background:{colour}"></span></div>'
        f'<div class="hbar-val">{v:.2f}{unit}</div></div>' for lab, v in rows)
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
    ("Association of Financiers of Kazakhstan, Kazakhstan–China commodity turnover, March 2026 (BNS data)",
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
    name, url = srcs[i]
    return f'<a href="{url}" rel="noopener">{name.split(",")[0]}</a>'


KASPI = dict(
    slug="kaspi-hepsiburada",
    url="research/kaspi-hepsiburada.html",
    tag="Companies",
    kind="Company note",
    title="Bigger but Less Profitable: Kaspi.kz after the Hepsiburada Acquisition",
    date="8 Oct 2026", date_long="8 October 2026", iso="2026-10-08",
    line="Revenue up 60%, net income up 1%: what the Turkish deal did to Kaspi's margins.",
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
    title="Raw Materials Out, Machines In: Kazakhstan's Trade with China, 2020–2025",
    date="8 Oct 2026", date_long="8 October 2026", iso="2026-10-08",
    line="Trade more than doubled in five years, and a surplus turned into a $3.7 billion deficit.",
    summary=("Trade between Kazakhstan and China more than doubled, from $15.4 billion to $34.1 billion. Kazakhstan "
             "still sells mostly raw materials and buys machinery, electronics and vehicles. Since 2023 it has run a "
             "trade deficit with China, which reached $3.7 billion in 2025."),
    art=columns([("Turnover", GREY, TURNOVER)], YEARS, w=300, h=150, hi=5, top=40, fmt="{:.0f}",
                desc="Kazakhstan–China trade turnover, $ billion, 2020 to 2025: 15, 18, 24, 32, 30, 34"),
    art_title="Trade turnover, $ bn",
    pdf="reports/kazakhstan-china-trade-2026.pdf", pages=3,
    data="data/kazakhstan-china-trade-2020-2025",
    og_num="−$3.7 bn", og_cap="Kazakhstan's trade balance with China in 2025",
    og_chart=columns([("Exports", GREY, EXPORTS), ("Imports", ACCENT, IMPORTS)], YEARS, w=420, h=260, top=22),
)
REPORTS = [TRADE, KASPI]  # newest first; the first one is featured on the home page


def row(r, pre=""):
    return f'''<div class="row" data-type="{r["tag"].lower()}">
<div class="row-date"><time datetime="{r["iso"]}">{r["date"]}</time></div>
<div class="row-main"><div class="label">{r["kind"]}</div><h3><a class="row-link" href="{pre}{r["url"]}">{r["title"]}</a></h3><p>{r["line"]}</p>
<div class="row-actions"><a href="{pre}{r["url"]}">Read &rarr;</a><a class="pdf-link" href="{pre}{r["pdf"]}" download>PDF <span>{r["pages"]} pp.</span></a><a class="pdf-link" href="{pre}{r["data"]}.xlsx" download>Data <span>XLSX</span></a></div></div>
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


data_files(KASPI["data"], "Kaspi.kz key financials, 2023–2025 (₸ million unless stated)",
           ["Source: Kaspi.kz Form 20-F for 2025, segment and earnings notes (pp. F-33 to F-42).",
            "Segment revenue is before inter-segment eliminations and customer rewards, so segments do not add up exactly to total revenue.",
            "Growth rates, margins and shares are calculated from these figures."],
           [("Financials", ["Indicator", "2023", "2024", "2025"],
             [["Payments revenue", *K_PAY], ["Marketplace revenue", *K_MKT], ["Fintech revenue", *K_FIN],
              ["Total revenue", *K_REV], ["Net income", *K_NI],
              ["Net margin, %", *K_MARGIN], ["Marketplace share of segment revenue, %", *K_MKT_SHARE]]),
            ("Turkey 2025", ["2025, ₸ million", "Segment revenue", "Net income"],
             [["Turkey (Hepsiburada)", 1031592, -93018], ["Kazakhstan and other markets", 3070369, 1160725]])])

data_files(TRADE["data"], "Kazakhstan's goods trade with China, 2020–2025 ($ billion)",
           ["Kazakh data: Bureau of National Statistics, Ministry of Trade and Integration, State Revenue Committee, as published by government bodies and national media.",
            "2020–2021 figures come from news reports citing official bodies and are less reliable than later years.",
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
    srcs = "".join(f'<li><a href="{u}" rel="noopener">{escape(n)}</a></li>' for n, u in sources)
    cite = (f'{AUTHOR} (2026). <i>{r["title"]}</i>. Steppe &amp; Silk Research, {r["date_long"]}. '
            f'{SITE}/{r["url"]}')
    dl = (f'<div class="downloads"><a href="{pre}{r["pdf"]}" download>Full report <span>PDF, {r["pages"]} pp.</span></a>'
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
        ["Revenue growth", "–", "+32.3%", "+59.8%"], ["Net income growth", "–", "+24.5%", "+1.0%"],
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
     "Kazakh official statistics, see sources 1–6", TRADE["data"])}
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


# ---------- Home ----------


# Companies and countries the research covers; every number comes from a report on the site.
COVERAGE = [
    dict(code="KSPI", tag="Company · Kazakhstan", name="Kaspi.kz", band="#d9352b",
         what="Payments, marketplace and fintech super app", r=KASPI,
         stats=[("Revenue, 2025", "₸4.05 trn"), ("Revenue growth", "+60%"), ("Net margin", "26.4%")]),
    dict(code="HEPS", tag="Company · Turkey", name="Hepsiburada", band="#e8590c",
         what="E-commerce marketplace, controlled by Kaspi since 2025", r=KASPI,
         stats=[("Segment revenue, 2025", "₸1.03 trn"), ("Net loss, 2025", "₸93 bn"), ("Kaspi's stake, Jan 2026", "85%")]),
    dict(code="KZ", tag="Country", name="Kazakhstan", band="#0a7f99",
         what="Largest economy in Central Asia", r=TRADE,
         stats=[("Trade with China, 2025", "$34.1 bn"), ("China's share of trade", "23.7%"), ("Balance with China", "−$3.7 bn")]),
    dict(code="CN", tag="Country", name="China", band="#b8261c",
         what="Buys Kazakh raw materials, sells machinery and goods", r=TRADE,
         stats=[("Goods to Kazakhstan, 2025", "$18.9 bn"), ("Same flow, Chinese data", "$29.7 bn"), ("Top buy from Kazakhstan", "Ores")]),
]


def card(c):
    return (f'<a class="card" href="{c["r"]["url"]}"><div class="card-band" style="background:{c["band"]}"><b>{c["code"]}</b><span>{c["tag"]}</span></div>'
            f'<div class="card-body"><h3>{c["name"]}</h3><p class="muted">{c["what"]}</p>'
            '<ul class="card-stats">' + "".join(f'<li><span>{k}</span><b>{v}</b></li>' for k, v in c["stats"]) + '</ul>'
            f'<span class="card-more">{c["r"]["kind"]} &rarr;</span></div></a>')


F = REPORTS[0]
home = f'''<section class="masthead"><div class="wrap">
<h1>Independent research on companies and trade in Kazakhstan, Central Asia and China</h1>
<p>Company notes and trade briefs built on annual reports and official statistics. Every chart names its source, and the data behind it can be downloaded.</p>
</div></section>

<section class="block"><div class="wrap">
<div class="block-head"><h2>Latest</h2></div>
<div class="featured">
<div class="featured-text">
<div class="label">{F["kind"]} &middot; <time datetime="{F["iso"]}">{F["date"]}</time></div>
<h2><a href="{F["url"]}">{F["title"]}</a></h2>
<p class="dek">{F["line"]}</p>
<p>{F["summary"]}</p>
<div class="row-actions"><a href="{F["url"]}">Read the brief &rarr;</a><a class="pdf-link" href="{F["pdf"]}" download>PDF <span>{F["pages"]} pp.</span></a><a class="pdf-link" href="{F["data"]}.xlsx" download>Data <span>XLSX</span></a></div>
</div>
<figure class="figure featured-chart"><div class="fig-title">Kazakhstan's exports to and imports from China, $ billion</div>
{columns([("Exports", GREY, EXPORTS), ("Imports", ACCENT, IMPORTS)], YEARS, w=520, h=270, top=22, desc="Exports and imports, 2020 to 2025")}
<figcaption>Source: Kazakh official statistics. From <a href="{F["url"]}">{F["title"].split(":")[0]}</a>.</figcaption></figure>
</div>
</div></section>

<section class="block"><div class="wrap">
<div class="block-head"><h2>Research</h2><a href="research.html">All research &rarr;</a></div>
<div class="rows">{"".join(row(r) for r in REPORTS[1:])}</div>
</div></section>

<section class="block"><div class="wrap">
<div class="block-head"><h2>Coverage</h2><a href="research.html">All research &rarr;</a></div>
<div class="cards">{"".join(card(c) for c in COVERAGE)}</div>
</div></section>

<section class="block block-tint"><div class="wrap">
<div class="block-head"><h2>Data</h2><a href="data.html">All data &rarr;</a></div>
<p class="block-lead">The figures behind every report, free to download and reuse with attribution.</p>
<div class="rows">{"".join(f'<div class="data-row"><div><b>{d["name"]}</b><span>{d["cover"]}</span></div><div class="data-links"><a href="{d["base"]}.xlsx" download>XLSX</a><a href="{d["base"]}.csv" download>CSV</a></div></div>' for d in [
    dict(name="Kazakhstan–China goods trade", cover="2020–2025 · Kazakh and Chinese data · top products", base=TRADE["data"]),
    dict(name="Kaspi.kz key financials", cover="2023–2025 · revenue by segment, net income, margins", base=KASPI["data"])])}</div>
</div></section>'''
page("index.html", "Steppe & Silk Research", home, "",
     "Independent research on companies and trade in Kazakhstan, Central Asia and China, with the data behind every chart.",
     ld={"@context": "https://schema.org", "@type": "WebSite", "name": "Steppe & Silk Research", "url": SITE})

# ---------- Research ----------

counts = {t: sum(r["tag"] == t for r in REPORTS) for t in ("Companies", "Trade")}
research = f'''<section class="page-head"><div class="wrap">
<h1>Research</h1>
<p><b>Company notes</b> look at how a company makes money and what has changed, based on its annual report.
<b>Trade briefs</b> look at what Kazakhstan sells and buys, based on official statistics.</p>
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
    dict(name="Kazakhstan–China goods trade", cover="2020–2025", unit="$ billion",
         what="Exports, imports, turnover and balance (Kazakh data); the same trade in Chinese customs data; top five product groups in 2024.",
         src="Bureau of National Statistics of Kazakhstan; GACC; UN Comtrade", base=TRADE["data"], r=TRADE),
    dict(name="Kaspi.kz key financials", cover="2023–2025", unit="₸ million",
         what="Revenue by segment, total revenue, net income, net margin, Marketplace share; Turkey vs. other markets in 2025.",
         src="Kaspi.kz Form 20-F, 2025", base=KASPI["data"], r=KASPI),
]
drows = "".join(f'''<tr><td><b>{d["name"]}</b><br><span class="muted">{d["what"]}</span></td><td>{d["cover"]}</td><td>{d["unit"]}</td>
<td>{d["src"]}</td><td class="nowrap"><a href="{d["base"]}.xlsx" download>XLSX</a> &middot; <a href="{d["base"]}.csv" download>CSV</a></td>
<td><a href="{d["r"]["url"]}">{d["r"]["title"].split(":")[0]}</a></td></tr>''' for d in DATASETS)
data_page = f'''<section class="page-head"><div class="wrap">
<h1>Data</h1>
<p>The figures behind every report. Each file names its sources and notes what the numbers do and do not include. Free to reuse with attribution to Steppe &amp; Silk Research.</p>
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
<p class="lead">Steppe &amp; Silk Research publishes independent research on companies and trade in Kazakhstan, Central Asia and China.</p>
<p>There are two formats. <b>Company notes</b> explain how a company makes money and what has changed, based on its annual report. <b>Trade briefs</b> show what Kazakhstan sells and buys, based on official statistics.</p>
<h2>How the research is made</h2>
<ul>
<li>Numbers come from annual reports and official statistics, and every source is linked.</li>
<li>The data behind each chart can be <a href="data.html">downloaded</a>.</li>
<li>When two sources disagree, as Kazakh and Chinese trade data do, the report says whose numbers it uses.</li>
<li>Opinions are kept apart from facts, in a section called "My view".</li>
<li>Nothing on this site is investment advice.</li>
</ul>
<p class="note">AI tools help collect data, run calculations and polish the English. The analysis and the conclusions are the author's own.</p>
<h2>Corrections</h2>
<p>If you find an error, please email me. Corrections are made openly and listed at the end of the report with their date.</p>
<h2>About the author</h2>
<p>I am Chingiz Bakytzhanov, an 18-year-old student from Kazakhstan. I speak Kazakh, Russian and English, and I plan to study finance because it explains how money and businesses really work. My interest in finance began when I became Director of Business and Finance at Earth Ambassadors, a youth organisation.</p>
<p>The idea for Steppe &amp; Silk Research came to me in September 2026, when I started looking at how Kazakhstan trades with China. I published the first two reports in October 2026.</p>
<h2 id="contact">Contact</h2>
<p>For questions about the research, collaboration or feedback, please write to me.</p>
<ul class="contact-list"><li><span>Email</span><a href="mailto:{EMAIL}">{EMAIL}</a></li></ul>
</div></div></section>'''
page("about.html", "About · Steppe & Silk Research", about, "about.html",
     "About Steppe & Silk Research, how its research is made, and its author.")

# Old addresses keep working.
redirect("companies.html", "research.html#companies")
redirect("trade.html", "research.html#trade")
redirect("contact.html", "about.html#contact")

# ---------- Sitemap, assets, link-preview cards ----------

urls = ["", "research.html", "data.html", "about.html"] + [r["url"] for r in REPORTS]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "".join(f"  <url><loc>{SITE}/{u}</loc><lastmod>2026-10-11</lastmod></url>\n" for u in urls) + "</urlset>\n")

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
                 '<div class="mid"><div><h1 style="font-size:46px">Independent research on companies and trade in Kazakhstan, Central Asia and China</h1>'
                 '<div class="cap">Company notes and trade briefs, with the data behind every chart.</div></div>'
                 '<div class="chart"><div class="cap" style="margin:0 0 6px;font-size:18px">Kazakhstan–China trade, $ billion</div>'
                 f'{columns([("Turnover", GREY, TURNOVER)], YEARS, w=420, h=280, hi=5, top=40, fmt="{:.0f}")}</div></div>'
                 f'<div class="foot"><span>{AUTHOR}</span><span>Kazakhstan &middot; Central Asia &middot; China</span></div>')
for slug, inner in cards.items():
    with open(os.path.join(og_dir, slug + ".html"), "w") as f:
        f.write(f'<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>{OG_CSS}</style></head>'
                f'<body><div class="c">{inner}</div></body></html>')
print("ok")
