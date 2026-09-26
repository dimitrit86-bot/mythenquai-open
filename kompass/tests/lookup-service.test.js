'use strict';
const assert=require('node:assert/strict'),core=require('../import-core.js'),{createHandler}=require('../server/lookup-service.js');
let count=0;const base='https://test.invalid',token='a'.repeat(64);
const req=(input,extra={},method='POST')=>new Request('https://test.invalid/functions/v1/lookup',{method,headers:{'Content-Type':'application/json','x-nk-session':token,...extra},...(method==='POST'?{body:JSON.stringify({action:'lookup',input})}:{})});
const product={code:'1234567890123',product_name:'Test',nutriments:{proteins_100g:26,fat_100g:6}};
function make({auth=true,external=async()=>Response.json({products:[product]})}={}){const calls=[];return {calls,handler:createHandler({core,base,service:'not-a-real-key',fetcher:async(u,o)=>{calls.push([u,o]);if(u.startsWith(base+'/rest'))return Response.json(auth?[{expires_at:'2099-01-01'}]:[]);return external(u,o);}})}}
async function test(n,f){await f();count++;console.log('PASS',n)}
(async()=>{
 await test('Absent session rejected before any external call',async()=>{const h=make();const r=await h.handler(req('Test',{'x-nk-session':''}));assert.equal(r.status,401);assert.equal(h.calls.length,0)});
 await test('Invalid session rejected before provider query',async()=>{const h=make({auth:false});assert.equal((await h.handler(req('Test'))).status,401);assert.equal(h.calls.length,1)});
 await test('Foreign origin rejected',async()=>assert.equal((await make().handler(req('Test',{origin:'https://evil.invalid'}))).status,403));
 await test('Auth uses hash not raw token in URL',async()=>{const h=make();await h.handler(req('Test'));assert.ok(h.calls[0][0].includes('token_hash=eq.'));assert.ok(!h.calls[0][0].includes(token))});
 await test('Search uses supported plain-text endpoint',async()=>{const h=make();const r=await h.handler(req('Test'));assert.equal(r.status,200);assert.ok(h.calls[1][0].includes('/cgi/search.pl?'));assert.equal((await r.json()).products[0].n.protein,26)});
 await test('Credentials never forwarded to external provider',async()=>{const h=make();await h.handler(req('Test'));const h2=h.calls[1][1].headers;assert.equal(h2.Authorization,undefined);assert.equal(h2['x-nk-session'],undefined);assert.ok(h2['User-Agent'].includes('Kompass'))});
 await test('Public result caching still checks sessions',async()=>{const h=make();await h.handler(req('Test'));await h.handler(req('Test'));assert.equal(h.calls.filter(x=>!x[0].startsWith(base)).length,1);assert.equal(h.calls.filter(x=>x[0].startsWith(base)).length,2)});
 await test('Unsupported URLs do not fetch external resources',async()=>{const h=make();assert.equal((await h.handler(req('https://localhost/secret'))).status,400);assert.equal(h.calls.length,1)});
 await test('Only exact known product has source fallback',async()=>{const h=make({external:async()=>new Response('',{status:403})});const r=await h.handler(req(core.seed('Redefine Flank Steak').sourceUrl));assert.equal(r.status,200);assert.equal((await r.json()).products[0].lookup.mode,'snapshot')});
 await test('Other inaccessible links return error not invented values',async()=>{const h=make({external:async()=>new Response('',{status:403})});const r=await h.handler(req('https://www.coop.ch/de/foo/p/1234567'));assert.equal(r.status,422);assert.equal((await r.json()).products,undefined)});
 await test('Cross-origin redirects never followed',async()=>{const h=make({external:async()=>new Response(null,{status:302,headers:{location:'https://localhost/secret'}})});assert.equal((await h.handler(req('https://www.coop.ch/de/foo/p/1234567'))).status,422);assert.equal(h.calls.length,2)});
 await test('Rate limit caps external lookups',async()=>{const h=make();for(let i=0;i<8;i++)assert.equal((await h.handler(req('Test '+i))).status,200);assert.equal((await h.handler(req('Test ninth'))).status,429)});
 await test('Invalid JSON and unexpected action handled',async()=>{const h=make();const r=await h.handler(new Request('https://test.invalid',{method:'POST',headers:{'x-nk-session':token},body:'{invalid'}));assert.equal(r.status,400)});
 await test('Live read is read-only GET to sources',async()=>{const h=make();await h.handler(req('Test'));assert.ok(h.calls.every(([,o])=>!o.method||o.method==='GET'))});
 console.log('TOTAL LOOKUP SERVICE CHECKS',count);
})().catch(e=>{console.error(e);process.exitCode=1});
