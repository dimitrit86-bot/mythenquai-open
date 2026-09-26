/* Profile form helpers. Preview only; saving stays in the existing authenticated app flow. */
(function(root){'use strict';
const M=root.NK_MACROS,C=root.NK,E=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=v=>Number.isFinite(v)?new Intl.NumberFormat('de-CH',{maximumFractionDigits:1}).format(v):'—';
const options=(items,v)=>items.map(([key,label])=>`<option value="${key}" ${String(v??'')===String(key)?'selected':''}>${E(label)}</option>`).join('');
function fields(p){return `<section class="macro-profile-section" aria-labelledby="macro-profile-title"><h3 id="macro-profile-title">Ernährungsprofil & Tagesziele</h3><div class="form-grid"><div class="field"><label for="nutrition-mode">Dein Ernährungsziel</label><select id="nutrition-mode">${options([['','Bisherige Ziele beibehalten'],...Object.entries(M.presets).map(([k,v])=>[k,v.label])],p.nutritionMode)}</select></div><div class="field"><label for="activity-pal">Aktivität im Tagesdurchschnitt</label><select id="activity-pal">${options([['','Bitte auswählen'],...M.activities],p.activityPAL)}</select></div></div><p class="tiny">Gilt nur für das aktive Personenprofil. Aktivität inklusive Sport einschätzen; die Zielauswahl selbst erhöht den Aktivitätsfaktor nicht.</p><div id="macro-preview" aria-live="polite">${preview(p)}</div></section>`;}
function read(form,p){
 const next=JSON.parse(JSON.stringify(p));
 const get=id=>form.querySelector('#'+id);
 for(const [key,id,min,max] of [['age','age',0,120],['weight','weight',1,600],['height','height',40,260],['calcWeight','calc-weight',1,600]])next[key]=C.number(get(id).value,{optional:true,min,max});
 if(next.age!==null&&!Number.isInteger(next.age))throw Error('Alter in ganzen Jahren eingeben.');
 next.sex=get('sex').value;next.special=get('special').checked;
 next.nutritionMode=get('nutrition-mode').value;next.activityPAL=C.number(get('activity-pal').value,{optional:true,min:1.4,max:2.2});M.validate(next);
 next.manual={...p.manual};
 for(const k of ['energy','protein','carbs','fat']){const v=C.number(get('target-'+k).value,{optional:true,min:0.000001});if(v===null)delete next.manual[k];else next.manual[k]=v;}
 return next;
}
function preview(p){
 const r=M.calculate(p),refs=C.targets(p).values;
 const rows=[['energy','Energie','kcal'],['protein','Protein','g'],['carbs','Kohlenhydrate','g'],['fat','Fett','g']];
 const card=rows.map(([k,label,unit])=>`<div class="macro-preview-item"><span>${label}</span><strong data-preview-target="${k}">${fmt(refs[k]?.value)} <small>${unit}/Tag</small></strong><small>${refs[k]?.type==='Eigenes Ziel'?'Eigenes Ziel':refs[k]?'Orientierungswert':'Noch nicht berechenbar'}</small></div>`).join('');
 const preset=M.presets[p.nutritionMode];
 const sources=[['energy','Energieformel & Aktivität'],['protein','Protein-Basisreferenz'],['fat','Fett-Richtwert'],['carbs','Kohlenhydrate'],['sport','Sport-Protein'],['muscle','Muskelaufbau-Studien'],['loss','Protein bei Gewichtsreduktion']];
 return `<p class="small"><b>${E(preset?.label||'Bisherige Ziele bleiben bestehen')}</b><br>${E(preset?.description||'Wähle ein Ernährungsziel und speichere das Profil, um die neue automatische Makroplanung zu aktivieren.')}</p><div class="macro-preview-grid">${card}</div>${r.weight?`<p class="small">Protein-Berechnungsgewicht: <b>${fmt(r.weight)} kg</b> · ${E(r.weightSource)}</p>`:''}${r.maintenance?`<p class="small">Geschätzter Erhaltungsbedarf: <b>${fmt(r.maintenance)} kcal/Tag</b>. ${r.energyAdjustment?'Plananpassung: '+fmt(r.energyAdjustment)+' kcal/Tag.':''}</p>`:''}${r.notes.map(n=>`<p class="macro-hint">${E(n)}</p>`).join('')}<p class="tiny">Vorschau – wird erst mit «Profil speichern» übernommen. Eigene Zielwerte unten haben Vorrang; ein leeres Feld verwendet wieder die Automatik. Ein neues Profil ändert keine bereits protokollierte Menge.</p><details><summary>Berechnung & Quellen</summary><p class="small">Ruheenergie nach DGE: (0,047 × aktuelles Gewicht − 0,01452 × Alter + 3,21 [+ 1,009 bei männlicher Tabellenbasis]) × 239. Erhaltungsbedarf = Ruheenergie × gewählte Aktivität. Grösse dient der BMI-Prüfung und dem Protein-Referenzgewicht.</p><p class="small">Makroplan: Protein nach Berechnungsgewicht; Fettanteil 30 % (Sport 25 %); Kohlenhydrate aus der verbleibenden Energie. Muskelaufbau: +5 %, maximal 200 kcal. Abnehmen: −10 %, maximal 300 kcal. Diese konkreten Voreinstellungen und die Übertragung auf BMI-22-Referenzgewicht sind vereinfachte App-Annahmen, keine exakt vorgeschriebenen individuellen Bedarfswerte. Die Planung nutzt 4/4/9 kcal je Gramm; Energie aus Ballaststoffen, Alkohol oder Polyolen ist darin nicht gesondert eingeplant.</p><p class="small">Automatik nur bei Erwachsenen mit BMI 18,5–40 ohne markierte besondere Situation. Abnehmen zusätzlich nicht automatisch bei BMI unter 20 oder ab 65 Jahren. Dies sind konservative Grenzen dieser App; keine medizinischen Grenzwerte. Fachlich abgestimmte eigene Ziele bleiben möglich.</p><p class="small">Quellen geprüft 26.09.2026: ${sources.map(([k,label])=>`<a href="${M.sources[k]}" target="_blank" rel="noopener noreferrer">${label}</a>`).join(' · ')}</p></details>`;
}
function refresh(){const form=document.getElementById('profile-form'),el=document.getElementById('macro-preview');if(!form||!el||!root.NK_APP)return;try{el.innerHTML=preview(read(form,root.NK_APP.getState().profile));}catch(e){el.innerHTML='<p class="error">'+E(e.message)+'</p>';}}
root.NK_MACRO_PROFILE={fields,read,preview,refresh};
let timer;document.addEventListener('input',e=>{if(e.target.closest('#profile-form')&&!e.target.closest('#macro-preview')){clearTimeout(timer);timer=setTimeout(refresh,150);}});document.addEventListener('change',e=>{if(e.target.closest('#profile-form'))refresh();});
})(window);
