/* Curated kitchen estimates. No inferred matches, no nutrient or private-state mutations. */
(function(root,factory){
 if(typeof module==='object'&&module.exports)module.exports=factory(require('./household-measures-data.js'));
 else {root.NK_MEASURES=factory(root.NK_MEASURE_DATA);if(root.NK_DATA)root.NK_MEASURES.decorate(root.NK_DATA.foods);}
})(typeof globalThis!=='undefined'?globalThis:this,function(D){
 'use strict';
 if(!D||D.schema!==1)throw Error('Haushaltsmass-Daten fehlen.');
 const copy=v=>JSON.parse(JSON.stringify(v)),records=new Map(D.records.map(r=>[r.id,r])),ids=new Map();
 for(const r of D.records)for(const [id,name] of r.foods)ids.set(id,{r,name});
 function record(food){
  if(!food||food.basis!=='g')return null;
  const direct=ids.get(food.id);if(direct&&direct.name===food.name)return direct.r;
  // A saved, deliberately chosen reference can accompany a custom/shared variant.
  for(const d of [food.cup,food.portion])if(d?.estimated===true&&records.has(d.reference?.catalogId))return records.get(d.reference.catalogId);
  return null;
 }
 function options(food,kind){return record(food)?.[kind==='cup'?'cups':'pieces']||[];}
 function source(r){const s=D.sources[r.source];return {name:s.name,url:r.fdcId?'https://fdc.nal.usda.gov/food-details/'+r.fdcId+'/nutrients':s.url};}
 function choose(food,kind,id){
  const r=record(food),v=options(food,kind).find(x=>x.id===id);
  if(!r||!v)throw Error('Keine passende Referenz für dieses Lebensmittel.');
  const s=source(r),reference={catalogId:r.id,variantId:v.id,form:v.label,sourceName:s.name,sourceUrl:s.url,sourceFood:r.sourceFood,checkedAt:D.checkedAt,...(r.fdcId?{fdcId:r.fdcId}:{}),...(v.portionId?{portionId:v.portionId}:{}),note:r.note};
  const def=kind==='cup'?{grams:v.grams,ml:D.cupMl}:{label:r.pieceLabel+(v.label.toLowerCase()===r.pieceLabel.toLowerCase()?'':' · '+v.label),size:v.grams,unit:'g'};
  const out=copy(food);out[kind==='cup'?'cup':'portion']={...def,estimated:true,reference};return out;
 }
 function defaults(food){
  const r=ids.get(food.id);if(!r||r.name!==food.name||food.basis!=='g')return food;
  let out=food;if(!food.portion&&r.r.pieces.length)out=choose(out,'piece',r.r.pieceDefault||r.r.pieces[0].id);
  // Native density and explicit product weights take priority. Bulk density is NOT
  // assigned to food.density, which is also used in unrelated weight/volume flows.
  if(!food.cup&&food.density==null&&r.r.cups.length)out=choose(out,'cup',r.r.cups[0].id);
  return out;
 }
 function decorate(foods){let count=0;for(let i=0;i<foods.length;i++){const f=defaults(foods[i]);if(f!==foods[i]){foods[i]=f;count++;}}return count;}
 function suggested(food,kind,text){
  const opts=options(food,kind),t=String(text||'').toLowerCase();let wanted='';
  const rules=kind==='cup'?[['grated',/gerieben|geraspelt|grated/],['ground',/gemahlen|ground/],['mashed',/zerdrückt|püriert|mashed/],['sliced',/scheiben|streifen|sliced/],['chopped',/gehackt|gewürfelt|chopped|diced/],['whole',/ganz|whole/]]:[['cherry',/cherry|kirschtomat/],['floret',/röschen|floret/],['xl',/\bxl\b|extra.?large/],['small',/\bklein\w*|\bsmall\b/],['large',/\bgro[ßs]\w*|\blarge\b/],['medium',/\bmittel\w*|\bmedium\b/]];
  for(const [id,re] of rules)if(re.test(t)&&opts.some(x=>x.id===id)){wanted=id;break;}
  const def=food[kind==='cup'?'cup':'portion'];return wanted||def?.reference?.variantId||opts[0]?.id||'';
 }
 function same(a,b){return Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=1e-7*Math.max(1,Math.abs(a),Math.abs(b));}
 function preserve(def,previous,kind){
  if(!def)return null;
  const equal=kind==='cup'?previous&&same(def.grams/def.ml,previous.grams/previous.ml):previous&&def.unit===previous.unit&&same(def.size,previous.size);
  return equal&&previous.estimated===true?{...copy(previous),...def}:def;
 }
 function estimated(food,unit){return unit==='piece'?food?.portion?.estimated===true:/^cup(?:240|250|US)$/.test(unit)?food?.basis==='g'&&food?.cup?.estimated===true:false;}
 function itemEstimated(i){const c=i.cupUse,p=i.portionUse;return estimated(i.food,i.unit)||c?.estimated===true&&i.unit===c.basis&&same(Number(i.quantity),c.baseAmount)||p?.estimated===true&&i.unit===p.unit&&same(Number(i.quantity),p.quantity*p.size);}
 function recipeEstimated(r){return r?.ingredients?.some(itemEstimated)||false;}
 function explanation(food,kind){const d=food?.[kind==='cup'?'cup':'portion'];if(!d?.estimated)return '';const r=d.reference;return 'Geschätzter Referenzwert · '+(r?.form||'Haushaltsmass')+'. '+(r?.note||'Grösse und Füllweise variieren.')+' Wiegen ist genauer.';}
 return {data:D,record,options,choose,defaults,decorate,suggested,preserve,estimated,itemEstimated,recipeEstimated,explanation};
});
