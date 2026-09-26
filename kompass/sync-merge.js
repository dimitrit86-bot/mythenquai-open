/* Three-way profile merge. Independent entries merge; conflicting edits require a choice. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.NK_MERGE=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const clone=x=>x===undefined?undefined:JSON.parse(JSON.stringify(x));
 function stable(x){if(x===undefined)return '~missing';if(x===null||typeof x!=='object')return JSON.stringify(x);if(Array.isArray(x))return '['+x.map(stable).join(',')+']';return '{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+stable(x[k])).join(',')+'}';}
 const equal=(a,b)=>stable(a)===stable(b);
 const own=(o,k)=>Object.prototype.hasOwnProperty.call(o||{},k);
 function merge(base,local,remote,choices={}){
  if(!local||!remote||local.schema!==1||remote.schema!==1)throw Error('Nicht unterstützter Datenstand.');
  const conflicts=[],legacy=!base,out=clone(remote);
  function choose(path,b,l,r,label){
   if(equal(l,r))return clone(l);
   if(!legacy&&equal(l,b))return clone(r);
   if(!legacy&&equal(r,b))return clone(l);
   if(legacy&&(l===undefined||r===undefined))return clone(l===undefined?r:l); // Old cache: never infer a deletion.
   const id=JSON.stringify(path),decision=choices[id];
   if(decision==='local')return clone(l);if(decision==='server')return clone(r);
   conflicts.push({id,path,label,local:clone(l),server:clone(r)});return clone(l);
  }
  function map(o){const m=new Map();for(const x of o||[]){if(!x||typeof x.id!=='string'||m.has(x.id))throw Error('Doppelte oder ungültige Eintragskennung.');m.set(x.id,x);}return m;}
  for(const k of ['entries','foods','recipes']){
   const b=map(base?.[k]),l=map(local[k]),r=map(remote[k]);out[k]=[];
   for(const id of new Set([...r.keys(),...l.keys(),...b.keys()])){
    const value=choose([k,id],b.get(id),l.get(id),r.get(id),({entries:'Tagebucheintrag',foods:'Produkt',recipes:'Gericht'})[k]+': '+(l.get(id)?.name||r.get(id)?.name||b.get(id)?.name||id));
    if(value!==undefined)out[k].push(value);
   }
  }
  function record(path,b,l,r){const o={};for(const k of new Set([...Object.keys(b||{}),...Object.keys(l||{}),...Object.keys(r||{})])){
    if(['__proto__','constructor','prototype'].includes(k))continue;
    const v=choose([...path,k],own(b,k)?b[k]:undefined,own(l,k)?l[k]:undefined,own(r,k)?r[k]:undefined,path.join(' / ')+' · '+k);
    if(v!==undefined)o[k]=v;
   }return o;}
  out.profile=record(['profile'],base?.profile,local.profile,remote.profile);
  // Manual targets have independent keys, rather than replacing the whole goal dictionary.
  const manualId=JSON.stringify(['profile','manual']);
  for(let i=conflicts.length-1;i>=0;i--)if(conflicts[i].id===manualId)conflicts.splice(i,1);
  out.profile.manual=record(['profile','manual'],base?.profile?.manual,local.profile.manual,remote.profile.manual);
  out.days=record(['days'],base?.days,local.days,remote.days);
  for(const k of ['favorites','recent']){
   const b=new Set(base?.[k]||[]),l=new Set(local[k]||[]),r=new Set(remote[k]||[]);
   out[k]=[...new Set([...(local[k]||[]),...(remote[k]||[])])].filter(id=>legacy?l.has(id)||r.has(id):l.has(id)===r.has(id)?l.has(id):l.has(id)===b.has(id)?r.has(id):l.has(id));
   if(k==='recent')out[k]=out[k].slice(0,30);
  }
  out.recipeDraft=null;
  return {state:out,conflicts,legacy};
 }
 return {merge,equal,stable};
});
