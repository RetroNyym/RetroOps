"""Entegrasyon modülleri: kayıt, şifreleme, normalizasyon, senkron ve rotalar."""

import json
import os
import threading
from datetime import date
from http.server import ThreadingHTTPServer

import pytest

from ops import entegrasyon, sifre, web
from ops.adapters.temel import AgHatasi, Yanit
from ops.db import connect

TRENDYOL_YANIT = {
    "page": 0,
    "size": 10,
    "totalPages": 1,
    "totalElements": 1,
    "content": [
        {
            "id": 555,
            "orderNumber": "TY-1001",
            "totalPrice": 299.90,
            "grossAmount": 299.90,
            "orderDate": 1756000000000,
            "status": "Shipped",
            "cargoTrackingNumber": "TYX123",
            "cargoProviderName": "Trendyol Express",
            "shipmentAddress": {"firstName": "Ayşe", "lastName": "Yılmaz"},
            "lines": [
                {"productName": "Kulaklık", "quantity": 2, "price": 149.95,
                 "commission": 20},
            ],
        }
    ],
}

BOS_TRENDYOL = {"content": [], "totalPages": 0, "totalElements": 0}

CICEKSEPETI_YANIT = {
    "supplierOrderListWithBranch": [
        {
            "orderId": "CS-9",
            "orderItemId": "1",
            "name": "Buket",
            "quantity": 1,
            "totalPrice": 450,
            "receiverName": "Mehmet Demir",
            "cargoNumber": "MRG99",
            "cargoCompany": "MNG Kargo",
            "orderCreateDate": "02/01/2026 10:00:00",
            "orderItemStatusId": 5,
            "cancellationResult": 1,
        }
    ],
}

BOS_CICEKSEPETI = {"supplierOrderListWithBranch": []}


@pytest.fixture(scope="module", autouse=True)
def ortam(tmp_path_factory):
    yol = tmp_path_factory.mktemp("db") / "entegrasyon.db"
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
    sonuc, icerik, _ = istek(taban, yol, metot, veri)
    return sonuc, icerik


def sahte_http(*yanitlar):
    """Sırayla (kod, gövde) döndüren sahte HTTP istemcisi."""
    durum = {"i": 0}

    def http(url, **kwargs):
        i = durum["i"]
        durum["i"] += 1
        cevap = yanitlar[min(i, len(yanitlar) - 1)]
        if isinstance(cevap, Exception):
            raise cevap
        if isinstance(cevap, Yanit):
            return cevap
        kod, veri = cevap
        return Yanit(kod, json.dumps(veri or {}), veri)

    return http


def test_platform_listesi():
    liste = entegrasyon.platform_listesi()
    assert len(liste) == 9
    ids = [p["id"] for p in liste]
    assert ids[0] == "trendyol" and "amazon" in ids
    for p in liste:
        assert p["ad"] and p["yetkinlik"] and p["alanlar"]
        assert all("id" in a and "ad" in a for a in p["alanlar"])
        zorunlu = [a for a in p["alanlar"] if a["zorunlu"]]
        assert zorunlu, p["id"]
        assert any(a["gizli"] for a in zorunlu), p["id"]


def test_kaydet_ve_sir_saklar(conn):
    kayit = entegrasyon.kaydet(
        conn, platform="trendyol", ad="Ana mağaza",
        ayarlar={"sellerId": "11"},
        kimlik={"apiKey": "super-gizli", "apiSecret": "gizli-2"},
    )
    assert kayit["id"] > 0
    assert kayit["ayarlar"]["sellerId"] == "11"
    assert kayit["dolu"] == ["apiKey", "apiSecret"]

    ham = json.dumps(entegrasyon.liste(conn), ensure_ascii=False)
    assert "super-gizli" not in ham
    assert "gizli-2" not in ham
    assert "sellerId" in ham


def test_kaydet_eksik_alan(conn):
    with pytest.raises(ValueError) as hata:
        entegrasyon.kaydet(conn, platform="trendyol", ad="Eksik",
                           ayarlar={}, kimlik={})
    assert "Eksik zorunlu alanlar" in str(hata.value)
    with pytest.raises(ValueError):
        entegrasyon.kaydet(conn, platform="yok-boyle", ad="X",
                           ayarlar={}, kimlik={})
    with pytest.raises(ValueError):
        entegrasyon.kaydet(conn, platform="trendyol", ad="   ",
                           ayarlar={"sellerId": "1"},
                           kimlik={"apiKey": "a", "apiSecret": "b"})


def test_kimlik_guncellenmeden_korunur(conn):
    entegrasyon.kaydet(
        conn, platform="n11", ad="N11 mağaza",
        ayarlar={}, kimlik={"appKey": "k1", "appSecret": "s1"},
    )
    entegrasyon.kaydet(
        conn, platform="n11", ad="N11 mağaza",
        ayarlar={"tabanAdres": "https://api.n11.com"}, kimlik={},
    )
    satirlar = entegrasyon.liste(conn)
    n11 = [k for k in satirlar if k["platform"] == "n11"][0]
    assert n11["dolu"] == ["appKey", "appSecret"]
    assert len([k for k in satirlar if k["platform"] == "n11"]) == 1


