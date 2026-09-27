from pathlib import Path
p=Path('kompass')
import hashlib
expected={'core.js':'9459fcde9d888b2d772d331a44323be945a80ed4354127af6b6fcf1fc4c7639d','app.js':'d5151609ebff7d42ca52d52bc0c62b02978741d9201467757ce94f106a06ed84','scanner.js':'e4bcb18dfdee90323c8d9bb5b7c8b0cc009541c8abc61ab0a983171eca326197','index.html':'23e0072d50b9fbcd68d6af77b572e8f25da3763b5974403664642c687f47967e','device.js':'5566093e86fcd066e8fc83fada413c640e314ac25ad8205c19443629a6ae58db','household.js':'6ba79e7f152af25db452c93150708c3b69e2d8bec69affe03b6ea819eea5d129','sw.js':'66629086affc3726bb7de2d40a3261127def438ba166da05dd264de17a6dee76','version.json':'c1240f7d9b3c0a50f3a9afd8011bb92bbbf3e0eaefbaa40e64e7ad475bbef488'}
if '1.8.0' in (p/'version.json').read_text():
 print('Already applied');raise SystemExit(0)
for name,h in expected.items():
 assert hashlib.sha256((p/name).read_bytes()).hexdigest()==h,'Base changed: '+name

def rep(s,a,b):
 assert s.count(a)==1,(a[:150],s.count(a));return s.replace(a,b)
