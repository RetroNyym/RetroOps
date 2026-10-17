"""Şikâyet takibi: Şikayetvar başlıklarıyla eşleşen kategoriler ve çözüm süresi."""

from __future__ import annotations

import sqlite3
from datetime import date

# Türkiye'de e-ticaret şikâyetlerinin dağılımı (Şikâhetvar 2025):
# %63 iptal-iade-değişim, %56 fiyat-fatura-ödeme, %34 teslim edilmedi.
KATEGORILER: dict[str, str] = {
    "iptal-iade-degisim": "İptal, iade ve değişim",
    "fiyat-fatura-odeme": "Fiyat, fatura ve ödeme",
    "teslim-edilmedi": "Teslim edilmeyen ürün",
    "urun-kalite": "Ürün kalitesi / eksik-yanlış ürün",
    "kargo": "Kargo ve nakliyat",
    "iletisim": "İletişim / çağrı merkezi",
    "web-site": "Web sitesi / uygulama",
}

KAYNAKLAR = {
    "sikayetvar": "Şikâyetvar",
    "musteri": "Müşteri iletişimi",
    "pazaryeri": "Pazaryeri mesaj",
    "sosyal": "Sosyal medya",
}

DURUMLAR = ("acik", "inceleniyor", "cozuldu")
DURUM_ETIKETLER = {
    "acik": "Açık",
    "inceleniyor": "İnceleniyor",
    "cozuldu": "Çözüldü",
}


def _gun(metin: str) -> date:
    return date.fromisoformat(str(metin)[:10])


def sikayet_ekle(
    conn: sqlite3.Connection,
    *,
    kategori: str,
    konu: str = "",
    tarih: str | None = None,
    kaynak: str = "musteri",
    siparis_id: int | None = None,
    notlar: str = "",
) -> int:
    if kategori not in KATEGORILER:
        raise ValueError(f"Bilinmeyen kategori: {kategori}")
    if kaynak not in KAYNAKLAR:
        raise ValueError(f"Bilinmeyen kaynak: {kaynak}")
    cur = conn.execute(
        """INSERT INTO sikayetler
           (kaynak, kategori, konu, tarih, siparis_id, notlar)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (kaynak, kategori, konu, tarih or date.today().isoformat(),
         siparis_id, notlar),
    )
    conn.commit()
    return int(cur.lastrowid)


def sikayet_coz(conn: sqlite3.Connection, sikayet_id: int) -> dict:
    satir = conn.execute("SELECT * FROM sikayetler WHERE id=?", (sikayet_id,)).fetchone()
    if satir is None:
        raise ValueError(f"Şikâyet bulunamadı: {sikayet_id}")
    if satir["durum"] != "cozuldu":
        conn.execute(
            "UPDATE sikayetler SET durum='cozuldu', cozum_tarihi=? WHERE id=?",
            (date.today().isoformat(), sikayet_id),
        )
        conn.commit()
        satir = conn.execute(
            "SELECT * FROM sikayetler WHERE id=?", (sikayet_id,)
        ).fetchone()
    return satirye_don(satir)


def durum_degistir(conn: sqlite3.Connection, sikayet_id: int, yeni: str) -> dict:
    if yeni not in DURUMLAR:
        raise ValueError(f"Bilinmeyen durum: {yeni}")
    satir = conn.execute("SELECT * FROM sikayetler WHERE id=?", (sikayet_id,)).fetchone()
    if satir is None:
        raise ValueError(f"Şikâyet bulunamadı: {sikayet_id}")
    cozum = date.today().isoformat() if yeni == "cozuldu" else None
    conn.execute(
        "UPDATE sikayetler SET durum=?, cozum_tarihi=? WHERE id=?",
        (yeni, cozum, sikayet_id),
    )
    conn.commit()
    yen = conn.execute("SELECT * FROM sikayetler WHERE id=?", (sikayet_id,)).fetchone()
    return satirye_don(yen)


def satirye_don(satir: sqlite3.Row) -> dict:
    veri = dict(satir)
    veri["kategori_etiket"] = KATEGORILER.get(veri["kategori"], veri["kategori"])
    veri["kaynak_etiket"] = KAYNAKLAR.get(veri["kaynak"], veri["kaynak"])
    veri["durum_etiket"] = DURUM_ETIKETLER.get(veri["durum"], veri["durum"])
    if veri.get("cozum_tarihi"):
        veri["cozum_gun"] = (_gun(veri["cozum_tarihi"]) - _gun(veri["tarih"])).days
    else:
        veri["cozum_gun"] = None
    return veri


def sikayet_listesi(conn: sqlite3.Connection) -> list[dict]:
    satirlar = conn.execute(
        "SELECT * FROM sikayetler ORDER BY tarih DESC, id DESC"
    )
    return [satirye_don(s) for s in satirlar]


def istatistik(conn: sqlite3.Connection) -> dict:
    """Kategori bazında şikâyet dağılımı + çözüm oranı + ort. çözüm süresi."""
    liste = sikayet_listesi(conn)
    toplam = len(liste)
    kategori_veri: dict[str, dict] = {
        k: {"ad": ad, "sayi": 0, "cozulen": 0, "sure_toplam": 0, "sure_sayi": 0}
        for k, ad in KATEGORILER.items()
    }
    acik = 0
    for s in liste:
        v = kategori_veri.setdefault(
            s["kategori"],
            {"ad": s["kategori"], "sayi": 0, "cozulen": 0,
             "sure_toplam": 0, "sure_sayi": 0},
        )
        v["sayi"] += 1
        if s["durum"] == "cozuldu":
            v["cozulen"] += 1
            if s["cozum_gun"] is not None:
                v["sure_toplam"] += s["cozum_gun"]
                v["sure_sayi"] += 1
        else:
            acik += 1

    satirlar = []
    for anahtar, v in kategori_veri.items():
        oran = round(v["sayi"] / toplam * 100, 1) if toplam else 0.0
        ort = (
            round(v["sure_toplam"] / v["sure_sayi"], 1) if v["sure_sayi"] else None
        )
        satirlar.append(
            {
                "kategori": anahtar,
                "ad": v["ad"],
                "sayi": v["sayi"],
                "yuzde": oran,
                "cozulen": v["cozulen"],
                "cozum_orani": (
                    round(v["cozulen"] / v["sayi"] * 100, 1) if v["sayi"] else 0.0
                ),
                "ortalama_cozum_gun": ort,
            }
        )
    satirlar.sort(key=lambda x: x["sayi"], reverse=True)

    cozulen = toplam - acik
    tum_sureler = [
        s["cozum_gun"] for s in liste if s["cozum_gun"] is not None
    ]
    return {
        "toplam": toplam,
        "acik": acik,
        "cozulen": cozulen,
        "cozum_orani": round(cozulen / toplam * 100, 1) if toplam else 0.0,
        "ortalama_cozum_gun": (
            round(sum(tum_sureler) / len(tum_sureler), 1) if tum_sureler else None
        ),
        "kategoriler": satirlar,
        "kaynaklar": KAYNAKLAR,
        "durum_etiketler": DURUM_ETIKETLER,
    }
