"""Actual UI with synthetic private API only. Never sends a real login or writes real profiles."""
import os,json,copy,threading,subprocess
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
server=ThreadingHTTPServer(('127.0.0.1',0),SimpleHTTPRequestHandler);threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/kompass/'
base=json.loads(subprocess.check_output(['node','-e',"console.log(JSON.stringify(require('./kompass/core.js').initial()))"]))
profiles={id:{'id':id,'name':name,'revision':0,'state':copy.deepcopy(base)} for id,name in [('test-d','Dimitri'),('test-p','Patricia')]}
for p in profiles.values():p['state']['profile']['manual']={'protein':60}
seed=json.loads(subprocess.check_output(['node','-e',"console.log(JSON.stringify(require('./kompass/import-core.js').seed('Redefine Flank Steak')))"]))
checks=[];errors=[];api_calls=[];ROOT.joinpath('test-output').mkdir(exist_ok=True)
def check(n,ok=True):
 assert ok,n
 checks.append(n);print('PASS',n,flush=True)
def intercept(route):
 req=route.request
 if req.url.startswith(url):return route.continue_()
 if '/functions/v1/' not in req.url:return route.abort()
 d=req.post_data_json;a=d.get('action');api_calls.append((a,d))
 if a=='login':r={'token':'a'*64,'expires':'2099-01-01T00:00:00Z'}
 elif a=='key':r={'key':'ab'*32}
 elif a=='profiles':r={'profiles':[{k:v for k,v in p.items() if k!='state'} for p in profiles.values()]}
 elif a=='get':r={'profile':copy.deepcopy(profiles[d['id']])}
 elif a=='save':
  p=profiles[d['id']]
  if p['revision']!=d['revision']:return route.fulfill(status=409,json={'error':'Conflict','conflict':True})
  p['state']=d['state'];p['revision']+=1;r={'revision':p['revision']}
 elif a=='catalog':r={'profiles':[{'id':p['id'],'name':p['name'],'revision':p['revision'],'foods':p['state']['foods'],'recipes':p['state']['recipes']} for p in profiles.values()]}
 elif a=='lookup':
  if 'unavailable' in d['input']:return route.fulfill(status=422,json={'error':'Testquelle nicht erreichbar.'})
  r={'products':[seed],'note':'Testantwort: geprüfter Datenstand.'}
 elif a=='logout':r={'ok':True}
 else:raise AssertionError('Unexpected action '+str(a))
 route.fulfill(status=200,json=r)
def nav(p,r):p.locator(f'.nav-btn[data-route="{r}"]:visible').first.click()
def flush(p):p.evaluate('NK_HOUSEHOLD.flush()')
def choose(p,id):
 p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('id=>window.NK_APP && NK_HOUSEHOLD.id===id && !document.querySelector("#app").hidden && !document.querySelector("#household-dialog").open',arg=id)
def finder(p,text):
 nav(p,'search');p.locator('[data-finder-for="food-search"]').click();p.locator('#finder-input').fill(text);p.locator('#finder-form button[type=submit]').click()
def save_import(p):
 p.locator('#finder-results [data-finder-pick]').first.click();p.locator('#custom-food-form input[type=checkbox][required]').check();p.locator('#custom-food-form button[type=submit]').click();p.locator('#dialog').wait_for(state='hidden');flush(p)
def log(p,id,amount):
 p.evaluate('id=>NK_APP.useFood(id)',id);p.locator('#food-qty').fill(str(amount));p.locator('#food-form button[type=submit]').click();p.locator('#dialog').wait_for(state='hidden');flush(p)
