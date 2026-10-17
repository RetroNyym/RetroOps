"""SQLite şeması ve bağlantı yardımcıları."""

from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
from pathlib import Path


def _exe_yolu() -> Path:
    """Derlenmiş programda ``.exe``nin gerçek (kalıcı) yolu."""
    for aday in (sys.executable, sys.argv[0] if sys.argv else ""):
        if aday:
            try:
                return Path(aday).resolve()
            except OSError:
                continue
    return Path.cwd()


def _kararli_klasor(klasor: Path) -> bool:
    """Bu klasöre veri yazmak güvenli mi? (geçici/zip klasörü değil, yazılabilir)"""
    try:
        if klasor == Path(tempfile.gettempdir()) or klasor.is_relative_to(
                Path(tempfile.gettempdir())):
            return False
        deneme = klasor / ".yazma-denemesi"
        deneme.write_text("ok", encoding="utf-8")
        deneme.unlink()
        return True
    except OSError:
        return False


_KOK_ONBELLEK: Path | None = None


def kok_dizin() -> Path:
    """Veri klasörünün kökü.

    - Kaynak kodda proje kökü kullanılır.
    - Derlenmiş ``.exe``de program yanındaki ``data/`` klasörü kullanılır
      (onefile tek dosya olsa bile ``exe``nin yanındaki klasör; geçici
      açılma klasörü asla veri için kullanılmaz).
    - Program zip içinden ya da salt-okunur bir klasörden çalıştırılıyorsa
      veri ``%LOCALAPPDATA%\\RetroOps`` altına yazılır; kullanıcı verisi
      hiçbir koşulda kaybolmaz.
    """
    global _KOK_ONBELLEK
    if _KOK_ONBELLEK is not None:
        return _KOK_ONBELLEK
    if not getattr(sys, "frozen", False):
        _KOK_ONBELLEK = Path(__file__).resolve().parent.parent
        return _KOK_ONBELLEK
    exe_klasor = _exe_yolu().parent
    if _kararli_klasor(exe_klasor):
        _KOK_ONBELLEK = exe_klasor
    else:
        yerel = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "RetroOps"
        try:
            yerel.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        _KOK_ONBELLEK = yerel
    return _KOK_ONBELLEK


DB_YOL = kok_dizin() / "data" / "ops.db"


def varsayilan_yol() -> Path:
    """``OPS_DB`` ortam değişkeni test/sandbox için yolun üstüne biner."""
    ortam = os.environ.get("OPS_DB")
    return Path(ortam) if ortam else DB_YOL

SCHEMA = """
CREATE TABLE IF NOT EXISTS siparisler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pazaryeri TEXT NOT NULL DEFAULT 'Diger',
    siparis_no TEXT NOT NULL DEFAULT '',
    urun TEXT NOT NULL,
    adet INTEGER NOT NULL DEFAULT 1,
    alis_fiyati REAL NOT NULL DEFAULT 0,
    satis_fiyati REAL NOT NULL,
    komisyon_yuzde REAL NOT NULL DEFAULT 0,
    kargo_ucreti REAL NOT NULL DEFAULT 0,
    paket_maliyeti REAL NOT NULL DEFAULT 0,
    kdv_orani REAL NOT NULL DEFAULT 20,
    diger_yuzde REAL NOT NULL DEFAULT 0,
    musteri TEXT NOT NULL DEFAULT '',
    siparis_tarihi TEXT NOT NULL,
    durum TEXT NOT NULL DEFAULT 'hazirlaniyor',
    notlar TEXT NOT NULL DEFAULT '',
    olusturma TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS iadeler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    siparis_id INTEGER REFERENCES siparisler(id) ON DELETE SET NULL,
    musteri TEXT NOT NULL DEFAULT '',
    tutar REAL NOT NULL DEFAULT 0,
    sebep TEXT NOT NULL DEFAULT '',
    talep_tarihi TEXT NOT NULL,
    son_tarih TEXT NOT NULL,
    durum TEXT NOT NULL DEFAULT 'talep',
    cozum_tarihi TEXT,
    notlar TEXT NOT NULL DEFAULT '',
    olusturma TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS gonderiler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    siparis_id INTEGER REFERENCES siparisler(id) ON DELETE SET NULL,
    kargo_firmasi TEXT NOT NULL,
    takip_no TEXT NOT NULL DEFAULT '',
    gonderim_tarihi TEXT NOT NULL,
    tahmini_teslim TEXT NOT NULL,
    son_durum TEXT NOT NULL DEFAULT 'hazir',
    sorun_tipi TEXT NOT NULL DEFAULT '',
    notlar TEXT NOT NULL DEFAULT '',
    olusturma TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sikayetler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kaynak TEXT NOT NULL DEFAULT 'musteri',
    kategori TEXT NOT NULL,
    konu TEXT NOT NULL DEFAULT '',
    tarih TEXT NOT NULL,
    durum TEXT NOT NULL DEFAULT 'acik',
    cozum_tarihi TEXT,
    siparis_id INTEGER REFERENCES siparisler(id) ON DELETE SET NULL,
    notlar TEXT NOT NULL DEFAULT '',
    olusturma TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS entegrasyonlar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    ad TEXT NOT NULL,
    ayarlar TEXT NOT NULL DEFAULT '{}',
    kimlik TEXT NOT NULL DEFAULT '',
    son_test TEXT,
    son_test_sonuc TEXT,
    son_test_mesaj TEXT,
    son_sync TEXT,
    son_sync_sonuc TEXT,
    son_sync_sayi INTEGER NOT NULL DEFAULT 0,
    aktif INTEGER NOT NULL DEFAULT 1,
    olusturma TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (platform, ad)
);

CREATE TABLE IF NOT EXISTS sms_gonderim (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alici TEXT NOT NULL,
    mesaj TEXT NOT NULL,
    baslik TEXT NOT NULL DEFAULT '',
    gonderim_zamani TEXT NOT NULL DEFAULT (datetime('now')),
    durum TEXT NOT NULL DEFAULT 'ok',
    http_kod INTEGER,
    sonuc TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_iadeler_durum ON iadeler(durum);
CREATE INDEX IF NOT EXISTS idx_gonderiler_durum ON gonderiler(son_durum);
CREATE INDEX IF NOT EXISTS idx_sikayetler_kategori ON sikayetler(kategori);
"""


