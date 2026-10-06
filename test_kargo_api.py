"""Kargo API entegrasyonu: firma listesi, kayıt, test, durum eşleme, rotalar."""

import json
import os
import threading
from http.server import ThreadingHTTPServer

import pytest

from ops import entegrasyon, kargo, kargo_api, web
from ops.adapters.temel import AgHatasi, Yanit
from ops.db import connect


@pytest.fixture(scope="module", autouse=True)
def ortam(tmp_path_factory):
    yol = tmp_path_factory.mktemp("db") / "kargo_api.db"
    os.environ["OPS_DB"] = str(yol)
    yield yol
    os.environ.pop("OPS_DB", None)


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
def conn():
    c = connect()
    yield c
    c.close()


def istek(taban, yol, metot="GET", govde=None):
    import urllib.error
    import urllib.request

    data, basliklar = None, {}
    if metot == "POST":
        data = json.dumps(govde or {}).encode("utf-8")
        basliklar["Content-Type"] = "application/json"
    istemci = urllib.request.Request(
        taban + yol, data=data, headers=basliklar, method=metot
    )
    try:
        with urllib.request.urlopen(istemci, timeout=20) as yanit:
            kod = yanit.status
            beden = yanit.read()
    except urllib.error.HTTPError as hata:
        kod = hata.code
        beden = hata.read()
    return json.loads(beden.decode("utf-8")), kod


def yakalayici(*yanitlar):
    durum = {"i": 0}
    cagri = []

    def http(url, **kwargs):
        cagri.append({"url": url, **kwargs})
        i = durum["i"]
        durum["i"] += 1
        cevap = yanitlar[min(i, len(yanitlar) - 1)]
        if isinstance(cevap, Exception):
            raise cevap
        if isinstance(cevap, Yanit):
            return cevap
        kod, veri = cevap
        return Yanit(kod, json.dumps(veri or {}), veri)

    return http, cagri


def test_firma_listesi():
    firmalar = kargo_api.firma_listesi()
    assert len(firmalar) == 6
    ids = [f["id"] for f in firmalar]
    assert ids[0] == "kargo_yurtici"
    assert "kargo_sendeo" in ids and "kargo_ptt" in ids
    for f in firmalar:
        assert f["platform"].startswith("kargo_")
        assert f["ad"] and f["alanlar"] and f["not"]
        assert f["id"] in entegrasyon.PLATFORMLAR
        zorunlu = [a for a in f["alanlar"] if a["zorunlu"]]
        assert any(a["id"] == "tabanAdres" for a in zorunlu), f["id"]
        assert any(a["gizli"] for a in zorunlu), f["id"]
    # pazaryeri listesi kargo firmalarıyla karışmaz
    assert len(entegrasyon.platform_listesi()) == 9
    assert not any(p["id"].startswith("kargo_")
                   for p in entegrasyon.platform_listesi())


def test_kaydet_sir_saklar(conn):
    kayit = kargo_api.kaydet(
        conn, firma="yurtici", ad="Ana şube",
        ayarlar={"tabanAdres": "https://webapi.yurticikargo.com",
                 "sorguYolu": "/track"},
        kimlik={"kullanici": "MUSTERI1", "parola": "gizli-kargo-sifre"},
    )
    assert kayit["id"] > 0
    assert kayit["platform"] == "kargo_yurtici"
    assert kayit["dolu"] == ["parola"]

    ham = json.dumps(kargo_api.liste(conn), ensure_ascii=False)
    assert "gizli-kargo-sifre" not in ham
    assert "MUSTERI1" in ham
    assert len(kargo_api.liste(conn)) == 1


def test_eksik_ya_bilinmeyen_firma(conn):
    with pytest.raises(ValueError) as hata:
        kargo_api.kaydet(conn, firma="yurtici", ad="Eksik",
                         ayarlar={}, kimlik={"kullanici": "a"})
    assert "Eksik zorunlu alanlar" in str(hata.value)
    with pytest.raises(ValueError) as hata:
        kargo_api.kaydet(conn, firma="boyle-firma", ad="X",
                         ayarlar={}, kimlik={})
    assert "Bilinmeyen kargo firması" in str(hata.value)


def test_adres_kur():
    ayar = {"tabanAdres": "https://api.ornek.com/",
            "sorguYolu": "v1/track", "takipAlani": "takipNo"}
    assert kargo_api._adres(ayar, "") == "https://api.ornek.com/v1/track"
    assert kargo_api._adres(ayar, "ABC 123") == \
        "https://api.ornek.com/v1/track?takipNo=ABC%20123"
    with pytest.raises(ValueError) as hata:
        kargo_api._adres({"tabanAdres": "  "}, "X")
    assert "API adresi girilmemiş" in str(hata.value)


