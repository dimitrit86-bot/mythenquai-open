/* Local package OCR and barcode recognition. Images never leave the browser. */
(function(root){'use strict';
const fields=[
 ['saturated',/ges[aä]ttigte(?:\s+fetts[aä]uren)?|saturated(?:\s+fat)?|acides gras satur[eé]s|grassi saturi/i,'g'],
 ['sugar',/(?:davon\s+)?zucker|(?:of which\s+)?sugars|sucres|zuccheri/i,'g'],
 ['fiber',/nahrungsfasern|ballaststoffe|(?:dietary\s+)?fibers?|fibres?/i,'g'],
 ['carbs',/kohlenhydrate|carbohydrates?|glucides|carboidrati/i,'g'],
 ['protein',/eiwei(?:ss|ß)|proteine?|prot[eé]ines?/i,'g'],
 ['fat',/fett|(?:total\s+)?fat\b|mati[eè]res grasses|grassi/i,'g'],
 ['salt',/salz|salt\b|sel\b|sale\b/i,'g'],
 ['vitB12',/vitamin[ea]?\s*b\s*12|cobalamin/i,'µg'],['vitB1',/vitamin[ea]?\s*b\s*1\b|thiamin[ea]?/i,'mg'],
 ['vitB2',/vitamin[ea]?\s*b\s*2\b|riboflavin[ea]?/i,'mg'],['vitB6',/vitamin[ea]?\s*b\s*6\b|pyridoxin/i,'mg'],
 ['vitB5',/pantothen(?:s[aä]ure|ic acid)|vitamin[ea]?\s*b\s*5\b/i,'mg'],
 ['vitC',/vitamin[ea]?\s*c\b|ascorbi[cn]/i,'mg'],['vitD',/vitamin[ea]?\s*d[23]?\b/i,'µg'],['vitK',/vitamin[ea]?\s*k[12]?\b/i,'µg'],
 ['biotin',/biotin[ea]?/i,'µg'],['niacin',/niacin[ea]?/i,'mg'],
 ['calcium',/calcium|kalzium/i,'mg'],['magnesium',/magnesium/i,'mg'],['potassium',/kalium|potassium/i,'mg'],
 ['sodium',/natrium|sodium/i,'mg'],['phosphorus',/phosphor(?:us|e)?/i,'mg'],['iron',/eisen|iron|fer\b|ferro/i,'mg'],
 ['zinc',/zink|zinc(?:o)?/i,'mg'],['iodine',/jod|iodine|iode|iodio/i,'µg'],['selenium',/selen(?:ium|io)?/i,'µg']
];
function quantities(s){return [...s.matchAll(/(?<![\d.,+−-])([<≤]?)\s*(\d+(?:[.,]\d+)?)\s*(kcal|kJ|mg|[µμu]g|g)\b/gi)].map(m=>({value:Number(m[2].replace(',','.')),unit:m[3].toLowerCase().replace(/[μu]g/,'µg'),less:!!m[1],raw:m[0].trim()}));}
function parse(text,column='first'){
 const n={},q={},warnings=[],lines=String(text).replace(/\r/g,'').split('\n').filter(Boolean);let basis=/100\s*m\s*l\b/i.test(text)?'ml':'g';
 if(!/100\s*(?:g|ml)\b/i.test(text))warnings.push('Bezugsmenge nicht erkannt. Vor dem Speichern auf 100 g oder 100 ml umrechnen.');
 const expectedColumns=root.NK_PORTIONS?.hints(text).length||1;
 const pick=a=>{if(column==='last'&&expectedColumns>1&&a.length<expectedColumns){warnings.push('Eine Zeile lässt sich der letzten Wertespalte nicht sicher zuordnen und bleibt unbekannt.');return undefined;}return column==='last'?a[a.length-1]:a[0];};
 for(let i=0;i<lines.length;i++){
  let line=lines[i];if(!quantities(line).length&&/^\s*[<≤]?\s*\d/.test(lines[i+1]||''))line+=' '+lines[i+1];
  if(/brennwert|energie|energy|energia|kcal|\bkj\b/i.test(line))for(const [key,u] of [['energy','kcal'],['energyKJ','kj']]){const v=pick(quantities(line).filter(v=>v.unit===u));if(v){if(v.less){n[key]=null;q[key]=v.raw;}else n[key]=v.value;}}
  for(const [key,re,unit] of fields){const match=line.match(re);if(!match)continue;const vals=quantities(line.slice(match.index+match[0].length)).filter(v=>!['kj','kcal'].includes(v.unit));const v=pick(vals);if(!v)break;if(v.less){n[key]=null;q[key]=v.raw;warnings.push(key+': Grenzwert, keine exakte Null.');}else{const scale={g:1,mg:0.001,'µg':0.000001};n[key]=v.value*scale[v.unit]/scale[unit];}break;}
 }
 if(n.energy===undefined&&Number.isFinite(n.energyKJ)){n.energy=Math.round(n.energyKJ/4.184*10)/10;warnings.push('kcal aus kJ umgerechnet.');}
 if(/vitamin[ea]?\s*[ae]\b|folat|folic|fols[aä]ure/i.test(text))warnings.push('Vitamin A/E und Folat wegen möglicher Äquivalenz-Unterschiede nicht automatisch übernommen. Bei Bedarf fachlich passende Werte manuell ergänzen.');
 warnings.push('Zahlen, Dezimalstellen, Bezugsmenge und richtige Tabellenspalte kontrollieren. Nicht gedruckte Werte bleiben unbekannt.');
 return {n,q,basis,warnings};
}
function fromOFF(product,basis='g'){
 const n={},p=product.nutriments||{},map={energy:'energy-kcal',protein:'proteins',carbs:'carbohydrates',fat:'fat',saturated:'saturated-fat',sugar:'sugars',fiber:'fiber',salt:'salt'};
 for(const [key,off] of Object.entries(map)){const v=p[off+'_100g'];n[key]=typeof v==='number'&&Number.isFinite(v)&&v>=0?v:null;}
 if(n.energy===null&&Number.isFinite(p.energy_100g)){n.energy=p.energy_100g/4.184;}
 // OFF standard mass units: nutriment _100g values are grams, vitamins/minerals included.
 for(const [key,off,mul] of [['vitC','vitamin-c',1000],['vitD','vitamin-d',1e6],['vitB1','vitamin-b1',1000],['vitB2','vitamin-b2',1000],['vitB6','vitamin-b6',1000],['vitB12','vitamin-b12',1e6],['calcium','calcium',1000],['magnesium','magnesium',1000],['potassium','potassium',1000],['sodium','sodium',1000],['iron','iron',1000],['zinc','zinc',1000],['iodine','iodine',1e6],['selenium','selenium',1e6]]){const v=p[off+'_100g'];n[key]=typeof v==='number'&&Number.isFinite(v)&&v>=0?v*mul:null;}
 return {id:'off-'+String(product.code||Date.now()).replace(/\D/g,''),name:((product.product_name_de||product.product_name||'Produkt')+' '+(product.brands||'')).trim().slice(0,240),basis,n,q:{},density:null,kind:'custom',source:'Open Food Facts · von mir geprüft',sourceUrl:'https://world.openfoodfacts.org/product/'+product.code};
}
const publicAPI={parse,fromOFF};if(typeof module==='object'&&module.exports){module.exports=publicAPI;return;}root.NK_SCANNER=publicAPI;
const $=s=>document.querySelector(s),E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let openOptions={},scanProfile='',ocrCache={};
let imageURL=null,image=null,worker=null,controls=null,scanBusy=false,rawText='',barcodeProduct=null,scanGeneration=0;
const dlg=$('#scan-dialog');
function load(src,global){if(root[global])return Promise.resolve();return new Promise((resolve,reject)=>{const s=document.createElement('script');s.src=src;s.onload=resolve;s.onerror=()=>reject(Error('Scanner-Dateien konnten nicht geladen werden. Bitte mit Internet erneut versuchen oder Werte manuell eingeben.'));document.head.append(s);});}
function stop(){scanGeneration++;root.NK_PHOTO_PRODUCT?.reset();ocrCache={};controls?.stop();controls=null;if(imageURL)URL.revokeObjectURL(imageURL);imageURL=null;image=null;worker?.terminate().catch(()=>{});worker=null;scanBusy=false;}
function message(t){const el=$('#scan-status');if(el)el.textContent=t;}
function open(opts={}){stop();openOptions=opts;scanProfile=root.NK_HOUSEHOLD?.id||'';rawText='';barcodeProduct=null;dlg.innerHTML=`<div class="modal-head"><h2>Produkt scannen</h2><button type="button" class="icon-btn" id="scan-close" aria-label="Schliessen">×</button></div><p class="small">Ein Foto, zwei Möglichkeiten: Produktbeschriftung erkennen und passende Nährwerte online suchen – oder die Nährwerttabelle direkt auslesen. Fotos bleiben auf deinem Gerät. Bei der Produktsuche wird nur der erkannte Suchbegriff / Barcode gesendet.</p><div class="scan-options"><label class="button" for="nutrition-photo">Packung fotografieren<input id="nutrition-photo" type="file" accept="image/*" capture="environment" hidden></label><label class="button secondary" for="gallery-photo">Foto aus Galerie<input id="gallery-photo" type="file" accept="image/*" hidden></label><button type="button" class="button secondary" id="barcode-camera">Barcode-Kamera</button></div><div class="form-grid spaced"><div class="field"><label for="barcode-input">Barcode eintippen</label><input id="barcode-input" inputmode="numeric" placeholder="8–14 Ziffern" maxlength="14"></div><button type="button" class="button secondary align-end" id="barcode-find">Produkt suchen</button></div><video id="barcode-video" muted playsinline hidden></video><div class="scan-image" hidden><img id="scan-photo-preview" alt="Dein Foto der Produktpackung oder Nährwerttabelle"><p class="tiny">Vorderseite mit Marke und Sorte für die Produktsuche; Nährwerttabelle für direktes Auslesen. Möglichst gerade, scharf und ohne Spiegelungen aufnehmen. Du kannst mit demselben Foto zwischen beiden Wegen wechseln.</p><div class="scan-photo-actions"><button class="button" id="recognize-product" type="button">Produkt erkennen &amp; suchen<small>Marke / Barcode lesen · passende Produktdaten online finden</small></button><button class="button secondary" id="recognize-photo" type="button">Nährwerttabelle auslesen<small>Zahlen direkt übernehmen · Bezugsmenge korrigieren</small></button></div></div><p id="scan-status" class="small" role="status"></p><div id="scan-review"></div><details class="spaced" id="scan-text-section"><summary>Text statt Foto einfügen</summary><p class="small">Eine kopierte Nährwerttabelle einfügen; jeder Nährstoff möglichst in einer eigenen Zeile.</p><textarea id="nutrition-text" rows="6" placeholder="pro 100 g&#10;Energie 230 kcal&#10;Fett 8 g&#10;Eiweiss 12 g"></textarea><button class="button secondary" type="button" id="parse-text">Text auswerten</button></details>`;dlg.showModal();
 $('#scan-close').onclick=()=>{stop();dlg.close();};dlg.oncancel=stop;$('#nutrition-photo').onchange=photo;$('#gallery-photo').onchange=photo;$('#recognize-photo').onclick=recognize;$('#recognize-product').onclick=identifyProduct;$('#parse-text').onclick=()=>{root.NK_PHOTO_PRODUCT?.pause();$('#scan-review').hidden=false;rawText=$('#nutrition-text').value.slice(0,30000);barcodeProduct=null;review();};$('#barcode-find').onclick=()=>lookup($('#barcode-input').value);$('#barcode-camera').onclick=camera;if(opts.textOnly){$('#scan-text-section').open=true;$('#nutrition-text').focus();$('#scan-dialog h2').textContent='Nährwerttext auslesen';}
}
function scanCurrent(generation){return generation===scanGeneration&&dlg.open&&scanProfile===(root.NK_HOUSEHOLD?.id||'');}
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
 try{await root.NK_PHOTO_PRODUCT.identify({image,load,readText:readPhotoText,current:()=>scanCurrent(generation),transfer:photoTransfer});if(scanCurrent(generation))message('');}
 catch(e){if(scanCurrent(generation))message('Produktsuche nicht möglich: '+e.message);}
}
function review(){
 const P=root.NK_PORTIONS,all=window.NK_DATA.nutrients,guesses=barcodeProduct?[{amount:100,unit:'g'}]:P.hints(rawText);
 let selected=barcodeProduct?{...fromOFF(barcodeProduct),warnings:[]}:parse(rawText),previewResult=null;
 const suggested=guesses[0],basis=suggested?.unit||selected.basis||'g';
 $('#scan-review').innerHTML=`<div class="notice"><b>Ausgangswerte und Bezugsmenge prüfen</b><p>${barcodeProduct?'Community-Daten aus Open Food Facts. Die gelieferten Werte gelten bereits pro 100 g/ml. Nicht die Packungsgrösse eintragen.':'Die Erkennung kann auch eine 30-g-Portionsspalte lesen. Trage die Menge ein, für die die angezeigten Ausgangswerte gelten.'}</p></div><div class="form-grid"><div class="field full"><label for="scan-name">Produktname / Marke</label><input id="scan-name" maxlength="240" value="${E(barcodeProduct?selected.name:openOptions.name||'')}" placeholder="Zum Beispiel meine Proteinmilch"></div>${!barcodeProduct?'<div class="field full"><label for="scan-column">Ausgelesene Wertespalte</label><select id="scan-column"><option value="first">Erste Wertespalte</option><option value="last">Letzte Wertespalte</option></select><small>Keine Prozent-/Referenzwertspalte wählen. Alle Ausgangswerte müssen zur selben Menge gehören.</small></div>':''}<div class="field"><label for="scan-amount">Diese Werte gelten für …</label><input id="scan-amount" inputmode="decimal" value="${suggested?E(suggested.amount):''}" placeholder="z. B. 30" aria-describedby="scan-portion-help" maxlength="20"></div><div class="field"><label for="scan-basis">Einheit der Bezugsmenge</label><select id="scan-basis"><option value="g" ${basis==='g'?'selected':''}>g</option><option value="ml" ${basis==='ml'?'selected':''}>ml</option></select></div></div><p class="small" id="scan-portion-help">Gemeint ist die Tabellenspalte, nicht deine gegessene Menge. Aus 30 g werden rechnerisch 100 g; aus 250 ml werden 100 ml. Gramm und Milliliter werden nicht ineinander umgerechnet.</p><p class="small" id="scan-suggestion">${guesses.length?'Erkannte Mengen als Vorschlag: '+guesses.map(h=>E(h.amount)+' '+h.unit).join(' / ')+'. Bitte mit der gewählten Spalte vergleichen.':'Keine eindeutige Bezugsmenge erkannt. Bitte selbst eintragen.'}</p><div id="scan-conversion-status" class="small" role="status" aria-live="polite"></div><div id="detected-values"></div><label class="check"><input id="scan-confirm" type="checkbox"> Ich habe die Ausgangswerte, ihre Bezugsmenge und die Einheiten geprüft. Alle Werte gehören zu dieser Spalte.</label><button class="button wide" type="button" id="scan-transfer">Auf 100 g/ml umrechnen und weiter</button><p class="tiny spaced">Noch keine Speicherung. Im nächsten Schritt sind die Werte pro 100 g/ml weiter bearbeitbar. Erst «Produkt speichern» übernimmt sie in euren Haushalt.</p>`;
 const format=x=>new Intl.NumberFormat('de-CH',{maximumFractionDigits:4}).format(x);
 function table(){
  const keys=all.filter(f=>selected.n[f.key]!=null||selected.q?.[f.key]);
  $('#detected-values').innerHTML=`<div class="scan-values-table"><div class="scan-values-head"><span>Nährstoff</span><span>Ausgangswert</span><span id="scan-output-heading">Pro 100 ${E($('#scan-basis').value)}</span></div>${keys.map(f=>`<div class="scan-value-row"><label for="scan-raw-${E(f.key)}">${E(f.label)}<small>${E(f.unit)}</small></label><div><input id="scan-raw-${E(f.key)}" data-scan-nutrient="${E(f.key)}" inputmode="decimal" aria-label="${E(f.label)} – Ausgangswert in ${E(f.unit)}" value="${selected.n[f.key]==null?'':E(selected.n[f.key])}" placeholder="unbekannt">${selected.q?.[f.key]?'<small>'+E(selected.q[f.key])+'</small>':''}</div><output id="scan-out-${E(f.key)}">—</output></div>`).join('')}</div><p class="tiny">Ausgangswerte hier korrigieren. Leere Felder bleiben unbekannt; eine echte 0 bleibt 0. Weitere Nährstoffe lassen sich im nächsten Schritt ergänzen.</p>${(selected.warnings||[]).filter(w=>!w.includes('Vor dem Speichern auf 100')).map(w=>'<p class="tiny">'+E(w)+'</p>').join('')}`;
 }
 function refresh(){
  previewResult=null;$('#scan-confirm').checked=false;$('#scan-transfer').disabled=true;
  $('#scan-output-heading').textContent='Pro 100 '+$('#scan-basis').value;
  try{
   const n={};all.forEach(f=>{const el=$('#scan-raw-'+f.key);n[f.key]=el?el.value:null;});
   previewResult=P.convert(n,selected.q||{},$('#scan-amount').value,$('#scan-basis').value);
   all.forEach(f=>{const out=$('#scan-out-'+f.key);if(out)out.textContent=previewResult.n[f.key]===null?'Unbekannt':format(previewResult.n[f.key])+' '+f.unit;});
   $('#scan-conversion-status').textContent='Umrechnung: Ausgangswert × 100 ÷ '+format(previewResult.sourceAmount)+' → pro 100 '+previewResult.basis+'.';
   $('#scan-transfer').disabled=!all.some(f=>previewResult.n[f.key]!==null);
  }catch(e){$('#scan-conversion-status').textContent=e.message;$('#detected-values').querySelectorAll('output').forEach(el=>el.textContent='—');}
 }
 table();refresh();
 $('#scan-amount').oninput=refresh;$('#scan-basis').onchange=refresh;
 $('#detected-values').oninput=e=>{if(e.target.dataset.scanNutrient)refresh();};
 if($('#scan-column'))$('#scan-column').onchange=()=>{
  selected=parse(rawText,$('#scan-column').value);
  const guess=$('#scan-column').value==='last'?guesses.at(-1):guesses[0];
  // Changing the column cannot carry a stale portion size unnoticed.
  $('#scan-amount').value=guesses.length>1&&guess?guess.amount:guesses.length===1&&$('#scan-column').value==='first'?guesses[0].amount:'';
  if(guess)$('#scan-basis').value=guess.unit;
  table();refresh();
 };
 $('#scan-transfer').onclick=()=>{
  if(!previewResult){message('Bitte eine gültige Bezugsmenge und Ausgangswerte eingeben.');return;}
  if(!$('#scan-confirm').checked){message('Bitte Ausgangswerte, Bezugsmenge und Einheiten bestätigen.');return;}
  const name=$('#scan-name').value.trim();if(!name){message('Bitte Produktname oder Marke ergänzen.');return;}
  const f=barcodeProduct?fromOFF(barcodeProduct,previewResult.basis):{id:'custom-'+(crypto.randomUUID?crypto.randomUUID():Array.from(crypto.getRandomValues(new Uint8Array(16)),v=>v.toString(16).padStart(2,'0')).join('')),density:null,kind:'custom',source:'Packungsfoto / Text · von mir geprüft'};
  f.name=name;f.n={...previewResult.n};f.q={...previewResult.q};f.basis=previewResult.basis;
  f.source+=' · Ausgangswerte pro '+previewResult.sourceAmount+' '+f.basis+'; auf 100 '+f.basis+' umgerechnet';
  // Validation precedes navigation so a failed conversion never destroys the original input.
  try{window.NK.validateFood(f,all.map(x=>x.key));}catch(e){message(e.message);return;}
  const done=openOptions.onTransfer;if(done){try{done(f);}catch(e){message(e.message);return;}stop();dlg.close();openOptions={};}else{stop();dlg.close();window.NK_APP.reviewFood(f);}
 };
}

async function lookup(code){const generation=scanGeneration;root.NK_PHOTO_PRODUCT?.pause();code=String(code).replace(/\s/g,'');try{if(!/^\d{8,14}$/.test(code))throw Error('Bitte einen Barcode mit 8–14 Ziffern eingeben.');message('Produkt wird gesucht …');const r=await window.NK_HOUSEHOLD.api('barcode',{code});if(!scanCurrent(generation))return;$('#scan-review').hidden=false;barcodeProduct={...r.product,code:r.product.code||code};review();message('Produkt gefunden. Werte und Bezugsmenge mit der Packung vergleichen.');}catch(e){message(e.message);}}
async function camera(){const generation=scanGeneration;try{await load('vendor/zxing-browser.min.js','ZXingBrowser');if(generation!==scanGeneration)return;const video=$('#barcode-video');video.hidden=false;message('Barcode in die Kamera halten. Bei verweigertem Zugriff den Code eintippen.');const reader=new ZXingBrowser.BrowserMultiFormatReader();controls=await reader.decodeFromVideoDevice(undefined,video,(result,error,c)=>{if(generation!==scanGeneration){c.stop();return;}if(result){c.stop();controls=null;video.hidden=true;$('#barcode-input').value=result.getText();lookup(result.getText());}});if(generation!==scanGeneration){controls?.stop();controls=null;}}catch(e){message('Kamera nicht verfügbar: '+e.message+' Barcode bitte eintippen.');}}
root.NK_SCANNER.open=open;
document.addEventListener('nk-profile-loaded',()=>{if(dlg.open&&scanProfile!==(root.NK_HOUSEHOLD?.id||'')){stop();dlg.close();}});
dlg.addEventListener('close',stop);
document.addEventListener('click',e=>{if(e.target.closest('[data-nk-scan]')){e.preventDefault();open();}});
})(typeof window!=='undefined'?window:globalThis);
