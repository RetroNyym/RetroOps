"""PyInstaller giriş noktası: paneli başlatır, tarayıcıyı açar.

Çift tıklandığında:
  1. Program zaten çalışıyorsa sadece tarayıcıyı açar.
  2. Değilse 8780 portunda başlatır (doluysa sıradaki portu dener).
Başlatma sorunları ``data/hata.log`` dosyasına yazılır.
"""

import json
import sys
import urllib.error
import urllib.request
import webbrowser

from ops.db import kok_dizin
from ops.web import main

PORTLAR = (8780, 8781, 8782, 8783, 8784)


def _kaydet(metin: str) -> None:
    try:
        hedef = kok_dizin() / "data" / "hata.log"
        hedef.parent.mkdir(parents=True, exist_ok=True)
        with hedef.open("a", encoding="utf-8") as f:
            f.write(metin.rstrip() + "\n")
    except OSError:
        pass


def biz_mi(port: int) -> bool:
    """O portta RetroOps mu çalışıyor? (başka program olabilir)"""
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/api/meta", timeout=2
        ) as yanit:
            veri = json.loads(yanit.read().decode("utf-8"))
        return isinstance(veri, dict) and "surum" in veri and "lisans" in veri
    except (urllib.error.URLError, OSError, ValueError):
        return False


def hizli_basla() -> bool:
    for port in PORTLAR:
        if biz_mi(port):
            webbrowser.open(f"http://127.0.0.1:{port}")
            return True
    return False


if __name__ == "__main__":
    if hizli_basla():
        sys.exit(0)
    son_hata = None
    for port in PORTLAR:
        try:
            main(port, tarayici_ac=True)
            sys.exit(0)
        except OSError as e:
            son_hata = e
            continue
        except Exception:
            import traceback
            _kaydet(traceback.format_exc())
            raise SystemExit(1)
    _kaydet(f"Uygun port bulunamadı ({son_hata}).")
    raise SystemExit(1)