s=(p/'core.js').read_text()
s=rep(s," const VERSION="," const PIECES=typeof module==='object'&&module.exports?require('./product-portions.js'):globalThis.NK_PIECES;\n const VERSION=")
s=rep(s,"  let q=positive(quantity),dimension;","  if(unit==='piece')return PIECES.factor(food,quantity);\n  let q=positive(quantity),dimension;")
s=rep(s,"  if(f.density!==null","  PIECES.validate(f);\n  if(f.density!==null")
(p/'core.js').write_text(s)
s=(p/'app.js').read_text()
s=rep(s,"const sourceFood=f=>","const P=window.NK_PIECES;\nconst sourceFood=f=>")
s=rep(s,"q:copy(f.q||{}),...(f.shared?","q:copy(f.q||{}),sourceUrl:f.sourceUrl||null,portion:f.portion?copy(f.portion):null,...(f.shared?")
s=rep(s,"const terms=clean(q).trim().split(/\\s+/).filter(Boolean);if(terms.length)all=all.filter(f=>{const text=clean(f.name+' '+f.synonyms);return terms.every(t=>text.includes(t)||t.endsWith('n')&&text.includes(t.slice(0,-1)));});","const terms=clean(q).trim().split(/\\s+/).filter(Boolean);if(terms.length)return window.NK_FOOD_SEARCH.select(all,q);")
s=s.replace("'Hühnerei, ganz, hartgekocht'","'Hühnerei, ganz, festgekocht'")
s=rep(s," · pro 100 ${f.basis}</small>"," · pro 100 ${f.basis}${f.portion?' · '+esc(P.label(f)):''}</small>")
s=rep(s,"dirty=false;route='editor';render();","draft.ingredients=draft.ingredients.map(P.hydrate);dirty=false;route='editor';render();")
s=rep(s,"existing?.quantity??100","existing?.quantity??(modal.food.portion?1:100)")
s=rep(s,"options([['g','g'],['kg','kg'],['ml','ml'],['dl','dl'],['l','l']],i.unit)","options(P.units(i.food),i.unit)")
s=rep(s,"${esc(i.food.source)} · ${i.food.density","${i.food.portion?esc(P.label(i.food))+' · ':''}${esc(i.food.source)} · ${i.food.density")
s=rep(s,"C.recipeTotal(r,KEYS);if(asVariant)","r.ingredients=r.ingredients.map(P.canonical);C.recipeTotal(r,KEYS);if(asVariant)")
s=rep(s,"options([['g','g'],['kg','kg'],['ml','ml'],['dl','dl'],['l','l']],existing?.unit??modal.food.basis)","options(P.units(modal.food),existing?.unit??(modal.food.portion?'piece':modal.food.basis))")
s=rep(s,'</select></div></div><details class="details-section" ${existing?.density?','</select></div></div><div class="piece-banner">${modal.food.portion?"<b>"+esc(P.label(modal.food))+"</b>":"Noch keine Stückportion hinterlegt."} ${btn(modal.food.portion?"Stückportion anpassen":"Stückportion hinterlegen","configure-portion","secondary")}<small>Nur essbarer Anteil, bei Eiern ohne Schale. Keine pauschalen Stückgewichte.</small></div><details class="details-section" ${existing?.density?')
s=rep(s,'<div class="preview-macros">${','<p class="piece-amount">${esc(P.describe(f,$(\'#food-qty\').value,$(\'#food-unit\').value))}</p><div class="preview-macros">${')
s=rep(s,"category:'Eigene Produkte'};C.validateFood","category:'Eigene Produkte',portion:readCustomPortion()};C.validateFood")
s=rep(s,"amountText:fmt(quantity)+' '+unit,n,","...P.entryAmount(m.food,quantity,unit),n,")
s=s.replace("amountText:f===1?ent.amountText:fmt(f)+' × ('+ent.amountText+')'","...P.scaledEntry(ent,f)")
s=rep(s,"if(m.returnIngredient)foodDialog(f,'ingredient');","if(m.returnIngredient)foodDialog(f,'ingredient',m.returnIndex??null);")
s=rep(s,'<form id="custom-food-form"><div class="form-grid">','<form id="custom-food-form"><div class="text-import-launch"><b>Nährwerte nicht abtippen</b><p class="small">Kopierte Nährwerttabelle auslesen, Bezugsmenge prüfen und übernehmen. Name und Stückportion bleiben erhalten; die Tabelle ersetzt die Nährwertfelder erst nach deiner Bestätigung.</p>${btn("Nährwerttext auslesen","custom-text","secondary")}</div><div class="form-grid">')
s=rep(s,'${numField(\'custom-density\',\'Dichte · g/ml (optional)\',f?.density)}</div><div class="notice">','${numField(\'custom-density\',\'Dichte · g/ml (optional)\',f?.density)}</div>${customPortionFields(f)}<div class="notice">')
s=rep(s,' Produkt speichern</button></div></form>`);}',' Produkt speichern</button></div></form>`);updateCustomPortionPreview();}')
s=rep(s,"if(a==='nav')nav(b.dataset.route);","if(a==='custom-text')openCustomText();\n else if(a==='configure-portion'){const old=modal;let f=copy(old.food);if(byId.has(f.id))f={...f,id:'custom-'+uid(),kind:'custom'};customFoodDialog(f,old.mode!=='log');modal.returnIndex=old.replaceIndex??null;$('#custom-piece-size').focus();}\n else if(a==='nav')nav(b.dataset.route);")
s=rep(s,"\n if(el.closest('#profile-form')){updateGoalPreview();}","\n if(el.closest('#custom-food-form')){updateCustomPortionPreview();}\n else if(el.closest('#profile-form')){updateGoalPreview();}")
s=rep(s,"else if(el.closest('#profile-form')){updateGoalPreview();}\n else if(el.id==='diary-date')","else if(el.closest('#custom-food-form')){updateCustomPortionPreview();}\n else if(el.closest('#profile-form')){updateGoalPreview();}\n else if(el.id==='diary-date')")
insert=r'''
function customPortionFields(f){return `<section class="piece-fields"><h3>Stückportion · optional</h3><p class="small">Einmal festlegen, dann Stückzahlen statt Gramm eintippen. Zum Beispiel Stück, Scheibe, Riegel oder Becher.</p><div class="form-grid"><div class="field"><label for="custom-piece-label">Bezeichnung für 1 Stück</label><input id="custom-piece-label" maxlength="40" value="${esc(f?.portion?.label||'Stück')}" placeholder="Stück"></div>${numField('custom-piece-size','1 Stück entspricht …',f?.portion?.size,'Wiegen oder von der Packung übernehmen.','placeholder="z. B. 50"')}<div class="field"><label for="custom-piece-unit">Einheit der Stückgrösse</label><select id="custom-piece-unit">${options([['g','g'],['ml','ml']],f?.portion?.unit||f?.basis||'g')}</select></div></div><div id="custom-piece-preview" class="small" role="status"></div><p class="tiny">Passend zur Nährwertbasis: g bei Angaben pro 100 g, ml bei Angaben pro 100 ml. Keine automatische Gleichsetzung. Ohne Verpackung / Schale wiegen. Menge leer lassen, um die Stückportion zu entfernen.</p></section>`;}
function readCustomPortion(){const size=C.number($('#custom-piece-size').value,{optional:true,min:.000001,max:100000});if(size===null)return null;const portion={label:$('#custom-piece-label').value.trim(),size,unit:$('#custom-piece-unit').value};P.validate({basis:$('#custom-basis').value,portion});return portion;}
function updateCustomPortionPreview(){const el=$('#custom-piece-preview');if(!el)return;try{const portion=readCustomPortion();if(!portion){el.textContent='Noch keine Stückgrösse – Angaben bleiben pro 100 g/ml.';return;}const f={portion,basis:$('#custom-basis').value};const details=[['energy','kcal'],['protein','g Protein'],['carbs','g Kohlenhydrate'],['fat','g Fett']].map(([k,u])=>{const n=C.number($('#custom-'+k).value,{optional:true});return n===null?null:fmt(n*portion.size/100)+' '+u;}).filter(Boolean);el.textContent=P.label(f)+(details.length?' · '+details.join(' · '):'');}catch(e){el.textContent=e.message;}}
function openCustomText(){const m=modal,form=$('#custom-food-form'),profileId=window.NK_HOUSEHOLD?.id;if(!form||m?.type!=='custom-food')return;window.NK_SCANNER.open({textOnly:true,name:$('#custom-name').value,onTransfer:f=>{if(modal!==m||!form.isConnected||profileId!==window.NK_HOUSEHOLD?.id)throw Error('Das Produktformular wurde gewechselt. Bitte erneut öffnen.');for(const n of NS)$('#custom-'+n.key).value=f.n[n.key]??'';$('#custom-name').value=f.name;$('#custom-basis').value=f.basis;m.food={...(m.food||{}),id:m.food?.id||f.id,source:f.source,sourceUrl:f.sourceUrl||null,q:copy(f.q||{})};$('#modal-error').innerHTML='<p class="small">Nährwerttext übernommen. Noch nicht gespeichert. Stückportion und Werte prüfen, dann Produkt speichern.</p>';updateCustomPortionPreview();}});}
'''
s=rep(s,'function customFoodDialog(',insert+'\nfunction customFoodDialog(')
(p/'app.js').write_text(s)
s=(p/'scanner.js').read_text()
s=rep(s,"let imageURL=null,","let openOptions={};\nlet imageURL=null,")
s=rep(s,"function open(){stop();rawText='';","function open(opts={}){stop();openOptions=opts;rawText='';")
s=rep(s,'<details class="spaced"><summary>Text statt Foto einfügen</summary>','<details class="spaced" id="scan-text-section"><summary>Text statt Foto einfügen</summary>')
s=rep(s,"$('#barcode-camera').onclick=camera;","$('#barcode-camera').onclick=camera;if(opts.textOnly){$('#scan-text-section').open=true;$('#nutrition-text').focus();$('#scan-dialog h2').textContent='Nährwerttext auslesen';}")
s=rep(s,"E(barcodeProduct?selected.name:'')","E(barcodeProduct?selected.name:openOptions.name||'')")
s=rep(s,"stop();dlg.close();window.NK_APP.reviewFood(f);","const done=openOptions.onTransfer;if(done){try{done(f);}catch(e){message(e.message);return;}stop();dlg.close();openOptions={};}else{stop();dlg.close();window.NK_APP.reviewFood(f);}")
s=s.replace("/ballaststoffe|(?:dietary","/nahrungsfasern|ballaststoffe|(?:dietary")
(p/'scanner.js').write_text(s)
for name in ['index.html','core.js','device.js','household.js','sw.js','version.json']:
 s=(p/name).read_text().replace('1.7.0','1.8.0')
 if name=='index.html':
  s=rep(s,'<script src="core.js?v=1.8.0">','<script src="product-portions.js?v=1.8.0"></script><script src="food-search.js?v=1.8.0"></script><script src="core.js?v=1.8.0">')
  s=rep(s,'<title>Nährstoff-Kompass','<link rel="stylesheet" href="product-portions.css?v=1.8.0"><title>Nährstoff-Kompass')
  s=s.replace('Visuelle Reports & PDF-Export','Stückportionen & Nährwerttext')
 if name=='sw.js':
  s=rep(s,"const scripts=[","const scripts=['product-portions.js','food-search.js',")
  s=rep(s,"const SHELL=[","const SHELL=['./product-portions.css?v='+VERSION,")
 (p/name).write_text(s)
(p/'version.json').write_text('{"version":"1.8.0","date":"2026-09-27"}\n')
