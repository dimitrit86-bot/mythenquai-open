/* Authenticated household library; never writes another profile or a public catalogue. */
(function(){'use strict';
 const C=window.NK,D=window.NK_DATA,KEYS=D.nutrients.map(n=>n.key);
 const ENDPOINT='https://wpmyuzpcraduhaybjvmb.supabase.co/functions/v1/nutrient-library';
 let rows=[],status='Wird nach der Anmeldung geladen.',asOf='',last=0,busy=null,epoch=0;
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function convert(record){
  if(!['food','recipe'].includes(record.kind)||typeof record.ownerId!=='string'||typeof record.ownerName!=='string'||!/^shared-[a-f0-9]{64}$/.test(record.key))throw Error('Ungültiger Bibliothekseintrag.');
  const item=C.clone(record.item),shared={ownerId:record.ownerId,ownerName:record.ownerName,originalId:item.id};
  item.id=record.key;item.shared=shared;
  if(record.kind==='food'){item.kind='custom';item.category='Gemeinsame Produkte · '+record.ownerName;C.validateFood(item,KEYS);}
  else{const test=C.initial();test.recipes=[item];C.validateState(test,KEYS);}
  return {kind:record.kind,item};
 }
 async function refresh(force=false){
  const H=window.NK_HOUSEHOLD;if(!H?.id||!H.authenticated)return false;
  if(busy)return busy;if(!force&&Date.now()-last<15000)return true;
  const captured=epoch;
  busy=(async()=>{try{
   const data=await H.api('list',{},ENDPOINT);
   if(captured!==epoch||!H.authenticated)return false;
   if(data.version!==1||!Array.isArray(data.items)||data.items.length>10000)throw Error('Ungültige Bibliotheksantwort.');
   let skipped=Number(data.skipped)||0;const next=[];const seen=new Set();
   for(const r of data.items){try{const x=convert(r);if(!seen.has(x.item.id)){seen.add(x.item.id);next.push(x);}}catch{skipped++;}}
   rows=next;asOf=data.asOf;last=Date.now();status=skipped?'Bibliothek geladen · '+skipped+' ungültige Einträge ausgelassen.':'Für alle Profile verfügbar · synchronisiert';
   document.dispatchEvent(new Event('nk-library-updated'));return true;
  }catch(e){if(captured===epoch){status=(rows.length?'Letzter geladener Stand. ':'')+e.message;document.dispatchEvent(new Event('nk-library-status'));}return false;}
  finally{busy=null;}})();return busy;
 }
 const list=kind=>rows.filter(r=>r.kind===kind&&r.item.shared.ownerId!==window.NK_HOUSEHOLD?.id).map(r=>C.clone(r.item));
 function notice(){return `<div class="shared-library-note"><div><b>Gemeinsame Produkte & Gerichte</b><p>Was ihr speichert, ist nach der Synchronisierung für alle Profile dieses privaten Bereichs nutzbar. Tagebücher und Tagesziele bleiben getrennt.</p><span class="small" data-library-status>${esc(status)}</span></div><button type="button" class="button secondary" data-shared-refresh>Bibliothek aktualisieren</button></div>`;}
 function clear(){epoch++;rows=[];last=0;asOf='';status='Nicht angemeldet';document.dispatchEvent(new Event('nk-library-updated'));}
 document.addEventListener('nk-profile-loaded',()=>refresh(true));
 document.addEventListener('nk-state-synced',()=>refresh(true));
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh(true);});
 window.addEventListener('online',()=>refresh(true));
 document.addEventListener('click',async e=>{const b=e.target.closest('[data-shared-refresh]');if(!b)return;b.disabled=true;await refresh(true);document.querySelectorAll('[data-library-status]').forEach(n=>n.textContent=status);b.disabled=false;});
 setInterval(()=>{if(!document.hidden)refresh();},60000);
 window.NK_LIBRARY={refresh,clear,notice,getFoods:()=>list('food'),getRecipes:()=>list('recipe'),get status(){return status;},get asOf(){return asOf;}};
})();
