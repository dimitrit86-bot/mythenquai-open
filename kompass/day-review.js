/* Ask about yesterday's unfinished diary. No invented meals or automatic completion. */
(function(root){'use strict';
 const C=root.NK,Rules=root.NK_DAY_REVIEW_CORE,app=document.getElementById('app');if(!C||!Rules||!app)return;
 let dialog=null,context=null,queued=false,busy=false,failed=false,previousFocus=null;const deferred=new Set();
 const E=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function active(){const H=root.NK_HOUSEHOLD;return H?.authenticated&&H.id&&root.NK_APP&&!app.hidden?H.id:'';}
 function candidate(){return active()?Rules.candidate(root.NK_APP.getState(),C.dateKey()):null;}
 function key(id,date){return id+':'+date;}
 function hasPending(){const c=candidate();return !!c&&!deferred.has(key(active(),c.date));}
 function safe(){return active()&&!document.hidden&&!root.NK_APP.hasDraft&&!root.NK_DEVICE?.hasUnsavedForm()&&!root.NK_HOUSEHOLD.blocked&&!root.NK_RELEASES?.hasPending()&&!document.querySelector('dialog[open]');}
 function close(later=true){if(later&&context)deferred.add(key(context.id,context.date));dialog?.close();schedule();}
 function signature(day){return Rules.signature(root.NK_APP.getState(),day,root.NK_SYNC.stable);}
 function draw(){const c=context;if(!c||c.id!==active())return;
  const date=new Intl.DateTimeFormat('de-CH',{weekday:'long',day:'numeric',month:'long'}).format(new Date(c.date+'T12:00:00'));
  dialog.innerHTML=`<div class="day-review-head"><span class="eyebrow">DEIN TAGEBUCH · KURZER CHECK</span><button type="button" class="icon-btn" data-day-review="later" aria-label="Später erinnern">×</button></div><div class="day-review-symbol" aria-hidden="true">✓</div><p class="day-review-for"></p><h2 id="day-review-title" tabindex="-1">Ist gestern vollständig?</h2><p id="day-review-description">Hast du für <strong>${E(date)}</strong> bereits alles protokolliert?</p><p class="day-review-info">${c.count} ${c.count===1?'Eintrag ist':'Einträge sind'} vorhanden. Das Häkchen «Tag vollständig protokolliert» fehlt noch.</p><p class="day-review-note">Mit «Ja» setzen wir das Häkchen direkt. Es werden keine Mahlzeiten hinzugefügt und keine Nährwerte verändert.</p><p id="day-review-error" class="error" role="alert"></p><div class="day-review-actions"><button type="button" class="button" data-day-review="yes">Ja, alles erfasst</button><button type="button" class="button secondary" data-day-review="no">Nein, Vortag öffnen</button><button type="button" class="muted-link" data-day-review="later">Später</button></div>`;
  dialog.querySelector('.day-review-for').textContent='Für '+root.NK_HOUSEHOLD.name;
 }
 function show(c){
  if(!dialog){dialog=document.createElement('dialog');dialog.id='day-review-dialog';dialog.setAttribute('aria-labelledby','day-review-title');dialog.setAttribute('aria-describedby','day-review-description');document.body.append(dialog);
   dialog.addEventListener('cancel',e=>{e.preventDefault();if(!busy)close();});
   dialog.addEventListener('close',()=>{if(previousFocus?.isConnected&&active()===context?.id)previousFocus.focus();schedule();});
   dialog.addEventListener('click',e=>{const b=e.target.closest('[data-day-review]');if(!b||busy)return;const action=b.dataset.dayReview;if(action==='later')close();else respond(action==='yes');});
  }
  failed=false;context={...c,id:active(),signature:signature(c.date)};previousFocus=document.activeElement;draw();dialog.showModal();dialog.querySelector('#day-review-title').focus();
 }
 async function respond(complete){
  const c=context;if(!c||busy||active()!==c.id)return;busy=true;dialog.querySelectorAll('button').forEach(b=>b.disabled=true);
  try{await root.NK_APP.respondDayReview(c.date,complete,c.id,c.signature);failed=false;
   if(active()===c.id){close();if(!complete)root.NK_APP.openDay(c.date);}
  }catch(e){if(active()===c.id&&dialog.open){
    failed=true;const entries=C.dayEntries(root.NK_APP.getState(),c.date);
    if(c.date!==Rules.previousDay(C.dateKey())||!entries.length){dialog.close();}else{
     if(signature(c.date)!==c.signature){context={date:c.date,count:entries.length,id:c.id,signature:signature(c.date)};draw();}
     dialog.querySelector('#day-review-error').textContent=e.message;
    }
   }}finally{busy=false;dialog?.querySelectorAll('button').forEach(b=>b.disabled=false);schedule();}
 }
 function check(){
  if(dialog?.open&&!busy){const c=failed&&active()===context?.id&&context.date===Rules.previousDay(C.dateKey())?context:candidate();if(active()!==context?.id||!c||c.date!==context.date){dialog.close();}else if(signature(c.date)!==context.signature){context={...c,id:active(),signature:signature(c.date)};draw();dialog.querySelector('#day-review-error').textContent='Die Einträge wurden zwischenzeitlich geändert. Bitte die Vollständigkeit nochmals prüfen.';}}
  if(!busy&&hasPending()&&safe())show(candidate());
 }
 function schedule(){if(!queued){queued=true;setTimeout(()=>{queued=false;check();},160);}}
 new MutationObserver(schedule).observe(app,{subtree:true,childList:true,attributes:true,attributeFilter:['hidden']});
 document.addEventListener('nk-synced',()=>{if(active()===context?.id)failed=false;schedule();});
 for(const event of ['nk-profile-loaded','nk-day-reviewed','visibilitychange'])document.addEventListener(event,schedule);
 document.addEventListener('close',schedule,true);root.addEventListener('focus',schedule);
 // Check the local calendar after midnight, including a long-running installed PWA.
 const timer=setInterval(()=>{if(!document.hidden)schedule();},60000);
 root.NK_DAY_REVIEW={refresh:schedule,hasPending};schedule();
})(window);
