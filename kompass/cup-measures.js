/* Explicit kitchen measures. Cup volumes are not ingredient weights. No assumed density. */
(function(root,f){if(typeof module==='object'&&module.exports)module.exports=f();else root.NK_CUPS=f();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const sizes={cup240:240,cup250:250,cupUS:236.5882365};
const units=[['cup240','Cup · 240 ml (Küche)'],['cup250','Cup · 250 ml (metrisch)'],['cupUS','US cup · 236,6 ml']];
const fractions={'½':'1/2','⅓':'1/3','⅔':'2/3','¼':'1/4','¾':'3/4','⅛':'1/8','⅜':'3/8','⅝':'5/8','⅞':'7/8'};
const copy=x=>JSON.parse(JSON.stringify(x)),fmt=n=>new Intl.NumberFormat('de-CH',{maximumFractionDigits:3}).format(n);
function amount(v){
 let s=String(v??'').trim().replace(/(\d)([½⅓⅔¼¾⅛⅜⅝⅞])/g,'$1 $2').replace(/[½⅓⅔¼¾⅛⅜⅝⅞]/g,c=>fractions[c]).replace(/⁄/g,'/').replace(',','.');let n;
 if(/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(s))n=Number(s);
 else{const m=s.match(/^(?:(\d+)\s+)?(\d+)\s*\/\s*(\d+)$/);if(m&&+m[3]>0)n=Number(m[1]||0)+Number(m[2])/Number(m[3]);}
 if(!Number.isFinite(n)||n<=0||n>1e9)throw Error('Bitte eine positive Menge eingeben, z. B. 0,5, 1/2 oder 1 1/2.');return n;
}
function isCup(unit){return Object.prototype.hasOwnProperty.call(sizes,unit);}
function validate(food){const c=food?.cup;if(c==null)return null;if(typeof c!=='object'||Array.isArray(c)||food.basis!=='g'||!Number.isFinite(c.grams)||c.grams<=0||c.grams>100000||!Number.isFinite(c.ml)||c.ml<=0||c.ml>1000)throw Error('Cup-Umrechnung prüfen: Grammgewicht und Cup-Volumen müssen positiv sein; nur für Produkte pro 100 g.');return c;}
function factor(food,quantity,unit,density){
 if(!isCup(unit))throw Error('Bitte eine bekannte Cup-Grösse auswählen.');const q=amount(quantity),volume=sizes[unit];
 if(food.basis==='ml')return q*volume/100;if(food.basis!=='g')throw Error('Ungültige Nährwertbasis.');
 const c=validate(food);if(c)return q*volume*c.grams/c.ml/100;
 const d=density??food.density;if(d===null||d===undefined||d==='')throw Error('Wie viel Gramm wiegt eine Cup dieser Zutat? Gewicht pro Cup oder eine bekannte Dichte ergänzen.');
 if(!Number.isFinite(Number(d))||Number(d)<=0||Number(d)>100)throw Error('Ungültige Dichte.');return q*volume*Number(d)/100;
}
function label(food){const c=validate(food);return c?'1 Cup ('+fmt(c.ml)+' ml) = '+fmt(c.grams)+' g':'';}
function describe(food,q,unit,density){return fmt(amount(q))+' '+units.find(x=>x[0]===unit)?.[1]+' ('+fmt(factor(food,q,unit,density)*100)+' '+food.basis+')';}
function canonical(item){const i=copy(item);if(!isCup(i.unit)){delete i.cupUse;return i;}const q=amount(i.quantity),baseAmount=factor(i.food,q,i.unit,i.density)*100;i.cupUse={quantity:q,unit:i.unit,baseAmount,basis:i.food.basis};i.quantity=baseAmount;i.unit=i.food.basis;delete i.portionUse;return i;}
function hydrate(item){const i=copy(item),c=i.cupUse;if(c&&isCup(c.unit)&&c.basis===i.unit&&Number.isFinite(c.baseAmount)&&Math.abs(c.baseAmount-i.quantity)<1e-6){try{if(Math.abs(factor(i.food,c.quantity,c.unit,i.density)*100-c.baseAmount)<1e-6){i.quantity=c.quantity;i.unit=c.unit;}}catch{}}return i;}
function entryAmount(food,q,unit,density){const i=canonical({food,quantity:q,unit,density});return {amountText:describe(food,q,unit,density),amountSpec:{quantity:i.quantity,unit:i.unit},cupUse:i.cupUse};}
function scaledEntry(entry,multiplier){const c=entry.cupUse;if(!c||!isCup(c.unit)||c.basis!==entry.amountSpec?.unit||Math.abs(c.baseAmount-entry.amountSpec.quantity)>1e-6)return null;const f=amount(multiplier),n={...c,quantity:c.quantity*f,baseAmount:c.baseAmount*f};return {amountText:fmt(n.quantity)+' '+units.find(x=>x[0]===n.unit)[1]+' ('+fmt(n.baseAmount)+' '+n.basis+')',amountSpec:{quantity:n.baseAmount,unit:n.basis},cupUse:n};}
return {sizes,units,amount,isCup,validate,factor,label,describe,canonical,hydrate,entryAmount,scaledEntry};
});
