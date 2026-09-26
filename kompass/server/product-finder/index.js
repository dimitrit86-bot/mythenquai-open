/* Public nutrient lookup behind the existing household session. No profile reads or writes. */
import './product-import-core.js';
const ORIGIN='https://dimitrit86-bot.github.io',BASE=Deno.env.get('SUPABASE_URL'),SERVICE=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY'),CORE=globalThis.NK_PRODUCT_CORE;
const UA='Naehrstoff-Kompass/1.4 (github.com/dimitrit86-bot/mythenquai-open)';
const cache=new Map();let lastSearch=0,lastPage=0;
const hash=async s=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s)))).map(x=>x.toString(16).padStart(2,'0')).join('');
async function limited(response,max=3500000){if(Number(response.headers.get('content-length')||0)>max)throw Error('Antwort zu gross.');const reader=response.body.getReader();let size=0,chunks=[];try{while(true){const {done,value}=await reader.read();if(done)break;size+=value.length;if(size>max)throw Error('Antwort zu gross.');chunks.push(value);}}catch(e){await reader.cancel();throw e;}const all=new Uint8Array(size);let offset=0;for(const c of chunks){all.set(c,offset);offset+=c.length;}return new TextDecoder().decode(all);}
async function fetchPublic(url,type){let u=url;for(let i=0;i<3;i++){const r=await fetch(u,{headers:{'User-Agent':UA,'Accept':type==='coop'?'text/html':'application/json','Accept-Language':'de-CH,de;q=0.9'},redirect:'manual',signal:AbortSignal.timeout(15000)});if(r.status>=300&&r.status<400){const target=new URL(r.headers.get('location')||'',u).href;u=type==='coop'?CORE.coopURL(target):target;if(type!=='coop'&&new URL(u).origin!=='https://world.openfoodfacts.org')throw Error('Nicht unterstützte Weiterleitung.');continue;}if(!r.ok)throw Error(type==='coop'?'Coop-Seite ist für den automatischen Abruf nicht zugänglich. Namen, Packungsfoto oder Nährwerttext verwenden.':'Produktsuche vorübergehend nicht erreichbar.');return await limited(r);}throw Error('Zu viele Weiterleitungen.');}
function remember(key,value){if(cache.size>=80)cache.delete(cache.keys().next().value);cache.set(key,{at:Date.now(),value});}
Deno.serve(async req=>{
 const origin=req.headers.get('origin'),headers={'Content-Type':'application/json','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Access-Control-Allow-Origin':ORIGIN,'Access-Control-Allow-Headers':'content-type,x-nk-session','Access-Control-Allow-Methods':'POST,OPTIONS','Vary':'Origin'},reply=(data,status=200)=>new Response(JSON.stringify(data),{status,headers});
 if(origin&&origin!==ORIGIN)return reply({error:'Unerlaubte Herkunft.'},403);if(req.method==='OPTIONS')return new Response(null,{status:204,headers});if(req.method!=='POST')return reply({error:'Methode nicht erlaubt.'},405);
 const token=req.headers.get('x-nk-session')||'';if(!/^[a-f0-9]{64}$/.test(token))return reply({error:'Bitte anmelden.'},401);
 try{
  const r=await fetch(BASE+'/rest/v1/nk_sessions?select=expires_at&token_hash=eq.'+await hash(token)+'&expires_at=gt.'+encodeURIComponent(new Date().toISOString())+'&limit=1',{headers:{apikey:SERVICE,Authorization:'Bearer '+SERVICE},signal:AbortSignal.timeout(5000)});
  if(!r.ok)throw Error('Sitzungsprüfung nicht erreichbar.');if(!(await r.json()).length)return reply({error:'Sitzung abgelaufen. Bitte erneut anmelden.'},401);
  let b;try{b=JSON.parse(await limited(req,4096));}catch{return reply({error:'Ungültige oder zu grosse Anfrage.'},400);}
  if(b?.action==='link'){
   let url;try{url=CORE.coopURL(b.url);}catch(e){return reply({error:e.message},400);}const old=cache.get(url);if(old&&Date.now()-old.at<21600000)return reply({...old.value,cached:true});
   if(Date.now()-lastPage<3000)return reply({error:'Bitte kurz vor dem nächsten Linkabruf warten.'},429);lastPage=Date.now();
   try{const html=await fetchPublic(url,'coop'),food=CORE.parseCoop(html,url);const result={food,source:'Coop',fetchedAt:new Date().toISOString()};remember(url,result);return reply(result);}catch(e){return reply({error:e.message,query:CORE.queryFromURL(url)},422);}
  }
  if(b?.action!=='search'||typeof b.query!=='string'||b.query.trim().length<2||b.query.length>120||/[\x00-\x1f]/.test(b.query))return reply({error:'Bitte einen Produktnamen mit 2–120 Zeichen eingeben.'},400);
  const query=b.query.trim(),key='q:'+query.toLowerCase(),old=cache.get(key);if(old&&Date.now()-old.at<3600000)return reply({...old.value,cached:true});
  if(Date.now()-lastSearch<6500)return reply({error:'Bitte etwa 7 Sekunden bis zur nächsten Online-Suche warten. Vorhandene Produkte kannst du sofort suchen.'},429);lastSearch=Date.now();
  const params=new URLSearchParams({search_terms:query,search_simple:'1',action:'process',json:'1',page_size:'20',fields:'code,product_name,product_name_de,brands,quantity,nutriments,nutrition_data_per'});
  const data=JSON.parse(await fetchPublic('https://world.openfoodfacts.org/cgi/search.pl?'+params,'off'));
  if(!Array.isArray(data.products))throw Error('Ungültige Antwort des Produktdienstes.');
  const products=data.products.slice(0,20).filter(p=>/^\d{8,14}$/.test(String(p.code||''))).map(p=>({code:p.code,product_name:p.product_name,product_name_de:p.product_name_de,brands:p.brands,quantity:p.quantity,nutriments:p.nutriments||{},nutrition_data_per:p.nutrition_data_per}));
  const result={products,source:'Open Food Facts',license:'ODbL 1.0',fetchedAt:new Date().toISOString()};remember(key,result);return reply(result);
 }catch{return reply({error:'Online-Produktsuche momentan nicht erreichbar. Vorhandene Produkte, Packungsfoto oder Nährwerttext bleiben nutzbar.'},503);}
});
