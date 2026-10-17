"""İade durum makinesi, 14 gün sayacı ve özet testleri."""

from datetime import date, timedelta

import pytest

from ops import iade
from ops.db import connect


@pytest.fixture()
def conn(tmp_path):
    c = connect(tmp_path / "t.db")
    yield c
    c.close()


def test_ekleme_ve_14_gun_sayaci(conn):
    bugun = date.today()
    yeni = iade.iade_ekle(conn, musteri="Ayşe", tutar=250.0,
                          sebep="Beden / model değişimi")
    satir = conn.execute("SELECT * FROM iadeler WHERE id=?", (yeni,)).fetchone()
    assert satir["talep_tarihi"] == bugun.isoformat()
    assert satir["son_tarih"] == (bugun + timedelta(days=14)).isoformat()
    assert satir["durum"] == "talep"


def test_eski_talep_gecikti_sayilir(conn):
    eski = (date.today() - timedelta(days=20)).isoformat()
    yeni = iade.iade_ekle(conn, musteri="Mehmet", tutar=99.0,
                          sebep="Vazgeçtim (cayma hakkı)", talep_tarihi=eski)
    liste = iade.iade_listesi(conn, sadece_geciken=True)
    assert any(s["id"] == yeni for s in liste)
    assert liste[0]["gecikti"] is True
    assert liste[0]["kalan_gun"] < 0


def test_gecerli_gecisler(conn):
    yeni = iade.iade_ekle(conn, musteri="Ali", tutar=10.0, sebep="Diğer")
    iade.durum_degistir(conn, yeni, "onaylandi")
    iade.durum_degistir(conn, yeni, "kargoya_verildi")
    iade.durum_degistir(conn, yeni, "inceleme")
    iade.durum_degistir(conn, yeni, "tamamlandi")
    satir = conn.execute("SELECT * FROM iadeler WHERE id=?", (yeni,)).fetchone()
    assert satir["durum"] == "tamamlandi"
    assert satir["cozum_tarihi"] == date.today().isoformat()


def test_gecersiz_gecis_rededilir(conn):
    yeni = iade.iade_ekle(conn, musteri="Ali", tutar=10.0, sebep="Diğer")
    with pytest.raises(ValueError, match="geçilemez"):
        iade.durum_degistir(conn, yeni, "inceleme")
    with pytest.raises(ValueError, match="Bilinmeyen durum"):
        iade.durum_degistir(conn, yeni, "uzayda")
    with pytest.raises(ValueError, match="bulunamadı"):
        iade.durum_degistir(conn, 9999, "onaylandi")


def test_terminal_durumdan_cikis_yok(conn):
    yeni = iade.iade_ekle(conn, musteri="Ay", tutar=5.0, sebep="Diğer")
    iade.durum_degistir(conn, yeni, "reddedildi")
    with pytest.raises(ValueError):
        iade.durum_degistir(conn, yeni, "onaylandi")


def test_siparis_durumu_guncellenir(conn):
    sid = conn.execute(
        """INSERT INTO siparisler (urun, satis_fiyati, siparis_tarihi)
           VALUES ('Test ürün', 100, date('now'))"""
    ).lastrowid
    conn.commit()
    yeni = iade.iade_ekle(conn, siparis_id=sid, musteri="X", tutar=100,
                          sebep="Diğer")
    satir = conn.execute("SELECT durum FROM siparisler WHERE id=?",
                         (sid,)).fetchone()
    assert satir["durum"] == "iade"
    iade.durum_degistir(conn, yeni, "onaylandi")
    iade.durum_degistir(conn, yeni, "kargoya_verildi")
    iade.durum_degistir(conn, yeni, "inceleme")
    iade.durum_degistir(conn, yeni, "tamamlandi")
    satir = conn.execute("SELECT durum FROM siparisler WHERE id=?",
                         (sid,)).fetchone()
    assert satir["durum"] == "iade_tamam"


def test_ozet(conn):
    bos = iade.iade_ozet(conn)
    assert bos["toplam"] == 0 and bos["acik"] == 0

    iade.iade_ekle(conn, musteri="A", tutar=10, sebep="Diğer")
    eski = (date.today() - timedelta(days=30)).isoformat()
    iade.iade_ekle(conn, musteri="B", tutar=20, sebep="Diğer",
                   talep_tarihi=eski)
    veri = iade.iade_ozet(conn)
    assert veri["toplam"] == 2
    assert veri["acik"] == 2
    assert veri["geciken"] == 1
    assert veri["toplam_tutar"] == 30
    assert set(veri["dagilim"]) == set(iade.DURUMLAR)


def test_liste_siralamasi(conn):
    iade.iade_ekle(conn, musteri="A", tutar=1, sebep="Diğer",
                   talep_tarihi="2026-01-01")
    iade.iade_ekle(conn, musteri="B", tutar=2, sebep="Diğer")
    liste = iade.iade_listesi(conn)
    assert liste[0]["musteri"] == "B"
