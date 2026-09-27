/* Two additional brand declarations, not BLV values. Checked 2026-09-27. */
(function(){'use strict';const D=window.NK_DATA,C=window.NK;if(!D||!C)return;
const rows=[
 {id:'label-koro-yeast-flakes',name:'KoRo Hefeflocken',synonyms:'Nährhefe Edelhefeflocken vegan vegetarisch nutritional yeast',category:'Würzmittel / Hefeflocken',url:'https://www.koro-shop.at/hefeflocken-500-g',market:'AT',n:{energyKJ:1426,energy:341,fat:6.4,saturated:1.2,carbs:9.1,sugar:0,fiber:22,protein:48,salt:0.2}},
 {id:'label-koro-soya-fine',name:'KoRo Bio Sojagranulat fein, trocken',synonyms:'Sojahack Sojagranulat Sojaschnetzel fein vegan vegetarisch',category:'Fleischalternativen / Sojagranulat',url:'https://www.koro.fr/petits-eminces-de-soja-bio-1-kg',market:'FR',n:{energyKJ:1687,energy:399,fat:11,saturated:2.3,carbs:17,sugar:7.7,fiber:17,protein:52,salt:0.02}}
];
const keys=D.nutrients.map(x=>x.key);D.methods.extraLabel='Deklaration der verlinkten Markenproduktseite; fehlende Nährstoffe bleiben unbekannt.';
let added=0;
for(const r of rows){if(D.foods.some(f=>f.id===r.id))continue;
 const f={id:r.id,name:r.name,synonyms:r.synonyms,category:r.category,basis:'g',density:null,kind:'brand',source:'KoRo-Produktdeklaration · '+r.market+' · geprüft 27.09.2026 · '+r.url+' · Trockenprodukt; Packung vergleichen.',sourceUrl:r.url,n:Object.fromEntries(keys.map(k=>[k,r.n[k]??null])),q:{},provenance:{},catalog:{brand:'KoRo',diet:'vegan',market:r.market,checkedAt:'2026-09-27',url:r.url}};
 C.validateFood(f,keys);D.sources[r.id]=f.source;for(const k of keys)f.provenance[k]=['extraLabel',r.id];D.foods.push(f);added++;
}
window.NK_EVERYDAY={version:'1.8.0',added,sourceDate:'2026-09-27'};
})();
