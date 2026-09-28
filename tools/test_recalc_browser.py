"""UI regression with synthetic household responses and encrypted browser storage.
No production household requests, credentials or personal data are used.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import os,json,copy,subprocess
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
OUT=ROOT/'test-output';OUT.mkdir(exist_ok=True)
FIXTURE=r'''
global.window=global;require('./kompass/data.js');const C=require('./kompass/core.js'),R=require('./kompass/nutrition-recalc.js'),crypto=require('node:crypto');
const K=NK_DATA.nutrients.map(n=>n.key),today=C.dateKey(),n=Object.fromEntries(K.map(k=>[k,null]));Object.assign(n,{energy:100,protein:10,fat:2,carbs:10,vitC:5});
const f={id:'custom-test',name:'Korrektur-Testprodukt',kind:'custom',basis:'g',density:1,n,q:{},source:'Synthetischer Test',category:'Eigene Produkte',synonyms:'',portion:{label:'Stück',size:30,unit:'g'},cup:{grams:100,ml:240}};
const other={...C.clone(f),id:'other',name:'Zweite Zutat',n:{...n,energy:200,protein:0,vitC:0}};
const ingredients=[{food:C.clone(f),quantity:100,unit:'g',density:null},{food:other,quantity:50,unit:'g',density:null}];
const recipe={id:'recipe-test',name:'Korrektur-Testgericht',version:1,servings:2,finalWeight:200,ingredients,notes:''};
const alias=id=>'shared-'+(id==='recipe-test'?'r-':'f-')+crypto.createHash('sha256').update('test-p:'+id).digest('hex').slice(0,32);
function initial(){const s=C.initial();s.profile.releaseNotesSeen='1.13.0';s.profile.dayReviewThrough=today;s.profile.manual={protein:500,vitC:50};s.days[today]={complete:true};return s;}
const p=initial();p.foods=[f];p.recipes=[recipe];p.entries=[{id:'food-p',name:f.name,kind:'food',date:today,meal:0,sourceId:f.id,amountText:'150 g',amountSpec:{quantity:150,unit:'g'},n:C.snapshot(f,150,'g',null,K)},{id:'recipe-p',name:recipe.name,kind:'recipe',date:today,meal:1,recipeId:recipe.id,recipeVersion:1,amountText:'1 Portion(en)',ingredients:C.clone(ingredients),n:C.recipePortion(recipe,1,'portion',K)}];
const d=initial();d.entries=[{...C.clone(p.entries[0]),id:'shared-food-d',sourceId:alias(f.id),amountText:'50 g',amountSpec:{quantity:50,unit:'g'},n:C.snapshot(f,50,'g',null,K)},{...C.clone(p.entries[1]),id:'shared-recipe-d',recipeId:alias(recipe.id),amountText:'0,5 Portion(en)',n:C.recipePortion(recipe,.5,'portion',K)}];
const variant={...C.clone(f),id:'custom-variant',name:'Eigene unabhängige Variante'};d.foods=[variant];d.entries.push({id:'variant-d',name:variant.name,kind:'food',date:today,meal:2,sourceId:variant.id,amountText:'40 g',amountSpec:{quantity:40,unit:'g'},n:C.snapshot(variant,40,'g',null,K)});
console.log(JSON.stringify({p,d,today,foodAlias:alias(f.id)}));
'''
fixture=json.loads(subprocess.check_output(['node','-e',FIXTURE]))
profiles={i:{'id':i,'name':name,'revision':0,'state':fixture[k]} for i,name,k in [('test-p','Patricia','p'),('test-d','Dimitri','d')]}
checks=[];errors=[];unexpected=[];requests=[];offline=False
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}/kompass/'
def check(n,ok=True):
 assert ok,n
 checks.append(n);print('PASS',n,flush=True)
def api(route):
 d=route.request.post_data_json or {};a=d.get('action');requests.append((route.request.url,d))
 if offline and a in ['save','catalog']:return route.fulfill(status=503,json={'error':'Synthetic unavailable'})
 if a=='login':out={'token':'f'*64,'expires':'2099-01-01T00:00:00Z'}
 elif a=='key':out={'key':'ab'*32}
 elif a=='profiles':out={'profiles':[{k:p[k] for k in ['id','name','revision']} for p in profiles.values()]}
 elif a=='get':out={'profile':copy.deepcopy(profiles[d['id']])}
 elif a=='save':
  p=profiles[d['id']]
  if p['revision']!=d['revision']:return route.fulfill(status=409,json={'error':'Synthetic revision conflict','conflict':True})
  p['state']=copy.deepcopy(d['state']);p['revision']+=1;out={'revision':p['revision']}
 elif a=='catalog':out={'profiles':[{**{k:p[k] for k in ['id','name','revision']},'foods':copy.deepcopy(p['state']['foods']),'recipes':copy.deepcopy(p['state']['recipes'])} for p in profiles.values()]}
 elif a=='logout':out={'ok':True}
 else:raise AssertionError('Unexpected request '+str(d))
 return route.fulfill(status=200,json=out)
def context(b):
 c=b.new_context(viewport={'width':390,'height':844},service_workers='block',accept_downloads=True)
 def routing(r):
  if '/functions/v1/' in r.request.url:return api(r)
  if r.request.url.startswith(URL) or r.request.url.startswith('blob:'+URL.split('/kompass/')[0]+'/'):return r.continue_()
  unexpected.append(r.request.url);return r.abort()
 c.route('**/*',routing);return c

def login(p,id='test-p'):
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.goto(URL);p.locator('#gate-password').fill('synthetic-test-only');p.locator('#gate-form button[type=submit]').click();p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('id=>window.NK_APP&&NK_HOUSEHOLD.id===id&&!document.querySelector("#app").hidden',arg=id)
def nav(p,v):p.locator(f'[data-action="nav"][data-route="{v}"]:visible').first.click()
def edit_product(p):
 nav(p,'search');p.locator('#food-search').fill('Korrektur-Testprodukt');p.locator('#search-results [data-action="food-pick"]').first.click();p.locator('details:has([data-action="edit-custom-food"])>summary').click();p.locator('[data-action="edit-custom-food"]').click()
def save_product(p):
 p.locator('#custom-food-form button[type=submit]').click();p.wait_for_function('!document.querySelector("#dialog").open');p.evaluate('NK_HOUSEHOLD.flush()')
def energy(p,id):return p.evaluate('id=>NK_APP.getState().entries.find(e=>e.id===id).n.energy.value',id)
engine=os.environ.get('TEST_BROWSER','chromium')
with sync_playwright() as play:
 launch={'headless':True}
 if os.environ.get('LOCAL_CHROME'):launch['executable_path']='/usr/bin/chromium'
 b=getattr(play,engine).launch(**launch);c=context(b);p=c.new_page();c2=context(b);d=c2.new_page()
 try:
  login(p);login(d,'test-d');p.evaluate('NK_SHARED.refresh(true)');d.evaluate('NK_SHARED.refresh(true)')
  check('Previous feature modules retained',p.evaluate('!!NK_CUPS&&!!NK_MEASURES&&!!NK_RECIPE_IMPORT&&!!NK_DAY_REVIEW_CORE&&!!NK_RELEASES&&!!NK_PHOTO_PRODUCT&&!!NK_REPORT_PDF'))
  before=p.evaluate('NK_APP.getState()');check('No retroactive recalculation on upgrade alone',before['entries']==fixture['p']['entries'])
  # Keep a form open on second device while the source is corrected.
  nav(d,'search');d.locator('[data-action="new-food"]').click();d.locator('#custom-name').fill('Unsaved product')
  edit_product(p);check('Editor explains retroactive correction','auch frühere Tage' in p.locator('#custom-food-form').inner_text())
  p.locator('#custom-energy').fill('120');p.locator('#custom-protein').fill('20');p.locator('details:has(#custom-vitC)>summary').click();p.locator('#custom-vitC').fill('30')
  check('Preview edits alone never mutate diary',energy(p,'food-p')==150)
  save_product(p);check('Product and direct old entry updated atomically',energy(p,'food-p')==180 and profiles['test-p']['state']['foods'][0]['n']['protein']==20)
  check('Legacy recipe entry recalculated with original share',energy(p,'recipe-p')==110)
  check('Linked recipe template updated',p.evaluate('NK_APP.getState().recipes[0].ingredients[0].food.n.energy')==120)
  after=p.evaluate('NK_APP.getState()');check('Dates, amounts and day flags unchanged',all((x['date'],x['meal'],x['amountText'])==(y['date'],y['meal'],y['amountText']) for x,y in zip(before['entries'],after['entries'])))
  check('Body data and personal targets unchanged',before['profile']==after['profile'] and before['days']==after['days'])
  d.evaluate('NK_SHARED.refresh(true)');d.wait_for_timeout(500);check('Other profile corrections wait for open unsaved form',energy(d,'shared-food-d')==50 and d.locator('#custom-name').input_value()=='Unsaved product')
  d.locator('#dialog [data-action="close-dialog"]').click();d.wait_for_function('NK_APP.getState().entries.find(e=>e.id==="shared-food-d").n.energy.value===60');d.evaluate('NK_HOUSEHOLD.flush()')
  check('Shared product corrects other profile after catalogue load',energy(d,'shared-food-d')==60)
  check('Legacy shared recipe corrected by exact owner',energy(d,'shared-recipe-d')==55)
  check('Independent variant not changed',energy(d,'variant-d')==40)
  d_before=d.evaluate('NK_APP.getState()');d.evaluate('NK_SHARED.refresh(true)');d.wait_for_timeout(500);check('Repeated shared refresh does not multiply values',d_before==d.evaluate('NK_APP.getState()'))
  # Reports are freshly derived and existing PDF export should use corrected totals.
  nav(p,'reports');p.locator('[data-action="report-period"][data-frequency="daily"]').click()
  p.locator('[data-action="report-current"]').click();check('Report energy total updates immediately','290' in p.locator('#report-group-macro').inner_text())
  p.screenshot(path=str(OUT/f'{engine}-corrected-report.png'),full_page=True)
  p.locator('[data-action="report-pdf"]').click()
  check('PDF export remains available',p.locator('#report-pdf-dialog').is_visible() if p.locator('#report-pdf-dialog').count() else 'PDF' in p.locator('dialog[open]').inner_text())
  p.locator('input[name="pdf-layout"][value="compact"]').check();p.locator('#pdf-create').click();p.locator('#pdf-download').wait_for()
  with p.expect_download() as download:p.locator('#pdf-download').click()
  download.value.save_as(str(OUT/f'{engine}-corrected-report.pdf'))
  check('Corrected PDF generated', (OUT/f'{engine}-corrected-report.pdf').stat().st_size>1000)
  p.locator('#pdf-close').click()
  # Capture and rescale newly recorded piece intake, then correct once more.
  nav(p,'search');p.locator('#food-search').fill('Korrektur-Testprodukt');p.locator('#search-results [data-action="food-pick"]').first.click();p.locator('#food-unit').select_option('piece');p.locator('#food-qty').fill('2');p.locator('#food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().entries.length===3');p.evaluate('NK_HOUSEHOLD.flush()')
  piece=p.evaluate('NK_APP.getState().entries.at(-1)');check('New piece entry stores exact original grams',piece['nutritionBase']['quantity']==60 and piece['n']['energy']['value']==72)
  edit_product(p);p.locator('#custom-energy').fill('200');p.locator('#custom-piece-size').fill('50');save_product(p)
  check('Old pieces use captured 30g not new 50g size',p.evaluate('id=>NK_APP.getState().entries.find(e=>e.id===id).n.energy.value',piece['id'])==120)
  p.reload();p.wait_for_function('window.NK_APP');check('Encrypted reload preserves recalculated values',energy(p,'food-p')==300 and energy(p,'recipe-p')==150)
  # Different basis cannot be silently used for historical mass/volume.
  edit_product(p);p.locator('#custom-piece-size').fill('');p.locator('#custom-cup-grams').fill('');p.locator('#custom-basis').select_option('ml');save_product(p)
  check('Incompatible basis preserves old totals and exposes review',energy(p,'food-p')==300 and p.locator('[data-action="nutrition-review"]').count()==1)
  p.locator('[data-action="nutrition-review"]').click();check('Review identifies affected entries',p.locator('#dialog .source-item').count()>=3)
  for w in [320,390,1440]:
   p.set_viewport_size({'width':w,'height':900});p.wait_for_timeout(100);check(f'Review fits {w}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  p.screenshot(path=str(OUT/f'{engine}-review.png'),full_page=True)
  check('No production or unexpected external calls',not unexpected)
  check('No JavaScript runtime errors',not errors)
 except Exception:
  import traceback
  (OUT/f'{engine}-failure.txt').write_text(traceback.format_exc()+str(errors));p.screenshot(path=str(OUT/f'{engine}-failure.png'),full_page=True);print(p.locator('body').inner_text()[-6000:]);raise
 finally:
  (OUT/f'{engine}-recalc-report.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'runtimeErrors':errors,'unexpected':unexpected},indent=2));b.close();server.shutdown()
