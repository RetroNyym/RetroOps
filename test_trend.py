"""Google Trends modülü: yerleşik veri her zaman, canlıya düşme davranışı."""

import pytest

from ops import trend


def test_yerlesik_her_zaman_dolu():
    veri = trend.veri_cek("e-ticaret", kategori="e-ticaret", canli_dene=False)
    assert veri["kaynak"] == "yerlesik"
    assert veri["canli_hata"] is None
    assert len(veri["seri"]) == trend.AY_SAYISI
    assert all(0 <= p["deger"] <= 100 for p in veri["seri"])
    assert all(len(p["tarih"]) == 7 for p in veri["seri"])


def test_kategorilerin_hepsi_var():
    for k in trend.KATEGORILER:
        veri = trend.veri_cek(kategori=k, canli_dene=False)
        assert veri["kategori"] == k
        assert len(veri["seri"]) == trend.AY_SAYISI
        assert veri["ipucu"]


def test_bilinmeyen_kategori_yedege_duser():
    veri = trend.veri_cek(kategori="boyle-kategori", canli_dene=False)
    assert veri["kategori"] == "e-ticaret"


def test_canli_hata_yerlesige_duser(monkeypatch):
    def patlak(*args, **kwargs):
        raise RuntimeError("429 Too Many Requests")

    monkeypatch.setattr(trend, "canli_veri", patlak)
    veri = trend.veri_cek("e-ticaret", kategori="e-ticaret")
    assert veri["kaynak"] == "yerlesik"
    assert "429" in veri["canli_hata"]
    assert len(veri["seri"]) == trend.AY_SAYISI


def test_deterministik():
    a = trend.veri_cek(kategori="iade", canli_dene=False)
    b = trend.veri_cek(kategori="iade", canli_dene=False)
    assert a["seri"] == b["seri"]


def test_etiketler_son_5_yil():
    etiketler = trend._ay_etiketleri()
    assert len(etiketler) == 60
    assert etiketler[0] < etiketler[-1]
    # son etiket içinde bulunduğumuz ay
    assert etiketler[-1].startswith("2026-")


def test_yapay_zeka_sicramasi():
    veri = trend.veri_cek(kategori="yapay zeka", canli_dene=False)
    seri = {p["tarih"]: p["deger"] for p in veri["seri"]}
    once = seri["2022-06"]
    sonra = seri["2024-01"]
    assert sonra > once + 40


def test_kategori_listesi():
    liste = trend.kategori_listesi()
    assert len(liste) == len(trend.KATEGORILER)
    assert {"id", "ad", "anahtar", "ipucu"} <= set(liste[0])


@pytest.mark.parametrize("kategori", list(trend.KATEGORILER))
def test_tum_kategoriler_cizilebilir(kategori):
    veri = trend.veri_cek(kategori=kategori, canli_dene=False)
    degerler = [p["deger"] for p in veri["seri"]]
    assert max(degerler) == 100  # en yüksek nokta 100'e normalize
    assert sum(degerler) > 0
