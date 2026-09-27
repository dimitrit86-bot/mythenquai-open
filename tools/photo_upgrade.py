"""Guarded change on the existing 1.8.1 source. Never read or migrate user data."""
from pathlib import Path
import hashlib,json
p=Path('kompass')
def rep(s,a,b):
    assert s.count(a)==1,(a[:100],s.count(a))
    return s.replace(a,b)
s=(p/'scanner.js').read_text()
if 'readPhotoText' in s:
    print('Already applied');raise SystemExit(0)
for name,sha in [('scanner.js','9e5ca8ec83a560a9800c1a7f8b86031bcfefaab7'),('app.js','4c152dca785dab3855705f8d343bbe44d686a9d7'),('index.html','078a7cbbb2d71a84b4b229732bb4a16c3d6464b1')]:
    data=(p/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==sha, 'Unexpected source: '+name
s=rep(s,"let openOptions={};","let openOptions={},scanProfile='',ocrCache={};")
s=rep(s,'function stop(){scanGeneration++;','function stop(){scanGeneration++;root.NK_PHOTO_PRODUCT?.reset();ocrCache={};')
s=rep(s,"function open(opts={}){stop();openOptions=opts;","function open(opts={}){stop();openOptions=opts;scanProfile=root.NK_HOUSEHOLD?.id||'';")
s=rep(s,'Nährwerttabelle fotografieren oder Barcode verwenden. Fotos werden nur auf deinem Gerät verarbeitet und nicht hochgeladen.','Ein Foto, zwei Möglichkeiten: Produktbeschriftung erkennen und passende Nährwerte online suchen – oder die Nährwerttabelle direkt auslesen. Fotos bleiben auf deinem Gerät. Bei der Produktsuche wird nur der erkannte Suchbegriff / Barcode gesendet.')
s=rep(s,'for="nutrition-photo">Nährwerttabelle fotografieren','for="nutrition-photo">Packung fotografieren')
s=rep(s,'alt="Dein Foto der Nährwerttabelle"','alt="Dein Foto der Produktpackung oder Nährwerttabelle"')
s=rep(s,'<p class="tiny">Die Tabelle möglichst gerade, scharf und ohne Spiegelungen aufnehmen. Bei mehreren Spalten unten die richtige Spalte wählen.</p><button class="button" id="recognize-photo" type="button">Nährwerte auslesen</button>','<p class="tiny">Vorderseite mit Marke und Sorte für die Produktsuche; Nährwerttabelle für direktes Auslesen. Möglichst gerade, scharf und ohne Spiegelungen aufnehmen. Du kannst mit demselben Foto zwischen beiden Wegen wechseln.</p><div class="scan-photo-actions"><button class="button" id="recognize-product" type="button">Produkt erkennen &amp; suchen<small>Marke / Barcode lesen · passende Produktdaten online finden</small></button><button class="button secondary" id="recognize-photo" type="button">Nährwerttabelle auslesen<small>Zahlen direkt übernehmen · Bezugsmenge korrigieren</small></button></div>')
s=rep(s,"$('#recognize-photo').onclick=recognize;","$('#recognize-photo').onclick=recognize;$('#recognize-product').onclick=identifyProduct;")
s=rep(s,"$('#parse-text').onclick=()=>{rawText=","$('#parse-text').onclick=()=>{root.NK_PHOTO_PRODUCT?.pause();$('#scan-review').hidden=false;rawText=")
a=s.index('async function photo(e)');b=s.index('function review(){',a)
s=s[:a]+r'''function scanCurrent(generation){return generation===scanGeneration&&dlg.open&&scanProfile===(root.NK_HOUSEHOLD?.id||'');}
function setBusy(value){scanBusy=value;for(const id of ['recognize-photo','recognize-product','barcode-camera','barcode-find']){const el=$('#'+id);if(el)el.disabled=value;}}
async function photo(e){
 const file=e.target.files[0];if(!file)return;stop();const generation=scanGeneration;
 $('.scan-image').hidden=true;$('#scan-review').innerHTML='';$('#scan-review').hidden=false;rawText='';barcodeProduct=null;setBusy(false);
 let url;try{if(file.size>25*1024*1024)throw Error('Foto zu gross. Bitte unter 25 MB aufnehmen.');url=URL.createObjectURL(file);const img=new Image();img.src=url;await img.decode();if(!scanCurrent(generation)){URL.revokeObjectURL(url);return;}imageURL=url;image=img;$('#scan-photo-preview').src=url;$('.scan-image').hidden=false;message('Foto bereit. Wähle «Produkt erkennen & suchen» oder «Nährwerttabelle auslesen».');}
 catch(err){if(url)URL.revokeObjectURL(url);if(scanCurrent(generation))message('Foto nicht lesbar. Bitte JPEG, PNG oder WebP verwenden. '+err.message);}
}
async function readPhotoText(mode='nutrition'){
 if(!image)throw Error('Bitte zuerst ein Foto wählen.');if(ocrCache[mode]!==undefined)return ocrCache[mode];if(scanBusy)throw Error('Erkennung läuft bereits.');
 const generation=scanGeneration,sourceImage=image;let ownWorker=null;setBusy(true);
 try{await load('vendor/tesseract.min.js','Tesseract');if(!scanCurrent(generation))throw Error('Erkennung beendet.');message('Texterkennung wird geladen …');
 ownWorker=await Tesseract.createWorker('deu+eng',1,{workerPath:new URL('vendor/worker.min.js',location.href).href,corePath:new URL('vendor/core',location.href).href,langPath:new URL('vendor/lang',location.href).href,logger:m=>{if(scanCurrent(generation)&&m.progress!=null)message('Texterkennung: '+Math.round(m.progress*100)+' %');}});
 if(!scanCurrent(generation))throw Error('Erkennung beendet.');worker=ownWorker;
 await ownWorker.setParameters({tessedit_pageseg_mode:mode==='product'?'11':'6'});
 const canvas=document.createElement('canvas'),scale=Math.min(1,2400/Math.max(sourceImage.naturalWidth,sourceImage.naturalHeight));canvas.width=Math.max(1,Math.round(sourceImage.naturalWidth*scale));canvas.height=Math.max(1,Math.round(sourceImage.naturalHeight*scale));canvas.getContext('2d').drawImage(sourceImage,0,0,canvas.width,canvas.height);
 const result=await ownWorker.recognize(canvas);if(!scanCurrent(generation))throw Error('Erkennung beendet.');return ocrCache[mode]=String(result.data.text||'').slice(0,30000);
 }finally{await ownWorker?.terminate().catch(()=>{});if(generation===scanGeneration){worker=null;setBusy(false);}}
}
async function recognize(){if(scanBusy||!image)return;const generation=scanGeneration;root.NK_PHOTO_PRODUCT?.pause();$('#scan-review').hidden=false;
 // Mode switching keeps already edited nutrition values rather than reading/scaling twice.
 if($('#scan-review').children.length&&!barcodeProduct)return;
 try{rawText=await readPhotoText('nutrition');if(!scanCurrent(generation))return;barcodeProduct=null;review();message('Ausgelesen. Zahlen und Bezugsmenge mit dem Foto vergleichen.');}
 catch(err){if(scanCurrent(generation))message('Automatisches Auslesen fehlgeschlagen: '+err.message+' Du kannst die Tabelle als Text oder manuell erfassen.');}
}
function photoTransfer(f,existing){
 const done=openOptions.onTransfer;
 if(done){if(existing)f={...f,id:'custom-'+crypto.randomUUID()};done(f);stop();dlg.close();openOptions={};}
 else{stop();dlg.close();if(existing)root.NK_APP.openFood(f);else root.NK_APP.reviewFood(f);}
}
async function identifyProduct(){if(scanBusy||!image)return;const generation=scanGeneration;controls?.stop();controls=null;$('#barcode-video').hidden=true;$('#scan-review').hidden=true;
 try{await root.NK_PHOTO_PRODUCT.identify({image,load,readText:readPhotoText,current:()=>scanCurrent(generation),transfer:photoTransfer});}
 catch(e){if(scanCurrent(generation))message('Produktsuche nicht möglich: '+e.message);}
}
''' + s[b:]
s=rep(s,'async function lookup(code){code=', 'async function lookup(code){const generation=scanGeneration;root.NK_PHOTO_PRODUCT?.pause();code=')
s=rep(s,"barcodeProduct={...r.product,code:r.product.code||code};review();", "if(!scanCurrent(generation))return;$('#scan-review').hidden=false;barcodeProduct={...r.product,code:r.product.code||code};review();")
s=rep(s,"document.addEventListener('click',e=>{if(e.target.closest('[data-nk-scan]'))", "document.addEventListener('nk-profile-loaded',()=>{if(dlg.open&&scanProfile!==(root.NK_HOUSEHOLD?.id||'')){stop();dlg.close();}});\ndlg.addEventListener('close',stop);\ndocument.addEventListener('click',e=>{if(e.target.closest('[data-nk-scan]'))")
(p/'scanner.js').write_text(s)
s=(p/'app.js').read_text()
s=rep(s,'function openCustomText(){','function openCustomText(textOnly=true){')
s=rep(s,'open({textOnly:true,name:', 'open({textOnly,name:')
s=rep(s,"else if(a==='custom-text')openCustomText();", "else if(a==='custom-text')openCustomText();\n else if(a==='custom-photo')openCustomText(false);")
s=rep(s,'${btn("Nährwerttext auslesen","custom-text","secondary")}', '${btn("Nährwerttext auslesen","custom-text","secondary")} ${btn("Foto: Produkt oder Nährwerte","custom-photo","secondary")}')
s=rep(s,'Nährwerttext übernommen. Noch nicht gespeichert.', 'Produktwerte übernommen. Noch nicht gespeichert.')
(p/'app.js').write_text(s)
# Conservatively preserve all other modules and libraries; only release references change.
for name in ['index.html','sw.js','device.js','household.js','version.json']:
 s=(p/name).read_text().replace('1.8.1','1.9.0')
 if name=='index.html':
  s=rep(s,'<script src="scanner.js?v=1.9.0">','<script src="photo-product.js?v=1.9.0"></script><script src="scanner.js?v=1.9.0">')
  s=rep(s,'<title>Nährstoff-Kompass</title>','<link rel="stylesheet" href="photo-product.css?v=1.9.0"><title>Nährstoff-Kompass</title>')
  s=s.replace('Stückportionen & Nährwerttext','Foto: Produkt finden & Nährwerte auslesen')
 elif name=='sw.js':
  s=rep(s,"const scripts=[","const scripts=['photo-product.js',")
  s=rep(s,"const SHELL=[","const SHELL=['./photo-product.css?v='+VERSION,")
 elif name=='device.js':
  s=rep(s,'if(window.NK_APP?.hasDraft||unsavedForm())','if(document.querySelector("#scan-dialog[open]")||window.NK_APP?.hasDraft||unsavedForm())')
 (p/name).write_text(s)
print('Photo update applied, existing data and server logic untouched.')
