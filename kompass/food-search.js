/* Search aliases are presentation metadata, not new or modified nutrient facts. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else{root.NK_FOOD_SEARCH=factory();root.NK_FOOD_SEARCH.enrich(root.NK_DATA.foods);}})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const clean=s=>String(s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/ß/g,'ss');
 const words=s=>clean(s).split(/[^a-z0-9]+/).filter(Boolean);
 const aliases={
 'blv-290':'Ei Eier Hühnereier Huhn egg eggs roh',
 'blv-1070':'Ei Eier Hühnereier gekochtes hartgekochtes Ei gekocht hartgekocht hart gekocht',
 'blv-410':'Eigelb Eigelbe Dotter Eidotter yolk',
 'blv-411':'Eiweiss Eiweiß Eiklar egg white',
 'blv-1500':'Omelett Omelette Eieromelett',
 'blv-1502':'Käseomelett Käseomelette'
 };
 const pairs=[[/^Kartoffel,/,'Kartoffeln Erdäpfel'],[/^Banane,/,'Bananen'],[/^Apfel,/,'Äpfel Aepfel'],[/^Tomate,/,'Tomaten'],[/^Karotte,/,'Rüebli Ruebli Karotten Möhren Moehren'],[/^Broccoli,/,'Brokkoli'],[/^Zucchetti,/,'Zucchini'],[/^Aubergine,/,'Auberginen'],[/^Peperoni,/,'Paprika'],[/^Blumenkohl,/,'Karfiol'],[/^Rande,/,'Rote Bete Rote Beete'],[/^Kichererbse,/,'Kichererbsen'],[/^Linse,/,'Linsen'],[/^Quark,/,'Topfen'],[/^Poulet/,'Hähnchen Haehnchen Huhn Chicken'],[/^Joghurt|^Jogurt/,'Joghurt Jogurt Yoghurt'],[/^Vollmilch/,'Milch'],[/^Haferflocken/,'Oats Porridgeflocken'],[/^Erdnussbutter/,'Erdnussmus Peanut Butter']];
 function enrich(foods){let changed=0;for(const f of foods){const more=[aliases[f.id]||'',...pairs.filter(([re])=>re.test(f.name)).map(([,a])=>a)].filter(Boolean);if(more.length){f.searchAliases=more.join(' ');changed++;}}return changed;}
 function score(f,query){const q=clean(query).trim(),terms=words(q);if(!terms.length)return 0;const name=clean(f.name),tokens=words(f.name+' '+(f.synonyms||'')+' '+(f.searchAliases||'')+' '+(f.catalog?.code||'')+' '+f.id),all=tokens.join(' ');let sum=0;
 for(const t of terms){if(tokens.includes(t))continue;if(t.length<3)return Infinity;if(tokens.some(w=>w.startsWith(t))){sum+=2;continue;}if(all.includes(t)){sum+=8;continue;}return Infinity;}
 return sum*100+(name===q?0:name.startsWith(q)?1:10)+(/\broh\b/.test(name)?0:1);
 }
 function search(foods,query){return foods.map((f,i)=>({f,i,s:score(f,query)})).filter(x=>Number.isFinite(x.s)).sort((a,b)=>a.s-b.s||a.f.name.localeCompare(b.f.name,'de')||a.i-b.i).map(x=>x.f);}
 return {clean,score,search,enrich};
});
