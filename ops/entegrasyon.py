"""Pazaryeri entegrasyonları: platform kaydı, şifreli kimlik, test ve senkron.

Platform listesi ``PLATFORMLAR`` içinde tanımlıdır; arayüz bu listeden form
alanlarını kurar. Kimlik bilgileri ``sifre`` modülüyle şifrelenerek saklanır
ve API tarafından geri gönderilmez.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timedelta

from . import sifre, sync
from .adapters import SIRA, al as adaptör_al
from .adapters.temel import AgHatasi, metin, test_sonucu


def _alan(id_: str, ad: str, *, zorunlu: bool = False, gizli: bool = False,
          varsayilan: str = "", ipucu: str = "") -> dict:
    return {"id": id_, "ad": ad, "zorunlu": zorunlu, "gizli": gizli,
            "varsayilan": varsayilan, "ipucu": ipucu}


PLATFORMLAR: dict[str, dict] = {
    "trendyol": {
        "id": "trendyol",
        "ad": "Trendyol",
        "pazaryeri": "Trendyol",
        "yetkinlik": ["Sipariş", "Kargo"],
        "not": "Satıcı paneli > API entegrasyonu bölümünden API anahtarınızı "
               "alın. Tarih aralıkları 14 günlük parçalar halinde çekilir.",
        "alanlar": [
            _alan("sellerId", "Mağaza (Seller) ID", zorunlu=True,
                  ipucu="örn. 12345"),
            _alan("apiKey", "API Key", zorunlu=True, gizli=True),
            _alan("apiSecret", "API Secret", zorunlu=True, gizli=True),
            _alan("tabanAdres", "API adresi",
                  varsayilan="https://apigw.trendyol.com",
                  ipucu="Değiştirmeniz gerekmez."),
        ],
    },
    "hepsiburada": {
        "id": "hepsiburada",
        "ad": "Hepsiburada",
        "pazaryeri": "Hepsiburada",
        "yetkinlik": ["Sipariş"],
        "not": "Hepsiburada API portalinde Basic kimlik kullanılır: kullanıcı "
               "adı = Merchant ID, parola = API anahtarı.",
        "alanlar": [
            _alan("merchantId", "Merchant ID", zorunlu=True),
            _alan("apiKey", "API anahtarı", zorunlu=True, gizli=True),
            _alan("tabanAdres", "API adresi",
                  varsayilan="https://oms-external.hepsiburada.com",
                  ipucu="Sandbox için sit adresini yazabilirsiniz."),
        ],
    },
    "n11": {
        "id": "n11",
        "ad": "N11",
        "pazaryeri": "N11",
        "yetkinlik": ["Sipariş", "Kargo"],
        "not": "N11 rest API anahtarları ``appkey`` ve ``appSecret`` "
               "başlıklarıyla gönderilir; teslimat paketleri listesi tarih "
               "aralığına göre süzülür.",
        "alanlar": [
            _alan("appKey", "App Key", zorunlu=True, gizli=True),
            _alan("appSecret", "App Secret", zorunlu=True, gizli=True),
            _alan("tabanAdres", "API adresi",
                  varsayilan="https://api.n11.com"),
        ],
    },
    "ciceksepeti": {
        "id": "ciceksepeti",
        "ad": "ÇiçekSepeti",
        "pazaryeri": "Diger",
        "yetkinlik": ["Sipariş", "Kargo", "İade"],
        "not": "Satıcı API'sinde ``x-api-key`` ve ``user-agent`` (mağaza "
               "numarası) başlıkları kullanılır; sorgular 14 günden uzun "
               "olamaz.",
        "alanlar": [
            _alan("magazaId", "Mağaza numarası", zorunlu=True,
                  ipucu="user-agent başlığı olarak gider"),
            _alan("apiKey", "API anahtarı", zorunlu=True, gizli=True),
            _alan("tabanAdres", "API adresi",
                  varsayilan="https://apis.ciceksepeti.com"),
        ],
    },
    "shopier": {
        "id": "shopier",
        "ad": "Shopier",
        "pazaryeri": "Diger",
        "yetkinlik": ["Sipariş", "Kargo", "İade"],
        "not": "Shopier > Ayarlar > API erişiminden kişisel erişim token'ı "
               "(PAT) alınır; ``Authorization: Bearer`` olarak gönderilir.",
        "alanlar": [
            _alan("token", "Erişim token'ı", zorunlu=True, gizli=True),
            _alan("tabanAdres", "API adresi",
                  varsayilan="https://api.shopier.com"),
        ],
    },
    "pazarama": {
        "id": "pazarama",
        "ad": "Pazarama",
        "pazaryeri": "Diger",
        "yetkinlik": ["Sipariş"],
        "not": "Mağaza entegrasyonu için client_id / client_secret alınır; "
               "panel önce OAuth2 jetonu alır, ardından siparişleri çeker.",
        "alanlar": [
            _alan("clientId", "Client ID", zorunlu=True),
            _alan("clientSecret", "Client Secret", zorunlu=True, gizli=True),
            _alan("tabanAdres", "API adresi",
                  varsayilan="https://isortagimapi.pazarama.com"),
            _alan("tokenAdres", "Jeton adresi",
                  varsayilan="https://isortagimgiris.pazarama.com/connect/"
                             "token"),
        ],
    },
    "shopify": {
        "id": "shopify",
        "ad": "Shopify",
        "pazaryeri": "Diger",
        "yetkinlik": ["Sipariş", "Kargo"],
        "not": "Shopify Admin > Uygulalar > Admin API erişim jetonu "
               "(``shpat_`` ile başlar).",
        "alanlar": [
            _alan("magaza", "Mağaza adresi", zorunlu=True,
                  ipucu="örn. dukkanim.myshopify.com"),
            _alan("accessToken", "Admin API access token", zorunlu=True,
                  gizli=True),
        ],
    },
    "woocommerce": {
        "id": "woocommerce",
        "ad": "WooCommerce",
        "pazaryeri": "Diger",
        "yetkinlik": ["Sipariş"],
        "not": "WooCommerce > Ayarlar > Gelişmiş > REST API: okuma yetkili "
               "Consumer Key / Consumer Secret üretin.",
        "alanlar": [
            _alan("magaza", "Mağaza adresi", zorunlu=True,
                  ipucu="örn. https://magazam.com"),
            _alan("consumerKey", "Consumer Key", zorunlu=True, gizli=True),
            _alan("consumerSecret", "Consumer Secret", zorunlu=True,
                  gizli=True),
        ],
    },
    "amazon": {
        "id": "amazon",
        "ad": "Amazon SP-API",
        "pazaryeri": "Amazon TR",
        "yetkinlik": ["Sipariş"],
        "not": "Selling Partner API (LWA): refresh token + client id/secret. "
               "TR pazarı kimliği varsayılan olarak A33AVAJ2PDY3EV'dir.",
        "alanlar": [
            _alan("refreshToken", "Refresh token", zorunlu=True, gizli=True),
            _alan("clientId", "LWA client id", zorunlu=True),
            _alan("clientSecret", "LWA client secret", zorunlu=True,
                  gizli=True),
            _alan("marketplaceId", "Marketplace ID",
                  varsayilan="A33AVAJ2PDY3EV"),
            _alan("bolge", "Bölge", varsayilan="eu",
                  ipucu="eu / na / fe"),
        ],
    },
}


def platform_listesi() -> list[dict]:
    return [dict(PLATFORMLAR[p]) for p in SIRA if p in PLATFORMLAR]


def _bilesenler(platform: str, ayarlar: dict, kimlik: dict,
                onceki: dict | None = None) -> tuple[dict, dict]:
    """Girdiyi ``ayarlar``/``kimlik`` olarak böler; ``onceki`` eski sırları
    tamamlar (boş bırakılan gizli alan silinmez)."""
    spec = PLATFORMLAR.get(platform)
    if spec is None:
        raise ValueError(f"Bilinmeyen platform: {platform}")
    onceki = onceki or {}
    a, k, eksik = {}, {}, []
    for alan in spec["alanlar"]:
        deger = metin((ayarlar or {}).get(alan["id"])) or \
            metin((kimlik or {}).get(alan["id"]))
        if not deger and alan["gizli"]:
            deger = metin(onceki.get(alan["id"]))
        if not deger:
            deger = metin(alan.get("varsayilan"))
        if not deger:
            if alan.get("zorunlu"):
                eksik.append(alan["ad"])
            continue
        (k if alan["gizli"] else a)[alan["id"]] = deger
    if eksik:
        raise ValueError("Eksik zorunlu alanlar: " + ", ".join(eksik))
    return a, k


def _kimlik_yaz(kimlik: dict) -> str:
    return sifre.sifrele(json.dumps(kimlik, ensure_ascii=False))


def _kimlik_coz(ham: str) -> dict:
    if not ham:
        return {}
    metin_ = sifre.coz(ham)
    veri = json.loads(metin_)
    return veri if isinstance(veri, dict) else {}


def liste(conn: sqlite3.Connection) -> list[dict]:
    satirlar = conn.execute(
        "SELECT * FROM entegrasyonlar ORDER BY id"
    ).fetchall()
    return [_donustur(s) for s in satirlar]


def _donustur(s: sqlite3.Row) -> dict:
    spec = PLATFORMLAR.get(s["platform"], {})
    try:
        kimlik = _kimlik_coz(s["kimlik"])
    except (ValueError, json.JSONDecodeError):
        kimlik = {}
    try:
        ayarlar = json.loads(s["ayarlar"] or "{}")
    except json.JSONDecodeError:
        ayarlar = {}
    return {
        "id": s["id"],
        "platform": s["platform"],
        "platform_ad": spec.get("ad", s["platform"]),
        "ad": s["ad"],
        "ayarlar": ayarlar,
        "dolu": [a["id"] for a in spec.get("alanlar", [])
                 if a["gizli"] and metin(kimlik.get(a["id"]))],
        "son_test": s["son_test"],
        "son_test_sonuc": s["son_test_sonuc"],
        "son_test_mesaj": s["son_test_mesaj"],
        "son_sync": s["son_sync"],
        "son_sync_sonuc": s["son_sync_sonuc"],
        "son_sync_sayi": s["son_sync_sayi"],
        "aktif": bool(s["aktif"]),
        "olusturma": s["olusturma"],
    }


def satir(conn: sqlite3.Connection, kayit_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM entegrasyonlar WHERE id=?", (int(kayit_id),)
    ).fetchone()


def _satir_cevir(conn: sqlite3.Connection, kayit) -> sqlite3.Row:
    """Kayıt satırını ya da ``id`` içeren sözlüğü satıra çevirir."""
    if kayit is None:
        raise ValueError("Bağlantı bulunamadı.")
    if isinstance(kayit, sqlite3.Row):
        return kayit
    kayit_id = (kayit or {}).get("id") if isinstance(kayit, dict) else kayit
    if kayit_id in (None, ""):
        raise ValueError("Bağlantı bulunamadı.")
    satircik = satir(conn, int(kayit_id))
    if satircik is None:
        raise ValueError(f"Bağlantı bulunamadı: {kayit_id}")
    return satircik


def kaydet(conn: sqlite3.Connection, *, platform: str, ad: str,
           ayarlar: dict | None = None, kimlik: dict | None = None) -> dict:
    """Bağlantıyı kaydeder; aynı (platform, ad) tekrarlanırsa güncellenir."""
    ad_metni = metin(ad)
    if not ad_metni:
        raise ValueError("Bağlantı adı zorunlu.")
    mevcut = conn.execute(
        "SELECT * FROM entegrasyonlar WHERE platform=? AND ad=?",
        (platform, ad_metni),
    ).fetchone()
    eski = _kimlik_coz(mevcut["kimlik"]) if mevcut else {}
    yeni_ayarlar, yeni_kimlik = _bilesenler(platform, ayarlar, kimlik,
                                            onceki=eski)
    if mevcut:
        conn.execute(
            "UPDATE entegrasyonlar SET ayarlar=?, kimlik=?, son_test=NULL, "
            "son_test_sonuc=NULL, son_test_mesaj=NULL WHERE id=?",
            (json.dumps(yeni_ayarlar, ensure_ascii=False),
             _kimlik_yaz(yeni_kimlik), int(mevcut["id"])),
        )
    else:
        conn.execute(
            """INSERT INTO entegrasyonlar (platform, ad, ayarlar, kimlik)
               VALUES (?,?,?,?)""",
            (platform, ad_metni,
             json.dumps(yeni_ayarlar, ensure_ascii=False),
             _kimlik_yaz(yeni_kimlik)),
        )
    conn.commit()
    kayit = conn.execute(
        "SELECT * FROM entegrasyonlar WHERE platform=? AND ad=?",
        (platform, ad_metni),
    ).fetchone()
    return _donustur(kayit)


def sil(conn: sqlite3.Connection, kayit_id: int) -> dict:
    kayit = satir(conn, kayit_id)
    if kayit is None:
        raise ValueError(f"Bağlantı bulunamadı: {kayit_id}")
    conn.execute("DELETE FROM entegrasyonlar WHERE id=?", (int(kayit_id),))
    conn.commit()
    return {"silindi": int(kayit_id), "ad": kayit["ad"]}


def acilan(conn: sqlite3.Connection, kayit: sqlite3.Row) -> tuple[dict, dict, str]:
    """Kayıtlı satırın ayarlarını ve şifreli kimliğini çözer."""
    if kayit is None:
        raise ValueError("Bağlantı bulunamadı.")
    platform = kayit["platform"]
    if platform not in PLATFORMLAR:
        raise ValueError(f"Bilinmeyen platform: {platform}")
    ayarlar = json.loads(kayit["ayarlar"] or "{}")
    try:
        kimlik = _kimlik_coz(kayit["kimlik"])
    except (ValueError, json.JSONDecodeError) as e:
        raise ValueError(
            "Kayıtlı kimlik bilgisi çözülemedi (anahtar dosyası değişmiş "
            f"olabilir): {e}"
        ) from e
    return ayarlar, kimlik, platform


def _son_test_yaz(conn, kayit_id: int, sonuc: dict) -> None:
    conn.execute(
        "UPDATE entegrasyonlar SET son_test=?, son_test_sonuc=?, "
        "son_test_mesaj=? WHERE id=?",
        (
            datetime.now().isoformat(timespec="seconds"),
            str(sonuc.get("durum") or ""),
            str(sonuc.get("mesaj") or ""),
            int(kayit_id),
        ),
    )
    conn.commit()


def test_et(conn: sqlite3.Connection, kayit: sqlite3.Row | None = None, *,
            platform: str = "", ayarlar: dict | None = None,
            kimlik: dict | None = None, http=None) -> dict:
    """Bağlantıyı gerçek bir istekle test eder (kayıtlı ya da taslak)."""
    if kayit is not None:
        kayit = _satir_cevir(conn, kayit)
        a, k, platform = acilan(conn, kayit)
    else:
        a, k = _bilesenler(platform, ayarlar, kimlik)
    adaptör = adaptör_al(platform)
    sonuc = adaptör.test(a, k, http=http)
    if kayit is not None:
        _son_test_yaz(conn, int(kayit["id"]), sonuc)
    return sonuc


def senkron(conn: sqlite3.Connection, kayit: sqlite3.Row, *, gun: int = 30,
            http=None) -> dict:
    """Tarih aralığındaki siparişleri çeker ve yerel veritabanına yazar."""
    kayit = _satir_cevir(conn, kayit)
    a, k, platform = acilan(conn, kayit)
    spec = PLATFORMLAR[platform]
    gun = max(1, min(90, int(gun or 30)))
    bit = date.today()
    bas = bit - timedelta(days=gun - 1)
    adaptör = adaptör_al(platform)

    try:
        veri = adaptör.cek(a, k, bas, bit, http=http)
    except AgHatasi as e:
        return _senkron_kaydet(conn, kayit, {
            "durum": "ag", "kod": None,
            "mesaj": "Ağ/SSL hatası — platforma ulaşılamadı: "
                     f"{type(e).__name__}: {e}",
            "sayi": None, "toplam": 0, "atlandi": 0, "notlar": [],
            "aralik": {"bas": bas.isoformat(), "bit": bit.isoformat()},
        })
    except ValueError as e:
        return _senkron_kaydet(conn, kayit, {
            "durum": "hata", "kod": None, "mesaj": str(e), "sayi": None,
            "toplam": 0, "atlandi": 0, "notlar": [],
            "aralik": {"bas": bas.isoformat(), "bit": bit.isoformat()},
        })

    kod = veri.get("kod")
    ek = " ".join(veri.get("notlar") or [])
    if kod is not None and not 200 <= int(kod) < 300:
        sonuc = test_sonucu(kod, ek)
        sonuc.update({
            "sayi": None, "toplam": 0, "atlandi": veri.get("atlandi", 0),
            "notlar": veri.get("notlar") or [],
        })
        return _senkron_kaydet(conn, kayit, {
            **sonuc,
            "aralik": {"bas": bas.isoformat(), "bit": bit.isoformat()},
        })

    say = sync.kaydet(conn, kaynak=platform, pazaryeri=spec["pazaryeri"],
                      siparisler=veri.get("siparisler") or [])
    toplam = len(veri.get("siparisler") or [])
    if toplam:
        mesaj = f"{say['siparis_yeni']} yeni, {say['siparis_guncel']} " \
                f"güncellenen sipariş; {say['gonderi_yeni'] + say['gonderi_guncel']} " \
                f"gönderi, {say['iade_yeni'] + say['iade_guncel']} iade kaydı."
        durum = "ok"
    elif veri.get("ham_toplam"):
        mesaj = f"Bağlantı çalışıyor fakat yanıt şekli tanınamadı — " \
                f"{veri.get('ham_toplam')} ham kayıt işlenemedi."
        durum = "uyari"
    else:
        mesaj = f"{bas.isoformat()} – {bit.isoformat()} aralığında sipariş yok."
        durum = "ok"
    if ek:
        mesaj += " " + ek
    if say.get("atlandi"):
        mesaj += f" {say['atlandi']} kayıt atlandı."

    return _senkron_kaydet(conn, kayit, {
        "durum": durum,
        "kod": kod,
        "mesaj": mesaj,
        "sayi": say,
        "toplam": toplam,
        "atlandi": veri.get("atlandi", 0),
        "notlar": veri.get("notlar") or [],
        "aralik": {"bas": bas.isoformat(), "bit": bit.isoformat()},
    })


def _senkron_kaydet(conn, kayit: sqlite3.Row, sonuc: dict) -> dict:
    say = sonuc.get("sayi") or {}
    girilen = int(say.get("siparis_yeni", 0)) + int(say.get("siparis_guncel", 0))
    conn.execute(
        "UPDATE entegrasyonlar SET son_sync=?, son_sync_sonuc=?, "
        "son_sync_sayi=? WHERE id=?",
        (
            datetime.now().isoformat(timespec="seconds"),
            str(sonuc.get("durum") or ""),
            girilen,
            int(kayit["id"]),
        ),
    )
    conn.commit()
    return sonuc
