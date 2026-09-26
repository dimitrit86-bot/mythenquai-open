/* Pure portion conversion. No network, personal storage, or assumptions about density. */
(function(root){'use strict';
function amount(value){
 const s=String(value??'').trim();
 if(!/^(?:\d+(?:[.,]\d*)?|[.,]\d+)$/.test(s))throw Error('Bitte eine gültige Bezugsmenge eingeben, zum Beispiel 30 oder 30,5.');
 const n=Number(s.replace(',','.'));
 if(!Number.isFinite(n)||n<=0||n>100000)throw Error('Die Bezugsmenge muss grösser als 0 und höchstens 100’000 sein.');
 return n;
}
function convert(values,notes,quantity,unit){
 const size=amount(quantity);
 if(!['g','ml'].includes(unit))throw Error('Bitte Gramm (g) oder Milliliter (ml) wählen. Keine Umrechnung zwischen Gewicht und Volumen.');
 const factor=100/size,n={},q={};
 for(const [key,v] of Object.entries(values||{})){
  if(v===null||v===undefined||v===''){n[key]=null;continue;}
  const s=String(v).trim();
  if(!/^(?:\d+(?:[.,]\d*)?|[.,]\d+)$/.test(s))throw Error('Ungültiger Ausgangswert für '+key+'. Bitte korrigieren oder das Feld leer lassen.');
  const value=Number(s.replace(',','.'))*factor;
  if(!Number.isFinite(value)||value<0||value>1e9)throw Error('Wert für '+key+' ausserhalb des unterstützten Bereichs.');
  n[key]=value; // Keep full precision; round only when displaying.
 }
 for(const [key,note] of Object.entries(notes||{})){
  if(n[key]!==null&&n[key]!==undefined)continue;
  // A declared bound is not an exact amount. Keep it unknown, with a scaled bound.
  const m=String(note).trim().match(/^([<≤])\s*(\d+(?:[.,]\d+)?)\s*(kcal|kJ|mg|[µμu]g|g)\s*$/i);
  q[key]=m?`${m[1]} ${Number((Number(m[2].replace(',','.'))*factor).toPrecision(12))} ${m[3]} pro 100 ${unit} (Grenzwert, kein exakter Wert)`:`${note} · Originalangabe pro ${size} ${unit}; unbekannt, nicht als Null gerechnet.`;
 }
 return {n,q,basis:unit,sourceAmount:size,factor};
}
function hints(text){
 const result=[];
 const lines=String(text||'').replace(/\r/g,'').split('\n');
 for(const line of lines){
  if(!/\b(?:pro|per|je|por(?:tion)?|serving|100\s*(?:g|ml))\b/i.test(line))continue;
  // Restrict to header-looking lines: nutrient labels, calories and daily reference notes are not portions.
  if(/fett|fat|protein|eiwei|salz|salt|kcal|\bkj\b|vitamin|tages|daily|referenz|decken/i.test(line))continue;
  for(const m of line.matchAll(/(\d+(?:[.,]\d+)?)\s*(ml|g)\b/gi)){
   const size=Number(m[1].replace(',','.')),unit=m[2].toLowerCase();
   if(size>0&&size<=100000&&!result.some(x=>x.amount===size&&x.unit===unit))result.push({amount:size,unit});
  }
 }
 return result.slice(0,6);
}
const API={amount,convert,hints};
if(typeof module==='object'&&module.exports)module.exports=API;else root.NK_PORTIONS=API;
})(typeof window!=='undefined'?window:globalThis);
