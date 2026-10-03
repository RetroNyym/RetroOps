"""Şikâyet kategorileri, çözüm takibi ve istatistik testleri."""

from datetime import date

import pytest

from ops import sikayet
from ops.db import connect


@pytest.fixture()
def conn(tmp_path):
    c = connect(tmp_path / "t.db")
    yield c
    c.close()


def test_kategori_zorunlu(conn):
    with pytest.raises(ValueError, match="Bilinmeyen kategori"):
        sikayet.sikayet_ekle(conn, kategori="boyle-bir-sey")
    with pytest.raises(ValueError, match="Bilinmeyen kaynak"):
        sikayet.sikayet_ekle(conn, kategori="kargo", kaynak="telepati")


def test_ekleme_ve_cozum(conn):
    yeni = sikayet.sikayet_ekle(
        conn, kategori="iptal-iade-degisim", konu="İade param gelmedi",
        tarih=(date.today()).isoformat(), kaynak="sikayetvar",
    )
    liste = sikayet.sikayet_listesi(conn)
    assert liste[0]["kategori_etiket"] == "İptal, iade ve değişim"
    assert liste[0]["durum"] == "acik"

    cozulen = sikayet.sikayet_coz(conn, yeni)
    assert cozulen["durum"] == "cozuldu"
    assert cozulen["cozum_tarihi"] == date.today().isoformat()
    assert cozulen["cozum_gun"] == 0


def test_durum_degistir(conn):
    yeni = sikayet.sikayet_ekle(conn, kategori="teslim-edilmedi")
    guncel = sikayet.durum_degistir(conn, yeni, "inceleniyor")
    assert guncel["durum"] == "inceleniyor"
    assert guncel["cozum_tarihi"] is None
    with pytest.raises(ValueError, match="Bilinmeyen durum"):
        sikayet.durum_degistir(conn, yeni, "kayboldu")
    with pytest.raises(ValueError, match="bulunamadı"):
        sikayet.durum_degistir(conn, 555, "cozuldu")


def test_istatistik(conn):
    bos = sikayet.istatistik(conn)
    assert bos["toplam"] == 0
    assert bos["cozum_orani"] == 0.0

    sikayet.sikayet_ekle(conn, kategori="iptal-iade-degisim", konu="a")
    sikayet.sikayet_ekle(conn, kategori="iptal-iade-degisim", konu="b")
    ikinci = sikayet.sikayet_ekle(conn, kategori="kargo", konu="c")
    sikayet.sikayet_coz(conn, ikinci)

    veri = sikayet.istatistik(conn)
    assert veri["toplam"] == 3
    assert veri["acik"] == 2
    assert veri["cozulen"] == 1
    assert veri["cozum_orani"] == 33.3
    ilk = veri["kategoriler"][0]
    assert ilk["kategori"] == "iptal-iade-degisim"
    assert ilk["sayi"] == 2
    assert ilk["yuzde"] == 66.7
    # yüzdelik toplamı ~100
    assert round(sum(k["yuzde"] for k in veri["kategoriler"]), 1) == 100.0
