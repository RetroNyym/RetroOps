"""WooCommerce sipariş entegrasyonu (REST v3, ``ck_``/``cs_`` Basic kimlik).

Uç: ``GET {mağaza}/wp-json/wc/v3/orders`` — mağaza adresi alanından gelir,
Consumer Key/Secret Basic kimlik olarak gönderilir.
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
    sayi,
    sonuc,
    tahmin_teslim,
    tarih_oku,
)

DURUM_HARITASI = {
    "pending": "hazirlaniyor",
    "processing": "hazirlaniyor",
    "on-hold": "hazirlaniyor",
    "checkout-draft": "hazirlaniyor",
    "completed": "teslim",
    "cancelled": "iptal",
    "canceled": "iptal",
    "failed": "iptal",
    "refunded": "iade",
    "trash": "iptal",
}


class Adapter(TemelAdapter):
    platform = "woocommerce"
    taban_varsayilan = ""

    def magaza_adresi(self, ayarlar: dict) -> str:
        magaza = metin(ayarlar.get("magaza")).rstrip("/")
        if not magaza:
            raise ValueError("Mağaza adresi girilmemiş.")
        if not magaza.startswith("http"):
            magaza = "https://" + magaza
        return magaza

    def cek(self, ayarlar, kimlik, bas, bit, *, sinir=MAK_SINIR, http=None):
        http = http or istek
        sorgu = urllib.parse.urlencode({
            "after": f"{bas.isoformat()}T00:00:00",
            "before": f"{bit.isoformat()}T23:59:59",
            "per_page": min(100, sinir),
            "status": "any",
        })
        url = f"{self.magaza_adresi(ayarlar)}/wp-json/wc/v3/orders?{sorgu}"
        temel = base64.b64encode(
            f"{metin(kimlik.get('consumerKey'))}:"
            f"{metin(kimlik.get('consumerSecret'))}".encode("utf-8")
        ).decode("ascii")
        yanit = http(url, basliklar={"Authorization": f"Basic {temel}"})
        if not 200 <= yanit.kod < 300:
            return sonuc(siparisler=[], atlandi=0, kod=yanit.kod,
                         notlar=[f"WooCommerce isteği HTTP {yanit.kod} "
                                 "döndü."])

        veri = yanit.veri
        liste = veri if isinstance(veri, list) else []
        if not liste and isinstance(veri, dict):
            liste = veri.get("orders") or veri.get("data") or []
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

    def _meta(self, ham: dict, *anahtarlar: str) -> str:
        for blok in ham.get("meta_data") or []:
            if isinstance(blok, dict) and metin(blok.get("key")) in anahtarlar:
                deger = metin(blok.get("value"))
                if deger:
                    return deger
        return ""

    def _satir(self, ham) -> dict | None:
        if not isinstance(ham, dict):
            return None
        siparis_no = metin(ham.get("number")) or metin(ham.get("id"))
        kimlik = ham.get("id") or siparis_no
        if not siparis_no and not kimlik:
            return None

        kalemler = ham.get("line_items")
        kalemler = [k for k in kalemler if isinstance(k, dict)] \
            if isinstance(kalemler, list) else []
        adet = sum(int(sayi(k.get("quantity"), 1) or 1) for k in kalemler)
        basliklar = [metin(k.get("name")) for k in kalemler]
        basliklar = [b for b in basliklar if b]

        satis = sayi(ham.get("total")) or sayi(ham.get("line_total"))
        if satis <= 0 and kalemler:
            satis = sum(sayi(k.get("total")) * (sayi(k.get("quantity"), 1) or 1)
                        for k in kalemler)
        if satis <= 0:
            return None

        fatura = ham.get("billing") or {}
        if not isinstance(fatura, dict):
            fatura = {}
        musteri = (metin(fatura.get("first_name")) + " "
                   + metin(fatura.get("last_name"))).strip()
        tarih = tarih_oku(ham.get("date_created") or ham.get("date_created_gmt")
                          or ham.get("date_modified"))
        durum = durum_eslestir(DURUM_HARITASI, ham.get("status"))

        takip = self._meta(ham, "_tracking_number", "tracking_number",
                           "_wc_tracking_number")
        gonderi = None
        if takip and tarih:
            gonderi = {
                "takip_no": takip,
                "kargo_firmasi": kargo_firmasi(
                    self._meta(ham, "_tracking_company", "tracking_company")
                ),
                "gonderim_tarihi": tarih,
                "tahmini_teslim": tahmin_teslim(tarih),
                "son_durum": ("teslim" if durum == "teslim" else
                              "hazir" if durum in ("hazirlaniyor", "iptal")
                              else "yolda"),
                "notlar": "",
            }

        iade = None
        if durum == "iade":
            iade = {
                "tutar": round(satis, 2),
                "sebep": "Diğer",
                "talep_tarihi": tarih,
                "musteri": musteri,
                "notlar": "WooCommerce iade durumu (otomatik).",
            }

        return {
            "dis_id": str(kimlik),
            "siparis_no": siparis_no or str(kimlik),
            "urun": basliklar[0] if basliklar else "WooCommerce siparişi",
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
