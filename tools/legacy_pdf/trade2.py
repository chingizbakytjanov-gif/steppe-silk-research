import sys; sys.path.insert(0,sys.argv[3]); from style import CSS,FONT
view=open(sys.argv[2]).read().strip()
yrs=["2020","2021","2022","2023","2024","2025"]
kx=[9.0,9.9,13.2,14.7,14.9,15.2]; km=[6.4,8.3,11.0,16.8,15.2,18.9]; kt=[15.4,18.2,24.2,31.5,30.1,34.1]
D1="#3b3b3b"; L1="#a9a9a9"
# Figure 1 grouped bars with y axis
W,H=460,200; x0,y0,top=40,170,15; sc=(y0-top)/20
s=[f'<svg viewBox="0 0 {W} {H}" width="100%" {FONT} font-size="9">']
for t in range(0,21,5):
    y=y0-t*sc; s.append(f'<line x1="{x0}" x2="{W-5}" y1="{y:.1f}" y2="{y:.1f}" stroke="#ddd" stroke-width="0.6"/><text x="{x0-5}" y="{y+3:.1f}" text-anchor="end">{t}</text>')
gw=(W-5-x0)/6
for i,yv in enumerate(yrs):
    cx=x0+gw*i+gw/2
    for k,(v,c) in enumerate(((kx[i],D1),(km[i],L1))):
        h=v*sc; x=cx-22+k*22
        s.append(f'<rect x="{x:.1f}" y="{y0-h:.1f}" width="20" height="{h:.1f}" fill="{c}"/>')
    s.append(f'<text x="{cx:.1f}" y="{y0+13}" text-anchor="middle">{yv}</text>')
s.append(f'<line x1="{x0}" x2="{W-5}" y1="{y0}" y2="{y0}" stroke="#000" stroke-width="0.8"/>')
s.append(f'<text x="8" y="{top+60}" transform="rotate(-90 8 {top+60})" text-anchor="middle">$ billion</text>')
s.append(f'<rect x="{x0+8}" y="{top-2}" width="9" height="9" fill="{D1}"/><text x="{x0+21}" y="{top+6}">Exports to China</text><rect x="{x0+110}" y="{top-2}" width="9" height="9" fill="{L1}"/><text x="{x0+123}" y="{top+6}">Imports from China</text>')
s.append('</svg>'); f1="".join(s)
ex=[("Ores, slag and ash",3.94),("Oil and mineral fuels",3.28),("Copper",2.69),("Inorganic chemicals (incl. uranium)",1.78),("Iron and steel",1.10)]
im=[("Machinery and equipment",3.70),("Electrical and electronic equipment",2.39),("Vehicles",2.31),("Clothing (not knitted)",0.61),("Articles of iron or steel",0.58)]
W,H=460,215; lx=185; sc=60
s=[f'<svg viewBox="0 0 {W} {H}" width="100%" {FONT} font-size="9">']
def blk(y,title,items,c):
    o=[f'<text x="0" y="{y}" font-style="italic">{title}</text>']
    for j,(n,v) in enumerate(items):
        yy=y+8+j*15; w=v*sc
        o.append(f'<text x="{lx-6}" y="{yy+9}" text-anchor="end">{n}</text><rect x="{lx}" y="{yy}" width="{w:.1f}" height="11" fill="{c}"/><text x="{lx+w+4:.1f}" y="{yy+9}">{v:.2f}</text>')
    return o
