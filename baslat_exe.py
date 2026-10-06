"""PyInstaller giriş noktası: RetroOps'u masaüstü uygulaması olarak açar.

Çift tıklandığında:
  1. Sunucu zaten çalışıyorsa yalnızca yeni bir RetroOps penceresi açılır.
  2. Değilse sunucu arka planda başlatılır ve yerel pencere açılır;
     pencere kapatıldığında süreç de sonlanır (sunucu durur).
Pencere açılamazsa (WebView2 yoksa, paketleme hatası vb.) varsayılan
tarayıcıya düşülür ve sunucu o sekmenin arkasında çalışmaya devam eder.
Sorunlar ``data/hata.log`` dosyasına yazılır.
"""

import json
import sys
import threading
import traceback
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

from ops.db import kok_dizin
from ops.web import arka_planda, main as web_main

PORTLAR = (8780, 8781, 8782, 8783, 8784)
BASLIK = "RetroOps - E-Ticaret Operasyon Paneli"
PENCERE = (1440, 900)
MIN_PENCERE = (1024, 640)
ARKA_RENK = "#0b1020"


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


def calisan_port() -> int | None:
    for port in PORTLAR:
        if biz_mi(port):
            return port
    return None


def ikon_yolu() -> str | None:
    adaylar = [Path(getattr(sys, "_MEIPASS", "")) / "retroops.ico",
               kok_dizin() / "retroops.ico",
               Path(__file__).resolve().parent / "retroops.ico"]
    for yol in adaylar:
        if yol.is_file():
            return str(yol)
    return None


def pencereye_basla(adres: str) -> bool:
    """Yerel pencereyi açar. True = pencere açıldı ve kapanması beklenir."""
    try:
        import webview
    except Exception:
        _kaydet("pywebview açılamadı:\n" + traceback.format_exc())
        return False
    try:
        webview.create_window(
            BASLIK, adres,
            width=PENCERE[0], height=PENCERE[1],
            min_size=MIN_PENCERE,
            easy_drag=False,
            background_color=ARKA_RENK,
            text_select=True,
            zoomable=True,
        )
        webview.start(http_server=False, icon=ikon_yolu())
        return True
    except Exception:
        _kaydet("Masaüstü penceresi açılamadı:\n" + traceback.format_exc())
        return False


def tarayicida_ac(adres: str) -> None:
    threading.Timer(1.0, lambda: webbrowser.open(adres)).start()


if __name__ == "__main__":
    zorla_tarayici = "--tarayici" in sys.argv
    port = None if zorla_tarayici else calisan_port()

    if port is not None:
        if not pencereye_basla(f"http://127.0.0.1:{port}"):
            webbrowser.open(f"http://127.0.0.1:{port}")
        sys.exit(0)

    if zorla_tarayici:
        for p in PORTLAR:
            try:
                web_main(p, tarayici_ac=True)
                sys.exit(0)
            except OSError as e:
                son_hata = e
                continue
            except Exception:
                _kaydet(traceback.format_exc())
                raise SystemExit(1)
        _kaydet(f"Uygun port bulunamadı ({son_hata}).")
        raise SystemExit(1)

    son_hata = None
    for p in PORTLAR:
        try:
            srv, adres = arka_planda(p)
        except OSError as e:
            son_hata = e
            continue
        except Exception:
            _kaydet(traceback.format_exc())
            raise SystemExit(1)
        if pencereye_basla(adres):
            sys.exit(0)
        # Pencere açılamadı → sunucu tarayıcıda çalışsın (eski davranış)
        tarayicida_ac(adres)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            srv.server_close()
        sys.exit(0)

    _kaydet(f"Uygun port bulunamadı ({son_hata}).")
    raise SystemExit(1)
