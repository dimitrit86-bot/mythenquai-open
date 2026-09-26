/* Private household library. Read-only; existing custom sessions are validated server-side. */
const BASE=Deno.env.get('SUPABASE_URL');
const SERVICE=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
const ORIGIN='https://dimitrit86-bot.github.io';
const encoder=new TextEncoder();
const sha=async s=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',encoder.encode(s)))).map(x=>x.toString(16).padStart(2,'0')).join('');
async function read(path){
 const r=await fetch(BASE+'/rest/v1/'+path,{headers:{apikey:SERVICE,Authorization:'Bearer '+SERVICE},signal:AbortSignal.timeout(15000)});
 if(!r.ok)throw Error('Read failed');return await r.json();
}
function pick(o,keys){const out={};for(const k of keys)if(Object.prototype.hasOwnProperty.call(o||{},k))out[k]=o[k];return out;}
function food(f){
 if(!f||! /^[A-Za-z0-9_-]{1,100}$/.test(f.id)||typeof f.name!=='string'||!f.name.trim()||f.name.length>240||!['g','ml'].includes(f.basis)||!f.n||typeof f.n!=='object'||Array.isArray(f.n))throw Error('Invalid item');
 return pick(f,['id','name','basis','n','q','source','sourceUrl','density','synonyms','category']);
}
function recipe(r){
 if(!r||! /^[A-Za-z0-9_-]{1,100}$/.test(r.id)||typeof r.name!=='string'||!r.name.trim()||r.name.length>240||!Array.isArray(r.ingredients)||!r.ingredients.length||r.ingredients.length>200)throw Error('Invalid item');
 const out=pick(r,['id','name','servings','finalWeight','notes','version','updatedAt']);
 out.ingredients=r.ingredients.map(i=>({...pick(i,['quantity','unit','density']),food:food(i.food)}));return out;
}
Deno.serve(async req=>{
 const origin=req.headers.get('origin');const allowed=!origin||origin===ORIGIN;
 const headers={'Content-Type':'application/json','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Access-Control-Allow-Origin':ORIGIN,'Access-Control-Allow-Headers':'content-type,x-nk-session','Access-Control-Allow-Methods':'POST,OPTIONS','Vary':'Origin'};
 const reply=(data,status=200)=>new Response(JSON.stringify(data),{status,headers});
 if(!allowed)return reply({error:'Unerlaubte Herkunft.'},403);
 if(req.method==='OPTIONS')return new Response(null,{status:204,headers});
 try{
  const token=req.headers.get('x-nk-session')||'';
  if(!/^[a-f0-9]{64}$/.test(token))return reply({error:'Bitte anmelden.'},401);
  const sessions=await read('nk_sessions?select=expires_at&token_hash=eq.'+await sha(token)+'&expires_at=gt.'+encodeURIComponent(new Date().toISOString())+'&limit=1');
  if(!sessions.length)return reply({error:'Sitzung abgelaufen. Bitte erneut anmelden.'},401);
  if(req.method!=='POST')return reply({error:'Methode nicht erlaubt.'},405);
  const text=await req.text();if(text.length>1000)return reply({error:'Anfrage zu gross.'},413);
  let body;try{body=JSON.parse(text);}catch{return reply({error:'Ungültige Anfrage.'},400);}
  if(body?.action!=='list')return reply({error:'Unbekannte Aktion.'},400);
  // Project hosts one private household. No diary or reference-profile fields are selected.
  const rows=await read('nk_profiles?select=id,name,foods:state->foods,recipes:state->recipes&order=name.asc&limit=9');
  if(rows.length>8)return reply({error:'Profilgrenze überschritten.'},409);
  const items=[];let skipped=0;
  for(const p of rows){for(const [kind,parse] of [['food',food],['recipe',recipe]]){
   const values=kind==='food'?p.foods:p.recipes;
   for(const value of Array.isArray(values)?values:[]){try{
    const item=parse(value);items.push({key:'shared-'+await sha(p.id+'/'+kind+'/'+item.id),kind,ownerId:p.id,ownerName:p.name,item});
    if(items.length>10000)return reply({error:'Gemeinsame Bibliothek zu gross. Bitte Support kontaktieren.'},413);
   }catch{skipped++;}}
  }}
  const result={version:1,items,skipped,asOf:new Date().toISOString()};
  if(JSON.stringify(result).length>6000000)return reply({error:'Bibliothek zu gross für eine einzelne Abfrage.'},413);
  return reply(result);
 }catch{return reply({error:'Gemeinsame Bibliothek momentan nicht erreichbar. Eure bestehenden Einträge bleiben unverändert.'},503);}
});
