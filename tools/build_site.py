#!/usr/bin/env python3
"""Generate the static Steppe & Silk Research site into the given folder."""
import sys, os

OUT = sys.argv[1]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700'
         '&family=Source+Serif+4:wght@400;600&display=swap" rel="stylesheet">')

MARK = '''<svg class="brand-mark" viewBox="0 0 34 34" aria-hidden="true">
<rect width="34" height="34" rx="3" fill="#1f3550"/>
<circle cx="22" cy="12" r="4.5" fill="#d9b874"/>
<path d="M3 25 C9 19 13 21 17 23 S26 20 31 17" stroke="#fff" stroke-width="2" fill="none"/>
<path d="M3 29 H31" stroke="#a8792a" stroke-width="2"/></svg>'''

HERO_ART = '''<svg class="hero-art" viewBox="0 0 620 300" aria-hidden="true">
<path d="M0 250 L70 190 L120 220 L190 140 L250 200 L320 110 L390 180 L450 130 L520 190 L620 120 L620 300 L0 300Z" fill="#ffffff" fill-opacity=".1"/>
<path d="M0 270 C120 230 200 280 310 240 S500 200 620 230" stroke="#d9b874" stroke-width="3" stroke-dasharray="2 10" stroke-linecap="round" stroke-opacity=".6" fill="none"/>
<circle cx="560" cy="60" r="34" fill="#d9b874" fill-opacity=".85"/></svg>'''

NAV = [("index.html", "Home"), ("companies.html", "Companies"), ("trade.html", "Trade"),
       ("about.html", "About"), ("contact.html", "Contact")]


