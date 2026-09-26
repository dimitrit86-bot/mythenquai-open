/* Read-only calendar reports. No private network calls and no missing-as-zero imputation. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory(require('./core.js'));else root.NK_REPORTS=factory(root.NK);})(typeof globalThis!=='undefined'?globalThis:this,function(C){
 'use strict';
 const FREQUENCIES={daily:'Täglich',weekly:'Wöchentlich',monthly:'Monatlich'};
 const TITLES={daily:'Tagesreport',weekly:'Wochenreport',monthly:'Monatsreport'};
 const TRACE=new Set(['iron','zinc','iodine','selenium','copper','manganese','chromium','molybdenum','fluoride']);
 const PLAN=new Set(['energy','carbs','fat']);
 const MINIMUM=new Set(['protein','fiber']);
 const SOURCES={reference:'https://www.dge.de/gesunde-ernaehrung/faq/referenzwerte/',vitD:'https://www.dge.de/wissenschaft/referenzwerte/vitamin-d/'};
 const STATUS={met:'Vergleichswert erreicht',within:'Im Planbereich',below:'Unter Vergleichswert',under_plan:'Unter Planbereich',over_plan:'Über Planbereich',provisional:'Vorläufig',gaps:'Datenlücken',no_data:'Keine Einträge',no_target:'Kein Ziel hinterlegt',incompatible:'Nicht direkt vergleichbar',comparison:'Nur Zahlenvergleich'};
 function frequency(p){return Object.hasOwn(FREQUENCIES,p?.reportFrequency)?p.reportFrequency:'weekly';}
 function checkFrequency(f){if(!Object.hasOwn(FREQUENCIES,f))throw Error('Report-Häufigkeit: täglich, wöchentlich oder monatlich wählen.');return f;}
 function dt(s){if(!C.validDate(s))throw Error('Bitte ein gültiges Report-Datum wählen.');return new Date(s+'T12:00:00Z');}
 function key(d){return d.toISOString().slice(0,10);}
 function shift(s,n){const d=dt(s);d.setUTCDate(d.getUTCDate()+n);return key(d);}
 function period(f,anchor){checkFrequency(f);const d=dt(anchor);let start=anchor,end=anchor;
  if(f==='weekly'){start=shift(anchor,-((d.getUTCDay()+6)%7));end=shift(start,6);}
  if(f==='monthly'){d.setUTCDate(1);start=key(d);d.setUTCMonth(d.getUTCMonth()+1);end=shift(key(d),-1);}
  return {frequency:f,start,end,id:f+':'+start};
 }
 function adjacent(p,direction){return period(p.frequency,shift(direction<0?p.start:p.end,direction<0?-1:1));}
 function dates(p){let a=[],d=p.start;while(d<=p.end){a.push(d);if(a.length>31)throw Error('Ungültiger Report-Zeitraum.');d=shift(d,1);}return a;}
 function previous(f,today=C.dateKey()){return adjacent(period(f,today),-1);}
 function history(state,f,today=C.dateKey()){
  const all=new Map();const add=d=>{const p=period(f,d);all.set(p.id,p);};add(today);add(previous(f,today).start);
  for(const e of state.entries)if(C.validDate(e.date)&&e.date<=today)add(e.date);
  return [...all.values()].sort((a,b)=>b.start.localeCompare(a.start));
 }
 function group(n){return TRACE.has(n.key)?'trace':n.group==='mineral'?'mineral':n.group;}
 function mode(n){return PLAN.has(n.key)?'plan':MINIMUM.has(n.key)||n.group==='vitamin'||(n.group==='mineral'&&n.key!=='sodium'&&n.key!=='chloride')?'minimum':'comparison';}
 function relationship(value,target,kind){const ratio=value/target;return kind==='plan'?(ratio<.9-1e-10?'under_plan':ratio>1.1+1e-10?'over_plan':'within'):kind==='minimum'?(ratio>=1-1e-10?'met':'below'):'comparison';}
 function summarizeNutrient(n,selected,refs){
  const ref=refs[n.key]||null,target=Number.isFinite(ref?.value)&&ref.value>0?ref.value:null;
  let sum=0,known=0,total=0,fullDays=0,unknownDays=0,comparableDays=0,metDays=0,belowDays=0,aboveDays=0;const missing=new Set(),dayValues=[];const kind=mode(n);
  for(const day of selected){let amount=0,dayKnown=0,dayTotal=0;
   for(const e of day.entries){const v=e.n?.[n.key];
    const valid=v&&Number.isFinite(v.value)&&v.value>=0&&Number.isInteger(v.known)&&v.known>0&&Number.isInteger(v.total)&&v.total>=v.known;
    const t=Number.isInteger(v?.total)&&v.total>0?v.total:1;
    dayTotal+=t;if(valid){amount+=v.value;dayKnown+=v.known;}
    if(!valid||v.known<v.total){const names=(v?.missing||[]).filter(x=>typeof x==='string');for(const name of names.length?names:[e.name||'Eintrag ohne Angabe'])missing.add(name);}
   }
   const full=dayKnown===dayTotal&&dayTotal>0;
   known+=dayKnown;total+=dayTotal;if(dayKnown)sum+=amount;
   if(full)fullDays++;else unknownDays++;
   let result=null;
   if(full&&day.complete&&target&&!ref.noPercent){result=relationship(amount,target,kind);if(kind!=='comparison'){comparableDays++;if(['met','within'].includes(result))metDays++;else if(['below','under_plan'].includes(result))belowDays++;else aboveDays++;}}
   dayValues.push({date:day.date,amount:dayKnown?amount:null,full,complete:day.complete,result});
  }
  const average=selected.length&&known?sum/selected.length:null,hasGaps=unknownDays>0,complete=selected.length>0&&selected.every(d=>d.complete);
  const relation=target&&average!==null&&!ref.noPercent?relationship(average,target,kind):null;
  let status=!selected.length?'no_data':!target?'no_target':ref.noPercent?'incompatible':hasGaps?'gaps':!complete?'provisional':relation;
  // Data with a missing nutrient entirely must never become a zero or a failed goal.
  const percent=target&&average!==null&&!ref.noPercent?average/target*100:null;
  return {key:n.key,label:n.label,unit:n.unit,group:group(n),mode:kind,target,ref,average,knownSum:known?sum:null,known,total,fullDays,unknownDays,missing:[...missing],hasGaps,complete,selectedDays:selected.length,percent,relation,status,dayValues,comparableDays,metDays,belowDays,aboveDays};
 }
 function build(state,nutrients,{frequency:f=frequency(state.profile),anchor=C.dateKey(),today=C.dateKey(),completeOnly=false}={}){
  const p=period(f,anchor);dt(today);const all=dates(p),elapsed=all.filter(d=>d<=today),map=new Map();
  for(const e of state.entries){if(e.date>=p.start&&e.date<=p.end&&e.date<=today){if(!map.has(e.date))map.set(e.date,[]);map.get(e.date).push(e);}}
  const recorded=elapsed.filter(d=>map.has(d)).map(date=>({date,entries:map.get(date),complete:state.days?.[date]?.complete===true}));
  const selected=recorded.filter(d=>!completeOnly||d.complete),refs=C.targets(state.profile),rows=nutrients.map(n=>summarizeNutrient(n,selected,refs.values));
  const counts={met:0,below:0,above:0,provisional:0,gaps:0,no_target:0,incompatible:0,no_data:0,comparison:0};
  for(const r of rows){if(['met','within'].includes(r.status))counts.met++;else if(['below','under_plan'].includes(r.status))counts.below++;else if(r.status==='over_plan')counts.above++;else counts[r.status]++;}
  return {period:p,today,calendarDays:all.length,elapsedDays:elapsed.length,futureDays:all.length-elapsed.length,unrecordedDays:elapsed.length-recorded.length,recordedDays:recorded.length,completeDays:recorded.filter(d=>d.complete).length,selectedDays:selected.length,excludedDays:recorded.length-selected.length,ongoing:p.end>=today,partialPeriod:recorded.length<all.length,completeOnly,counts,rows,notes:refs.notes,days:elapsed.map(date=>({date,entries:map.get(date)?.length||0,complete:state.days?.[date]?.complete===true&&map.has(date)})),targetBasis:'Aktuelle gespeicherte Profilziele, auch für frühere Zeiträume. Keine rückwirkende Zielhistorie.'};
 }
 function csv(report,name){
  const cell=v=>'"'+String(v??'').replace(/^([\s]*[=+@-])/g,"'$1").replace(/"/g,'""')+'"';
  const header=['Profil','Von','Bis','Datenbasis','Berücksichtigte Tage','Nährstoff','Einheit pro Tag','Bekannte Zufuhr im Tagesmittel','Aktuelles Ziel pro Tag','Prozent (ggf. Untergrenze)','Status','Tage mit vollständigen Nährstoffangaben','Fehlende Angaben','Vergleichsgrundlage'];
  const data=report.rows.map(r=>[name,report.period.start,report.period.end,report.completeOnly?'Vollständig markierte Tage':'Protokollierte Tage',report.selectedDays,r.label,r.unit,r.average,r.target,r.percent,STATUS[r.status]+(r.hasGaps?' · bekannte Teilmenge':r.status==='provisional'?' · '+STATUS[r.relation]:''),r.fullDays,r.missing.join(' | '),report.targetBasis]);
  return '\uFEFF'+[header,...data].map(row=>row.map(cell).join(';')).join('\r\n');
 }
 return {FREQUENCIES,TITLES,STATUS,SOURCES,frequency,checkFrequency,period,adjacent,shift,previous,history,group,mode,build,csv};
});
