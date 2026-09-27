"""Actual browser forms with synthetic household sessions and intercepted external requests."""
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
initial=json.loads(subprocess.check_output(['node','-e',"const C=require('./kompass/core.js');console.log(JSON.stringify(C.initial()))"],text=True))
profiles={id:{'id':id,'name':name,'revision':0,'state':copy.deepcopy(initial)} for id,name in zip(ids,['Dimitri','Patricia'])}

def check(label,ok=True):
 assert ok,label
 checks.append(label);print('PASS',label,flush=True)
def api(route):
 data=route.request.post_data_json or {};action=data.get('action')
 if action=='login':r={'token':'a'*64,'expires':'2099-01-01T00:00:00Z'}
 elif action=='key':r={'key':'b'*64}
 elif action=='profiles':r={'profiles':[{k:p[k] for k in ['id','name','revision']} for p in profiles.values()]}
 elif action=='get':r={'profile':copy.deepcopy(profiles[data['id']])}
 elif action=='save':
  p=profiles[data['id']]
  if data['revision']!=p['revision']:return route.fulfill(status=409,json={'error':'Synthetic conflict','conflict':True})
  p['state']=data['state'];p['revision']+=1;r={'revision':p['revision']}
 elif action=='catalog':r={'profiles':[{'id':p['id'],'name':p['name'],'revision':p['revision'],'foods':p['state']['foods'],'recipes':p['state']['recipes']} for p in profiles.values()]}
 elif action=='logout':r={'ok':True}
 else:unexpected.append(action);return route.fulfill(status=400,json={'error':'Unexpected synthetic action'})
 route.fulfill(status=200,json=r)
def make_context(browser):
 c=browser.new_context(viewport={'width':390,'height':844},timezone_id='Europe/Zurich',service_workers='block',accept_downloads=True)
 def network(route):
  if route.request.url.startswith(URL):return route.continue_()
  if '/functions/v1/' in route.request.url:return api(route)
  unexpected.append(route.request.url);route.abort()
 c.route('**/*',network);return c
def page(c):
 p=c.new_page();p.clock.set_fixed_time(datetime(2026,9,27,12,0,0,tzinfo=timezone.utc));p.on('pageerror',lambda e:errors.append(str(e)));return p
def login(p):
 p.goto(URL);p.locator('#gate-password').fill('synthetic-password');p.locator('#gate-form button[type=submit]').click();p.locator('#household-dialog[open]').wait_for()
def choose(p,id):
 p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('id=>window.NK_APP && NK_HOUSEHOLD.id===id && !document.querySelector("#household-dialog").open',arg=id)
def nav(p,route):p.locator(f'.nav-btn[data-route="{route}"]:visible').first.click()
def open_product(p,name):
 nav(p,'search');p.locator('[data-action="new-food"]').first.click();p.locator('#custom-text-panel').wait_for();p.locator('#custom-name').fill(name)
def paste(p,text):
 if not p.locator('#custom-text-panel').evaluate('(e)=>e.open'):p.locator('#custom-text-panel>summary').click()
 p.locator('#custom-nutrition-text').fill(text);p.locator('#custom-read-text').click()
def apply(p):
 p.locator('#custom-text-confirm').check();p.locator('#custom-apply-text').click()
def save_product(p):
 p.locator('#custom-food-form button[type=submit]').click();p.wait_for_function('!document.querySelector("#dialog").open || !!document.querySelector("#food-form")');p.evaluate('NK_HOUSEHOLD.flush()')
def close(p):p.locator('#dialog [data-action="close-dialog"]').click()

