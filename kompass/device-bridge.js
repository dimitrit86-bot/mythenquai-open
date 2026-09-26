/* Additive device UI; existing authentication and private storage remain unchanged. */
(function(){'use strict';const D=window.NK_DEVICE;if(!D)return;const LAST='nk:last-profile:1';
try{const p=D.read();if(p.mode==='fixed')localStorage.setItem(LAST,p.id);else if(p.mode==='ask')localStorage.removeItem(LAST);}catch{}
let editorTouched=false,ready=false;
const root=document.getElementById('app'),dlg=document.getElementById('household-dialog');
const profiles=()=>[...dlg.querySelectorAll('[data-nk="choose"]')].map(b=>({id:b.dataset.id,name:b.querySelector('b')?.textContent||'Profil'}));
function enhance(){const H=window.NK_HOUSEHOLD,A=window.NK_APP,active=H?.name&&!root.hidden;
 const b=document.getElementById('device-profile-button');if(b)b.hidden=!active;
 if(A&&!Object.getOwnPropertyDescriptor(A,'hasDraft'))Object.defineProperty(A,'hasDraft',{get:()=>editorTouched&&!!document.getElementById('recipe-name')});
 if(H&&!Object.getOwnPropertyDescriptor(H,'authenticated'))Object.defineProperty(H,'authenticated',{get:()=>!!H.name});
 if(active&&!ready){ready=true;document.dispatchEvent(new Event('nk-profile-loaded'));}if(!active)ready=false;
 const ps=profiles();if(ps.length&&!dlg.querySelector('.device-preference')){const e=document.createElement('div');e.innerHTML=D.controls(ps);dlg.querySelector('.profile-grid')?.after(e);}
 root.querySelectorAll('[data-nk="install"]').forEach(b=>b.dataset.device='install');
}
document.addEventListener('click',e=>{const b=e.target.closest('[data-nk]');if(!b)return;
 if(b.dataset.nk==='install'){e.preventDefault();e.stopImmediatePropagation();D.install();}
 if(b.dataset.nk==='device-save'){e.preventDefault();e.stopImmediatePropagation();try{const v=dlg.querySelector('#device-profile-choice').value;D.save(v.startsWith('profile:')?{mode:'fixed',id:v.slice(8)}:{mode:v},profiles());let t=dlg.querySelector('#device-save-message');if(!t){t=document.createElement('p');t.id='device-save-message';t.className='small';b.after(t);}t.textContent='Startprofil auf diesem Gerät gespeichert. Der aktuelle Profilwechsel bleibt möglich.';}catch(err){alert(err.message);}}
},true);
document.addEventListener('input',e=>{if(e.target.closest('#main')&&document.getElementById('recipe-name'))editorTouched=true;});
let queued=false;const obs=new MutationObserver(()=>{if(!queued){queued=true;queueMicrotask(()=>{queued=false;if(!document.getElementById('recipe-name'))editorTouched=false;enhance();});}});obs.observe(root,{subtree:true,childList:true,attributes:true,attributeFilter:['hidden']});obs.observe(dlg,{subtree:true,childList:true});enhance();
})();
