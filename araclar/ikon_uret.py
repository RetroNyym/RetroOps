"""RetroOps logosundan .exe ikonu ve .png üretir.

Kullanım: python araclar/ikon_uret.py
Çıktı: retroops.ico (çok boyutlu) + retroops-logo.png (512px)
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

KOK = Path(__file__).resolve().parent.parent
ICON_YOL = KOK / "retroops.ico"
PNG_YOL = KOK / "retroops-logo.png"

DURAKLAR = [(0.0, (10, 27, 51)), (0.5, (13, 74, 88)), (1.0, (18, 162, 147))]
FONT_YOLLARI = [
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "DejaVuSans-Bold.ttf",
]


def _renk(t: float) -> tuple:
    for i in range(len(DURAKLAR) - 1):
        t0, r0 = DURAKLAR[i]
        t1, r1 = DURAKLAR[i + 1]
        if t0 <= t <= t1:
            oran = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return tuple(round(a + (b - a) * oran) for a, b in zip(r0, r1))
    return DURAKLAR[-1][1]


def _gradyan(boyut: int) -> Image.Image:
    gorsel = Image.new("RGBA", (boyut, boyut), (0, 0, 0, 0))
    piksel = gorsel.load()
    for y in range(boyut):
        for x in range(boyut):
            t = (x + y) / (2 * max(boyut - 1, 1))
            piksel[x, y] = (*_renk(t), 255)
    return gorsel


def _font(boyut: int) -> ImageFont.FreeTypeFont:
    for yol in FONT_YOLLARI:
        try:
            return ImageFont.truetype(yol, boyut)
        except OSError:
            continue
    return ImageFont.load_default()


def logo(boyut: int = 512) -> Image.Image:
    k = boyut / 100.0
    gorsel = _gradyan(boyut)
    maske = Image.new("L", (boyut, boyut), 0)
    ciz = ImageDraw.Draw(maske)
    ciz.rounded_rectangle(
        [7 * k, 7 * k, 93 * k, 93 * k], radius=26 * k, fill=255
    )
    sonuc = Image.new("RGBA", (boyut, boyut), (0, 0, 0, 0))
    sonuc.paste(gorsel, (0, 0), maske)

    katman = ImageDraw.Draw(sonuc)
    # beyaz çerçeve (SVG: stroke-width 7)
    katman.rounded_rectangle(
        [7 * k, 7 * k, 93 * k, 93 * k], radius=26 * k,
        outline=(255, 255, 255, 255), width=max(1, round(7 * k)),
    )
    # "R+" altındaki kaide (SVG: M20 60 H80 L56 79 V90 H44 V79 Z)
    kaide = [(20, 60), (80, 60), (56, 79), (56, 90), (44, 90), (44, 79)]
    katman.polygon([(x * k, y * k) for x, y in kaide],
                   fill=(255, 255, 255, 255))
    # "R+" yazısı
    font = _font(round(40 * k))
    katman.text((50 * k, 53 * k), "R+", font=font, fill=(255, 255, 255, 255),
                anchor="ms")
    return sonuc


def main() -> None:
    gorsel = logo(512)
    gorsel.save(PNG_YOL, "PNG")
    kucuk = [16, 24, 32, 48, 64, 128, 256]
    ikon = logo(256)
    ikon.save(ICON_YOL, "ICO", sizes=[(s, s) for s in kucuk])
    print(f"yazildi: {ICON_YOL.name} ({ICON_YOL.stat().st_size} bayt)")
    print(f"yazildi: {PNG_YOL.name} ({PNG_YOL.stat().st_size} bayt)")


if __name__ == "__main__":
    sys.exit(main())
