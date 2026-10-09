#!/usr/bin/env python3
"""Generate the static Steppe & Silk Research site (v2 layout) into the given folder."""
import sys, os

OUT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500'
         '&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400'
         '&display=swap" rel="stylesheet">')

INK, GREY, ACCENT = "#161616", "#b9b9b4", "#a63d1f"
CHART_FONT = "IBM Plex Sans,Arial"

NAV = [("research.html", "Research"), ("about.html", "About")]

FAVICON = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<rect width="32" height="32" fill="{INK}"/><rect x="6" y="18" width="5" height="8" fill="#fff"/>
<rect x="13.5" y="12" width="5" height="14" fill="#fff"/><rect x="21" y="6" width="5" height="20" fill="{ACCENT}"/></svg>'''


def page(path, title, body, active, desc):
    pre = "../" * path.count("/")
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
<script>document.documentElement.classList.add("js")</script>
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
<div>Steppe &amp; Silk Research &middot; Chingiz Bakytzhanov, 2026</div>
<div><a href="mailto:chingiz.bakytjanov@gmail.com">chingiz.bakytjanov@gmail.com</a></div>
</div></footer>
</body>
</html>
'''
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(html)


def redirect(path, target):
    with open(os.path.join(OUT, path), "w") as f:
        f.write(f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={target}">'
                f'<link rel="canonical" href="{target}"><a href="{target}">Moved</a>\n')


def bars(values, labels, w=520, h=150, hi=None, fmt="{:.1f}", unit="", top=None):
    """Labelled bar chart: grey bars, the highlighted one in the accent colour."""
    n = len(values)
    top = top or max(values) * 1.15
    pad_b, pad_t = 24, 20
    gw = w / n
    bw = gw * 0.5
    out = [f'<svg class="chart" viewBox="0 0 {w} {h}" role="img">',
           f'<line x1="0" y1="{h-pad_b}" x2="{w}" y2="{h-pad_b}" stroke="{INK}"/>']
    for i, (v, lab) in enumerate(zip(values, labels)):
        bh = (h - pad_b - pad_t) * v / top
        x = i * gw + (gw - bw) / 2
        y = h - pad_b - bh
        c = ACCENT if i == hi else GREY
        out.append(f'<rect class="bar" style="--i:{i}" x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{c}"/>')
        out.append(f'<text class="val" style="--i:{i}" x="{x+bw/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-size="13" font-family="{CHART_FONT}" fill="{INK}" font-weight="500">{fmt.format(v)}{unit}</text>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{h-6}" text-anchor="middle" font-size="12" font-family="{CHART_FONT}" fill="#6b6b6b">{lab}</text>')
    out.append('</svg>')
    return "".join(out)


def grouped(a, b, labels, w=640, h=230):
    """Exports vs imports grouped bars."""
    n = len(labels)
    top = max(a + b) * 1.15
    pad_b, pad_t = 26, 34
    gw = w / n
    bw = gw * 0.3
    out = [f'<svg class="chart" viewBox="0 0 {w} {h}" role="img">',
           f'<rect x="0" y="4" width="12" height="12" fill="{GREY}"/><text x="18" y="15" font-size="13" font-family="{CHART_FONT}" fill="#444">Exports to China</text>',
           f'<rect x="150" y="4" width="12" height="12" fill="{ACCENT}"/><text x="168" y="15" font-size="13" font-family="{CHART_FONT}" fill="#444">Imports from China</text>',
           f'<line x1="0" y1="{h-pad_b}" x2="{w}" y2="{h-pad_b}" stroke="{INK}"/>']
    for i in range(n):
        cx = i * gw + gw / 2
        for j, (v, c) in enumerate(((a[i], GREY), (b[i], ACCENT))):
            bh = (h - pad_b - pad_t) * v / top
            x = cx - bw - 2 + j * (bw + 4)
            y = h - pad_b - bh
            out.append(f'<rect class="bar" style="--i:{i}" x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{c}"/>')
            out.append(f'<text class="val" style="--i:{i}" x="{x+bw/2:.1f}" y="{y-5:.1f}" text-anchor="middle" font-size="11" font-family="{CHART_FONT}" fill="{INK}">{v:.1f}</text>')
        out.append(f'<text x="{cx:.1f}" y="{h-7}" text-anchor="middle" font-size="12" font-family="{CHART_FONT}" fill="#6b6b6b">{labels[i]}</text>')
    out.append('</svg>')
    return "".join(out)


