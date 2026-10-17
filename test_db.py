"""``ops.db.kok_dizin`` yol mantığı — kaynak kod, onedir/onefile ve zip/Temp."""
import sys
import tempfile
from pathlib import Path

import pytest

from ops import db

KOK = Path(__file__).resolve().parent


@pytest.fixture(autouse=True)
def onbelke_sifirla():
    db._KOK_ONBELLEK = None
    yield
    db._KOK_ONBELLEK = None


def test_kaynak_kodda_proje_koku():
    assert db.kok_dizin() == KOK
    assert db.kok_dizin() == db.kok_dizin()  # önbellek aynı değeri döner


def test_gecici_klasor_kararli_degil():
    assert db._kararli_klasor(Path(tempfile.gettempdir())) is False
    assert db._kararli_klasor(KOK) is True


def test_frozen_exe_yaninda_veri_tutulur(tmp_path, monkeypatch):
    exe_klasor = tmp_path / "RetroOps"
    exe_klasor.mkdir()
    exe = str(exe_klasor / "RetroOps.exe")
    # pytest klasörü gerçekte %TEMP% altında; "geçici" sayılmasın diye
    # gettempdir'i başka bir yere çekiyoruz.
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path / "sanki-temp"))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", exe)
    monkeypatch.setattr(sys, "argv", [exe])
    assert db.kok_dizin() == exe_klasor


def test_frozen_geciciden_calisirsa_yerel_veri_klasoru(tmp_path, monkeypatch):
    gecici = Path(tempfile.gettempdir()) / "Temp-Zip-ops-test"
    gecici.mkdir(exist_ok=True)
    exe = str(gecici / "RetroOps.exe")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "yerel"))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", exe)
    monkeypatch.setattr(sys, "argv", [exe])
    assert db.kok_dizin() == tmp_path / "yerel" / "RetroOps"
    assert (tmp_path / "yerel" / "RetroOps").is_dir()