with sync_playwright() as pw:
 kind=os.getenv('TEST_BROWSER','chromium');opts={'headless':True}
 if kind=='chromium' and Path('/usr/bin/chromium').exists():opts.update(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 b=getattr(pw,kind).launch(**opts);ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block');ctx.route('**/*',intercept);p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('dialog',lambda d:d.accept())
 try:
  p.goto(url);p.locator('#gate-password').fill('synthetic-only');p.locator('#gate-form button[type=submit]').click();choose(p,'test-d');check('Real UI starts with synthetic authenticated profile')
  check('No celebration just for opening an empty diary',p.locator('#protein-celebration[open]').count()==0)
  p.evaluate('NK_SCANNER.open()');p.locator('#scan-dialog details').last.locator('summary').click();p.locator('#nutrition-text').fill('pro 30 g\nEnergie 150 kcal\nFett 9 g\nEiweiss 3 g\nZucker 0 g');p.locator('#parse-text').click();p.locator('#scan-name').fill('Pringles Testportion');check('Photo/text output recognises 30 g',p.locator('#scan-amount').input_value()=='30');check('30 g protein scales to 100 g',p.locator('#scan-out-protein').inner_text()=='10 g')
  p.locator('#scan-amount').fill('60');check('Correction recalculates from original not previous result',p.locator('#scan-out-protein').inner_text()=='5 g');p.locator('#scan-amount').fill('30');p.locator('#scan-raw-protein').fill('3,6');check('Editable comma decimal value recalculates',p.locator('#scan-out-protein').inner_text()=='12 g');p.locator('#scan-raw-protein').fill('3');p.locator('#scan-confirm').check();p.locator('#scan-transfer').click();check('Product editor contains normalised not portion data',p.locator('#custom-protein').input_value()=='10');p.locator('#custom-food-form button[type=submit]').click();p.locator('#dialog').wait_for(state='hidden');flush(p)
  fid=p.evaluate('NK_APP.getState().foods[0].id');log(p,fid,100);check('Consumed amount tracked separately',p.evaluate('NK_APP.getState().entries[0].n.protein.value')==10)
  finder(p,'Redefine Flank Steak');check('Name finds the verified exact example',p.locator('#finder-results').inner_text().count('Redefine')>0);check('Saved source explicitly shows dated snapshot', 'nicht live' in p.locator('#finder-results').inner_text());save_import(p);check('Imported product saved without logging a meal',p.evaluate('NK_APP.getState().entries.length')==1)
  finder(p,seed['sourceUrl']+'?gclid=ignore');p.wait_for_function('document.querySelector("#finder-status").textContent.includes("Treffer")');check('Product URL reuses saved product instead of silently duplicating',p.locator('#finder-results .finder-result').count()==1 and 'Verwenden' in p.locator('#finder-results').inner_text());p.locator('#finder-close').click()
  log(p,'coop-7451865',200);p.locator('#protein-celebration[open]').wait_for();check('Goal crossing shows Spanish success screen','¡La concha de la lora!' in p.locator('#protein-celebration').inner_text() and '¡Felicitaciones!' in p.locator('#protein-celebration').inner_text());check('Success refers to correct target and sum','62' in p.locator('.celebration-total').inner_text() and '60' in p.locator('.celebration-total').inner_text());p.screenshot(path=str(ROOT/'test-output/celebration.png'))
  p.set_viewport_size({'width':320,'height':720});check('Success screen fits small mobile viewport',p.locator('#protein-celebration').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'));p.locator('.celebration-close').click();log(p,fid,10);p.wait_for_timeout(250);check('Further intake does not show success again',p.locator('#protein-celebration[open]').count()==0)
  p.reload();p.wait_for_function('window.NK_APP && NK_HOUSEHOLD.id==="test-d"');p.wait_for_timeout(200);check('Daily once-per-profile state survives reload',p.locator('#protein-celebration[open]').count()==0)
  p.locator('#device-profile-button').click();choose(p,'test-p');p.evaluate('NK_SHARED.refresh(true)');finder(p,'Pringles Testportion');check('Other profile finds shared imported product','Unser Haushalt' in p.locator('#finder-results').inner_text());p.locator('#finder-results [data-finder-pick]').first.click();p.locator('#food-qty').fill('100');p.locator('#food-form button[type=submit]').click();p.locator('#dialog').wait_for(state='hidden');flush(p);check('Shared product does not share eaten quantities',len(profiles['test-p']['state']['entries'])==1 and len(profiles['test-d']['state']['entries'])==3)
  shared=p.evaluate('NK_SHARED.foods().find(x=>x.shared.sourceId==="coop-7451865").id');log(p,shared,200);p.locator('#protein-celebration[open]').wait_for();check('Patricia can independently reach her goal');p.locator('.celebration-close').click()
  finder(p,'https://localhost/secret');check('Unsupported URL is explained without fake result','unterstützt' in p.locator('#finder-status').inner_text());p.locator('#finder-close').click()
  finder(p,'unavailable xyz');p.wait_for_function('document.querySelector("#finder-status").textContent.includes("nicht erreichbar")');check('Failed online lookup leaves diary intact',p.evaluate('NK_APP.getState().entries.length')==2);p.locator('#finder-close').click()
  nav(p,'recipes');p.locator('[data-action="new-recipe"]').first.click();p.locator('#recipe-name').fill('Test dinner');p.locator('#recipe-servings').fill('2');p.locator('[data-action="ingredient-search"]').click();p.locator('[data-finder-for="ingredient-search"]').click();p.locator('#finder-input').fill('Redefine Flank Steak');p.locator('#finder-form button[type=submit]').click();p.locator('#finder-results [data-finder-pick]').first.click();p.locator('#food-qty').fill('200');p.locator('#food-form button[type=submit]').click();p.locator('#dialog').wait_for(state='hidden');p.locator('[data-action="save-recipe"]').click();p.wait_for_function('NK_APP.getState().recipes.length===1');flush(p);check('Finder works as recipe ingredient without logging extra food',p.evaluate('NK_APP.getState().entries.length')==2)
  nav(p,'search');p.locator('[data-finder-for="food-search"]').click();check('Open import protects against unsafe reload',p.evaluate('NK_DEVICE.hasUnsavedForm()'));p.locator('#finder-close').click();check('Small viewport page does not overflow',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  p.set_viewport_size({'width':1440,'height':950});check('Desktop layout does not overflow',p.evaluate('document.documentElement.scrollWidth<=innerWidth'));check('No JavaScript errors',not errors)
 except Exception:
  import traceback
  ROOT.joinpath('test-output/failure.txt').write_text(traceback.format_exc());p.screenshot(path=str(ROOT/'test-output/failure.png'),full_page=True);print('ERRORS',errors);print(p.locator('body').inner_text()[-4000:]);raise
 finally:
  ROOT.joinpath('test-output/browser-'+kind+'.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'errors':errors},indent=2));b.close();server.shutdown()
