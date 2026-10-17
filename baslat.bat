@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo == RetroOps E-Ticaret Operasyon Paneli ==
echo 1 - Paneli baslat  http://127.0.0.1:8780
echo 2 - Ornek veri yukle (bos veritabani icin)
echo 3 - Testleri calistir
echo 4 - Paneli baslat + ornek veri
choice /c 1234 /n /m "Secim: "
if %errorlevel%==1 python -m ops.web 8780
if %errorlevel%==2 python -m ops.ornek_veri
if %errorlevel%==3 python -m pytest -q
if %errorlevel%==4 (
  python -m ops.ornek_veri
  python -m ops.web 8780
)
pause
