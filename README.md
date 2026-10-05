# RetroOps · E-Ticaret Operasyon Paneli

Son 5 yılın Google Trends araştırmasında **en net problem e-ticarette**: Türkiye'de
e-ticaret 2025'te 365.395 şikâyetle en çok şikâyet edilen sektör (%63 iptal-iade-değişim,
%56 fiyat-fatura-ödeme, %34 teslim edilmeyen ürün), kargo gecikmesi ve artan pazaryeri
komisyonları (giyimde %18–23) en sık zorlanan başlıklar. Bu panel tam bu dört noktayı
tek yerde çözer: **iade takibi, kargo problem panosu, kâr/kırılma noktası hesabı ve
şikâyet izleyici** — üstelik pazaryeri entegrasyonlarıyla sipariş/kargo/iade verisi
otomatik gelir.

> Arayüz: koyu tema, RetroOps (R+) markalı tek sayfa uygulama · Sunucu: saf stdlib
> · Veri: yerel SQLite · Harici bağımlılık: **yok**

## Hızlı başlangıç

**Müşteri kurulumu (Python gerekmez):**

1. `RetroOps-v1.0.0.zip` dosyasını bir klasöre çıkarın.
2. `RetroOps.exe` dosyasına çift tıklayın → tarayıcı otomatik açılır.
3. İlk 14 gün deneme; sonra Panel → Lisans alanına anahtar girilir.
4. Entegrasyonlar sekmesinden pazaryeri API hesapları bağlanır → **Test** → **Senkronize et**.

Paket içeriği: `RetroOps.exe`, `_internal/`, `KILOGUZ.md`, `LICENSE.txt`, `Baslat.bat`.
Veriler program klasöründeki `data/ops.db` dosyasında tutulur.

**Geliştirici başlatması:**

```powershell
cd eticaret-ops
python -m ops.ornek_veri     # ilk açılış için demo veri (opsiyonel)
python -m ops.web 8780       # veya: baslat.bat
# tarayıcıda: http://127.0.0.1:8780
```

`baslat.bat` → panel / örnek veri / test menüsü.
`.exe` derlemesi: `pyinstaller --onedir --windowed --name RetroOps --add-data "KILOGUZ.md;." baslat_exe.py`
(çıktı `dist/RetroOps/` altına düşer).

## Sekmeler

| Sekme | Ne yapar | Çözdüğü problem |
|---|---|---|
| **Panel** | Ciro, net kâr, marj, açık/geciken iade, problemli gönderi, şikâyet dağılımı ve ort. çözüm süresi kartları; **satış listesi**: her satışta KDV oranı, otomatik KDV tutarı ve KDV sonrası net kâr, altında toplam ciro + toplam KDV + toplam KDV sonrası net kâr; **Lisans** (deneme/anahtar) ve **Veri & Yedek** panelleri | "Nerede yanıyorum?" |
| **İadeler** | 14 günlük yasal süre sayacı, `talep → onay → kargoya verildi → inceleme → tamamlandı` durum makinesi, süresi aşanlar kırmızı | Şikâyetlerin %63'ü iade-değişim |
| **Kargo** | Gönderi + takip no, tahmini teslimden 3 gün sonra otomatik gecikme; kayıp/yanlış/hasar işaretleme; "sadece problemli" filtresi | Teslimat gecikmesi / kayıp gönderi |
| **Kâr Hesabı** | Komisyon + kargo + paket + KDV + diğer kesintilerle net kâr; **minimum (kırılma) fiyatı** ve hedef kârlı fiyat; 2026 komisyon tablosu | Komisyon oranlarının yükselmesi, fiyat hassasiyeti |
| **Şikâyetler** | Türkiye pazarının başlıklarıyla kayıt, çözüm oranı ve ort. çözüm süresi | Müşteri şikâyet takibi |
| **Entegrasyonlar** | 9 pazaryeri/servis API hesabını **bağla** (Trendyol, Hepsiburada, N11, ÇiçekSepeti, Shopier, Pazarama, Shopify, WooCommerce, Amazon); şifreli sakla, **Test** ile bağlantıyı dene, **Senkronize et** ile sipariş/kargo/iade kayıtlarını otomatik çek | Manuel sipariş girişi ve takip no kopyalama |
| **CSV** | Tablo listesini Excel uyumlu indir, şablon al, siparişleri toplu yükle | Elle tek tek giriş yok |

