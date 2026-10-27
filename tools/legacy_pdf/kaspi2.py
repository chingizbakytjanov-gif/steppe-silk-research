import sys; sys.path.insert(0,sys.argv[2]); from style import CSS,FONT
yrs=["2023","2024","2025"]
pay=[478684,587097,658726]; mkt=[448223,732943,1931472]; fin=[1026721,1281827,1542934]
seg=[1953068,2586381,4101961]; rev=[1913490,2532156,4046074]; ni=[848770,1056834,1067707]
C={"fin":"#2b2b2b","pay":"#8a8a8a","mkt":"#c8c8c8"}
W,H=300,210; x0,y0,top=34,180,22; sc=(y0-top)/4.5e6
s=[f'<svg viewBox="0 0 {W} {H}" width="100%" {FONT} font-size="9">']
for t in range(0,5):
    y=y0-t*1e6*sc; s.append(f'<line x1="{x0}" x2="{W-5}" y1="{y:.1f}" y2="{y:.1f}" stroke="#ddd" stroke-width="0.6"/><text x="{x0-5}" y="{y+3:.1f}" text-anchor="end">{t}</text>')
for i,yv in enumerate(yrs):
    x=x0+18+i*82; cur=y0
    for k,v in (("fin",fin[i]),("pay",pay[i]),("mkt",mkt[i])):
        h=v*sc; cur-=h; s.append(f'<rect x="{x}" y="{cur:.1f}" width="44" height="{h:.1f}" fill="{C[k]}" stroke="#000" stroke-width="0.3"/>')
    s.append(f'<text x="{x+22}" y="{y0+13}" text-anchor="middle">{yv}</text>')
s.append(f'<line x1="{x0}" x2="{W-5}" y1="{y0}" y2="{y0}" stroke="#000" stroke-width="0.8"/>')
for j,(k,l) in enumerate((("fin","Fintech"),("pay","Payments"),("mkt","Marketplace"))):
    s.append(f'<rect x="{x0+6+j*80}" y="4" width="9" height="9" fill="{C[k]}" stroke="#000" stroke-width="0.3"/><text x="{x0+19+j*80}" y="12">{l}</text>')
s.append('</svg>'); f1="".join(s)
m=[a/b for a,b in zip(ni,rev)]
s=[f'<svg viewBox="0 0 {W} {H}" width="100%" {FONT} font-size="9">']; sc=(y0-top)/0.5
for t in range(0,51,10):
    y=y0-t/100*sc; s.append(f'<line x1="{x0}" x2="{W-5}" y1="{y:.1f}" y2="{y:.1f}" stroke="#ddd" stroke-width="0.6"/><text x="{x0-5}" y="{y+3:.1f}" text-anchor="end">{t}%</text>')
for i,yv in enumerate(yrs):
    x=x0+18+i*82; h=m[i]*sc
    s.append(f'<rect x="{x}" y="{y0-h:.1f}" width="44" height="{h:.1f}" fill="#4a4a4a"/><text x="{x+22}" y="{y0-h-4:.1f}" text-anchor="middle">{m[i]*100:.1f}%</text><text x="{x+22}" y="{y0+13}" text-anchor="middle">{yv}</text>')
