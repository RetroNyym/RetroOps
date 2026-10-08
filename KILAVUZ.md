# RetroOps · Kullanım Kılavuzu

E-ticaret operasyon paneli — iade, kargo, kâr hesabı, şikâyet ve pazaryeri
entegrasyonları tek ekranda. **Python bilmeniz gerekmez.**

---

## 1) Kurulum (2 dakika)

1. Size gönderilen `RetroOps-v1.1.0.zip` dosyasını bir klasöre çıkarın
   (Windows 10/11 sıkıştırılmış klasörü açar: sağ tık → **Tümünü çıkar**).
   Zip'i açmadan da çalıştırabilirsiniz: program **tek dosyadır**,
   her şeyin içine gömülüdür.
2. Klasördeki **`RetroOps.exe`** dosyasına çift tıklayın.
3. **RetroOps masaüstü penceresi** açılır (tarayıcı değil; adres çubuğu ve
   sekme yoktur). Panelle yaptığınız her şey bu pencerede olur.

> **Windows SmartScreen uyarısı** çıkarsa: *Daha fazla bilgi* → *Yine de çalıştır*.
> Bu, yeni ve imzalanmamış programlarda normal bir uyarıdır.

Pencereyi kapatmanız programı kapatır. Yeniden açmak için `RetroOps.exe`'ye
tekrar çift tıklamanız yeterlidir. Pencere açılamazsa program kendiliğinden
**Edge uygulama penceresinde** (adres çubuksuz, aynı program gibi), o da
yoksa tarayıcıda açılır; işlev farkı olmaz.

Tarayıcıdan da açmak isterseniz (isterseniz): `http://127.0.0.1:8780`
— ya da programı `RetroOps.exe --tarayici` ile başlatın.

**Verileriniz nerede?** Programı normal bir klasöre çıkardıysanız
program yanındaki `data\ops.db` dosyasında; zip içinden ya da geçici bir
klasörden çalıştırdıysanız `C:\Users\<ad>\AppData\Local\RetroOps\data\ops.db`
dosyasında. Her iki durumda da bu dosyayı kopyalamanız tüm verilerinizi
yedeklemek demektir.

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
| **Kargo** | Gönderi + takip no; tahmini teslimden 3 gün sonra gecikme uyarısı; kargo firması API hesabını bağlama, test ve otomatik durum güncelleme |
| **Kâr Hesabı** | Komisyon + kargo + paket + KDV ile net kâr ve kırılma noktası |
| **Şikâyetler** | Müşteri şikâyet kaydı, çözüm oranı ve süreleri |
| **Entegrasyonlar** | Pazaryeri hesaplarını bağlama, test ve senkronizasyon |
| **CSV** | Listeleri Excel'e indirme, şablon alma, toplu sipariş yükleme |
| **SMS** | Netgsm ile bilgilendirme SMS'i gönderme (satıcıdan alınan kodla açılır) |

**KDV:** Her siparişteki KDV oranı (`kdv_orani`) üzerinden KDV tutarı ve
KDV sonrası net kâr otomatik hesaplanır; Panel → Satışlar listesinde satır satır,
altında toplam olarak görünür.

---

## 5) SMS entegrasyonunu açma (Netgsm)

1. Panel → **Lisans** kutusundaki **makine kimliğinizi** satış kanalına gönderin.
2. Satıcı size `SMS-…` biçiminde **imzalı bir aktivasyon kodu** iletir.
3. Üst menüden **SMS** sekmesine girin; sekme kilitli ekranda açılır.
4. Kodu yapıştırıp **Etkinleştir** deyin → gönderim ekranı açılır.
5. Netgsm'den aldığınız **kullanıcı adı**, **API şifresi** ve **gönderici
   başlığı**nı doldurun → **Kaydet**.
6. Telefon numarası ve mesajı yazıp **Gönder** deyin; sonuç ve saat aynı
   sayfanın altında listelenir.

> Gönderici bilgileri bilgisayarınızda şifreli saklanır (`data\.sms`); şifre
> hiçbir ekranda veya yanıtta görünmez. **Kapat** düğmesi sekmeyi yeniden
> kilitler, istediğinizde aynı kodla tekrar açabilirsiniz.
> Sadece **cep numaraları** gönderilebilir; 0850/0212 gibi sabit hatlar
> reddedilir.

---

## 6) Kargo firması API bağlantısı

**Kargo** sekmesindeki **Kargo API bağlantıları** paneli, takip sorgularını
elle yapmaktan kurtarır:

1. **Firma** seçin (Yurtiçi, Aras, MNG, Sürat, Sendeo, PTT).
2. Firmanızın API dokümanındaki **taban adresi**ni yazın (örn.
   `https://api.firma.com.tr`); gerekirse sorgu yolu ve takip alanını
   değiştirin.
3. Kimlik türünü seçin: **kullanıcı adı/şifre** (Basic) veya **API anahtarı**
   (Bearer), bilgileri girin.
