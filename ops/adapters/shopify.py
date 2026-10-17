"""Shopify sipariş entegrasyonu (Admin API, ``X-Shopify-Access-Token``).

Uç: ``GET https://{mağaza}.myshopify.com/admin/api/latest/orders.json`` —
mağaza adı alanından gelir, jeton başlıkta taşınır.
"""

from __future__ import annotations

import urllib.parse

from .temel import (
    MAK_SINIR,
    TemelAdapter,
    istek,
    kargo_firmasi,
    metin,
    sayi,
    sonuc,
    tahmin_teslim,
    tarih_oku,
)

class Adapter(TemelAdapter):
    platform = "shopify"
    taban_varsayilan = "https://shop.myshopify.com"

    def magaza_adresi(self, ayarlar: dict) -> str:
        magaza = metin(ayarlar.get("magaza")).replace("https://", "") \
            .replace("http://", "").strip("/")
        if not magaza:
            raise ValueError("Mağaza adresi girilmemiş.")
        if "." not in magaza:
            magaza = f"{magaza}.myshopify.com"
        return magaza

    def cek(self, ayarlar, kimlik, bas, bit, *, sinir=MAK_SINIR, http=None):
        http = http or istek
        magaza = self.magaza_adresi(ayarlar)
        sorgu = urllib.parse.urlencode({
            "status": "any",
            "limit": min(250, sinir),
            "created_at_min": f"{bas.isoformat()}T00:00:00Z",
            "created_at_max": f"{bit.isoformat()}T23:59:59Z",
        })
        url = f"https://{magaza}/admin/api/latest/orders.json?{sorgu}"
        yanit = http(url, basliklar={
            "X-Shopify-Access-Token": metin(kimlik.get("accessToken")),
        })
        if not 200 <= yanit.kod < 300:
            return sonuc(siparisler=[], atlandi=0, kod=yanit.kod,
                         notlar=[f"Shopify isteği HTTP {yanit.kod} döndü."])

        veri = yanit.veri if isinstance(yanit.veri, dict) else {}
        liste = veri.get("orders") if isinstance(veri.get("orders"), list) \
            else []
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
        siparis_no = metin(ham.get("name")) or metin(ham.get("order_number"))
        kimlik = ham.get("id") or siparis_no
        if not siparis_no and not kimlik:
            return None

        kalemler = ham.get("line_items")
        kalemler = [k for k in kalemler if isinstance(k, dict)] \
            if isinstance(kalemler, list) else []
        adet = sum(int(sayi(k.get("quantity"), 1) or 1) for k in kalemler)
        basliklar = [metin(k.get("title") or k.get("name")) for k in kalemler]
        basliklar = [b for b in basliklar if b]

        satis = sayi(ham.get("total_price")) or sayi(ham.get("current_total_price"))
        if satis <= 0 and kalemler:
            satis = sum(sayi(k.get("price")) * (sayi(k.get("quantity"), 1) or 1)
                        for k in kalemler)
        if satis <= 0:
            return None

        musteri_bilgi = ham.get("customer") or {}
        if not isinstance(musteri_bilgi, dict):
            musteri_bilgi = {}
        teslimat = ham.get("shipping_address") or {}
        if not isinstance(teslimat, dict):
            teslimat = {}
        musteri = (metin(ham.get("customer_name"))
                   or (metin(musteri_bilgi.get("first_name")) + " "
                       + metin(musteri_bilgi.get("last_name"))).strip()
                   or (metin(teslimat.get("first_name")) + " "
                       + metin(teslimat.get("last_name"))).strip())

        tarih = tarih_oku(ham.get("created_at") or ham.get("processed_at")
                          or ham.get("updated_at"))
        iptal = ham.get("cancelled_at")
        if iptal:
            durum = "iptal"
        elif metin(ham.get("fulfillment_status")).lower() == "fulfilled":
            durum = "kargoya_verildi"
        else:
            durum = "hazirlaniyor"
        if metin(ham.get("financial_status")).lower() == "refunded":
            durum = "iade"

        iade = None
        iadeler = ham.get("refunds")
        iadeler = [r for r in iadeler if isinstance(r, dict)] \
            if isinstance(iadeler, list) else []
        if iadeler:
            ilk = iadeler[0]
            tutar = sayi(ilk.get("amount")) or sayi(ilk.get("total")) or satis
            iade = {
                "tutar": round(tutar, 2),
                "sebep": "Diğer",
                "talep_tarihi": tarih_oku(ilk.get("created_at"),
                                          varsayilan=tarih),
                "musteri": musteri,
                "notlar": "Shopify iade kaydı (otomatik).",
            }
            durum = "iade"

        gonderi = None
        sevkiyat = ham.get("fulfillments")
        sevkiyat = [s for s in sevkiyat if isinstance(s, dict)] \
            if isinstance(sevkiyat, list) else []
        takip = ""
        for s in sevkiyat:
            takip = metin(s.get("tracking_number"))
            if takip:
                break
        if takip:
            ilk = sevkiyat[0]
            gonderi = {
                "takip_no": takip,
                "kargo_firmasi": kargo_firmasi(ilk.get("tracking_company")),
                "gonderim_tarihi": tarih_oku(ilk.get("processed_at")
                                            or ilk.get("created_at"),
                                            varsayilan=tarih),
                "tahmini_teslim": tahmin_teslim(tarih),
                "son_durum": "teslim" if durum == "teslim" else "yolda",
                "notlar": "",
            }

        return {
            "dis_id": str(kimlik),
            "siparis_no": siparis_no or str(kimlik),
            "urun": basliklar[0] if basliklar else "Shopify siparişi",
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
