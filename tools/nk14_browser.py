"""Real UI flows with synthetic private API; never uses real credentials or profile data."""
from playwright.sync_api import sync_playwright
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
import copy,json,os
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT);OUT=ROOT/'test-output';OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Quiet);Thread(target=server.serve_forever,daemon=True).start();URL=f'http://127.0.0.1:{server.server_port}/kompass/'
base={'schema':1,'profile':{'sex':'','age':None,'weight':None,'height':None,'special':False,'smoker':False,'menopause':'','phytate':'','manual':{}},'entries':[],'foods':[],'recipes':[],'favorites':[],'recent':[],'days':{},'recipeDraft':None}
D='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';P='bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb';profiles={i:{'id':i,'name':n,'revision':0,'state':copy.deepcopy(base)} for i,n in [(D,'Dimitri'),(P,'Patricia')]}
products=[{'code':'8721022801612','product_name':'Flank Steak','brands':'Redefine Meat','quantity':'200 g','nutriments':{'energy-kcal_100g':188,'proteins_100g':26,'carbohydrates_100g':4,'fat_100g':6.6}}]
requests=[];errors=[];passed=[]
def ok(name,cond=True):
 assert cond,name
 passed.append(name);print('PASS',name,flush=True)
def api(route):
 req=route.request
 if req.url.startswith(URL):return route.continue_()
 if '/functions/v1/' not in req.url:return route.abort()
 data=req.post_data_json or {};a=data.get('action');requests.append((a,data))
 if a=='login':result={'token':'a'*64,'expires':'2099-01-01T00:00:00Z'}
 elif a=='key':result={'key':'b'*64}
 elif a=='profiles':result={'profiles':[{'id':x['id'],'name':x['name'],'revision':x['revision']} for x in profiles.values()]}
 elif a=='get':result={'profile':copy.deepcopy(profiles[data['id']])}
 elif a=='save':
  x=profiles[data['id']]
  if data['revision']!=x['revision']:return route.fulfill(status=409,json={'error':'Synthetic conflict','conflict':True})
  x['state']=copy.deepcopy(data['state']);x['revision']+=1;result={'revision':x['revision']}
 elif a=='catalog':result={'profiles':[{'id':x['id'],'name':x['name'],'foods':x['state']['foods'],'recipes':x['state']['recipes']} for x in profiles.values()]}
 elif a=='search':result={'products':products}
 elif a=='barcode':result={'product':products[0]}
 elif a=='link':return route.fulfill(status=422,json={'error':'Coop automatic access unavailable in test fixture'})
 elif a=='logout':result={'ok':True}
 else:return route.fulfill(status=400,json={'error':'Unexpected test action: '+str(a)})
 route.fulfill(status=200,json=result)
def nav(p,route):p.locator(f'.nav-btn[data-route="{route}"]:visible').first.click()
def profile(p,id):
 p.locator('#device-profile-button').click();p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('id=>NK_HOUSEHOLD.id===id&&!document.querySelector("#household-dialog").open',arg=id)
def goal(p,amount):
 nav(p,'profile');p.locator('#target-protein').fill(str(amount));p.locator('#profile-form button[type=submit]').click();p.wait_for_function('n=>NK_APP.getState().profile.manual.protein===n',arg=amount);nav(p,'today')
def search(p,q):
 nav(p,'search');p.locator('#finder-query').fill(q);p.locator('#finder-form button').click()
def own_save(p):
 p.locator('#custom-food-form input[type=checkbox][required]').check();p.locator('#custom-food-form button[type=submit]').click();p.locator('#dialog').wait_for(state='hidden');p.evaluate('NK_HOUSEHOLD.flush()')
def log(p,id,amount):
 p.evaluate('id=>NK_APP.openFood(NK_APP.getState().foods.find(f=>f.id===id)||NK_SHARED.foods().find(f=>f.id===id))',id);p.locator('#food-qty').fill(str(amount));p.locator('#food-form button[type=submit]').click();p.locator('#dialog').wait_for(state='hidden');p.evaluate('NK_HOUSEHOLD.flush()')
