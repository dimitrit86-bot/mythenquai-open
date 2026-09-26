/* Unified name / barcode / link entry. No automatic diary writes or public product uploads. */
(function(){'use strict';
const C=window.NK_IMPORT_CORE,ENDPOINT='https://wpmyuzpcraduhaybjvmb.supabase.co/functions/v1/nutrient-product-lookup';
const E=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let dlg,rows=[],generation=0,owner='',mode='log',lastInput='',limit=40;
const $=s=>dlg?.querySelector(s);
function full(f){const copy=JSON.parse(JSON.stringify(f));copy.n=Object.fromEntries(window.NK_DATA.nutrients.map(n=>[n.key,typeof f.n[n.key]==='number'&&Number.isFinite(f.n[n.key])?f.n[n.key]:null]));return copy;}
function local(input){
 const p=C.normalize(input),state=window.NK_APP.getState(),saved=[...state.foods,...(window.NK_SHARED?.foods()||[])];
 const seen=new Set(),out=[];const match=f=>p.type==='name'?C.matches(f,p.query):f.id===p.key||f.shared?.sourceId===p.key||f.catalog?.code===p.code&&!!p.code||(()=>{try{return !!f.sourceUrl&&C.normalize(f.sourceUrl).key===p.key;}catch{return false;}})();
 for(const [list,kind] of [[saved,'saved'],[window.NK_DATA.foods,'base'],[window.NK_RETAIL_FOODS||[],'candidate']])for(const f of list){if(!match(f)||seen.has(f.id))continue;seen.add(f.id);out.push({f,kind});}
 const f=C.seed(input);if(f&&!seen.has(f.id)&&!out.some(r=>r.f.shared?.sourceId===f.id))out.push({f,kind:'candidate'});
 return out;
}
function label(row){const f=row.f;return row.kind==='saved'?(f.shared?'Unser Haushalt · '+f.shared.ownerName:'Bereits in deinem Profil'):row.kind==='base'?'Hinterlegte Lebensmitteldaten':f.lookup?.mode==='snapshot'?'Geprüfter Datenstand · 26.09.2026 · nicht live':(f.lookup?.provider||(f.catalog?.type==='off'?'Open Food Facts':'Produktquelle'));}
function render(){
 $('#finder-results').innerHTML=rows.slice(0,limit).map((r,i)=>`<article class="finder-result"><div><strong>${E(r.f.name)}</strong><small>${E(label(r))}${r.f.lookup?.quantity?' · '+E(r.f.lookup.quantity):''}</small><p>${r.f.n.energy==null?'—':E(Math.round(r.f.n.energy*10)/10)} kcal · ${r.f.n.protein==null?'—':E(Math.round(r.f.n.protein*100)/100)} g Protein · ${r.f.needsBasisConfirmation||r.f.lookup?.basisUncertain?'Bezugsmenge 100 g/ml prüfen':'pro 100 '+E(r.f.basis)}</p></div><button type="button" class="button secondary" data-finder-pick="${i}">${['saved','base'].includes(r.kind)?'Verwenden':'Prüfen & speichern'}</button></article>`).join('')+(rows.length>limit?'<button type="button" class="button secondary wide" id="finder-more">Weitere Treffer anzeigen</button>':'');
 const b=$('#finder-more');if(b)b.onclick=()=>{limit+=40;render();};
}
async function online(input,reset=false){const gen=++generation,id=owner;$('#finder-status').textContent='Online-Produktdaten werden gesucht …';$('#finder-online').disabled=true;
 try{const result=await window.NK_HOUSEHOLD.api('lookup',{input},ENDPOINT);if(gen!==generation||!dlg.open||window.NK_HOUSEHOLD.id!==id)return;
 const incoming=(result.products||[]).flatMap(f=>{try{const n=full(f);window.NK.validateFood(n,window.NK_DATA.nutrients.map(x=>x.key));return [{f:n,kind:'candidate'}];}catch{return [];}});
 if(reset&&incoming.length)rows=rows.filter(r=>r.kind==='saved');
 for(const r of incoming){if(!rows.some(old=>old.f.id===r.f.id||old.f.shared?.sourceId===r.f.id))rows.push(r);}
 $('#finder-status').textContent=(result.note?result.note+' ':'')+(rows.length?rows.length+' Treffer. Produktvariante vor dem Speichern prüfen.':'Kein passender Datensatz gefunden. Packung scannen oder Nährwerttext einfügen.');render();
 }catch(e){if(gen!==generation||!dlg.open||window.NK_HOUSEHOLD.id!==id)return;$('#finder-status').textContent=e.message+(rows.length?' Vorhandene Treffer bleiben verfügbar.':'');render();}
 finally{if(gen===generation&&$('#finder-online'))$('#finder-online').disabled=false;}
}
function open(which='log',value=''){
 if(!window.NK_APP||!window.NK_HOUSEHOLD?.id)return;generation++;owner=window.NK_HOUSEHOLD.id;mode=which;rows=[];limit=40;
 if(!dlg){dlg=document.createElement('dialog');dlg.id='product-finder-dialog';dlg.setAttribute('aria-labelledby','finder-title');document.body.append(dlg);dlg.addEventListener('close',()=>generation++);}
 dlg.innerHTML=`<div class="modal-head"><h2 id="finder-title">Nährwerte finden</h2><button type="button" class="icon-btn" id="finder-close" aria-label="Schliessen">×</button></div><p>Produktname, Barcode oder Produktlink eingeben. Vorhandene Produkte werden zuerst gesucht; gespeichert wird erst nach deiner Bestätigung.</p><form id="finder-form"><label for="finder-input">Name, Barcode oder Link</label><input id="finder-input" type="text" maxlength="2400" placeholder="Redefine Flank Steak oder Coop-Link" autocomplete="off" value="${E(value)}"><button class="button wide" type="submit">Nährwerte finden</button></form><p class="tiny">Links: Coop und Open Food Facts. Nicht jede Händlerseite erlaubt automatische Abrufe. Namen werden in euren Produkten und Katalogen gesucht; «Online ergänzen» fragt zusätzlich Open Food Facts ab. Nur der Suchtext/Produktlink wird übertragen, keine Profile oder Tagebücher.</p><p id="finder-status" role="status" class="small"></p><div id="finder-results"></div><button type="button" class="button secondary wide" id="finder-online" hidden>Online ergänzen</button><button type="button" class="muted-link" id="finder-scan">Stattdessen Packung scannen / Nährwerttext einfügen</button><p class="tiny">Community-Daten: Open Food Facts (ODbL). Fehlende Vitamine bleiben unbekannt. Schon gespeicherte Mahlzeiten werden nicht verändert.</p>`;
 $('#finder-close').onclick=()=>dlg.close();$('#finder-scan').onclick=()=>{dlg.close();window.NK_SCANNER.open();};
 $('#finder-form').onsubmit=async e=>{e.preventDefault();e.stopPropagation();generation++;limit=40;lastInput=$('#finder-input').value;try{const p=C.normalize(lastInput);rows=local(lastInput);render();$('#finder-online').hidden=p.type!=='name';$('#finder-online').disabled=false;$('#finder-status').textContent=rows.length?rows.length+' vorhandene Treffer.':'Kein lokaler Treffer.';if(p.type!=='name'||!rows.length)await online(lastInput,p.type!=='name');}catch(e){$('#finder-status').textContent=e.message;}};
 $('#finder-online').onclick=()=>online(lastInput);
 $('#finder-results').onclick=e=>{const b=e.target.closest('[data-finder-pick]');if(!b)return;const row=rows[Number(b.dataset.finderPick)];if(!row||owner!==window.NK_HOUSEHOLD.id)return;
 if(['saved','base'].includes(row.kind)){dlg.close();window.NK_APP.useFood(row.f.id,mode);return;}
 const f=full(row.f);dlg.close();window.NK_APP.reviewFood(f,mode==='ingredient');const form=document.getElementById('custom-food-form');if(!form)return;
 const notice=document.createElement('div');notice.className='notice';notice.innerHTML='<b>'+E(f.lookup?.mode==='snapshot'?'Geprüfter Datenstand – nicht live':f.lookup?.provider||'Importierte Produktangaben')+'</b><p>'+E(f.source||'')+'</p>'+(f.lookup?.warnings||[]).map(x=>'<p>'+E(x)+'</p>').join('')+(f.sourceUrl?'<a href="'+E(f.sourceUrl)+'" target="_blank" rel="noopener noreferrer">Originalquelle öffnen</a>':'');form.prepend(notice);
 const basis=form.querySelector('#custom-basis');if(f.needsBasisConfirmation||f.lookup?.basisUncertain){basis.insertAdjacentHTML('afterbegin','<option value="">Bitte die Packung prüfen</option>');basis.value='';basis.required=true;}
 const check=document.createElement('label');check.className='check';check.innerHTML='<input type="checkbox" required> Produktvariante, Bezugsmenge und Werte geprüft.';form.querySelector('.modal-foot').before(check);
 };
 dlg.showModal();$('#finder-input').focus();
}
function mount(){for(const [id,m] of [['food-search','log'],['ingredient-search','ingredient']]){const input=document.getElementById(id);if(!input||document.querySelector('[data-finder-for="'+id+'"]'))continue;const b=document.createElement('button');b.type='button';b.className='button secondary wide finder-launch';b.dataset.finderFor=id;b.textContent='Nährwerte finden · Name / Barcode / Link';b.onclick=()=>open(m,input.value);input.closest('.searchbox').after(b);}}
let queued=false;new MutationObserver(()=>{if(!queued){queued=true;queueMicrotask(()=>{queued=false;mount();});}}).observe(document.getElementById('app'),{subtree:true,childList:true});new MutationObserver(mount).observe(document.getElementById('dialog'),{subtree:true,childList:true});
document.addEventListener('nk-profile-loaded',()=>{if(dlg?.open)dlg.close();});
window.NK_FINDER={open,local};mount();
})();
