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
:root{--bg:#0b1220;--panel:#131c2e;--line:#223050;--txt:#e6edf7;--mut:#8fa3c0;--acc:#3b82f6;--ok:#22c55e;--uy:#f59e0b;--kotu:#ef4444}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.5 system-ui,"Segoe UI",Roboto,Arial,sans-serif}
header{display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;padding:12px 18px;background:var(--panel);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
.marka{display:flex;align-items:center;gap:11px}
.marka svg{width:44px;height:44px;display:block}
.marka b{font-size:19px;letter-spacing:.2px}
.marka span{display:block;color:var(--mut);font-size:12px}
#menu{display:flex;flex-wrap:wrap;gap:6px}
#menu button{background:#0e1626;border:1px solid var(--line);color:var(--mut);padding:8px 13px;border-radius:9px;font-size:14px;font-weight:600;cursor:pointer}
#menu button:hover{color:var(--txt);border-color:#31507f}
#menu button.aktif{background:var(--acc);border-color:var(--acc);color:#fff}
main{padding:18px;max-width:1240px;margin:0 auto}
.sekme{display:none}
.sekme.aktif{display:block}
.baslik-satir{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;margin-bottom:12px}
.baslik-satir h2{margin:0;font-size:18px}
.baslik-satir p{margin:2px 0 0;color:var(--mut);font-size:13px}
.kartlar{display:grid;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));gap:12px}
.kart{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:14px}
.kart .etiket{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.07em}
.kart .deger{font-size:25px;font-weight:700;margin-top:5px}
.iy{color:#4ade80}.kt{color:#f87171}.uy{color:#fbbf24}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:16px;margin-top:14px}
.panel h3{margin:0 0 12px;font-size:15px}
.ust{display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:14px}
label{display:flex;flex-direction:column;gap:5px;font-size:12px;color:var(--mut);font-weight:600}
input,select,textarea{padding:9px 11px;border-radius:9px;border:1px solid var(--line);background:#0e1626;color:var(--txt);font-size:14px;font-family:inherit;min-width:120px}
input:focus,select:focus{outline:none;border-color:var(--acc)}
button{padding:9px 15px;border:0;border-radius:9px;background:var(--acc);color:#fff;font-weight:600;cursor:pointer;font-size:14px}
button:hover{filter:brightness(1.08)}
button.ikincil{background:#26344f}
button.tehlike{background:#b91c1c}
button.kucuk{padding:6px 10px;font-size:13px}
.dugme{display:inline-block;padding:9px 15px;border-radius:9px;background:var(--acc);color:#fff;font-weight:600;font-size:14px;text-decoration:none;cursor:pointer}
.dugme:hover{filter:brightness(1.08)}
.dugme.ikincil{background:#26344f}
table{width:100%;border-collapse:collapse}
th,td{padding:9px 10px;border-bottom:1px solid var(--line);text-align:left;font-size:14px;vertical-align:middle}
th{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.06em}
tr:hover td{background:#16203a33}
.rozet{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap}
.r-kirmizi{background:#ef44441f;color:#f87171;border:1px solid #ef444455}
.r-yesil{background:#22c55e1f;color:#4ade80;border:1px solid #22c55e55}
.r-sari{background:#f59e0b1f;color:#fbbf24;border:1px solid #f59e0b55}
.r-mavi{background:#3b82f61f;color:#93c5fd;border:1px solid #3b82f655}
.r-gri{background:#8fa3c01f;color:#8fa3c0;border:1px solid #8fa3c055}
.cubuk{display:grid;grid-template-columns:minmax(120px,210px) 1fr 66px;gap:11px;align-items:center;margin:8px 0;font-size:13px}
.cubuk .yol{background:#0e1626;border-radius:7px;height:11px;overflow:hidden;border:1px solid var(--line)}
.cubuk .yol i{display:block;height:100%;background:linear-gradient(90deg,#3b82f6,#12a293)}
.cubuk b{text-align:right;color:var(--mut)}
.uyari-cubugu{background:#f59e0b14;border:1px solid #f59e0b55;color:#fbbf24;padding:10px 13px;border-radius:10px;font-size:13px;margin-top:12px}
.basari-cubugu{background:#22c55e14;border:1px solid #22c55e55;color:#4ade80;padding:10px 13px;border-radius:10px;font-size:13px;margin-top:12px}
.bos{color:var(--mut);font-size:14px}
.izgara2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.sonuc-kutu{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin-top:12px}
.mini{background:#0e1626;border:1px solid var(--line);border-radius:11px;padding:12px}
.mini .etiket{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.06em}
.mini .deger{font-size:21px;font-weight:700;margin-top:4px}
#bildirim{position:fixed;right:18px;bottom:18px;padding:12px 16px;border-radius:11px;font-size:14px;font-weight:600;opacity:0;transform:translateY(8px);transition:.2s;z-index:50;max-width:360px}
#bildirim.acik{opacity:1;transform:none}
#bildirim.ok{background:#14532d;color:#bbf7d0;border:1px solid #22c55e}
#bildirim.hata{background:#7f1d1d;color:#fecaca;border:1px solid #ef4444}
.gizle{display:none}
.grafik svg{width:100%;height:auto;display:block}
.not{color:var(--mut);font-size:13px;margin-top:8px}
@media (max-width:760px){.cubuk{grid-template-columns:1fr;gap:4px}.cubuk b{text-align:left}}
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
    <button data-sekme="trend">Trendler</button>
    <button data-sekme="entegrasyon">Entegrasyonlar</button>
    <button data-sekme="csv">CSV</button>
  </nav>
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
  <div class="izgara2">
    <div class="panel"><h3>İade durum dağılımı (14 günlük yasal süre)</h3><div id="ozet-iade"><p class="bos">Veri yok</p></div></div>
    <div class="panel"><h3>Şikâyet kategorileri</h3><div id="ozet-sikayet"><p class="bos">Veri yok</p></div></div>
  </div>
  <div class="izgara2">
    <div class="panel"><h3>Süresi aşan iadeler</h3><div id="ozet-geciken"><p class="bos">Kayıt yok</p></div></div>
    <div class="panel"><h3>Problemli gönderiler</h3><div id="ozet-problem"><p class="bos">Kayıt yok</p></div></div>
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

<section id="sekme-trend" class="sekme">
  <div class="baslik-satir">
    <div><h2>Google Trends — son 5 yıl</h2><p>Canlı API denenir; ulaşılamazsa yerleşik 5 yıllık araştırma verisine düşer (grafik hiç boş kalmaz).</p></div>
  </div>
  <form class="ust" id="form-trend">
    <label>Kategori<select id="t-kategori"></select></label>
    <label>Anahtar kelime<input id="t-anahtar" placeholder="e-ticaret"></label>
    <label style="flex-direction:row;align-items:center;gap:8px"><input type="checkbox" id="t-canli" checked style="min-width:auto"> Canlı Google Trends dene</label>
    <button type="submit">Çek</button>
  </form>
  <div id="t-durum"></div>
  <div class="panel">
    <div class="baslik-satir" style="margin-bottom:6px">
      <div><b id="t-baslik">—</b><div class="not" id="t-ipucu"></div></div>
      <span class="rozet r-mavi" id="t-kaynak">—</span>
    </div>
    <div class="grafik" id="t-grafik"><p class="bos">Veri bekleniyor…</p></div>
    <div class="not" id="t-not"></div>
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
  if(ad==='kargo')gonderilerYukle();
  if(ad==='kar')karVerisi();
  if(ad==='sikayet')sikayetYukle();
  if(ad==='csv')csvHazir();
  if(ad==='entegrasyon')entegrasyonYukle();
  if(ad==='trend'&&!$('#t-grafik').dataset.doldur) trendYukle();
}

// ---- panel ----
async function ozetYukle(){
  try{
    const [d,gec,karListe]=await Promise.all([
      api('/api/ozet'),
      api('/api/iadeler?sadece=geciken'),
      api('/api/gonderiler?sadece=problem')
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

    const dag=d.iade.dagilim||{};
    const toplamI=d.iade.toplam||0;
    $('#ozet-iade').innerHTML=toplamI?Object.keys(dag).map(k=>cubuk(d.iade.etiketler[k]||k,toplamI?dag[k]/toplamI*100:0,dag[k]+' adet')).join(''):'<p class="bos">Kayıt yok</p>';

    const kat=d.sikayet.kategoriler||[];
    $('#ozet-sikayet').innerHTML=d.sikayet.toplam?kat.map(k=>cubuk(k.ad,k.yuzde,k.sayi+' ('+k.yuzde+'%)')).join(''):'<p class="bos">Kayıt yok</p>';

    $('#ozet-geciken').innerHTML=gec.liste.length?gec.liste.map(s=>
      '<div class="cubuk"><span class="ad">'+esc(s.musteri||('#'+s.id))+'</span><div class="yol"><i style="width:'+Math.min(100,Math.abs(s.kalan_gun)*5)+'%;background:#ef4444"></i></div><b class="kt">'+s.kalan_gun+' gün</b></div>').join(''):'<p class="bos">Süresi aşan iade yok</p>';

    $('#ozet-problem').innerHTML=karListe.liste.length?karListe.liste.map(s=>
      '<div class="cubuk"><span class="ad">'+esc(s.kargo_firmasi)+' · '+esc(s.takip_no||'#'+s.id)+'</span><div class="yol"><i style="width:'+Math.min(100,60+s.gecikme_gun*8)+'%;background:#f59e0b"></i></div><b class="uy">'+esc(s.sorun_etiket)+'</b></div>').join(''):'<p class="bos">Problemli gönderi yok</p>';
  }catch(e){bildir('Panel yüklenemedi: '+e.message,'hata');}
}
$('#ozet-yenile').addEventListener('click',ozetYukle);

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

// ---- trend ----
function grafik(seri){
  if(!seri||!seri.length)return '<p class="bos">Seri boş</p>';
  const w=980,h=310,l=46,r=16,t=16,b=36;
  const d=seri.map(p=>Number(p.deger)||0);
  let mx=Math.max.apply(null,d),mn=Math.min.apply(null,d);
  if(mx===mn){mx=mn+1;}
  const N=seri.length;
  const X=i=>l+(N<2?0:i*(w-l-r)/(N-1));
  const Y=v=>t+(mx-v)/(mx-mn)*(h-t-b);
  const nokta=d.map((v,i)=>X(i).toFixed(1)+','+Y(v).toFixed(1)).join(' ');
  const alan=l+','+(h-b)+' '+nokta+' '+X(N-1).toFixed(1)+','+(h-b);
  let cizgi='';
  for(let k=0;k<=4;k++){
    const v=mn+(mx-mn)*k/4,y=Y(v);
    cizgi+='<line x1="'+l+'" y1="'+y.toFixed(1)+'" x2="'+(w-r)+'" y2="'+y.toFixed(1)+'" stroke="#223050"/>'+
      '<text x="'+(l-8)+'" y="'+(y+4).toFixed(1)+'" fill="#8fa3c0" font-size="11" text-anchor="end">'+Math.round(v)+'</text>';
  }
  const adim=Math.max(1,Math.round(N/6));
  let etiket='';
  for(let i=0;i<N;i+=adim){
    etiket+='<text x="'+X(i).toFixed(1)+'" y="'+(h-12)+'" fill="#8fa3c0" font-size="11" text-anchor="middle">'+esc(seri[i].tarih)+'</text>';
  }
  let noktalar='';
  for(let i=0;i<N;i+=Math.max(1,Math.round(N/40))){
    noktalar+='<circle cx="'+X(i).toFixed(1)+'" cy="'+Y(d[i]).toFixed(1)+'" r="2.2" fill="#12a293"/>';
  }
  return '<svg viewBox="0 0 '+w+' '+h+'" role="img" aria-label="Trend grafiği">'+
    '<defs><linearGradient id="dolgu" x1="0" y1="0" x2="0" y2="1">'+
    '<stop offset="0" stop-color="#3b82f6" stop-opacity=".45"/><stop offset="1" stop-color="#3b82f6" stop-opacity="0"/></linearGradient></defs>'+
    cizgi+'<polygon points="'+alan+'" fill="url(#dolgu)"/>'+
    '<polyline points="'+nokta+'" fill="none" stroke="#60a5fa" stroke-width="2.4" stroke-linejoin="round"/>'+
    noktalar+etiket+'</svg>';
}
async function trendYukle(){
  const kutu=$('#t-grafik');
  kutu.innerHTML='<p class="bos">Çekiliyor…</p>';
  try{
    const kategori=$('#t-kategori').value;
    const anahtar=$('#t-anahtar').value.trim()||kategori;
    const canli=$('#t-canli').checked?'1':'0';
    const d=await api('/api/trend?kategori='+encodeURIComponent(kategori)+'&anahtar='+encodeURIComponent(anahtar)+'&canli='+canli);
    kutu.dataset.doldur='1';
    kutu.innerHTML=grafik(d.seri);
    $('#t-baslik').textContent=(d.ad||d.kategori)+' · son 5 yıl ('+d.seri.length+' nokta)';
    $('#t-ipucu').textContent=d.ipucu||'';
    const rozet=$('#t-kaynak');
    if(d.kaynak==='canli'){rozet.textContent='CANLI GOOGLE TRENDS';rozet.className='rozet r-yesil';}
    else{rozet.textContent='YERLEŞİK VERİ';rozet.className='rozet r-sari';}
    $('#t-not').textContent=d.canli_hata?('Canlı veri alınamadı ('+d.canli_hata+') — '+d.kaynak_not):(d.kaynak_not||'');
    $('#t-durum').innerHTML=d.canli_hata?'<div class="uyari-cubugu">Google Trends canlı servisi yanıt vermedi; grafik yerleşik 5 yıllık araştırma verisiyle çizildi. Canlı denemeyi kapatıp tekrar deneyebilirsiniz.</div>':'';
  }catch(e){
    kutu.innerHTML='<p class="bos">Grafik yüklenemedi</p>';
    bildir(e.message,'hata');
  }
}
$('#form-trend').addEventListener('submit',e=>{e.preventDefault();trendYukle();});
$('#t-kategori').addEventListener('change',()=>{
  const k=META.trend_kategorileri.find(x=>x.id===$('#t-kategori').value);
  if(k)$('#t-anahtar').value=k.anahtar;
  trendYukle();
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
    IADE_ETIKET=Object.fromEntries(META.iade_durumlari.map(x=>[x.id,x.ad]));
    $('#f-i-sebep').innerHTML=secenekler(META.sebepler);
    $('#f-i-tarih').value=bugun();
    $('#f-k-firma').innerHTML=secenekler(META.kargo_firmalari);
    $('#f-k-bas').value=bugun();$('#f-k-bit').value=gunEkle(0,3);
    $('#f-s-kaynak').innerHTML=secenekler(META.sikayet_kaynaklari);
    $('#f-s-kategori').innerHTML=secenekler(META.sikayet_kategorileri);
    $('#f-s-tarih').value=bugun();
    $('#t-kategori').innerHTML=secenekler(META.trend_kategorileri.map(x=>({id:x.id,ad:x.ad})));
    const ilk=META.trend_kategorileri[0];
    $('#t-kategori').value=ilk.id;$('#t-anahtar').value=ilk.anahtar;
    $('#v-tablo').innerHTML=secenekler(META.csv_tablolari);
    $('#v-etiket').classList.remove('gizle');
    await siparisleriYukle();
    ozetYukle();
    trendYukle();
  }catch(e){bildir('Başlatma hatası: '+e.message,'hata');}
}
document.addEventListener('DOMContentLoaded',baslat);
</script>
</body>
</html>"""
