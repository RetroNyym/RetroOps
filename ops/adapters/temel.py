"""Ortak HTTP istekleri ve normalize yardımcıları.

Tüm platform adaptörleri bu modüldeki ``istek`` fonksiyonunu çağırır;
testler aynı arayüzü sahte bir fonksiyonla değiştirip gerçek ağa
çıkmadan normalizasyonu doğrulayabilir.
"""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from collections import namedtuple
from datetime import date, datetime, time, timedelta

ZAMAN_ASIMI = 15
MAK_SINIR = 300

Yanit = namedtuple("Yanit", ["kod", "metin", "veri"])

LISTE_ANAHTARLARI = (
    "orders", "content", "data", "result", "items", "list", "orderList",
    "shipments", "packages", "Orders",
)

TARIH_BICIMLERI = (
    "%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y",
    "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%d-%m-%Y", "%Y%m%d",
)


class AgHatasi(Exception):
    """Sunucuya ulaşılamadı: ağ, SSL veya zaman aşımı hatası."""


def istek(
    url: str,
    *,
    metot: str = "GET",
    basliklar: dict | None = None,
    govde=None,
    bicim: str | None = None,
    zaman_asimi: int = ZAMAN_ASIMI,
) -> Yanit:
    """HTTP isteği atar; ``(kod, ham_metin, çözülmüş JSON)`` döndürür."""
    bas = {"User-Agent": "RetroOps/1.0",
           "Accept": "application/json"}
    bas.update(basliklar or {})
    veri = None
    if govde is not None:
        if bicim == "form":
            veri = urllib.parse.urlencode(govde).encode("utf-8")
            bas.setdefault("Content-Type",
                           "application/x-www-form-urlencoded")
        elif bicim == "json":
            veri = json.dumps(govde, ensure_ascii=False).encode("utf-8")
            bas.setdefault("Content-Type", "application/json")
        else:
            veri = str(govde).encode("utf-8")
    istemci = urllib.request.Request(url, data=veri, headers=bas,
                                     method=metot)
    try:
        with urllib.request.urlopen(istemci, timeout=zaman_asimi) as yanit:
            ham = yanit.read().decode("utf-8", "replace")
            kod = yanit.status
    except urllib.error.HTTPError as hata:
        ham = hata.read().decode("utf-8", "replace")
        kod = hata.code
    except (urllib.error.URLError, ssl.SSLError, OSError, TimeoutError) as e:
        raise AgHatasi(f"{type(e).__name__}: {e}") from e
    return Yanit(kod, ham, _coz(ham))


def _coz(ham: str):
    ham = ham.strip()
    if not ham:
        return None
    try:
        return json.loads(ham)
    except json.JSONDecodeError:
        return None


def test_sonucu(kod: int | None, ek: str = "") -> dict:
    """HTTP kodunu kullanıcıya dönmesi gereken test sonucuna çevirir."""
    if kod is None:
        return {"durum": "ag", "kod": None,
                "mesaj": "Sunucuya ulaşılamadı." + (" " + ek if ek else "")}
    if 200 <= kod < 300:
        return {"durum": "ok", "kod": kod,
                "mesaj": f"Bağlantı doğrulandı (HTTP {kod})."
                         + (" " + ek if ek else "")}
    if kod in (401, 403):
        mesaj = (f"Kimlik reddedildi (HTTP {kod}) — API anahtarı, appkey/"
                 "token veya mağaza bilgilerinizi kontrol edin.")
    elif kod == 404:
        mesaj = "Uç nokta bulunamadı (404) — adres veya mağaza ID'si yanlış olabilir."
    elif kod == 429:
        mesaj = "İstek limiti aşıldı (429) — bir süre bekleyip tekrar deneyin."
    elif kod >= 500:
        mesaj = f"Platform sunucusu hata döndü (HTTP {kod})."
    else:
        mesaj = f"Beklenmeyen yanıt (HTTP {kod})."
    if ek:
        mesaj += " " + ek
    return {"durum": "hata", "kod": kod, "mesaj": mesaj}