with sync_playwright() as pw:
 engine=os.environ.get('TEST_BROWSER','chromium');browser=getattr(pw,engine).launch(**({'executable_path':'/usr/bin/chromium','args':['--no-sandbox']} if engine=='chromium' and Path('/usr/bin/chromium').exists() else {}));ctx=browser.new_context(viewport={'width':390,'height':844},service_workers='block');ctx.route('**/*',api);p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 try:
  p.goto(URL);p.locator('#gate-password').fill('synthetic-only');p.locator('#gate-form button[type=submit]').click();p.locator(f'[data-nk="choose"][data-id="{D}"]').click();p.wait_for_function('window.NK_APP && NK_HOUSEHOLD.id');ok('Authenticated app starts')
  goal(p,50);ok('Daily target still visible',p.locator('.protein-target').inner_text().find('50')>=0)
  nav(p,'search');before=len([x for x in requests if x[0]=='search']);p.locator('#finder-query').fill('redefine flank steak');ok('No external request while typing',len([x for x in requests if x[0]=='search'])==before)
  p.locator('#finder-form button').click();p.locator('#finder-results [data-found]').first.wait_for();ok('Name lookup finds reviewed local source',p.locator('#finder-results').inner_text().lower().find('flank')>=0)
  p.locator('#finder-online').click();p.wait_for_function('document.querySelector("#finder-status").textContent.includes("ergänzt")');ok('Online lookup adds real variant fields',p.locator('#finder-results').inner_text().find('Open Food Facts')>=0)
  p.locator('[data-nk-scan]').first.click();p.locator('#scan-dialog details summary').click();p.locator('#nutrition-text').fill('Pro Portion (30 g)\nEnergie 150 kcal\nFett 9 g\nKohlenhydrate 12 g\nEiweiss 3 g\nZucker 0 g\nVitamin B12 0,3 µg');p.locator('#parse-text').click();p.locator('#scan-name').fill('Synthetic 30g product');ok('Portion header proposed',p.locator('#scan-amount').input_value()=='30');ok('Protein per 100g calculated',p.locator('#scan-out-protein').inner_text()=='10 g')
  p.locator('#scan-amount').fill('60');ok('Changing denominator does not compound',p.locator('#scan-out-protein').inner_text()=='5 g');p.locator('#scan-amount').fill('30');p.locator('#scan-confirm').check();p.locator('#scan-raw-protein').fill('3');ok('Changing values clears confirmation',not p.locator('#scan-confirm').is_checked());p.locator('#scan-confirm').check();p.screenshot(path=str(OUT/'portion.png'));p.locator('#scan-transfer').click();ok('Preview normalised only once',p.locator('#custom-protein').input_value()=='10');p.locator('#custom-food-form button[type=submit]').click();p.locator('#dialog').wait_for(state='hidden');p.evaluate('NK_HOUSEHOLD.flush()');fid=p.evaluate('NK_APP.getState().foods[0].id');ok('Unknown vitamin remains unknown',p.evaluate('NK_APP.getState().foods[0].n.vitC===null'));log(p,fid,100);ok('Below target does not celebrate',not p.locator('#protein-party').count() or not p.locator('#protein-party').is_visible())
  link='https://www.coop.ch/de/lebensmittel/fleisch-fisch/the-veggie-chef/steaks-filets/redefine-vegane-alternative-zu-flank-steak/p/7451865?gclid=TEST'
  search(p,link);p.wait_for_function('document.querySelector("#finder-status").textContent.includes("Quellenstand")');ok('Blocked live link explicitly uses reviewed snapshot',p.locator('#finder-status').inner_text().find('kein aktueller Live-Abruf')>=0);ok('Tracking removed before server call',not any('gclid' in d.get('url','') for a,d in requests if a=='link'));p.locator('#finder-results [data-found]').first.click();ok('Link import has correct protein',p.locator('#custom-protein').input_value()=='26');own_save(p);log(p,'coop-7451865',200);p.locator('#protein-party[open]').wait_for();ok('Protein target triggers Spanish screen','¡Felicitaciones!' in p.locator('#protein-party').inner_text());p.screenshot(path=str(OUT/'celebration.png'));p.locator('#party-close').click();nav(p,'search');nav(p,'today');p.wait_for_timeout(250);ok('Party does not repeat during navigation',not p.locator('#protein-party').is_visible());p.reload();p.wait_for_function('window.NK_APP');p.wait_for_timeout(300);ok('Party does not repeat after reload',not p.locator('#protein-party').count() or not p.locator('#protein-party').is_visible())
  profile(p,P);p.evaluate('NK_SHARED.refresh(true)');goal(p,20);search(p,'Redefine');p.locator('#finder-results [data-found]').first.click();ok('Other profile can use imported shared product directly',p.locator('#food-form').is_visible());p.locator('#food-qty').fill('100');p.locator('#food-form button[type=submit]').click();p.locator('#protein-party[open]').wait_for();ok('Patricia celebrates independently','Patricia' in p.locator('#protein-party').inner_text());p.locator('#party-close').click();p.evaluate('NK_HOUSEHOLD.flush()');ok('Personal diaries remain separate',len(profiles[P]['state']['entries'])==1 and len(profiles[D]['state']['entries'])==2)
  search(p,'https://127.0.0.1/private');p.wait_for_timeout(150);ok('Unsupported/private URL rejected',p.locator('#finder-status').inner_text().find('ausschliesslich')>=0)
  nav(p,'recipes');p.locator('[data-action="new-recipe"]').first.click();p.locator('#recipe-name').fill('Synthetic shared steak meal');p.locator('#recipe-servings').fill('2');p.locator('#recipe-weight').fill('200');p.locator('[data-action="ingredient-search"]').click();p.locator('#ingredient-search').fill('Redefine');p.locator('#ingredient-results [data-action="food-pick"]').first.click();p.locator('#food-qty').fill('200');p.locator('#food-form button[type=submit]').click();p.locator('[data-action="save-recipe"]').click();p.wait_for_function('NK_APP.getState().recipes.length===1');p.evaluate('NK_HOUSEHOLD.flush()');ok('Shared imported food usable in saved recipe',len(profiles[P]['state']['recipes'])==1)
  profile(p,D);p.evaluate('NK_SHARED.refresh(true)');nav(p,'recipes');ok('Recipe remains visible across profiles','Synthetic shared steak meal' in p.locator('#main').inner_text())
  nav(p,'search');p.set_viewport_size({'width':320,'height':780});ok('320px layout no horizontal overflow',p.evaluate('document.documentElement.scrollWidth<=innerWidth'));p.screenshot(path=str(OUT/'finder-mobile.png'));p.set_viewport_size({'width':1440,'height':1000});ok('Desktop layout no overflow',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  ok('No JavaScript runtime errors',not errors)
 except Exception:
  import traceback
  (OUT/'failure.txt').write_text(traceback.format_exc());p.screenshot(path=str(OUT/'failure.png'),full_page=True);print('JS errors',errors);raise
 finally:
  (OUT/(engine+'-report.json')).write_text(json.dumps({'passed':len(passed),'checks':passed,'runtimeErrors':errors},indent=2));browser.close();server.shutdown()
