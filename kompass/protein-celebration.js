/* Celebrate a confirmed current-day diary crossing. No effect on nutrition targets or calculations. */
(function(root){'use strict';
function crossing(before,after,day,C){
 const target=C.targets(after.profile).values.protein?.value,oldTarget=C.targets(before.profile).values.protein?.value;
 if(!Number.isFinite(target)||target<=0||target!==oldTarget)return null;
 const sum=s=>C.aggregate(C.dayEntries(s,day).map(e=>e.n),['protein']).protein,a=sum(before),b=sum(after);
 if(!b.total||b.known!==b.total||!Number.isFinite(b.value)||b.value+1e-8<target)return null;
 // An incomplete previous tally can cross when its missing values are genuinely supplied.
 if(a.known===a.total&&Number.isFinite(a.value)&&a.value+1e-8>=target)return null;
 if(JSON.stringify(C.dayEntries(before,day))===JSON.stringify(C.dayEntries(after,day)))return null;
 return {amount:b.value,target};
}
const API={crossing};if(typeof module==='object'&&module.exports){module.exports=API;return;}root.NK_CELEBRATION=API;
const mem=new Set();let pending=null,dialog=null,previousFocus=null;
function key(id,day){return 'nk:protein-celebrated:1:'+id+':'+day;}
function already(k){try{return mem.has(k)||localStorage.getItem(k)==='1';}catch{return mem.has(k);}}
function mark(k){mem.add(k);try{localStorage.setItem(k,'1');}catch{}}
function clear(){pending=null;if(dialog?.open)dialog.close();}
function show(){
 if(!pending||document.hidden||root.NK_APP?.hasDraft||document.querySelector('dialog[open]'))return;
 const p=pending;if(p.id!==root.NK_HOUSEHOLD?.id||p.day!==root.NK.dateKey()||already(p.key)){pending=null;return;}
 const state=root.NK_APP.getState(),n=root.NK.aggregate(root.NK.dayEntries(state,p.day).map(e=>e.n),['protein']).protein,target=root.NK.targets(state.profile).values.protein?.value;
 if(target!==p.target||n.total!==n.known||!n.total||n.value+1e-8<target){pending=null;return;}
 if(!dialog){dialog=document.createElement('dialog');dialog.id='protein-celebration';dialog.lang='es';dialog.setAttribute('aria-labelledby','celebration-title');document.body.append(dialog);dialog.addEventListener('close',()=>{if(previousFocus?.isConnected)previousFocus.focus();});}
 const fmt=n=>new Intl.NumberFormat('es-AR',{maximumFractionDigits:1}).format(n);
 dialog.innerHTML='<div class="celebration-confetti" aria-hidden="true">'+Array.from({length:18},(_,i)=>'<i style="--i:'+i+'"></i>').join('')+'</div><button type="button" class="celebration-x" aria-label="Cerrar">×</button><div class="celebration-star" aria-hidden="true">★</div><p class="celebration-kicker">¡OBJETIVO ALCANZADO!</p><h2 id="celebration-title">¡La concha de la lora!<br><span>¡Felicitaciones!</span></h2><p>Alcanzaste tu objetivo de proteína de hoy.</p><div class="celebration-total">'+fmt(n.value)+' <small>/ '+fmt(target)+' g</small></div><p class="celebration-note">Según lo que registraste hoy.</p><button type="button" class="button wide celebration-close">¡Vamos!</button>';
 previousFocus=document.activeElement;dialog.querySelector('.celebration-x').onclick=()=>dialog.close();dialog.querySelector('.celebration-close').onclick=()=>dialog.close();dialog.showModal();mark(p.key);pending=null;dialog.querySelector('.celebration-close').focus();
}
document.addEventListener('nk-state-saved',e=>{const {before,after,profileId}=e.detail||{};if(!before||!after||!profileId)return;const day=root.NK.dateKey(),value=crossing(before,after,day,root.NK);if(value&&!already(key(profileId,day)))pending={...value,id:profileId,day,key:key(profileId,day)};setTimeout(show,100);});
document.addEventListener('nk-profile-loaded',clear);document.addEventListener('visibilitychange',show);
document.addEventListener('click',()=>setTimeout(show,100));
new MutationObserver(()=>{if(pending)setTimeout(show,20);}).observe(document.getElementById('app'),{subtree:true,childList:true,attributes:true,attributeFilter:['hidden']});
API.refresh=show;
})(typeof window!=='undefined'?window:globalThis);
