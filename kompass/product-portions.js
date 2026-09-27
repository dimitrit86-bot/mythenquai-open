/* Explicit piece sizes. Stored recipe quantities remain g/ml for older clients. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.NK_PIECES=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const fmt=n=>new Intl.NumberFormat('de-CH',{maximumFractionDigits:3}).format(n);
function positive(value){const s=String(value??'').trim().replace(',','.');if(!/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(s)||!Number.isFinite(+s)||+s<=0)throw Error('Bitte eine positive Menge eingeben.');return +s;}
function validate(food){const p=food?.portion;if(p==null)return null;if(typeof p!=='object'||Array.isArray(p)||typeof p.label!=='string'||!p.label.trim()||p.label.length>40||typeof p.size!=='number'||!Number.isFinite(p.size)||p.size<=0||p.size>100000||!['g','ml'].includes(p.unit)||p.unit!==food.basis)throw Error('Stückportion prüfen: Name, positive Menge und dieselbe Einheit wie die Nährwertbasis (g oder ml) sind erforderlich.');return p;}
function factor(food,quantity){const p=validate(food);if(!p)throw Error('Zuerst hinterlegen, wie viel g oder ml ein Stück dieses Produkts entspricht.');return positive(quantity)*p.size/100;}
function label(food){const p=validate(food);return p?'1 '+p.label+' = '+(p.estimated?'ca. ':'')+fmt(p.size)+' '+p.unit+(p.estimated?' · geschätzt':''):'';}
function units(food){const base=[['g','g'],['kg','kg'],['ml','ml'],['dl','dl'],['l','l']];const p=validate(food);return p?[['piece',p.label+' · '+(p.estimated?'ca. ':'')+fmt(p.size)+' '+p.unit],...base]:base;}
function describe(food,quantity,unit){const q=positive(quantity);if(unit!=='piece')return fmt(q)+' '+unit;const p=validate(food);factor(food,q);return fmt(q)+' '+p.label+' ('+(p.estimated?'ca. ':'')+fmt(q*p.size)+' '+p.unit+')'+(p.estimated?' · geschätzt':'');}
function canonical(item){const i=JSON.parse(JSON.stringify(item));if(i.unit==='piece'){const p=validate(i.food);factor(i.food,i.quantity);i.portionUse={quantity:positive(i.quantity),label:p.label,size:p.size,unit:p.unit,...(p.estimated?{estimated:true,reference:JSON.parse(JSON.stringify(p.reference||{}))}:{})};i.quantity=i.portionUse.quantity*p.size;i.unit=p.unit;}else delete i.portionUse;return i;}
function hydrate(item){const i=JSON.parse(JSON.stringify(item)),p=i.portionUse;if(p&&typeof p.quantity==='number'&&p.quantity>0&&i.food.portion&&p.unit===i.unit&&Math.abs(p.quantity*p.size-i.quantity)<1e-6&&p.size===i.food.portion.size){i.quantity=p.quantity;i.unit='piece';}return i;}
function entryAmount(food,q,unit){return {amountText:describe(food,q,unit),amountSpec:{quantity:positive(q),unit,...(unit==='piece'?{portion:JSON.parse(JSON.stringify(validate(food)))}:{})}};}
function scaledEntry(entry,multiplier){const f=positive(multiplier),a=entry.amountSpec;if(!a)return {amountText:f===1?entry.amountText:fmt(f)+' × ('+entry.amountText+')'};const food={basis:a.portion?.unit||'g',portion:a.portion||null};return entryAmount(food,a.quantity*f,a.unit);}
return {positive,validate,factor,label,units,describe,canonical,hydrate,entryAmount,scaledEntry};
});
