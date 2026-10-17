"""Kargo gecikme eşiği, problem listesi ve durum testleri."""

from datetime import date, timedelta

import pytest

from ops import kargo
from ops.db import connect


@pytest.fixture()
def conn(tmp_path):
    c = connect(tmp_path / "t.db")
    yield c
    c.close()


def _gun(n: int) -> str:
    return (date.today() + timedelta(days=n)).isoformat()


def test_ekleme(conn):
    yeni = kargo.gonderi_ekle(
        conn, kargo_firmasi="Yurtiçi Kargo", gonderim_tarihi=_gun(-1),
        tahmini_teslim=_gun(2), takip_no="YT123",
    )
    satir = conn.execute("SELECT * FROM gonderiler WHERE id=?",
                         (yeni,)).fetchone()
    assert satir["kargo_firmasi"] == "Yurtiçi Kargo"
    assert satir["son_durum"] == "yolda"


def test_gersiz_girdi(conn):
    with pytest.raises(ValueError, match="Bilinmeyen gönderi durumu"):
        kargo.gonderi_ekle(conn, kargo_firmasi="X", gonderim_tarihi=_gun(0),
                           tahmini_teslim=_gun(1), son_durum="uzayda")
    with pytest.raises(ValueError):
        kargo.gonderi_ekle(conn, kargo_firmasi="X", gonderim_tarihi="bozuk",
                           tahmini_teslim=_gun(1))


def test_esik_asimi_problem(conn):
    # tahmini teslim 5 gün önce, eşik 3 gün → gecikmiş
    kargo.gonderi_ekle(conn, kargo_firmasi="MNG Kargo", gonderim_tarihi=_gun(-8),
                       tahmini_teslim=_gun(-5))
    problem = kargo.gonderi_listesi(conn, sadece_problem=True)
    assert len(problem) == 1
    assert problem[0]["gecikti"] is True
    assert problem[0]["sorunlu"] is True
    assert problem[0]["gecikme_gun"] == 5


def test_esik_icinde_problem_degil(conn):
    kargo.gonderi_ekle(conn, kargo_firmasi="Aras Kargo", gonderim_tarihi=_gun(-1),
                       tahmini_teslim=_gun(-1))
    problem = kargo.gonderi_listesi(conn, sadece_problem=True)
    assert problem == []


def test_esik_parametresi(conn):
    kargo.gonderi_ekle(conn, kargo_firmasi="Sürat Kargo", gonderim_tarihi=_gun(-4),
                       tahmini_teslim=_gun(-2))
    assert kargo.gonderi_listesi(conn, sadece_problem=True, esik=1)
    assert not kargo.gonderi_listesi(conn, sadece_problem=True, esik=10)


def test_sorun_tipi_isaretleme(conn):
    yeni = kargo.gonderi_ekle(conn, kargo_firmasi="PTT Kargo",
                              gonderim_tarihi=_gun(-2), tahmini_teslim=_gun(1))
    guncel = kargo.durum_degistir(conn, yeni, "sorunlu", sorun_tipi="kayip")
    assert guncel["sorunlu"] is True
    assert guncel["sorun_etiket"] == "Kayıp gönderi"
    with pytest.raises(ValueError, match="Bilinmeyen sorun tipi"):
        kargo.durum_degistir(conn, yeni, "yolda", sorun_tipi="yok-boyle")
    with pytest.raises(ValueError, match="bulunamadı"):
        kargo.durum_degistir(conn, 9999, "teslim")


def test_teslim_edilen_problem_sayilmaz(conn):
    yeni = kargo.gonderi_ekle(conn, kargo_firmasi="Trendyol Express",
                              gonderim_tarihi=_gun(-10),
                              tahmini_teslim=_gun(-7))
    kargo.durum_degistir(conn, yeni, "teslim")
    assert kargo.gonderi_listesi(conn, sadece_problem=True) == []


def test_ozet(conn):
    bos = kargo.gonderi_ozet(conn)
    assert bos["toplam"] == 0 and bos["problem"] == 0

    kargo.gonderi_ekle(conn, kargo_firmasi="Yurtiçi Kargo",
                       gonderim_tarihi=_gun(-9), tahmini_teslim=_gun(-6))
    kargo.gonderi_ekle(conn, kargo_firmasi="MNG Kargo", gonderim_tarihi=_gun(0),
                       tahmini_teslim=_gun(3))
    veri = kargo.gonderi_ozet(conn)
    assert veri["toplam"] == 2
    assert veri["problem"] == 1
    assert veri["dagilim"]["yolda"] == 2
    assert veri["sorun_dagilim"].get("gecikme") == 1
