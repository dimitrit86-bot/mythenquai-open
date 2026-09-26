'use strict';const assert=require('node:assert/strict'),C=require('../core.js'),S=require('../sync-core.js');let count=0;const cp=C.clone;
function test(n,f){f();console.log('PASS',n);count++;}
const base=C.initial();base.entries=[{id:'a',name:'Original'}];base.foods=[{id:'f',name:'Original food'}];
test('disjoint additions union without changing base',()=>{const l=cp(base),r=cp(base);l.entries.push({id:'l'});r.entries.push({id:'r'});const m=S.merge(base,l,r);assert.deepEqual(m.state.entries.map(e=>e.id),['a','l','r']);assert.equal(m.conflicts.length,0);assert.equal(base.entries.length,1);});
test('key order and duplicate acknowledgement compare equal',()=>assert.ok(S.equal({a:1,b:2},{b:2,a:1})));
test('one-side edit preserved',()=>{const l=cp(base),r=cp(base);l.foods[0].name='New';const m=S.merge(base,l,r);assert.equal(m.state.foods[0].name,'New');assert.equal(m.conflicts.length,0);});
test('delete unchanged item respected',()=>{const l=cp(base),r=cp(base);l.foods=[];assert.equal(S.merge(base,l,r).state.foods.length,0);});
test('delete versus edit requires explicit choice',()=>{const l=cp(base),r=cp(base);l.foods=[];r.foods[0].name='Edit';const m=S.merge(base,l,r);assert.equal(m.conflicts.length,1);assert.equal(S.merge(base,l,r,'server').state.foods[0].name,'Edit');});
test('conflicting records never auto-resolve',()=>{const l=cp(base),r=cp(base);l.entries[0].name='L';r.entries[0].name='R';assert.equal(S.merge(base,l,r).conflicts.length,1);});
test('conflict choice preserves other remote additions',()=>{const l=cp(base),r=cp(base);l.entries[0].name='L';r.entries[0].name='R';r.entries.push({id:'extra'});const m=S.merge(base,l,r,'local');assert.equal(m.state.entries[0].name,'L');assert.equal(m.state.entries[1].id,'extra');});
test('independent profile fields merge',()=>{const l=cp(base),r=cp(base);l.profile.age=40;r.profile.height=180;const m=S.merge(base,l,r);assert.equal(m.state.profile.height,180);assert.equal(m.state.profile.age,40);assert.equal(m.conflicts.length,0);});
test('independent manual goals merge',()=>{const l=cp(base),r=cp(base);l.profile.manual.protein=90;r.profile.manual.energy=2300;const m=S.merge(base,l,r);assert.equal(m.state.profile.manual.protein,90);assert.equal(m.state.profile.manual.energy,2300);assert.equal(m.conflicts.length,0);});
test('same manual goal conflict detectable',()=>{const l=cp(base),r=cp(base);l.profile.manual.protein=90;r.profile.manual.protein=100;assert.ok(S.merge(base,l,r).conflicts.includes('profile.manual.protein'));});
test('legacy additive recovery safe',()=>{const l=cp(base),r=cp(base);l.entries.push({id:'old-local'});r.entries.push({id:'remote'});const m=S.merge(null,l,r);assert.equal(m.conflicts.length,0);assert.equal(m.state.entries.length,3);});
test('legacy collision needs choice',()=>{const l=cp(base),r=cp(base);l.entries[0].name='Old';assert.equal(S.merge(null,l,r).conflicts.length,1);});
test('favorites respect one-sided removal',()=>{const b=cp(base);b.favorites=['f'];const l=cp(b),r=cp(b);l.favorites=[];assert.equal(S.merge(b,l,r).state.favorites.length,0);});
test('new favorites union',()=>{const l=cp(base),r=cp(base);l.favorites=['l'];r.favorites=['r'];assert.equal(S.merge(base,l,r).state.favorites.length,2);});
test('empty journals stay empty',()=>{const b=C.initial();assert.equal(S.merge(b,b,b).state.entries.length,0);});
console.log('TOTAL SYNC TESTS',count);
