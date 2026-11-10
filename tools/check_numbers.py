"""Recomputes the derived figures the site publishes and fails if any of them no longer adds up.

Usage: python3 tools/check_numbers.py            (run from anywhere; needs no extra packages)

It builds the site into a temporary folder, so nothing in the repo changes, then checks:
  - totals, balances, margins and shares against the numbers they are computed from;
  - every published CSV against the figures the pages are built from;
  - the valuation table (market value, P/E, P/B, dividend yield);
  - news briefs: related reports exist, every brief has a picture, a chart and a source.
Exit code 1 if any check fails. Runs on every pull request (.github/workflows/checks.yml).
"""
import csv, os, runpy, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
fails, n = [], 0


def check(ok, what):
    global n
    n += 1
    if not ok:
        fails.append(what)


def near(a, b, tol):
    return abs(a - b) <= tol + 1e-9


def rows(name):
    with open(os.path.join(ROOT, "data", name), newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def series(table, label):
    """Numbers of the first row whose first cell starts with label."""
    for r in table:
        if r and r[0].startswith(label):
            return [float(x) for x in r[1:] if x not in ("", "n/a")]
    raise KeyError(label)


tmp = tempfile.mkdtemp()
try:
    shutil.copytree(os.path.join(ROOT, "data"), os.path.join(tmp, "data"))   # the build rewrites the spreadsheets
    argv, sys.argv = sys.argv, [os.path.join(HERE, "build_site.py"), tmp]
    out, sys.stdout = sys.stdout, open(os.devnull, "w")
    try:
        g = runpy.run_path(os.path.join(HERE, "build_site.py"))
    finally:
        sys.stdout, sys.argv = out, argv

    # --- Kazakhstan-China trade, Kazakh data: one-decimal figures, so sums may differ by 0.1 ---
    for i, y in enumerate(g["YEARS"]):
        e, m, t, b = g["EXPORTS"][i], g["IMPORTS"][i], g["TURNOVER"][i], g["BALANCE"][i]
        check(near(e + m, t, 0.1), f"KZ-China {y}: exports {e} + imports {m} is not turnover {t}")
        check(near(e - m, b, 0.1), f"KZ-China {y}: exports {e} - imports {m} is not balance {b}")
    t = rows("kazakhstan-china-trade-2020-2025.csv")
    for label, key in (("Exports to China", "EXPORTS"), ("Imports from China", "IMPORTS"), ("Total trade", "TURNOVER"), ("Balance", "BALANCE")):
        check(series(t, label) == g[key], f"kazakhstan-china-trade CSV: row '{label}' differs from the page")

    # --- Chinese customs data (US$ thousand): total = exports + imports, to the last thousand ---
    for name, raw in (("China-Kazakhstan", g["CN_KZ_RAW"]), ("China-Russia", g["RU_RAW"])):
        for y, (a, b, c) in zip(g["YEARS"], raw):
            check(abs(a - b - c) <= 1, f"{name} {y} (GACC): {b} + {c} is not {a}")
    kz25 = g["CN_KZ_RAW"][-1][0] / 1e6
    ca = {r[0]: r for r in g["CA_ROWS"]}
    check(near(ca["Kazakhstan"][1], kz25, 0.05), "Central Asia brief: Kazakhstan total differs from the GACC figure in the trade brief")
    check(near(ca["Kazakhstan"][5], g["TURNOVER"][-1], 0.001), "Central Asia brief: Kazakhstan's own total differs from the trade brief")
    for j, key in ((1, "CA_TOTAL"), (3, "CA_EXP"), (4, "CA_IMP")):
        check(near(sum(r[j] for r in g["CA_ROWS"]), g[key], 0.15), f"Central Asia brief: {key} is not the sum of the five countries")
    for r in g["CA_ROWS"]:
        check(near(r[3] + r[4], r[1], 0.1), f"Central Asia brief: {r[0]} exports + imports is not the total")
    prev, last = g["CN_KZ_RAW"][-2][0], g["CN_KZ_RAW"][-1][0]
    check(near((last / prev - 1) * 100, ca["Kazakhstan"][2], 0.5), "Central Asia brief: Kazakhstan growth rate")

    # --- Kaspi ---
    k = rows("kaspi-financials-2023-2025.csv")
    for i, y in enumerate(g["K_YEARS"]):
        check(near(g["K_NI"][i] / g["K_REV"][i] * 100, g["K_MARGIN"][i], 0.05), f"Kaspi {y}: net margin")
        check(near(g["K_MKT"][i] / g["K_SEG"][i] * 100, g["K_MKT_SHARE"][i], 0.05), f"Kaspi {y}: Marketplace share")
        check(g["K_PAY"][i] + g["K_MKT"][i] + g["K_FIN"][i] >= g["K_SEG"][i] >= g["K_REV"][i], f"Kaspi {y}: segments, segment total and revenue out of order")
    for label, key in (("Payments revenue", "K_PAY"), ("Marketplace revenue", "K_MKT"), ("Fintech revenue", "K_FIN"), ("Total revenue", "K_REV"),
                       ("Net income", "K_NI"), ("Net margin", "K_MARGIN"), ("Marketplace share", "K_MKT_SHARE")):
        check(series(k, label) == [float(v) for v in g[key]], f"Kaspi CSV: row '{label}' differs from the page")

    # --- other company files: the first rows of each CSV are the series the charts use ---
    for fname, pairs in (
        ("halyk-bank-2023-2026.csv", (("Net income", "H_NI"), ("Return on average equity", "H_ROAE"), ("Net interest margin", "H_NIM"), ("Cost-to-income", "H_CI"))),
        ("kazmunaygas-2023-2026.csv", (("Revenue", "M_REV"), ("Net profit", "M_NP"), ("EBITDA", "M_EBITDA"), ("Free cash flow", "M_FCF"),
                                       ("Net debt", "M_NETDEBT"), ("Oil and condensate", "M_OIL"), ("Dated Brent", "M_BRENT"), ("Average exchange rate", "M_FX"))),
        ("air-astana-2023-2026.csv", (("Revenue and other income", "A_REV"), ("Profit for the year", "A_PAT"), ("Passengers", "A_PAX"))),
    ):
        tab = rows(fname)
        for label, key in pairs:
            check(series(tab, label)[:3] == [float(v) for v in g[key]], f"{fname}: row '{label}' differs from the page")

    # --- last-twelve-months profit = full year - first half of that year + first half of the next ---
    check(near(g["M_LTM"], g["M_NP"][2] - g["M_H1"]["np"][0] + g["M_H1"]["np"][1], 1e-6), "KazMunayGas: last-twelve-months profit")
    check(near(g["A_LTM"], g["A_PAT"][2] - g["A_H1"]["pat"][0] + g["A_H1"]["pat"][1], 1e-6), "Air Astana: last-twelve-months profit")

    # --- Geely: brands add up to the total ---
    g9 = {r[0]: r for r in g["G_9M"]}
    for j in (1, 2):
        check(g9["Geely brand"][j] + g9["Lynk & Co"][j] + g9["Zeekr"][j] == g9["**Total"][j], "Geely: nine-month brand volumes do not add up to the total")
        check(g9["of which Galaxy"][j] <= g9["Geely brand"][j] and g9["Exports (included above)"][j] <= g9["**Total"][j], "Geely: a part is larger than the whole")

    # --- Kazatomprom: regional shares of sales add up to 100% ---
    for j, y in zip((1, 2, 3), g["U_YEARS"]):
        check(sum(r[j] for r in g["U_ASIA"]) == 100, f"Kazatomprom {y}: regional shares do not add up to 100%")

    # --- valuation table ---
    usd, hkd, cny = g["USD_KZT"], g["HKD_KZT"], g["CNY_KZT"]
    val = {r[0]: r for r in rows([f for f in sorted(os.listdir(os.path.join(ROOT, "data"))) if f.startswith("valuation-") and f.endswith(".csv")][-1])[1:]}
    for v in g["VAL"].values():
        local = v["price"] * v["shares"] / 1000
        usd_bn = local * hkd / usd if v["cur"] == "HK$" else local / usd
        mv = local * hkd / cny if v["cur"] == "HK$" else (local / usd if v["unit"] == "$" else local)
        check(near(v["usd"], usd_bn, 1e-6) and near(v["mv"], mv, 1e-6), f'{v["name"]}: market value')
        check(near(v["pe"], mv / v["profit"], 1e-6), f'{v["name"]}: P/E')
        check(v["pb"] is None or near(v["pb"], mv / v["book"], 1e-6), f'{v["name"]}: P/B')
        check(v["dy"] is None or near(v["dy"], v["dps"] / v["price"] * 100, 1e-6), f'{v["name"]}: dividend yield')
        r = val.get(v["name"])
        check(r is not None, f'{v["name"]}: missing from the valuation CSV')
        if r:
            check(near(float(r[1]), v["price"], 0.005), f'{v["name"]}: price in the CSV')
            check(near(float(r[4]), v["mv"], 0.006) and near(float(r[6]), v["usd"], 0.006), f'{v["name"]}: market value in the CSV')
            check(near(float(r[7]), v["pe"], 0.06), f'{v["name"]}: P/E in the CSV')
            check((r[8] == "") == (v["pb"] is None) and (r[8] == "" or near(float(r[8]), v["pb"], 0.006)), f'{v["name"]}: P/B in the CSV')
            check((r[9] == "") == (v["dy"] is None) and (r[9] == "" or near(float(r[9]), v["dy"], 0.06)), f'{v["name"]}: dividend yield in the CSV')

    # --- news and reports hang together ---
    slugs = {r["slug"] for r in g["REPORTS"]}
    check(len(slugs) == len(g["REPORTS"]), "two reports share a slug")
    isos = [x["iso"] for x in g["NEWS"]]
    check(isos == sorted(isos, reverse=True), "news briefs are not in date order, newest first")
    for x in g["NEWS"]:
        check(x["id"] in g["NEWS_VISUALS"], f'news {x["id"]}: no picture and chart')
        check(bool(x["sources"]) and all(u.startswith("https://") for _, u in x["sources"]), f'news {x["id"]}: missing or non-https source')
        for s in x["related"] or []:
            check(s in slugs, f'news {x["id"]}: related report {s} does not exist')
        for key, _ in g["NEWS_VISUALS"].get(x["id"], {}).get("photos", []):
            f = key + (".jpg" if key.startswith("learn-") else "-800.jpg")
            check(os.path.exists(os.path.join(ROOT, "assets", "photos", f)), f'news {x["id"]}: photo {f} is missing')
            check(key in g["NEWS_CREDITS"], f'news {x["id"]}: photo {key} has no credit')
    for r in g["REPORTS"]:
        check(os.path.exists(os.path.join(tmp, r["url"])), f'report {r["slug"]}: page was not built')
        for ext in (".csv", ".xlsx"):
            check(os.path.exists(os.path.join(ROOT, r["data"] + ext)), f'report {r["slug"]}: {r["data"]}{ext} is missing')
finally:
    shutil.rmtree(tmp, ignore_errors=True)

if fails:
    print(f"{len(fails)} of {n} number checks FAILED:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print(f"All {n} number checks passed")
