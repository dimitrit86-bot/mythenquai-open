"""Actual client UI with synthetic household responses. Never contacts a private server."""
import json,copy,os,traceback,functools
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(BASE)));Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}/kompass/'
D='11111111-1111-4111-8111-111111111111';P='22222222-2222-4222-8222-222222222222'
def initial():return {'schema':1,'profile':{'sex':'m','age':40,'weight':80,'height':180,'special':False,'smoker':False,'menopause':'','phytate':'','manual':{}},'entries':[],'recipes':[],'foods':[],'favorites':[],'recent':[],'days':{},'recipeDraft':None}
profiles={D:{'id':D,'name':'Dimitri','revision':0,'state':initial()},P:{'id':P,'name':'Patricia','revision':0,'state':initial()}}
profiles[P]['state']['profile'].update({'sex':'w','weight':60,'height':165,'age':35})
checks=[];errors=[];requests=[]
def check(name,ok=True):
 assert ok,name
 checks.append(name);print('PASS',name,flush=True)
def intercept(route):
 u=route.request.url
 if u.startswith(URL):return route.continue_()
 if '.supabase.co/functions/v1/' not in u:return route.abort()
 b=route.request.post_data_json or {};a=b.get('action');requests.append(a)
 if a=='login':r={'token':'a'*64,'expires':'2099-01-01T00:00:00Z'}
 elif a=='key':r={'key':'b'*64}
 elif a=='profiles':r={'profiles':[{k:p[k] for k in ['id','name','revision']} for p in profiles.values()]}
 elif a=='catalog':r={'profiles':[{**{k:p[k] for k in ['id','name','revision']},'foods':p['state']['foods'],'recipes':p['state']['recipes']} for p in profiles.values()]}
 elif a=='get':r={'profile':copy.deepcopy(profiles[b['id']])}
 elif a=='save':
  p=profiles[b['id']]
  if b['revision']!=p['revision']:return route.fulfill(status=409,json={'conflict':True,'error':'Synthetic revision conflict'})
  p['state']=copy.deepcopy(b['state']);p['revision']+=1;r={'revision':p['revision']}
 elif a=='logout':r={'ok':True}
 else:return route.fulfill(status=400,json={'error':'Unexpected synthetic action '+str(a)})
 route.fulfill(status=200,json=copy.deepcopy(r))
def newcontext(b,**opts):
 c=b.new_context(service_workers='block',accept_downloads=True,**opts);c.route('**/*',intercept);return c
def choose(p,id):
 p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('id=>window.NK_APP && NK_HOUSEHOLD.id===id && !document.querySelector("#app").hidden && !document.querySelector("#household-dialog").open',arg=id)
def login(p,id):
 p.goto(URL);p.locator('#gate-password').fill('synthetic-test-password');p.locator('#gate-form button[type=submit]').click();p.locator('#household-dialog[open]').wait_for();choose(p,id)
def nav(p,route):p.locator(f'.nav-btn[data-route="{route}"]:visible').first.click()
def save(p):
 p.evaluate('document.querySelector("#toast").textContent=""');p.locator('#profile-form button[type=submit]').click();p.wait_for_function('document.querySelector("#toast").textContent.includes("Tagesziele gespeichert")');p.evaluate('NK_HOUSEHOLD.flush()');p.wait_for_timeout(120)
def plan(p,goal='normal',pal='1.4'):
 nav(p,'profile');p.locator('#nutrition-goal').select_option(goal);p.locator('#activity-pal').select_option(pal);save(p)
