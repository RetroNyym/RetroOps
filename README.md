# RetroOps · E-Ticaret Operasyon Paneli

Son 5 yılın Google Trends araştırmasında **en net problem e-ticarette**: Türkiye'de
e-ticaret 2025'te 365.395 şikâyetle en çok şikâyet edilen sektör (%63 iptal-iade-değişim,
%56 fiyat-fatura-ödeme, %34 teslim edilmeyen ürün), kargo gecikmesi ve artan pazaryeri
komisyonları (giyimde %18–23) en sık zorlanan başlıklar. Bu panel tam bu dört noktayı
tek yerde çözer: **iade takibi, kargo problem panosu, kâr/kırılma noktası hesabı ve
şikâyet izleyici** — üstelik trend sekmesiyle Google Trends verisini canlı çeker.

> Arayüz: koyu tema, RetroOps (R+) markalı tek sayfa uygulama · Sunucu: saf stdlib
> · Veri: yerel SQLite · Harici bağımlılık: **yok**

## Hızlı başlangıç

```powershell
cd eticaret-ops
python -m ops.ornek_veri     # ilk açılış için demo veri (opsiyonel)
python -m ops.web 8780       # veya: baslat.bat
# tarayıcıda: http://127.0.0.1:8780
```

`baslat.bat` → panel / örnek veri / test menüsü.

## Sekmeler

| Sekme | Ne yapar | Çözdüğü problem |
|---|---|---|
| **Panel** | Ciro, net kâr, marj, açık/geciken iade, problemli gönderi, şikâyet dağılımı ve ort. çözüm süresi kartları | "Nerede yanıyorum?" |
| **İadeler** | 14 günlük yasal süre sayacı, `talep → onay → kargoya verildi → inceleme → tamamlandı` durum makinesi, süresi aşanlar kırmızı | Şikâyetlerin %63'ü iade-değişim |
| **Kargo** | Gönderi + takip no, tahmini teslimden 3 gün sonra otomatik gecikme; kayıp/yanlış/hasar işaretleme; "sadece problemli" filtresi | Teslimat gecikmesi / kayıp gönderi |
| **Kâr Hesabı** | Komisyon + kargo + paket + KDV + diğer kesintilerle net kâr; **minimum (kırılma) fiyatı** ve hedef kârlı fiyat; 2026 komisyon tablosu | Komisyon oranlarının yükselmesi, fiyat hassasiyeti |
| **Şikâyetler** | Türkiye pazarının başlıklarıyla kayıt, çözüm oranı ve ort. çözüm süresi | Müşteri şikâyet takibi |
| **Entegrasyonlar** | 9 pazaryeri/servis API hesabını **bağla** (Trendyol, Hepsiburada, N11, ÇiçekSepeti, Shopier, Pazarama, Shopify, WooCommerce, Amazon); şifreli sakla, **Test** ile bağlantıyı dene, **Senkronize et** ile sipariş/kargo/iade kayıtlarını otomatik çek | Manuel sipariş girişi ve takip no kopyalama |
| **Trendler** | Google Trends son 5 yıl — canlı API denenir, **429/ağ hatasında yerleşik 5 yıllık araştırma verisine düşer** (grafik hiç boş kalmaz) | Talep eğilimini görmek |
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
    trend.py       Canlı Google Trends (urllib) → hata anında yerleşik 60 aylık seri
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
  test_*.py        80 test
  baslat.bat, README.md, requirements.txt
```

## API

| Metot | Yol | Not |
|---|---|---|
| GET | `/api/meta` | Durum/kategori listeleri (arayüz bununla dolar) |
| GET | `/api/ozet` | Panel kartları + istatistikler |
| GET/POST | `/api/siparisler` | Liste / ekle (kâr hesabıyla birlikte) |
| GET/POST | `/api/iadeler?sadece=geciken` | Liste / ekle |
| POST | `/api/iadeler/{id}/durum` | `{durum}` — geçersiz geçiş 400 döner |
| GET/POST | `/api/gonderiler?sadece=problem` | Liste / ekle |
| POST | `/api/gonderiler/{id}/durum` | `{durum, sorun_tipi}` |
| GET/POST | `/api/sikayetler` · POST `/api/sikayetler/{id}/durum` | Kayıt / çözüm |
| POST | `/api/hesapla` | Kâr dökümü + minimum + hedefli fiyat |
| GET | `/api/komisyonlar` · `/api/kategoriler` · `/api/trend` | Komisyon, trend kategorileri, Trends serisi |
| GET/POST | `/api/entegrasyonlar` | 9 platform + kayıtlı bağlantılar / yeni bağlantı (sır asla dönmez) |
| POST | `/api/entegrasyonlar/test` | Taslak test: `{platform, ayarlar, kimlik}` |
| POST | `/api/entegrasyonlar/{id}/test` · `/{id}/senkron` · `/{id}/sil` | Test / `{gun:1..90}` senkron / sil |
| GET | `/api/export/csv?tablo=` · `/api/sablon?tablo=` | İndirme |
| POST | `/api/import/csv?tablo=siparisler` | Ham CSV gövdesiyle toplu yükleme |

## Test

```powershell
cd eticaret-ops
python -m pytest -q          # 80 test, ~11 sn
python -m pyflakes ops       # 0 hata
python kontrol_ara.py        # JS <-> HTML id bütünlüğü
python kontrol_api.py        # JS yolları <-> sunucu rotaları
```

## Notlar

- **Trend kaynağı:** Canlı Google Trends isteği önce denenir; API 429/engel/ölüm
  durumunda yanıt `kaynak: "yerlesik"` + `canli_hata` alanıyla bilgi verir ve grafik
  yerleşik 60 aylık (2021→2026) araştırma serisiyle çizilir. Hiçbir seçenek boş kalmaz.
- **Kâr formülü:** Komisyon ve diğer kesintiler KDV *dahil* satış üzerinden;
  kâr = KDV hariç satış − alış − komisyon − kargo − paket − diğer. Minimum fiyat bu
  denklemin kâr=0 çözümüdür (komisyon paydası silerse anlaşılır hata döner).
- **Yasal süre:** İade için 14 gün (Tüketiciyi Koruma Kanunu) `talep_tarihi + 14`
  olarak sayılır; `cozum_tarihi` terminal durumlarda otomatik yazılır.
- **Entegrasyon:** API anahtarları/şifreleri `data/.anahtar` dosyasıyla şifrelenerek
  saklanır ve hiçbir API yanıtında/ekranında geri dönmez (yalnız doluluk bilgisi);
  `cryptography` kuruluysa Fernet, yoksa aynı biçimde stdlib PBKDF2+HMAC ile çalışır.
  "Senkronize et" aynı siparişi ikinci kez satır yapmaz (kaynak + platform sipariş
  no ile tekilleşir); okunamayan yanıt için `uyari`, 4xx/5xx için `hata`, ağ/SSL
  hatası için `ag` sonucu döner — hiçbir sekme boş kalmaz.
- Veritabanı elle taşınacaksa `OPS_DB` ortam değişkeniyle yol verilebilir.

## Lisans

Telif hakkı © 2026 RetroOps. **Tüm hakları saklıdır.**

Bu proje açık kaynak değildir; kaynak kodu yalnızca bu depoda (gizli) tutulur.
Lisanssız çoğaltma, değiştirme, yeniden yayınlama veya ticari kullanım yasaktır.
Kullanım ve dağıtım koşulları için `LICENSE.txt` dosyasına bakın.
