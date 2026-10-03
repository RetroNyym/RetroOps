"""CSV şablon, toplu yükleme ve dışa aktarma testleri."""

import pytest

from ops import csv_io
from ops.db import connect


@pytest.fixture()
def conn(tmp_path):
    c = connect(tmp_path / "t.db")
    yield c
    c.close()


GECERLI = (
    "pazaryeri,siparis_no,urun,adet,alis_fiyati,satis_fiyati,komisyon_yuzde,"
    "kargo_ucreti,paket_maliyeti,kdv_orani,diger_yuzde,musteri,siparis_tarihi,"
    "durum,notlar\n"
    "Trendyol,SY-1,Kulaklik,1,120,299,20,30,10,20,0,Ayse,2026-09-01,"
    "hazirlaniyor,test\n"
    "N11,N-2,Mouse,2,80,180,15,25,5,20,0,Mehmet,01.09.2026,teslim,\n"
)


def test_sablon():
    sablon = csv_io.sablon_olustur("siparisler")
    assert "pazaryeri" in sablon
    assert "komisyon_yuzde" in sablon
    assert sablon.startswith("\ufeff")
    with pytest.raises(ValueError):
        csv_io.sablon_olustur("yok-boyle")


def test_gecerli_satirlar_yuklenir(conn):
    sonuc = csv_io.siparisleri_aktar(conn, GECERLI)
    assert sonuc["eklenen"] == 2
    assert sonuc["hatalar"] == []
    sayi = conn.execute("SELECT COUNT(*) c FROM siparisler").fetchone()["c"]
    assert sayi == 2
    # DD.MM.YYYY tarihi çözüldü mü
    tarih = conn.execute(
        "SELECT siparis_tarihi FROM siparisler WHERE siparis_no='N-2'"
    ).fetchone()["siparis_tarihi"]
    assert tarih == "2026-09-01"


def test_hatali_satirlar_raporlanir(conn):
    bozuk = (
        "urun,satis_fiyati,siparis_tarihi,durum\n"
        ",100,2026-01-01,hazirlaniyor\n"      # ürün yok
        "Urun,0,2026-01-01,hazirlaniyor\n"    # satış 0
        "Urun,50,bozuk-tarih,hazirlaniyor\n"  # tarih bozuk
        "Urun,50,2026-01-01,uzayda\n"         # durum bozuk
        "Iyi Urun,150,2026-01-02,\n"          # geçerli
    )
    sonuc = csv_io.siparisleri_aktar(conn, bozuk)
    assert sonuc["eklenen"] == 1
    assert len(sonuc["hatalar"]) == 4
    assert sonuc["toplam"] == 5


def test_bos_csv(conn):
    sonuc = csv_io.siparisleri_aktar(conn, "urun,satis_fiyati\n")
    assert sonuc["eklenen"] == 0


def test_disa_aktar_bos_tablo(conn):
    metin = csv_io.disa_aktar(conn, "siparisler")
    assert "pazaryeri" in metin


def test_disa_aktar_gersiz_tablo(conn):
    with pytest.raises(ValueError):
        csv_io.disa_aktar(conn, "yok")
    with pytest.raises(ValueError):
        csv_io.sablon_olustur("yok")


def test_aktar_sonrasi_disa_ve_tekrar_aktar(conn, tmp_path):
    csv_io.siparisleri_aktar(conn, GECERLI)
    disa = csv_io.disa_aktar(conn, "siparisler")
    assert disa.count("\n") == 3  # başlık + 2 satır

    conn2 = connect(tmp_path / "ikinci.db")
    try:
        sonuc = csv_io.siparisleri_aktar(conn2, disa)
        assert sonuc["eklenen"] == 2
        assert sonuc["hatalar"] == []
    finally:
        conn2.close()
