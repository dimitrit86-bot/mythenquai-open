/* Inline paste/import. No clipboard permissions, network or personal persistence. */
(function(root){'use strict';
const E=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function mount(form){
 if(!form||form.querySelector('#custom-text-panel')||!root.NK_SCANNER||!root.NK_PORTIONS)return;
 const panel=document.createElement('details');panel.id='custom-text-panel';panel.className='custom-text-panel';panel.open=!root.NK_DATA.nutrients.some(n=>form.querySelector('#custom-'+n.key)?.value);
 panel.innerHTML=`<summary>Nährwerttext einfügen & auslesen</summary><p class="small">Kopiere die Nährwerttabelle von einer Packung oder Webseite hierher. Auch Text aus der Fotoerkennung deines Handys ist möglich. Der Text bleibt auf diesem Gerät.</p><label for="custom-nutrition-text">Nährwerttext</label><textarea id="custom-nutrition-text" rows="5" maxlength="30000" placeholder="pro 30 g&#10;Energie 150 kcal&#10;Fett 9 g&#10;Kohlenhydrate 12 g&#10;Eiweiss 3 g&#10;Salz 0,2 g"></textarea><button type="button" class="button secondary" id="custom-read-text">Text auslesen</button><section id="custom-text-review" hidden><div class="form-grid spaced"><div class="field"><label for="custom-text-column">Wertespalte</label><select id="custom-text-column"><option value="first">Erste Wertespalte</option><option value="last">Letzte Wertespalte</option></select></div><div class="field"><label for="custom-text-amount">Diese Werte gelten für …</label><input id="custom-text-amount" inputmode="decimal" placeholder="z. B. 30"></div><div class="field"><label for="custom-text-unit">Einheit</label><select id="custom-text-unit"><option value="g">g</option><option value="ml">ml</option></select></div></div><p class="tiny">Tabellenspalte und Bezugsmenge müssen zusammenpassen. Nicht die gegessene Menge eintragen. Gramm und Milliliter werden nicht gleichgesetzt.</p><div id="custom-text-values"></div><p class="small" id="custom-text-warnings"></p><label class="check"><input id="custom-text-confirm" type="checkbox"> Werte, Spalte und Bezugsmenge geprüft. Die Nährwertfelder unten werden ersetzt; nicht gefundene Werte bleiben leer.</label><button type="button" class="button" id="custom-apply-text">Werte in dieses Produkt übernehmen</button></section><p id="custom-text-status" class="small" role="status" aria-live="polite"></p><button type="button" class="muted-link" id="custom-undo-text" hidden>Letzte Textübernahme rückgängig</button><p class="tiny">Name und Rezeptkontext bleiben erhalten. Erst «Produkt speichern» speichert das Produkt.</p>`;
 const grid=form.querySelector('.form-grid');grid.after(panel);
 const $=s=>panel.querySelector(s);let parsed=null,raw='',result=null,undo=null;
 const fmt=v=>new Intl.NumberFormat('de-CH',{maximumFractionDigits:4}).format(v);
 function clearPreview(message){result=null;$('#custom-text-confirm').checked=false;$('#custom-apply-text').disabled=true;$('#custom-text-status').textContent=message;}
 function refresh(){
  clearPreview('');if(!parsed)return;
  try{
   const data={};for(const n of root.NK_DATA.nutrients){const input=$('#text-raw-'+n.key);if(input)data[n.key]=input.value;}
   result=root.NK_PORTIONS.convert(data,parsed.q,$('#custom-text-amount').value,$('#custom-text-unit').value);
   const count=Object.values(result.n).filter(v=>v!==null).length;
   $('#custom-text-status').textContent=count?`${count} Werte · Ausgangswert × 100 ÷ ${fmt(result.sourceAmount)} → pro 100 ${result.basis}. Noch nicht übernommen.`:'Keine sicher bezifferten Nährwerte gefunden.';
   panel.querySelectorAll('[data-text-output]').forEach(el=>{const v=result.n[el.dataset.textOutput];el.textContent=v==null?'Unbekannt':fmt(v);});
   $('#custom-apply-text').disabled=!count;
  }catch(e){clearPreview(e.message);panel.querySelectorAll('[data-text-output]').forEach(el=>el.textContent='—');}
 }
 function table(){
  const fields=root.NK_DATA.nutrients.filter(n=>parsed.n[n.key]!=null||parsed.q[n.key]);
  $('#custom-text-values').innerHTML='<div class="text-table-head"><span>Nährstoff</span><span>Ausgangswert</span><span>Pro 100 g/ml</span></div>'+fields.map(n=>`<div class="text-table-row"><label for="text-raw-${n.key}">${E(n.label)}<small>${E(n.unit)}</small></label><input id="text-raw-${n.key}" data-text-raw="${n.key}" aria-label="${E(n.label)} Ausgangswert" inputmode="decimal" placeholder="unbekannt" value="${parsed.n[n.key]==null?'':E(parsed.n[n.key])}"><output data-text-output="${n.key}">—</output></div>${parsed.q[n.key]?'<p class="tiny">'+E(parsed.q[n.key])+'</p>':''}`).join('');
  $('#custom-text-warnings').textContent=parsed.warnings.filter(w=>!w.includes('Vor dem Speichern auf 100')).join(' ');
 }
 function parseNow(reset){
  if(reset){raw=$('#custom-nutrition-text').value;$('#custom-text-column').value='first';}
  if(!raw.trim()){clearPreview('Bitte zuerst Nährwerttext einfügen.');return;}
  if(raw.length>30000){clearPreview('Bitte höchstens 30’000 Zeichen einfügen.');return;}
  const column=$('#custom-text-column').value;parsed=root.NK_SCANNER.parse(raw,column);
  const guesses=root.NK_PORTIONS.hints(raw),guess=column==='last'?guesses.at(-1):guesses[0];
  $('#custom-text-amount').value=(column==='first'||guesses.length>1)&&guess?guess.amount:'';
  if(guess)$('#custom-text-unit').value=guess.unit;
  $('#custom-text-review').hidden=false;table();refresh();
 }
 $('#custom-read-text').onclick=()=>parseNow(true);
 $('#custom-text-column').onchange=()=>parseNow(false);
 $('#custom-text-amount').oninput=refresh;$('#custom-text-unit').onchange=refresh;
 $('#custom-text-values').oninput=e=>{if(e.target.hasAttribute('data-text-raw'))refresh();};
 $('#custom-nutrition-text').oninput=()=>{clearPreview('Text geändert. Bitte erneut «Text auslesen» drücken.');$('#custom-text-review').hidden=true;};
 $('#custom-apply-text').onclick=()=>{
  if(!result||!$('#custom-text-confirm').checked){$('#custom-text-status').textContent='Bitte die Vorschau und das Ersetzen der Nährwertfelder bestätigen.';return;}
  try{undo=root.NK_APP.applyTextNutrition(result);$('#custom-undo-text').hidden=false;$('#custom-text-status').textContent='Nährwerte übernommen. Du kannst unten weiter korrigieren. Zum Speichern «Produkt speichern» drücken.';$('#custom-text-confirm').checked=false;}
  catch(e){$('#custom-text-status').textContent='Nicht übernommen: '+e.message;}
 };
 $('#custom-undo-text').onclick=()=>{if(undo){root.NK_APP.restoreTextNutrition(undo);undo=null;$('#custom-undo-text').hidden=true;$('#custom-text-status').textContent='Die vorherigen Nährwertfelder sind wiederhergestellt. Noch nicht gespeichert.';}};
}
let queued=false;const rootDialog=document.getElementById('dialog');
new MutationObserver(()=>{if(queued)return;queued=true;queueMicrotask(()=>{queued=false;mount(rootDialog.querySelector('#custom-food-form'));});}).observe(rootDialog,{childList:true,subtree:true});
root.NK_CUSTOM_TEXT={mount};
})(window);