## Mimari

```
eticaret-ops/
  ops/
    db.py          SQLite şeması + şema geçişi (OPS_DB ortam değişkeni test içindir)
    kar.py         2026 komisyon tabloları, kâr dökümü, minimum/hedefli fiyat
    iade.py        14 gün sayacı + durum makinesi (geçişler katı)
    kargo.py       Gecikme eşiği, problem listesi, sorun tipleri
    sikayet.py     Kategori/çözüm istatistikleri
    csv_io.py      Şablon, toplu yükleme, dışa aktarma (UTF-8 BOM, Excel uyumlu)
    ornek_veri.py  Demo veri (idempotent: doluysa dokunmaz)
    entegrasyon.py Platform listesi, bağlantı CRUD, şifreli saklama, test/senkron
    adapters/      9 platform adaptörü (temel.py + trendyol, hepsiburada, n11,
                   ciceksepeti, shopier, pazarama, shopify, woocommerce, amazon)
    sync.py        Adaptör çıktısını sipariş/gönderi/iade tablolarına yazar
    sifre.py       Kimlik sırlarını şifreler (Fernet varsa, yoksa stdlib PBKDF2+HMAC)
    sayfa.py       Panel HTML/CSS/JS + RetroOps SVG logo
    web.py         http.server JSON API
  data/ops.db      Veritabanı (ilk çalıştırmada oluşur)
  test_*.py        72 test
  baslat.bat, README.md, requirements.txt
```

## API

