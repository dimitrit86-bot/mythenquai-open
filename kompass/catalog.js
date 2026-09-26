/* Additive public catalog. No reads/writes to personal storage, profiles, auth or APIs. */
(function(){'use strict';
const D=window.NK_DATA,V=window.NK_VEGGIE,C=window.NK;
if(!D||!V||!C||window.NK_CATALOG)return;
const keys=D.nutrients.map(n=>n.key),baseCount=D.foods.length,ids=new Set(D.foods.map(f=>f.id));
const columns=['energyKJ','energy','fat','saturated','carbs','sugar','fiber','protein','salt'];
const foods=V.rows.map(row=>{
 const r=Object.fromEntries(V.fields.map((k,i)=>[k,row[i]])),n=Object.fromEntries(keys.map(k=>[k,null]));
 if(ids.has(r.id))throw Error('Doppelte Katalog-ID: '+r.id);
 if(r.values.length!==columns.length||!['vegan','vegetarisch'].includes(r.diet))throw Error('Ungültiger Katalogdatensatz.');
 columns.forEach((k,i)=>n[k]=r.values[i]);
 for(const [k,v] of Object.entries(r.micro)){if(!keys.includes(k))throw Error('Unbekannter Nährstoff: '+k);n[k]=v;}
 const sourceUrl=new URL(r.url);if(sourceUrl.protocol!=='https:')throw Error('Ungültige Quellenadresse.');
 const f={id:r.id,name:r.name,synonyms:[r.aliases,r.brand,r.group,'Veggie Ersatzprodukt',r.diet==='vegan'?'vegan pflanzlich vegetarisch':'vegetarisch'].join(' '),category:(r.diet==='vegan'?'Vegan':'Vegetarisch (mit Ei/Milch)')+' · '+r.group,density:null,basis:r.basis,kind:'brand',source:(sourceUrl.hostname==='www.coop.ch'?'Produktdeklaration Coop: ':'Hersteller: ')+r.brand+' · '+r.market+' · '+V.checkedAt+' · '+r.url,n,q:{...r.quality},provenance:{},catalog:{...r,checkedAt:V.checkedAt}};
 C.validateFood(f,keys);if(n.sugar!==null&&n.carbs!==null&&n.sugar>n.carbs+.05)throw Error('Zucker über Kohlenhydraten.');if(n.saturated!==null&&n.fat!==null&&n.saturated>n.fat+.05)throw Error('Gesättigtes Fett über Gesamtfett.');ids.add(f.id);return f;
});
D.methods.catalogLabel='Deklarierte Produktwerte; separate Ergänzung zur BLV-Basis.';
for(const f of foods){
 D.sources[f.id]=f.source+(f.catalog.notes?' · '+f.catalog.notes:'');
 for(const k of keys)f.provenance[k]=['catalogLabel',f.id];
}
D.foods.push(...foods);
const byId=new Map(foods.map(f=>[f.id,f]));
window.NK_CATALOG={version:V.version,checkedAt:V.checkedAt,baseCount,added:foods.length,total:D.foods.length,foods};
})();
