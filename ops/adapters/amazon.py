"""Amazon SP-API sipariş entegrasyonu (LWA + Selling Partner API, TR).

Kimlik: ``POST https://api.amazon.com/auth/o2/token`` (form
``grant_type=refresh_token``) ile alınan erişim jetonu, sipariş isteklerinde
``x-amz-access-token`` başlığında kullanılır. Sipariş kalemleri ayrı uçtan
okunur; erişim limitine takılırsa sipariş toplam tutarıyla devam edilir.
"""

from __future__ import annotations

import urllib.parse
from datetime import datetime, timezone

from .temel import (
    MAK_SINIR,
    TemelAdapter,
    durum_eslestir,
    istek,
    metin,
    sayi,
    sonuc,
    tarih_oku,
)

DURUM_HARITASI = {
    "pendingacceptance": "hazirlaniyor",
    "pending": "hazirlaniyor",
    "unshipped": "hazirlaniyor",
    "invoiceunconfirmed": "hazirlaniyor",
    "shipmentqueued": "hazirlaniyor",
    "shipped": "kargoya_verildi",
    "partiallyshipped": "kargoya_verildi",
    "delivered": "teslim",
    "canceled": "iptal",
    "cancelled": "iptal",
    "returned": "iade",
    "unfulfillable": "hazirlaniyor",
}

MAK_KALEM = 10


class Adapter(TemelAdapter):
    platform = "amazon"
    taban_varsayilan = "https://sellingpartnerapi-eu.amazon.com"

    def jeton(self, kimlik, http) -> str:
        refresh = metin(kimlik.get("refreshToken"))
        client_id = metin(kimlik.get("clientId"))
        client_secret = metin(kimlik.get("clientSecret"))
        if not (refresh and client_id and client_secret):
            raise ValueError("refreshToken/clientId/clientSecret girilmemiş.")
        yanit = http(
            "https://api.amazon.com/auth/o2/token",
            metot="POST",
            govde={
                "grant_type": "refresh_token",
                "refresh_token": refresh,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            bicim="form",
        )
        if not 200 <= yanit.kod < 300:
            return ""
        veri = yanit.veri if isinstance(yanit.veri, dict) else {}
        return metin(veri.get("access_token"))

    def cek(self, ayarlar, kimlik, bas, bit, *, sinir=MAK_SINIR, http=None):
        http = http or istek
        jeton = self.jeton(kimlik, http)
        if not jeton:
            return sonuc(siparisler=[], atlandi=0, kod=401,
                         notlar=["Amazon erişim jetonu alınamadı "
                                 "(LWA refresh token geçersiz olabilir)."])

        bolge = metin(ayarlar.get("bolge")) or "eu"
        pazar = metin(ayarlar.get("marketplaceId")) or "A33AVAJ2PDY3EV"
        taban = metin(ayarlar.get("tabanAdres")) or \
            f"https://sellingpartnerapi-{bolge}.amazon.com"
        sorgu = urllib.parse.urlencode({
            "CreatedAfter": _zaman(bas),
            "CreatedBefore": _zaman(bit),
            "MarketplaceIds": pazar,
            "MaxResultsPerPage": min(50, sinir),
        })
        url = f"{taban}/orders/v0/orders?{sorgu}"
        yanit = http(url, basliklar={"x-amz-access-token": jeton})
        if not 200 <= yanit.kod < 300:
            return sonuc(siparisler=[], atlandi=0, kod=yanit.kod,
                         notlar=[f"Amazon isteği HTTP {yanit.kod} döndü."])

        veri = yanit.veri if isinstance(yanit.veri, dict) else {}
        payload = veri.get("payload") if isinstance(veri.get("payload"), dict) \
            else veri
        liste = payload.get("Orders") or payload.get("orders") or []
        liste = liste if isinstance(liste, list) else []

        kayitlar, atlandi = [], 0
        for sira, ham in enumerate(liste):
            if len(kayitlar) >= sinir:
                break
            kalemler = []
            if sira < MAK_KALEM:
                kalemler = self._kalemler(
                    metin(ham.get("AmazonOrderId")), jeton, taban,
                    http,
                )
            satir = self._satir(ham, kalemler)
            if satir:
                kayitlar.append(satir)
            else:
                atlandi += 1
        return sonuc(siparisler=kayitlar, atlandi=atlandi, kod=yanit.kod,
                     ham_toplam=len(liste))

    def _kalemler(self, siparis_id: str, jeton: str, taban: str, http) -> list:
        if not siparis_id:
            return []
        try:
            yanit = http(f"{taban}/orders/v0/orders/{siparis_id}/orderItems",
                         basliklar={"x-amz-access-token": jeton})
        except Exception:
            return []
        if not 200 <= yanit.kod < 300:
            return []
        veri = yanit.veri if isinstance(yanit.veri, dict) else {}
        payload = veri.get("payload") if isinstance(veri.get("payload"), dict) \
            else veri
        kalemler = payload.get("OrderItems") or payload.get("orderItems") or []
        return [k for k in kalemler if isinstance(k, dict)] \
            if isinstance(kalemler, list) else []

    def _satir(self, ham, kalemler: list) -> dict | None:
        if not isinstance(ham, dict):
            return None
        siparis_no = metin(ham.get("AmazonOrderId"))
        if not siparis_no:
            return None

        satis = sayi((ham.get("OrderTotal") or {}).get("Amount")) \
            if isinstance(ham.get("OrderTotal"), dict) else 0.0
        adet = 0
        urunler = []
        for k in kalemler:
            adet += int(sayi(k.get("Quantity"), 1) or 1)
            ad = metin(k.get("Title"))
            if ad:
                urunler.append(ad)
            if satis <= 0:
                fiyat = k.get("ItemPrice")
                if isinstance(fiyat, dict):
                    satis += sayi(fiyat.get("Amount"))
        if satis <= 0:
            return None

        ad = ham.get("ShippingAddress") or {}
        musteri = (metin(ham.get("BuyerName"))
                   or (metin(ad.get("Name")) if isinstance(ad, dict) else "")
                   or metin((ham.get("BuyerInfo") or {}).get("BuyerName")
                            if isinstance(ham.get("BuyerInfo"), dict) else ""))
        tarih = tarih_oku(ham.get("PurchaseDate") or ham.get("purchaseDate"))
        durum = durum_eslestir(DURUM_HARITASI, ham.get("OrderStatus")
                               or ham.get("orderStatus"))

        return {
            "dis_id": siparis_no,
            "siparis_no": siparis_no,
            "urun": urunler[0] if urunler else f"Amazon siparişi {siparis_no}",
            "adet": max(1, adet),
            "satis_fiyati": round(satis, 2),
            "musteri": musteri,
            "siparis_tarihi": tarih,
            "durum": durum,
            "komisyon_yuzde": 0.0,
            "notlar": "",
            "gonderi": None,
            "iade": None,
        }


def _zaman(bas) -> str:
    an = datetime.fromisoformat(bas.isoformat()).replace(
        tzinfo=timezone.utc, hour=0, minute=0, second=0
    )
    return an.strftime("%Y-%m-%dT%H:%M:%SZ")
