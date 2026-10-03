"""JS'te çağrılan API yolları sunucu rota tablosunda var mı?"""
import re
from pathlib import Path

kok = Path(__file__).resolve().parent
js = re.search(r"<script>(.*?)</script>",
               (kok / "ops" / "sayfa.py").read_text(encoding="utf-8"),
               re.S).group(1)
kaynak = (kok / "ops" / "web.py").read_text(encoding="utf-8")

# --- JS tarafı: sabit yollar, dinamik ('/api/iadeler/'+id+'/durum') yollar, href'ler
sabit = {y.split("?")[0]
         for _, y in re.findall(r"""(?:api|post)\((['"`])(/api/[^'"`]+)\1""", js)}
sabit = {y for y in sabit if not y.endswith("/")}  # dinamik önekleri ele
dinamik = {on + "ID" + son
           for _, on, _, son in
           re.findall(r"""(['"`])(/api/[a-z]+/)['"]\s*\+\s*\w+\s*\+\s*(['"`])(/[^'"`]+)['"]""", js)}
href = {y.split("?")[0] for y in re.findall(r"""href=['"](/api/[^'"]+)""", js)}
istem = sabit | dinamik | href

# --- sunucu tarafı: kaynak içindeki tüm /api/... dize literalleri
tum = set(re.findall(r"""["'](/api/[^"']+)["']""", kaynak))
regex = {t.replace(r"(\d+)", "ID") for t in tum if r"(\d+)" in t}
literal = {t for t in tum if r"(\d+)" not in t}
rotalar = literal | regex

eksik = sorted(y for y in istem if y not in rotalar)
kullanilmayan = sorted(r for r in rotalar
                       if not any(r == y or r.startswith(y) or y.startswith(r.split("/ID")[0])
                                  for y in istem))

print(f"JS istenen: {len(istem)} yol | sunucu tanımlı: {len(rotalar)} rota")
print("Eksik rota:", eksik or "YOK — hepsi sunucuda tanımlı")
print("Kullanılmayan (bilgi):", kullanilmayan or "YOK")
raise SystemExit(1 if eksik else 0)
