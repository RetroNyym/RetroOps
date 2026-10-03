"""Kargo/gönderi takibi: gecikme eşiği ve problem listesi."""

from __future__ import annotations

import sqlite3
from datetime import date

DURUMLAR = ("hazir", "yolda", "subede", "teslim", "sorunlu")
ETIKETLER = {
    "hazir": "Hazırlanıyor",
    "yolda": "Yolda",
    "subede": "Şubede",
    "teslim": "Teslim edildi",
    "sorunlu": "Sorunlu",
}

KARGO_FIRMALARI = (
    "Yurtiçi Kargo",
    "MNG Kargo",
    "Aras Kargo",
    "Surat Kargo",
    "PTT Kargo",
    "Sendeo",
    "Trendyol Express",
    "Hepsijet",
    "KargomKolay",
    "Diger",
)

SORUN_TIPLERI = (
    "",
    "gecikme",
    "kayip",
    "yanlis_teslim",
    "hasar",
    "iade_kargo",
)

SORUN_ETIKETLERI = {
    "": "Yok",
    "gecikme": "Gecikme",
    "kayip": "Kayıp gönderi",
    "yanlis_teslim": "Yanlış teslimat",
    "hasar": "Hasarlı ürün",
    "iade_kargo": "İade kargosu takıldı",
}

# Teslimat şikâyetlerinin çoğunu oluşturan gecikme eşiği (gün).
VARSAYILAN_ESIK = 3


def _gun(metin: str) -> date:
    return date.fromisoformat(str(metin)[:10])


def gonderi_ekle(
    conn: sqlite3.Connection,
    *,
    kargo_firmasi: str,
    gonderim_tarihi: str,
    tahmini_teslim: str,
    takip_no: str = "",
    siparis_id: int | None = None,
    son_durum: str = "yolda",
    notlar: str = "",
) -> int:
    if son_durum not in DURUMLAR:
        raise ValueError(f"Bilinmeyen gönderi durumu: {son_durum}")
    _gun(gonderim_tarihi)
    _gun(tahmini_teslim)
    cur = conn.execute(
        """INSERT INTO gonderiler
           (siparis_id, kargo_firmasi, takip_no, gonderim_tarihi,
            tahmini_teslim, son_durum, notlar)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (siparis_id, kargo_firmasi, takip_no, gonderim_tarihi,
         tahmini_teslim, son_durum, notlar),
    )
    conn.commit()
    return int(cur.lastrowid)


def satirye_don(satir: sqlite3.Row, esik: int = VARSAYILAN_ESIK,
                gunler: date | None = None) -> dict:
    veri = dict(satir)
    bugun = gunler or date.today()
    tahmini = _gun(veri["tahmini_teslim"])
    gecikme_gun = (bugun - tahmini).days
    gecikti = gecikme_gun > esik and veri["son_durum"] in ("hazir", "yolda", "subede")
    veri["gecikme_gun"] = max(0, gecikme_gun)
    veri["gecikti"] = gecikti
    veri["sorunlu"] = bool(veri["sorun_tipi"]) or gecikti or veri["son_durum"] == "sorunlu"
    veri["durum_etiket"] = ETIKETLER.get(veri["son_durum"], veri["son_durum"])
    veri["sorun_etiket"] = SORUN_ETIKETLERI.get(
        veri["sorun_tipi"], veri["sorun_tipi"]
    )
    return veri


def gonderi_listesi(
    conn: sqlite3.Connection,
    *,
    sadece_problem: bool = False,
    esik: int = VARSAYILAN_ESIK,
    gunler: date | None = None,
) -> list[dict]:
    satirlar = conn.execute(
        "SELECT * FROM gonderiler ORDER BY gonderim_tarihi DESC, id DESC"
    )
    liste = [satirye_don(s, esik, gunler) for s in satirlar]
    if sadece_problem:
        liste = [s for s in liste if s["sorunlu"]]
    return liste


def durum_degistir(
    conn: sqlite3.Connection,
    gonderi_id: int,
    yeni: str,
    sorun_tipi: str | None = None,
) -> dict:
    if yeni not in DURUMLAR:
        raise ValueError(f"Bilinmeyen gönderi durumu: {yeni}")
    satir = conn.execute("SELECT * FROM gonderiler WHERE id=?", (gonderi_id,)).fetchone()
    if satir is None:
        raise ValueError(f"Gönderi bulunamadı: {gonderi_id}")
    if sorun_tipi is not None and sorun_tipi not in SORUN_TIPLERI:
        raise ValueError(f"Bilinmeyen sorun tipi: {sorun_tipi}")
    alan = sorun_tipi if sorun_tipi is not None else satir["sorun_tipi"]
    conn.execute(
        "UPDATE gonderiler SET son_durum=?, sorun_tipi=? WHERE id=?",
        (yeni, alan, gonderi_id),
    )
    conn.commit()
    yen = conn.execute("SELECT * FROM gonderiler WHERE id=?", (gonderi_id,)).fetchone()
    return satirye_don(yen)


def gonderi_ozet(conn: sqlite3.Connection, esik: int = VARSAYILAN_ESIK) -> dict:
    hepsi = gonderi_listesi(conn, esik=esik)
    problem = [s for s in hepsi if s["sorunlu"]]
    dagilim = {d: 0 for d in DURUMLAR}
    for s in hepsi:
        dagilim[s["son_durum"]] = dagilim.get(s["son_durum"], 0) + 1
    sorun_dagilim: dict[str, int] = {}
    for s in problem:
        anahtar = "gecikme" if s["gecikti"] and not s["sorun_tipi"] else s["sorun_tipi"] or "diger"
        sorun_dagilim[anahtar] = sorun_dagilim.get(anahtar, 0) + 1
    teslim_edilen = dagilim.get("teslim", 0)
    return {
        "toplam": len(hepsi),
        "problem": len(problem),
        "dagilim": dagilim,
        "sorun_dagilim": sorun_dagilim,
        "esik_gun": esik,
        "teslim_orani": (
            round(teslim_edilen / len(hepsi) * 100, 1) if hepsi else 0.0
        ),
        "sorun_etiketler": SORUN_ETIKETLERI,
    }