def test_test_durumlari(conn):
    with pytest.raises(ValueError) as hata:
        kargo_api.test(None, firma="yurtici", ayarlar={},
                       kimlik={"kullanici": "a", "parola": "b"})
    assert "Eksik zorunlu alanlar" in str(hata.value)

    temel = {"tabanAdres": "https://api.ornek.com"}
    kimlik = {"kullanici": "a", "parola": "b"}

    ok, cagri = yakalayici((200, {"status": "ok"}))
    son = kargo_api.test(None, firma="yurtici", ayarlar=temel,
                          kimlik=kimlik, http=ok)
    assert son["durum"] == "ok"
    assert "Sorgu yolu boş" in son["mesaj"]
    assert "Basic " in cagri[0]["basliklar"]["Authorization"]

    jeton, cagri = yakalayici((200, {}))
    son = kargo_api.test(None, firma="sendeo",
                          ayarlar={"tabanAdres": "https://api.sendeo.com"},
                          kimlik={"apiKey": "sd-secret"}, http=jeton)
    assert son["durum"] == "ok"
    assert cagri[0]["basliklar"]["Authorization"] == "Bearer sd-secret"

    redd, _ = yakalayici((401, {"message": "unauthorized"}))
    son = kargo_api.test(None, firma="yurtici", ayarlar=temel,
                          kimlik=kimlik, http=redd)
    assert son["durum"] == "hata"
    assert "401" in son["mesaj"]

    ag, _ = yakalayici(AgHatasi("SSLEOFError: kesildi"))
    son = kargo_api.test(None, firma="yurtici", ayarlar=temel,
                          kimlik=kimlik, http=ag)
    assert son["durum"] == "ag"
    assert "SSLEOFError" in son["mesaj"]

    # kayıtlı bağlantı testi sonucu veritabanına yazılır
    kayit = kargo_api.kaydet(
        conn, firma="sendeo", ad="Sendeo mağaza",
        ayarlar={"tabanAdres": "https://api.sendeo.com"},
        kimlik={"apiKey": "sd-secret"},
    )
    son = kargo_api.test(conn, entegrasyon.satir(conn, kayit["id"]),
                         http=yakalayici((200, {}))[0])
    assert son["durum"] == "ok"
    taze = entegrasyon.satir(conn, kayit["id"])
    assert taze["son_test_sonuc"] == "ok"
    assert taze["son_test"]


def test_durum_eslestir():
    durumlar = {
        "Teslim edildi": "teslim",
        "DELIVERED": "teslim",
        "TESLİM EDİLEMEDİ": "sorunlu",
        "İptal edildi": "sorunlu",
        "Dağıtımda": "subede",
        "Gönderi şubeye ulaştı": "subede",
        "Out for delivery": "subede",
        "Yola çıktı": "yolda",
        "Kargoya verildi": "yolda",
        "Sipariş oluşturuldu": "hazir",
        "Pending": "hazir",
    }
    for ham, beklenen in durumlar.items():
        assert kargo_api.durum_eslestir(ham) == beklenen, ham
    assert kargo_api.durum_eslestir("tamamen farklı metin") is None
    assert kargo_api.durum_eslestir("") is None


def test_durum_metni():
    assert kargo_api._durum_metni({"status": "Yola çıktı"}) == "Yola çıktı"
    assert kargo_api._durum_metni({"result": {"state": "Teslim edildi"}}) == \
        "Teslim edildi"
    assert kargo_api._durum_metni({"count": 3}) == ""
    assert kargo_api._durum_metni(None) == ""