def ag_sonucu(hata: Exception) -> dict:
    return {
        "durum": "ag",
        "kod": None,
        "mesaj": "Ağ/SSL hatası — platforma ulaşılamadı (erişim engellenmiş "
                 f"olabilir): {type(hata).__name__}: {hata}",
    }


def sonuc(*, siparisler: list, atlandi: int = 0, kod: int | None = None,
          notlar: list | None = None, ham_toplam: int = 0) -> dict:
    return {
        "siparisler": siparisler,
        "atlandi": atlandi,
        "ham_toplam": ham_toplam or (len(siparisler) + atlandi),
        "kod": kod,
        "notlar": notlar or [],
    }


def metin(deger) -> str:
    if deger is None:
        return ""
    if isinstance(deger, float) and deger.is_integer():
        return str(int(deger))
    return str(deger).strip()


def sayi(deger, varsayilan: float = 0.0) -> float:
    """Tutar/alan sayısını güvenli biçimde float'a çevirir."""
    if isinstance(deger, bool):
        return float(deger)
    if isinstance(deger, (int, float)):
        return float(deger)
    if isinstance(deger, dict):
        for anahtar in ("amount", "value", "total", "valueGross", "price"):
            if anahtar in deger:
                return sayi(deger[anahtar], varsayilan)
        return varsayilan
    s = str(deger or "").strip()
    if not s:
        return varsayilan
    for karakter in ("₺", "TL", "%", " "):
        s = s.replace(karakter, "")
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return varsayilan


def tarih_oku(deger, varsayilan: str = "") -> str:
    """Yaygın tarih biçimlerini ``YYYY-MM-DD``ye çevirir."""
    bugun = varsayilan or date.today().isoformat()
    if deger in (None, ""):
        return bugun
    if isinstance(deger, bool):
        return bugun
    if isinstance(deger, (int, float)):
        deger = int(deger)
        birim = float(deger)
        if birim > 1e12:
            birim /= 1000
        if birim > 1e9:
            try:
                return datetime.fromtimestamp(birim).date().isoformat()
            except (OverflowError, OSError, ValueError):
                return bugun
        deger = str(deger)
    s = str(deger).strip()
    if not s:
        return bugun
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10]
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        pass
    for bicim in TARIH_BICIMLERI:
        try:
            return datetime.strptime(s, bicim).date().isoformat()
        except ValueError:
            continue
    if s.isdigit() and len(s) >= 10:
        return tarih_oku(int(s), bugun)
    return bugun


def tahmin_teslim(tarih_iso: str, gun: int = 3) -> str:
    temel = date.fromisoformat(tarih_iso[:10])
    return (temel + timedelta(days=gun)).isoformat()


def pencere_dondur(bas: date, bit: date, gun: int = 14) -> list[tuple[date, date]]:
    """Tarih aralığını ``gun`` günlük pencerelere böler (sondan geriye)."""
    pencereler = []
    ust = bit
    while ust >= bas:
        alt = max(bas, ust - timedelta(days=gun - 1))
        pencereler.append((alt, ust))
        ust = alt - timedelta(days=1)
    return pencereler


def pencere_zamani(bas: date, bit: date) -> tuple[int, int]:
    """Pencereyi milisaniye zaman damgasına çevirir."""
    bas_damga = datetime.combine(bas, time(0, 0)).timestamp() * 1000
    bit_damga = datetime.combine(bit, time(23, 59, 59)).timestamp() * 1000
    return int(bas_damga), int(bit_damga)


def liste_bul(veri, anahtarlar=LISTE_ANAHTARLARI) -> list | None:
    """Yanıt gövdesindeki kayıt listesini olası anahtarlarda arar."""
    if isinstance(veri, list):
        return veri
    if not isinstance(veri, dict):
        return None
    for anahtar in anahtarlar:
        deger = veri.get(anahtar)
        if isinstance(deger, list):
            return deger
        if isinstance(deger, dict):
            for alt in anahtarlar:
                if isinstance(deger.get(alt), list):
                    return deger[alt]
    return None


