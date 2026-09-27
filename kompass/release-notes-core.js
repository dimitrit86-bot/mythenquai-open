/* Release acknowledgement is display metadata, never nutrition or diary data. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.NK_RELEASE_CORE=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const BASELINE='1.9.0';
 function normalize(v){if(typeof v!=='string'||!/^(0|[1-9]\d{0,4})\.(0|[1-9]\d{0,4})(?:\.(0|[1-9]\d{0,4}))?$/.test(v))return null;const p=v.split('.');return p.length===2?v+'.0':v;}
 function compare(a,b){a=normalize(a);b=normalize(b);if(!a||!b)throw Error('Ungültige Release-Version.');const x=a.split('.').map(Number),y=b.split('.').map(Number);for(let i=0;i<3;i++)if(x[i]!==y[i])return x[i]>y[i]?1:-1;return 0;}
 function highest(...values){return values.map(normalize).filter(Boolean).reduce((a,b)=>!a||compare(b,a)>0?b:a,null);}
 function validate(data){
  if(!data||data.schema!==1||!Array.isArray(data.releases)||!data.releases.length)throw Error('Release-Katalog fehlt.');
  const ids=new Set();for(const r of data.releases){const v=normalize(r.version);if(v!==r.version||ids.has(v)||compare(v,BASELINE)<0)throw Error('Ungültige oder doppelte Release-Version.');ids.add(v);
   if(!/^\d{4}-\d{2}-\d{2}$/.test(r.date)||typeof r.title!=='string'||!r.title||typeof r.summary!=='string'||!Array.isArray(r.changes)||!r.changes.length||!r.changes.every(c=>c&&typeof c.title==='string'&&typeof c.text==='string')||!Array.isArray(r.notes)||!r.notes.every(n=>typeof n==='string'))throw Error('Unvollständiger Release-Eintrag.');
  }return data;
 }
 function available(data,current){validate(data);if(!normalize(current))return [];return data.releases.filter(r=>compare(r.version,current)<=0).slice().sort((a,b)=>compare(b.version,a.version));}
 function unread(data,seen,current){const read=normalize(seen);return available(data,current).filter(r=>!read||compare(r.version,read)>0);}
 return {BASELINE,normalize,compare,highest,validate,available,unread};
});
