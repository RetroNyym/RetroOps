"""Kargo firmalarının API'leri: bağlantı kaydı, test ve takip durumu sorgusu.

Bağlantılar ``entegrasyonlar`` tablosunda ``kargo_`` önekli platform olarak
saklanır; şifreli kimlik saklama ve form doğrulaması için pazaryeri
entegrasyonu altyapısı kullanılır. API adresi/sorgu yolu gibi uçlar her
firmaya göre farklılık gösterdiğinden alanlar arayüzden düzenlenebilir;
doküman firmanızdan alınır.

``senkron`` takip numarası olan gönderileri bağlı firmanın API'sine sorar,
dönen durum metnini panel durumuna eşler ve ``gonderiler`` tablosunu
günceller. Ağ erişimi olmayan ortamlarda sonuç Türkçe hata mesajıyla raporlanır.
"""

from __future__ import annotations

import base64
import sqlite3
import urllib.parse
from datetime import datetime

from . import entegrasyon, kargo
from .adapters.temel import AgHatasi, istek, metin, test_sonucu

ON_EK = "kargo_"
MAK_SINIR = 100  # tek senkronda sorgulanacak azami gönderi


def _alan(id_: str, ad: str, *, zorunlu: bool = False, gizli: bool = False,
          varsayilan: str = "", ipucu: str = "") -> dict:
    return {"id": id_, "ad": ad, "zorunlu": zorunlu, "gizli": gizli,
            "varsayilan": varsayilan, "ipucu": ipucu}


_ORTAK = [
    _alan("tabanAdres", "API adresi", zorunlu=True,
          ipucu="Firmanızın size verdiği API adresi (https://…)."),
    _alan("sorguYolu", "Takip sorgu yolu",
          ipucu="Dokümandaki sorgu adresi, örn. /v1/shipments/track."),
    _alan("takipAlani", "Takip parametresi", varsayilan="trackingNumber",
          ipucu="Sorgu adresinde takip numarasının adı."),
    _alan("denemeTakip", "Deneme takip no",
          ipucu="Test için örnek gönderi numarası (isteğe bağlı)."),
]

FIRMALAR: dict[str, dict] = {
    "yurtici": {
        "id": "yurtici",
        "ad": "Yurtiçi Kargo",
        "kimlikTuru": "temel",
        "not": "Yurtiçi Kurumsal Çözümler API erişim bilgilerinizi (kullanıcı "
               "kodu, şifre, cari hesap) firmanızdan alın; sorgu yolunu "
               "dokümana göre doldurun.",
        "alanlar": list(_ORTAK) + [
            _alan("kullanici", "Kullanıcı kodu", zorunlu=True),
            _alan("parola", "Şifre", zorunlu=True, gizli=True),
        ],
    },
    "aras": {
        "id": "aras",
        "ad": "Aras Kargo",
        "kimlikTuru": "temel",
        "not": "Aras Kurumsal API erişim bilgilerinizi (müşteri kodu, "
               "kullanıcı adı, parola) firmanızdan alın.",
        "alanlar": list(_ORTAK) + [
            _alan("kullanici", "Kullanıcı adı", zorunlu=True),
            _alan("parola", "Parola", zorunlu=True, gizli=True),
        ],
    },
    "mng": {
        "id": "mng",
        "ad": "MNG Kargo",
        "kimlikTuru": "temel",
        "not": "MNG Kargo iş ortağı API bilgilerinizi (kullanıcı adı, parola) "
               "firmanızdan alın; sorgu adresi dokümanda belirtilir.",
        "alanlar": list(_ORTAK) + [
            _alan("kullanici", "Kullanıcı adı", zorunlu=True),
            _alan("parola", "Parola", zorunlu=True, gizli=True),
        ],
    },
    "surat": {
        "id": "surat",
        "ad": "Surat Kargo",
        "kimlikTuru": "temel",
        "not": "Surat Kargo kurumsal API erişim bilgilerinizi firmanızdan "
               "alin; adres ve sorgu yolunu dokümana göre güncelleyin.",
        "alanlar": list(_ORTAK) + [
            _alan("kullanici", "Kullanıcı kodu", zorunlu=True),
            _alan("parola", "Şifre", zorunlu=True, gizli=True),
        ],
    },
    "sendeo": {
        "id": "sendeo",
        "ad": "Sendeo",
        "kimlikTuru": "jeton",
        "not": "Sendeo API anahtarınızı panelinizden alın; "
               "``Authorization: Bearer`` olarak gönderilir.",
        "alanlar": list(_ORTAK) + [
            _alan("apiKey", "API anahtarı", zorunlu=True, gizli=True),
        ],
    },
    "ptt": {
        "id": "ptt",
        "ad": "PTT Kargo",
        "kimlikTuru": "temel",
        "not": "PTT Kargo API erişim bilgilerinizi (kullanıcı, parola) "
               "firmanızdan alın.",
        "alanlar": list(_ORTAK) + [
            _alan("kullanici", "Kullanıcı adı", zorunlu=True),
            _alan("parola", "Parola", zorunlu=True, gizli=True),
        ],
    },
}

