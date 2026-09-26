/* Private household session + versioned cloud sync. No password in browser source. */
(function(){'use strict';
const BASE='https://wpmyuzpcraduhaybjvmb.supabase.co/functions/v1/',ENDPOINT=BASE+'nutrient-compass';
const SESSION='nk:session:1',CACHE='nk:encrypted-pending:1',LAST='nk:last-profile:1';
const $=s=>document.querySelector(s),E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let auth=null,current=null,raw=null,baseRaw=null,conflictDetails=[],writeLock=Promise.resolve(),pending=false,busy=null,blocked=false,timer,cryptoKey=null,cacheJob=Promise.resolve(),cacheSeq=0,status='Nicht angemeldet',started=false,profiles=[],activation=new URLSearchParams(location.hash.slice(1)).get('activate');
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
function locked(fn){const result=writeLock.then(fn);writeLock=result.catch(()=>{});return result;}
async function cacheState(){
 if(!current||!cryptoKey)return;
 const seq=++cacheSeq,record={id:current.id,name:current.name,revision:current.revision,raw,baseRaw,pending};
 cacheJob=(async()=>{const iv=crypto.getRandomValues(new Uint8Array(12));const cipher=await crypto.subtle.encrypt({name:'AES-GCM',iv},cryptoKey,new TextEncoder().encode(JSON.stringify(record)));if(seq===cacheSeq)await window.NK_SAFE_CACHE.write(CACHE,JSON.stringify({iv:b64(iv),data:b64(new Uint8Array(cipher)),savedAt:Date.now()}));})();return cacheJob;
}
async function readCache(){const s=await window.NK_SAFE_CACHE.read(CACHE);if(!s)return null;try{const c=JSON.parse(s);return JSON.parse(new TextDecoder().decode(await crypto.subtle.decrypt({name:'AES-GCM',iv:bytes(c.iv)},cryptoKey,bytes(c.data))));}catch{throw Error('Die lokale Sicherung konnte nicht entschlüsselt werden. Sie bleibt unverändert.');}}
function checked(s){return window.NK.validateState(s,window.NK_DATA.nutrients.map(n=>n.key));}
function syncView(){window.NK_APP?.acceptSyncState(JSON.parse(raw));}
async function reconcile(choice){
 const p=(await api('get',{id:current.id})).profile,remote=checked(p.state),local=checked(JSON.parse(raw));
 if(window.NK_SYNC.equal(local,remote)){raw=JSON.stringify(remote);baseRaw=raw;current.revision=p.revision;pending=false;blocked=false;conflictDetails=[];await cacheState().catch(()=>{});syncView();return true;}
 const result=window.NK_SYNC.merge(baseRaw?checked(JSON.parse(baseRaw)):null,local,remote,choice);
 if(result.conflicts.length&&!choice){blocked=true;conflictDetails=result.conflicts;setStatus('Lokal gesichert · gleichzeitige Änderungen bitte prüfen');await cacheState().catch(()=>{});return false;}
 raw=JSON.stringify(checked(result.state));baseRaw=JSON.stringify(remote);current.revision=p.revision;blocked=false;conflictDetails=[];pending=!window.NK_SYNC.equal(result.state,remote);await cacheState().catch(()=>{});syncView();return true;
}
async function syncNow(choice){
 if(!current||!pending)return true;
 if(blocked&&!await reconcile(choice)){const e=Error('Gleichzeitige Änderungen an denselben Daten. Neue Eingaben bleiben lokal gespeichert. Bitte «Profile & Sync» öffnen und den Abgleich prüfen.');e.code='SYNC_CONFLICT';throw e;}
 for(let attempts=0;pending&&current&&attempts<4;attempts++){
  const captured=raw;setStatus('Wird synchronisiert …');
  try{const r=await api('save',{id:current.id,revision:current.revision,state:JSON.parse(captured)});current.revision=r.revision;baseRaw=captured;pending=raw!==captured;blocked=false;await cacheState().catch(()=>{});setStatus(pending?'Weitere Änderungen …':'Synchronisiert');document.dispatchEvent(new Event('nk-synced'));}
  catch(e){
   if(e.conflict){if(await reconcile(choice))continue;e.code='SYNC_CONFLICT';e.message='Gleichzeitige Änderungen bitte über «Profile & Sync» prüfen. Deine Eingaben bleiben erhalten.';}
   else setStatus(e.status===401?'Sitzung abgelaufen · lokal gespeichert, bitte anmelden':'Lokal gespeichert · Verbindung für Synchronisierung nötig');
   await cacheState().catch(()=>setStatus('Nicht dauerhaft gesichert! Bitte Profil exportieren.'));throw e;
  }
 }
 if(pending)throw Error('Weitere Änderungen auf einem anderen Gerät. Bitte erneut synchronisieren.');return true;
}
async function flush(choice){clearTimeout(timer);if(busy)return busy;busy=locked(()=>syncNow(choice));try{return await busy;}finally{busy=null;}}
async function queue(value,expected){return locked(async()=>{
 if(!auth||!current)throw Error('Bitte zuerst anmelden und ein Profil wählen.');
 if(value.length>3900000)throw Error('Dieses Profil überschreitet die zulässige Datengrösse. Bitte zuerst exportieren; es wurde nichts gelöscht.');
 let next=checked(JSON.parse(value));
 // A completed background sync may have brought in another device's additions.
 if(expected&&raw&&!window.NK_SYNC.equal(JSON.parse(expected),JSON.parse(raw))){const result=window.NK_SYNC.merge(checked(JSON.parse(expected)),next,checked(JSON.parse(raw)));next=checked(result.state);if(result.conflicts.length){blocked=true;conflictDetails=result.conflicts;}}
 raw=JSON.stringify(next);pending=true;setStatus('Wird lokal gesichert …');
 try{await cacheState();setStatus(blocked?'Lokal gespeichert · Abgleich prüfen':'Lokal gespeichert · Synchronisierung …');}
 catch(cacheError){try{await syncNow();setStatus('Auf Server gespeichert · lokale Sicherung nicht verfügbar');}catch(serverError){serverError.message='Noch nicht dauerhaft gespeichert: Lokale Sicherung und Serverabgleich sind derzeit nicht verfügbar. Eingabe offen lassen und erneut versuchen. '+serverError.message;serverError.bufferedRaw=raw;throw serverError;}}
 clearTimeout(timer);if(pending)timer=setTimeout(()=>flush().catch(()=>{}),350);return raw;
 });}
window.NK_STORE={getItem:()=>raw,setItem:(k,v,expected)=>queue(String(v),expected),removeItem:()=>queue(JSON.stringify(window.NK.initial()))};
function download(name,text,type='application/json'){const u=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),10000);}
function showGate(mode='login',message=''){
 gate.hidden=false;$('#app').hidden=true;
 gate.innerHTML=`<div class="gate-card"><div class="gate-symbol">N<span>+</span></div><p class="eyebrow">DEIN PRIVATER NÄHRSTOFF-KOMPASS</p><h1>${mode==='setup'?'Euren Bereich aktivieren.':'Willkommen zurück.'}</h1><p class="sub">${mode==='setup'?'Nur mit deinem persönlichen Aktivierungslink. Danach meldet ihr euch mit eurem gemeinsamen Passwort an.':'Eure Gerichte, eure Routinen. Ein gemeinsamer Zugang – getrennte persönliche Profile.'}</p><form id="gate-form"><div class="field"><label for="gate-password">${mode==='setup'?'Gemeinsames Passwort festlegen':'Passwort'}</label><input id="gate-password" type="password" required minlength="4" maxlength="72" autocomplete="${mode==='setup'?'new-password':'current-password'}"></div>${mode==='setup'?'<div class="field"><label for="gate-confirm">Passwort wiederholen</label><input id="gate-confirm" type="password" required autocomplete="new-password"></div><div class="form-grid"><div class="field"><label for="first-name">Erstes Profil</label><input id="first-name" value="Patricia" maxlength="60" required></div><div class="field"><label for="second-name">Zweites Profil</label><input id="second-name" value="Dimitri" maxlength="60" required></div></div><p class="small">Eine längere Passphrase ist deutlich schwerer zu erraten als eine vierstellige PIN. Das Passwort kann später im Profilmenü geändert werden.</p>':'<label class="check"><input id="remember-session" type="checkbox"> Auf diesem privaten Gerät 7 Tage angemeldet bleiben</label>'}<p id="gate-error" class="error" role="alert">${E(message)}</p><button class="button wide" type="submit">${mode==='setup'?'Privaten Bereich aktivieren':'Anmelden'}</button></form><p class="tiny spaced">Persönliche Einträge werden geschützt bei Supabase gespeichert, nicht öffentlich auf GitHub. Fotos werden lokal auf deinem Gerät ausgelesen. Wer das gemeinsame Passwort kennt, kann alle Haushaltsprofile öffnen.</p><button type="button" class="muted-link" data-nk="install">Web-App installieren</button><span class="tiny"> · Version 1.4.0</span></div>`;
 $('#gate-form').addEventListener('submit',async e=>{e.preventDefault();e.stopPropagation();const b=e.currentTarget.querySelector('button[type=submit]');b.disabled=true;$('#gate-error').textContent='';const password=$('#gate-password').value;try{
  if(mode==='setup'){if(password!==$('#gate-confirm').value)throw Error('Die Passwörter stimmen nicht überein.');await api('setup',{activation,password,names:[$('#first-name').value.trim(),$('#second-name').value.trim()]});activation=null;showGate('login','Aktiviert. Bitte mit eurem Passwort anmelden.');return;}
  const remember=$('#remember-session').checked,r=await api('login',{password,remember});auth={token:r.token,expires:r.expires};const k=await api('key',{},BASE+'nutrient-device-key');auth.key=k.key;cryptoKey=await importKey(k.key);saveSession(remember);await afterLogin();
 }catch(err){const n=$('#gate-error');if(n)n.textContent=err.message+(err.retry?' Sperre: ungefähr '+Math.ceil(err.retry/60)+' Minuten.':'');}finally{b.disabled=false;}});
}
async function afterLogin(){
 profiles=(await api('profiles')).profiles;
 let cached;try{cached=await readCache();}catch(e){showGate('login',e.message);return;}
 if(cached?.pending&&profiles.some(p=>p.id===cached.id)){
  current={id:cached.id,name:cached.name,revision:cached.revision};raw=cached.raw;baseRaw=cached.baseRaw||null;pending=true;blocked=false;
  await reconcile();await openApp();if(blocked)manager(false,'Lokale Eingaben bleiben erhalten. Unabhängige Ergänzungen werden automatisch zusammengeführt; dieselben geänderten Werte brauchen deine Auswahl.');else flush().catch(()=>{});return;
 }
 if(current&&pending){await flush();return;}
 const id=window.NK_DEVICE.preferred(profiles,localStorage.getItem(LAST));if(id)await choose(id);else manager(true);
}
async function openApp(){
 gate.hidden=true;$('#app').hidden=false;if(!started){await new Promise((resolve,reject)=>{const s=document.createElement('script');s.src='app.js?v=1.4.0';s.onload=resolve;s.onerror=()=>reject(Error('App konnte nicht geladen werden. Bitte erneut laden.'));document.body.append(s);});started=true;}else window.NK_APP.loadState(JSON.parse(raw));
 setStatus(blocked?'Lokal gespeichert · Abgleich prüfen':pending?'Noch nicht synchronisiert':'Synchronisiert');document.dispatchEvent(new Event('nk-profile-loaded'));
}
async function choose(id){
 if(window.NK_APP&&!window.NK_APP.canSwitch())return;
 if(pending)await flush();const p=(await api('get',{id})).profile;
 current=p;raw=JSON.stringify(checked(p.state));baseRaw=raw;pending=false;blocked=false;conflictDetails=[];safeStore(localStorage,LAST,p.id);await cacheState().catch(()=>{});dlg.close();await openApp();
}
function manager(first=false,message=''){
 if(!auth){showGate();return;}
 dlg.innerHTML=`<div class="modal-head"><h2>${first?'Wer nutzt den Kompass?':'Euer privater Bereich'}</h2>${first?'':'<button type="button" class="icon-btn" data-nk="close" aria-label="Schliessen">×</button>'}</div><p class="small">Gemeinsame Produkte und Gerichte, getrennte Tagebücher und persönliche Ziele. Das gemeinsame Passwort öffnet alle Haushaltsprofile.</p><div class="profile-grid">${profiles.map(p=>`<button type="button" class="profile-choice ${current?.id===p.id?'selected':''}" data-nk="choose" data-id="${p.id}"><span class="avatar">${E(p.name.slice(0,1).toUpperCase())}</span><b>${E(p.name)}</b><small>${current?.id===p.id?'Aktuelles Profil':'Profil öffnen'}</small></button>`).join('')}</div><p class="small" data-nk-status>${E(status)}</p>${blocked?'<div class="notice"><b>Gleichzeitige Änderungen erkannt</b><p>Neue Produkte und Mahlzeiten können weiter lokal gespeichert werden. Unabhängige Änderungen werden zusammengeführt. Bei tatsächlich widersprüchlichen Änderungen entscheidest du, welche Fassung dieser Werte gilt. Andere Einträge bleiben erhalten.</p><button class="button secondary" data-nk="backup-both">Beide Fassungen sichern</button><button class="button secondary" data-nk="merge-local">Konflikte: dieses Gerät bevorzugen</button><button class="button secondary" data-nk="merge-server">Konflikte: Server bevorzugen</button><button class="button secondary" data-nk="sync">Abgleich erneut prüfen</button></div>':''}<p class="error" id="household-error">${E(message)}</p><div class="actions wrap">${current?'<button class="button secondary" data-nk="sync">Jetzt synchronisieren</button><button class="button secondary" data-nk="rename">Profil umbenennen</button>':''}<button class="button secondary" data-nk="add">Profil hinzufügen</button><button class="button secondary" data-nk="backup-all">Alle Profile sichern</button><label class="button secondary" for="household-import">Haushalt wiederherstellen<input id="household-import" type="file" accept=".json,application/json" hidden></label><button class="button secondary" data-nk="password">Passwort ändern</button><button class="button secondary" data-nk="install">Installieren</button>${current?'<button class="button ghost" data-nk="delete">Aktuelles Profil löschen</button>':''}<button class="button ghost" data-nk="logout">Abmelden und Gerät sperren</button></div>`;
 if(!dlg.open)dlg.showModal();
 const imp=$('#household-import');if(imp)imp.onchange=restoreHousehold;
}
async function restoreHousehold(e){const file=e.target.files[0];e.target.value='';if(!file)return;try{if(file.size>20*1024*1024)throw Error('Datei zu gross.');const b=JSON.parse(await file.text());if(b.format!=='nk-household'||b.version!==1||!Array.isArray(b.profiles)||!b.profiles.length)throw Error('Keine gültige Haushaltssicherung.');const validated=b.profiles.map(p=>({name:String(p.name).slice(0,40)+' · wiederhergestellt',state:window.NK.validateState(p.state,window.NK_DATA.nutrients.map(n=>n.key))}));const existing=(await api('profiles')).profiles;if(validated.length+existing.length>8)throw Error('Maximal 8 Profile. Vor dem Wiederherstellen gegebenenfalls ein nicht benötigtes Profil löschen.');if(!confirm(validated.length+' zusätzliche Profile aus der Sicherung erstellen? Bestehende Profile bleiben unverändert.'))return;await flush();for(const p of validated){const created=(await api('create',{name:p.name})).profile;await api('save',{id:created.id,revision:created.revision,state:p.state});}profiles=(await api('profiles')).profiles;manager(false,'Sicherung als zusätzliche Profile wiederhergestellt.');}catch(err){const n=$('#household-error');if(n)n.textContent='Wiederherstellung: '+err.message;}}
function install(){alert('Android: Seite in Chrome öffnen → Menü → «App installieren» oder «Zum Startbildschirm hinzufügen».\n\niPhone: In Safari öffnen → Teilen → «Zum Home-Bildschirm» → als Web-App öffnen.\n\nDie erste Anmeldung und Synchronisierung benötigen Internet. Nach erfolgreicher Anmeldung bleibt das geöffnete Tagebuch bei kurzem Verbindungsabbruch nutzbar; Änderungen werden verschlüsselt zwischengespeichert.');}
async function logout(){if(pending)await flush();await api('logout');auth=null;cryptoKey=null;current=null;raw=null;baseRaw=null;pending=false;blocked=false;cacheSeq++;await cacheJob.catch(()=>{});sessionStorage.removeItem(SESSION);localStorage.removeItem(SESSION);await window.NK_SAFE_CACHE.remove(CACHE);window.NK_SHARED?.clear();window.NK_APP?.clearState();dlg.close();showGate();}
document.addEventListener('click',async e=>{const b=e.target.closest('[data-nk]');if(!b)return;e.preventDefault();e.stopPropagation();const a=b.dataset.nk;try{
 if(a==='install'){install();return;}
 if(a==='manager'){try{profiles=(await api('profiles')).profiles;manager();}catch(e){if(e.status===401){if(!window.NK_APP||window.NK_APP.canSwitch())showGate('login','Sitzung abgelaufen. Bitte erneut anmelden. Lokal gesicherte Einträge bleiben erhalten.');}else manager(false,'Profilabfrage derzeit nicht möglich. Lokale Einträge bleiben erhalten.');}return;}
 if(a==='close'){dlg.close();return;}
 if(a==='choose'){await choose(b.dataset.id);return;}
 if(a==='sync'){await flush();manager(false,'Synchronisiert.');return;}
 if(a==='merge-local'||a==='merge-server'){if(!confirm('Nur bei widersprüchlichen Änderungen '+(a==='merge-local'?'diese Gerätefassung':'die Serverfassung')+' verwenden? Unabhängige Ergänzungen beider Seiten bleiben bestehen. Vorher kannst du beide Fassungen sichern.'))return;await flush(a==='merge-local'?'local':'server');manager(false,'Abgleich abgeschlossen.');return;}
 if(a==='backup-both'){const server=(await api('get',{id:current.id})).profile;download('Kompass-Abgleich-beide-Fassungen.json',JSON.stringify({format:'nk-sync-recovery',local:JSON.parse(raw),server:server.state},null,2));return;}
 if(a==='backup-current'){download('Kompass-lokale-Fassung.json',raw||'{}');return;}
 if(a==='reload-server'){if(!confirm('Lokale Fassung zuerst gesichert? Ungesendete Änderungen werden durch die Serverfassung ersetzt.'))return;pending=false;blocked=false;await choose(current.id);return;}
 if(a==='add'){const name=prompt('Name des neuen Profils:');if(!name?.trim())return;await flush();const r=await api('create',{name});profiles=(await api('profiles')).profiles;await choose(r.profile.id);return;}
 if(a==='rename'){const name=prompt('Neuer Profilname:',current.name);if(!name?.trim())return;await api('rename',{id:current.id,name});current.name=name.trim();profiles=(await api('profiles')).profiles;window.NK_APP?.refresh();manager();return;}
 if(a==='delete'){if(!confirm('Profil «'+current.name+'» mit allen Einträgen endgültig löschen? Zuerst eine Sicherung erstellen.'))return;await flush();await api('delete',{id:current.id});await window.NK_SAFE_CACHE.remove(CACHE);current=null;raw=null;baseRaw=null;profiles=(await api('profiles')).profiles;await choose(profiles[0].id);return;}
 if(a==='backup-all'){await flush();const list=(await api('profiles')).profiles,all=[];for(const p of list)all.push((await api('get',{id:p.id})).profile);download('Kompass-Haushalt-'+window.NK.dateKey()+'.json',JSON.stringify({format:'nk-household',version:1,profiles:all},null,2));manager(false,'Sicherung erstellt. Zum Wiederherstellen kann eine einzelne Profil-Sicherung im Bereich Profil importiert werden; Haushaltsdatei über «Haushalt wiederherstellen».');return;}
 if(a==='password'){dlg.innerHTML='<div class="modal-head"><h2>Gemeinsames Passwort ändern</h2><button class="icon-btn" data-nk="manager">×</button></div><form id="change-password"><div class="field"><label for="old-pass">Bisheriges Passwort</label><input id="old-pass" type="password" autocomplete="current-password" required></div><div class="field"><label for="new-pass">Neues Passwort · mindestens 8 Zeichen</label><input id="new-pass" type="password" minlength="8" autocomplete="new-password" required></div><div class="field"><label for="again-pass">Neues Passwort wiederholen</label><input id="again-pass" type="password" autocomplete="new-password" required></div><p>Andere Geräte werden abgemeldet. Dies betrifft alle Haushaltsprofile.</p><p id="household-error" class="error"></p><button class="button" type="submit">Passwort ändern</button></form>';$('#change-password').onsubmit=async ev=>{ev.preventDefault();ev.stopPropagation();try{if($('#new-pass').value!==$('#again-pass').value)throw Error('Passwörter stimmen nicht überein.');await api('password',{old:$('#old-pass').value,next:$('#new-pass').value});manager(false,'Passwort geändert. Andere Geräte müssen sich erneut anmelden.');}catch(er){$('#household-error').textContent=er.message;}};return;}
 if(a==='logout'){await logout();return;}
 }catch(err){const out=$('#household-error');if(out)out.textContent=err.message;else alert(err.message);}});
