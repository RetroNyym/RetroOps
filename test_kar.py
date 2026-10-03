"""Kâr hesabı, komisyon tablosu ve kırılma noktası fiyat testleri."""

import pytest

from ops import kar


def test_bilinen_deger():
    h = kar.hesap(alis=100, satis=250, komisyon_yuzde=20, kargo=30,
                  paket=10, kdv=20, diger_yuzde=0)
    assert h["satis_kdv_haric"] == pytest.approx(208.33, abs=0.01)
    assert h["giderler"]["komisyon"] == 50.0
    assert h["toplam_gider"] == 190.0
    assert h["kar"] == pytest.approx(18.33, abs=0.01)
    assert h["marj_yuzde"] == pytest.approx(8.8, abs=0.1)


def test_kdv_ve_diger_kesinti():
    h = kar.hesap(alis=80, satis=200, komisyon_yuzde=10, kdv=20,
                  diger_yuzde=2)
    assert h["giderler"]["diger"] == 4.0
    assert h["satis_kdv_haric"] == pytest.approx(166.67, abs=0.01)
    assert h["kar"] == pytest.approx(62.67, abs=0.01)


def test_minimum_fiyat_sifir_kar():
    fiyat = kar.minimum_fiyat(alis=100, komisyon_yuzde=20, kargo=30,
                              paket=10, kdv=20, diger_yuzde=0)
    assert fiyat == pytest.approx(221.05, abs=0.01)
    h = kar.hesap(alis=100, satis=fiyat, komisyon_yuzde=20, kargo=30,
                  paket=10, kdv=20, diger_yuzde=0)
    assert h["kar"] == pytest.approx(0.0, abs=0.02)


def test_hedefli_fiyat():
    fiyat = kar.minimum_fiyat(alis=100, komisyon_yuzde=20, kargo=30,
                              paket=10, kdv=20, hedef_kar=50)
    h = kar.hesap(alis=100, satis=fiyat, komisyon_yuzde=20, kargo=30,
                  paket=10, kdv=20, hedef_kar=50)
    assert h["kar"] == pytest.approx(50.0, abs=0.02)


def test_imkansiz_kesinti_hatasi():
    with pytest.raises(ValueError, match="hesaplanamaz"):
        kar.minimum_fiyat(alis=100, komisyon_yuzde=90, kdv=20)


def test_sifir_satis_hatasi():
    with pytest.raises(ValueError):
        kar.hesap(alis=10, satis=0, komisyon_yuzde=10)
    with pytest.raises(ValueError):
        kar.hesap(alis=10, satis=-5, komisyon_yuzde=10)


def test_komisyon_tablosu_ortasi():
    assert kar.komisyon_ortasi("Trendyol", "Giyim") == 20.5
    assert kar.komisyon_ortasi("N11", "Elektronik") == 13.5
    assert kar.komisyon_ortasi("Bilinmeyen", "X") == 0.0
    assert kar.komisyon_ortasi("Amazon TR", "Yok Boyle Bir Sey") == 7.0


def test_virgullu_girdi():
    h = kar.hesap(alis="100,50", satis="250,50", komisyon_yuzde="10")
    assert h["giderler"]["komisyon"] == 25.05
    assert h["giderler"]["alis"] == 100.5
    assert h["kar"] == pytest.approx(83.2, abs=0.01)


def test_api_sarmalayici():
    s = kar.hesapla_ve_fiyat_ara({
        "alis": 100, "satis": 250, "komisyon_yuzde": 20, "kargo": 30,
        "paket": 10, "kdv": 20, "diger_yuzde": 0, "hedef_kar": 0,
        "pazaryeri": "Trendyol", "kategori": "Giyim",
    })
    assert s["kar"]["kar"] == pytest.approx(18.33, abs=0.01)
    assert s["minimum_fiyat"] == pytest.approx(221.05, abs=0.01)
    assert s["hedefli_fiyat"] == pytest.approx(221.05, abs=0.01)
    assert s["onerilen_komisyon"] == 20.5
    assert s["hesap_hatasi"] is None


def test_api_imkansiz_durum():
    s = kar.hesapla_ve_fiyat_ara({
        "alis": 100, "satis": 500, "komisyon_yuzde": 95, "kdv": 20,
    })
    assert s["minimum_fiyat"] is None
    assert s["hesap_hatasi"]
    # satış varsa kâr dökümü yine döner
    assert s["kar"]["kar"] < 0
