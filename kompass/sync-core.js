/* Pure three-way reconciliation. No network, storage, credentials or mutations. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.NK_SYNC=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const clone=x=>x===undefined?undefined:JSON.parse(JSON.stringify(x));
 const equal=(a,b)=>stable(a)===stable(b);
 function stable(x){if(x===undefined)return 'undefined';if(x===null||typeof x!=='object')return JSON.stringify(x);if(Array.isArray(x))return '['+x.map(stable).join(',')+']';return '{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+stable(x[k])).join(',')+'}';}
 function merge(base,local,remote,choice){
  const conflicts=[],legacy=!base;
  function atom(b,l,r,path){
   if(equal(l,r))return clone(l);
   if(!legacy&&equal(l,b))return clone(r);
   if(!legacy&&equal(r,b))return clone(l);
   if(legacy&&l===undefined)return clone(r);
   if(legacy&&r===undefined)return clone(l);
   conflicts.push(path);return clone(choice==='server'?r:l);
  }
  function object(b,l,r,path){
   const out={};for(const k of new Set([...Object.keys(b||{}),...Object.keys(l||{}),...Object.keys(r||{})])){
    // Prototype names from arbitrary imports never become object properties.
    if(['__proto__','constructor','prototype'].includes(k))continue;
    const v=atom(b?.[k],l?.[k],r?.[k],path+'.'+k);if(v!==undefined)out[k]=v;
   }return out;
  }
  function records(key){
   const B=new Map((base?.[key]||[]).map(x=>[x.id,x])),L=new Map(local[key].map(x=>[x.id,x])),R=new Map(remote[key].map(x=>[x.id,x]));
   const out=[];for(const id of new Set([...L.keys(),...R.keys(),...B.keys()])){
    const v=atom(B.get(id),L.get(id),R.get(id),key+'.'+id);if(v!==undefined)out.push(v);
   }return out;
  }
  const out=clone(local);out.schema=1;
  for(const key of ['entries','recipes','foods'])out[key]=records(key);
  const lp={...local.profile},rp={...remote.profile},bp=base?{...base.profile}:null;
  delete lp.manual;delete rp.manual;if(bp)delete bp.manual;
  out.profile=object(bp,lp,rp,'profile');out.profile.manual=object(base?.profile?.manual,local.profile.manual,remote.profile.manual,'profile.manual');
  out.days=object(base?.days,local.days,remote.days,'days');
  const bFav=new Set(base?.favorites||[]),lFav=new Set(local.favorites),rFav=new Set(remote.favorites);
  out.favorites=[...new Set([...lFav,...rFav])].filter(id=>legacy||!bFav.has(id)||lFav.has(id)&&rFav.has(id));
  out.recent=[...new Set([...local.recent,...remote.recent])].slice(0,30);out.recipeDraft=null;
  return {state:out,conflicts};
 }
 return {merge,equal,stable};
});
