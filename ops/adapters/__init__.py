"""Platform adaptörleri: her pazaryeri için test ve sipariş çekme mantığı."""

from __future__ import annotations

from . import (amazon, ciceksepeti, hepsiburada, n11, pazarama, shopier,
               shopify, trendyol, woocommerce)
from .temel import AgHatasi, TemelAdapter, istek, sonuc, test_sonucu

SIRA = (
    "trendyol",
    "hepsiburada",
    "n11",
    "ciceksepeti",
    "shopier",
    "pazarama",
    "shopify",
    "woocommerce",
    "amazon",
)

ADAPTERLER: dict[str, TemelAdapter] = {
    p: modul.Adapter()
    for p, modul in (
        ("trendyol", trendyol),
        ("hepsiburada", hepsiburada),
        ("n11", n11),
        ("ciceksepeti", ciceksepeti),
        ("shopier", shopier),
        ("pazarama", pazarama),
        ("shopify", shopify),
        ("woocommerce", woocommerce),
        ("amazon", amazon),
    )
}


def al(platform: str) -> TemelAdapter:
    try:
        return ADAPTERLER[platform]
    except KeyError:
        raise ValueError(f"Bilinmeyen platform: {platform}") from None


__all__ = [
    "ADAPTERLER",
    "AgHatasi",
    "SIRA",
    "TemelAdapter",
    "al",
    "istek",
    "sonuc",
    "test_sonucu",
]