# Şifreli depolama ve form doğrulaması için entegrasyon altyapısını kullanırız.
entegrasyon.PLATFORMLAR.update(
    {ON_EK + s["id"]: {**s, "id": ON_EK + s["id"]} for s in FIRMALAR.values()}
)


def firma_listesi() -> list[dict]:
    """Arayüz için firma listesi (``platform`` alanı ``kargo_`` öneklidir)."""
    return [
        {**s, "id": ON_EK + s["id"], "platform": ON_EK + s["id"]}
        for s in FIRMALAR.values()
    ]


def _platform(firma: str) -> str:
    platform = str(firma or "").strip()
    if not platform.startswith(ON_EK):
        platform = ON_EK + platform
    if platform not in entegrasyon.PLATFORMLAR:
        raise ValueError(f"Bilinmeyen kargo firması: {firma}")
    return platform


def liste(conn: sqlite3.Connection) -> list[dict]:
    return [
        k for k in entegrasyon.liste(conn)
        if k["platform"].startswith(ON_EK)
    ]


def kaydet(conn: sqlite3.Connection, *, firma: str, ad: str,
           ayarlar: dict | None = None, kimlik: dict | None = None) -> dict:
    return entegrasyon.kaydet(
        conn, platform=_platform(firma), ad=ad, ayarlar=ayarlar,
        kimlik=kimlik,
    )


def sil(conn: sqlite3.Connection, kayit_id: int) -> dict:
    return entegrasyon.sil(conn, kayit_id)


def _kimlik_basliklar(spec: dict, ayarlar: dict, kimlik: dict) -> dict:
    if spec.get("kimlikTuru") == "jeton":
        anahtar = metin((kimlik or {}).get("apiKey"))
        if not anahtar:
            raise ValueError("API anahtarı girilmemiş.")
        return {"Authorization": "Bearer " + anahtar}
    kullanici = metin((ayarlar or {}).get("kullanici")) or \
        metin((kimlik or {}).get("kullanici"))
    parola = metin((kimlik or {}).get("parola"))
    if not kullanici or not parola:
        raise ValueError("Kullanıcı adı ve şifre girilmemiş.")
    tok = base64.b64encode(f"{kullanici}:{parola}".encode("utf-8"))
    return {"Authorization": "Basic " + tok.decode("ascii")}


def _adres(ayarlar: dict, takip: str) -> str:
    base = metin((ayarlar or {}).get("tabanAdres")).rstrip("/")
    if not base:
        raise ValueError("API adresi girilmemiş. Firmanızın size verdiği API "
                         "adresini yazın.")
    yol = metin((ayarlar or {}).get("sorguYolu"))
    if yol and not yol.startswith("/"):
        yol = "/" + yol
    url = base + yol
    if takip:
        param = metin((ayarlar or {}).get("takipAlani")) or "trackingNumber"
        ayrac = "&" if "?" in url else "?"
        url += f"{ayrac}{param}={urllib.parse.quote(str(takip), safe='')}"
    return url


def _istek(spec: dict, ayarlar: dict, kimlik: dict, *, takip: str = "",
           http=None):
    url = _adres(ayarlar, takip)
    basliklar = _kimlik_basliklar(spec, ayarlar, kimlik)
    fonk = http or istek
    return fonk(url, metot="GET", basliklar=basliklar)


def _govde_mesaji(veri, derinlik: int = 0) -> str:
    """Yanıttaki olası hata/açıklama metnini bulur."""
    if derinlik > 3:
        return ""
    anahtarlar = ("message", "error", "description", "detail", "aciklama",
                  "errormessage", "error_message", "mesaj")
    if isinstance(veri, dict):
        for k, v in veri.items():
            if str(k).lower() in anahtarlar and isinstance(v, str) and v.strip():
                return v.strip()[:200]
        for v in veri.values():
            bulunan = _govde_mesaji(v, derinlik + 1)
            if bulunan:
                return bulunan
    elif isinstance(veri, list):
        for v in veri[:5]:
            bulunan = _govde_mesaji(v, derinlik + 1)
            if bulunan:
                return bulunan
    return ""


