/* Corrections to user-owned nutrition declarations. Quantities and historical recipes
   are frozen; public catalogue updates are never applied to diaries automatically. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory(require('./core.js'));else root.NK_RECALC=factory(root.NK);})(typeof globalThis!=='undefined'?globalThis:this,function(C){
'use strict';
const clone=C.clone,validId=v=>typeof v==='string'&&/^[A-Za-z0-9_-]{1,100}$/.test(v);
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const positive=n=>typeof n==='number'&&Number.isFinite(n)&&n>0&&n<=1e12;
function link(food,ownerId){
 const l=food?.shared?{ownerId:food.shared.ownerId,sourceId:food.shared.sourceId}:food?.nutritionLink||{ownerId,sourceId:food?.id};
 return validId(l?.ownerId)&&validId(l?.sourceId)?{ownerId:l.ownerId,sourceId:l.sourceId}:null;
}
const key=l=>l?l.ownerId+':'+l.sourceId:'';
function stamp(food,ownerId){const f=clone(food),l=link(f,ownerId);if(l)f.nutritionLink=l;return f;}
function savedFood(previous,next,ownerId,id,at){
 const f=clone(next);delete f.nutritionCorrection;delete f.nutritionLink;
 if(!previous||previous.id!==f.id)return f;
 if(!validId(ownerId)||!validId(id))throw Error('Produktkorrektur benötigt eine gültige Profilkennung.');
 f.nutritionCorrection={schema:1,id,ownerId,sourceId:f.id,at,before:{id:previous.id,name:previous.name,basis:previous.basis,n:clone(previous.n),q:clone(previous.q||{}),density:previous.density??null}};
 return f;
}
function captured(food,quantity,unit,density,ownerId){return {foodSnapshot:stamp(food,ownerId),nutritionBase:{quantity:C.factor(food,quantity,unit,density)*100,basis:food.basis},nutritionLink:link(food,ownerId)};}
function share(recipe,amount,unit){const n=C.positive(amount);return unit==='portion'?n/C.positive(recipe.servings):unit==='g'?n/C.positive(recipe.finalWeight):unit==='batch'?n:(()=>{throw Error('Ungültige Gerichtmenge.');})();}
function scaled(entry,multiplier){const out={},f=C.positive(multiplier);if(entry.nutritionBase)out.nutritionBase={...clone(entry.nutritionBase),quantity:entry.nutritionBase.quantity*f};if(positive(entry.recipeShare))out.recipeShare=entry.recipeShare*f;return out;}
// Strict parsing of the app's old amount labels, not free-form recipe text.
function legacyAmount(text,depth=0){
 if(depth>5||typeof text!=='string')return null;
 const s=text.trim().replace(/[’'\u00a0\u202f]/g,'').replace(/ · geschätzt$/,'');
 const numeric='(\\d+(?:[.,]\\d+)?)';
 let m=s.match(new RegExp('^'+numeric+'\\s*×\\s*\\((.*)\\)$'));
 if(m){const inner=legacyAmount(m[2],depth+1);return inner?{quantity:inner.quantity*Number(m[1].replace(',','.')),unit:inner.unit}:null;}
 m=s.match(new RegExp('^(?:ca\\.\\s*)?'+numeric+'\\s*(g|kg|ml|dl|l)$'));
 if(m)return {quantity:Number(m[1].replace(',','.')),unit:m[2]};
 m=s.match(new RegExp('^'+numeric+'\\s+[^()]+\\((?:ca\\.\\s*)?'+numeric+'\\s*(g|ml)\\)$'));
 if(m)return {quantity:Number(m[2].replace(',','.')),unit:m[3]};
 return null;
}
function inferredShare(snapshot,total,keys){
 let factor=null;
 for(const k of keys){const a=snapshot[k],b=total[k];if(!a||!b||a.known!==b.known||a.total!==b.total||(a.value===null)!==(b.value===null))return null;
  if(b.value===null)continue;if(!Number.isFinite(a.value)||!Number.isFinite(b.value)||a.value<0||b.value<0)return null;
  if(b.value===0){if(a.value!==0)return null;continue;}
  const ratio=a.value/b.value;if(!positive(ratio))return null;
  if(factor===null)factor=ratio;else if(Math.abs(ratio-factor)>Math.max(1e-9,Math.abs(factor)*1e-8))return null;
 }
 return factor;
}
function baseAmount(entry,source,keys){
 if(entry.nutritionBase){const b=entry.nutritionBase;if(!positive(b.quantity)||b.basis!==source.basis)throw Error('Die gespeicherte Mengenbasis passt nicht zur neuen 100-g-/100-ml-Spalte.');return b.quantity;}
 const before=entry.foodSnapshot||source.nutritionCorrection.before;
 if(before?.basis&&before.basis!==source.basis)throw Error('Nährwertbasis von g auf ml oder umgekehrt geändert. Menge bitte neu zuordnen.');
 const spec=entry.amountSpec||legacyAmount(entry.amountText);
 if(spec&&positive(spec.quantity)){
  const frozen={...(before||source),n:source.n,basis:source.basis,portion:spec.portion||null};
  // Only use an explicitly captured historical density. Old implicit conversions
  // can instead be recovered by checking every stored nutrient against its source.
  const dim=spec.unit==='kg'?'g':['l','dl'].includes(spec.unit)?'ml':spec.unit;
  if(dim===source.basis||spec.unit==='piece'&&spec.portion)return C.factor(frozen,spec.quantity,spec.unit,null)*100;
  if(entry.foodSnapshot)return C.factor(frozen,spec.quantity,spec.unit,entry.foodSnapshot.density)*100;
 }
 if(before){const factor=inferredShare(entry.n,C.snapshot(before,100,before.basis,null,keys),keys);if(positive(factor))return factor*100;}
 throw Error('Die ursprüngliche Menge lässt sich nicht eindeutig rekonstruieren. Eintrag prüfen und neu erfassen.');
}
function sources(foods,ownerId,keys){
 const map=new Map();for(const f of foods||[]){try{const c=f.nutritionCorrection,l=link(f,ownerId);if(c?.schema!==1||!validId(c.id)||!l||c.ownerId!==l.ownerId||c.sourceId!==l.sourceId)continue;C.validateFood(f,keys);map.set(key(l),f);}catch{}}
 return map;
}
function recalculate(state,foods,ownerId,keys,foreignRecipes=[]){
 const map=sources(foods,ownerId,keys),aliases=new Map(),stats={entries:0,recipes:0,skipped:[],changed:false};
 for(const f of map.values())aliases.set(f.id,f);
 const recordIssue=(obj,reason,token,kind)=>{stats.skipped.push({kind,id:obj.id,name:obj.name,reason});const next={reason,token};if(!same(obj.nutritionReview,next)){obj.nutritionReview=next;stats.changed=true;}};
 function updateIngredients(items,defaultOwner){
  const next=clone(items),applied=[];
  for(const i of next){const f=map.get(key(link(i.food,defaultOwner)));if(!f)continue;
   const c=f.nutritionCorrection;if(i.food.nutritionCorrectionId===c.id)continue;
   if(i.food.basis!==f.basis)throw Error('Eine Zutat hat eine andere 100-g-/100-ml-Basis. Die ursprüngliche Zutat manuell prüfen.');
   i.food.n=clone(f.n);i.food.q=clone(f.q||{});i.food.nutritionLink=link(f,ownerId);i.food.nutritionCorrectionId=c.id;
   applied.push(c);
  }
  return {ingredients:next,applied};
 }
 for(const r of state.recipes){try{const x=updateIngredients(r.ingredients,ownerId);if(!x.applied.length)continue;C.recipeTotal({...r,ingredients:x.ingredients},keys);r.ingredients=x.ingredients;r.nutritionRecalculatedAt=x.applied.map(c=>c.at).sort().at(-1);delete r.nutritionReview;stats.recipes++;stats.changed=true;}
  catch(e){recordIssue(r,e.message,[...map.values()].map(f=>f.nutritionCorrection.id).join('|'),'recipe');}}
 for(const e of state.entries){
  if(e.kind==='food'){
   const f=e.nutritionLink?map.get(key(e.nutritionLink)):aliases.get(e.sourceId);if(!f||e.nutritionCorrectionId===f.nutritionCorrection.id)continue;
   try{const base=baseAmount(e,f,keys),frozen={...(e.foodSnapshot||f),basis:f.basis,n:clone(f.n),q:clone(f.q||{})};
    e.n=C.snapshot(frozen,base,f.basis,null,keys);e.nutritionBase={quantity:base,basis:f.basis};e.nutritionLink=link(f,ownerId);e.foodSnapshot=stamp(frozen,ownerId);e.nutritionCorrectionId=f.nutritionCorrection.id;e.nutritionRecalculatedAt=f.nutritionCorrection.at;delete e.nutritionReview;stats.entries++;stats.changed=true;
   }catch(err){recordIssue(e,err.message,f.nutritionCorrection.id,'entry');}
  }else if(e.kind==='recipe'&&Array.isArray(e.ingredients)&&e.ingredients.length){
   try{const defaultOwner=e.recipeOwnerId||foreignRecipes.find(r=>r.id===e.recipeId)?.shared?.ownerId||(String(e.recipeId).startsWith('shared-')?'':ownerId);const x=updateIngredients(e.ingredients,defaultOwner);if(!x.applied.length)continue;
    const oldTotal=C.recipeTotal({ingredients:e.ingredients},keys),factor=positive(e.recipeShare)?e.recipeShare:inferredShare(e.n,oldTotal,keys);
    if(!positive(factor))throw Error('Der Anteil des früher erfassten Gerichts ist nicht eindeutig. Eintrag prüfen und neu erfassen.');
    e.n=C.scale(C.recipeTotal({ingredients:x.ingredients},keys),factor);e.ingredients=x.ingredients;e.recipeShare=factor;e.nutritionRecalculatedAt=x.applied.map(c=>c.at).sort().at(-1);delete e.nutritionReview;stats.entries++;stats.changed=true;
   }catch(err){recordIssue(e,err.message,[...map.values()].map(f=>f.nutritionCorrection.id).join('|'),'entry');}
  }
 }
 return stats;
}
function issues(state){return [...state.entries.filter(e=>e.nutritionReview).map(e=>({kind:'entry',id:e.id,name:e.name,date:e.date,reason:e.nutritionReview.reason})),...state.recipes.filter(r=>r.nutritionReview).map(r=>({kind:'recipe',id:r.id,name:r.name,reason:r.nutritionReview.reason}))];}
return {link,stamp,savedFood,captured,share,scaled,legacyAmount,inferredShare,recalculate,issues};
});
