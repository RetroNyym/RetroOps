"""SMS entegrasyonu: kod üretimi/etkinleştirme, ayarlar, gönderim ve rotalar."""

import base64
import json
import os
import threading
from datetime import date
from http.server import ThreadingHTTPServer

import pytest

from ops import sms, web
from ops.adapters.temel import AgHatasi, Yanit
from ops.db import connect
from ops.lisans import makine_id


@pytest.fixture(scope="module", autouse=True)
def ortam(tmp_path_factory):
    yol = tmp_path_factory.mktemp("db") / "sms.db"
    os.environ["OPS_DB"] = str(yol)
    sms.kaldir()
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
    """Sırayla yanıtları döndüren ve isteği kaydeden sahte istemci."""
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


def etkinlestir():
    return sms.etkinlestir(sms.kod_uret())


def test_kod_uret_ve_coz():
    kod = sms.kod_uret("aabbccddeeff0011")
    assert kod.startswith("SMS-")
    coz = sms.kod_coz(kod)
    assert coz == {"makine": "aabbccddeeff0011",
                   "tarih": date.today().isoformat()}
    assert sms.kod_coz("SMS-BOZUK-KOD") is None
    assert sms.kod_coz("RETROOPS-ABCDE") is None
    assert sms.kod_coz("") is None


def test_etkinlestir_kaldir():
    assert sms.durum()["etkin"] is False
    with pytest.raises(ValueError) as hata:
        sms.etkinlestir("SMS-12345-67890")
    assert "geçersiz" in str(hata.value)

    baska = sms.kod_uret("0000000000000000")
    with pytest.raises(ValueError) as hata:
        sms.etkinlestir(baska)
    assert "başka bir bilgisayara" in str(hata.value)
    assert sms.durum()["etkin"] is False

    son = etkinlestir()
    assert son["etkin"] is True
    assert son["makine"] == makine_id()
    assert son["kod"].startswith("SMS-")
    assert son["kod"].endswith("…")

    kilitli = sms.kaldir()
    assert kilitli["etkin"] is False
    assert not kilitli["kod"]


def test_ayar_kaydet_sifre_saklanir():
    with pytest.raises(ValueError) as hata:
        sms.ayar_yaz({"kullanici": "", "parola": "s"})
    assert "Kullanıcı kodu" in str(hata.value)
    with pytest.raises(ValueError) as hata:
        sms.ayar_yaz({"kullanici": "5XX0001"})
    assert "şifresi" in str(hata.value).lower()

    son = sms.ayar_yaz({"kullanici": "5XX0001", "parola": "gizli-sifre-99",
                        "baslik": "MAGAZAM"})
    assert son["kullanici"] == "5XX0001"
    assert son["parola_var"] is True
    assert "parola" not in son
    assert "gizli-sifre-99" not in json.dumps(son, ensure_ascii=False)

    ham = sms.sms_yolu().read_text(encoding="utf-8")
    assert "gizli-sifre-99" not in ham
    assert "5XX0001" in ham

    # şifre boş gönderildiğinde eskisi korunur
    guncel = sms.ayar_yaz({"kullanici": "5XX0002", "parola": ""})
    assert guncel["kullanici"] == "5XX0002"
    assert guncel["parola_var"] is True


def test_tel_no_dogrulama():
    assert sms.tel_no("0532 123 45 67") == "5321234567"
    assert sms.tel_no("+90 532 123 45 67") == "5321234567"
    assert sms.tel_no("905321234567") == "5321234567"
    for hatali in ("12345", "02121234567", "", "abcdef"):
        with pytest.raises(ValueError):
            sms.tel_no(hatali)


def test_gonder_kilitli(conn):
    with pytest.raises(ValueError) as hata:
        sms.gonder(conn, "05321234567", "Merhaba")
    assert "kilitli" in str(hata.value)


