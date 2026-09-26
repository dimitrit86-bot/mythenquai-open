/* Pure public-product import helpers. Never execute markup or invent missing nutrients. */
(function(root){'use strict';
function coopURL(value){
 let u;try{u=new URL(String(value).trim());}catch{throw Error('Bitte einen vollständigen HTTPS-Produktlink eingeben.');}
 if(u.protocol!=='https:'||u.username||u.password||u.port||!['www.coop.ch','coop.ch'].includes(u.hostname))throw Error('Direkter Linkimport unterstützt derzeit ausschliesslich HTTPS-Produktseiten von Coop. Andere Produkte bitte über Namen, Barcode oder Foto suchen.');
 if(!/^\/de\/[a-z0-9/-]+\/p\/\d{5,12}\/?$/i.test(u.pathname))throw Error('Bitte einen deutschen Coop-Produktlink mit /p/ und Artikelnummer verwenden.');
 return 'https://www.coop.ch'+u.pathname.replace(/\/$/,'');
}
function queryFromURL(value){const url=coopURL(value),parts=new URL(url).pathname.split('/'),slug=parts[parts.length-3];return slug.split('-').filter(x=>!['vegane','veganer','vegetarische','alternative','zu','auf','basis','von','und'].includes(x)).join(' ').slice(0,120);}
function text(value){return String(value||'').replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,'').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,'').replace(/<(?:br|\/p|\/li|\/tr|\/h[1-6]|\/div)\b[^>]*>/gi,'\n').replace(/<[^>]+>/g,' ').replace(/&(?:nbsp|#160);/gi,' ').replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&#(\d+);/g,(_,x)=>+x<0x110000?String.fromCodePoint(+x):'').replace(/[ \t]+/g,' ').trim();}
const F=[['saturated',/davon gesättigte Fettsäuren|gesättigte Fettsäuren/i,'g'],['sugar',/davon Zucker|Zucker/i,'g'],['fiber',/Nahrungsfasern(?:\s*\(Ballaststoffe\))?|Ballaststoffe/i,'g'],['protein',/Eiweiss|Eiweiß|Protein/i,'g'],['carbs',/Kohlenhydrate/i,'g'],['fat',/Fett/i,'g'],['salt',/Salz/i,'g'],['vitB12',/Vitamin B\s*12/i,'µg'],['vitD',/Vitamin D/i,'µg'],['calcium',/Calcium|Kalzium/i,'mg'],['iron',/Eisen/i,'mg'],['vitB2',/Vitamin B\s*2|Riboflavin/i,'mg'],['magnesium',/Magnesium/i,'mg'],['zinc',/Zink/i,'mg'],['iodine',/Jod/i,'µg'],['vitC',/Vitamin C/i,'mg']];
function parseCoop(html,url,now=new Date().toISOString()){
 const canonical=coopURL(url),id=canonical.split('/').at(-1),plain=text(html);
 const start=plain.search(/Durchschnittliche Nährwerte pro\s*:/i);if(start<0)throw Error('Keine eindeutig erkennbare Nährwerttabelle auf der Coop-Seite. Bitte Packungsfoto oder Nährwerttext verwenden.');
 const section=plain.slice(start,start+2200).split(/Bewertungen|Finden Sie eine Filiale/i)[0],basisMatch=section.match(/pro\s*:\s*100\s*(g|ml)\b/i);
 if(!basisMatch)throw Error('Die Bezugsmenge 100 g/ml konnte nicht eindeutig bestätigt werden.');
 const n={},q={};const units={g:1,mg:.001,'µg':.000001};
 for(const line of section.split('\n').map(x=>x.trim()).filter(Boolean)){
  for(const [key,re,unit] of F){const m=line.match(re);if(!m)continue;const part=line.slice(m.index+m[0].length),v=part.match(/^\s*([<≤]?)\s*(\d+(?:[.,]\d+)?)\s*(µg|μg|ug|mg|g)\b/i);if(!v)break;
   const raw=v[0].trim();if(v[1]){n[key]=null;q[key]=raw+' pro 100 '+basisMatch[1];}else n[key]=Number(v[2].replace(',','.'))*units[v[3].replace(/[μu]g/,'µg')]/units[unit];break;}
  if(/Energie|Brennwert/i.test(line)){for(const [key,unit] of [['energy','kcal'],['energyKJ','kJ']]){const m=line.match(new RegExp('(\\d+(?:[.,]\\d+)?)\\s*'+unit+'\\b','i'));if(m)n[key]=Number(m[1].replace(',','.'));}}
 }
 if(n.energy==null&&n.energyKJ!=null){n.energy=n.energyKJ/4.184;q.energy='Aus kJ umgerechnet.';}
 if(!Number.isFinite(n.protein)||!Number.isFinite(n.fat)||!Number.isFinite(n.carbs))throw Error('Grundnährwerte konnten nicht sicher gelesen werden. Es wurden keine Werte übernommen.');
 for(const k of ['protein','fat','carbs','sugar','saturated','fiber','salt'])if(n[k]!=null&&(!Number.isFinite(n[k])||n[k]<0||n[k]>100))throw Error('Unplausible Nährwertangabe. Bitte Packung kontrollieren.');
 if(n.energy!=null&&n.energy>950)throw Error('Unplausible Energieangabe.');
 const name=text(html.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/i)?.[1])||queryFromURL(canonical);
 return {id:'coop-'+id,name:name.slice(0,230),basis:basisMatch[1],n,q,density:null,kind:'custom',source:'Coop-Produktdeklaration · abgerufen '+now.slice(0,10),sourceUrl:canonical,importedAt:now};
}
const api={coopURL,queryFromURL,parseCoop};if(typeof module==='object'&&module.exports)module.exports=api;else root.NK_PRODUCT_CORE=api;
})(typeof globalThis!=='undefined'?globalThis:this);
