'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..'),ctx={console,URL};ctx.window=ctx;vm.createContext(ctx);
function load(f){vm.runInContext(fs.readFileSync(path.join(root,f),'utf8'),ctx,{filename:f});}
for(const f of ['data.js','macro-goals.js','product-portions.js','food-search.js','core.js','veggie-data.js','catalog.js'])load(f);
const before=JSON.stringify(ctx.NK_DATA.foods),len=ctx.NK_DATA.foods.length;load('additional-foods.js');
const extra=ctx.NK_ADDITIONAL_FOODS.foods,keys=ctx.NK_DATA.nutrients.map(n=>n.key);let count=0;
function check(n,fn){fn();console.log('PASS',n);count++;}
check('Eight new records',()=>assert.equal(extra.length,8));
check('1305 directly available records',()=>assert.equal(ctx.NK_DATA.foods.length,1305));
check('Original food values unchanged',()=>assert.equal(JSON.stringify(ctx.NK_DATA.foods.slice(0,len)),before));
check('IDs unique',()=>assert.equal(new Set(ctx.NK_DATA.foods.map(f=>f.id)).size,1305));
check('Full nutrient schema and valid values',()=>extra.forEach(f=>{ctx.NK.validateFood(f,keys);assert.equal(Object.keys(f.n).length,keys.length);}));
check('Missing vitamins stay unknown',()=>extra.forEach(f=>assert.equal(f.n.vitC,null)));
check('Manufacturer source recorded',()=>extra.forEach(f=>assert.ok(f.sourceUrl.startsWith('https://eatplanted.com/products/')&&f.catalog.checkedAt==='2026-09-27')));
check('No invented density or serving size',()=>extra.forEach(f=>{assert.equal(f.density,null);assert.equal(f.portion,undefined);assert.equal(f.basis,'g');}));
check('Per-nutrient provenance provided',()=>extra.forEach(f=>keys.forEach(k=>assert.equal(f.provenance[k][1],f.id))));
check('Repeated script load adds no duplicates',()=>{load('additional-foods.js');assert.equal(ctx.NK_DATA.foods.length,1305);});
console.log('ADDITIONAL FOOD TESTS',count);
