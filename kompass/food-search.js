/* Names and exact-word ranking only. No nutrient values or source records changed. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.NK_FOOD_SEARCH=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const clean=s=>String(s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/ß/g,'ss');
const names={'blv-1070':'Ei Eier gekochtes gekochte gekocht hartgekocht hart festgekocht Huhn','blv-290':'Ei Eier rohes rohe roh Huhn','blv-410':'Eigelb Eidotter Dotter','blv-411':'Eiweiss Eiweiß Eiklar'};
const groups=[[/^Hühnerei, ganz,/i,'Ei Eier Huhn'],[/öl(?:,|$)/i,'Öl Oel'],[/^Linse[, ]/i,'Linsen'],[/^Kichererbse[, ]/i,'Kichererbsen'],[/^Kartoffel[, ]/i,'Kartoffeln Erdapfel'],[/^Karotte[, ]/i,'Karotten Möhre Möhren Rüebli'],[/^Broccoli[, ]/i,'Brokkoli'],[/^Peperoni[, ]/i,'Paprika'],[/^Aubergine[, ]/i,'Auberginen'],[/^Zucchetti[, ]/i,'Zucchini'],[/^Champignon[, ]/i,'Champignons Pilz Pilze'],[/^Poulet[, ]/i,'Hähnchen Huhn Hühnchen'],[/^Sojabohne[, ]/i,'Sojabohnen'],[/^Edamame/i,'Sojabohnen unreif'],[/^Quark/i,'Topfen'],[/^Joghurt/i,'Jogurt'],[/^Erdnuss[, ]/i,'Erdnüsse'],[/^Walnuss[, ]/i,'Baumnuss Baumnüsse Walnüsse']];
function alias(f){return (names[f.id]||'')+' '+groups.filter(([re])=>re.test(f.name)).map(([,v])=>v).join(' ');}
function select(foods,query){const q=clean(query).trim(),terms=q.split(/\s+/).filter(Boolean);if(!terms.length)return foods.slice();const result=[];
 for(const f of foods){const name=clean(f.name),extra=clean((f.synonyms||'')+' '+alias(f)),text=name+' '+extra,words=text.split(/[^a-z0-9]+/).filter(Boolean);if(!terms.every(t=>words.includes(t)||(t.length>2&&(text.includes(t)||t.endsWith('n')&&text.includes(t.slice(0,-1))))))continue;
 let score=name===q?0:terms.every(t=>name.split(/[^a-z0-9]+/).includes(t))?1:terms.every(t=>words.includes(t))?2:3;
 if(names[f.id]&&terms.some(t=>['ei','eier'].includes(t)))score-=2;
 result.push({f,score});}
 return result.sort((a,b)=>a.score-b.score||a.f.name.localeCompare(b.f.name,'de')).map(x=>x.f);
}
return {select,alias,clean};
});