YEARS = ["2020", "2021", "2022", "2023", "2024", "2025"]
TURNOVER = [15.4, 18.2, 24.2, 31.5, 30.1, 34.1]
EXPORTS = [9.0, 9.9, 13.2, 14.7, 14.9, 15.2]
IMPORTS = [6.4, 8.3, 11.0, 16.8, 15.2, 18.9]
MARGIN = [44.4, 41.7, 26.4]
MKT_SHARE = [22.9, 28.3, 47.1]

# Texts Chingiz rewrites in his own words (see TEXTS-TO-REWRITE in the thread).
HOME_INTRO = ("I'm Chingiz, a student from Kazakhstan. Here I publish my own research on companies and trade "
              "in Kazakhstan, Central Asia and China, built on annual reports and official statistics. "
              "Every report ends with what I think.")

KASPI = dict(
    url="research/kaspi-hepsiburada.html",
    tag="Companies",
    title="Bigger but Less Profitable: Kaspi.kz after the Hepsiburada Acquisition",
    date="Oct 2026",
    date_long="October 2026",
    summary=("In January 2025 Kaspi.kz bought a controlling stake in Hepsiburada, a leading Turkish online "
             "marketplace. The deal lifted revenue by 60% in 2025 but left net income almost flat, cutting the "
             "net margin from 41.7% to 26.4%. The Kazakh business stayed highly profitable; the fall comes from Turkey."),
    line="Revenue up 60%, net income up 1%: what the Turkish deal did to Kaspi's margins.",
    art=bars(MARGIN, ["2023", "2024", "2025"], w=300, h=130, hi=2, unit="%", top=55),
    pdf="reports/kaspi-hepsiburada-2026.pdf",
)
TRADE = dict(
    url="research/kazakhstan-china-trade.html",
    tag="Trade",
    title="Raw Materials Out, Machines In: Kazakhstan's Trade with China, 2020–2025",
    date="Oct 2026",
    date_long="October 2026",
    summary=("Trade between Kazakhstan and China more than doubled, from $15.4 billion to $34.1 billion. Kazakhstan "
             "still sells mostly raw materials and buys machinery, electronics and vehicles. Since 2023 it has run a "
             "trade deficit with China, which reached $3.7 billion in 2025."),
    line="Trade more than doubled in five years, and a surplus turned into a $3.7 billion deficit.",
    art=bars(TURNOVER, YEARS, w=300, h=130, hi=5, top=40, fmt="{:.0f}"),
    pdf="reports/kazakhstan-china-trade-2026.pdf",
)
REPORTS = [KASPI, TRADE]


def row(r, pre=""):
    return f'''<a class="row" href="{pre}{r["url"]}" data-type="{r["tag"].lower()}">
<div class="row-date">{r["date"]}</div>
<div class="row-main"><div class="label">{r["tag"]}</div><h3>{r["title"]}</h3><p>{r["line"]}</p></div>
<div class="row-art">{r["art"]}</div></a>'''


# Home
home = f'''<section class="intro"><div class="wrap">
<h1 class="split">Companies and trade in Kazakhstan, Central Asia and China</h1>
<p class="intro-text">{HOME_INTRO}</p>
<p class="intro-more"><a href="about.html">More about me and the project &rarr;</a></p>
</div></section>

<section class="block"><div class="wrap">
<div class="block-head"><h2>Research</h2><a href="research.html">All research &rarr;</a></div>
<div class="rows">{"".join(row(r) for r in REPORTS)}</div>
</div></section>

<section class="block block-chart"><div class="wrap">
<div class="block-head"><h2>Chart</h2></div>
<figure class="figure figure-wide">
<div class="fig-title">Kazakhstan–China trade turnover, $ billion</div>
{bars(TURNOVER, YEARS, w=760, h=200, hi=5, top=40)}
<figcaption>Source: Bureau of National Statistics of Kazakhstan. From <a href="research/kazakhstan-china-trade.html">Raw Materials Out, Machines In</a>.</figcaption>
</figure>
</div></section>'''
page("index.html", "Steppe & Silk Research", home, "",
     "Independent research on companies and trade in Kazakhstan, Central Asia and China, by Chingiz Bakytzhanov.")

