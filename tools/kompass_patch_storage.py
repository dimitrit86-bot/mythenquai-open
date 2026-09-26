"""Guarded storage repair; modifies application code, never personal user data."""
from pathlib import Path
import hashlib,json,sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'kompass')
def sha(name):
 b=(p/name).read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
assert sha('app.js')=='732e0b813ae7b74bdb3dda8d3d7d9e98e4b7e53c','Unexpected app base'
assert sha('household.js')=='62690337bf5168cfd32243f0d130c081088317e3','Unexpected household base'
def rep(s,a,b):
 assert s.count(a)==1,(a[:80],s.count(a));return s.replace(a,b)
s=(p/'app.js').read_text()
s=rep(s,"storageProblem='Speichern fehlgeschlagen: Der Browserspeicher ist voll oder nicht verfügbar. Bitte bestehende Daten im Profil sichern.';throw Error(storageProblem);", "storageProblem=window.NK_SAVE_GUARD.message(e);throw Error(storageProblem);")
s=rep(s,"if(el)el.innerHTML=`<div class=\"error\" role=\"alert\">${esc(text)}</div>`;", "if(el)el.innerHTML=`<div class=\"error\" role=\"alert\">${esc(text)}</div>${window.NK_HOUSEHOLD?.blocked?'<button type=\"button\" class=\"button secondary\" data-nk=\"manager\">Fassungen prüfen & sichern</button>':''}`;")
(p/'app.js').write_text(s)
s=(p/'household.js').read_text()
start=s.index('async function flush(){');end=s.index('\nfunction queue(',start)
s=s[:start]+'''async function acknowledge(captured,revision){
 current.revision=revision;pending=raw!==captured;blocked=false;
 try{await cacheState();setStatus(pending?'Weitere Änderungen …':'Synchronisiert');}
 catch{setStatus(pending?'Neue Änderungen noch nicht lokal gesichert · App offen lassen':'Synchronisiert · lokale Offline-Sicherung nicht verfügbar');}
}
async function flush(){
 clearTimeout(timer);if(busy)return busy;if(blocked)throw Error('Unterschiedliche Datenstände. Bitte über «Profile & Sync» die lokale Fassung sichern. Nicht den Browserspeicher löschen.');
 busy=(async()=>{while(pending&&current){const captured=raw,rev=current.revision;setStatus('Wird synchronisiert …');
  try{const r=await api('save',{id:current.id,revision:rev,state:JSON.parse(captured)});await acknowledge(captured,r.revision);}
  catch(e){
   if(e.conflict){
    // A response may have been lost after a successful save. Never infer success
    // from a revision alone: compare the complete validated payload first.
    try{const server=(await api('get',{id:current.id})).profile;
     if(window.NK_SAVE_GUARD.sameState(JSON.parse(captured),server.state)){
      await acknowledge(captured,server.revision);continue;
     }
    }catch{/* Keep the original pending copy; no blind overwrite or merge. */}
    blocked=true;setStatus('Unterschiedliche Datenstände · Fassungen prüfen');
   }else setStatus(e.status===401?'Erneut anmelden · Änderungen noch nicht synchronisiert':'Offline / nicht synchronisiert');
   await cacheState().catch(()=>setStatus('Nicht lokal gesichert! Bitte exportieren und App offen lassen.'));
   if(e.status===401)showGate('login','Sitzung abgelaufen. Bitte erneut anmelden. Ungesendete Änderungen werden beibehalten.');
   throw e;
  }
 }})();
 try{await busy;}finally{busy=null;}return true;
}'''+s[end:]
s=s.replace("if(blocked)throw Error('Versionskonflikt: Bitte über das Profilmenü die Fassungen prüfen.');", "if(blocked)throw Error('Unterschiedliche Datenstände: Bitte «Fassungen prüfen & sichern» öffnen. Die vorhandenen Einträge wurden nicht überschrieben.');")
start=s.index(' if(cached?.pending&&profiles.some(p=>p.id===cached.id)){');end=s.index('\n if(current&&pending)',start)
s=s[:start]+''' if(cached?.pending&&profiles.some(p=>p.id===cached.id)){
  const server=(await api('get',{id:cached.id})).profile;
  const keys=window.NK_DATA.nutrients.map(n=>n.key);
  const localState=window.NK.validateState(JSON.parse(cached.raw),keys);
  const serverState=window.NK.validateState(server.state,keys);
  const alreadySaved=window.NK_SAVE_GUARD.sameState(localState,serverState);
  current={...server,revision:alreadySaved?server.revision:cached.revision};
  raw=JSON.stringify(alreadySaved?serverState:localState);pending=!alreadySaved;
  blocked=pending&&server.revision!==cached.revision;
  await cacheState().catch(()=>{});await openApp();
  if(blocked){setStatus('Unterschiedliche Datenstände · lokale Fassung erhalten');manager();}
  else if(pending)flush().catch(()=>{});
  return;
 }'''+s[end:]
