/* Read-only protein view tests. No personal data, network or storage access. */
'use strict';
const assert = require('node:assert/strict'), fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const C = require('../core.js');
const ctx = {NK:C, Intl, console, document:{getElementById:()=>({}),addEventListener(){}}, MutationObserver:class{observe(){}}, queueMicrotask(){}};
ctx.window=ctx; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname,'../protein-overview.js'),'utf8'),ctx);
const model=ctx.NK_PROTEIN_OVERVIEW.model, p={...C.initial().profile,age:40,weight:80,height:180,sex:'m'};
const intake=(value,known=1,total=1)=>({value,known,total});
let passed=0;function test(name,fn){fn();passed++;console.log('PASS',name);}
test('existing adult reference is reused',()=>assert.equal(model(p,intake(40)).target,64));
test('existing reference at 65 is reused',()=>assert.equal(model({...p,age:65},intake(40)).target,80));
test('manual goal takes priority and is labelled',()=>{const m=model({...p,manual:{protein:95}},intake(40));assert.equal(m.target,95);assert.equal(m.own,true);});
test('empty diary still shows daily need, not zero intake',()=>{const m=model(p,intake(null,0,0));assert.equal(m.target,64);assert.equal(m.amount,null);assert.equal(m.remaining,null);});
test('remaining amount based on recorded intake',()=>assert.equal(model(p,intake(40)).remaining,24));
test('real zero remains a known zero',()=>{const m=model(p,intake(0));assert.equal(m.amount,0);assert.equal(m.remaining,64);});
test('unknown intake not replaced with zero',()=>assert.equal(model(p,intake(null,0,1)).amount,null));
test('partial nutrient data suppresses exact remaining amount',()=>{const m=model(p,intake(40,1,2));assert.equal(m.partial,true);assert.equal(m.percent,null);assert.equal(m.remaining,null);});
test('exceeding target never produces negative remaining amount',()=>assert.equal(model(p,intake(100)).remaining,0));
test('missing profile never invents a target',()=>assert.equal(model(C.initial().profile,intake(10)).target,null));
test('existing out-of-range BMI protection preserved',()=>assert.equal(model({...p,weight:120},intake(10)).target,null));
test('explicit calculation weight remains supported',()=>assert.equal(model({...p,weight:120,calcWeight:80},intake(10)).target,64));
test('special situations retain automatic-target exclusion',()=>assert.equal(model({...p,special:true},intake(10)).target,null));
test('underage profiles retain exclusion',()=>assert.equal(model({...p,age:16},intake(10)).target,null));
test('view does not mutate profile or intake',()=>{const n=intake(40),before=JSON.stringify([p,n]);model(p,n);assert.equal(JSON.stringify([p,n]),before);});
console.log('TOTAL PROTEIN VIEW TESTS',passed);
