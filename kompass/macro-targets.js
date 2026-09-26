/* Transparent adult macro planning. No storage or network. Defaults are planning assumptions, not diagnoses. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.NK_MACROS=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const presets=Object.freeze({
 normal:{label:'Normal · Gewicht halten',protein:0.8,fat:0.30,energy:0,description:'Basisreferenz für Protein, 30 % der Energie aus Fett, übrige Planenergie aus Kohlenhydraten.'},
 muscle:{label:'Muskelaufbau',protein:1.6,fat:0.30,energy:0.05,description:'Für regelmässiges Krafttraining: 1,6 g Protein/kg Berechnungsgewicht und ein kleiner Planüberschuss von 5 % (höchstens 200 kcal).'},
 sport:{label:'Sportler · intensives Training',protein:1.4,fat:0.25,energy:0,description:'Startwert für intensives Training, insbesondere über 5 Stunden/Woche: 1,4 g Protein/kg und 25 % Fett. Der Aktivitätsfaktor muss das Training bereits enthalten.'},
 loss:{label:'Abnehmen · moderat',protein:1.2,fat:0.30,energy:-0.10,description:'Planstart mit 10 % weniger als dem geschätzten Erhaltungsbedarf (höchstens 300 kcal), 1,2 g Protein/kg Berechnungsgewicht und 30 % Fett.'}
});
const activities=Object.freeze([[1.4,'Wenig aktiv · überwiegend sitzend (1,4)'],[1.6,'Leicht aktiv · zeitweise Gehen/Stehen (1,6)'],[1.8,'Aktiv · viel Bewegung oder regelmässiges Training (1,8)'],[2.0,'Sehr aktiv · hohe Alltags- und Trainingsbelastung (2,0)'],[2.2,'Sehr hohe Belastung · intensive Trainingsphasen (2,2)']]);
const sources=Object.freeze({
 energy:'https://www.dge.de/gesunde-ernaehrung/faq/energiezufuhr/',
 protein:'https://www.dge.de/wissenschaft/referenzwerte/protein/',
 fat:'https://www.dge.de/wissenschaft/referenzwerte/fett-essenzielle-fettsaeuren/',
 carbs:'https://www.dge.de/wissenschaft/referenzwerte/kohlenhydrate/',
 sport:'https://www.dge.de/presse/meldungen/2020/positionspapier-zur-proteinzufuhr-im-sport/',
 sportFat:'https://www.dge.de/gesunde-ernaehrung/gezielte-ernaehrung/ernaehrung-und-sport/',
 muscle:'https://pubmed.ncbi.nlm.nih.gov/28698222/',
 loss:'https://pubmed.ncbi.nlm.nih.gov/25926512/'
});
const positive=v=>typeof v==='number'&&Number.isFinite(v)&&v>0;
const num=v=>new Intl.NumberFormat('de-CH',{maximumFractionDigits:1}).format(v);
function validate(p){
 if(p.nutritionMode!=null&&p.nutritionMode!==''&&!Object.hasOwn(presets,p.nutritionMode))throw Error('Ungültiges Ernährungsprofil.');
 if(p.activityPAL!=null&&!activities.some(([v])=>v===p.activityPAL))throw Error('Ungültiges Aktivitätsniveau.');
}
function calculate(p){
 const mode=p.nutritionMode||'',preset=presets[mode];
 const result={mode,label:preset?.label||'Bisherige Referenzen',values:{},notes:[],weight:null,weightSource:'',rest:null,maintenance:null,energyAdjustment:0,macroEnergy:null,complete:false};
 const {values,notes}=result,own=p.manual||{};
 const manual=k=>positive(own[k])?own[k]:null;
 for(const k of ['energy','protein','fat','carbs'])if(manual(k)!==null)values[k]={value:manual(k),type:'Eigenes Ziel',note:'Von dir eingetragener Wert. Beim Profilwechsel nicht überschrieben.',url:null,year:null};
 if(!preset)return result;
 const add=(k,v,source,note)=>{if(!values[k]&&positive(v))values[k]={value:v,type:'Planungswert',url:sources[source],year:2026,note};};
 const stop=message=>{notes.push(message);return result;};
 if(!Number.isInteger(p.age)||p.age<19||p.age>120||p.special)return stop('Automatische Makroplanung nur für gesunde Erwachsene ab 19 Jahren. Bei Schwangerschaft, Stillzeit, Erkrankungen oder medizinisch angepasster Ernährung eigene fachlich abgestimmte Ziele verwenden.');
 if(!positive(p.weight)||!positive(p.height))return stop('Bitte Körpergewicht und Körpergrösse ergänzen. Eigene Zielwerte bleiben unabhängig davon erhalten.');
 const bmi=p.weight/(p.height/100)**2;
 if(bmi<18.5||bmi>40)return stop('Für diese Körpermasse wird kein pauschaler Makroplan erstellt. Bitte individuelle Ziele fachlich abstimmen; eigene Eingaben bleiben möglich.');
 if(mode==='loss'&&(bmi<20||p.age>=65))return stop('Für Abnehmen bei BMI unter 20 oder ab 65 Jahren erstellt diese App vorsorglich keinen automatischen Plan. Eine individuelle fachliche Abstimmung ist hier sinnvoll. Dies ist eine App-Schutzregel, keine Diagnose.');
 result.weight=positive(p.calcWeight)?p.calcWeight:bmi>25?22*(p.height/100)**2:p.weight;
 result.weightSource=positive(p.calcWeight)?'Eigenes Protein-Berechnungsgewicht':bmi>25?'Referenzgewicht aus BMI 22 (App-Annahme, kein Wunschgewicht)':'Aktuelles Körpergewicht';
 if(bmi>25&&!positive(p.calcWeight))notes.push('Protein wird mit '+num(result.weight)+' kg berechnet (Grösse × Grösse × BMI 22), nicht mit '+num(p.weight)+' kg. Diese ausdrücklich vereinfachte Referenzgewicht-Annahme ist kein Abnehmziel. Bei hoher Muskelmasse ein passendes Berechnungsgewicht eintragen.');
 const coefficient=mode==='normal'&&p.age>=65?1:preset.protein;
 add('protein',result.weight*coefficient,mode==='normal'?'protein':mode,coefficient+' g/kg × '+num(result.weight)+' kg. '+result.weightSource+'. '+(mode==='normal'?'DGE-Basisreferenz.':'Gewählter App-Startwert, kein individueller Pflichtbedarf.'));
 if(mode==='sport')notes.push('Der Sport-Startwert ist für intensives Training gedacht. Bei höchstens rund 5 Stunden Sport pro Woche ist laut DGE nicht automatisch mehr Protein erforderlich. Ausdauerbedarf kann je nach Training deutlich schwanken.');
 if(['m','w'].includes(p.sex))result.rest=(0.047*p.weight-0.01452*p.age+3.21+(p.sex==='m'?1.009:0))*239;
 if(!result.rest||!activities.some(([v])=>v===p.activityPAL)){
  if(!values.energy)notes.push('Für die Energie-, Fett- und Kohlenhydratziele Geschlecht und Aktivitätsniveau ergänzen oder ein eigenes Energieziel eintragen.');
 }else{
  // Resting estimate also exists without PAL, so a manual energy target is still checked.
  result.maintenance=result.rest*p.activityPAL;
  if(!values.energy){
   result.energyAdjustment=mode==='muscle'?Math.min(200,result.maintenance*0.05):mode==='loss'?-Math.min(300,result.maintenance*0.10):0;
   const energy=result.maintenance+result.energyAdjustment;
   if(positive(energy)&&energy>=result.rest)add('energy',energy,'energy','DGE-Ruheenergieformel × Aktivitätsfaktor '+p.activityPAL+'. Plananpassung '+num(result.energyAdjustment)+' kcal. Überschuss/Defizit sind App-Annahmen, keine exakte Bedarfsmessung.');
  }
 }
 if(manual('energy')!==null)notes.push('Dein eigenes Energieziel hat Vorrang. Es wird kein weiterer Überschuss oder Abzug darauf angewandt.');
 const energy=values.energy?.value;
 if(positive(energy)){
  // Below resting expenditure, do not automatically derive a restrictive macro prescription.
  if(result.rest&&energy<result.rest){notes.push('Dein eigenes Energieziel liegt unter dem geschätzten Ruheenergieverbrauch. Deshalb keine automatische Fett-/Kohlenhydrat-Aufteilung; bitte die Ziele fachlich überprüfen.');}
  else{
   add('fat',energy*preset.fat/9,mode==='sport'?'sportFat':'fat',num(preset.fat*100)+' % des Energieziels ÷ 9 kcal/g. Gewählter Fett-Richtwert, keine Obergrenze.');
   const protein=values.protein?.value,fat=values.fat?.value;
   if(positive(protein)&&positive(fat)){
    const remaining=energy-4*protein-9*fat;
    if(remaining>0)add('carbs',remaining/4,'carbs','Verbleibende Planenergie nach Protein (4 kcal/g) und Fett (9 kcal/g), geteilt durch 4 kcal/g. Keine physiologische Mindestmenge.');
    else notes.push('Protein- und Fettziele beanspruchen bereits die gesamte Planenergie. Kein automatisches Kohlenhydratziel möglich; eigene Vorgaben prüfen.');
   }
  }
 }
 if(['energy','protein','fat','carbs'].every(k=>positive(values[k]?.value))){
  result.complete=true;result.macroEnergy=4*values.protein.value+9*values.fat.value+4*values.carbs.value;
  if(Math.abs(result.macroEnergy-energy)>Math.max(50,energy*0.03))notes.push('Die eigenen Makroziele ergeben '+num(result.macroEnergy)+' kcal und passen nicht zum Energieziel von '+num(energy)+' kcal. Eigene Werte wurden trotzdem nicht verändert.');
  if(mode==='normal'&&4*values.carbs.value/energy<=0.5)notes.push('Diese Verteilung liegt bei höchstens 50 % Kohlenhydratenergie und weicht vom allgemeinen DGE-Richtwert ab. Insbesondere eigene Zielwerte überprüfen.');
 }
 notes.push('Orientierungswerte statt exakter Tagespflicht. Bewegung ist bereits im Aktivitätsfaktor enthalten; keine Trainingskalorien doppelt addieren. Lebensmittelqualität und ausreichende Energieversorgung bleiben wichtig.');
 return result;
}
return {presets,activities,sources,validate,calculate};
});
