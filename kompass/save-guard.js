/* Storage repair: semantic equality, not revision guessing or silent data merging. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.NK_SAVE_GUARD=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 function canonical(value){
  if(value===null||typeof value!=='object')return JSON.stringify(value);
  if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
  return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';
 }
 function sameState(a,b){
  if(!a||!b||a.schema!==1||b.schema!==1)return false;
  try{return canonical(a)===canonical(b);}catch{return false;}
 }
 function message(e){
  const name=e?.name||'';
  if(name==='QuotaExceededError'||name==='NS_ERROR_DOM_QUOTA_REACHED')return 'Der lokale Browserspeicher hat seine Grenze erreicht. Bitte vorhandene Daten im Profil sichern. Nicht ohne Sicherung Browserdaten löschen.';
  if(name==='SecurityError')return 'Der Browser erlaubt hier keinen lokalen Speicherzugriff. Bitte die App im normalen Browser öffnen und die Datenschutzeinstellungen prüfen. Vorhandene Daten nicht löschen.';
  return 'Speichern nicht möglich: '+(typeof e?.message==='string'&&e.message?e.message.slice(0,500):'Unbekannter Speicherfehler. Bitte die Daten sichern und den Synchronisierungsstatus prüfen.');
 }
 return {version:'1.2.2',sameState,message};
});
