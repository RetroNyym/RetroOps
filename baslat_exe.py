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
import subprocess
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
ARKA_RENK = "#070b14"
EDGE_YOLLARI = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)


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


def edge_uygulama(adres: str) -> bool:
    """Paneli Edge'in uygulama penceresinde (adres çubuksuz) açar.

    pywebview/.NET çalışmıyorsa da program ``RetroOps`` penceresi gibi açılmış
    olur; kullanıcı hiçbir fark görmez. True = pencere açıldı.
    """
    for yol in EDGE_YOLLARI:
        if not Path(yol).is_file():
            continue
        try:
            subprocess.Popen([
                yol, f"--app={adres}",
                f"--window-size={PENCERE[0]},{PENCERE[1]}",
                "--no-first-run", "--no-default-browser-check",
            ])
            return True
        except OSError:
            continue
    return False


def kritik_hata(hata: str) -> None:
    """Beklenmeyen hatayı kaydeder ve Türkçe açıklama penceresi gösterir."""
    _kaydet(hata)
    klasor = str(kok_dizin() / "data" / "hata.log")
    mesaj = (
        "RetroOps beklenmedik bir hatayla karşılaştı.\n\n"
        f"Detaylar kaydedildi:\n{klasor}\n\n"
        "Yapabilecekleriniz:\n"
        "· Programı kapatıp tekrar açın\n"
        "· Windows Defender/antivirüs programın dosyalarını silmiş olabilir;\n"
        "  program klasörünü \"güvenilir\" olarak işaretleyin\n"
        "· Sorun sürerse program klasörüyle birlikte hata.log dosyasını\n"
        "  satış kanalına iletin"
    )
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, mesaj, "RetroOps", 0x10)
    except Exception:
        pass


def main() -> None:
    zorla_tarayici = "--tarayici" in sys.argv
    port = None if zorla_tarayici else calisan_port()

    if port is not None:
        adres = f"http://127.0.0.1:{port}"
        if not pencereye_basla(adres) and not edge_uygulama(adres):
            webbrowser.open(adres)
        sys.exit(0)

    if zorla_tarayici:
        son_hata = None
        for p in PORTLAR:
            try:
                web_main(p, tarayici_ac=True)
                sys.exit(0)
            except OSError as e:
                son_hata = e
                continue
        _kaydet(f"Uygun port bulunamadı ({son_hata}).")
        raise SystemExit(1)

    son_hata = None
    for p in PORTLAR:
        try:
            srv, adres = arka_planda(p)
        except OSError as e:
            son_hata = e
            continue
        if pencereye_basla(adres):
            sys.exit(0)
        # Masaüstü penceresi açılamadıysa Edge uygulama penceresi, o da yoksa
        # tarayıcı; sunucu açık kaldığı sürece panel çalışmaya devam eder.
        if not edge_uygulama(adres):
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


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        kritik_hata(traceback.format_exc())
        raise SystemExit(1)
