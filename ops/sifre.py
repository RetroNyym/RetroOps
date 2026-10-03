"""API kimlik bilgilerinin yerel şifrelenmesi.

Anahtar ``data/.anahtar`` dosyasında tutulur. ``cryptography`` (Fernet)
kuruluysa onu kullanır; kurulu değilse saf stdlib ile PBKDF2 tabanlı
akış şifrelemesi + HMAC doğrulama çalışır. Her iki durumda da değerler
veritabanında düz metin olarak saklanmaz ve API asla geri göndermez.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from pathlib import Path

from .db import varsayilan_yol

_FERNET: object | None = None
_FERNET_DENE = False
_TUR = 120_000


def anahtar_yolu() -> Path:
    return varsayilan_yol().parent / ".anahtar"


def _satir(ad: str) -> bytes:
    yol = anahtar_yolu()
    yol.parent.mkdir(parents=True, exist_ok=True)
    satirlar: dict[bytes, bytes] = {}
    if yol.exists():
        for satir in yol.read_bytes().splitlines():
            if b"=" in satir:
                anahtar, deger = satir.split(b"=", 1)
                satirlar[anahtar] = deger
    if ad not in satirlar:
        satirlar[ad] = base64.b64encode(secrets.token_bytes(32))
        icerik = b"".join(f"{k.decode()}=".encode() + v + b"\n"
                          for k, v in satirlar.items())
        yol.write_bytes(icerik)
        try:
            os.chmod(yol, 0o600)
        except OSError:
            pass
    return base64.b64decode(satirlar[ad])


def _fernet() -> object | None:
    global _FERNET, _FERNET_DENE
    if not _FERNET_DENE:
        _FERNET_DENE = True
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            return None
        try:
            _FERNET = Fernet(_satir(b"fernet"))
        except Exception:
            _FERNET = None
    return _FERNET


def _akis(uzunluk: int, tuz: bytes) -> bytes:
    anahtar = _satir(b"akis")
    cikti = b""
    sayac = 0
    while len(cikti) < uzunluk:
        cikti += hashlib.pbkdf2_hmac(
            "sha256", anahtar, tuz + sayac.to_bytes(4, "big"), _TUR, dklen=32
        )
        sayac += 1
    return cikti[:uzunluk]


def sifrele(metin: str) -> str:
    """Düz metni şifreli dizeye çevirir."""
    ham = str(metin).encode("utf-8")
    f = _fernet()
    if f is not None:
        return "f:" + f.encrypt(ham).decode("ascii")
    tuz = secrets.token_bytes(16)
    cikti = bytes(a ^ b for a, b in zip(ham, _akis(len(ham), tuz)))
    etiket = hmac.new(_satir(b"akis"), tuz + cikti, hashlib.sha256).hexdigest()
    govde = base64.b64encode(tuz + cikti).decode("ascii")
    return f"s:{govde}:{etiket}"


def coz(metin: str) -> str:
    """``sifrele`` ile üretilen dizeyi geri açar."""
    ham = str(metin)
    if ham.startswith("f:"):
        f = _fernet()
        if f is None:
            raise ValueError(
                "Kayıt Fernet ile şifrelenmiş ama kütüphane kurulu değil."
            )
        return f.decrypt(ham[2:].encode("ascii")).decode("utf-8")
    if ham.startswith("s:"):
        govde, etiket = ham[2:].rsplit(":", 1)
        blok = base64.b64decode(govde)
        tuz, sifreli = blok[:16], blok[16:]
        beklenen = hmac.new(
            _satir(b"akis"), tuz + sifreli, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(beklenen, etiket):
            raise ValueError(
                "Şifreleme doğrulaması başarısız (anahtar dosyası değişmiş "
                "olabilir)."
            )
        akis = _akis(len(sifreli), tuz)
        return bytes(a ^ b for a, b in zip(sifreli, akis)).decode("utf-8")
    raise ValueError("Şifreleme ön eki tanınmadı (kayıt şifreli değil).")
