"""Pazarama sipariş entegrasyonu (Mağaza Gateway, OAuth2 istemci kimliği).

Kimlik: ``POST /connect/token`` (Basic ``client_id:client_secret``, form
``grant_type=client_credentials``) ile alınan erişim jetonu, sipariş isteğinde
``Authorization: Bearer`` olarak kullanılır.
"""

from __future__ import annotations

import base64
from datetime import datetime

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
    "waiting": "hazirlaniyor",
    "preparing": "hazirlaniyor",
    "readytoship": "hazirlaniyor",
    "shipped": "kargoya_verildi",
    "intransit": "kargoya_verildi",
    "delivered": "teslim",
    "completed": "teslim",
    "cancelled": "iptal",
    "canceled": "iptal",
    "refunded": "iade",
    "returned": "iade",
    "closed": "teslim",
    "open": "hazirlaniyor",
}

ANAHTARLAR = ("data", "orders", "orderList", "content", "result", "items")


class Adapter(TemelAdapter):
    platform = "pazarama"
    taban_varsayilan = "https://isortagimapi.pazarama.com"
    token_varsayilan = "https://isortagimgiris.pazarama.com/connect/token"

    def jeton(self, ayarlar, kimlik, http) -> tuple[str | None, int | None]:
        client_id = metin(kimlik.get("clientId"))
        client_secret = metin(kimlik.get("clientSecret"))
        if not client_id or not client_secret:
            raise ValueError("clientId/clientSecret girilmemiş.")
        token_url = metin(ayarlar.get("tokenAdres")) or self.token_varsayilan
        temel = base64.b64encode(
            f"{client_id}:{client_secret}".encode("utf-8")
        ).decode("ascii")
        yanit = http(
            token_url,
            metot="POST",
            basliklar={"Authorization": f"Basic {temel}"},
            govde={"grant_type": "client_credentials",
                   "scope": "merchantgatewayapi.fullaccess"},
            bicim="form",
        )
        if not 200 <= yanit.kod < 300:
            return None, yanit.kod
        veri = yanit.veri if isinstance(yanit.veri, dict) else {}
        return metin(veri.get("access_token")), yanit.kod

    def cek(self, ayarlar, kimlik, bas, bit, *, sinir=MAK_SINIR, http=None):
        http = http or istek
        jeton, kod = self.jeton(ayarlar, kimlik, http)
        if not jeton:
            return sonuc(siparisler=[], atlandi=0, kod=kod,
                         notlar=["Pazarama erişim jetonu alınamadı."])

        govde = {
            "startDate": datetime.combine(bas, datetime.min.time())
            .strftime("%Y-%m-%dT%H:%M:%S"),
            "endDate": datetime.combine(bit, datetime.min.time())
            .strftime("%Y-%m-%dT23:59:59"),
            "orderNumber": "",
        }
        url = f"{self.taban(ayarlar)}/order/getOrdersForApi"
        yanit = http(url, metot="POST", basliklar={
            "Authorization": f"Bearer {jeton}",
        }, govde=govde, bicim="json")
        if not 200 <= yanit.kod < 300:
            return sonuc(siparisler=[], atlandi=0, kod=yanit.kod,
                         notlar=[f"Pazarama isteği HTTP {yanit.kod} döndü."])

        liste = liste_bul(yanit.veri, ANAHTARLAR) or []
        kayitlar, atlandi = [], 0
        for ham in liste:
            if len(kayitlar) >= sinir:
                break
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
        siparis_no = (metin(ham.get("orderNumber")) or metin(ham.get("number"))
                      or metin(ham.get("merchantOrderId")))
        kimlik = ham.get("orderId") or ham.get("id") or siparis_no
        if not siparis_no and not kimlik:
            return None

        satis = (sayi(ham.get("totalPrice")) or sayi(ham.get("grandTotal"))
                 or sayi(ham.get("total")) or sayi(ham.get("orderTotal"))
                 or sayi(ham.get("amount")))
        if satis <= 0:
            kalem = ham.get("items") or ham.get("orderItems") or []
            if isinstance(kalem, list):
                satis = sum(
                    sayi(s.get("total") or s.get("price"))
                    * (sayi(s.get("quantity"), 1) or 1)
                    for s in kalem if isinstance(s, dict)
                )
        if satis <= 0:
            return None

        tarih = tarih_oku(ham.get("orderDate") or ham.get("createdDate")
                          or ham.get("creationDate") or ham.get("createdAt")
                          or ham.get("date"))
        musteri = metin(ham.get("customerName") or ham.get("buyerName"))
        if not musteri:
            musteri_bilgi = ham.get("customer") or ham.get("shippingAddress") \
                or {}
            if isinstance(musteri_bilgi, dict):
                musteri = (metin(musteri_bilgi.get("firstName")) + " "
                           + metin(musteri_bilgi.get("lastName"))).strip()

        durum = durum_eslestir(DURUM_HARITASI,
                               ham.get("status") or ham.get("orderStatus")
                               or ham.get("state"))
        takip = (metin(ham.get("trackingNumber"))
                 or metin(ham.get("cargoTrackingNumber"))
                 or metin(ham.get("waybillNumber")))
        gonderi = None
        if takip and tarih:
            gonderi = {
                "takip_no": takip,
                "kargo_firmasi": kargo_firmasi(ham.get("cargoCompany")
                                               or ham.get("cargoName")
                                               or ham.get("shippingCarrier")),
                "gonderim_tarihi": tarih,
                "tahmini_teslim": tahmin_teslim(tarih),
                "son_durum": ("teslim" if durum == "teslim" else
                              "hazir" if durum in ("hazirlaniyor", "iptal")
                              else "yolda"),
                "notlar": "",
            }

        kalem = ham.get("items") or ham.get("orderItems") or []
        urunler = [metin(s.get("name") or s.get("productName"))
                   for s in kalem if isinstance(s, dict)] if isinstance(kalem, list) else []
        urunler = [u for u in urunler if u]
        adet = 1
        if isinstance(kalem, list) and kalem:
            adet = sum(int(sayi(s.get("quantity"), 1) or 1)
                       for s in kalem if isinstance(s, dict))

        return {
            "dis_id": str(kimlik),
            "siparis_no": siparis_no or str(kimlik),
            "urun": urunler[0] if urunler else "Pazarama siparişi",
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
