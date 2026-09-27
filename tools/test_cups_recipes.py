"""Browser integration with actual encrypted storage and synthetic household responses."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import os,json,copy,subprocess,traceback
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT);OUT=ROOT/'test-output-cups';OUT.mkdir(exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=server.serve_forever,daemon=True).start();URL=f'http://127.0.0.1:{server.server_port}/kompass/'
seed=json.loads(subprocess.check_output(['node','-e',"console.log(JSON.stringify(require('./kompass/core.js').initial()))"]))
seed['profile']['releaseNotesSeen']='1.10.0'
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
  if r.request.url.startswith(URL) or r.request.url.startswith('blob:'):return r.continue_()
  unexpected.append(r.request.url);return r.abort()
 c.route('**/*',route);return c
def login(p,id='test-d'):
 p.goto(URL);p.locator('#gate-password').fill('synthetic-password');p.locator('#gate-form button[type=submit]').click();p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('id=>window.NK_APP && NK_HOUSEHOLD.id===id && !document.querySelector("#app").hidden',arg=id)
def nav(p,r):p.locator(f'[data-action="nav"][data-route="{r}"]:visible').first.click()
def sync(p):p.evaluate('NK_HOUSEHOLD.flush()')
def paste(p,text):
 nav(p,'recipes');p.locator('[data-action="paste-recipe"]').click();p.locator('#recipe-paste-text').fill(text);p.locator('#recipe-paste-form button[type=submit]').click();p.locator('#recipe-review-form').wait_for()
engine=os.environ.get('TEST_BROWSER','chromium')
with sync_playwright() as play:
 args={'headless':True}
 if os.environ.get('LOCAL_CHROME'):args['executable_path']='/usr/bin/chromium'
 b=getattr(play,engine).launch(**args);c=context(b);p=c.new_page();p.set_default_timeout(12000);p.on('pageerror',lambda e:errors.append(str(e)));p.on('dialog',lambda d:d.accept())
 try:
  login(p);nav(p,'search');p.locator('[data-action="new-food"]').first.click();p.locator('#custom-name').fill('Testmehl')
  for k,v in [('energy','360'),('protein','10'),('carbs','70'),('fat','2')]:p.locator('#custom-'+k).fill(v)
  p.locator('#custom-piece-size').fill('30');p.locator('details:has(#custom-cup-grams)>summary').click();p.locator('#custom-cup-grams').fill('120');p.locator('#custom-food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().foods.length===2');sync(p)
  f=p.evaluate('NK_APP.getState().foods.find(f=>f.name==="Testmehl")');fid=f['id']
  check('Product stores piece and cup definitions independently',f['cup']=={'grams':120,'ml':240} and f['portion']['size']==30)
  p.locator(f'[data-action="food-pick"][data-id="{fid}"]').click();p.locator('#food-unit').select_option('cup240');p.locator('#food-qty').fill('1/2')
  check('Cup input preview uses ingredient mass, not water','60 g' in p.locator('#food-preview').inner_text() and '6' in p.locator('#food-preview').inner_text())
  for w in [320,390,1440]:
   p.set_viewport_size({'width':w,'height':900});p.wait_for_timeout(120);check(f'Cup input fits {w}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  p.set_viewport_size({'width':390,'height':844});p.locator('#food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().entries.length===1');sync(p)
  entry=p.evaluate('NK_APP.getState().entries[0]');check('Diary stores canonical grams and descriptive cups',entry['amountSpec']['unit']=='g' and entry['amountSpec']['quantity']==60 and entry['n']['protein']['value']==6 and 'Cup' in entry['amountText'])
  p.locator('[data-action="entry-menu"]').first.click();p.locator('#entry-factor').fill('2');p.locator('#entry-edit-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().entries[0].n.protein.value===12');check('Changing logged amount scales cup display',p.evaluate('NK_APP.getState().entries[0].cupUse.quantity')==1)
  nav(p,'search');p.locator('#food-search').fill('Testdrink');p.locator('[data-action="food-pick"][data-id="test-drink"]').first.click();p.locator('#food-unit').select_option('cup250');p.locator('#food-qty').fill('½');check('Drink converts cup directly to millilitres','125 ml' in p.locator('#food-preview').inner_text());p.locator('#food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().entries.length===2');sync(p)
  nav(p,'search');p.locator('[data-action="filter"][data-filter="all"]').click();p.locator('#food-search').fill('Haferflocken');p.locator('#search-results [data-action="food-pick"]').first.click();p.locator('#food-unit').select_option('cup240');p.locator('#food-qty').fill('1');check('Unknown mass blocks cup calculation','Gramm' in p.locator('#food-preview').inner_text());p.locator('#food-form button[type=submit]').click();check('No diary entry silently created without conversion',p.evaluate('NK_APP.getState().entries.length')==2);p.locator('#dialog [data-action="close-dialog"]').click()
  text='Pancakes zum Testen\nFür 2 Portionen\nZutaten:\n1 cup Testmehl\n200 ml Testdrink\n2 Eier\nZubereitung:\n1. Alles mischen.\n2. 10 Minuten backen.\nNährwerte: angeblich 999 kcal'
  paste(p,text);check('Whole recipe produces exactly three ingredient rows',p.locator('.paste-row').count()==3);check('Title and servings prefilled',p.locator('#paste-name').input_value()=='Pancakes zum Testen' and p.locator('#paste-servings').input_value()=='2')
  check('Exact known product is preselected',p.locator('#paste-food-0').input_value()==fid)
  p.locator('#paste-food-2').select_option('blv-290');p.locator('#paste-confirm').check();p.locator('#recipe-review-form button[type=submit]').click();check('Piece weight required instead of assuming egg size',p.locator('#recipe-paste-dialog').is_visible() and p.evaluate('NK_APP.getState().recipes.length')==0)
  p.locator('#paste-per-2').fill('50');check('Changing quantities resets confirmation',not p.locator('#paste-confirm').is_checked());check('Live recipe preview available after all mappings','Vorschau pro Portion' in p.locator('#paste-preview').inner_text())
  for w in [320,390,1440]:
   p.set_viewport_size({'width':w,'height':900});p.wait_for_timeout(120);check(f'Recipe review fits {w}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth && document.querySelector("#recipe-paste-dialog").scrollWidth<=document.querySelector("#recipe-paste-dialog").clientWidth'))
  p.set_viewport_size({'width':390,'height':844});p.screenshot(path=str(OUT/f'{engine}-recipe-preview.png'),full_page=True)
  p.locator('#paste-confirm').check();p.locator('#recipe-review-form button[type=submit]').click();p.locator('#recipe-name').wait_for();check('Accepted recipe is only an unsaved draft',p.evaluate('NK_APP.getState().recipes.length')==0 and p.evaluate('NK_APP.hasDraft'))
  check('Recipe editor retains original cup quantity',p.locator('[data-ingredient="0"][data-field="unit"]').input_value()=='cup240' and p.locator('[data-ingredient="0"][data-field="quantity"]').input_value()=='1')
  p.locator('[data-action="save-recipe"]').click();p.wait_for_function('NK_APP.getState().recipes.length===1');sync(p)
  recipe=p.evaluate('NK_APP.getState().recipes[0]');check('Saved recipe uses canonical weights',recipe['ingredients'][0]['quantity']==120 and recipe['ingredients'][0]['unit']=='g');check('Preparation and whole original preserved',recipe['importText']==text and '10 Minuten' in recipe['notes'])
  check('Copying a recipe does not eat it',p.evaluate('NK_APP.getState().entries.length')==2)
  p.locator('[data-action="log-recipe"]').first.click();p.locator('#recipe-log-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().entries.length===3');sync(p);historical=p.evaluate('NK_APP.getState().entries[2]')
  check('Recipe can be logged by portion',historical['kind']=='recipe' and historical['n']['protein']['value']>0)
  nav(p,'recipes');p.locator('[data-action="edit-recipe"]').first.click();p.locator('[data-ingredient="0"][data-field="quantity"]').fill('2');p.locator('[data-action="save-recipe"]').click();p.wait_for_function('NK_APP.getState().recipes[0].ingredients[0].quantity===240');check('Changing recipe never rewrites logged history',p.evaluate('NK_APP.getState().entries[2]')==historical)
  text2='Unsichere Zutat\nZutaten:\n20 g Testzauber\nSalz nach Geschmack\nZubereitung:\nMischen.'
  paste(p,text2);check('Missing servings requires explicit entry',p.locator('#paste-servings').input_value()=='');p.locator('#paste-servings').fill('1');p.locator('#paste-food-0').select_option('unknown');p.locator('#paste-search-1').fill('Speisesalz');p.locator('#paste-food-1').select_option('unknown');p.locator('#paste-qty-1').fill('1');p.locator('#paste-unit-1').select_option('g');check('Ingredient choice survives unchanged search blur',p.locator('#paste-food-1').input_value()=='unknown');check('Unknown ingredient creates visible partial preview','*' in p.locator('#paste-preview').inner_text());p.locator('#paste-confirm').check();p.locator('#recipe-review-form button[type=submit]').click();p.locator('#recipe-name').wait_for();p.locator('[data-action="save-recipe"]').click();p.wait_for_function('NK_APP.getState().recipes.length===2');sync(p)
  r=p.evaluate('NK_APP.getState().recipes.find(r=>r.name==="Unsichere Zutat")');check('Unknown nutrient values stay null',r['ingredients'][0]['food']['n']['protein'] is None)
  paste(p,'Discard Test\nFür 1 Portion\nZutaten:\n50 g Testmehl');p.locator('[data-paste-close]').click();check('Cancel leaves recipes and diaries intact',p.evaluate('NK_APP.getState().recipes.length')==2 and p.evaluate('NK_APP.getState().entries.length')==3)
  sync(p);p.reload();p.wait_for_function('window.NK_APP');check('Reload restores cups and full recipe source',p.evaluate('NK_APP.getState().recipes.find(r=>r.name==="Pancakes zum Testen").importText')==text)
  c2=context(b);p2=c2.new_page();login(p2,'test-p');p2.evaluate('NK_SHARED.refresh(true)');check('Other household profile sees cup product',p2.evaluate('NK_SHARED.foods().some(f=>f.name==="Testmehl"&&f.cup.grams===120)'));check('Other profile sees shared imported recipe',p2.evaluate('NK_SHARED.recipes().some(r=>r.name==="Pancakes zum Testen"&&!!r.importText)'));check('Other profile diary remains empty',p2.evaluate('NK_APP.getState().entries.length')==0);c2.close()
  check('No extra service calls for parsing',all(d['action'] in ['login','key','profiles','get','save','catalog','logout'] for d in requests));check('Reports and both photo paths remain installed',p.evaluate('!!NK_REPORT_PDF && !!NK_PHOTO_PRODUCT && !!NK_SCANNER'))
  check('Release catalogue documents 1.10.0',p.evaluate('NK_RELEASE_DATA.releases.some(r=>r.version==="1.10.0")'));check('No unexpected network calls',not unexpected);check('No JavaScript runtime errors',not errors)
 except Exception:
  (OUT/f'{engine}-failure.txt').write_text(traceback.format_exc()+str(errors));p.screenshot(path=str(OUT/f'{engine}-failure.png'),full_page=True);print(p.locator('body').inner_text()[-9000:]);raise
 finally:
  (OUT/f'{engine}-report.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'errors':errors,'unexpected':unexpected},indent=2));b.close();server.shutdown()
