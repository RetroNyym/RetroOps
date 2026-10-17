"""Komisyon tabloları, net kâr ve kırılma noktası (minimum) fiyat hesabı.

Formül notu (Türkiye pazaryeri gerçeği):
- Komisyon ve diğer kesintiler (KVKS vb.) KDV **dahil** satış fiyatı üzerinden alınır.
- Kâr = KDV hariç satış - alış - komisyon - kargo - paket - diğer kesinti.
- Minimum fiyat: kâr=0 olacak şekilde satış fiyatının tersine çözülmesi.
"""

from __future__ import annotations

# 2026 güncel orta seviye komisyon aralıkları (kaynak: pazaryeri ücret listeleri).
# Değerler (alt, üst) yüzde aralığıdır.
KOMISYON_TABLOSU: dict[str, dict[str, tuple[float, float]]] = {
    "Trendyol": {
        "Giyim": (18, 23),
        "Elektronik": (7, 17),
        "Ev & Yasam": (15, 21),
        "Kozmetik": (16, 18),
        "Anne & Bebek": (12, 18),
        "Supermarket": (14, 17),
    },
    "Hepsiburada": {
        "Altin": (5, 5),
        "Giyim & Aksesuar": (18, 20),
        "Elektronik": (6, 16),
        "Ev & Yasam": (14, 19),
        "Kozmetik": (15, 17),
        "Yapi Market": (14, 17),
    },
    "Amazon TR": {
        "Elektronik": (6, 8),
        "Elektronik Aksesuar": (12, 12),
        "Giyim": (13, 15),
        "Kozmetik": (11, 14),
        "Yapi Market & Bahce": (12, 12),
    },
    "N11": {
        "Giyim": (19, 21),
        "Elektronik": (5, 22),
        "Kozmetik": (13, 16),
        "Yapi Market & Bahce": (14, 18),
    },
    "Diger (elle gir)": {
        "Genel": (0, 0),
    },
}


def komisyon_ortasi(pazaryeri: str, kategori: str) -> float:
    """Verilen pazaryeri/kategori için önerilen (orta) komisyon yüzdesi."""
    sat = KOMISYON_TABLOSU.get(pazaryeri)
    if not sat:
        return 0.0
    aralik = sat.get(kategori)
    if not aralik and sat:
        aralik = next(iter(sat.values()))
    if not aralik:
        return 0.0
    return round((aralik[0] + aralik[1]) / 2, 2)


def _sayi(deger, varsayilan: float = 0.0) -> float:
    try:
        if deger is None or deger == "":
            return varsayilan
        return float(str(deger).replace(",", "."))
    except (TypeError, ValueError):
        return varsayilan


def hesap(
    alis: float,
    satis: float,
    komisyon_yuzde: float,
    kargo: float = 0.0,
    paket: float = 0.0,
    kdv: float = 20.0,
    diger_yuzde: float = 0.0,
    hedef_kar: float = 0.0,
) -> dict:
    """Sipariş başına kâr dökümü döndürür.

    ``satis`` KDV dahil, ``alis`` KDV hariç kabul edilir (perakende gerçeği).
    """
    alis = _sayi(alis)
    satis = _sayi(satis)
    komisyon_yuzde = _sayi(komisyon_yuzde)
    kargo = _sayi(kargo)
    paket = _sayi(paket)
    kdv = _sayi(kdv, 20.0)
    diger_yuzde = _sayi(diger_yuzde)
    hedef_kar = _sayi(hedef_kar)

    if satis <= 0:
        raise ValueError("Satış fiyatı 0'dan büyük olmalı.")
    if komisyon_yuzde < 0 or kdv < 0:
        raise ValueError("Yüzde değerleri negatif olamaz.")

    komisyon_tutar = satis * komisyon_yuzde / 100
    diger_tutar = satis * diger_yuzde / 100
    satis_kdv_haric = satis / (1 + kdv / 100)
    satis_kdv = satis - satis_kdv_haric
    alis_kdv = alis * kdv / 100

    giderler = {
        "alis": alis,
        "komisyon": round(komisyon_tutar, 2),
        "kargo": round(kargo, 2),
        "paket": round(paket, 2),
        "diger": round(diger_tutar, 2),
    }
    toplam_gider = round(sum(giderler.values()), 2)
    kar = round(satis_kdv_haric - toplam_gider, 2)
    marj = round(kar / satis_kdv_haric * 100, 2) if satis_kdv_haric else 0.0

    return {
        "satis": round(satis, 2),
        "satis_kdv_haric": round(satis_kdv_haric, 2),
        "satis_kdv": round(satis_kdv, 2),
        "alis_kdv": round(alis_kdv, 2),
        "giderler": giderler,
        "toplam_gider": toplam_gider,
        "kar": kar,
        "marj_yuzde": marj,
        "hedef_kar": round(hedef_kar, 2),
        "kar_hedef_karsiz": kar,
    }


