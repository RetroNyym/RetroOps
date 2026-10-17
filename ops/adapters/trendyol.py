"""Trendyol sipariş entegrasyonu (Satıcı API v3).

Uç: ``GET /integration/order/sellers/{sellerId}/orders`` — Basic kimlik
(``apiKey:apiSecret``), ``User-Agent: {apiKey} - SelfIntegration`` başlığı
zorunlu. Tarih aralığı en fazla 2 hafta istenebildiği için aralık
14 günlük pencerelere bölünür.
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
    metin,
    pencere_dondur,
    pencere_zamani,
    sayi,
    sonuc,
    tahmin_teslim,
    tarih_oku,
)

DURUM_HARITASI = {
    "created": "hazirlaniyor",
    "picking": "hazirlaniyor",
    "waiting": "hazirlaniyor",
    "readytoship": "hazirlaniyor",
    "invoiced": "hazirlaniyor",
    "shipped": "kargoya_verildi",
    "shippedbyexport": "kargoya_verildi",
    "delivered": "teslim",
    "undelivered": "kargoya_verildi",
    "returned": "iade",
    "returning": "iade",
    "partiallyreturned": "iade",
    "cancelled": "iptal",
    "canceled": "iptal",
    "pending": "hazirlaniyor",
}

DURUM_GONDERI = {
    "hazirlaniyor": "hazir",
    "kargoya_verildi": "yolda",
    "teslim": "teslim",
    "iade": "sorunlu",
    "iade_tamam": "teslim",
    "iptal": "hazir",
}


class Adapter(TemelAdapter):
    platform = "trendyol"
    taban_varsayilan = "https://apigw.trendyol.com"

    def basliklar(self, kimlik: dict) -> dict:
        api_key = metin(kimlik.get("apiKey"))
        api_secret = metin(kimlik.get("apiSecret"))
        temel = base64.b64encode(
            f"{api_key}:{api_secret}".encode("utf-8")
        ).decode("ascii")
        return {
            "Authorization": f"Basic {temel}",
            "User-Agent": f"{api_key} - SelfIntegration",
        }

    def cek(self, ayarlar, kimlik, bas, bit, *, sinir=MAK_SINIR, http=None):
        http = http or istek
        satici = metin(ayarlar.get("sellerId"))
        if not satici:
            raise ValueError("Mağaza (Seller) ID girilmemiş.")
        taban = self.taban(ayarlar)
        basliklar = self.basliklar(kimlik)
        kayitlar: list[dict] = []
        notlar: list[str] = []
        atlandi = ham_toplam = 0
        kod = None

        for alt, ust in pencere_dondur(bas, bit, 14):
            if len(kayitlar) >= sinir:
                break
            bas_ts, bit_ts = pencere_zamani(alt, ust)
            sayfa, toplam_sayfa = 0, 1
            while sayfa < toplam_sayfa and sayfa < 4:
                sorgu = urllib.parse.urlencode({
                    "startDate": bas_ts,
                    "endDate": bit_ts,
                    "page": sayfa,
                    "size": 200,
                })
                url = (f"{taban}/integration/order/sellers/{satici}"
                       f"/orders?{sorgu}")
                yanit = http(url, basliklar=basliklar)
                kod = yanit.kod
                if not 200 <= kod < 300:
                    notlar.append(f"Trendyol isteği HTTP {kod} döndü.")
                    return sonuc(siparisler=kayitlar, atlandi=atlandi, kod=kod,
                                 notlar=notlar, ham_toplam=ham_toplam)
                veri = yanit.veri if isinstance(yanit.veri, dict) else {}
                liste = veri.get("content")
                liste = liste if isinstance(liste, list) else []
                ham_toplam += len(liste)
                toplam_sayfa = int(sayi(veri.get("totalPages"), 1) or 1)
                for paket in liste:
                    if len(kayitlar) >= sinir:
                        break
                    satir = self._satir(paket)
                    if satir:
                        kayitlar.append(satir)
                    else:
                        atlandi += 1
                sayfa += 1
                if not liste:
                    break

        return sonuc(siparisler=kayitlar, atlandi=atlandi, kod=kod,
                     notlar=notlar, ham_toplam=ham_toplam)

    def _satir(self, paket) -> dict | None:
        if not isinstance(paket, dict):
            return None
        paket_id = paket.get("id") or paket.get("shipmentPackageId")
        if paket_id in (None, ""):
            return None
        satirlar = paket.get("lines") or paket.get("lineItems") or []
        if not isinstance(satirlar, list):
            satirlar = []

        adet, urunler = 0, []
        for s in satirlar:
            if not isinstance(s, dict):
                continue
            adet += int(sayi(s.get("quantity"), 1) or 1)
            ad = metin(s.get("productName") or s.get("title"))
            if ad:
                urunler.append(ad)

        satis = sayi(paket.get("totalPrice")) or sayi(paket.get("grossAmount"))
        if satis <= 0:
            satis = sum(
                sayi(s.get("price")) * (sayi(s.get("quantity"), 1) or 1)
                for s in satirlar if isinstance(s, dict)
            )
        if satis <= 0:
            return None

        adres = paket.get("shipmentAddress") or paket.get("invoiceAddress")
        if not isinstance(adres, dict):
            adres = {}
        musteri = (metin(adres.get("firstName")) + " "
                   + metin(adres.get("lastName"))).strip()
        tarih = tarih_oku(paket.get("orderDate") or paket.get("createDate"))
        durum = durum_eslestir(
            DURUM_HARITASI,
            paket.get("status") or paket.get("shipmentPackageStatus"),
        )

        komisyon = 0.0
        if satirlar and isinstance(satirlar[0], dict):
            deger = sayi(satirlar[0].get("commission"))
            if 0 < deger < 100:
                komisyon = deger

        gonderi = None
        takip = metin(paket.get("cargoTrackingNumber"))
        if takip:
            gonderi = {
                "takip_no": takip,
                "kargo_firmasi": kargo_firmasi(paket.get("cargoProviderName")),
                "gonderim_tarihi": tarih,
                "tahmini_teslim": tahmin_teslim(tarih),
                "son_durum": DURUM_GONDERI.get(durum, "yolda"),
                "notlar": "",
            }

        return {
            "dis_id": str(paket_id),
            "siparis_no": metin(paket.get("orderNumber")) or str(paket_id),
            "urun": urunler[0] if urunler else "Trendyol siparişi",
            "adet": max(1, adet),
            "satis_fiyati": round(satis, 2),
            "musteri": musteri,
            "siparis_tarihi": tarih,
            "durum": durum,
            "komisyon_yuzde": komisyon,
            "notlar": "",
            "gonderi": gonderi,
            "iade": None,
        }