# Research (all reports, filtered by type)
counts = {t: sum(r["tag"] == t for r in REPORTS) for t in ("Companies", "Trade")}
research = f'''<section class="page-head"><div class="wrap">
<h1 class="split">Research</h1>
<p>Two types of work. <b>Companies</b>: how a company makes money and what has changed, based on its annual report.
<b>Trade</b>: what Kazakhstan sells and buys, based on official statistics.</p>
<div class="filters">
<button class="on" data-f="all">All <span>{len(REPORTS)}</span></button>
<button data-f="companies">Companies <span>{counts["Companies"]}</span></button>
<button data-f="trade">Trade <span>{counts["Trade"]}</span></button>
</div>
</div></section>
<section class="block"><div class="wrap"><div class="rows" id="rows">{"".join(row(r) for r in REPORTS)}</div></div></section>
<script>
(function () {{
  var btns = document.querySelectorAll('.filters button');
  function show(f) {{
    btns.forEach(function (b) {{ b.classList.toggle('on', b.dataset.f === f); }});
    document.querySelectorAll('#rows .row').forEach(function (r) {{
      r.style.display = (f === 'all' || r.dataset.type === f) ? '' : 'none';
      r.style.viewTransitionName = 'row-' + r.dataset.type;
    }});
  }}
  btns.forEach(function (b) {{ b.addEventListener('click', function () {{ if (document.startViewTransition) document.startViewTransition(function () {{ show(b.dataset.f); }}); else show(b.dataset.f); history.replaceState(null, '', b.dataset.f === 'all' ? 'research.html' : '#' + b.dataset.f); }}); }});
  var h = location.hash.slice(1);
  if (h === 'companies' || h === 'trade') show(h);
}})();
</script>'''
page("research.html", "Research · Steppe & Silk Research", research, "research.html",
     "Company analyses and trade reviews on Kazakhstan, Central Asia and China.")

# Old addresses keep working.
redirect("companies.html", "research.html#companies")
redirect("trade.html", "research.html#trade")
redirect("contact.html", "about.html#contact")


def report(r, findings, figures, view, facts, sources):
    figs = "".join(f'<figure class="figure"><div class="fig-title">{cap}</div>{svg}<figcaption>{src}</figcaption></figure>'
                   for svg, cap, src in figures)
    items = "".join(f"<li>{f}</li>" for f in findings)
    kv = "".join(f'<div class="fact"><div class="fact-num">{v}</div><div class="fact-label">{k}</div></div>' for k, v in facts)
    srcs = "".join(f"<li>{s}</li>" for s in sources)
    body = f'''<article class="report"><div class="wrap">
<header class="report-head">
<div class="label"><a href="../research.html#{r["tag"].lower()}">{r["tag"]}</a> &middot; Report</div>
<h1 class="split">{r["title"]}</h1>
<div class="byline">Chingiz Bakytzhanov &middot; {r["date_long"]} &middot; <a href="../{r["pdf"]}" target="_blank" rel="noopener">Download PDF</a></div>
</header>
<div class="facts">{kv}</div>
<div class="report-body">
<h2>Summary</h2><p>{r["summary"]}</p>
<h2>Key findings</h2><ol>{items}</ol>
{figs}
<h2>My view</h2><blockquote class="view">{view}</blockquote>
<h2>Sources</h2><ul class="sources">{srcs}</ul>
<h2>Full report</h2>
<iframe class="pdf-frame" src="../{r["pdf"]}" title="{r["title"]} (PDF)"></iframe>
</div>
</div></article>'''
    page(r["url"], r["title"] + " · Steppe & Silk Research", body, "research.html", r["summary"][:150])


