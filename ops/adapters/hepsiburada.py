"""Hepsiburada sipariş entegrasyonu (OMS, Basic kimlik).

Uç: ``GET /orders/merchantid/{merchantId}`` — kimlik ``merchantId:apiKey``
Basic; ``User-Agent`` başlığı zorunlu. Yanıt gövdesi belgelerde örneklenmediği
için liste anahtarları ve alan adları savunmacı biçimde aranır.
"""

from __future__ import annotations

import base64
import urllib.parse

from .temel import (
    MAK_SINIR,
    TemelAdapter,
    durum_eslestir,
    istek,
    kargo_firmasi,
    liste_bul,
    metin,
    sayi,
    sonuc,
    tahmin_teslim,
    tarih_oku,
)

DURUM_HARITASI = {
    "new": "hazirlaniyor",
    "created": "hazirlaniyor",
    "preparing": "hazirlaniyor",
    "readytoship": "hazirlaniyor",
    "invoiced": "hazirlaniyor",
    "awaiting": "hazirlaniyor",
    "shipped": "kargoya_verildi",
    "intransit": "kargoya_verildi",
    "delivered": "teslim",
    "completed": "teslim",
    "cancelled": "iptal",
    "canceled": "iptal",
    "returned": "iade",
    "returning": "iade",
    "paymentpending": "hazirlaniyor",
    "paymentcompleted": "hazirlaniyor",
}

ANAHTARLAR = ("orders", "lineItems", "content", "data", "result", "orderList")


class Adapter(TemelAdapter):
    platform = "hepsiburada"
    taban_varsayilan = "https://oms-external.hepsiburada.com"

    def cek(self, ayarlar, kimlik, bas, bit, *, sinir=MAK_SINIR, http=None):
        http = http or istek
        magaza = metin(ayarlar.get("merchantId"))
        if not magaza:
            raise ValueError("Merchant ID girilmemiş.")
        sorgu = urllib.parse.urlencode({
            "begindate": bas.isoformat(),
            "enddate": bit.isoformat(),
            "offset": 0,
            "limit": min(200, sinir),
        })
        url = f"{self.taban(ayarlar)}/orders/merchantid/{magaza}?{sorgu}"
        kimlik_b64 = base64.b64encode(
            f"{magaza}:{metin(kimlik.get('apiKey'))}".encode("utf-8")
        ).decode("ascii")
        yanit = http(url, basliklar={
            "Authorization": f"Basic {kimlik_b64}",
            "User-Agent": "RetroOps/1.0",
        })
        if not 200 <= yanit.kod < 300:
            return sonuc(siparisler=[], atlandi=0, kod=yanit.kod,
                         notlar=[f"Hepsiburada isteği HTTP {yanit.kod} döndü."])

        liste = liste_bul(yanit.veri, ANAHTARLAR) or []
        kayitlar, atlandi = [], 0
        for ham in liste[:sinir]:
            satir = self._satir(ham)
            if satir:
                kayitlar.append(satir)
            else:
                atlandi += 1
        return sonuc(siparisler=kayitlar, atlandi=atlandi, kod=yanit.kod,
                     ham_toplam=len(liste))

    def _satir(self, ham) -> dict | None:
        if not isinstance(ham, dict):
            return None
        satirlar = ham.get("lineItems")
        satirlar = [s for s in satirlar if isinstance(s, dict)] \
            if isinstance(satirlar, list) else []

        adet = sum(int(sayi(s.get("quantity"), 1) or 1) for s in satirlar)
        urunler = [u for u in (
            metin(s.get("productName") or s.get("title") or s.get("name"))
            for s in satirlar
        ) if u]
        if not urunler:
            ad = metin(ham.get("productName") or ham.get("title")
                       or ham.get("name"))
            if ad:
                urunler.append(ad)
        if not adet:
            adet = int(sayi(ham.get("quantity"), 1) or 1)

        satis = (sayi(ham.get("totalPrice")) or sayi(ham.get("grossAmount"))
                 or sayi(ham.get("total")) or sayi(ham.get("price")))
        if satis <= 0 and satirlar:
            satis = sum(
                (sayi(s.get("total")) or sayi(s.get("price")))
                * (sayi(s.get("quantity"), 1) or 1)
                for s in satirlar
            )
        if satis <= 0:
            return None

        siparis_no = (metin(ham.get("orderNumber")) or metin(ham.get("orderNo"))
                      or metin(ham.get("packageNumber")))
        kimlik = ham.get("id") or ham.get("lineItemId") or siparis_no
        if not siparis_no and not kimlik:
            return None

        adres = ham.get("deliveryAddress") or ham.get("invoiceAddress") \
            or ham.get("customer") or {}
        if not isinstance(adres, dict):
            adres = {}
        musteri = (metin(ham.get("customerName")) or metin(ham.get("buyerName"))
                   or (metin(adres.get("firstName")) + " "
                       + metin(adres.get("lastName"))).strip())
        tarih = tarih_oku(ham.get("orderDate") or ham.get("createDate")
                          or ham.get("creationDate") or ham.get("date"))
        durum = durum_eslestir(DURUM_HARITASI,
                               ham.get("status") or ham.get("orderStatus")
                               or ham.get("state"))
        gonderi = None
        takip = (metin(ham.get("trackingNumber"))
                 or metin(ham.get("cargoTrackingNumber"))
                 or metin(ham.get("waybillNumber")))
        if takip:
            gonderi = {
                "takip_no": takip,
                "kargo_firmasi": kargo_firmasi(ham.get("cargoCompany")
                                               or ham.get("cargoFirm")),
                "gonderim_tarihi": tarih,
                "tahmini_teslim": tahmin_teslim(tarih),
                "son_durum": ("teslim" if durum == "teslim" else
                              "hazir" if durum in ("hazirlaniyor", "iptal")
                              else "yolda"),
                "notlar": "",
            }

        return {
            "dis_id": str(kimlik),
            "siparis_no": siparis_no or str(kimlik),
            "urun": urunler[0] if urunler else "Hepsiburada siparişi",
            "adet": max(1, adet),
            "satis_fiyati": round(satis, 2),
            "musteri": musteri,
            "siparis_tarihi": tarih,
            "durum": durum,
            "komisyon_yuzde": 0.0,
            "notlar": "",
            "gonderi": gonderi,
            "iade": None,
        }
