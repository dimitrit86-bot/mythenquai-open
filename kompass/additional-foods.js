/* Manufacturer-label additions, reviewed 2026-09-27. Unknown values stay unknown. */
(function(){'use strict';
const D=window.NK_DATA,C=window.NK;if(!D||!C||window.NK_ADDITIONAL_FOODS)return;
const columns=['energyKJ','energy','fat','saturated','carbs','sugar','fiber','protein','salt'];
const rows=[
 ['planted-chicken-natur','planted.chicken Nature',[607,144,3.4,.6,1.8,.2,4.3,24,1.1],{vitB12:1,iron:4.8},'CH/DACH','Geschnetzeltes Nature Pouletalternative Hähnchen'],
 ['planted-chicken-jerusalemstyle','planted.chicken Jerusalem Style',[899,216,12,1,3.2,.5,3.6,22,1.9],{vitB12:1,iron:4.2},'CH/DACH','Geschnetzeltes Oriental Style Pouletalternative Hähnchen NENI'],
 ['planted-burger-crispy','planted.burger Crispy',[1136,272,14,1.1,20,.5,2.7,15,1.5],{vitB12:1},'DE/AT','Burger Patty paniert Mykoprotein'],
 ['planted-sausage-herbs','planted.bratwurst Herbs',[790,190,13,1.8,.9,.5,.4,16,1.4],{vitB12:1.3,iron:3.2},'CH/DACH','Bratwurst Kräuter Grillwurst Erbse'],
 ['planted-sausage-original','planted.bratwurst Original',[790,190,13,1.8,.9,.5,.4,16,1.4],{vitB12:1.3,iron:3.2},'CH','Bratwurst Grillwurst Erbse'],
 ['planted-chicken-crispy-strips','planted.chicken Crispy Strips',[869,207,9,1,14,.4,3,16,1.5],{vitB12:.9,iron:5.2},'CH/AT','Crispy Strips Pouletalternative Hähnchen Erbse'],
 ['planted-filetstreifen-asia-style','planted.filetstreifen Asia-Style',[645,154,4.1,.4,10,4.4,5.5,17,1.6],{vitB12:1.8,iron:2.8},'CH','Geschnetzeltes Filetstreifen Soja Asia'],
 ['planted-schnitzel','planted.schnitzel Wiener Art',[1030,246,11,1.2,17,.6,3.1,17,1.5],{vitB12:.3,iron:3.6},'CH','Schnitzel paniert Erbse Wiener Art']
];
const keys=D.nutrients.map(x=>x.key),existing=new Set(D.foods.map(f=>f.id)),foods=[];
for(const [slug,name,values,micro,market,aliases] of rows){
 const id='label-'+slug;if(existing.has(id))continue;
 const url='https://eatplanted.com/products/'+slug,n=Object.fromEntries(keys.map(k=>[k,null]));
 columns.forEach((k,i)=>n[k]=values[i]);Object.assign(n,micro);
 const note='Herstellerdeklaration pro 100 g, geprüft 27.09.2026. Länderfassung '+market+'. Packungswerte vergleichen; kein Live-Bestandsabgleich. Numerische Mengenangaben übernommen, nicht gerundete Referenz-Prozente.';
 const f={id,name,basis:'g',density:null,n,q:{},kind:'brand',category:'Vegan · Fleischalternativen',synonyms:'Planted vegan vegetarisch pflanzlich '+aliases,source:note+' '+url,sourceUrl:url,catalog:{brand:'Planted',diet:'vegan',market,group:'Fleischalternativen',url,checkedAt:'2026-09-27'},provenance:{}};
 C.validateFood(f,keys);D.sources[id]=f.source;for(const k of keys)f.provenance[k]=['extraLabel',id];foods.push(f);existing.add(id);
}
D.methods.extraLabel='Deklaration der verlinkten Herstellerseite; keine BLV-Lebensmittelanalyse.';
D.foods.push(...foods);window.NK_ADDITIONAL_FOODS={count:foods.length,checkedAt:'2026-09-27',foods};
})();
