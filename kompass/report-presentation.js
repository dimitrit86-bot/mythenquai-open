/* Shared display rules for screen and PDF. Pure: no profile, storage or network writes. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory(require('./report-core.js'));else root.NK_REPORT_PRESENTATION=factory(root.NK_REPORTS);})(typeof globalThis!=='undefined'?globalThis:this,function(R){
'use strict';
const GROUPS=[['macro','Energie & Makronährstoffe'],['vitamin','Vitamine'],['mineral','Mineralstoffe · Mengenelemente'],['trace','Spurenelemente'],['other','Weitere Nährstoffangaben']];
const fmt=(v,d=1)=>v===null||v===undefined||!Number.isFinite(v)?'—':new Intl.NumberFormat('de-CH',{maximumFractionDigits:d}).format(v);
const date=s=>new Intl.DateTimeFormat('de-CH',{day:'2-digit',month:'2-digit',year:'numeric',timeZone:'UTC'}).format(new Date(s+'T12:00:00Z'));
const range=p=>p.start===p.end?date(p.start):date(p.start)+' – '+date(p.end);
function tone(r){return ['met','within'].includes(r.status)?'met':['below','under_plan','over_plan'].includes(r.status)?'deviation':'neutral';}
function status(r){return r.status==='provisional'?'Vorläufig · '+(R.STATUS[r.relation]||'Angaben ergänzen'):r.status==='gaps'?'Datenlücken':R.STATUS[r.status]||'Nicht beurteilbar';}
function shortStatus(r){return {met:'Erreicht',within:'Im Planbereich',below:'Unter Vergleich',under_plan:'Unter Planbereich',over_plan:'Über Planbereich',provisional:'Vorläufig',gaps:'Datenlücken',no_data:'Keine Einträge',no_target:'Kein Ziel',incompatible:'Nicht vergleichbar',comparison:'Zahlenvergleich'}[r.status]||'Offen';}
function amount(r){return r.average===null?'—':(r.hasGaps?'≥ ':'')+fmt(r.average,r.unit==='kcal'?0:2)+' '+r.unit;}
function percent(r){return r.percent===null?'—':(r.hasGaps?'mind. ':'')+fmt(r.percent)+' %';}
function stats(rows){return rows.reduce((a,r)=>{const t=tone(r);if(t==='met')a.met++;else if(t==='deviation')a.deviation++;else a.open++;a.total++;return a;},{met:0,deviation:0,open:0,total:0});}
function headline(report){if(!report.selectedDays)return 'Dein Überblick wartet auf Einträge.';if(report.counts.provisional)return 'Deine Bilanz ist noch ein Zwischenstand.';if(report.counts.below)return 'Erreichte Werte und offene Ziele im Blick.';return 'Deine Nährstoffbilanz auf einen Blick.';}
function insights(report){
 const rows=report.rows,met=rows.filter(r=>tone(r)==='met'),below=rows.filter(r=>['below','under_plan'].includes(r.status)),gaps=rows.filter(r=>r.status==='gaps');
 const names=a=>a.slice(0,3).map(r=>r.label).join(', ')+(a.length>3?' …':'');
 return [
 {title:'Erreicht',text:met.length?names(met):'Noch keine abschliessend bewerteten Zieltreffer.',tone:met.length?'met':'neutral'},
 {title:'Unter dem Vergleich',text:below.length?names(below):'Keine bestätigten Unterschreitungen in dieser Datenbasis.',tone:below.length?'deviation':'neutral'},
 {title:'Nächster sinnvoller Schritt',text:report.recordedDays>report.completeDays?'Erfasste Tage prüfen und vollständige Protokolle unter «Heute» abschliessen.':gaps.length?'Nährwertangaben ergänzen, zum Beispiel bei '+names(gaps)+'.':!report.selectedDays?'Lebensmittel erfassen oder einen Zeitraum mit Einträgen wählen.':'Auch die Tagesverteilung und fehlende Protokolltage beachten.',tone:'neutral'}
 ];
}
function snapshot(report,name,meta={}){return JSON.parse(JSON.stringify({report,name:String(name||'Profil'),createdAt:meta.createdAt||new Date().toISOString(),syncPending:!!meta.syncPending,appVersion:'1.7.0'}));}
function filename(snap){const name=snap.name.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9_-]+/gi,'-').replace(/^-|-$/g,'').slice(0,60)||'Profil';return `Kompass-${name}-${snap.report.period.frequency}-${snap.report.period.start}-${snap.report.period.end}.pdf`;}
return {GROUPS,fmt,date,range,tone,status,shortStatus,amount,percent,stats,headline,insights,snapshot,filename};
});
