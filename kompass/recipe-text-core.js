/* Conservative plain-text recipe extraction. No external service or invented nutrient data. */
(function(root,f){if(typeof module==='object'&&module.exports)module.exports=f(require('./cup-measures.js'));else root.NK_RECIPE_TEXT=f(root.NK_CUPS);})(typeof globalThis!=='undefined'?globalThis:this,function(U){
'use strict';
const clean=s=>String(s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/ß/g,'ss');
const unitMap={g:'g',gr:'g',gram:'g',grams:'g',gramm:'g',kg:'kg',kilogramm:'kg',ml:'ml',milliliter:'ml',dl:'dl',cl:'cl',l:'l',liter:'l',litre:'l',liters:'l',litres:'l',cup:'cup',cups:'cup',tasse:'cup',tassen:'cup',taza:'cup',tazas:'cup',el:'tbsp',essloffel:'tbsp',tbsp:'tbsp',tablespoon:'tbsp',tablespoons:'tbsp',tl:'tsp',teeloffel:'tsp',tsp:'tsp',teaspoon:'tsp',teaspoons:'tsp',stuck:'piece',stk:'piece',st:'piece',piece:'piece',pieces:'piece'};
const qty=/^(\d+\s+\d+\s*\/\s*\d+|\d+\s*\/\s*\d+|\d*\s*[½⅓⅔¼¾⅛⅜⅝⅞]|\d+(?:[.,]\d+)?)/;
function line(raw){
 let s=raw.replace(/^\s*(?:[-*•▢☐✓]|\d+[.)]\s+)\s*/,'').trim(),out={raw,name:s,quantity:'',unit:'',warning:''};
 const range=s.match(/^\d+(?:[.,]\d+)?\s*[-–—]\s*\d+(?:[.,]\d+)?\s*/);if(range){s=s.slice(range[0].length);out.warning='Mengenbereich: gewünschte Menge festlegen.';}
 const pack=s.match(/^(\d+)\s*[x×]\s*(\d+(?:[.,]\d+)?)\s*(g|ml)\b\s*(.*)$/i);
 if(pack){out.quantity=String(+pack[1]*U.amount(pack[2]));out.unit=pack[3].toLowerCase();out.name=pack[4].trim();out.warning='Packungsmenge prüfen, insbesondere Abtropfgewicht.';return out;}
 if(!range){const m=s.match(qty);if(m){try{out.quantity=String(U.amount(m[1]));}catch{out.warning='Menge prüfen.';}s=s.slice(m[0].length).trim();}}
 const u=s.match(/^([\p{L}]+)\.?\s*/u);if(u&&unitMap[clean(u[1])]){out.unit=unitMap[clean(u[1])];s=s.slice(u[0].length).trim();}
 else if(out.quantity&&!/^(?:dose|dosen|pack|packung|packungen|becher|bund|prise|handvoll|can|cans|package|packet|pinch|dash)\b/i.test(s)){out.unit='piece';out.warning=out.warning||'Stückgewicht prüfen – nur essbarer Anteil.';}
 else if(out.quantity)out.warning='Unklare Einheit: Packungs-/Stückgrösse oder Grammmenge festlegen.';
 out.name=s.replace(/^(?:of|de)\s+/i,'').trim()||out.name;if(!out.quantity)out.warning=out.warning||'Keine genaue Menge erkannt.';
 return out;
}
function parse(text){
 if(typeof text!=='string'||!text.trim())throw Error('Bitte zuerst ein Rezept hineinkopieren.');if(text.length>30000)throw Error('Maximal 30’000 Zeichen pro Rezept.');
 const lines=text.replace(/\r\n?/g,'\n').replace(/^(Zutaten|Ingredients|Ingredientes)\s*:\s*(\S.+)$/gmi,'$1:\n$2').split('\n').map(s=>s.trim()).filter(Boolean);let name='',servings='',state='start',ingredients=[],notes=[],warnings=[],headed=false;
 for(let raw of lines){const s=raw.replace(/^#{1,6}\s*/,'').replace(/\*\*/g,'').trim();
  if(/^(?:zutaten|ingredients|ingredientes)(?:\s+(?:für|for)\b[^:]*|\s*\([^)]*\))?\s*:?$/i.test(s)){state='ingredients';headed=true;const m=s.match(/(?:für|for|\()\s*(\d+(?:[.,]\d+)?)/i);if(m)servings=m[1];continue;}
  if(/^(?:zubereitung|anleitung|zubereitungsschritte|zubereitungsanleitung|instructions|method|directions|preparation|preparaci[oó]n)\s*:/i.test(s)||/^(?:zubereitung|anleitung|instructions|method|directions|preparation|preparaci[oó]n)$/i.test(s)){state='notes';notes.push(raw);continue;}
  const count=s.match(/^(?:für\s+|for\s+|ergibt\s+|yield\s*:\s*|serves\s+)?(\d+(?:[.,]\d+)?)\s*(?:portionen?|personen?|servings?|porciones?)\b/i)||s.match(/^(?:portionen?|personen?|servings?|serves|porciones)\s*:?\s*(\d+(?:[.,]\d+)?)/i);
  if(count&&state!=='notes'){servings=count[1];continue;}
  if(state==='notes'){notes.push(raw);continue;}
  if(/^(?:nährwert|nahrwert|nutrition|kalorien|calories)\b/i.test(s)){state='notes';notes.push(raw);continue;}
  if(/^(?:zubereitungszeit|gesamtzeit|arbeitszeit|kochzeit|backzeit|prep time|cook time|total time|nährwert|nahrwert|nutrition|kalorien|calories)\b/i.test(s)){notes.push(raw);continue;}
  if(!headed&&state==='ingredients'&&/^(?:ofen|backofen|mischen|vermischen|erhitzen|backen|mix\b|heat\b|preheat\b|bake\b|stir\b|\d+[.)]\s+\p{L})/iu.test(s)){state='notes';notes.push(raw);continue;}
  if(state==='ingredients'&&headed||qty.test(s.replace(/^[-*•▢☐✓]\s*/,''))){ingredients.push(line(s));if(state!=='ingredients')state='ingredients';continue;}
  if(!name&&state==='start'){name=s.slice(0,240);continue;}
  if(state==='ingredients'&&!headed&&s.length<120){ingredients.push(line(s));continue;}notes.push(raw);
 }
 if(!ingredients.length)throw Error('Keine Zutatenzeilen erkannt. Verwende eine Überschrift «Zutaten» und eine Zutat je Zeile.');if(ingredients.length>200)throw Error('Maximal 200 Zutatenzeilen pro Rezept.');
 if(!headed)warnings.push('Ohne Zutatenüberschrift ist die Trennung unsicher. Originaltext und alle Zutaten prüfen.');
 if(!servings)warnings.push('Portionszahl nicht erkannt – bitte ergänzen.');
 return {name,servings,ingredients,notes:notes.join('\n'),original:text,warnings};
}
const aliases={flour:'Mehl',oats:'Haferflocken',milk:'Milch',water:'Wasser',egg:'Ei roh',eggs:'Eier roh',sugar:'Zucker',butter:'Butter',salt:'Salz',rice:'Reis',tofu:'Tofu',chickpeas:'Kichererbsen',lentils:'Linsen',onion:'Zwiebel',onions:'Zwiebeln',garlic:'Knoblauch',spinach:'Spinat',banana:'Banane',bananas:'Banane',tomatoes:'Tomaten',yogurt:'Joghurt',yoghurt:'Joghurt',oil:'Öl',olive:'Oliven',peanut:'Erdnuss',potatoes:'Kartoffeln'};
function query(name){return String(name).replace(/olive oil/gi,'Olivenöl').replace(/(?:all[- ]purpose|plain) flour/gi,'Weizenmehl').replace(/(?:rolled|quick) oats/gi,'Haferflocken').replace(/oat milk/gi,'Haferdrink').replace(/so[yj]a? milk/gi,'Sojadrink').replace(/almond milk/gi,'Mandeldrink').replace(/coconut milk/gi,'Kokosmilch').replace(/baking powder/gi,'Backpulver').replace(/\([^)]*\)/g,' ').replace(/,.*$/,'').replace(/\b(?:gehackt|geschnitten|gewürfelt|gewuerfelt|geschält|geschalt|chopped|diced|peeled|fresh|frisch|optional|nach Geschmack|to taste)\b/gi,' ').replace(/\b[a-z]+\b/gi,w=>aliases[w.toLowerCase()]||w).replace(/\s+/g,' ').trim();}
function candidates(foods,name,search){const q=query(name);if(!q)return [];const first=search(foods,q);return first.slice(0,30);}
return {parse,line,query,candidates};
});
