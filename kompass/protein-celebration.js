/* Celebration is UI-only; goals, consumed amounts and their reference calculation never change. */
(function(root){'use strict';
function eligible(state,date,C){const entries=C.dayEntries(state,date),intake=C.aggregate(entries.map(e=>e.n),['protein']).protein,target=C.targets(state.profile).values.protein?.value;return Number.isFinite(target)&&target>0&&intake.total>0&&intake.known===intake.total&&Number.isFinite(intake.value)&&intake.value+1e-9>=target?{amount:intake.value,target}:null;}
if(typeof module==='object'&&module.exports){module.exports={eligible};return;}
const C=root.NK,prefix='nk:protein-party:1:',seen=new Set();let queued=false,busy=false,lastId='',dialog=null;
function already(key){if(seen.has(key))return true;try{return localStorage.getItem(key)==='1';}catch{return false;}}
function mark(key){seen.add(key);try{localStorage.setItem(key,'1');const old=[];for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k?.startsWith(prefix))old.push(k);}old.sort((a,b)=>a.slice(-10).localeCompare(b.slice(-10))).slice(0,Math.max(0,old.length-100)).forEach(k=>localStorage.removeItem(k));}catch{/* Session fallback still prevents repetition when storage is unavailable. */}}
function check(){const A=root.NK_APP,H=root.NK_HOUSEHOLD,id=H?.id;if(id!==lastId){dialog?.close();lastId=id;}if(!A||!id||document.getElementById('app')?.hidden||document.hidden||busy||A.hasDraft||root.NK_DEVICE?.hasUnsavedForm()||document.querySelector('dialog[open]'))return;
 const day=C.dateKey(new Date()),visibleDate=document.getElementById('diary-date')?.value;if(visibleDate!==day)return;const key=prefix+id+':'+day;if(already(key))return;const result=eligible(A.getState(),day,C);if(!result)return;
 busy=true;const focus=document.activeElement;try{
  if(!dialog){dialog=document.createElement('dialog');dialog.id='protein-party';dialog.setAttribute('aria-labelledby','party-title');dialog.setAttribute('aria-describedby','party-message');dialog.lang='es';document.body.append(dialog);}
  dialog.innerHTML='<div class="party-confetti" aria-hidden="true">'+Array.from({length:22},(_,i)=>'<i style="--x:'+((i*47)%100)+'%;--delay:'+(i%7)*.11+'s;--turn:'+(i*39)+'deg"></i>').join('')+'</div><div class="party-content"><div class="party-medal" aria-hidden="true">🏆</div><p class="party-eyebrow">OBJETIVO DEL DÍA</p><h2 id="party-title">¡La concha de la lora!</h2><p class="party-congrats">¡Felicitaciones!</p><p id="party-message"></p><p id="party-amount"></p><p class="party-note">Objetivo alcanzado según tus registros. ¡A disfrutar el día!</p><button type="button" id="party-close">¡Vamos! Volver al día</button></div>';
  dialog.querySelector('#party-message').textContent=(H.name?H.name+', ':'')+'alcanzaste tu objetivo de proteína de hoy.';
  const f=new Intl.NumberFormat('es-AR',{maximumFractionDigits:1});dialog.querySelector('#party-amount').textContent=f.format(result.amount)+' / '+f.format(result.target)+' g de proteína';
  dialog.querySelector('#party-close').onclick=()=>dialog.close();dialog.onclose=()=>focus?.isConnected&&focus.focus();dialog.showModal();mark(key);
 }finally{busy=false;}}
function schedule(){if(!queued){queued=true;setTimeout(()=>{queued=false;check();},100);}}
const app=document.getElementById('app');new MutationObserver(schedule).observe(app,{subtree:true,childList:true,attributes:true,attributeFilter:['hidden']});document.addEventListener('nk-profile-loaded',schedule);document.addEventListener('nk-synced',schedule);document.addEventListener('visibilitychange',schedule);document.addEventListener('close',schedule,true);root.NK_CELEBRATION={eligible,refresh:schedule};schedule();
})(typeof window!=='undefined'?window:globalThis);
