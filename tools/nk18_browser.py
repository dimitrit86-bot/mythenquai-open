"""Exercise actual UI and encrypted persistence using synthetic API responses only."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from datetime import datetime, timezone
import copy, json, os, subprocess, traceback
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1];os.chdir(BASE)
OUT=BASE/'test-output';OUT.mkdir(exist_ok=True)
server=ThreadingHTTPServer(('127.0.0.1',0),SimpleHTTPRequestHandler)
Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}/kompass/'
engine=os.environ.get('TEST_BROWSER','chromium');checks=[];errors=[];unexpected=[]
ids=['11111111-1111-4111-8111-111111111111','22222222-2222-4222-8222-222222222222']
script="""const C=require('./kompass/core.js');const s=C.initial();s.profile={...s.profile,age:40,sex:'m',height:180,weight:80,manual:{protein:100,vitC:100,calcium:1000,energy:2000,fat:60,carbs:250}};const t=C.clone(s);t.profile.sex='w';console.log(JSON.stringify([s,t]));"""
fixtures=json.loads(subprocess.check_output(['node','-e',script],text=True))
profiles={ids[i]:{'id':ids[i],'name':n,'revision':0,'state':fixtures[i]} for i,n in enumerate(['Dimitri','Patricia'])}
def check(label,ok=True):
 assert ok,label
 checks.append(label);print('PASS',label,flush=True)
def api(route):
 data=route.request.post_data_json or {};a=data.get('action')
 if a=='login':r={'token':'a'*64,'expires':'2099-01-01T00:00:00Z'}
 elif a=='key':r={'key':'b'*64}
 elif a=='profiles':r={'profiles':[{k:p[k] for k in ['id','name','revision']} for p in profiles.values()]}
 elif a=='get':r={'profile':copy.deepcopy(profiles[data['id']])}
 elif a=='save':
  p=profiles[data['id']]
  if p['revision']!=data['revision']:return route.fulfill(status=409,json={'error':'Synthetic conflict','conflict':True})
  p['revision']+=1;p['state']=data['state'];r={'revision':p['revision']}
 elif a=='catalog':r={'profiles':[{'id':p['id'],'name':p['name'],'revision':p['revision'],'foods':p['state']['foods'],'recipes':p['state']['recipes']} for p in profiles.values()]}
 elif a=='logout':r={'ok':True}
 else:
  unexpected.append(a);return route.fulfill(status=400,json={'error':'Unexpected synthetic request'})
 route.fulfill(status=200,json=r)
def context(b):
 c=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/Zurich',service_workers='block',accept_downloads=True)
 def network(route):
  if route.request.url.startswith(URL):return route.continue_()
  if '/functions/v1/' in route.request.url:return api(route)
  unexpected.append(route.request.url);route.abort()
 c.route('**/*',network);return c
def page(c):
 p=c.new_page();p.clock.set_fixed_time(datetime(2026,9,26,12,0,0,tzinfo=timezone.utc));p.on('pageerror',lambda e:errors.append(str(e)));return p
def login(p):
 p.goto(URL);p.locator('#gate-password').fill('synthetic-password');p.locator('#gate-form button[type=submit]').click();p.locator('#household-dialog[open]').wait_for()
def choose(p,id):
 p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('id=>window.NK_APP && NK_HOUSEHOLD.id===id && !document.querySelector("#household-dialog").open',arg=id)
def nav(p,r):
 p.locator(f'.nav-btn[data-route="{r}"]:visible').first.click()
 if r=='reports' and p.locator('[data-action="report-expand-all"]').inner_text()=='Alle Details aufklappen':p.locator('[data-action="report-expand-all"]').click()
with sync_playwright() as play:
 b=getattr(play,engine).launch();c=context(b);p=page(c);p.set_default_timeout(12000)
 try:
  login(p);choose(p,ids[0]);p.on('dialog',lambda dialog:dialog.accept())
  nav(p,'search');p.locator('#food-search').fill('Ei');check('Ei ranks actual eggs first',all('Hühnerei' in t for t in p.locator('#search-results .food-open').all_text_contents()[:2]))
  check('Egg first result not unrelated substring','Hühnerei' in p.locator('#search-results .food-open').first.inner_text())
  p.locator('[data-action="new-food"]').first.click();p.locator('#custom-name').fill('Test Proteinriegel');p.locator('#custom-piece-label').fill('Riegel');p.locator('#custom-piece-amount').fill('30')
  p.locator('[data-action="custom-read-text"]').click();check('Direct text mode opens',p.locator('#scan-text-details').evaluate('(e)=>e.open'))
  p.locator('#nutrition-text').fill('pro 30 g\nEnergie 150 kcal\nFett 9 g\nKohlenhydrate 15 g\nEiweiss 3 g\nZucker 0 g');p.locator('#parse-text').click();check('Product name carried forward',p.locator('#scan-name').input_value()=='Test Proteinriegel')
  p.locator('#scan-confirm').check();p.locator('#scan-transfer').click();check('Returns into same custom form',p.locator('#custom-name').input_value()=='Test Proteinriegel' and p.locator('#custom-piece-amount').input_value()=='30')
  check('Text 30 g scaled exactly once',p.locator('#custom-protein').input_value()=='10' and p.locator('#custom-energy').input_value()=='500')
  check('Import not auto-saved',p.evaluate('NK_APP.getState().foods.length')==0)
  p.locator('#custom-food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().foods.length===1');f=p.evaluate('NK_APP.getState().foods[0]');id=f['id'];check('Portion persisted with product',f['portion']=={'label':'Riegel','amount':30,'unit':'g'})
  check('Piece label displayed in product row','1 Stück · Riegel = 30 g' in p.locator('#search-results').inner_text())
  p.locator(f'#search-results [data-action="food-pick"][data-id="{id}"]').click();check('Product opens as one piece',p.locator('#food-unit').input_value()=='piece' and p.locator('#food-qty').input_value()=='1')
  p.locator('#food-qty').fill('2');p.locator('#food-unit').select_option('g');check('Changing units keeps total amount',p.locator('#food-qty').input_value()=='60');p.locator('#food-unit').select_option('piece');check('Back to piece count',p.locator('#food-qty').input_value()=='2')
  p.locator('#food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().entries.length===1');ent=p.evaluate('NK_APP.getState().entries[0]');check('Two pieces count and grams in diary',ent['amountText']=='2 Stück · Riegel (60 g)' and ent['n']['protein']['value']==6)
  nav(p,'recipes');p.locator('[data-action="new-recipe"]').first.click();p.locator('#recipe-name').fill('Stückgericht');p.locator('#recipe-servings').fill('1');p.locator('[data-action="ingredient-search"]').click();p.locator('#ingredient-search').fill('Test Proteinriegel');p.locator(f'#ingredient-results [data-id="{id}"][data-action="food-pick"]').click();p.locator('#food-qty').fill('0,5');p.locator('#food-form button[type=submit]').click()
  check('Recipe ingredient shows piece count',p.locator('[data-ingredient="0"][data-field="unit"]').input_value()=='piece')
  p.locator('[data-ingredient="0"][data-field="quantity"]').fill('1,5');p.locator('[data-action="save-recipe"]').click();p.wait_for_function('NK_APP.getState().recipes.length===1');r=p.evaluate('NK_APP.getState().recipes[0]');check('Recipe stores grams for backwards compatibility',r['ingredients'][0]['quantity']==45 and r['ingredients'][0]['unit']=='g' and r['ingredients'][0]['piece']['count']==1.5)
  p.locator('[data-action="edit-recipe"]').first.click();check('Saved count round-trips',p.locator('[data-ingredient="0"][data-field="quantity"]').input_value()=='1.5')
  p.locator('[data-ingredient="0"][data-field="quantity"]').fill('');p.locator('[data-action="save-recipe"]').click();check('Blank piece quantity never saves stale amount',p.locator('#recipe-error .error').count()>0 and p.evaluate('NK_APP.getState().recipes[0].ingredients[0].quantity')==45)
  p.locator('[data-ingredient="0"][data-field="quantity"]').fill('2');p.locator('[data-ingredient="0"][data-field="unit"]').select_option('kg');check('Piece to kg amount conversion',p.locator('[data-ingredient="0"][data-field="quantity"]').input_value()=='0.06')
  p.locator('[data-action="save-recipe"]').click();nav(p,'search');p.locator('[data-action="filter"][data-filter="all"]').click();p.locator('#food-search').fill('Ei');p.locator('#search-results [data-action="food-pick"][data-id="blv-290"]').click();p.locator('[data-action="define-piece"]').click();p.locator('#custom-piece-label').fill('Ei');p.locator('#custom-piece-amount').fill('50');p.locator('#custom-food-form button[type=submit]').click();p.locator('#food-form').wait_for();check('Base egg definition returns to recording',p.locator('#food-unit').input_value()=='piece');p.locator('#food-qty').fill('2');p.locator('#food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().entries.length===2');check('Eggs calculate from official per-100 values',p.evaluate('NK_APP.getState().entries.at(-1).n.protein.value')==12.6)
  p.evaluate('NK_HOUSEHOLD.flush()');check('Piece products and recipes reached synthetic server',profiles[ids[0]]['state']['foods'][0]['portion']['amount']==50)
  old=copy.deepcopy(profiles[ids[0]]['state']['entries']);original=copy.deepcopy(profiles[ids[0]]['state']['foods'])
  p.locator('[data-nk="manager"]:visible').first.click();choose(p,ids[1]);nav(p,'search');p.locator('[data-action="filter"][data-filter="custom"]').click();p.locator('#food-search').fill('Ei');p.wait_for_function('NK_SHARED.foods().some(f=>f.portion?.label==="Ei")')
  check('Actual shared loader retains portion definition','1 Stück · Ei = 50 g' in p.locator('#search-results').inner_text())
  shared=p.evaluate('NK_SHARED.foods().find(f=>f.portion?.label==="Ei").id');p.locator(f'[data-action="food-pick"][data-id="{shared}"]').click();p.locator('#food-qty').fill('1');p.locator('#food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().entries.length===1');p.evaluate('NK_HOUSEHOLD.flush()');check('Profiles keep separate consumed amounts',profiles[ids[0]]['state']['entries']==old and profiles[ids[1]]['state']['entries'][0]['n']['protein']['value']==6.3)
  nav(p,'search');p.locator('#food-search').fill('Ei');p.locator(f'[data-action="food-pick"][data-id="{shared}"]').click();p.locator('[data-action="define-piece"]').click();p.locator('#custom-piece-amount').fill('60');p.locator('#custom-food-form button[type=submit]').click();p.locator('#food-form').wait_for();p.locator('#dialog [data-action="close-dialog"]').click();p.evaluate('NK_HOUSEHOLD.flush()');check('Editing shared portion creates variant not overwrite',profiles[ids[0]]['state']['foods']==original and profiles[ids[1]]['state']['foods'][0]['portion']['amount']==60)
  p.reload();p.wait_for_function('window.NK_APP && NK_HOUSEHOLD.id');check('Encrypted persistence restores portion',p.evaluate('NK_APP.getState().foods[0].portion.amount')==60)
  nav(p,'search');p.locator('#food-search').fill('Ei');p.locator('[data-action="new-food"]').first.click();p.locator('#custom-name').fill('Test Drink');p.locator('#custom-basis').select_option('ml');p.locator('#custom-piece-label').fill('Becher');p.locator('#custom-piece-amount').fill('250');p.locator('#custom-protein').fill('4');p.locator('#custom-food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().foods[0].name==="Test Drink"');drink=p.evaluate('NK_APP.getState().foods[0].id');p.locator(f'#search-results [data-action="food-pick"][data-id="{drink}"]').click();p.locator('#food-qty').fill('0,5');p.locator('#food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().entries.length===2');check('Half volume cup counts protein without density',p.evaluate('NK_APP.getState().entries.at(-1).n.protein.value')==5)
  nav(p,'search');p.locator('[data-action="new-food"]').first.click();p.locator('#custom-name').fill('Unsaved');p.locator('#custom-protein').fill('11');p.locator('#custom-piece-amount').fill('30');p.locator('#custom-piece-label').fill('Riegel');p.locator('[data-action="custom-read-text"]').click();p.locator('#nutrition-text').fill('pro 100 g\nEiweiss 5 g');p.locator('#scan-close').click();check('Cancelled text import preserves form',p.locator('#custom-protein').input_value()=='11' and p.locator('#custom-piece-amount').input_value()=='30')
  p.locator('#custom-piece-amount').fill('0');p.locator('#custom-food-form button[type=submit]').click();check('Zero piece definition refused',p.locator('#modal-error .error').count()>0)
  for width in [320,390,1440]:
   p.set_viewport_size({'width':width,'height':950});p.wait_for_timeout(150);check(f'Product editor fits at {width}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  p.set_viewport_size({'width':390,'height':844});p.screenshot(path=str(OUT/f'{engine}-product-editor.png'))
  p.locator('#dialog [data-action="close-dialog"]').click();nav(p,'reports');check('Reports still available after piece entries',p.locator('[data-action="report-pdf"]').count()>0)
  check('No JavaScript errors or external requests',not errors and not unexpected)
 except Exception:
  (OUT/f'{engine}-pieces-failure.txt').write_text(traceback.format_exc());p.screenshot(path=str(OUT/f'{engine}-pieces-failure.png'),full_page=True);print('Errors',errors,'Unexpected requests',unexpected,flush=True);raise
 finally:
  (OUT/f'{engine}-pieces-report.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'errors':errors,'unexpected':unexpected},indent=2));b.close();server.shutdown()
