"""Real browser integration with synthetic private service responses only."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import copy,json,os,traceback,subprocess
BASE=Path(os.environ.get('NK_ROOT','.')).resolve();OUT=BASE/'test-output';OUT.mkdir(exist_ok=True)
os.chdir(BASE)
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}/kompass/'
initial=json.loads(subprocess.check_output(['node','-e',"console.log(JSON.stringify(require('./kompass/core.js').initial()))"]))
D='00000000-0000-4000-8000-000000000001';P='00000000-0000-4000-8000-000000000002'
profiles={i:{'id':i,'name':name,'revision':0,'state':copy.deepcopy(initial)} for i,name in [(D,'Dimitri Test'),(P,'Patricia Test')]}
checks=[];errors=[];unexpected=[]
def check(name,cond):
 assert cond,name
 checks.append(name);print('PASS',name,flush=True)
def api(route):
 data=route.request.post_data_json or {};a=data.get('action')
 if a=='login':out={'token':'a'*64,'expires':'2099-01-01T00:00:00Z'}
 elif a=='key':out={'key':'b'*64}
 elif a=='profiles':out={'profiles':[{k:v for k,v in p.items() if k!='state'} for p in profiles.values()]}
 elif a=='get':out={'profile':copy.deepcopy(profiles[data['id']])}
 elif a=='save':
  target=profiles[data['id']]
  if target['revision']!=data['revision']:return route.fulfill(status=409,json={'error':'Test conflict','conflict':True})
  target['state']=copy.deepcopy(data['state']);target['revision']+=1;out={'revision':target['revision']}
 elif a=='catalog':out={'profiles':[{'id':p['id'],'name':p['name'],'revision':p['revision'],'foods':p['state']['foods'],'recipes':p['state']['recipes']} for p in profiles.values()]}
 elif a=='logout':out={'ok':True}
 else:unexpected.append(a);return route.fulfill(status=400,json={'error':'Unexpected action'})
 route.fulfill(status=200,json=out)
def intercept(route):
 if '/functions/v1/' in route.request.url:return api(route)
 if route.request.url.startswith(URL):return route.continue_()
 unexpected.append(route.request.url);route.abort()
def nav(p,r):p.locator(f'.nav-btn[data-route="{r}"]:visible').first.click()
def choose(p,i):
 p.locator(f'[data-nk="choose"][data-id="{i}"]').click();p.wait_for_function('id=>NK_HOUSEHOLD.id===id && !document.querySelector("#household-dialog").open && !!window.NK_APP',arg=i)
def sync(p):p.evaluate('NK_HOUSEHOLD.flush()')
def new_food(p,name,size=None,unit='g',label='Stück'):
 nav(p,'search');p.locator('[data-action="new-food"]').first.click();p.locator('#custom-name').fill(name);p.locator('#custom-basis').select_option(unit)
 if size is not None:p.locator('#custom-piece-size').fill(str(size));p.locator('#custom-piece-unit').select_option(unit);p.locator('#custom-piece-label').fill(label)
def save_food(p):p.locator('#custom-food-form button[type="submit"]').click();p.locator('#dialog').wait_for(state='hidden');sync(p)
def pick_own(p,i):
 nav(p,'search');p.locator('#food-search').fill('');p.locator(f'#search-results [data-action="food-pick"][data-id="{i}"]').click()
engine=os.environ.get('TEST_BROWSER','chromium')
with sync_playwright() as play:
 browser=getattr(play,engine).launch();ctx=browser.new_context(viewport={'width':390,'height':844},service_workers='block',accept_downloads=True)
 ctx.route('**/*',intercept);p=ctx.new_page();p.set_default_timeout(15000);p.on('pageerror',lambda e:errors.append(str(e)))
 try:
  p.goto(URL);p.locator('#gate-password').fill('synthetic-password');p.locator('#gate-form button[type="submit"]').click();choose(p,D)
  check('Eight new manufacturer records loaded',p.evaluate('NK_ADDITIONAL_FOODS.count===8 && NK_DATA.foods.length===1305'))
  nav(p,'search');p.locator('#food-search').fill('planted.chicken Nature');p.locator('#search-results [data-action="food-pick"][data-id="label-planted-chicken-natur"]').click();p.locator('#food-qty').fill('50')
  check('New product quantity preview uses declared protein','12' in p.locator('#food-preview').inner_text());p.locator('#dialog [data-action="close-dialog"]').click();p.locator('#food-search').fill('')
  new_food(p,'Testriegel',30,label='Riegel');p.locator('[data-action="custom-text"]').click()
  check('Text reader reachable from own product',p.locator('#scan-text-section').get_attribute('open') is not None)
  p.locator('#nutrition-text').fill('pro 30 g\nEnergie 150 kcal\nFett 9 g\ndavon gesättigte Fettsäuren 1.5 g\nKohlenhydrate 15 g\ndavon Zucker 0 g\nNahrungsfasern 2 g\nEiweiss 3 g\nSalz 0.1 g');p.locator('#parse-text').click()
  check('Existing name carried into text review',p.locator('#scan-name').input_value()=='Testriegel')
  check('Portion amount suggested from text',p.locator('#scan-amount').input_value()=='30')
  check('Text protein correctly normalised',p.locator('#scan-out-protein').inner_text()=='10 g')
  p.locator('#scan-confirm').check();p.locator('#scan-transfer').click();p.locator('#scan-dialog').wait_for(state='hidden')
  check('Own product fields filled without saving',p.locator('#custom-protein').input_value()=='10' and len(profiles[D]['state']['foods'])==0)
  check('Piece weight and label kept',p.locator('#custom-piece-size').input_value()=='30' and p.locator('#custom-piece-label').input_value()=='Riegel')
  check('Piece preview displays its own nutrients','3 g Protein' in p.locator('#custom-piece-preview').inner_text())
  p.screenshot(path=str(OUT/f'{engine}-product.png'),full_page=True)
  save_food(p);fid=profiles[D]['state']['foods'][0]['id']
  check('Piece metadata persisted',profiles[D]['state']['foods'][0]['portion']=={'label':'Riegel','size':30,'unit':'g'})
  check('Product row includes portion label','1 Riegel = 30 g' in p.locator('#search-results').inner_text())
  pick_own(p,fid);check('Piece is default when defined',p.locator('#food-unit').input_value()=='piece' and p.locator('#food-qty').input_value()=='1')
  p.locator('#food-qty').fill('2');check('Two pieces show the actual mass','2 Riegel (60 g)' in p.locator('#food-preview').inner_text())
  p.locator('#food-form button[type="submit"]').click();p.locator('#dialog').wait_for(state='hidden');sync(p)
  e=profiles[D]['state']['entries'][0];check('Diary contains two pieces and correct protein',e['amountText']=='2 Riegel (60 g)' and abs(e['n']['protein']['value']-6)<1e-8)
  check('Unknown vitamin remains unknown',e['n']['vitB12']['value'] is None);old_e=copy.deepcopy(e)
  nav(p,'recipes');p.locator('[data-action="new-recipe"]').first.click();p.locator('#recipe-name').fill('Testgericht mit Stückportion');p.locator('#recipe-servings').fill('2')
  p.locator('[data-action="ingredient-search"]').click();p.locator('#ingredient-search').fill('Testriegel');p.locator(f'#ingredient-results [data-id="{fid}"][data-action="food-pick"]').click()
  p.locator('#food-qty').fill('0,5');p.locator('#food-form button[type="submit"]').click();p.locator('#dialog').wait_for(state='hidden')
  p.locator('[data-action="save-recipe"]').click();p.wait_for_function('NK_APP.getState().recipes.length===1');sync(p)
  r=profiles[D]['state']['recipes'][0];rid=r['id'];i=r['ingredients'][0]
  check('Recipe stores canonical mass and piece count',i['unit']=='g' and i['quantity']==15 and i['portionUse']['quantity']==.5)
  p.locator(f'[data-action="edit-recipe"][data-id="{rid}"]').click();check('Recipe restores piece selection',p.locator('[data-ingredient="0"][data-field="unit"]').input_value()=='piece')
  p.locator('[data-ingredient="0"][data-field="quantity"]').fill('2');p.locator('[data-action="save-recipe"]').click();p.wait_for_function('NK_APP.getState().recipes[0].ingredients[0].quantity===60');sync(p)
  check('Recipe piece quantity is editable',profiles[D]['state']['recipes'][0]['ingredients'][0]['portionUse']['quantity']==2)
  p.locator('#device-profile-button').click();choose(p,P);p.evaluate('NK_SHARED.refresh(true)');nav(p,'search');p.locator('#food-search').fill('Testriegel')
  p.locator('#search-results [data-action="food-pick"]').first.click();check('Other profile can use piece definition',p.locator('#food-unit').input_value()=='piece' and '1 Riegel = 30 g' in p.locator('#food-form').inner_text())
  p.locator('#food-qty').fill('1');p.locator('#food-form button[type="submit"]').click();p.locator('#dialog').wait_for(state='hidden');sync(p)
  check('Shared product keeps separate consumption',len(profiles[P]['state']['entries'])==1 and profiles[D]['state']['entries']==[old_e])
  nav(p,'recipes');check('Piece-based shared recipe visible',p.locator('[data-action="log-recipe"]').count()==1)
  new_food(p,'Testdrink',150,unit='ml',label='Becher');p.locator('#custom-protein').fill('2');p.locator('#custom-energy').fill('60')
  p.locator('#custom-piece-unit').select_option('g');p.locator('#custom-food-form button[type="submit"]').click();check('Mismatched g/ml cannot be saved',p.locator('#dialog').is_visible() and 'Stückportion prüfen' in p.locator('#modal-error').inner_text())
  p.locator('#custom-piece-unit').select_option('ml');save_food(p);drinkid=profiles[P]['state']['foods'][0]['id'];pick_own(p,drinkid);p.locator('#food-qty').fill('2');p.locator('#food-form button[type="submit"]').click();p.locator('#dialog').wait_for(state='hidden');sync(p)
  check('Two ml-based cups use correct volume',profiles[P]['state']['entries'][-1]['amountText']=='2 Becher (300 ml)' and profiles[P]['state']['entries'][-1]['n']['protein']['value']==6)
  nav(p,'search');p.locator('[data-action="filter"][data-filter="all"]').click();p.locator('#food-search').fill('Ei')
  check('Ei prioritises actual eggs',p.locator('#search-results [data-action="food-pick"]').first.get_attribute('data-id') in ['blv-1070','blv-290'])
  p.locator('#food-search').fill('Eier gekocht');p.locator('#search-results [data-action="food-pick"]').first.click();check('No egg mass is guessed',p.locator('#food-unit option[value="piece"]').count()==0)
  p.locator('[data-action="configure-portion"]').click();p.locator('#custom-piece-size').fill('50');save_food(p)
  check('An explicit egg piece can be saved as private template',profiles[P]['state']['foods'][0]['portion']['size']==50)
  new_food(p,'Unfertiges Produkt',20);p.locator('#custom-protein').fill('7');p.locator('[data-action="custom-text"]').click();p.locator('#nutrition-text').fill('nicht erkannte Angaben');p.locator('#scan-close').click()
  check('Cancel text reader retains unsaved product',p.locator('#custom-name').input_value()=='Unfertiges Produkt' and p.locator('#custom-protein').input_value()=='7')
  p.locator('#custom-piece-size').fill('0');p.locator('#custom-food-form button[type="submit"]').click();check('Zero piece size blocked',p.locator('#dialog').is_visible() and p.locator('#modal-error').inner_text()!='')
  p.locator('#dialog [data-action="close-dialog"]').click()
  nav(p,'profile');p.locator('#report-frequency').select_option('monthly');p.locator('#profile-form button[type="submit"]').click();sync(p)
  check('Monthly report preference saved',profiles[P]['state']['profile']['reportFrequency']=='monthly')
  nav(p,'reports');check('Reports retain nutrient groups','Spurenelemente' in p.locator('#main').inner_text())
  p.locator('[data-action="report-pdf"]').click();p.locator('[name="pdf-layout"][value="compact"]').check();p.locator('#pdf-create').click();p.locator('#pdf-download').wait_for()
  with p.expect_download() as dl:p.locator('#pdf-download').click()
  dl.value.save_as(str(OUT/f'{engine}-report.pdf'));check('Report really downloads as PDF',(OUT/f'{engine}-report.pdf').read_bytes().startswith(b'%PDF-'))
  p.locator('#pdf-close').click()
  for width in [320,390,1440]:
   p.set_viewport_size({'width':width,'height':900});p.wait_for_timeout(150);check(f'Report layout fits {width}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  p.set_viewport_size({'width':390,'height':844});p.screenshot(path=str(OUT/f'{engine}-reports.png'),full_page=True)
  p.reload();p.wait_for_function('window.NK_APP && NK_HOUSEHOLD.name==="Patricia Test"');check('Reload preserves report preference and piece values',p.evaluate('NK_APP.getState().profile.reportFrequency==="monthly" && NK_APP.getState().foods[0].portion.size===50'))
  check('No runtime errors',not errors);check('No unapproved external requests',not unexpected)
 except Exception:
  (OUT/f'{engine}-failure.txt').write_text(traceback.format_exc());p.screenshot(path=str(OUT/f'{engine}-failure.png'),full_page=True);print('ERRORS',errors,flush=True);print(p.locator('body').inner_text()[-4000:],flush=True);raise
 finally:
  (OUT/f'{engine}-report.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'runtimeErrors':errors,'unexpectedRequests':unexpected},indent=2));browser.close();server.shutdown()
