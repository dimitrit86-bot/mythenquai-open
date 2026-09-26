from pathlib import Path
p=Path('tools/kompass_v13_ui.py');s=p.read_text()
s=s.replace("wait_for(state='detached')","wait_for(state='hidden')")
s=s.replace("p.wait_for_function('id=>NK_HOUSEHOLD.id===id',arg=id)","p.wait_for_function('id=>NK_HOUSEHOLD.id===id && !document.querySelector(\"#household-dialog\").open && !document.querySelector(\"#app\").hidden',arg=id)")
s=s.replace("print('JS errors:',errors);", "print('JS errors:',errors);print('Visible UI:',p.locator('body').inner_text()[-6000:]);")
s=s.replace("p.evaluate('window.originalCacheWrite=NK_SAFE_CACHE.write;NK_SAFE_CACHE.write=async()=>{throw new DOMException(\"quota\", \"QuotaExceededError\")};')", "p.evaluate('() => {window.originalCacheWrite=NK_SAFE_CACHE.write;NK_SAFE_CACHE.write=async()=>{throw new DOMException(\"quota\", \"QuotaExceededError\")};}')")
s=s.replace("p.evaluate('NK_SAFE_CACHE.write=originalCacheWrite')", "p.evaluate('() => {NK_SAFE_CACHE.write=originalCacheWrite;}')")
p.write_text(s)
print('Browser tests: wait for modal closure; install and remove failure-injection stubs without invoking them.')
