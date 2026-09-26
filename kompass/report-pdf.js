/* On-device PDF export; pinned local jsPDF, no HTML evaluation or upload service. */
(function(root){'use strict';
const V=root.NK_REPORT_PRESENTATION,R=root.NK_REPORTS;
const COL={ink:'#203b32',green:'#1b493b',lime:'#d9e9a1',muted:'#69756b',line:'#dfe6dc',paper:'#f6f7f1',met:'#e7efe2',deviation:'#faeddc',neutral:'#eaf0f2',amber:'#805522',blue:'#526977',white:'#ffffff'};
const E=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
// Standard PDF fonts cover German/Spanish and µ. Equivalent text for mathematical glyphs.
const clean=v=>String(v??'').replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g,'').replace(/≥/g,'mind. ').replace(/α/g,'Alpha').replace(/↔/g,' / ').replace(/→/g,' > ').replace(/[–—]/g,'-').replace(/[‘’]/g,"'").replace(/[„“”«»]/g,'"').replace(/\u2026/g,'...').replace(/\u202f|\u00a0/g,' ');
function create(snapshot,{detail=true}={}){
 if(!root.jspdf?.jsPDF)throw Error('PDF-Modul noch nicht verfügbar. Bitte die App einmal mit Internet öffnen.');
 const snap=JSON.parse(JSON.stringify(snapshot)),report=snap.report;
 if(!report||!Array.isArray(report.rows)||report.rows.length>100||!Array.isArray(report.days)||report.days.length>31)throw Error('Ungültiger Report. Bitte den Zeitraum erneut öffnen.');
 const doc=new root.jspdf.jsPDF({unit:'pt',format:'a4',compress:true,putOnlyUsedFonts:true});
 const W=595.28,H=841.89,M=42,B=W-M,WIDTH=W-2*M,FOOT=785;
 const refs=[];for(const r of report.rows){if(r.ref?.url&&!refs.includes(r.ref.url)&&/^https:\/\//.test(r.ref.url))refs.push(r.ref.url);}
 let y=0,pageTitle='';const layout=[];
 doc.setProperties({title:clean(R.TITLES[report.period.frequency]+' · '+snap.name),subject:'Persönliche Nährstoffbilanz – exportierter Stand',author:'Nährstoff-Kompass',creator:'Nährstoff-Kompass 1.7.0; lokale PDF-Erstellung'});
 function font(size=10,bold=false){doc.setFont('helvetica',bold?'bold':'normal');doc.setFontSize(size);}
 function txt(value,x,y,size=10,color=COL.ink,bold=false){
  const s=clean(value);font(size,bold);doc.setTextColor(color);
  if(/[^\u0020-\u00ff\n\r]/u.test(s)&&root.document){
   // Preserve uncommon profile/food characters without distributing any font file.
   const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d'),scale=3;
   ctx.font=`${bold?'600':'400'} ${size*scale}px Arial, sans-serif`;
   canvas.width=Math.ceil(ctx.measureText(s).width+10);canvas.height=Math.ceil(size*scale*1.5);
   ctx.font=`${bold?'600':'400'} ${size*scale}px Arial, sans-serif`;ctx.fillStyle=color;ctx.textBaseline='alphabetic';ctx.fillText(s,0,size*scale);
   doc.addImage(canvas.toDataURL('image/png'),'PNG',x,y-size,canvas.width/scale,canvas.height/scale);
  }else doc.text(s,x,y);
 }
 function lines(value,width,size=10,bold=false){font(size,bold);return doc.splitTextToSize(clean(value),width);}
 function para(value,x,start,width,size=10,color=COL.muted,bold=false,lineHeight=size*1.42){const a=lines(value,width,size,bold);a.forEach((l,i)=>txt(l,x,start+i*lineHeight,size,color,bold));return start+a.length*lineHeight;}
 function box(x,y,w,h,fill,r=12){doc.setFillColor(fill);doc.roundedRect(x,y,w,h,r,r,'F');}
 function rule(y){doc.setDrawColor(COL.line);doc.setLineWidth(.5);doc.line(M,y,B,y);}
 function progress(x,y,w,percent,tone='neutral'){box(x,y,w,5,COL.line,2);if(percent!==null&&Number.isFinite(percent)&&percent>0){const width=w*Math.min(100,Math.max(0,percent))/100;doc.setFillColor(tone==='met'?'#7d9e63':tone==='deviation'?'#c19960':'#97aab3');doc.rect(x,y,width,5,'F');}}
 function header(title){txt('NÄHRSTOFF / KOMPASS',M,35,9,COL.green,true);txt('PRIVATER REPORT',B-87,35,8,COL.muted);rule(48);txt(title,M,83,22,COL.ink,true);para(snap.name+' · '+V.range(report.period),M,103,WIDTH,9,COL.muted);y=129;pageTitle=title;}
 function next(title=pageTitle){doc.addPage();header(title);}
 function ensure(h,title=pageTitle){if(y+h>FOOT-10)next(title);}
 function section(title){ensure(48);txt(title,M,y,14,COL.ink,true);y+=23;}
 function body(value,size=10){const a=lines(value,WIDTH,size);for(const l of a){ensure(size*1.48);txt(l,M,y,size);y+=size*1.48;}y+=9;}
 const created=new Date(snap.createdAt);const stamp=Number.isFinite(+created)?new Intl.DateTimeFormat('de-CH',{dateStyle:'short',timeStyle:'short'}).format(created):snap.createdAt;
 // Page one is deliberately compact and independent of the screen filter.
 txt('NÄHRSTOFF / KOMPASS',M,34,10,COL.green,true);txt('DEIN PERSÖNLICHER REPORT',B-154,34,8,COL.muted);
 box(M,55,WIDTH,174,COL.green,18);
 txt(R.TITLES[report.period.frequency].toUpperCase(),M+23,82,9,'#dae6db',true);
 txt({daily:'Dein Tag.',weekly:'Deine Woche.',monthly:'Dein Monat.'}[report.period.frequency],M+23,124,35,COL.white,true);
 txt('Auf einen Blick.',M+23,166,35,COL.lime,true);
 para(snap.name,M+24,192,WIDTH-48,10,COL.white,false,12);
 txt(V.range(report.period),M+24,219,10,'#dbe7da');
 txt(String(report.recordedDays)+' / '+report.elapsedDays,B-113,120,31,COL.lime,true);
 txt('Tage erfasst',B-113,144,10,COL.white);
 txt(report.completeDays+' vollständig',B-113,164,9,'#dbe7da');
 const phase=report.ongoing?'Laufender Zeitraum · Zwischenstand':report.partialPeriod?'Teilbericht · Protokolltage fehlen':'Abgeschlossener Zeitraum';
 txt(phase,M,255,11,COL.ink,true);
 para(report.selectedDays+' Tage berücksichtigt · '+(report.completeOnly?'nur vollständig markierte Protokolle':'alle protokollierten Tage')+(report.futureDays?' · '+report.futureDays+' Tage noch zukünftig':''),M,272,WIDTH,9);
 const stats=V.stats(report.rows),cardW=(WIDTH-30)/4;
 [[report.counts.met,'Erreicht / im Plan',COL.met,COL.green],[report.counts.below,'Unter Vergleich',COL.deviation,COL.amber],[report.counts.above,'Über Makro-Plan','#f3e4db','#80513a'],[stats.open,'Offen / ohne Bewertung',COL.neutral,COL.blue]].forEach(([num,label,bg,ink],i)=>{const x=M+i*(cardW+10);box(x,308,cardW,77,bg,12);txt(String(num),x+14,344,28,ink,true);para(label,x+14,365,cardW-23,8,ink,false,10);});
 txt('Zählung nur in der gewählten Datenbasis – kein Gesundheitsscore.',M,404,8,COL.muted);if(snap.syncPending)txt('Lokaler Stand: enthält noch nicht synchronisierte Änderungen.',M,419,8,COL.amber);
 txt('Energie & Makros',M,434,15,COL.ink,true);txt(report.period.frequency==='daily'?'Erfasste Tagesmenge':'Mittelwerte pro berücksichtigtem Tag',M,450,8,COL.muted);
 const macros=report.rows.filter(r=>['energy','protein','carbs','fat'].includes(r.key));
 macros.forEach((r,i)=>{const x=M+i*(cardW+10);box(x,465,cardW,113,COL.paper,12);txt(r.label,x+12,484,9,COL.muted);if(r.hasGaps&&r.average!==null)txt('Bekannte Teilmenge',x+12,499,7,COL.blue);const value=r.average===null?'—':V.fmt(r.average,r.unit==='kcal'?0:1)+' '+r.unit;let size=17;font(size,true);while(doc.getTextWidth(clean(value))>cardW-24&&size>7){size-=.5;font(size,true);}txt(value,x+12,519,size,COL.ink,true);progress(x+12,533,cardW-24,r.percent,V.tone(r));txt('Ziel '+(r.target!==null?V.fmt(r.target)+' '+r.unit:'offen'),x+12,551,8,COL.muted);txt(V.shortStatus(r),x+12,568,8,V.tone(r)==='deviation'?COL.amber:COL.muted);});
 txt('Deine Bilanz in drei Sätzen',M,612,15,COL.ink,true);
 const iw=(WIDTH-24)/3;
 V.insights(report).forEach((v,i)=>{const x=M+i*(iw+12);txt('0'+(i+1)+' / '+v.title,x,638,9,COL.green,true);const a=lines(v.text,iw,9);a.slice(0,6).forEach((t,j)=>txt(t,x,655+j*12,9,COL.muted));});
 para('Fehlende Tage sind keine Nullzufuhr. „mind.“ bedeutet bekannte Teilmenge. Offene Protokolle sind vorläufig. Ziele sind aktuelle Referenz-/Planwerte; eine Unterschreitung ist keine Mangeldiagnose.',M,747,WIDTH,8,COL.muted,false,11);
 if(!detail)para('Kompaktansicht. Alle Einzelwerte, Datenlücken und Quellen stehen im vollständigen PDF bzw. in der App.',M,780,WIDTH,7,COL.muted,false,9);
 if(detail){
  next('Deine Nährstoffe im Detail');
  para('Tagesmittel der '+report.selectedDays+' berücksichtigten Tage; Vergleich mit den aktuellen Profilzielen. Kein gesamter Wochen-/Monatsnachweis bei fehlenden Tagen.',M,y,WIDTH,9);y+=40;
  const columns=()=>{box(M,y,WIDTH,25,COL.paper,5);txt('NÄHRSTOFF',M+8,y+16,8,COL.muted,true);txt('ERFASST / TAG',M+177,y+16,8,COL.muted,true);txt('ZIEL / TAG',M+280,y+16,8,COL.muted,true);txt('EINORDNUNG',M+365,y+16,8,COL.muted,true);y+=32;};
  for(const [group,label] of V.GROUPS){const rows=report.rows.filter(r=>r.group===group);if(!rows.length)continue;ensure(95,'Deine Nährstoffe im Detail');section(label);columns();
   for(const r of rows){const labelLines=lines(r.label,155,10,true),statusLines=lines(V.status(r),WIDTH-375,9),height=Math.max(37,labelLines.length*12+10,statusLines.length*11+10);
    if(y+height>FOOT-10){next('Deine Nährstoffe im Detail');txt(label+' · Fortsetzung',M,y,12,COL.ink,true);y+=23;columns();}
    layout.push({page:doc.getNumberOfPages(),kind:'nutrient',key:r.key,y,height});
    labelLines.forEach((t,j)=>txt(t,M+8,y+12+j*13,10,COL.ink,true));
    txt(V.amount(r),M+177,y+12,10,COL.ink,true);txt(V.percent(r),M+177,y+27,8,COL.muted);
    para(r.target===null?'Kein Ziel':V.fmt(r.target)+' '+r.unit,M+280,y+12,77,9,COL.muted,false,12);
    statusLines.forEach((t,j)=>txt(t,M+365,y+12+j*12,9,V.tone(r)==='met'?COL.green:V.tone(r)==='deviation'?COL.amber:COL.blue));
    y+=height;rule(y-4);
   }y+=15;
  }
  next('Datenbasis & Einordnung');
  section('So liest du deinen Report');
  body(report.recordedDays+' von '+report.elapsedDays+' bisherigen Tagen protokolliert, '+report.completeDays+' vollständig markiert. '+report.selectedDays+' Tage sind in diesem PDF berücksichtigt. '+report.unrecordedDays+' bisherige Tage ohne Einträge und '+report.futureDays+' zukünftige Tage gehen nicht als null in den Durchschnitt ein.');
  body('Eine bekannte Teilmenge („mind.“) ist kein vollständiger Wert. Fehlen Nährstoffangaben, erfolgt keine Erfolgs-/Mangelbewertung. Auch mit vollständigen Zahlen bleibt die Einordnung vorläufig, solange ein berücksichtigter Protokolltag offen ist.');
  body('„Erreicht“: mindestens 100 % bei Protein und passenden Mikronährstoffreferenzen. „Im Planbereich“: 90–110 % bei Energie, Kohlenhydraten und Fett, als Darstellungsannahme der App. Mehr ist nicht automatisch besser; 100 % ist keine Sicherheitsobergrenze.');
  body(report.targetBasis+' Dieser Export hält den lokalen Stand vom '+stamp+' fest.'+(snap.syncPending?' Zum Exportzeitpunkt waren lokale Änderungen noch nicht synchronisiert.':''));
  body('Referenzwerte müssen nicht jeden Tag genau erreicht werden. Eine rechnerische Unterschreitung ist keine Mangeldiagnose. Vitamin D aus körpereigener Bildung wird im Tagebuch nicht gemessen. Der Report enthält keine Supplement-Dosierungsempfehlungen.');
  section('Tagesverteilung & Datenlücken');
  body('Die Nährstofftabelle zeigt Mittelwerte, nicht die Zahl erreichter Einzeltage. Detaillierte Tageswerte stehen beim Aufklappen jedes Nährstoffs in der App.',9);
  const gaps=report.rows.filter(r=>r.hasGaps);
  body(gaps.length?'Fehlende Nährstoffzahlen bei: '+gaps.map(r=>r.label+' ('+r.fullDays+'/'+r.selectedDays+' Tage vollständig)').join('; ')+'.':'Alle berücksichtigten Nährstoffzahlen sind vollständig vorhanden.',9);
  const names=[...new Set(gaps.flatMap(r=>r.missing))];
  if(names.length)body('Beispiele betroffener Einträge: '+names.slice(0,4).join('; ')+(names.length>4?' · und '+(names.length-4)+' weitere. Einzelheiten in der App.':'.'),9);
  if(report.notes.length){section('Hinweise aus der Zielberechnung');for(const note of report.notes)body(note,9);}
  next('Referenzen & Quellen');
  body('Verwendet werden die aktuell gespeicherten Referenzen bzw. eigenen Ziele des aktiven Profils. Die Quellen nachfolgend erläutern die Vergleichswerte, nicht Laborwerte. Vitamin-/Mineralstoff-Äquivalente werden nur verglichen, wenn die bestehende App-Berechnung dies erlaubt.',9);
  const bundles=new Map();
  for(const r of report.rows.filter(r=>r.ref)){const id=r.ref.url||'manual';if(!bundles.has(id))bundles.set(id,[]);bundles.get(id).push(r);}
  for(const [url,rows] of bundles){
   const labels=rows.map(r=>r.label).join(', '),kind=[...new Set(rows.map(r=>r.ref.type||'Referenz'))].join(' / '),years=[...new Set(rows.map(r=>r.ref.year).filter(Boolean))].join(', ');
   const a=lines(labels,WIDTH,10,true);ensure(a.length*14+39,'Referenzen & Quellen');a.forEach(t=>{txt(t,M,y,10,COL.ink,true);y+=14;});txt(kind+(years?' · Stand '+years:''),M,y,8,COL.muted);y+=14;
   if(/^https:\/\//.test(url)){font(8);doc.setTextColor(COL.green);doc.textWithLink('Quelle öffnen · '+new URL(url).hostname,M,y,{url});y+=22;}else{txt('Vom Profil vorgegebene eigene Zielwerte.',M,y,8,COL.muted);y+=22;}
  }
  section('Allgemeine Einordnung');for(const [label,url] of [['DGE: Referenzwerte und Grenzen des Vergleichs',R.SOURCES.reference],['DGE: Vitamin D und körpereigene Bildung',R.SOURCES.vitD]]){ensure(25);font(9);doc.setTextColor(COL.green);doc.textWithLink(label,M,y,{url});y+=23;}
  body('Privater Export. Die PDF-Datei wird auf deinem Gerät erzeugt und enthält persönliche Angaben. Sie wird nicht automatisch an einen Dienst, in euren gemeinsamen Produktkatalog oder auf GitHub hochgeladen.',9);
 }
 const count=doc.getNumberOfPages();for(let i=1;i<=count;i++){doc.setPage(i);rule(801);txt('KOMPASS / '+(detail?'VOLLSTÄNDIG':'KOMPAKT')+' · '+stamp,M,818,7,COL.muted);txt(i+' / '+count,B-28,818,8,COL.muted);}
 const blob=doc.output('blob');return {blob,filename:V.filename(snap),pages:count,layout,snapshot:snap};
}
let activeURL=null,current=null,sequence=0;
function dispose(){sequence++;if(activeURL){URL.revokeObjectURL(activeURL);activeURL=null;}current=null;}
function open(report,name,meta={}){
 let dlg=document.getElementById('report-export-dialog');if(!dlg){dlg=document.createElement('dialog');dlg.id='report-export-dialog';document.body.append(dlg);}dispose();
 const snap=V.snapshot(report,name,meta),owner=root.NK_HOUSEHOLD?.id||null;
 dlg.innerHTML=`<div class="modal-head"><h2>Dein Report als PDF</h2><button type="button" class="icon-btn" id="pdf-close" aria-label="Schliessen">×</button></div><p><b>${E(snap.name)}</b> · ${E(V.range(report.period))}</p><p class="small">${report.selectedDays} berücksichtigte Tage · ${report.completeOnly?'nur vollständige Protokolle':'alle protokollierten Tage'}. Das PDF umfasst den gewählten Zeitraum und <b>alle Nährstoffe</b>, unabhängig vom Bildschirmfilter.</p>${snap.syncPending?'<p class="notice">Enthält noch nicht synchronisierte lokale Änderungen. Das PDF kennzeichnet diesen Stand.</p>':''}<div class="pdf-layouts"><label><input type="radio" name="pdf-layout" value="compact"><b>Kompakt</b><small>Eine Seite mit Übersicht, Makros und Kernaussagen.</small></label><label><input type="radio" name="pdf-layout" value="full" checked><b>Vollständig</b><small>Übersicht, alle Nährstoffwerte, Datenlücken und Quellen.</small></label></div><button type="button" class="button wide" id="pdf-create">PDF erstellen</button><div class="pdf-status" id="pdf-status" role="status"></div><div id="pdf-result"></div><p class="pdf-privacy">Erstellung nur auf diesem Gerät. Kein Upload. Die Datei ist nicht passwortverschlüsselt und enthält persönliche Nährstoffangaben. Bewusst speichern oder teilen.</p>`;
 dlg.querySelector('#pdf-close').onclick=()=>dlg.close();dlg.onclose=dispose;
 dlg.querySelector('#pdf-create').onclick=()=>{
  if(owner!==(root.NK_HOUSEHOLD?.id||null)){dlg.close();return;}
  const button=dlg.querySelector('#pdf-create'),status=dlg.querySelector('#pdf-status');button.disabled=true;status.textContent='PDF wird auf deinem Gerät erstellt …';
  const ticket=++sequence;requestAnimationFrame(()=>{try{if(!dlg.open||ticket!==sequence||owner!==(root.NK_HOUSEHOLD?.id||null))return;
   if(activeURL)URL.revokeObjectURL(activeURL);current=create(snap,{detail:dlg.querySelector('input[name="pdf-layout"]:checked').value==='full'});activeURL=URL.createObjectURL(current.blob);
   const result=dlg.querySelector('#pdf-result');result.innerHTML=`<div class="pdf-ready"><b>Dein PDF ist bereit.</b><p class="small">${current.pages} ${current.pages===1?'Seite':'Seiten'} · ${Math.ceil(current.blob.size/1024)} KB</p><div class="actions"><a class="button" id="pdf-download" download="${E(current.filename)}" href="${activeURL}">PDF speichern</a><a class="button secondary" id="pdf-open" href="${activeURL}" target="_blank" rel="noopener">PDF öffnen</a><button type="button" class="button secondary" id="pdf-share" hidden>PDF teilen</button></div><p class="tiny">Auf dem iPhone gegebenenfalls «PDF öffnen» → Teilen → «In Dateien sichern» verwenden.</p></div>`;
   const file=new File([current.blob],current.filename,{type:'application/pdf'}),share=dlg.querySelector('#pdf-share');
   if(navigator.canShare?.({files:[file]})){share.hidden=false;share.onclick=async()=>{try{await navigator.share({files:[file],title:'Nährstoff-Kompass Report'});}catch(e){status.textContent=e.name==='AbortError'?'Teilen abgebrochen. Das PDF bleibt bereit.':'Teilen nicht verfügbar. Bitte PDF speichern oder öffnen.';}};}
   status.textContent='Erstellt. Noch nicht automatisch gespeichert.';
  }catch(e){status.textContent='PDF nicht erstellt: '+e.message;}finally{button.disabled=false;}});
 };
 if(!dlg.open)dlg.showModal();
}
root.NK_REPORT_PDF={create,open,clean};
})(typeof window!=='undefined'?window:globalThis);
