/* Safe product identifiers and public label parsers. Unknowns are never zero-filled. */
(function(root){'use strict';
const SOURCE='https://www.coop.ch/de/lebensmittel/fleisch-fisch/the-veggie-chef/steaks-filets/redefine-vegane-alternative-zu-flank-steak/p/7451865';
const SEED={id:'coop-7451865',name:'Redefine vegane Alternative zu Flank Steak',basis:'g',density:null,kind:'custom',n:{energy:188,energyKJ:790,protein:26,fat:6.6,saturated:0.8,carbs:4,sugar:1.9,fiber:4.5,salt:0.88,vitB12:2.5},q:{},source:'Coop Produktdeklaration · geprüfter Datenstand 26.09.2026 · kein Live-Abgleich',sourceUrl:SOURCE,lookup:{provider:'Coop',productId:'7451865',quantity:'200 g',checkedAt:'2026-09-26',mode:'snapshot',warnings:['Geprüfter Datenstand, keine Garantie für die aktuelle Rezeptur. Packung vergleichen.']}};
const clone=x=>JSON.parse(JSON.stringify(x));
function normalize(input){
 const s=String(input??'').trim();if(s.length>2400||!s)throw Error('Bitte Produktname, Barcode oder Produktlink eingeben.');
 if(/^\d{8,14}$/.test(s))return {type:'barcode',code:s,key:'off-'+s};
 if(/^(?:https?:\/\/|www\.)/i.test(s)){
  const u=new URL(s.startsWith('www.')?'https://'+s:s);
  if(u.protocol!=='https:'||u.username||u.password||u.port)throw Error('Nur öffentliche HTTPS-Produktlinks ohne Zugangsdaten sind erlaubt.');
  if(['www.coop.ch','coop.ch'].includes(u.hostname)){
   const m=u.pathname.match(/^\/(?:de|fr|it|en)\/[A-Za-z0-9_\-/.]+\/p\/(\d{5,10})\/?$/);
   if(!m||u.pathname.includes('..')||u.pathname.includes('//'))throw Error('Bitte einen vollständigen Coop-Produktlink mit Artikelnummer verwenden.');
   return {type:'coop',id:m[1],key:'coop-'+m[1],url:'https://www.coop.ch'+u.pathname.replace(/\/$/,'')};
  }
  if(/^(?:world|de|ch|fr|en|it)\.openfoodfacts\.org$/.test(u.hostname)){
   const m=u.pathname.match(/^\/(?:product|produkt|produit|prodotto)\/(\d{8,14})(?:\/[^?]*)?$/);
   if(m)return {type:'barcode',code:m[1],key:'off-'+m[1],url:'https://world.openfoodfacts.org/product/'+m[1]};
  }
  throw Error('Linkimport unterstützt aktuell Coop und Open Food Facts. Für andere Seiten Produktname, Barcode oder kopierte Nährwerttabelle verwenden.');
 }
 if(s.length>160||/[\r\n<>]/.test(s)||/^[a-z]+:/i.test(s))throw Error('Bitte einen kurzen Produktnamen eingeben.');
 return {type:'name',query:s,key:s.toLocaleLowerCase('de')};
}
const clean=s=>String(s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/ß/g,'ss');
function matches(f,q){return clean(q).split(/\s+/).filter(Boolean).every(t=>clean(f.name+' '+(f.synonyms||'')+' '+(f.catalog?.brand||'')).includes(t));}
function seed(query){const x=normalize(query);return x.key===SEED.id||x.type==='name'&&matches(SEED,x.query)?clone(SEED):null;}
const map={energy:['energy-kcal',1],energyKJ:['energy',1],protein:['proteins',1],fat:['fat',1],saturated:['saturated-fat',1],carbs:['carbohydrates',1],sugar:['sugars',1],fiber:['fiber',1],salt:['salt',1],vitC:['vitamin-c',1000],vitB1:['vitamin-b1',1000],vitB2:['vitamin-b2',1000],vitB6:['vitamin-b6',1000],vitB12:['vitamin-b12',1e6],vitD:['vitamin-d',1e6],calcium:['calcium',1000],magnesium:['magnesium',1000],iron:['iron',1000],zinc:['zinc',1000],iodine:['iodine',1e6],selenium:['selenium',1e6]};
function fromOFF(p){
 if(!/^\d{8,14}$/.test(String(p?.code)))throw Error('Ungültiger Produktcode.');
 const n={};for(const [key,[k,mul]] of Object.entries(map)){const v=p.nutriments?.[k+'_100g'];n[key]=typeof v==='number'&&Number.isFinite(v)&&v>=0?v*mul:null;}
 if(n.energy===null&&n.energyKJ!==null)n.energy=n.energyKJ/4.184;
 if(!['energy','protein','fat','carbs'].some(k=>n[k]!==null))throw Error('Keine verwertbaren Nährwerte im Produktdatensatz.');
 if(n.energy>950||['protein','fat','carbs'].some(k=>n[k]>100.5))throw Error('Unplausible Nährwerte; bitte Packung verwenden.');
 const name=String(p.product_name_de||p.product_name||'Unbenanntes Produkt').slice(0,180),brand=String(p.brands||'').slice(0,50);
 return {id:'off-'+p.code,name:name+(brand&&!clean(name).includes(clean(brand))?' · '+brand:''),basis:'g',density:null,kind:'custom',n,q:{},source:'Open Food Facts · Community-Angaben · Bezugsmenge und Packung prüfen',sourceUrl:'https://world.openfoodfacts.org/product/'+p.code,lookup:{provider:'Open Food Facts (ODbL)',productId:String(p.code),quantity:String(p.quantity||'').slice(0,80),mode:'live',basisUncertain:true,warnings:['Daten gelten pro 100 g oder 100 ml. Bitte die passende Einheit ausdrücklich bestätigen. Fehlende Angaben bleiben unbekannt.']}};
}
function decode(s){return String(s).replace(/&#(x[\da-f]+|\d+);/gi,(_,n)=>{const v=n[0].toLowerCase()==='x'?parseInt(n.slice(1),16):Number(n);return v>0&&v<=0x10ffff?String.fromCodePoint(v):'';}).replace(/&(nbsp|amp|lt|gt|quot|apos|micro|uuml|auml|ouml|szlig);/gi,(_,n)=>({nbsp:' ',amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",micro:'µ',uuml:'ü',auml:'ä',ouml:'ö',szlig:'ß'}[n.toLowerCase()]));}
function text(s){return decode(s.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,'').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,'').replace(/<[^>]+>/g,' ')).replace(/\s+/g,' ').trim();}
function parseCoop(html,link){
 const x=normalize(link);if(x.type!=='coop'||typeof html!=='string'||html.length>4000000)throw Error('Ungültige Produktseite.');
 const name=text(html.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/i)?.[1]||'');if(!name||name.length>240)throw Error('Produktname nicht sicher erkannt.');
 const n={},q={};let basis=null;
 // Only a single explicit per-100 basis in the nutrition block is safe for automatic transfer.
 const plain=text(html),at=plain.search(/Durchschnittliche Nährwerte pro|Valeurs nutritives moyennes pour|Average nutritional values per/i);
 if(at<0)throw Error('Nährwerttabelle nicht eindeutig lesbar. Bitte Tabelle kopieren oder Packung scannen.');
 const section=plain.slice(at,at+2400).split(/Bewertungen|Filialsuche|Finden Sie eine Filiale|Reviews/)[0];
 const amounts=[...section.matchAll(/(\d+(?:[.,]\d+)?)\s*(g|ml)\b/gi)];
 const header=section.slice(0,section.search(/Energie|Energy|Fett|Fat/i));
 const h=[...header.matchAll(/(\d+(?:[.,]\d+)?)\s*(g|ml)\b/gi)];
 if(h.length!==1||Number(h[0][1])!==100)throw Error('Mehrere oder unklare Spalten: bitte die Nährwerttabelle als Text übernehmen.');basis=h[0][2].toLowerCase();
 const fields=[['energy','(?:Energie|Energy|Brennwert)','kcal'],['energyKJ','(?:Energie|Energy|Brennwert)','kJ'],['saturated','(?:davon )?gesättigte Fettsäuren','g'],['fat','(?:^|\\s)Fett','g'],['carbs','Kohlenhydrate','g'],['sugar','(?:davon )?Zucker','g'],['fiber','(?:Nahrungsfasern(?: \\(Ballaststoffe\\))?|Ballaststoffe)','g'],['protein','(?:Eiweiss|Eiweiß|Protein)','g'],['salt','Salz','g'],['vitB12','Vitamin B12','µg']];
 for(const [k,label,unit] of fields){
  const re=new RegExp(label+'\\s*:?\\s*([<≤]?)\\s*(\\d+(?:[.,]\\d+)?)\\s*'+(unit==='µg'?'[µμu]g':unit)+'\\b','i'),m=section.match(re);
  if(m){if(m[1]){n[k]=null;q[k]=m[1]+' '+m[2]+' '+unit+' pro 100 '+basis;}else n[k]=Number(m[2].replace(',','.'));}
 }
 if(!Number.isFinite(n.protein)||!Number.isFinite(n.fat)||!Number.isFinite(n.carbs))throw Error('Grundnährwerte nicht eindeutig erkannt. Bitte Tabelle kopieren oder Packung scannen.');
 if(n.energy==null&&n.energyKJ!=null)n.energy=n.energyKJ/4.184;
 if(n.energy>950||['protein','fat','carbs'].some(k=>n[k]>100.5))throw Error('Unplausible Tabelle. Bitte Packung prüfen.');
 return {id:x.key,name,basis,density:null,kind:'custom',n,q,source:'Coop · Produktseite abgerufen am '+new Date().toISOString().slice(0,10),sourceUrl:x.url,lookup:{provider:'Coop',productId:x.id,mode:'live',checkedAt:new Date().toISOString(),warnings:['Automatisch gelesene Produktdeklaration. Bezugsmenge, Variante und Packung kontrollieren.']}};
}
const API={normalize,matches,seed,fromOFF,parseCoop};if(typeof module==='object'&&module.exports)module.exports=API;else root.NK_IMPORT_CORE=API;
})(typeof window!=='undefined'?window:globalThis);
