"""SQLite şeması ve bağlantı yardımcıları."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DB_YOL = Path(__file__).resolve().parent.parent / "data" / "ops.db"


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
