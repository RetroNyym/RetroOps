"""Yerel panel sunucusu: HTML + JSON API (stdlib http.server)."""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import __surum__, csv_io, entegrasyon, iade, kargo, kar, sikayet, trend
from .db import connect
from .sayfa import LOGO_SVG, PAGE


def _tarih_dogrula(metin: str) -> str:
    metin = str(metin or "").strip()
    if not metin:
        return date.today().isoformat()
    return date.fromisoformat(metin[:10]).isoformat()


def siparis_satiri(conn, satir) -> dict:
    veri = dict(satir)
    try:
        h = kar.hesap(
            alis=veri["alis_fiyati"],
            satis=veri["satis_fiyati"],
            komisyon_yuzde=veri.get("komisyon_yuzde", 0),
            kargo=veri["kargo_ucreti"],
            paket=veri["paket_maliyeti"],
            kdv=veri["kdv_orani"],
            diger_yuzde=veri.get("diger_yuzde", 0),
        )
        veri["kar"] = h["kar"]
        veri["marj_yuzde"] = h["marj_yuzde"]
    except ValueError:
        veri["kar"] = None
        veri["marj_yuzde"] = None
    return veri


def siparis_ozet(conn) -> dict:
    satirlar = conn.execute("SELECT * FROM siparisler").fetchall()
    ciro = kdv_haric = kar_toplam = 0.0
    dagilim: dict[str, int] = {}
    for s in satirlar:
        dagilim[s["durum"]] = dagilim.get(s["durum"], 0) + 1
        ciro += s["satis_fiyati"]
        kdv_haric += s["satis_fiyati"] / (1 + s["kdv_orani"] / 100)
        veri = siparis_satiri(conn, s)
        kar_toplam += veri["kar"] or 0.0
    return {
        "toplam": len(satirlar),
        "ciro": round(ciro, 2),
        "kdv_haric_ciro": round(kdv_haric, 2),
        "kar": round(kar_toplam, 2),
        "marj_yuzde": round(kar_toplam / kdv_haric * 100, 1) if kdv_haric else 0.0,
        "durum_dagilim": dagilim,
    }


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    # -- gönderim yardımcıları ------------------------------------------------
    def _gonder(self, kod: int, veri, tip: str = "application/json",
                ek: dict | None = None) -> None:
        if isinstance(veri, bytes):
            data = veri
        elif isinstance(veri, str):
            data = veri.encode("utf-8")
        else:
            data = json.dumps(veri, ensure_ascii=False).encode("utf-8")
        self.send_response(kod)
        self.send_header("Content-Type", f"{tip}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        for ad, deger in (ek or {}).items():
            self.send_header(ad, deger)
        self.end_headers()
        self.wfile.write(data)

    def _json(self, kod: int, obj) -> None:
        self._gonder(kod, obj)

    def _hata(self, kod: int, mesaj: str) -> None:
        self._json(kod, {"hata": mesaj})

    def _govde_json(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        ham = self.rfile.read(n) if n else b"{}"
        if not ham.strip():
            return {}
        veri = json.loads(ham.decode("utf-8"))
        if not isinstance(veri, dict):
            raise ValueError("Beklenen JSON nesnesi.")
        return veri

    def _govde_metin(self) -> str:
        n = int(self.headers.get("Content-Length") or 0)
        return (self.rfile.read(n) if n else b"").decode("utf-8", "replace")

    # -- GET ------------------------------------------------------------------
    def do_GET(self) -> None:
        adli = urlparse(self.path)
        yol = adli.path
        sorgu = parse_qs(adli.query)

        def al(ad: str, varsayilan: str = "") -> str:
            return sorgu.get(ad, [varsayilan])[0]

        try:
            if yol in ("/", "/index.html"):
                self._gonder(200, PAGE, "text/html")
            elif yol == "/logo.svg":
                self._gonder(200, LOGO_SVG, "image/svg+xml")
            elif yol == "/api/meta":
                self._json(200, self._meta())
            elif yol == "/api/ozet":
                conn = connect()
                try:
                    veri = {
                        "gun": date.today().isoformat(),
                        "surum": __surum__,
                        "siparis": siparis_ozet(conn),
                        "iade": iade.iade_ozet(conn),
                        "kargo": kargo.gonderi_ozet(conn),
                        "sikayet": sikayet.istatistik(conn),
                    }
                finally:
                    conn.close()
                self._json(200, veri)
            elif yol == "/api/siparisler":
                conn = connect()
                try:
                    satirlar = conn.execute(
                        "SELECT * FROM siparisler ORDER BY siparis_tarihi DESC, id DESC"
                    ).fetchall()
                    liste = [siparis_satiri(conn, s) for s in satirlar]
                finally:
                    conn.close()
                self._json(200, {"liste": liste})
            elif yol == "/api/iadeler":
                conn = connect()
                try:
                    liste = iade.iade_listesi(
                        conn, sadece_geciken=al("sadece") == "geciken"
                    )
                finally:
                    conn.close()
                self._json(200, {"liste": liste})
            elif yol == "/api/gonderiler":
                conn = connect()
                try:
                    liste = kargo.gonderi_listesi(
                        conn, sadece_problem=al("sadece") == "problem"
                    )
                finally:
                    conn.close()
                self._json(200, {"liste": liste})
            elif yol == "/api/sikayetler":
                conn = connect()
                try:
                    liste = sikayet.sikayet_listesi(conn)
                finally:
                    conn.close()
                self._json(200, {"liste": liste})
            elif yol == "/api/komisyonlar":
                self._json(200, {
                    "tablo": {
                        p: {k: {"alt": a, "ust": b, "orta": (a + b) / 2}
                            for k, (a, b) in kategoriler.items()}
                        for p, kategoriler in kar.KOMISYON_TABLOSU.items()
                    }
                })
            elif yol == "/api/kategoriler":
                self._json(200, {"liste": trend.kategori_listesi()})
            elif yol == "/api/trend":
                veri = trend.veri_cek(
                    al("anahtar") or "e-ticaret",
                    kategori=al("kategori", "e-ticaret"),
                    canli_dene=al("canli", "1") != "0",
                    zaman_asimi=int(al("zaman", "8")),
                )
                self._json(200, veri)
            elif yol == "/api/entegrasyonlar":
                conn = connect()
                try:
                    veri = {
                        "platformlar": entegrasyon.platform_listesi(),
                        "liste": entegrasyon.liste(conn),
                    }
                finally:
                    conn.close()
                self._json(200, veri)
            elif yol == "/api/export/csv":
                tablo = al("tablo")
                conn = connect()
                try:
                    metin = csv_io.disa_aktar(conn, tablo)
                finally:
                    conn.close()
                self._gonder(
                    200, metin, "text/csv",
                    {"Content-Disposition":
                     f'attachment; filename="{tablo}.csv"'},
                )
            elif yol == "/api/sablon":
                tablo = al("tablo")
                self._gonder(
                    200, csv_io.sablon_olustur(tablo), "text/csv",
                    {"Content-Disposition":
                     f'attachment; filename="{tablo}_sablon.csv"'},
                )
            else:
                self._hata(404, f"Bulunamadı: {yol}")
        except ValueError as e:
            self._hata(400, str(e))
        except Exception as e:  # ranel asla düşmesin
            self._hata(500, f"{type(e).__name__}: {e}")

    # -- POST -----------------------------------------------------------------
    def do_POST(self) -> None:
        adli = urlparse(self.path)
        yol = adli.path
        sorgu = parse_qs(adli.query)

        def al(ad: str, varsayilan: str = "") -> str:
            return sorgu.get(ad, [varsayilan])[0]

        try:
            if yol == "/api/siparisler":
                self._json(201, self._siparis_ekle(self._govde_json()))
            elif yol == "/api/iadeler":
                self._json(201, self._iade_ekle(self._govde_json()))
            elif yol == "/api/gonderiler":
                self._json(201, self._gonderi_ekle(self._govde_json()))
            elif yol == "/api/sikayetler":
                self._json(201, self._sikayet_ekle(self._govde_json()))
            elif (m := re.fullmatch(r"/api/iadeler/(\d+)/durum", yol)):
                veri = self._govde_json()
                conn = connect()
                try:
                    sonuc = iade.durum_degistir(
                        conn, int(m.group(1)), str(veri.get("durum", ""))
                    )
                finally:
                    conn.close()
                self._json(200, sonuc)
            elif (m := re.fullmatch(r"/api/gonderiler/(\d+)/durum", yol)):
                veri = self._govde_json()
                conn = connect()
                try:
                    sonuc = kargo.durum_degistir(
                        conn,
                        int(m.group(1)),
                        str(veri.get("durum", "")),
                        sorun_tipi=veri.get("sorun_tipi"),
                    )
                finally:
                    conn.close()
                self._json(200, sonuc)
            elif (m := re.fullmatch(r"/api/sikayetler/(\d+)/durum", yol)):
                veri = self._govde_json()
                conn = connect()
                try:
                    sonuc = sikayet.durum_degistir(
                        conn, int(m.group(1)), str(veri.get("durum", ""))
                    )
                finally:
                    conn.close()
                self._json(200, sonuc)
            elif yol == "/api/hesapla":
                self._json(200, kar.hesapla_ve_fiyat_ara(self._govde_json()))
            elif yol == "/api/import/csv":
                tablo = al("tablo", "siparisler")
                if tablo != "siparisler":
                    raise ValueError(
                        "Toplu yükleme yalnızca 'siparisler' tablosu için "
                        "desteklenir."
                    )
                metin = self._govde_metin()
                if not metin.strip():
                    raise ValueError("Boş dosya.")
                conn = connect()
                try:
                    sonuc = csv_io.siparisleri_aktar(conn, metin)
                finally:
                    conn.close()
                self._json(200, sonuc)
            elif yol == "/api/entegrasyonlar":
                v = self._govde_json()
                conn = connect()
                try:
                    kayit = entegrasyon.kaydet(
                        conn,
                        platform=str(v.get("platform") or ""),
                        ad=str(v.get("ad") or ""),
                        ayarlar=v.get("ayarlar") or {},
                        kimlik=v.get("kimlik") or {},
                    )
                finally:
                    conn.close()
                self._json(201, kayit)
            elif yol == "/api/entegrasyonlar/test":
                v = self._govde_json()
                conn = connect()
                try:
                    sonuc = entegrasyon.test_et(
                        conn,
                        None,
                        platform=str(v.get("platform") or ""),
                        ayarlar=v.get("ayarlar") or {},
                        kimlik=v.get("kimlik") or {},
                    )
                finally:
                    conn.close()
                self._json(200, sonuc)
            elif (m := re.fullmatch(r"/api/entegrasyonlar/(\d+)/test", yol)):
                conn = connect()
                try:
                    kayit = entegrasyon.satir(conn, int(m.group(1)))
                    if kayit is None:
                        self._hata(404, f"Bağlantı bulunamadı: {m.group(1)}")
                        return
                    sonuc = entegrasyon.test_et(conn, kayit)
                finally:
                    conn.close()
                self._json(200, sonuc)
            elif (m := re.fullmatch(r"/api/entegrasyonlar/(\d+)/senkron", yol)):
                v = self._govde_json()
                gun = int(v.get("gun") or 30)
                conn = connect()
                try:
                    kayit = entegrasyon.satir(conn, int(m.group(1)))
                    if kayit is None:
                        self._hata(404, f"Bağlantı bulunamadı: {m.group(1)}")
                        return
                    sonuc = entegrasyon.senkron(conn, kayit, gun=gun)
                finally:
                    conn.close()
                self._json(200, sonuc)
            elif (m := re.fullmatch(r"/api/entegrasyonlar/(\d+)/sil", yol)):
                conn = connect()
                try:
                    sonuc = entegrasyon.sil(conn, int(m.group(1)))
                finally:
                    conn.close()
                self._json(200, sonuc)
            else:
                self._hata(404, f"Bulunamadı: {yol}")
        except ValueError as e:
            self._hata(400, str(e))
        except json.JSONDecodeError:
            self._hata(400, "Geçersiz JSON gövdesi.")
        except Exception as e:
            self._hata(500, f"{type(e).__name__}: {e}")

    # -- POST yardımcıları ----------------------------------------------------
    def _siparis_ekle(self, v: dict) -> dict:
        urun = str(v.get("urun", "")).strip()
        if not urun:
            raise ValueError("Ürün adı zorunlu.")
        satis = float(v.get("satis_fiyati") or 0)
        if satis <= 0:
            raise ValueError("Satış fiyatı 0'dan büyük olmalı.")
        durum = str(v.get("durum") or "hazirlaniyor")
        if durum not in csv_io.SIPARIS_DURUMLARI:
            raise ValueError(f"Geçersiz sipariş durumu: {durum}")
        conn = connect()
        try:
            cur = conn.execute(
                """INSERT INTO siparisler
                   (pazaryeri, siparis_no, urun, adet, alis_fiyati,
                    satis_fiyati, komisyon_yuzde, kargo_ucreti,
                    paket_maliyeti, kdv_orani, diger_yuzde, musteri,
                    siparis_tarihi, durum, notlar)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    str(v.get("pazaryeri") or "Diger"),
                    str(v.get("siparis_no") or ""),
                    urun,
                    int(float(v.get("adet") or 1) or 1),
                    float(v.get("alis_fiyati") or 0),
                    satis,
                    float(v.get("komisyon_yuzde") or 0),
                    float(v.get("kargo_ucreti") or 0),
                    float(v.get("paket_maliyeti") or 0),
                    float(v.get("kdv_orani") if v.get("kdv_orani") not in
                           (None, "") else 20),
                    float(v.get("diger_yuzde") or 0),
                    str(v.get("musteri") or ""),
                    _tarih_dogrula(v.get("siparis_tarihi")),
                    durum,
                    str(v.get("notlar") or ""),
                ),
            )
            conn.commit()
            yeni = conn.execute(
                "SELECT * FROM siparisler WHERE id=?", (cur.lastrowid,)
            ).fetchone()
            return siparis_satiri(conn, yeni)
        finally:
            conn.close()

    def _iade_ekle(self, v: dict) -> dict:
        siparis_id = v.get("siparis_id")
        tutar = float(v.get("tutar") or 0)
        conn = connect()
        try:
            if siparis_id:
                var = conn.execute(
                    "SELECT id FROM siparisler WHERE id=?", (int(siparis_id),)
                ).fetchone()
                if var is None:
                    raise ValueError(f"Sipariş bulunamadı: {siparis_id}")
                siparis_id = int(siparis_id)
            else:
                siparis_id = None
            yeni_id = iade.iade_ekle(
                conn,
                siparis_id=siparis_id,
                musteri=str(v.get("musteri") or ""),
                tutar=tutar,
                sebep=str(v.get("sebep") or ""),
                talep_tarihi=v.get("talep_tarihi") or None,
                notlar=str(v.get("notlar") or ""),
            )
            satir = conn.execute(
                "SELECT * FROM iadeler WHERE id=?", (yeni_id,)
            ).fetchone()
            return iade.satirye_don(satir)
        finally:
            conn.close()

    def _gonderi_ekle(self, v: dict) -> dict:
        firma = str(v.get("kargo_firmasi") or "").strip()
        if not firma:
            raise ValueError("Kargo firması zorunlu.")
        conn = connect()
        try:
            yeni_id = kargo.gonderi_ekle(
                conn,
                kargo_firmasi=firma,
                gonderim_tarihi=str(v.get("gonderim_tarihi") or ""),
                tahmini_teslim=str(v.get("tahmini_teslim") or ""),
                takip_no=str(v.get("takip_no") or ""),
                siparis_id=int(v["siparis_id"]) if v.get("siparis_id") else None,
                son_durum=str(v.get("son_durum") or "yolda"),
                notlar=str(v.get("notlar") or ""),
            )
            satir = conn.execute(
                "SELECT * FROM gonderiler WHERE id=?", (yeni_id,)
            ).fetchone()
            return kargo.satirye_don(satir)
        finally:
            conn.close()

    def _sikayet_ekle(self, v: dict) -> dict:
        conn = connect()
        try:
            yeni_id = sikayet.sikayet_ekle(
                conn,
                kategori=str(v.get("kategori") or ""),
                konu=str(v.get("konu") or ""),
                tarih=v.get("tarih") or None,
                kaynak=str(v.get("kaynak") or "musteri"),
                siparis_id=int(v["siparis_id"]) if v.get("siparis_id") else None,
                notlar=str(v.get("notlar") or ""),
            )
            satir = conn.execute(
                "SELECT * FROM sikayetler WHERE id=?", (yeni_id,)
            ).fetchone()
            return sikayet.satirye_don(satir)
        finally:
            conn.close()

    def _meta(self) -> dict:
        return {
            "surum": __surum__,
            "gun": datetime.now().isoformat(timespec="seconds"),
            "iade_durumlari": [
                {"id": d, "ad": iade.ETIKETLER[d]} for d in iade.DURUMLAR
            ],
            "iade_gecisler": {k: list(v) for k, v in iade.GECISLER.items()},
            "sebepler": list(iade.SEBEPLER),
            "kargo_firmalari": list(kargo.KARGO_FIRMALARI),
            "kargo_durumlari": [
                {"id": d, "ad": kargo.ETIKETLER[d]} for d in kargo.DURUMLAR
            ],
            "sorun_tipleri": [
                {"id": s, "ad": kargo.SORUN_ETIKETLERI[s]}
                for s in kargo.SORUN_TIPLERI
            ],
            "sikayet_kategorileri": [
                {"id": k, "ad": ad} for k, ad in sikayet.KATEGORILER.items()
            ],
            "sikayet_kaynaklari": [
                {"id": k, "ad": ad} for k, ad in sikayet.KAYNAKLAR.items()
            ],
            "sikayet_durumlari": [
                {"id": d, "ad": sikayet.DURUM_ETIKETLER[d]}
                for d in sikayet.DURUMLAR
            ],
            "pazaryerleri": list(kar.KOMISYON_TABLOSU.keys()),
            "siparis_durumlari": list(csv_io.SIPARIS_DURUMLARI),
            "csv_tablolari": list(csv_io.TABLOLAR),
            "trend_kategorileri": trend.kategori_listesi(),
        }


def main(port: int = 8780) -> None:
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"RetroOps E-Ticaret Operasyon: http://127.0.0.1:{port}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 8780
    main(p)