s+=blk(12,"(a) Exports to China",ex,D1); s+=blk(115,"(b) Imports from China",im,L1)
s.append(f'<line x1="{lx}" x2="{lx}" y1="16" y2="{H-5}" stroke="#000" stroke-width="0.6"/></svg>'); f2="".join(s)
rows="".join(f"<tr><td>{n}</td>"+"".join(f"<td>{v:.1f}</td>" for v in vs)+"</tr>" for n,vs in (("Exports to China",kx),("Imports from China",km),("Total trade",kt)))
rows+="<tr><td>Balance</td>"+"".join(f"<td>{a-b:+.1f}</td>" for a,b in zip(kx,km))+"</tr>"
html=f"""<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>
<div class=title><h1>Raw Materials Out, Machines In:<br>Kazakhstan's Trade with China, 2020-2025</h1>
<div class=au>Chingiz Bakytzhanov</div><div class=dt>Independent research brief, October 2026</div></div>
<div class=abs><b>Summary.</b> This brief looks at goods trade between Kazakhstan and China from 2020 to 2025. According to Kazakhstan's official statistics, trade more than doubled over the period, from $15.4 billion to $34.1 billion, and China's share of Kazakhstan's foreign trade rose from 18.1% to 23.7%. The structure of trade, however, has barely changed: Kazakhstan exports mostly raw materials and imports machinery, electronics and vehicles. Since 2023 Kazakhstan has run a trade deficit with China, which reached $3.7 billion in 2025.</div>
<h2>1. Introduction</h2>
<p>China has become one of Kazakhstan's most important economic partners, and its role keeps growing. This brief asks three simple questions: what Kazakhstan sells to China, what it buys from China, and how the balance between the two has changed over the last six years.</p>
<h2>2. Data</h2>
<p>The main series come from Kazakhstan's official statistics (the Bureau of National Statistics, the Ministry of Trade and Integration and the State Revenue Committee), as published by government bodies and national media [1-6]. Data on goods by category are Kazakhstan's figures reported to UN Comtrade [8]. China publishes its own trade figures [1, 7]. They differ markedly from Kazakhstan's, so they are discussed separately in Section 4 and are not mixed with the Kazakh series. Figures for 2020 and 2021 come from news reports citing official bodies and are less reliable than later years.</p>
<h2>3. Findings</h2>
<div class=cap><b>Table 1.</b> Kazakhstan's goods trade with China, $ billion (Kazakh data)</div>
<table><tr><th></th>{''.join(f'<th>{y}</th>' for y in yrs)}</tr>{rows}</table>
<div class=tn>Note: total trade for 2022 is the sum of exports and imports; the ministry reported "more than $24 billion". The 2023 import figure is an early estimate that was later revised to about $15.4 billion. Sources: [1]-[6].</div>
<p style="margin-top:9px">Trade grew in almost every year, with the only pause in 2024, when turnover stayed at about $30 billion. Growth was driven mostly by imports. Between 2020 and 2025 imports from China nearly tripled, from $6.4 billion to $18.9 billion, while exports rose by about two thirds, from $9.0 billion to $15.2 billion (Figure 1).</p>
<div style="break-inside:avoid"><div class=cap><b>Figure 1.</b> Kazakhstan's exports to and imports from China, 2020-2025, $ billion</div>
<div class=fig>{f1}</div></div>
<p>As a result, the balance changed sign. Kazakhstan had a surplus with China of $2.6, $1.6 and $2.2 billion in 2020, 2021 and 2022, but it has been in deficit since 2023. In 2025 the deficit reached $3.7 billion, as imports grew by 24% and exports by only 2%.</p>
<p>The composition of trade explains much of this pattern (Figure 2). Kazakhstan's five largest exports to China in 2024 were ores, slag and ash, oil and fuels, copper, inorganic chemicals including uranium compounds, and iron and steel. All five are raw materials or products of primary processing, so their value depends heavily on world commodity prices. Its largest imports, by contrast, were finished goods: machinery and equipment ($3.7 billion), electronics ($2.4 billion) and vehicles ($2.3 billion).</p>
<div style="break-inside:avoid"><div class=cap><b>Figure 2.</b> Top five product groups in Kazakhstan's trade with China, 2024, $ billion</div>
<div class=fig>{f2}</div>
<div class=tn>Source: Kazakhstan's data reported to UN Comtrade, via Trading Economics [8].</div></div>
<h2>4. A note on the statistics</h2>
<p>The two countries record the same trade very differently. China reports $48.7 billion of trade with Kazakhstan in 2025, compared with $34.1 billion in Kazakhstan's own data [2, 7]. Most of the gap is on the Chinese export side: in 2024 China recorded $28.0 billion of goods sent to Kazakhstan, while Kazakhstan recorded only $15.2 billion arriving from China [1]. Such "mirror statistics" gaps usually come from goods passing through third countries, different valuation methods and under-declared imports. Any analysis of this trade should therefore state clearly whose data it uses.</p>
<h2>5. Author's view</h2>
<p>{view}</p>
<h2>References</h2>
<ol class=ref>
<li>Embassy of the Republic of Kazakhstan in the People's Republic of China. Trade and economic cooperation (2024 data, SRC and GACC). https://www.gov.kz/memleket/entities/mfa-beijing/activities/2110?lang=en</li>
<li>Association of Financiers of Kazakhstan. Kazakhstan-China commodity turnover, March 2026 (BNS data). https://afk.kz/2026/03/Kazakhstan-China-Commodity-Turnover-March2026.pdf</li>
<li>Kazinform. Trade turnover between Kazakhstan and China exceeded $31 billion in 2023. https://www.inform.kz/ru/tovarooborot-mezhdu-kazahstanom-i-kitaem-v-2023-godu-previsil-31-mlrd-d0a0bc</li>
<li>The Astana Times. Trade between China, Central Asian states reach $32.1 billion in 2022 (April 2023). https://astanatimes.com/2023/04/trade-between-china-central-asian-states-reach-32-1-billion-in-2022/</li>
<li>Kapital.kz. Kazakhstan's foreign trade and trade with China in 2021 (2022). https://kapital.kz/economic/104880/kak-razvivayut-sya-torgovyye-otnosheniya-kazakhstana-i-kitaya.html</li>
<li>Inbusiness.kz. Trade growth, exports and the opening of the Chinese market for Kazakhstan. https://inbusiness.kz/ru/news/rost-torgovli-eksport-i-otkrytie-kitajskogo-rynka-dlya-kazahstana-chto-govoryat-cifry</li>
<li>PwC China. Invest in Kazakhstan (April 2026), citing the General Administration of Customs of China. https://www.pwccn.com/zh/issues-based/invest-in-kazakhstan-apr2026.pdf</li>
<li>Trading Economics. Kazakhstan exports to China; Kazakhstan imports from China (UN Comtrade). https://tradingeconomics.com/kazakhstan/exports/china</li>
</ol>
</body></html>"""
open(sys.argv[1],"w").write(html)
