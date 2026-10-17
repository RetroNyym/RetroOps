"""ÇiçekSepeti sipariş entegrasyonu (SATICI API, ``x-api-key``).

Uç: ``POST /api/v1/Order/GetOrders`` — ``x-api-key`` başlığı ve ``user-agent``
(mağaza numarası) gönderilir; gövde ``startDate``/``endDate`` kabul eder ve
aralık 14 günden uzun olamaz.
"""

from __future__ import annotations

from datetime import datetime

from .temel import (
    MAK_SINIR,
    TemelAdapter,
    durum_eslestir,
    istek,
    kargo_firmasi,
    liste_bul,
    metin,
    pencere_dondur,
    sayi,
    sonuc,
    tahmin_teslim,
    tarih_oku,
)

DURUM_ID = {
    "1": "hazirlaniyor",
    "2": "hazirlaniyor",
    "3": "hazirlaniyor",
    "4": "hazirlaniyor",
    "11": "hazirlaniyor",
    "12": "hazirlaniyor",
    "5": "kargoya_verildi",
    "6": "kargoya_verildi",
    "7": "teslim",
    "8": "teslim",
    "17": "iptal",
    "18": "iptal",
    "10": "iade",
    "13": "iade",
}

DURUM_METIN = {
    "new": "hazirlaniyor",
    "preparing": "hazirlaniyor",
    "readytoship": "hazirlaniyor",
    "shipped": "kargoya_verildi",
    "delivered": "teslim",
    "cancelled": "iptal",
    "returned": "iade",
    "returning": "iade",
    "completed": "teslim",
}

ANAHTARLAR = ("supplierOrderListWithBranch", "orderList", "orders", "content",
              "data", "result")


class Adapter(TemelAdapter):
    platform = "ciceksepeti"
    taban_varsayilan = "https://apis.ciceksepeti.com"

    def cek(self, ayarlar, kimlik, bas, bit, *, sinir=MAK_SINIR, http=None):
        http = http or istek
        magaza = metin(ayarlar.get("magazaId"))
        if not magaza:
            raise ValueError("Mağaza numarası girilmemiş.")
        basliklar = {
            "x-api-key": metin(kimlik.get("apiKey")),
            "user-agent": magaza,
        }
        kayitlar, atlandi, ham_toplam = [], 0, 0
        kod = None
        notlar = []

        for alt, ust in pencere_dondur(bas, bit, 14):
            if len(kayitlar) >= sinir:
                break
            govde = {
                "startDate": datetime.combine(alt, datetime.min.time())
                .strftime("%Y-%m-%dT%H:%M:%S"),
                "endDate": datetime.combine(ust, datetime.min.time())
                .strftime("%Y-%m-%dT23:59:59"),
                "pageSize": 100,
                "page": 0,
            }
            url = f"{self.taban(ayarlar)}/api/v1/Order/GetOrders"
            yanit = http(url, metot="POST", basliklar=basliklar,
                         govde=govde, bicim="json")
            kod = yanit.kod
            if not 200 <= kod < 300:
                notlar.append(f"ÇiçekSepeti isteği HTTP {kod} döndü.")
                return sonuc(siparisler=kayitlar, atlandi=atlandi, kod=kod,
                             notlar=notlar, ham_toplam=ham_toplam)
            liste = liste_bul(yanit.veri, ANAHTARLAR) or []
            ham_toplam += len(liste)
            for ham in liste:
                if len(kayitlar) >= sinir:
                    break
                satir = self._satir(ham)
                if satir:
                    kayitlar.append(satir)
                else:
                    atlandi += 1

        return sonuc(siparisler=kayitlar, atlandi=atlandi, kod=kod,
                     notlar=notlar, ham_toplam=ham_toplam)

    def _satir(self, ham) -> dict | None:
        if not isinstance(ham, dict):
            return None
        siparis_no = metin(ham.get("orderId"))
        satir_no = metin(ham.get("orderItemId"))
        if not siparis_no and not satir_no:
            return None
        satis = sayi(ham.get("totalPrice")) or sayi(ham.get("itemPrice")) \
            * (sayi(ham.get("quantity"), 1) or 1)
        if satis <= 0:
            return None

        tarih = tarih_oku(ham.get("orderCreateDate") or ham.get("orderDate")
                          or ham.get("orderModifyDate"))
        durum_durum_id = metin(ham.get("orderItemStatusId"))
        durum = DURUM_ID.get(durum_durum_id) or durum_eslestir(
            DURUM_METIN,
            ham.get("orderItemStatus") or ham.get("status") or durum_durum_id,
        )
        iade = None
        iptal = ham.get("cancellationResult")
        if iptal not in (None, "", 0, 0.0, False):
            iade = {
                "tutar": round(satis, 2),
                "sebep": "Diğer",
                "talep_tarihi": tarih_oku(ham.get("orderModifyDate"),
                                          varsayilan=tarih),
                "musteri": metin(ham.get("receiverName")),
                "notlar": "ÇiçekSepeti iade süreci (otomatik).",
            }
            durum = "iade"

        gonderi = None
        takip = metin(ham.get("cargoNumber"))
        if takip:
            gonderi = {
                "takip_no": takip,
                "kargo_firmasi": kargo_firmasi(ham.get("cargoCompany")),
                "gonderim_tarihi": tarih,
                "tahmini_teslim": tahmin_teslim(tarih),
                "son_durum": ("teslim" if durum == "teslim" else
                              "hazir" if durum in ("hazirlaniyor", "iptal")
                              else "yolda"),
                "notlar": "",
            }

        return {
            "dis_id": f"{siparis_no}/{satir_no}" if satir_no else siparis_no,
            "siparis_no": siparis_no,
            "urun": metin(ham.get("name")) or "ÇiçekSepeti siparişi",
            "adet": max(1, int(sayi(ham.get("quantity"), 1) or 1)),
            "satis_fiyati": round(satis, 2),
            "musteri": metin(ham.get("receiverName")),
            "siparis_tarihi": tarih,
            "durum": durum,
            "komisyon_yuzde": 0.0,
            "notlar": "",
            "gonderi": gonderi,
            "iade": iade,
        }
