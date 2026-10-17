"""Uzaktan güncelleme kontrolü: public GitHub sürüm dosyası.

``https://raw.githubusercontent.com/RetroNyym/RetroOps/main/surum.json``
adresindeki dosya ile yerel sürüm karşılaştırılır:

    {"surum": "1.1.0", "indirme": "", "not": "..."}

Ağ hatası hiçbir zaman hata vermez; panel sessizce güncelleme bandını
göstermez. Sonuç 6 saat boyunca bellekte önbelleğe alınır. Testler için
``OPS_GUNCELLEME_DOSYA`` ortam değişkeni URL yerine yerel dosyayı gösterir
(``OPS_GUNCELLEME=yok`` ile tamamen kapatılır).
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from . import __surum__

SURUM_URL = (
    "https://raw.githubusercontent.com/RetroNyym/RetroOps/main/"
    "surum.json"
)
ONBELLEK_SURE = 6 * 3600  # saniye
_onbellek: dict = {}


def surum_sozluk(surum: str) -> tuple:
    """``"1.10.2"`` → ``(1, 10, 2)``; sayısal olmayan parçalar 0 sayılır."""
    parcalar = []
    for p in str(surum or "").strip().split("."):
        parcalar.append(int(p) if p.isdigit() else 0)
    return tuple(parcalar or [0])


def _kaynak() -> tuple[str, str]:
    """``(kaynak, tür)`` — tür: ``url`` / ``dosya`` / ``kapali``."""
    if os.environ.get("OPS_GUNCELLEME", "").lower() == "yok":
        return "", "kapali"
    dosya = os.environ.get("OPS_GUNCELLEME_DOSYA", "")
    if dosya:
        return dosya, "dosya"
    return SURUM_URL, "url"


def _oku(kaynak: str, tur: str) -> dict:
    if tur == "dosya":
        metin = Path(kaynak).read_text(encoding="utf-8")
    else:
        istemci = urllib.request.Request(
            kaynak, headers={"User-Agent": "RetroOps/" + __surum__}
        )
        with urllib.request.urlopen(istemci, timeout=8) as yanit:
            metin = yanit.read().decode("utf-8", "replace")
    veri = json.loads(metin)
    if not isinstance(veri, dict):
        raise ValueError("Sürüm dosyası JSON nesnesi değil.")
    return veri


def kontrol(http_oku=None) -> dict:
    """Yeni sürüm var mı kontrol eder; asla hata fırlatmaz."""
    kaynak, tur = _kaynak()
    mevcut = __surum__
    temel = {"mevcut": mevcut, "son": "", "yeni_var": False,
             "indirme": "", "not": "", "hata": ""}
    if tur == "kapali":
        temel["hata"] = "Güncelleme kontrolü kapalı."
        return temel
    su = time.time()
    kayit = _onbellek.get(kaynak)
    if kayit and su - kayit[0] < ONBELLEK_SURE:
        return dict(kayit[1])
    sonuc = dict(temel)
    try:
        if http_oku is not None:
            veri = http_oku(kaynak)
        else:
            veri = _oku(kaynak, tur)
        son = str(veri.get("surum") or "").strip()
        if not son:
            raise ValueError("Sürüm dosyasında 'surum' alanı yok.")
        sonuc["son"] = son
        sonuc["indirme"] = str(veri.get("indirme") or "")
        sonuc["not"] = str(veri.get("not") or "")
        sonuc["yeni_var"] = surum_sozluk(son) > surum_sozluk(mevcut)
    except (OSError, ValueError, TypeError, json.JSONDecodeError,
            urllib.error.URLError) as e:
        sonuc["hata"] = (f"Güncelleme kontrol edilemedi: "
                         f"{type(e).__name__}: {e}")
    except Exception as e:  # ağ/SSL tuhaflıkları
        sonuc["hata"] = (f"Güncelleme kontrol edilemedi: "
                         f"{type(e).__name__}: {e}")
    _onbellek[kaynak] = (su, sonuc)
    return dict(sonuc)


def onbellek_temizle() -> None:
    """Testler için önbelleği boşaltır."""
    _onbellek.clear()
