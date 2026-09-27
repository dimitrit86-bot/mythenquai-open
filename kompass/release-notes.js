/* New features since the profile's last explicit acknowledgement. No tracking service. */
(function(root){'use strict';
 const R=root.NK_RELEASE_CORE,D=root.NK_RELEASE_DATA;if(!R||!D)return;
 try{R.validate(D);}catch(e){console.warn('Release Notes: '+e.message);return;}
 const E=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const app=document.getElementById('app'),deferred=new Set();let dialog=null,owner='',view='new',busy=false,queued=false,previousFocus=null;
 const current=()=>root.NK_DEVICE?.version;
 function active(){const H=root.NK_HOUSEHOLD;return H?.authenticated&&H.id&&root.NK_APP&&!app.hidden?H.id:'';}
 function pending(){return active()?R.unread(D,root.NK_APP.getState().profile.releaseNotesSeen,current()):[];}
 function hasPending(){const id=active();return !!id&&!deferred.has(id)&&pending().length>0;}
 function safe(){return active()&&!document.hidden&&!root.NK_APP.hasDraft&&!root.NK_DEVICE?.hasUnsavedForm()&&!root.NK_HOUSEHOLD.blocked&&!document.querySelector('dialog[open]');}
 function date(s){return new Intl.DateTimeFormat('de-CH',{day:'2-digit',month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(s+'T12:00:00Z'));}
 function cards(items,archive){return items.map((r,i)=>`<details class="release-card" ${!archive||i===0?'open':''} data-release-version="${E(r.version)}"><summary><span class="release-stamp">v${E(r.version)}</span><span class="release-card-heading"><strong>${E(r.title)}</strong><time datetime="${E(r.date)}">${E(date(r.date))}</time></span><span class="release-chevron" aria-hidden="true">⌄</span></summary><div class="release-card-body"><p class="release-summary">${E(r.summary)}</p><div class="release-changes">${r.changes.map((c,j)=>`<section class="release-change"><span class="release-step" aria-hidden="true">${String(j+1).padStart(2,'0')}</span><div><h3>${E(c.title)}</h3><p>${E(c.text)}</p></div></section>`).join('')}</div><details class="release-fineprint"><summary>Gut zu wissen</summary>${r.notes.map(n=>`<p>${E(n)}</p>`).join('')}</details><a class="release-text-link" href="release-notes/v${E(r.version)}.md" download>Release Notes als Text speichern</a></div></details>`).join('');}
 function render(){
  const id=active();if(!id)return;const unread=pending(),all=R.available(D,current()),items=view==='archive'?all:unread;
  const seen=R.normalize(root.NK_APP.getState().profile.releaseNotesSeen),name=root.NK_HOUSEHOLD.name||'Dein Profil';
  dialog.innerHTML=`<header class="release-hero"><div class="release-hero-top"><span class="release-kicker">DEIN KOMPASS · WEITERENTWICKELT</span><button type="button" data-release-action="later" class="release-close" aria-label="Neuerungen schliessen">×</button></div><p class="release-for"></p><h2 id="release-dialog-title" tabindex="-1">${view==='archive'?'Dein Release-Archiv.':'Das ist neu für dich.'}</h2><p id="release-dialog-description">${view==='archive'?'Alle Neuerungen ab v1.9. Jederzeit nachlesen.':seen?'Alle Updates seit deinem bestätigten Stand v'+E(seen)+'.':'Zum Start zeigen wir dir die Neuerungen ab v1.9.'}</p><div class="release-hero-pills"><span>${items.length} ${items.length===1?'Update':'Updates'}</span><span>Aktuell: v${E(current())}</span>${unread.length?'<span>'+unread.length+' noch nicht bestätigt</span>':'<span>Alles auf dem neuesten Stand</span>'}</div></header><div class="release-body">${cards(items,view==='archive')}<div class="release-archive-hint"><span aria-hidden="true">▤</span><div><strong>Ein Platz für alle Release Notes.</strong><p>Das Archiv startet mit v1.9. Danach kommen die neuen Versionen hinzu.</p><a href="release-notes/" target="_blank" rel="noopener noreferrer">Ordner «Release Notes» öffnen</a></div></div></div><footer class="release-footer"><p id="release-ack-status" class="release-ack-status" role="status">${unread.length?'Erst «Gelesen – weiter» bestätigt die angezeigten Neuerungen für dieses Profil.':'Dein bestätigter Stand: v'+E(seen||current())+'.'}</p><div class="release-footer-actions">${unread.length?'<button type="button" class="button" data-release-action="ack">Gelesen – weiter</button>':'<button type="button" class="button" data-release-action="later">Zurück zur App</button>'}<button type="button" class="button secondary" data-release-action="'+(view==='archive'?'new':'archive')+'" '+(view==='archive'&&!unread.length?'hidden':'')+'>${view==='archive'?'Nur neue Updates':'Alle Release Notes'}</button>${unread.length?'<button type="button" class="muted-link" data-release-action="later">Später</button>':''}</div></footer>`;
  dialog.querySelector('.release-for').textContent='Für '+name;dialog.dataset.lastSeen=seen||'';
 }
 function open(mode='new'){
  const id=active();if(!id)return;if(!dialog?.open&&document.querySelector('dialog[open]'))return;
  if(!dialog){dialog=document.createElement('dialog');dialog.id='release-notes-dialog';dialog.setAttribute('aria-labelledby','release-dialog-title');dialog.setAttribute('aria-describedby','release-dialog-description');document.body.append(dialog);
   dialog.addEventListener('cancel',e=>{e.preventDefault();if(!busy)later();});
   dialog.addEventListener('close',()=>{if(previousFocus?.isConnected&&active()===owner)previousFocus.focus();schedule();});
  }
  owner=id;view=mode;previousFocus=dialog.open?previousFocus:document.activeElement;render();
  if(!dialog.open)dialog.showModal();dialog.querySelector('#release-dialog-title').focus();
 }
 function later(){if(owner)deferred.add(owner);dialog?.close();schedule();}
 async function acknowledge(){
  if(busy||active()!==owner)return;const id=owner,version=current();busy=true;
  dialog.querySelectorAll('button').forEach(b=>b.disabled=true);dialog.querySelector('#release-ack-status').textContent='Lesestand wird gesichert …';
  try{await root.NK_APP.acknowledgeReleases(version,id);if(active()===id){deferred.add(id);dialog.close();}}
  catch(e){if(active()===id&&dialog.open){dialog.querySelector('#release-ack-status').textContent='Noch nicht bestätigt: '+e.message;dialog.querySelectorAll('button').forEach(b=>b.disabled=false);}}
  finally{busy=false;schedule();}
 }
 function enhance(){
  const id=active(),button=document.getElementById('release-notes-button');if(button){button.hidden=!id;const n=id?pending().length:0,badge=button.querySelector('[data-release-count]');if(badge){badge.hidden=!n;if(badge.textContent!==String(n))badge.textContent=String(n);}button.setAttribute('aria-label',n?'Neuerungen: '+n+' unbestätigte Updates':'Neuerungen und Release-Archiv');}
  if(dialog?.open&&owner!==id){dialog.close();owner='';}
  if(!id)return;
  const form=document.getElementById('profile-form');if(form&&!document.getElementById('release-profile-card')){const box=document.createElement('section');box.id='release-profile-card';box.className='release-profile-card';box.innerHTML='<div><p class="release-kicker">APP & NEUERUNGEN</p><h2>Dein Kompass entwickelt sich weiter.</h2><p>Alle Release Notes ab v1.9 an einem Ort. Dein Lesestand gehört zu diesem Profil.</p></div><button type="button" class="button secondary" data-release-action="archive">Neuerungen & Release Notes</button>';form.after(box);}
  if(dialog?.open&&!busy&&(dialog.dataset.lastSeen||'')!==(R.normalize(root.NK_APP.getState().profile.releaseNotesSeen)||'')){if(view==='new'&&!pending().length){dialog.close();}else render();}
  if(hasPending()&&safe())open('new');
 }
 function schedule(){if(!queued){queued=true;setTimeout(()=>{queued=false;enhance();},60);}}
 document.addEventListener('click',e=>{const b=e.target.closest('[data-release-action]');if(!b)return;e.preventDefault();const a=b.dataset.releaseAction;if(a==='ack')acknowledge();else if(a==='later'&&!busy)later();else if(a==='archive'||a==='new')open(a);});
 new MutationObserver(schedule).observe(app,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden']});
 for(const event of ['nk-profile-loaded','nk-synced','nk-release-acknowledged','visibilitychange'])document.addEventListener(event,schedule);
 document.addEventListener('close',schedule,true);root.NK_RELEASES={openArchive:()=>open('archive'),refresh:schedule,hasPending};schedule();
})(window);
