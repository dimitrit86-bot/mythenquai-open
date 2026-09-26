/* Household-only shared templates. Nutrition snapshots and private diary state stay separate. */
(function(){'use strict';
 const URL='https://wpmyuzpcraduhaybjvmb.supabase.co/functions/v1/nutrient-household-catalog';
 let records=[],status='Gemeinsamer Katalog wird nach Anmeldung geladen.',busy=null,last=0,generation=0;
 const hash=async s=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s)))).map(v=>v.toString(16).padStart(2,'0')).join('').slice(0,32);
 const get=(type)=>records.filter(x=>x.ownerId!==window.NK_HOUSEHOLD?.id).flatMap(x=>x[type]);
 function show(s){status=s;document.querySelectorAll('[data-shared-status]').forEach(e=>e.textContent=s);}
 async function build(list){const C=window.NK,keys=window.NK_DATA.nutrients.map(n=>n.key),out=[];for(const p of list){if(typeof p.id!=='string'||typeof p.name!=='string')continue;const item={ownerId:p.id,foods:[],recipes:[]};for(const type of ['foods','recipes'])for(const raw of p[type]||[]){try{let f=C.clone(raw),sourceId=f.id;const stub=C.initial();stub[type]=[f];C.validateState(stub,keys);const id='shared-'+(type==='foods'?'f-':'r-')+await hash(p.id+':'+sourceId);f.id=id;f.shared={ownerId:p.id,ownerName:p.name,sourceId};if(type==='foods'){f.kind='custom';f.category='Unser Haushalt · '+p.name;f.synonyms=(f.synonyms||'')+' '+p.name;f.source=(f.source||'Eigene Packungsangaben')+' · geteilt von '+p.name;}item[type].push(f);}catch{/* A malformed template never blocks the rest of the diary. */}}out.push(item);}return out;}
 async function refresh(force=false){const H=window.NK_HOUSEHOLD;if(!H?.authenticated)return;if(busy)return busy;if(!force&&Date.now()-last<12000)return;const gen=generation;show('Gemeinsamen Katalog laden …');busy=(async()=>{try{const r=await H.api('catalog',{},URL);if(!Array.isArray(r.profiles))throw Error('Ungültige Katalogantwort.');const data=await build(r.profiles);if(gen!==generation)return;records=data;last=Date.now();const count=get('foods').length,recipes=get('recipes').length;show(count+' Produkte und '+recipes+' Gerichte aus anderen Profilen verfügbar.');window.NK_APP?.refreshCatalog();}catch(e){if(gen!==generation)return;show((records.length?'Letzter geladener Katalog bleibt verfügbar. ':'')+(e.status===401?'Bitte erneut anmelden.':'Aktualisierung derzeit nicht möglich.'));}finally{busy=null;}})();return busy;}
 function clear(){generation++;records=[];last=0;show('Nach Anmeldung verfügbar.');}
 window.NK_SHARED={foods:()=>get('foods'),recipes:()=>get('recipes'),refresh,clear,get status(){return status;}};
 document.addEventListener('nk-profile-loaded',()=>refresh(true));
 document.addEventListener('nk-synced',()=>refresh(true));
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh();});
 document.addEventListener('click',e=>{const b=e.target.closest('[data-action="nav"]');if(b&&['recipes','search'].includes(b.dataset.route))refresh();});
 window.addEventListener('online',()=>refresh(true));
})();