4. **Test** deyin → panel gerçek isteği atar ve yanıtı/HTTP kodunu gösterir.
5. **Kaydet** → bağlantı listeye düşer.
6. **Senkronize et** → gönderilerinizdeki takip numaraları sorgulanır, bulunan
   durum (yolda/şubede/teslim edildi/…) gönderilere işlenir.

> "Ağ hatası" görürseniz adresi ya da interneti kontrol edin. Tek seferde en
> fazla 100 takip numarası sorgulanır. Firma bilgilerinizi hiç bir sunucuya
> göndermezsiniz; sorgular kendi bilgisayarınızdan firmaya gider.

---

## 7) Güncellemeler

- Program açıldığında uzak sürüm dosyası kontrol edilir; yeni sürüm çıktığında
  panelin en üstünde **"Yeni sürüm var"** bandı belirir.
- Bantta kurulu sürüm, sürüm notu ve (varsa) **İndir →** bağlantısı görünür;
  bağlantı yoksa "Güncel dosyaları satış kanalından isteyin." yazar.
- Kontrol yaklaşık 6 saatte bir tekrarlanır; internet yoksa sessizce geçer,
  panel normal çalışmaya devam eder.

---

## 8) Yedekleme ve geri alma

- **Yedek indir (.db)** → tüm veriniz tek dosya olarak iner. Bu dosyayı
  USB'ye, bulut diske veya e-postaya atabilirsiniz.
- **Yedek yükle** → daha önce indirdiğiniz yedek dosyasını geri yükler.
  Dosya önce doğrulanır; bozuksa yüklemez.
- **Önceki veriye dön** → son yüklemeden önceki haline döner.

Haftada bir yedek almanızı öneririz.

---

## 9) Sık karşılaşılan durumlar

- **Pencere açılmıyor:** program kapalı olabilir. `RetroOps.exe`'ye tekrar
  çift tıklayın. Hâlâ olmuyorsa tarayıcıda `http://127.0.0.1:8780` yazın
  (program yine arka planda çalışıyordur).
- **"DLL bulunamadı / modül eksik" hatası:** program tek dosya olduğu için
  bu hata normalde çıkmaz. Görürseniz dosya yarım inmiş veya antivirüs bir
  parçasını silmiş demektir: zip'i **Tümünü çıkar** ile yeniden çıkarıp
  `RetroOps.exe`'yi çalıştırın; Defender uyarısında *Yine de çalıştır*
  deyin ve program klasörüne izin verin.
- **"Bağlantı reddedildi":** port başka bir program tarafından kullanılıyor.
  Bilgisayarı yeniden başlatıp tekrar deneyin.
- **Panel boş görünüyor:** entegrasyon bağlayın veya **CSV** sekmesinden
  siparişlerinizi toplu yükleyin (şablonu oradan indirirsiniz).
- **Pencere yerine Edge penceresi veya tarayıcı açıldı:** bilgisayarınızda
  masaüstü penceresi bileşeni (WebView2/.NET) çalışmıyordur; program bunu
  algılayıp kendiliğinden Edge uygulama penceresine, o da yoksa tarayıcıya
  geçer. İşlev farkı yoktur.
- **Yeni sürüm bandı çıktı:** panelin üstündeki "Yeni sürüm var" bandındaki
  bağlantıdan (ya da satış kanalından) güncel dosyaları alıp exe'yi
  değiştirmeniz yeterlidir; verileriniz aynen kalır.
- **KDV oranı yanlış görünüyorsa:** siparişin KDV alanını düzenleyin
  (CSV ile yüklerken `kdv_orani` sütunu tanımlıdır).

---

## 10) Gizlilik

- Tüm veriler (sipariş, müşteri, şikâyet, anahtarlar) **yalnız bu
  bilgisayarda** tutulur; hiçbir veri satıcısı olmayan bir sunucuya gönderilmez.
- Programın kendi paneli internete açılmaz: yalnız `127.0.0.1` (bu
  bilgisayar) üzerinde dinler, dışarıdan erişilemez.
- Dışarıya giden tek trafik sizin açtığınız bağlantılardır: bağlı olduğunuz
  pazaryeri API'leri, kargo firması sorguları, gönderdiğiniz SMS ve
  (6 saatte bir) güncelleme kontrolü. Başka hiçbir veri paylaşılmaz.
- Müşteri bilgilerini işlerken 6698 sayılı KVKK kapsamında yalnızca kendi
  verinizin sorumlususunuz; yedeklerinizi güvende tutun.

---

## 11) Destek

- Sorularınız için **RetroOps satış kanalı** üzerinden yazın.
- Sorun bildirirken şu bilgileri ekleyin: Makine kimliği (Panel → Lisans),
  program sürümü (Panel altbilgisi) ve yaptığınız işlem.

*Telif © 2026 RetroOps. Tüm hakları saklıdır — kaynak kod lisans kapsamında
kopyalanamaz, dağıtılamaz.*