def page(path, title, body, active, desc):
    depth = path.count("/")
    pre = "../" * depth
    act = ' class="active"'
    nav = "".join(f'<a href="{pre}{h}"{act if h == active else ""}>{n}</a>' for h, n in NAV)
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="d7XHlEAizrVEeJg0uOvRMYoe6iXHknmiZpDfU_INxrk">
<meta name="google-site-verification" content="rOkVrHh45H8W7YMARKQRI90o3m_RzjbPe74PImvKOU8">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
{FONTS}
<link rel="stylesheet" href="{pre}assets/style.css">
<link rel="icon" href="{pre}assets/favicon.svg" type="image/svg+xml">
</head>
<body>
<header class="site-header"><div class="wrap">
<a class="brand" href="{pre}index.html">{MARK}<span class="brand-name">Steppe <span>&amp;</span> Silk Research</span></a>
<nav class="nav">{nav}</nav>
</div></header>
<main>
{body}
</main>
<footer class="site-footer"><div class="wrap">
<div>&copy; 2026 Steppe &amp; Silk Research &middot; Independent student research</div>
<div><a href="{pre}about.html">About</a> &nbsp;&middot;&nbsp; <a href="{pre}contact.html">Contact</a></div>
</div></footer>
</body>
</html>
'''
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(html)


def bars(values, labels, w=520, h=150, color="#1f3550", hi=None, fmt="{:.1f}", unit="", top=None):
    """Simple labelled bar chart as inline SVG."""
    n = len(values)
    top = top or max(values) * 1.15
    pad_b, pad_t = 24, 20
    gw = w / n
    bw = gw * 0.56
    out = [f'<svg viewBox="0 0 {w} {h}" role="img">']
    out.append(f'<line x1="0" y1="{h-pad_b}" x2="{w}" y2="{h-pad_b}" stroke="#cfc8bb"/>')
    for i, (v, lab) in enumerate(zip(values, labels)):
        bh = (h - pad_b - pad_t) * v / top
        x = i * gw + (gw - bw) / 2
        y = h - pad_b - bh
        c = "#a8792a" if hi is not None and i == hi else color
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{c}"/>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-size="13" font-family="Inter,Arial" fill="#1b2430" font-weight="600">{fmt.format(v)}{unit}</text>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{h-6}" text-anchor="middle" font-size="12" font-family="Inter,Arial" fill="#7a8390">{lab}</text>')
    out.append('</svg>')
    return "".join(out)


def grouped(a, b, labels, w=640, h=230):
    """Exports vs imports grouped bars."""
    n = len(labels)
    top = max(a + b) * 1.15
    pad_b, pad_t = 26, 34
    gw = w / n
    bw = gw * 0.3
    out = [f'<svg viewBox="0 0 {w} {h}" role="img">',
           f'<rect x="0" y="4" width="12" height="12" fill="#1f3550"/><text x="18" y="15" font-size="13" font-family="Inter,Arial" fill="#4a5563">Exports to China</text>',
           f'<rect x="150" y="4" width="12" height="12" fill="#a8792a"/><text x="168" y="15" font-size="13" font-family="Inter,Arial" fill="#4a5563">Imports from China</text>',
           f'<line x1="0" y1="{h-pad_b}" x2="{w}" y2="{h-pad_b}" stroke="#cfc8bb"/>']
    for i in range(n):
        cx = i * gw + gw / 2
        for j, (v, c) in enumerate(((a[i], "#1f3550"), (b[i], "#a8792a"))):
            bh = (h - pad_b - pad_t) * v / top
            x = cx - bw - 2 + j * (bw + 4)
            y = h - pad_b - bh
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{c}"/>')
            out.append(f'<text x="{x+bw/2:.1f}" y="{y-5:.1f}" text-anchor="middle" font-size="11" font-family="Inter,Arial" fill="#1b2430">{v:.1f}</text>')
        out.append(f'<text x="{cx:.1f}" y="{h-7}" text-anchor="middle" font-size="12" font-family="Inter,Arial" fill="#7a8390">{labels[i]}</text>')
    out.append('</svg>')
    return "".join(out)


YEARS = ["2020", "2021", "2022", "2023", "2024", "2025"]
TURNOVER = [15.4, 18.2, 24.2, 31.5, 30.1, 34.1]
EXPORTS = [9.0, 9.9, 13.2, 14.7, 14.9, 15.2]
IMPORTS = [6.4, 8.3, 11.0, 16.8, 15.2, 18.9]
MARGIN = [44.4, 41.7, 26.4]
MKT_SHARE = [22.9, 28.3, 47.1]

KASPI = dict(
    url="research/kaspi-hepsiburada.html",
    tag="Companies",
    title="Bigger but Less Profitable: Kaspi.kz after the Hepsiburada Acquisition",
    date="October 2026",
    summary=("In January 2025 Kaspi.kz bought a controlling stake in Hepsiburada, a leading Turkish online "
             "marketplace. The deal lifted revenue by 60% in 2025 but left net income almost flat, cutting the "
             "net margin from 41.7% to 26.4%. The Kazakh business stayed highly profitable; the fall comes from Turkey."),
    art=bars(MARGIN, ["2023", "2024", "2025"], w=420, h=150, hi=2, unit="%", top=55),
    art_caption="Net margin, %",
    pdf="reports/kaspi-hepsiburada-2026.pdf",
)
TRADE = dict(
    url="research/kazakhstan-china-trade.html",
    tag="Trade",
    title="Raw Materials Out, Machines In: Kazakhstan's Trade with China, 2020–2025",
    date="October 2026",
    summary=("Trade between Kazakhstan and China more than doubled, from $15.4 billion to $34.1 billion. Kazakhstan "
             "still sells mostly raw materials and buys machinery, electronics and vehicles. Since 2023 it has run a "
             "trade deficit with China, which reached $3.7 billion in 2025."),
    art=bars(TURNOVER, YEARS, w=420, h=150, hi=5, top=40),
    art_caption="Trade turnover, $ bn",
    pdf="reports/kazakhstan-china-trade-2026.pdf",
)


def card(r):
    return f'''<a class="card" href="{r["url"]}">
<div class="card-art">{r["art"]}</div>
<div class="card-body"><div class="tag">{r["tag"]}</div><h3>{r["title"]}</h3>
<p>{r["summary"].split(". ")[0]}.</p>
<div class="card-meta"><span>{r["date"]}</span><span>Read the report &rarr;</span></div></div></a>'''


def list_item(r):
    return f'''<a class="list-item" href="{r["url"]}">
<div class="card-art">{r["art"]}</div>
<div><div class="tag">{r["tag"]}</div><h3>{r["title"]}</h3><p>{r["summary"]}</p>
<div class="small">{r["date"]} &middot; PDF report</div></div></a>'''


# Home
home = f'''<section class="hero"><div class="wrap">
{HERO_ART}
<p class="eyebrow">Independent student research</p>
<h1>Kazakhstan, its neighbours and China, in numbers</h1>
<p>Research on companies and trade in Central Asia and China, based on annual reports and official statistics.</p>
<a class="btn btn-gold" href="#latest">Latest research</a><a class="btn btn-line" href="about.html">About the project</a>
</div></section>

