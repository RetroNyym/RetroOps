"""Ağdan gelen normalize kayıtların veritabanına yazılması.

Yazım ``kaynak`` + ``dis_id`` üzerinden tekrarlanabilir (idempotent): aynı
kayıt ikinci senkronda çoğaltılmaz, güncellenir. Alış/kâr maliyeti alanlarına
dokunulmaz çünkü platform API'leri bu bilgiyi vermez.
"""

from __future__ import annotations

import sqlite3
from datetime import date, timedelta

from . import iade as iade_mod
from . import kargo as kargo_mod

GUNLER = ("siparis_yeni", "siparis_guncel", "gonderi_yeni", "gonderi_guncel",
          "iade_yeni", "iade_guncel", "atlandi")


def _metin(deger) -> str:
    return "" if deger is None else str(deger).strip()


def _tarih(deger, varsayilan: str) -> str:
    try:
        return date.fromisoformat(str(deger)[:10]).isoformat()
    except (TypeError, ValueError):
        return varsayilan


def _sifirla() -> dict:
    return {ad: 0 for ad in GUNLER}


def kaydet(conn: sqlite3.Connection, *, kaynak: str, pazaryeri: str,
           siparisler: list[dict]) -> dict:
    """Normalize kayıtları ``siparisler``/``gonderiler``/``iadeler``e yazar."""
    say = _sifirla()
    for s in siparisler:
        dis = _metin(s.get("dis_id"))
        if not dis:
            say["atlandi"] += 1
            continue
        tarih = _tarih(s.get("siparis_tarihi"), date.today().isoformat())
        satis = float(s.get("satis_fiyati") or 0)
        if satis <= 0:
            say["atlandi"] += 1
            continue
        urun = _metin(s.get("urun")) or "Pazaryeri siparişi"
        durum = _metin(s.get("durum")) or "hazirlaniyor"
        if durum not in ("hazirlaniyor", "kargoya_verildi", "teslim", "iade",
                         "iade_tamam", "iptal"):
            durum = "hazirlaniyor"
        komisyon = float(s.get("komisyon_yuzde") or 0)
        notlar = _metin(s.get("notlar")) or f"Otomatik yüklendi ({kaynak})"

        mevcut = conn.execute(
            "SELECT * FROM siparisler WHERE kaynak=? AND dis_id=? "
            "AND dis_id!=''",
            (kaynak, dis),
        ).fetchone()
        if mevcut:
            siparis_id = int(mevcut["id"])
            conn.execute(
                """UPDATE siparisler SET urun=?, adet=?, satis_fiyati=?,
                   musteri=?, siparis_tarihi=?, durum=?, komisyon_yuzde=?,
                   notlar=? WHERE id=?""",
                (
                    urun,
                    max(1, int(s.get("adet") or 1)),
                    satis,
                    _metin(s.get("musteri")),
                    tarih,
                    durum,
                    komisyon if komisyon > 0 else float(
                        mevcut["komisyon_yuzde"] or 0
                    ),
                    _metin(mevcut["notlar"]) or notlar,
                    siparis_id,
                ),
            )
            say["siparis_guncel"] += 1
        else:
            cur = conn.execute(
                """INSERT INTO siparisler
                   (pazaryeri, siparis_no, urun, adet, alis_fiyati,
                    satis_fiyati, komisyon_yuzde, kargo_ucreti,
                    paket_maliyeti, kdv_orani, diger_yuzde, musteri,
                    siparis_tarihi, durum, notlar, kaynak, dis_id)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    pazaryeri,
                    _metin(s.get("siparis_no")),
                    urun,
                    max(1, int(s.get("adet") or 1)),
                    0.0,
                    satis,
                    komisyon,
                    0.0,
                    0.0,
                    20.0,
                    0.0,
                    _metin(s.get("musteri")),
                    tarih,
                    durum,
                    notlar,
                    kaynak,
                    dis,
                ),
            )
            siparis_id = int(cur.lastrowid)
            say["siparis_yeni"] += 1

        if isinstance(s.get("gonderi"), dict):
            _gonderi_yaz(conn, say, kaynak, dis, siparis_id, s["gonderi"],
                         bugun=tarih)
        if isinstance(s.get("iade"), dict):
            _iade_yaz(conn, say, kaynak, dis, siparis_id, s["iade"])

    conn.commit()
    return say


def _gonderi_yaz(conn, say, kaynak, dis, siparis_id, g, bugun) -> None:
    takip = _metin(g.get("takip_no"))
    firma = _metin(g.get("kargo_firmasi")) or "Diger"
    gonderim = _tarih(g.get("gonderim_tarihi"), bugun)
    tahmini = _tarih(g.get("tahmini_teslim"), gonderim)
    durum = _metin(g.get("son_durum"))
    if durum not in kargo_mod.DURUMLAR:
        durum = "yolda"
    if not takip:
        say["atlandi"] += 1
        return

    mevcut = conn.execute(
        "SELECT id FROM gonderiler WHERE kaynak=? AND dis_id=? "
        "AND dis_id!=''",
        (kaynak, dis),
    ).fetchone()
    if mevcut:
        conn.execute(
            """UPDATE gonderiler SET siparis_id=?, kargo_firmasi=?,
               takip_no=?, gonderim_tarihi=?, tahmini_teslim=?,
               son_durum=? WHERE id=?""",
            (siparis_id, firma, takip, gonderim, tahmini, durum,
             int(mevcut["id"])),
        )
        say["gonderi_guncel"] += 1
    else:
        conn.execute(
            """INSERT INTO gonderiler
               (siparis_id, kargo_firmasi, takip_no, gonderim_tarihi,
                tahmini_teslim, son_durum, notlar, kaynak, dis_id)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (siparis_id, firma, takip, gonderim, tahmini, durum,
             _metin(g.get("notlar")), kaynak, dis),
        )
        say["gonderi_yeni"] += 1


def _iade_yaz(conn, say, kaynak, dis, siparis_id, i) -> None:
    tutar = float(i.get("tutar") or 0)
    if tutar <= 0:
        say["atlandi"] += 1
        return
    talep = _tarih(i.get("talep_tarihi"), date.today().isoformat())
    son_tarih = (date.fromisoformat(talep)
                 + timedelta(days=iade_mod.SURE_GUN)).isoformat()
    sebep = _metin(i.get("sebep")) or "Diğer"
    notlar = _metin(i.get("notlar"))
    musteri = _metin(i.get("musteri"))

    mevcut = conn.execute(
        "SELECT * FROM iadeler WHERE kaynak=? AND dis_id=? AND dis_id!=''",
        (kaynak, dis),
    ).fetchone()
    if mevcut:
        conn.execute(
            """UPDATE iadeler SET tutar=?, talep_tarihi=?, son_tarih=?,
               siparis_id=?, musteri=CASE WHEN musteri='' THEN ? ELSE
               musteri END, sebep=CASE WHEN sebep='' THEN ? ELSE sebep END
               WHERE id=?""",
            (tutar, talep, son_tarih, siparis_id, musteri, sebep,
             int(mevcut["id"])),
        )
        say["iade_guncel"] += 1
        return

    cur = conn.execute(
        """INSERT INTO iadeler
           (siparis_id, musteri, tutar, sebep, talep_tarihi, son_tarih,
            durum, notlar, kaynak, dis_id)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (siparis_id, musteri, tutar, sebep, talep, son_tarih, "talep",
         notlar, kaynak, dis),
    )
    if cur.lastrowid:
        conn.execute(
            "UPDATE siparisler SET durum='iade' WHERE id=?", (siparis_id,)
        )
    say["iade_yeni"] += 1
