/* Show new releases once per profile/version; archive access stays explicit. */
(function(root){'use strict';
 const R=root.NK_RELEASE_CORE,D=root.NK_RELEASE_DATA;if(!R||!D)return;
 try{R.validate(D);}catch(e){console.warn('Release Notes: '+e.message);return;}
 const E=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const app=document.getElementById('app'),prefix='nk:release-shown:1:',shown=new Map(),attempts=new Map();
 let dialog=null,owner='',view='new',queued=false,saving=false,previousFocus=null,itemsShown=[],fromVersion=null;
 const current=()=>root.NK_DEVICE?.version;
 function active(){const H=root.NK_HOUSEHOLD;return H?.authenticated&&H.id&&root.NK_APP&&!app.hidden?H.id:'';}
 function stored(id){try{return R.normalize(localStorage.getItem(prefix+encodeURIComponent(id)));}catch{return null;}}
 function seenVersion(){const id=active();return id?R.highest(root.NK_APP.getState().profile.releaseNotesSeen,stored(id),shown.get(id)):null;}
 function pending(){return active()?R.unread(D,seenVersion(),current()):[];}
 function hasPending(){return pending().length>0;}
 function idle(){return active()&&!document.hidden&&!root.NK_APP.hasDraft&&!root.NK_DEVICE?.hasUnsavedForm()&&!root.NK_HOUSEHOLD.blocked;}
 function safe(){return idle()&&!document.querySelector('dialog[open]');}
 function status(text){const el=dialog?.querySelector('#release-ack-status');if(el&&dialog.open&&owner===active()&&el.textContent!==text)el.textContent=text;}
 function remember(id,version){const top=R.highest(shown.get(id),stored(id),version);shown.set(id,top);try{localStorage.setItem(prefix+encodeURIComponent(id),top);}catch{/* Profile persistence remains primary; memory avoids repetition in this session. */}}
 async function saveDisplayed(){
  const id=active();if(!id||saving||!idle())return;
  const version=R.highest(shown.get(id),stored(id)),saved=R.normalize(root.NK_APP.getState().profile.releaseNotesSeen);
  if(!version||R.compare(version,current())>0||saved&&R.compare(saved,version)>=0)return;
  const key=id+':'+version;if((attempts.get(key)||0)>Date.now()-5000)return;attempts.set(key,Date.now());saving=true;
  try{await root.NK_APP.acknowledgeReleases(version,id);if(active()===id)status('Bereits angezeigt. Nach der Synchronisierung gilt dieser Stand auch auf deinen anderen Geräten.');}
  catch(e){if(active()===id)status('Auf diesem Gerät vorgemerkt. Der Abgleich mit deinen anderen Geräten steht noch aus. '+e.message);setTimeout(schedule,5200);}
  finally{saving=false;schedule();}
 }
 function date(s){return new Intl.DateTimeFormat('de-CH',{day:'2-digit',month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(s+'T12:00:00Z'));}
 function cards(items,archive){return items.map((r,i)=>`<details class="release-card" ${!archive||i===0?'open':''} data-release-version="${E(r.version)}"><summary><span class="release-stamp">v${E(r.version)}</span><span class="release-card-heading"><strong>${E(r.title)}</strong><time datetime="${E(r.date)}">${E(date(r.date))}</time></span><span class="release-chevron" aria-hidden="true">⌄</span></summary><div class="release-card-body"><p class="release-summary">${E(r.summary)}</p><div class="release-changes">${r.changes.map((c,j)=>`<section class="release-change"><span class="release-step" aria-hidden="true">${String(j+1).padStart(2,'0')}</span><div><h3>${E(c.title)}</h3><p>${E(c.text)}</p></div></section>`).join('')}</div><details class="release-fineprint"><summary>Gut zu wissen</summary>${r.notes.map(n=>`<p>${E(n)}</p>`).join('')}</details><a class="release-text-link" href="release-notes/v${E(r.version)}.md" download>Release Notes als Text speichern</a></div></details>`).join('');}
 function render(){
  const id=active();if(!id)return;const items=view==='archive'?R.available(D,current()):itemsShown,name=root.NK_HOUSEHOLD.name||'Dein Profil';
  dialog.innerHTML=`<header class="release-hero"><div class="release-hero-top"><span class="release-kicker">DEIN KOMPASS · WEITERENTWICKELT</span><button type="button" data-release-action="close" class="release-close" aria-label="Neuerungen schliessen">×</button></div><p class="release-for"></p><h2 id="release-dialog-title" tabindex="-1">${view==='archive'?'Dein Release-Archiv.':'Das ist neu für dich.'}</h2><p id="release-dialog-description">${view==='archive'?'Alle Neuerungen ab v1.9. Jederzeit nachlesen.':fromVersion?'Alle Updates seit deinem zuletzt angezeigten Stand v'+E(fromVersion)+'.':'Zum Start zeigen wir dir die Neuerungen ab v1.9.'}</p><div class="release-hero-pills"><span>${items.length} ${items.length===1?'Update':'Updates'}</span><span>Aktuell: v${E(current())}</span><span>Automatisch nur einmal</span></div></header><div class="release-body">${cards(items,view==='archive')}<div class="release-archive-hint"><span aria-hidden="true">▤</span><div><strong>Ein Platz für alle Release Notes.</strong><p>Du kannst diese Änderungen jederzeit wieder nachlesen.</p><a href="release-notes/" target="_blank" rel="noopener noreferrer">Ordner «Release Notes» öffnen</a></div></div></div><footer class="release-footer"><p id="release-ack-status" class="release-ack-status" role="status">${view==='archive'?'Das Archiv bleibt jederzeit verfügbar.':'Diese Neuerungen werden automatisch als angezeigt gemerkt – auch beim Schliessen. Keine Lesebestätigung nötig.'}</p><div class="release-footer-actions"><button type="button" class="button" data-release-action="close">Weiter zur App</button>${view==='new'?'<button type="button" class="button secondary" data-release-action="archive">Alle Release Notes</button>':''}</div></footer>`;
  dialog.querySelector('.release-for').textContent='Für '+name;
 }
 function close(){dialog?.close();schedule();}
 function open(mode='archive'){
  const id=active();if(!id||(!dialog?.open&&document.querySelector('dialog[open]')))return;
  if(mode==='new'){itemsShown=pending();fromVersion=seenVersion();if(!itemsShown.length)return;}
  if(!dialog){dialog=document.createElement('dialog');dialog.id='release-notes-dialog';dialog.setAttribute('aria-labelledby','release-dialog-title');dialog.setAttribute('aria-describedby','release-dialog-description');document.body.append(dialog);
   dialog.addEventListener('cancel',e=>{e.preventDefault();close();});
   dialog.addEventListener('close',()=>{if(previousFocus?.isConnected&&active()===owner)previousFocus.focus();schedule();});
  }
  owner=id;view=mode;previousFocus=dialog.open?previousFocus:document.activeElement;render();
  if(!dialog.open)dialog.showModal();dialog.querySelector('#release-dialog-title').focus();
  // Mark only after a real, visible opening. Keep the rendered snapshot on screen
  // while persistence changes the marker; otherwise it would immediately disappear.
  if(mode==='new'){remember(id,R.highest(...itemsShown.map(r=>r.version)));saveDisplayed();}
 }
 function enhance(){
  const id=active(),button=document.getElementById('release-notes-button');if(button){button.hidden=!id;const n=id?pending().length:0,badge=button.querySelector('[data-release-count]');if(badge){badge.hidden=!n;if(badge.textContent!==String(n))badge.textContent=String(n);}button.setAttribute('aria-label',n?'Neuerungen: '+n+' noch nicht angezeigte Updates':'Neuerungen und Release-Archiv');}
  if(dialog?.open&&owner!==id){dialog.close();owner='';}if(!id)return;
  const form=document.getElementById('profile-form');if(form&&!document.getElementById('release-profile-card')){const box=document.createElement('section');box.id='release-profile-card';box.className='release-profile-card';box.innerHTML='<div><p class="release-kicker">APP & NEUERUNGEN</p><h2>Dein Kompass entwickelt sich weiter.</h2><p>Neue Funktionen erscheinen automatisch nur einmal je Profil und Version. Im Archiv kannst du jederzeit alles nachlesen.</p></div><button type="button" class="button secondary" data-release-action="archive">Neuerungen & Release Notes</button>';form.after(box);}
  if(hasPending()&&safe())open('new');else saveDisplayed();
 }
 function schedule(){if(!queued){queued=true;setTimeout(()=>{queued=false;enhance();},60);}}
 document.addEventListener('click',e=>{const b=e.target.closest('[data-release-action]');if(!b)return;e.preventDefault();if(b.dataset.releaseAction==='archive')open('archive');else if(['close','later','ack'].includes(b.dataset.releaseAction))close();});
 new MutationObserver(schedule).observe(app,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden']});
 for(const event of ['nk-profile-loaded','nk-synced','nk-release-acknowledged','visibilitychange'])document.addEventListener(event,schedule);
 document.addEventListener('close',schedule,true);root.addEventListener('storage',e=>{if(e.key?.startsWith(prefix))schedule();});
 root.NK_RELEASES={openArchive:()=>open('archive'),refresh:schedule,hasPending};schedule();
})(window);