def test_sifre_akisi(tmp_path, monkeypatch):
    monkeypatch.setenv("OPS_DB", str(tmp_path / "s.db"))
    monkeypatch.setattr(sifre, "_FERNET", None)
    monkeypatch.setattr(sifre, "_FERNET_DENE", True)
    s = sifre.sifrele("hem-gizli-123")
    assert s.startswith("s:")
    assert sifre.coz(s) == "hem-gizli-123"

    bozuk = s[:-4] + "0000"
    with pytest.raises(ValueError):
        sifre.coz(bozuk)

    with pytest.raises(ValueError):
        sifre.coz("duz-metin-girisi")


def test_trendyol_normalizasyon():
    adaptör = entegrasyon.adaptör_al("trendyol")
    son = adaptör.cek(
        {"sellerId": "11"},
        {"apiKey": "a", "apiSecret": "b"},
        date(2026, 9, 1),
        date(2026, 9, 30),
        http=sahte_http((200, TRENDYOL_YANIT), (200, BOS_TRENDYOL)),
    )
    assert son["kod"] == 200
    assert len(son["siparisler"]) == 1
    s = son["siparisler"][0]
    assert s["dis_id"] == "555"
    assert s["siparis_no"] == "TY-1001"
    assert s["urun"] == "Kulaklık"
    assert s["adet"] == 2
    assert s["satis_fiyati"] == pytest.approx(299.90)
    assert s["durum"] == "kargoya_verildi"
    assert s["musteri"] == "Ayşe Yılmaz"
    assert s["komisyon_yuzde"] == 20
    assert s["gonderi"]["takip_no"] == "TYX123"
    assert s["gonderi"]["kargo_firmasi"] == "Trendyol Express"


def test_test_durumlari(conn):
    kayit = entegrasyon.kaydet(
        conn, platform="trendyol", ad="Test mağaza",
        ayarlar={"sellerId": "11"},
        kimlik={"apiKey": "a", "apiSecret": "b"},
    )
    basari = entegrasyon.test_et(
        conn, kayit, http=sahte_http((200, TRENDYOL_YANIT))
    )
    assert basari["durum"] == "ok"
    assert "1 kayıt okundu" in basari["mesaj"]

    taze = entegrasyon.satir(conn, kayit["id"])
    assert taze["son_test_sonuc"] == "ok"
    assert taze["son_test"]

    reddedilen = entegrasyon.test_et(
        conn, kayit, http=sahte_http((401, {"message": "unauthorized"}))
    )
    assert reddedilen["durum"] == "hata"
    assert "401" in reddedilen["mesaj"]
    assert entegrasyon.satir(conn, kayit["id"])["son_test_sonuc"] == "hata"

    ag = entegrasyon.test_et(
        conn, kayit,
        http=sahte_http(AgHatasi("SSLEOFError: bağlantı kesildi")),
    )
    assert ag["durum"] == "ag"
    assert "SSLEOFError" in ag["mesaj"]

    taninamayan = entegrasyon.test_et(
        conn, kayit,
        http=sahte_http((200, {"content": [{"bilinmeyen": 1}]}),
                        (200, {"content": [{"bilinmeyen": 1}]}),
                        (200, {"content": [{"bilinmeyen": 1}]}),
                        (200, {"content": [{"bilinmeyen": 1}]})),
    )
    assert taninamayan["durum"] == "uyari"
    assert "tanınamadı" in taninamayan["mesaj"]


def test_senkron_ve_tekrar(conn):
    kayit = entegrasyon.kaydet(
        conn, platform="trendyol", ad="Senkron mağaza",
        ayarlar={"sellerId": "11"},
        kimlik={"apiKey": "a", "apiSecret": "b"},
    )
    http = sahte_http((200, TRENDYOL_YANIT), (200, BOS_TRENDYOL))
    ilk = entegrasyon.senkron(conn, kayit, gun=30, http=http)
    assert ilk["durum"] == "ok"
    assert ilk["sayi"]["siparis_yeni"] == 1
    assert ilk["sayi"]["gonderi_yeni"] == 1

    satirlar = conn.execute("SELECT * FROM siparisler").fetchall()
    assert len(satirlar) == 1
    assert satirlar[0]["pazaryeri"] == "Trendyol"
    assert satirlar[0]["kaynak"] == "trendyol"
    assert satirlar[0]["dis_id"] == "555"
    assert satirlar[0]["satis_fiyati"] == pytest.approx(299.90)
    assert satirlar[0]["notlar"].startswith("Otomatik yüklendi")

    gonderi = conn.execute("SELECT * FROM gonderiler").fetchall()
    assert len(gonderi) == 1
    assert gonderi[0]["takip_no"] == "TYX123"
    assert gonderi[0]["kargo_firmasi"] == "Trendyol Express"

    tekrar = entegrasyon.senkron(
        conn, kayit, gun=30,
        http=sahte_http((200, BOS_TRENDYOL)),
    )
    assert tekrar["durum"] == "ok"
    assert len(conn.execute("SELECT * FROM siparisler").fetchall()) == 1
    assert len(conn.execute("SELECT * FROM gonderiler").fetchall()) == 1

    taze = entegrasyon.satir(conn, kayit["id"])
    assert taze["son_sync_sonuc"] == "ok"


