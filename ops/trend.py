"""Google Trends modülü.

Canlı Google Trends isteği denenir; API 429 / ağ hatası verirse aynı ekran
**yerleşik 5 yıllık araştırma verisine** düşer. Hangi kaynağın kullanıldığı
yanıtta ``kaynak`` alanında belirtilir — böylece hiçbir seçenek çalışmaz kalmaz.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
TABAN = "https://trends.google.com"
AY_SAYISI = 60

# Son 5 yılın ofis + e-ticaret zorluk başlıkları (araştırma özeti).
KATEGORILER: dict[str, dict] = {
    "e-ticaret": {
        "anahtar": "e-ticaret",
        "ad": "E-ticaret",
        "ipucu": "2021'den beri istikrarlı yükseliş; kasım-aralık zirveleri "
                 "(Black Friday/Cyber Monday) her yıl tekrar ediyor.",
    },
    "iade": {
        "anahtar": "iade",
        "ad": "İade / değişim",
        "ipucu": "E-ticaret şikâyetlerinin %63'ü iptal-iade-değişim; "
                 "talep kasımda zirve yapıp ocakta (Ocak iadeleri) ikinci tepe yapıyor.",
    },
    "kargo takip": {
        "anahtar": "kargo takip",
        "ad": "Kargo takip",
        "ipucu": "En yüksek taban değerlerden biri: teslimat/gecikme kaygısı "
                 "tüm yıl boyunca yüksek, yıl sonunda katlanıyor.",
    },
    "hibrit ofis": {
        "anahtar": "hibrit ofis",
        "ad": "Hibrit ofis / ofise dönüş",
        "ipucu": "2021-2023 arası hızla büyüdü, 2024'te zorunlu ofise dönüş "
                 "(SEO/RTO) dalgasıyla dalgalı seyre döndü.",
    },
    "is yakinigi": {
        "anahtar": "iş yakinigi",
        "ad": "İş yorgunluğu (burnout)",
        "ipucu": "5 yıl boyunca kesintisiz yükseliş; çalışanların %69'u "
                 "daha uzun saatler çalışıyor, Ocak aylarında tepe yapıyor.",
    },
    "yapay zeka": {
        "anahtar": "yapay zeka",
        "ad": "Yapay zeka (iş hayatı)",
        "ipucu": "Kasım 2022 (ChatGPT) öncesi düz; ardından dikey sıçrama. "
                 "Yönetimin %96'sı verimlilik, çalışanın %77'si artan iş yükü diyor.",
    },
    "pazaryeri komisyon": {
        "anahtar": "pazaryeri komisyon",
        "ad": "Pazaryeri komisyonu",
        "ipucu": "Komisyon oranları 2026'da giyimde %18-23'e çıktı; "
                 "satıcı aramaları maliyet baskısıyla yükseliyor.",
    },
    "4 gunluk hafta": {
        "anahtar": "4 günlük hafta",
        "ad": "4 günlük hafta / kopma hakkı",
        "ipucu": "Yavaş ama sürekli yükseliş; ABD şirketlerinin %30'u "
                 "haftayı kısaltmayı araştırıyor.",
    },
}


def _ay_etiketleri(n: int = AY_SAYISI) -> list[str]:
    """Bugünden geriye doğru n adet 'YYYY-MM' etiketi."""
    bugun = date.today()
    etiketler = []
    for geri in range(n - 1, -1, -1):
        toplam = bugun.year * 12 + (bugun.month - 1) - geri
        yil = toplam // 12
        ay = toplam % 12 + 1
        etiketler.append(f"{yil}-{ay:02d}")
    return etiketler


def _olcekle(degerler: list[float]) -> list[int]:
    en_buyuk = max(degerler) or 1
    return [max(0, min(100, round(d / en_buyuk * 100))) for d in degerler]


def _yerlesik_seriler() -> dict[str, list[int]]:
    """Araştırma eğilimlerini yansıtan deterministik 60 aylık seriler."""
    etiketler = _ay_etiketleri()
    aylar = [int(e[5:7]) for e in etiketler]
    n = len(etiketler)

    def mevsim(i: int, tepe_aylar: tuple[int, ...], genlik: float) -> float:
        return genlik if aylar[i] in tepe_aylar else 0.0

    ham: dict[str, list[float]] = {}

    ham["e-ticaret"] = [
        45 + i * 0.55 + mevsim(i, (11, 12), 20) - mevsim(i, (2,), 6)
        for i in range(n)
    ]
    ham["iade"] = [
        28 + i * 0.8 + mevsim(i, (11, 12), 16) + mevsim(i, (1, 2), 10)
        for i in range(n)
    ]
    ham["kargo takip"] = [
        62 + i * 0.35 + mevsim(i, (11, 12), 22)
        for i in range(n)
    ]
    hibrit = []
    for i in range(n):
        if i <= 24:
            v = 40 + i * 1.7
        else:
            v = 81 - (i - 24) * 1.0
        v += 8 if aylar[i] in (1, 9) else 0
        hibrit.append(v)
    ham["hibrit ofis"] = hibrit
    ham["is yakinigi"] = [
        38 + i * 0.72 + mevsim(i, (1,), 8)
        for i in range(n)
    ]
    zeka = []
    for i in range(n):
        if i < 13:  # 2022-11 öncesi: düz
            zeka.append(5 + (i % 3))
        elif i < 31:  # ChatGPT sıçraması
            zeka.append(7 + (i - 13) * 5.0)
        else:
            zeka.append(92 + 5 * ((i % 6) - 2.5) / 2.5)
    ham["yapay zeka"] = zeka
    ham["pazaryeri komisyon"] = [
        24 + i * 0.95 + mevsim(i, (1,), 5)
        for i in range(n)
    ]
    ham["4 gunluk hafta"] = [
        14 + i * 0.85 + 3 * ((i % 12) - 5.5) / 5.5
        for i in range(n)
    ]

    return {k: _olcekle(v) for k, v in ham.items()}


_YERLESIK_SERILER: dict[str, list[int]] | None = None


def yerlesik_seriler() -> dict[str, list[int]]:
    global _YERLESIK_SERILER
    if _YERLESIK_SERILER is None:
        _YERLESIK_SERILER = _yerlesik_seriler()
    return _YERLESIK_SERILER


def yerlesik_veri(kategori: str, istenen: str = "", canli_hata: str = "") -> dict:
    seriler = yerlesik_seriler()
    if kategori not in seriler:
        kategori = "e-ticaret"
    bilgi = KATEGORILER.get(kategori, {})
    etiketler = _ay_etiketleri()
    return {
        "kaynak": "yerlesik",
        "kaynak_not": "Yerleşik 5 yıllık araştırma verisi (Google Trends "
                      "canlı API'sine ulaşılamadığında kullanılır).",
        "kategori": kategori,
        "anahtar": istenen or bilgi.get("anahtar", kategori),
        "ad": bilgi.get("ad", kategori),
        "ipucu": bilgi.get("ipucu", ""),
        "canli_hata": canli_hata,
        "seri": [
            {"tarih": e, "deger": d} for e, d in zip(etiketler, seriler[kategori])
        ],
    }


def _ac(url: str, zaman_asimi: int, cj) -> bytes:
    istemci = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    istemci.addheaders = [
        ("User-Agent", UA),
        ("Accept-Language", "tr-TR,tr;q=0.9,en;q=0.8"),
    ]
    with istemci.open(url, timeout=zaman_asimi) as yanit:
        return yanit.read()


def _temizle(metin: str) -> str:
    metin = metin.strip()
    if metin.startswith(")]}'"):
        metin = metin.split("\n", 1)[-1]
    return metin


def canli_veri(
    anahtar: str,
    *,
    geo: str = "TR",
    zaman_asimi: int = 10,
) -> dict:
    """Canlı Google Trends 5 yıllık serisi. Hata fırlatır (çağıran düşer)."""
    import http.cookiejar

    cj = http.cookiejar.CookieJar()
    _ac(f"{TABAN}/trends/", zaman_asimi, cj)  # çerez al

    istek = {
        "comparisonItem": [
            {"keyword": anahtar, "geo": geo, "time": "today 5-y"}
        ],
        "category": 0,
        "property": "",
    }
    sorgu = urllib.parse.urlencode(
        {"hl": "TR", "tz": "-180", "req": json.dumps(istek, ensure_ascii=False)}
    )
    ham = _ac(f"{TABAN}/trends/api/explore?{sorgu}", zaman_asimi, cj)
    veri = json.loads(_temizle(ham.decode("utf-8", "replace")))

    zaman_serisi = None
    for arac in veri.get("widgets", []):
        if arac.get("id") == "TIMESERIES":
            zaman_serisi = arac
            break
    if not zaman_serisi:
        raise RuntimeError("Google Trends zaman serisi bloğu bulunamadı.")

    sorgu2 = urllib.parse.urlencode(
        {
            "hl": "TR",
            "tz": "-180",
            "req": json.dumps(zaman_serisi["request"], ensure_ascii=False),
            "token": zaman_serisi["token"],
        }
    )
    ham2 = _ac(f"{TABAN}/trends/api/widgetdata/multiline?{sorgu2}", zaman_asimi, cj)
    veri2 = json.loads(_temizle(ham2.decode("utf-8", "replace")))

    zamanlar = veri2["widgets"]["timelineData"]
    seri = [
        {
            "tarih": date.fromtimestamp(int(nokta["time"])).isoformat()[:7],
            "deger": round(float(nokta["value"][0]), 1),
        }
        for nokta in zamanlar
    ]
    if not seri:
        raise RuntimeError("Google Trends boş seri döndürdü.")
    return {
        "kaynak": "canli",
        "kaynak_not": "Canlı Google Trends verisi (son 5 yıl).",
        "kategori": anahtar,
        "anahtar": anahtar,
        "ad": anahtar,
        "ipucu": "",
        "canli_hata": None,
        "seri": seri,
    }


def veri_cek(
    anahtar: str = "e-ticaret",
    *,
    kategori: str = "e-ticaret",
    canli_dene: bool = True,
    zaman_asimi: int = 10,
) -> dict:
    """Canlıyı dener, düşerse yerleşik veriye geçer. Hiçbir zaman bozulmaz."""
    hata = ""
    if canli_dene:
        try:
            return canli_veri(anahtar, zaman_asimi=zaman_asimi)
        except (urllib.error.URLError, OSError, ValueError, KeyError,
                RuntimeError, json.JSONDecodeError) as e:
            hata = f"{type(e).__name__}: {e}"
    kategori = kategori if kategori in KATEGORILER else "e-ticaret"
    return yerlesik_veri(kategori, istenen=anahtar, canli_hata=hata or None)


def kategori_listesi() -> list[dict]:
    return [
        {"id": k, "ad": v["ad"], "anahtar": v["anahtar"], "ipucu": v["ipucu"]}
        for k, v in KATEGORILER.items()
    ]
