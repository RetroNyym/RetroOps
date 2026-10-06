"""SMS entegrasyonu: satıcı koduyla etkinleşen modül + Netgsm gönderimi.

Etkinleştirme kodu lisans anahtarındaki gibi HMAC-SHA256 imzalıdır ve yalnız
kodu üreten bilgisayarda açılır:

    python araclar/sms_kodu_uret.py               # bu bilgisayar için
    python araclar/sms_kodu_uret.py a1b2c3d4e5f6   # müşteri makinesi için

Müşterinin makine kimliği Panel → SMS sekmesinde görünür. Kilitliyken
gönderim yapılamaz; ayarlar ``data/.sms`` dosyasında tutulur, şifre
``sifre`` modülüyle şifrelenir ve API'ye geri gönderilmez. Gönderimler
``sms_gonderim`` tablosuna yazılır.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import sqlite3
from datetime import date

from . import sifre
from .adapters.temel import AgHatasi, istek, metin
from .db import varsayilan_yol
from .lisans import makine_id

SIR = b"retroops-sms-v1-2026-satici-siri"
ON_EK = "SMS"
NETGSM_ADRES = "https://api.netgsm.com.tr/rest/v1/sendSms"
VARSAYILAN_BASLIK = "BILGI"


def sms_yolu():
    return varsayilan_yol().parent / ".sms"


def _imza(govde: str) -> str:
    return hmac.new(SIR, govde.encode("utf-8"), hashlib.sha256).hexdigest()[:32]


def kod_uret(makine: str | None = None) -> str:
    """Satıcı için SMS entegrasyon kodu üretir."""
    makine = makine or makine_id()
    govde = f"v1|{makine}|{date.today().isoformat()}"
    ham = f"{govde}|{_imza(govde)}"
    token = base64.urlsafe_b64encode(ham.encode("utf-8")).decode("ascii")
    token = token.rstrip("=")
    parcalar = [token[i:i + 5] for i in range(0, len(token), 5)]
    return "-".join([ON_EK, *parcalar])


def kod_coz(kod: str) -> dict | None:
    """Geçerliyse gövdeyi, değilse ``None`` döndürür."""
    try:
        parcalar = str(kod or "").strip().split("-")
        if not parcalar or parcalar[0] != ON_EK or len(parcalar) < 3:
            return None
        token = "".join(parcalar[1:])
        token += "=" * (-len(token) % 4)
        ham = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
        govde, imza = ham.rsplit("|", 1)
        if not hmac.compare_digest(imza, _imza(govde)):
            return None
        _, makine, tarih = govde.split("|")
        date.fromisoformat(tarih)
        return {"makine": makine, "tarih": tarih}
    except Exception:
        return None


def _maskele(kod: str) -> str:
    return kod if len(kod) <= 16 else kod[:13] + "…"


def _kayit_oku() -> dict:
    yol = sms_yolu()
    if yol.exists():
        try:
            veri = json.loads(yol.read_text(encoding="utf-8"))
            if isinstance(veri, dict):
                veri.setdefault("kod", None)
                veri.setdefault("ayarlar", {})
                return veri
        except (OSError, ValueError, TypeError):
            pass
    return {"kod": None, "ayarlar": {}}


def _kayit_yaz(kayit: dict) -> None:
    yol = sms_yolu()
    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_text(json.dumps(kayit, ensure_ascii=False), encoding="utf-8")


def durum() -> dict:
    """``etkin`` durumu, makine kimliğini ve maskeli kodu döndürür."""
    kayit = _kayit_oku()
    kod = kayit.get("kod")
    coz = kod_coz(kod) if kod else None
    makine = makine_id()
    if coz:
        if coz["makine"] == makine:
            return {"etkin": True, "makine": makine, "kod": _maskele(str(kod)),
                    "tarih": coz["tarih"],
                    "mesaj": "SMS entegrasyonu etkin."}
        kayit["kod"] = None
        _kayit_yaz(kayit)
    return {"etkin": False, "makine": makine, "kod": "", "tarih": "",
            "mesaj": "SMS entegrasyonu kilitli — entegrasyon kodu girin."}


def etkinlestir(kod: str) -> dict:
    coz = kod_coz(kod)
    if not coz:
        raise ValueError("SMS entegrasyon kodu geçersiz. Kodu kontrol edip "
                         "tekrar girin.")
    if coz["makine"] != makine_id():
        raise ValueError("Bu kod başka bir bilgisayara kayıtlı. Makine "
                         "kimliği: " + makine_id())
    kayit = _kayit_oku()
    kayit["kod"] = str(kod).strip()
    _kayit_yaz(kayit)
    return durum()


def kaldir() -> dict:
    """Etkinleştirme kodunu siler (gönderici ayarları kalır)."""
    kayit = _kayit_oku()
    kayit["kod"] = None
    _kayit_yaz(kayit)
    return durum()


def _ayar_ham() -> dict | None:
    """Şifreli dahil tüm ayarları döndürür; ayar yoksa ``None``."""
    a = (_kayit_oku().get("ayarlar") or {})
    kullanici = metin(a.get("kullanici"))
    if not kullanici:
        return None
    parola = ""
    if a.get("parola"):
        try:
            parola = sifre.coz(str(a["parola"]))
        except ValueError:
            parola = ""
    return {
        "apiAdres": metin(a.get("apiAdres")) or NETGSM_ADRES,
        "baslik": metin(a.get("baslik")) or VARSAYILAN_BASLIK,
        "kullanici": kullanici,
        "parola": parola,
    }


def ayar_oku() -> dict:
    """Arayüz için ayarlar (şifre asla dönmez)."""
    ham = _ayar_ham()
    return {
        "saglayici": "Netgsm",
        "apiAdres": (ham or {}).get("apiAdres") or NETGSM_ADRES,
        "baslik": (ham or {}).get("baslik") or VARSAYILAN_BASLIK,
        "kullanici": (ham or {}).get("kullanici") or "",
        "parola_var": bool(ham and ham.get("parola")),
    }


def ayar_yaz(girdi: dict) -> dict:
    girdi = girdi or {}
    kullanici = metin(girdi.get("kullanici"))
    if not kullanici:
        raise ValueError("Kullanıcı kodu zorunlu (Netgsm SMS kullanıcı kodu).")
    eski = _kayit_oku().get("ayarlar") or {}
    parola = metin(girdi.get("parola"))
    if not parola and eski.get("parola"):
        try:
            parola = sifre.coz(str(eski["parola"]))
        except ValueError:
            parola = ""
    if not parola:
        raise ValueError("SMS şifresi zorunlu.")
    kayit = _kayit_oku()
    kayit["ayarlar"] = {
        "saglayici": "Netgsm",
        "apiAdres": metin(girdi.get("apiAdres")) or NETGSM_ADRES,
        "baslik": metin(girdi.get("baslik")) or VARSAYILAN_BASLIK,
        "kullanici": kullanici,
        "parola": sifre.sifrele(parola),
    }
    _kayit_yaz(kayit)
    return ayar_oku()


def tel_no(deger) -> str:
    """``0532 123 45 67`` biçimlerini ``905321234567``ya çevirir."""
    ham = re.sub(r"\D", "", metin(deger))
    if ham.startswith("90") and len(ham) == 12:
        ham = ham[2:]
    elif ham.startswith("0") and len(ham) == 11:
        ham = ham[1:]
    if len(ham) != 10 or not ham.startswith("5"):
        raise ValueError("Geçersiz telefon numarası (örn. 0532 123 45 67).")
    return ham


def _yorumla(kod: int, veri) -> tuple[str, str]:
    """Netgsm yanıtını ``ok``/``hata`` ve kullanıcı mesajına çevirir."""
    v = veri if isinstance(veri, dict) else {}
    durum_ = v.get("status") if isinstance(v.get("status"), dict) else {}
    servis_kodu = durum_.get("code", v.get("code"))
    aciklama = metin(
        durum_.get("description") or v.get("description") or v.get("message")
    )
    if not 200 <= kod < 300:
        return "hata", f"HTTP {kod}" + (
            f" — {aciklama}" if aciklama else " — SMS sunucusu hata döndürdü."
        )
    if servis_kodu is not None and str(servis_kodu) not in ("200", "202"):
        return "hata", aciklama or f"Servis hatası: kod {servis_kodu}"
    return "ok", aciklama or f"Mesaj operatöre iletildi (HTTP {kod})."


def _gecmis_yaz(conn: sqlite3.Connection, alici: str, mesaj: str,
                baslik: str, durum_: str, http_kod: int | None,
                sonuc: str) -> None:
    conn.execute(
        "INSERT INTO sms_gonderim (alici, mesaj, baslik, durum, http_kod, "
        "sonuc) VALUES (?,?,?,?,?,?)",
        (alici, mesaj, baslik, durum_, http_kod, sonuc),
    )
    conn.commit()


def gonder(conn: sqlite3.Connection, alici: str, mesaj: str, *,
           http=None) -> dict:
    """SMS gönderir ve geçmişe yazar; ``http`` sahte istemciyle test edilir."""
    if not durum()["etkin"]:
        raise ValueError("SMS entegrasyonu kilitli. Satın alımda size verilen "
                         "entegrasyon kodunu SMS sekmesinden girin.")
    no = tel_no(alici)
    metin_ = metin(mesaj)
    if not metin_:
        raise ValueError("Mesaj metni boş olamaz.")
    if len(metin_) > 1060:
        raise ValueError("Mesaj çok uzun (en fazla 1060 karakter).")
    ayar = _ayar_ham()
    if not ayar or not ayar["parola"]:
        raise ValueError("SMS gönderici ayarları girilmemiş. SMS sekmesinden "
                         "kullanıcı kodu ve şifrenizi kaydedin.")
    kimlik = base64.b64encode(
        f"{ayar['kullanici']}:{ayar['parola']}".encode("utf-8")
    ).decode("ascii")
    govde = {
        "messages": [{
            "msgId": "1",
            "text": metin_,
            "receipents": [{"no": "90" + no}],
        }],
        "sender": ayar["baslik"],
        "encoding": "UTF-8",
    }
    fonk = http or istek
    try:
        yanit = fonk(
            ayar["apiAdres"], metot="POST", govde=govde, bicim="json",
            basliklar={"Authorization": "Basic " + kimlik},
        )
    except AgHatasi as e:
        mesaj_ = ("Ağ/SSL hatası — SMS sunucusuna ulaşılamadı (erişim "
                  f"engellenmiş olabilir): {type(e).__name__}: {e}")
        _gecmis_yaz(conn, no, metin_, ayar["baslik"], "hata", None, mesaj_)
        return {"durum": "ag", "kod": None, "mesaj": mesaj_, "alici": no}
    durum_, aciklama = _yorumla(yanit.kod, yanit.veri)
    _gecmis_yaz(conn, no, metin_, ayar["baslik"], durum_, yanit.kod, aciklama)
    return {"durum": durum_, "kod": yanit.kod, "mesaj": aciklama,
            "alici": no}


def gecmis(conn: sqlite3.Connection, sinir: int = 50) -> list[dict]:
    satirlar = conn.execute(
        "SELECT * FROM sms_gonderim ORDER BY id DESC LIMIT ?",
        (int(sinir),),
    ).fetchall()
    return [dict(s) for s in satirlar]
