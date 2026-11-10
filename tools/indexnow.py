#!/usr/bin/env python3
"""Tell IndexNow search engines (Bing, Yandex, Seznam, Naver) which pages exist.

Run from the repository root after a deploy:  python3 tools/indexnow.py
Reads sitemap.xml and the key from the <key>.txt file in the site root. No account is needed:
the search engines check that https://www.steppesilk.com/<key>.txt holds the same key.
"""
import glob, json, re, sys, urllib.request

HOST = "www.steppesilk.com"
keys = [f for f in glob.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}\.txt", f)]
if len(keys) != 1:
    sys.exit(f"expected one key file in the site root, found {keys}")
key = open(keys[0]).read().strip()
urls = re.findall(r"<loc>(.*?)</loc>", open("sitemap.xml").read())

live = urllib.request.urlopen(f"https://{HOST}/{key}.txt", timeout=30).read().decode().strip()
if live != key:
    sys.exit("the key file on the live site does not match: has the deploy finished?")

body = json.dumps({"host": HOST, "key": key, "keyLocation": f"https://{HOST}/{key}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"})
with urllib.request.urlopen(req, timeout=30) as r:
    print(f"IndexNow: HTTP {r.status} for {len(urls)} URLs")