def _payda(komisyon_yuzde: float, kdv: float, diger_yuzde: float) -> float:
    return 1 / (1 + kdv / 100) - komisyon_yuzde / 100 - diger_yuzde / 100


def minimum_fiyat(
    alis: float,
    komisyon_yuzde: float,
    kargo: float = 0.0,
    paket: float = 0.0,
    kdv: float = 20.0,
    diger_yuzde: float = 0.0,
    hedef_kar: float = 0.0,
) -> float:
    """Kârın hedef_kar olacağı KDV dahil satış fiyatı (kırılma noktası).

    ``hedef_kar=0`` iken zarar etmeden satılabilecek en düşük fiyattır.
    """
    alis = _sayi(alis)
    komisyon_yuzde = _sayi(komisyon_yuzde)
    kargo = _sayi(kargo)
    paket = _sayi(paket)
    kdv = _sayi(kdv, 20.0)
    diger_yuzde = _sayi(diger_yuzde)
    hedef_kar = _sayi(hedef_kar)

    payda = _payda(komisyon_yuzde, kdv, diger_yuzde)
    if payda <= 0.0001:
        raise ValueError(
            "Bu kesinti oranlarıyla kârlı fiyat hesaplanamaz: "
            "komisyon + diğer kesintiler, KDV hariç satış payını siliyor."
        )
    pay = alis + kargo + paket + hedef_kar
    return round(pay / payda, 2)


def hesapla_ve_fiyat_ara(payload: dict) -> dict:
    """API için tek çağrı: kâr dökümü + minimum ve hedefli fiyat."""
    alanlar = {
        "alis": payload.get("alis", 0),
        "satis": payload.get("satis", 0),
        "komisyon_yuzde": payload.get("komisyon_yuzde", 0),
        "kargo": payload.get("kargo", 0),
        "paket": payload.get("paket", 0),
        "kdv": payload.get("kdv", 20),
        "diger_yuzde": payload.get("diger_yuzde", 0),
        "hedef_kar": payload.get("hedef_kar", 0),
    }
    sonuc = {"girdi": alanlar}
    satis = _sayi(alanlar["satis"])
    if satis > 0:
        sonuc["kar"] = hesap(
            alis=alanlar["alis"],
            satis=satis,
            komisyon_yuzde=alanlar["komisyon_yuzde"],
            kargo=alanlar["kargo"],
            paket=alanlar["paket"],
            kdv=alanlar["kdv"],
            diger_yuzde=alanlar["diger_yuzde"],
        )
    orta = komisyon_ortasi(
        str(payload.get("pazaryeri", "")), str(payload.get("kategori", ""))
    )
    sonuc["onerilen_komisyon"] = orta
    try:
        sonuc["minimum_fiyat"] = minimum_fiyat(
            alis=alanlar["alis"],
            komisyon_yuzde=alanlar["komisyon_yuzde"],
            kargo=alanlar["kargo"],
            paket=alanlar["paket"],
            kdv=alanlar["kdv"],
            diger_yuzde=alanlar["diger_yuzde"],
        )
        sonuc["hedefli_fiyat"] = minimum_fiyat(
            alis=alanlar["alis"],
            komisyon_yuzde=alanlar["komisyon_yuzde"],
            kargo=alanlar["kargo"],
            paket=alanlar["paket"],
            kdv=alanlar["kdv"],
            diger_yuzde=alanlar["diger_yuzde"],
            hedef_kar=alanlar["hedef_kar"],
        )
        sonuc["hesap_hatasi"] = None
    except ValueError as hata:
        sonuc["minimum_fiyat"] = None
        sonuc["hedefli_fiyat"] = None
        sonuc["hesap_hatasi"] = str(hata)
    return sonuc
