"""Lisans: makineye bağlı anahtar + 14 günlük deneme (saf stdlib).

Anahtar biçimi: ``RETROOPS-XXXXX-…`` (HMAC-SHA256 imzalı gövde + gövdenin
base64url kodlanmış hali). Anahtar yalnız üretildiği bilgisayarda geçerlidir.

Durum ``data/.lisans`` dosyasında saklanır:
``{"ilk": "YYYY-AA-GG", "anahtar": "…" | null}``
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import platform
import uuid
from datetime import date, timedelta
from pathlib import Path

from .db import varsayilan_yol

# Satıcı sırrı — anahtar üretimi (araclar/lisans_uret.py) da bunu kullanır.
SIR = b"retroops-lisans-v1-2026-satici-siri"
DENEME_GUN = 14
ON_EK = "RETROOPS"


def lisans_yolu() -> Path:
    return varsayilan_yol().parent / ".lisans"


def makine_id() -> str:
    """Bu bilgisayara özgü, kısa ve kararlı kimlik."""
    ham = "|".join([
        str(uuid.getnode()),
        platform.node(),
        platform.system(),
        str(os.environ.get("PROCESSOR_IDENTIFIER", "")),
        str(Path.home()),
    ])
    return hashlib.sha256(ham.encode("utf-8")).hexdigest()[:16]


def _imza(metin: str) -> str:
    return hmac.new(SIR, metin.encode("utf-8"), hashlib.sha256).hexdigest()[:32]


def anahtar_uret(bit_tarih: str, makine: str | None = None,
                 tur: str = "yillik") -> str:
    """Satıcı için anahtar üretir: ``anahtar_uret("2027-10-05")``."""
    makine = makine or makine_id()
    date.fromisoformat(bit_tarih)
    govde = f"v1|{makine}|{bit_tarih}|{tur}"
    ham = f"{govde}|{_imza(govde)}"
    token = base64.urlsafe_b64encode(ham.encode("utf-8")).decode("ascii")
    token = token.rstrip("=")
    parcalar = [token[i:i + 5] for i in range(0, len(token), 5)]
    return "-".join([ON_EK, *parcalar])


def anahtar_coz(anahtar: str) -> dict | None:
    """Geçerliyse gövdeyi, değilse ``None`` döndürür."""
    try:
        parcalar = str(anahtar or "").strip().split("-")
        if not parcalar or parcalar[0] != ON_EK or len(parcalar) < 3:
            return None
        token = "".join(parcalar[1:])
        token += "=" * (-len(token) % 4)
        ham = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
        govde, imza = ham.rsplit("|", 1)
        if not hmac.compare_digest(imza, _imza(govde)):
            return None
        _, makine, bitis, tur = govde.split("|")
        date.fromisoformat(bitis)
        return {"makine": makine, "bitis": bitis, "tur": tur}
    except Exception:
        return None


def _kayit_oku() -> dict:
    yol = lisans_yolu()
    if yol.exists():
        try:
            veri = json.loads(yol.read_text(encoding="utf-8"))
            if isinstance(veri, dict) and veri.get("ilk"):
                date.fromisoformat(str(veri["ilk"]))
                return veri
        except (OSError, ValueError, TypeError):
            pass
    kayit = {"ilk": date.today().isoformat(), "anahtar": None}
    _kayit_yaz(kayit)
    return kayit


def _kayit_yaz(kayit: dict) -> None:
    yol = lisans_yolu()
    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_text(json.dumps(kayit, ensure_ascii=False), encoding="utf-8")


def durum() -> dict:
    """``lisansli`` / ``deneme`` / ``suresi_doldu`` durumu döndürür."""
    kayit = _kayit_oku()
    makine = makine_id()
    anahtar = kayit.get("anahtar")
    if anahtar:
        coz = anahtar_coz(anahtar)
        if coz and coz["makine"] == makine:
            bitis = date.fromisoformat(coz["bitis"])
            kalan = (bitis - date.today()).days
            if kalan >= 0:
                return {"durum": "lisansli", "kalan_gun": kalan,
                        "bitis": coz["bitis"], "makine": makine,
                        "tur": coz.get("tur", ""),
                        "mesaj": f"Lisans geçerli (bitiş {coz['bitis']})."}
            return {"durum": "suresi_doldu", "kalan_gun": 0,
                    "bitis": coz["bitis"], "makine": makine, "tur": coz.get("tur", ""),
                    "mesaj": f"Lisans süresi doldu ({coz['bitis']})."}
        # anahtar bu makineye ait değil ya da bozuk → kaydı temizle
        kayit["anahtar"] = None
        _kayit_yaz(kayit)
    ilk = date.fromisoformat(kayit["ilk"])
    deneme_bitis = ilk + timedelta(days=DENEME_GUN)
    kalan = (deneme_bitis - date.today()).days
    if kalan > 0:
        return {"durum": "deneme", "kalan_gun": kalan,
                "bitis": deneme_bitis.isoformat(), "makine": makine, "tur": "",
                "mesaj": f"Deneme süresi: {kalan} gün kaldı."}
    return {"durum": "suresi_doldu", "kalan_gun": 0,
            "bitis": deneme_bitis.isoformat(), "makine": makine, "tur": "",
            "mesaj": f"Deneme süresi doldu ({deneme_bitis.isoformat()})."}


def etkinlestir(anahtar: str) -> dict:
    coz = anahtar_coz(anahtar)
    if not coz:
        raise ValueError("Lisans anahtarı geçersiz. Anahtarı kontrol edip "
                         "tekrar girin.")
    if coz["makine"] != makine_id():
        raise ValueError("Bu anahtar başka bir bilgisayara kayıtlı. "
                         "Makine kimliği: " + makine_id())
    if date.fromisoformat(coz["bitis"]) < date.today():
        raise ValueError("Lisans anahtarının süresi geçmiş: " + coz["bitis"])
    kayit = _kayit_oku()
    kayit["anahtar"] = anahtar.strip()
    _kayit_yaz(kayit)
    return durum()


def kilitli() -> bool:
    return durum()["durum"] == "suresi_doldu"
