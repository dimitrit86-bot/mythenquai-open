/* Private household session + versioned cloud sync. No password in browser source. */
(function(){'use strict';
const BASE='https://wpmyuzpcraduhaybjvmb.supabase.co/functions/v1/',ENDPOINT=BASE+'nutrient-compass';
const SESSION='nk:session:1',CACHE='nk:encrypted-pending:1',LAST='nk:last-profile:1';
const $=s=>document.querySelector(s),E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let baseRaw=null,conflictInfo=null,auth=null,current=null,raw=null,pending=false,busy=null,blocked=false,timer,cryptoKey=null,cacheJob=Promise.resolve(),cacheSeq=0,status='Nicht angemeldet',started=false,profiles=[],activation=new URLSearchParams(location.hash.slice(1)).get('activate');
if(activation)history.replaceState(null,'',location.pathname+location.search);
const gate=$('#gate-root'),dlg=$('#household-dialog');
function setStatus(text){status=text;document.querySelectorAll('[data-nk-status]').forEach(n=>{n.textContent=text;n.classList.toggle('sync-warning',pending||blocked);});}
async function api(action,data={},endpoint=ENDPOINT){
 const controller=new AbortController(),t=setTimeout(()=>controller.abort(),25000);
 try{const r=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json',...(auth?.token?{'x-nk-session':auth.token}:{})},body:JSON.stringify({action,...data}),signal:controller.signal,cache:'no-store'});let j;try{j=await r.json();}catch{throw Error('Der Datenservice antwortet nicht korrekt.');}if(!r.ok){const e=Error(j.error||'Anfrage fehlgeschlagen.');e.status=r.status;e.conflict=!!j.conflict;e.retry=j.retry;throw e;}return j;}catch(e){if(e.name==='AbortError')throw Error('Verbindung unterbrochen. Änderungen sind noch nicht synchronisiert.');throw e;}finally{clearTimeout(t);}}
function safeStore(store,k,v){try{v===null?store.removeItem(k):store.setItem(k,v);}catch{throw Error('Der Browserspeicher ist nicht verfügbar. Bitte privaten Modus oder Speicherplatz prüfen.');}}
function saveSession(remember=false){safeStore(sessionStorage,SESSION,JSON.stringify(auth));if(remember)safeStore(localStorage,SESSION,JSON.stringify(auth));else safeStore(localStorage,SESSION,null);}
function b64(bytes){let s='';for(let i=0;i<bytes.length;i+=8192)s+=String.fromCharCode(...bytes.subarray(i,i+8192));return btoa(s);}
function bytes(s){return Uint8Array.from(atob(s),x=>x.charCodeAt(0));}
async function importKey(key){if(!/^[a-f0-9]{64}$/.test(key))throw Error('Verschlüsselungsschlüssel fehlt.');return crypto.subtle.importKey('raw',Uint8Array.from(key.match(/../g),x=>parseInt(x,16)),'AES-GCM',false,['encrypt','decrypt']);}
async function cacheState(){
 if(!current||!cryptoKey)return;const seq=++cacheSeq,record={id:current.id,name:current.name,revision:current.revision,raw,pending,baseRaw};
 cacheJob=(async()=>{const iv=crypto.getRandomValues(new Uint8Array(12));const cipher=await crypto.subtle.encrypt({name:'AES-GCM',iv},cryptoKey,new TextEncoder().encode(JSON.stringify(record)));if(seq===cacheSeq)safeStore(localStorage,CACHE,JSON.stringify({iv:b64(iv),data:b64(new Uint8Array(cipher))}));})();return cacheJob;
}
async function readCache(){const s=localStorage.getItem(CACHE);if(!s)return null;try{const c=JSON.parse(s);return JSON.parse(new TextDecoder().decode(await crypto.subtle.decrypt({name:'AES-GCM',iv:bytes(c.iv)},cryptoKey,bytes(c.data))));}catch{throw Error('Die lokale Sicherung konnte nicht entschlüsselt werden. Sie bleibt unverändert.');}}
function publishMerged(){window.NK_APP?.applySyncedState(JSON.parse(raw));}
async function reconcile(){
 const server=(await api('get',{id:current.id})).profile;
 const remote=window.NK.validateState(server.state,window.NK_DATA.nutrients.map(n=>n.key));
 const merged=window.NK_MERGE.merge(baseRaw?JSON.parse(baseRaw):null,JSON.parse(raw),remote);
 if(merged.conflicts.length){
  blocked=true;conflictInfo={remote,revision:server.revision,localRaw:raw,conflicts:merged.conflicts};
  setStatus('Änderungskonflikt · lokale Eingaben erhalten · Profile & Sync öffnen');
  await cacheState().catch(()=>setStatus('Konflikt · lokale Sicherung fehlgeschlagen! Bitte exportieren.'));
  return false;
 }
 current.revision=server.revision;baseRaw=JSON.stringify(remote);raw=JSON.stringify(merged.state);
 pending=!window.NK_MERGE.equal(merged.state,remote);blocked=false;conflictInfo=null;
 await cacheState().catch(()=>setStatus('Lokale Sicherung nicht verfügbar · bitte exportieren.'));
 publishMerged();return true;
}
async function flush(){
 clearTimeout(timer);if(busy)return busy;
 busy=(async()=>{
  let retries=0;
  if(blocked){if(!await reconcile()){const e=Error('Unterschiedliche Änderungen am selben Eintrag. Bitte unter Profile & Sync prüfen. Neue Eingaben bleiben lokal erhalten.');e.conflict=true;throw e;}}
  while(pending&&current){
   const captured=raw,rev=current.revision;setStatus('Wird synchronisiert …');
   try{
    const r=await api('save',{id:current.id,revision:rev,state:JSON.parse(captured)});
    current.revision=r.revision;baseRaw=captured;pending=raw!==captured;blocked=false;conflictInfo=null;
    await cacheState().catch(()=>{});
    setStatus(pending?'Weitere Änderungen …':'Synchronisiert');
    document.dispatchEvent(new Event('nk-state-synced'));
   }catch(e){
    if(e.conflict&&retries++<4){try{if(await reconcile())continue;}catch(readError){e=readError;}}
    if(e.conflict){blocked=true;setStatus('Änderungskonflikt · lokal erhalten · Profile & Sync öffnen');}
    else if(e.status===401)setStatus('Erneut anmelden · noch nicht synchronisiert');
    else if(e.status===400||e.status===413)setStatus('Speichern abgelehnt: '+e.message);
    else setStatus('Keine Verbindung · noch nicht synchronisiert');
    await cacheState().catch(()=>setStatus('Nicht gesichert! Bitte lokale Fassung exportieren.'));
    if(e.status===401)showGate('login','Sitzung abgelaufen. Bitte erneut anmelden. Noch nicht gesendete Änderungen bleiben erhalten.');
    throw e;
   }
  }
  if(!pending&&!blocked)setStatus('Synchronisiert');
  return true;
 })();
 try{return await busy;}finally{busy=null;}
}
function queue(value){
 if(!auth||!current)throw Error('Bitte zuerst anmelden und ein Profil wählen.');
 if(value.length>3900000)throw Error('Dieses Profil erreicht die Grössenbegrenzung. Bitte die Daten sichern; die Eingabe wurde nicht gespeichert.');
 raw=value;pending=true;
 setStatus(blocked?'Änderungskonflikt · neue Eingaben werden lokal gesichert':'Wird gespeichert …');
 cacheState().then(()=>{if(pending)setStatus(blocked?'Lokal gesichert · Änderungskonflikt bitte prüfen':'Lokal gesichert · Synchronisierung …');}).catch(()=>setStatus('Lokale Sicherung fehlgeschlagen! App offen lassen und exportieren.'));
 clearTimeout(timer);if(!blocked)timer=setTimeout(()=>flush().catch(()=>{}),500);
}
window.NK_STORE={getItem:()=>raw,setItem:(k,v)=>queue(String(v)),removeItem:()=>queue(JSON.stringify(window.NK.initial()))};
function download(name,text,type='application/json'){const u=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),10000);}
function showGate(mode='login',message=''){
 gate.hidden=false;$('#app').hidden=true;
 gate.innerHTML=`<div class="gate-card"><div class="gate-symbol">N<span>+</span></div><p class="eyebrow">DEIN PRIVATER NÄHRSTOFF-KOMPASS</p><h1>${mode==='setup'?'Euren Bereich aktivieren.':'Willkommen zurück.'}</h1><p class="sub">${mode==='setup'?'Nur mit deinem persönlichen Aktivierungslink. Danach meldet ihr euch mit eurem gemeinsamen Passwort an.':'Eure Gerichte, eure Routinen. Ein gemeinsamer Zugang – getrennte persönliche Profile.'}</p><form id="gate-form"><div class="field"><label for="gate-password">${mode==='setup'?'Gemeinsames Passwort festlegen':'Passwort'}</label><input id="gate-password" type="password" required minlength="4" maxlength="72" autocomplete="${mode==='setup'?'new-password':'current-password'}"></div>${mode==='setup'?'<div class="field"><label for="gate-confirm">Passwort wiederholen</label><input id="gate-confirm" type="password" required autocomplete="new-password"></div><div class="form-grid"><div class="field"><label for="first-name">Erstes Profil</label><input id="first-name" value="Patricia" maxlength="60" required></div><div class="field"><label for="second-name">Zweites Profil</label><input id="second-name" value="Dimitri" maxlength="60" required></div></div><p class="small">Eine längere Passphrase ist deutlich schwerer zu erraten als eine vierstellige PIN. Das Passwort kann später im Profilmenü geändert werden.</p>':'<label class="check"><input id="remember-session" type="checkbox"> Auf diesem privaten Gerät 7 Tage angemeldet bleiben</label>'}<p id="gate-error" class="error" role="alert">${E(message)}</p><button class="button wide" type="submit">${mode==='setup'?'Privaten Bereich aktivieren':'Anmelden'}</button></form><p class="tiny spaced">Persönliche Einträge werden geschützt bei Supabase gespeichert, nicht öffentlich auf GitHub. Fotos werden lokal auf deinem Gerät ausgelesen. Wer das gemeinsame Passwort kennt, kann alle Haushaltsprofile öffnen.</p><button type="button" class="muted-link" data-nk="install">Web-App installieren</button><span class="tiny"> · Version 1.3.0</span></div>`;
 $('#gate-form').addEventListener('submit',async e=>{e.preventDefault();e.stopPropagation();const b=e.currentTarget.querySelector('button[type=submit]');b.disabled=true;$('#gate-error').textContent='';const password=$('#gate-password').value;try{
  if(mode==='setup'){if(password!==$('#gate-confirm').value)throw Error('Die Passwörter stimmen nicht überein.');await api('setup',{activation,password,names:[$('#first-name').value.trim(),$('#second-name').value.trim()]});activation=null;showGate('login','Aktiviert. Bitte mit eurem Passwort anmelden.');return;}
  const remember=$('#remember-session').checked,r=await api('login',{password,remember});auth={token:r.token,expires:r.expires};const k=await api('key',{},BASE+'nutrient-device-key');auth.key=k.key;cryptoKey=await importKey(k.key);saveSession(remember);await afterLogin();
 }catch(err){const n=$('#gate-error');if(n)n.textContent=err.message+(err.retry?' Sperre: ungefähr '+Math.ceil(err.retry/60)+' Minuten.':'');}finally{b.disabled=false;}});
}
async function afterLogin(){
 profiles=(await api('profiles')).profiles;
 // Live pending state is newer than an asynchronous disk snapshot on reauthentication.
 if(current&&pending){gate.hidden=true;$('#app').hidden=false;await flush();return;}
 let cached;try{cached=await readCache();}catch(e){showGate('login',e.message);return;}
 if(cached?.pending&&profiles.some(p=>p.id===cached.id)){
  const server=(await api('get',{id:cached.id})).profile;
  current={id:server.id,name:server.name,revision:cached.revision};raw=cached.raw;
  baseRaw=typeof cached.baseRaw==='string'?cached.baseRaw:null;pending=true;blocked=server.revision!==cached.revision;conflictInfo=null;
  await openApp();flush().catch(()=>{if(blocked)manager(false,'Deine lokalen Einträge sind erhalten. Bitte Änderungskonflikt prüfen.');});return;
 }
 const id=window.NK_DEVICE?.preferred(profiles,localStorage.getItem(LAST));if(id)await choose(id);else manager(true);
}
async function openApp(){
 gate.hidden=true;$('#app').hidden=false;if(!started){await new Promise((resolve,reject)=>{const s=document.createElement('script');s.src='app.js?v=1.3.0';s.onload=resolve;s.onerror=()=>reject(Error('App konnte nicht geladen werden. Bitte erneut laden.'));document.body.append(s);});started=true;}else window.NK_APP.loadState(JSON.parse(raw));
 setStatus(blocked?'Änderungskonflikt · bitte prüfen':pending?'Noch nicht synchronisiert':'Synchronisiert');document.dispatchEvent(new Event('nk-profile-loaded'));
}
async function choose(id){
 if(window.NK_APP&&!window.NK_APP.canSwitch())return;
 if(pending)await flush();const p=(await api('get',{id})).profile;
 current=p;raw=JSON.stringify(window.NK.validateState(p.state,window.NK_DATA.nutrients.map(n=>n.key)));baseRaw=raw;pending=false;blocked=false;conflictInfo=null;safeStore(localStorage,LAST,p.id);await cacheState().catch(()=>{});dlg.close();await openApp();
}
function manager(first=false,message=''){
 if(!auth){showGate();return;}
 dlg.innerHTML=`<div class="modal-head"><h2>${first?'Wer nutzt den Kompass?':'Euer privater Bereich'}</h2>${first?'':'<button type="button" class="icon-btn" data-nk="close" aria-label="Schliessen">×</button>'}</div><p class="small">Persönliche Tagebücher und Ziele bleiben getrennt. Eigene Produkte und Gerichte sind für alle Profile eures privaten Bereichs nutzbar. Die Profile sind keine voneinander abgeschotteten Konten.</p><div class="profile-grid">${profiles.map(p=>`<button type="button" class="profile-choice ${current?.id===p.id?'selected':''}" data-nk="choose" data-id="${p.id}"><span class="avatar">${E(p.name.slice(0,1).toUpperCase())}</span><b>${E(p.name)}</b><small>${current?.id===p.id?'Aktuelles Profil':'Profil öffnen'}</small></button>`).join('')}</div><p class="small" data-nk-status>${E(status)}</p>${blocked?'<div class="notice"><b>Änderungskonflikt, nicht Speichermangel.</b><p>Neue Eingaben bleiben lokal erhalten. Unabhängige Einträge werden automatisch zusammengeführt; unterschiedliche Bearbeitungen desselben Eintrags müssen geprüft werden.</p><button type="button" class="button" data-nk="resolve-conflict">Änderungen abgleichen</button> <button type="button" class="button secondary" data-nk="backup-conflict">Beide Fassungen sichern</button></div>':''}<p class="error" id="household-error">${E(message)}</p><div class="actions wrap">${current?'<button class="button secondary" data-nk="sync">Jetzt synchronisieren</button><button class="button secondary" data-nk="backup-current">Lokale Fassung sichern</button><button class="button secondary" data-nk="rename">Profil umbenennen</button>':''}<button class="button secondary" data-nk="add">Profil hinzufügen</button><button class="button secondary" data-nk="backup-all">Alle Profile sichern</button><label class="button secondary" for="household-import">Haushalt wiederherstellen<input id="household-import" type="file" accept=".json,application/json" hidden></label><button class="button secondary" data-nk="password">Passwort ändern</button><button class="button secondary" data-nk="install">Installieren</button>${current?'<button class="button ghost" data-nk="delete">Aktuelles Profil löschen</button>':''}<button class="button ghost" data-nk="logout">Abmelden und Gerät sperren</button></div>`;
 if(!dlg.open)dlg.showModal();
 const imp=$('#household-import');if(imp)imp.onchange=restoreHousehold;
}
async function restoreHousehold(e){const file=e.target.files[0];e.target.value='';if(!file)return;try{if(file.size>20*1024*1024)throw Error('Datei zu gross.');const b=JSON.parse(await file.text());if(b.format!=='nk-household'||b.version!==1||!Array.isArray(b.profiles)||!b.profiles.length)throw Error('Keine gültige Haushaltssicherung.');const validated=b.profiles.map(p=>({name:String(p.name).slice(0,40)+' · wiederhergestellt',state:window.NK.validateState(p.state,window.NK_DATA.nutrients.map(n=>n.key))}));const existing=(await api('profiles')).profiles;if(validated.length+existing.length>8)throw Error('Maximal 8 Profile. Vor dem Wiederherstellen gegebenenfalls ein nicht benötigtes Profil löschen.');if(!confirm(validated.length+' zusätzliche Profile aus der Sicherung erstellen? Bestehende Profile bleiben unverändert.'))return;await flush();for(const p of validated){const created=(await api('create',{name:p.name})).profile;await api('save',{id:created.id,revision:created.revision,state:p.state});}profiles=(await api('profiles')).profiles;manager(false,'Sicherung als zusätzliche Profile wiederhergestellt.');}catch(err){const n=$('#household-error');if(n)n.textContent='Wiederherstellung: '+err.message;}}
function install(){alert('Android: Seite in Chrome öffnen → Menü → «App installieren» oder «Zum Startbildschirm hinzufügen».\n\niPhone: In Safari öffnen → Teilen → «Zum Home-Bildschirm» → als Web-App öffnen.\n\nDie erste Anmeldung und Synchronisierung benötigen Internet. Nach erfolgreicher Anmeldung bleibt das geöffnete Tagebuch bei kurzem Verbindungsabbruch nutzbar; Änderungen werden verschlüsselt zwischengespeichert.');}
function conflictSummary(v){if(v===undefined)return 'Auf dieser Seite gelöscht';if(v===null)return 'Leer';if(typeof v!=='object')return String(v);return JSON.stringify(v,null,2);}
async function resolveDialog(){
 if(!current)return;
 if(!blocked){manager(false,'Kein Änderungskonflikt.');return;}
 if(await reconcile()){await flush();manager(false,'Änderungen zusammengeführt und synchronisiert.');return;}
 const info=conflictInfo;
 dlg.innerHTML=`<div class="modal-head"><h2>Änderungen abgleichen</h2><button type="button" class="icon-btn" data-nk="manager" aria-label="Zurück">×</button></div><p>Unabhängige Einträge werden zusammengeführt. Nur bei den folgenden Unterschieden musst du wählen. Es wird nichts automatisch doppelt ins Tagebuch eingetragen.</p><button class="button secondary" type="button" data-nk="backup-conflict">Beide Fassungen sichern</button><form id="conflict-form">${info.conflicts.map((c,i)=>`<section class="conflict-row"><h3>${E(c.label)}</h3><div class="form-grid"><details><summary>Dieses Gerät</summary><pre>${E(conflictSummary(c.local))}</pre></details><details><summary>Server / anderes Gerät</summary><pre>${E(conflictSummary(c.server))}</pre></details></div><label for="conflict-${i}">Zu übernehmende Fassung</label><select id="conflict-${i}" required><option value="">Bitte auswählen</option><option value="local">Dieses Gerät</option><option value="server">Server / anderes Gerät</option></select></section>`).join('')}<p id="household-error" class="error" role="alert"></p><button type="submit" class="button wide">Auswahl übernehmen und synchronisieren</button></form>`;
 if(!dlg.open)dlg.showModal();
 $('#conflict-form').onsubmit=async e=>{e.preventDefault();e.stopPropagation();const button=e.currentTarget.querySelector('[type=submit]');button.disabled=true;try{
  if(raw!==info.localRaw)throw Error('Die lokalen Daten haben sich geändert. Bitte den Abgleich erneut öffnen.');
  const choices={};info.conflicts.forEach((c,i)=>{const v=$('#conflict-'+i).value;if(!['local','server'].includes(v))throw Error('Bitte für jeden Unterschied eine Fassung wählen.');choices[c.id]=v;});
  const latest=(await api('get',{id:current.id})).profile;
  if(latest.revision!==info.revision)throw Error('Der Server wurde inzwischen geändert. Bitte den Abgleich erneut öffnen.');
  const result=window.NK_MERGE.merge(baseRaw?JSON.parse(baseRaw):null,JSON.parse(raw),info.remote,choices);
  if(result.conflicts.length)throw Error('Noch nicht alle Unterschiede sind geklärt.');
  // Preserve both originals before applying a choice. Download is user-initiated by this action.
  download('Kompass-Abgleich-'+window.NK.dateKey()+'.json',JSON.stringify({format:'nk-conflict-backup',profileId:current.id,local:JSON.parse(raw),server:info.remote},null,2));
  raw=JSON.stringify(window.NK.validateState(result.state,window.NK_DATA.nutrients.map(n=>n.key)));
  baseRaw=JSON.stringify(info.remote);current.revision=info.revision;blocked=false;conflictInfo=null;pending=true;
  await cacheState().catch(()=>{});publishMerged();await flush();manager(false,'Änderungen zusammengeführt und synchronisiert. Die Sicherung enthält beide ursprünglichen Fassungen.');
 }catch(err){$('#household-error').textContent=err.message;}finally{button.disabled=false;}};
}

async function logout(){if(pending)await flush();await api('logout');auth=null;cryptoKey=null;current=null;raw=null;baseRaw=null;pending=false;blocked=false;conflictInfo=null;window.NK_LIBRARY?.clear();cacheSeq++;await cacheJob.catch(()=>{});sessionStorage.removeItem(SESSION);localStorage.removeItem(SESSION);localStorage.removeItem(CACHE);window.NK_APP?.clearState();dlg.close();showGate();}
document.addEventListener('click',async e=>{const b=e.target.closest('[data-nk]');if(!b)return;e.preventDefault();e.stopPropagation();const a=b.dataset.nk;try{
 if(a==='install'){install();return;}
 if(a==='manager'){profiles=(await api('profiles')).profiles;manager();return;}
 if(a==='close'){dlg.close();return;}
 if(a==='choose'){await choose(b.dataset.id);return;}
 if(a==='sync'){await flush();await window.NK_LIBRARY?.refresh(true);manager(false,'Synchronisiert.');return;}
 if(a==='resolve-conflict'){await resolveDialog();return;}
 if(a==='backup-conflict'){const server=(await api('get',{id:current.id})).profile;download('Kompass-Abgleich-'+window.NK.dateKey()+'.json',JSON.stringify({format:'nk-conflict-backup',profileId:current.id,local:JSON.parse(raw),server:server.state},null,2));return;}
 if(a==='backup-current'){download('Kompass-lokale-Fassung.json',raw||'{}');return;}
 if(a==='reload-server'){if(!confirm('Lokale Fassung zuerst gesichert? Ungesendete Änderungen werden durch die Serverfassung ersetzt.'))return;pending=false;blocked=false;await choose(current.id);return;}
 if(a==='add'){const name=prompt('Name des neuen Profils:');if(!name?.trim())return;await flush();const r=await api('create',{name});profiles=(await api('profiles')).profiles;await choose(r.profile.id);return;}
 if(a==='rename'){const name=prompt('Neuer Profilname:',current.name);if(!name?.trim())return;await api('rename',{id:current.id,name});current.name=name.trim();profiles=(await api('profiles')).profiles;window.NK_APP?.refresh();manager();return;}
 if(a==='delete'){if(!confirm('Profil «'+current.name+'» mit allen Einträgen endgültig löschen? Zuerst eine Sicherung erstellen.'))return;await flush();await api('delete',{id:current.id});localStorage.removeItem(CACHE);current=null;raw=null;profiles=(await api('profiles')).profiles;await choose(profiles[0].id);return;}
 if(a==='backup-all'){await flush();const list=(await api('profiles')).profiles,all=[];for(const p of list)all.push((await api('get',{id:p.id})).profile);download('Kompass-Haushalt-'+window.NK.dateKey()+'.json',JSON.stringify({format:'nk-household',version:1,profiles:all},null,2));manager(false,'Sicherung erstellt. Zum Wiederherstellen kann eine einzelne Profil-Sicherung im Bereich Profil importiert werden; Haushaltsdatei über «Haushalt wiederherstellen».');return;}
 if(a==='password'){dlg.innerHTML='<div class="modal-head"><h2>Gemeinsames Passwort ändern</h2><button class="icon-btn" data-nk="manager">×</button></div><form id="change-password"><div class="field"><label for="old-pass">Bisheriges Passwort</label><input id="old-pass" type="password" autocomplete="current-password" required></div><div class="field"><label for="new-pass">Neues Passwort · mindestens 8 Zeichen</label><input id="new-pass" type="password" minlength="8" autocomplete="new-password" required></div><div class="field"><label for="again-pass">Neues Passwort wiederholen</label><input id="again-pass" type="password" autocomplete="new-password" required></div><p>Andere Geräte werden abgemeldet. Dies betrifft alle Haushaltsprofile.</p><p id="household-error" class="error"></p><button class="button" type="submit">Passwort ändern</button></form>';$('#change-password').onsubmit=async ev=>{ev.preventDefault();ev.stopPropagation();try{if($('#new-pass').value!==$('#again-pass').value)throw Error('Passwörter stimmen nicht überein.');await api('password',{old:$('#old-pass').value,next:$('#new-pass').value});manager(false,'Passwort geändert. Andere Geräte müssen sich erneut anmelden.');}catch(er){$('#household-error').textContent=er.message;}};return;}
 if(a==='logout'){await logout();return;}
 }catch(err){const out=$('#household-error');if(out)out.textContent=err.message;else alert(err.message);}});
window.addEventListener('online',()=>{if(auth&&pending&&!blocked)flush().catch(()=>{});});
window.addEventListener('beforeunload',e=>{if(pending){e.preventDefault();e.returnValue='Änderungen sind noch nicht synchronisiert.';}});
async function protectForReload(){
 if(!current||!pending)return true;
 await cacheState();const saved=await readCache();
 if(!saved||saved.id!==current.id||saved.raw!==raw||saved.pending!==pending)throw Error('Die letzten Änderungen konnten noch nicht sicher zwischengespeichert werden. Bitte exportieren.');
 return true;
}
window.NK_HOUSEHOLD={api,flush,protectForReload,manager,get id(){return current?.id||'';},get authenticated(){return !!auth;},get name(){return current?.name||'';},get status(){return status;},get pending(){return pending;},get conflicted(){return blocked;},install};
async function boot(){
 if(activation){showGate('setup');return;}
 try{const saved=sessionStorage.getItem(SESSION)||localStorage.getItem(SESSION);if(saved)auth=JSON.parse(saved);if(auth&&Date.parse(auth.expires)>Date.now()){
  cryptoKey=await importKey(auth.key);try{await afterLogin();return;}catch(e){if(e.status===401||e.status===403){auth=null;sessionStorage.removeItem(SESSION);localStorage.removeItem(SESSION);showGate('login','Sitzung abgelaufen. Bitte erneut anmelden. Ungesendete Änderungen bleiben verschlüsselt erhalten.');return;}const c=await readCache();if(c){current={id:c.id,name:c.name,revision:c.revision};raw=c.raw;baseRaw=c.baseRaw||null;pending=c.pending;await openApp();setStatus('Offline · zuletzt gespeicherte Fassung');return;}throw e;}
 }}catch(e){showGate('login',e.message);return;}auth=null;showGate();
}
boot();
if('serviceWorker' in navigator&&location.protocol==='https:')navigator.serviceWorker.register('./sw.js',{scope:'./',updateViaCache:'none'}).catch(()=>{});
})();
