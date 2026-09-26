import os,json,copy,threading,traceback,time
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'test-output';OUT.mkdir(exist_ok=True)
os.chdir(ROOT)
class Silent(SimpleHTTPRequestHandler):
 def log_message(self,*x):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Silent);threading.Thread(target=server.serve_forever,daemon=True).start();URL=f'http://127.0.0.1:{server.server_port}/kompass/'
P='11111111-1111-4111-8111-111111111111';D='22222222-2222-4222-8222-222222222222'
initial={'schema':1,'profile':{'sex':'','age':None,'weight':None,'height':None,'special':False,'smoker':False,'menopause':'','phytate':'','manual':{}},'entries':[],'recipes':[],'foods':[],'favorites':[],'recent':[],'days':{},'recipeDraft':None}
profiles={k:{'id':k,'name':n,'revision':0,'state':copy.deepcopy(initial)} for k,n in [(P,'Patricia'),(D,'Dimitri')]}
flags={'offline':False,'saveDelay':0};errors=[];passed=[];requests=[]
def check(n,v):
 assert v,n
 passed.append(n);print('PASS',n,flush=True)
def api(route):
 if flags['offline']:return route.abort()
 b=route.request.post_data_json or {};a=b.get('action');requests.append(a)
 if a=='login':r={'token':'1'*64,'expires':'2099-01-01T00:00:00Z'}
 elif a=='key':r={'key':'a'*64}
 elif a=='profiles':r={'profiles':[{k:p[k] for k in ['id','name','revision']} for p in profiles.values()]}
 elif a=='catalog':r={'profiles':[{'id':p['id'],'name':p['name'],'revision':p['revision'],'foods':p['state']['foods'],'recipes':p['state']['recipes']} for p in profiles.values()]}
 elif a=='get':r={'profile':copy.deepcopy(profiles[b['id']])}
 elif a=='save':
  p=profiles[b['id']]
  if b['revision']!=p['revision']:return route.fulfill(status=409,json={'conflict':True,'error':'Auf anderem Gerät geändert.'})
  p['revision']+=1;p['state']=copy.deepcopy(b['state']);r={'revision':p['revision']}
 elif a=='logout':r={'ok':True}
 else:raise Exception(a)
 route.fulfill(status=200,json=r)
def new_page(browser,**kw):
 ctx=browser.new_context(service_workers='block',viewport={'width':390,'height':844},**kw)
 def route(r):
  if '/functions/v1/' in r.request.url:return api(r)
  if r.request.url.startswith(URL):return r.continue_()
  return r.abort()
 ctx.route('**/*',route);p=ctx.new_page();p.set_default_timeout(15000);p.on('pageerror',lambda e:errors.append(str(e)));return p,ctx
def login(p,id):
 p.goto(URL);p.locator('#gate-password').fill('synthetic-test-only');p.locator('#remember-session').check();p.locator('#gate-form button[type=submit]').click();p.locator('#household-dialog[open]').wait_for();p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('window.NK_APP && !document.querySelector("#app").hidden')
def nav(p,r):p.locator(f'.nav-btn[data-route="{r}"]:visible').first.click()
def flush(p):p.evaluate('NK_HOUSEHOLD.flush()')
def choose(p,id):
 p.locator('#device-profile-button').click();p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('id=>NK_HOUSEHOLD.id===id && !document.querySelector("#household-dialog").open && !document.querySelector("#app").hidden',arg=id)
def custom(p,name):
 nav(p,'search');p.locator('[data-action="new-food"]').first.click();p.locator('#custom-name').fill(name)
 for n,v in [('energy','512'),('protein','6.2'),('carbs','54'),('fat','29')]:p.locator('#custom-'+n).fill(v)
 p.locator('#custom-food-form button[type=submit]').click();p.wait_for_function('name=>NK_APP.getState().foods.some(f=>f.name===name)',arg=name);flush(p)
 return p.evaluate('name=>NK_APP.getState().foods.find(f=>f.name===name).id',name)
