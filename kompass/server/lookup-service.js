/* Authenticated read-only product lookup. No database writes or forwarding of household credentials. */
(function(root){'use strict';
function createHandler({core,fetcher=fetch,base,service,now=()=>Date.now()}){
 const origin='https://dimitrit86-bot.github.io',cache=new Map();let requests=[];
 const headers={'Content-Type':'application/json','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Access-Control-Allow-Origin':origin,'Access-Control-Allow-Headers':'content-type,x-nk-session','Access-Control-Allow-Methods':'POST,OPTIONS','Vary':'Origin'};
 const reply=(data,status=200)=>new Response(JSON.stringify(data),{status,headers});
 const ua='Naehrstoff-Kompass/1.4 (https://github.com/dimitrit86-bot/mythenquai-open)';
 async function body(r,max){if(Number(r.headers.get('content-length')||0)>max)throw Error('Antwort zu gross.');const reader=r.body.getReader();let size=0,parts=[];try{while(true){const {done,value}=await reader.read();if(done)break;size+=value.length;if(size>max)throw Error('Antwort zu gross.');parts.push(value);}}finally{await reader.cancel().catch(()=>{});}const joined=new Uint8Array(size);let offset=0;for(const part of parts){joined.set(part,offset);offset+=part.length;}return new TextDecoder().decode(joined);}
 async function external(url,kind,id){
  for(let step=0;step<3;step++){
   const r=await fetcher(url,{redirect:'manual',headers:{'User-Agent':ua,'Accept':kind==='coop'?'text/html':'application/json','Accept-Language':'de-CH,de;q=0.9'},signal:AbortSignal.timeout(16000)});
   if([301,302,303,307,308].includes(r.status)){
    if(kind!=='coop')throw Error('Unerwartete Weiterleitung der Datenquelle.');
    const next=core.normalize(new URL(r.headers.get('location')||'',url).href);
    if(next.type!=='coop'||next.id!==id)throw Error('Produktweiterleitung konnte nicht sicher geprüft werden.');url=next.url;continue;
   }
   if(!r.ok)throw Error(r.status===403?'Die Händlerseite erlaubt diesen automatischen Abruf nicht.':r.status===429?'Die Datenquelle begrenzt die Abfragen. Bitte später erneut versuchen.':'Die Datenquelle ist gerade nicht erreichbar.');
   return await body(r,kind==='coop'?4000000:2000000);
  }throw Error('Zu viele Weiterleitungen.');
 }
 return async req=>{
  if(req.headers.get('origin')&&req.headers.get('origin')!==origin)return reply({error:'Unerlaubte Herkunft.'},403);
  if(req.method==='OPTIONS')return new Response(null,{status:204,headers});
  if(req.method!=='POST')return reply({error:'Methode nicht erlaubt.'},405);
  const token=req.headers.get('x-nk-session')||'';
  if(!/^[a-f0-9]{64}$/.test(token))return reply({error:'Bitte anmelden.'},401);
  try{
   const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(token)))).map(x=>x.toString(16).padStart(2,'0')).join('');
   const auth=await fetcher(base+'/rest/v1/nk_sessions?select=expires_at&token_hash=eq.'+hash+'&expires_at=gt.'+encodeURIComponent(new Date(now()).toISOString())+'&limit=1',{headers:{apikey:service,Authorization:'Bearer '+service},signal:AbortSignal.timeout(8000)});
   if(!auth.ok)throw Error('Anmeldung konnte nicht geprüft werden.');
   const sessions=await auth.json();if(!Array.isArray(sessions)||!sessions.length)return reply({error:'Sitzung abgelaufen. Bitte erneut anmelden.'},401);
   if(Number(req.headers.get('content-length')||0)>5000)return reply({error:'Anfrage zu gross.'},413);
   const raw=await body(req,5000);let input;try{input=JSON.parse(raw);}catch{return reply({error:'Ungültige Anfrage.'},400);}
   if(input.action!=='lookup')return reply({error:'Unbekannte Aktion.'},400);
   let parsed;try{parsed=core.normalize(input.input);}catch(e){return reply({error:e.message},400);}
   const hit=cache.get(parsed.key);if(hit&&now()-hit.at<3600000)return reply({...hit.data,cached:true});
   requests=requests.filter(t=>now()-t<60000);if(requests.length>=8)return reply({error:'Bitte kurz warten. Höchstens acht neue Online-Abfragen pro Minute.'},429);requests.push(now());
   let data;
   try{
    if(parsed.type==='coop')data={products:[core.parseCoop(await external(parsed.url,'coop',parsed.id),parsed.url)]};
    else if(parsed.type==='barcode'){
     const j=JSON.parse(await external('https://world.openfoodfacts.org/api/v3.6/product/'+parsed.code+'.json?fields=code,product_name,product_name_de,brands,quantity,nutriments','off'));
     if(!j.product)throw Error('Produkt nicht gefunden.');data={products:[core.fromOFF({...j.product,code:j.product.code||parsed.code})]};
    }else{
     // Documented legacy full-text endpoint; v2 search ignores free-text queries.
     const q=new URLSearchParams({search_terms:parsed.query,search_simple:'1',action:'process',json:'1',page_size:'15',fields:'code,product_name,product_name_de,brands,quantity,nutriments'});
     const j=JSON.parse(await external('https://world.openfoodfacts.org/cgi/search.pl?'+q,'off'));
     if(!Array.isArray(j.products))throw Error('Die Produktsuche liefert kein lesbares Ergebnis.');
     data={products:j.products.flatMap(p=>{try{return [core.fromOFF(p)];}catch{return [];}}),note:'Open Food Facts · Community-Daten; Treffer und Packung vergleichen.'};
    }
   }catch(e){const fallback=core.seed(input.input);if(!fallback)return reply({error:e.message+' Alternativ Barcode, Packungsfoto oder kopierte Nährwerttabelle verwenden.'},422);data={products:[fallback],note:'Liveabruf nicht möglich. Geprüfter Datenstand 26.09.2026, nicht live aktualisiert.'};}
   if(cache.size>=60)cache.delete(cache.keys().next().value);cache.set(parsed.key,{at:now(),data});return reply(data);
  }catch(e){return reply({error:e?.name==='TimeoutError'?'Zeitüberschreitung. Vorhandene Einträge bleiben unverändert.':'Produktsuche momentan nicht erreichbar. Bitte später erneut versuchen oder Packung scannen.'},503);}
 };
}
const API={createHandler};if(typeof module==='object'&&module.exports)module.exports=API;else root.NK_LOOKUP_SERVICE=API;
})(globalThis);