def test_durum_sorgula_ve_senkron(conn):
    kargo_api.kaydet(
        conn, firma="mng", ad="MNG merkez",
        ayarlar={"tabanAdres": "https://api.mngkargo.com.tr",
                 "sorguYolu": "/shipments/track", "takipAlani": "takipNo"},
        kimlik={"kullanici": "kullanici", "parola": "sifre"},
    )
    kargo.gonderi_ekle(
        conn, kargo_firmasi="MNG Kargo", gonderim_tarihi="2026-10-01",
        tahmini_teslim="2026-10-05", takip_no="MNG789",
    )
    g = conn.execute(
        "SELECT * FROM gonderiler ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert g["son_durum"] == "yolda"

    http, cagri = yakalayici((200, {"result": {"status": "Dağıtımda"}}))
    son = kargo_api.durum_sorgula(conn, g, http=http)
    assert son["durum"] == "ok"
    assert son["son_durum"] == "subede"
    assert "takipNo=MNG789" in cagri[0]["url"]
    assert cagri[0]["url"].startswith("https://api.mngkargo.com.tr/")

    senkron = kargo_api.senkron(
        conn, http=yakalayici((200, {"status": "Dağıtımda"}))[0]
    )
    assert senkron["durum"] == "ok"
    assert senkron["sorgulanan"] == 1
    assert senkron["guncel"] == 1
    g2 = conn.execute("SELECT * FROM gonderiler WHERE id=?", (g["id"],)
                      ).fetchone()
    assert g2["son_durum"] == "subede"

    senkron = kargo_api.senkron(
        conn, http=yakalayici((200, {"status": "Teslim edildi"}))[0]
    )
    assert senkron["guncel"] == 1
    g3 = conn.execute("SELECT * FROM gonderiler WHERE id=?", (g["id"],)
                      ).fetchone()
    assert g3["son_durum"] == "teslim"

    hatali = kargo_api.senkron(
        conn, http=yakalayici(AgHatasi("SSLEOFError: kesildi"))[0]
    )
    assert hatali["hatali"] == 1
    assert hatali["durum"] == "uyari"
    assert "SSLEOFError" in hatali["notlar"][0]

    # bağlantı silinince sorgulanacak gönderi kalmaz
    mng = [k for k in kargo_api.liste(conn) if k["platform"] == "kargo_mng"]
    kargo_api.sil(conn, mng[0]["id"])
    bos = kargo_api.senkron(conn, http=yakalayici((200, {}))[0])
    assert bos["durum"] == "uyari"
    assert bos["sorgulanan"] == 0


def test_durum_sorgula_takipsiz_ve_baglantisiz(conn):
    kargo.gonderi_ekle(
        conn, kargo_firmasi="Aras Kargo", gonderim_tarihi="2026-10-01",
        tahmini_teslim="2026-10-05", takip_no="",
    )
    g = conn.execute("SELECT * FROM gonderiler ORDER BY id DESC LIMIT 1"
                     ).fetchone()
    with pytest.raises(ValueError) as hata:
        kargo_api.durum_sorgula(conn, g, http=yakalayici((200, {}))[0])
    assert "takip numarası yok" in str(hata.value)

    kargo.gonderi_ekle(
        conn, kargo_firmasi="Surat Kargo", gonderim_tarihi="2026-10-01",
        tahmini_teslim="2026-10-05", takip_no="SD456",
    )
    g = conn.execute("SELECT * FROM gonderiler ORDER BY id DESC LIMIT 1"
                     ).fetchone()
    with pytest.raises(ValueError) as hata:
        kargo_api.durum_sorgula(conn, g, http=yakalayici((200, {}))[0])
    assert "bağlantısı yok" in str(hata.value)


def test_web_rota(sunucu, monkeypatch):
    d, kod = istek(sunucu, "/api/kargo/api")
    assert kod == 200
    assert len(d["firmalar"]) == 6
    assert all(k["platform"].startswith("kargo_") for k in d["liste"])

    yeni, kod = istek(sunucu, "/api/kargo/api", "POST", {
        "firma": "ptt", "ad": "PTT şube",
        "ayarlar": {"tabanAdres": "https://api.ptt.gov.tr"},
        "kimlik": {"kullanici": "u", "parola": "gizli-ptt"},
    })
    assert kod == 201
    assert yeni["platform"] == "kargo_ptt"

    eksik, kod = istek(sunucu, "/api/kargo/api", "POST",
                       {"firma": "ptt", "ad": "Boş", "kimlik": {}})
    assert kod == 400
    assert "hata" in eksik

    liste, _ = istek(sunucu, "/api/kargo/api")
    ptt = [k for k in liste["liste"] if k["platform"] == "kargo_ptt"]
    assert len(ptt) == 1
    assert "gizli-ptt" not in json.dumps(liste, ensure_ascii=False)

    # pazaryeri listesine kargo bağlantıları karışmaz
    paz, _ = istek(sunucu, "/api/entegrasyonlar")
    assert len(paz["platformlar"]) == 9
    assert all(not k["platform"].startswith("kargo_") for k in paz["liste"])

    def sahte_test(conn, kayit=None, *, firma="", ayarlar=None,
                   kimlik=None, http=None):
        return {"durum": "ok", "kod": 200, "mesaj": "sahte test"}

    monkeypatch.setattr(kargo_api, "test", sahte_test)
    taslak, kod = istek(sunucu, "/api/kargo/api/test", "POST",
                        {"firma": "ptt", "ayarlar": {"tabanAdres": "x"},
                         "kimlik": {"kullanici": "u", "parola": "p"}})
    assert kod == 200 and taslak["durum"] == "ok"

    kayitli, kod = istek(sunucu, f"/api/kargo/api/{yeni['id']}/test",
                         "POST", {})
    assert kod == 200 and kayitli["durum"] == "ok"

    yok, kod = istek(sunucu, "/api/kargo/api/9999/test", "POST", {})
    assert kod == 404
    assert "hata" in yok

    def sahte_senkron(conn, *, http=None, sinir=100):
        return {"durum": "ok", "mesaj": "sahte senkron", "sorgulanan": 2,
                "guncel": 1, "hatali": 0, "notlar": []}

    monkeypatch.setattr(kargo_api, "senkron", sahte_senkron)
    senk, kod = istek(sunucu, "/api/kargo/senkron", "POST", {})
    assert kod == 200
    assert senk["guncel"] == 1

    silinen, kod = istek(sunucu, f"/api/kargo/api/{yeni['id']}/sil",
                         "POST", {})
    assert kod == 200
    assert silinen["silindi"] == yeni["id"]
    liste, _ = istek(sunucu, "/api/kargo/api")
    assert all(k["id"] != yeni["id"] for k in liste["liste"])
