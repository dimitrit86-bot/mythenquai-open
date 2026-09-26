/* Explicit, profile-local planning presets. No network/storage and no inferred personal data. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.NK_MACROS=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const VERSION='1.5.0',CHECKED='2026-09-26';
 const SOURCES={
  energy:'https://www.dge.de/gesunde-ernaehrung/faq/energiezufuhr/',
  protein:'https://www.dge.de/wissenschaft/referenzwerte/protein/',
  sport:'https://www.dge.de/presse/meldungen/2020/positionspapier-zur-proteinzufuhr-im-sport/',
  loss:'https://pubmed.ncbi.nlm.nih.gov/25926512/',
  fat:'https://www.dge.de/wissenschaft/referenzwerte/fett-essenzielle-fettsaeuren/',
  carbs:'https://www.dge.de/wissenschaft/referenzwerte/kohlenhydrate/',
  referenceWeight:'https://www.dge.de/wissenschaft/referenzwerte/energie/'
 };
 const PRESETS={
  normal:{label:'Normal · Gewicht halten',protein:null,description:'Alltagsorientierung: Protein-Basisreferenz, geschätzte Erhaltungsenergie, 30 % Energie aus Fett und der Rest aus Kohlenhydraten.'},
  muscle:{label:'Muskelaufbau',protein:1.6,description:'Für regelmässiges Krafttraining: 1,6 g Protein/kg Berechnungsgewicht. Kleiner Energieaufschlag von 5 % (höchstens 200 kcal), bei BMI über 25 zunächst Erhaltungsenergie. Das sind anpassbare App-Startwerte, keine Muskelaufbau-Garantie.'},
  sport:{label:'Sportler · ambitioniertes Training',protein:1.4,description:'Startwert für mehr als 5 Trainingsstunden pro Woche: 1,4 g Protein/kg Berechnungsgewicht und geschätzte Erhaltungsenergie. Bei weniger Sport genügt meist «Normal». Sehr intensive Ausdauerbelastungen benötigen eine individuellere Planung.'},
  loss:{label:'Abnehmen · moderat',protein:1.2,description:'Anpassbarer Startwert: 1,2 g Protein/kg Berechnungsgewicht und 10 % weniger als die geschätzte Erhaltungsenergie (höchstens 400 kcal weniger). Keine vorgegebene Abnehmgeschwindigkeit.'}
 };
 const ACTIVITIES=[['','Bitte Aktivität einschätzen'],['1.4','Wenig aktiv · überwiegend sitzend (1,4)'],['1.6','Leicht aktiv · Sitzen, Gehen und Stehen (1,6)'],['1.8','Aktiv · viel Bewegung, regelmässiger Sport (1,8)'],['2','Sehr aktiv · anstrengender Alltag / viel Training (2,0)'],['2.2','Hoch aktiv · körperliche Arbeit und viel Training (2,2)']];
 const valid=v=>typeof v==='number'&&Number.isFinite(v)&&v>0;
 const active=p=>Object.prototype.hasOwnProperty.call(PRESETS,p?.goal);
 function validate(p){
  if(p.goal!==undefined&&p.goal!==null&&!['',...Object.keys(PRESETS)].includes(p.goal))throw Error('Ungültiges Ernährungsziel.');
  if(p.pal!==undefined&&p.pal!==null&&![1.4,1.6,1.8,2,2.2].includes(p.pal))throw Error('Bitte ein gültiges Aktivitätsniveau auswählen.');
 }
 function referenceWeight(height){return valid(height)&&height>=130&&height<=220?22*(height/100)**2:null;}
 function calculate(p){
  const values={},notes=[],detail={mode:p?.goal||'',label:PRESETS[p?.goal]?.label||'Basiswerte / eigene Ziele',rest:null,maintenance:null,energyAdjustment:0,proteinWeight:null,proteinFactor:null,bmi:null,macroEnergy:null,manual:[]};
  const own=k=>valid(p?.manual?.[k])?p.manual[k]:null;
  const ref=(k,value,url,note,type='Tagesziel · App-Schätzung')=>{if(valid(value))values[k]={value,url,year:2026,type,note,sourceLabel:type==='Tagesziel · App-Schätzung'?'App-Planungsmodell auf Basis der verlinkten Quelle':'DGE/ÖGE',checkedAt:CHECKED};};
  const finish=()=>{for(const k of ['energy','protein','fat','carbs'])if(own(k)!==null){values[k]={value:own(k),type:'Eigenes Ziel',note:'Manuell eingetragen; ersetzt die Automatik für diesen Wert.',url:null,year:null};detail.manual.push(k);}
   const e=values.energy?.value,pr=values.protein?.value,f=values.fat?.value,c=values.carbs?.value;
   if([pr,f,c].every(valid)){detail.macroEnergy=4*pr+9*f+4*c;if(valid(e)&&Math.abs(detail.macroEnergy-e)>Math.max(50,e*.05))notes.push('Die eigenen Makroziele passen rechnerisch nicht zum Energieziel (4/4/9-Rechnung). Bitte die Angaben prüfen.');}
   if(valid(e)&&valid(pr)&&pr*4/e>.35)notes.push('Der Proteinanteil liegt über 35 % des Energieziels. Eigene Vorgaben bitte individuell prüfen.');
   if(valid(e)&&valid(f)&&(f*9/e<.2||f*9/e>.35))notes.push('Das eigene Fettziel liegt ausserhalb von 20–35 % der Energie. Die App ändert es nicht automatisch.');
   return {values,notes,detail};};
  if(!active(p))return finish();
  const age=p.age;
  if(!valid(age)||age<19||age>120||p.special){notes.push('Diese automatischen Zielprofile gelten nur für gesunde Erwachsene ab 19 Jahren. Bei Schwangerschaft, Stillzeit oder medizinisch angepasster Ernährung nur individuell abgestimmte eigene Ziele verwenden.');return finish();}
  if(!valid(p.weight)||!valid(p.height)){notes.push('Für gewichtsbezogene Ziele Körpergewicht und Grösse ergänzen.');return finish();}
  const bmi=p.weight/(p.height/100)**2;detail.bmi=bmi;
  if(p.weight<35||p.weight>250||p.height<130||p.height>220||bmi<18.5||bmi>40){notes.push('Körpermasse liegen ausserhalb des automatischen Planungsbereichs dieser App. Keine automatische Diät oder Makroempfehlung; eigene fachlich abgestimmte Ziele bleiben möglich.');return finish();}
  const cw=valid(p.calcWeight)?p.calcWeight:bmi<=25?p.weight:null;
  if(cw!==null){detail.proteinWeight=cw;detail.proteinFactor=PRESETS[p.goal].protein||(age>=65?1:.8);
   ref('protein',cw*detail.proteinFactor,p.goal==='normal'?SOURCES.protein:p.goal==='loss'?SOURCES.loss:SOURCES.sport,`${detail.proteinFactor} g/kg × ${cw} kg Berechnungsgewicht. ${p.goal==='normal'?'DGE/ÖGE-Basisreferenz.':'Anpassbarer Startwert dieses App-Profils; kein exakt gemessener Bedarf.'}`,p.goal==='normal'?(age>=65?'Schätzwert':'Empfohlene Zufuhr'):'Tagesziel · App-Schätzung');
  }else notes.push('Protein: Bei BMI über 25 bitte ein Berechnungsgewicht bestätigen. «Referenzgewicht einsetzen» bietet eine BMI-22-Modellannahme an, kein Abnehmziel.');
  if(p.goal==='sport')notes.push('Sportler-Startwert für mehr als 5 Trainingsstunden pro Woche; die DGE nennt hierfür je nach Belastung 1,2–2,0 g/kg. Training ist bereits im gewählten Aktivitätsfaktor enthalten und wird nicht nochmals addiert.');
  const energyInputs=['m','w'].includes(p.sex)&&[1.4,1.6,1.8,2,2.2].includes(p.pal)&&age<=80;
  let autoEnergy=null;
  if(energyInputs){
   detail.rest=(.047*p.weight-.01452*age+3.21+(p.sex==='m'?1.009:0))*239;
   detail.maintenance=detail.rest*p.pal;
   autoEnergy=detail.maintenance;
   if(p.goal==='muscle'){if(bmi<=25){detail.energyAdjustment=Math.min(200,autoEnergy*.05);autoEnergy+=detail.energyAdjustment;}else notes.push('Muskelaufbau: Bei BMI über 25 verwendet die App zunächst Erhaltungsenergie, keinen automatischen Überschuss.');}
   if(p.goal==='loss'){
    if(bmi<20||age>=65){autoEnergy=null;notes.push('Abnehmen: Unter BMI 20 oder ab 65 Jahren setzt diese App kein automatisches Defizit. Bitte das Ziel individuell abstimmen. Dies ist eine vorsichtige App-Grenze, keine Diagnose.');}
    else{detail.energyAdjustment=-Math.min(400,autoEnergy*.1);autoEnergy+=detail.energyAdjustment;}
   }
   if(autoEnergy!==null&&(autoEnergy<Math.max(1500,detail.rest)||autoEnergy>6000)){autoEnergy=null;notes.push('Energie ausserhalb des vorsichtigen automatischen Planungsrahmens. Kein automatisches Kalorienziel; 1’500 kcal sind eine App-Grenze, kein universeller Mindestbedarf.');}
  }else if(own('energy')===null)notes.push('Für das Energie-, Fett- und Kohlenhydratziel Geschlecht und Aktivität ergänzen. Die automatische Energieformel wird hier bis 80 Jahre verwendet; alternativ ein eigenes Energieziel eintragen.');
  if(autoEnergy!==null)ref('energy',autoEnergy,SOURCES.energy,'Ruheenergie nach DGE-FAQ × gewählter Aktivitätsfaktor. Aktuelles Gewicht für Energie; Berechnungsgewicht nur für Protein. Auf-/Abschläge sind App-Startannahmen, keine DGE-Vorgaben.');
  const energy=own('energy')??autoEnergy,protein=own('protein')??values.protein?.value;
  if(valid(energy)&&energy>=1500&&energy<=6000){
   const fat=own('fat')??energy*.3/9;
   ref('fat',fat,SOURCES.fat,'App-Standard: 30 % des Energieziels ÷ 9 kcal/g. Kein exakt individueller Fettbedarf.');
   if(valid(protein)){
    const rest=energy-protein*4-fat*9;
    if(rest>0){ref('carbs',rest/4,SOURCES.carbs,'Verbleibende Energie nach Protein und Fett ÷ 4 kcal/g. Vereinfachte 4/4/9-Planung; Lebensmittelenergie kann wegen Ballaststoffen, Polyolen oder Alkohol abweichen.');
     if(p.goal==='normal'&&rest/energy<.5)notes.push('Die gewählte Kombination liegt unter der allgemeinen DGE-Orientierung von mehr als 50 % Kohlenhydratenergie. Eigene Vorgaben prüfen.');
    }else notes.push('Protein- und Fettziele verbrauchen bereits das ganze Energieziel. Deshalb kein automatisches Kohlenhydratziel statt eines negativen oder erfundenen Wertes.');
   }else notes.push('Kohlenhydrate können erst mit einem Protein-Berechnungsgewicht oder einem eigenen Proteinziel abgeleitet werden.');
  }else if(own('energy')!==null)notes.push('Eigenes Energieziel gespeichert; ausserhalb 1’500–6’000 kcal werden keine zusätzlichen automatischen Makros abgeleitet. Das ist eine App-Grenze, keine individuelle Ernährungsempfehlung.');
  return finish();
 }
 return {VERSION,CHECKED,SOURCES,PRESETS,ACTIVITIES,active,validate,referenceWeight,calculate};
});
