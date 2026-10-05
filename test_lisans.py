"""Lisans ve yedek akışlarının uç ucaca sınanması."""

import json
import os
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from ops import lisans, web
from ops.db import varsayilan_yol


@pytest.fixture(scope="module")
def sunucu(tmp_path_factory):
    yol = tmp_path_factory.mktemp("lisansdb") / "web.db"
    os.environ["OPS_DB"] = str(yol)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), web.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    taban = f"http://127.0.0.1:{srv.server_address[1]}"
    yield taban
    srv.shutdown()
    srv.server_close()
    os.environ.pop("OPS_DB", None)


def istek(taban, yol, metot="GET", govde=None, icerik_tipi=None):
    data, basliklar = None, {}
    if metot == "POST":
        if isinstance(govde, (bytes, bytearray)):
            data = bytes(govde)
            basliklar["Content-Type"] = icerik_tipi or "application/octet-stream"
        else:
            data = json.dumps(govde or {}).encode("utf-8")
            basliklar["Content-Type"] = "application/json"
    istemci = urllib.request.Request(
        taban + yol, data=data, headers=basliklar, method=metot
    )
    try:
        with urllib.request.urlopen(istemci, timeout=20) as yanit:
            ham, kod = yanit.read(), yanit.status
            tip = yanit.headers.get("Content-Type", "")
    except urllib.error.HTTPError as hata:
        ham, kod = hata.read(), hata.code
        tip = hata.headers.get("Content-Type", "")
    if "json" in tip:
        return json.loads(ham.decode("utf-8")), kod
    return ham, kod


def test_deneme_suresi_baslar(sunucu):
    durum, kod = istek(sunucu, "/api/lisans")
    assert kod == 200
    assert durum["durum"] == "deneme"
    assert durum["kalan_gun"] == lisans.DENEME_GUN
    assert durum["makine"] == lisans.makine_id()


def test_meta_lisans_bilgisi_tasir(sunucu):
    meta, kod = istek(sunucu, "/api/meta")
    assert kod == 200
    assert meta["lisans"]["durum"] in ("deneme", "lisansli")
    assert "surum" in meta


def test_gecersiz_anahtar_reddedilir(sunucu):
    _, kod = istek(sunucu, "/api/lisans", "POST", {"anahtar": "RETROOPS-ABCDE-FGHJK"})
    assert kod == 400
    _, kod = istek(sunucu, "/api/lisans", "POST", {"anahtar": ""})
    assert kod == 400


def test_baska_makinaya_anahtar_reddedilir(sunucu):
    anahtar = lisans.anahtar_uret("2099-01-01", makine="0" * 16)
    veri, kod = istek(sunucu, "/api/lisans", "POST", {"anahtar": anahtar})
    assert kod == 400
    assert "başka bir bilgisayar" in veri["hata"]


def test_anahtar_etkinlestirir(sunucu):
    anahtar = lisans.anahtar_uret("2099-01-01")
    durum, kod = istek(sunucu, "/api/lisans", "POST", {"anahtar": anahtar})
    assert kod == 200
    assert durum["durum"] == "lisansli"
    assert durum["bitis"] == "2099-01-01"
    # veri uçları açık
    _, kod = istek(sunucu, "/api/ozet")
    assert kod == 200
    # tekrar oku
    tekrar, _ = istek(sunucu, "/api/lisans")
    assert tekrar["durum"] == "lisansli"


def test_sure_dolunca_kilit_veri_uclari_kapanir(sunucu):
    # mevcut anahtarı temizle ve denemeyi 20 gün geriye al
    kayit = json.loads(lisans.lisans_yolu().read_text(encoding="utf-8"))
    kayit["anahtar"] = None
    kayit["ilk"] = "2000-01-01"
    lisans.lisans_yolu().write_text(json.dumps(kayit), encoding="utf-8")

    durum, _ = istek(sunucu, "/api/lisans")
    assert durum["durum"] == "suresi_doldu"

    _, kod = istek(sunucu, "/api/ozet")
    assert kod == 402
    _, kod = istek(sunucu, "/api/siparisler")
    assert kod == 402
    _, kod = istek(sunucu, "/api/meta")
    assert kod == 200

    anahtar = lisans.anahtar_uret("2099-06-01")
    durum, kod = istek(sunucu, "/api/lisans", "POST", {"anahtar": anahtar})
    assert kod == 200 and durum["durum"] == "lisansli"
    _, kod = istek(sunucu, "/api/ozet")
    assert kod == 200


def test_yedek_indir_dogrula_geri_al(sunucu):
    istek(sunucu, "/api/siparisler", "POST", {
        "pazaryeri": "Trendyol", "urun": "Yedek ürün", "adet": 1,
        "alis_fiyati": 10, "satis_fiyati": 50, "kdv_orani": 20,
        "siparis_tarihi": "2026-01-01",
    })
    ham, kod = istek(sunucu, "/api/yedek/indir")
    assert kod == 200
    assert isinstance(ham, bytes) and ham[:15] == b"SQLite format 3"

    _, kod = istek(sunucu, "/api/yedek/yukle", "POST", b"bozuk-dosya")
    assert kod == 400
    assert varsayilan_yol().exists()

    sonuc, kod = istek(sunucu, "/api/yedek/yukle", "POST", ham)
    assert kod == 200 and sonuc["durum"] == "ok"

    sonuc, kod = istek(sunucu, "/api/yedek/geri_al", "POST", {})
    assert kod == 200 and sonuc["durum"] == "ok"

    liste, _ = istek(sunucu, "/api/siparisler")
    assert any(s["urun"] == "Yedek ürün" for s in liste["liste"])


def test_siparis_limit_parametresi(sunucu):
    for i in range(3):
        istek(sunucu, "/api/siparisler", "POST", {
            "pazaryeri": "Trendyol", "urun": f"Limit {i}", "adet": 1,
            "alis_fiyati": 1, "satis_fiyati": 10 + i, "kdv_orani": 20,
            "siparis_tarihi": "2026-02-02",
        })
    tam, _ = istek(sunucu, "/api/siparisler")
    kisali, _ = istek(sunucu, "/api/siparisler?limit=2")
    assert len(kisali["liste"]) == 2
    assert len(kisali["liste"]) <= len(tam["liste"])


def test_kilavuz_sayfasi(sunucu):
    ham, kod = istek(sunucu, "/kilavuz")
    assert kod == 200
    metin = ham.decode("utf-8")
    assert "Kurulum" in metin and "Panele dön" in metin
