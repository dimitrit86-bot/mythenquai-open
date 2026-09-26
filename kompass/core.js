/* Nährstoff-Kompass calculation core. No network, no UI, no silent missing-value imputation. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.NK=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const VERSION='1.3.0', SCHEMA=1;
 const clone=x=>JSON.parse(JSON.stringify(x));
 function number(v,{optional=false,min=0,max=1e9}={}){
  if(v===null||v===undefined||String(v).trim()===''){if(optional)return null;throw Error('Bitte eine Zahl eingeben.');}
  const s=String(v).trim().replace(',','.');
  if(!/^\d+(\.\d*)?$|^\.\d+$/.test(s))throw Error('Bitte eine gültige, nicht negative Zahl eingeben.');
  const n=Number(s);if(!Number.isFinite(n)||n<min||n>max)throw Error(`Wert muss zwischen ${min} und ${max} liegen.`);return n;
 }
 function positive(v){return number(v,{min:0.000001});}
 function factor(food,quantity,unit,density){
  let q=positive(quantity),dimension;
  if(unit==='kg'){q*=1000;dimension='g';}else if(unit==='g')dimension='g';
  else if(unit==='l'){q*=1000;dimension='ml';}else if(unit==='dl'){q*=100;dimension='ml';}else if(unit==='ml')dimension='ml';
  else throw Error('Unbekannte Mengeneinheit.');
  if(!['g','ml'].includes(food.basis))throw Error('Ungültige Bezugsmenge.');
  const d=number(density??food.density,{optional:true,min:0.000001,max:100});
  if(dimension!==food.basis){if(!d)throw Error('Für diese Umrechnung ist eine Dichte in g/ml erforderlich. Alternativ die passende Einheit verwenden.');q=dimension==='ml'?q*d:q/d;}
  return q/100;
 }
 function snapshot(food,quantity,unit,density,keys){
  const f=factor(food,quantity,unit,density); const out={};
  for(const key of keys){const v=food.n[key];const ok=typeof v==='number'&&Number.isFinite(v)&&v>=0;
   out[key]={value:ok?v*f:null,known:ok?1:0,total:1,missing:ok?[]:[food.name+(food.q?.[key]?' ('+food.q[key]+')':'')]};}
  return out;
 }
 function aggregate(list,keys){
  const out={};
  for(const key of keys){let value=0,known=0,total=0,missing=[];
   for(const snap of list){const v=snap[key];if(!v)continue; if(v.value!==null)value+=v.value;known+=v.known;total+=v.total;missing.push(...(v.missing||[]));}
   out[key]={value:known?value:null,known,total,missing:[...new Set(missing)]};
  }return out;
 }
 function scale(snap,f){f=positive(f);const out=clone(snap);for(const v of Object.values(out))if(v.value!==null)v.value*=f;return out;}
 function recipeTotal(recipe,keys){if(!recipe.ingredients?.length)throw Error('Bitte mindestens eine Zutat hinzufügen.');return aggregate(recipe.ingredients.map(x=>snapshot(x.food,x.quantity,x.unit,x.density,keys)),keys);}
 function recipePortion(recipe,amount,unit,keys){
  const a=positive(amount);let share;
  if(unit==='portion'){share=a/positive(recipe.servings);}else if(unit==='g'){share=a/positive(recipe.finalWeight);}else if(unit==='batch'){share=a;}else throw Error('Ungültige Portion.');
  return scale(recipeTotal(recipe,keys),share);
 }
 function recipeWeight(recipe){let total=0;for(const i of recipe.ingredients){const f=factor(i.food,i.quantity,i.unit,i.density);if(i.food.basis==='g')total+=f*100;else {const d=i.density??i.food.density;if(!d)return null;total+=f*100*d;}}return total;}
 function dateKey(d=new Date()){const local=new Date(d.getTime()-d.getTimezoneOffset()*60000);return local.toISOString().slice(0,10);}
 function validDate(s){if(typeof s!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(s))return false;const d=new Date(s+'T12:00:00Z');return Number.isFinite(d.getTime())&&d.toISOString().slice(0,10)===s;}
 function dayEntries(state,date){return state.entries.filter(e=>e.date===date);}
 function history(state,end,days,keys,completeOnly=false){
  const start=new Date(end+'T12:00:00');start.setDate(start.getDate()-days+1);const a=dateKey(start);
  const dates=[...new Set(state.entries.filter(e=>e.date>=a&&e.date<=end).map(e=>e.date))].filter(d=>!completeOnly||state.days[d]?.complete).sort();
  const rows=dates.map(d=>({date:d,complete:!!state.days[d]?.complete,n:aggregate(dayEntries(state,d).map(e=>e.n),keys)}));
  const sum=aggregate(rows.map(r=>r.n),keys);const avg=dates.length?scale(sum,1/dates.length):sum;
  return {rows,average:avg,days:dates.length,completeDays:rows.filter(r=>r.complete).length};
 }
 function initial(){return {schema:SCHEMA,profile:{sex:'',age:null,weight:null,height:null,special:false,smoker:false,menopause:'',phytate:'',manual:{}},entries:[],recipes:[],foods:[],favorites:[],recent:[],days:{},recipeDraft:null};}
 const REF='https://www.dge.de/wissenschaft/referenzwerte/';
 function targets(p){
  const out={}, notes=[];const add=(k,v,slug,year,type='Empfohlene Zufuhr',note='')=>{out[k]={value:v,url:REF+slug+'/',year,type,note};};
  const age=Number(p.age),m=p.sex==='m',w=p.sex==='w';
  if(p.age&&age>=19&&age<=120&&!p.special){
   const a=age<25?0:age<51?1:age<65?2:3;
   add('vitD',20,'vitamin-d',2012,'Schätzwert','Gilt bei fehlender körpereigener Bildung. Der Ernährungseintrag erfasst Sonnenlicht nicht.');
   add('vitE',8,'vitamin-e',2024,'Schätzwert','Bezugsform RRR-α-Tocopherol. Packungswerte anderer Formen nicht ungeprüft übernehmen.');
   add('vitB5',5,'pantothensaeure',2021,'Schätzwert');add('vitB12',4,'vitamin-b12',2018,'Schätzwert');
   add('calcium',1000,'calcium',2013);add('potassium',4000,'kalium',2016,'Schätzwert');
   add('phosphorus',550,'phosphor',2022,'Schätzwert');add('iodine',150,'jod',2025);
   // The BLV column is food folate, not dietary folate equivalents. Show reference but do not generate a percentage.
   add('folate',300,'folat',2015,'Empfohlene Zufuhr','300 µg Folat-Äquivalente. Die Datenbank enthält Nahrungsfolat, nicht gesicherte Gesamtäquivalente bei Anreicherung. Daher kein automatischer Prozentvergleich.');out.folate.noPercent=true;
   if(m||w){
    add('vitA',m?(a===3?800:850):700,'vitamin-a',2020,'Empfohlene Zufuhr','Retinolaktivitätsäquivalente (RAE), nicht RE.');
    add('vitC',p.smoker?(m?155:135):(m?110:95),'vitamin-c',2015);
    add('vitB1',m?[1.3,1.2,1.2,1.1][a]:1,'thiamin',2015,'Empfohlene Zufuhr','Alters- und geschlechtsspezifischer Tabellenwert; keine direkte Gewichts-Skalierung.');
    add('vitB2',m?[1.4,1.4,1.3,1.3][a]:[1.1,1.1,1,1][a],'riboflavin',2015);
    add('niacinEq',m?[16,15,15,14][a]:[13,12,11,11][a],'niacin',2015,'Empfohlene Zufuhr','Niacin-Äquivalente; kein Vergleich mit einfachem Niacin.');
    add('vitB6',m?1.6:1.4,'vitamin-b6',2019);add('magnesium',m?350:300,'magnesium',2021,'Schätzwert');add('selenium',m?70:60,'selenium',2015,'Schätzwert');
    if(m)add('iron',11,'eisen',2023);else if(p.menopause==='post'||age>=65)add('iron',14,'eisen',2023);else if(p.menopause==='pre')add('iron',16,'eisen',2023);else notes.push('Für den Eisen-Referenzwert bitte das Menopause-Profil ergänzen; kein Rückschluss allein aus dem Alter.');
    if(['low','medium','high'].includes(p.phytate)){const ix=['low','medium','high'].indexOf(p.phytate);add('zinc',m?[11,14,16][ix]:[7,8,10][ix],'zink',2019,'Empfohlene Zufuhr','Abhängig von der gewählten Phytatzufuhr.');}else notes.push('Zink: Ohne Phytat-Einschätzung kein einzelner Zielwert (Männer 11–16 mg; Frauen 7–10 mg).');
   }else notes.push('Geschlechtsabhängige Vergleiche erscheinen nach Auswahl eines Referenzprofils.');
   if(p.weight&&p.height){const bmi=p.weight/(p.height/100)**2;const custom=Number(p.calcWeight);let cw=null;
    if(custom>0)cw=custom;else if(bmi>=18.5&&bmi<=25)cw=Number(p.weight);
    if(cw)add('protein',cw*(age>=65?1:0.8),'protein',2017,age>=65?'Schätzwert':'Empfohlene Zufuhr',`Berechnungsgewicht: ${cw} kg. Basiswert für gesunde Erwachsene; kein individuelles Sportziel.`);
    else notes.push('Protein: Der Basiswert bezieht sich auf Normalgewicht. Bitte ein fachlich abgestimmtes Berechnungsgewicht oder ein eigenes Proteinziel eingeben.');
   }else notes.push('Für einen gewichtsabhängigen Protein-Basiswert bitte Gewicht und Grösse ergänzen.');
  }else notes.push('Automatische Referenzen gelten hier nur für gesunde Erwachsene ab 19 Jahren. Alter ergänzen; bei besonderen Lebenssituationen eigene fachlich abgestimmte Ziele verwenden.');
  for(const [k,v] of Object.entries(p.manual||{}))if(Number.isFinite(v)&&v>0)out[k]={value:v,type:'Eigenes Ziel',note:'Von dir eingetragener Wert, keine automatisch abgeleitete Empfehlung.',year:null,url:null};
  return {values:out,notes};
 }
 function validateFood(f,keys){
  if(!f||typeof f.name!=='string'||!f.name.trim()||f.name.length>240)throw Error('Ungültiger Lebensmittelname.');
  if(typeof f.id!=='string'||!/^[A-Za-z0-9_-]{1,100}$/.test(f.id)||!['g','ml'].includes(f.basis)||!f.n||typeof f.n!=='object')throw Error('Ungültiges Lebensmittel.');
  if(f.density!==null&&f.density!==undefined)positive(f.density);
  for(const k of keys)if(f.n[k]!==null&&f.n[k]!==undefined&&(!Number.isFinite(f.n[k])||f.n[k]<0||f.n[k]>1e9))throw Error('Ungültiger Nährwert.');
 }
 function validateState(s,keys){
  if(!s||s.schema!==SCHEMA||!s.profile||!s.days||typeof s.days!=='object')throw Error('Nicht unterstützte Sicherungsdatei.');
  for(const k of ['entries','recipes','foods','favorites','recent'])if(!Array.isArray(s[k])||s[k].length>30000)throw Error('Ungültige Sicherungsdatei.');
  s.foods.forEach(f=>validateFood(f,keys));
  for(const r of s.recipes){if(typeof r.id!=='string'||!/^[A-Za-z0-9_-]{1,100}$/.test(r.id)||typeof r.name!=='string'||r.name.length>240||!Array.isArray(r.ingredients)||!r.ingredients.length||r.ingredients.length>200)throw Error('Ungültiges Gericht.');positive(r.servings);if(r.finalWeight!==null&&r.finalWeight!==undefined)positive(r.finalWeight);r.ingredients.forEach(i=>{validateFood(i.food,keys);factor(i.food,i.quantity,i.unit,i.density);});}
  for(const e of s.entries){if(typeof e.id!=='string'||!/^[A-Za-z0-9_-]{1,100}$/.test(e.id)||!Number.isInteger(e.meal)||e.meal<0||e.meal>3||typeof e.name!=='string'||!validDate(e.date)||!e.n)throw Error('Ungültiger Tagebucheintrag.');for(const k of keys){const v=e.n[k];if(!v||v.value!==null&&(!Number.isFinite(v.value)||v.value<0)||!Number.isInteger(v.known)||!Number.isInteger(v.total)||v.known<0||v.total<v.known||!Array.isArray(v.missing)||v.missing.some(m=>typeof m!=='string'))throw Error('Ungültige Nährwert-Zusammenfassung.');}}
  const p=s.profile;
  if(!['','m','w'].includes(p.sex)||typeof p.special!=='boolean'||typeof p.smoker!=='boolean'||!['','pre','post'].includes(p.menopause)||!['','low','medium','high'].includes(p.phytate)||!p.manual||Array.isArray(p.manual)||typeof p.manual!=='object')throw Error('Ungültiges Referenzprofil.');
  for(const [k,lo,hi] of [['age',0,120],['weight',1,600],['height',40,260],['calcWeight',1,600]])if(p[k]!==null&&p[k]!==undefined&&(!Number.isFinite(p[k])||p[k]<lo||p[k]>hi))throw Error('Ungültiger Profilwert.');
  for(const [k,v] of Object.entries(p.manual))if(!keys.includes(k)||!Number.isFinite(v)||v<=0||v>1e9)throw Error('Ungültiges eigenes Ziel.');
  if(s.favorites.some(v=>typeof v!=='string')||s.recent.some(v=>typeof v!=='string'))throw Error('Ungültige Lebensmittelliste.');
  for(const k of Object.keys(s.days))if(!validDate(k)||!s.days[k]||typeof s.days[k].complete!=='boolean')throw Error('Ungültiges Tagesprotokoll.');
  // Sanitize stored draft independently; it must never block diary recovery.
  s.recipeDraft=null;return clone(s);
 }
 return {VERSION,SCHEMA,clone,number,positive,factor,snapshot,aggregate,scale,recipeTotal,recipePortion,recipeWeight,dateKey,validDate,dayEntries,history,initial,targets,validateFood,validateState};
});