def durum_eslestir(harita: dict, ham, varsayilan: str = "hazirlaniyor") -> str:
    """Platform durum metnini panel durumuna çevirir."""
    s = metin(ham).lower()
    if not s:
        return varsayilan
    if s in harita:
        return harita[s]
    for anahtar, deger in harita.items():
        if len(anahtar) > 3 and (anahtar in s or s in anahtar):
            return deger
    return varsayilan


KARGO_ESLESME = {
    "yurtici": "Yurtiçi Kargo", "yurtici kargo": "Yurtiçi Kargo",
    "mng": "MNG Kargo", "mng kargo": "MNG Kargo",
    "aras": "Aras Kargo", "aras kargo": "Aras Kargo",
    "surat": "Surat Kargo", "suratkargo": "Surat Kargo",
    "surat kargo": "Surat Kargo", "ptt": "PTT Kargo",
    "ptt kargo": "PTT Kargo", "sendeo": "Sendeo",
    "trendyol": "Trendyol Express", "trendyol express": "Trendyol Express",
    "ty express": "Trendyol Express", "hepsijet": "Hepsijet",
    "hepsi jet": "Hepsijet", "kargomkolay": "KargomKolay",
    "kargom kolay": "KargomKolay",
}


def kargo_firmasi(ad) -> str:
    s = metin(ad)
    if not s:
        return "Diger"
    bulunan = KARGO_ESLESME.get(s.lower())
    if bulunan:
        return bulunan
    for anahtar, deger in KARGO_ESLESME.items():
        if anahtar in s.lower():
            return deger
    return s


class TemelAdapter:
    """Her adaptörün miras aldığı ortak test akışı ve adres yardımcıları."""

    platform = ""
    taban_varsayilan = ""

    def taban(self, ayarlar: dict) -> str:
        deger = metin((ayarlar or {}).get("tabanAdres")) or self.taban_varsayilan
        return deger.rstrip("/")

    def eksikler(self, alanlar: list[dict], girdi: dict) -> list[str]:
        """Zorunlu alanlardan boş kalanların ``id`` listesini döndürür."""
        return [a["id"] for a in alanlar
                if a.get("zorunlu") and not metin(girdi.get(a["id"]))]

    def cek(self, ayarlar, kimlik, bas, bit, *, sinir=MAK_SINIR, http=None):
        raise NotImplementedError

    def test(self, ayarlar, kimlik, *, http=None, sinir=3) -> dict:
        """Küçük bir tarih aralığında gerçek istek atıp sonucu yorumlar."""
        bit = date.today()
        bas = bit - timedelta(days=13)
        try:
            c = self.cek(ayarlar, kimlik, bas, bit, sinir=sinir, http=http)
        except AgHatasi as e:
            return ag_sonucu(e)
        except ValueError as e:
            return {"durum": "hata", "kod": None, "mesaj": str(e)}
        except Exception as e:
            return {"durum": "hata", "kod": None,
                    "mesaj": f"{type(e).__name__}: {e}"}
        return self.test_yorumla(c)

    def test_yorumla(self, c: dict) -> dict:
        temel = test_sonucu(c.get("kod"))
        ek = " ".join(c.get("notlar") or [])
        if temel["durum"] == "ok":
            if c.get("siparisler"):
                temel["mesaj"] += f" {len(c['siparisler'])} kayıt okundu."
            elif c.get("ham_toplam"):
                return {
                    "durum": "uyari",
                    "kod": c.get("kod"),
                    "mesaj": f"Bağlantı kuruldu (HTTP {c.get('kod')}) fakat yanıt "
                             f"şekli tanınamadı — {c['ham_toplam']} kayıt "
                             "okunamadı. " + ek,
                }
        if ek and temel["durum"] != "ok":
            temel["mesaj"] += " " + ek
        return temel