s=rep(s,"s.src='app.js';","s.src='app.js?v=1.2.2';")
s=s.replace('Version 1.0.0','Version 1.2.2')
s=rep(s,"<b>Änderung auf einem anderen Gerät erkannt.</b><p>Die lokale Fassung wurde nicht überschrieben. Sichere sie zuerst. Danach kannst du die Serverfassung laden und die Änderungen anhand der Sicherung übernehmen.</p>","<b>Unterschiedliche Datenstände erkannt.</b><p>Keine Fassung wurde überschrieben. Sichere die lokale Fassung als zusätzliches Profil, um damit weiterzuarbeiten. Das ursprüngliche Serverprofil bleibt erhalten. Alternativ kannst du zuerst eine Datei exportieren.</p><button class=\"button\" data-nk=\"preserve-local\">Lokale Fassung als neues Profil sichern</button>")
s=rep(s," if(a==='backup-current'){",''' if(a==='preserve-local'){
  if(!current||!raw)throw Error('Keine lokale Fassung vorhanden.');
  if(window.NK_APP&&!window.NK_APP.canSwitch())return;
  if(!confirm('Die gespeicherte lokale Fassung als zusätzliches Profil sichern und darin weiterarbeiten? Die ursprüngliche Serverfassung bleibt unverändert. Noch nicht übernommene Formulareingaben sind nicht Teil dieser Sicherung.'))return;
  b.disabled=true;
  try{
   const state=window.NK.validateState(JSON.parse(raw),window.NK_DATA.nutrients.map(n=>n.key));
   if((await api('profiles')).profiles.length>=8)throw Error('Maximal 8 Profile. Bitte die lokale Fassung als Datei sichern; es wurde nichts überschrieben.');
   const name=current.name.slice(0,34)+' · lokale Sicherung';
   const created=(await api('create',{name})).profile;
   const saved=await api('save',{id:created.id,revision:created.revision,state});
   // Only release the blocked copy AFTER the server confirms the new backup.
   current={id:created.id,name:created.name,revision:saved.revision};raw=JSON.stringify(state);
   pending=false;blocked=false;profiles=[...profiles.filter(p=>p.id!==created.id),current];
   let localSaved=true;try{safeStore(localStorage,LAST,current.id);await cacheState();}catch{localSaved=false;}
   dlg.close();await openApp();setStatus(localSaved?'Lokale Fassung als zusätzliches Profil gesichert':'Neues Profil auf dem Server gesichert · lokale Offline-Sicherung nicht verfügbar');
  }finally{b.disabled=false;}
  return;
 }
 if(a==='backup-current'){''')
s=rep(s,"get pending(){return pending;},install","get pending(){return pending;},get blocked(){return blocked;},install")
(p/'household.js').write_text(s)
# Bust the unversioned app.js cache as well; the public URL stays unchanged.
for name in ['index.html','device.js','sw.js','version.json']:
 s=(p/name).read_text().replace('1.2.1','1.2.2')
 if name=='index.html':
  s=s.replace('Protein-Tagesbedarf im Überblick','Speichern & Synchronisierung korrigiert')
  s=rep(s,'<script src="household.js?v=1.2.2">','<script src="save-guard.js?v=1.2.2"></script><script src="household.js?v=1.2.2">')
 if name=='sw.js':
  s=rep(s,"'scanner.js','household.js'","'scanner.js','save-guard.js','household.js'")
  s=rep(s,"'./app.js'","'./app.js?v='+VERSION")
 (p/name).write_text(s)
print('Guarded repair applied successfully.')
