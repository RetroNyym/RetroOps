"""CSV içe/dışa aktarma: toplu sipariş yükleme, rapor indirme, şablonlar."""

from __future__ import annotations

import csv
import io
import sqlite3
from datetime import date, datetime

TABLOLAR = ("siparisler", "iadeler", "gonderiler", "sikayetler")

SABLONLAR: dict[str, list[str]] = {
    "siparisler": [
        "pazaryeri", "siparis_no", "urun", "adet", "alis_fiyati",
        "satis_fiyati", "komisyon_yuzde", "kargo_ucreti", "paket_maliyeti",
        "kdv_orani", "diger_yuzde", "musteri", "siparis_tarihi", "durum",
        "notlar",
    ],
    "iadeler": [
        "musteri", "tutar", "sebep", "talep_tarihi", "durum", "notlar",
    ],
    "gonderiler": [
        "kargo_firmasi", "takip_no", "gonderim_tarihi", "tahmini_teslim",
        "son_durum", "sorun_tipi", "notlar",
    ],
    "sikayetler": [
        "kaynak", "kategori", "konu", "tarih", "durum", "notlar",
    ],
}

SIPARIS_DURUMLARI = (
    "hazirlaniyor", "kargoya_verildi", "teslim", "iade", "iade_tamam", "iptal",
)


def sablon_olustur(tablo: str) -> str:
    if tablo not in SABLONLAR:
        raise ValueError(f"Bilinmeyen tablo: {tablo}")
    tampon = io.StringIO()
    yaz = csv.writer(tampon)
    yaz.writerow(SABLONLAR[tablo])
    yaz.writerow(["ornek-veri"] + [""] * (len(SABLONLAR[tablo]) - 1))
    return "\ufeff" + tampon.getvalue()


def _satirlar(metin: str) -> list[dict]:
    metin = metin.lstrip("\ufeff")
    okuyucu = csv.DictReader(io.StringIO(metin))
    if not okuyucu.fieldnames:
        raise ValueError("CSV başlık satırı yok.")
    return [
        {(k or "").strip(): (v or "").strip() for k, v in satir.items()}
        for satir in okuyucu
    ]


def _sayi(metin: str, varsayilan: float = 0.0) -> float:
    try:
        return float(str(metin).replace(".", "").replace(",", ".")) \
            if "," in str(metin) else float(str(metin))
    except (TypeError, ValueError):
        return varsayilan


def _tarih(metin: str) -> str:
    metin = str(metin).strip()
    if not metin:
        return date.today().isoformat()
    for bicim in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(metin, bicim).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"Tarih anlaşılamadı: {metin} (YYYY-MM-DD kullanın)")


def siparisleri_aktar(conn: sqlite3.Connection, metin: str) -> dict:
    """Sipariş CSV'sini yükler; satır satır hata raporu döndürür."""
    satirlar = _satirlar(metin)
    eklenen, hatalar = 0, []
    for no, satir in enumerate(satirlar, start=2):
        if not any(satir.values()):
            continue
        try:
            urun = satir.get("urun", "")
            if not urun:
                raise ValueError("urun boş")
            satis = _sayi(satir.get("satis_fiyati", ""))
            if satis <= 0:
                raise ValueError("satis_fiyati 0'dan büyük olmalı")
            durum = satir.get("durum") or "hazirlaniyor"
            if durum not in SIPARIS_DURUMLARI:
                raise ValueError(f"geçersiz durum: {durum}")
            conn.execute(
                """INSERT INTO siparisler
                   (pazaryeri, siparis_no, urun, adet, alis_fiyati,
                    satis_fiyati, komisyon_yuzde, kargo_ucreti,
                    paket_maliyeti, kdv_orani,
                    diger_yuzde, musteri, siparis_tarihi, durum, notlar)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    satir.get("pazaryeri") or "Diger",
                    satir.get("siparis_no", ""),
                    urun,
                    int(_sayi(satir.get("adet", "1"), 1) or 1),
                    _sayi(satir.get("alis_fiyati", "")),
                    satis,
                    _sayi(satir.get("komisyon_yuzde", "")),
                    _sayi(satir.get("kargo_ucreti", "")),
                    _sayi(satir.get("paket_maliyeti", "")),
                    _sayi(satir.get("kdv_orani", "20"), 20),
                    _sayi(satir.get("diger_yuzde", "")),
                    satir.get("musteri", ""),
                    _tarih(satir.get("siparis_tarihi", "")),
                    durum,
                    satir.get("notlar", ""),
                ),
            )
            eklenen += 1
        except (ValueError, TypeError, sqlite3.Error) as e:
            hatalar.append(f"{no}. satır: {e}")
    conn.commit()
    return {"eklenen": eklenen, "hatalar": hatalar, "toplam": len(satirlar)}


def disa_aktar(conn: sqlite3.Connection, tablo: str) -> str:
    """Tabloyu UTF-8 (Excel uyumlu) CSV metnine çevirir."""
    if tablo not in TABLOLAR:
        raise ValueError(f"Bilinmeyen tablo: {tablo}")
    satirlar = conn.execute(f"SELECT * FROM {tablo}").fetchall()
    tampon = io.StringIO()
    if satirlar:
        alanlar = list(satirlar[0].keys())
        yaz = csv.DictWriter(tampon, fieldnames=alanlar)
        yaz.writeheader()
        for s in satirlar:
            yaz.writerow(dict(s))
    else:
        yaz = csv.writer(tampon)
        yaz.writerow(SABLONLAR[tablo])
    return "\ufeff" + tampon.getvalue()
