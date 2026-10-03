"""Örnek veri: paneli ilk açılışta anlamlı göstermek için demo kayıtlar.

``python -m ops.ornek_veri`` — veritabanı boşsa doldurur, dolusa hiçbir şey yapmaz.
"""

from __future__ import annotations

from datetime import date, timedelta

from . import iade, kargo, sikayet
from .db import connect


def _gun(n: int) -> str:
    return (date.today() + timedelta(days=n)).isoformat()


SIPARISLER = [
    # pazaryeri, no, ürün, adet, alış, satış, komisyon, kargo, paket, müşteri
    ("Trendyol", "TY-1001", "Kablosuz kulaklık", 1, 120, 299, 20, 30, 10, "Ayşe Yılmaz"),
    ("Trendyol", "TY-1002", "Mouse RGB", 2, 85, 189, 20, 30, 10, "Mehmet Demir"),
    ("Hepsiburada", "HB-2210", "Mekanik klavye", 1, 410, 849, 15, 0, 15, "Zeynep Kaya"),
    ("Amazon TR", "AM-3301", "USB-C kablo 2m", 5, 38, 99, 12, 45, 20, "Ali Çelik"),
    ("N11", "NN-4401", "Telefon kılıfı", 3, 22, 79, 15, 25, 10, "Fatma Şahin"),
    ("Trendyol", "TY-1003", "Powerbank 20.000 mAh", 1, 260, 549, 20, 30, 10, "Can Aydın"),
    ("Hepsiburada", "HB-2211", "Web kamera", 1, 220, 469, 15, 0, 15, "Ece Öztürk"),
    ("Amazon TR", "AM-3302", "Laptop standı", 2, 145, 329, 12, 35, 15, "Burak Arslan"),
]

# (sipariş index, müşteri, tutar, sebep, talep günü önce, durum)
IADELER = [
    (1, "Mehmet Demir", 189, "Beden / model değişimi", 3, "talep"),
    (0, "Ayşe Yılmaz", 299, "Hasarlı ürün", 6, "onaylandi"),
    (4, "Fatma Şahin", 79, "Yanlış / eksik ürün", 20, "inceleme"),   # süresi aştı
    (3, "Ali Çelik", 99, "Vazgeçtim (cayma hakkı)", 25, "talep"),    # süresi aştı
    (6, "Ece Öztürk", 469, "Ürün beklentiyi karşılamadı", 2, "kargoya_verildi"),
]

# (sipariş index, firma, takip, gönderim, tahmini, durum, sorun)
GONDERILER = [
    (0, "Yurtiçi Kargo", "YTR778899", -6, -3, "subede", ""),
    (1, "Trendyol Express", "TXP112233", -9, -6, "yolda", "gecikme"),
    (2, "MNG Kargo", "MNG445566", -2, 1, "yolda", ""),
    (3, "Aras Kargo", "ARS990011", -12, -9, "sorunlu", "kayip"),
    (4, "Sendeo", "SND556677", -1, 2, "yolda", ""),
    (5, "Hepsijet", "HPJ334455", -8, -5, "sorunlu", "yanlis_teslim"),
]

# (kategori, konu, kaynak, tarih günü önce, durum)
SIKAYETLER = [
    ("iptal-iade-degisim", "İade tutarı 14 gündür hesaba geçmedi", "sikayetvar", 12, "inceleniyor"),
    ("iptal-iade-degisim", "Değişim talebine yanıt yok", "musteri", 5, "acik"),
    ("kargo", "Kargo 6 gündür şubede bekliyor", "sikayetvar", 7, "acik"),
    ("fiyat-fatura-odeme", "Faturada ürün bedeli eksik görünüyor", "pazaryeri", 4, "inceleniyor"),
    ("teslim-edilmedi", "Sipariş kargodan geri döndü", "sosyal", 9, "acik"),
    ("urun-kalite", "Gelen ürün kutusu ezilmiş", "musteri", 3, "acik"),
    ("iletisim", "Çağrı merkezine ulaşılamıyor", "sikayetvar", 15, "cozuldu"),
]


def doldur(db_yol=None) -> dict:
    conn = connect(db_yol)
    try:
        mevcut = conn.execute("SELECT COUNT(*) c FROM siparisler").fetchone()["c"]
        if mevcut:
            return {"eklendi": 0, "not": f"Veritabanı dolu ({mevcut} sipariş), "
                                         "örnek veri yüklenmedi."}

        siparis_id: list[int] = []
        for p, no, urun, adet, alis, satis, kom, krg, pkt, musteri in SIPARISLER:
            cur = conn.execute(
                """INSERT INTO siparisler
                   (pazaryeri, siparis_no, urun, adet, alis_fiyati, satis_fiyati,
                    komisyon_yuzde, kargo_ucreti, paket_maliyeti, kdv_orani,
                    musteri, siparis_tarihi, durum)
                   VALUES (?,?,?,?,?,?,?,?,?,20,?,?,?)""",
                (p, no, urun, adet, alis, satis, kom, krg, pkt, musteri,
                 _gun(-10), "teslim"),
            )
            siparis_id.append(int(cur.lastrowid))

        for idx, musteri, tutar, sebep, gun_once, durum in IADELER:
            yeni = iade.iade_ekle(
                conn, siparis_id=siparis_id[idx], musteri=musteri,
                tutar=tutar, sebep=sebep, talep_tarihi=_gun(-gun_once),
            )
            # durumu izinli geçişlerle sırayla taşı
            hedef = durum
            while True:
                simdi = conn.execute(
                    "SELECT durum FROM iadeler WHERE id=?", (yeni,)
                ).fetchone()["durum"]
                if simdi == hedef:
                    break
                adaylar = iade.GECISLER[simdi]
                if not adaylar:
                    break
                iade.durum_degistir(conn, yeni, adaylar[0])

        for idx, firma, takip, bas, bit, durum, sorun in GONDERILER:
            yeni = kargo.gonderi_ekle(
                conn, kargo_firmasi=firma, takip_no=takip,
                gonderim_tarihi=_gun(bas), tahmini_teslim=_gun(bit),
                siparis_id=siparis_id[idx], son_durum="yolda",
            )
            kargo.durum_degistir(conn, yeni, durum, sorun_tipi=sorun)

        for kategori, konu, kaynak, gun_once, durum in SIKAYETLER:
            yeni = sikayet.sikayet_ekle(
                conn, kategori=kategori, konu=konu, kaynak=kaynak,
                tarih=_gun(-gun_once),
            )
            if durum != "acik":
                sikayet.durum_degistir(conn, yeni, durum)

        conn.commit()
        return {
            "eklendi": len(SIPARISLER),
            "iadeler": len(IADELER),
            "gonderiler": len(GONDERILER),
            "sikayetler": len(SIKAYETLER),
            "not": "Örnek veri yüklendi.",
        }
    finally:
        conn.close()


if __name__ == "__main__":
    print(doldur())
