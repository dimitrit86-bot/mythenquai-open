"""Browser integration with actual encrypted storage and synthetic household responses."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import os,json,copy,subprocess,traceback
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT);OUT=ROOT/'test-output-measures';OUT.mkdir(exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=server.serve_forever,daemon=True).start();URL=f'http://127.0.0.1:{server.server_port}/kompass/'
if os.environ.get('LOCAL_CHROME'):URL='https://kompass.test/kompass/'
seed=json.loads(subprocess.check_output(['node','-e',"console.log(JSON.stringify(require('./kompass/core.js').initial()))"]))
seed['profile']['releaseNotesSeen']='1.11.0'
seed['foods']=[{'id':'test-drink','name':'Testdrink','basis':'ml','density':None,'n':{'energy':50,'protein':5,'carbs':5,'fat':1},'q':{},'source':'Synthetic fixture','kind':'custom','category':'Eigene Produkte','synonyms':''}]
profiles={i:{'id':i,'name':n,'revision':0,'state':copy.deepcopy(seed)} for i,n in [('test-d','Dimitri'),('test-p','Patricia')]}
checks=[];errors=[];unexpected=[];requests=[]
def check(name,ok=True):
 assert ok,name
 checks.append(name);print('PASS',name,flush=True)
def api(route):
 d=route.request.post_data_json or {};requests.append(d);a=d.get('action')
 if a=='login':r={'token':'f'*64,'expires':'2099-01-01T00:00:00Z'}
 elif a=='key':r={'key':'ab'*32}
 elif a=='profiles':r={'profiles':[{k:p[k] for k in ['id','name','revision']} for p in profiles.values()]}
 elif a=='get':r={'profile':copy.deepcopy(profiles[d['id']])}
 elif a=='save':
  p=profiles[d['id']]
  if p['revision']!=d['revision']:return route.fulfill(status=409,json={'error':'Synthetic conflict','conflict':True})
  p['state']=d['state'];p['revision']+=1;r={'revision':p['revision']}
 elif a=='catalog':r={'profiles':[{**{k:p[k] for k in ['id','name','revision']},'foods':p['state']['foods'],'recipes':p['state']['recipes']} for p in profiles.values()]}
 elif a=='logout':r={'ok':True}
 else:raise AssertionError('Unexpected action '+str(d))
 route.fulfill(status=200,json=r)
def context(b):
 c=b.new_context(viewport={'width':390,'height':844},service_workers='block',accept_downloads=True)
 def route(r):
  if '/functions/v1/' in r.request.url:return api(r)
  if r.request.url.startswith(URL):
   if not os.environ.get('LOCAL_CHROME'):return r.continue_()
   import urllib.parse,mimetypes
   rel=urllib.parse.urlsplit(r.request.url).path.lstrip('/');dest=(ROOT/rel).resolve()
   if not dest.is_relative_to(ROOT):return r.abort()
   if dest.is_dir():dest=dest/'index.html'
   if not dest.exists():return r.fulfill(status=404,body='Not found')
   return r.fulfill(path=str(dest),content_type=mimetypes.guess_type(str(dest))[0] or 'application/octet-stream')
  if r.request.url.startswith('blob:'):return r.continue_()
  unexpected.append(r.request.url);return r.abort()
 c.route('**/*',route);return c
def login(p,id='test-d'):
 p.goto(URL);p.locator('#gate-password').fill('synthetic-password');p.locator('#gate-form button[type=submit]').click();p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('id=>window.NK_APP && NK_HOUSEHOLD.id===id && !document.querySelector("#app").hidden',arg=id)
def nav(p,r):p.locator(f'[data-action="nav"][data-route="{r}"]:visible').first.click()
def sync(p):p.evaluate('NK_HOUSEHOLD.flush()')
def paste(p,text):
 nav(p,'recipes');p.locator('[data-action="paste-recipe"]').click();p.locator('#recipe-paste-text').fill(text);p.locator('#recipe-paste-form button[type=submit]').click();p.locator('#recipe-review-form').wait_for()
def pick(p,query,id):
 nav(p,'search');p.locator('[data-action="filter"][data-filter="all"]').click();p.locator('#food-search').fill(query);p.locator(f'#search-results [data-action="food-pick"][data-id="{id}"]').click();p.locator('#food-form').wait_for()
def cancel(p):p.locator('#dialog [data-action="close-dialog"]').click()
def log(p,count):p.locator('#food-form button[type=submit]').click();p.wait_for_function('n=>NK_APP.getState().entries.length===n',arg=count);sync(p)
engine=os.environ.get('TEST_BROWSER','chromium')
with sync_playwright() as play:
 args={'headless':True}
 if os.environ.get('LOCAL_CHROME'):args['executable_path']='/usr/bin/chromium'
 b=getattr(play,engine).launch(**args);c=context(b);p=c.new_page();p.set_default_timeout(12000);p.on('pageerror',lambda e:errors.append(str(e)));p.on('dialog',lambda d:d.accept())
 try:
  login(p);pick(p,'Zwiebel','blv-368')
  check('Onion defaults to one edible medium piece',p.locator('#food-unit').input_value()=='piece' and p.locator('#food-piece-size').input_value()=='110')
  p.locator('#food-qty').fill('2');check('Two onions display approximate220g','ca. 220 g' in p.locator('#food-preview').inner_text() and 'geschätzt' in p.locator('#food-preview').inner_text())
  check('Source and edible-part guidance visible','USDA' in p.locator('#food-piece-reference').inner_text() and 'Schale' in p.locator('#food-piece-reference').inner_text())
  p.locator('#food-piece-kind').select_option('small');check('Size selection recalculates two small onions','140 g' in p.locator('#food-preview').inner_text())
  p.locator('#food-piece-kind').select_option('large');check('Dropdown label updates along with piece weight','150' in p.locator('#food-unit option:checked').inner_text() and '300 g' in p.locator('#food-preview').inner_text())
  p.locator('#food-piece-size').fill('80');check('Manual80g overrides source and removes estimate','160 g' in p.locator('#food-preview').inner_text() and 'geschätzt' not in p.locator('#food-preview').inner_text())
  log(p,1);entry=p.evaluate('NK_APP.getState().entries[0]');check('Manual weights saved not source defaults',entry['amountSpec']['portion']['size']==80 and not entry['amountSpec']['portion'].get('estimated'))
  pick(p,'Zwiebel','blv-368');p.locator('#food-qty').fill('2');log(p,2);historical=p.evaluate('NK_APP.getState().entries[1]');check('Approximation stays visible in diary',historical['amountSpec']['portion']['estimated'] and 'geschätzt' in historical['amountText'])
  pick(p,'Zwiebel','blv-368');p.locator('#food-unit').select_option('cup240');p.locator('#food-qty').fill('1/2')
  check('Chopped onion cup has reference160g and half80g',p.locator('#food-cup-grams').input_value()=='160' and '80 g' in p.locator('#food-preview').inner_text())
  check('Equivalent bulk density explained','0.667' in p.locator('#food-cup-reference').inner_text() and 'Schüttdichte' in p.locator('#food-cup-reference').inner_text())
  p.locator('#food-cup-kind').select_option('sliced');check('Sliced onion cup changes reference','57.5 g' in p.locator('#food-preview').inner_text())
  p.locator('#food-unit').select_option('cup250');check('Cup250 rescales same filling',abs(float(p.locator('#food-cup-grams').input_value())-115/240*250)<1e-7)
  log(p,3);cupEntry=p.evaluate('NK_APP.getState().entries[2]');check('Cup metadata stores source form and uncertainty',cupEntry['cupUse']['estimated'] and cupEntry['cupUse']['reference']['variantId']=='sliced')
  pick(p,'Paprika','blv-360');p.locator('#food-qty').fill('½');check('Half medium paprika59.5g','59.5 g' in p.locator('#food-preview').inner_text());cancel(p)
  pick(p,'Haferflocken','blv-198');p.locator('#food-unit').select_option('cup240');p.locator('#food-qty').fill('1');check('Oats uses backed reference not water','89 g' in p.locator('#food-preview').inner_text() and 'King Arthur' in p.locator('#food-cup-reference').inner_text())
  for w in [320,390,1440]:
   p.set_viewport_size({'width':w,'height':900});p.wait_for_timeout(120);check(f'Cup references fit {w}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth && document.querySelector("#dialog").scrollWidth<=document.querySelector("#dialog").clientWidth'))
  p.set_viewport_size({'width':390,'height':844});p.screenshot(path=str(OUT/f'{engine}-cup.png'),full_page=True);cancel(p)
  pick(p,'Paprika','blv-663');check('Paprika powder receives no vegetable piece default',p.locator('#food-unit option[value="piece"]').count()==0);p.locator('#food-unit').select_option('cup240');p.locator('#food-qty').fill('1');check('Unsupported ingredient still requires conversion','Gramm' in p.locator('#food-preview').inner_text());cancel(p)
  pick(p,'Zwiebel','blv-368');p.locator('#food-unit').select_option('g');p.locator('#food-qty').fill('100');check('Weighed grams do not inherit estimated label','geschätzt' not in p.locator('#food-preview').inner_text());cancel(p)
  pick(p,'Zwiebel','blv-368');p.locator('#food-piece-kind').select_option('large');p.locator('[data-action="configure-portion"]').click();p.locator('#custom-name').fill('Unsere grosse Zwiebel');check('Permanent variant uses selected size not initial size',p.locator('#custom-piece-size').input_value()=='150');p.locator('#custom-food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().foods.length===2');sync(p)
  variant=p.evaluate('NK_APP.getState().foods.find(f=>f.name==="Unsere grosse Zwiebel")');check('Unchanged source provenance retained in own variant',variant['portion']['estimated'] and variant['portion']['reference']['variantId']=='large')
  pick(p,'Unsere grosse Zwiebel',variant['id']);p.locator('#food-piece-size').fill('175');p.locator('[data-action="configure-portion"]').click();p.locator('#custom-food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().foods.find(f=>f.name==="Unsere grosse Zwiebel").portion.size===175');sync(p)
  check('User weighed175g becomes own definition',not p.evaluate('NK_APP.getState().foods.find(f=>f.name==="Unsere grosse Zwiebel").portion.estimated||false'))
  check('Existing diary snapshot unchanged by template edits',p.evaluate('NK_APP.getState().entries[1]')==historical)
  text='Gemüsereis\nFür 2 Portionen\nZutaten:\n2 grosse Zwiebeln\n1 cup Reis, gekocht\n1 Paprika\nZubereitung:\nAlles mischen.'
  paste(p,text);check('Complete recipe imported as three rows',p.locator('.paste-row').count()==3)
  p.locator('#paste-food-0').select_option('blv-368');p.locator('#paste-search-1').fill('Reis gekocht');p.locator('#paste-food-1').select_option('blv-1066');p.locator('#paste-food-2').select_option('blv-360')
  check('Recipe text suggests large onion with source weight',p.locator('#paste-reference-0').input_value()=='large' and '300 g' in p.locator('#paste-line-status-0').inner_text())
  check('Cooked rice uses158g not185g dry','158 g' in p.locator('#paste-line-status-1').inner_text())
  check('Recipe preview prominently marks estimates','Referenzschätzungen' in p.locator('#paste-preview').inner_text())
  p.locator('#paste-confirm').check();p.locator('#paste-reference-0').select_option('small');check('Changing reference resets required confirmation',not p.locator('#paste-confirm').is_checked());p.locator('#paste-per-0').fill('75');check('Manual recipe size wins','150 g' in p.locator('#paste-line-status-0').inner_text() and 'geschätzt' not in p.locator('#paste-line-status-0').inner_text())
  for w in [320,390,1440]:
   p.set_viewport_size({'width':w,'height':900});p.wait_for_timeout(120);check(f'Recipe reference review fits {w}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth && document.querySelector("#recipe-paste-dialog").scrollWidth<=document.querySelector("#recipe-paste-dialog").clientWidth'))
  p.set_viewport_size({'width':390,'height':844});p.screenshot(path=str(OUT/f'{engine}-recipe.png'),full_page=True)
  p.locator('#paste-confirm').check();p.locator('#recipe-review-form button[type=submit]').click();p.locator('#recipe-name').wait_for();check('Imported draft not saved or consumed yet',p.evaluate('NK_APP.getState().recipes.length===0 && NK_APP.getState().entries.length===3'))
  check('Editor shows approximate ingredient quantities','Referenzschätzungen' in p.locator('#recipe-summary').inner_text());p.locator('[data-action="save-recipe"]').click();p.wait_for_function('NK_APP.getState().recipes.length===1');sync(p)
  r=p.evaluate('NK_APP.getState().recipes[0]');check('Canonical saved grams and source metadata retained',r['ingredients'][0]['quantity']==150 and r['ingredients'][1]['quantity']==158 and r['ingredients'][2]['quantity']==119 and r['ingredients'][2]['portionUse']['estimated'])
  p.locator('[data-action="log-recipe"]').first.click();check('Recipe serving preview cautions estimated amounts','näherungsweise' in p.locator('#log-preview').inner_text());p.locator('#recipe-log-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().entries.length===4');sync(p)
  check('Logged recipe retains estimate notice','geschätzt' in p.evaluate('NK_APP.getState().entries[3].amountText'))
  p.reload();p.wait_for_function('window.NK_APP');check('Reload preserves own175g size and historical snapshots',p.evaluate('NK_APP.getState().foods.find(f=>f.name==="Unsere grosse Zwiebel").portion.size')==175 and p.evaluate('NK_APP.getState().entries[1]')==historical)
  c2=context(b);p2=c2.new_page();login(p2,'test-p');p2.evaluate('NK_SHARED.refresh(true)');check('Shared template retains user-weight priority',p2.evaluate('NK_SHARED.foods().some(f=>f.name==="Unsere grosse Zwiebel"&&f.portion.size===175&&!f.portion.estimated)'));check('Shared recipe retains estimation metadata',p2.evaluate('NK_SHARED.recipes().some(r=>r.name==="Gemüsereis"&&r.ingredients[2].portionUse.estimated)'));check('Other personal diary remains separate',p2.evaluate('NK_APP.getState().entries.length')==0);c2.close()
  check('Reports PDF and photo imports remain loaded',p.evaluate('!!NK_REPORT_PDF && !!NK_PHOTO_PRODUCT && !!NK_SCANNER'))
  check('New release documents changes',p.evaluate('NK_RELEASE_DATA.releases.some(r=>r.version==="1.11.0")'))
  check('No new services or requests',all(d['action'] in ['login','key','profiles','get','save','catalog','logout'] for d in requests) and not unexpected)
  check('No JavaScript runtime errors',not errors)
 except Exception:
  (OUT/f'{engine}-failure.txt').write_text(traceback.format_exc()+str(errors));p.screenshot(path=str(OUT/f'{engine}-failure.png'),full_page=True);print(p.locator('body').inner_text()[-10000:]);raise
 finally:
  (OUT/f'{engine}-report.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'errors':errors,'unexpected':unexpected},indent=2));b.close();server.shutdown()
