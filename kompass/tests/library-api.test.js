'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),{webcrypto}=require('crypto');
let handler,queries=[],valid=true,rows=[],fail=false;const token='ab'.repeat(32);
const context={Request,Response,URL,TextEncoder,AbortSignal,crypto:webcrypto,Deno:{env:{get:k=>k==='SUPABASE_URL'?'https://db.test':'server-secret-test-only'},serve:f=>handler=f},fetch:async(url,opt)=>{queries.push({url,opt});assert.equal(opt.headers.apikey,'server-secret-test-only');if(fail)return new Response('unavailable',{status:503});return Response.json(url.includes('/nk_sessions?')?(valid?[{expires_at:'2099-01-01'}]:[]):rows);}};
vm.createContext(context);vm.runInContext(fs.readFileSync(__dirname+'/../server/nutrient-library.js','utf8'),context);
const call=(data={action:'list'},headers={},method='POST')=>handler(new Request('https://edge.test',{method,headers:{'x-nk-session':token,...headers},...(method==='POST'?{body:typeof data==='string'?data:JSON.stringify(data)}:{})}));
let passed=0;async function test(name,f){await f();console.log('PASS',name);passed++;}
(async()=>{
await test('unauthenticated request rejected before database read',async()=>{queries=[];const r=await call({}, {'x-nk-session':''});assert.equal(r.status,401);assert.equal(queries.length,0);});
await test('expired session rejected',async()=>{valid=false;assert.equal((await call()).status,401);valid=true;});
await test('unexpected origin rejected',async()=>assert.equal((await call({}, {origin:'https://attacker.test'})).status,403));
await test('GET does not expose data',async()=>assert.equal((await call({}, {},'GET')).status,405));
await test('request size bounded',async()=>assert.equal((await call('x'.repeat(1001))).status,413));
await test('malformed JSON rejected',async()=>assert.equal((await call('{invalid')).status,400));
await test('unrecognized operation rejected',async()=>assert.equal((await call({action:'delete'})).status,400));
const food={id:'custom-test',name:'Synthetic crisps',basis:'g',n:{protein:6.2},entries:['PRIVATE-DIARY'],profile:{weight:'PRIVATE-WEIGHT'}};
const recipe={id:'recipe-test',name:'Synthetic meal',servings:2,finalWeight:100,ingredients:[{quantity:100,unit:'g',food}],entries:['PRIVATE-DIARY']};
rows=[{id:'test-profile',name:'Test owner',foods:[food],recipes:[recipe],entries:['PRIVATE-DIARY'],profile:{weight:'PRIVATE-WEIGHT'}}];
let answer;
await test('authenticated library returns products and recipes',async()=>{const r=await call();assert.equal(r.status,200);answer=await r.json();assert.equal(answer.items.length,2);assert.equal(answer.items[0].item.n.protein,6.2);});
await test('no personal diary or profile fields selected from database',async()=>{const q=queries.at(-1).url;assert.ok(q.includes('foods:state->foods,recipes:state->recipes'));assert.ok(!q.includes('select=*'));});
await test('whitelist excludes unintended personal fields even when present',async()=>{assert.ok(!JSON.stringify(answer).includes('PRIVATE-'));});
await test('stable shared IDs remain valid app identifiers',async()=>{const other=await (await call()).json();assert.equal(other.items[0].key,answer.items[0].key);assert.match(other.items[0].key,/^shared-[a-f0-9]{64}$/);});
await test('private response explicitly non-cacheable',async()=>assert.equal((await call()).headers.get('cache-control'),'no-store'));
await test('invalid rows omitted explicitly',async()=>{rows[0].foods.push({id:'x',name:'broken'});const r=await (await call()).json();assert.equal(r.skipped,1);});
await test('upstream error does not disclose environment or tokens',async()=>{fail=true;const r=await call();assert.equal(r.status,503);assert.ok(!(await r.text()).includes('server-secret'));});
console.log('TOTAL LIBRARY API TESTS',passed);
})().catch(e=>{console.error(e);process.exit(1);});
