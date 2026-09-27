"""Exercise actual app UI and encrypted persistence with synthetic API responses only."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from datetime import datetime, timezone
import copy, json, os, subprocess, traceback
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[2]
os.chdir(BASE)
OUT=BASE/'test-output';OUT.mkdir(exist_ok=True)
server=ThreadingHTTPServer(('127.0.0.1',0),SimpleHTTPRequestHandler)
Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}/kompass/'
engine=os.environ.get('TEST_BROWSER','chromium');checks=[];errors=[];unexpected=[]
ids=['11111111-1111-4111-8111-111111111111','22222222-2222-4222-8222-222222222222']
script="""global.window=global;require('./kompass/data.js');const C=require('./kompass/core.js');
const s=C.initial();s.profile={...s.profile,age:40,sex:'m',height:180,weight:80,manual:{protein:100,vitC:100,calcium:1000,energy:2000,fat:60,carbs:250,sugar:5}};
function entry(id,date,values){return {id,date,name:'Synthetic food '+id,kind:'food',meal:0,amountText:'100 g',n:Object.fromEntries(NK_DATA.nutrients.map(n=>[n.key,{value:values[n.key]??null,known:values[n.key]!=null?1:0,total:1,missing:values[n.key]!=null?[]:['Synthetic food '+id]}]))};}
s.entries=[entry('a','2026-09-21',{protein:100,vitC:120,calcium:500,energy:2000,fat:60,carbs:250,sugar:3}),entry('b','2026-09-22',{protein:100,vitC:80,calcium:500,energy:2000,fat:60,carbs:250,sugar:3}),entry('c','2026-09-23',{protein:30,vitC:200,calcium:300})];s.days={'2026-09-21':{complete:true},'2026-09-22':{complete:true},'2026-09-23':{complete:false}};
const t=C.clone(s);t.profile.sex='w';t.profile.reportFrequency='daily';t.profile.manual.vitC=95;t.entries=[entry('p','2026-09-21',{protein:30,vitC:95,calcium:1000})];t.days={'2026-09-21':{complete:true}};console.log(JSON.stringify([s,t]));"""
fixtures=json.loads(subprocess.check_output(['node','-e',script],text=True))
profiles={ids[i]:{'id':ids[i],'name':n,'revision':0,'state':fixtures[i]} for i,n in enumerate(['Dimitri','Patricia'])}
original_entries=copy.deepcopy(fixtures[0]['entries']);original_p=copy.deepcopy(fixtures[1])
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
 c.route('**/*',network)
 return c
def page(c):
 p=c.new_page();p.clock.set_fixed_time(datetime(2026,9,26,12,0,0,tzinfo=timezone.utc));p.on('pageerror',lambda e:errors.append(str(e)));return p
def login(p):
 p.goto(URL);p.locator('#gate-password').fill('synthetic-password');p.locator('#gate-form button[type=submit]').click();p.locator('#household-dialog[open]').wait_for()
def choose(p,id):
 p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('id=>window.NK_APP && NK_HOUSEHOLD.id===id && !document.querySelector("#household-dialog").open',arg=id)
def nav(p,r):
 p.locator(f'.nav-btn[data-route="{r}"]:visible').first.click()
 if r=='reports' and p.locator('[data-action="report-expand-all"]').inner_text()=='Alle Details aufklappen':p.locator('[data-action="report-expand-all"]').click()
def report(p,k):return p.locator(f'[data-report-key="{k}"]')

def open_text(p,text):
 p.locator('[data-action="custom-text-import"]').click();p.locator('#nutrition-text').fill(text);p.locator('#parse-text').click();p.locator('#scan-amount').wait_for()
def transfer(p):
 p.locator('#scan-confirm').check();p.locator('#scan-transfer').click()
def save_product(p):
 p.locator('#custom-food-form button[type=submit]').click();p.locator('#dialog').wait_for(state='hidden');p.evaluate('NK_HOUSEHOLD.flush()')
with sync_playwright() as play:
 args={'executable_path':'/usr/bin/chromium','args':['--no-sandbox']} if engine=='chromium' and Path('/usr/bin/chromium').exists() else {}
 browser=getattr(play,engine).launch(**args);c=context(browser);p=page(c)
 try:
  login(p);choose(p,ids[0]);nav(p,'search');p.locator('#food-search').fill('Ei')
  first=p.locator('#search-results [data-action="food-pick"]').evaluate_all('(els)=>els.slice(0,2).map(e=>e.dataset.id)')
  check('Eggs are the first ordinary search results',set(first)=={'blv-290','blv-1070'})
  p.locator('#food-search').fill('gekochtes Ei');check('Cooked egg variant is first',p.locator('#search-results [data-action="food-pick"]').first.get_attribute('data-id')=='blv-1070')
  p.locator('#finder-query').fill('Ei');p.locator('#finder-form button').click();check('Automatic local finder uses same egg ranking','Hühnerei' in p.locator('#finder-results [data-found]').first.inner_text())
  p.locator('#food-search').fill('');p.locator('[data-action="foods-more"]').click();check('More than first 75 foods accessible',p.locator('#search-results [data-action="food-pick"]').count()==150)
  check('Eight real manufacturer foods loaded',p.evaluate('NK_ADDITIONAL_FOODS.count===8 && NK_DATA.foods.length===1305'))
  p.locator('[data-action="filter"][data-filter="custom"]').click();p.locator('#food-search').fill('Ei');p.locator('#search-results [data-action="filter"][data-filter="all"]').click();check('Empty household filter offers all foods',p.locator('#search-results [data-action="food-pick"]').count()>=2)
  p.locator('[data-action="new-food"]').first.click();check('Own product offers both text and photo',p.locator('[data-action="custom-text-import"]').is_visible() and p.locator('[data-action="custom-photo-import"]').is_visible())
  p.locator('#custom-name').fill('Demo Chips');p.locator('#custom-fat').fill('1');p.locator('details:has(#custom-calcium)>summary').click();p.locator('#custom-calcium').fill('120')
  before=p.evaluate('JSON.stringify(NK_APP.getState())')
  text='Pro Portion (30 g)\nEnergie 150 kcal\nFett 9 g\nEiweiss 3 g\nNahrungsfasern 1,5 g'
  open_text(p,text);check('Text mode opens textarea directly and carries name',p.locator('#scan-text-block').evaluate('(e)=>e.open') and p.locator('#scan-name').input_value()=='Demo Chips')
  check('30 gram detected and protein normalized','10 g' in p.locator('#scan-out-protein').inner_text())
  p.locator('#scan-confirm').check();p.locator('#scan-amount').fill('60');check('Amount change clears confirmation',not p.locator('#scan-confirm').is_checked());p.locator('#scan-amount').fill('30')
  p.locator('#scan-transfer').click();check('Unconfirmed transfer blocked',p.locator('#scan-dialog').evaluate('(e)=>e.open'))
  transfer(p);p.locator('#scan-dialog').wait_for(state='hidden')
  check('Values fill existing editor without dropping calcium',p.locator('#custom-protein').input_value()=='10' and p.locator('#custom-fat').input_value()=='30' and p.locator('#custom-calcium').input_value()=='120')
  check('Text import not yet persisted',before==p.evaluate('JSON.stringify(NK_APP.getState())'))
  p.locator('[data-action="custom-import-undo"]').click();check('Undo restores original values',p.locator('#custom-fat').input_value()=='1' and p.locator('#custom-protein').input_value()=='')
  p.locator('[data-action="custom-photo-import"]').click();check('Photo entry available within own product',p.locator('#nutrition-photo').count()==1);p.locator('#scan-close').click();check('Closing photo import preserves editor',p.locator('#custom-name').input_value()=='Demo Chips' and p.locator('#custom-fat').input_value()=='1')
  open_text(p,text);transfer(p);save_product(p);check('Product stored using established sync',profiles[ids[0]]['state']['foods'][0]['name']=='Demo Chips' and profiles[ids[0]]['state']['foods'][0]['n']['protein']==10)
  fid=profiles[ids[0]]['state']['foods'][0]['id']
  p.locator(f'#search-results [data-action="food-pick"][data-id="{fid}"]').click();p.locator('#food-qty').fill('30');p.locator('#food-form button[type=submit]').click();p.locator('#dialog').wait_for(state='hidden');p.evaluate('NK_HOUSEHOLD.flush()')
  check('Consumed portion independent from label quantity',profiles[ids[0]]['state']['entries'][-1]['n']['protein']['value']==3)
  nav(p,'search');p.locator('#food-search').fill('Demo Chips');p.locator(f'#search-results [data-id="{fid}"][data-action="food-pick"]').click();p.locator('details:has([data-action="edit-custom-food"])>summary').click();p.locator('[data-action="edit-custom-food"]').click()
  open_text(p,'Pro 100 ml\nEiweiss 4 g');transfer(p);check('Mismatched dimensions cannot preserve old gram values','Einheit wechselt' in p.locator('#scan-status').inner_text() and p.locator('#scan-dialog').evaluate('(e)=>e.open'))
  p.locator('#scan-merge-mode').select_option('replace');transfer(p);check('Explicit replacement clears absent values',p.locator('#custom-calcium').input_value()=='' and p.locator('#custom-basis').input_value()=='ml')
  p.locator('[data-action="custom-import-undo"]').click();check('Undo also restores basis and omitted nutrients',p.locator('#custom-basis').input_value()=='g' and p.locator('#custom-calcium').input_value()=='120')
  open_text(p,'Pro 100 g\nEiweiss <0,5 g\nFett 30 g');transfer(p);check('Declared limit clears a previous exact quantity',p.locator('#custom-protein').input_value()=='' and p.locator('#custom-fat').input_value()=='30');p.locator('[data-action="custom-import-undo"]').click()
  open_text(p,'Zutaten: Kartoffeln, Salz, Wasser.');p.locator('#scan-amount').fill('100');check('Ingredients alone do not create fabricated nutrition',p.locator('#scan-transfer').is_disabled());p.locator('#scan-close').click()
  # No generated HTML from pasted text: preview and unknown source stay plain.
  open_text(p,'Pro 100 g\nProtein 10 g\n<img src=x onerror=window.evil=1>');check('Pasted markup never executes',p.evaluate('!window.evil'));p.locator('#scan-close').click();save_product(p)
  check('Editing existing product does not duplicate it',len(profiles[ids[0]]['state']['foods'])==1)
  p.locator('#device-profile-button').click();choose(p,ids[1]);p.evaluate('NK_SHARED.refresh(true)');nav(p,'search');p.locator('#food-search').fill('Demo Chips');check('Text-created food shared with Patricia',p.locator('#search-results [data-action="food-pick"]').count()==1 and 'Dimitri' in p.locator('#search-results').inner_text())
  check('Patricia diary not changed',profiles[ids[1]]['state']==original_p)
  # Create recipe from an imported product without losing ingredient return flow.
  nav(p,'recipes');p.locator('[data-action="new-recipe"]').first.click();p.locator('#recipe-name').fill('Demo text recipe');p.locator('#recipe-servings').fill('1');p.locator('[data-action="ingredient-search"]').click();p.locator('#ingredient-search').fill('Ei');check('Recipe ingredient search finds egg first',p.locator('#ingredient-results [data-action="food-pick"]').first.get_attribute('data-id') in ['blv-290','blv-1070'])
  p.locator('[data-action="ingredient-new-product"]').click();p.locator('#custom-name').fill('Demo Drink');open_text(p,'Pro 250 ml\nEiweiss 10 g');transfer(p);p.locator('#custom-food-form button[type=submit]').click();p.locator('#food-form').wait_for();check('Text import returns to ingredient quantity picker',p.locator('#food-form button[type=submit]').inner_text().endswith('Zutat übernehmen'))
  p.locator('#food-qty').fill('50');p.locator('#food-form button[type=submit]').click();p.locator('#dialog').wait_for(state='hidden');p.locator('[data-action="save-recipe"]').click();p.wait_for_function('NK_APP.getState().recipes.length===1');p.evaluate('NK_HOUSEHOLD.flush()');check('Text-import recipe saves',len(profiles[ids[1]]['state']['recipes'])==1)
  nav(p,'search');p.locator('[data-action="new-food"]').first.click();p.locator('#custom-name').fill('Mobile test');open_text(p,text)
  for w in [320,390,1440]:
   p.set_viewport_size({'width':w,'height':950});p.wait_for_timeout(150);check(f'Text preview fits {w}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth && document.querySelector("#scan-dialog").scrollWidth<=document.querySelector("#scan-dialog").clientWidth+1'))
  p.set_viewport_size({'width':390,'height':844});p.locator('#scan-review').scroll_into_view_if_needed();p.screenshot(path=str(OUT/f'{engine}-text-preview.png'))
  p.locator('#scan-close').click();p.locator('#dialog [data-action="close-dialog"]').click();nav(p,'reports');check('Reports retained',p.locator('[data-action="report-pdf"]').count()==1)
  p.reload();p.wait_for_function('window.NK_APP');check('Reload retains imported food and recipe',p.evaluate('NK_APP.getState().foods.length===1 && NK_APP.getState().recipes.length===1'))
  check('No runtime errors',not errors);check('No unexpected external requests',not unexpected)
 except Exception:
  (OUT/f'{engine}-food-entry-failure.txt').write_text(traceback.format_exc());p.screenshot(path=str(OUT/f'{engine}-food-entry-failure.png'),full_page=True);print(errors,unexpected);raise
 finally:
  (OUT/f'{engine}-food-entry-checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'runtimeErrors':errors,'unexpectedRequests':unexpected,'syntheticDataOnly':True},indent=2));browser.close();server.shutdown()