engine=os.environ.get('TEST_BROWSER','chromium')
with sync_playwright() as pw:
 launch={'headless':True}
 if os.environ.get('LOCAL_CHROMIUM')=='1':launch['executable_path']='/usr/bin/chromium';launch['args']=['--no-sandbox']
 browser=getattr(pw,engine).launch(**launch);context=newcontext(browser,viewport={'width':390,'height':844});p=context.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 try:
  login(p,D);check('Stable URL works with password gate and existing default profile',p.url==URL)
  nav(p,'profile');check('Four requested goals are in the existing profile select',all(p.locator(f'#nutrition-goal option[value="{v}"]').count()==1 for v in ['normal','muscle','sport','loss']))
  check('Legacy preference not silently changed',p.locator('#nutrition-goal').input_value()=='' and not profiles[D]['state']['profile'].get('goal'))
  check('Activity must be explicitly selected',p.locator('#activity-pal').input_value()=='')
  p.locator('#nutrition-goal').select_option('normal');p.locator('#activity-pal').select_option('1.4');check('Preview shows all three grams before saving',all('—' not in p.locator(f'[data-preview-key="{k}"] strong').inner_text() for k in ['protein','fat','carbs']))
  check('Unsaved preview does not mutate profile',p.evaluate('!NK_APP.getState().profile.goal'))
  save(p);check('Goal and PAL are saved through normal sync',profiles[D]['state']['profile']['goal']=='normal' and profiles[D]['state']['profile']['pal']==1.4)
  nav(p,'today');check('All four overview cards show targets on an empty diary',p.locator('.macro-target').count()==4 and '64' in p.locator('[data-macro-key="protein"] .macro-target').inner_text())
  check('No fake zero intake or duplicate protein overlay',all(p.locator(f'[data-macro-key="{k}"] .metric-number').inner_text().startswith('—') for k in ['protein','carbs','fat']) and p.locator('.protein-target').count()==0)
  p.screenshot(path=str(BASE/'test-output'/f'{engine}-overview.png'))
  plan(p,'muscle');nav(p,'today');check('Muscle profile changes protein goal to 128g',p.locator('[data-macro-key="protein"] .macro-target strong').inner_text().startswith('128'))
  plan(p,'sport');check('Sport mode uses saved independent activity factor',p.evaluate('Math.abs(NK.targets(NK_APP.getState().profile).values.protein.value-112)<1e-8 && NK_APP.getState().profile.pal===1.4'))
  plan(p,'loss');check('Weight loss mode applies the explicit moderate energy adjustment',p.evaluate('Math.abs(NK_MACROS.calculate(NK_APP.getState().profile).detail.energyAdjustment + NK_MACROS.calculate(NK_APP.getState().profile).detail.maintenance*.1)<1e-8'))
  p.locator('#weight').fill('75');check('Weight edit recalculates preview, not stored body weight',p.locator('[data-preview-key="protein"] strong').inner_text().startswith('90') and p.evaluate('NK_APP.getState().profile.weight===80'));save(p)
  p.reload();p.wait_for_function('window.NK_APP && NK_HOUSEHOLD.id');nav(p,'profile');check('Selection survives reload with same profile',p.locator('#nutrition-goal').input_value()=='loss' and p.locator('#weight').input_value()=='75')
  p.locator('#target-protein').fill('150');p.locator('#target-energy').fill('2200');p.locator('#target-fat').fill('70');save(p)
  p.locator('#nutrition-goal').select_option('muscle');check('Explicit previous goals remain visible and override preset',p.locator('[data-preview-key="protein"] strong').inner_text().startswith('150') and p.locator('#macro-preview').inner_text().count('Eigene Werte haben Vorrang')==1);save(p)
  p.locator('details:has(#target-vitD)>summary').click();p.locator('#target-vitD').fill('42');save(p)
  p.once('dialog',lambda d:d.accept());p.locator('[data-action="reset-macro-goals"]').click();check('Reset button clears only macro fields and does not save yet',p.locator('#target-protein').input_value()=='' and p.locator('#target-vitD').input_value()=='42' and p.evaluate('NK_APP.getState().profile.manual.protein===150'));save(p)
  check('Micronutrient manual target survived macro reset',profiles[D]['state']['profile']['manual']=={'vitD':42})
  p.locator('#weight').fill('100');check('High BMI asks to confirm calculation weight',p.locator('[data-action="suggest-calc-weight"]').is_visible())
  p.locator('[data-action="suggest-calc-weight"]').click();check('Reference suggestion is explicit and does not change body weight',p.locator('#weight').input_value()=='100' and p.locator('#calc-weight').input_value()=='71.3');save(p)
  check('Different energy and protein calculation weights retained',p.evaluate('NK_MACROS.calculate(NK_APP.getState().profile).detail.proteinWeight===71.3 && NK_APP.getState().profile.weight===100'))
  p.locator('#special').check();check('Special situation suppresses all automatic preview goals',all('—' in p.locator(f'[data-preview-key="{k}"] strong').inner_text() for k in ['protein','fat','carbs','energy']));save(p)
  p.locator('#special').uncheck();p.locator('#weight').fill('80');p.locator('details:has(#calc-weight)>summary').click();p.locator('#calc-weight').fill('');p.locator('#nutrition-goal').select_option('muscle');save(p)
  check('Existing product finder and portion converter still loaded',p.evaluate('!!NK_PORTIONS && !!NK_PRODUCT_CORE && !!NK_SHARED'))
  ctx2=newcontext(browser,viewport={'width':390,'height':844});p2=ctx2.new_page();p2.on('pageerror',lambda e:errors.append(str(e)));login(p2,P);plan(p2,'normal','1.6')
  check('Patricia has her own unchanged weight and normal mode',profiles[P]['state']['profile']['goal']=='normal' and profiles[P]['state']['profile']['weight']==60)
  check('Dimitri muscle goal not overwritten by Patricia',profiles[D]['state']['profile']['goal']=='muscle')
  ctx3=newcontext(browser);p3=ctx3.new_page();login(p3,D);nav(p3,'profile');check('Goal syncs to another device of same person',p3.locator('#nutrition-goal').input_value()=='muscle' and p3.locator('#activity-pal').input_value()=='1.4');ctx3.close()
  nav(p,'today');p.evaluate("NK_APP.openFood({id:'synthetic-test-food',name:'Synthetic test food',basis:'g',density:null,n:Object.fromEntries(NK_DATA.nutrients.map(n=>[n.key,({energy:128,protein:32,carbs:0,fat:0})[n.key]??null])),q:{},kind:'custom',source:'Synthetic only'})")
  p.locator('#food-qty').fill('400');p.locator('#food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().entries.length===1');p.evaluate('NK_HOUSEHOLD.flush()')
  p.locator('#protein-party[open]').wait_for();check('Spanish celebration uses new muscle target',p.locator('#party-amount').inner_text().count('128')==2);p.locator('#party-close').click()
  before=p.evaluate('JSON.stringify(NK_APP.getState().entries)');plan(p,'normal');check('Changing goal never rewrites historical nutrient snapshots',p.evaluate('JSON.stringify(NK_APP.getState().entries)')==before)
  p2.reload();p2.wait_for_function('window.NK_APP');check('Consumption stays private per profile',p2.evaluate('NK_APP.getState().entries.length===0'))
  nav(p,'profile');p.locator('#target-energy').fill('2000');p.locator('#target-protein').fill('400');p.locator('#target-fat').fill('100');check('Inconsistent manual plan has warning and no negative carb target','kein automatisches Kohlenhydratziel' in p.locator('#macro-preview').inner_text() and '—' in p.locator('[data-preview-key="carbs"] strong').inner_text())
  p.locator('#target-protein').fill('1,5');check('Comma decimals accepted in live preview',p.locator('[data-preview-key="protein"] strong').inner_text().startswith('1.5'))
  for width in [320,390,1440]:
   p.set_viewport_size({'width':width,'height':900});p.wait_for_timeout(150);check(f'Profile layout fits {width}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  p.set_viewport_size({'width':320,'height':900});p.locator('details:has(#calc-weight)>summary').click();p.wait_for_timeout(150);check('Expanded reference fields also fit narrow WebKit layout',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  p.set_viewport_size({'width':390,'height':844});p.screenshot(path=str(BASE/'test-output'/f'{engine}-profile.png'),full_page=True)
  p.locator('#target-protein').fill('');p.locator('#target-energy').fill('');p.locator('#target-fat').fill('');save(p);nav(p,'today')
  for width in [320,1440]:
   p.set_viewport_size({'width':width,'height':900});p.wait_for_timeout(150);check(f'Overview layout fits {width}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  check('No browser runtime errors',not errors)
  check('No real private data requested',not any(a in requests for a in ['create','delete','rename','setup','password']))
 except Exception:
  layout=p.evaluate('''() => ({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,overflows:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+.5||e.scrollWidth>e.clientWidth+2).map(e=>({tag:e.tagName,id:e.id,classes:String(e.className).slice(0,100),right:e.getBoundingClientRect().right,left:e.getBoundingClientRect().left,client:e.clientWidth,scroll:e.scrollWidth,display:getComputedStyle(e).display,text:e.textContent.slice(0,100)})).slice(0,100)})''')
  (BASE/'test-output'/f'{engine}-layout.json').write_text(json.dumps(layout,indent=2))
  p.screenshot(path=str(BASE/'test-output'/f'{engine}-failure.png'),full_page=True);print(p.locator('body').inner_text()[-5000:]);(BASE/'test-output'/f'{engine}-failure.txt').write_text(traceback.format_exc());raise
 finally:
  (BASE/'test-output'/f'{engine}-goals-report.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'runtimeErrors':errors,'realPrivateApiCalls':False},indent=2));browser.close();server.shutdown()