def log_food(p,id,q='50',name=None):
 nav(p,'search');p.locator('#food-search').fill(name or 'Test Pringles');p.locator(f'#search-results [data-action="food-pick"][data-id="{id}"]').click();p.locator('#food-qty').fill(q);p.locator('#food-form button[type=submit]').click();p.locator('#food-form').wait_for(state='hidden')
def add_direct(p,id,name):
 return p.evaluate('''async ({id,name})=>{const base=NK_APP.getState(),s=NK.clone(base),f=NK_DATA.foods[0];s.entries.push({id,name,date:'2026-09-26',meal:3,kind:'food',amountText:'100 g',n:NK.snapshot(f,100,f.basis,null,NK_DATA.nutrients.map(n=>n.key))});const raw=await NK_STORE.setItem('test',JSON.stringify(s),JSON.stringify(base));NK_APP.acceptSyncState(JSON.parse(raw));}''',{'id':id,'name':name})
with sync_playwright() as pw:
 b=pw.chromium.launch(args=['--no-sandbox']);p,ctx=new_page(b)
 try:
  login(p,P);check('login and encrypted initial profile cache work',p.evaluate('NK_HOUSEHOLD.name')=='Patricia')
  fid=custom(p,'Test Pringles');check('new product saved to server',len(profiles[P]['state']['foods'])==1)
  log_food(p,fid);flush(p);check('50 g logged correctly',abs(profiles[P]['state']['entries'][0]['n']['energy']['value']-256)<1e-8)
  nav(p,'recipes');p.locator('[data-action="new-recipe"]').first.click();p.locator('#recipe-name').fill('Test Rezept Patricia');p.locator('#recipe-servings').fill('2');p.locator('#recipe-weight').fill('200');p.locator('[data-action="ingredient-search"]').click();p.locator('#ingredient-search').fill('Test Pringles');p.locator(f'#ingredient-results [data-id="{fid}"][data-action="food-pick"]').click();p.locator('#food-qty').fill('100');p.locator('#food-form button[type=submit]').click();p.locator('#food-form').wait_for(state='hidden');p.locator('[data-action="save-recipe"]').click();p.wait_for_function('NK_APP.getState().recipes.length===1');flush(p);check('new recipe stored with ingredients',len(profiles[P]['state']['recipes'][0]['ingredients'])==1)
  choose(p,D);p.evaluate('NK_SHARED.refresh(true)');check('Patricia product visible for Dimitri',p.evaluate('NK_SHARED.foods().some(f=>f.name==="Test Pringles")'))
  shared=p.evaluate('NK_SHARED.foods().find(f=>f.name==="Test Pringles").id');log_food(p,shared);flush(p);check('shared product consumption remains personal',len(profiles[D]['state']['entries'])==1 and len(profiles[P]['state']['entries'])==1)
  nav(p,'recipes');p.locator('[data-action="log-recipe"]').first.click();p.locator('#recipe-log-form button[type=submit]').click();p.locator('#recipe-log-form').wait_for(state='hidden');flush(p);check('shared recipe can be logged directly',len(profiles[D]['state']['entries'])==2)
  old_snapshot=copy.deepcopy(profiles[D]['state']['entries'][1]['n']);nav(p,'recipes');p.locator('[data-action="edit-recipe"]').first.click();check('editing another profile recipe makes a variant','Variante' in p.locator('#recipe-name').input_value());p.locator('[data-ingredient="0"][data-field="quantity"]').fill('200');p.locator('[data-action="save-recipe"]').click();p.wait_for_function('NK_APP.getState().recipes.length===1');flush(p);check('original shared recipe unaffected',profiles[P]['state']['recipes'][0]['ingredients'][0]['quantity']==100);check('historical nutrition immutable',profiles[D]['state']['entries'][1]['n']==old_snapshot)
  # Two pages for the same profile create independent records from an outdated baseline.
  p2,c2=new_page(b);login(p2,D)
  add_direct(p2,'remote-entry','From second device');flush(p2)
  add_direct(p,'local-entry','From first device');flush(p)
  check('stale revision merges independent additions',{'remote-entry','local-entry'}<=set(e['id'] for e in profiles[D]['state']['entries']))
  check('no conflict left after disjoint merge',not p.evaluate('NK_HOUSEHOLD.blocked'))
  # Real collision in a target remains explicit, but new food still saves locally.
  profiles[D]['state']['profile']['manual']['protein']=120;profiles[D]['revision']+=1
  nav(p,'profile');p.locator('#target-protein').fill('90');p.locator('#profile-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().profile.manual.protein===90')
  try:flush(p)
  except Exception:pass
  check('actual same-field conflict is not silently overwritten',p.evaluate('NK_HOUSEHOLD.blocked'))
  add_direct(p,'while-conflicted','Saved while conflict open')
  check('new diary entry accepted during unresolved conflict',p.evaluate('NK_APP.getState().entries.some(e=>e.id==="while-conflicted")'))
  p.evaluate("NK_HOUSEHOLD.flush('local')");check('explicit conflict decision retains independent additions',profiles[D]['state']['profile']['manual']['protein']==90 and any(e['id']=='remote-entry' for e in profiles[D]['state']['entries']))
  # Cached recovery persists through an offline reload.
  flags['offline']=True;add_direct(p,'offline-record','Offline example');p.reload();p.wait_for_function('window.NK_APP && !document.querySelector("#app").hidden');check('offline reload recovers pending encrypted entries',p.evaluate('NK_APP.getState().entries.some(e=>e.id==="offline-record")'))
  flags['offline']=False;p.evaluate("window.dispatchEvent(new Event('online'))");flush(p);check('offline changes synchronize without duplicates',sum(e['id']=='offline-record' for e in profiles[D]['state']['entries'])==1)
  # Storage API failure with connectivity: direct server acknowledgement.
  p.evaluate('() => {window.originalCacheWrite=NK_SAFE_CACHE.write;NK_SAFE_CACHE.write=async()=>{throw new DOMException("quota", "QuotaExceededError")};}')
  add_direct(p,'cache-unavailable','Server fallback');check('server fallback saves when local encrypted cache is unavailable',any(e['id']=='cache-unavailable' for e in profiles[D]['state']['entries']));p.evaluate('() => {NK_SAFE_CACHE.write=originalCacheWrite;}')
  # Existing malformed/full-storage generic message is gone on the successful recovery path.
  check('no misleading full-storage message','Browserspeicher ist voll' not in p.locator('body').inner_text())
  nav(p,'today');check('protein target card remains visible',p.locator('.protein-target').count()==1)
  p.set_viewport_size({'width':320,'height':780});check('320px layout fits viewport',p.evaluate('document.documentElement.scrollWidth<=innerWidth'));p.screenshot(path=str(OUT/'mobile.png'),full_page=True)
  p.set_viewport_size({'width':1440,'height':1000});check('desktop layout fits viewport',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  nav(p,'search');p.locator('[data-retail-panel="main"] summary').click();p.locator('#main-source').select_option('Alpro');check('retailer catalogue preserved',p.locator('.catalog-results .food-row').count()>0)
  check('no JavaScript runtime errors',not errors)
  c2.close()
 except Exception:
  print(traceback.format_exc());print('JS errors:',errors);print('Visible UI:',p.locator('body').inner_text()[-6000:]);p.screenshot(path=str(OUT/'failure.png'),full_page=True);raise
 finally:
  (OUT/'browser-report.json').write_text(json.dumps({'passed':len(passed),'checks':passed,'errors':errors},ensure_ascii=False,indent=2));b.close();server.shutdown()
