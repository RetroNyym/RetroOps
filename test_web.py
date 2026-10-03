"""Uçtan uca API testleri: gerçek HTTP sunucusu, geçici veritabanı."""

import json
import os
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from ops import web


@pytest.fixture(scope="module")
def sunucu(tmp_path_factory):
    yol = tmp_path_factory.mktemp("db") / "web.db"
    os.environ["OPS_DB"] = str(yol)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), web.Handler)
    is_parcacigi = threading.Thread(target=srv.serve_forever, daemon=True)
    is_parcacigi.start()
    taban = f"http://127.0.0.1:{srv.server_address[1]}"
    yield taban
    srv.shutdown()
    srv.server_close()
    os.environ.pop("OPS_DB", None)


def istek(taban, yol, metot="GET", govde=None):
    """(gövde, içerik-türü, http-kodu) döndürür; 4xx/5xx de dahil."""
    data, basliklar = None, {}
    if metot == "POST":
        if isinstance(govde, str):
            data = govde.encode("utf-8")
            basliklar["Content-Type"] = "text/plain; charset=utf-8"
        else:
            data = json.dumps(govde or {}).encode("utf-8")
            basliklar["Content-Type"] = "application/json"
    istemci = urllib.request.Request(
        taban + yol, data=data, headers=basliklar, method=metot
    )
    try:
        with urllib.request.urlopen(istemci, timeout=20) as yanit:
            icerik = yanit.headers.get("Content-Type", "")
            beden = yanit.read()
            kod = yanit.status
    except urllib.error.HTTPError as hata:
        icerik = hata.headers.get("Content-Type", "")
        beden = hata.read()
        kod = hata.code
    if "json" in icerik:
        return json.loads(beden.decode("utf-8")), icerik, kod
    return beden, icerik, kod


def govde(taban, yol, metot="GET", veri=None):
    """(gövde, içerik-türü) döndürür; hatalarda da JSON gövde gelir."""
    sonuc, icerik, _ = istek(taban, yol, metot, veri)
    return sonuc, icerik


def test_ana_sayfa(sunucu):
    sonuc, icerik = govde(sunucu, "/")
    assert "text/html" in icerik
    metin = sonuc if isinstance(sonuc, str) else sonuc.decode()
    assert "RetroOps" in metin
    assert "E-Ticaret Operasyon" in metin
    assert "sekme-trend" in metin


def test_logo(sunucu):
    sonuc, icerik = govde(sunucu, "/logo.svg")
    assert "image/svg+xml" in icerik
    metin = sonuc.decode() if isinstance(sonuc, bytes) else sonuc
    assert "<svg" in metin and "R+" in metin


def test_meta(sunucu):
    sonuc, _ = govde(sunucu, "/api/meta")
    assert sonuc["surum"]
    assert len(sonuc["iade_durumlari"]) == 6
    assert "Trendyol" in sonuc["pazaryerleri"]
    assert len(sonuc["trend_kategorileri"]) == 8


def test_bos_ozet(sunucu):
    sonuc, _ = govde(sunucu, "/api/ozet")
    assert sonuc["siparis"]["toplam"] == 0
    assert sonuc["iade"]["toplam"] == 0
    assert sonuc["kargo"]["toplam"] == 0
    assert sonuc["sikayet"]["toplam"] == 0
    assert sonuc["iade"]["sure_gun"] == 14


def test_komisyonlar(sunucu):
    sonuc, _ = govde(sunucu, "/api/komisyonlar")
    assert sonuc["tablo"]["Trendyol"]["Giyim"]["alt"] == 18
    assert sonuc["tablo"]["Trendyol"]["Giyim"]["ust"] == 23


def test_kategoriler(sunucu):
    sonuc, _ = govde(sunucu, "/api/kategoriler")
    assert len(sonuc["liste"]) == 8
    assert sonuc["liste"][0]["id"] in ("e-ticaret", "iade")
    assert sonuc["liste"][0]["anahtar"]