| Metot | Yol | Not |
|---|---|---|
| GET | `/api/meta` | Durum/kategori listeleri (arayüz bununla dolar) + lisans durumu |
| GET/POST | `/api/lisans` | Deneme/lisans durumu / anahtar etkinleştirme (makineye bağlı) |
| GET | `/kilavuz` | Kullanım kılavuzu (KILOGUZ.md'den üretilir) |
| GET | `/api/yedek/indir` · POST `/api/yedek/yukle` · POST `/api/yedek/geri_al` | Veritabanı yedeği indir / yükle (doğrulanır) / geri al |
| GET | `/api/ozet` | Panel kartları + istatistikler |
| GET/POST | `/api/siparisler` | Liste (`?limit=200` ile son N) / ekle (kâr hesabıyla birlikte) |
| GET/POST | `/api/iadeler?sadece=geciken` | Liste / ekle |
| POST | `/api/iadeler/{id}/durum` | `{durum}` — geçersiz geçiş 400 döner |
| GET/POST | `/api/gonderiler?sadece=problem` | Liste / ekle |
| POST | `/api/gonderiler/{id}/durum` | `{durum, sorun_tipi}` |
| GET/POST | `/api/sikayetler` · POST `/api/sikayetler/{id}/durum` | Kayıt / çözüm |
| POST | `/api/hesapla` | Kâr dökümü + minimum + hedefli fiyat |
| GET | `/api/komisyonlar` | Komisyon tablosu (kâr hesabı) |
| GET/POST | `/api/entegrasyonlar` | 9 platform + kayıtlı bağlantılar / yeni bağlantı (sır asla dönmez) |
| POST | `/api/entegrasyonlar/test` | Taslak test: `{platform, ayarlar, kimlik}` |
| POST | `/api/entegrasyonlar/{id}/test` · `/{id}/senkron` · `/{id}/sil` | Test / `{gun:1..90}` senkron / sil |
| GET | `/api/export/csv?tablo=` · `/api/sablon?tablo=` | İndirme |
| POST | `/api/import/csv?tablo=siparisler` | Ham CSV gövdesiyle toplu yükleme |

## Test

```powershell
cd eticaret-ops
python -m pytest -q          # 72 test
python -m pyflakes ops       # 0 hata
python kontrol_ara.py        # JS <-> HTML id bütünlüğü
python kontrol_api.py        # JS yolları <-> sunucu rotaları
```

## Notlar

- **Kâr formülü:** Komisyon ve diğer kesintiler KDV *dahil* satış üzerinden;
  kâr = KDV hariç satış − alış − komisyon − kargo − paket − diğer. Minimum fiyat bu
  denklemin kâr=0 çözümüdür (komisyon paydası silerse anlaşılır hata döner).
- **Otomatik KDV:** Her siparişin `kdv_orani` alanı esas alınır (yoksa %20); satır bazlı
  KDV tutarı ve KDV sonrası net kâr `/api/siparisler`, toplam KDV `/api/ozet`
  (`kdv_tutar`) üzerinden hesaplanır ve Panel'de satış listesinde gösterilir.
- **Yasal süre:** İade için 14 gün (Tüketiciyi Koruma Kanunu) `talep_tarihi + 14`
  olarak sayılır; `cozum_tarihi` terminal durumlarda otomatik yazılır.
- **Entegrasyon:** API anahtarları/şifreleri `data/.anahtar` dosyasıyla şifrelenerek
  saklanır ve hiçbir API yanıtında/ekranında geri dönmez (yalnız doluluk bilgisi);
  `cryptography` kuruluysa Fernet, yoksa aynı biçimde stdlib PBKDF2+HMAC ile çalışır.
  "Senkronize et" aynı siparişi ikinci kez satır yapmaz (kaynak + platform sipariş
  no ile tekilleşir); okunamayan yanıt için `uyari`, 4xx/5xx için `hata`, ağ/SSL
  hatası için `ag` sonucu döner — hiçbir sekme boş kalmaz.
- **Lisans:** İlk açılıştan itibaren 14 gün deneme; süresi dolan program yalnız
  `/api/meta`, `/api/lisans` ve `/kilavuz` uçlarını açık tutar, veri uçları
  `402` döner ve arayüz lisans ekranını gösterir. Anahtar `RETROOPS-…` biçiminde,
  HMAC-SHA256 imzalı ve makine kimliğine bağlıdır; satıcı `araclar/lisans_uret.py`
  ile üretir, durum `data/.lisans` dosyasında tutulur.
- **Yedek:** Panel → Veri & Yedek; `.db` dosyası indirilir/yüklenir, yüklemeden
  önce `PRAGMA integrity_check` + zorunlu tablo kontrolü yapılır, eski veri
  `.eski` dosyasında saklanır ve "Önceki veriye dön" ile geri alınır.
- **Kılavuz:** `KILOGUZ.md` (son kullanıcıya yönelik) hem repoda hem pakette
  bulunur; `/kilavuz` adresinden program içinden de okunur.
- **Bilinen sınırlama:** Bazı ağlarda pazaryeri API uçlarına TLS doğrulaması
  engellendiğinden canlı uç testi yapılamıyor (bu ortamda Trendyol/Hepsiburada/N11
  el sıkışması kesiliyor); uygulama bunu "Ağ hatası" olarak raporlar ve diğer
  tüm akışlar aynı kalır. Satış öncesi müşteri ağından bir kez gerçek anahtarla
  **Test** çalıştırılmalıdır.
- Veritabanı elle taşınacaksa `OPS_DB` ortam değişkeniyle yol verilebilir.

## Lisans

Telif hakkı © 2026 RetroOps. **Tüm hakları saklıdır.**

Bu proje açık kaynak değildir; kaynak kodu yalnızca bu depoda (gizli) tutulur.
Lisanssız çoğaltma, değiştirme, yeniden yayınlama veya ticari kullanım yasaktır.
Kullanım ve dağıtım koşulları için `LICENSE.txt` dosyasına bakın.