window.addEventListener('online',()=>{if(auth&&pending&&!blocked)flush().catch(()=>{});});
window.addEventListener('beforeunload',e=>{if(pending){e.preventDefault();e.returnValue='Änderungen sind noch nicht synchronisiert.';}});
window.NK_HOUSEHOLD={api,flush,manager,get id(){return current?.id||'';},get name(){return current?.name||'';},get status(){return status;},get pending(){return pending;},get authenticated(){return !!auth;},get blocked(){return blocked;},install};
async function boot(){
 if(activation){showGate('setup');return;}
 try{const saved=sessionStorage.getItem(SESSION)||localStorage.getItem(SESSION);if(saved)auth=JSON.parse(saved);if(auth&&Date.parse(auth.expires)>Date.now()){
  cryptoKey=await importKey(auth.key);try{await afterLogin();return;}catch(e){if(e.status===401||e.status===403){auth=null;sessionStorage.removeItem(SESSION);localStorage.removeItem(SESSION);showGate('login','Sitzung abgelaufen. Bitte erneut anmelden. Ungesendete Änderungen bleiben verschlüsselt erhalten.');return;}const c=await readCache();if(c){current={id:c.id,name:c.name,revision:c.revision};raw=c.raw;baseRaw=c.baseRaw||null;pending=c.pending;await openApp();setStatus('Offline · zuletzt gespeicherte Fassung');return;}throw e;}
 }}catch(e){showGate('login',e.message);return;}auth=null;showGate();
}
boot();
if('serviceWorker' in navigator&&location.protocol==='https:')navigator.serviceWorker.register('./sw.js',{scope:'./'}).catch(()=>{});
})();