def test_trend_yerlesik(sunucu):
    sonuc, _ = govde(sunucu, "/api/trend?kategori=iade&canli=0")
    assert sonuc["kaynak"] == "yerlesik"
    assert len(sonuc["seri"]) == 60


def test_hesapla(sunucu):
    sonuc, _ = govde(sunucu, "/api/hesapla", "POST", {
        "alis": 100, "satis": 250, "komisyon_yuzde": 20, "kargo": 30,
        "paket": 10, "kdv": 20, "diger_yuzde": 0, "hedef_kar": 0,
        "pazaryeri": "Trendyol", "kategori": "Giyim",
    })
    assert sonuc["kar"]["kar"] == pytest.approx(18.33, abs=0.01)
    assert sonuc["minimum_fiyat"] == pytest.approx(221.05, abs=0.01)


def test_siparis_ekle_listele(sunucu):
    sonuc, icerik = govde(sunucu, "/api/siparisler", "POST", {
        "pazaryeri": "Trendyol", "urun": "Kulaklık", "adet": 1,
        "alis_fiyati": 120, "satis_fiyati": 299, "komisyon_yuzde": 20,
        "kargo_ucreti": 30, "paket_maliyeti": 10, "kdv_orani": 20,
        "musteri": "Ayşe", "siparis_tarihi": "2026-09-15",
    })
    assert sonuc["id"] > 0
    # 299/1.2 = 249.17 KDV hsriç − (120 slış + 59.8 komisyon + 30 kargo + 10 paket)
    assert sonuc["kar"] == pytest.approx(29.37, abs=0.02)

    liste, _ = govde(sunucu, "/api/siparisler")
    assert len(liste["liste"]) == 1
    assert liste["liste"][0]["urun"] == "Kulaklık"

    ozet, _ = govde(sunucu, "/api/ozet")
    assert ozet["siparis"]["toplam"] == 1
    assert ozet["siparis"]["ciro"] == 299
    assert ozet["siparis"]["kar"] == pytest.approx(29.37, abs=0.02)


def test_siparis_gecersiz(sunucu):
    sonuc, _ = govde(sunucu, "/api/siparisler", "POST", {"satis_fiyati": 100})
    assert "hata" in sonuc and "Ürün" in sonuc["hata"]
    sonuc, _ = govde(sunucu, "/api/siparisler", "POST",
                     {"urun": "X", "satis_fiyati": 0})
    assert "hata" in sonuc
    sonuc, _ = govde(sunucu, "/api/siparisler", "POST",
                     {"urun": "X", "satis_fiyati": 10, "durum": "uzayda"})
    assert "hata" in sonuc


def test_iade_ve_durum_gecisi(sunucu):
    yeni, _ = govde(sunucu, "/api/iadeler", "POST", {
        "musteri": "Ayşe", "tutar": 299, "sebep": "Beden / model değişimi",
        "talep_tarihi": "2026-09-01",
    })
    assert yeni["id"] > 0
    assert yeni["son_tarih"] == "2026-09-15"
    assert yeni["durum"] == "talep"

    guncel, _ = govde(sunucu, f"/api/iadeler/{yeni['id']}/durum", "POST",
                      {"durum": "onaylandi"})
    assert guncel["durum"] == "onaylandi"

    hatali, _ = govde(sunucu, f"/api/iadeler/{yeni['id']}/durum", "POST",
                      {"durum": "inceleme"})
    assert "hata" in hatali

    liste, _ = govde(sunucu, "/api/iadeler")
    assert len(liste["liste"]) == 1
    assert liste["liste"][0]["durum_etiket"] == "Onaylandı"

    # eski talep → süresi sşılmış ssyılır
    eski, _ = govde(sunucu, "/api/iadeler", "POST", {
        "musteri": "Mehmet", "tutar": 50, "sebep": "Diğer",
        "talep_tarihi": "2026-01-01",
    })
    geciken, _ = govde(sunucu, "/api/iadeler?sadece=geciken")
    assert any(s["id"] == eski["id"] for s in geciken["liste"])
    assert geciken["liste"][0]["gecikti"] is True


