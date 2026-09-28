"""Minimal integration on 1.11.0. No production credentials or profile reads."""
from pathlib import Path
import json
P=Path('kompass')
def rep(s,a,b):
    assert s.count(a)==1,(a[:90],s.count(a))
    return s.replace(a,b)
if json.loads((P/'version.json').read_text())['version']=='1.12.0':
    print('Integration already applied');raise SystemExit(0)
assert json.loads((P/'version.json').read_text())['version']=='1.11.0'
s=(P/'core.js').read_text()
s=rep(s,"const p=s.profile;if(p.releaseNotesSeen", "const p=s.profile;if(p.dayReviewThrough!==undefined&&!validDate(p.dayReviewThrough))delete p.dayReviewThrough;if(p.releaseNotesSeen")
(P/'core.js').write_text(s)
s=(P/'sync-core.js').read_text()
s=rep(s,"  delete lp.releaseNotesSeen;", "  const dayReviewThrough=[bp?.dayReviewThrough,lp.dayReviewThrough,rp.dayReviewThrough].filter(v=>typeof v==='string'&&/^\\d{4}-\\d{2}-\\d{2}$/.test(v)).sort().at(-1);\n  delete lp.dayReviewThrough;delete rp.dayReviewThrough;if(bp)delete bp.dayReviewThrough;\n  delete lp.releaseNotesSeen;")
s=rep(s,"  out.days=object(base?.days,local.days,remote.days,'days');", "  if(dayReviewThrough)out.profile.dayReviewThrough=dayReviewThrough;\n  out.days=object(base?.days,local.days,remote.days,'days');")
(P/'sync-core.js').write_text(s)
s=(P/'app.js').read_text()
addition="""async function respondDayReview(day,complete,expectedId,entrySignature){
 const H=window.NK_HOUSEHOLD,R=window.NK_DAY_REVIEW_CORE;
 if(!H?.authenticated||H.id!==expectedId)throw Error('Das Profil wurde gewechselt. Bitte erneut öffnen.');
 if(typeof complete!=='boolean'||!C.validDate(day)||day!==R.previousDay(C.dateKey()))throw Error('Der Kalendertag hat gewechselt. Bitte die neue Tagesübersicht öffnen.');
 if(mutationBusy)throw Error('Bitte den laufenden Speichervorgang abwarten.');
 mutationBusy=true;
 try{await change(s=>{
  if(H.id!==expectedId)throw Error('Profilwechsel: Es wurde kein Häkchen gesetzt.');
  if(day!==R.previousDay(C.dateKey()))throw Error('Der Kalendertag hat gewechselt. Bitte erneut prüfen.');
  if(!C.dayEntries(s,day).length)throw Error('Für diesen Tag sind keine Einträge mehr vorhanden.');
  if(R.signature(s,day,window.NK_SYNC.stable)!==entrySignature)throw Error('Die Einträge wurden zwischenzeitlich geändert. Bitte nochmals prüfen.');
  if(complete)s.days[day]={...s.days[day],complete:true};
  s.profile.dayReviewThrough=R.highest(s.profile.dayReviewThrough,day);
 });
 render();document.dispatchEvent(new Event('nk-day-reviewed'));
 if(complete)notify('Vortag als vollständig protokolliert markiert.');
 }finally{mutationBusy=false;}
}
function openDay(day){if(!C.validDate(day))throw Error('Ungültiges Datum.');if(window.NK_APP.hasDraft||window.NK_DEVICE?.hasUnsavedForm())throw Error('Bitte offene Eingaben zuerst speichern.');date=day;nav('today');}
"""
s=rep(s,'function notify(text,allowUndo=false)',addition+'function notify(text,allowUndo=false)')
s=rep(s,'window.NK_APP={acceptRecipeImport,acknowledgeReleases,','window.NK_APP={respondDayReview,openDay,acceptRecipeImport,acknowledgeReleases,')
s=rep(s,"else if(el.id==='day-complete'){await change(s=>s.days[date]={complete:el.checked});}","else if(el.id==='day-complete'){const day=date,complete=el.checked;await change(s=>s.days[day]={...s.days[day],complete});}")
(P/'app.js').write_text(s)
s=(P/'protein-celebration.js').read_text()
s=rep(s,'root.NK_RELEASES?.hasPending()||A.hasDraft','root.NK_RELEASES?.hasPending()||root.NK_DAY_REVIEW?.hasPending()||A.hasDraft')
(P/'protein-celebration.js').write_text(s)
for name in ['index.html','sw.js','device.js','household.js','version.json']:
    s=(P/name).read_text().replace('1.11.0','1.12.0')
    if name=='index.html':
        s=rep(s,'<script src="protein-celebration.js?v=1.12.0">','<script src="day-review-core.js?v=1.12.0"></script><script src="day-review.js?v=1.12.0"></script><script src="protein-celebration.js?v=1.12.0">')
        s=rep(s,'<title>Nährstoff-Kompass</title>','<link rel="stylesheet" href="day-review.css?v=1.12.0"><title>Nährstoff-Kompass</title>')
        import re
        s=re.sub(r'(<span id="device-update-status"[^>]*>)[^<]*',r'\g<1>Version 1.12.0 · Neuerungen einmalig & Vortag-Check',s)
    if name=='sw.js':
        s=s.replace("'./release-notes/v1.12.0.md'","'./release-notes/v1.11.0.md','./release-notes/v1.12.0.md'")
        s=rep(s,'const scripts=[',"const scripts=['day-review-core.js','day-review.js',")
        s=rep(s,'const SHELL=[',"const SHELL=['./day-review.css?v='+VERSION,")
    if name=='device.js':
        s=rep(s,'document.querySelector("#release-notes-dialog[open]")||','document.querySelector("#day-review-dialog[open]")||document.querySelector("#release-notes-dialog[open]")||')
    if name=='version.json':s=json.dumps({'version':'1.12.0','date':'2026-09-28'})+'\n'
    (P/name).write_text(s)
