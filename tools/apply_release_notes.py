"""Guarded minimal edits on Kompass 1.9.0. No personal data or server changes."""
from pathlib import Path
import hashlib,json
P=Path('kompass')
def replace(s,a,b):
    assert s.count(a)==1,(a[:100],s.count(a))
    return s.replace(a,b)
if (P/'version.json').read_text().find('1.9.1')>=0:
    assert 'acknowledgeReleases' in (P/'app.js').read_text()
    print('Release notes integration already applied.');raise SystemExit(0)
s=(P/'core.js').read_text()
s=replace(s," const VERSION='1.8.0', SCHEMA=1;"," const VERSION='1.8.0', SCHEMA=1;\n const RELEASES=typeof module==='object'&&module.exports?require('./release-notes-core.js'):globalThis.NK_RELEASE_CORE;")
s=replace(s,"  const p=s.profile;GOALS.validate(p);", "  const p=s.profile;if(p.releaseNotesSeen!==undefined){const v=RELEASES.normalize(p.releaseNotesSeen);if(v)p.releaseNotesSeen=v;else delete p.releaseNotesSeen;}GOALS.validate(p);")
(P/'core.js').write_text(s)
s=(P/'sync-core.js').read_text()
s=replace(s," 'use strict';", " 'use strict';\n const RELEASES=typeof module==='object'&&module.exports?require('./release-notes-core.js'):globalThis.NK_RELEASE_CORE;")
s=replace(s,"  delete lp.manual;delete rp.manual;if(bp)delete bp.manual;", "  const readVersion=RELEASES.highest(bp?.releaseNotesSeen,lp.releaseNotesSeen,rp.releaseNotesSeen);\n  delete lp.releaseNotesSeen;delete rp.releaseNotesSeen;if(bp)delete bp.releaseNotesSeen;\n  delete lp.manual;delete rp.manual;if(bp)delete bp.manual;")
s=replace(s,"  out.days=object(base?.days,local.days,remote.days,'days');", "  if(readVersion)out.profile.releaseNotesSeen=readVersion;\n  out.days=object(base?.days,local.days,remote.days,'days');")
(P/'sync-core.js').write_text(s)
s=(P/'app.js').read_text()
s=replace(s,"function notify(text,allowUndo=false)", """async function acknowledgeReleases(version,expectedId){
 const R=window.NK_RELEASE_CORE,H=window.NK_HOUSEHOLD;
 if(!R.normalize(version)||R.compare(version,window.NK_DEVICE.version)>0)throw Error('Ungültiger Release-Stand.');
 if(!H?.authenticated||H.id!==expectedId)throw Error('Das aktive Profil wurde gewechselt. Bitte erneut öffnen.');
 if(mutationBusy)throw Error('Bitte warten, bis der laufende Speichervorgang abgeschlossen ist.');
 mutationBusy=true;try{await change(s=>{if(H.id!==expectedId)throw Error('Profilwechsel: Lesestand nicht gespeichert.');s.profile.releaseNotesSeen=R.highest(s.profile.releaseNotesSeen,version);});document.dispatchEvent(new Event('nk-release-acknowledged'));}finally{mutationBusy=false;}
}
function notify(text,allowUndo=false)""")
s=replace(s,"window.NK_APP={version:C.VERSION,", "window.NK_APP={acknowledgeReleases,version:C.VERSION,")
(P/'app.js').write_text(s)
s=(P/'protein-celebration.js').read_text()
s=replace(s,"document.hidden||busy||A.hasDraft", "document.hidden||busy||root.NK_RELEASES?.hasPending()||A.hasDraft")
(P/'protein-celebration.js').write_text(s)
for name in ['index.html','sw.js','device.js','household.js','version.json']:
    s=(P/name).read_text().replace('1.9.0','1.9.1')
    if name=='index.html':
        s=replace(s,'<script src="core.js?v=1.9.1">','<script src="release-notes-core.js?v=1.9.1"></script><script src="core.js?v=1.9.1">')
        s=replace(s,'<script src="protein-celebration.js?v=1.9.1">','<script src="release-notes/catalog.js?v=1.9.1"></script><script src="release-notes.js?v=1.9.1"></script><script src="protein-celebration.js?v=1.9.1">')
        s=replace(s,'<title>Nährstoff-Kompass</title>','<link rel="stylesheet" href="release-notes.css?v=1.9.1"><title>Nährstoff-Kompass</title>')
        s=replace(s,'<span id="device-update-status"','<button type="button" id="release-notes-button" class="button secondary" data-release-action="archive" hidden>Neuerungen<span class="release-badge" data-release-count hidden></span></button><span id="device-update-status"')
        s=s.replace('Foto: Produkt finden & Nährwerte auslesen','Neuerungen & Release-Archiv')
    if name=='sw.js':
        s=replace(s,'const scripts=[',"const scripts=['release-notes-core.js','release-notes/catalog.js','release-notes.js',")
        s=replace(s,'const SHELL=[',"const SHELL=['./release-notes.css?v='+VERSION,'./release-notes/','./release-notes/index.html','./release-notes/v1.9.0.md','./release-notes/v1.9.1.md',")
        s=replace(s,'webmanifest|html|wasm|gz)', 'webmanifest|html|wasm|gz|md)')
        old="if(e.request.mode==='navigate'){try{const r=await fetch(e.request);if(r.ok){await c.put('./index.html',r.clone());return r;}}catch{}return await c.match('./index.html')||Response.error();}"
        new="if(e.request.mode==='navigate'){const isNotes=u.pathname===new URL('./release-notes/',self.registration.scope).pathname||u.pathname===new URL('./release-notes/index.html',self.registration.scope).pathname,key=isNotes?'./release-notes/index.html':'./index.html';try{const r=await fetch(e.request);if(r.ok){await c.put(key,r.clone());return r;}}catch{}return await c.match(key)||Response.error();}"
        s=replace(s,old,new)
    if name=='device.js':
        s=replace(s,'if(document.querySelector("#scan-dialog[open]")||', 'if(document.querySelector("#release-notes-dialog[open]")||document.querySelector("#scan-dialog[open]")||')
    (P/name).write_text(s)
print('Integrated profile release notes and monotone read-state sync.')