def test(conn: sqlite3.Connection | None, kayit=None, *, firma: str = "",
         ayarlar: dict | None = None, kimlik: dict | None = None,
         http=None) -> dict:
    """Bağlantıyı (kayıtlı ya da taslak) gerçek bir istekle test eder."""
    if kayit is not None:
        ayarlar, kimlik, platform = entegrasyon.acilan(conn, kayit)
    else:
        platform = _platform(firma)
        ayarlar, kimlik = entegrasyon._bilesenler(
            platform, ayarlar or {}, kimlik or {}
        )
    spec = entegrasyon.PLATFORMLAR[platform]
    try:
        yanit = _istek(spec, ayarlar, kimlik,
                       takip=metin(ayarlar.get("denemeTakip")), http=http)
    except AgHatasi as e:
        sonuc = {
            "durum": "ag", "kod": None,
            "mesaj": "Ağ/SSL hatası — API'ye ulaşılamadı (erişim "
                     f"engellenmiş olabilir): {type(e).__name__}: {e}",
        }
    except ValueError as e:
        sonuc = {"durum": "hata", "kod": None, "mesaj": str(e)}
    else:
        ek = ""
        if not metin(ayarlar.get("sorguYolu")):
            ek = ("Sorgu yolu boş — yalnızca API adresi sorgulandı. Takip "
                  "için dokümandaki sorgu yolunu doldurun.")
        sonuc = test_sonucu(yanit.kod, ek)
        if sonuc["durum"] != "ok":
            mesaj = _govde_mesaji(yanit.veri)
            if mesaj:
                sonuc["mesaj"] += " Sunucu: " + mesaj
    if kayit is not None:
        _son_test_yaz(conn, int(kayit["id"]), sonuc)
    return sonuc


def _son_test_yaz(conn: sqlite3.Connection, kayit_id: int, sonuc: dict) -> None:
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


DURUM_ANAHTARLARI = (
    "status", "sondurum", "son_durum", "state", "durum", "shipmentstatus",
    "message", "aciklama", "description", "statusdescription",
    "durumaciklama", "result",
)

# Panel durumlarına eşleme (önce sorunlu/teslim, sonra ara durumlar).
ESLEME: tuple[tuple[tuple[str, ...], str], ...] = (
    (("teslim edilemedi", "edilemedi", "deliver failed", "undeliverable",
      "iptal", "iptal edildi", "hasar", "kayip", "kayboldu", "sorunlu",
      "failed", "cancel", "damaged", "lost", "return"), "sorunlu"),
    (("teslim edildi", "teslim", "delivered", "teslimat tamam"), "teslim"),
    (("subede", "sube", "dagitima cikti", "dagitim", "out for delivery",
      "sube teslim"), "subede"),
    (("hazirlan", "olusturuldu", "created", "beklemede",
      "kayit alindi", "pending", "hazir"), "hazir"),
    (("yola cikti", "yolda", "kargoya verildi", "gonderi alindi",
      "transit", "shipped", "picked up", "gonderildi", "yurti",
      "aktarma"), "yolda"),
)

_CEVIR = str.maketrans({
    "ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u",
    "Ç": "c", "Ğ": "g", "İ": "i", "Ö": "o", "Ş": "s", "Ü": "u",
})


def _katla(s: str) -> str:
    return s.translate(_CEVIR).lower()


def durum_eslestir(ham) -> str | None:
    """Dönen durum metnini panel durumuna çevirir; tanınmazsa ``None``."""
    s = _katla(metin(ham))
    if not s:
        return None
    for anahtarlar, durum in ESLEME:
        for a in anahtarlar:
            if a in s:
                return durum
    return None


DURUM_METNI_ANAHTARLARI = {
    "status", "sondurum", "son_durum", "state", "durum", "shipmentstatus",
    "message", "aciklama", "description", "statusdescription",
    "durumaciklama", "result",
}


def _durum_metni(veri, derinlik: int = 0) -> str:
    if derinlik > 4:
        return ""
    if isinstance(veri, dict):
        for k, v in veri.items():
            if str(k).lower() in DURUM_METNI_ANAHTARLARI and isinstance(v, str):
                if v.strip() and not v.strip().isdigit():
                    return v.strip()
        for v in veri.values():
            bulunan = _durum_metni(v, derinlik + 1)
            if bulunan:
                return bulunan
    elif isinstance(veri, list):
        for v in veri[:5]:
            bulunan = _durum_metni(v, derinlik + 1)
            if bulunan:
                return bulunan
    return ""


def _baglanti_bul(conn: sqlite3.Connection, kargo_firmasi: str):
    """Paneldeki firma adına göre kayıtlı API bağlantısını bulur."""
    ad = metin(kargo_firmasi)
    for spec in FIRMALAR.values():
        if spec["ad"] == ad:
            platform = ON_EK + spec["id"]
            break
    else:
        return None
    satir = conn.execute(
        "SELECT * FROM entegrasyonlar WHERE platform=? AND aktif=1 "
        "ORDER BY id DESC LIMIT 1",
        (platform,),
    ).fetchone()
    return satir


