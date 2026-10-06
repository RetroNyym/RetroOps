"""Panelin tüm sekmelerinin ekran görüntülerini alır (GitHub/README için).

Headless Edge ile, masaüstüne hiç dokunmadan yakalar; her sekme
`#sekme` derin bağlantısıyla açılır (ör. http://127.0.0.1:8786/#iade).

Kullanım: python araclar/goruntu_al.py
Çıktı:   gorseller/01-panel.png ... gorseller/07-csv.png
"""

import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

from ops.web import arka_planda  # noqa: E402

PORT = 8786
GENISLIK, YUKSEKLIK = 1440, 900
SANAL_ZAMAN = 9000  # ms: veri yüklemelerinin bitmesi için
SEKMELER = [
    ("", "01-panel"),
    ("iade", "02-iadeler"),
    ("kargo", "03-kargo"),
    ("kar", "04-kar-hesabi"),
    ("sikayet", "05-sikayetler"),
    ("entegrasyon", "06-entegrasyonlar"),
    ("csv", "07-csv"),
]
CIKTI = KOK / "gorseller"

EDGE_YOLLARI = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def edge_bul() -> str:
    for yol in EDGE_YOLLARI:
        if Path(yol).is_file():
            return yol
    bulunan = shutil.which("msedge")
    if bulunan:
        return bulunan
    raise RuntimeError("Edge bulunamadı (headless ekran görüntüsü için gerekli)")


def yakala() -> None:
    edge = edge_bul()
    CIKTI.mkdir(exist_ok=True)
    srv, adres = arka_planda(PORT)
    try:
        for sekme, dosya in SEKMELER:
            hedef = CIKTI / f"{dosya}.png"
            if hedef.exists():
                hedef.unlink()
            profil = tempfile.mkdtemp(prefix="retroops-shot-")  # her çekime özel
            komut = [
                edge, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                "--no-first-run", "--force-device-scale-factor=1",
                "--window-size=%d,%d" % (GENISLIK, YUKSEKLIK),
                "--virtual-time-budget=%d" % SANAL_ZAMAN,
                "--user-data-dir=" + profil,
                "--screenshot=" + str(hedef),
                f"{adres}/#{sekme}",
            ]
            try:
                subprocess.run(komut, capture_output=True, timeout=90)
                for _ in range(40):  # dosyanın yazılmasını bekle
                    if hedef.exists() and hedef.stat().st_size > 0:
                        break
                    time.sleep(0.25)
            finally:
                shutil.rmtree(profil, ignore_errors=True)
            boyut = hedef.stat().st_size // 1024 if hedef.exists() else 0
            if not boyut:
                raise RuntimeError(f"görüntü alınamadı: {dosya}")
            print(f"kaydedildi: gorseller/{dosya}.png (~{boyut} KB)", flush=True)
    finally:
        srv.shutdown()
    print("bitti", flush=True)


if __name__ == "__main__":
    yakala()