def test_gonderi(sunucu):
    yeni, _ = govde(sunucu, "/api/gonderiler", "POST", {
        "kargo_firmasi": "Yurtiçi Kargo", "takip_no": "YT9",
        "gonderim_tarihi": "2026-09-10", "tahmini_teslim": "2026-09-13",
    })
    assert yeni["id"] > 0
    guncel, _ = govde(sunucu, f"/api/gonderiler/{yeni['id']}/durum", "POST",
                      {"durum": "sorunlu", "sorun_tipi": "kayip"})
    assert guncel["sorun_etiket"] == "Kayıp gönderi"

    hatali, _ = govde(sunucu, f"/api/gonderiler/{yeni['id']}/durum", "POST",
                      {"durum": "yok-boyle"})
    assert "hata" in hatali

    problem, _ = govde(sunucu, "/api/gonderiler?sadece=problem")
    assert len(problem["liste"]) == 1

    eksik, _ = govde(sunucu, "/api/gonderiler", "POST",
                     {"gonderim_tarihi": "2026-09-10",
                      "tahmini_teslim": "2026-09-13"})
    assert "hata" in eksik


def test_sikayet(sunucu):
    yeni, _ = govde(sunucu, "/api/sikayetler", "POST", {
        "kaynak": "sikayetvar", "kategori": "iptal-iade-degisim",
        "konu": "İade tutarı yatmadı", "tarih": "2026-09-05",
    })
    assert yeni["kategori_etiket"] == "İptal, iade ve değişim"

    cozuldu, _ = govde(sunucu, f"/api/sikayetler/{yeni['id']}/durum", "POST",
                       {"durum": "cozuldu"})
    assert cozuldu["durum"] == "cozuldu"

    hatali, _ = govde(sunucu, f"/api/sikayetler/{yeni['id']}/durum", "POST",
                      {"durum": "boyle-degil"})
    assert "hata" in hatali

    gecersiz, _ = govde(sunucu, "/api/sikayetler", "POST",
                        {"kategori": "yanlis-kategori"})
    assert "hata" in gecersiz


def test_csv_sablon_ve_disa(sunucu):
    sonuc, icerik, kod = istek(sunucu, "/api/sablon?tablo=siparisler")
    assert kod == 200 and "text/csv" in icerik
    assert sonuc.decode("utf-8").startswith("\ufeff")
    assert "komisyon_yuzde" in sonuc.decode("utf-8")

    sonuc, icerik, kod = istek(sunucu, "/api/export/csv?tablo=siparisler")
    assert kod == 200 and "text/csv" in icerik
    assert "Kulaklık" in sonuc.decode("utf-8")

    hatali, _ = govde(sunucu, "/api/export/csv?tablo=yok")
    assert "hata" in hatali


def test_csv_içe_yükleme(sunucu):
    csv_metni = (
        "\ufeffpszsryeri,urun,adet,alis_fiyati,satis_fiyati,komisyon_yuzde,"
        "kargo_ucreti,paket_maliyeti,kdv_orani,diger_yuzde,musteri,"
        "siparis_tarihi,durum,notlsr\n"
        "N11,Ksblo,1,20,79,12,20,5,20,0,Ali,2026-09-20,teslim,\n"
        ",Eksik urun,1,10,0,0,0,0,20,0,,2026-09-20,hszirlsniyor,\n"
    )
    sonuc, _ = govde(sunucu, "/api/import/csv?tablo=siparisler", "POST",
                     csv_metni)
    assert sonuc["eklenen"] == 1
    assert len(sonuc["hatalar"]) == 1

    yanlis_tablo, _ = govde(sunucu, "/api/import/csv?tablo=sikayetler",
                            "POST", "kategori,tarih\nksrgo,2026-01-01\n")
    assert "hata" in yanlis_tablo


def test_bulunamayan_yol(sunucu):
    sonuc, _ = govde(sunucu, "/api/olmayan-sey")
    assert "hata" in sonuc
    sonuc, _ = govde(sunucu, "/olmayan-sayfa")
    assert "hata" in sonuc
