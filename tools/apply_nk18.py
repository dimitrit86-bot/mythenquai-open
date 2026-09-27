"""Reviewed public-source migration. No private profile data is read or modified."""
from pathlib import Path
import json,hashlib
P=Path('kompass')
GUARDS=json.loads(Path('tools/nk18-hashes.json').read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if all(digest(P/n)==pair[1] for n,pair in GUARDS.items()):
 print('Source migration already applied.');raise SystemExit(0)
for n,pair in GUARDS.items():assert digest(P/n)==pair[0], 'Unexpected source base: '+n

def rep(s,a,b):
 assert s.count(a)==1,(a[:120],s.count(a));return s.replace(a,b)
s=(P/'core.js').read_text()
s=rep(s,"const VERSION='1.7.0', SCHEMA=1;","const VERSION='1.8.0', SCHEMA=1;\n const PIECES=typeof module==='object'&&module.exports?require('./food-portions.js'):globalThis.NK_PIECES;")
s=rep(s,"let q=positive(quantity),dimension;","let q=positive(quantity),dimension;\n  if(unit==='piece'){const x=PIECES.toBase(food,q);q=x.quantity;unit=x.unit;}")
s=rep(s,"if(f.density!==null&&f.density!==undefined)positive(f.density);","if(f.density!==null&&f.density!==undefined)positive(f.density);\n  if(f.portion!=null)PIECES.definition(f);")
(P/'core.js').write_text(s)
s=(P/'app.js').read_text()
s=rep(s,"const D=window.NK_DATA,C=window.NK,KEY=","const D=window.NK_DATA,C=window.NK,M=window.NK_PIECES,S=window.NK_FOOD_SEARCH,KEY=")
s=rep(s,"saveChain=Promise.resolve(),reportOptions=null;","saveChain=Promise.resolve(),reportOptions=null,searchLimit=75,ingredientLimit=40;")
s=rep(s,"kind:f.kind||'custom',n:copy(f.n)","kind:f.kind||'custom',sourceUrl:f.sourceUrl||null,portion:f.portion?copy(f.portion):null,baseFoodId:f.baseFoodId||null,searchAliases:f.searchAliases||'',n:copy(f.n)")
s=rep(s,"let all=[...state.foods,...D.foods,...(window.NK_SHARED?.foods()||[])];", "const overrides=new Set(state.foods.map(f=>f.baseFoodId).filter(Boolean));let all=[...state.foods,...D.foods.filter(f=>!overrides.has(f.id)),...(window.NK_SHARED?.foods()||[])];")
a="const terms=clean(q).trim().split(/\\s+/).filter(Boolean);if(terms.length)all=all.filter(f=>{const text=clean(f.name+' '+f.synonyms);return terms.every(t=>text.includes(t)||t.endsWith('n')&&text.includes(t.slice(0,-1)));});"
s=rep(s,a,"const terms=clean(q).trim().split(/\\s+/).filter(Boolean);if(terms.length)return S.search(all,q);")
s=s.replace('Hühnerei, ganz, hartgekocht','Hühnerei, ganz, festgekocht')
s=rep(s," · pro 100 ${f.basis}</small></span>"," · pro 100 ${f.basis}</small>${pieceTag(f)}</span>")
s=rep(s,"${arr.length>75?' · die ersten 75 angezeigt':''}","${arr.length>searchLimit?' · '+searchLimit+' angezeigt':''}")
s=rep(s,"${foodRows(arr.slice(0,75))}</div>","${foodRows(arr.slice(0,searchLimit))}</div>${arr.length>searchLimit?btn('Weitere Treffer anzeigen','more-foods','secondary wide'):''}")
s=rep(s,"${arr.length} Treffer · bis zu 40 angezeigt","${arr.length} Treffer · bis zu ${ingredientLimit} angezeigt")
s=rep(s,"el.innerHTML=foodRows(arr.slice(0,40),'ingredient');","el.innerHTML=foodRows(arr.slice(0,ingredientLimit),'ingredient')+(arr.length>ingredientLimit?btn('Weitere Treffer anzeigen','more-ingredients','secondary wide'):'');")
s=rep(s,"value=\"${esc(i.quantity)}\" data-ingredient=", "value=\"${esc(M.selection(i).quantity)}\" data-ingredient=")
s=rep(s,"${options([['g','g'],['kg','kg'],['ml','ml'],['dl','dl'],['l','l']],i.unit)}", "${options(foodUnits(i.food),M.selection(i).unit)}")
s=rep(s,"<div class=\"ingredient-source\">${esc(i.food.source)}", "${pieceTag(i.food)}<div class=\"ingredient-source\">${esc(i.food.source)}")
s=rep(s,"async function saveRecipe(asVariant=false){readDraft();", "async function saveRecipe(asVariant=false){readDraft();readIngredientInputs();")
s=rep(s,"const existing=mode==='ingredient-edit'?draft.ingredients[replaceIndex]:null;", "const existing=mode==='ingredient-edit'?draft.ingredients[replaceIndex]:null,selection=existing?M.selection(existing):null;")
s=rep(s,"${numField('food-qty','Menge',existing?.quantity??100)}", "${pieceTag(modal.food)}${numField('food-qty','Menge',selection?.quantity??(modal.food.portion?1:100))}")
s=rep(s,"${options([['g','g'],['kg','kg'],['ml','ml'],['dl','dl'],['l','l']],existing?.unit??modal.food.basis)}", "${options(foodUnits(modal.food),selection?.unit??(modal.food.portion?'piece':modal.food.basis))}")
s=rep(s,"</select></div></div><details class=\"details-section\" ${existing?.density?", "</select></div></div>${btn(modal.food.portion?'Stückportion bearbeiten':'Stückportion festlegen','define-piece','secondary wide')}<details class=\"details-section\" ${existing?.density?")
s=rep(s,"<p>* Bekannte Teilmenge bei fehlenden genauen Nährstoffangaben.</p>","<p>${esc(M.text(f,$('#food-qty').value,$('#food-unit').value,fmt))}</p><p>* Bekannte Teilmenge bei fehlenden genauen Nährstoffangaben.</p>")
s=rep(s,"name:m.food.name,kind:'food',amountText:fmt(quantity)+' '+unit,n,", "name:m.food.name,kind:'food',amountText:M.text(m.food,quantity,unit,fmt),n,")
s=rep(s,"const item={food:m.food,quantity,unit,density};", "const item=M.ingredient(m.food,quantity,unit,density);")
s=rep(s,"synonyms:'',category:'Eigene Produkte'};", "synonyms:m.food?.synonyms||'',searchAliases:m.food?.searchAliases||'',baseFoodId:m.food?.baseFoodId||null,portion:readCustomPortion(),category:'Eigene Produkte'};")
s=rep(s,"closeDialog();if(m.returnIngredient)foodDialog(f,'ingredient');else{", "closeDialog();if(m.returnToFood)foodDialog(f,m.returnToFood.mode,m.returnToFood.replaceIndex);else if(m.returnIngredient)foodDialog(f,'ingredient');else{")
s=rep(s,"<form id=\"custom-food-form\"><div class=\"form-grid\">", "<form id=\"custom-food-form\"><div class=\"custom-import-actions\"><div class=\"actions\">${btn('Text einfügen & auslesen','custom-read-text','secondary')}${btn('Packungsfoto auslesen','custom-read-photo','secondary')}</div><p>Vorhandene Angaben bleiben beim Öffnen erhalten. Die erkannten Werte erst nach Prüfung ins Formular übernehmen; gespeichert wird weiterhin nur mit «Produkt speichern».</p></div><div class=\"form-grid\">")
s=rep(s,"f?.density)}</div><div class=\"notice\">", "f?.density)}</div>${pieceFields(f)}<div class=\"notice\">")
s=rep(s," Produkt speichern</button></div></form>`);}", " Produkt speichern</button></div></form>`);updatePiecePreview();}")
s=rep(s,"if(a==='nav')nav(b.dataset.route);", "if(a==='custom-read-text'||a==='custom-read-photo'){readIntoCustom(a==='custom-read-text'?'text':'photo');}\n else if(a==='define-piece'){definePiece();}\n else if(a==='more-foods'){searchLimit+=75;renderSearchResults();}\n else if(a==='more-ingredients'){ingredientLimit+=40;renderIngredientResults();}\n else if(a==='nav')nav(b.dataset.route);")
s=rep(s,"\n if(el.closest('#profile-form')){updateGoalPreview();}", "if(el.closest('#custom-food-form')){updatePiecePreview();}\n else if(el.closest('#profile-form')){updateGoalPreview();}")
s=rep(s,"search=el.value;renderSearchResults();", "search=el.value;searchLimit=75;renderSearchResults();")
s=rep(s,"else if(el.id==='ingredient-search')renderIngredientResults();", "else if(el.id==='ingredient-search'){ingredientLimit=40;renderIngredientResults();}")
a="else if(el.dataset.ingredient!==undefined){draft.ingredients[Number(el.dataset.ingredient)][el.dataset.field]=el.value;dirty=true;updateRecipeSummary();}"
b="else if(el.dataset.ingredient!==undefined){const i=draft.ingredients[Number(el.dataset.ingredient)];M.edit(i,el.dataset.field,el.value);dirty=true;if(el.dataset.field==='unit'){const q=$('#ingredients input[data-ingredient=\"'+el.dataset.ingredient+'\"]');if(q)q.value=M.selection(i).quantity;}updateRecipeSummary();}"
assert s.count(a)==2;s=s.replace(a,b)
s=s.replace("else if(el.dataset.ingredient!==undefined){const i=", "else if(el.dataset.ingredient!==undefined&&el.dataset.field==='quantity'){const i=",1)
s=rep(s,"else if(el.closest('#profile-form')){updateGoalPreview();}\n else if(el.id==='diary-date')", "else if(el.id==='custom-basis'){const input=$('#custom-piece-amount');if(input.value&&modal.pieceBasis!==el.value){input.value='';notify('Bezugsmenge geändert: bitte die Stückmenge in der neuen Einheit erneut eingeben.');}modal.pieceBasis=el.value;updatePiecePreview();}\n else if(el.closest('#profile-form')){updateGoalPreview();}\n else if(el.id==='diary-date')")
addition=r'''
function foodUnits(f){return [...(f.portion?[['piece','Stück · '+M.definition(f).label]]:[]),['g','g'],['kg','kg'],['ml','ml'],['dl','dl'],['l','l']];}
function pieceTag(f){const p=M.definition(f);if(!p)return '';return `<small class="piece-tag">1 Stück${p.label==='Stück'?'':' · '+esc(p.label)} = ${fmt(p.amount)} ${p.unit} · ${f.n.energy==null?'kcal unbekannt':fmt(f.n.energy*p.amount/100,0)+' kcal'} · ${f.n.protein==null?'Protein unbekannt':fmt(f.n.protein*p.amount/100)+' g Protein'}</small>`;}
function pieceFields(f){const p=M.definition(f),basis=f?.basis||'g';modal.pieceBasis=basis;return `<section class="product-portions"><h3>Stückportion · optional</h3><p class="small">Einmal definieren, danach zum Beispiel 0,5 oder 2 Stück erfassen. Nährwerte bleiben pro 100 g/ml gespeichert.</p><div class="form-grid"><div class="field"><label for="custom-piece-label">Bezeichnung für 1 Stück</label><input id="custom-piece-label" maxlength="40" value="${esc(p?.label||'')}" placeholder="Stück, Ei, Scheibe, Riegel, Becher …"></div>${numField('custom-piece-amount','Menge pro Stück · <span id="custom-piece-unit">'+basis+'</span>',p?.amount,'Essbarer Anteil: ohne Schale, Kern, Gefäss oder Verpackung. Keine Schätzung aus dem Produktnamen.','placeholder="z. B. 50"')}</div><p id="custom-piece-summary" class="piece-preview" role="status"></p></section>`;}
function readCustomPortion(){const amount=$('#custom-piece-amount').value.trim(),label=$('#custom-piece-label').value.trim(),basis=$('#custom-basis').value;if(!amount){if(label)throw Error('Bitte die Menge pro Stück ergänzen oder beide Stückfelder leeren.');return null;}const portion={label:label||'Stück',amount:C.number(amount,{min:.000001,max:100000}),unit:basis};M.definition({basis,portion});return portion;}
function updatePiecePreview(){const out=$('#custom-piece-summary');if(!out)return;$('#custom-piece-unit').textContent=$('#custom-basis').value||'g/ml';try{const portion=readCustomPortion();if(!portion){out.textContent='Ohne Stückdefinition werden g bzw. ml verwendet.';return;}const protein=C.number($('#custom-protein').value,{optional:true}),energy=C.number($('#custom-energy').value,{optional:true});out.textContent='1 Stück · '+portion.label+' = '+fmt(portion.amount)+' '+portion.unit+' · '+(energy===null?'kcal unbekannt':fmt(energy*portion.amount/100,0)+' kcal')+' · '+(protein===null?'Protein unbekannt':fmt(protein*portion.amount/100)+' g Protein');}catch(e){out.textContent=e.message;}}
function definePiece(){if(modal?.type!=='food')return;const previous=modal;let f=copy(previous.food);if(byId.has(f.id)){f.baseFoodId=f.id;f.id='custom-'+uid();}customFoodDialog(f);modal.returnToFood={mode:previous.mode,replaceIndex:previous.replaceIndex};$('#custom-piece-label').focus();}
function readIngredientInputs(){document.querySelectorAll('#ingredients input[data-field="quantity"]').forEach(el=>{const i=draft.ingredients[Number(el.dataset.ingredient)];M.edit(i,'quantity',el.value);});}
function readIntoCustom(mode){if(modal?.type!=='custom-food')return;const original=modal,form=$('#custom-food-form');window.NK_SCANNER.open({mode,name:$('#custom-name').value,onImport:f=>{
 if(modal!==original||!form.isConnected||!$('#dialog').open)return;
 const keys=f.importFields||Object.keys(f.n).filter(k=>f.n[k]!=null),different=$('#custom-basis').value!==f.basis;
 const any=NS.some(n=>$('#custom-'+n.key).value.trim());
 if(any&&!confirm(different?'Die Bezugsmenge ändert sich. Bisherige Nährwerte und Stückmenge werden geleert; nur die geprüften Textwerte werden übernommen. Fortfahren?':'Die erkannten Nährstofffelder im Formular ersetzen? Nicht erkannte Angaben und die Stückportion bleiben erhalten.'))return;
 if(different){NS.forEach(n=>$('#custom-'+n.key).value='');$('#custom-piece-amount').value='';$('#custom-piece-label').value='';}
 $('#custom-basis').value=f.basis;modal.pieceBasis=f.basis;if(f.name.trim())$('#custom-name').value=f.name;
 const old=modal.food||{q:{}};old.q=different?{}:{...(old.q||{})};for(const k of keys){const el=$('#custom-'+k);if(el){el.value=f.n[k]??'';delete old.q[k];if(f.q?.[k])old.q[k]=f.q[k];}}
 old.source=(old.source?old.source+' · ':'')+f.source;modal.food=old;updatePiecePreview();notify('Geprüfte Werte übernommen. Noch nicht gespeichert.');
 }});}
'''
s=rep(s,"function customFoodDialog(existing=null,returnIngredient=false)",addition+"\nfunction customFoodDialog(existing=null,returnIngredient=false)")
(P/'app.js').write_text(s)
s=(P/'scanner.js').read_text()
s=rep(s,"let imageURL=null", "let launchOptions={};\nlet imageURL=null")
s=rep(s,"function open(){stop();", "function open(opts={}){stop();launchOptions=opts;")
s=rep(s,'<details class="spaced"><summary>Text statt Foto einfügen</summary>', '<details class="spaced" id="scan-text-details"><summary>Text statt Foto einfügen</summary>')
s=rep(s,"$('#barcode-camera').onclick=camera;", "$('#barcode-camera').onclick=camera;if(opts.mode==='text'){$('#scan-text-details').open=true;$('#nutrition-text').focus();}$('#scan-close').textContent=opts.onImport?'Zurück':'×';")
s=rep(s,"barcodeProduct?selected.name:''", "barcodeProduct?selected.name:(launchOptions.name||'')")
s=rep(s,"stop();dlg.close();window.NK_APP.reviewFood(f);", "f.importFields=[...document.querySelectorAll('#detected-values [data-scan-nutrient]')].map(el=>el.dataset.scanNutrient);const callback=launchOptions.onImport;stop();dlg.close();if(callback)callback(f);else window.NK_APP.reviewFood(f);")
(P/'scanner.js').write_text(s)
s=(P/'product-finder.js').read_text()
a="function local(q){const words=clean(q).split(/\\s+/).filter(Boolean);return all().filter(f=>words.every(w=>clean(f.name+' '+f.synonyms+' '+(f.catalog?.code||'')+' '+f.id).includes(w)));}"
s=rep(s,a,"function local(q){return root.NK_FOOD_SEARCH.search(all(),q);}")
(P/'product-finder.js').write_text(s)
for name in ['index.html','sw.js','device.js','version.json']:
 s=(P/name).read_text().replace('1.7.0','1.8.0')
 if name=='index.html':
  s=s.replace('Visuelle Reports & PDF-Export','Stückportionen · Textimport · Ei-Suche')
  s=s.replace('<title>Nährstoff-Kompass</title>','<link rel="stylesheet" href="food-portions.css?v=1.8.0"><title>Nährstoff-Kompass</title>')
  s=s.replace('<script src="core.js?v=1.8.0">','<script src="food-portions.js?v=1.8.0"></script><script src="food-search.js?v=1.8.0"></script><script src="core.js?v=1.8.0">')
 if name=='sw.js':
  s=s.replace("'core.js'","'food-portions.js','food-search.js','core.js'")
  s=s.replace("'./reports.css?v='+VERSION", "'./food-portions.css?v='+VERSION,'./reports.css?v='+VERSION")
 (P/name).write_text(s)
s=(P/'household.js').read_text().replace('app.js?v=1.7.0','app.js?v=1.8.0')
(P/'household.js').write_text(s)
s=(P/'app.js').read_text()
s=s.replace("modal.returnToFood={mode:previous.mode,replaceIndex:previous.replaceIndex};","modal.returnToFood={mode:previous.mode==='log'?'log':'ingredient',replaceIndex:previous.replaceIndex};")
s=s.replace('<div class="amount-grid">${pieceTag(modal.food)}','${pieceTag(modal.food)}<div class="amount-grid">')
s=s.replace('</form>`);updateFoodPreview();}',"</form>`);modal.previousUnit=$('#food-unit').value;updateFoodPreview();}")
s=s.replace("else if(el.id==='food-unit')updateFoodPreview();","else if(el.id==='food-unit'){const old=modal.previousUnit;try{$('#food-qty').value=M.convertQuantity(modal.food,$('#food-qty').value,old,el.value,$('#food-density').value||null);modal.previousUnit=el.value;}catch(err){el.value=old;throw err;}updateFoodPreview();}")
(P/'app.js').write_text(s)
s=(P/'version.json').read_text().replace('2026-09-26','2026-09-27')
(P/'version.json').write_text(s)
for n,pair in GUARDS.items():assert digest(P/n)==pair[1], 'Result checksum mismatch: '+n
print('Verified',len(GUARDS),'source changes; personal state untouched.')
