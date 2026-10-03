"""Arayüz bütünlük kontrolü: JS'te referans verilen her id HTML'de var mı?"""
import re
from pathlib import Path

kaynak = Path(__file__).with_name("ops") / "sayfa.py"
metin = kaynak.read_text(encoding="utf-8")
html = metin.split('PAGE = r"""', 1)[1].split('"""', 1)[0]
js = re.search(r"<script>(.*?)</script>", html, re.S).group(1)

html_ids = set(re.findall(r'id="([^"]+)"', html))
js_ids = set(re.findall(r"\$\('#([A-Za-z0-9_-]+)'\)", js))

eksik = sorted(js_ids - html_ids)
print("HTML id:", len(html_ids), "| JS referans:", len(js_ids))
print("JS'te var ama HTML'de YOK:", eksik or "YOK — hepsi eşleşiyor")

# menü sekmeleri <-> bölümler
menu = set(re.findall(r'data-sekme="([^"]+)"', html))
bolumler = {s.replace("sekme-", "") for s in html_ids if s.startswith("sekme-")}
print("Menü/Bölüm farkı:", sorted(menu ^ bolumler) or "YOK — birebir")

# sekmeAc'taki yükleyici çağrıları
yukleyiciler = set(re.findall(r"if\(ad==='([a-z]+)'\)", js))
print("Sekme yükleyicisi olmayan menü:", sorted(menu - yukleyiciler - {"trend"}) or "YOK")

if eksik or (menu ^ bolumler):
    raise SystemExit(1)
print("ARAYUZ BUTUNLUGU OK")
