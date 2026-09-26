from pathlib import Path
p=Path('tools/kompass_v13_ui.py');s=p.read_text()
s=s.replace("wait_for(state='detached')","wait_for(state='hidden')")
s=s.replace("p.wait_for_function('id=>NK_HOUSEHOLD.id===id',arg=id)","p.wait_for_function('id=>NK_HOUSEHOLD.id===id && !document.querySelector(\"#household-dialog\").open && !document.querySelector(\"#app\").hidden',arg=id)")
s=s.replace("print('JS errors:',errors);", "print('JS errors:',errors);print('Visible UI:',p.locator('body').inner_text()[-6000:]);")
s=s.replace("p.evaluate('window.originalCacheWrite=NK_SAFE_CACHE.write;NK_SAFE_CACHE.write=async()=>{throw new DOMException(\"quota\", \"QuotaExceededError\")};')", "p.evaluate('() => {window.originalCacheWrite=NK_SAFE_CACHE.write;NK_SAFE_CACHE.write=async()=>{throw new DOMException(\"quota\", \"QuotaExceededError\")};}')")
s=s.replace("p.evaluate('NK_SAFE_CACHE.write=originalCacheWrite')", "p.evaluate('() => {NK_SAFE_CACHE.write=originalCacheWrite;}')")
s=s.replace("p.locator(f'.bottom-nav [data-route=\"{r}\"]').click()", "p.locator(f'.nav-btn[data-route=\"{r}\"]:visible').first.click()")
p.write_text(s)
print('Browser harness uses actual visible navigation and non-invoked failure-injection assignments.')

# Only unauthenticated requests to the deployed endpoint: no credentials or private data.
import urllib.request,urllib.error,json
url='https://wpmyuzpcraduhaybjvmb.supabase.co/functions/v1/nutrient-household-catalog'
checks=[]
for label,extra,expected in [('missing session',{},401),('invalid session',{'x-nk-session':'0'*64},401),('unapproved origin',{'Origin':'https://example.invalid'},403)]:
 req=urllib.request.Request(url,data=b'{"action":"catalog"}',headers={'Content-Type':'application/json',**extra},method='POST')
 try:
  with urllib.request.urlopen(req,timeout=25) as response:status=response.status;body=json.load(response)
 except urllib.error.HTTPError as error:status=error.code;body=json.load(error)
 assert status==expected,(label,status)
 assert 'profiles' not in body,label
 checks.append({'check':label,'status':status})
 print('PASS live private catalogue rejects',label,status)
Path('test-output').mkdir(exist_ok=True)
Path('test-output/backend-access-report.json').write_text(json.dumps({'passed':len(checks),'checks':checks},indent=2))