def _al(kayit, anahtar: str, varsayilan=None):
    """Sözlük ya da ``sqlite3.Row`` üzerinden alan okur."""
    if kayit is None:
        return varsayilan
    if isinstance(kayit, dict):
        return kayit.get(anahtar, varsayilan)
    try:
        return kayit[anahtar]
    except (IndexError, KeyError, TypeError):
        return varsayilan


def durum_sorgula(conn: sqlite3.Connection, gonderi, *, kayit=None,
                  http=None) -> dict:
    """Gönderinin takip numarasını firmasının API'sine sorar."""
    takip = metin(_al(gonderi, "takip_no"))
    if not takip:
        raise ValueError("Bu gönderinin takip numarası yok.")
    if kayit is None:
        kayit = _baglanti_bul(conn, metin(_al(gonderi, "kargo_firmasi")))
        if kayit is None:
            raise ValueError(
                f"{metin(_al(gonderi, 'kargo_firmasi'))} için kayıtlı API "
                "bağlantısı yok — Kargo API bağlantısını kaydedin."
            )
    ayarlar, kimlik, platform = entegrasyon.acilan(conn, kayit)
    spec = entegrasyon.PLATFORMLAR[platform]
    try:
        yanit = _istek(spec, ayarlar, kimlik, takip=takip, http=http)
    except AgHatasi as e:
        return {
            "durum": "ag", "kod": None,
            "mesaj": "Ağ/SSL hatası — kargo API'sine ulaşılamadı: "
                     f"{type(e).__name__}: {e}",
            "ham": "", "son_durum": None,
        }
    except ValueError as e:
        return {"durum": "hata", "kod": None, "mesaj": str(e),
                "ham": "", "son_durum": None}
    ham = _durum_metni(yanit.veri)
    if not ham and isinstance(yanit.veri, (dict, list)):
        ham = _govde_mesaji(yanit.veri)
    if not 200 <= yanit.kod < 300:
        ek = _govde_mesaji(yanit.veri)
        return {
            "durum": "hata", "kod": yanit.kod, "ham": ham,
            "son_durum": None,
            "mesaj": test_sonucu(yanit.kod, ek)["mesaj"],
        }
    yeni = durum_eslestir(ham)
    return {
        "durum": "ok", "kod": yanit.kod, "ham": ham, "son_durum": yeni,
        "mesaj": (
            f"Durum: {ham}" if ham else
            "Yanıt alındı fakat içinde durum metni bulunamadı."
        ) + ("" if yeni else " Panel durumu değiştirilmedi."),
    }


def senkron(conn: sqlite3.Connection, *, http=None,
            sinir: int = MAK_SINIR) -> dict:
    """Takip numarası olan gönderilerin durumlarını toplu günceller."""
    satirlar = conn.execute(
        "SELECT * FROM gonderiler WHERE TRIM(takip_no) != '' "
        "ORDER BY gonderim_tarihi DESC, id DESC LIMIT ?",
        (max(1, int(sinir)),),
    ).fetchall()
    baglantilar = {k["platform"]: k for k in liste(conn)}
    sorgulanan = guncel = hatali = 0
    notlar: list[str] = []
    for g in satirlar:
        platform = ""
        for spec in FIRMALAR.values():
            if spec["ad"] == metin(g["kargo_firmasi"]):
                platform = ON_EK + spec["id"]
        if not platform or platform not in baglantilar:
            continue
        sorgulanan += 1
        son = durum_sorgula(
            conn, g, kayit=entegrasyon.satir(conn, baglantilar[platform]["id"]),
            http=http,
        )
        if son["durum"] != "ok":
            hatali += 1
            notlar.append(f"#{g['id']} {g['takip_no']}: {son['mesaj']}")
            continue
        yeni = son.get("son_durum")
        if yeni and yeni != g["son_durum"]:
            kargo.durum_degistir(conn, int(g["id"]), yeni)
            guncel += 1
    if not sorgulanan:
        return {
            "durum": "uyari",
            "mesaj": "Sorgulanacak gönderi yok — önce takip numaralı gönderi "
                     "ekleyin ve kargo API bağlantısı kaydedin.",
            "sorgulanan": 0, "guncel": 0, "hatali": 0, "notlar": [],
        }
    mesaj = f"{sorgulanan} gönderi sorgulandı, {guncel} durum güncellendi."
    if hatali:
        mesaj += f" {hatali} gönderide hata var."
    return {
        "durum": "uyari" if hatali else "ok",
        "mesaj": mesaj,
        "sorgulanan": sorgulanan,
        "guncel": guncel,
        "hatali": hatali,
        "notlar": notlar[:10],
    }