<section class="stats"><div class="wrap">
<div class="stat"><div class="stat-num">$34.1 bn</div><div class="stat-label">Kazakhstan–China trade turnover, 2025</div><div class="stat-src">Bureau of National Statistics of Kazakhstan</div></div>
<div class="stat"><div class="stat-num">23.7%</div><div class="stat-label">China's share of Kazakhstan's foreign trade, 2025</div><div class="stat-src">Bureau of National Statistics of Kazakhstan</div></div>
<div class="stat"><div class="stat-num">26.4%</div><div class="stat-label">Kaspi.kz net margin after buying Hepsiburada, 2025</div><div class="stat-src">Kaspi.kz annual report (Form 20-F)</div></div>
</div></section>

<section class="section" id="latest"><div class="wrap">
<div class="section-head"><h2>Latest research</h2></div>
<div class="cards">{card(KASPI)}{card(TRADE)}</div>
</div></section>

<section class="section section-alt"><div class="wrap">
<div class="section-head"><h2>Two kinds of work</h2></div>
<div class="cards">
<a class="card" href="companies.html"><div class="card-body"><div class="tag">Companies</div><h3>How companies make money</h3><p>Analyses of the largest companies of Kazakhstan, and Chinese companies active in the region, based on their annual reports.</p><div class="card-meta"><span>1 report</span><span>View all &rarr;</span></div></div></a>
<a class="card" href="trade.html"><div class="card-body"><div class="tag">Trade</div><h3>What Kazakhstan sells and buys</h3><p>Reviews of trade between Kazakhstan, China and its neighbours, based on official statistics.</p><div class="card-meta"><span>1 report</span><span>View all &rarr;</span></div></div></a>
</div></div></section>'''
page("index.html", "Steppe & Silk Research", home, "index.html",
     "Independent student research on companies and trade in Kazakhstan, Central Asia and China.")

# Section pages
companies = f'''<section class="page-head"><div class="wrap"><div class="tag">Research</div><h1>Companies</h1>
<p>Company analyses based on annual reports: how the largest companies of Kazakhstan, and Chinese companies active in the region, make money and what has changed.</p></div></section>
<section class="section"><div class="wrap">{list_item(KASPI)}</div></section>'''
page("companies.html", "Companies · Steppe & Silk Research", companies, "companies.html",
     "Company analyses based on annual reports.")

trade = f'''<section class="page-head"><div class="wrap"><div class="tag">Research</div><h1>Trade</h1>
<p>Trade reviews based on official statistics: what Kazakhstan sells to and buys from China and its neighbours, and how this is changing.</p></div></section>
<section class="section"><div class="wrap">{list_item(TRADE)}</div></section>'''
page("trade.html", "Trade · Steppe & Silk Research", trade, "trade.html",
     "Trade reviews based on official statistics.")


def report(r, findings, figures, view, facts, sources, active):
    figs = "".join(f'<figure class="figure">{svg}<figcaption><b>{cap}</b> {src}</figcaption></figure>'
                   for svg, cap, src in figures)
    items = "".join(f"<li>{f}</li>" for f in findings)
    kv = "".join(f'<div class="kv"><span>{k}</span><b>{v}</b></div>' for k, v in facts)
    srcs = "".join(f"<li>{s}</li>" for s in sources)
    body = f'''<section class="report-head"><div class="wrap">
