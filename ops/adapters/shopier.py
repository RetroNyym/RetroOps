"""Shopier sipariş entegrasyonu (v1, Bearer kişisel erişim token'ı).

Uç: ``GET /v1/orders`` — ``Authorization: Bearer {token}`` başlığı; tarihler
``yyyy-MM-ddTHH:mm:ss+03:00`` biçiminde gönderilir.
"""

from __future__ import annotations

import urllib.parse
from datetime import datetime, timedelta, timezone

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
    "unfulfilled": "hazirlaniyor",
    "readytoship": "hazirlaniyor",
    "processing": "hazirlaniyor",
    "fulfilled": "kargoya_verildi",
    "shipped": "kargoya_verildi",
    "delivered": "teslim",
    "completed": "teslim",
    "cancelled": "iptal",
    "canceled": "iptal",
    "refunded": "iade",
    "returned": "iade",
}

GONDERI_DURUM = {
    "delivered": "teslim",
    "in_transit": "yolda",
    "shipped": "yolda",
    "picked_up": "yolda",
    "preparing": "hazir",
    "problem": "sorunlu",
    "lost": "sorunlu",
}

ANAHTARLAR = ("data", "orders", "content", "result", "items")


def _damga(tarih_iso: str) -> str:
    saat = datetime.fromisoformat(tarih_iso).replace(
        tzinfo=timezone(timedelta(hours=3))
    )
    return saat.isoformat(timespec="seconds")


class Adapter(TemelAdapter):
    platform = "shopier"
    taban_varsayilan = "https://api.shopier.com"

    def cek(self, ayarlar, kimlik, bas, bit, *, sinir=MAK_SINIR, http=None):
        http = http or istek
        sorgu = urllib.parse.urlencode({
            "limit": min(100, sinir),
            "dateStart": _damga(bas.isoformat()),
            "dateEnd": _damga(bit.isoformat()),
        })
        url = f"{self.taban(ayarlar)}/v1/orders?{sorgu}"
        yanit = http(url, basliklar={
            "Authorization": f"Bearer {metin(kimlik.get('token'))}",
        })
        if not 200 <= yanit.kod < 300:
            return sonuc(siparisler=[], atlandi=0, kod=yanit.kod,
                         notlar=[f"Shopier isteği HTTP {yanit.kod} döndü."])

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
        siparis_no = metin(ham.get("id") or ham.get("orderNumber"))
        if not siparis_no:
            return None

        urunler = ham.get("lineItems")
        urunler = [u for u in urunler if isinstance(u, dict)] \
            if isinstance(urunler, list) else []
        adet = sum(int(sayi(u.get("quantity"), 1) or 1) for u in urunler)
        basliklar = [metin(u.get("title") or u.get("name")) for u in urunler]
        basliklar = [b for b in basliklar if b]

        toplamlar = ham.get("totals") or {}
        if not isinstance(toplamlar, dict):
            toplamlar = {}
        satis = (sayi(toplamlar.get("total")) or sayi(ham.get("total"))
                 or sayi(ham.get("grandTotal")))
        if satis <= 0 and urunler:
            satis = sum((sayi(u.get("total")) or sayi(u.get("price")))
                        * (sayi(u.get("quantity"), 1) or 1) for u in urunler)
        if satis <= 0:
            return None

        adres = ham.get("shippingInfo") or {}
        if not isinstance(adres, dict):
            adres = {}
        musteri = (metin(ham.get("customerName"))
                   or (metin(adres.get("firstName")) + " "
                       + metin(adres.get("lastName"))).strip())
        tarih = tarih_oku(ham.get("dateCreated") or ham.get("createdAt")
                          or ham.get("date") or ham.get("dateModified"))

        durum = durum_eslestir(
            DURUM_HARITASI,
            ham.get("status") or ham.get("orderStatus")
            or ham.get("paymentStatus"),
        )

        iade = None
        iadeler = ham.get("refunds")
        iadeler = [r for r in iadeler if isinstance(r, dict)] \
            if isinstance(iadeler, list) else []
        if iadeler:
            ilk = iadeler[0]
            tutar = sayi(ilk.get("total")) or satis
            iade = {
                "tutar": round(tutar, 2),
                "sebep": metin(ilk.get("reason")) or "Diğer",
                "talep_tarihi": tarih_oku(ilk.get("dateCreated"),
                                          varsayilan=tarih),
                "musteri": musteri,
                "notlar": "Shopier iade kaydı (otomatik).",
            }
            durum = "iade"

        gonderi = None
        sevkiyat = ham.get("fulfillments")
        if isinstance(sevkiyat, dict):
            sevkiyat = sevkiyat.get("shipping") or sevkiyat.get("list") or []
        sevkiyat = [f for f in sevkiyat if isinstance(f, dict)] \
            if isinstance(sevkiyat, list) else []
        takip = ""
        for k in sevkiyat:
            takip = metin(k.get("trackingNumber") or k.get("tracking_number"))
            if takip:
                break
        if takip:
            ilk_k = sevkiyat[0]
            gonderi = {
                "takip_no": takip,
                "kargo_firmasi": kargo_firmasi(ilk_k.get("company")
                                               or ilk_k.get("carrier")),
                "gonderim_tarihi": tarih_oku(ilk_k.get("dateDispatched")
                                            or ilk_k.get("dateCreated"),
                                            varsayilan=tarih),
                "tahmini_teslim": tahmin_teslim(tarih),
                "son_durum": GONDERI_DURUM.get(
                    metin(ilk_k.get("status")).lower(), "yolda"
                ),
                "notlar": "",
            }

        return {
            "dis_id": siparis_no,
            "siparis_no": siparis_no,
            "urun": basliklar[0] if basliklar else "Shopier siparişi",
            "adet": max(1, adet),
            "satis_fiyati": round(satis, 2),
            "musteri": musteri,
            "siparis_tarihi": tarih,
            "durum": durum,
            "komisyon_yuzde": 0.0,
            "notlar": "",
            "gonderi": gonderi,
            "iade": iade,
        }
