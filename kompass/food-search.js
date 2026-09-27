/* Local name matching only: no nutrient mutations and no external search calls. */
(function(root){'use strict';
const extras={
 'blv-290':['Ei','Eier','Hühnerei','rohes Ei','rohe Eier','Vollei','egg raw'],
 'blv-1070':['Ei','Eier','Hühnerei','gekochtes Ei','gekochte Eier','hartgekochtes Ei','hartgekochte Eier','boiled egg'],
 'blv-410':['Eigelb','Eidotter','Dotter','egg yolk'],
 'blv-411':['Eiweiss','Eiweiß','Eiklar','egg white'],
 'blv-198':['Haferflocken','oats'], 'blv-71':['Magerquark','Quark mager'],
 'blv-351':['Brokkoli','Broccoli'], 'blv-349':['Aubergine','eggplant'],
 'blv-359':['Paprika grün','Peperoni grün'], 'blv-360':['Paprika rot','Peperoni rot'],
 'blv-22':['Hähnchenbrust','Huhn Brust','Hühnerbrust','Pouletbrust','chicken breast'],
 'blv-13457':['Chiasamen','Chia Samen'], 'blv-277':['Leinsamen','flaxseed'],
 'blv-14160':['Edamame','Sojabohnen grün'], 'blv-14055':['Hummus','Humus'],
 'blv-14118':['Seitan'], 'blv-14251':['Tempeh'],
 'blv-13437':['Tofu','Naturtofu','Tofu natur'], 'blv-14090':['Räuchertofu','Tofu geräuchert'],
 'blv-13438':['Seidentofu','Tofu seidig'],
 'blv-14114':['Haferdrink','Hafermilch'], 'blv-14130':['Haferdrink angereichert','Hafermilch angereichert'],
 'blv-14113':['Mandeldrink','Mandelmilch'], 'blv-14131':['Mandeldrink angereichert','Mandelmilch angereichert']
};
function clean(s){return String(s??'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/ß/g,'ss').replace(/ae/g,'a').replace(/oe/g,'o').replace(/ue/g,'u');}
function canonical(t){return /^(ei|eier|huhnerei|huhnereier|eggs?)$/.test(t)?'ei':/^(gekocht(?:e|en|es|er)?|hartgekocht(?:e|en|es|er)?|festgekocht(?:e|en|es|er)?|boiled)$/.test(t)?'gekocht':/^roh(?:e|en|es|er)?$/.test(t)?'roh':t;}
function tokens(s){return clean(s).match(/[a-z0-9]+/g)?.map(canonical)||[];}
function aliases(f){
 const out=[...(extras[f.shared?.sourceId||f.id]||[])],name=clean(f.name);
 if(name.startsWith('teigwaren'))out.push('Pasta Nudeln');
 if(name.startsWith('zucchetti'))out.push('Zucchini');
 if(name.startsWith('kartoffel,'))out.push('Kartoffeln');
 if(name.startsWith('kichererbse,'))out.push('Kichererbsen Chickpeas');
 if(name.startsWith('linse,'))out.push('Linsen');
 if(name.startsWith('joghurt,'))out.push('Jogurt');
 if(name.startsWith('erdnussmus'))out.push('Erdnussbutter');
 if(name.startsWith('reis unpoliert'))out.push('Vollkornreis Naturreis');
 return out;
}
function score(f,query){
 const q=tokens(query);if(!q.length)return 0;
 const names=tokens(f.name),a=aliases(f),words=[...names,...tokens(f.synonyms),...a.flatMap(tokens)];
 let total=0;
 for(const t of q){
  if(words.includes(t)){total+=0;continue;}
  if(t.length<=2)return Infinity;
  if(words.some(w=>w.startsWith(t))){total+=3;continue;}
  if(t.length>4&&words.some(w=>w===t.replace(/(?:en|n|e|s)$/,''))){total+=4;continue;}
  if(words.some(w=>w.includes(t))){total+=9;continue;}
  return Infinity;
 }
 const phrase=q.join(' ');
 if(names.join(' ')===phrase)total-=8;
 if(a.some(x=>tokens(x).join(' ')===phrase))total-=9;
 if(q.length===1&&q[0]==='ei'&&['blv-290','blv-1070'].includes(f.id))total-=20;
 return total;
}
function ranked(foods,query){
 const ids=new Set(),items=[];
 for(const f of foods){if(ids.has(f.id))continue;ids.add(f.id);const s=score(f,query);if(Number.isFinite(s))items.push({f,s});}
 return items.sort((a,b)=>a.s-b.s||a.f.name.localeCompare(b.f.name,'de')).map(x=>x.f);
}
const api={clean,tokens,aliases,score,ranked};
if(typeof module==='object'&&module.exports)module.exports=api;else root.NK_FOOD_SEARCH=api;
})(typeof window!=='undefined'?window:globalThis);