def test_gonder_basarili_ve_gecmis(conn):
    etkinlestir()
    with pytest.raises(ValueError) as hata:
        sms.gonder(conn, "05321234567", "")
    assert "boş" in str(hata.value)
    with pytest.raises(ValueError) as hata:
        sms.gonder(conn, "02121234567", "Merhaba")
    assert "Geçersiz telefon" in str(hata.value)

    # gönderici ayarları henüz kaydedilmemişken net hata
    kayit = sms._kayit_oku()
    kayit["ayarlar"] = {}
    sms._kayit_yaz(kayit)
    with pytest.raises(ValueError) as hata:
        sms.gonder(conn, "05321234567", "Merhaba")
    assert "ayarları girilmemiş" in str(hata.value)

    sms.ayar_yaz({"kullanici": "5XX0001", "parola": "sir", "baslik": "DEMO"})
    http, cagri = yakalayici((200, {"status": {"code": "200",
                                               "description": "Mesaj kabul"}}))
    son = sms.gonder(conn, "0532 123 45 67", "Siparişiniz kargoya verildi",
                     http=http)
    assert son["durum"] == "ok"
    assert son["alici"] == "5321234567"
    assert "Mesaj kabul" in son["mesaj"]

    cagri_ = cagri[0]
    assert cagri_["metot"] == "POST"
    assert cagri_["govde"]["sender"] == "DEMO"
    assert cagri_["govde"]["messages"][0]["receipents"][0]["no"] == \
        "905321234567"
    beklenen = base64.b64encode(b"5XX0001:sir").decode()
    assert cagri_["basliklar"]["Authorization"] == "Basic " + beklenen

    gecmis = sms.gecmis(conn)
    assert gecmis[0]["durum"] == "ok"
    assert gecmis[0]["alici"] == "5321234567"
    assert "kargoya verildi" in gecmis[0]["mesaj"]

    hatali, _ = yakalayici((200, {"status": {"code": "105",
                                             "description": "Başlık kayıtlı değil"}}))
    son = sms.gonder(conn, "05321234567", "Deneme", http=hatali)
    assert son["durum"] == "hata"
    assert "Başlık kayıtlı değil" in son["mesaj"]

    ag, _ = yakalayici(AgHatasi("SSLEOFError: kesildi"))
    son = sms.gonder(conn, "05321234567", "Deneme", http=ag)
    assert son["durum"] == "ag"
    assert "SSLEOFError" in son["mesaj"]

    gecmis = sms.gecmis(conn)
    assert [g["durum"] for g in gecmis[:3]] == ["hata", "hata", "ok"]


def test_hatali_http_kodu(conn):
    http, _ = yakalayici((401, {"message": "unauthorized"}))
    son = sms.gonder(conn, "05321234567", "Deneme", http=http)
    assert son["durum"] == "hata"
    assert son["kod"] == 401
    assert "401" in son["mesaj"]


def test_web_rota(sunucu, monkeypatch):
    kilit, kod = istek(sunucu, "/api/sms/kaldir", "POST", {})
    assert kod == 200
    assert kilit["etkin"] is False

    d, kod = istek(sunucu, "/api/sms")
    assert kod == 200
    assert d["durum"]["etkin"] is False
    assert d["durum"]["makine"] == makine_id()
    assert d["ayarlar"]["saglayici"] == "Netgsm"
    assert isinstance(d["gecmis"], list)

    kodd = sms.kod_uret()
    son, kod = istek(sunucu, "/api/sms/etkinlestir", "POST", {"kod": kodd})
    assert kod == 200
    assert son["etkin"] is True

    gecersiz, kod = istek(sunucu, "/api/sms/etkinlestir", "POST",
                          {"kod": "SMS-HATALI"})
    assert kod == 400
    assert "geçersiz" in gecersiz["hata"]

    ayar, kod = istek(sunucu, "/api/sms/ayar", "POST",
                      {"kullanici": "5XX9", "parola": "sir", "baslik": "DEMO"})
    assert kod == 200
    assert ayar["parola_var"] is True

    def sahte_gonder(conn, alici, mesaj, *, http=None):
        return {"durum": "ok", "kod": 200, "mesaj": "sahte gönderim",
                "alici": alici}

    monkeypatch.setattr(sms, "gonder", sahte_gonder)
    gonderilen, kod = istek(sunucu, "/api/sms/gonder", "POST",
                            {"alici": "05321234567", "mesaj": "Merhaba"})
    assert kod == 200
    assert gonderilen["durum"] == "ok"

    liste, kod = istek(sunucu, "/api/sms")
    assert kod == 200
    assert liste["durum"]["etkin"] is True
    assert "sir" not in json.dumps(liste, ensure_ascii=False)

    kilit, kod = istek(sunucu, "/api/sms/kaldir", "POST", {})
    assert kod == 200
    assert kilit["etkin"] is False
