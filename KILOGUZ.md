# RetroOps · Kullanım Kılavuzu

E-ticaret operasyon paneli — iade, kargo, kâr hesabı, şikâyet ve pazaryeri
entegrasyonları tek ekranda. **Python bilmeniz gerekmez.**

---

## 1) Kurulum (2 dakika)

1. Size gönderilen `RetroOps-v1.0.0.zip` dosyasını bir klasöre çıkarın.
   (Windows 10/11 sıkıştırılmış klasörü açar: sağ tık → **Tümünü çıkar**)
2. Klászördeki **`RetroOps.exe`** dosyasına çift tıklayın.
3. Program arka planda başlar ve tarayıcınız otomatik olarak açılır:
   `http://127.0.0.1:8780`

> **Windows SmartScreen uyarısı** çıkarsa: *Daha fazla bilgi* → *Yine de çalıştır*.
> Bu, yeni ve imzalanmamış programlarda normal bir uyarıdır.

Elle açmak isterseniz tarayıcıya şu adresi yazın: `http://127.0.0.1:8780`

**Verileriniz nerede?** Program klasöründeki `data\ops.db` dosyasında.
Bu dosyayı kopyalamanız tüm verilerinizi yedeklemek demektir.
Programı kapatmak için görev çubuğundaki RetroOps simgesine sağ tık → kapat
(veya `Alt+F4` ile açık pencereyi kapatıp program simgesini kapatın).

---

## 2) Deneme süresi ve lisans

- İlk açılışta **14 günlük deneme** başlar (ücretsiz, kayıt istemez).
- 14 gün sonunda program lisans sorar; satın aldığınızda size verilen
  `RETROOPS-XXXXX-XXXXX-…` biçimindeki anahtarı **Panel → Lisans** alanına
  yazıp **Etkinleştir** deyin.
- Anahtar **yalnızca aldığınız bilgisayarda** çalışır. Makine kimliğinizi
  Lisans kutusunda görürsünüz; yeni bilgisayara taşırsanız yeni anahtar gerekir.
- Anahtarınızı kaybederseniz satın alma kanalından tekrar talep edebilirsiniz.

---

## 3) Pazaryeri hesaplarını bağlama (Entegrasyonlar sekmesi)

1. Üst menüden **Entegrasyonlar** sekmesine girin.
2. **Platform** seçin (Trendyol, Hepsiburada, N11, ÇiçekSepeti, Shopier,
   Pazarama, Shopify, WooCommerce, Amazon SP-API).
3. Karşınıza çıkan alanları doldurun. Alanların ne olduğu yazan kutuda
   (API anahtarı / satıcı anahtarı / gizli anahtar vb.) belirir.
4. **Test** deyin → bağlantı denenir.
5. **Senkronize et** deyin → son N günün sipariş, kargo ve iade kayıtları
   panelinize çekilir.

**Durum rozetleri:**

| Rozet | Anlamı | Yapılacak |
|---|---|---|
| Sorunsuz | API çalıştı, veriler geldi | — |
| Veri okunamadı | Bağlantı kuruldu ama yanıt eksik | Anahtar yetkilerini / mağaza bilgisini kontrol edin |
| Ağ hatası | İnternet veya API adresine ulaşılamadı | İnternet bağlantınızı, API'nin açık olup olmadığını kontrol edin |
| Hata | Yanıt reddedildi | Anahtarın geçerliliğini ve yetkilerini kontrol edin |

> Anahtarlarınızı **paylaşmayın**; program bunları bilgisayarınızda şifreli
> saklar (`data\.anahtar`) ve hiçbir ekranda/yanıta geri yazmaz.

---

## 4) Günlük kullanım

| Sekme | Ne işe yarar |
|---|---|
| **Panel** | Ciro, net kâr, KDV, satış listesi, iade/kargo/şikâyet özeti, lisans ve yedek |
| **İadeler** | 14 günlük yasal süre; durum ilerletme; süresi aşanlar kırmızı |
| **Kargo** | Gönderi + takip no; tahmini teslimden 3 gün sonra gecikme uyarısı |
| **Kâr Hesabı** | Komisyon + kargo + paket + KDV ile net kâr ve kırılma noktası |
| **Şikâyetler** | Müşteri şikâyet kaydı, çözüm oranı ve süreleri |
| **Entegrasyonlar** | Pazaryeri hesaplarını bağlama, test ve senkronizasyon |
| **CSV** | Listeleri Excel'e indirme, şablon alma, toplu sipariş yükleme |

**KDV:** Her siparişteki KDV oranı (`kdv_orani`) üzerinden KDV tutarı ve
KDV sonrası net kâr otomatik hesaplanır; Panel → Satışlar listesinde satır satır,
altında toplam olarak görünür.

---

## 5) Yedekleme ve geri alma

- **Yedek indir (.db)** → tüm veriniz tek dosya olarak iner. Bu dosyayı
  USB'ye, bulut diske veya e-postaya atabilirsiniz.
- **Yedek yükle** → daha önce indirdiğiniz yedek dosyasını geri yükler.
  Dosya önce doğrulanır; bozuksa yüklemez.
- **Önceki veriye dön** → son yüklemeden önceki haline döner.

Haftada bir yedek almanızı öneririz.

---

## 6) Sık karşılaşılan durumlar

- **Sayfa açılmıyor:** program kapalı olabilir. `RetroOps.exe`'ye tekrar
  çift tıklayın. Hâlâ olmuyorsa tarayıcıda `http://127.0.0.1:8780` yazın.
- **"Bağlantı reddedildi":** port başka bir program tarafından kullanılıyor.
  Bilgisayarı yeniden başlatıp tekrar deneyin.
- **Panel boş görünüyor:** entegrasyon bağlayın veya **CSV** sekmesinden
  siparişlerinizi toplu yükleyin (şablonu oradan indirirsiniz).
- **Tarayıcı otomatik açılmazsa:** adresi elle yazın (yukarıdaki bağlantı).
- **KDV oranı yanlış görünüyorsa:** siparişin KDV alanını düzenleyin
  (CSV ile yüklerken `kdv_orani` sütunu tanımlıdır).

---

## 7) Gizlilik

- Tüm veriler (sipariş, müşteri, şikâyet, anahtarlar) **yalnız bu
  bilgisayarda** tutulur; hiçbir veri satıcısı olmayan bir sunucuya gönderilmez.
- Program yalnız `127.0.0.1` (bu bilgisayar) üzerinde dinler; internete
  açılmaz, dışarıdan erişilemez.
- Müşteri bilgilerini işlerken 6698 sayılı KVKK kapsamında yalnızca kendi
  verinizin sorumlususunuz; yedeklerinizi güvende tutun.

---

## 8) Destek

- Sorularınız için **RetroOps satış kanalı** üzerinden yazın.
- Sorun bildirirken şu bilgileri ekleyin: Makine kimliği (Panel → Lisans),
  program sürümü (Panel altbilgisi) ve yaptığınız işlem.

*Telif © 2026 RetroOps. Tüm hakları saklıdır — kaynak kod lisans kapsamında
kopyalanamaz, dağıtılamaz.*
