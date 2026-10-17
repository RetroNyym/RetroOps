"""N11 teslimat/sipariş entegrasyonu (REST, ``appkey``/``appSecret`` başlıkları).

Uç: ``GET /rest/delivery/v1/shipmentPackages`` — kimlik doğrulama başlıklarda
(``appkey`` + ``appSecret`` her ikisi gönderilir). Uç nokta tarih filtresi
belgelerde yer almadığı için gelen kayıtlar istenen tarih aralığına göre
istemci tarafında süzülür; tarihi okunamayan kayıt atlanır.
"""

from __future__ import annotations

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
    "shipped": "kargoya_verildi",
    "intransit": "kargoya_verildi",
    "delivered": "teslim",
    "completed": "teslim",
    "cancelled": "iptal",
    "canceled": "iptal",
    "returned": "iade",
    "returning": "iade",
    "pending": "hazirlaniyor",
    "open": "hazirlaniyor",
    "closed": "teslim",
}

ANAHTARLAR = ("result", "shipments", "shipmentPackages", "packages",
              "orders", "content", "data", "list")


class Adapter(TemelAdapter):
    platform = "n11"
    taban_varsayilan = "https://api.n11.com"

    def cek(self, ayarlar, kimlik, bas, bit, *, sinir=MAK_SINIR, http=None):
        http = http or istek
        url = f"{self.taban(ayarlar)}/rest/delivery/v1/shipmentPackages"
        yanit = http(url, basliklar={
            "appkey": metin(kimlik.get("appKey")),
            "appsecret": metin(kimlik.get("appSecret")),
        })
        if not 200 <= yanit.kod < 300:
            return sonuc(siparisler=[], atlandi=0, kod=yanit.kod,
                         notlar=[f"N11 isteği HTTP {yanit.kod} döndü."])

        liste = liste_bul(yanit.veri, ANAHTARLAR) or []
        kayitlar, atlandi, tarihsiz = [], 0, 0
        for ham in liste:
            if len(kayitlar) >= sinir:
                break
            satir = self._satir(ham)
            if satir is None:
                atlandi += 1
                continue
            if not satir["siparis_tarihi"]:
                tarihsiz += 1
                atlandi += 1
                continue
            if not (bas.isoformat() <= satir["siparis_tarihi"] <= bit.isoformat()):
                continue
            kayitlar.append(satir)

        notlar = []
        if tarihsiz:
            notlar.append(f"N11: tarih alanı okunamayan {tarihsiz} kayıt "
                          "atlandı.")
        if not liste:
            notlar.append("N11 yanıtında kayıt listesi bulunamadı.")
        elif not kayitlar and not atlandi:
            notlar.append("İstenen tarih aralığında kayıt yok.")

        return sonuc(siparisler=kayitlar, atlandi=atlandi, kod=yanit.kod,
                     notlar=notlar, ham_toplam=len(liste))

    def _satir(self, ham) -> dict | None:
        if not isinstance(ham, dict):
            return None
        siparis_no = (metin(ham.get("orderNumber")) or metin(ham.get("orderNo"))
                      or metin(ham.get("orderId")) or metin(ham.get("order_id")))
        kimlik = (ham.get("id") or ham.get("shipmentId")
                  or ham.get("packageNumber") or siparis_no)
        if not siparis_no and not kimlik:
            return None

        satis = (sayi(ham.get("totalPrice")) or sayi(ham.get("salePrice"))
                 or sayi(ham.get("price")) or sayi(ham.get("saleAmount"))
                 or sayi(ham.get("orderTotal")) or sayi(ham.get("amount")))
        adet = int(sayi(ham.get("quantity") or ham.get("lineCount"), 1) or 1)
        if satis <= 0:
            return None

        tarih = tarih_oku(
            ham.get("orderDate") or ham.get("createDate")
            or ham.get("dateCreated") or ham.get("creationDate")
            or ham.get("updateDate") or ham.get("date"),
            varsayilan="",
        )
        musteri = (metin(ham.get("customerName")) or metin(ham.get("buyerName"))
                   or metin(ham.get("recipientName"))
                   or metin(ham.get("memberName"))
                   or (metin(ham.get("firstName")) + " "
                       + metin(ham.get("lastName"))).strip())
        durum = durum_eslestir(DURUM_HARITASI,
                               ham.get("status") or ham.get("shipmentStatus")
                               or ham.get("orderStatus") or ham.get("state"))
        takip = (metin(ham.get("trackingNumber"))
                 or metin(ham.get("cargoTrackingNumber"))
                 or metin(ham.get("waybillNumber")))
        gonderi = None
        if takip and tarih:
            gonderi = {
                "takip_no": takip,
                "kargo_firmasi": kargo_firmasi(ham.get("cargoFirm")
                                               or ham.get("cargoCompany")),
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
            "urun": (metin(ham.get("productName"))
                     or metin(ham.get("productNameWithOption"))
                     or metin(ham.get("title")) or metin(ham.get("name"))
                     or "N11 siparişi"),
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
