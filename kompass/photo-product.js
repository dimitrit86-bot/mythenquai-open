/* Package photo -> local barcode/text recognition -> reviewed public-product lookup.
   No image upload. Names are hypotheses, never nutrient estimates. */
(function(root){'use strict';
const clean=v=>String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/ß/g,'ss');
function barcode(v){const s=String(v||'').replace(/\s/g,'');if(!/^(?:\d{8}|\d{12,14})$/.test(s)||/^0+$/.test(s))return '';let sum=0;for(let i=s.length-2,n=0;i>=0;i--,n++)sum+=Number(s[i])*(n%2?1:3);return (10-sum%10)%10===Number(s.at(-1))?s:'';}
function suggest(raw){
 // Keep the front-label product words, discard nutrition, legal/contact and weight lines.
 const stop=/https?:|www\.|@|zutaten|ingredients|allerg|n[aä]hrwert|nutrition|energie|energy|kcal|\bkj\b|davon|fett\b|fat\b|kohlenhydrat|carbohydrate|sugar|zucker|salz|salt\b|ballaststoff|nahrungsfas|vitamin|mindestens haltbar|best before|aufbewahr|hergestellt|hersteller|kontakt|customer|recycl|serving|referenz|daily intake/i;
 const lines=[];
 for(let line of String(raw||'').slice(0,30000).split(/\r?\n/)){
  line=line.trim();if(!line||stop.test(line)||/^(?:eiweiss|eiweiß|protein)\s+[\d<]/i.test(line))continue;
  line=line.replace(/\b\d+(?:[.,]\d+)?\s*(?:kg|mg|g|ml|cl|dl|litre|liter|l|%)\b/gi,' ').replace(/\b\d{5,}\b/g,' ').replace(/[^\p{L}\p{N}. '&-]+/gu,' ').replace(/\s+/g,' ').trim();
  if(line.length<3||!/[a-zäöü]/i.test(line)||/^(?:vegan|vegetarisch|bio|plant based|neu|new)$/i.test(line))continue;
  if(!lines.some(x=>clean(x)===clean(line)))lines.push(line);
  if(lines.length===4)break;
 }
 return lines.join(' ').split(/\s+/).slice(0,9).join(' ').slice(0,120).trim();
}
function rank(foods,query){const code=barcode(query),words=[...new Set(clean(query).match(/[\p{L}\p{N}]+/gu)||[])].filter(w=>w.length>1);if(!words.length)return [];
 return foods.map(f=>{const name=clean(f.name),hay=clean([f.name,f.synonyms,f.catalog?.brand].join(' '));const exact=code&&(String(f.catalog?.code||'')===code||String(f.id).endsWith('-'+code)||String(f.shared?.sourceId||'').endsWith('-'+code));const count=words.filter(w=>hay.includes(w)).length;return {f,count,score:exact?10000:count*10+words.filter(w=>name.includes(w)).length,exact};}).filter(x=>x.exact||x.count>=Math.max(1,Math.ceil(words.length*.6))).sort((a,b)=>b.score-a.score).slice(0,20).map(x=>x.f);
}
function publicSource(f){try{const u=new URL(f.sourceUrl||f.catalog?.url||'');return u.protocol==='https:'&&!u.username&&!u.password?u.href:'';}catch{return '';}}
const API={barcode,suggest,rank};if(typeof module==='object'&&module.exports){module.exports=API;return;}
root.NK_PHOTO_PRODUCT=API;
const E=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const endpoint='https://wpmyuzpcraduhaybjvmb.supabase.co/functions/v1/nutrient-product-finder';
let session=null,epoch=0;
const $=s=>document.querySelector(s);
function reset(){epoch++;session=null;$('#photo-product-review')?.remove();}
function pause(){epoch++;if(session)session.busy=false;$('#photo-product-review')?.setAttribute('hidden','');}
function current(s,n){return session===s&&epoch===n&&s.options.current()&&$('#photo-product-review')?.hidden===false;}
function say(t){const p=$('#photo-product-status');if(p)p.textContent=t;}
function known(){return [...(root.NK_APP?.getState().foods||[]),...(root.NK_SHARED?.foods()||[]),...root.NK_DATA.foods];}
function catalog(){const map=new Map();for(const f of [...known(),...(root.NK_PRODUCT_SOURCES||[]),...(root.NK_RETAIL_FOODS||[])])if(!map.has(f.id))map.set(f.id,f);return [...map.values()];}
function source(f){return f.shared?'Unser Haushalt · '+f.shared.ownerName:f.sourceSnapshot?'Gespeicherter Quellenstand · '+f.importedAt:f.catalog?.type==='off'?'Open Food Facts · Community-Daten':f.source||'Hinterlegter Katalog';}
function render(s){const el=$('#photo-product-results');if(!el)return;el.innerHTML=s.matches.map((f,i)=>`<button type="button" class="photo-match" data-photo-match="${i}"><strong>${E(f.name)}</strong><span>${E(source(f))}</span><span>${f.n.energy==null?'Energie unbekannt':E(f.n.energy)+' kcal'} · ${f.n.protein==null?'Protein unbekannt':E(f.n.protein)+' g Protein'} · ${f.needsBasisConfirmation?'pro 100 g/ml – prüfen':'pro 100 '+E(f.basis)}</span></button>`).join('');}
function mount(s){let box=$('#photo-product-review');if(box){box.hidden=false;return;}
 box=document.createElement('section');box.id='photo-product-review';box.className='photo-product-panel';box.innerHTML=`<p class="eyebrow">FOTO → PRODUKT → NÄHRWERTE</p><h3>Welches Produkt ist es?</h3><p class="small">Wir lesen Marke, Produktname oder Barcode auf deinem Foto und suchen passende Datensätze. Die Erkennung ist ein Vorschlag, keine sichere Identifikation.</p><form id="photo-product-search"><label for="photo-product-query">Erkannter Suchbegriff / Barcode · bearbeitbar</label><input id="photo-product-query" maxlength="120" autocomplete="off" placeholder="Marke und genaue Sorte"><button type="submit" class="button wide">Nährwerte suchen</button></form><p id="photo-product-status" class="small" role="status" aria-live="polite"></p><div id="photo-product-results"></div><div id="photo-product-details"></div><details class="spaced"><summary>Gelesenen Packungstext ansehen</summary><pre id="photo-product-raw"></pre></details><p class="tiny">Dein Foto bleibt auf diesem Gerät. Nur der angezeigte Suchbegriff oder Barcode geht bei der Online-Suche an den Datenservice / Open Food Facts (ODbL). Keine umgekehrte Bildsuche und keine Veröffentlichung deiner Produkte.</p>`;
 $('#scan-review').before(box);
 box.querySelector('form').onsubmit=e=>{e.preventDefault();search(s,true);};
 box.querySelector('#photo-product-query').oninput=()=>{epoch++;s.busy=false;s.matches=[];render(s);$('#photo-product-details').innerHTML='';say('Suchbegriff geändert. Mit «Nährwerte suchen» erneut suchen.');};
 box.onclick=e=>{const b=e.target.closest('[data-photo-match]');if(b)details(s,s.matches[Number(b.dataset.photoMatch)]);};
}
async function search(s,force=false){const q=$('#photo-product-query')?.value.trim();if(!q||q.length<2){say('Kein lesbarer Produktname gefunden. Vorderseite schärfer fotografieren oder Marke und Sorte hier ergänzen.');return;}
 if(s.busy)return;s.busy=true;const n=++epoch;
 s.matches=rank(catalog(),q);render(s);$('#photo-product-details').innerHTML='';say('Passende Produktdaten werden gesucht …');
 try{
  const code=barcode(q);
  if(!navigator.onLine){say('Offline: '+s.matches.length+' hinterlegte Treffer. Neue Online-Produkte benötigen eine Verbindung.');return;}
  // Repeat the same query only on explicit request, never per keystroke or mode switch.
  if(!force&&s.searched===q)return;s.searched=q;
  const response=code?await root.NK_HOUSEHOLD.api('barcode',{code}):await root.NK_HOUSEHOLD.api('search',{query:q},endpoint);
  if(!current(s,n))return;
  const products=code?[response.product]:response.products||[];const seen=new Set(s.matches.map(f=>f.id));
  for(const p of products.slice(0,20)){if(!p)continue;const f=root.NK_FINDER.fromOFF(p);if(f&&!seen.has(f.id)){s.matches.push(f);seen.add(f.id);}}
  render(s);say(s.matches.length?'Bitte den passenden Treffer auswählen. Marke, Sorte und Bezugsmenge mit der Packung vergleichen.':'Kein Treffer mit Nährwerten. Suchbegriff kürzen/korrigieren, Barcode fotografieren oder die Nährwerttabelle auslesen.');
 }catch(e){if(current(s,n))say('Online-Suche: '+e.message+(s.matches.length?' Hinterlegte Treffer bleiben auswählbar.':' Du kannst oben zur Nährwerttabelle wechseln oder den Suchbegriff korrigieren.'));}
 finally{if(current(s,n))s.busy=false;}
}
function details(s,f){if(!f)return;const duplicate=known().find(x=>x.id===f.id||x.shared?.sourceId===f.id||publicSource(f)&&publicSource(x)===publicSource(f));if(duplicate)f=duplicate;const area=$('#photo-product-details'),all=root.NK_DATA.nutrients,link=publicSource(f);const existed=known().some(x=>x.id===f.id);const autoBasis=existed||(!f.needsBasisConfirmation&&['g','ml'].includes(f.basis));
 area.innerHTML=`<form id="photo-product-confirm"><h3>${E(f.name)}</h3><p class="small">${E(source(f))}</p>${link?'<p><a target="_blank" rel="noopener noreferrer" href="'+E(link)+'">Produktquelle öffnen</a></p>':''}<label for="photo-product-basis">Diese Produktwerte gelten pro …</label><select id="photo-product-basis" required><option value="">Packungsspalte auswählen</option><option value="g">100 g</option><option value="ml">100 ml</option></select><details class="spaced"><summary>Alle gefundenen Nährwerte</summary>${all.map(k=>`<div class="source-item">${E(k.label)}: <b>${f.n[k.key]==null?'Unbekannt':E(f.n[k.key])+' '+E(k.unit)}</b></div>`).join('')}</details><label class="check"><input type="checkbox" required id="photo-product-checked">Das ist die richtige Marke und Variante; die Angaben und Bezugsmenge passen zu meiner Packung.</label><p class="small">Keine gegessene Menge eintragen. Es werden nur Produktwerte übernommen; im nächsten Schritt kannst du sie bearbeiten und eine Stückportion hinterlegen. Kein Produkt wird allein durch ein Foto gespeichert.</p><button class="button wide" type="submit">Werte übernehmen</button><p id="photo-product-error" class="error" role="status"></p></form>`;
 $('#photo-product-basis').value=autoBasis?f.basis:'';$('#photo-product-basis').disabled=existed;
 $('#photo-product-basis').onchange=()=>{$('#photo-product-checked').checked=false;};
 area.querySelector('form').onsubmit=e=>{e.preventDefault();try{if(!s.options.current())throw Error('Profil oder Foto wurde gewechselt. Bitte neu öffnen.');const draft=root.NK.clone(f);draft.basis=$('#photo-product-basis').value;if(!['g','ml'].includes(draft.basis)||!$('#photo-product-checked').checked)throw Error('Bitte Produkt und Bezugsmenge bestätigen.');draft.n=Object.fromEntries(all.map(k=>[k.key,Number.isFinite(f.n[k.key])?f.n[k.key]:null]));draft.needsBasisConfirmation=false;draft.source=source(f);draft.sourceUrl=link||null;root.NK.validateFood(draft,all.map(k=>k.key));if(!all.some(k=>draft.n[k.key]!==null))throw Error('Keine Nährwerte vorhanden. Bitte die Tabelle fotografieren.');s.options.transfer(draft,existed);}catch(err){$('#photo-product-error').textContent=err.message;}};
 area.scrollIntoView({block:'nearest'});
}
async function identify(options){
 if(session?.options.image===options.image){session.options=options;mount(session);return;}
 reset();const s={options,matches:[],busy:false,searched:''};session=s;mount(s);const n=++epoch;say('Barcode und Produktbeschriftung werden auf deinem Gerät gelesen …');
 let code='',text='';try{
  await options.load('vendor/zxing-browser.min.js','ZXingBrowser');if(!current(s,n))return;
  try{const canvas=document.createElement('canvas'),img=options.image,scale=Math.min(1,1800/Math.max(img.naturalWidth,img.naturalHeight));canvas.width=Math.max(1,Math.round(img.naturalWidth*scale));canvas.height=Math.max(1,Math.round(img.naturalHeight*scale));canvas.getContext('2d').drawImage(img,0,0,canvas.width,canvas.height);const result=new root.ZXingBrowser.BrowserMultiFormatReader().decodeFromCanvas(canvas);code=barcode(result.getText());}catch{}
 }catch{} // Barcode library failure must not prevent the existing local OCR path.
 if(!current(s,n))return;
 if(!code){try{text=await options.readText('product');}catch(e){if(current(s,n))say('Beschriftung nicht lesbar: '+e.message+' Bitte Marke und Sorte eingeben.');}}
 if(!current(s,n))return;const query=code||suggest(text);$('#photo-product-query').value=query;$('#photo-product-raw').textContent=text|| (code?'Barcode: '+code:'Kein Text erkannt.');
 if(query)await search(s);else say('Keine lesbare Produktbeschriftung erkannt. Bitte Vorderseite mit Marke und Sorte fotografieren oder Suchbegriff eingeben. Lose Lebensmittel und Tellerfotos sind keine exakte Produktidentifikation.');
}
Object.assign(API,{identify,reset,pause});
})(typeof window!=='undefined'?window:globalThis);
