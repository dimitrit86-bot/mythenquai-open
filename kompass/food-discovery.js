/* Search metadata only: original BLV nutrients, names, IDs and provenance stay unchanged. */
(function(root){'use strict';
const aliases={
 'blv-1070':['Ei','Eier','gekochtes Ei','gekochte Eier','Ei gekocht','Eier gekocht','hartgekochtes Ei','Frühstücksei','Hühnerei gekocht','egg boiled'],
 'blv-290':['Ei','Eier','rohes Ei','rohe Eier','Ei roh','Eier roh','Hühnerei roh','egg raw'],
 'blv-410':['Eigelb','Eidotter','Dotter','egg yolk'],
 'blv-411':['Eiweiss','Eiklar','Eiweiss vom Ei','egg white'],
 'blv-1602':['Rührei','Rühreier','scrambled eggs'],
 'blv-1603':['Rührei mit Kräutern','Kräuterrührei'],
 'blv-1604':['Rührei mit Pilzen','Pilzrührei'],
 'blv-1605':['Rührei mit Käse','Käserührei'],
 'blv-1500':['Omelett','Omelette','Eieromelett'],
 'blv-13437':['Tofu','Naturtofu','Tofu natur'],
 'blv-14090':['Räuchertofu','Rauchtofu'],
 'blv-13438':['Seidentofu','Silken Tofu'],
 'blv-14251':['Tempeh','Tempeh natur'],
 'blv-14118':['Seitan'],
 'blv-14160':['Edamame','Sojabohnen grün']
};
const normalise=v=>String(v||'').toLowerCase().replace(/ä|ae/g,'a').replace(/ö|oe/g,'o').replace(/ü|ue/g,'u').replace(/ß/g,'ss').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^\p{L}\p{N}]+/gu,' ').trim().replace(/\s+/g,' ');
const cache=new WeakMap();
function metadata(f){
 let d=cache.get(f);if(d)return d;
 const extras=[...(aliases[f.id]||[])];const name=normalise(f.name);
 for(const [term,other] of [['broccoli','brokkoli'],['randen','rote beete rote bete'],['peperoni','paprika'],['cottage cheese','hüttenkäse'],['kartoffelstock','kartoffelbrei kartoffelpüree'],['teigwaren','nudeln pasta'],['kichererbse','kichererbsen chickpeas'],['weisse bohne','weisse bohnen'],['sojadrink','sojamilch'],['haferdrink','hafermilch']])if(name.includes(normalise(term)))extras.push(other);
 d={name,alias:extras.map(normalise),words:normalise(f.name+' '+(f.synonyms||'')+' '+(f.catalog?.code||'')+' '+f.id+' '+extras.join(' ')).split(' ')};
 cache.set(f,d);return d;
}
function search(foods,query){
 const q=normalise(query),plural={kartoffeln:'kartoffel',bananen:'banane',tomaten:'tomate',gurken:'gurke',karotten:'karotte',linsen:'linse'},terms=q.split(' ').filter(Boolean).map(t=>plural[t]||t);
 if(!terms.length)return [...foods];
 return foods.map((f,index)=>{
  const d=metadata(f);let score=0;
  for(const t of terms){
   if(d.words.includes(t))score+=20;
   else if(t.length>2&&d.words.some(w=>w.startsWith(t)))score+=8;
   else if(t.length>3&&d.words.some(w=>w.includes(t)))score+=2;
   else return null;
  }
  if(d.name===q)score+=200;
  if(d.alias.includes(q))score+=160;
  if(d.name.startsWith(q+' '))score+=70;
  if(f.kind==='generic')score+=2;
  if(q==='ei'||q==='eier'){if(f.id==='blv-1070')score+=20;if(f.id==='blv-290')score+=15;}
  return {f,score,index};
 }).filter(Boolean).sort((a,b)=>b.score-a.score||a.f.name.localeCompare(b.f.name,'de')||a.index-b.index).map(x=>x.f);
}
const api={normalise,search,aliases};if(typeof module==='object'&&module.exports)module.exports=api;else root.NK_FOOD_DISCOVERY=api;
})(typeof globalThis!=='undefined'?globalThis:this);
