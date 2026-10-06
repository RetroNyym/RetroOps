"""Panel sayfası: RetroOps markalı tek sayfa uygulama (HTML + CSS + JS)."""

LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-label="RetroOps logosu">
  <defs>
    <linearGradient id="rgrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0a1b33"/>
      <stop offset=".5" stop-color="#0d4a58"/>
      <stop offset="1" stop-color="#12a293"/>
    </linearGradient>
  </defs>
  <rect x="7" y="7" width="86" height="86" rx="26" fill="url(#rgrad)" stroke="#ffffff" stroke-width="7"/>
  <text x="50" y="53" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="40" font-weight="700" fill="#ffffff">R+</text>
  <path d="M20 60 H80 L56 79 V90 H44 V79 Z" fill="#ffffff"/>
</svg>"""

PAGE = r"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RetroOps · E-Ticaret Operasyon Paneli</title>
<link rel="icon" href="/logo.svg" type="image/svg+xml">
<style>
:root{
  --bg:#070b14;--bg2:#0a1120;--panel:#0f1829;--panel2:#121d33;--line:#1f2c47;--line2:#2a3b5e;
  --txt:#eaf1fb;--mut:#93a6c4;--acc:#3b82f6;--acc2:#12a293;--ok:#22c55e;--uy:#f59e0b;--kotu:#ef4444;
  --grad:linear-gradient(135deg,#3b82f6 0%,#12a293 100%);
  --golge:0 18px 40px -22px #000c;--r:16px
}
*{box-sizing:border-box}
html{color-scheme:dark}
body{
  margin:0;color:var(--txt);font:15px/1.5 "Segoe UI Variable Text","Segoe UI",system-ui,Roboto,Arial,sans-serif;
  background:
    radial-gradient(900px 480px at 12% -8%,#12a2931f,transparent 60%),
    radial-gradient(1100px 560px at 92% -12%,#3b82f61d,transparent 62%),
    radial-gradient(760px 420px at 55% 108%,#12a29314,transparent 60%),
    linear-gradient(180deg,#070b14 0%,#080d18 100%);
  background-attachment:fixed
}
::-webkit-scrollbar{width:11px;height:11px}
::-webkit-scrollbar-track{background:#0a1120}
::-webkit-scrollbar-thumb{background:#22314f;border:2px solid #0a1120;border-radius:8px}
::-webkit-scrollbar-thumb:hover{background:#31507f}
header{
  display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;
  padding:12px 20px;position:sticky;top:0;z-index:5;
  background:linear-gradient(180deg,#0c1324f2,#0c1324dd);backdrop-filter:blur(14px) saturate(140%);
  border-bottom:1px solid var(--line);
  box-shadow:0 1px 0 #ffffff0a inset,0 10px 30px -18px #000
}
header::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:1px;background:linear-gradient(90deg,transparent,#3b82f6aa,#12a293aa,transparent);opacity:.7}
.marka{display:flex;align-items:center;gap:12px}
.marka svg{width:44px;height:44px;display:block;filter:drop-shadow(0 6px 14px #12a29355)}
.marka b{font-size:19px;letter-spacing:.3px;background:linear-gradient(90deg,#fff,#cfe3ff);-webkit-background-clip:text;background-clip:text}
.marka span{display:block;color:var(--mut);font-size:12px;letter-spacing:.04em}
#menu{display:flex;flex-wrap:wrap;gap:6px}
#menu button{
  background:transparent;border:1px solid transparent;color:var(--mut);
  padding:8px 14px;border-radius:999px;font-size:13.5px;font-weight:600;cursor:pointer;
  transition:.16s ease;letter-spacing:.01em
}
#menu button:hover{color:var(--txt);background:#ffffff0a;border-color:#ffffff14}
#menu button.aktif{
  background:var(--grad);border-color:transparent;color:#fff;
  box-shadow:0 8px 20px -8px #3b82f6cc,0 0 0 1px #ffffff14 inset
}
main{padding:20px 18px 8px;max-width:1280px;margin:0 auto;animation:belir .3s ease}
@keyframes belir{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.sekme{display:none}
.sekme.aktif{display:block;animation:belir .28s ease}
.baslik-satir{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;margin-bottom:14px}
.baslik-satir h2{margin:0;font-size:19px;letter-spacing:.2px}
.baslik-satir p{margin:3px 0 0;color:var(--mut);font-size:13px}
.kartlar{display:grid;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));gap:12px}
.kart{
  position:relative;overflow:hidden;padding:15px 15px 14px;border-radius:var(--r);
  background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);
  box-shadow:var(--golge);transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease
}
.kart::before{content:"";position:absolute;inset:0 0 auto 0;height:2px;background:var(--grad);opacity:.65}
.kart:hover{transform:translateY(-3px);border-color:var(--line2);box-shadow:0 24px 44px -24px #000d}
.kart .etiket{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.09em}
.kart .deger{font-size:26px;font-weight:700;margin-top:6px;font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.iy{color:#4ade80}.kt{color:#f87171}.uy{color:#fbbf24}
.panel{
  background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);
  border-radius:var(--r);padding:17px;margin-top:14px;box-shadow:var(--golge)
}
.panel h3{margin:0 0 13px;font-size:15.5px;letter-spacing:.2px}
.ust{
  display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;
  background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);
  border-radius:var(--r);padding:15px;box-shadow:var(--golge)
}
label{display:flex;flex-direction:column;gap:5px;font-size:11.5px;color:var(--mut);font-weight:700;letter-spacing:.05em;text-transform:uppercase}
input,select,textarea{
  padding:9px 12px;border-radius:10px;border:1px solid var(--line2);background:#0b1322;color:var(--txt);
  font-size:14px;font-family:inherit;min-width:120px;transition:border-color .15s,box-shadow .15s
}
input:focus,select:focus{outline:none;border-color:var(--acc);box-shadow:0 0 0 3px #3b82f633}
button{
  padding:9px 16px;border:0;border-radius:10px;background:var(--grad);color:#fff;font-weight:600;
  cursor:pointer;font-size:14px;transition:transform .12s ease,filter .15s ease,box-shadow .15s ease;
  box-shadow:0 8px 18px -10px #3b82f6cc
}
button:hover{filter:brightness(1.08);transform:translateY(-1px);box-shadow:0 12px 22px -10px #3b82f6cc}
button:active{transform:translateY(0);filter:brightness(.96)}
button.ikincil{background:#1b2740;box-shadow:none;border:1px solid var(--line2)}
button.ikincil:hover{border-color:#3b82f666;box-shadow:0 8px 18px -12px #000}
button.tehlike{background:linear-gradient(135deg,#ef4444,#b91c1c);box-shadow:0 8px 18px -10px #ef444488}
button.kucuk{padding:6px 11px;font-size:13px;border-radius:8px}
.dugme{
  display:inline-block;padding:9px 16px;border-radius:10px;background:var(--grad);color:#fff;
  font-weight:600;font-size:14px;text-decoration:none;cursor:pointer;transition:.15s;
  box-shadow:0 8px 18px -10px #3b82f6cc
}
.dugme:hover{filter:brightness(1.08);transform:translateY(-1px)}
.dugme.ikincil{background:#1b2740;border:1px solid var(--line2);box-shadow:none}
table{width:100%;border-collapse:collapse}
th,td{padding:10px 11px;border-bottom:1px solid var(--line);text-align:left;font-size:14px;vertical-align:middle}
th{
  color:var(--mut);font-size:10.5px;text-transform:uppercase;letter-spacing:.08em;font-weight:700;
  background:#0c1424;border-bottom:1px solid var(--line2);white-space:nowrap
}
tbody tr:nth-child(even) td{background:#ffffff04}
tr:hover td{background:#3b82f60f}
.rozet{display:inline-block;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;box-shadow:0 0 0 1px #ffffff08 inset}
.r-kirmizi{background:#ef44441f;color:#f87171;border:1px solid #ef444455}
.r-yesil{background:#22c55e1f;color:#4ade80;border:1px solid #22c55e55}
.r-sari{background:#f59e0b1f;color:#fbbf24;border:1px solid #f59e0b55}
.r-mavi{background:#3b82f61f;color:#93c5fd;border:1px solid #3b82f655}
.r-gri{background:#8fa3c01f;color:#8fa3c0;border:1px solid #8fa3c055}
.cubuk{display:grid;grid-template-columns:minmax(120px,210px) 1fr 66px;gap:11px;align-items:center;margin:9px 0;font-size:13px}
.cubuk .yol{background:#0b1322;border-radius:8px;height:12px;overflow:hidden;border:1px solid var(--line)}
.cubuk .yol i{display:block;height:100%;border-radius:8px;background:linear-gradient(90deg,#3b82f6,#12a293);box-shadow:0 0 12px #12a29366}
.cubuk b{text-align:right;color:var(--mut);font-variant-numeric:tabular-nums}
.uyari-cubugu{background:#f59e0b14;border:1px solid #f59e0b55;color:#fbbf24;padding:11px 14px;border-radius:11px;font-size:13px;margin-top:12px}
.basari-cubugu{background:#22c55e14;border:1px solid #22c55e55;color:#4ade80;padding:11px 14px;border-radius:11px;font-size:13px;margin-top:12px}
.bos{color:var(--mut);font-size:14px}
.izgara2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.sonuc-kutu{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin-top:12px}
.mini{background:#0c1424;border:1px solid var(--line);border-radius:12px;padding:13px}
.mini .etiket{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.07em}
.mini .deger{font-size:21px;font-weight:700;margin-top:4px;font-variant-numeric:tabular-nums}
#bildirim{
  position:fixed;right:18px;bottom:18px;padding:13px 17px;border-radius:12px;font-size:14px;font-weight:600;
  opacity:0;transform:translateY(8px);transition:.22s ease;z-index:50;max-width:360px;
  backdrop-filter:blur(10px);box-shadow:0 20px 40px -18px #000e
}
#bildirim.acik{opacity:1;transform:none}
#bildirim.ok{background:#14532ded;color:#bbf7d0;border:1px solid #22c55e88}
#bildirim.hata{background:#7f1d1ded;color:#fecaca;border:1px solid #ef444488}
#guncelleme-band:not(.gizle){
  flex-basis:100%;display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:center;
  background:linear-gradient(90deg,#12a29326,#3b82f626);border:1px solid #3b82f659;border-radius:12px;
  padding:9px 15px;font-size:13.5px;box-shadow:0 8px 22px -14px #3b82f6
}
#guncelleme-band a{color:#93c5fd;font-weight:700;text-decoration:none}
#guncelleme-band a:hover{text-decoration:underline}
.gizle{display:none}
.not{color:var(--mut);font-size:13px;margin-top:8px}
.rakam{display:block;color:var(--mut);font-size:11px;line-height:1.4;font-variant-numeric:tabular-nums}
tr.satir-toplam td{border-top:2px solid var(--line2);font-weight:700;padding-top:10px;background:#3b82f60a}
tr.satir-toplam .rakam{font-weight:400}
#lisans-kapak{
  position:fixed;inset:0;z-index:99;display:flex;align-items:center;justify-content:center;padding:20px;
  background:radial-gradient(900px 500px at 50% -10%,#12a29322,transparent 60%),#070b14f7;backdrop-filter:blur(6px)
}
#lisans-kapak.gizle{display:none}
.altbilgi{display:flex;gap:16px;flex-wrap:wrap;align-items:center;color:var(--mut);font-size:12px;margin-top:22px;padding-top:14px;border-top:1px solid var(--line)}
.altbilgi a{color:var(--acc2);text-decoration:none}
.altbilgi a:hover{text-decoration:underline}
@media (max-width:760px){.cubuk{grid-template-columns:1fr;gap:4px}.cubuk b{text-align:left}main{padding:14px 10px 6px}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
</head>
<body>
<header>
  <div class="marka">
    <svg viewBox="0 0 100 100" role="img" aria-label="RetroOps logosu"><defs><linearGradient id="hg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0a1b33"/><stop offset=".5" stop-color="#0d4a58"/><stop offset="1" stop-color="#12a293"/></linearGradient></defs><rect x="7" y="7" width="86" height="86" rx="26" fill="url(#hg)" stroke="#fff" stroke-width="7"/><text x="50" y="53" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="40" font-weight="700" fill="#fff">R+</text><path d="M20 60 H80 L56 79 V90 H44 V79 Z" fill="#fff"/></svg>
    <div><b>RetroOps</b><span>E-Ticaret Operasyon Paneli</span></div>
  </div>
  <nav id="menu">
    <button data-sekme="ozet" class="aktif">Panel</button>
    <button data-sekme="iade">İadeler</button>
    <button data-sekme="kargo">Kargo</button>
    <button data-sekme="kar">Kâr Hesabı</button>
    <button data-sekme="sikayet">Şikâyetler</button>
    <button data-sekme="entegrasyon">Entegrasyonlar</button>
    <button data-sekme="sms">SMS</button>
    <button data-sekme="csv">CSV</button>
  </nav>
  <div id="guncelleme-band" class="gizle"></div>
</header>

<main>
<section id="sekme-ozet" class="sekme aktif">
  <div class="baslik-satir">
    <div><h2>Operasyon paneli</h2><p id="ozet-tarih">—</p></div>
    <button class="ikincil kucuk" id="ozet-yenile">Yenile</button>
  </div>
  <div class="kartlar">
    <div class="kart"><div class="etiket">Sipariş</div><div class="deger" id="k-siparis">—</div></div>
    <div class="kart"><div class="etiket">Ciro (KDV dahil)</div><div class="deger" id="k-ciro">—</div></div>
    <div class="kart"><div class="etiket">Net kâr</div><div class="deger" id="k-kar">—</div></div>
    <div class="kart"><div class="etiket">Net marj</div><div class="deger" id="k-marj">—</div></div>
    <div class="kart"><div class="etiket">Açık iade</div><div class="deger" id="k-iade-acik">—</div></div>
    <div class="kart"><div class="etiket">Süresi aşan iade</div><div class="deger" id="k-iade-geciken">—</div></div>
    <div class="kart"><div class="etiket">Problemli gönderi</div><div class="deger" id="k-kargo">—</div></div>
    <div class="kart"><div class="etiket">Açık şikâyet</div><div class="deger" id="k-sikayet">—</div></div>
    <div class="kart"><div class="etiket">Ort. çözüm süresi</div><div class="deger" id="k-cozum">—</div></div>
  </div>
  <div class="panel gizle" id="ilk-adim">
    <h3>İlk adım: pazaryeri hesabınızı bağlayın</h3>
    <p class="not">Sipariş, kargo ve iade kayıtlarınızın otomatik gelmesi için
    tek yapmanız gereken API hesabınızı bağlamak. Entegrasyonlar sekmesinden
    platformunuzu seçin, anahtarlarınızı girin, <b>Test</b> deyin; ardından
    <b>Senkronize et</b> ile veriler çekilsin. Öncelikle CSV şablonuyla da
    veri yükleyebilirsiniz.</p>
    <button type="button" id="ilk-git">Entegrasyonlar sekmesine git →</button>
  </div>
  <div class="izgara2">
    <div class="panel"><h3>İade durum dağılımı (14 günlük yasal süre)</h3><div id="ozet-iade"><p class="bos">Veri yok</p></div></div>
    <div class="panel"><h3>Şikâyet kategorileri</h3><div id="ozet-sikayet"><p class="bos">Veri yok</p></div></div>
  </div>
  <div class="izgara2">
    <div class="panel"><h3>Süresi aşan iadeler</h3><div id="ozet-geciken"><p class="bos">Kayıt yok</p></div></div>
    <div class="panel"><h3>Problemli gönderiler</h3><div id="ozet-problem"><p class="bos">Kayıt yok</p></div></div>
  </div>
  <div class="panel">
    <div class="baslik-satir"><div><h3>Satışlar</h3>
      <p>KDV oranı her siparişten otomatik alınır; KDV tutarı ve KDV sonrası net kâr otomatik hesaplanır.</p></div></div>
    <table><thead><tr>
      <th>#</th><th>Ürün</th><th>Müşteri</th><th>Pazaryeri</th>
      <th>Satış (KDV dahil)</th><th>KDV</th><th>KDV sonrası net kâr</th>
    </tr></thead>
    <tbody id="ozet-satis"><tr><td colspan="7" class="bos">Kayıt yok</td></tr></tbody>
    <tfoot id="ozet-satis-toplam"></tfoot></table>
    <p class="not">Toplamlar <b>tüm</b> siparişlerden hesaplanır; tabloda en fazla
    son 200 satış listelenir.</p>
  </div>
  <div class="izgara2">
    <div class="panel"><h3>Lisans</h3>
      <div id="lisans-durum" class="not" style="margin-top:0">Kontrol ediliyor…</div>
      <div class="ust" style="border:0;padding:0;background:none;margin-top:10px">
        <label style="flex:1">Lisans anahtarı<input id="l-anahtar" placeholder="RETROOPS-XXXXX-XXXXX-…"></label>
        <button type="button" id="l-etkinlestir">Etkinleştir</button>
      </div>
      <p class="not">Program 14 gün ücretsiz denenebilir. Satın aldığınızda size
      verilen anahtarı girin — anahtar yalnız bu bilgisayarda geçerlidir.</p>
    </div>
    <div class="panel"><h3>Veri &amp; Yedek</h3>
      <div class="ust" style="border:0;padding:0;background:none">
        <a class="dugme ikincil" href="/api/yedek/indir">Yedek indir (.db)</a>
        <label>Yedek yükle<input type="file" id="y-dosya" accept=".db"></label>
        <button type="button" id="y-geri">Önceki veriye dön</button>
      </div>
      <p class="not">Tüm veriler yalnız bu bilgisayardaki <code>data/ops.db</code>
      dosyasında tutulur; hiçbir veri internete gönderilmez. Yüklenen yedek önce
      doğrulanır, gerekirse "Önceki veriye dön" ile eski haline alınır.</p>
    </div>
  </div>
</section>

<section id="sekme-iade" class="sekme">
  <div class="baslik-satir">
    <div><h2>İade takibi</h2><p>Yasal süre 14 gün — talep tarihinden itibaren sayılır, süresi aşanlar kırmızı.</p></div>
    <label style="flex-direction:row;align-items:center;gap:8px"><input type="checkbox" id="f-i-geciken" style="min-width:auto"> Sadece süresi aşanlar</label>
  </div>
  <form class="ust" id="form-iade">
    <label>Sipariş<select id="f-i-siparis"><option value="">— serbest kayıt —</option></select></label>
    <label>Müşteri<input id="f-i-musteri" placeholder="Ad Soyad"></label>
    <label>Tutar (₺)<input id="f-i-tutar" type="number" step="0.01" min="0" placeholder="0,00"></label>
    <label>Sebep<select id="f-i-sebep"></select></label>
    <label>Talep tarihi<input id="f-i-tarih" type="date"></label>
    <button type="submit">İade ekle</button>
  </form>
  <div class="panel">
    <table><thead><tr><th>#</th><th>Müşteri</th><th>Tutar</th><th>Sebep</th><th>Talep</th><th>Son gün</th><th>Kalan</th><th>Durum</th><th></th></tr></thead>
    <tbody id="i-tablo"><tr><td colspan="9" class="bos">Kayıt yok</td></tr></tbody></table>
  </div>
</section>

<section id="sekme-kargo" class="sekme">
  <div class="baslik-satir">
    <div><h2>Kargo / gönderi takibi</h2><p>Tahmini teslimden 3 gün sonra sorunlu sayılır; kayıp/yanlış/hasar işaretleyin.</p></div>
    <label style="flex-direction:row;align-items:center;gap:8px"><input type="checkbox" id="f-k-problem" style="min-width:auto"> Sadece problemli</label>
  </div>
  <form class="ust" id="form-kargo">
    <label>Kargo firması<select id="f-k-firma"></select></label>
    <label>Takip no<input id="f-k-takip" placeholder="ABC123..."></label>
    <label>Gönderim<input id="f-k-bas" type="date"></label>
    <label>Tahmini teslim<input id="f-k-bit" type="date"></label>
    <label>Not<input id="f-k-not" placeholder="isteğe bağlı"></label>
    <button type="submit">Gönderi ekle</button>
  </form>
  <div class="panel">
    <table><thead><tr><th>#</th><th>Firma</th><th>Takip no</th><th>Gönderim</th><th>Tahmini</th><th>Sorun</th><th>Durum</th><th>İşlem</th></tr></thead>
    <tbody id="k-tablo"><tr><td colspan="8" class="bos">Kayıt yok</td></tr></tbody></table>
  </div>
  <div class="panel" id="ka-panel">
    <div class="baslik-satir" style="margin-bottom:10px">
      <div><h3 style="margin:0">Kargo API bağlantıları</h3>
        <p>Firmanızın API bilgileriyle bağlanın; takip durumları tek tuşla güncellensin.</p></div>
      <button class="ikincil kucuk" id="ka-yenile">Yenile</button>
    </div>
    <div class="izgara2">
      <div class="panel" style="margin-top:0;box-shadow:none">
        <div class="ust" style="border:0;padding:0;background:none">
          <label>Firma<select id="ka-firma"></select></label>
          <label>Bağlantı adı<input id="ka-ad" placeholder="örn. Ana şube"></label>
        </div>
        <div class="ust" id="ka-alanlar" style="border:0;padding:0;background:none"></div>
        <div class="not" id="ka-not"></div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:12px">
          <button type="button" id="ka-test">Bağlantıyı test et</button>
          <button type="button" class="ikincil" id="ka-kaydet">Kaydet ve bağla</button>
        </div>
      </div>
      <div class="panel" style="margin-top:0;box-shadow:none">
        <h3>Sonuç</h3>
        <div id="ka-sonuc"><p class="bos">Henüz işlem yapılmadı. Firma ve bilgileri seçip "Bağlantıyı test et" ile başlayın.</p></div>
        <div style="margin-top:12px"><button type="button" id="ka-senkron">Takip durumlarını güncelle</button></div>
        <div id="ka-senkron-sonuc"></div>
      </div>
    </div>
    <table><thead><tr><th>#</th><th>Firma</th><th>Bağlantı</th><th>Kimlik</th><th>Son test</th><th>İşlem</th></tr></thead>
    <tbody id="ka-tablo"><tr><td colspan="6" class="bos">Bağlı kargo API'si yok</td></tr></tbody></table>
    <p class="not">Bağlantı bilgileri (API adresi, sorgu yolu, kimlik) firmanızın
    API dokümanına göre doldurulur; adresler ve yollar firmadan firmaya değişir.
    Test, girdiğiniz bilgilerle API adresine istek atarak kimliğinizi doğrular.</p>
  </div>
</section>

<section id="sekme-kar" class="sekme">
  <div class="baslik-satir">
    <div><h2>Kâr ve kırılma noktası hesabı</h2><p>Komisyon + diğer kesintiler KDV dahil satış üzerinden; kâr KDV hariç satıştan çıkar.</p></div>
  </div>
  <form class="ust" id="form-kar">
    <label>Pazaryeri<select id="f-c-pazaryeri"></select></label>
    <label>Kategori<select id="f-c-kategori"></select></label>
    <label>Alış (KDV hariç ₺)<input id="f-c-alis" type="number" step="0.01" min="0" value="100"></label>
    <label>Satış (KDV dahil ₺)<input id="f-c-satis" type="number" step="0.01" min="0" value="250"></label>
    <label>Komisyon %<input id="f-c-komisyon" type="number" step="0.01" min="0" value="20"></label>
    <label>Kargo ₺<input id="f-c-kargo" type="number" step="0.01" min="0" value="30"></label>
    <label>Paket ₺<input id="f-c-paket" type="number" step="0.01" min="0" value="10"></label>
    <label>KDV %<input id="f-c-kdv" type="number" step="0.01" min="0" value="20"></label>
    <label>Diğer kesinti %<input id="f-c-diger" type="number" step="0.01" min="0" value="0"></label>
    <label>Hedef kâr ₺<input id="f-c-hedef" type="number" step="0.01" min="0" value="0"></label>
    <button type="submit">Hesapla</button>
    <button type="button" class="ikincil" id="c-kaydet">Sipariş olarak kaydet</button>
  </form>
  <div id="c-sonuc"></div>
  <div class="panel"><h3>2026 komisyon tablosu (pazaryeri ortalamaları)</h3><div id="c-tablo"><p class="bos">Yükleniyor…</p></div></div>
</section>

<section id="sekme-sikayet" class="sekme">
  <div class="baslik-satir">
    <div><h2>Şikâyet izleyici</h2><p>Kategoriler Türkiye pazarının en çok şikâyet başlıklarıyla eşleşir.</p></div>
  </div>
  <form class="ust" id="form-sikayet">
    <label>Kaynak<select id="f-s-kaynak"></select></label>
    <label>Kategori<select id="f-s-kategori"></select></label>
    <label>Konu<input id="f-s-konu" placeholder="kısaca ne oldu?"></label>
    <label>Tarih<input id="f-s-tarih" type="date"></label>
    <button type="submit">Şikâyet ekle</button>
  </form>
  <div class="izgara2">
    <div class="panel"><h3>Şikâyetler</h3>
      <table><thead><tr><th>#</th><th>Kategori</th><th>Konu</th><th>Kaynak</th><th>Tarih</th><th>Durum</th><th></th></tr></thead>
      <tbody id="s-tablo"><tr><td colspan="7" class="bos">Kayıt yok</td></tr></tbody></table>
    </div>
    <div class="panel"><h3>Dağılım ve çözüm performansı</h3><div id="s-istatistik"><p class="bos">Veri yok</p></div></div>
  </div>
</section>

<section id="sekme-entegrasyon" class="sekme">
  <div class="baslik-satir">
    <div><h2>Pazaryeri entegrasyonları</h2><p>Hesabınızı bağlayın; sipariş, kargo ve iade verileri otomatik gelsin — elle giriş yok.</p></div>
    <button class="ikincil kucuk" id="e-yenile">Yenile</button>
  </div>
  <div class="izgara2">
    <div class="panel"><h3>Hesap bağla</h3>
      <div class="ust" style="border:0;padding:0;background:none">
        <label>Platform<select id="e-platform"></select></label>
        <label>Bağlantı adı<input id="e-ad" placeholder="örn. Ana mağaza"></label>
        <span id="e-yetenek" style="align-self:center"></span>
      </div>
      <div class="ust" id="e-alanlar" style="border:0;padding:0;background:none"></div>
      <div class="not" id="e-not"></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:12px">
        <button type="button" id="e-test">Bağlantıyı test et</button>
        <button type="button" class="ikincil" id="e-kaydet">Kaydet ve bağla</button>
      </div>
    </div>
    <div class="panel"><h3>Sonuç</h3><div id="e-sonuc"><p class="bos">Henüz işlem yapılmadı. Bilgileri doldurup "Bağlantıyı test et" ile başlayın.</p></div></div>
  </div>
  <div class="panel">
    <div class="baslik-satir" style="margin-bottom:8px">
      <h3 style="margin:0">Bağlı hesaplar</h3>
      <label style="flex-direction:row;align-items:center;gap:8px">Senkron aralığı
        <select id="e-gun"><option value="7">son 7 gün</option><option value="30" selected>son 30 gün</option><option value="90">son 90 gün</option></select>
      </label>
    </div>
    <table><thead><tr><th>#</th><th>Platform</th><th>Bağlantı</th><th>Kimlik</th><th>Son test</th><th>Son senkron</th><th>İşlem</th></tr></thead>
    <tbody id="e-tablo"><tr><td colspan="7" class="bos">Bağlı hesap yok</td></tr></tbody></table>
  </div>
</section>

<section id="sekme-sms" class="sekme">
  <div class="baslik-satir">
    <div><h2>SMS entegrasyonu</h2><p>Müşterilere bilgilendirme SMS'i gönderin; gönderim geçmişi bu bilgisayarda saklanır.</p></div>
    <span id="sms-rozet" class="rozet r-gri">Kontrol ediliyor…</span>
  </div>
  <div class="panel gizle" id="sms-kilit">
    <h3>Kilitli — entegrasyon kodu gerekli</h3>
    <p class="not" style="margin-top:0">SMS gönderimi, satın alımda size verilen
    <b>SMS entegrasyon kodu</b> ile açılır. Kod yalnız bu bilgisayarda geçerlidir.
    Makine kimliğiniz:</p>
    <div class="ust" style="border:0;padding:0;background:none">
      <span id="sms-makine" class="rozet r-mavi" style="align-self:center">—</span>
      <label style="flex:1">Entegrasyon kodu<input id="sms-kod" placeholder="SMS-XXXXX-XXXXX-…"></label>
      <button type="button" id="sms-etkinlestir">Etkinleştir</button>
    </div>
    <div id="sms-kilit-sonuc"></div>
    <p class="not">Kodu satış kanalından alın; sorun yaşarsanız destek alabilirsiniz.</p>
  </div>
  <div class="izgara2 gizle" id="sms-ayar">
    <div class="panel" style="margin-top:0">
      <h3>Gönderici ayarları (Netgsm)</h3>
      <div class="ust" style="border:0;padding:0;background:none">
        <label>Kullanıcı kodu<input id="sms-kullanici" placeholder="örn. 5XX0001"></label>
        <label>Şifre<input id="sms-parola" type="password" placeholder="SMS servis şifreniz"></label>
        <label>Gönderici başlık<input id="sms-baslik" placeholder="BILGI"></label>
      </div>
      <div class="ust" style="border:0;padding:0;background:none">
        <label style="flex:1">API adresi<input id="sms-adres" placeholder="https://api.netgsm.com.tr/rest/v1/sendSms"></label>
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:10px">
        <button type="button" id="sms-kaydet">Ayarları kaydet</button>
        <button type="button" class="tehlike" id="sms-kaldir">Etkinliği kaldır</button>
      </div>
      <p class="not">Kullanıcı kodu, şifre ve başlık SMS sağlayıcınızın panelinden
      alınır; başlığın kayıtlı olması gerekir. Şifre bu bilgisayarda şifrelenerek
      saklanır ve hiçbir yere geri gönderilmez.</p>
    </div>
    <div class="panel" style="margin-top:0">
      <h3>SMS gönder</h3>
      <div class="ust" style="border:0;padding:0;background:none">
        <label>Telefon<input id="sms-alici" placeholder="0532 123 45 67"></label>
        <label style="flex:2">Mesaj<textarea id="sms-mesaj" rows="3" placeholder="Siparişiniz kargoya verildi…"></textarea></label>
        <button type="button" id="sms-gonder">Gönder</button>
      </div>
      <div id="sms-sonuc"></div>
    </div>
  </div>
  <div class="panel">
    <h3>Gönderim geçmişi</h3>
    <table><thead><tr><th>#</th><th>Alıcı</th><th>Mesaj</th><th>Başlık</th><th>Zaman</th><th>Sonuç</th></tr></thead>
    <tbody id="sms-tablo"><tr><td colspan="6" class="bos">Kayıt yok</td></tr></tbody></table>
  </div>
</section>

<section id="sekme-csv" class="sekme">
  <div class="baslik-satir">
    <div><h2>CSV içe / dışa aktarma</h2><p>Listeleri Excel uyumlu CSV olarak indirin, siparişleri toplu yükleyin.</p></div>
  </div>
  <div class="ust">
    <label>Tablo<select id="v-tablo"></select></label>
    <a id="v-sablon" class="dugme ikincil" href="/api/sablon?tablo=siparisler">Şablon indir</a>
    <a id="v-indir" class="dugme" href="/api/export/csv?tablo=siparisler">Listeyi indir</a>
    <label id="v-etiket">CSV seç<input type="file" id="v-dosya" accept=".csv,text/csv"></label>
    <button type="button" id="v-yukle">Sipariş CSV yükle</button>
  </div>
  <div class="panel"><h3>Sonuç</h3><div id="v-sonuc"><p class="bos">Henüz işlem yapılmadı.</p></div>
    <div class="not">Yükleme yalnızca <b>siparisler</b> tablosu içindir; şablon indirip doldurun. Sütunlar:
    <code>pazaryeri, siparis_no, urun, adet, alis_fiyati, satis_fiyati, komisyon_yuzde, kargo_ucreti, paket_maliyeti, kdv_orani, diger_yuzde, musteri, siparis_tarihi, durum, notlar</code></div>
  </div>
</section>
</main>

<footer class="altbilgi">
  <span>RetroOps <b id="f-surum">—</b></span>
  <a href="/kilavuz" target="_blank" rel="noopener">Kullanım kılavuzu</a>
  <span>Gizlilik: veriler yalnız bu bilgisayarda saklanır, dışarı gönderilmez.</span>
  <span>Destek: RetroOps satış kanalı üzerinden.</span>
</footer>

<div id="lisans-kapak" class="gizle">
  <div class="panel" style="max-width:540px">
    <h3>Lisans süresi doldu</h3>
    <p class="not" id="k-mesaj">14 günlük deneme süresi doldu.</p>
    <div class="ust" style="border:0;padding:0;background:none">
      <label style="flex:1">Lisans anahtarı<input id="k-anahtar" placeholder="RETROOPS-XXXXX-XXXXX-…"></label>
      <button type="button" id="k-etkinlestir">Etkinleştir</button>
    </div>
    <p class="not">Anahtarınızı programı satın aldığınızda aldığınız bilgilerde
    bulabilirsiniz. Sorun yaşarsanız satış kanalı üzerinden destek alabilirsiniz.</p>
  </div>
</div>

<div id="bildirim"></div>

<script>
const $=s=>document.querySelector(s);
let META=null, KOM=null, SIPARISLER=[], IADE_ETIKET={};

function esc(x){return String(x==null?'':x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function para(x){return Number(x||0).toLocaleString('tr-TR',{minimumFractionDigits:2,maximumFractionDigits:2});}
function bugun(){return new Date().toISOString().slice(0,10);}
function gunEkle(g,n){const d=new Date();d.setDate(d.getDate()+n);return d.toISOString().slice(0,10);}
function bildir(metin,tip){const b=$('#bildirim');b.textContent=metin;b.className='acik '+(tip||'ok');clearTimeout(b._t);b._t=setTimeout(()=>{b.className='';},3200);}

async function api(yol,secenek){
  const r=await fetch(yol,secenek);
  const tip=r.headers.get('content-type')||'';
  const veri=tip.includes('json')?await r.json():await r.text();
  if(!r.ok)throw new Error((veri&&veri.hata)||('HTTP '+r.status));
  return veri;
}
function post(yol,nesne){return api(yol,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(nesne||{})});}
function secenekler(liste,bos){return (bos?'<option value="">'+esc(bos)+'</option>':'')+liste.map(o=>{const id=(o&&o.id!==undefined)?o.id:o;const ad=(o&&o.ad!==undefined)?o.ad:o;return '<option value="'+esc(id)+'">'+esc(ad)+'</option>';}).join('');}
function cubuk(ad,yuzde,sag){return '<div class="cubuk"><span class="ad">'+esc(ad)+'</span><div class="yol"><i style="width:'+Math.max(1,Math.min(100,yuzde))+'%"></i></div><b>'+esc(sag)+'</b></div>';}

// ---- sekmeler ----
document.addEventListener('click',e=>{
  const b=e.target.closest('#menu button');
  if(b)sekmeAc(b.dataset.sekme);
});
function sekmeAc(ad){
  document.querySelectorAll('.sekme').forEach(s=>s.classList.toggle('aktif',s.id==='sekme-'+ad));
  document.querySelectorAll('#menu button').forEach(b=>b.classList.toggle('aktif',b.dataset.sekme===ad));
  if(ad==='ozet')ozetYukle();
  if(ad==='iade')iadelerYukle();
  if(ad==='kargo'){gonderilerYukle();kargoApiYukle();}
  if(ad==='kar')karVerisi();
  if(ad==='sikayet')sikayetYukle();
  if(ad==='csv')csvHazir();
  if(ad==='entegrasyon')entegrasyonYukle();
  if(ad==='sms')smsYukle();
}

// ---- panel ----
async function ozetYukle(){
  try{
    const [d,gec,karListe,sip]=await Promise.all([
      api('/api/ozet'),
      api('/api/iadeler?sadece=geciken'),
      api('/api/gonderiler?sadece=problem'),
      api('/api/siparisler?limit=200')
    ]);
    $('#ozet-tarih').textContent='Veri günü: '+d.gun+' · sürüm '+d.surum;
    $('#k-siparis').textContent=d.siparis.toplam;
    $('#k-ciro').textContent=para(d.siparis.ciro)+' ₺';
    const karEl=$('#k-kar');karEl.textContent=para(d.siparis.kar)+' ₺';
    karEl.className='deger '+(d.siparis.kar<0?'kt':'iy');
    $('#k-marj').textContent='%'+d.siparis.marj_yuzde;
    const ia=$('#k-iade-acik');ia.textContent=d.iade.acik;
    ia.className='deger '+(d.iade.acik>0?'uy':'');
    const ig=$('#k-iade-geciken');ig.textContent=d.iade.geciken;
    ig.className='deger '+(d.iade.geciken>0?'kt':'iy');
    const kg=$('#k-kargo');kg.textContent=d.kargo.problem;
    kg.className='deger '+(d.kargo.problem>0?'kt':'iy');
    $('#k-sikayet').textContent=d.sikayet.acik;
    $('#k-cozum').textContent=(d.sikayet.ortalama_cozum_gun==null?'—':d.sikayet.ortalama_cozum_gun+' gün');
    const ilk=$('#ilk-adim');
    if(ilk)ilk.classList.toggle('gizle',d.siparis.toplam>0);

    const dag=d.iade.dagilim||{};
    const toplamI=d.iade.toplam||0;
    $('#ozet-iade').innerHTML=toplamI?Object.keys(dag).map(k=>cubuk(d.iade.etiketler[k]||k,toplamI?dag[k]/toplamI*100:0,dag[k]+' adet')).join(''):'<p class="bos">Kayıt yok</p>';

    const kat=d.sikayet.kategoriler||[];
    $('#ozet-sikayet').innerHTML=d.sikayet.toplam?kat.map(k=>cubuk(k.ad,k.yuzde,k.sayi+' ('+k.yuzde+'%)')).join(''):'<p class="bos">Kayıt yok</p>';

    $('#ozet-geciken').innerHTML=gec.liste.length?gec.liste.map(s=>
      '<div class="cubuk"><span class="ad">'+esc(s.musteri||('#'+s.id))+'</span><div class="yol"><i style="width:'+Math.min(100,Math.abs(s.kalan_gun)*5)+'%;background:#ef4444"></i></div><b class="kt">'+s.kalan_gun+' gün</b></div>').join(''):'<p class="bos">Süresi aşan iade yok</p>';

    $('#ozet-problem').innerHTML=karListe.liste.length?karListe.liste.map(s=>
      '<div class="cubuk"><span class="ad">'+esc(s.kargo_firmasi)+' · '+esc(s.takip_no||'#'+s.id)+'</span><div class="yol"><i style="width:'+Math.min(100,60+s.gecikme_gun*8)+'%;background:#f59e0b"></i></div><b class="uy">'+esc(s.sorun_etiket)+'</b></div>').join(''):'<p class="bos">Problemli gönderi yok</p>';

    satisCiz(sip.liste||[],d.siparis);
  }catch(e){bildir('Panel yüklenemedi: '+e.message,'hata');}
}
function satisCiz(liste,ozet){
  $('#ozet-satis').innerHTML=liste.length?liste.map(s=>{
    const karS=s.kar;
    const karMetin=karS==null?'—':para(karS)+' ₺';
    const karSinif=karS==null?'':(karS<0?'kt':'iy');
    return '<tr><td>'+s.id+'</td><td>'+esc(s.urun||'—')+'</td><td>'+esc(s.musteri||'—')+'</td>'+
      '<td>'+esc(s.pazaryeri||'—')+'</td>'+
      '<td>'+para(s.satis_fiyati)+' ₺</td>'+
      '<td><span class="rakam">%'+esc(s.kdv_orani==null?'20':s.kdv_orani)+'</span><span class="rakam">'+para(s.kdv_tutar)+' ₺</span></td>'+
      '<td><b class="'+karSinif+'">'+karMetin+'</b>'+
      (s.marj_yuzde==null?'':'<span class="rakam">marj %'+s.marj_yuzde+'</span>')+'</td></tr>';
  }).join(''):'<tr><td colspan="7" class="bos">Kayıt yok</td></tr>';
  const karT=ozet.kar;
  $('#ozet-satis-toplam').innerHTML=liste.length?
    '<tr class="satir-toplam"><td colspan="4"><b>Toplam ('+ozet.toplam+' satış)</b></td>'+
    '<td>'+para(ozet.ciro)+' ₺<span class="rakam">KDV hariç '+para(ozet.kdv_haric_ciro)+' ₺</span></td>'+
    '<td><span class="rakam">KDV toplamı</span><span class="rakam">'+para(ozet.kdv_tutar)+' ₺</span></td>'+
    '<td><b class="'+(karT<0?'kt':'iy')+'">'+para(karT)+' ₺</b><span class="rakam">Toplam KDV sonrası net kâr</span></td></tr>':'';
}
$('#ozet-yenile').addEventListener('click',ozetYukle);
$('#ilk-git').addEventListener('click',()=>sekmeAc('entegrasyon'));

// ---- lisans & yedek ----
function lisansGoster(d){
  if(!d)return;
  const etiket=d.durum==='lisansli'?'Lisanslı':(d.durum==='deneme'?'Deneme: '+d.kalan_gun+' gün':'Süresi doldu');
  const cls=d.durum==='lisansli'?'r-yesil':(d.durum==='deneme'?'r-sari':'r-kirmizi');
  const el=$('#lisans-durum');
  if(el)el.innerHTML='<span class="rozet '+cls+'">'+esc(etiket)+'</span> <span class="not" style="margin:0">'+esc(d.mesaj||'')+'</span><br><span class="not" style="margin:0">Makine kimliği: <code>'+esc(d.makine||'')+'</code></span>';
  const mesaj=$('#k-mesaj');if(mesaj)mesaj.textContent=d.mesaj||'';
  const kapak=$('#lisans-kapak');
  if(kapak)kapak.classList.toggle('gizle',d.durum!=='suresi_doldu');
}
async function lisansEtkinlestir(girdiId){
  const anahtar=$('#'+girdiId).value.trim();
  if(!anahtar){bildir('Önce lisans anahtarını girin','hata');return;}
  try{
    const d=await post('/api/lisans',{anahtar});
    lisansGoster(d);
    bildir(d.mesaj||'Lisans etkinleştirildi');
    if(d.durum==='lisansli')setTimeout(()=>location.reload(),700);
  }catch(e){bildir(e.message,'hata');}
}
$('#l-etkinlestir').addEventListener('click',()=>lisansEtkinlestir('l-anahtar'));
$('#k-etkinlestir').addEventListener('click',()=>lisansEtkinlestir('k-anahtar'));
$('#y-geri').addEventListener('click',async()=>{
  if(!window.confirm('Son yedek yüklemeden önceki veritabanına dönülsün mü?'))return;
  try{const d=await post('/api/yedek/geri_al');bildir(d.mesaj);setTimeout(()=>location.reload(),700);}
  catch(e){bildir(e.message,'hata');}
});
$('#y-dosya').addEventListener('change',async()=>{
  const f=$('#y-dosya').files[0];if(!f)return;
  try{
    const buf=await f.arrayBuffer();
    const d=await api('/api/yedek/yukle',{method:'POST',headers:{'Content-Type':'application/octet-stream'},body:buf});
    bildir(d.mesaj||'Yedek yüklendi');
    setTimeout(()=>location.reload(),900);
  }catch(e){bildir(e.message,'hata');$('#y-dosya').value='';}
});

// ---- iadeler ----
async function siparisleriYukle(){
  const d=await api('/api/siparisler');
  SIPARISLER=d.liste;
  $('#f-i-siparis').innerHTML='<option value="">— serbest kayıt —</option>'+d.liste.map(s=>
    '<option value="'+s.id+'">#'+s.id+' · '+esc(s.urun)+' · '+esc(s.musteri||'—')+'</option>').join('');
}
$('#f-i-siparis').addEventListener('change',()=>{
  const id=Number($('#f-i-siparis').value);
  const s=SIPARISLER.find(x=>x.id===id);
  if(s){$('#f-i-musteri').value=s.musteri||'';$('#f-i-tutar').value=s.satis_fiyati;}
});
function iadeRozet(s){
  if(s.durum==='tamamlandi')return '<span class="rozet r-yesil">Tamamlandı</span>';
  if(s.durum==='reddedildi')return '<span class="rozet r-gri">Reddedildi</span>';
  if(s.gecikti)return '<span class="rozet r-kirmizi">'+Math.abs(s.kalan_gun)+' gün gecikti</span>';
  return '<span class="rozet r-sari">'+s.kalan_gun+' gün kaldı</span>';
}
async function iadelerYukle(){
  try{
    const sadece=$('#f-i-geciken').checked?'?sadece=geciken':'';
    const d=await api('/api/iadeler'+sadece);
    $('#i-tablo').innerHTML=d.liste.length?d.liste.map(s=>{
      const izin=META.iade_gecisler[s.durum]||[];
      const kapali=s.durum==='tamamlandi'||s.durum==='reddedildi';
      const kontrol=kapali?'<span class="rozet r-gri">Kapandı</span>':
        '<select data-id="'+s.id+'">'+izin.map(x=>'<option value="'+x+'">'+esc(IADE_ETIKET[x]||x)+'</option>').join('')+'</select> <button class="kucuk iade-kaydet" data-id="'+s.id+'">Uygula</button>';
      return '<tr data-id="'+s.id+'"><td>'+s.id+'</td><td>'+esc(s.musteri||'—')+'</td><td>'+para(s.tutar)+' ₺</td><td>'+esc(s.sebep||'—')+'</td><td>'+esc(s.talep_tarihi)+'</td><td>'+esc(s.son_tarih)+'</td><td>'+iadeRozet(s)+'</td><td><span class="rozet r-mavi">'+esc(s.durum_etiket)+'</span></td><td>'+kontrol+'</td></tr>';
    }).join(''):'<tr><td colspan="9" class="bos">Kayıt yok</td></tr>';
  }catch(e){bildir(e.message,'hata');}
}
$('#f-i-geciken').addEventListener('change',iadelerYukle);
$('#i-tablo').addEventListener('click',async e=>{
  const b=e.target.closest('.iade-kaydet');if(!b)return;
  const id=b.dataset.id;
  const satir=$('#i-tablo').querySelector('tr[data-id="'+id+'"]');
  const sel=satir?satir.querySelector('select'):null;
  if(!sel)return;
  try{await post('/api/iadeler/'+id+'/durum',{durum:sel.value});bildir('İade durumu güncellendi');iadelerYukle();}catch(err){bildir(err.message,'hata');}
});
$('#form-iade').addEventListener('submit',async e=>{
  e.preventDefault();
  try{
    await post('/api/iadeler',{
      siparis_id:$('#f-i-siparis').value?Number($('#f-i-siparis').value):null,
      musteri:$('#f-i-musteri').value.trim(),
      tutar:Number($('#f-i-tutar').value||0),
      sebep:$('#f-i-sebep').value,
      talep_tarihi:$('#f-i-tarih').value
    });
    bildir('İade kaydı eklendi');
    $('#f-i-siparis').value='';$('#f-i-musteri').value='';$('#f-i-tutar').value='';
    iadelerYukle();ozetYukle();
  }catch(err){bildir(err.message,'hata');}
});

// ---- kargo ----
async function gonderilerYukle(){
  try{
    const sadece=$('#f-k-problem').checked?'?sadece=problem':'';
    const d=await api('/api/gonderiler'+sadece);
    $('#k-tablo').innerHTML=d.liste.length?d.liste.map(s=>{
      const durumSec='<select class="k-durum" data-id="'+s.id+'">'+
        META.kargo_durumlari.map(x=>'<option value="'+x.id+'"'+(x.id===s.son_durum?' selected':'')+'>'+esc(x.ad)+'</option>').join('')+'</select>';
      const sorunSec='<select class="k-sorun" data-id="'+s.id+'">'+
        META.sorun_tipleri.map(x=>'<option value="'+x.id+'"'+(x.id===s.sorun_tipi?' selected':'')+'>'+esc(x.ad)+'</option>').join('')+'</select>';
      const rozet=s.sorunlu?'<span class="rozet '+(s.gecikti?'r-kirmizi':'r-sari')+'">'+esc(s.sorun_etiket)+(s.gecikti?' · '+s.gecikme_gun+' gün':'')+'</span>':'<span class="rozet r-yesil">Zamanında</span>';
      return '<tr><td>'+s.id+'</td><td>'+esc(s.kargo_firmasi)+'</td><td>'+esc(s.takip_no||'—')+'</td><td>'+esc(s.gonderim_tarihi)+'</td><td>'+esc(s.tahmini_teslim)+'</td><td>'+rozet+'</td><td>'+durumSec+'</td><td>'+sorunSec+' <button class="kucuk k-kaydet" data-id="'+s.id+'">Kaydet</button></td></tr>';
    }).join(''):'<tr><td colspan="8" class="bos">Kayıt yok</td></tr>';
  }catch(e){bildir(e.message,'hata');}
}
$('#f-k-problem').addEventListener('change',gonderilerYukle);
$('#k-tablo').addEventListener('click',async e=>{
  const b=e.target.closest('.k-kaydet');if(!b)return;
  const id=b.dataset.id;
  const durum=document.querySelector('select.k-durum[data-id="'+id+'"]');
  const sorun=document.querySelector('select.k-sorun[data-id="'+id+'"]');
  try{
    await post('/api/gonderiler/'+id+'/durum',{durum:durum.value,sorun_tipi:sorun.value});
    bildir('Gönderi güncellendi');gonderilerYukle();ozetYukle();
  }catch(err){bildir(err.message,'hata');}
});
$('#form-kargo').addEventListener('submit',async e=>{
  e.preventDefault();
  try{
    await post('/api/gonderiler',{
      kargo_firmasi:$('#f-k-firma').value,
      takip_no:$('#f-k-takip').value.trim(),
      gonderim_tarihi:$('#f-k-bas').value,
      tahmini_teslim:$('#f-k-bit').value,
      notlar:$('#f-k-not').value.trim()
    });
    bildir('Gönderi eklendi');
    $('#f-k-takip').value='';$('#f-k-not').value='';
    gonderilerYukle();ozetYukle();
  }catch(err){bildir(err.message,'hata');}
});

// ---- kâr ----
async function karVerisi(){
  try{
    if(!KOM){const k=await api('/api/komisyonlar');KOM=k.tablo;}
    if(!$('#f-c-pazaryeri').options.length){
      $('#f-c-pazaryeri').innerHTML=secenekler(META.pazaryerleri);
      kategoriDegisti();
    }
    komisyonTablosu();
    karHesapla(true);
  }catch(e){bildir(e.message,'hata');}
}
function kategoriDegisti(){
  const p=$('#f-c-pazaryeri').value;
  const kat=Object.keys(KOM[p]||{});
  $('#f-c-kategori').innerHTML=secenekler(kat);
  komisyonDoldur();
}
function komisyonDoldur(){
  const p=$('#f-c-pazaryeri').value,k=$('#f-c-kategori').value;
  const v=(KOM[p]||{})[k];
  if(v&&v.orta>0)$('#f-c-komisyon').value=v.orta;
}
$('#f-c-pazaryeri').addEventListener('change',kategoriDegisti);
$('#f-c-kategori').addEventListener('change',komisyonDoldur);
function komisyonTablosu(){
  let html='<table><thead><tr><th>Pazaryeri</th><th>Kategori</th><th>Alt</th><th>Üst</th><th>Önerilen</th></tr></thead><tbody>';
  for(const p of Object.keys(KOM)){
    for(const k of Object.keys(KOM[p])){
      const v=KOM[p][k];
      html+='<tr><td>'+esc(p)+'</td><td>'+esc(k)+'</td><td>%'+v.alt+'</td><td>%'+v.ust+'</td><td><b>%'+v.orta+'</b></td></tr>';
    }
  }
  $('#c-tablo').innerHTML=html+'</tbody></table>';
}
function karOku(){
  return {
    pazaryeri:$('#f-c-pazaryeri').value,
    kategori:$('#f-c-kategori').value,
    alis:$('#f-c-alis').value,
    satis:$('#f-c-satis').value,
    komisyon_yuzde:$('#f-c-komisyon').value,
    kargo:$('#f-c-kargo').value,
    paket:$('#f-c-paket').value,
    kdv:$('#f-c-kdv').value,
    diger_yuzde:$('#f-c-diger').value,
    hedef_kar:$('#f-c-hedef').value
  };
}
async function karHesapla(sessiz){
  try{
    const d=await api('/api/hesapla',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(karOku())});
    let html='';
    if(d.hesap_hatasi)html+='<div class="uyari-cubugu">'+esc(d.hesap_hatasi)+'</div>';
    if(d.kar){
      const g=d.kar.giderler;
      html+='<div class="panel"><h3>Kâr dökümü (sipariş toplamı)</h3><table><tbody>'+
        '<tr><td>Satış (KDV dahil)</td><td>'+para(d.kar.satis)+' ₺</td></tr>'+
        '<tr><td>KDV hariç satış</td><td>'+para(d.kar.satis_kdv_haric)+' ₺</td></tr>'+
        '<tr><td>− Alış</td><td class="kt">−'+para(g.alis)+' ₺</td></tr>'+
        '<tr><td>− Pazaryeri komisyonu ('+esc($('#f-c-komisyon').value)+'%)</td><td class="kt">−'+para(g.komisyon)+' ₺</td></tr>'+
        '<tr><td>− Kargo</td><td class="kt">−'+para(g.kargo)+' ₺</td></tr>'+
        '<tr><td>− Paket/operasyon</td><td class="kt">−'+para(g.paket)+' ₺</td></tr>'+
        '<tr><td>− Diğer kesinti</td><td class="kt">−'+para(g.diger)+' ₺</td></tr>'+
        '<tr><td><b>Net kâr</b></td><td><b class="'+(d.kar.kar<0?'kt':'iy')+'">'+para(d.kar.kar)+' ₺</b> (marj %'+d.kar.marj_yuzde+')</td></tr>'+
        '</tbody></table></div>';
    }
    html+='<div class="sonuc-kutu">'+
      '<div class="mini"><div class="etiket">Minimum satış fiyatı</div><div class="deger '+(d.hesap_hatasi?'kt':'uy')+'">'+(d.minimum_fiyat==null?'—':para(d.minimum_fiyat)+' ₺')+'</div><div class="not">Zarar etmeden satılabilecek en düşük fiyat</div></div>'+
      '<div class="mini"><div class="etiket">'+para($('#f-c-hedef').value)+' ₺ kârlı fiyat</div><div class="deger iy">'+(d.hedefli_fiyat==null?'—':para(d.hedefli_fiyat)+' ₺')+'</div><div class="not">Hedef kârı garantileyen fiyat</div></div>'+
      '<div class="mini"><div class="etiket">Önerilen komisyon</div><div class="deger">%'+d.onerilen_komisyon+'</div><div class="not">'+esc($('#f-c-pazaryeri').value)+' · '+esc($('#f-c-kategori').value)+'</div></div>'+
      '</div>';
    $('#c-sonuc').innerHTML=html;
  }catch(e){if(!sessiz)bildir(e.message,'hata');}
}
$('#form-kar').addEventListener('submit',e=>{e.preventDefault();karHesapla();});
$('#c-kaydet').addEventListener('click',async()=>{
  try{
    const v=karOku();
    const yeni=await post('/api/siparisler',{
      pazaryeri:v.pazaryeri,urun:$('#f-c-kategori').value+' ürünü',
      alis_fiyati:v.alis,satis_fiyati:v.satis,komisyon_yuzde:v.komisyon_yuzde,
      kargo_ucreti:v.kargo,paket_maliyeti:v.paket,kdv_orani:v.kdv,
      diger_yuzde:v.diger_yuzde,siparis_tarihi:bugun(),
      notlar:'Kâr hesabından eklendi'
    });
    bildir('Sipariş #'+yeni.id+' kaydedildi (kâr: '+para(yeni.kar)+' ₺)');
    ozetYukle();
  }catch(e){bildir(e.message,'hata');}
});

// ---- şikâyetler ----
async function sikayetYukle(){
  try{
    const [liste,ist]=await Promise.all([api('/api/sikayetler'),api('/api/ozet')]);
    $('#s-tablo').innerHTML=liste.liste.length?liste.liste.map(s=>{
      const rozet=s.durum==='cozuldu'?'<span class="rozet r-yesil">Çözüldü</span>':
        (s.durum==='inceleniyor'?'<span class="rozet r-sari">İnceleniyor</span>':'<span class="rozet r-kirmizi">Açık</span>');
      const btn=s.durum==='cozuldu'?'<span class="rozet r-yesil">'+(s.cozum_gun==null?'—':s.cozum_gun+' gün')+'</span>':
        '<button class="kucuk s-coz" data-id="'+s.id+'">Çözüldü</button>';
      return '<tr><td>'+s.id+'</td><td>'+esc(s.kategori_etiket)+'</td><td>'+esc(s.konu||'—')+'</td><td>'+esc(s.kaynak_etiket)+'</td><td>'+esc(s.tarih)+'</td><td>'+rozet+'</td><td>'+btn+'</td></tr>';
    }).join(''):'<tr><td colspan="7" class="bos">Kayıt yok</td></tr>';
    const s=ist.sikayet;
    $('#s-istatistik').innerHTML=s.toplam?
      '<div class="cubuk"><span class="ad">Çözüm oranı</span><div class="yol"><i style="width:'+s.cozum_orani+'%"></i></div><b>%'+s.cozum_orani+'</b></div>'+
      '<div class="cubuk"><span class="ad">Ort. çözüm süresi</span><div class="yol"><i style="width:'+Math.min(100,(s.ortalama_cozum_gun||0)*10)+'%"></i></div><b>'+(s.ortalama_cozum_gun==null?'—':s.ortalama_cozum_gun+' gün')+'</b></div>'+
      s.kategoriler.filter(k=>k.sayi>0).map(k=>cubuk(k.ad,k.yuzde,k.yuzde+'%')).join(''):
      '<p class="bos">Kayıt yok</p>';
  }catch(e){bildir(e.message,'hata');}
}
$('#s-tablo').addEventListener('click',async e=>{
  const b=e.target.closest('.s-coz');if(!b)return;
  try{await post('/api/sikayetler/'+b.dataset.id+'/durum',{durum:'cozuldu'});bildir('Şikâyet çözüldü olarak işaretlendi');sikayetYukle();ozetYukle();}catch(err){bildir(err.message,'hata');}
});
$('#form-sikayet').addEventListener('submit',async e=>{
  e.preventDefault();
  try{
    await post('/api/sikayetler',{kaynak:$('#f-s-kaynak').value,kategori:$('#f-s-kategori').value,konu:$('#f-s-konu').value.trim(),tarih:$('#f-s-tarih').value});
    bildir('Şikâyet eklendi');$('#f-s-konu').value='';sikayetYukle();ozetYukle();
  }catch(err){bildir(err.message,'hata');}
});

// ---- entegrasyonlar ----
let PLATFORMLAR=[];
function eSecilenPlatform(){return PLATFORMLAR.find(p=>p.id===$('#e-platform').value)||PLATFORMLAR[0];}
function alanlariKur(){
  const p=eSecilenPlatform();
  if(!p)return;
  $('#e-yetenek').innerHTML=(p.yetkinlik||[]).map(y=>'<span class="rozet r-mavi">'+esc(y)+'</span>').join(' ');
  $('#e-alanlar').innerHTML=(p.alanlar||[]).map(a=>
    '<label>'+esc(a.ad)+
    '<input data-alan="'+esc(a.id)+'" data-gizli="'+(a.gizli?1:0)+'" type="'+(a.gizli?'password':'text')+'" placeholder="'+esc(a.varsayilan||'')+'">'+
    (a.ipucu?'<span class="not" style="margin:0">'+esc(a.ipucu)+'</span>':'')+
    '</label>').join('');
  $('#e-not').textContent=p.not||'';
}
function entegrasyonDegerleri(){
  const p=eSecilenPlatform(),ayarlar={},kimlik={};
  document.querySelectorAll('#e-alanlar input').forEach(i=>{
    const v=i.value.trim();
    if(!v)return;
    (i.dataset.gizli==='1'?kimlik:ayarlar)[i.dataset.alan]=v;
  });
  return {platform:p?p.id:'',ad:$('#e-ad').value.trim(),ayarlar,kimlik};
}
function sonucKutu(s){
  const baslik=s.durum==='ok'?'Başarılı':(s.durum==='ag'?'Ağ hatası':(s.durum==='uyari'?'Veri okunamadı':'Hata'));
  return '<div class="'+(s.durum==='ok'?'basari-cubugu':'uyari-cubugu')+'"><b>'+baslik+'.</b> '+esc(s.mesaj||'')+'</div>';
}
function senkronKutu(s){
  let html=sonucKutu(s);
  if(s.sayi){
    html+='<div class="sonuc-kutu">'+
      '<div class="mini"><div class="etiket">Yeni sipariş</div><div class="deger">'+s.sayi.siparis_yeni+'</div></div>'+
      '<div class="mini"><div class="etiket">Güncellenen</div><div class="deger">'+s.sayi.siparis_guncel+'</div></div>'+
      '<div class="mini"><div class="etiket">Gönderi</div><div class="deger">'+(s.sayi.gonderi_yeni+s.sayi.gonderi_guncel)+'</div></div>'+
      '<div class="mini"><div class="etiket">İade</div><div class="deger">'+(s.sayi.iade_yeni+s.sayi.iade_guncel)+'</div></div>'+
      '</div>';
  }
  if(s.aralik)html+='<div class="not">Aralık: '+esc(s.aralik.bas)+' → '+esc(s.aralik.bit)+'</div>';
  if(s.notlar&&s.notlar.length)html+='<div class="not">'+s.notlar.map(n=>esc(n)).join('<br>')+'</div>';
  return html;
}
function eRozet(s){
  if(!s)return '<span class="rozet r-gri">—</span>';
  const cls=s==='ok'?'r-yesil':(s==='uyari'?'r-sari':'r-kirmizi');
  const ad=s==='ok'?'Sorunsuz':(s==='uyari'?'Veri okunamadı':(s==='ag'?'Ağ hatası':'Hata'));
  return '<span class="rozet '+cls+'">'+ad+'</span>';
}
function entegrasyonTablo(liste){
  $('#e-tablo').innerHTML=liste.length?liste.map(k=>
    '<tr><td>'+k.id+'</td><td>'+esc(k.platform_ad)+'</td><td>'+esc(k.ad)+'</td>'+
    '<td>'+(k.dolu.length?'<span class="rozet r-yesil">'+k.dolu.length+' alan dolu</span>':'<span class="rozet r-sari">eksik</span>')+'</td>'+
    '<td>'+(k.son_test?eRozet(k.son_test_sonuc)+'<div class="not">'+esc(k.son_test)+'</div>':'<span class="rozet r-gri">Test edilmedi</span>')+'</td>'+
    '<td>'+(k.son_sync?eRozet(k.son_sync_sonuc)+'<div class="not">'+esc(k.son_sync)+' · '+(k.son_sync_sayi||0)+' kayıt</div>':'<span class="rozet r-gri">Çekilmedi</span>')+'</td>'+
    '<td><button class="kucuk ikincil" data-islem="test" data-id="'+k.id+'">Test</button> <button class="kucuk" data-islem="senkron" data-id="'+k.id+'">Senkronize et</button> <button class="kucuk tehlike" data-islem="sil" data-id="'+k.id+'">Sil</button></td></tr>'
  ).join(''):'<tr><td colspan="7" class="bos">Bağlı hesap yok — yukarıdan hesabınızı bağlayın.</td></tr>';
}
async function entegrasyonYukle(){
  try{
    const d=await api('/api/entegrasyonlar');
    PLATFORMLAR=d.platformlar;
    if(!$('#e-platform').options.length){
      $('#e-platform').innerHTML=d.platformlar.map(p=>'<option value="'+p.id+'">'+esc(p.ad)+'</option>').join('');
      alanlariKur();
    }
    entegrasyonTablo(d.liste);
  }catch(e){bildir(e.message,'hata');}
}
$('#e-platform').addEventListener('change',alanlariKur);
$('#e-yenile').addEventListener('click',entegrasyonYukle);
$('#e-test').addEventListener('click',async()=>{
  try{
    const t=entegrasyonDegerleri();
    $('#e-sonuc').innerHTML='<p class="bos">Test ediliyor…</p>';
    const s=await post('/api/entegrasyonlar/test',t);
    $('#e-sonuc').innerHTML=sonucKutu(s);
    bildir(s.mesaj,s.durum==='ok'?'ok':'hata');
  }catch(e){
    $('#e-sonuc').innerHTML='<p class="bos">Test tamamlanmadı: '+esc(e.message)+'</p>';
    bildir(e.message,'hata');
  }
});
$('#e-kaydet').addEventListener('click',async()=>{
  try{
    const k=await post('/api/entegrasyonlar',entegrasyonDegerleri());
    bildir('"'+k.ad+'" kaydedildi');
    $('#e-ad').value='';
    alanlariKur();
    $('#e-sonuc').innerHTML='<div class="basari-cubugu">Bağlantı kaydedildi. Tablodan <b>Senkronize et</b> ile siparişleri çekin.</div>';
    await entegrasyonYukle();
  }catch(e){bildir(e.message,'hata');}
});
$('#e-tablo').addEventListener('click',async e=>{
  const b=e.target.closest('button[data-islem]');
  if(!b)return;
  const id=b.dataset.id,islem=b.dataset.islem;
  b.disabled=true;
  try{
    if(islem==='test'){
      $('#e-sonuc').innerHTML='<p class="bos">Test ediliyor…</p>';
      const s=await post('/api/entegrasyonlar/'+id+'/test');
      $('#e-sonuc').innerHTML=sonucKutu(s);
      bildir(s.mesaj,s.durum==='ok'?'ok':'hata');
      await entegrasyonYukle();
    }else if(islem==='senkron'){
      $('#e-sonuc').innerHTML='<p class="bos">Veriler çekiliyor…</p>';
      const s=await post('/api/entegrasyonlar/'+id+'/senkron',{gun:Number($('#e-gun').value||30)});
      $('#e-sonuc').innerHTML=senkronKutu(s);
      bildir(s.mesaj||'Senkron tamamlandı',s.durum==='ok'?'ok':'hata');
      await entegrasyonYukle();
      ozetYukle();
    }else if(islem==='sil'){
      if(!window.confirm('Bu bağlantı silinsin mi? Daha önce çekilmiş veriler silinmez.'))return;
      await post('/api/entegrasyonlar/'+id+'/sil');
      bildir('Bağlantı silindi');
      await entegrasyonYukle();
    }
  }catch(err){
    bildir(err.message,'hata');
    $('#e-sonuc').innerHTML='<p class="bos">İşlem tamamlanmadı: '+esc(err.message)+'</p>';
  }
  b.disabled=false;
});

// ---- sms ----
async function smsYukle(){
  try{
    const d=await api('/api/sms');
    const etkin=!!(d.durum&&d.durum.etkin);
    $('#sms-makine').textContent=(d.durum&&d.durum.makine)||'—';
    const r=$('#sms-rozet');
    r.textContent=etkin?'Etkin':'Kilitli';
    r.className='rozet '+(etkin?'r-yesil':'r-kirmizi');
    $('#sms-kilit').classList.toggle('gizle',etkin);
    $('#sms-ayar').classList.toggle('gizle',!etkin);
    const a=d.ayarlar||{};
    if(a.kullanici)$('#sms-kullanici').value=a.kullanici;
    if(a.baslik)$('#sms-baslik').value=a.baslik;
    if(a.apiAdres)$('#sms-adres').value=a.apiAdres;
    const liste=d.gecmis||[];
    $('#sms-tablo').innerHTML=liste.length?liste.map(s=>
      '<tr><td>'+s.id+'</td><td>'+esc(s.alici)+'</td><td>'+esc(s.mesaj)+'</td>'+
      '<td>'+esc(s.baslik||'—')+'</td><td><span class="rakam">'+esc(s.gonderim_zamani)+'</span></td>'+
      '<td>'+(s.durum==='ok'?'<span class="rozet r-yesil">Gönderildi</span>':'<span class="rozet r-kirmizi">Hata</span>')+
      (s.sonuc?'<div class="not" style="margin:0">'+esc(s.sonuc)+'</div>':'')+'</td></tr>'
    ).join(''):'<tr><td colspan="6" class="bos">Kayıt yok</td></tr>';
  }catch(e){bildir(e.message,'hata');}
}
$('#sms-etkinlestir').addEventListener('click',async()=>{
  const kod=$('#sms-kod').value.trim();
  if(!kod){bildir('Entegrasyon kodunu girin','hata');return;}
  try{
    const d=await post('/api/sms/etkinlestir',{kod});
    $('#sms-kod').value='';
    $('#sms-kilit-sonuc').innerHTML='<div class="basari-cubugu">'+esc(d.mesaj||'Etkinleştirildi.')+'</div>';
    bildir(d.mesaj||'SMS entegrasyonu etkinleştirildi');
    await smsYukle();
  }catch(e){
    $('#sms-kilit-sonuc').innerHTML='<div class="uyari-cubugu">'+esc(e.message)+'</div>';
    bildir(e.message,'hata');
  }
});
$('#sms-kaydet').addEventListener('click',async()=>{
  try{
    await post('/api/sms/ayar',{
      kullanici:$('#sms-kullanici').value.trim(),
      parola:$('#sms-parola').value,
      baslik:$('#sms-baslik').value.trim(),
      apiAdres:$('#sms-adres').value.trim()
    });
    $('#sms-parola').value='';
    bildir('Gönderici ayarları kaydedildi');
    await smsYukle();
  }catch(e){bildir(e.message,'hata');}
});
$('#sms-kaldir').addEventListener('click',async()=>{
  if(!window.confirm('SMS entegrasyonu kilitlensin mi? Gönderici ayarlarınız korunur.'))return;
  try{
    const d=await post('/api/sms/kaldir');
    bildir(d.mesaj||'SMS entegrasyonu kilitlendi');
    $('#sms-kilit-sonuc').innerHTML='';
    await smsYukle();
  }catch(e){bildir(e.message,'hata');}
});
$('#sms-gonder').addEventListener('click',async()=>{
  try{
    const d=await post('/api/sms/gonder',{alici:$('#sms-alici').value.trim(),mesaj:$('#sms-mesaj').value});
    $('#sms-sonuc').innerHTML=sonucKutu(d);
    bildir(d.mesaj||'SMS gönderildi',d.durum==='ok'?'ok':'hata');
    if(d.durum==='ok')$('#sms-mesaj').value='';
    await smsYukle();
  }catch(e){
    $('#sms-sonuc').innerHTML='<div class="uyari-cubugu">'+esc(e.message)+'</div>';
    bildir(e.message,'hata');
  }
});

// ---- kargo API ----
let KA_FIRMALAR=[];
function kaSecilen(){return KA_FIRMALAR.find(f=>f.id===$('#ka-firma').value)||KA_FIRMALAR[0];}
function kaAlanlariKur(){
  const f=kaSecilen();if(!f)return;
  $('#ka-not').textContent=f.not||'';
  $('#ka-alanlar').innerHTML=(f.alanlar||[]).map(a=>
    '<label>'+esc(a.ad)+
    '<input data-alan="'+esc(a.id)+'" data-gizli="'+(a.gizli?1:0)+'" type="'+(a.gizli?'password':'text')+'" placeholder="'+esc(a.varsayilan||'')+'">'+
    (a.ipucu?'<span class="not" style="margin:0">'+esc(a.ipucu)+'</span>':'')+
    '</label>').join('');
}
function kaDegerleri(){
  const f=kaSecilen(),ayarlar={},kimlik={};
  document.querySelectorAll('#ka-alanlar input').forEach(i=>{
    const v=i.value.trim();
    if(!v)return;
    (i.dataset.gizli==='1'?kimlik:ayarlar)[i.dataset.alan]=v;
  });
  return {firma:f?f.id:'',ad:$('#ka-ad').value.trim(),ayarlar,kimlik};
}
async function kargoApiYukle(){
  try{
    const d=await api('/api/kargo/api');
    KA_FIRMALAR=d.firmalar||[];
    if(!$('#ka-firma').options.length){
      $('#ka-firma').innerHTML=KA_FIRMALAR.map(f=>'<option value="'+f.id+'">'+esc(f.ad)+'</option>').join('');
      kaAlanlariKur();
    }
    const liste=d.liste||[];
    $('#ka-tablo').innerHTML=liste.length?liste.map(k=>
      '<tr><td>'+k.id+'</td><td>'+esc(k.platform_ad)+'</td><td>'+esc(k.ad)+'</td>'+
      '<td>'+(k.dolu.length?'<span class="rozet r-yesil">'+k.dolu.length+' alan dolu</span>':'<span class="rozet r-sari">eksik</span>')+'</td>'+
      '<td>'+(k.son_test?eRozet(k.son_test_sonuc)+'<div class="not">'+esc(k.son_test)+'</div>':'<span class="rozet r-gri">Test edilmedi</span>')+'</td>'+
      '<td><button class="kucuk ikincil" data-ka="test" data-id="'+k.id+'">Test</button> '+
      '<button class="kucuk tehlike" data-ka="sil" data-id="'+k.id+'">Sil</button></td></tr>'
    ).join(''):'<tr><td colspan="6" class="bos">Bağlı kargo API\'si yok — yukarıdan bilgilerinizi girin.</td></tr>';
  }catch(e){bildir(e.message,'hata');}
}
$('#ka-firma').addEventListener('change',kaAlanlariKur);
$('#ka-yenile').addEventListener('click',kargoApiYukle);
$('#ka-test').addEventListener('click',async()=>{
  try{
    $('#ka-sonuc').innerHTML='<p class="bos">Test ediliyor…</p>';
    const s=await post('/api/kargo/api/test',kaDegerleri());
    $('#ka-sonuc').innerHTML=sonucKutu(s);
    bildir(s.mesaj,s.durum==='ok'?'ok':'hata');
  }catch(e){
    $('#ka-sonuc').innerHTML='<p class="bos">Test tamamlanmadı: '+esc(e.message)+'</p>';
    bildir(e.message,'hata');
  }
});
$('#ka-kaydet').addEventListener('click',async()=>{
  try{
    const k=await post('/api/kargo/api',kaDegerleri());
    bildir('"'+k.ad+'" kaydedildi');
    $('#ka-ad').value='';
    kaAlanlariKur();
    $('#ka-sonuc').innerHTML='<div class="basari-cubugu">Bağlantı kaydedildi. "Takip durumlarını güncelle" ile gönderiler sorulur.</div>';
    await kargoApiYukle();
  }catch(e){bildir(e.message,'hata');}
});
$('#ka-senkron').addEventListener('click',async()=>{
  try{
    $('#ka-senkron-sonuc').innerHTML='<p class="bos">Durumlar sorgulanıyor…</p>';
    const s=await post('/api/kargo/senkron');
    $('#ka-senkron-sonuc').innerHTML=sonucKutu(s)+
      ((s.notlar&&s.notlar.length)?'<div class="not">'+s.notlar.map(n=>esc(n)).join('<br>')+'</div>':'');
    bildir(s.mesaj||'Senkron tamamlandı',s.durum==='ok'?'ok':'hata');
    await gonderilerYukle();
    ozetYukle();
  }catch(e){
    $('#ka-senkron-sonuc').innerHTML='<p class="bos">'+esc(e.message)+'</p>';
    bildir(e.message,'hata');
  }
});
$('#ka-tablo').addEventListener('click',async e=>{
  const b=e.target.closest('button[data-ka]');
  if(!b)return;
  const id=b.dataset.id,islem=b.dataset.ka;
  b.disabled=true;
  try{
    if(islem==='test'){
      $('#ka-sonuc').innerHTML='<p class="bos">Test ediliyor…</p>';
      const s=await post('/api/kargo/api/'+id+'/test');
      $('#ka-sonuc').innerHTML=sonucKutu(s);
      bildir(s.mesaj,s.durum==='ok'?'ok':'hata');
      await kargoApiYukle();
    }else if(islem==='sil'){
      if(!window.confirm('Bu kargo API bağlantısı silinsin mi?'))return;
      await post('/api/kargo/api/'+id+'/sil');
      bildir('Bağlantı silindi');
      await kargoApiYukle();
    }
  }catch(err){bildir(err.message,'hata');}
  b.disabled=false;
});

// ---- güncelleme ----
async function guncellemeKontrol(){
  try{
    const d=await api('/api/guncelleme');
    if(!d||!d.yeni_var)return;
    const b=$('#guncelleme-band');
    let html='<b>Yeni sürüm var: '+esc(d.son)+'</b><span>kurulu sürüm '+esc(d.mevcut)+'</span>';
    if(d.not)html+='<span>'+esc(d.not)+'</span>';
    if(d.indirme)html+='<a href="'+esc(d.indirme)+'" target="_blank" rel="noopener">İndir →</a>';
    else html+='<span>Güncel dosyaları satış kanalından isteyin.</span>';
    b.innerHTML=html;
    b.classList.remove('gizle');
  }catch(e){}
}

// ---- csv ----
function csvHazir(){
  if(!$('#v-tablo').options.length){
    $('#v-tablo').innerHTML=secenekler(META.csv_tablolari);
    $('#v-etiket').classList.remove('gizle');
  }
  const t=$('#v-tablo').value;
  $('#v-sablon').href='/api/sablon?tablo='+t;
  $('#v-indir').href='/api/export/csv?tablo='+t;
}
$('#v-tablo').addEventListener('change',csvHazir);
$('#v-yukle').addEventListener('click',async()=>{
  const dosya=$('#v-dosya').files[0];
  if(!dosya){bildir('Önce bir CSV dosyası seçin','hata');return;}
  try{
    const metin=await dosya.text();
    const d=await api('/api/import/csv?tablo=siparisler',{method:'POST',headers:{'Content-Type':'text/plain; charset=utf-8'},body:metin});
    let html='<div class="basari-cubugu"><b>'+d.eklenen+'</b> sipariş yüklendi ('+d.toplam+' satır).</div>';
    if(d.hatalar.length)html+='<div class="uyari-cubugu"><b>'+d.hatalar.length+' satır atlandı:</b><ul>'+d.hatalar.map(h=>'<li>'+esc(h)+'</li>').join('')+'</ul></div>';
    $('#v-sonuc').innerHTML=html;
    bildir(d.eklenen+' sipariş yüklendi');
    ozetYukle();
  }catch(e){bildir(e.message,'hata');}
});

// ---- başlangıç ----
async function baslat(){
  try{
    META=await api('/api/meta');
    lisansGoster(META.lisans);
    const surum=$('#f-surum');if(surum)surum.textContent=META.surum;
    if(META.lisans&&META.lisans.durum==='suresi_doldu')return;
    IADE_ETIKET=Object.fromEntries(META.iade_durumlari.map(x=>[x.id,x.ad]));
    $('#f-i-sebep').innerHTML=secenekler(META.sebepler);
    $('#f-i-tarih').value=bugun();
    $('#f-k-firma').innerHTML=secenekler(META.kargo_firmalari);
    $('#f-k-bas').value=bugun();$('#f-k-bit').value=gunEkle(0,3);
    $('#f-s-kaynak').innerHTML=secenekler(META.sikayet_kaynaklari);
    $('#f-s-kategori').innerHTML=secenekler(META.sikayet_kategorileri);
    $('#f-s-tarih').value=bugun();
    $('#v-tablo').innerHTML=secenekler(META.csv_tablolari);
    $('#v-etiket').classList.remove('gizle');
    await siparisleriYukle();
    ozetYukle();
    const h=location.hash.slice(1);
    if(h&&['ozet','iade','kargo','kar','sikayet','entegrasyon','sms','csv'].includes(h))sekmeAc(h);
    else if(h==='kargo-api'){
      sekmeAc('kargo');
      setTimeout(()=>{const k=$('#ka-panel');if(k)k.scrollIntoView();},150);
    }
    guncellemeKontrol();
  }catch(e){bildir('Başlatma hatası: '+e.message,'hata');}
}
document.addEventListener('DOMContentLoaded',baslat);
</script>
</body>
</html>"""
