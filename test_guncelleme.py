"""Uzaktan güncelleme kontrolü: yerel sürüm dosyası, önbellek ve rota."""

import json
import os
import threading
from http.server import ThreadingHTTPServer

import pytest

from ops import __surum__, guncelleme, web


@pytest.fixture(scope="module", autouse=True)
def ortam(tmp_path_factory):
    yol = tmp_path_factory.mktemp("db") / "guncelleme.db"
    os.environ["OPS_DB"] = str(yol)
    guncelleme.onbellek_temizle()
    yield yol
    os.environ.pop("OPS_DB", None)
    guncelleme.onbellek_temizle()


@pytest.fixture(scope="module")
def sunucu(ortam):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), web.Handler)
    is_parcacigi = threading.Thread(target=srv.serve_forever, daemon=True)
    is_parcacigi.start()
    taban = f"http://127.0.0.1:{srv.server_address[1]}"
    yield taban
    srv.shutdown()
    srv.server_close()


@pytest.fixture()
def dosya(tmp_path, monkeypatch):
    """Yerel sürüm dosyasını ``OPS_GUNCELLEME_DOSYA`` olarak gösterir."""
    yol = tmp_path / "surum.json"

    def yaz(**veri):
        yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
        monkeypatch.setenv("OPS_GUNCELLEME_DOSYA", str(yol))
        guncelleme.onbellek_temizle()
        return yol

    return yaz


def istek(taban, yol):
    import urllib.request

    with urllib.request.urlopen(taban + yol, timeout=20) as yanit:
        return json.loads(yanit.read().decode("utf-8")), yanit.status


def test_surum_sozluk():
    assert guncelleme.surum_sozluk("1.10.2") == (1, 10, 2)
    assert guncelleme.surum_sozluk("1.1.0") < guncelleme.surum_sozluk("1.1.1")
    assert guncelleme.surum_sozluk("1.10.0") > guncelleme.surum_sozluk("1.9.9")
    assert guncelleme.surum_sozluk("2.0.0-beta") > guncelleme.surum_sozluk("1.9.9")
    assert guncelleme.surum_sozluk("") == (0,)


def test_yeni_surum_var(dosya):
    dosya(**{"surum": "9.9.9", "indirme": "https://ornek.com/indir",
             "not": "Yeni özellikler eklendi."})
    son = guncelleme.kontrol()
    assert son["yeni_var"] is True
    assert son["son"] == "9.9.9"
    assert son["mevcut"] == __surum__
    assert son["indirme"] == "https://ornek.com/indir"
    assert son["not"] == "Yeni özellikler eklendi."
    assert son["hata"] == ""


def test_guncel_surum(dosya):
    dosya(surum=__surum__)
    son = guncelleme.kontrol()
    assert son["yeni_var"] is False
    assert son["son"] == __surum__
    assert son["hata"] == ""


def test_onbellek(dosya):
    yol = dosya(surum="9.9.9")
    ilk = guncelleme.kontrol()
    assert ilk["yeni_var"] is True

    # dosya değişse de önbellek süresi dolmadan eski sonuç döner
    yol.write_text(json.dumps({"surum": __surum__}), encoding="utf-8")
    tekrar = guncelleme.kontrol()
    assert tekrar == ilk

    guncelleme.onbellek_temizle()
    sonra = guncelleme.kontrol()
    assert sonra["yeni_var"] is False


def test_bozuk_ve_eksik_dosya(tmp_path, monkeypatch):
    bozuk = tmp_path / "bozuk.json"
    bozuk.write_text("{bozuk json", encoding="utf-8")
    monkeypatch.setenv("OPS_GUNCELLEME_DOSYA", str(bozuk))
    guncelleme.onbellek_temizle()
    son = guncelleme.kontrol()
    assert son["yeni_var"] is False
    assert "Güncelleme kontrol edilemedi" in son["hata"]

    eksik = tmp_path / "eksik.json"
    eksik.write_text(json.dumps({"indirme": "x"}), encoding="utf-8")
    monkeypatch.setenv("OPS_GUNCELLEME_DOSYA", str(eksik))
    guncelleme.onbellek_temizle()
    son = guncelleme.kontrol()
    assert son["yeni_var"] is False
    assert "'surum' alanı yok" in son["hata"]

    yok = tmp_path / "yok.json"
    monkeypatch.setenv("OPS_GUNCELLEME_DOSYA", str(yok))
    guncelleme.onbellek_temizle()
    son = guncelleme.kontrol()
    assert son["yeni_var"] is False
    assert son["hata"]


def test_kapali(monkeypatch):
    monkeypatch.setenv("OPS_GUNCELLEME", "yok")
    son = guncelleme.kontrol()
    assert son["yeni_var"] is False
    assert "kapalı" in son["hata"]


def test_web_rota(sunucu, dosya):
    dosya(**{"surum": "99.0.0", "not": "Yeni sürüm çıktı."})
    d, kod = istek(sunucu, "/api/guncelleme")
    assert kod == 200
    assert d["mevcut"] == __surum__
    assert d["yeni_var"] is True
    assert d["son"] == "99.0.0"