with sync_playwright() as play:
 args={}
 if engine=='chromium' and Path('/usr/bin/chromium').exists():args={'executable_path':'/usr/bin/chromium','args':['--no-sandbox']}
 browser=getattr(play,engine).launch(**args);c=make_context(browser);p=page(c)
 try:
  login(p);choose(p,ids[0]);nav(p,'search');p.locator('#food-search').fill('Ei')
  check('Ei returns whole cooked and raw eggs first',p.locator('#search-results .food-open').evaluate_all('(els)=>els.slice(0,2).map(e=>e.dataset.id)')==['blv-1070','blv-290'])
  p.locator('[data-action="filter"][data-filter="custom"]').click();check('Active household filter is visible','Aktiver Filter: Unser Haushalt' in p.locator('#search-results').inner_text())
  p.locator('[data-action="quick-food"][data-query="Ei"]').click();check('Quick egg button resets restrictive filter',p.locator('[data-action="filter"][data-filter="all"]').get_attribute('class').find('active')>=0 and p.locator('#search-results .food-open').first.get_attribute('data-id')=='blv-1070')
  for term,target in [('Eiklar','blv-411'),('Eigelb','blv-410'),('Rührei','blv-1602')]:
   p.locator('#food-search').fill(term);check(term+' is discoverable',p.locator('#search-results .food-open').first.get_attribute('data-id')==target)
  p.locator('#food-search').fill('');p.locator('[data-action="more-foods"]').click();check('All basic matches accessible beyond first page',p.locator('#search-results .food-open').count()==150)
  p.locator('#food-search').fill('Hefeflocken');check('Verified new pantry food discoverable',p.locator('#search-results .food-open[data-id="label-koro-yeast-flakes"]').count()==1)
  p.locator('#food-search').fill('Sojagranulat');check('Verified dry soy food discoverable',p.locator('#search-results .food-open[data-id="label-koro-soya-fine"]').count()==1)

  open_product(p,'Text Test Snack');p.locator('#custom-density').fill('1.03');p.locator('#custom-protein').fill('7')
  p.locator('#custom-food-form details:has(#custom-vitC)>summary').click();p.locator('#custom-vitC').fill('80')
  before=p.evaluate('JSON.stringify(NK_APP.getState())')
  paste(p,'pro 30 g\nEnergie 150 kcal\nFett 9 g\nDavon gesättigte Fettsäuren 1,5 g\nKohlenhydrate 12 g\nDavon Zucker 0 g\nEiweiss 3 g\nSalz 0,2 g\nVitamin B12 0,3 µg')
  check('Text parser offers source quantity 30 g',p.locator('#custom-text-amount').input_value()=='30' and p.locator('#custom-text-unit').input_value()=='g')
  check('Text preview calculates protein per100g',p.locator('[data-text-output="protein"]').inner_text()=='10')
  check('Parsing does not replace fields or save state',p.locator('#custom-protein').input_value()=='7' and p.evaluate('JSON.stringify(NK_APP.getState())')==before)
  p.locator('#custom-apply-text').click();check('Explicit replacement approval required',p.locator('#custom-protein').input_value()=='7' and 'bestätigen' in p.locator('#custom-text-status').inner_text())
  p.locator('#custom-text-confirm').check();p.locator('#custom-text-amount').fill('60');check('Changing source amount clears approval and avoids double scaling',not p.locator('#custom-text-confirm').is_checked() and p.locator('[data-text-output="protein"]').inner_text()=='5')
  p.locator('#custom-text-amount').fill('30');p.locator('#text-raw-protein').fill('3,6');check('Individual source values accept comma',p.locator('[data-text-output="protein"]').inner_text()=='12')
  apply(p);check('Applies corrected values to same product',p.locator('#custom-protein').input_value()=='12' and p.locator('#custom-name').input_value()=='Text Test Snack' and p.locator('#custom-density').input_value()=='1.03')
  check('Unknown values not mixed with old basis, real zero preserved',p.locator('#custom-vitC').input_value()=='' and p.locator('#custom-sugar').input_value()=='0')
  check('Applying only edits the draft',p.evaluate('JSON.stringify(NK_APP.getState())')==before)
  p.locator('#custom-undo-text').click();check('Undo restores old nutrient fields',p.locator('#custom-protein').input_value()=='7' and p.locator('#custom-vitC').input_value()=='80')
  apply(p)
  for width in [320,390,1440]:
   p.set_viewport_size({'width':width,'height':950});p.wait_for_timeout(180);check(f'Text editor fits {width}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth && document.querySelector("#dialog").scrollWidth<=document.querySelector("#dialog").clientWidth+1'))
  p.set_viewport_size({'width':390,'height':844});p.locator('#custom-text-panel').scroll_into_view_if_needed();p.screenshot(path=str(OUT/f'{engine}-text-import.png'))
  save_product(p);snack=profiles[ids[0]]['state']['foods'][0];snack_id=snack['id']
  check('Final product save uses normalized nutrient values',snack['name']=='Text Test Snack' and snack['n']['protein']==12 and snack['n']['vitB12']==1 and snack['basis']=='g')
  check('Raw pasted text not stored, source quantity retained','Ausgangswerte pro 30 g' in snack['source'] and 'Davon gesättigte' not in json.dumps(snack))
  p.locator(f'#search-results .food-open[data-id="{snack_id}"]').click();p.locator('#food-qty').fill('30');p.locator('#food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().entries.length===1');p.evaluate('NK_HOUSEHOLD.flush()')
  check('Consumed quantity remains separate from table quantity',abs(profiles[ids[0]]['state']['entries'][0]['n']['protein']['value']-3.6)<1e-9)
  history=copy.deepcopy(profiles[ids[0]]['state']['entries'])
  p.reload();p.wait_for_function('window.NK_APP && NK_HOUSEHOLD.id');check('Saved product survives encrypted reload',p.evaluate('id=>NK_APP.getState().foods.find(f=>f.id===id).n.protein',snack_id)==12)
  nav(p,'search');p.locator('#food-search').fill('Text Test Snack');p.locator(f'#search-results .food-open[data-id="{snack_id}"]').click();p.locator('#dialog details:has([data-action="edit-custom-food"])>summary').click();p.locator('[data-action="edit-custom-food"]').click()
  paste(p,'pro 100 g\nProtein 5 g');apply(p);p.locator('#custom-undo-text').click();save_product(p)
  check('Undo preserves saved source metadata and history',profiles[ids[0]]['state']['foods'][0]['source']==snack['source'] and profiles[ids[0]]['state']['entries']==history)

  open_product(p,'Liquid test');paste(p,'pro 250 ml\nEnergie 150 kcal\nFett 5 g\nKohlenhydrate 10 g\nEiweiss 7,5 g\nSalz <0,1 g')
  check('Liquid header detected without density conversion',p.locator('#custom-text-amount').input_value()=='250' and p.locator('#custom-text-unit').input_value()=='ml')
  apply(p);check('Liquid normalized and limit remains unknown',p.locator('#custom-basis').input_value()=='ml' and p.locator('#custom-protein').input_value()=='3' and p.locator('#custom-salt').input_value()=='')
  paste(p,'pro 100 g / pro 30 g\nEnergie 500 kcal 150 kcal\nFett 30 g 9 g\nKohlenhydrate 40 g 12 g\nProtein 10 g 3 g')
  p.locator('#custom-text-column').select_option('last');check('Last column selects matching30g source',p.locator('#custom-text-amount').input_value()=='30' and p.locator('#text-raw-protein').input_value()=='3' and p.locator('[data-text-output="protein"]').inner_text()=='10')
  p.locator('#custom-text-amount').fill('0');check('Zero source quantity cannot be applied',p.locator('#custom-apply-text').is_disabled())
  paste(p,'pro 100 g Energie 188 kcal; Fett 6,6 g; gesättigte Fettsäuren 0,8 g; Kohlenhydrate 4 g; Zucker 1,9 g; Eiweiss 26 g; Salz 0,88 g; Vitamin B12 2,5 µg')
  p.locator('#custom-text-amount').fill('100');p.locator('#custom-text-unit').select_option('g');apply(p)
  check('Single line copied table works',p.locator('#custom-protein').input_value()=='26' and p.locator('#custom-vitB12').input_value()=='2.5')
  p.locator('#custom-nutrition-text').fill('Unfinished edit');check('Editing pasted text invalidates stale preview',p.locator('#custom-text-review').is_hidden())
  paste(p,'Natürlich lecker und frisch');check('Unparseable text cannot overwrite fields',p.locator('#custom-apply-text').is_disabled() and p.locator('#custom-protein').input_value()=='26')
  close(p)

  nav(p,'recipes');p.locator('[data-action="new-recipe"]').first.click();p.locator('#recipe-name').fill('Egg with text ingredient');p.locator('#recipe-servings').fill('2');p.locator('#recipe-weight').fill('200')
  p.locator('[data-action="ingredient-search"]').click();p.locator('#ingredient-search').fill('Ei');check('Recipe ingredient search also prioritizes eggs',p.locator('#ingredient-results .food-open').first.get_attribute('data-id')=='blv-1070')
  p.locator('#ingredient-results .food-open').first.click();p.locator('#food-qty').fill('100');p.locator('#food-form button[type=submit]').click()
  p.locator('[data-action="ingredient-search"]').click();p.locator('[data-action="ingredient-new-product"]').click();p.locator('#custom-text-panel').wait_for();p.locator('#custom-name').fill('Text ingredient sauce')
  paste(p,'pro 100 g\nEnergie 80 kcal\nFett 2 g\nKohlenhydrate 8 g\nEiweiss 7 g');apply(p);save_product(p)
  check('Saving inline recipe product returns to ingredient quantity',p.locator('#food-form').is_visible())
  p.locator('#food-qty').fill('50');p.locator('#food-form button[type=submit]').click();check('Recipe draft and previous ingredient preserved',p.locator('#recipe-name').input_value()=='Egg with text ingredient' and p.locator('.ingredient-row').count()==2)
  p.locator('[data-action="save-recipe"]').click();p.wait_for_function('NK_APP.getState().recipes.length===1');p.evaluate('NK_HOUSEHOLD.flush()')
  check('Recipe stores the normalized source snapshot',profiles[ids[0]]['state']['recipes'][0]['ingredients'][1]['food']['n']['protein']==7)

  c2=make_context(browser);p2=page(c2);login(p2);choose(p2,ids[1]);nav(p2,'search');p2.locator('#food-search').fill('Text Test Snack');p2.wait_for_function('document.querySelectorAll("#search-results .food-open").length>0')
  check('Other profile sees synchronized text product','Von Dimitri' in p2.locator('#search-results').inner_text())
  check('Shared food never copies diary or goals',profiles[ids[1]]['state']['entries']==[] and profiles[ids[1]]['state']['profile']==initial['profile'])
  nav(p2,'recipes');p2.wait_for_function('document.querySelectorAll(".recipe-card").length>0');check('Recipe available to other profile','Egg with text ingredient' in p2.locator('#main').inner_text())
  c2.close()
  nav(p,'search')
  for width in [320,390,1440]:
   p.set_viewport_size({'width':width,'height':950});p.wait_for_timeout(180);check(f'Search shortcuts fit {width}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  check('No browser JavaScript errors',not errors);check('No unexpected external requests',not unexpected)
 except Exception:
  (OUT/f'{engine}-entry-failure.txt').write_text(traceback.format_exc());p.screenshot(path=str(OUT/f'{engine}-entry-failure.png'),full_page=True)
  print('RUNTIME',errors,'UNEXPECTED',unexpected);raise
 finally:
  (OUT/f'{engine}-entry-checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'runtimeErrors':errors,'unexpectedRequests':unexpected,'syntheticDataOnly':True},indent=2));browser.close();server.shutdown()
