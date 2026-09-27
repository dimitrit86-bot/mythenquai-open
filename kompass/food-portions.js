/* Optional piece definitions in the food's own g/ml basis. Persist recipe quantities
   in g/ml so older clients can still read them. No private data or network access. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.NK_PIECES=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 function positive(v){const s=String(v??'').trim().replace(',','.');if(!/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(s))throw Error('Bitte eine gültige Menge eingeben.');const n=Number(s);if(!Number.isFinite(n)||n<=0||n>1e9)throw Error('Die Menge muss grösser als 0 sein.');return n;}
 function definition(f){if(f?.portion==null)return null;const p=f.portion;if(typeof p!=='object'||Array.isArray(p)||typeof p.label!=='string'||!p.label.trim()||p.label.length>40||typeof p.amount!=='number'||!Number.isFinite(p.amount)||p.amount<=0||p.amount>100000||!['g','ml'].includes(p.unit)||p.unit!==f.basis)throw Error('Ungültige Stückportion. Bitte Menge und g/ml-Bezugsmenge prüfen.');return {label:p.label,amount:p.amount,unit:p.unit};}
 function toBase(f,count){const p=definition(f);if(!p)throw Error('Bitte zuerst eine Stückportion am Produkt hinterlegen.');const q=positive(count);return {quantity:q*p.amount,unit:p.unit,piece:{count:q,...p}};}
 function ingredient(f,quantity,unit,density){if(unit!=='piece')return {food:f,quantity:positive(quantity),unit,density};return {food:f,...toBase(f,quantity),density};}
 function selection(i){const p=i?.piece;if(p&&typeof p.count==='number'&&p.count>0&&Number.isFinite(p.count)&&typeof p.amount==='number'&&p.amount>0&&Number.isFinite(p.amount)&&p.unit===i.unit&&['g','ml'].includes(p.unit)&&Math.abs(i.quantity-p.count*p.amount)<Math.max(1e-8,i.quantity*1e-10)&&definition(i.food)?.amount===p.amount&&typeof p.label==='string')return {quantity:p.count,unit:'piece'};return {quantity:i.quantity,unit:i.unit};}
 function convertQuantity(f,q,from,to,density){q=positive(q);const units={g:['g',1],kg:['g',1000],ml:['ml',1],dl:['ml',100],l:['ml',1000]};if(from==='piece'){const x=toBase(f,q);q=x.quantity;from=x.unit;}const dest=to==='piece'?definition(f)?.unit:to;if(!units[from]||!units[dest])throw Error('Ungültige Mengeneinheit oder fehlende Stückportion.');q*=units[from][1];if(units[from][0]!==units[dest][0]){const d=positive(density??f.density);q=units[from][0]==='ml'?q*d:q/d;}q/=units[dest][1];if(to==='piece')q/=definition(f).amount;return q;}
 function edit(i,field,value){const s=selection(i);if(field==='quantity'){if(s.unit==='piece'){const p=toBase(i.food,value);i.quantity=p.quantity;i.unit=p.unit;i.piece=p.piece;}else i.quantity=value;return;}
  if(field!=='unit')return;
  if(value==='piece'){const p=definition(i.food);if(!p)throw Error('Für dieses Produkt ist keine Stückportion definiert.');let q=positive(i.quantity);const old=i.unit;if(old==='kg')q*=1000;else if(old==='l')q*=1000;else if(old==='dl')q*=100;const dimension=['g','kg'].includes(old)?'g':'ml';if(dimension!==p.unit){const d=positive(i.density??i.food.density);q=dimension==='ml'?q*d:q/d;}Object.assign(i,toBase(i.food,q/p.amount));}
  else{const quantity=convertQuantity(i.food,i.quantity,i.unit,value,i.density);delete i.piece;i.unit=value;i.quantity=quantity;}
 }
 function text(f,q,unit,format=String){if(unit!=='piece')return format(q)+' '+unit;const x=toBase(f,q);return format(positive(q))+' Stück'+(x.piece.label==='Stück'?'':' · '+x.piece.label)+' ('+format(x.quantity)+' '+x.unit+')';}
 return {positive,definition,toBase,ingredient,selection,convertQuantity,edit,text};
});