report(KASPI,
       ["Revenue grew by 60% in 2025 after Hepsiburada was consolidated, up from 32% growth in 2024.",
        "Net income rose by only 1%, so the net margin fell from 41.7% to 26.4%.",
        "The marketplace segment grew from 22.9% to 47.1% of segment revenue, mostly because of Turkey.",
        "Kaspi bought 65.4% of Hepsiburada for about $1.13 billion and raised its stake to 85% by January 2026."],
       [(bars(MARGIN, ["2023", "2024", "2025"], w=640, h=210, hi=2, unit="%", top=55),
         "Figure 1. Net margin, %", "Source: Kaspi.kz Form 20-F, 2025."),
        (bars(MKT_SHARE, ["2023", "2024", "2025"], w=640, h=210, hi=2, unit="%", top=60),
         "Figure 2. Marketplace share of segment revenue, %", "Source: Kaspi.kz Form 20-F, 2025.")],
       "I don't consider the fall in margin a big problem. Large acquisitions and investments dilute margins at first, "
       "because the new business is not yet as profitable as the main one. In my opinion, it is a great tactic to grow "
       "Kaspi beyond Kazakhstan, because it gives the company more ways to make a profit. I would buy Kaspi shares as a "
       "long-term investment.",
       [("Revenue growth, 2025", "+60%"), ("Net income growth, 2025", "+1%"), ("Net margin, 2024", "41.7%"),
        ("Net margin, 2025", "26.4%"), ("Stake in Hepsiburada", "85%")],
       ["Kaspi.kz, Annual Report on Form 20-F for 2025", "Kaspi.kz investor relations, ir.kaspi.kz"])

report(TRADE,
       ["Trade turnover grew from $15.4 billion in 2020 to $34.1 billion in 2025.",
        "China's share of Kazakhstan's foreign trade rose from 18.1% to 23.7%.",
        "Kazakhstan exports mainly ores, oil, copper and uranium, and imports machinery, electronics and vehicles.",
        "A surplus of $2.6 billion in 2020 turned into a deficit of $3.7 billion in 2025."],
       [(bars(TURNOVER, YEARS, w=640, h=210, hi=5, top=40),
         "Figure 1. Kazakhstan–China trade turnover, $ bn", "Source: Bureau of National Statistics of Kazakhstan."),
        (grouped(EXPORTS, IMPORTS, YEARS),
         "Figure 2. Kazakhstan's exports to and imports from China, $ bn",
         "Source: Bureau of National Statistics of Kazakhstan. Chinese customs data (GACC) show higher values; see the full report.")],
       open(os.path.join(HERE, "view2.txt")).read().strip(),
       [("Turnover, 2025", "$34.1 bn"), ("Exports, 2025", "$15.2 bn"), ("Imports, 2025", "$18.9 bn"),
        ("Balance, 2025", "−$3.7 bn"), ("China's share", "23.7%")],
       ["Bureau of National Statistics of Kazakhstan", "General Administration of Customs of China (GACC)"])

about = '''<section class="page-head"><div class="wrap"><h1 class="split">About</h1></div></section>
<section class="block"><div class="wrap"><div class="prose">
<p>I am Chingiz Bakytzhanov, an 18-year-old student from Kazakhstan. I speak Kazakh, Russian and English, and I plan to study finance because it explains how money and businesses really work. My interest in finance began when I became Director of Business and Finance at Earth Ambassadors, a youth organisation.</p>
<p>The idea for Steppe &amp; Silk Research came to me in September 2026, when I started looking at how Kazakhstan trades with China. In October I published the first two reports. Each report is based on official statistics or company annual reports, and ends with my own view.</p>
<p class="note">I use AI tools to help collect data, run calculations and polish my English. The conclusions and opinions are my own.</p>
<h2 id="contact">Contact</h2>
<p>For enquiries regarding my research, collaboration or feedback, please contact me by email.</p>
<ul class="contact-list"><li><span>Email</span><a href="mailto:chingiz.bakytjanov@gmail.com">chingiz.bakytjanov@gmail.com</a></li></ul>
</div></div></section>'''
page("about.html", "About · Steppe & Silk Research", about, "about.html", "About Steppe & Silk Research and its author.")

os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
with open(os.path.join(OUT, "assets", "favicon.svg"), "w") as f:
    f.write(FAVICON)
for src, dst in (("style_v2.css", "style.css"), ("site_v2.js", "site.js")):
    with open(os.path.join(HERE, src)) as a, open(os.path.join(OUT, "assets", dst), "w") as b:
        b.write(a.read())
print("ok")