def test_senkron_iade(conn):
    kayit = entegrasyon.kaydet(
        conn, platform="ciceksepeti", ad="Çiçekçi",
        ayarlar={"magazaId": "1234"}, kimlik={"apiKey": "anahtar"},
    )
    http = sahte_http((200, CICEKSEPETI_YANIT),
                      (200, BOS_CICEKSEPETI),
                      (200, BOS_CICEKSEPETI))
    son = entegrasyon.senkron(conn, kayit, gun=30, http=http)
    assert son["durum"] == "ok"
    assert son["sayi"]["siparis_yeni"] == 1
    assert son["sayi"]["gonderi_yeni"] == 1
    assert son["sayi"]["iade_yeni"] == 1

    siparis = conn.execute(
        "SELECT * FROM siparisler WHERE kaynak='ciceksepeti'"
    ).fetchone()
    assert siparis["durum"] == "iade"
    assert siparis["siparis_tarihi"] == "2026-01-02"

    iade = conn.execute("SELECT * FROM iadeler").fetchone()
    assert iade["tutar"] == pytest.approx(450)
    assert iade["talep_tarihi"] == "2026-01-02"
    assert iade["son_tarih"] == "2026-01-16"


def test_web_liste_ve_kayit(sunucu):
    d, _ = govde(sunucu, "/api/entegrasyonlar")
    assert len(d["platformlar"]) == 9
    assert all(p["alanlar"] for p in d["platformlar"])

    yeni, _ = govde(sunucu, "/api/entegrasyonlar", "POST", {
        "platform": "shopier", "ad": "Web mağaza",
        "ayarlar": {"tabanAdres": "https://api.shopier.com"},
        "kimlik": {"token": "PAT-COK-GIZLI"},
    })
    assert yeni["id"] > 0
    assert yeni["dolu"] == ["token"]

    liste, _ = govde(sunucu, "/api/entegrasyonlar")
    assert "PAT-COK-GIZLI" not in json.dumps(liste, ensure_ascii=False)
    assert "Web mağaza" in [k["ad"] for k in liste["liste"]]

    eksik, _ = govde(sunucu, "/api/entegrasyonlar", "POST",
                     {"platform": "shopier", "ad": "Boş", "kimlik": {}})
    assert "hata" in eksik

    silinen, _ = govde(sunucu, f"/api/entegrasyonlar/{yeni['id']}/sil",
                       "POST", {})
    assert silinen["silindi"] == yeni["id"]
    liste, _ = govde(sunucu, "/api/entegrasyonlar")
    assert all(k["id"] != yeni["id"] for k in liste["liste"])

    bulunamadi, _ = govde(sunucu, "/api/entegrasyonlar/9999/sil", "POST", {})
    assert "hata" in bulunamadi


def test_web_test_ve_senkron_rota(sunucu, monkeypatch):
    def sahte_test(conn, kayit=None, *, platform="", ayarlar=None,
                   kimlik=None, http=None):
        return {"durum": "ok", "kod": 200, "mesaj": "sahte test sonucu"}

    def sahte_senkron(conn, kayit, *, gun=30, http=None):
        return {"durum": "ok", "kod": 200, "mesaj": "sahte senkron",
                "gun": gun, "sayi": {"siparis_yeni": 3,
                                     "siparis_guncel": 1,
                                     "gonderi_yeni": 0, "gonderi_guncel": 0,
                                     "iade_yeni": 0, "iade_guncel": 0}}

    monkeypatch.setattr(entegrasyon, "test_et", sahte_test)
    monkeypatch.setattr(entegrasyon, "senkron", sahte_senkron)

    taslak, _ = govde(sunucu, "/api/entegrasyonlar/test", "POST", {
        "platform": "trendyol", "ayarlar": {"sellerId": "1"},
        "kimlik": {"apiKey": "a", "apiSecret": "b"},
    })
    assert taslak["durum"] == "ok"

    kayit, _ = govde(sunucu, "/api/entegrasyonlar", "POST", {
        "platform": "shopify", "ad": "Dükkan",
        "ayarlar": {"magaza": "dukkanim"},
        "kimlik": {"accessToken": "shpat_x"},
    })
    test_sonuc, _ = govde(sunucu, f"/api/entegrasyonlar/{kayit['id']}/test",
                          "POST", {})
    assert test_sonuc["durum"] == "ok"

    senkron_sonuc, _ = govde(
        sunucu, f"/api/entegrasyonlar/{kayit['id']}/senkron", "POST",
        {"gun": 7},
    )
    assert senkron_sonuc["gun"] == 7
    assert senkron_sonuc["sayi"]["siparis_yeni"] == 3

    yok, _ = govde(sunucu, "/api/entegrasyonlar/9999/test", "POST", {})
    assert "hata" in yok
