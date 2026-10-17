"""İade takibi: durum makinesi + 14 günlük yasal süre sayacı."""

from __future__ import annotations

import sqlite3
from datetime import date, timedelta

# Tüketiciyi Koruma Kanunu: cayma hakkı 14 gün, satıcı ödeme/değişim 14 gün.
SURE_GUN = 14

DURUMLAR = ("talep", "onaylandi", "kargoya_verildi", "inceleme", "tamamlandi", "reddedildi")

GECISLER: dict[str, tuple[str, ...]] = {
    "talep": ("onaylandi", "reddedildi"),
    "onaylandi": ("kargoya_verildi", "reddedildi"),
    "kargoya_verildi": ("inceleme",),
    "inceleme": ("tamamlandi", "reddedildi"),
    "tamamlandi": (),
    "reddedildi": (),
}

BITIS_DURUMLARI = ("tamamlandi", "reddedildi")

ETIKETLER = {
    "talep": "Talep alındı",
    "onaylandi": "Onaylandı",
    "kargoya_verildi": "Kargoya verildi",
    "inceleme": "İnceleniyor",
    "tamamlandi": "Tamamlandı",
    "reddedildi": "Reddedildi",
}

SEBEPLER = (
    "Yanlış / eksik ürün",
    "Ürün beklentiyi karşılamadı",
    "Hasarlı ürün",
    "Beden / model değişimi",
    "Vazgeçtim (cayma hakkı)",
    "Teslim edilmedi",
    "Diğer",
)


def _gun(metin: str) -> date:
    return date.fromisoformat(str(metin)[:10])


def bugun() -> date:
    return date.today()


def iade_ekle(
    conn: sqlite3.Connection,
    *,
    siparis_id: int | None = None,
    musteri: str = "",
    tutar: float = 0.0,
    sebep: str = "",
    talep_tarihi: str | None = None,
    notlar: str = "",
) -> int:
    talep = talep_tarihi or bugun().isoformat()
    son = (_gun(talep) + timedelta(days=SURE_GUN)).isoformat()
    cur = conn.execute(
        """INSERT INTO iadeler
           (siparis_id, musteri, tutar, sebep, talep_tarihi, son_tarih, notlar)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (siparis_id, musteri, tutar, sebep, talep, son, notlar),
    )
    if siparis_id:
        conn.execute(
            "UPDATE siparisler SET durum='iade' WHERE id=?", (siparis_id,)
        )
    conn.commit()
    return int(cur.lastrowid)


def gecerli_gecis(mevcut: str, yeni: str) -> bool:
    return yeni in GECISLER.get(mevcut, ())


def durum_degistir(conn: sqlite3.Connection, iade_id: int, yeni: str) -> dict:
    """Geçerliyse durumu günceller, aksi halde ValueError fırlatır."""
    if yeni not in DURUMLAR:
        raise ValueError(f"Bilinmeyen durum: {yeni}")
    satir = conn.execute("SELECT * FROM iadeler WHERE id=?", (iade_id,)).fetchone()
    if satir is None:
        raise ValueError(f"İade kaydı bulunamadı: {iade_id}")
    mevcut = satir["durum"]
    if yeni == mevcut:
        return satirye_don(satir)
    if not gecerli_gecis(mevcut, yeni):
        raise ValueError(
            f"'{ETIKETLER.get(mevcut, mevcut)}' durumundan "
            f"'{ETIKETLER.get(yeni, yeni)}' durumuna geçilemez."
        )
    cozum = bugun().isoformat() if yeni in BITIS_DURUMLARI else None
    conn.execute(
        "UPDATE iadeler SET durum=?, cozum_tarihi=? WHERE id=?",
        (yeni, cozum, iade_id),
    )
    if yeni == "tamamlandi" and satir["siparis_id"]:
        conn.execute(
            "UPDATE siparisler SET durum='iade_tamam' WHERE id=?",
            (satir["siparis_id"],),
        )
    conn.commit()
    yen = conn.execute("SELECT * FROM iadeler WHERE id=?", (iade_id,)).fetchone()
    return satirye_don(yen)


def satirye_don(satir: sqlite3.Row) -> dict:
    veri = dict(satir)
    talep = _gun(veri["talep_tarihi"])
    son = _gun(veri["son_tarih"])
    if veri["durum"] in BITIS_DURUMLARI and veri.get("cozum_tarihi"):
        kalan = 0
        gecikti = False
        sure = (_gun(veri["cozum_tarihi"]) - talep).days
    else:
        fark = (son - bugun()).days
        kalan = fark
        gecikti = fark < 0
        sure = None
    veri["kalan_gun"] = kalan
    veri["gecikti"] = gecikti
    veri["sure_gun"] = sure
    veri["durum_etiket"] = ETIKETLER.get(veri["durum"], veri["durum"])
    return veri


def iade_listesi(conn: sqlite3.Connection, sadece_geciken: bool = False) -> list[dict]:
    satirlar = conn.execute("SELECT * FROM iadeler ORDER BY talep_tarihi DESC, id DESC")
    liste = [satirye_don(s) for s in satirlar]
    if sadece_geciken:
        liste = [s for s in liste if s["gecikti"]]
    return liste


def iade_ozet(conn: sqlite3.Connection) -> dict:
    satirlar = [satirye_don(s) for s in conn.execute("SELECT * FROM iadeler")]
    dagilim = {d: 0 for d in DURUMLAR}
    for s in satirlar:
        dagilim[s["durum"]] = dagilim.get(s["durum"], 0) + 1
    acik = [s for s in satirlar if s["durum"] not in BITIS_DURUMLARI]
    geciken = [s for s in acik if s["gecikti"]]
    tamamlanan_sureler = [s["sure_gun"] for s in satirlar if s["sure_gun"] is not None]
    ort = (
        round(sum(tamamlanan_sureler) / len(tamamlanan_sureler), 1)
        if tamamlanan_sureler
        else None
    )
    toplam_tutar = round(sum(s["tutar"] for s in satirlar), 2)
    return {
        "toplam": len(satirlar),
        "acik": len(acik),
        "geciken": len(geciken),
        "dagilim": dagilim,
        "ortalama_cozum_gun": ort,
        "toplam_tutar": toplam_tutar,
        "sure_gun": SURE_GUN,
        "etiketler": ETIKETLER,
    }
