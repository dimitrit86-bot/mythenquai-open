"""Reviewed release UI safeguards and faithful synthetic browser fixtures."""
from pathlib import Path

def rep(s,a,b):
    assert s.count(a)==1 or b in s,a[:100]
    return s.replace(a,b) if a in s else s
p=Path('kompass/release-notes.js');s=p.read_text()
a="""data-release-action="'+(view==='archive'?'new':'archive')+'" '+(view==='archive'&&!unread.length?'hidden':'')+'>"""
b="""data-release-action="${view==='archive'?'new':'archive'}" ${view==='archive'&&!unread.length?'hidden':''}>"""
s=rep(s,a,b)
s=rep(s,"previousFocus=null;","previousFocus=null,failedAck=null;")
s=rep(s," function pending(){return active()?R.unread(D,root.NK_APP.getState().profile.releaseNotesSeen,current()):[];}"," function seenVersion(){return failedAck?.id===active()?failedAck.prior:R.normalize(root.NK_APP.getState().profile.releaseNotesSeen);}\n function pending(){return active()?R.unread(D,seenVersion(),current()):[];}")
s=rep(s,"const seen=R.normalize(root.NK_APP.getState().profile.releaseNotesSeen),name=","const seen=seenVersion(),name=")
s=rep(s,"const id=owner,version=current();busy=true;","const id=owner,version=current(),prior=seenVersion();busy=true;")
s=rep(s,"await root.NK_APP.acknowledgeReleases(version,id);if(active()===id)","await root.NK_APP.acknowledgeReleases(version,id);failedAck=null;if(active()===id)")
s=rep(s,"catch(e){if(active()===id&&dialog.open)","catch(e){failedAck={id,prior,through:version};if(active()===id&&dialog.open)")
s=rep(s,"!==(R.normalize(root.NK_APP.getState().profile.releaseNotesSeen)||'')","!==(seenVersion()||'')")
s=rep(s,"['nk-profile-loaded','nk-synced','nk-release-acknowledged','visibilitychange']","['nk-profile-loaded','nk-release-acknowledged','visibilitychange']")
s=rep(s," document.addEventListener('close',schedule,true);", " document.addEventListener('nk-synced',()=>{if(failedAck?.id===active()&&R.compare(root.NK_APP.getState().profile.releaseNotesSeen||R.BASELINE,failedAck.through)>=0)failedAck=null;schedule();});\n document.addEventListener('close',schedule,true);")
p.write_text(s)
# The application registers automatically on HTTPS. For the actual worker test on
# secure localhost, explicitly perform the same registration without a real login.
p=Path('tools/test_release_notes.py');s=p.read_text()
s=rep(s,"sp.goto(URL);sp.wait_for_function('navigator.serviceWorker.controller!==null'","sp.goto(URL);sp.evaluate(\"navigator.serviceWorker.register('./sw.js',{scope:'./'})\");sp.wait_for_function('navigator.serviceWorker.controller!==null'")
s=rep(s,"NK_STORE.setItem=async()=>{throw Error('Synthetic storage failure');};", "NK_STORE.setItem=async(k,raw)=>{const e=Error('Synthetic storage failure');e.bufferedRaw=raw;throw e;};")
s=rep(s,"check('Storage failure leaves notice and unread marker intact',p.locator('#release-notes-dialog[open]').count()==1 and 'releaseNotesSeen' not in p.evaluate('NK_APP.getState().profile'))", "p.wait_for_timeout(200);check('Storage failure with buffered state keeps notices unread',p.locator('#release-notes-dialog[open]').count()==1 and p.locator('#release-notes-button [data-release-count]').inner_text()=='2' and 'releaseNotesSeen' not in profiles['test-p']['state']['profile'])")
p.write_text(s)
# Keep algorithm fixtures fixed as later real releases are added to the catalogue.
p=Path('kompass/tests/release-notes.test.js');s=p.read_text()
s=rep(s,"D=require('../release-notes/catalog.js'),C=", "LIVE=require('../release-notes/catalog.js'),C=")
s=rep(s,"const copy=C.clone,b=C.initial();", "const D={schema:1,releases:LIVE.releases.filter(r=>['1.9.0','1.9.1'].includes(r.version))};\nconst copy=C.clone,b=C.initial();")
s=rep(s,"assert.ok(D.releases.some(r=>r.version===JSON.parse", "assert.ok(LIVE.releases.some(r=>r.version===JSON.parse")
s=rep(s,"'Markdown available for each release',()=>D.releases.forEach", "'Markdown available for each release',()=>LIVE.releases.forEach")
p.write_text(s)
print('Explicit error feedback, numerical future-proof fixtures and actual offline worker test prepared.')