<div class="crumbs"><a href="../{active}">{r["tag"]}</a> &rsaquo; Report</div>
<h1>{r["title"]}</h1>
<div class="byline">By Chingiz Bakytzhanov &middot; {r["date"]}</div>
</div></section>
<div class="wrap"><div class="report-grid">
<article class="report-main">
<h2>Summary</h2><p>{r["summary"]}</p>
<h2>Key findings</h2><ul>{items}</ul>
<h2>In charts</h2>{figs}
<h2>My view</h2><div class="view"><span class="view-label">Author's view</span>{view}</div>
<h2>Full report</h2>
<iframe class="pdf-frame" src="../{r["pdf"]}" title="{r["title"]} (PDF)"></iframe>
</article>
<aside>
<div class="aside-box"><h4>Key figures</h4>{kv}</div>
<div class="aside-box"><h4>Report</h4><a class="btn btn-gold" href="../{r["pdf"]}" target="_blank" rel="noopener">Open PDF</a></div>
<div class="aside-box"><h4>Sources</h4><ul>{srcs}</ul></div>
</aside>
</div></div>'''
    page(r["url"], r["title"] + " · Steppe & Silk Research", body, active, r["summary"][:150])


report(KASPI,
       ["Revenue grew by 60% in 2025 after Hepsiburada was consolidated, up from 32% growth in 2024.",
        "Net income rose by only 1%, so the net margin fell from 41.7% to 26.4%.",
        "The marketplace segment grew from 22.9% to 47.1% of segment revenue, mostly because of Turkey.",
        "Kaspi bought 65.4% of Hepsiburada for about $1.13 billion and raised its stake to 85% by January 2026."],
       [(bars(MARGIN, ["2023", "2024", "2025"], w=560, h=200, hi=2, unit="%", top=55),
         "Figure 1. Net margin, %.", "Source: Kaspi.kz Form 20-F, 2025."),
        (bars(MKT_SHARE, ["2023", "2024", "2025"], w=560, h=200, hi=2, unit="%", top=60),
         "Figure 2. Marketplace share of segment revenue, %.", "Source: Kaspi.kz Form 20-F, 2025.")],
       "I don't consider the fall in margin a big problem. Large acquisitions and investments dilute margins at first, "
       "because the new business is not yet as profitable as the main one. In my opinion, it is a great tactic to grow "
       "Kaspi beyond Kazakhstan, because it gives the company more ways to make a profit. I would buy Kaspi shares as a "
       "long-term investment.",
       [("Revenue growth, 2025", "+60%"), ("Net income growth, 2025", "+1%"), ("Net margin, 2024", "41.7%"),
        ("Net margin, 2025", "26.4%"), ("Stake in Hepsiburada", "85%")],
       ["Kaspi.kz, Annual Report on Form 20-F for 2025", "Kaspi.kz investor relations, ir.kaspi.kz"],
       "companies.html")

report(TRADE,
       ["Trade turnover grew from $15.4 billion in 2020 to $34.1 billion in 2025.",
        "China's share of Kazakhstan's foreign trade rose from 18.1% to 23.7%.",
        "Kazakhstan exports mainly ores, oil, copper and uranium, and imports machinery, electronics and vehicles.",
        "A surplus of $2.6 billion in 2020 turned into a deficit of $3.7 billion in 2025."],
       [(bars(TURNOVER, YEARS, w=640, h=210, hi=5, top=40),
         "Figure 1. Kazakhstan–China trade turnover, $ bn.", "Source: Bureau of National Statistics of Kazakhstan."),
        (grouped(EXPORTS, IMPORTS, YEARS),
         "Figure 2. Kazakhstan's exports to and imports from China, $ bn.",
         "Source: Bureau of National Statistics of Kazakhstan. Chinese customs data (GACC) show higher values; see the full report.")],
       open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "view2.txt")).read().strip(),
       [("Turnover, 2025", "$34.1 bn"), ("Exports, 2025", "$15.2 bn"), ("Imports, 2025", "$18.9 bn"),
        ("Balance, 2025", "−$3.7 bn"), ("China's share", "23.7%")],
       ["Bureau of National Statistics of Kazakhstan", "General Administration of Customs of China (GACC)"],
       "trade.html")

about = '''<section class="page-head"><div class="wrap"><div class="tag">About</div><h1>About the project</h1></div></section>
<section class="section"><div class="wrap prose">
<p>I am Chingiz Bakytzhanov, an 18-year-old student from Kazakhstan. I speak Kazakh, Russian and English, and I plan to study finance because it explains how money and businesses really work. My interest in finance began when I became Director of Business and Finance at Earth Ambassadors, a youth organisation.</p>
<p>The idea for Steppe &amp; Silk Research came to me in September 2026, when I started looking at how Kazakhstan trades with China. In October I published the first two reports. Each report is based on official statistics or company annual reports, and ends with my own view.</p>
<p class="note">I use AI tools to help collect data, run calculations and polish my English. The conclusions and opinions are my own.</p>
</div></section>'''
page("about.html", "About · Steppe & Silk Research", about, "about.html", "About Steppe & Silk Research and its author.")

contact = '''<section class="page-head"><div class="wrap"><div class="tag">Contact</div><h1>Contact</h1>
<p>For enquiries regarding my research, collaboration or feedback, please contact me by email.</p></div></section>
<section class="section"><div class="wrap prose">
<ul class="contact-list">
<li><span>Email</span><a href="mailto:chingiz.bakytjanov@gmail.com">chingiz.bakytjanov@gmail.com</a></li>
</ul></div></section>'''
page("contact.html", "Contact · Steppe & Silk Research", contact, "contact.html", "Contact the author of Steppe & Silk Research.")

with open(os.path.join(OUT, "assets", "favicon.svg"), "w") as f:
    f.write(MARK.replace(' class="brand-mark"', ' xmlns="http://www.w3.org/2000/svg"'))
print("ok")