s=(P/'release-notes/build.py').read_text()
s=s.replace('Diesen bestätigst du in der App mit «Gelesen – weiter».','Die App merkt automatisch, welche Neuerungen sie deinem Profil bereits gezeigt hat.')
s=s.replace('Erst eine ausdrückliche Bestätigung schreibt den Stand ins Personenprofil.','Nach dem tatsächlichen automatischen Anzeigen wird der Stand ins Personenprofil geschrieben; zusätzlich merkt dieses Gerät den Versionsstand, auch wenn das Fenster direkt geschlossen wird.')
s=s.replace('Die automatische Anzeige wartet bei offenen Formularen/Scannern; «Später» verschiebt bis zum nächsten App-Start.','Die automatische Anzeige wartet bei offenen Formularen/Scannern. Schliessen und Escape lösen keine erneute automatische Anzeige aus.')
(P/'release-notes/build.py').write_text(s)
p=P/'release-notes/releases.json';data=json.loads(p.read_text());data['releases'].append({
 'version':'1.12.0','date':'2026-09-28','title':'Einmal neu. Gestern im Blick.',
 'summary':'Weniger Wiederholungen und ein kurzer Check, damit vollständig erfasste Tage nicht offen bleiben.',
 'changes':[
  {'title':'Neuerungen automatisch nur einmal','text':'Die App merkt bereits beim Anzeigen, welche Updates dein Profil gesehen hat. Schliessen, Escape oder «Weiter zur App» führt beim nächsten Start nicht zur Wiederholung. Nach der Synchronisierung gilt der Stand auch auf deinen anderen Geräten. Im Release-Archiv kannst du weiterhin alles nachlesen.'},
  {'title':'Hast du gestern alles protokolliert?','text':'Wenn für den Vortag Einträge vorhanden sind, aber das Häkchen fehlt, fragt die App nach. «Ja, alles erfasst» setzt «Tag vollständig protokolliert» direkt für diesen Vortag. Du musst nicht mehr selbst zurückblättern.'},
  {'title':'Noch etwas nachtragen?','text':'«Nein, Vortag öffnen» öffnet den betreffenden Tag ohne Häkchen und merkt die Antwort für dieses Profil. «Später» oder Schliessen lässt alles unverändert und verschiebt die Nachfrage bis zum nächsten App-Start.'},
  {'title':'Deine Eingaben haben Vorrang','text':'Die Hinweise warten bei offenen Eingaben, Scannern und Dialogen. Bereits vollständige Tage und Vortage ohne Einträge werden nicht abgefragt. Ein Bestätigen ändert keine gegessenen Mengen oder Nährwerte.'}],
 'notes':[
  'Die Nachfrage bezieht sich auf den Vortag laut lokalem Kalender des Geräts. Ein fehlendes Vollständigkeits-Häkchen sagt nichts darüber aus, ob Nährstoffziele erreicht wurden.',
  'Bei «Ja» und «Nein» wird die Antwort im aktiven Personenprofil gespeichert. Offline gilt der lokal gesicherte Stand; auf einem noch nicht synchronisierten anderen Gerät kann der Hinweis erneut erscheinen.',
  'Cups, Dichteschätzwerte, Gemüse-Stückportionen, Rezept-Textimport, Fotoerkennung und PDF-Reports bleiben unverändert verfügbar.']})
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('Integrated once-only release notices and previous-day confirmation.')