def _gecisler(conn: sqlite3.Connection) -> None:
    """Eski şemalardan yeni alanlara taşıma."""
    alanlar = {
        r["name"] for r in conn.execute("PRAGMA table_info(siparisler)")
    }
    if "komisyon_yuzde" not in alanlar:
        conn.execute(
            "ALTER TABLE siparisler ADD COLUMN komisyon_yuzde "
            "REAL NOT NULL DEFAULT 0"
        )
    for tablo in ("siparisler", "gonderiler", "iadeler"):
        sutunlar = {
            r["name"] for r in conn.execute(f"PRAGMA table_info({tablo})")
        }
        if "kaynak" not in sutunlar:
            conn.execute(
                f"ALTER TABLE {tablo} ADD COLUMN kaynak "
                "TEXT NOT NULL DEFAULT ''"
            )
        if "dis_id" not in sutunlar:
            conn.execute(
                f"ALTER TABLE {tablo} ADD COLUMN dis_id "
                "TEXT NOT NULL DEFAULT ''"
            )
        conn.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{tablo}_dis "
            f"ON {tablo}(kaynak, dis_id) WHERE dis_id != ''"
        )


def connect(db_yol: Path | str | None = None) -> sqlite3.Connection:
    """Şeması garanti edilmiş bir bağlantı döndürür."""
    yol = Path(db_yol) if db_yol else varsayilan_yol()
    yol.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(yol))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    _gecisler(conn)
    conn.commit()
    return conn


ZORUNLU_TABLOLAR = {"siparisler", "iadeler", "gonderiler",
                    "sikayetler", "entegrasyonlar"}


def yedek_indir() -> bytes:
    """Veritabanının ham kopyasını döndürür."""
    yol = varsayilan_yol()
    conn = connect()
    try:
        conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
        conn.commit()
    finally:
        conn.close()
    if not yol.exists():
        connect().close()
    return yol.read_bytes()


def yedek_yaz(ham: bytes) -> dict:
    """Yedeği doğrular ve mevcut veritabanının yerine koyar (eskiyi saklar)."""
    hedef = varsayilan_yol()
    hedef.parent.mkdir(parents=True, exist_ok=True)
    gecici = hedef.with_name(hedef.name + ".yeni")
    eski = hedef.with_name(hedef.name + ".eski")
    gecici.write_bytes(ham)
    try:
        conn = sqlite3.connect(str(gecici))
        try:
            kontrol = conn.execute("PRAGMA integrity_check").fetchone()[0]
            tablolar = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
        finally:
            conn.close()
        if kontrol != "ok":
            raise ValueError("Yedek dosyası bozuk (integrity_check hatası).")
        eksik = ZORUNLU_TABLOLAR - tablolar
        if eksik:
            raise ValueError("Bu dosya RetroOps yedeği değil; eksik tablolar: "
                             + ", ".join(sorted(eksik)) + ".")
    except Exception as e:
        gecici.unlink(missing_ok=True)
        if isinstance(e, ValueError):
            raise
        raise ValueError("Yedek dosyası okunamadı; bu bir RetroOps yedeği değil. "
                         + str(e)) from e
    if hedef.exists():
        eski.unlink(missing_ok=True)
        hedef.replace(eski)
    gecici.replace(hedef)
    return {"durum": "ok", "mesaj": "Yedek yüklendi, veriler geri alınabilir.",
            "geri_alabilir": eski.exists()}


def yedek_geri_al() -> dict:
    """Son yedek yüklemesinden önceki veritabanına döner."""
    hedef = varsayilan_yol()
    eski = hedef.with_name(hedef.name + ".eski")
    if not eski.exists():
        raise ValueError("Geri alınacak önceki yedek yok.")
    if hedef.exists():
        hedef.unlink()
    eski.replace(hedef)
    return {"durum": "ok", "mesaj": "Önceki veritabanına dönüldü."}