s.append(f'<line x1="{x0}" x2="{W-5}" y1="{y0}" y2="{y0}" stroke="#000" stroke-width="0.8"/></svg>'); f2="".join(s)
f=lambda v:f"{v:,}"
g=lambda a,b:f"{(b-a)/a*100:+.1f}%"
rows="".join(f"<tr><td>{n}</td>"+"".join(f"<td>{f(v)}</td>" for v in vs)+"</tr>" for n,vs in (("Payments",pay),("Marketplace",mkt),("Fintech",fin)))
rows+="<tr><td><b>Total revenue</b></td>"+"".join(f"<td><b>{f(v)}</b></td>" for v in rev)+"</tr>"
rows+="<tr><td><b>Net income</b></td>"+"".join(f"<td><b>{f(v)}</b></td>" for v in ni)+"</tr>"
rows+=f"<tr><td>Revenue growth</td><td>n/a</td><td>{g(rev[0],rev[1])}</td><td>{g(rev[1],rev[2])}</td></tr>"
rows+=f"<tr><td>Net income growth</td><td>n/a</td><td>{g(ni[0],ni[1])}</td><td>{g(ni[1],ni[2])}</td></tr>"
rows+="<tr><td>Net margin</td>"+"".join(f"<td>{x*100:.1f}%</td>" for x in m)+"</tr>"
rows+="<tr><td>Marketplace share of segment revenue</td>"+"".join(f"<td>{a/b*100:.1f}%</td>" for a,b in zip(mkt,seg))+"</tr>"
view="I don't consider the fall in margin a big problem. Large acquisitions and investments dilute margins at first, because the new business is not yet as profitable as the main one. In my opinion, it is a great tactic to grow Kaspi beyond Kazakhstan, because it gives the company more ways to make a profit. I would buy Kaspi shares as a long-term investment."
html=f"""<!doctype html><html><head><meta charset=utf-8><style>{CSS}
.two{{display:flex;gap:18px}} .two>div{{flex:1}}</style></head><body>
<div class=title><h1>Bigger but Less Profitable:<br>Kaspi.kz after the Hepsiburada Acquisition</h1>
<div class=au>Chingiz Bakytzhanov</div><div class=dt>Independent investment note, October 2026</div></div>
<div class=abs><b>Summary.</b> In January 2025 Kaspi.kz, a leading Kazakh fintech and e-commerce company, bought a controlling stake in Hepsiburada, a leading Turkish online marketplace. Based on Kaspi's annual report for 2025, this note shows that the deal lifted revenue by 60% but left net income almost flat, cutting the net margin from 41.7% to 26.4%. The Kazakh business remained highly profitable, and the fall in margin comes from the Turkish business.</div>
<h2>1. The company</h2>
<p>Kaspi.kz operates a "super app" that combines payments, online shopping and personal finance. At the end of 2025 the app had about 15.7 million monthly active users, 68% of whom used it every day, and about 764,000 active merchants [1]. The company reports three segments: Payments, Marketplace (e-commerce) and Fintech (consumer loans and deposits). Its shares are listed on NASDAQ under the ticker KSPI.</p>
<h2>2. Results, 2023-2025</h2>
<div class=cap><b>Table 1.</b> Kaspi.kz key financials, ₸ million</div>
<table><tr><th></th>{''.join(f'<th>{y}</th>' for y in yrs)}</tr>{rows}</table>
<div class=tn>Note: segment revenue is shown before inter-segment eliminations and customer rewards, so the three segments do not add up exactly to total revenue. Source: [1], segment and earnings notes, pp. F-33 to F-42; growth and margins calculated from these figures.</div>
<div class=two style="margin-top:8px;break-inside:avoid">
<div><div class=cap><b>Figure 1.</b> Segment revenue, ₸ trillion</div>{f1}</div>
<div><div class=cap><b>Figure 2.</b> Net margin (net income / revenue)</div>{f2}</div></div>
<p>Revenue grew by 32% in 2024 and by 60% in 2025, but net income grew by 25% and then by only 1%. As a result, the net margin, which had been above 40%, fell to 26% in 2025. The Marketplace segment changed most: its share of segment revenue rose from 23% in 2023 to 47% in 2025, making it Kaspi's largest business.</p>
<h2>3. What changed in 2025</h2>
<p>On 29 January 2025 Kaspi bought 65.4% of Hepsiburada for about $1.13 billion. It raised its stake to 76% in December 2025 and signed an agreement in January 2026 that took it to 85% [1]. The company itself calls this its first meaningful step toward international expansion.</p>
<p>The acquisition explains almost all of the change in the numbers. In 2025 the Turkish business added ₸1.03 trillion of segment revenue but made a net loss of ₸93 billion. Kazakhstan and Kaspi's other markets, by contrast, earned ₸1.16 trillion of net income on ₸3.07 trillion of segment revenue [1]. In other words, the core business remained very profitable, and the lower group margin reflects the new, loss-making Turkish business.</p>
<h2>4. Risks</h2>
<p>Three risks seem most important. First, Hepsiburada still loses money, and the key test for 2026 is whether these losses shrink. Second, Turkey has high inflation and a weak lira, and the deal was paid in U.S. dollars, which increases Kaspi's exposure to exchange-rate risk. Third, integration may be difficult: Kaspi warns that its international expansion may fail, and before the deal Hepsiburada had reported weaknesses in its internal financial controls [1].</p>
<h2>5. Author's view</h2>
<p>{view}</p>
<h2>References</h2>
<ol class=ref><li>Kaspi.kz JSC. Annual Report on Form 20-F for the fiscal year ended December 31, 2025. U.S. Securities and Exchange Commission filing; also available at https://ir.kaspi.kz</li></ol>
</body></html>"""
open(sys.argv[1],"w").write(html)
